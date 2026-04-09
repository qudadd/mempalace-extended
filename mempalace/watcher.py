"""Folder watch support for automatic incremental ingest."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from .config import MempalaceConfig
from .convo_miner import mine_convos, scan_convos
from .miner import mine, scan_project

DEFAULT_POLL_SECONDS = 5.0


def build_watch_id(directory: str, palace_path: str, mode: str, wing: str = None) -> str:
    """Create a stable watch identifier for one directory/config combination."""
    resolved_dir = str(Path(directory).expanduser().resolve())
    resolved_palace = str(Path(palace_path).expanduser().resolve())
    signature = f"{resolved_dir}|{resolved_palace}|{mode}|{wing or ''}"
    digest = hashlib.sha1(signature.encode("utf-8"), usedforsecurity=False).hexdigest()[:10]
    slug = _slugify(Path(resolved_dir).name or "watch")
    return f"{slug}-{digest}"


def save_watch_state(state: dict) -> Path:
    """Persist one watcher's state as a standalone JSON file."""
    path = watch_state_path(state["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=True)
    os.replace(tmp_path, path)
    return path


def load_watch_state(watch_id: str) -> dict | None:
    """Load persisted state for one watcher."""
    path = watch_state_path(watch_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_watch_states() -> list[dict]:
    """Return all known watcher states sorted by creation time."""
    states = []
    for path in sorted(watch_root().glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                states.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue
    states.sort(key=lambda item: (item.get("created_at", ""), item.get("id", "")))
    return states


def watch_root() -> Path:
    """Directory containing watch state files and logs."""
    root = MempalaceConfig().watchers_dir
    root.mkdir(parents=True, exist_ok=True)
    return root


def watch_state_path(watch_id: str) -> Path:
    """JSON state file for one watcher."""
    return watch_root() / f"{watch_id}.json"


def watch_log_path(watch_id: str) -> Path:
    """Log file for one watcher process."""
    return watch_root() / f"{watch_id}.log"


def create_watch_state(
    directory: str,
    palace_path: str,
    mode: str,
    wing: str = None,
    agent: str = "mempalace-watch",
    limit: int = 0,
    extract: str = "exchange",
    respect_gitignore: bool = True,
    include_ignored: list | None = None,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    prune_missing: bool = True,
    initial_sync: bool = True,
) -> dict:
    """Build the persisted configuration for one watch."""
    resolved_dir = str(Path(directory).expanduser().resolve())
    resolved_palace = str(Path(palace_path).expanduser().resolve())
    include_ignored = include_ignored or []
    watch_id = build_watch_id(resolved_dir, resolved_palace, mode, wing=wing)
    state = load_watch_state(watch_id) or {}
    state.update(
        {
            "id": watch_id,
            "dir": resolved_dir,
            "palace_path": resolved_palace,
            "mode": mode,
            "wing": wing,
            "agent": agent,
            "limit": limit,
            "extract": extract,
            "respect_gitignore": respect_gitignore,
            "include_ignored": include_ignored,
            "poll_seconds": max(float(poll_seconds), 1.0),
            "prune_missing": bool(prune_missing),
            "initial_sync": bool(initial_sync),
            "log_path": str(watch_log_path(watch_id)),
            "created_at": state.get("created_at") or _timestamp(),
        }
    )
    return state


def start_watch(state: dict) -> dict:
    """Launch a detached watch process and persist its config."""
    existing = load_watch_state(state["id"])
    if existing and existing.get("pid") and _is_process_running(existing["pid"]):
        raise RuntimeError(f"Watch already running: {state['id']}")

    state["status"] = "starting"
    state["pid"] = None
    state["last_error"] = None
    save_watch_state(state)

    command = [
        sys.executable,
        "-u",
        "-m",
        "mempalace",
        "--palace",
        state["palace_path"],
        "watch",
        "run",
        "--watch-id",
        state["id"],
    ]

    log_path = watch_log_path(state["id"])
    with open(log_path, "ab") as log_file:
        kwargs = {
            "stdin": subprocess.DEVNULL,
            "stdout": log_file,
            "stderr": subprocess.STDOUT,
            "cwd": state["dir"],
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
                subprocess, "CREATE_NEW_PROCESS_GROUP", 0
            )
        else:
            kwargs["start_new_session"] = True

        process = subprocess.Popen(command, **kwargs)

    state["pid"] = process.pid
    state["status"] = "starting"
    state["started_at"] = _timestamp()
    save_watch_state(state)
    return state


def stop_watch(target: str = None, stop_all: bool = False) -> list[dict]:
    """Stop one watcher by id/path, or every watcher when stop_all is set."""
    matches = resolve_watch_targets(target=target, stop_all=stop_all)
    stopped = []

    for state in matches:
        pid = state.get("pid")
        if pid and _is_process_running(pid):
            _terminate_process(pid)
        state["status"] = "stopped"
        state["pid"] = None
        state["stopped_at"] = _timestamp()
        save_watch_state(state)
        stopped.append(state)

    return stopped


def resolve_watch_targets(target: str = None, stop_all: bool = False) -> list[dict]:
    """Resolve a user-facing watch target into concrete state records."""
    states = list_watch_states()
    if stop_all:
        return states
    if not target:
        return []

    normalized_target = target
    try:
        normalized_target = str(Path(target).expanduser().resolve())
    except OSError:
        pass

    matches = [
        state
        for state in states
        if state.get("id") == target or state.get("dir") == normalized_target
    ]
    return matches


def sync_watch_once(state: dict) -> dict:
    """Run one incremental ingest pass for a watch definition."""
    watch_id = state["id"]
    current = load_watch_state(watch_id) or state.copy()
    current["last_heartbeat"] = _timestamp()
    save_watch_state(current)

    try:
        if current["mode"] == "convos":
            mine_convos(
                convo_dir=current["dir"],
                palace_path=current["palace_path"],
                wing=current.get("wing"),
                agent=current.get("agent", "mempalace-watch"),
                limit=current.get("limit", 0),
                dry_run=False,
                extract_mode=current.get("extract", "exchange"),
                prune_missing=current.get("prune_missing", True),
            )
        else:
            mine(
                project_dir=current["dir"],
                palace_path=current["palace_path"],
                wing_override=current.get("wing"),
                agent=current.get("agent", "mempalace-watch"),
                limit=current.get("limit", 0),
                dry_run=False,
                respect_gitignore=current.get("respect_gitignore", True),
                include_ignored=current.get("include_ignored", []),
                prune_missing=current.get("prune_missing", True),
            )
    except Exception as exc:
        current["last_sync_status"] = "error"
        current["last_error"] = str(exc)
        current["last_sync_at"] = _timestamp()
        save_watch_state(current)
        raise

    current["last_sync_status"] = "ok"
    current["last_error"] = None
    current["last_sync_at"] = _timestamp()
    save_watch_state(current)
    return current


def run_watch(watch_id: str):
    """Run one watcher in the foreground until interrupted."""
    state = load_watch_state(watch_id)
    if not state:
        raise RuntimeError(f"Unknown watch id: {watch_id}")

    state["status"] = "running"
    state["pid"] = os.getpid()
    state["started_at"] = state.get("started_at") or _timestamp()
    state["stopped_at"] = None
    save_watch_state(state)

    try:
        previous_snapshot = build_watch_snapshot(state)
        if state.get("initial_sync", True):
            sync_watch_once(state)

        while True:
            state = load_watch_state(watch_id) or state
            state["last_heartbeat"] = _timestamp()
            save_watch_state(state)

            time.sleep(max(float(state.get("poll_seconds", DEFAULT_POLL_SECONDS)), 1.0))
            current_snapshot = build_watch_snapshot(state)
            if current_snapshot != previous_snapshot:
                state["last_change_at"] = _timestamp()
                state["last_change_count"] = diff_snapshot_counts(
                    previous_snapshot, current_snapshot
                )
                save_watch_state(state)
                sync_watch_once(state)
                previous_snapshot = current_snapshot
    except KeyboardInterrupt:
        pass
    finally:
        state = load_watch_state(watch_id) or state
        state["status"] = "stopped"
        state["pid"] = None
        state["stopped_at"] = _timestamp()
        save_watch_state(state)


def build_watch_snapshot(state: dict) -> dict[str, float]:
    """Build the file snapshot that drives change detection."""
    directory = state["dir"]
    snapshot_paths = []

    if state["mode"] == "convos":
        snapshot_paths = scan_convos(directory)
    else:
        snapshot_paths = scan_project(
            directory,
            respect_gitignore=state.get("respect_gitignore", True),
            include_ignored=state.get("include_ignored", []),
        )
        root = Path(directory)
        for extra_name in ("mempalace.yaml", "mempal.yaml", "entities.json"):
            extra = root / extra_name
            if extra.exists():
                snapshot_paths.append(extra)

    snapshot = {}
    for path in snapshot_paths:
        try:
            snapshot[str(Path(path).resolve())] = os.path.getmtime(path)
        except OSError:
            continue
    return snapshot


def refresh_watch_status(state: dict) -> dict:
    """Mark stale PIDs as stopped so status output stays honest."""
    pid = state.get("pid")
    if state.get("status") in {"running", "starting"} and pid and not _is_process_running(pid):
        state["status"] = "stopped"
        state["pid"] = None
        state["stopped_at"] = state.get("stopped_at") or _timestamp()
        save_watch_state(state)
    return state


def _is_process_running(pid: int) -> bool:
    if not pid:
        return False
    if os.name == "nt":
        import ctypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259

        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            int(pid),
        )
        if not handle:
            return False

        try:
            exit_code = ctypes.c_ulong()
            if not ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == STILL_ACTIVE
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    return True


def _terminate_process(pid: int):
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return

    try:
        os.kill(int(pid), signal.SIGTERM)
    except OSError:
        return


def _timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _slugify(value: str) -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        else:
            chars.append("-")
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "watch"


def diff_snapshot_counts(previous: dict[str, float], current: dict[str, float]) -> int:
    """Count added, removed, and modified files between two snapshots."""
    count = 0
    previous_keys = set(previous)
    current_keys = set(current)

    count += len(previous_keys - current_keys)
    count += len(current_keys - previous_keys)

    for key in previous_keys & current_keys:
        if previous[key] != current[key]:
            count += 1

    return count

import time
from pathlib import Path

import chromadb
import yaml

from mempalace.watcher import (
    build_watch_snapshot,
    create_watch_state,
    diff_snapshot_counts,
    load_watch_state,
    save_watch_state,
    sync_watch_once,
)


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_watch_snapshot_tracks_project_files_and_config(tmp_path):
    project_root = tmp_path / "project"
    write_file(project_root / "src" / "app.py", "print('hello')\n" * 20)
    with open(project_root / "mempalace.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"wing": "watch_test", "rooms": [{"name": "src", "description": "Code"}]}, f)

    state = create_watch_state(
        directory=str(project_root),
        palace_path=str(tmp_path / "palace"),
        mode="projects",
    )

    snapshot_one = build_watch_snapshot(state)
    time.sleep(1.1)
    write_file(project_root / "mempalace.yaml", "wing: watch_test\nrooms:\n  - name: src\n")
    snapshot_two = build_watch_snapshot(state)

    assert str((project_root / "src" / "app.py").resolve()) in snapshot_one
    assert str((project_root / "mempalace.yaml").resolve()) in snapshot_one
    assert diff_snapshot_counts(snapshot_one, snapshot_two) == 1


def test_sync_watch_once_records_success_and_files_drawers(tmp_path):
    project_root = tmp_path / "project"
    write_file(project_root / "backend" / "app.py", "print('watch me')\n" * 40)
    with open(project_root / "mempalace.yaml", "w", encoding="utf-8") as f:
        yaml.dump(
            {
                "wing": "watch_test",
                "rooms": [
                    {"name": "backend", "description": "Backend code"},
                    {"name": "general", "description": "General"},
                ],
            },
            f,
        )

    palace_path = tmp_path / "palace"
    state = create_watch_state(
        directory=str(project_root),
        palace_path=str(palace_path),
        mode="projects",
        agent="watcher-test",
    )
    save_watch_state(state)

    synced = sync_watch_once(state)
    persisted = load_watch_state(state["id"])

    client = chromadb.PersistentClient(path=str(palace_path))
    col = client.get_collection("mempalace_drawers")

    assert synced["last_sync_status"] == "ok"
    assert persisted["last_sync_status"] == "ok"
    assert persisted["last_sync_at"]
    assert col.count() > 0

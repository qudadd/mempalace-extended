# MemPalace Extended

Repository name: `mempalace-extended`

[![Python](https://img.shields.io/badge/python-%3E%3D3.9-blue)](pyproject.toml)
[![Windows](https://img.shields.io/badge/windows-recommended%203.11-0A7CFF)](#runtime-environment)
[![CI](https://img.shields.io/badge/CI-3.9%20%7C%203.11%20%7C%203.13-brightgreen)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-stdio-orange)](#mcp-integration)

MemPalace Extended is a GitHub-ready extension of the original
[MemPalace](https://github.com/milla-jovovich/mempalace) project.
It keeps the original local-first memory workflow and adds:

- read-only ingestion for `PDF`, `DOCX`, and `XLSX`
- image asset storage for `PNG`, `JPG`, `JPEG`, `GIF`, `WEBP`, and `BMP`
- mixed `text + image` MCP responses
- folder watch with `start / stop / status`
- stable embedding cache configuration

The Python package and CLI command remain `mempalace` for compatibility.

## Attribution

This repository is based on the original MemPalace project by
`milla-jovovich` and contributors.

- Original repository: <https://github.com/milla-jovovich/mempalace>
- Original license: MIT
- Upstream source baseline used for this extension: original `main` branch
  source version `3.0.14`
- Original repository's latest visible GitHub Release: `v3.0.0`
- Extension status: this repository adds document ingestion, image asset
  handling, MCP multimodal responses, and folder watching on top of the
  original project structure

See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).

### Upstream Baseline Note

This extension was prepared from the upstream source state where
`mempalace/version.py` reported `3.0.14`.

That is different from the original repository's latest visible GitHub Release
tag, which is currently `v3.0.0`.

For provenance, the most accurate short description is:

`based on original MemPalace main-branch source version 3.0.14`

## What This Version Focuses On

This extension is intended for practical local knowledge management:

- mine source code, notes, reports, papers, and spreadsheets into one palace
- keep source directories untouched during indexing
- let MCP-compatible AI clients search the palace and retrieve related images
- monitor a folder continuously and ingest new knowledge automatically

This repository does not try to preserve the original README's benchmark and
marketing framing. It documents the extension as a usable engineering fork.

## Feature Summary

### Core memory workflow

- `mempalace init <dir>`
- `mempalace mine <dir>`
- `mempalace search "query"`
- `mempalace status`
- `mempalace wake-up`

### Extended project ingest

- plain text, Markdown, code, JSON, YAML, CSV, SQL, HTML, CSS, TOML
- `PDF` text extraction via `pypdf`
- `DOCX` text and table extraction via `python-docx`
- `XLSX` sheet and cell extraction via `openpyxl`
- image asset indexing with sidecar metadata and palace-managed copies

### Extended MCP behavior

- semantic text search
- image asset retrieval through `mempalace_get_asset`
- search responses can include related images alongside text hits
- works with MCP clients that support `stdio` servers

### Automatic folder watch

- `mempalace watch start <dir>`
- `mempalace watch status`
- `mempalace watch stop <dir-or-id>`
- supports project folders and conversation export folders
- optional pruning of drawers for deleted files

## Supported Inputs

### Projects mode

Supported directly:

- `.txt`, `.md`
- `.py`, `.js`, `.ts`, `.jsx`, `.tsx`
- `.json`, `.yaml`, `.yml`, `.toml`
- `.html`, `.css`
- `.java`, `.go`, `.rs`, `.rb`, `.sh`, `.sql`, `.csv`
- `.pdf`, `.docx`, `.xlsx`
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`

### Conversations mode

Supported directly:

- `.txt`, `.md`
- `.json`, `.jsonl`

Built-in normalization handles:

- Claude Code JSONL
- OpenAI Codex CLI JSONL
- Claude exports
- ChatGPT conversations JSON
- Slack exports

## Runtime Environment

### Compatibility at a glance

| Target | Python | Status | Notes |
| --- | --- | --- | --- |
| Windows local use | `3.11` | recommended | best default for conda or `uv` |
| Windows local use | `3.10` or `3.12` | supported with caution | often workable, but not the primary local baseline |
| Windows local use | `3.13` or `3.14` | not recommended | may require native builds in the `chromadb` dependency chain |
| Linux or macOS | `3.9`, `3.11`, `3.13` | CI-validated | current GitHub Actions matrix runs on Ubuntu |

### Recommended baseline

- operating system: Windows 10 or Windows 11
- shell: PowerShell or Windows Terminal
- Python: `3.11`
- environment manager: `conda` or `uv`
- storage: local SSD with enough space for the palace, image assets, and embedding cache
- MCP client: a client that supports `stdio` MCP servers and tool calling

### Supported Python range

The package metadata currently declares `Python >= 3.9`, and the current CI
matrix exercises `3.9`, `3.11`, and `3.13` on Ubuntu.

For practical local use, this fork is best treated as:

- recommended: `3.11`
- practical target range: `3.9` to `3.13`, depending on platform
- not recommended on Windows: `3.13` and `3.14` unless you are prepared to
  build native dependencies locally

Reason: the `chromadb` dependency chain may pull native build steps on newer
Windows Python versions.

### Tested environment

This extension has been exercised in the following setup:

| Item | Value |
| --- | --- |
| OS | Windows 11 |
| Shell | PowerShell |
| Python | 3.11.15 in a conda environment |
| Environment manager | Anaconda / conda |
| Install mode | `pip install -e .` and `uv sync --python 3.11` |
| MCP client | Cherry Studio |
| Storage layout | palace on a secondary drive, embedding cache on a configurable local path |

Current GitHub Actions coverage:

| OS | Python |
| --- | --- |
| Ubuntu | `3.9`, `3.11`, `3.13` |

### Runtime dependencies

Core dependencies used by this fork:

- `chromadb`
- `pyyaml`
- `pypdf`
- `python-docx`
- `openpyxl`

Optional development dependencies:

- `pytest`
- `pytest-cov`
- `ruff`
- `psutil`

### MCP client requirements

For the multimodal MCP path to work well, the client should support:

- `stdio` MCP servers
- tool calling
- rendering mixed `text + image` tool responses if you want image output

Cherry Studio is the reference client currently documented in this repository.

## Installation

### Windows with conda (`3.11` recommended)

This is the safest Windows path for most users.

```powershell
git clone https://github.com/qudadd/mempalace-extended.git
cd mempalace-extended

conda create -n mempalace python=3.11 -y
conda activate mempalace

pip install -e .
```

### Windows with conda (`3.10` or `3.12`)

If you already standardize on one of these versions, use the same flow:

```powershell
git clone https://github.com/qudadd/mempalace-extended.git
cd mempalace-extended

conda create -n mempalace python=3.10 -y
conda activate mempalace
pip install -e .
```

or:

```powershell
conda create -n mempalace python=3.12 -y
conda activate mempalace
pip install -e .
```

If installation on Windows fails with native dependency errors, switch back to
`3.11` before troubleshooting anything else.

### Windows with `uv`

`uv` can resolve the Python version per machine:

```powershell
uv sync --python 3.11
```

Alternative examples:

```powershell
uv sync --python 3.10
uv sync --python 3.12
```

### Linux or macOS with `venv`

Example with Python `3.11`:

```bash
git clone https://github.com/qudadd/mempalace-extended.git
cd mempalace-extended

python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Other supported CI-backed examples:

```bash
python3.9 -m venv .venv
python3.13 -m venv .venv
```

### Windows launcher scripts

- [`start_mempalace.bat`](start_mempalace.bat) is included as a generic template
- [`mempalace_mcp.bat`](mempalace_mcp.bat) is included as a Windows MCP server launcher
- override `CONDA_ROOT`, `ENV_NAME`, `PALACE_PATH`, or
  `MEMPALACE_EMBEDDING_CACHE_PATH` if your local setup differs

### Recommended storage placement

If your system drive is small, put the palace on another drive:

```powershell
$env:MEMPALACE_PALACE_PATH = "D:\MemPalaceData\palace"
$env:MEMPALACE_EMBEDDING_CACHE_PATH = "D:\MemPalaceData\cache\onnx_models"
```

You can also persist those values through `~/.mempalace/config.json` or your
launcher script.

## Quick Start

### 1. Initialize a project directory

```powershell
mempalace init "D:\Projects\my_project"
```

This writes a sidecar config such as `mempalace.yaml` into the target
directory. It does not modify existing project files.

### 2. Mine the directory

```powershell
mempalace mine "D:\Projects\my_project"
```

If you want drawers for deleted files to be removed during the sync:

```powershell
mempalace mine "D:\Projects\my_project" --prune-missing
```

### 3. Search

```powershell
mempalace search "authentication flow"
mempalace search "Figure 2" --wing my_project
```

### 4. Check status

```powershell
mempalace status
```

## Automatic Folder Watch

The extension adds a poll-based watcher that runs incremental ingest for a
folder in the background.

### Start watching a project folder

```powershell
mempalace watch start "D:\Projects\my_project"
```

### Start watching a conversation export folder

```powershell
mempalace watch start "D:\Exports\chat_logs" --mode convos --extract general
```

### Run in the foreground for debugging

```powershell
mempalace watch start "D:\Projects\my_project" --foreground --poll-seconds 2
```

### Check watch status

```powershell
mempalace watch status
```

### Stop one watch

```powershell
mempalace watch stop "D:\Projects\my_project"
```

### Stop all watches

```powershell
mempalace watch stop --all
```

### Watch behavior

- first sync runs immediately by default
- changed files are re-mined
- new files are mined automatically
- deleted files can be pruned unless `--no-prune-missing` is used
- watch state is stored in `~/.mempalace/watchers`

### Watch verification notes

This extension has been smoke-tested with the following sequence on Windows:

- `watch start`
- initial sync reaches `Sync: ok`
- add one new file into the watched folder
- `watch status` reports `Change: 1 file(s)`
- `watch stop` cleanly stops the worker

Practical caveat:

- if the embedding cache is empty, the first sync may need to download the
  ONNX embedding model before mining can finish
- on slow or restricted networks, pre-warm the cache by running one normal
  `mempalace mine <dir>` first, or point
  `MEMPALACE_EMBEDDING_CACHE_PATH` to a populated cache location

## Storage Layout

Global defaults are managed by `~/.mempalace/config.json`.

Common paths:

- palace database: `~/.mempalace/palace`
- image assets: `<palace>/assets/images`
- knowledge graph: `<palace>/knowledge_graph.sqlite3`
- watcher state: `~/.mempalace/watchers`
- embedding cache: `~/.mempalace/cache/onnx_models`

You can override the palace location:

```powershell
mempalace --palace "D:\MemPalaceData\palace" status
```

You can override the embedding cache path:

```powershell
$env:MEMPALACE_EMBEDDING_CACHE_PATH = "D:\MemPalaceData\cache\onnx_models"
```

## MCP Integration

This extension is designed to work as a local `stdio` MCP server.

Examples in this section use Windows paths for illustration only. Replace them
with paths from your own machine.

Server entry:

```powershell
python -m mempalace.mcp_server --palace "D:\MemPalaceData\palace"
```

### What MCP exposes

This fork currently exposes the original MemPalace toolset plus the added
image asset tool:

- `mempalace_status`
- `mempalace_list_wings`
- `mempalace_list_rooms`
- `mempalace_get_taxonomy`
- `mempalace_search`
- `mempalace_get_asset`
- `mempalace_check_duplicate`
- `mempalace_get_aaak_spec`
- `mempalace_add_drawer`
- `mempalace_delete_drawer`
- `mempalace_kg_query`
- `mempalace_kg_add`
- `mempalace_kg_invalidate`
- `mempalace_kg_timeline`
- `mempalace_kg_stats`
- `mempalace_traverse`
- `mempalace_find_tunnels`
- `mempalace_graph_stats`
- `mempalace_diary_write`
- `mempalace_diary_read`

### Generic MCP configuration

For any MCP client that supports `stdio`, configure:

- command: path to your Python executable
- args:
  `-m`
  `mempalace.mcp_server`
  `--palace`
  `<your-palace-path>`

Windows example:

- command: `D:\anaconda\envs\mempalace\python.exe`
- args:
  `-m`
  `mempalace.mcp_server`
  `--palace`
  `D:\MemPalaceData\palace`

Optional environment variables:

- `MEMPALACE_PALACE_PATH`
- `MEMPALACE_EMBEDDING_CACHE_PATH`
- `PYTHONIOENCODING=utf-8`

### Machine-specific command paths

The sample path `D:\anaconda\envs\mempalace\python.exe` is only an example.
It is not portable across machines.

For real deployments, use one of these approaches:

1. Point the MCP client at the Python executable inside that machine's active
   environment.
2. On Windows, point the client at the repo-local
   [`mempalace_mcp.bat`](mempalace_mcp.bat) wrapper.
3. Use environment variables such as `PALACE_PATH`, `ENV_NAME`, and
   `CONDA_ROOT` to adapt the wrapper script without editing the repository.

The included `mempalace_mcp.bat` script is the portable Windows option in this
fork. It auto-detects common Conda installation locations and uses the repo's
own directory as the working directory.

You can verify the wrapper before wiring it into an MCP client:

```powershell
mempalace_mcp.bat --check
```

### Cherry Studio configuration

Cherry Studio works well with this extension when configured as a manual
`stdio` MCP server.

Recommended setup:

1. Open `Settings`
2. Open `MCP Server`
3. Add a new server
4. Fill the fields with:

- Name: `mempalace`
- Type: `stdio`
- Command: `D:\anaconda\envs\mempalace\python.exe`
- Parameters:
  `-m`
  `mempalace.mcp_server`
  `--palace`
  `D:\MemPalaceData\palace`

Portable Windows option:

- Command: `C:\path\to\mempalace-extended\mempalace_mcp.bat`
- Parameters: leave empty

Optional variables for the wrapper:

```text
ENV_NAME=mempalace
PALACE_PATH=D:\MemPalaceData\palace
MEMPALACE_EMBEDDING_CACHE_PATH=D:\MemPalaceData\cache\onnx_models
```

Optional environment variables:

```text
MEMPALACE_EMBEDDING_CACHE_PATH=D:\MemPalaceData\cache\onnx_models
PYTHONIOENCODING=utf-8
```

### How to verify MCP is working

1. Save the MCP server configuration
2. Start a new chat
3. Enable the `mempalace` MCP server for that chat
4. Use a model that supports tool calling
5. Ask the model to call tools explicitly the first time

Example prompts:

```text
Use mempalace_status first, then summarize the current palace structure and total drawer count.
```

```text
Use mempalace_search to find "authentication flow" in wing "my_project".
Return the most relevant passages together with source file names.
```

```text
Use mempalace_search to find "meeting notes" across the whole palace and group the results by source file.
```

```text
Use mempalace_get_asset to fetch "Figure 2" from wing "research_notes".
Return the related text context together with the image.
```

### MCP behavior notes

- `mempalace_search` returns standard structured search results and can also
  include image blocks for MCP clients that render images
- `mempalace_get_asset` is the direct image retrieval tool
- image indexing is file-based and context-based
- OCR is not enabled in this extension

## Common Commands

```powershell
# setup
mempalace init <dir>

# mining
mempalace mine <dir>
mempalace mine <dir> --prune-missing
mempalace mine <dir> --mode convos
mempalace mine <dir> --mode convos --extract general

# watch
mempalace watch start <dir>
mempalace watch start <dir> --mode convos
mempalace watch status
mempalace watch stop <dir-or-id>
mempalace watch stop --all

# search
mempalace search "query"
mempalace search "query" --wing my_project
mempalace search "query" --room figures

# memory stack
mempalace wake-up
mempalace wake-up --wing my_project

# maintenance
mempalace status
mempalace repair
```

## Limitations

- image content is stored and returned, but not OCR-indexed
- watch mode is poll-based, not kernel-event based
- the package import path is still `mempalace`
- if you publish this as a new PyPI package, you should rename the package and
  update package metadata accordingly

## Development

Run tests:

```powershell
python -m pytest
```

## Publishing Notes

If you publish this fork on GitHub:

- keep [LICENSE](LICENSE)
- keep [NOTICE.md](NOTICE.md)
- keep the attribution section in this README
- do not claim the original MemPalace codebase as entirely new work

Before publishing a package or release artifact, review:

- `project.urls` in [pyproject.toml](pyproject.toml)
- `authors` in [pyproject.toml](pyproject.toml) if needed
- repository visibility, description, and screenshots in GitHub settings

## License

MIT. See [LICENSE](LICENSE).

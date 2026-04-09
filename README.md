# MemPalace Extended

Repository name: `mempalace-extended`

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
- Extension status: this repository adds document ingestion, image asset
  handling, MCP multimodal responses, and folder watching on top of the
  original project structure

See [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).

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

## Installation

### Recommended on Windows

Python `3.11` is the safest target on Windows.

```powershell
git clone https://github.com/qudadd/mempalace-extended.git
cd mempalace-extended

conda create -n mempalace python=3.11 -y
conda activate mempalace

pip install -e .
```

If you prefer `uv`:

```powershell
uv sync --python 3.11
```

Optional Windows launcher:

- [`start_mempalace.bat`](start_mempalace.bat) is included as a generic template
- override `CONDA_ROOT`, `ENV_NAME`, `PALACE_PATH`, or
  `MEMPALACE_EMBEDDING_CACHE_PATH` if your local setup differs

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
Call mempalace_status first, then summarize the current palace.
```

```text
Use mempalace_search to find "loop gain" in wing "no9_monitoring_review".
Return the source file names and the most relevant passages.
```

```text
Use mempalace_get_asset to fetch "Figure 2" from wing "no9_monitoring_review".
Return the text summary and the image together.
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

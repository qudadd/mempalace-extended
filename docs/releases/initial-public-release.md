# MemPalace Extended: Initial Public Release

Suggested GitHub release title:

`MemPalace Extended - Initial Public Release`

This repository is an extension of the original
[MemPalace](https://github.com/milla-jovovich/mempalace) project.
It keeps the original `mempalace` package and CLI surface, then adds a more
practical local-first workflow for documents, images, MCP, and automatic folder
tracking.

## What this extension adds

- read-only ingestion for `PDF`, `DOCX`, and `XLSX`
- image asset storage under the palace path
- mixed `text + image` MCP responses
- `mempalace_get_asset` for direct image retrieval
- background folder watch with `start`, `status`, and `stop`
- configurable embedding cache placement
- source-directory-safe indexing

## Runtime summary

- package metadata: `Python >= 3.9`
- recommended Windows target: `Python 3.11`
- current CI matrix on Ubuntu: `3.9`, `3.11`, `3.13`
- Windows `3.13` and `3.14` are not the recommended default targets

## MCP summary

This extension is intended to run as a local `stdio` MCP server:

```text
python -m mempalace.mcp_server --palace <your-palace-path>
```

Typical tool flow:

- `mempalace_status`
- `mempalace_search`
- `mempalace_get_asset`

For Windows users, this repository also includes `mempalace_mcp.bat` so MCP
clients do not need to hard-code one specific `python.exe` path from another
machine.

## Folder watch summary

The extension adds incremental folder tracking:

- `mempalace watch start <dir>`
- `mempalace watch status`
- `mempalace watch stop <dir-or-id>`

Verified workflow:

- start a watch
- initial sync completes
- add one new file
- watcher reports one file change
- stop the watcher cleanly

Operational note:

- if the embedding model is not already cached, the first sync may need to
  download the ONNX model before mining finishes

## Attribution

This repository remains an extension of the original MemPalace project by
`milla-jovovich` and contributors.

- Original repository: <https://github.com/milla-jovovich/mempalace>
- Upstream source baseline used for this extension: original `main` branch
  source version `3.0.14`
- Original repository's latest visible GitHub Release: `v3.0.0`
- License: MIT

See `NOTICE.md` for attribution details.

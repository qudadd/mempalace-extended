"""Binary asset storage for MemPalace-managed files."""

from __future__ import annotations

import base64
import hashlib
import mimetypes
from pathlib import Path


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
}


def is_image_file(path: str | Path) -> bool:
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def store_image_asset(source_file: str | Path, palace_path: str | Path) -> dict:
    source = Path(source_file)
    palace = Path(palace_path)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    ext = source.suffix.lower()

    assets_dir = palace / "assets" / "images"
    assets_dir.mkdir(parents=True, exist_ok=True)
    asset_path = assets_dir / f"{digest}{ext}"

    if not asset_path.exists():
        asset_path.write_bytes(source.read_bytes())

    mime_type = mimetypes.guess_type(asset_path.name)[0] or _fallback_mime(ext)
    return {
        "asset_type": "image",
        "asset_path": str(asset_path),
        "asset_sha256": digest,
        "mime_type": mime_type,
        "original_filename": source.name,
    }


def encode_image_asset(asset_path: str | Path) -> str:
    data = Path(asset_path).read_bytes()
    return base64.b64encode(data).decode("ascii")


def _fallback_mime(ext: str) -> str:
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }.get(ext, "application/octet-stream")

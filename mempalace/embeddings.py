"""Shared embedding function configuration for MemPalace."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

from .config import MempalaceConfig


class MempalaceEmbeddingFunction(ONNXMiniLM_L6_V2):
    """Use the same ONNX model, but cache it in a stable, configurable location."""

    def __init__(self) -> None:
        super().__init__()
        custom_root = Path(MempalaceConfig().embedding_cache_path)
        if custom_root.name == self.MODEL_NAME:
            self.DOWNLOAD_PATH = custom_root
        else:
            self.DOWNLOAD_PATH = custom_root / self.MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_function() -> MempalaceEmbeddingFunction:
    return MempalaceEmbeddingFunction()

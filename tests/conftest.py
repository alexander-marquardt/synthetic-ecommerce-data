from __future__ import annotations

import struct
from pathlib import Path

import pytest


@pytest.fixture
def png_size():
    """Width and height read out of the PNG's own IHDR chunk.

    Deliberately independent of the production helper and of the figure size:
    the question is what the file says, not what the renderer intended.
    """

    def _read(path: Path) -> tuple[int, int]:
        raw = Path(path).read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
        assert raw[12:16] == b"IHDR", f"{path} has no IHDR where one must be"
        return struct.unpack(">II", raw[16:24])

    return _read

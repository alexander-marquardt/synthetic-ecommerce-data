"""``scale.templates()`` computed once per worker (#1035): the stub of the red commit."""

from __future__ import annotations


def patched() -> bool:
    return False


def watch() -> None:
    return None


def memo(real):
    return real


def install() -> None:
    return None

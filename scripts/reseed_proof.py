"""Stub of #50's reseed proof (the red commit)."""

from __future__ import annotations

REBUILD: tuple[tuple[str, ...], ...] = ()


class ProofError(Exception):
    pass


def reseed(text: str, seed: int | None = None) -> tuple[str, int]:
    return text, 0


def red_tests(output: str) -> list[str]:
    return []

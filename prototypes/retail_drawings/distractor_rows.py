"""The distractors three failure classes need at catalog scale (gen#125): data only (stub)."""

from __future__ import annotations

from class_model import Style

STYLES: tuple[Style, ...] = ()


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [s.doc() for s in STYLES]

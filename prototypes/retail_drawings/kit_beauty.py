"""Beauty shapes for the retail drawing kit (gen#214): stub, drawn in the next commit."""

from __future__ import annotations

from kit import Fill, register


def _blank(paint: str, fill: Fill, label: str | None, **params: str) -> list[str]:
    return []


SHAPES = {name: _blank for name in (
    "mascara", "primer", "setting_spray", "serum", "face_mask", "eye_patches", "body_mist",
    "aftershave", "talc", "sun_cream",
)}  # fmt: skip
register(SHAPES)

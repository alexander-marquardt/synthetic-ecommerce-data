"""The picture manifest and its loader: the one bridge from the pictures to our products (gen#1022).

A manifest row is the spec one picture was drawn from, in the generator's own drawing vocabulary,
under an opaque image id. It has a closed schema: every field is one of :data:`FIELDS`, and every
value is an enum of the generator's, an integer count or a small rounded ratio. There is no
free-text field, so no title, description or other prose can pass through it. :func:`load` refuses
any other field or value with a ``ValueError`` that names it::

    {
      "image_id": "2b5d454ad52f6674",
      "type": "sideboard",
      "color": "Natural",
      "parts": {"doors": 3, "drawers": 3, "legs": "tapered"},
      "proportions": {"height_per_width": 0.5, "depth_per_width": 0.27}
    }

* ``image_id`` (required): lower-case hex, 12 to 64 digits. It is random, not derived from any
  other id, and it is only a hand-over key: no product, SKU or image file the writer makes keeps it.
* ``type`` (required): one of :data:`TYPES`, the kit shapes with a table of params.
* ``color`` (required): one of :data:`COLORS`, the generator's color words.
* ``parts``: the type's own params (``kit_home_furniture.PARAMS``,
  ``kit_storage_furniture.PARAMS``). A count (doors, drawers, shelves, tiers, stools) is an
  integer and any other part is one of the words its shape draws. A part left out is drawn as
  the shape's default.
* ``proportions``: ``height_per_width`` and ``depth_per_width``, each a number from 0.05 to 20
  with at most two decimals. A ratio left out is the type's nominal one (``drawings.PROPORTIONS``).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data.domains.retail import (
    dark_blues,
    kit_home_furniture,
    kit_storage_furniture,
)
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS

FIELDS: tuple[str, ...] = ("image_id", "type", "color", "parts", "proportions")
REQUIRED: tuple[str, ...] = ("image_id", "type", "color")
RATIOS: tuple[str, ...] = ("height_per_width", "depth_per_width")
#: The least and most a ratio may be, and its decimals: a proportion, never a measured value.
RATIO_RANGE: tuple[float, float] = (0.05, 20.0)
RATIO_DECIMALS = 2

#: Each type the manifest names, and the parts its shape draws with the values each takes.
TYPES: dict[str, dict[str, tuple[str, ...]]] = {
    **kit_home_furniture.PARAMS,
    **kit_storage_furniture.PARAMS,
}

#: The generator's color words a picture is filled with, and the hex each is drawn in: the six
#: main colors (gen#275) and the furniture tones (``furniture_rows``).
COLORS: dict[str, str] = {
    **MAIN_COLORS,
    "White": "#f2efe8",
    "Natural": "#c9a06a",
    "Dark Brown": "#5e3b25",
    "Tan": "#b07a43",
    "Grey": "#9a9ca0",
    "Navy": dark_blues.NAVY,
    "Pink": "#e3b2ad",
    "Gold": "#c9a24a",
    "Silver": "#b9bcc0",
}

_IMAGE_ID = re.compile(r"[0-9a-f]{12,64}")


@dataclass(frozen=True)
class Picture:
    """One manifest row, checked: what one picture shows, under its opaque image id."""

    image_id: str
    type: str
    color: str
    #: ``(part, value)`` pairs, each value as the shape's own string ("3", "tapered").
    parts: tuple[tuple[str, str], ...]
    #: ``(height_per_width, depth_per_width)``.
    proportions: tuple[float, float]

    def attributes(self, width: float | None = None) -> dict[str, Any]:
        """The attributes ``drawings.render`` draws this picture from: its fill, its parts and a
        size at its proportions, ``width`` inches wide (the type's nominal width by default)."""
        w = drawings.PROPORTIONS[self.type][1] if width is None else width
        rh, rd = self.proportions
        return {
            "color": COLORS[self.color],
            "width": w,
            "height": w * rh,
            "depth": w * rd,
            **dict(self.parts),
        }


def is_count(type_: str, part: str) -> bool:
    """Whether ``part`` of ``type_`` is a count (every value it takes is a number)."""
    return all(v.isdigit() for v in TYPES[type_][part])


def _nominal(type_: str) -> tuple[float, float]:
    _, w, h, d = drawings.PROPORTIONS[type_]
    return (round(h / w, RATIO_DECIMALS), round(d / w, RATIO_DECIMALS))


def _parts(where: str, type_: str, given: Any) -> tuple[tuple[str, str], ...]:
    if not isinstance(given, Mapping):
        raise ValueError(f"{where}: parts must be an object, not {given!r}")
    table = TYPES[type_]
    out: list[tuple[str, str]] = []
    for part, value in given.items():
        if part not in table:
            raise ValueError(f"{where}: {type_} has no part {part!r}; one of {tuple(table)}")
        if is_count(type_, part):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{where}: {part} is a count, an integer, not {value!r}")
            value = str(value)
        elif not isinstance(value, str):
            raise ValueError(f"{where}: {part} is one of {table[part]}, not {value!r}")
        if value not in table[part]:
            raise ValueError(f"{where}: {part} {value!r} is not drawn; one of {table[part]}")
        out.append((part, value))
    return tuple(sorted(out))


def _proportions(where: str, type_: str, given: Any) -> tuple[float, float]:
    if not isinstance(given, Mapping):
        raise ValueError(f"{where}: proportions must be an object, not {given!r}")
    unknown = sorted(set(given) - set(RATIOS))
    if unknown:
        raise ValueError(f"{where}: no proportion {unknown[0]!r}; one of {RATIOS}")
    out = dict(zip(RATIOS, _nominal(type_), strict=True))
    lo, hi = RATIO_RANGE
    for key, value in given.items():
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"{where}: {key} must be a number, not {value!r}")
        if not lo <= value <= hi or round(value, RATIO_DECIMALS) != value:
            raise ValueError(
                f"{where}: {key} {value!r} is not a ratio from {lo} to {hi} "
                f"with at most {RATIO_DECIMALS} decimals"
            )
        out[key] = float(value)
    return (out["height_per_width"], out["depth_per_width"])


def check(row: Any, where: str = "row") -> Picture:
    """One manifest row as a :class:`Picture`; a field or value outside the schema raises
    ``ValueError`` naming it."""
    if not isinstance(row, Mapping):
        raise ValueError(f"{where}: a manifest row is an object, not {type(row).__name__}")
    unknown = sorted(str(k) for k in row if k not in FIELDS)
    if unknown:
        raise ValueError(f"{where}: no field {unknown[0]!r}; the manifest's fields are {FIELDS}")
    missing = [k for k in REQUIRED if k not in row]
    if missing:
        raise ValueError(f"{where}: missing {missing[0]!r}")
    image_id, type_, color = row["image_id"], row["type"], row["color"]
    if not isinstance(image_id, str) or not _IMAGE_ID.fullmatch(image_id):
        raise ValueError(f"{where}: image_id must be 12 to 64 lower-case hex digits")
    if type_ not in TYPES:
        raise ValueError(f"{where}: unknown type {type_!r}; one of {tuple(TYPES)}")
    if color not in COLORS:
        raise ValueError(f"{where}: unknown color {color!r}; one of {tuple(COLORS)}")
    return Picture(
        image_id=image_id,
        type=type_,
        color=color,
        parts=_parts(where, type_, row.get("parts", {})),
        proportions=_proportions(where, type_, row.get("proportions", {})),
    )


def load(rows: Iterable[Any]) -> list[Picture]:
    """Stub: checks nothing yet."""
    return []


def load_file(path: str | Path) -> list[Picture]:
    """Stub: reads nothing yet."""
    return []

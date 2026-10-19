"""The digests that hold a re-expressed figure to its old bytes (#74).

A figure that moves onto the shared primitives must draw the same SVG for the
same record. ``pin_digests()`` draws, for each type below, every SKU of the
small catalog plus five variants of the first SKU's record: its length set
past the type's extent (a broken screw), the same with the thread run the whole
length, the optional attributes removed (a partial read), every inch value
unreadable, and an empty record. A record the figure refuses is pinned as the
refusal's class name. It returns one
sha256 per type over all of those drawings' bytes.

The pinned values in ``tests/test_drawing_primitives_74.py`` were taken from
main before the first figure moved. Print the current ones with
``uv run python -c "from drawing_pins import pin_digests; print(pin_digests())"`` from ``tests/``.
"""

from __future__ import annotations

import hashlib

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.drawing import draw_sku
from synthetic_ecommerce_data.domains.industrial.generate import generate

#: The figures this issue moves onto the primitives, and the ones that share a helper
#: with them.
PINNED_TYPES = (
    "end_mill_square",
    "end_mill_ball",
    "drill_jobber",
    "tap_spiral_point",
    "screw_flat_head",
    "screw_button_head",
    "screw_low_head",
    "bolt_hex",
    "washer_flat",
    "nut_hex",
)

#: Attributes a figure falls back from when they are absent.
OPTIONAL = (
    "Head Dia.",
    "Head Height",
    "Thread Length",
    "Overall Length",
    "Flute Length",
    "Length of Cut",
    "Shank Dia.",
    "Height",
    "Width Across Flats",
    "Point Angle",
    "Helix Angle",
    "Number of Flutes",
)


def variants(record: dict[str, str]) -> list[dict[str, str]]:
    long = {k: ('14-5/8"' if k == "Length" else v) for k, v in record.items()}
    threaded = {
        k: ('14-5/8"' if k in ("Length", "Thread Length") else v) for k, v in record.items()
    }
    return [
        long,
        threaded,
        {k: v for k, v in record.items() if k not in OPTIONAL},
        {k: ("n/a" if v.endswith('"') else v) for k, v in record.items()},
        {},
    ]


def pin_digests() -> dict[str, str]:
    catalog = generate(SMALL)
    records: dict[str, list[dict[str, str]]] = {t: [] for t in PINNED_TYPES}
    brands: dict[str, str] = {}
    for line in catalog.lines:
        if line.type_key in records:
            brands.setdefault(line.type_key, line.brand)
            records[line.type_key].extend(
                emit.drawing_record(catalog, line, child) for child in line.children
            )
    digests = {}
    for key in PINNED_TYPES:
        digest = hashlib.sha256()
        drawn = [*records[key], *variants(records[key][0])]
        for record in drawn:
            try:
                data, source = draw_sku(key, brands[key], record)
            except Exception as exc:  # noqa: BLE001  (a refusal is part of the pinned behaviour)
                data, source = type(exc).__name__.encode(), "refused"
            digest.update(data + source.encode())
        digests[key] = f"{len(drawn)}:{digest.hexdigest()}"
    return digests

"""Breadth shapes drawn from found SVG files (#102).

A hard-to-draw shape (a clamp, a hook, a bucket) is cheaper to find than to draw. A found file is
used only after ``scripts/normalise_found_svg.py`` has reduced it to ``<path class="part|plain">``
polygons in ``data/found_svg/`` and ``MANIFEST.csv`` there names its source and licence
(``tests/test_found_svg_102.py`` pins both). This module reads such a file back into a
:class:`..Figure`, so the colour, the hatch and the sheet come from the same pipeline every other
drawing uses: ``part`` is the product's body and ``plain`` a secondary surface.

Like the six shapes in :mod:`.breadth_shapes`, a found shape ignores the record: the geometry is
fixed, and only the record's material and finish paint it.
"""

from __future__ import annotations

import functools
import re
import xml.etree.ElementTree as ET
from importlib import resources

from synthetic_ecommerce_data.core.drawing.model import Figure

_SVG = "{http://www.w3.org/2000/svg}"
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
ROLES = ("part", "plain")
Parsed = tuple[float, float, tuple[tuple[str, tuple[tuple[float, float], ...]], ...]]


@functools.cache
def _parsed(name: str) -> Parsed:
    """``(width, height, ((role, points), ...))`` of ``found_svg/<name>.svg``, in file units."""
    text = (
        resources.files("synthetic_ecommerce_data.domains.industrial.data")
        .joinpath("found_svg", f"{name}.svg")
        .read_text(encoding="utf-8")
    )
    root = ET.fromstring(text)
    width, height = (float(v) for v in root.get("viewBox", "").split()[2:4])
    shapes = []
    for path in root.iter(_SVG + "path"):
        role = path.get("class", "")
        if role not in ROLES:
            raise ValueError(f"found shape {name!r} has a path of role {role!r}")
        numbers = [float(n) for n in _NUMBER.findall(path.get("d", ""))]
        shapes.append((role, tuple(zip(numbers[::2], numbers[1::2], strict=True))))
    return width, height, tuple(shapes)


def extent(name: str, longest_in: float) -> tuple[float, float]:
    """The drawn ``(width, height)`` in inches when the longer side is ``longest_in``."""
    width, height, _ = _parsed(name)
    k = longest_in / max(width, height)
    return width * k, height * k


def load(name: str, longest_in: float) -> Figure:
    """The found shape ``name`` as a figure whose longer side is ``longest_in`` inches."""
    width, height, shapes = _parsed(name)
    k = longest_in / max(width, height)
    fig = Figure(size_in=longest_in)
    for role, points in shapes:
        fig.poly(((x * k, y * k) for x, y in points), role)
    return fig

"""What every product drawing shares whatever its brand, and what tells two products apart (#849).

THE ONE PAPER. Every drawing, industrial and retail, sits on :data:`PAPER` with no texture
behind the figure. A brand's tinted paper read as a search signal at a demo (a green sheet
looks like a different kind of product from a blue one), so the brand is shown by its mark,
wordmark, frame and outline hand only. The paper is pure white (the maintainer's ruling on
#860): a white part or colorway reads by its outline, as it does on a shop's own pages.

ONE ANGLE PER PRODUCT. Two products of one type from two brands drew the same figure, and
looked like one product that should have been grouped. A product's figure is turned by
:func:`angle_of` its product id, over the angles its type's :data:`ORIENTATIONS` entry
allows: every SKU of the product shares it, and two products of one type differ in it
unless their ids land on the same angle of the set (one pair in 24 for a type drawn at
``any`` angle, one in seven for ``upright`` and ``slight``; every product of a ``level`` type
is drawn at 0). The angle is a hash of the id, never a rank in
the catalog, so adding a product moves no other product's drawing. A drawing scales its
figure by its product's angle (:func:`turned`), so the turned figure and its dimension
lines stay inside the frame.

FOUR ORIENTATIONS. Every type names one (the industrial table in
``domains/industrial/orientation.py``, the retail one, by drawn shape, in
``domains/retail/orientation.py``):

* ``any``: the 24 clock positions, the hours and the half hours, for a part with no natural
  up (a screw, a nut, a washer, bar stock, a glove);
* ``upright``: within +-36 degrees in 12 degree steps, for a product that looks wrong upside
  down (a sink, a bottle, a vise, a sofa), and for any type nobody was sure of;
* ``slight``: within +-15 degrees in 5 degree steps, for clothing and footwear, where even
  +-36 degrees reads as a garment falling over;
* ``level``: 0 degrees only, for a set or kit drawn as several items (#884).

A PACK IS LEVEL. A product any SKU of which is a pack of several items (a cup set in 2, 4
and 8 packs, a card of end mills) is drawn level on every SKU, whatever its type's
orientation: a turned group of items sits on a slant and overlaps (#884). A single product
keeps its tilt (the maintainer, on #884: "singular products look OK tilted in general"). The
rule is per product, so its SKUs still share one angle; :func:`product_orientation` applies
it.
"""

from __future__ import annotations

import hashlib
import math

#: The paper every product drawing sits on.
PAPER = "#ffffff"

#: The angles a figure may be turned by, in degrees clockwise on screen (SVG's ``rotate``), per
#: orientation: ``any`` the 24 clock positions, ``upright`` the multiples of 12 within +-36,
#: ``slight`` the multiples of 5 within +-15, ``level`` none but 0.
ORIENTATIONS: dict[str, tuple[int, ...]] = {
    "any": tuple(range(0, 360, 15)),
    "upright": (-36, -24, -12, 0, 12, 24, 36),
    "slight": (-15, -10, -5, 0, 5, 10, 15),
    "level": (0,),
}

#: The ``any`` set, which the clock positions name.
ANGLES: tuple[int, ...] = ORIENTATIONS["any"]


def product_orientation(orientation: str, packed: bool) -> str:
    """The orientation a product is drawn at: its type's ``orientation``, or ``level`` when
    ``packed``, some SKU of it drawn as several items (#884)."""
    return "level" if packed else orientation


def angle_of(product_id: str, orientation: str) -> int:
    """The angle every SKU of product ``product_id`` is drawn at, one of its type's
    ``orientation`` set (a ``KeyError`` for a name not in :data:`ORIENTATIONS`)."""
    angles = ORIENTATIONS[orientation]
    digest = hashlib.sha256(product_id.encode("utf-8")).digest()
    return angles[int.from_bytes(digest[:8], "big") % len(angles)]


def turned(width: float, height: float, angle: float) -> tuple[float, float]:
    """The width and height of the box a ``width`` x ``height`` box covers turned by ``angle``."""
    a = math.radians(angle)
    c, s = abs(math.cos(a)), abs(math.sin(a))
    return width * c + height * s, width * s + height * c

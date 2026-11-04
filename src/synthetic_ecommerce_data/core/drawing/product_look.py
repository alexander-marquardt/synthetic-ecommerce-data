"""What every product drawing shares whatever its brand, and what tells two products apart (#849).

THE ONE PAPER. Every drawing, industrial and retail, sits on :data:`PAPER` with no texture
behind the figure. A brand's tinted paper read as a search signal at a demo (a green sheet
looks like a different kind of product from a blue one), so the brand is shown by its mark,
wordmark, frame and outline hand only. The tint is the book's first, the light neutral every
brand at paper index 0 already drew on: a hair off white, so a white part, a white colorway and
the magnifier's white lens still read against it.

ONE ANGLE PER PRODUCT. Two products of one type from two brands drew the same figure, and
looked like one product that should have been grouped. A product's figure is turned by
:func:`angle_of` its product id: every SKU of the product shares it, and two products differ
in it unless their ids land on the same one of the :data:`ANGLES` (one pair in seven). The
angle is a hash of the id, never a rank in the catalog, so adding a product moves no other
product's drawing. A drawing scales its figure by its product's angle (:func:`turned`), so the
turned figure and its dimension lines stay inside the frame.
"""

from __future__ import annotations

import hashlib
import math

#: The paper every product drawing sits on.
PAPER = "#f9f9f7"

#: The angles a figure is turned by, in degrees clockwise on screen (SVG's ``rotate``): the
#: multiples of 12 within +-36, so the nearest two are apart at the 180 px tile.
ANGLES: tuple[int, ...] = (-36, -24, -12, 0, 12, 24, 36)


def angle_of(product_id: str) -> int:
    """The angle every SKU of product ``product_id`` is drawn at."""
    digest = hashlib.sha256(product_id.encode("utf-8")).digest()
    return ANGLES[int.from_bytes(digest[:8], "big") % len(ANGLES)]


def turned(width: float, height: float, angle: float) -> tuple[float, float]:
    """The width and height of the box a ``width`` x ``height`` box covers turned by ``angle``."""
    a = math.radians(angle)
    c, s = abs(math.cos(a)), abs(math.sin(a))
    return width * c + height * s, width * s + height * c

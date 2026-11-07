"""The emblem each invented film prints on every product it sells (gen#904).

A film's products (:mod:`kids_films`) are drawn with their types' shapes, so nothing but the
emblem says that a mug and a sticker sheet belong to one film. Each film has one emblem, drawn
here in SVG paths: a round badge, a white disc in a dark ring with the film's picture in it. The
badge is printed on the product itself (:func:`on_product`, at the place :data:`PLACES` gives
its shape) and drawn the same on every product, so it scales and turns with the product but
never takes the product's color: The Blue Balloon's balloon is blue on a red mug too.

Each film product's brand panel also carries a licence line beside the maker's logo, as
licensed merchandise does: the emblem and "Licensed from <studio>" (:func:`licence`). Each
film's studio is invented and named after it (:data:`STUDIOS`).

The drawings are original (MIT, like the rest of the code): no copied art and nothing drawn
after a real film's logo. They are drawn in a unit box, -1 to 1 on each axis, y down.
"""

# ruff: noqa: E501 -- SVG literals read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.core.drawing import brand_type

#: The badge's ink: not the kit's ink, so a brand's restyle (``house_styles.restyle``) never
#: changes an emblem's line.
EMBLEM_INK = "#25303b"
#: The balloon's blue, on every Blue Balloon product whatever its color.
BALLOON_BLUE = "#2f6db5"
_DISC = '<circle cx="0" cy="0" r="1" fill="#ffffff" stroke="#25303b" stroke-width="0.09"/>'


def _ink(d: str, w: float = 0.06, fill: str = "none") -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{EMBLEM_INK}" stroke-width="{w:g}" stroke-linecap="round" stroke-linejoin="round"/>'


def _scared_face() -> str:
    """Home Without Anybody: a face with wide eyes, raised brows and an open mouth."""
    return "".join([
        '<circle cx="0" cy="0.04" r="0.7" fill="#f3cfa4" stroke="#25303b" stroke-width="0.06"/>',
        _ink("M-0.66,-0.12 C-0.62,-0.62 0.62,-0.62 0.66,-0.12 C0.5,-0.4 -0.5,-0.4 -0.66,-0.12 Z", 0.04, "#7a4a2a"),
        '<ellipse cx="-0.26" cy="-0.06" rx="0.16" ry="0.2" fill="#ffffff" stroke="#25303b" stroke-width="0.05"/>',
        '<ellipse cx="0.26" cy="-0.06" rx="0.16" ry="0.2" fill="#ffffff" stroke="#25303b" stroke-width="0.05"/>',
        '<circle cx="-0.26" cy="-0.04" r="0.06" fill="#25303b"/>',
        '<circle cx="0.26" cy="-0.04" r="0.06" fill="#25303b"/>',
        _ink("M-0.44,-0.36 Q-0.3,-0.48 -0.14,-0.38", 0.05),
        _ink("M0.14,-0.38 Q0.3,-0.48 0.44,-0.36", 0.05),
        '<ellipse cx="0" cy="0.36" rx="0.13" ry="0.18" fill="#7a2626" stroke="#25303b" stroke-width="0.05"/>',
        _ink("M0.56,-0.3 Q0.66,-0.12 0.6,-0.04 Q0.5,0.02 0.5,-0.1 Q0.5,-0.2 0.56,-0.3 Z", 0.03, "#8ec5ea"),
    ])  # fmt: skip


def _blue_balloon() -> str:
    """The Blue Balloon: one blue balloon on its string, in the badge's circle."""
    return "".join([
        _ink("M0,0.26 Q-0.14,0.44 0.02,0.58 Q0.16,0.72 0,0.86", 0.04),
        _ink("M0,-0.78 C0.36,-0.78 0.48,-0.46 0.46,-0.24 C0.44,0.02 0.2,0.2 0,0.24 C-0.2,0.2 -0.44,0.02 -0.46,-0.24 C-0.48,-0.46 -0.36,-0.78 0,-0.78 Z", 0.05, BALLOON_BLUE),
        _ink("M-0.07,0.32 L0.07,0.32 L0,0.23 Z", 0.03, BALLOON_BLUE),
        '<ellipse cx="-0.2" cy="-0.46" rx="0.08" ry="0.15" fill="#ffffff" opacity="0.8" transform="rotate(25 -0.2 -0.46)"/>',
    ])  # fmt: skip


def _ice_castle() -> str:
    """Really Cold: an ice castle of three pointed towers over a gate."""
    ice, edge = "#cfe8f7", 0.05
    return "".join([
        _ink("M-0.56,0.62 L-0.56,-0.06 L-0.32,-0.06 L-0.32,0.62 Z", edge, ice),
        _ink("M0.32,0.62 L0.32,-0.06 L0.56,-0.06 L0.56,0.62 Z", edge, ice),
        _ink("M-0.6,-0.06 L-0.44,-0.42 L-0.28,-0.06 Z", edge, "#9ccbec"),
        _ink("M0.28,-0.06 L0.44,-0.42 L0.6,-0.06 Z", edge, "#9ccbec"),
        _ink("M-0.2,0.62 L-0.2,-0.3 L0.2,-0.3 L0.2,0.62 Z", edge, ice),
        _ink("M-0.25,-0.3 L0,-0.82 L0.25,-0.3 Z", edge, "#9ccbec"),
        _ink("M-0.66,0.62 L0.66,0.62", edge),
        _ink("M-0.11,0.62 L-0.11,0.36 Q0,0.22 0.11,0.36 L0.11,0.62 Z", 0.04, "#5f97c4"),
        _ink("M-0.06,-0.08 L0.06,-0.08 L0.06,0.08 L-0.06,0.08 Z", 0.03, "#5f97c4"),
        _ink("M-0.44,0.1 L-0.44,0.24 M0.44,0.1 L0.44,0.24", 0.06),
    ])  # fmt: skip


def _duck() -> str:
    """Duck Run: a yellow duck running to the right, legs mid-stride."""
    return "".join([
        _ink("M-0.18,0.36 L-0.3,0.66 L-0.42,0.66 M0.1,0.36 L0.26,0.62 L0.38,0.58", 0.06),
        _ink("M-0.66,0.0 Q-0.72,-0.2 -0.54,-0.2 Q-0.3,-0.12 -0.1,-0.06 L0.12,-0.12 Q0.42,0.0 0.38,0.24 Q0.3,0.44 -0.02,0.44 Q-0.44,0.42 -0.66,0.0 Z", 0.05, "#f4c430"),
        '<circle cx="0.3" cy="-0.36" r="0.26" fill="#f4c430" stroke="#25303b" stroke-width="0.05"/>',
        _ink("M0.52,-0.4 L0.82,-0.32 L0.52,-0.24 Z", 0.04, "#e8822a"),
        '<circle cx="0.36" cy="-0.42" r="0.05" fill="#25303b"/>',
        _ink("M-0.36,0.08 Q-0.08,-0.02 0.08,0.16 Q-0.14,0.26 -0.36,0.08 Z", 0.04, "#e5b020"),
    ])  # fmt: skip


def _toy_cowboy() -> str:
    """Plaything Story: a toy cowboy's head, his hat and his red neckerchief."""
    return "".join([
        _ink("M-0.3,0.42 L0.3,0.42 L0,0.74 Z", 0.05, "#c8312e"),
        '<circle cx="0" cy="0.08" r="0.38" fill="#f3cfa4" stroke="#25303b" stroke-width="0.05"/>',
        _ink("M-0.8,-0.2 Q0,0.02 0.8,-0.2 Q0.6,-0.08 0,-0.06 Q-0.6,-0.08 -0.8,-0.2 Z", 0.05, "#9a6232"),
        _ink("M-0.36,-0.16 L-0.3,-0.62 Q-0.16,-0.72 0,-0.6 Q0.16,-0.72 0.3,-0.62 L0.36,-0.16 Z", 0.05, "#9a6232"),
        _ink("M-0.34,-0.26 Q0,-0.18 0.34,-0.26", 0.05),
        '<circle cx="-0.13" cy="0.06" r="0.045" fill="#25303b"/>',
        '<circle cx="0.13" cy="0.06" r="0.045" fill="#25303b"/>',
        _ink("M-0.14,0.22 Q0,0.32 0.14,0.22", 0.045),
    ])  # fmt: skip


def _lantern() -> str:
    """Lovely and the Beast: a lit lantern with a ring to carry it by."""
    return "".join([
        '<circle cx="0" cy="-0.72" r="0.1" fill="none" stroke="#25303b" stroke-width="0.05"/>',
        _ink("M-0.3,-0.44 L0,-0.62 L0.3,-0.44 Z", 0.05, "#3c3c4a"),
        _ink("M-0.3,-0.44 L-0.3,0.46 L0.3,0.46 L0.3,-0.44 Z", 0.05, "#fbe39a"),
        '<ellipse cx="0" cy="0.04" rx="0.11" ry="0.2" fill="#f29a2e"/>',
        '<ellipse cx="0" cy="0.1" rx="0.05" ry="0.1" fill="#fff4c8"/>',
        _ink("M0,-0.44 L0,-0.2 M0,0.28 L0,0.46", 0.04),
        _ink("M-0.4,0.46 L0.4,0.46 L0.32,0.62 L-0.32,0.62 Z", 0.05, "#3c3c4a"),
    ])  # fmt: skip


def _small_crown() -> str:
    """Little Tiny Queen: a small gold crown of five points with three jewels."""
    return "".join([
        _ink("M-0.6,0.36 L-0.66,-0.34 L-0.34,-0.04 L-0.18,-0.52 L0,-0.12 L0.18,-0.52 L0.34,-0.04 L0.66,-0.34 L0.6,0.36 Z", 0.05, "#f2c230"),
        _ink("M-0.62,0.36 L0.62,0.36 L0.62,0.54 L-0.62,0.54 Z", 0.05, "#e0a91c"),
        '<circle cx="-0.32" cy="0.18" r="0.08" fill="#c8312e"/>',
        '<circle cx="0" cy="0.16" r="0.09" fill="#2f6db5"/>',
        '<circle cx="0.32" cy="0.18" r="0.08" fill="#3c8d4f"/>',
        '<circle cx="-0.66" cy="-0.38" r="0.06" fill="#f2c230" stroke="#25303b" stroke-width="0.03"/>',
        '<circle cx="0" cy="-0.16" r="0.06" fill="#f2c230" stroke="#25303b" stroke-width="0.03"/>',
        '<circle cx="0.66" cy="-0.38" r="0.06" fill="#f2c230" stroke="#25303b" stroke-width="0.03"/>',
    ])  # fmt: skip


#: Each film's picture, inside its badge.
_PICTURES = {
    "Plaything Story": _toy_cowboy,
    "Lovely and the Beast": _lantern,
    "Duck Run": _duck,
    "Really Cold": _ice_castle,
    "Little Tiny Queen": _small_crown,
    "Home Without Anybody": _scared_face,
    "The Blue Balloon": _blue_balloon,
}

#: Each film's invented studio, named after it: what its licence line names.
STUDIOS: dict[str, str] = {
    "Plaything Story": "Plaything Story Studios",
    "Lovely and the Beast": "Lovely and the Beast Studios",
    "Duck Run": "Duck Run Studios",
    "Really Cold": "Really Cold Studios",
    "Little Tiny Queen": "Little Tiny Queen Studios",
    "Home Without Anybody": "Home Without Anybody Studios",
    "The Blue Balloon": "Blue Balloon Studios",
}

#: Where a shape prints the emblem, in the kit's 400-unit sheet: the badge's center and radius.
#: A label, a pocket or a printed panel the shape draws stays where it is; the badge sits on
#: the product's widest plain surface.
PLACES: dict[str, tuple[float, float, float]] = {
    "mug": (180, 232, 54),
    "tshirt": (200, 188, 50),
    "sweatshirt": (200, 196, 48),
    "pyjamas": (100, 182, 30),
    "box": (180, 288, 44),
    "duvet": (186, 196, 64),
    "sticker_sheet": (250, 282, 30),
    "party_cup": (200, 220, 50),
    "gift_bag": (190, 186, 30),
    "cat": (200, 284, 34),
    "dinosaur": (192, 250, 26),
    "bird": (280, 248, 28),
    "cake": (194, 202, 32),
    "bag": (200, 206, 42),
}


def badge(film: str) -> str:
    """The film's emblem in the unit box: the same SVG on every product of the film."""
    return f'<g class="emblem">{_DISC}{_PICTURES[film]()}</g>'


def _at(film: str, x: float, y: float, r: float) -> str:
    return f'<g transform="translate({x:g} {y:g}) scale({r:g})">{badge(film)}</g>'


def on_product(film: str, shape: str) -> str:
    """The emblem printed on a product of ``shape``, in the kit's sheet; a shape no film sells
    has no place, and raises ``KeyError``."""
    return _at(film, *PLACES[shape])


@dataclass(frozen=True)
class _LineType:
    """The licence line's type: the brand's family, regular weight, as written."""

    font: str
    weight: int = 400
    case: str = "title"
    spacing: float = 0.0
    italic: bool = False


#: The licence line's font size, the emblem's radius beside it and the gap between them, in
#: the 400-unit sheet; :data:`LICENCE_HEIGHT` is the band the line takes from the product.
LICENCE_SIZE = 11.0
LICENCE_BADGE = 9.0
LICENCE_GAP = 5.0
LICENCE_HEIGHT = 2 * LICENCE_BADGE + 6


def licence_text(film: str) -> str:
    """The words of the film's licence line."""
    return f"Licensed from {STUDIOS[film]}"


def licence(font: str, ink: str, film: str, center_y: float, sheet: float = 400) -> list[str]:
    """The licence line, centered across the sheet on ``center_y``: the film's emblem, then
    "Licensed from <studio>" in the brand's ``font`` family and ``ink``."""
    kind = _LineType(font)
    words = licence_text(film)
    w = brand_type.width(kind, words, LICENCE_SIZE)
    x0 = (sheet - (2 * LICENCE_BADGE + LICENCE_GAP + w)) / 2
    base = center_y + brand_type.cap_height(kind) * LICENCE_SIZE / 2
    text = brand_type.text(
        kind, words, x0 + 2 * LICENCE_BADGE + LICENCE_GAP, base, LICENCE_SIZE, ink
    )
    return [_at(film, x0 + LICENCE_BADGE, center_y, LICENCE_BADGE), text]


def licence_band(
    top: float, bottom: float, sheet: float = 400
) -> tuple[float, tuple[float, float]]:
    """Where the licence line goes beside a logo whose text reaches ``top`` down from the
    sheet's top and ``bottom`` up from its foot (``house_styles.reach``): its center, on the
    product's side of the logo's text, and the reach (top, bottom) it adds to the logo's, which
    the product is drawn clear of."""
    if top >= bottom:
        return top + 2 + LICENCE_HEIGHT / 2, (LICENCE_HEIGHT + 2, 0.0)
    return sheet - bottom - 2 - LICENCE_HEIGHT / 2, (0.0, LICENCE_HEIGHT + 2)

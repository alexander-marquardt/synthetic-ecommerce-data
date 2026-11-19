"""The public draw call: one product drawing from its type and attributes, in a finish (gen#1022).

A loader outside the generator (elastic/prism-wands#1) draws a product with one call, without
importing the generator's internals::

    from synthetic_ecommerce_data import drawings

    svg = drawings.render(
        "sideboard",
        {"color": "#8a5a3a", "width": 72, "height": 32, "doors": "3", "drawers": "3"},
        "unbranded",
        product_id="any-stable-id",
    )

ONE FIGURE, TWO FINISHES. The figure is drawn from the attributes alone (:func:`figure`): the
type's shape, its params, the color as its fill, and its proportions. The finish only dresses it:

* ``unbranded`` is keyed only by ``product_id`` (:func:`unbranded_look`): the angle the figure is
  turned by (``product_look.angle_of``, as every drawing is), one of the five frame treatments,
  the frame's margin, the line weight, the dash, and a grey frame accent. No mark, no wordmark,
  no text of any kind, and no tinted accent: a tinted sheet once read as a search signal (#849).
* ``brand`` is the brand's house style as the generator's own products draw it
  (:data:`...house_styles.HOUSE_STYLES`): mark, wordmark, frame, ink and outline hand, plus
  the same angle.

THE ATTRIBUTES are a closed vocabulary; any other key or value is refused with a ``ValueError``
naming it:

* ``color``: the fill, ``#rrggbb`` (the caller maps its own color words to it);
* ``width``, ``height``, ``depth``: the piece's size in inches, for a type in
  :data:`PROPORTIONS`. A type seen from the front draws its width against its height, one seen
  from above (a rug) its width against its depth. A dimension left out is the type's nominal
  one, and a type with no entry refuses a dimension;
* the type's own params (a sideboard's ``doors``, ``drawers`` and ``legs``), each one of the
  values its kit shape draws.

:func:`picture_share` measures how many products of a set share a picture, for the figure
alone and in each finish (``scripts/picture_share_1022.py`` prints it).
"""

from __future__ import annotations

import hashlib
import inspect
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from synthetic_ecommerce_data.core.drawing import product_look
from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail import kit, orientation

FINISHES: tuple[str, ...] = ("unbranded", "brand")
DIMENSIONS: tuple[str, ...] = ("width", "height", "depth")

#: Type -> (view, nominal width, height, depth in inches): the size its kit shape is drawn at.
#: ``front`` draws width against height, ``top`` width against depth.
PROPORTIONS: dict[str, tuple[str, float, float, float]] = {
    "sideboard": ("front", 60, 32, 18),
    "bar_cabinet": ("front", 36, 60, 18),
    "storage_cabinet": ("front", 30, 66, 16),
    "shoe_storage": ("front", 32, 22, 12),
    "wall_shelf": ("front", 24, 16, 8),
    "tile": ("front", 12, 12, 0.4),
    "vanity": ("front", 36, 34, 21),
    "cabinet_pull": ("front", 5, 1.25, 1.25),
    "sink_faucet": ("front", 6, 10, 5),
    "bath_storage": ("front", 24, 60, 9),
    "canister": ("front", 16, 9, 5),
    "bar_stool": ("front", 17, 41, 17),
    "desk": ("front", 48, 30, 24),
    "office_chair": ("front", 26, 42, 26),
    "tv_stand": ("front", 60, 22, 16),
    "kitchen_island": ("front", 48, 36, 30),
    "bookcase": ("front", 32, 72, 12),
    "wardrobe": ("front", 40, 72, 22),
    "chest_of_drawers": ("front", 32, 44, 18),
    "sofa": ("front", 80, 34, 36),
    "rug": ("top", 96, 0.5, 60),
    "vanity_light": ("front", 24, 9, 7),
    "bench": ("front", 48, 18, 16),
}

#: The least a figure is squeezed along one axis, so a very long piece still reads as itself.
LEAST = 0.4

#: The unbranded finish's choices, each picked by the product id.
UNBRANDED_FRAMES: tuple[str, ...] = ("thin", "double", "rounded", "heavy", "ticks")
UNBRANDED_MARGINS: tuple[float, ...] = (1.0, 0.985, 0.97, 0.955)
UNBRANDED_STROKES: tuple[float, ...] = (0.8, 1.0, 1.2)
UNBRANDED_ACCENTS: tuple[str, ...] = ("#666666", "#7d7d7d", "#9a9a9a", "#b4b4b4")

_HEX = re.compile(r"#[0-9a-fA-F]{6}")
_FIRST_PARAMS = 3  # every kit shape takes (paint, fill, label) before its own params


@dataclass(frozen=True)
class UnbrandedLook:
    """What the ``unbranded`` finish draws for one product id."""

    frame: str
    margin: float
    stroke: float
    dashed: bool
    accent: str


def unbranded_look(product_id: str) -> UnbrandedLook:
    """The unbranded finish of ``product_id``: each choice from its own bytes of a hash of the
    id, so it is the same on every call and every machine, and adding a product moves no other."""
    d = hashlib.sha256(f"unbranded:{product_id}".encode()).digest()
    return UnbrandedLook(
        frame=UNBRANDED_FRAMES[d[0] % len(UNBRANDED_FRAMES)],
        margin=UNBRANDED_MARGINS[d[1] % len(UNBRANDED_MARGINS)],
        stroke=UNBRANDED_STROKES[d[2] % len(UNBRANDED_STROKES)],
        dashed=bool(d[3] % 2),
        accent=UNBRANDED_ACCENTS[d[4] % len(UNBRANDED_ACCENTS)],
    )


def _unbranded_style(look: UnbrandedLook) -> hs.HouseStyle:
    """A house style that draws no mark and no text: the frame, accent and outline hand only."""
    return hs.HouseStyle(
        frame=look.frame,
        color=look.accent,
        ink=hs.DEFAULT_INK,
        stroke=look.stroke,
        dashed=look.dashed,
        joins="round",
        mark=hs.NO_MARK,
        layout="mark_only",
        place="top_left",
        tag="plain",
        font=next(iter(hs.brand_type.FAMILIES)),
        weight=400,
        case="title",
        spacing=0.0,
    )


def _draw_of(type_: str):
    try:
        return kit._draw(type_)
    except KeyError:
        raise ValueError(f"unknown type {type_!r}: no kit shape draws it") from None


def _stretch(type_: str, dims: Mapping[str, float]) -> tuple[float, float]:
    """The (x, y) scale that draws ``type_`` at ``dims``' proportions, the larger at full size."""
    if not dims:
        return (1.0, 1.0)
    if type_ not in PROPORTIONS:
        raise ValueError(
            f"type {type_!r} has no proportions: it takes no {', '.join(sorted(dims))}"
        )
    view, w, h, d = PROPORTIONS[type_]
    rx = dims.get("width", w) / w
    ry = dims.get("depth", d) / d if view == "top" else dims.get("height", h) / h
    k = max(rx, ry)
    return (round(max(rx / k, LEAST), 4), round(max(ry / k, LEAST), 4))


def _split(
    type_: str, attributes: Mapping[str, Any]
) -> tuple[kit.Fill, dict[str, float], dict[str, str]]:
    """The fill, the dimensions and the shape's params ``attributes`` state, each checked."""
    draw = _draw_of(type_)
    own = list(inspect.signature(draw).parameters)[_FIRST_PARAMS:]
    color = attributes.get("color")
    if not isinstance(color, str) or not _HEX.fullmatch(color):
        raise ValueError(f"color must be #rrggbb, not {color!r}")
    dims: dict[str, float] = {}
    params: dict[str, str] = {}
    for key, value in attributes.items():
        if key == "color":
            continue
        if key in DIMENSIONS:
            if isinstance(value, bool) or not isinstance(value, int | float) or not value > 0:
                raise ValueError(f"{key} must be a positive number of inches, not {value!r}")
            dims[key] = float(value)
        elif key in own:
            params[key] = str(value)
        else:
            raise ValueError(
                f"{type_} takes no attribute {key!r}; "
                f"one of color, {', '.join((*DIMENSIONS, *own))}"
            )
    return kit.Fill("solid", color), dims, params


def _uid(product_id: str) -> str:
    return "p" + hashlib.sha256(product_id.encode()).hexdigest()[:10]


def figure(type_: str, attributes: Mapping[str, Any]) -> str:
    """The figure alone, as the ``<g class="figure">`` both finishes draw: the shape, its params,
    the color as its fill and its proportions, with no sheet, frame, angle or finish."""
    fill, dims, params = _split(type_, attributes)
    pid = "fill-figure"
    defs = kit.pattern_defs(fill, pid)
    draw = kit.figure_at(_draw_of(type_), _stretch(type_, dims), defs)
    return "".join(kit._drawn(draw, kit._paint(fill, pid), fill, None, params))


def render(
    type_: str,
    attributes: Mapping[str, Any],
    finish: str = "unbranded",
    *,
    product_id: str,
    brand: str | None = None,
) -> str:
    """One product drawing as a standalone SVG: ``type_``'s figure from ``attributes``, turned by
    ``product_id``'s angle and dressed in ``finish`` (``brand`` names the house style a ``brand``
    finish draws). A value outside the vocabulary raises ``ValueError`` naming it."""
    if finish not in FINISHES:
        raise ValueError(f"unknown finish {finish!r}; one of {FINISHES}")
    fill, dims, params = _split(type_, attributes)
    angle = product_look.angle_of(product_id, orientation.of(type_))
    common = {
        "uid": _uid(product_id),
        "params": params or None,
        "angle": angle,
        "stretch": _stretch(type_, dims),
    }
    if finish == "brand":
        if brand not in hs.HOUSE_STYLES:
            raise ValueError(f"the brand finish needs a brand with a house style, not {brand!r}")
        return kit.render(type_, fill, brand=brand, style=hs.HOUSE_STYLES[brand], **common)
    look = unbranded_look(product_id)
    svg = kit.render(type_, fill, brand="", style=_unbranded_style(look), **common)
    inset = (
        ""
        if look.margin == 1.0
        else f' transform="translate(200 200) scale({look.margin}) translate(-200 -200)"'
    )
    assert svg.count('<g class="brand">') == 1, "the house style's overlay is where the frame sits"
    return svg.replace('<g class="brand">', f'<g class="frame"{inset}>')


def picture_share(rows: Iterable[Mapping[str, Any]]) -> dict[str, tuple[int, int]]:
    """How many products of ``rows`` share their picture with another, of how many: for the
    figure alone and in each finish. A row is ``{"product_id", "type", "attributes", "brand"}``."""
    rows = list(rows)
    pictures: dict[str, list[str]] = {"figure": [], **{f: [] for f in FINISHES}}
    for r in rows:
        pictures["figure"].append(figure(r["type"], r["attributes"]))
        for f in FINISHES:
            pictures[f].append(
                render(
                    r["type"], r["attributes"], f, product_id=r["product_id"], brand=r.get("brand")
                )
            )
    out: dict[str, tuple[int, int]] = {}
    for name, svgs in pictures.items():
        counts = Counter(svgs)
        out[name] = (sum(1 for s in svgs if counts[s] > 1), len(svgs))
    return out

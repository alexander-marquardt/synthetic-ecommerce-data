"""Vanity lights and benches, variants of the wall light and dining bench (gen#1022, slice 7).

WANDS sells vanity lighting and benches, and the kit already draws their nearest kin: the wall
light (:mod:`kit_lighting`) and the dining-chair bench (:mod:`kit_furniture`). Each variant here is
a type of its own, built from those parts, because ``drawings.PROPORTIONS`` holds one row per
type: a vanity bar is wide where a sconce is tall, and a bench is wide where a chair is tall, so
neither fits its kin's row. (Kitchen mats, doormats and kids' rugs fit the rug's row: they are new
values of ``rug`` in :mod:`kit_softfurn`.)

============  ==============================================  ==================================
shape         draws                                           params
============  ==============================================  ==================================
vanity_light  a bar of ``lights`` shades on a wall plate      lights, shade, aim, finish
              over the top of a mirror, the shades a cone,
              a drum or a globe, aimed up or down
bench         the dining bench's padded seat (or a wooden     back, seat, storage
              slab) on four legs, with or without a back,
              over nothing, a shelf of baskets or two drawers
============  ==============================================  ==================================

:data:`PARAMS` is each shape's table of params and the values it draws; any other value is refused
with a ``ValueError`` naming the param. The record's color fills the shades and the bench; the
plate and arms are drawn in the light's ``finish``, and the mirror stays light, so a White piece
reads white (gen#226). ``drawings.render`` draws both in a finish; no generator product uses them
yet.
"""

# ruff: noqa: E501 -- param tables and SVG path literals read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW,
    LW_DETAIL,
    Fill,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_furniture import (
    BENCH_SEAT,
    GLASS,
    _drawer_fronts,
    _grain,
    _legs,
    _rect,
)
from synthetic_ecommerce_data.domains.retail.kit_home_furniture import _group
from synthetic_ecommerce_data.domains.retail.kit_lighting import (
    FINISHES,
    _circle,
    _drum,
    _plate,
    _rod,
    finish_color,
)

#: Each shape's params and the values it draws, in the order a picker would list them.
PARAMS: dict[str, dict[str, tuple[str, ...]]] = {
    "vanity_light": {"lights": ("1", "2", "3", "4", "5"), "shade": ("cone", "drum", "globe"), "aim": ("up", "down"), "finish": tuple(FINISHES)},
    "bench": {"back": ("no", "yes"), "seat": ("upholstered", "wood"), "storage": ("none", "shelf", "drawers")},
}  # fmt: skip
#: The drawers a bench with ``storage="drawers"`` draws under its seat.
BENCH_DRAWERS = 2
#: The woven baskets a bench's shelf holds.
WICKER = "#c8a06a"
#: Where a vanity light's plate sits, and the step between its shades.
BAR_Y = 170
STEP = 68


def _valid(kind: str, /, **given: str) -> None:
    """Refuse a value the shape does not draw, naming the param."""
    for key, value in given.items():
        if value not in PARAMS[kind][key]:
            raise ValueError(f"unknown {kind} {key} {value!r}; one of {PARAMS[kind][key]}")


def _shade_at(x: float, shade: str, up: bool, paint: str, metal: str) -> list[str]:
    """One shade on its arm from the plate at ``x``: its neck 30 units off the plate, its mouth
    60 further on, above the plate when it is aimed ``up``."""
    sign = -1 if up else 1
    neck, mouth = BAR_Y + sign * 30, BAR_Y + sign * 90
    top, bottom = min(neck, mouth), max(neck, mouth)
    out = _rod(f"M{x:.1f},{BAR_Y} L{x:.1f},{neck}", metal, 5)
    if shade == "cone":
        out.append(
            _path(
                f"M{x - 10:.1f},{neck} L{x + 10:.1f},{neck} L{x + 30:.1f},{mouth} L{x - 30:.1f},{mouth} Z",
                paint,
            )
        )
    elif shade == "drum":
        out += _drum(x, top, 48, 48, bottom - top, paint)
    else:
        out += [
            _circle(x, (neck + mouth) / 2, 30, paint, LW),
            _line(
                f"M{x - 16:.1f},{(neck + mouth) / 2 - 8:.1f} Q{x - 14:.1f},{(neck + mouth) / 2 - 20:.1f} {x - 2:.1f},{(neck + mouth) / 2 - 24:.1f}",
                3,
                ' stroke-opacity=".6"',
                "#ffffff",
            ),
        ]
    out.append(_circle(x, mouth - sign * 6, 6, metal))
    return ['<g class="shade">', *out, "</g>"]


def vanity_light(
    paint: str,
    fill: Fill,
    label: str | None,
    lights: str = "3",
    shade: str = "cone",
    aim: str = "up",
    finish: str = "chrome",
) -> list[str]:
    """A vanity bar over the top of a bathroom mirror: ``lights`` shades (``class="shade"``) on
    arms from one wall plate, each a ``shade`` in the record's fill, aimed ``up`` or ``down``, the
    plate and arms in the ``finish``."""
    _valid("vanity_light", lights=lights, shade=shade, aim=aim, finish=finish)
    metal = finish_color(finish)
    n = int(lights)
    xs = [200 + (i - (n - 1) / 2) * STEP for i in range(n)]
    w = max(48, (n - 1) * STEP + 64)
    out = [
        _rect(96, 290, 208, 96, GLASS, LW, rx=4),
        _line("M120,312 L156,300 M120,336 L190,306", 2.4, ' stroke-opacity=".7"', "#ffffff"),
    ]
    out.append(_plate(200 - w / 2, BAR_Y - 8, w, 16, metal))
    for x in xs:
        out += _shade_at(x, shade, aim == "up", paint, metal)
    return out


def bench(
    paint: str,
    fill: Fill,
    label: str | None,
    back: str = "no",
    seat: str = "upholstered",
    storage: str = "none",
) -> list[str]:
    """A bench three-quarters front, the dining bench widened into a piece of its own: the bench's
    padded seat (``upholstered``) or a wooden slab (``wood``) on four legs, a slatted ``back``
    (``class="back"``), and under the seat nothing, a ``shelf`` (``class="shelf"``) or
    :data:`BENCH_DRAWERS` drawers (``class="drawer"``), all in the record's fill."""
    _valid("bench", back=back, seat=seat, storage=storage)
    rear = _shade(paint, 0.12)
    out: list[str] = []
    if back == "yes":
        slats = [_rect(x, 100, 10, 92, rear, LW_DETAIL) for x in (120, 170, 220, 270)]
        out += _group(
            "back",
            [
                _rect(66, 84, 12, 120, paint, LW_DETAIL),
                _rect(322, 84, 12, 120, paint, LW_DETAIL),
                *slats,
                _rect(60, 80, 280, 20, paint, LW_DETAIL, rx=3),
            ],
        )
    out += _legs([112, 288], 236, 316, rear, 10)
    if storage == "shelf":
        baskets = [
            p
            for x in (110, 210)
            for p in (
                _rect(x, 254, 80, 34, WICKER, LW_DETAIL, rx=4),
                _line(
                    f"M{x + 4},{265} L{x + 76},{265} M{x + 4},{277} L{x + 76},{277}",
                    1.2,
                    ' stroke-opacity=".5"',
                ),
            )
        ]
        out += _group("shelf", [_rect(92, 288, 216, 14, paint, LW_DETAIL, rx=2), *baskets])
    elif storage == "drawers":
        out.append(_rect(84, 244, 232, 62, rear, LW_DETAIL))
        out += _drawer_fronts(84, 244, 232, 62, BENCH_DRAWERS, paint, cols=BENCH_DRAWERS)
    out += _legs([86, 314], 236, 336, paint, 14)
    if seat == "upholstered":
        out += [
            _path(BENCH_SEAT, paint),
            _line("M60,226 L340,226", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
            _line("M76,204 Q200,192 324,204", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
        ]
    else:
        out += [
            _rect(50, 200, 300, 22, paint, LW, rx=3),
            _rect(54, 222, 292, 14, rear, LW_DETAIL),
            _grain(50, 200, 300, 22, paint),
        ]
    return out


register({"vanity_light": vanity_light, "bench": bench})

"""Own-kind shapes for the home furniture the kit could not draw (gen#1022, slice 1).

Bar stools, desks, office chairs, TV stands and kitchen islands, each a flat front drawing in the
kit's house style with the record's fill (its finish: a wood tone, a paint, a fabric) on the main
surface. Each is drawn from the attributes a record states: the variant axis that changes how the
piece looks is a param, so two products that differ on it draw differently, and the drawn count of
drawers, doors or shelves is the stated count.

=================  ==============================================  ==========================
shape              draws                                           params
=================  ==============================================  ==========================
bar_stool          a stool at counter or bar height, its seat,     height, back, seat, base
                   its back and its base
desk               a desk top over its legs, a drawer pedestal     outline, drawers, legs
                   (one front per drawer), an L-shaped return
office_chair       a swivel chair: back, seat, arms, its base      back, cover, arms, base
tv_stand           a low media unit: one front per door, an open   doors, shelves, legs
                   bay with one board per shelf
kitchen_island     a worktop over a run of drawers and doors       doors, drawers, top, wheels
=================  ==============================================  ==========================

:data:`PARAMS` is each shape's table of params and the values it draws; any other value is refused
with a ``ValueError`` naming the param. Every value is a string, as a style row's ``params`` carry
it. A White piece reads white (gen#226): no body is shaded far toward black, and the metal parts
(legs, castors, gas lifts) are drawn in the kit's metal.

These shapes draw no generator product yet: gen#1022's later slices add the public draw call and
the products that use them.
"""

# ruff: noqa: E501 -- param tables and SVG path literals read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_furniture import (
    METAL,
    _drawer_fronts,
    _grain,
    _knob,
    _legs,
    _rect,
    _veins,
)

#: Each shape's params and the values it draws, in the order a picker would list them.
PARAMS: dict[str, dict[str, tuple[str, ...]]] = {
    "bar_stool": {"seat_height": ("counter", "bar"), "back": ("none", "low", "full"), "seat": ("round", "square"), "base": ("four_leg", "pedestal", "sled")},
    "desk": {"outline": ("rectangular", "l_shaped"), "drawers": ("0", "1", "2", "3", "4"), "legs": ("straight", "panel", "hairpin")},
    "office_chair": {"back": ("mid", "high"), "cover": ("mesh", "fabric"), "arms": ("yes", "no"), "base": ("castor", "sled")},
    "tv_stand": {"doors": ("0", "1", "2", "3", "4"), "shelves": ("0", "1", "2", "3"), "legs": ("short", "plinth", "hairpin")},
    "kitchen_island": {"doors": ("0", "1", "2", "3", "4"), "drawers": ("0", "1", "2", "3"), "top": ("wood", "marble_effect", "steel"), "wheels": ("no", "yes")},
}  # fmt: skip

FLOOR = 352
#: A kitchen island's worktop, by its ``top`` (the worktop is not the body's color).
WORKTOPS = {"wood": "#c8a06a", "marble_effect": "#ece9e4", "steel": "#c9ccd1"}


def _valid(shape: str, **given: str) -> None:
    """Refuse a value the shape does not draw, naming the param."""
    for key, value in given.items():
        if value not in PARAMS[shape][key]:
            raise ValueError(f"unknown {shape} {key} {value!r}; one of {PARAMS[shape][key]}")


def _group(cls: str, parts: list[str]) -> list[str]:
    return [f'<g class="{cls}">', *parts, "</g>"]


def _slab(x: float, y: float, w: float, h: float, paint: str) -> str:
    """A top seen a little from above: its front edge, a lip proud of the body."""
    return _path(f"M{x:.1f},{y:.1f} L{x + w:.1f},{y:.1f} L{x + w:.1f},{y + h:.1f} L{x:.1f},{y + h:.1f} Z", paint, LW_DETAIL)


def bar_stool(paint: str, fill: Fill, label: str | None, seat_height: str = "bar", back: str = "low", seat: str = "round", base: str = "four_leg") -> list[str]:
    """A stool whose seat (``class="seat"``) stands at ``counter`` or ``bar`` ``seat_height``, with no
    back, a ``low`` or a ``full`` back, a ``round`` or ``square`` seat, on four legs, a pedestal
    or a sled frame."""
    _valid("bar_stool", seat_height=seat_height, back=back, seat=seat, base=base)
    sy = {"counter": 172, "bar": 120}[seat_height]
    out: list[str] = []
    if back != "none":
        top = sy - (54 if back == "low" else 120)
        out += [_rect(150, top, 100, 26, paint, LW_DETAIL, rx=8), _rect(160, top + 26, 10, sy - top - 26, paint, LW_DETAIL), _rect(230, top + 26, 10, sy - top - 26, paint, LW_DETAIL)]
        if back == "full":
            out += [_rect(186, top + 26, 8, sy - top - 26, paint, 1.0), _rect(206, top + 26, 8, sy - top - 26, paint, 1.0)]
    if base == "four_leg":
        out += [_path(f"M146,{sy + 20} L158,{sy + 20} L134,{FLOOR} L122,{FLOOR} Z", paint, LW_DETAIL), _path(f"M242,{sy + 20} L254,{sy + 20} L278,{FLOOR} L266,{FLOOR} Z", paint, LW_DETAIL), _path(f"M174,{sy + 20} L184,{sy + 20} L180,{FLOOR - 6} L172,{FLOOR - 6} Z", _shade(paint, 0.1), 1.0), _path(f"M216,{sy + 20} L226,{sy + 20} L228,{FLOOR - 6} L220,{FLOOR - 6} Z", _shade(paint, 0.1), 1.0)]
        rung = (sy + 20 + FLOOR) / 2 + 20
        out.append(_line(f"M{140 - (rung - sy) * 0.08:.1f},{rung:.1f} L{260 + (rung - sy) * 0.08:.1f},{rung:.1f}", 6, stroke=METAL))
    elif base == "pedestal":
        ring = (sy + FLOOR) / 2 + 16
        out += [_rect(192, sy + 20, 16, FLOOR - sy - 28, METAL, LW_DETAIL), f'<ellipse cx="200" cy="{ring:.1f}" rx="40" ry="8" fill="none" stroke="{METAL}" stroke-width="5"/>', f'<ellipse cx="200" cy="{FLOOR - 6}" rx="58" ry="10" fill="{METAL}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>']
    else:  # sled: two side frames that run along the floor
        out += [_line(f"M150,{sy + 20} L136,{FLOOR - 4} L264,{FLOOR - 4} L250,{sy + 20}", 7, stroke=METAL), _line(f"M143,{(sy + FLOOR) / 2 + 24:.1f} L257,{(sy + FLOOR) / 2 + 24:.1f}", 5, stroke=METAL)]
    out.append(_rect(136, sy, 128, 22, paint, LW, rx=11 if seat == "round" else 2, cls="seat"))
    if seat == "round":
        out.append(f'<ellipse cx="200" cy="{sy + 2}" rx="60" ry="7" fill="{paint}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
    return out


def desk(paint: str, fill: Fill, label: str | None, outline: str = "rectangular", drawers: str = "2", legs: str = "straight") -> list[str]:
    """A desk top over its ``legs``, with a pedestal of exactly ``drawers`` drawer fronts
    (``class="drawer"``) under its right end; an ``l_shaped`` desk adds its return
    (``class="return"``), the wing that runs back from the right end."""
    _valid("desk", outline=outline, drawers=drawers, legs=legs)
    n = int(drawers)
    x0, x1, ty = (48, 352, 168) if outline == "rectangular" else (40, 290, 182)
    out: list[str] = []
    if outline == "l_shaped":
        wing = [_path(f"M{x1 - 6},{ty} L{x1 + 30},{ty} L{x1 + 80},{ty - 34} L{x1 + 44},{ty - 34} Z", paint, LW), _path(f"M{x1 + 30},{ty} L{x1 + 80},{ty - 34} L{x1 + 80},{ty - 22} L{x1 + 30},{ty + 12} Z", _shade(paint, 0.12), LW_DETAIL), _rect(x1 + 70, ty - 22, 10, FLOOR - ty - 8, paint, LW_DETAIL)]
        out += _group("return", wing)
    span = FLOOR - ty - 14
    if legs == "straight":
        out += [_rect(x0 + 8, ty + 14, 14, span, paint, LW_DETAIL), _rect(x1 - 22, ty + 14, 14, span, paint, LW_DETAIL)]
    elif legs == "panel":
        out += [_rect(x0 + 4, ty + 14, 20, span, paint, LW_DETAIL), _rect(x1 - 24, ty + 14, 20, span, paint, LW_DETAIL), _line(f"M{x0 + 24},{FLOOR - 70} L{x1 - 24},{FLOOR - 70}", 4, stroke=_shade(paint, 0.12))]
    else:  # hairpin: two rods per end, meeting at the floor
        pins = " ".join(f"M{x - 12},{ty + 14} L{x},{FLOOR} L{x + 12},{ty + 14}" for x in (x0 + 22, x1 - 22))
        out.append(_line(pins, 4, stroke=METAL))
    if n:
        px1 = x1 - (30 if legs != "hairpin" else 44)
        out += [_rect(px1 - 84, ty + 14, 84, 40 * n + 8, paint, LW_DETAIL), *_drawer_fronts(px1 - 82, ty + 16, 80, 40 * n + 4, n, paint)]
    out += [_slab(x0, ty, x1 - x0, 14, paint), _grain(x0, ty, x1 - x0, 14, paint)]
    return out


def office_chair(paint: str, fill: Fill, label: str | None, back: str = "mid", cover: str = "mesh", arms: str = "yes", base: str = "castor") -> list[str]:
    """A swivel chair: a ``mid`` or ``high`` back (a high one carries a headrest) covered in
    ``mesh`` (a woven grid) or ``fabric`` (a stitched seam), two arms (``class="arm"``) when
    ``arms`` is yes, on a five-star ``castor`` base or a cantilever ``sled``."""
    _valid("office_chair", back=back, cover=cover, arms=arms, base=base)
    top = 112 if back == "mid" else 64
    bx, bw, by1 = 146, 108, 204
    out: list[str] = []
    if base == "castor":
        hub = (200, 300)
        feet = ((112, 330), (150, 340), (200, 344), (250, 340), (288, 330))
        out += [_rect(193, 236, 14, 64, METAL, LW_DETAIL), _line(" ".join(f"M{hub[0]},{hub[1]} L{x},{y}" for x, y in feet), 7, stroke=METAL)]
        out += [f'<circle class="castor" cx="{x}" cy="{y + 6}" r="7" fill="{METAL}" stroke="{INK}" stroke-width="1"/>' for x, y in feet]
    else:  # sled: one bent rod per side, along the floor and up to the seat
        out.append(_line(f"M142,236 L130,{FLOOR - 4} L270,{FLOOR - 4} L258,236", 7, stroke=METAL))
    if back == "high":
        out += [_rect(168, top - 34, 64, 30, paint, LW_DETAIL, rx=10), _rect(196, top - 6, 8, 8, METAL, 1.0)]
    out += [_rect(bx, top, bw, by1 - top, paint, LW, rx=18)]
    if cover == "mesh":
        rows = " ".join(f"M{bx + 8},{y} L{bx + bw - 8},{y}" for y in range(top + 12, by1 - 6, 10))
        cols = " ".join(f"M{x},{top + 8} L{x},{by1 - 8}" for x in range(bx + 12, bx + bw - 6, 10))
        out.append(_line(f"{rows} {cols}", 0.8, ' stroke-opacity=".45"', _shade(paint, 0.4)))
    else:
        out += [_line(f"M{bx + 14},{(top + by1) / 2:.1f} L{bx + bw - 14},{(top + by1) / 2:.1f}", 1.2, ' stroke-opacity=".6"'), _line(f"M{bx + 10},{top + 10} L{bx + bw - 10},{top + 10}", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"')]
    out += [_rect(194, by1, 12, 10, METAL, 1.0), _rect(132, 210, 136, 28, paint, LW, rx=12, cls="seat")]
    if arms == "yes":
        for x in (114, 268):
            out += _group("arm", [_rect(x + 6, 186, 6, 34, METAL, 1.0), _rect(x - 4, 178, 26, 10, paint, LW_DETAIL, rx=5)])
    return out


def tv_stand(paint: str, fill: Fill, label: str | None, doors: str = "2", shelves: str = "1", legs: str = "short") -> list[str]:
    """A low media unit: exactly ``doors`` door fronts (``class="door"``) and an open bay with
    exactly ``shelves`` boards (``class="shelf"``) in it, on short legs, a plinth or hairpin legs.
    With no open shelf the doors fill the front; with neither, the front is one plain panel."""
    _valid("tv_stand", doors=doors, shelves=shelves, legs=legs)
    nd, ns = int(doors), int(shelves)
    x0, w, y0, h = 44, 312, 206, 104
    out = [_rect(x0, y0, w, h, paint), _slab(x0 - 6, y0 - 12, w + 12, 12, paint)]
    bay = 96 if ns else 0
    bx = x0 + (w - bay) / 2 if nd else x0 + 6
    if ns:
        bw = bay if nd else w - 12
        out.append(_rect(bx, y0 + 6, bw, h - 12, _shade(paint, 0.1), LW_DETAIL))
        for k in range(ns):
            sy = y0 + 6 + (h - 12) * (k + 1) / (ns + 1)
            out.append(_rect(bx + 2, sy - 3, bw - 4, 6, paint, 1.0, cls="shelf"))
    if nd:
        left = (nd + 1) // 2 if ns else nd
        spans = [(x0 + 6, bx - (x0 + 6), left), (bx + bay, x0 + w - 6 - bx - bay, nd - left)] if ns else [(x0 + 6, w - 12, nd)]
        for sx, sw, k in spans:
            for i in range(k):
                dw = sw / k
                dx = sx + i * dw
                out += [_rect(dx + 3, y0 + 6, dw - 6, h - 12, paint, LW_DETAIL, rx=2, cls="door"), _knob(dx + dw / 2 + (dw / 2 - 14) * (1 if i % 2 == 0 else -1), y0 + h / 2)]
    elif not ns:
        out.append(_rect(x0 + 8, y0 + 8, w - 16, h - 16, paint, LW_DETAIL, rx=2))
    if legs == "short":
        out += _legs([x0 + 16, x0 + 70, x0 + w - 70, x0 + w - 16], y0 + h, y0 + h + 26, paint, 12)
    elif legs == "plinth":
        out.append(_rect(x0 + 10, y0 + h, w - 20, 14, _shade(paint, 0.1), LW_DETAIL))
    else:
        pins = " ".join(f"M{x - 10},{y0 + h} L{x},{FLOOR} L{x + 10},{y0 + h}" for x in (x0 + 24, x0 + w - 24))
        out.append(_line(pins, 4, stroke=METAL))
    return out


def kitchen_island(paint: str, fill: Fill, label: str | None, doors: str = "2", drawers: str = "2", top: str = "wood", wheels: str = "no") -> list[str]:
    """A kitchen island: a ``top`` worktop (wood grain, marble-effect veins or brushed steel) over
    a row of exactly ``drawers`` drawer fronts (``class="drawer"``) and exactly ``doors`` door
    fronts (``class="door"``) below it (no door: open shelves), on a plinth or on castors."""
    _valid("kitchen_island", doors=doors, drawers=drawers, top=top, wheels=wheels)
    nd, nr = int(doors), int(drawers)
    x0, w, y0 = 68, 264, 152
    y1 = FLOOR - (22 if wheels == "yes" else 14)
    out = [_rect(x0, y0, w, y1 - y0, paint)]
    band = 46 if nr else 0
    if nr:
        out += _drawer_fronts(x0 + 4, y0 + 4, w - 8, band, nr, paint, cols=nr)
    lo = y0 + 4 + band
    if nd:
        dw = (w - 8) / nd
        for i in range(nd):
            dx = x0 + 4 + i * dw
            out += [_rect(dx + 3, lo + 3, dw - 6, y1 - lo - 10, paint, LW_DETAIL, rx=2, cls="door"), _line(f"M{dx + dw / 2:.1f},{lo + 18:.1f} L{dx + dw / 2:.1f},{lo + 42:.1f}", 4, stroke=METAL)]
    else:
        out.append(_rect(x0 + 8, lo + 4, w - 16, y1 - lo - 12, _shade(paint, 0.1), LW_DETAIL))
        out += [_line(f"M{x0 + 10},{y:.1f} L{x0 + w - 10},{y:.1f}", 4, stroke=_shade(paint, 0.25)) for y in (lo + (y1 - lo) / 3, lo + 2 * (y1 - lo) / 3)]
    if wheels == "yes":
        out += [f'<circle class="castor" cx="{x}" cy="{FLOOR - 10}" r="10" fill="{METAL}" stroke="{INK}" stroke-width="1"/>' for x in (x0 + 20, x0 + w - 20)]
    else:
        out.append(_rect(x0 + 8, y1, w - 16, 14, _shade(paint, 0.1), LW_DETAIL))
    worktop = WORKTOPS[top]
    tx, tw, ty = x0 - 16, w + 32, y0 - 18
    out.append(_slab(tx, ty, tw, 18, worktop).replace("<path", '<path class="top"', 1))
    if top == "wood":
        out.append(_grain(tx, ty, tw, 18, worktop))
    elif top == "marble_effect":
        out += _veins(tx + tw / 2, ty + 9, tw / 2, 9, worktop)
    else:
        out.append(_highlight(f"M{tx + 20},{ty + 6} L{tx + tw - 20},{ty + 6}", 3, 0.8))
    return out


register(
    {"bar_stool": bar_stool, "desk": desk, "office_chair": office_chair, "tv_stand": tv_stand,
     "kitchen_island": kitchen_island},
)  # fmt: skip

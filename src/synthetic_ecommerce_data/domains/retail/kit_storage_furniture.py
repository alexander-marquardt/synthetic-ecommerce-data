"""Own-kind shapes for the storage furniture the kit could not draw (gen#1022, slice 2).

Sideboards, bar cabinets, office storage cabinets, shoe storage and wall shelves, each a front
drawing in the kit's house style with the record's fill on the main surface (a sideboard also
shows its top and right side, lit and shaded, on a ground shadow: gen#1214), drawn from
the attributes a record states, as slice 1's shapes (:mod:`kit_home_furniture`) are: the variant
axis that changes how the piece looks is a param, and the drawn count of doors, drawers,
shelves, tiers and stools is the stated count.

===============  ==============================================  ===============================
shape            draws                                           params
===============  ==============================================  ===============================
sideboard        a long low cabinet: a row of drawers over a     doors, drawers, legs
                 row of doors (no door: an open bay), on legs
bar_cabinet      a drinks cabinet: a bottle rack over its        doors, glass_rack, stools
                 doors, glasses hung from a rack, and the
                 stools of a bar set standing in front
storage_cabinet  a tall office cabinet: files on its shelves,    front, shelves, drawers, lock
                 open or behind glass doors, filing drawers
                 under them, a lock
shoe_storage     tiers of shoes on an open rack, or under the    tiers, form, frame
                 cushioned seat of a bench
wall_shelf       boards on a wall, floating, on brackets or on   shelves, mount, layout
                 rails, stacked or staggered
===============  ==============================================  ===============================

:data:`PARAMS` is each shape's table of params and the values it draws; any other value is refused
with a ``ValueError`` naming the param. A White piece reads white (gen#226): what stands on a
shelf (books, files, bottles, shoes) is drawn in the kit's book colors and the metal parts in
its metal, and no body is shaded far toward black.

``drawings.render`` (:mod:`synthetic_ecommerce_data.drawings`) is the public call that draws
these shapes in a finish; no generator product uses them yet.
"""

# ruff: noqa: E501 -- param tables and SVG path literals read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import ground_shadow
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_furniture import (
    BOOKS,
    GLASS,
    METAL,
    _dim,
    _drawer_fronts,
    _front,
    _grain,
    _knob,
    _legs,
    _lit,
    _quad,
    _rect,
    _side,
)
from synthetic_ecommerce_data.domains.retail.kit_home_furniture import FLOOR, _group, _slab

#: Each shape's params and the values it draws, in the order a picker would list them.
PARAMS: dict[str, dict[str, tuple[str, ...]]] = {
    "sideboard": {"doors": ("0", "1", "2", "3", "4"), "drawers": ("0", "1", "2", "3", "4"), "legs": ("tapered", "plinth", "hairpin")},
    "bar_cabinet": {"doors": ("0", "1", "2"), "glass_rack": ("yes", "no"), "stools": ("0", "1", "2", "3")},
    "storage_cabinet": {"front": ("open", "glass"), "shelves": ("1", "2", "3", "4", "5"), "drawers": ("0", "1", "2", "3"), "lock": ("no", "yes")},
    "shoe_storage": {"tiers": ("2", "3", "4", "5"), "form": ("rack", "bench"), "frame": ("wood", "metal")},
    "wall_shelf": {"shelves": ("1", "2", "3", "4"), "mount": ("floating", "bracket", "rail"), "layout": ("stacked", "staggered")},
}  # fmt: skip


def _valid(shape: str, **given: str) -> None:
    """Refuse a value the shape does not draw, naming the param."""
    for key, value in given.items():
        if value not in PARAMS[shape][key]:
            raise ValueError(f"unknown {shape} {key} {value!r}; one of {PARAMS[shape][key]}")


def _doors(x: float, y: float, w: float, h: float, n: int, paint: str, cls: str = "door") -> list[str]:
    """``n`` door fronts side by side filling the box, a knob each by its meeting edge."""
    out: list[str] = []
    dw = w / n
    for i in range(n):
        dx = x + i * dw
        knob_x = dx + dw - 12 if i % 2 == 0 else dx + 12
        out += [_rect(dx + 3, y + 3, dw - 6, h - 6, paint, LW_DETAIL, rx=2, cls=cls), _knob(knob_x, y + h / 2)]
    return out


def _bottle(cx: float, base: float, height: float, color: str) -> list[str]:
    """One bottle standing on ``base``: a body and a neck."""
    bw = 12
    neck = height * 0.35
    return [_path(f"M{cx - bw / 2:.1f},{base:.1f} L{cx - bw / 2:.1f},{base - height + neck:.1f} Q{cx:.1f},{base - height + neck - 8:.1f} {cx + bw / 2:.1f},{base - height + neck:.1f} L{cx + bw / 2:.1f},{base:.1f} Z", color, 1.0), _rect(cx - 2.5, base - height, 5, neck - 4, color, 1.0)]


def _file(x: float, base: float, w: float, h: float, color: str) -> str:
    """A box file or binder standing on a shelf, its spine facing out."""
    return _rect(x, base - h, w, h, color, 1.0, rx=1)


def _shoe(x: float, base: float, color: str) -> str:
    """One shoe on a tier, toe to the right."""
    return _path(f"M{x:.1f},{base:.1f} L{x:.1f},{base - 16:.1f} L{x + 12:.1f},{base - 16:.1f} Q{x + 18:.1f},{base - 8:.1f} {x + 34:.1f},{base - 7:.1f} Q{x + 40:.1f},{base - 5:.1f} {x + 40:.1f},{base:.1f} Z", color, 1.0)


#: The sideboard's front (width, height), the depth its top and right side recede, and its legs' height.
SIDEBOARD = (296.0, 180.0, 36.0)
SIDEBOARD_LEGS = {"tapered": 40.0, "plinth": 14.0, "hairpin": 40.0}


def sideboard(paint: str, fill: Fill, label: str | None, doors: str = "2", drawers: str = "2", legs: str = "tapered") -> list[str]:
    """A long low cabinet seen from in front, a little above and to the right, as the kit's other
    cabinets are (:func:`.kit_furniture._cabinet`): its top and right side show, lit from the left,
    and it stands on a ground shadow (:func:`.ground_shadow.ellipse`), so it fills half the product
    area (gen#1214). A band of exactly ``drawers`` drawer fronts (``class="drawer"``) over exactly
    ``doors`` door fronts (``class="door"``), each door with a recessed panel; with no door the lower
    part is an open bay with a board across it. On ``tapered`` legs, a ``plinth`` or ``hairpin`` legs."""
    _valid("sideboard", doors=doors, drawers=drawers, legs=legs)
    nd, nr = int(doors), int(drawers)
    w, h, d = SIDEBOARD
    lip = 6.0
    x0 = 200 - (w + 2 * lip + d) / 2 + lip
    x1 = x0 + w
    y1 = FLOOR - SIDEBOARD_LEGS[legs]
    y0 = y1 - h
    rise = d * 0.4
    side = _shade(paint, 0.17)
    out = [ground_shadow.ellipse(x0 + (w + d) / 2, FLOOR, (w + d) / 2 + 4, 8.0)]
    # The back right leg shows under the side; the others stand at the front corners.
    if legs == "tapered":
        out += _legs([x1 + d - 12], y1 - d * 0.5, FLOOR - d * 0.5, side, 12)
    elif legs == "hairpin":
        out.append(_line(f"M{x1 + d - 22:.1f},{y1 - d * 0.5:.1f} L{x1 + d - 10:.1f},{FLOOR - d * 0.5:.1f} L{x1 + d + 2:.1f},{y1 - d * 0.5:.1f}", 4, stroke=METAL))
    out.append(_side(x1, y0, h, d, paint))
    out.append(_dim(_quad((x1, y0), (x1 + d, y0 - rise), (x1 + d, y1 - d * 0.5), (x1, y1)), 0.12))
    out.append(_rect(x0, y0, w, h, paint))
    # The top: a lip proud of the body, its surface receding to the back, lit from the left.
    t0 = y0 - 12
    top = _quad((x0 - lip, t0), (x0 - lip + d, t0 - rise), (x1 + lip + d, t0 - rise), (x1 + lip, t0))
    out += [_path(top, _tint(paint, 0.08), LW_DETAIL), _lit(_quad((x0, t0 - 2), (x0 + d * 0.6, t0 - rise + 2), (x0 + w * 0.45, t0 - rise + 2), (x0 + w * 0.35, t0 - 2)), 0.35)]
    out.append(_path(_quad((x1 + lip, t0), (x1 + lip + d, t0 - rise), (x1 + lip + d, y0 - rise), (x1 + lip, y0)), side, LW_DETAIL))
    out += [_rect(x0 - lip, t0, w + 2 * lip, 12, paint, LW_DETAIL), _grain(x0 - lip, t0, w + 2 * lip, 12, paint), _highlight(f"M{x0:.1f},{t0 + 2:.1f} L{x0 + w * 0.4:.1f},{t0 + 2:.1f}", 2.5, 0.8)]
    out.append(_dim(_quad((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x1 - 2, y0 + 8), (x0 + 2, y0 + 8)), 0.12))  # the shade under the lip
    band = 48 if nr else 0
    if nr:
        out += _drawer_fronts(x0 + 6, y0 + 8, w - 12, band, nr, paint, cols=nr)
        out += _front(x0 + 6, y0 + 8, w - 12, band)
    lo = y0 + 8 + band
    if nd:
        out += _doors(x0 + 6, lo, w - 12, y1 - lo - 6, nd, paint)
        dw = (w - 12) / nd
        for i in range(nd):
            out.append(_rect(x0 + 6 + i * dw + 16, lo + 18, dw - 32, y1 - lo - 42, _shade(paint, 0.06), 1.0, rx=1))
        out += _front(x0 + 6, lo, w - 12, y1 - lo - 6)
    else:
        out.append(_rect(x0 + 10, lo + 4, w - 20, y1 - lo - 14, _shade(paint, 0.12), LW_DETAIL))
        out.append(_dim(_quad((x0 + 10, lo + 4), (x1 - 10, lo + 4), (x1 - 10, lo + 20), (x0 + 10, lo + 28)), 0.18))
        out.append(_line(f"M{x0 + 12:.1f},{(lo + y1) / 2:.1f} L{x1 - 12:.1f},{(lo + y1) / 2:.1f}", 5, stroke=_shade(paint, 0.25)))
    if legs == "tapered":
        out += _legs([x0 + 18, x1 - 18], y1, FLOOR, paint, 14)
    elif legs == "plinth":
        out += [_path(_quad((x1 - 10, y1), (x1 - 10 + d * 0.8, y1 - d * 0.4), (x1 - 10 + d * 0.8, y1 - d * 0.4 + 14), (x1 - 10, FLOOR)), side, LW_DETAIL), _rect(x0 + 10, y1, w - 20, 14, _shade(paint, 0.1), LW_DETAIL)]
    else:  # hairpin: two rods per end, meeting at the floor
        pins = " ".join(f"M{x - 12:.1f},{y1:.1f} L{x:.1f},{FLOOR} L{x + 12:.1f},{y1:.1f}" for x in (x0 + 28, x1 - 28))
        out.append(_line(pins, 4, stroke=METAL))
    return out


def _stool(cx: float, paint: str) -> list[str]:
    """A backless bar stool standing in front of the cabinet: a lighter seat on splayed metal
    legs with a footrest, so it reads against the doors behind it."""
    seat_y = FLOOR - 104
    legs = f"M{cx - 22},{seat_y + 12} L{cx - 32},{FLOOR} M{cx + 22},{seat_y + 12} L{cx + 32},{FLOOR}"
    return _group("stool", [_line(legs, 6, stroke=METAL), _line(f"M{cx - 28},{FLOOR - 36} L{cx + 28},{FLOOR - 36}", 4, stroke=METAL), _rect(cx - 34, seat_y, 68, 16, _tint(paint, 0.35), LW, rx=8)])


def bar_cabinet(paint: str, fill: Fill, label: str | None, doors: str = "2", glass_rack: str = "yes", stools: str = "0") -> list[str]:
    """A drinks cabinet: an open upper bay with a rack of bottles, wine glasses
    (``class="wine_glass"``) hung under its top when ``glass_rack`` is yes, exactly ``doors``
    door fronts (``class="door"``) below (no door: a shelf of laid bottles), and the bar set's
    exactly ``stools`` stools (``class="stool"``) standing in front."""
    _valid("bar_cabinet", doors=doors, glass_rack=glass_rack, stools=stools)
    nd, ns = int(doors), int(stools)
    x0, w, y0, y1 = 104, 192, 58, FLOOR - 14
    mid = y0 + 128
    out = [_rect(x0, y0, w, y1 - y0, paint), _slab(x0 - 8, y0 - 12, 16 + w, 12, paint), _rect(x0 + 10, y1, w - 20, 14, _shade(paint, 0.1), LW_DETAIL)]
    out.append(_rect(x0 + 8, y0 + 8, w - 16, mid - y0 - 12, _shade(paint, 0.12), LW_DETAIL))
    rack = mid - 8
    out.append(_rect(x0 + 10, rack - 4, w - 20, 6, paint, 1.0))
    for i, cx in enumerate(range(x0 + 24, x0 + w - 16, 22)):
        out += _bottle(cx, rack - 4, 58 + 6 * (i % 3), BOOKS[i % len(BOOKS)])
    if glass_rack == "yes":
        out.append(_line(f"M{x0 + 14},{y0 + 14} L{x0 + w - 14},{y0 + 14}", 3, stroke=METAL))
        for gx in range(x0 + 30, x0 + w - 20, 34):
            out.append(_path(f"M{gx},{y0 + 14} L{gx},{y0 + 30} M{gx - 11},{y0 + 30} Q{gx},{y0 + 54} {gx + 11},{y0 + 30} Z", GLASS, 1.2).replace("<path", '<path class="wine_glass"', 1))
    if nd:
        out += _doors(x0 + 4, mid, w - 8, y1 - mid - 4, nd, paint)
    else:
        out.append(_rect(x0 + 8, mid + 4, w - 16, y1 - mid - 12, _shade(paint, 0.12), LW_DETAIL))
        for k, cx in enumerate(range(x0 + 28, x0 + w - 20, 30)):
            out.append(f'<circle cx="{cx}" cy="{y1 - 26}" r="11" fill="{BOOKS[(k + 2) % len(BOOKS)]}" stroke="{INK}" stroke-width="1"/>')
    if ns:
        span = 260
        for i in range(ns):
            out += _stool(200 - span / 2 + span * (i + 0.5) / ns if ns > 1 else 200, paint)
    return out


def storage_cabinet(paint: str, fill: Fill, label: str | None, front: str = "open", shelves: str = "3", drawers: str = "0", lock: str = "no") -> list[str]:
    """A tall office cabinet: exactly ``shelves`` shelves (``class="shelf"``) of files, open or
    behind two ``glass`` doors (``class="glass"``), over exactly ``drawers`` filing drawers
    (``class="drawer"``), with a lock (``class="lock"``) when ``lock`` is yes."""
    _valid("storage_cabinet", front=front, shelves=shelves, drawers=drawers, lock=lock)
    ns, nr = int(shelves), int(drawers)
    x0, w, y0, y1 = 116, 168, 34, FLOOR - 12
    out = [_rect(x0, y0, w, y1 - y0, paint), _slab(x0 - 6, y0 - 10, w + 12, 10, paint), _rect(x0 + 8, y1, w - 16, 12, _shade(paint, 0.1), LW_DETAIL)]
    band = 46 * nr
    bay_bottom = y1 - 6 - band
    out.append(_rect(x0 + 8, y0 + 8, w - 16, bay_bottom - y0 - 10, _shade(paint, 0.1), LW_DETAIL))
    pitch = (bay_bottom - y0 - 8) / ns
    for k in range(ns):
        sy = y0 + 8 + pitch * (k + 1)
        for j, fx in enumerate(range(x0 + 14, x0 + w - 24, 16)):
            out.append(_file(fx, sy - 6, 12, min(pitch - 14, 58) - 4 * ((j + k) % 3), BOOKS[(j + 2 * k) % len(BOOKS)]))
        out.append(_rect(x0 + 8, sy - 6, w - 16, 6, paint, 1.0, cls="shelf"))
    if front == "glass":
        for gx in (x0 + 8, x0 + w / 2):
            out.append(f'<rect class="glass" x="{gx + 2:.1f}" y="{y0 + 10:.1f}" width="{w / 2 - 12:.1f}" height="{bay_bottom - y0 - 14:.1f}" rx="2" fill="{GLASS}" fill-opacity=".35" stroke="{INK}" stroke-width="{LW_DETAIL}"/>')
        out += [_knob(x0 + w / 2 - 8, (y0 + bay_bottom) / 2), _knob(x0 + w / 2 + 8, (y0 + bay_bottom) / 2)]
    if nr:
        out += _drawer_fronts(x0 + 4, bay_bottom + 2, w - 8, band, nr, paint)
    if lock == "yes":
        out.append(f'<circle class="lock" cx="{x0 + w / 2:.1f}" cy="{y0 + 4:.1f}" r="4" fill="{METAL}" stroke="{INK}" stroke-width="1"/>')
    return out


def shoe_storage(paint: str, fill: Fill, label: str | None, tiers: str = "3", form: str = "rack", frame: str = "wood") -> list[str]:
    """Exactly ``tiers`` tiers (``class="tier"``) of shoes between two side frames of ``wood``
    or ``metal``: an open ``rack``, or a ``bench`` with a cushioned seat (``class="seat"``) on
    top."""
    _valid("shoe_storage", tiers=tiers, form=form, frame=frame)
    n = int(tiers)
    pitch = 44 if form == "rack" else 34
    x0, w = (96, 208) if form == "rack" else (64, 272)
    top = FLOOR - 16 - n * pitch
    side = METAL if frame == "metal" else paint
    out: list[str] = []
    if frame == "wood":
        out += [_rect(x0, top, 14, FLOOR - top, side), _rect(x0 + w - 14, top, 14, FLOOR - top, side)]
    else:
        out.append(_line(f"M{x0 + 6},{top} L{x0 + 6},{FLOOR} M{x0 + w - 6},{top} L{x0 + w - 6},{FLOOR}", 5, stroke=METAL))
    for k in range(n):
        base = FLOOR - 16 - k * pitch
        for j, sx in enumerate(range(x0 + 20, x0 + w - 56, 46)):
            out.append(_shoe(sx, base, BOOKS[(j + k) % len(BOOKS)]))
        if frame == "wood":
            out.append(_rect(x0 + 14, base, w - 28, 8, paint, LW_DETAIL, cls="tier"))
        else:
            out += _group("tier", [_line(f"M{x0 + 6},{base + 2} L{x0 + w - 6},{base + 2} M{x0 + 6},{base + 7} L{x0 + w - 6},{base + 7}", 3, stroke=METAL)])
    lid = _slab(x0 - 6, top - 12, w + 12, 12, paint)
    out.append(lid)
    if form == "bench":
        out.append(_rect(x0 - 2, top - 34, w + 4, 22, _shade(paint, 0.12), LW, rx=10, cls="seat"))
        out.append(_line(" ".join(f"M{x},{top - 30} L{x},{top - 16}" for x in range(x0 + 40, x0 + w - 20, 48)), 1.2, ' stroke-opacity=".6"'))
    return out


def wall_shelf(paint: str, fill: Fill, label: str | None, shelves: str = "2", mount: str = "floating", layout: str = "stacked") -> list[str]:
    """Exactly ``shelves`` boards (``class="shelf"``) on a wall with books and a pot on them:
    ``floating`` (no fixing shows), on two brackets each (``class="bracket"``), or hung from two
    ``rail`` uprights (``class="rail"``); ``stacked`` one above the other or ``staggered``."""
    _valid("wall_shelf", shelves=shelves, mount=mount, layout=layout)
    n = int(shelves)
    bw, th = 220, 14
    pitch = min(88, 290 / n)
    bottom = 200 + n * pitch / 2
    out: list[str] = []
    boards = []
    for k in range(n):
        y = bottom - k * pitch
        shift = (-40 if k % 2 == 0 else 40) if layout == "staggered" else 0
        boards.append((200 - bw / 2 + shift, y))
    if mount == "rail":
        xs = (200 - bw / 2 + 40, 200 + bw / 2 - 40)
        rail_top, rail_bottom = boards[-1][1] - pitch + 30, bottom + th + 10
        out += [_rect(x - 5, rail_top, 10, rail_bottom - rail_top, METAL, 1.0, cls="rail") for x in xs]
    for k, (x, y) in enumerate(boards):
        for j, bx in enumerate(range(int(x) + 16, int(x) + 96, 13)):
            out.append(_file(bx, y, 11, 46 - 6 * ((j + k) % 3), BOOKS[(j + k) % len(BOOKS)]))
        out.append(_path(f"M{x + 150:.1f},{y:.1f} L{x + 144:.1f},{y - 30:.1f} L{x + 180:.1f},{y - 30:.1f} L{x + 174:.1f},{y:.1f} Z", BOOKS[(k + 3) % len(BOOKS)], 1.0))
        out += [_rect(x, y, bw, th, paint, LW, cls="shelf"), _grain(x, y, bw, th, paint)]
        if mount == "bracket":
            for bx in (x + 30, x + bw - 30):
                out.append(_path(f"M{bx - 4:.1f},{y + th:.1f} L{bx + 4:.1f},{y + th:.1f} L{bx + 4:.1f},{y + th + 30:.1f} L{bx - 4:.1f},{y + th + 30:.1f} Z M{bx - 4:.1f},{y + th:.1f} L{bx + 22:.1f},{y + th:.1f}", METAL, 1.0).replace("<path", '<path class="bracket"', 1))
    return out


register(
    {"sideboard": sideboard, "bar_cabinet": bar_cabinet, "storage_cabinet": storage_cabinet,
     "shoe_storage": shoe_storage, "wall_shelf": wall_shelf},
)  # fmt: skip

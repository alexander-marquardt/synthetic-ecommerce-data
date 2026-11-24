"""Household tool sets and assortment kits, drawn open and lit, filling the figure area (#1215).

Both are drawn as the container of their ``Container Type``, open, from the front, with what it
holds in it. A household set holds a hammer, pliers, screwdrivers and a wrench, and one bit for each
piece it counts; its container is in its published ``Color``, its tools in their ``Material``. An
assortment kit holds one item for each listed size, each drawn as its ``Type`` (hex keys, drills,
taps, or compartments of screws) in its ``Finish``.

Figures are laid out in a 164 by 200 box, in hundredths, y down: the figure area's own proportion.
"""

from __future__ import annotations

import math

from synthetic_ecommerce_data.core.drawing.model import Figure, arc
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, Record, _kit_slots
from synthetic_ecommerce_data.domains.industrial.drawing.lit import block, box, inches, lit

#: The box both types are drawn in, in inches: their extent.
EXTENT = (1.64, 2.0)
#: The scale of the smallest household set, of the largest one's: siblings draw apart.
SMALLEST = 0.95

STEEL = {
    "Chrome Vanadium Steel": "#c3cad0",
    "Carbon Steel": "#8f979e",
    "Alloy Steel": "#a9b2b9",
}
#: A molded tray, the wood of a hammer's handle, and a kit's containers.
TRAY, WOOD = "#c4ccd2", "#c89a5b"
SHELL = {
    "Plastic Case": "#3f5f7d",
    "Metal Index": "#7c8790",
    "Folding Holder": "#4a4f55",
    "Pouch": "#8a7758",
}


# --- tools ---------------------------------------------------------------------------------------


def _driver(fig: Figure, x: float, y0: float, y1: float, grip: str, steel: str) -> None:
    mid = y0 + 0.45 * (y1 - y0)
    fig.poly(box(x - 1.8, mid, x + 1.8, y1), "handle", steel)
    lit(fig, block(x - 6, y0, x + 6, mid, 4), grip)


def _hammer(fig: Figure, x: float, y0: float, y1: float, grip: str, steel: str) -> None:
    fig.poly(box(x - 4, y0, x + 4, y1), "handle", WOOD)
    claw = [(x + 8, y0 + 2), (x + 18, y0 + 12), (x + 6, y0 + 14)]
    lit(fig, [(x - 17, y0 + 2), *claw, (x - 17, y0 + 14)], steel, across=True)
    del grip


def _pliers(fig: Figure, x: float, y0: float, y1: float, grip: str, steel: str) -> None:
    pivot = y0 + 0.4 * (y1 - y0)
    for side in (-1, 1):
        fig.poly(
            [(x, y0), (x + 4 * side, y0), (x + 7 * side, pivot), (x, pivot + 4)], "handle", steel
        )
        fig.poly(
            [(x, pivot), (x + 7 * side, pivot), (x + 12 * side, y1), (x + 5 * side, y1)],
            "handle",
            grip,
        )
    fig.disc((x, pivot), 2.5, "dark")


def _wrench(fig: Figure, x: float, y0: float, y1: float, grip: str, steel: str) -> None:
    fig.poly(box(x - 3, y0 + 14, x + 3, y1), "handle", steel)
    jaw = [(x - 9, y0), (x - 4, y0), (x - 4, y0 + 8), (x + 4, y0 + 8), (x + 4, y0), (x + 9, y0)]
    fig.poly([*jaw, (x + 9, y0 + 12), (x + 3, y0 + 19), (x - 3, y0 + 19), (x - 9, y0 + 12)],
             "handle", steel)  # fmt: skip
    del grip


TOOLS = (_hammer, _pliers, _driver, _wrench, _driver)


def _tools(fig, x0: float, x1: float, y0: float, y1: float, grip, steel, tools=TOOLS) -> None:
    """``tools`` standing in a row, handles down but a screwdriver's."""
    step = (x1 - x0) / len(tools)
    for k, tool in enumerate(tools):
        tool(fig, x0 + step * (k + 0.5), y0 + 3 * (k % 2), y1, grip, steel)


def _bits(fig: Figure, pieces: int, x0: float, y0: float, x1: float, y1: float) -> None:
    """A tray of one bit for each piece, in rows."""
    fig.poly(box(x0, y0, x1, y1), "handle", TRAY)
    wide, high = x1 - x0 - 6, y1 - y0 - 6
    cols = max(1, math.ceil(math.sqrt(pieces * wide / high)))
    rows = math.ceil(pieces / cols)
    dx, dy = wide / cols, high / rows
    half = min(0.32 * min(dx, dy), 6.0)
    fig.bars(
        [
            (cx - half, cy - half, cx + half, cy + half)
            for cx, cy in (
                (x0 + 3 + dx * (k % cols + 0.5), y0 + 3 + dy * (k // cols + 0.5))
                for k in range(pieces)
            )
        ],
        "dark",
    )


# --- the household set's containers --------------------------------------------------------------


def _molded(fig: Figure, fill: str, steel: str, pieces: int) -> None:
    """A hinged case: tools in its lid, bits in its base, two latches and a carry handle."""
    fig.poly(block(52, 188, 112, 200, 4), "handle", fill)
    for y0, y1 in ((0, 94), (97, 193)):
        lit(fig, block(0, y0, 164, y1, 9), fill)
    fig.poly(box(16, 9, 144, 86), "handle", TRAY)
    _tools(fig, 16, 144, 13, 82, fill, steel)
    _bits(fig, pieces, 16, 106, 144, 182)
    for x in (30, 118):
        fig.poly(box(x, 90, x + 16, 101), "dark")


def _zippered(fig: Figure, fill: str, steel: str, pieces: int) -> None:
    """A soft case opened like a book: tools under a strap, bits, a zip round its edge."""
    for x0 in (0, 84):
        lit(fig, block(x0, 0, x0 + 80, 200, 16), fill)
    fig.lines(
        [((x0 + 4, y), (x0 + 4, y + 5)) for x0 in (0, 72, 84, 156) for y in range(20, 180, 10)]
    )
    fig.poly(box(79, 4, 85, 196), "handle", fill)
    _tools(fig, 10, 72, 20, 180, TRAY, steel, (_pliers, _driver, _wrench))
    fig.poly(box(10, 96, 70, 108), "handle", fill)
    _bits(fig, pieces, 96, 20, 148, 180)
    fig.disc((160, 190), 4, "dark")


def _toolbox(fig: Figure, fill: str, steel: str, pieces: int, metal: bool) -> None:
    """A box with its lid up: bits in the lid, tools standing in the body, a handle on top."""
    for x0, x1 in ((50, 58), (106, 114)):
        fig.poly(box(x0, 0, x1, 14), "dark")
    fig.poly(block(50, 0, 114, 7, 3), "handle", "#4a4f55")
    slope = 14 if metal else 3
    lit(fig, [(slope, 12), (164 - slope, 12), (164, 84), (0, 84)], fill)
    _bits(fig, pieces, 20, 19, 144, 77)
    fig.poly(box(5, 84, 159, 112), "handle", "#4a4f55")
    _tools(fig, 8, 156, 87, 130, "#d8b13b", steel)
    if metal:
        lit(fig, box(0, 112, 164, 200), fill)
        fig.lines([((0, 124), (164, 124)), ((0, 190), (164, 190))])
        fig.discs([(x, y) for x in (6, 158) for y in (118, 195)], 2.5, "dark")
        for x in (36, 114):
            fig.poly(box(x, 108, x + 14, 134), "handle", "#d5dade")
    else:
        lit(fig, block(0, 112, 164, 200, 8), fill)
        fig.lines([((10, 140), (154, 140)), ((10, 172), (154, 172))])
        for x in (30, 116):
            fig.poly(block(x, 106, x + 18, 128, 3), "dark")


def _roll(fig: Figure, fill: str, steel: str, pieces: int) -> None:
    """A pouch unrolled: tools standing in stitched pockets, bits on its lower flap, a tie."""
    fig.poly(box(150, 94, 164, 104), "handle", "#4a4f55")
    lit(fig, block(0, 0, 156, 200, 6), fill)
    _tools(fig, 8, 148, 12, 116, TRAY, steel)
    lit(fig, box(3, 84, 153, 136), fill)
    fig.lines([((8 + 28 * k, 84), (8 + 28 * k, 136)) for k in range(1, 5)])
    _bits(fig, pieces, 14, 144, 142, 190)


def _bag(fig: Figure, fill: str, steel: str, pieces: int) -> None:
    """An open-top bag: two looped handles, tools standing in its mouth, bits on its front."""
    arch = arc((82, 78), 50, 180, 360, 10)
    fig.poly([*arch, *arc((82, 78), 41, 360, 180, 10)], "handle", "#4a4f55")
    fig.poly([(14, 66), (150, 66), (160, 90), (4, 90)], "handle", "#4a4f55")
    _tools(fig, 14, 150, 40, 110, "#d8b13b", steel)
    lit(fig, [(5, 84), (159, 84), (164, 192), (158, 200), (6, 200), (0, 192)], fill)
    fig.lines([((5, 92), (159, 92))])
    _bits(fig, pieces, 24, 108, 140, 188)


CONTAINERS = {
    "Blow-Molded Case": _molded,
    "Zippered Case": _zippered,
    "Plastic Tool Box": lambda *a: _toolbox(*a, metal=False),
    "Metal Tool Box": lambda *a: _toolbox(*a, metal=True),
    "Roll-Up Pouch": _roll,
    "Canvas Tool Bag": _bag,
}


def household_set(record: Record, fill: str, pieces: int, counts: tuple[int, ...]) -> Figure:
    """The set of ``pieces`` in ``fill``, open; ``counts`` are the piece counts it is sold in."""
    fig = Figure()
    steel = STEEL.get(str(record.get("Material", "")), STEEL["Carbon Steel"])
    draw = CONTAINERS.get(str(record.get("Container Type", "")), _molded)
    draw(fig, fill, steel, pieces)
    low, high = math.log(counts[0]), math.log(counts[-1])
    place = min(1.0, max(0.0, (math.log(pieces) - low) / (high - low)))
    return inches(fig, SMALLEST + (1 - SMALLEST) * place)


# --- the assortment kit --------------------------------------------------------------------------


def _rows(count: int, x0: float, x1: float) -> list[tuple[float, float]]:
    """The centre and width of each of ``count`` items across ``x0`` to ``x1``."""
    step = (x1 - x0) / count
    return [(x0 + step * (k + 0.5), min(0.62 * step, 14.0)) for k in range(count)]


def _keys(fig: Figure, count: int, x0, y0, x1, y1) -> None:
    """Hex keys: a short arm bent across the top of a long one, stepped by size."""
    bars, shades = [], []
    for k, (x, wide) in enumerate(_rows(count, x0, x1)):
        top = y1 - (y1 - y0) * (0.55 + 0.45 * (k + 1) / count)
        thick = wide * (0.3 + 0.3 * (k + 1) / count)
        bars.append((x - thick / 2, top, x + thick / 2, y1))
        bars.append((x - thick / 2, top, x + wide / 2 + thick / 2, top + thick))
        shades.append((x + thick / 6, top + thick, x + thick / 2, y1))
    _bars(fig, bars, shades)


def _drills(fig: Figure, count: int, x0, y0, x1, y1) -> None:
    """Drills: a fluted body, point up, stepped by size."""
    bars, shades, flutes = [], [], []
    for k, (x, wide) in enumerate(_rows(count, x0, x1)):
        top = y1 - (y1 - y0) * (0.5 + 0.5 * (k + 1) / count)
        half = wide * (0.3 + 0.7 * (k + 1) / count) / 2
        bars.append((x - half, top + half, x + half, y1))
        fig.poly([(x - half, top + half), (x, top), (x + half, top + half)], "part")
        shades.append((x + half / 3, top + half, x + half, y1))
        flutes += [((x - half, y), (x + half, y - 5)) for y in (top + 24, top + 40, top + 56)]
    _bars(fig, bars, shades)
    fig.lines(flutes)


def _taps(fig: Figure, count: int, x0, y0, x1, y1) -> None:
    """Taps: a threaded body, point up, on a thinner shank."""
    bars, shades, threads = [], [], []
    for k, (x, wide) in enumerate(_rows(count, x0, x1)):
        top = y1 - (y1 - y0) * (0.6 + 0.4 * (k + 1) / count)
        half = wide * (0.5 + 0.5 * (k + 1) / count) / 2
        mid = top + 0.5 * (y1 - top)
        bars += [(x - half, top, x + half, mid), (x - half * 0.6, mid, x + half * 0.6, y1)]
        shades.append((x + half / 3, top, x + half, mid))
        threads += [((x - half, y), (x + half, y - 2)) for y in range(int(top) + 6, int(mid), 6)]
    _bars(fig, bars, shades)
    fig.lines(threads)


def _screws(fig: Figure, count: int, x0, y0, x1, y1) -> None:
    """Socket head screws: a compartment for each size, the heads in it growing with the size."""
    cols = min(count, 3 if count <= 9 else 5)
    rows = math.ceil(count / cols)
    dx, dy = (x1 - x0) / cols, (y1 - y0) / rows
    for k in range(count):
        left, top = x0 + dx * (k % cols), y0 + dy * (k // cols)
        fig.poly(box(left + 1, top + 1, left + dx - 1, top + dy - 1), "handle", TRAY)
        radius = min(dx, dy) * (0.1 + 0.07 * (k + 1) / count)
        centres = [
            (left + dx * fx, top + dy * fy) for fx, fy in ((0.28, 0.3), (0.7, 0.34), (0.48, 0.72))
        ]
        fig.discs(centres, radius)
        fig.discs(centres, 0.45 * radius, "dark")


ITEMS = {"Hex Key Set": _keys, "Jobber Drill Set": _drills, "Tap Set": _taps}


def _bars(fig: Figure, bars, shades) -> None:
    fig.bars(bars)
    for rect in shades:
        fig.poly(box(*rect), "shade")


def _plastic(fig: Figure, fill: str, items, count: int) -> None:
    """A hinged case: a clear lid over its tray, and a latch."""
    lit(fig, block(0, 0, 164, 70, 8), fill)
    fig.poly(block(10, 8, 154, 62, 4), "handle", "#dbe7ee")
    fig.poly([(20, 62), (50, 8), (70, 8), (40, 62)], "gloss")
    lit(fig, block(0, 73, 164, 200, 8), fill)
    fig.poly(box(16, 82, 140, 190), "handle", TRAY)
    items(fig, count, 18, 86, 138, 188)
    fig.poly(box(70, 66, 94, 78), "dark")


def _index(fig: Figure, fill: str, items, count: int) -> None:
    """A folded steel index: side walls, a tilted rack and a lip along its foot."""
    lit(fig, [(14, 0), (150, 0), (164, 24), (164, 200), (0, 200), (0, 24)], fill)
    fig.poly(box(18, 26, 138, 186), "handle", TRAY)
    items(fig, count, 20, 32, 136, 184)
    lit(fig, box(0, 176, 164, 200), fill, across=True)
    fig.discs([(8, 188), (156, 188)], 3, "dark")


def _holder(fig: Figure, fill: str, items, count: int) -> None:
    """A folding holder: the items opened out of a grip with a screw at each end."""
    screws = items is _screws
    if not screws:
        items(fig, count, 14, 0, 150, 104)
    lit(fig, block(0, 26 if screws else 88, 164, 200, 12), fill)
    if screws:
        items(fig, count, 20, 44, 138, 182)
    else:
        fig.poly(block(24, 112, 136, 176, 8), "shade")
    fig.discs([(11, 188), (153, 188)], 5, "dark")


def _pouch(fig: Figure, fill: str, items, count: int) -> None:
    """A fabric pouch: its flap open behind the items, which stand in the pocket."""
    lit(fig, [(8, 0), (156, 0), (164, 20), (164, 200), (0, 200), (0, 20)], fill)
    screws = items is _screws
    if not screws:
        items(fig, count, 14, 14, 138, 140)
    lit(fig, block(0, 100, 164, 200, 5), fill)
    fig.lines([((5, 106), (159, 106)), ((5, 195), (159, 195))])
    if screws:
        items(fig, count, 20, 112, 138, 190)
    else:
        fig.disc((82, 150), 7, "dark")


KIT_CONTAINERS = {
    "Plastic Case": _plastic,
    "Metal Index": _index,
    "Folding Holder": _holder,
    "Pouch": _pouch,
}


def kit(record: Record) -> Drawn:
    """An assortment kit's container, open, with one item for each size it lists, up to 15."""
    container = str(record.get("Container Type", ""))
    if container not in KIT_CONTAINERS:
        container = "Plastic Case"
    items = ITEMS.get(str(record.get("Type", "")), _screws)
    fig = Figure()
    KIT_CONTAINERS[container](fig, SHELL[container], items, _kit_slots(record))
    return Drawn(inches(fig), "record" if record.get("Sizes Included") else "partial")

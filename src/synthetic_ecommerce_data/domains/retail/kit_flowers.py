"""Cut flower, house plant and plant food shapes for the retail drawing kit (gen#1115).

Each type has its own flat drawing in the kit's house style (the outlines in the kit's ink, the
record's fill on the product's main surface), and each param is the lower-cased value of the
attribute it draws, so a derived style that swaps a value is drawn true (gen#512).

============  ==============================================  =====================================
shape         draws                                           params
============  ==============================================  =====================================
cut_flowers   seven flower heads in the record's fill, on     flower (rose, tulip, lily, carnation,
              stems with leaves, hand-tied in a kraft cone    gerbera, mixed flower), pack
              or laid in a slim letterbox box                 (bouquet, letterbox)
house_plant   a house plant of its kind in a pot painted in   kind (orchid, echeveria, christmas
              the record's fill                               cactus, monstera, peace lily, snake
                                                              plant, pothos, calathea, spider
                                                              plant, aloe vera), pot (ceramic,
                                                              plastic, metal)
plant_food    a liquid feed bottle with a measuring cap, a    form (liquid, feed sticks, granules),
              carton of feed sticks or a tub of granules      plant (the plant it feeds: its leaf
              with a scoop, its pack in the record's fill     or fruit on the pack: house plant,
                                                              orchid, rose, cactus, tomato, citrus)
============  ==============================================  =====================================

The bloom is the record's color on a cut flower; a house plant's leaves and blooms are its own
and the pot takes the color. A drawing never prints a size: a style's stem counts, pot sizes and
pack sizes share one image.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

LEAF = "#5a8f4a"
KRAFT = "#c9a77c"
SOIL = "#5b4636"
CX = 200

FLOWERS = ("rose", "tulip", "lily", "carnation", "gerbera", "mixed flower")
PACKS = ("bouquet", "letterbox")
KINDS = (
    "orchid", "echeveria", "christmas cactus", "monstera", "peace lily", "snake plant", "pothos",
    "calathea", "spider plant", "aloe vera",
)  # fmt: skip
POTS = ("ceramic", "plastic", "metal")
FORMS = ("liquid", "feed sticks", "granules")
PLANTS = ("house plant", "orchid", "rose", "cactus", "tomato", "citrus")


def _pick(value: str, allowed: tuple[str, ...], what: str) -> str:
    if value not in allowed:
        raise ValueError(f"no {what} {value!r}: one of {', '.join(allowed)}")
    return value


# --------------------------------------------------------------------------
# Cut flowers
# --------------------------------------------------------------------------


def _petal(cx: float, cy: float, r: float, angle: float, length: float, width: float, paint: str) -> str:
    """One pointed petal from (cx, cy) at ``angle`` degrees."""
    a = math.radians(angle)
    tx, ty = cx + math.cos(a) * length * r, cy + math.sin(a) * length * r
    nx, ny = -math.sin(a) * width * r, math.cos(a) * width * r
    mx, my = cx + math.cos(a) * 0.5 * length * r, cy + math.sin(a) * 0.5 * length * r
    return _path(f"M{cx:.1f},{cy:.1f} Q{mx + nx:.1f},{my + ny:.1f} {tx:.1f},{ty:.1f} Q{mx - nx:.1f},{my - ny:.1f} {cx:.1f},{cy:.1f} Z", paint, LW_DETAIL)


def _head(flower: str, cx: float, cy: float, r: float, paint: str, base: str) -> list[str]:
    """One flower head of ``flower``, its petals in ``paint``."""
    dark = _shade(base, 0.35)
    if flower == "rose":
        return [
            _ell(cx, cy, r, r, paint, 2.4, ' class="bloom"'),
            _line(f"M{cx - 0.45 * r:.1f},{cy:.1f} Q{cx - 0.4 * r:.1f},{cy - 0.55 * r:.1f} {cx + 0.1 * r:.1f},{cy - 0.5 * r:.1f} "
                  f"Q{cx + 0.55 * r:.1f},{cy - 0.3 * r:.1f} {cx + 0.4 * r:.1f},{cy + 0.15 * r:.1f} Q{cx + 0.2 * r:.1f},{cy + 0.5 * r:.1f} {cx - 0.15 * r:.1f},{cy + 0.4 * r:.1f}", 1.6, stroke=dark),
        ]  # fmt: skip
    if flower == "tulip":  # a closed cup of three pointed petals
        return [
            _path(f"M{cx - r:.1f},{cy - 0.6 * r:.1f} Q{cx - r:.1f},{cy + r:.1f} {cx:.1f},{cy + r:.1f} Q{cx + r:.1f},{cy + r:.1f} {cx + r:.1f},{cy - 0.6 * r:.1f} "
                  f"L{cx + 0.45 * r:.1f},{cy - 0.1 * r:.1f} L{cx:.1f},{cy - r:.1f} L{cx - 0.45 * r:.1f},{cy - 0.1 * r:.1f} Z", paint, 2.4, ' class="bloom"'),
            _line(f"M{cx:.1f},{cy - 0.7 * r:.1f} L{cx:.1f},{cy + 0.8 * r:.1f}", 1.4, stroke=dark),
        ]  # fmt: skip
    if flower == "lily":  # six pointed petals and three stamens
        out = [_petal(cx, cy, r, 30 + 60 * i, 1.25, 0.32, paint) for i in range(6)]
        out += [_line(f"M{cx:.1f},{cy:.1f} L{cx + math.cos(math.radians(a)) * 0.8 * r:.1f},{cy + math.sin(math.radians(a)) * 0.8 * r:.1f}", 1.4, stroke="#7a4a2a") for a in (-120, -90, -60)]
        return [f'<g class="bloom">{"".join(out)}</g>']
    if flower == "carnation":  # a ruffled round head
        n = 14
        pts = []
        for i in range(n * 2):
            a = math.pi * i / n
            rr = r if i % 2 == 0 else 0.8 * r
            pts.append(f"{cx + math.cos(a) * rr:.1f},{cy + math.sin(a) * rr:.1f}")
        return [_path("M" + " L".join(pts) + " Z", paint, 2.4, ' class="bloom"'), _ell(cx, cy, 0.45 * r, 0.45 * r, "none", 1.2)]
    if flower == "gerbera":  # a ring of long petals round a dark disc
        out = [_petal(cx, cy, r, 360 / 16 * i, 1.1, 0.16, paint) for i in range(16)]
        return [f'<g class="bloom">{"".join(out)}</g>', _ell(cx, cy, 0.32 * r, 0.32 * r, "#4a3524", 1.6)]
    raise ValueError(f"no flower head {flower!r}")


def cut_flowers(paint: str, fill: Fill, label: str | None, flower: str = "rose", pack: str = "bouquet") -> list[str]:
    """Seven heads of ``flower`` (a mixed bouquet cycles rose, tulip, lily and gerbera) on stems,
    hand-tied in a kraft cone (``bouquet``) or laid flat in a slim box (``letterbox``)."""
    _pick(flower, FLOWERS, "flower")
    _pick(pack, PACKS, "pack")
    kinds = ("rose", "tulip", "lily", "gerbera") if flower == "mixed flower" else (flower,)
    if pack == "letterbox":  # the box seen from above, its lid open behind, the flowers laid in it
        heads = [(96.0 + 34 * i, 150.0 + (34 if i % 2 else 0)) for i in range(7)]
        out = [
            _path("M60,86 L340,86 L320,136 L80,136 Z", _tint(KRAFT, 0.2)),
            _rect(50, 136, 300, 170, KRAFT, 4),
            _rect(66, 150, 268, 142, _tint(KRAFT, 0.45), 2, LW_DETAIL),
        ]
        out += [_line(f"M{x:.1f},{y:.1f} L{150 + i * 16:.1f},286", 3.0, stroke=_shade(LEAF, 0.2)) for i, (x, y) in enumerate(heads)]
        out += [_path("M120,270 Q160,236 210,262 Q170,286 120,270 Z", LEAF, LW_DETAIL), _path("M232,268 Q270,238 300,262 Q262,284 232,268 Z", LEAF, LW_DETAIL)]
        r = 22.0
        out += [_rect(140, 270, 120, 16, "#e9e2d2", 3, LW_DETAIL), _line("M50,320 L350,320", 2)]
    else:
        heads = [(x, 120.0) for x in (140, 200, 260)] + [(x, 172.0) for x in (112, 170, 230, 288)]
        out = [_path("M78,212 L98,118 Q200,150 302,118 L322,212 Z", _tint(KRAFT, 0.25))]
        out += [_line(f"M{x:.1f},{y + 20:.1f} L{CX + (x - CX) * 0.12:.1f},360", 3.0, stroke=_shade(LEAF, 0.25)) for x, y in heads]
        out += [_path("M108,190 Q70,150 62,112 Q100,130 120,176 Z", LEAF, LW_DETAIL), _path("M292,190 Q330,150 338,112 Q300,130 280,176 Z", LEAF, LW_DETAIL)]
        r = 30.0
    for i, (x, y) in enumerate(heads):
        out += _head(kinds[i % len(kinds)], x, y, r, paint, fill.base)
    if pack == "bouquet":
        out += [
            _path("M66,198 Q200,236 334,198 L214,378 L186,378 Z", KRAFT),
            _line("M134,226 L194,372 M270,224 L210,372", 1.0, ' stroke-opacity=".45"'),
            _path("M130,290 L270,290 L261,306 L139,306 Z", "#d6b56a", LW_DETAIL),
        ]
    return _label(out, label)


# --------------------------------------------------------------------------
# House plants
# --------------------------------------------------------------------------


def _pot(paint: str, pot: str) -> list[str]:
    """The pot in the record's fill: a glazed ceramic, a ribbed plastic or a riveted metal one."""
    body = "M120,250 L280,250 L262,362 L138,362 Z"
    out = [_path(body, paint), _rect(112, 236, 176, 20, _shade(paint, 0.08), 4), _path("M128,240 L272,240 L272,248 L128,248 Z", SOIL, 1.0)]
    if pot == "ceramic":
        out.append(_highlight("M136,262 L148,350", 7, 0.45))
    elif pot == "plastic":
        out.append(_line(" ".join(f"M{124 + i * 2.4:.1f},{270 + i * 22} L{276 - i * 2.4:.1f},{270 + i * 22}" for i in range(4)), 1.4))
    elif pot == "metal":
        out += [_line("M126,286 L274,286 M132,330 L268,330", 2.4), *[_ell(x, y, 3, 3, _tint(paint, 0.5), 1.0) for y in (286, 330) for x in (150, 200, 250)]]
    else:
        raise ValueError(f"no pot {pot!r}: one of {', '.join(POTS)}")
    return out


def _blade(x: float, base: float, top: float, lean: float, w: float, color: str) -> str:
    return _path(f"M{x - w:.1f},{base:.1f} Q{x - w + lean:.1f},{(base + top) / 2:.1f} {x + lean:.1f},{top:.1f} Q{x + w + lean:.1f},{(base + top) / 2:.1f} {x + w:.1f},{base:.1f} Z", color, LW_DETAIL)


def _oval_leaf(cx: float, cy: float, rx: float, ry: float, angle: float, color: str, vein: bool = True) -> str:
    g = f'<g transform="rotate({angle:g} {cx:.1f} {cy:.1f})">{_ell(cx, cy, rx, ry, color, LW_DETAIL)}'
    if vein:
        g += _line(f"M{cx - rx * 0.85:.1f},{cy:.1f} L{cx + rx * 0.85:.1f},{cy:.1f}", 1.2, stroke=_shade(color, 0.35))
    return g + "</g>"


def _plant(kind: str) -> list[str]:
    """The plant of ``kind`` above the pot rim at y=240."""
    if kind == "orchid":  # broad basal leaves, a staked arching stem of moth-shaped blooms
        out = [_oval_leaf(160, 228, 44, 13, -12, "#4f7d3a"), _oval_leaf(240, 228, 44, 13, 12, "#4f7d3a"), _line("M200,236 L200,90", 2.4, stroke="#6b5a3a")]
        out.append(_line("M200,110 Q250,80 290,120", 2.4, stroke="#5f7d3a"))
        for x, y in ((214, 100), (240, 90), (264, 98), (284, 116), (200, 140)):
            out += [_petal(x, y, 16, a, 1.0, 0.5, "#f3eef6") for a in (0, 90, 180, 270)] + [_ell(x, y, 4, 4, "#b8327a", 1.0)]
        return out
    if kind == "echeveria":  # a low rosette of thick pointed leaves
        out = [_petal(CX, 214, 34, a, 1.9, 0.4, "#8fb3a3") for a in range(0, 360, 30)]
        return out + [_petal(CX, 214, 22, a + 15, 1.6, 0.42, "#a9c7b6") for a in range(0, 360, 45)]
    if kind == "christmas cactus":  # arching chains of flat segments, a bloom at each tip
        out = []
        for side in (-1, 1):
            for k, lift in enumerate((0, 40)):
                x, y = CX, 236.0
                for _ in range(4):
                    nx, ny = x + side * 26, y - 22 + lift * 0.2 - k * 6
                    out.append(_oval_leaf((x + nx) / 2, (y + ny) / 2, 16, 8, math.degrees(math.atan2(ny - y, nx - x)), "#4f8a45", False))
                    x, y = nx, ny
                out += [_petal(x, y, 12, -90 + side * a, 1.4, 0.3, "#d8336f") for a in (-25, 0, 25)]
        return out
    if kind == "monstera":  # big split heart leaves on long stalks
        out = []
        for x, y, ang in ((140, 140, -25), (200, 100, 0), (262, 140, 25)):
            out.append(_line(f"M200,240 Q{(200 + x) / 2:.0f},{y + 60} {x},{y + 34}", 3, stroke="#3f6e2e"))
            out.append(_oval_leaf(x, y, 52, 40, ang, "#2f6b2a", False))
            out.append(_line(" ".join(f"M{x + dx:.0f},{y + 40} L{x + dx * 1.3:.0f},{y + 12}" for dx in (-30, -12, 12, 30)), 3.2, stroke="#fbfaf6"))
        return out
    if kind == "peace lily":  # glossy lance leaves and white spathes on stalks
        out = [_blade(x, 238, top, lean, 16, "#2f6b33") for x, top, lean in ((150, 120, -30), (180, 96, -10), (220, 96, 10), (250, 120, 30))]
        for x, y in ((176, 76), (226, 84)):
            out += [_line(f"M{x},{y + 30} L{x + (200 - x) * 0.2:.0f},236", 2.2, stroke="#3f6e2e"), _petal(x, y + 30, 26, -90, 1.6, 0.45, "#f7f6ef"), _line(f"M{x},{y + 22} L{x},{y + 2}", 4, stroke="#e8dca0")]
        return out
    if kind == "snake plant":  # stiff upright banded blades
        out = []
        for x, top, lean in ((150, 96, -14), (178, 60, -4), (206, 50, 4), (234, 74, 10), (258, 110, 18)):
            out.append(_blade(x, 240, top, lean, 13, "#3d6b3a"))
            out.append(_line(" ".join(f"M{x - 9 + lean * (240 - y) / (240 - top):.0f},{y} L{x + 9 + lean * (240 - y) / (240 - top):.0f},{y - 6}" for y in range(220, top + 20, -26)), 1.4, stroke="#a7c48c"))
        return out
    if kind == "pothos":  # trailing vines of heart leaves over the rim
        out = []
        for side in (-1, 1):
            out.append(_line(f"M200,238 Q{200 + side * 110},236 {200 + side * 104},360", 2.2, stroke="#4f7d3a"))
            for t, (dx, dy) in enumerate(((60, 238), (92, 270), (100, 310), (104, 350))):
                out.append(_oval_leaf(200 + side * dx, dy, 18, 13, side * (20 + 15 * t), "#5d9a3c"))
        return out + [_oval_leaf(x, y, 22, 15, a, "#6aa845") for x, y, a in ((176, 214, -30), (224, 214, 30), (200, 196, 90))]
    if kind == "calathea":  # upright oval leaves striped dark and light
        out = []
        for x, y, ang in ((150, 170, -60), (200, 140, -90), (250, 170, -120), (176, 196, -40), (224, 196, -140)):
            out.append(_oval_leaf(x, y, 40, 20, ang, "#4a7a45"))
            out.append(f'<g transform="rotate({ang:g} {x} {y})">' + _line(" ".join(f"M{x + dx},{y - 14} L{x + dx},{y + 14}" for dx in (-22, -10, 2, 14)), 3, stroke="#203d22") + "</g>")
        return out
    if kind == "spider plant":  # arching thin striped leaves and a plantlet on a runner
        out = []
        for ang in (-150, -125, -105, -90, -75, -55, -30):
            a = math.radians(ang)
            tx, ty = CX + math.cos(a) * 120, 236 + math.sin(a) * 90 + 50
            out.append(_line(f"M200,236 Q{CX + math.cos(a) * 70:.0f},{236 + math.sin(a) * 110:.0f} {tx:.0f},{ty:.0f}", 7, stroke="#4f8a3f"))
            out.append(_line(f"M200,236 Q{CX + math.cos(a) * 70:.0f},{236 + math.sin(a) * 110:.0f} {tx:.0f},{ty:.0f}", 2, stroke="#e6efc8"))
        out.append(_line("M200,236 Q330,200 320,320", 1.6, stroke="#8a9a5a"))
        return out + [_petal(320, 320, 12, a, 1.5, 0.25, "#4f8a3f") for a in (-150, -90, -30)]
    if kind == "aloe vera":  # thick upright toothed spears
        out = []
        for x, top, lean in ((150, 120, -50), (176, 90, -20), (200, 76, 0), (224, 90, 20), (250, 120, 50)):
            out.append(_blade(x, 240, top, lean, 15, "#7da36a"))
            out.append(_line(" ".join(f"M{x - 15 + lean * (240 - y) / (240 - top):.0f},{y} l-5,-3" for y in range(226, top + 24, -22)), 1.4))
        return out
    raise ValueError(f"no house plant {kind!r}: one of {', '.join(KINDS)}")


def house_plant(paint: str, fill: Fill, label: str | None, kind: str = "monstera", pot: str = "ceramic") -> list[str]:
    """A house plant of ``kind`` in a ``pot`` painted in the record's fill."""
    _pick(pot, POTS, "pot")
    out = [_line("M60,364 L340,364", 3)]
    out += _plant(_pick(kind, KINDS, "house plant"))
    out += _pot(paint, pot)
    return _label(out, label)


# --------------------------------------------------------------------------
# Plant food
# --------------------------------------------------------------------------


def _motif(plant: str, cx: float, cy: float) -> list[str]:
    """The plant a feed is for, on its pack: a bloom for a flowering plant, else a leaf."""
    if plant in ("orchid", "rose"):
        head = "rose" if plant == "rose" else "lily"
        return _head(head, cx, cy, 20, "#d8336f" if plant == "rose" else "#f3eef6", "#d8336f")
    if plant == "cactus":
        return [_rect(cx - 10, cy - 28, 20, 52, "#4f8a45", 10, LW_DETAIL), _rect(cx - 26, cy - 8, 12, 24, "#4f8a45", 6, LW_DETAIL)]
    if plant == "tomato":
        return [_ell(cx, cy, 20, 18, "#d23a2a", LW_DETAIL), _path(f"M{cx - 10},{cy - 16} L{cx},{cy - 10} L{cx + 10},{cy - 16} L{cx + 4},{cy - 8} Z", LEAF, 1.0)]
    if plant == "citrus":
        return [_ell(cx + 6, cy + 6, 20, 20, "#f0a020", LW_DETAIL), _oval_leaf(cx - 14, cy - 16, 16, 8, -30, LEAF)]
    if plant != "house plant":
        raise ValueError(f"no plant food motif {plant!r}: one of {', '.join(PLANTS)}")
    return [_oval_leaf(cx - 10, cy, 22, 11, -35, LEAF), _oval_leaf(cx + 12, cy + 4, 20, 10, 30, "#6aa845")]


def plant_food(paint: str, fill: Fill, label: str | None, form: str = "liquid", plant: str = "house plant") -> list[str]:
    """A ``liquid`` feed bottle with a measuring cap, a carton of ``feed sticks`` with three
    sticks out of its top, or a tub of ``granules`` with a scoop; its pack in the record's fill
    and the plant it feeds on its panel."""
    _pick(form, FORMS, "plant food form")
    out = [_line("M60,364 L340,364", 3)]
    if form == "liquid":
        out += [
            _path("M140,150 Q140,120 172,112 L228,112 Q260,120 260,150 L260,350 Q260,362 248,362 L152,362 Q140,362 140,350 Z", paint),
            _rect(176, 72, 48, 42, _shade(paint, 0.25), 5),
            _rect(162, 200, 76, 110, "#fbfaf6", 6, LW_DETAIL),
            _highlight("M150,160 L150,340", 6, 0.4),
        ]
        cx, cy = 200, 250
    elif form == "feed sticks":
        out += [_line(f"M{x},{150} L{x},{86}", 6, stroke="#7ab648") for x in (170, 196, 222)]
        out += [_path("M122,150 L278,150 L278,362 L122,362 Z", paint), _path("M122,150 L148,128 L304,128 L278,150 Z", _tint(paint, 0.3)),
                _path("M278,150 L304,128 L304,340 L278,362 Z", _shade(paint, 0.2)), _rect(140, 196, 120, 120, "#fbfaf6", 6, LW_DETAIL)]  # fmt: skip
        cx, cy = 200, 256
    else:
        out += [
            _path("M110,180 L290,180 L276,362 L124,362 Z", paint),
            _rect(102, 160, 196, 26, _shade(paint, 0.2), 6),
            _rect(148, 220, 104, 100, "#fbfaf6", 6, LW_DETAIL),
            _path("M232,150 L300,96 L316,112 L250,160 Z", "#e9e2d2", LW_DETAIL),
            *[_ell(x, y, 4, 4, "#8a6a4a", 1.0) for x, y in ((250, 150), (262, 144), (240, 156))],
        ]
        cx, cy = 200, 266
    out += _motif(plant, cx, cy)
    return _label(out, label)


SHAPES = {"cut_flowers": cut_flowers, "house_plant": house_plant, "plant_food": plant_food}
register(SHAPES)

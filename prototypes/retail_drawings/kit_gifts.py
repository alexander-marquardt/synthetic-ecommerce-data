"""Gift shapes for the retail drawing kit (gen#425): a mug, a greeting card, a notebook, a money box
and a pamper hamper, each drawn as its own product (not a recolored neighbour).

==============  ==========================================  ==============================
shape           draws                                       params
==============  ==========================================  ==============================
gift_mug        a tapered mug with a handle and a design    design (slogan, initial,
                on its side                                 pattern, plain), material
                                                            (ceramic, stoneware, enamel)
greeting_card   a card stood open before its envelope,      occasion (birthday,
                with the occasion's motif on the front      anniversary, thank_you,
                                                            wedding, new_baby, christmas)
notebook        an open notebook: two ruled pages in a      ruling (lined, dotted, plain),
                cover, the cover's edge and stitching       cover (hardback, softback,
                showing its kind                            leather)
money_box       a pig, a rocket or a house with a coin      form (pig, rocket, house),
                slot (one ``class="slot"``)                 material (ceramic, tin, wood)
gift_hamper     a lidless basket with a ribbon and the      contents (bath_body,
                things it holds sticking out                candle_diffuser, sock_slipper)
==============  ==========================================  ==============================

A drawing never prints a capacity, a size or a price. Every param is a string with a default.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import FONT, INK, Fill, _highlight, _line, _path, _shade, _tint, register
from kit_sports import PAPER2, _ell, _label, _rect

SLOT_CLASS = "slot"
RIBBON = "#c8312e"


def gift_mug(
    paint: str, fill: Fill, label: str | None, design: str = "plain", material: str = "ceramic"
) -> list[str]:
    """A mug: a tapered body, a ring handle and a design (``slogan`` bars, an ``initial``, a ``pattern`` of dots)."""
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M290,150 C350,150 350,262 286,262", "none", 16),
        _path("M290,150 C350,150 350,262 286,262", "none", 7, stroke=dark),
        _path("M100,120 L300,120 L282,300 C280,318 120,318 118,300 Z", paint),
        _ell(200, 120, 100, 20, _tint(fill.base, 0.35)),
        _ell(200, 120, 84, 13, dark, 2),
    ]
    if design == "slogan":
        out += [
            _rect(140, 170, 120, 14, PAPER2, 7, 1.6),
            _rect(158, 198, 84, 14, PAPER2, 7, 1.6),
            _rect(146, 226, 108, 14, PAPER2, 7, 1.6),
        ]
    elif design == "initial":
        out += [
            _ell(200, 208, 42, 42, PAPER2, 2),
            f'<text x="200" y="228" text-anchor="middle" font-family="{FONT}" font-size="58" font-weight="700" fill="{INK}">A</text>',
        ]
    elif design == "pattern":
        out += [
            _ell(x, y, 8, 8, PAPER2, 1.6)
            for y, xs in ((176, (150, 200, 250)), (214, (175, 225)), (252, (150, 200, 250)))
            for x in xs
        ]
    if material == "enamel":
        out.append(_line("M101,132 C140,142 260,142 299,132", 5, "", INK))
    elif material == "stoneware":
        out += [
            _ell(x, y, 2.4, 2.4, dark, 0)
            for x, y in ((130, 160), (262, 190), (146, 270), (240, 282), (180, 150))
        ]
    else:
        out.append(_highlight("M124,150 L134,280", 6, 0.55))
    return _label(out, label)


def _motif(occasion: str) -> list[str]:
    """The occasion's motif, centered near (200, 190) in white."""
    w = PAPER2
    if occasion == "anniversary":
        return [_path("M200,236 C140,196 160,150 200,176 C240,150 260,196 200,236 Z", w, 2.4)]
    if occasion == "thank_you":
        return [
            _ell(200 + dx, 190 + dy, 18, 18, w, 2)
            for dx, dy in ((0, -26), (26, 0), (0, 26), (-26, 0))
        ] + [_ell(200, 190, 12, 12, "#f2c230", 2)]
    if occasion == "wedding":
        return [_ell(180, 196, 30, 30, "none", 6), _ell(222, 196, 30, 30, "none", 6)]
    if occasion == "new_baby":
        return [
            _path("M214,150 A44,44 0 1,0 214,236 A32,32 0 1,1 214,150 Z", w, 2.4),
            _path(
                "M236,160 L242,176 L258,176 L246,186 L250,202 L236,192 L222,202 L226,186 L214,176 L230,176 Z",
                "#f2c230",
                2,
            ),
        ]
    if occasion == "christmas":
        return [
            _path("M200,140 L240,190 L216,190 L252,232 L148,232 L184,190 L160,190 Z", w, 2.4),
            _rect(192, 232, 16, 18, "#8a5a2b", 2, 2),
        ]
    return [
        _ell(200, 176, 34, 42, w, 2.4),
        _line("M200,218 C186,236 214,246 200,262", 2.4),
        _path("M194,218 L206,218 L200,210 Z", w, 2),
    ]


def greeting_card(
    paint: str, fill: Fill, label: str | None, occasion: str = "birthday"
) -> list[str]:
    """A card standing open before its envelope; the front carries the occasion's motif."""
    out = [
        _path("M84,150 L316,150 L316,326 L84,326 Z", PAPER2),
        _path("M84,150 L200,244 L316,150", "none", 2.4),
        _path("M118,92 L330,104 L330,300 L118,300 Z", _shade(fill.base, 0.2)),
        _path("M132,100 L318,100 L318,304 L132,304 Z", paint),
        _line("M132,100 L132,304", 3),
    ]
    out += _motif(occasion)
    out.append(_line("M170,274 L280,274", 3, "", PAPER2))
    return _label(out, label)


def notebook(
    paint: str, fill: Fill, label: str | None, ruling: str = "lined", cover: str = "hardback"
) -> list[str]:
    """An open notebook: two ruled pages inside a cover whose edge shows hardback, softback or leather-effect."""
    edge = {"hardback": 16, "softback": 6, "leather": 11}.get(cover, 11)
    out = [
        _path(
            f"M{60 - edge},{70 - edge} L{340 + edge},{70 - edge} L{340 + edge},{320 + edge} L{60 - edge},{320 + edge} Z",
            paint,
        ),
        _path("M60,70 L196,70 L196,320 L60,320 Z", PAPER2),
        _path("M204,70 L340,70 L340,320 L204,320 Z", PAPER2),
        _line("M200,70 L200,320", 5, "", _shade(fill.base, 0.4)),
    ]
    for x0 in (60, 204):
        if ruling == "lined":
            out += [
                _line(f"M{x0 + 10},{y} L{x0 + 126},{y}", 1.6, ' stroke-opacity=".6"', "#6d86a8")
                for y in range(100, 310, 24)
            ]
        elif ruling == "dotted":
            out += [
                _ell(x, y, 1.8, 1.8, "#6d86a8", 0)
                for y in range(100, 310, 20)
                for x in range(x0 + 14, x0 + 130, 20)
            ]
    if cover == "leather":
        out.append(
            _line(
                f"M{60 - edge // 2},{70 - edge // 2} L{340 + edge // 2},{70 - edge // 2} L{340 + edge // 2},{320 + edge // 2} L{60 - edge // 2},{320 + edge // 2} Z",
                1.6,
                ' stroke-dasharray="6 4" class="stitch"',
                _tint(fill.base, 0.6),
            )
        )
    return _label(out, label)


def money_box(
    paint: str, fill: Fill, label: str | None, form: str = "pig", material: str = "ceramic"
) -> list[str]:
    """A money box: a ``pig`` (snout, ears, legs, curly tail), a ``rocket`` (nose cone and fins) or a ``house`` (roof and door), with a coin slot."""
    dark = _shade(fill.base, 0.3)
    slot = f'<rect class="{SLOT_CLASS}" x="%s" y="%s" width="%s" height="%s" rx="4" fill="{INK}"/>'
    if form == "rocket":
        out = [
            _path("M150,300 L90,350 L150,230 Z", dark),
            _path("M250,300 L310,350 L250,230 Z", dark),
            _path("M200,40 C270,100 270,230 250,320 L150,320 C130,230 130,100 200,40 Z", paint),
            _ell(200, 150, 28, 28, "#dbe9f2", 2.4),
            slot % (176, 214, 48, 9),
            _path("M150,320 L250,320 L240,350 L160,350 Z", dark),
        ]
    elif form == "house":
        out = [
            _path("M90,200 L310,200 L310,336 L90,336 Z", paint),
            _path("M70,206 L200,90 L330,206 Z", dark),
            _rect(176, 262, 48, 74, _tint(fill.base, 0.4), 4, 2.4),
            slot % (170, 188, 60, 9),
            _rect(110, 224, 40, 34, "#dbe9f2", 2, 2),
        ]
    else:
        out = [
            _path("M130,140 L146,98 L176,134 Z", dark),
            _ell(196, 224, 118, 92, paint),
            _ell(310, 232, 38, 32, _tint(fill.base, 0.35), 2.4),
            _ell(302, 232, 4, 6, INK, 1),
            _ell(318, 232, 4, 6, INK, 1),
        ]
        out += [_rect(x, 292, 30, 44, dark, 8, 2.4) for x in (130, 220)] + [
            slot % (170, 140, 56, 9),
            _line("M80,210 C56,196 70,170 84,184", 4),
        ]
    if material == "tin":
        out += [_line(f"M120,{y} L280,{y}", 1.6, ' stroke-opacity=".5"') for y in (190, 250)]
    elif material == "wood":
        out += [
            _line(f"M130,{y} C170,{y - 8} 230,{y + 8} 270,{y}", 1.6, ' stroke-opacity=".5"', dark)
            for y in (200, 240, 280)
        ]
    else:
        out.append(_highlight("M130,200 C140,180 160,170 180,168", 6, 0.55))
    return _label(out, label)


def gift_hamper(
    paint: str, fill: Fill, label: str | None, contents: str = "bath_body"
) -> list[str]:
    """A lidless basket tied with a ribbon; ``bath_body`` shows bottles and soap, ``candle_diffuser`` a candle jar and a reed diffuser, ``sock_slipper`` rolled socks and a slipper."""
    dark = _shade(fill.base, 0.3)
    if contents == "candle_diffuser":
        items = [
            _rect(120, 130, 80, 80, "#f2e6c9", 10),
            _line("M160,130 L160,112", 3),
            _rect(236, 148, 34, 62, "#9ec7d8", 8),
            *[_line(f"M253,148 L{x},84", 2.4) for x in (236, 253, 270)],
        ]
    elif contents == "sock_slipper":
        items = [
            _ell(140, 180, 36, 30, "#f2c230", 2.4),
            _ell(196, 176, 32, 28, "#9ec7d8", 2.4),
            _path("M230,206 C230,150 300,150 300,206 Z", "#d9b98a", 2.4),
            _line("M240,176 L290,176", 2.4),
        ]
    else:
        items = [
            _rect(128, 100, 34, 110, "#9ec7d8", 8),
            _rect(176, 126, 30, 84, "#f2b8c6", 8),
            _rect(222, 168, 62, 40, "#fbfaf6", 8),
            _line("M232,184 L274,184", 2),
        ]
    out = [
        *items,
        _path("M90,200 L310,200 L286,330 L114,330 Z", paint),
        _path("M72,196 L328,196 L328,214 L72,214 Z", dark),
        *[
            _line(f"M{x},214 L{x - 8},330", 1.6, ' stroke-opacity=".5"', dark)
            for x in range(130, 280, 28)
        ],
        _line("M96,258 L304,258", 1.6, ' stroke-opacity=".5"', dark),
        _path("M200,214 C170,174 150,222 200,214 C250,222 230,174 200,214 Z", RIBBON, 2.4),
        _path("M200,214 L184,264 M200,214 L216,264", "none", 4, stroke=RIBBON),
    ]
    return _label(out, label)


SHAPES = {
    "gift_mug": gift_mug,
    "greeting_card": greeting_card,
    "notebook": notebook,
    "money_box": money_box,
    "gift_hamper": gift_hamper,
}
register(SHAPES)

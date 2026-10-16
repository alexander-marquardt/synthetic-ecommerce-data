"""Drawings of five ordinary products whose names hold a Toys word (gen#424, class 8 of #326).

==================  ==========================================  ======
shape               what it draws                               params
==================  ==========================================  ======
kitchen_scales      a flat platform on a body with a dial       none
greeting_card       a folded card standing open, a heart on it  none
gift_card           a flat card with a strip and a ribbon bow   none
glue_gun            a pistol with a nozzle and a glue stick     none
caulking_gun        a frame with a cartridge, rod and trigger   none
==================  ==========================================  ======

A kitchen roll reuses ``wrapping_paper`` (a roll of paper). No drawing prints a number.
"""

from __future__ import annotations

from kit import Fill, _highlight, _line, _path, _shade, _tint, register
from kit_sports import _ell, _label, _rect

METAL, GLASS = "#b9bdc4", "#cfe3ee"


def kitchen_scales(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Kitchen scales: a platform on a body whose face carries a dial and a needle."""
    out = [
        _rect(60, 120, 280, 24, METAL, 10),
        _path("M90,144 L310,144 L340,330 L60,330 Z", paint),
        _ell(200, 235, 62, 62, "#f4f1ea"),
        _line("M200,235 L236,198", 4),
        _line("M200,183 L200,195 M148,235 L160,235 M240,235 L252,235", 3),
    ]
    out.append(_highlight("M96,160 L112,300", 6, 0.35))
    return _label(out, label)


def greeting_card(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A greeting card standing open on its fold, a heart on the front."""
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M60,120 L200,100 L200,330 L60,350 Z", _tint(fill.base, 0.5)),
        _path("M200,100 L340,120 L340,350 L200,330 Z", paint),
        _path(
            "M200,240 C170,205 140,235 160,262 L200,296 L240,262 C260,235 230,205 200,240 Z",
            dark,
            2.6,
        ),
    ]
    return _label(out, label)


def gift_card(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A gift card: a flat plastic card with a stripe and a ribbon bow in the corner."""
    out = [
        _rect(40, 110, 320, 200, paint, 18),
        _rect(40, 150, 320, 34, _shade(fill.base, 0.3), 0),
        _path("M270,250 L310,230 L310,270 Z M270,250 L230,230 L230,270 Z", _tint(fill.base, 0.5)),
        _ell(270, 250, 12, 12, _tint(fill.base, 0.4)),
    ]
    out.append(_highlight("M60,128 L300,128", 4, 0.4))
    return _label(out, label)


def glue_gun(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A hot glue gun: a pistol body, a metal nozzle, a glue stick at the back and a trigger."""
    dark = _shade(fill.base, 0.3)
    out = [
        _rect(20, 150, 130, 18, "#f4f1ea", 6),
        _rect(130, 120, 190, 70, paint, 24),
        _path("M320,140 L372,168 L320,176 Z", METAL),
        _rect(318, 150, 30, 18, dark, 4),
        _path("M170,190 L150,320 L214,320 L226,190 Z", dark),
        _path("M232,190 Q248,230 262,206", "none", 4),
    ]
    return _label(out, label)


def caulking_gun(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A caulking gun: a cartridge in an open frame, a plunger rod and a trigger handle."""
    dark = _shade(fill.base, 0.3)
    out = [
        _rect(120, 110, 200, 56, "#f4f1ea", 14),
        _path("M320,124 L362,138 L320,152 Z", METAL),
        _line("M40,138 L120,138", 8),
        _rect(26, 124, 22, 28, dark, 5),
        _path("M120,166 L120,200 L240,200 L240,166 Z", paint),
        _path("M140,200 L120,310 L176,310 L192,200 Z", dark),
        _path("M206,200 L222,300 L254,296 L240,200 Z", paint),
    ]
    return _label(out, label)


SHAPES = {
    "kitchen_scales": kitchen_scales,
    "greeting_card": greeting_card,
    "gift_card": gift_card,
    "glue_gun": glue_gun,
    "caulking_gun": caulking_gun,
}
register(SHAPES)

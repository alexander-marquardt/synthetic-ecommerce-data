"""Pliers for the retail drawing kit (gen#1130): one shape, six jaws.

The handles carry the record's fill; the jaw is the kind the title names:

=============  ==============================================
jaw            draws
=============  ==============================================
combination    a blunt square jaw with a gripping flat
long_nose      two long tapering jaws
side_cutter    a short round head with a cutting slot
pump           a long angled jaw with an adjusting slot
slip_joint     a blunt jaw with a two-position pivot
locking        a wide jaw with a lever and an adjusting screw
=============  ==============================================

Every param is a string with a default, so the shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import Fill, _line, _path, _tint, register
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

METAL = "#aeb4bb"
PIVOT = (200, 176)

#: The pivot-to-tip outline of each jaw, left and right halves mirrored about x=200.
JAWS = {
    "combination": "M{a},176 L{b},120 L{b},76 L{c},60 L200,60 L200,176 Z",
    "long_nose": "M{a},176 L{b},130 L{c},44 L{c},38 L200,38 L200,176 Z",
    "side_cutter": "M{a},176 L{b},140 L{b},106 L{c},88 L200,88 L200,176 Z",
    "pump": "M{a},176 L{b},120 L{c},72 L{c},54 L200,48 L200,176 Z",
    "slip_joint": "M{a},176 L{b},128 L{b},92 L{c},74 L200,74 L200,176 Z",
    "locking": "M{a},176 L{b},118 L{b},74 L{c},58 L200,58 L200,176 Z",
}
#: Half-widths (a at the pivot, b at the shoulder, c at the tip) per jaw.
WIDTHS = {
    "combination": (30, 34, 18),
    "long_nose": (26, 24, 5),
    "side_cutter": (30, 34, 10),
    "pump": (24, 40, 30),
    "slip_joint": (28, 32, 16),
    "locking": (34, 40, 26),
}


def pliers(
    paint: str, fill: Fill, label: str | None, jaw: str = "combination", size: str = "standard"
) -> list[str]:
    """A pair of pliers: two handles in the record's fill and a jaw of the kind ``jaw`` names.
    ``size`` is the length in the title (``short``, ``standard``, ``long``): the handles' length."""
    kind = jaw if jaw in JAWS else "combination"
    foot = {"short": 310, "standard": 340, "long": 366}.get(size, 340)
    a, b, c = WIDTHS[kind]
    out: list[str] = []
    for side in (-1, 1):
        out.append(
            _path(
                JAWS[kind].format(a=200 + side * a, b=200 + side * b, c=200 + side * c), METAL, 1.8
            )
        )
        out.append(
            _path(
                f"M{200 + side * 10},188 C{200 + side * 70},214 {200 + side * 96},262 {200 + side * 88},{foot - 14} Q{200 + side * 86},{foot} {200 + side * 70},{foot} L{200 + side * 64},{foot} "
                f"C{200 + side * 64},{foot - 60} {200 + side * 46},236 {200 + side * 2},200 Z",
                paint,
            )
        )
        out.append(
            _line(
                f"M{200 + side * 44},222 Q{200 + side * 76},262 {200 + side * 74},{foot - 24}",
                3.4,
                stroke=_tint(fill.base, 0.4),
            )
        )
    tip = {
        "combination": 60,
        "long_nose": 38,
        "side_cutter": 88,
        "pump": 48,
        "slip_joint": 74,
        "locking": 58,
    }[kind]
    if kind == "side_cutter":
        out += [_path(f"M{194},{tip} L206,{tip} L203,158 L197,158 Z", "#6f767e", 1.4)]
    elif kind != "long_nose":
        out += [
            _line(f"M{200 - c + 3},{y} L{200 + c - 3},{y}", 1.8) for y in range(tip + 14, 112, 12)
        ]
    if kind == "pump":
        out.append(_rect(188, 124, 24, 46, "none", 8, 2))
        out += [_line(f"M188,{y} L212,{y}", 1.4) for y in (136, 148, 160)]
    elif kind == "slip_joint":
        out += [_ell(200, 148, 8, 8, "#ffffff", 1.8)]
    elif kind == "locking":
        out += [
            _path(f"M196,200 L204,200 L176,{foot - 62} L150,{foot - 90} Z", METAL, 1.8),
            _rect(200 + 60, foot - 6, 20, 16, METAL, 4, 1.6),
            _line(f"M270,{foot + 10} L270,{foot + 16}", 5),
        ]
    out += [_ell(*PIVOT, 14, 14, METAL, 2), _ell(*PIVOT, 4, 4, "none", 1.6)]
    return _label(out, label)


register({"pliers": pliers})

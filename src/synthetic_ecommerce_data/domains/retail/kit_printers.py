"""Printers and ink for the retail drawing kit (gen#956, slice 3b).

=============  =========================================  =========================================
shape          draws                                      params
=============  =========================================  =========================================
printer        a printer body with a paper tray and a     printer_type (inkjet, laser),
               sheet coming out; ``laser`` is a deep      printer_function (photo, multifunction)
               box with a toner door, ``inkjet`` a low
               wide one; ``multifunction`` adds a
               scanner lid, ``photo`` a photo on the
               sheet
ink_cartridge  a cartridge whose ink window shows the     ink_yield (standard, xl),
               SKU's color; ``xl`` is a taller body with  ink_formula (dye, pigment)
               a long window; a drop on the label for
               ``dye``, a hatched band for ``pigment``
=============  =========================================  =========================================

Each param's values are the lower-cased attribute values of the spec rows. A derived style that
changes any of these params draws what it states (gen#512).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The paper's white, the output slot's and the nozzle's dark plastic, a photo's sky and hill.
PAPER = "#fbfbf7"
SLOT = "#3a3b40"
SKY = "#7cc4e8"
HILL = "#5aa65a"
#: The cartridge's grey shell and the label's white.
SHELL = "#c9ccd2"
LABEL = "#f4f4f1"


def printer(paint: str, fill: Fill, label: str | None, printer_type: str = "inkjet",
            printer_function: str = "multifunction") -> list[str]:  # fmt: skip
    """A printer by ``printer_type``, with a scanner lid or a photo on its sheet."""
    if printer_type == "laser":
        x, y, w, h = 80.0, 150.0, 240.0, 170.0
    else:
        x, y, w, h = 60.0, 190.0, 280.0, 120.0
    sheet = (f"M{x + 50},{y + h - 24} L{x + w - 50},{y + h - 24} L{x + w - 30},{y + h + 30} "
             f"L{x + 30},{y + h + 30} Z")  # fmt: skip
    out = [
        _rect(x + 40, y - 70, w - 80, 90, PAPER, 4, LW_DETAIL),
        _rect(x, y, w, h, paint, 18),
        _rect(x + 30, y + h - 34, w - 60, 14, SLOT, 4, LW_DETAIL),
        _path(sheet, PAPER, LW_DETAIL),
    ]
    if printer_type == "laser":
        out.append(_rect(x + 24, y + 30, w - 48, 60, _shade(fill.base, 0.3), 8, LW_DETAIL))
    else:
        out.append(_line(f"M{x + 20},{y + 40} L{x + w - 20},{y + 40}", 3.0))
    if printer_function == "multifunction":
        out.append(_rect(x - 6, y - 22, w + 12, 30, _shade(fill.base, 0.45), 10, LW_DETAIL))
    else:
        px, py = x + w / 2 - 40, y + h - 10
        hill = (f"M{px},{py + 34} L{px + 30},{py + 14} L{px + 50},{py + 26} L{px + 80},{py + 10} "
                f"L{px + 80},{py + 34} Z")  # fmt: skip
        out += [_rect(px, py, 80, 34, SKY, 2, 1.0), _path(hill, HILL, 1.0)]
    out += [_ell(x + w - 40 - 18 * i, y + 60, 6, 6, _shade(fill.base, 0.5), 1.0) for i in range(3)]
    gloss = f"M{x + 16},{y + 30} C{x + 18},{y + 18} {x + 28},{y + 10} {x + 44},{y + 8}"
    out.append(_highlight(gloss, 4, 0.5))
    return _label(out, label)


def ink_cartridge(paint: str, fill: Fill, label: str | None, ink_yield: str = "standard",
                  ink_formula: str = "dye") -> list[str]:  # fmt: skip
    """An ink cartridge by ``ink_yield``, its window in the ink's color, marked by
    ``ink_formula``."""
    if ink_yield == "xl":
        x, y, w, h = 130.0, 50.0, 140.0, 300.0
    else:
        x, y, w, h = 130.0, 110.0, 140.0, 220.0
    out = [
        _rect(x, y, w, h, SHELL, 14),
        _rect(x + 46, y + h, 48, 18, SLOT, 3, LW_DETAIL),
        _rect(x + 18, y + 20, w - 36, h * 0.45, paint, 8, LW_DETAIL),
        _rect(x + 18, y + 30 + h * 0.45, w - 36, h * 0.4, LABEL, 6, LW_DETAIL),
    ]
    cy = y + 30 + h * 0.65
    if ink_formula == "pigment":
        out += [_line(f"M{x + 26 + 14 * i},{cy + 20} L{x + 40 + 14 * i},{cy - 20}", 2.0)
                for i in range(6)]  # fmt: skip
    else:
        out.append(_path(f"M200,{cy - 26} C190,{cy - 10} 184,{cy} 184,{cy + 8} "
                         f"A16,16 0 1 0 216,{cy + 8} C216,{cy} 210,{cy - 10} 200,{cy - 26} Z",
                         paint, LW_DETAIL))  # fmt: skip
    gloss = f"M{x + 26},{y + 60} C{x + 28},{y + 44} {x + 36},{y + 34} {x + 50},{y + 32}"
    out.append(_highlight(gloss, 4, 0.6))
    return _label(out, label)


SHAPES = {"printer": printer, "ink_cartridge": ink_cartridge}
register(SHAPES)

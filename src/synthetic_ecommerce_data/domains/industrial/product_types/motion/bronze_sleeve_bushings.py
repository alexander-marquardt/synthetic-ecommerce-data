"""Bronze sleeve bushings: deepened from a breadth row into a modelled type (#833).

The breadth row offered five bores in one bronze on two SKUs. A bushing's
inch sizes follow no dimensional standard: ASTM B438 and ASTM B584 are the
materials' specifications, and the sizes are the stock tables a maker prints.
So the inch spec space is one public stock catalogue, and the metric one is
the standard's own table:

* **Inch.** Boston Gear's "Bearings" catalogue P-1930-BG (6/18), as MRO
  Supply hosts it
  (https://documents.mrosupply.com/product_documents/MS/MS22/p-1930-bg_bearings.pdf),
  read on 2026-11-04. Three of its tables: the Bost-Bronz oil-impregnated
  sintered bronze plain cylindrical bearings (printed pages 138 to 140) and
  flanged bearings (pages 141 and 142), and the Bear-N-Bronz cast bronze plain
  cylindrical bearings (pages 146 to 150). The catalogue states Bost-Bronz
  "conforms to ASTM B438-73 Grade 1, Type 2, and SAE-841" (page 136) and
  Bear-N-Bronz to "SAE CA932 (660) and ASTM B584-78 (alloy C93200)" (page 145).
* **Metric.** ISO 2795:2014 Table 1, the preferred nominal dimensions of
  cylindrical sintered bushes, in the standards library
  (``iso_2795_sintered_bushes_mm``): the normal series and the thin-wall
  series, each row's inside diameter, outside diameter and preferred lengths.

Each catalogue row below is one catalogue number prefix and the lengths it is
stocked in, written as the catalogue writes them, so a reviewer can find each
in the PDF: ``B46 1/4 3/8: 2, 2 1/2, 3`` is B46-2, B46-2 1/2 and B46-3. The
number is the size: the first digits are the inside diameter and the next the
outside diameter, both in sixteenths of an inch, and the suffix the length in
eighths, so B46-2 1/2 is 1/4" x 3/8" x 5/16" (``test_every_row_is_its_catalogue_number``).
A flanged row adds the flange diameter and thickness, the table's D and E
columns. The decimal actual sizes the catalogue prints beside each nominal
are not published: a shopper reads the nominal size.

A line is one form (plain or flanged), one material and one unit system: one
row of that table, in rotation, and its SKUs a window of the row's lengths, so
a line never offers a size its table does not. The metric flanged bushes are not built: the ISO 2795
preview does not reach the flanged table.

**Names.** ``Bore Dia.`` is the breadth row's size attribute and the census's
name; ``Outside Dia.`` and ``Length`` are census names. ``Flange Dia.`` and
``Flange Thickness`` are the catalogue's D and E columns, which the census
lacks; ``names.NAME_EXCEPTIONS`` cites the catalogue for both. ``Type`` is
Plain or Flanged, and ``Material`` the bronze.

**Brands.** The type keeps the ``motion`` pool its breadth row had.
"""

from __future__ import annotations

import contextlib
import math
from collections.abc import Mapping
from fractions import Fraction
from functools import cache
from typing import TYPE_CHECKING, Any, NamedTuple

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.model import keyword_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import (
    MM_PER_INCH,
    NO_STANDARD,
    _weighted,
    _window,
    table_provenance,
)
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

KEY = "bronze_sleeve_bushings"
ITEM = "Bronze Sleeve Bushing"

BORE = "Bore Dia."
OUTSIDE = "Outside Dia."
LENGTH = "Length"
FLANGE_DIA = "Flange Dia."
FLANGE_THICKNESS = "Flange Thickness"
FORM = "Type"
MATERIAL = "Material"

PLAIN, FLANGED = "Plain", "Flanged"
SINTERED = "Oil-Impregnated Sintered Bronze"
CAST = "Cast Bronze"

ISO_2795 = "ISO 2795"
ASTM_B438 = "ASTM B438"
ASTM_B584 = "ASTM B584"
#: The standard each inch material conforms to, as the catalogue states it.
MATERIAL_STANDARD = {SINTERED: ASTM_B438, CAST: ASTM_B584}

#: The stock tables every inch dimension is read from, as a record names them.
CHART = "supplier's stock bushing table"

# --- the inch stock tables (Boston Gear P-1930-BG) ----------------------------------

#: Bost-Bronz plain cylindrical, printed pages 138 to 140: catalogue number
#: prefix, inside and outside diameter, then the length codes (eighths of an inch).
_SINTERED_PLAIN = """
B24 1/8 1/4: 1, 2, 3, 4
B25 1/8 5/16: 1, 2, 3, 4, 5
B34 3/16 1/4: 2, 3, 4, 5, 6
B35 3/16 5/16: 2, 3, 4, 5, 6
B36 3/16 3/8: 3, 4, 5, 6
B45 1/4 5/16: 2, 3, 4, 6
B46 1/4 3/8: 2, 2 1/2, 3, 4, 5, 6, 7, 8, 10
B47 1/4 7/16: 3, 4, 5, 6, 7, 8
B48 1/4 1/2: 3, 4, 5, 6, 7, 8, 10
B56 5/16 3/8: 3, 4, 5, 6, 7, 8
B57 5/16 7/16: 2, 3, 4, 5, 6, 7, 8, 10, 11
B58 5/16 1/2: 3, 4, 5, 6, 7, 8, 10, 12, 14
B67 3/8 7/16: 4, 5, 6, 8
B68 3/8 1/2: 3, 4, 5, 6, 7, 8, 10
B69 3/8 9/16: 3, 4, 5, 6, 7, 8, 10
B610 3/8 5/8: 3, 4, 5, 6, 7, 8, 10
B612 3/8 3/4: 3, 4, 6, 8, 10
B79 7/16 9/16: 3, 4, 6, 7, 8, 10
B710 7/16 5/8: 3, 4, 5, 6, 7, 8, 10
B711 7/16 11/16: 4, 8, 12
B810 1/2 5/8: 4, 5, 6, 7, 8, 9, 10, 12
B811 1/2 11/16: 4, 5, 6, 7, 8, 9, 10, 12
B812 1/2 3/4: 4, 5, 6, 7, 8, 9, 10, 12, 14, 16
B813 1/2 13/16: 4, 6, 8, 12
B814 1/2 7/8: 4, 5, 6, 7, 8, 10, 12
B816 1/2 1: 6, 8, 12, 16
B911 9/16 11/16: 4, 6, 8, 12
B912 9/16 3/4: 4, 6, 8, 12
B913 9/16 13/16: 4, 6, 8, 10, 12
B1012 5/8 3/4: 4, 5, 6, 7, 8, 9, 10, 12
B1013 5/8 13/16: 4, 5, 6, 7, 8, 10, 12, 16
B1014 5/8 7/8: 5, 6, 7, 8, 10, 12, 14, 16
B1016 5/8 1: 4, 5, 6, 7, 8, 10, 12, 14, 16
B1114 11/16 7/8: 6, 8, 10, 12, 14, 16
B1214 3/4 7/8: 4, 5, 6, 7, 8, 10, 12, 13
B1215 3/4 15/16: 4, 5, 6, 7, 8, 10, 12, 14, 16
B1216 3/4 1: 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20
B1218 3/4 1-1/8: 4, 6, 8, 10, 12, 14, 16
B1220 3/4 1-1/4: 6, 8, 10, 12, 16
B1316 13/16 1: 6, 8, 10, 12, 14, 16
B1416 7/8 1: 6, 7, 8, 10, 12
B1418 7/8 1-1/8: 6, 7, 8, 9, 10, 11, 12, 14, 16, 20
B1420 7/8 1-1/4: 6, 8, 10, 12, 16
B1519 15/16 1-3/16: 6, 8, 10, 12, 16
B1520 15/16 1-1/4: 6, 8, 10, 14, 16
B1618 1 1-1/8: 6, 8, 10, 12, 14, 16
B1619 1 1-3/16: 6, 8, 10, 12, 14, 16
B1620 1 1-1/4: 6, 7, 8, 10, 11, 12, 14, 16, 18, 20, 24
B1621 1 1-5/16: 8, 10, 12, 14, 16, 20, 24
B1622 1 1-3/8: 8, 10, 12, 14, 16, 20, 24
B1624 1 1-1/2: 8, 12, 16, 20, 24
B1721 1-1/16 1-5/16: 8, 12, 16, 20
B1820 1-1/8 1-1/4: 8, 10, 12
B1821 1-1/8 1-5/16: 8, 10, 12, 16
B1822 1-1/8 1-3/8: 6, 8, 10, 12, 14, 16, 20, 24
B1824 1-1/8 1-1/2: 8, 12, 16
B1923 1-3/16 1-7/16: 10, 16, 20, 24
B1924 1-3/16 1-1/2: 8, 10, 12, 14, 16, 20, 24
B2024 1-1/4 1-1/2: 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 24
B2026 1-1/4 1-5/8: 8, 10, 12, 14, 16, 20, 24
B2126 1-5/16 1-5/8: 10, 12, 16, 20, 24
B2226 1-3/8 1-5/8: 12, 16, 20, 24
B2228 1-3/8 1-3/4: 8, 12, 16, 20, 24
B2328 1-7/16 1-3/4: 8, 10, 12, 14, 16, 20, 24
B2428 1-1/2 1-3/4: 8, 10, 12, 20, 24
B2429 1-1/2 1-13/16: 12, 24
B2430 1-1/2 1-7/8: 12, 16, 20, 24
B2432 1-1/2 2: 8, 12, 16, 20, 24
B2630 1-5/8 1-7/8: 10, 12, 16, 20, 24
B2632 1-5/8 2: 8, 16, 24
B2735 1-11/16 2-3/16: 14, 16, 24, 32
B2832 1-3/4 2: 16, 20, 24
B2834 1-3/4 2-1/8: 12, 16, 24
B3137 1-15/16 2-5/16: 16, 24, 32
B3238 2 2-3/8: 14, 16, 22, 24, 32
B3240 2 2-1/2: 8, 16, 24
B3644 2-1/4 2-3/4: 16, 24
B3844 2-3/8 2-3/4: 16, 24, 32
B4048 2-1/2 3: 16, 24, 32
B4452 2-3/4 3-1/4: 16, 24, 32
B4856 3 3-1/2: 16, 24, 32
"""
#: Bost-Bronz flanged, pages 141 and 142: as above, then the flange diameter
#: and thickness (the table's D and E columns), in inches.
_SINTERED_FLANGED = """
FB25 1/8 5/16 0.375 3/64: 2, 3
FB35 3/16 5/16 0.375 3/64: 1, 2, 3
FB46 1/4 3/8 0.500 3/64: 2, 3, 4, 5, 6
FB56 5/16 3/8 0.500 3/64: 3
FB57 5/16 7/16 0.625 3/32: 3, 4, 5, 6, 7, 8
FB58 5/16 1/2 0.688 3/32: 3, 4, 5
FB68 3/8 1/2 0.688 3/32: 3, 3 1/4, 4, 5, 6, 7, 8, 10
FB69 3/8 9/16 0.750 1/8: 4, 6, 10
FB610 3/8 5/8 0.875 1/8: 3, 4, 5, 6, 8, 10
FB612 3/8 3/4 1.000 1/8: 4
FB79 7/16 9/16 0.688 1/16: 4, 5, 6
FB710 7/16 5/8 0.875 1/8: 5, 6, 10
FB810 1/2 5/8 0.875 1/8: 4, 5, 6, 7, 8, 10, 12, 14
FB811 1/2 11/16 0.938 1/8: 4, 5, 6
FB812 1/2 3/4 1.000 1/8: 4, 5, 6, 7, 8, 10, 12
FB912 9/16 3/4 1.000 1/8: 4, 6, 8
FB1012 5/8 3/4 1.000 1/8: 4, 5, 6, 8, 10
FB1013 5/8 13/16 1.063 5/32: 5, 6, 8, 10, 11 1/2, 12, 16
FB1014 5/8 7/8 1.125 5/32: 5, 6, 8, 14
FB1016 5/8 1 1.250 5/32: 6, 8
FB1214 3/4 7/8 1.125 5/32: 6, 8, 10
FB1215 3/4 15/16 1.188 5/32: 8, 10, 12
FB1216 3/4 1 1.250 5/32: 5, 6, 8, 10, 12, 16
FB1416 7/8 1 1.250 5/32: 6, 8, 10
FB1418 7/8 1-1/8 1.375 5/32: 8, 10, 12
FB1620 1 1-1/4 1.500 3/16: 6, 8, 10, 12, 16
FB1622 1 1-3/8 1.625 3/16: 8, 12, 14
FB1822 1-1/8 1-3/8 1.750 1/8: 6, 8, 10
FB2024 1-1/4 1-1/2 1.750 3/16: 8, 10, 12
FB2226 1-3/8 1-5/8 2.000 1/8: 6, 8
FB2428 1-1/2 1-3/4 2.063 3/16: 12
FB3236 2 2-1/4 2.500 1/8: 6, 8, 10
FB4452 2-3/4 3-1/4 4.000 3/16: 12
"""
#: Bear-N-Bronz cast bronze plain cylindrical, pages 146 to 150.
_CAST_PLAIN = """
M35 3/16 5/16: 4, 6, 8
M46 1/4 3/8: 6, 8, 10
M47 1/4 7/16: 6, 8, 10
M57 5/16 7/16: 6, 8, 10
M58 5/16 1/2: 6, 8, 10
M68 3/8 1/2: 6, 8, 10, 12
M69 3/8 9/16: 6, 8, 10
M610 3/8 5/8: 6, 8, 10, 12
M79 7/16 9/16: 8, 10, 12
M710 7/16 5/8: 8, 10, 12, 16
M711 7/16 11/16: 12
M712 7/16 3/4: 8, 10, 12
M713 7/16 13/16: 12
M810 1/2 5/8: 5, 6, 7, 8, 10, 11, 12, 14, 16, 18
M811 1/2 11/16: 6, 8, 10, 12, 14, 16, 18, 20
M812 1/2 3/4: 6, 8, 10, 12, 14, 16, 18, 20, 22
M813 1/2 13/16: 8, 12, 18
M814 1/2 7/8: 8, 10, 12, 14, 16
M816 1/2 1: 8, 12, 16, 18
M911 9/16 11/16: 8, 10, 12, 14, 16, 18
M912 9/16 3/4: 8, 10, 12, 14, 16, 20
M913 9/16 13/16: 8, 10, 12, 14, 16
M914 9/16 7/8: 8, 12, 16
M1012 5/8 3/4: 8, 9, 10, 12, 14, 16, 18, 20
M1013 5/8 13/16: 8, 10, 12, 14, 16, 18, 20
M1014 5/8 7/8: 6, 8, 10, 12, 14, 16, 18, 20, 24
M1015 5/8 15/16: 8, 12, 20
M1016 5/8 1: 8, 12, 16, 18, 20, 24
M1018 5/8 1-1/8: 12, 16, 18
M1113 11/16 13/16: 8, 12, 14, 16
M1114 11/16 7/8: 8, 10, 12, 16, 20
M1115 11/16 15/16: 8, 10, 12, 20
M1116 11/16 1: 10, 18, 20
M1214 3/4 7/8: 6, 8, 10, 12, 14, 16, 18, 20
M1215 3/4 15/16: 8, 10, 12, 14, 16, 18, 20, 24
M1216 3/4 1: 6, 8, 9, 10, 11, 12, 14, 16, 17, 18, 20, 22, 24, 28
M1217 3/4 1-1/16: 8, 12, 16, 24
M1218 3/4 1-1/8: 8, 12, 16, 20, 24
M1219 3/4 1-3/16: 12, 16
M1220 3/4 1-1/4: 14, 16, 20, 24
M1315 13/16 15/16: 8, 12, 16
M1316 13/16 1: 12, 16, 20
M1317 13/16 1-1/16: 12, 16, 22
M1318 13/16 1-1/8: 12, 16
M1416 7/8 1: 8, 10, 11, 12, 13, 16
M1417 7/8 1-1/16: 8, 10, 12, 14, 16, 18, 20, 24
M1418 7/8 1-1/8: 6, 8, 10, 11, 12, 14, 16, 18, 20, 24, 26, 28
M1419 7/8 1-3/16: 8, 24
M1420 7/8 1-1/4: 12, 14, 16, 18, 20, 24, 28
M1422 7/8 1-3/8: 12, 16, 20, 24
M1518 15/16 1-1/8: 12, 16
M1519 15/16 1-3/16: 10, 12, 16, 24
M1520 15/16 1-1/4: 8, 12, 16, 20, 22
M1521 15/16 1-5/16: 12, 16
M1618 1 1-1/8: 11, 12, 14, 16, 20
M1619 1 1-3/16: 7, 10, 12, 14, 16, 20
M1620 1 1-1/4: 6, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 32, 36
M1621 1 1-5/16: 12, 16, 18, 20, 24, 28
M1622 1 1-3/8: 10, 12, 14, 16, 20, 22, 24, 28, 32, 36
M1624 1 1-1/2: 12, 14, 16, 20, 24, 32
M1626 1 1-5/8: 16, 20, 24, 28
M1628 1 1-3/4: 52
M1632 1 2: 24, 52
M1721 1-1/16 1-5/16: 12, 16, 20
M1723 1-1/16 1-7/16: 20
M1820 1-1/8 1-1/4: 12, 14, 16
M1821 1-1/8 1-5/16: 18, 20
M1822 1-1/8 1-3/8: 8, 10, 12, 14, 16, 18, 20, 24, 26, 28, 32
M1823 1-1/8 1-7/16: 12, 24
M1824 1-1/8 1-1/2: 12, 16, 20, 24, 28, 32
M1826 1-1/8 1-5/8: 14, 16, 20, 24, 28, 36
M1830 1-1/8 1-7/8: 52
M1832 1-1/8 2: 24
M1922 1-3/16 1-3/8: 14, 16, 20
M1923 1-3/16 1-7/16: 10, 12, 16, 20, 24, 28
M1924 1-3/16 1-1/2: 16, 24, 32
M1925 1-3/16 1-9/16: 24, 28
M1926 1-3/16 1-5/8: 16, 20, 24
M1927 1-3/16 1-11/16: 16, 20, 24
M2023 1-1/4 1-7/16: 20, 24
M2024 1-1/4 1-1/2: 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 32, 34, 36, 40, 44
M2025 1-1/4 1-9/16: 16, 20, 24, 28, 30
M2026 1-1/4 1-5/8: 14, 16, 20, 24, 26, 28, 32, 36, 38
M2027 1-1/4 1-11/16: 16, 26
M2028 1-1/4 1-3/4: 14, 16, 18, 20, 22, 24, 28, 30, 32, 40
M2030 1-1/4 1-7/8: 16, 20, 32
M2032 1-1/4 2: 24, 32, 52
M2124 1-5/16 1-1/2: 14, 24
M2126 1-5/16 1-5/8: 16, 24, 38
M2129 1-5/16 1-13/16: 24, 32
M2130 1-5/16 1-7/8: 28
M2224 1-3/8 1-1/2: 14, 16, 20
M2226 1-3/8 1-5/8: 16, 24, 26, 28, 32
M2227 1-3/8 1-11/16: 28
M2228 1-3/8 1-3/4: 16, 18, 20, 24, 28, 32
M2230 1-3/8 1-7/8: 24, 28, 32, 36
M2232 1-3/8 2: 24, 32
M2234 1-3/8 2-1/8: 52
M2326 1-7/16 1-5/8: 14, 22, 24
M2327 1-7/16 1-11/16: 20, 24, 28, 32
M2328 1-7/16 1-3/4: 18, 24, 32
M2329 1-7/16 1-13/16: 24, 34
M2330 1-7/16 1-7/8: 24, 32, 36, 40
M2331 1-7/16 1-15/16: 16, 24
M2332 1-7/16 2: 32
M2426 1-1/2 1-5/8: 16
M2427 1-1/2 1-11/16: 22
M2428 1-1/2 1-3/4: 14, 16, 18, 20, 24, 28, 32, 36, 40, 44
M2429 1-1/2 1-13/16: 24
M2430 1-1/2 1-7/8: 16, 20, 22, 24, 28, 32, 36, 40, 44
M2432 1-1/2 2: 20, 24, 28, 32, 36, 40
M2434 1-1/2 2-1/8: 24, 32
M2436 1-1/2 2-1/4: 24, 32, 40, 52
M2529 1-9/16 1-13/16: 24, 28
M2531 1-9/16 1-15/16: 28
M2630 1-5/8 1-7/8: 18, 24, 30
M2632 1-5/8 2: 14, 20, 24, 32, 40, 44
M2634 1-5/8 2-1/8: 24, 32
M2731 1-11/16 1-15/16: 24, 28
M2732 1-11/16 2: 28, 36
M2733 1-11/16 2-1/16: 24, 32, 36, 44
M2735 1-11/16 2-3/16: 16, 24, 32
M2736 1-11/16 2-1/4: 24, 36
M2832 1-3/4 2: 18, 20, 24, 32, 36, 42
M2833 1-3/4 2-1/16: 28
M2834 1-3/4 2-1/8: 22, 26, 28, 32, 34, 40
M2836 1-3/4 2-1/4: 14, 16, 20, 24, 28, 32, 34, 40
M2838 1-3/4 2-3/8: 28, 40
M2840 1-3/4 2-1/2: 52
M2935 1-13/16 2-3/16: 32
M2937 1-13/16 2-5/16: 32, 40
M3034 1-7/8 2-1/8: 20, 24, 32
M3036 1-7/8 2-1/4: 24, 40
M3038 1-7/8 2-3/8: 24, 32, 42
M3135 1-15/16 2-3/16: 16, 24
M3136 1-15/16 2-1/4: 24, 36
M3137 1-15/16 2-5/16: 28, 32, 40, 50
M3138 1-15/16 2-3/8: 32, 44
M3139 1-15/16 2-7/16: 24
M3140 1-15/16 2-1/2: 24, 40
M3236 2 2-1/4: 16, 20, 24, 28, 32, 36
M3238 2 2-3/8: 24, 28, 32, 36
M3240 2 2-1/2: 20, 24, 28, 32, 36, 40, 48
M3242 2 2-5/8: 32
M3244 2 2-3/4: 52
M3440 2-1/8 2-1/2: 24, 32
M3442 2-1/8 2-5/8: 32, 40, 48
M3542 2-3/16 2-5/8: 32, 40
M3543 2-3/16 2-11/16: 28, 36, 40
M3544 2-3/16 2-3/4: 36, 42, 48
M3546 2-3/16 2-7/8: 36
M3640 2-1/4 2-1/2: 28, 32
M3642 2-1/4 2-5/8: 24, 32, 40
M3643 2-1/4 2-11/16: 38
M3644 2-1/4 2-3/4: 28, 32, 36, 40, 48
M3648 2-1/4 3: 28, 40
M3844 2-3/8 2-3/4: 32, 48
M3846 2-3/8 2-7/8: 32, 40
M3944 2-7/16 2-3/4: 32, 40
M3946 2-7/16 2-7/8: 24, 40
M3947 2-7/16 2-15/16: 32, 40, 50
M3948 2-7/16 3: 30, 40, 50
M4044 2-1/2 2-3/4: 32, 40
M4046 2-1/2 2-7/8: 26, 36
M4048 2-1/2 3: 32, 40, 48, 56
M4050 2-1/2 3-1/8: 28, 32, 36
M4052 2-1/2 3-1/4: 32, 40, 48, 58
M4056 2-1/2 3-1/2: 52
M4248 2-5/8 3: 24, 40
M4250 2-5/8 3-1/8: 40, 48, 58
M4252 2-5/8 3-1/4: 56
M4254 2-5/8 3-3/8: 52
M4351 2-11/16 3-3/16: 50
M4450 2-3/4 3-1/8: 32, 40, 48
M4452 2-3/4 3-1/4: 32, 40, 48
M4656 2-7/8 3-1/2: 36, 54
M4755 2-15/16 3-7/16: 28, 40, 52
M4854 3 3-3/8: 36, 64
M4856 3 3-1/2: 36, 48, 72
M4858 3 3-5/8: 40
M4860 3 3-3/4: 50
M4864 3 4: 52
M5256 3-1/4 3-1/2: 32
M5260 3-1/4 3-3/4: 40
M5563 3-7/16 3-15/16: 36, 52
M5664 3-1/2 4: 44, 56
M5666 3-1/2 4-1/8: 48
M5668 3-1/2 4-1/4: 36, 56, 78
M6068 3-3/4 4-1/4: 40, 56
M6072 3-3/4 4-1/2: 52
M6472 4 4-1/2: 32, 48, 56
M6480 4 5: 40, 48
M6876 4-1/4 4-3/4: 40, 48, 56
M6880 4-1/4 5: 40, 48, 56
M7280 4-1/2 5: 48, 56, 64
"""


class Size(NamedTuple):
    """One stocked bushing, in inches."""

    bore: float
    outside: float
    length: float
    #: The flange's diameter and thickness; 0.0 on a plain bushing.
    flange_dia: float = 0.0
    flange_thickness: float = 0.0


def _inch(text: str) -> Fraction:
    """``1-3/8`` or ``5/16`` or ``2`` as a fraction of an inch."""
    whole, _, part = text.partition("-") if "/" in text and "-" in text else ("", "", text)
    return Fraction(whole or 0) + Fraction(part)


def _code(text: str) -> Fraction:
    """A catalogue length code (``2 1/2``: eighths of an inch) as inches."""
    return sum((Fraction(p) for p in text.split()), Fraction(0)) / 8


class Row(NamedTuple):
    """One catalogue number prefix as the table prints it."""

    number: str
    bore: Fraction
    outside: Fraction
    lengths: tuple[Fraction, ...]
    flange: tuple[Fraction, Fraction] | None


def parse_table(text: str) -> tuple[Row, ...]:
    """The rows of one catalogue table, as written above."""
    rows = []
    for line in text.strip().splitlines():
        head, _, codes = line.partition(":")
        number, bore, outside, *flange = head.split()
        rows.append(
            Row(
                number,
                _inch(bore),
                _inch(outside),
                tuple(_code(c) for c in codes.split(",")),
                (Fraction(flange[0]), Fraction(flange[1])) if flange else None,
            )
        )
    return tuple(rows)


def _sizes(rows: tuple[Row, ...]) -> tuple[tuple[Size, ...], ...]:
    """Each catalogue row's sizes, one bore and outside diameter in its lengths."""
    out = []
    for row in rows:
        fd, ft = row.flange or (0, 0)
        out.append(
            tuple(
                Size(float(row.bore), float(row.outside), float(n), float(fd), float(ft))
                for n in row.lengths
            )
        )
    return tuple(out)


@cache
def iso_2795() -> tuple[tuple[tuple[Size, ...], ...], tuple[tuple[Size, ...], ...]]:
    """ISO 2795 Table 1's normal and thin-wall series, in inches. For an inside
    diameter up to 20 mm the row's last length is not a thin-wall one (the
    table's footnote a); a second-choice diameter is not in the library table.
    Each row is one inside and outside diameter in its lengths."""
    normal, thin = [], []
    for row in library.table("iso_2795_sintered_bushes_mm").rows:
        d = row["d"] / MM_PER_INCH
        lengths = row["lengths"]
        normal.append(
            tuple(Size(d, row["D_normal"] / MM_PER_INCH, n / MM_PER_INCH) for n in lengths)
        )
        if row["D_thin_wall"] is not None:
            kept = lengths[:-1] if row["d"] <= 20 else lengths
            thin.append(
                tuple(Size(d, row["D_thin_wall"] / MM_PER_INCH, n / MM_PER_INCH) for n in kept)
            )
    return tuple(normal), tuple(thin)


class Series(NamedTuple):
    """One table a line draws its sizes from."""

    name: str
    form: str
    material: str
    system: str
    #: One bore and outside diameter each, in its lengths, rising.
    rows: tuple[tuple[Size, ...], ...]

    @property
    def sizes(self) -> tuple[Size, ...]:
        return tuple(size for row in self.rows for size in row)


@cache
def series() -> tuple[Series, ...]:
    """Every table, its rows rising by bore and outside diameter."""
    normal, thin = iso_2795()
    return tuple(
        Series(name, form, material, system, tuple(sorted(rows)))
        for name, form, material, system, rows in (
            ("sintered-plain", PLAIN, SINTERED, "in", _sizes(parse_table(_SINTERED_PLAIN))),
            ("sintered-flanged", FLANGED, SINTERED, "in", _sizes(parse_table(_SINTERED_FLANGED))),
            ("cast-plain", PLAIN, CAST, "in", _sizes(parse_table(_CAST_PLAIN))),
            ("iso-normal", PLAIN, SINTERED, "mm", normal),
            ("iso-thin-wall", PLAIN, SINTERED, "mm", thin),
        )
    )


def provenance(table: Series) -> str:
    """Which table each published dimension was read from."""
    if table.system == "mm":
        return table_provenance((BORE, ISO_2795), (OUTSIDE, ISO_2795), (LENGTH, ISO_2795))
    names = (BORE, OUTSIDE, LENGTH) + (
        (FLANGE_DIA, FLANGE_THICKNESS) if table.form == FLANGED else ()
    )
    return table_provenance(*((name, CHART) for name in names)) + "; " + NO_STANDARD


VOCAB = (
    AttrSpec(FORM, "line"),
    AttrSpec(MATERIAL, "line"),
    AttrSpec(BORE, "sku", kind="length"),
    AttrSpec(OUTSIDE, "sku", kind="length"),
    AttrSpec(LENGTH, "sku", kind="length"),
    AttrSpec(FLANGE_DIA, "sku", kind="length"),
    AttrSpec(FLANGE_THICKNESS, "sku", kind="length"),
)


def _stride(count: int) -> int:
    """The step a line takes through a table's rows: about 0.38 of them and
    prime to their count, so the rotation still visits every row once, and a
    small build's few lines spread over the bores and do not stop at the
    smallest (the breadth row's 5/8" and 3/4" bores are built by default)."""
    step = max(1, round(count * 0.382))
    while math.gcd(step, count) != 1:
        step += 1
    return step


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a table, weighted by its size count; one of its rows, in
    rotation, so every bore and outside diameter is drafted before any repeats;
    and a window of that row's lengths."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    table = _weighted(rng, [(t, len(t.sizes)) for t in series()])
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"{'FB' if table.form == FLANGED else 'SB'}{rng.randint(100, 999)}",
        category=category,
        provenance=provenance(table),
        standard=ISO_2795 if table.system == "mm" else "",
    )
    draft.line_attrs = [
        keyword_attribute(FORM, table.form),
        keyword_attribute(MATERIAL, table.material),
    ]
    draft.descriptors = [(FORM, table.form), (MATERIAL, table.material)]
    style = gen._style(table.system)
    count = len(table.rows)
    index = gen._rotate(f"bushing:{table.name}", count) * _stride(count) % count
    row = list(table.rows[index])
    for size in _window(gen, f"bushing:{table.name}:{index}", row, gen._variant_count()):
        child = ChildDraft(system=table.system)
        child.primary = gen._length(BORE, size.bore, style)
        child.also = gen._length(LENGTH, size.length, style)
        child.attrs = [child.primary, gen._length(OUTSIDE, size.outside, style), child.also]
        if table.form == FLANGED:
            child.attrs += [
                gen._length(FLANGE_DIA, size.flange_dia, style),
                gen._length(FLANGE_THICKNESS, size.flange_thickness, style),
            ]
        draft.children.append(child)
    return draft


# --- the drawing ------------------------------------------------------------------

#: The drawing's extent (docs/adding-a-type.md "Figure and extent"): the largest
#: drawn is 14.50 x 5.00 in, at the ``--lines 39000`` build (9.75 x 3.50 at the
#: default), a 4-1/2" x 5" x 8" cast bushing's face beside its side view,
#: plus 0.1" and rounded to 0.05".
EXTENT = (14.6, 5.1)

#: What a bushing is drawn at when the record gives no readable size: B48-6.
_NOMINAL = Size(0.5, 0.625, 0.75)


def _inches(record: Mapping[str, str], name: str) -> float | None:
    with contextlib.suppress(KeyError, DimensionParseError):
        value = parse_length(record[name]).inches
        return value if value > 0 else None
    return None


def figure(record: dict[str, str]) -> Drawn:
    """The bushing's end face (a ring, with the flange behind it) and, beside
    it, its side view: the sleeve's outline, the flange at one end, and the
    bore drawn through it."""
    bore, outside, length = (_inches(record, n) for n in (BORE, OUTSIDE, LENGTH))
    if bore and outside and length and outside > bore:
        source = "record"
    else:
        source = "nominal"
        bore, outside, length = _NOMINAL.bore, _NOMINAL.outside, _NOMINAL.length
    flange = _inches(record, FLANGE_DIA) or 0.0
    thickness = _inches(record, FLANGE_THICKNESS) or 0.0
    if flange <= outside or thickness <= 0.0 or thickness >= length:
        flange = thickness = 0.0
    face = max(flange, outside)
    fig = Figure(size_in=max(face, length))
    if flange:
        fig.disc((0.0, 0.0), flange / 2)
    fig.disc((0.0, 0.0), outside / 2)
    fig.disc((0.0, 0.0), bore / 2, "hole")
    x0 = face / 2 + 0.3 * face
    if flange:
        fig.rect(x0, -flange / 2, x0 + thickness, flange / 2)
    fig.rect(x0 + thickness, -outside / 2, x0 + length, outside / 2)
    fig.lines(
        [((x0, -bore / 2), (x0 + length, -bore / 2)), ((x0, bore / 2), (x0 + length, bore / 2))]
    )
    return Drawn(fig, source)


# --- price ------------------------------------------------------------------------

#: What a material multiplies the price by. GENERATED, not measured: a machined
#: cast bronze bushing sells for about twice a pressed sintered one of its size.
MATERIAL_FACTORS = {SINTERED: 1.0, CAST: 2.0}

#: No census prices: the price census has no bushings. NOT MEASURED: the level
#: is hand-set near the breadth row's 2 to 15 USD for 1/4" to 3/4" bores, 4 USD
#: for a 1/2" sintered bushing, rising a little under linearly with the bore.
PRICE = PriceModel(
    4.0, 0.5, 0.9, 0.15, 0.1,
    measured=False,
    option_attribute=MATERIAL,
    option_factors=MATERIAL_FACTORS,
)  # fmt: skip


def claims(facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str) -> list[str]:
    """A metric line claims ISO 2795, the table every row was read from; an inch
    line the specification the catalogue says its bronze conforms to."""
    if metric:
        return [standard]
    return [MATERIAL_STANDARD.get(facts.get(MATERIAL, ""), "")]


SPEC = TypeSpec(
    KEY,
    category=("Motion Control & Fluid Power", "Bushings", "Bronze Sleeve Bushings"),
    standards_family="motion",
    vocab=VOCAB,
    figure=figure,
    extent=EXTENT,
    make=build,
    share=0.015,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({ISO_2795, ASTM_B438, ASTM_B584}),
    key_attributes=(BORE,),
    compat=False,
    use_lines=(
        "Presses into a housing as a plain bearing for a rotating or sliding shaft.",
        "Runs without added grease where the bronze holds its own oil.",
    ),
)

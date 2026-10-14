"""Near-white shades on apparel, more women's jumpers, and every bra shape in each main color (gen#302).

A color-group demo ("womens cream jumper", "ladies ivory cardigan", "off white dress", "white
minimiser bras") needs products for a shopper to find, and the catalog lacked them:

- **Near-white shades** (Cream, Ivory, Off White) sat on bras, skirts and homeware but on no
  knitwear, top or dress, so a group "white" with cream, ivory and off white as members had
  nothing to group on apparel. :data:`APPAREL` puts each shade next to White on jumpers,
  cardigans, dresses, tops and blouses. The row's colors are its SKUs'; no description or title
  names one, so the text never states a color the style does not carry.
- **Women's jumpers**: 40 SKUs became at least 150, so a page of 10 does not repeat one style.
- **Bra shape x main color**: :data:`BRAS` holds one style per shape a shopper names (minimiser,
  plunge, balcony, full cup, t-shirt) in White, Black, Beige, Red and Blue, and a second
  minimiser, the shape that had only Black and Beige.

There is no color-group attribute: the group is a vocabulary on the consumer's side
(gen#186). These rows are templates only: :func:`scale.derivable` leaves them out, as it does
the seasonal rows, so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import variants
from main_colors import MAIN_COLORS
from scale_rows import Bra
from seasonal_rows import SRow
from variants import cw

CREAM, IVORY, OFF_WHITE = cw("Cream", "#efe4cf"), cw("Ivory", "#f3ecd9"), cw("Off White", "#f4f1ea")
WHITE, BLACK = cw("White", "#ffffff"), cw("Black", "#2a2a2e")
RED, BLUE = cw("Red", MAIN_COLORS["Red"]), cw("Blue", MAIN_COLORS["Blue"])
ALMOND = cw("Almond", "#d9b79a")  # the plain color word is Beige
NAVY, GREEN = cw("Navy", "#26365c"), cw("Green", MAIN_COLORS["Green"])
CAMEL, OATMEAL = cw("Camel", "#b5835a"), cw("Oatmeal", "#d9ccb4")
STONE, ROSE = cw("Stone", "#bdb5a6"), cw("Rose", "#d98a96")

#: The near-white shades every apparel type carries; the test pins the same three.
SHADES = ("Cream", "Ivory", "Off White")

_SIZES = ("XS", "S", "M", "L", "XL")
_C = "Clothing"
_JUMP = ("Women", "Knitwear", "Jumpers")
_CARDI = ("Women", "Knitwear", "Cardigans")
_DRESS = ("Women", "Dresses", "Midi Dresses")
_TOP = ("Women", "Tops", "Long Sleeve Tops")
_BLOUSE = ("Women", "Shirts & Blouses", "Blouses")


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, shape: str,
         price: float, description: str, colors: tuple, material: str) -> SRow:
    return SRow(code, title, brand, _C, path, ptype, price, shape, description, colors,
                (("material", "Material", material),), tuple((s, price) for s in _SIZES))


#: Apparel styles: each row's colors times five sizes are its SKUs.
APPAREL = (
    # Women's jumpers: eight styles of four colors in five sizes, 160 SKUs on top of the 40.
    _row("NWJ1", "Cable Knit Crew Neck Jumper", "Harbour & Pine", _JUMP, "Jumper", "sweatshirt", 38.0,
         "A chunky cable knit jumper with a crew neck and ribbed cuffs, warm and relaxed.",
         (CREAM, NAVY, IVORY, BLACK), "Wool blend"),
    _row("NWJ2", "Fine Gauge Roll Neck Jumper", "Larkmoor", _JUMP, "Jumper", "sweatshirt", 34.0,
         "A fine gauge jumper with a roll neck that sits close under a coat.",
         (OFF_WHITE, CREAM, CAMEL, RED), "Merino wool"),
    _row("NWJ3", "Soft Touch V Neck Jumper", "Harbour & Pine", _JUMP, "Jumper", "sweatshirt", 30.0,
         "A soft V neck jumper with a slightly cropped hem, easy over a shirt.",
         (IVORY, OFF_WHITE, GREEN, BLUE), "Cotton blend"),
    _row("NWJ4", "Brushed Mohair Blend Jumper", "Larkmoor", _JUMP, "Jumper", "sweatshirt", 44.0,
         "A light brushed jumper with a loose neck and dropped shoulders.",
         (WHITE, CREAM, ROSE, STONE), "Mohair blend"),
    _row("NWJ5", "Waffle Knit Crew Neck Jumper", "Harbour & Pine", _JUMP, "Jumper", "sweatshirt", 32.0,
         "A waffle knit jumper with a crew neck, ribbed cuffs and a straight hem.",
         (OFF_WHITE, IVORY, OATMEAL, BLACK), "Cotton"),
    _row("NWJ6", "Lambswool Boxy Jumper", "Larkmoor", _JUMP, "Jumper", "sweatshirt", 48.0,
         "A boxy lambswool jumper with a high crew neck and a soft, dense finish.",
         (CREAM, WHITE, NAVY, RED), "Lambswool"),
    _row("NWJ7", "Ribbed Turtle Neck Jumper", "Harbour & Pine", _JUMP, "Jumper", "sweatshirt", 28.0,
         "A ribbed jumper with a turtle neck and a close fit, to layer under a blazer.",
         (IVORY, OFF_WHITE, BLACK, GREEN), "Cotton blend"),
    _row("NWJ8", "Oversized Crew Neck Jumper", "Larkmoor", _JUMP, "Jumper", "sweatshirt", 36.0,
         "An oversized jumper with a crew neck, dropped shoulders and a long hem.",
         (CREAM, OFF_WHITE, BLUE, ROSE), "Wool blend"),
    # Cardigans.
    _row("NWC1", "Button Front Knit Cardigan", "Harbour & Pine", _CARDI, "Cardigan", "cardigan", 36.0,
         "A knit cardigan with a button front, patch pockets and ribbed cuffs.",
         (IVORY, CREAM, NAVY, BLACK), "Cotton blend"),
    _row("NWC2", "Longline Edge To Edge Cardigan", "Larkmoor", _CARDI, "Cardigan", "cardigan", 42.0,
         "A longline cardigan that falls open at the front, light enough for the office.",
         (OFF_WHITE, IVORY, STONE, RED), "Wool blend"),
    _row("NWC3", "Chunky Shawl Collar Cardigan", "Harbour & Pine", _CARDI, "Cardigan", "cardigan", 46.0,
         "A chunky cardigan with a shawl collar and deep pockets, to wrap up in.",
         (CREAM, OFF_WHITE, OATMEAL, GREEN), "Acrylic blend"),
    # Dresses.
    _row("NWD1", "Jersey Wrap Midi Dress", "Harbour & Pine", _DRESS, "Dress", "dress", 36.0,
         "A jersey midi dress that wraps at the waist, with a flared skirt.",
         (OFF_WHITE, CREAM, NAVY, BLACK), "Jersey"),
    _row("NWD2", "Broderie Midi Dress", "Larkmoor", _DRESS, "Dress", "dress", 44.0,
         "A cotton midi dress with eyelet embroidery and a tiered skirt, for a warm day.",
         (IVORY, WHITE, BLUE, ROSE), "Cotton"),
    _row("NWD3", "Textured Smock Midi Dress", "Harbour & Pine", _DRESS, "Dress", "dress", 40.0,
         "A loose smock dress with a gathered neck and long sleeves.",
         (CREAM, IVORY, OFF_WHITE, GREEN), "Viscose"),
    # Tops and blouses.
    _row("NWT1", "Ribbed Long Sleeve Top", "Harbour & Pine", _TOP, "Top", "top", 18.0,
         "A ribbed top with a fitted body and long sleeves, to layer or wear alone.",
         (CREAM, OFF_WHITE, BLACK, RED), "Cotton"),
    _row("NWT2", "Boat Neck Long Sleeve Top", "Larkmoor", _TOP, "Top", "top", 22.0,
         "A soft long sleeve top with a wide neckline and a relaxed fit.",
         (IVORY, CREAM, NAVY, WHITE), "Cotton blend"),
    _row("NWB1", "Pleated Front Blouse", "Larkmoor", _BLOUSE, "Blouse", "blouse", 34.0,
         "A blouse with a pleated front, a soft collar and buttoned cuffs.",
         (OFF_WHITE, IVORY, CREAM, BLACK), "Crepe"),
    _row("NWB2", "Tie Neck Satin Blouse", "Harbour & Pine", _BLOUSE, "Blouse", "blouse", 38.0,
         "A satin blouse with a tie neck and a soft drape, from desk to dinner.",
         (CREAM, IVORY, BLUE, ROSE), "Satin"),
)


def _bra(code: str, line: str, brand: str, kind: str, bands: tuple[int, int],
         cups: tuple[str, str], price: float) -> Bra:
    """A bra style of one shape in all five main colors: White, Black, Beige, Red and Blue."""
    return Bra(code, line, brand, kind, bands, cups, (WHITE, BLACK, ALMOND, RED, BLUE), price,
               wired=False)


#: One style per shape, each in the five main colors a bra comes in, plus a second minimiser.
BRAS = (
    _bra("NWMIN1", "Alderley", "Saltmarsh", "Minimiser", (34, 46), ("C", "G"), 24.0),
    _bra("NWMIN2", "Ravenscar", "Bramblewood", "Minimiser", (32, 44), ("B", "F"), 26.0),
    _bra("NWPLG1", "Tarrant", "Bramblewood", "Plunge", (30, 40), ("A", "E"), 22.0),
    _bra("NWBAL1", "Ouseburn", "Saltmarsh", "Balcony", (30, 40), ("A", "E"), 22.0),
    _bra("NWFUL1", "Kingsett", "Saltmarsh", "Full Cup", (32, 46), ("B", "H"), 24.0),
    _bra("NWTSH1", "Merrow", "Bramblewood", "T-Shirt", (30, 42), ("A", "F"), 20.0),
)


def docs() -> list[dict]:
    """Every row's catalog document: the apparel rows, then the bras."""
    return [*(r.doc() for r in APPAREL), *(d for s in BRAS for d in variants.style_docs("Bras", s))]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset([*(f"BRD-{r.code}" for r in APPAREL), *(f"BRA-{s.code}" for s in BRAS)])

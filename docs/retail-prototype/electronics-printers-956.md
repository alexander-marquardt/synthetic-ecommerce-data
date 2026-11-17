# Electronics printers and ink, slice 3b (gen#956)

Electronics held 1,166 SKUs at the ceiling build, against the 14,000 the catalogue mix plans
(`docs/catalogue-mix-837.md`). A search for a `printer` or for `ink` found no printer and no
cartridge. Slice 3 of gen#956 named five types, more than the three a PR may add
(`docs/new-type-quick-path.md`, "Sizing rule"), so it was cut in two. Slice 3a added power
banks, webcams and smartwatches ([electronics-gadgets-956.md](electronics-gadgets-956.md)).
Slice 3b, this page, adds printers and ink, each a derivable spec of its own.

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Printer | `type_specs/printer.py` | Electronics > Printers > Printers | 8 (4 title patterns x 2 brands) | color |
| Ink Cartridge | `type_specs/ink_cartridge.py` | Electronics > Printers > Ink Cartridges | 8 (4 title patterns x 2 brands) | color |

`printers_rows.py` holds the shared pieces: the paths, the six main colors of gen#275, `row()`
and `decoy()`. Every brand is an invented Electronics brand of `electronics_rows.py`
(`ELECTRONICS_OWNERS`).

**Attributes.**
- Printers carry `printer_type` (Inkjet, Laser), `printer_function` (Multifunction, Photo) and
  `printer_feature` (Wi-Fi, Auto Duplex).
- Ink cartridges carry `ink_yield` (Standard, XL), `ink_formula` (Dye, Pigment) and
  `ink_feature` (Smart Chip, Ink Level Window). The test holds the `XL` case in derived titles.
  A row's text names only its own yield: the XL row says "a regular cartridge", never
  "standard", and the XL decoy reads "a high-yield", so no article meets `XL`.

Every key is new to the catalogue and carries no unit, so no key's values clash with another
type's.

**Drawings** (`kit_printers.py`, both upright in `orientation.py`).
- `printer` draws its type: a low wide inkjet, or a deep laser box with a toner door. It draws
  its function: a scanner lid for multifunction, or a photo on the sheet for photo.
- `ink_cartridge` draws its yield: a standard cartridge, or a tall XL one with a long ink
  window. The window is the ink's color. It draws its formula: a drop on the label for dye, or
  a hatched band for pigment.

A derived style that changes one of these params draws what it states (gen#512).

**Colors.** Every template is offered in the six main colors (gen#275). A printer's color is its
case. An ink cartridge's color is its ink: photo and pigment printers sell red, blue, green and
white inks beside black and yellow. No type declares an exception.

**Decoys** (gen#309), two per type. Each is cut from a template, holds one color, and names
another color in its title:
- `Laser Printer with Green Status Light` is black. `Red Fern Multifunction Printer` is white.
- `Standard Ink Cartridge with Blue Pull Tab` is black. `Yellow Cove XL Pigment Ink Cartridge`
  is black.

**Breadth.** Measured on the ceiling build, seed 0: Printer 443 and Ink Cartridge 435 SKUs. That
is 878 on its own, and Electronics goes from 1,166 to 2,044 on main. With slice 1 (9,479),
slice 2a (+1,782), slice 2b (+1,052) and slice 3a (+1,459), the department holds about 14,647.
That passes the issue's 14,000 target.

**Test.** `tests/test_retail_electronics_printers_956.py` checks the following:
- the slice's floor of 230 SKUs, and each type's band of 350 to 600;
- each type's node, and that each type is derived;
- unique ids, titles, SKUs and twin keys;
- deterministic rows and drawings, and that each param changes its drawing;
- the `XL` case, and a golden slice per type.

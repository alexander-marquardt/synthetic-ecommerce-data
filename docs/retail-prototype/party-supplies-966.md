# Gifts: party supplies (gen#966, slice 1)

The Gifts department held 1,003 SKUs at the ceiling build, against a target of 3,000 in the 500K
mix (`docs/catalogue-mix-837.md`). It had nothing for a party, so a search for `balloons` or
`bunting` found no product of the kind. Slice 1 adds three types under `Gifts > Party Supplies`.

| Type | Spec | Leaf | Drawn by | Title-shown attributes | SKU axis |
|---|---|---|---|---|---|
| Balloon | `type_specs/balloon.py` | `Balloons` | `kit_party.balloon` | finish (Matte, Pearl, Metallic, Clear), style (Latex, Foil, Confetti) | six main colors x pack (`pack_size`) |
| Party Plate | `type_specs/party_plate.py` | `Party Tableware` | `kit_tableware.plate` | material (Paper, Bamboo, Card), kind (Dinner, Side) | six main colors x pack (`pack_size`) |
| Bunting | `type_specs/party_bunting.py` | `Party Decorations` | `kit_party.bunting` | material (Paper, Fabric, Felt), flag shape (Pennant, Square, Scalloped) | six main colors x length in metres (`item_length`) |

All three are derivable, offer the six main colors (gen#275) and are sold by the department's
own invented brands (gen#720). Each carries two text-match decoys: a class 4 one whose title
names a color its fields do not hold ("Red Ribbon Foil Balloons" in white) and a class 6 one
whose range name holds a color word ("Blue Moon Latex Balloons" in yellow). The shared pieces
(the paths, the colors, `packs()`, `lengths()`, `row()` and `decoy()`) are in `party_rows.py`.

## The drawings

`kit_party.py` draws two shapes, and each param's values are the lower-cased attribute values,
so a derived style that swaps one draws what it states (gen#512):

- `balloon`: by `style` a latex oval with its knot, a round foil one with a crimped seal, or a
  clear one holding confetti in the color; by `finish` its sheen (none when matte).
- `bunting`: two swags of flags, every second one a tint of the color; by `flag` pointed, square
  or round-bottomed flags; by `material` stitching (fabric) or a felt edge.

A plate's `kind` (dinner, side) and `finish` (a rim band) are the tableware plate's own params.
Both new shapes are filed as upright in `orientation.py`.

## Measured

The ceiling build (seed 0) holds 2,869 Gifts SKUs: Balloons 795, Bunting 624 and Party Plates
447 are new. `tests/test_retail_party_966.py` holds the slice's floor of 1,650 and, per type,
unique ids, titles, twin keys and SKUs, determinism and a golden slice.

Adding the three types moves the range names the build gives some Home tableware styles (the
name allocation is shared across the build), and the Home plates, bowls and dinner sets lose 36
SKUs between them.

## Remaining

Slices 2 (seasonal decorations: Christmas baubles, Halloween decorations, tinsel garlands) and
3 (ribbons and bows, gift tags, tissue paper) of gen#966.

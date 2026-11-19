# Décor drawings: wall art, decorative objects, garden statues, faux florals, fountains (gen#1022, slice 6)

The kit could not draw wall art, a tabletop decorative object, a garden statue, a faux floral
arrangement or a fountain. These are the largest décor classes the WANDS persona still lacked a
drawing for, in order of product count. This slice adds them as kit shapes in
`src/synthetic_ecommerce_data/domains/retail/kit_decor_pieces.py`. Each one draws through
`drawings.render` ([slice 2](render-and-finishes-1022.md)) in both finishes, at a product's own
width, height and depth. No generator product uses them yet.

The kit's own `ornament` (a vase, a bird figure, a glass orb) and `stems` (loose artificial stems
or stems in a vase) shapes in `kit_decor.py` are unchanged. The products drawn with them keep
their pictures.

Each shape is drawn from the attributes a record states. `kit_decor_pieces.PARAMS` is each
shape's table of params and the values it draws:

| Shape | Draws | Params (values) |
|---|---|---|
| `wall_art` | panels hung side by side on wires, each a picture of its subject | `panels` (1 to 3), `subject` (abstract, landscape, botanical, geometric), `frame` (canvas, thin, wide) |
| `decor_object` | a row of tabletop pieces on a shelf, largest first | `form` (sculpture, bowl, lantern, box), `material` (ceramic, metal, wood, glass), `pieces` (1 to 3) |
| `garden_statue` | a statue on its cast footing, on a plinth or not | `form` (animal, figure, sphere, obelisk), `base` (none, plinth), `material` (stone, metal, resin) |
| `faux_floral` | artificial greenery in a pot, or a wreath with a bow | `form` (arrangement, wreath, topiary, tree), `bloom` (leaf, flower, berry) |
| `fountain` | basins spilling water, on a column, a back panel or in a tray | `form` (tiered, wall, tabletop), `basins` (1 to 3), `material` (stone, metal, resin) |

The record's color fills the product itself: the art's ground, the piece, the statue, the pot or
the bow and the blooms, the fountain. The material shows as a texture of its own. Stone is
speckled, metal catches two upright sheens, resin one soft curved one, ceramic a glaze line and
wood its grain. Glass is drawn see-through. A picture's subject is drawn in the kit's book colors,
leaves and water in their own. What the product is drawn against stays light: a mat, a shelf, the
ground.

`tests/test_decor_drawings_1022.py` checks what the picture promises:

- Every value of every param draws a picture of its own, as a well-formed SVG, on every `form`.
- A value outside the table is refused with a `ValueError` naming the param.
- The drawn count is the stated count, on every form: one `class="panel"` per panel, one
  `class="piece"` per piece and one `class="basin"` per basin.
- Framed wall art draws one `class="frame"` per panel and a canvas none. A wide frame draws a mat
  and a thin one does not. A statue stands on a plinth only when it says so. Stone is speckled
  and metal or resin is not. Wood shows its grain. Glass is see-through. A wreath hangs from a
  bow, and the other florals stand in a pot. Flowers and berries are drawn only when the record
  says so.
- A White piece reads white (gen#226).
- Each type draws through `drawings.render` in both finishes, at its own dimensions.

`drawings.PROPORTIONS` gives each shape its nominal width, height and depth in inches. A set of
panels or of pieces is measured as a set:

| Shape | View | Width | Height | Depth |
|---|---|---|---|---|
| `wall_art` | front | 36 | 24 | 1.5 |
| `decor_object` | front | 12 | 10 | 6 |
| `garden_statue` | front | 14 | 24 | 12 |
| `faux_floral` | front | 18 | 24 | 18 |
| `fountain` | front | 30 | 48 | 30 |

`wall_art` and `decor_object` are `level` in `orientations/decor_pieces.py` (#1045). Wall art
hangs level, and a set drawn as several items is level too (#884). The other three are `upright`.

## What comes next

Slice 7 adds the `rug` (kitchen mats, doormats, kids' rugs), `wall_light` (vanity lighting) and
bench variants. Slice 5 ships a home type in a generator build with its own products.

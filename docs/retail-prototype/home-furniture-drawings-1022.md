# Home furniture drawings: bar stools, desks, office chairs, TV stands, kitchen islands (gen#1022, slice 1)

The kit could draw dining tables, chairs, wardrobes and sofas, but not a bar stool, a desk, an
office chair, a TV stand or a kitchen island. A home department that grows into those types needs
them drawn first. This slice adds them as kit shapes in
`src/synthetic_ecommerce_data/domains/retail/kit_home_furniture.py`, and no generator product uses
them yet. gen#1022's later slices add the public draw call with its finishes, the rest of the home
types, and the products that use them.

Each shape is drawn from the attributes a record states. `kit_home_furniture.PARAMS` is each
shape's table of params and the values it draws:

| Shape | Params (values) |
|---|---|
| `bar_stool` | `height` (counter, bar), `back` (none, low, full), `seat` (round, square), `base` (four_leg, pedestal, sled) |
| `desk` | `outline` (rectangular, l_shaped), `drawers` (0 to 4), `legs` (straight, panel, hairpin) |
| `office_chair` | `back` (mid, high), `cover` (mesh, fabric), `arms` (yes, no), `base` (castor, sled) |
| `tv_stand` | `doors` (0 to 4), `shelves` (0 to 3), `legs` (short, plinth, hairpin) |
| `kitchen_island` | `doors` (0 to 4), `drawers` (0 to 3), `top` (wood, marble_effect, steel), `wheels` (no, yes) |

`tests/test_home_furniture_drawings_1022.py` holds what the picture promises:

- every value of every param draws a picture of its own, and a well-formed SVG;
- a value outside the table is refused with a `ValueError` naming the param;
- the drawn count is the stated count: one `class="drawer"` front per drawer, one `class="door"`
  per door, one `class="shelf"` board per shelf;
- a bar-height seat stands higher than a counter-height one, an office chair has arms only when
  it says so, and an L-shaped desk draws its return;
- a White piece reads white, by the gen#226 rule the rest of the furniture range keeps: legs,
  castors and gas lifts are the kit's metal, and no body is shaded far toward black.

Each shape is `upright` in the orientation table (`orientation.py`, #860).

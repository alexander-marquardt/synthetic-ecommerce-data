# Garden, slice 1 (gen#961)

The Garden department held machines, barbecues, furniture sets, parasols and plants, far short
of the 9,000 SKUs the 500K mix plans for it (`docs/catalogue-mix-837.md`), so a search for a
`planter`, a `solar path light` or a `folding garden chair` found nothing. Slice 1 adds three
types, each a spec of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Planter | `type_specs/planter.py` | Garden > Pots & Planters > Planters | Round Ceramic, Square Plastic, Tall Fiberglass, Trough Concrete, Round Galvanized Steel | color x width (cm) |
| Outdoor Light | `type_specs/outdoor_light.py` | Garden > Outdoor Lighting > Path Lights / Wall Lights | Solar Lantern, Plug-In Bollard, Battery Globe (path); Solar Lantern, Hardwired Bulkhead, Battery Cube (wall) | color x single, 2 pack, 4 pack |
| Garden Chair | `type_specs/garden_chair.py` | Garden > Garden Furniture > Garden Chairs | Folding Acacia, Stacking Steel, Reclining Aluminum, Adirondack Rattan, Stacking Plastic | color x single, 2 pack, 4 pack |

The title of each is `<value> <value> <type>`: a planter's shape and material, a light's power
source and style, a chair's style and material. Every template offers the six main colors
(gen#275) and comes from the department's invented brands (`outdoor_helpers`). `packs()` in
`outdoor_helpers` writes a pack axis as `Single` or `<n> pack`.

**Drawings.** `kit_patio.py` draws three shapes. `planter` takes `form` (round, square, tall,
trough), which draws the pot's outline, and `material` (ceramic, plastic, fiberglass, concrete,
galvanized steel), which draws its surface marks. `outdoor_light` takes `style` (lantern,
bollard, globe, bulkhead, cube), which draws the head, `power_source` (solar, plug-in, hardwired,
battery), which draws a solar panel, a cable or a battery box, and `mounting` (ground stake,
wall). `garden_chair` takes `style` (folding, stacking, reclining, adirondack) and `material`
(acacia, steel, aluminum, rattan, plastic). Each param is the lower-cased attribute value, so a
derived style that swaps the value is drawn true (gen#512).

**Breadth.** The three types are derivable. The scale pools values per leaf, so a path light
never takes a wall light's style. A derived style's twin key is its leaf, brand and title, so a
leaf yields at most (title-shown value combinations x brands) styles.

**Decoys.** Each type carries fifteen text-match decoys in `garden_rows.py` (gen#294), three of
each class: a cushion, an apron and a candle that hold the type word; a real product that names a
material or power source it lacks ("Plastic Free Round Ceramic Planter", "Plug-In Bollard Path
Light, Not Solar"); a short title with a color word ("Red Harrier Planter", which draws the rim
red); a part's color ("Green Round Ceramic Planter with Red Rim"); and a color in the description
only. `kit_patio.PARTS` lists the parts a decoy can name, and `kit_garden.PARTS` takes them.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. The
slice's floor is 3,400 Garden SKUs at the ceiling build, a third of the way to the issue's
target. Hand tools, watering cans and bird care (slice 2), then garden tables, grill accessories
and storage (slice 3) are the rest of gen#961. The guards are in
`tests/test_retail_garden_961.py` and `tests/test_retail_garden_203.py`.

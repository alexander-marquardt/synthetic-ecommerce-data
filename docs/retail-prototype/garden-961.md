# Garden, slices 1 to 3 (gen#961)

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

## Slice 2: hand tools, watering cans and bird feeders

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Hand Tool | `type_specs/hand_tool.py` | Garden > Garden Tools > Hand Tools | Stainless Steel Trowel, Carbon Steel Hand Fork, Cast Aluminum Cultivator, Stainless Steel Transplanter, Carbon Steel Pruner | handle color |
| Watering Can | `type_specs/watering_can.py` | Garden > Watering > Watering Cans | Classic Plastic, Long Reach Galvanized Steel, Indoor Powder-Coated Steel, Slimline Plastic, Classic Galvanized Steel | color x capacity (l) |
| Bird Feeder | `type_specs/bird_feeder.py` | Garden > Bird Care > Bird Feeders | Metal Tube, Plastic Window, Metal Suet Cage, Wood Platform, Plastic Tube | color x single, 2 pack, 3 pack |

A hand tool's title is `<head metal> <kind>`, a watering can's `<style> <material> Watering Can`
and a bird feeder's `<material> <style> Bird Feeder`. `size_axes.AXES` reads a watering can by
capacity.

**Drawings.** `kit_garden_care.py` draws three shapes. `hand_tool` takes `kind` (trowel, hand
fork, cultivator, transplanter, pruner), which draws the head (or a pruner's two blades and
handles), and `head` (stainless steel, carbon steel, cast aluminum), which draws its metal.
`watering_can` takes `style` (classic, long reach, indoor, slimline), which draws the body and
spout, and `material` (plastic, galvanized steel, powder-coated steel), which draws its surface
marks. `bird_feeder` takes `style` (tube, window, suet cage, platform) and `material` (metal,
plastic, wood). `kit_garden_care.PARTS` (a tool's grip, ferrule and hang loop; a can's rose,
handle and spout; a feeder's roof, perch and hanger) is added to `kit_garden.PARTS`.

**Decoys.** Each type carries fifteen decoys in `garden_rows.py`, three of each class, as in
slice 1: a cushion and a candle that hold the type word; a real product that names plastic it
lacks ("Carbon Steel Hand Fork, Not Plastic", "Plastic Free Classic Watering Can"); a short
title with a color word ("Red Harrier Trowel"); a part's color ("Green Classic Watering Can with
Red Rose"); and a color in the description only.

## Slice 3: garden tables, grill accessories and garden storage

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Garden Table | `type_specs/garden_table.py` | Garden > Garden Furniture > Garden Tables | Bistro Acacia, Dining Aluminum, Side Steel, Folding Acacia, Dining Steel | color x width (cm) |
| Grill Accessory | `type_specs/grill_accessory.py` | Garden > Barbecues & Grills > Grill Tools / Grill Covers | Stainless Steel Tool Set, Bamboo Tool Set, Stainless Steel Brush, Bamboo Tongs (tools); Polyester Kettle, Canvas Cabinet (covers) | color |
| Garden Storage | `type_specs/garden_storage.py` | Garden > Garden Storage > Storage Boxes / Outbuildings | Resin Deck Box, Wood Storage Bench, Resin Tall Cabinet (boxes); Steel Apex, Wood Pent (outbuildings) | color x capacity (l) for a box, color x width (cm) for a shed |

A garden table's title is `<style> <material> Garden Table`, a grill tool's `<material> Grill
<tool>`, a grill cover's `<material> <fits> Grill Cover`, a storage box's `<material> <style>`
and a shed's `<material> <roof> Shed`. The scale pools values per leaf, so a cover never takes a
tool's material and a box never takes a shed's roof. `size_axes.AXES` reads a garden table by
width and garden storage by capacity, then width.

**Drawings.** `kit_garden_yard.py` draws three shapes. `garden_table` takes `style` (bistro,
dining, side, folding), which draws the top and the legs, and `material` (acacia, steel,
aluminum), which draws its marks. `grill_accessory` takes `kind` (tool set, brush, tongs, kettle,
cabinet), which draws the tools or the cover, and `material` (stainless steel, bamboo, polyester,
canvas). `garden_storage` takes `style` (deck box, storage bench, tall cabinet, apex, pent) and
`material` (resin, wood, steel). `kit_garden_yard.PARTS` (a table's legs, rim and feet; an
accessory's trim, strap and tag; storage's lid, handle and hinges) is added to
`kit_garden.PARTS`.

**Decoys.** Each type carries fifteen decoys in `garden_rows.py`, three of each class, as in
slices 1 and 2: a cushion and a candle that hold the type word; a real product that names
plastic it lacks ("Plastic Free Acacia Garden Table", "Bamboo Grill Tongs, Not Plastic"); a
short title with a color word ("Red Harrier Grill Brush"); a part's color ("Green Bistro Garden
Table with Red Legs"); and a color in the description only.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. Slice
1's floor was 3,400 Garden SKUs at the ceiling build, a third of the way to the issue's target;
slice 2's was 6,000 and slice 3's is 8,550, within five percent of the 9,000 the issue asks for.
Slice 3 completes gen#961. The guards are in `tests/test_retail_garden_961.py` and
`tests/test_retail_garden_203.py`.

# Sports & Outdoors, outdoors and winter sports, slice 3 (gen#959)

Slice 2 (`docs/retail-prototype/sports-fitness-team-959.md`) took the retail `Sports & Outdoors`
department to about 7,500 SKUs at the ceiling build, against the 11,000 of
`docs/catalogue-mix-837.md`. Slice 3, the last, adds eight breadth types: hiking backpacks under a
new Hiking family, coolers and insulated water bottles under Camping, bike lights and bike locks
under Cycling, and sleds, snowboards and ski goggles under a new Winter Sports family. Every type
is a spec of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Hiking Backpack | `type_specs/hiking_backpack.py` | Sports & Outdoors > Hiking > Hiking Backpacks | internal frame (two), external frame, frameless | color x capacity (l) |
| Cooler | `type_specs/cooler.py` | Sports & Outdoors > Camping > Coolers | hard, soft (two), wheeled | color x capacity (l) |
| Insulated Water Bottle | `type_specs/insulated_water_bottle.py` | Sports & Outdoors > Camping > Insulated Water Bottles | straw lid, screw cap, chug lid (two) | color x capacity (ml) |
| Bike Light | `type_specs/bike_light.py` | Sports & Outdoors > Cycling > Bike Lights | front, rear (two), twin-pack | color x light output (lumens) |
| Bike Lock | `type_specs/bike_lock.py` | Sports & Outdoors > Cycling > Bike Locks | shackle, chain, folding, cable | color x length (cm) |
| Sled | `type_specs/sled.py` | Sports & Outdoors > Winter Sports > Sleds | toboggan, saucer (two), steerable | color x length (cm) |
| Snowboard | `type_specs/snowboard.py` | Sports & Outdoors > Winter Sports > Snowboards | camber (two), rocker, flat | color x length (cm) |
| Ski Goggles | `type_specs/ski_goggles.py` | Sports & Outdoors > Winter Sports > Ski Goggles | spherical, cylindrical (two), toric | color x size S to L |

The paths are in `outdoor_winter_rows.py`. The rows use the department's own brands, so no brand
joins the scale roster and `range_ownership.py` is unchanged. Every type offers the six main
colors of gen#275 across its templates. Bike lights and bike locks were listed under "Not built"
in `docs/retail-sports-tree.md` (optional in gen#352); they leave that table now they are built.

**Titles.** Each type's title shows three values a shopper reads on the shelf: a pack's fabric,
frame and opening (Top Lid, Roll Top, Panel Zip), a cooler's use, type and ice retention (2-Day to
7-Day), a bottle's coating, mouth and lid, a light's power, position and modes, a lock's grade
(Heavy-Duty, Everyday, Lightweight), type and opening (Key, Combination), a sled's build, seats
(1-Person, 2-Person) and type, a snowboard's riding style, shape and profile, and goggles' lens
coating, lens shape and fit (Regular, Over-the-Glasses, Low-Bridge). The title words avoid the
lead words the jeans range numbers its lines by (`line_grammar`), so the scaled build's brands
stay distinct. A bike light's output is a rating, not a size (`size_axes.NOT_SIZES`), and its
own option (`light_output`).

**Drawings.** `kit_outdoor_winter.py` draws eight shapes, each taking one param, the lower-cased
attribute value, so a derived style that swaps the value is drawn true (gen#512):
`hiking_backpack` takes `pack_frame`, `cooler` `cooler_type`, `bottle_insul` `bottle_lid`,
`bike_light` `light_position`, `bike_lock` `lock_type`, `sled` `sled_type`, `snowboard`
`board_profile` and `ski_goggles` `lens_shape`. A lock, a bottle, a pack and a snowboard stand
upright; a light, a cooler, goggles and a sled lie level (`orientations/outdoor_winter.py`,
gen#849 and #1045). A capacity and a length are size axes (`size_axes.py`, gen#719).

**Breadth.** The scaled build draws more styles from each type by the three values its title
shows. The department's rate is left as slice 2 set it: the ruling of 2026-11-16 holds department
shares to loose guidance, and the rate moves no style of the ceiling build, where every template is
drawn until it is exhausted.

**Decoys.** Each type carries two class-8 text-match decoys in
`feature_decoys/outdoor_winter_959.py` (DY9621 to DY9636): a product of another department whose
title holds the shopper's words, such as a `Snowboard Print T-Shirt` or a `Cooler Print Cushion`.
No title or description names a color. `tests/decoy_true_nodes/outdoor_winter.py` maps each noun
to its node. `outdoor_winter_959.ids()` keeps them out of the apparel decoys' exemplars and out of
the kids' films neighbours, as slices 1 and 2 do.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the authored
and derived split are read from the build (`retail_figures`), never typed here. Slice 3's floor is
10,450 SKUs, 95% of the 11,000 target; the guards are in `tests/test_retail_sports_959.py`.

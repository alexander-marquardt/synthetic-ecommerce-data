# Toys in depth, slice 3: arts and crafts kits, remote-control vehicles and learning toys (gen#960)

The Toys department held 12 craft kits, all authored and none derived, and no remote-control
vehicle or learning toy, so a search for `bead kit`, `remote control car` or `shape sorter`
found a handful of styles or none. Slice 3 makes the three types derivable breadth types:

| Type | Spec | Path | Title shows | SKU axis |
|---|---|---|---|---|
| Arts and Crafts Kit | `type_specs/arts_and_crafts_kit.py` | Toys > Arts & Crafts > Craft Kits | theme, craft (bead, mosaic, gem art, pom-pom) | piece count (no color) |
| Remote-Control Vehicle | `type_specs/remote_control_vehicle.py` | Toys > Vehicles > Remote-Control Vehicles | theme, vehicle (car, truck, boat, helicopter) | the six main colors |
| Learning Toy | `type_specs/learning_toy.py` | Toys > Learning Toys > Early Learning | theme, toy (activity cube, shape sorter, learning tablet, counting abacus) | the six main colors |

The older craft kits stay in `toys_rows` as templates only; the new rows in the spec file are
the derivable ones. A craft kit holds pieces of every color, so it has no color selector, the
exception the craft kits already declare (ruling 2026-10-13, gen#275). Every theme is invented
(ruling 2026-10-30, gen#720). A derived style keeps its template's age (6+ kits and vehicles,
18+ months learning toys). `Remote-Control Vehicle` and `Learning Toy` are kinds of the toys line
grammar (`line_grammar_families/toys.py`).

**Drawings.** `kit_toys_learning.py` draws three shapes. `craft_tub` opens the kit's box: the
craft's beads, tiles, gems or pom-poms in four trays. `rc_vehicle` draws the car, truck, boat or
helicopter in the body's color with its handset. `learning_toy` draws the cube, sorter, tablet or
abacus in the toy's color. Each prints the theme on a name panel, as the title shows it, so two
derived styles of one kind never share a results tile, and a derived style that swaps the value is
drawn true (gen#512). No drawing prints a number: a kit's piece counts share one image.

**Decoys.** Each type carries a class 6 decoy (another type's word in a range name, such as
`Kite Chaser Remote-Control Helicopter`) and a class 4 decoy (a material claim the product does
not have, such as a glass-look bead kit whose beads are plastic).

**Measured** (ceiling build, seed 0, on main `d9937f05` with this slice): Toys holds 6,557 SKUs,
5,093 more than main's 1,464; the three types hold 1,544, 1,655 and 1,911. With slice 1 (+1,938,
board games and puzzles) and slice 2 (+3,768, figures, dolls and building sets) the department
passes the 10,450 SKUs of gen#960's Done-when. Trampolines and swings are left out: the floor is
met without them. The guards are in `tests/test_retail_toys_960_slice3.py`.

# Toys in depth, slice 2: action figures, dolls and building sets (gen#960)

The Toys department held 25 dolls and 89 building sets, all authored and none derived, and no
action figure, so a search for `action figure`, `rag doll` or `pirate building set` found a
handful of styles. Slice 2 makes the three types derivable breadth types:

| Type | Spec | Path | Title shows | SKU axis |
|---|---|---|---|---|
| Action Figure | `type_specs/action_figure.py` | Toys > Figures & Playsets > Action Figures | character, kind (superhero, space, adventure) | the six main colors |
| Doll | `type_specs/doll.py` | Toys > Dolls & Accessories > Dolls | theme, kind (fashion, baby, rag) | the six main colors |
| Building Set | `type_specs/building_set.py` | Toys > Building & Construction > Building Sets | theme, model (vehicle, tower, creature) | piece count (no color) |

The older dolls and building sets stay in their shared row modules as templates only; the new
rows in the spec files are the derivable ones. Every character and theme is invented (ruling
2026-10-30, gen#720). A derived style keeps its template's age (4+ figures, 3+ dolls, 6+ sets).
`Action Figure` is a kind of the toys line grammar (`line_grammar_families/toys.py`).

**Drawings.** `kit_toys_figures.py` draws three shapes. `action_figure` puts a figure in a
blister on a card, with a cape, a helmet or a hat by its kind; `doll_box` puts the doll of the
kind in a window box; `brick_box` draws the set's box with its model in a corner. Each prints
the character or theme on a name panel, as the title shows it, so two derived styles of one
kind never share a results tile, and a derived style that swaps the value is drawn true
(gen#512). No drawing prints a number: a style's sizes share one image.

**Never derived.** `scale.left_out()` now also leaves out the film merchandise (`kids_films`,
gen#887) and the Barry Plotter range (`barry_plotter`, gen#925): the building set spec reads the
Barry Plotter rows, and a derived copy would sell the range under another brand. No derivable
spec held them before, so the build of main does not move.

**Decoys.** Each type carries a class 6 decoy (another type's word in a range name, such as
`Kite Flyer Space Action Figure`) and a class 4 decoy (a material claim the product does not
have, such as a metal-look figure that is plastic).

**Measured** (ceiling build, seed 0): the three types' styles and SKUs are read from the build
(`retail_figures`), never typed here. Together with slice 1 (board games and puzzles) the slice
takes Toys past 7,000 of the 11,000 target in `docs/catalogue-mix-837.md`; arts and crafts,
remote-control vehicles, learning toys and outdoor play are the last slice of gen#960. The
guards are in `tests/test_retail_toys_960_slice2.py`.

# Utility hooks: home hardware for general retail (gen#958, slice 3)

`Hardware > Fasteners > Hooks > Utility hooks` is a new modelled type, `product_types/fasteners/utility_hooks.py`, and `tests/test_type_utility_hooks.py` runs the per-type gates on it. It is one of the six home-hardware types gen#958 plans for the `Hardware` department, after the picture hangers ([picture-hangers-958.md](picture-hangers-958.md)), the cabinet hinges ([cabinet-hinges-958.md](cabinet-hinges-958.md)), the cabinet knobs ([cabinet-knobs-958.md](cabinet-knobs-958.md)) and the shelf brackets ([shelf-brackets-958.md](shelf-brackets-958.md)). The large build (`ecom-generate build --lines 39000`) has its own count of them in `measured_builds.json`. The test reads that count and requires at least 248, which is 95% of a sixth of the issue's 1,564.

**Root.** The hook is filed under `Fasteners`, as the other home-hardware types are, in its own `Hooks` node. A new root would have to be one of the real catalogue's own top-level menu entries (`REAL_CATALOG_ROOTS` in `tests/test_catalog_generate.py`), and the one that fits, `Hardware`, is already the name of a department.

**Lines.** A line is one brand's hooks of one style (cup, J-shaped, double prong or S-shaped), one metal (steel, brass or zinc alloy) and one color. Its SKUs are a run of the lengths that style is stocked in: a cup hook 1" to 2", a J-shaped hook 2" to 8", a double-prong coat hook 3" to 6", and an S-shaped hook 2" to 6".

**Lengths.** A length is published as `Length` in inches, in the brand's inch style (`3"`, `3 in.` or `3.000"`), the way the catalogue's other inch lengths are, so the facet ranges across them. No standard fixes the stocked lengths, so no line claims one and each record's provenance says so. A load rating is not published, for the reason the shelf brackets give: the industrial unit table reads no kilograms.

**Titles.** A title names the length, the style and the color (`Utility Hook: 4" L, J-Shaped, Black`), so a search for `cup hook` or `double prong hook` finds the style.

**Colors.** The hook comes in all six main colors (gen#275), a vinyl-coated or painted finish over the metal. The color rotation steps one further at each full turn of the 12 style and metal combinations, so every combination is built in more than one color.

**Decoys.** Two lines in every six name a room before the item ("Laundry Series Utility Hook"). A search for `mudroom`, `entryway`, `laundry` or `patio` then finds a utility hook, which a category policy can remove (gen#294).

**Price.** Generated, not measured: the price census has no utility hooks. It is about the length to the 0.8 power, anchored at 3 USD for a 3" hook.

**Drawing.** The hook is drawn side on, as long as its length, filled with the record's color. Each style has its own outline: a threaded shank with an open curl below it (cup), a wall plate with an arm that turns up at its end (J-shaped), a wall plate with a short and a long arm, each with a ball tip (double prong), or two curls open at opposite ends (S-shaped).

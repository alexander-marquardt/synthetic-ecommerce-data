# Cabinet knobs: home hardware for general retail (gen#958, slice 3)

`Hardware > Fasteners > Cabinet hardware > Cabinet knobs` is a new modelled type, `product_types/fasteners/cabinet_knobs.py`, and `tests/test_type_cabinet_knobs.py` runs the per-type gates on it. It is the second of six home-hardware types gen#958 plans for the `Hardware` department, after the picture hangers ([picture-hangers-958.md](picture-hangers-958.md)). The cabinet hinges of the next slice are filed beside it under `Cabinet hardware`. The large build (`ecom-generate build --lines 39000`) has its own count of them in `measured_builds.json`. The test reads that count and requires at least 248, which is 95% of a sixth of the issue's 1,564.

**Root.** The knob is filed under `Fasteners`, as the picture hangers are. A new root would have to be one of the real catalogue's own top-level menu entries (`REAL_CATALOG_ROOTS` in `tests/test_catalog_generate.py`), and the one that fits, `Hardware`, is already the name of a department.

**Lines.** A line is one brand's knobs of one style (round, mushroom, square or drop ring), one metal (brass, stainless steel or aluminum) and one color. Its SKUs are a run of the diameters that style is stocked in: a square knob 3/4" to 1-1/2", a mushroom knob 1" to 1-3/4".

**Diameters.** A diameter is published as `Diameter` in inches, in the brand's inch style (`1-1/4"`, `1-1/4 in.` or `1.250"`), the way the catalogue's other inch lengths are, so the facet ranges across them.

**Titles.** A title names the diameter, the style and the color (`Cabinet Knob: 1-1/4" Dia, Round, Blue`), so a search for `mushroom knob` or `drop ring` finds the style.

**Colors.** The knob comes in all six main colors (gen#275), a painted or powder-coated finish over the metal. The color rotation steps one further at each full turn of the 12 style and metal combinations, so every combination is built in more than one color.

**Decoys.** Two lines in every six name the furniture a knob goes on before the item ("Dresser Series Cabinet Knob"). A search for `dresser` or `vanity` then finds a cabinet knob, which a category policy can remove (gen#294).

**Price.** Generated, not measured: the price census has no cabinet knobs. It is about the diameter to the 0.8 power, anchored at 4.5 USD for a 1-1/4" knob.

**Drawing.** The knob is drawn from the side, standing off the cabinet face on its stem, filled with the record's color and sized to its diameter. Each style has its own outline: a ball, a dome, a block, or a ring hanging from a small boss.

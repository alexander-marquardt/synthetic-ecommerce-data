# Cabinet hinges: home hardware for general retail (gen#958, slice 2)

`Hardware > Fasteners > Cabinet hardware > Cabinet hinges` is a new modelled type, `product_types/fasteners/cabinet_hinges.py`, and `tests/test_type_cabinet_hinges.py` runs the per-type gates on it. It is one of the six home-hardware types gen#958 plans for the `Hardware` department, after the picture hangers ([picture-hangers-958.md](picture-hangers-958.md)). The large build (`ecom-generate build --lines 39000`) has its own count of them in `measured_builds.json`. The test reads that count and requires at least 248, which is 95% of a sixth of the issue's 1,564.

**Root.** The hinge is filed under `Fasteners`, as the picture hangers are. A new root would have to be one of the real catalogue's own top-level menu entries (`REAL_CATALOG_ROOTS` in `tests/test_catalog_generate.py`), and the one that fits, `Hardware`, is already the name of a department.

**Lines.** A line is one brand's hinges of one style (butt, flush, surface mount or overlay), one metal (steel, brass or stainless steel) and one color. Its SKUs are a run of the lengths that style is stocked in: a butt hinge 1-1/2" to 3-1/2", a flush hinge 2" to 3", an overlay hinge 2" to 2-3/4".

**Lengths.** A length is published as `Length` in inches, in the brand's inch style (`2-1/2"`, `2-1/2 in.` or `2.500"`), the way the catalogue's other inch lengths are, so the facet ranges across them. No standard fixes the stocked lengths, so no line claims one and each record's provenance says so.

**Titles.** A title names the length, the style and the color (`Cabinet Hinge: 2-1/2" L, Butt, Blue`), so a search for `butt hinge` or `overlay hinge` finds the style.

**Colors.** The hinge comes in all six main colors (gen#275), a painted or powder-coated finish over the metal. The color rotation steps one further at each full turn of the 12 style and metal combinations, so every combination is built in more than one color.

**Decoys.** Two lines in every six name the furniture a hinge goes on before the item ("Wardrobe Series Cabinet Hinge"). A search for `wardrobe` or `cupboard` then finds a cabinet hinge, which a category policy can remove (gen#294).

**Price.** Generated, not measured: the price census has no cabinet hinges. It is about the length to the 0.8 power, anchored at 4 USD for a 2-1/2" hinge.

**Drawing.** The hinge is drawn face on and opened flat, as tall as its length, filled with the record's color: two leaves either side of the knuckle, with screw holes. Each style has its own outline: two equal leaves (butt), a narrower leaf that nests in the other (flush), two flared leaves (surface mount), or a cranked leaf that steps out to lap the cabinet face (overlay).

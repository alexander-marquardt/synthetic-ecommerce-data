# Shelf brackets: home hardware for general retail (gen#958, slice 3)

`Hardware > Fasteners > Shelving hardware > Shelf brackets` is a new modelled type, `product_types/fasteners/shelf_brackets.py`, and `tests/test_type_shelf_brackets.py` runs the per-type gates on it. It is one of the six home-hardware types gen#958 plans for the `Hardware` department, after the picture hangers ([picture-hangers-958.md](picture-hangers-958.md)) and the cabinet hinges ([cabinet-hinges-958.md](cabinet-hinges-958.md)). The large build (`ecom-generate build --lines 39000`) has its own count of them in `measured_builds.json`. The test reads that count and requires at least 248, which is 95% of a sixth of the issue's 1,564.

**Root.** The bracket is filed under `Fasteners`, as the picture hangers and the hinges are. A new root would have to be one of the real catalogue's own top-level menu entries (`REAL_CATALOG_ROOTS` in `tests/test_catalog_generate.py`), and the one that fits, `Hardware`, is already the name of a department.

**Lines.** A line is one brand's brackets of one style (L-shaped, heavy duty, decorative or floating), one metal (steel, aluminum or cast iron) and one color. Its SKUs are a run of the arm lengths that style is stocked in: an L-shaped bracket 4" to 12", a heavy-duty one 8" to 16", a decorative one 6" to 12", and a floating-shelf bracket's rods 4" to 8".

**Lengths.** A length is published as `Length` in inches, in the brand's inch style (`8"`, `8 in.` or `8.000"`), the way the catalogue's other inch lengths are, so the facet ranges across them. No standard fixes the stocked lengths, so no line claims one and each record's provenance says so. A load rating is not published: the industrial unit table reads no kilograms, so a `Load Capacity` could carry pounds-force only (see the picture hangers), and the type keeps to the attributes the hinges publish.

**Titles.** A title names the length, the style and the color (`Shelf Bracket: 8" L, Heavy Duty, Black`), so a search for `heavy duty shelf bracket` or `floating shelf bracket` finds the style.

**Colors.** The bracket comes in all six main colors (gen#275), a painted or powder-coated finish over the metal. The color rotation steps one further at each full turn of the 12 style and metal combinations, so every combination is built in more than one color.

**Decoys.** Two lines in every six name a place a shelf goes before the item ("Garage Series Shelf Bracket"). A search for `garage`, `pantry`, `closet` or `bookcase` then finds a shelf bracket, which a category policy can remove (gen#294).

**Price.** Generated, not measured: the price census has no shelf brackets. It is about the length to the 0.9 power, anchored at 5 USD for an 8" bracket.

**Drawing.** The bracket is drawn side on, its arm as long as its length, filled with the record's color: the arm along the top that the shelf rests on and the leg down the wall, with screw holes. Each style has its own outline: the bare arm and leg (L-shaped), a triangular gusset between them (heavy duty), a curved brace (decorative), or a wall plate with two rods that slide into the shelf (floating).

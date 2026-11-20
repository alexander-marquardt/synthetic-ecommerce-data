# Wall anchors: home hardware for general retail (gen#958, slice 3)

`Hardware > Fasteners > Anchors > Wall anchors` is a new modelled type, `product_types/fasteners/wall_anchors.py`, and `tests/test_type_wall_anchors.py` runs the per-type gates on it. It is the last of the six home-hardware types gen#958 plans for the `Hardware` department, after the picture hangers ([picture-hangers-958.md](picture-hangers-958.md)), the cabinet hinges ([cabinet-hinges-958.md](cabinet-hinges-958.md)), the cabinet knobs ([cabinet-knobs-958.md](cabinet-knobs-958.md)), the shelf brackets ([shelf-brackets-958.md](shelf-brackets-958.md)) and the utility hooks ([utility-hooks-958.md](utility-hooks-958.md)). The large build (`ecom-generate build --lines 39000`) has its own count of them in `measured_builds.json`. The test reads that count and requires at least 248, which is 95% of a sixth of the issue's 1,564.

**Root.** The anchor is filed under `Fasteners > Anchors`, beside the trade sleeve and wedge anchors, in its own `Wall anchors` leaf. The two-SKU `nylon_wall_anchors` ("Screw Anchor", under `Plastic wall anchors`) stays what it is: a text-match decoy for the industrial seed query `screws` (gen#462). This type is the homeowner depth the issue asks for.

**Lines.** A line is one brand's anchors of one style (ribbed, self-drilling, winged toggle or conical), one plastic (nylon, polyolefin or ABS plastic) and one color. Its SKUs are a run of the lengths that style is stocked in: a ribbed anchor 3/4" to 1-1/2", a self-drilling drywall anchor 1" to 1-3/4", a winged toggle 1-1/4" to 2-1/2", and a conical anchor 3/4" to 2".

**Lengths.** A length is published as `Length` in inches, in the brand's inch style, the way the catalogue's other inch lengths are, so the facet ranges across them. No standard fixes the stocked lengths, so no line claims one and each record's provenance says so.

**Titles.** A title names the length, the style and the color (`Wall Anchor: 1" L, Self-Drilling, Yellow`), so a search for `self-drilling anchor` or `toggle anchor` finds the style.

**Colors.** Plastic anchors are sold color-coded, and the anchor comes in all six main colors (gen#275). The color rotation steps one further at each full turn of the 12 style and plastic combinations, so every combination is built in more than one color.

**Decoys.** Two lines in every six name a room before the item ("Nursery Series Wall Anchor"). A search for `nursery`, `hallway`, `gallery` or `studio` then finds a wall anchor, which a category policy can remove (gen#294).

**Price.** Generated, not measured: the price census has no wall anchors. A pack is about the length to the 0.6 power, anchored at 5 USD for 1" anchors.

**Drawing.** The anchor is drawn side on, collar at the left, as long as its length and filled with the record's color. Each style has its own outline: a straight sleeve with ribs across it (ribbed), a threaded body tapering to a drill point (self-drilling), a slim sleeve with two wings folded back from its tip (winged toggle), or a sleeve tapering to its tip with a split along it (conical).

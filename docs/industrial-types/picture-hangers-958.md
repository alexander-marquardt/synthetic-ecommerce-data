# Picture hangers: home hardware for general retail (gen#958, slice 1)

`Hardware > Fasteners > Picture hanging > Picture hangers` is a new modelled type, `product_types/fasteners/picture_hangers.py`, and `tests/test_type_picture_hangers.py` runs the per-type gates on it. It is the first of six home-hardware types gen#958 plans for the `Hardware` department (picture hanging, knobs and hinges, shelf brackets, hooks, wall anchors). The large build (`ecom-generate build --lines 39000`) holds 395 of them; the test reads that count from `measured_builds.json` and holds it to at least 248, 95% of a sixth of the issue's 1,564.

**Lines.** A line is one brand's hangers of one style (nail hook, sawtooth hanger, D-ring hanger or hanging kit), one metal (steel, stainless steel or brass) and one color. Its SKUs are a run of the weight ratings that style is stocked in: a sawtooth strip 10 to 30 lb, a nail hook 10 to 100 lb.

**Ratings.** A rating is published as `Load Capacity` in pounds-force (`30 lbf`), the census name and the unit the casters, shackles and turnbuckles use: `tests/test_no_wrong_kind_values_404.py` holds a facet key to one quantity kind, so a `30 lb` mass beside their `lbf` force is refused. Kilograms are not offered: the industrial unit table (`core/entry.UNIT_FOR_SUFFIX`) reads neither `kg` nor `kgf`.

**Titles.** A title names the rating, the style and the color (`Picture Hanger: 50 lbf Load, Nail Hook, Blue`), so a search for `nail hook` or `sawtooth hanger` finds the style.

**Colors.** The hanger comes in all six main colors (gen#275). The color rotation steps one further at each full turn of the 12 style and metal combinations, so every combination is built in more than one color.

**Decoys.** Two lines in every six name a thing a hanger holds before the item ("Mirror Series Picture Hanger"). A search for `mirror` or `clock` then finds a picture hanger, which a category policy can remove (gen#294).

**Price.** Generated, not measured: the price census has no picture hangers. It is about the rating to the 0.45 power, anchored at 6 USD for a 30 lb hanger.

**Drawing.** The hanger is drawn face on, filled with the record's color and sized to its rating. Each style has its own outline: a bent hook with its nail, a toothed strip with two nail holes, a ring on a strap plate, or a hook beside a coil of wire.

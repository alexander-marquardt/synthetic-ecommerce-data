# Utility knives: a homeowner tool for general retail (gen#971, slice 3)

`Tools > Hand tools > Cutters > Utility knives` is a new modelled type, `product_types/hand_tools/utility_knives.py`, and `tests/test_type_utility_knives.py` runs the per-type gates over it. It is the fourth of the homeowner tools gen#971 adds to `Tools`, after tape measures, levels and stud finders.

**Lines.** A line is one brand's knives of one style, on the blade width that style takes, with one handle material (aluminum, zinc alloy or nylon) and one handle color. A retractable, folding or fixed-blade knife takes the 19 mm trapezoid blade. A snap-off knife takes a segmented blade, 9, 18 or 25 mm wide. No standard fixes the widths, and the provenance says so. Its SKUs are the pack sizes it is sold in: the knife with 3, 5, 10 or 20 blades, published as `Number of Blades`, a census name.

**Colors.** The handle comes in all six main colors (gen#275). The color rotation steps one further at each full turn of the 18 style, width and material combinations, so over 108 lines every combination is built in every color. At `--lines 39000`, 306 of the 388 SKUs are distinct specs, and the type's floor is 0.75 (`tests/test_catalog_brands_voice.py`).

**Decoys.** Two lines in every six name another tool before the item ("Scraper Series Utility Knife"). That way a search for that tool's word finds a utility knife (gen#294).

**Price.** The price is generated, not measured, because the price census has no utility knives. It is about the blade count to the 0.15 power, anchored at 12 USD for a knife with 5 blades.

**Drawing.** The knife is drawn from the side, its handle filled with the record's color and grown with the blade's width. A snap-off blade is drawn long and scored into segments, any other the trapezoid blade. A retractable or snap-off knife has its slider on top, a folding one its pivot. The pack's blades are laid out below the knife, five to a row, so siblings draw differently. The type is drawn `upright` (`domains/industrial/orientation.py`). The zinc alloy handle has its own fill and hatch in `core/drawing/style.py`.

**Names.** `Knife` is sold as `knives`, which the `-s`/`-es` plural rule did not read: `names.noun_forms` adds the `-fe` to `-ves` plural, and the head-noun test reads the leaf with it.

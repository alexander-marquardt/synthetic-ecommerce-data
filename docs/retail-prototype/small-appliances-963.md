# Small kitchen appliances, slice 1 (gen#963)

`Home > Small Appliances` held only kettles and toasters, both templates the scaled build never
derives, so a search for `air fryer`, `coffee maker` or `blender` found nothing. Slice 1 adds
three derivable types, each a spec of its own:

| Type | Spec | Path | Templates | Type values (drawn) | Second axis | SKU axis |
|---|---|---|---|---|---|---|
| Coffee Maker | `type_specs/coffee_maker.py` | Home > Small Appliances > Coffee Makers | 8, one per design, and 2 decoys | Drip, Espresso, Pod, Bean to Cup, Cold Brew | design (Classic, Retro, Compact, Digital, Slimline, Programmable, Stainless, Matte) | the six main colors |
| Air Fryer | `type_specs/air_fryer.py` | Home > Small Appliances > Air Fryers | 6 and 2 decoys | Single Basket, Dual Basket, Viewing Window, Rotisserie, Compact | controls (Digital, Dial, Smart, Touchscreen, Push Button, LED Display) | the six main colors times two capacities in litres (`capacity_l`, a declared size axis in `size_axes.AXES`), each at its price |
| Blender | `type_specs/blender.py` | Home > Small Appliances > Blenders | 8 and 2 decoys | Jug, Personal, Hand | design (Classic, Compact, Pro, Digital, Retro, High Speed, Glass Jar, Cordless) | the six main colors |

The shared pieces (the path, the brands, the six colors, `litres()`, `row()`, `table()` and
`decoy()`) are in `kitchen_appliance_rows.py`. `table()` makes a template for each brand, or for
each type value or second-axis value if there are more, and cycles the three together, so every
value is on a template. The brands are invented (ruling 2026-10-30, gen#720): Hearth & Table,
Lanternby, Calderby & Lune and Brackenmere Home, the four Home brands the kitchen family's
templates already carry, each with an owner, a mark and a house style already. The scaled build
adds the department's extra brands (`scale.EXTRA_BRANDS`) to each type's pool and makes one style
per brand and title, so the brands and the second axis bound each type's depth.

**No brand new to the build.** The range names (`range_ownership.Deal`) and the model words
(`line_grammar.Deal`) are dealt round the sorted set of every brand a derived style may carry, so
one brand new to that set moves the range name of a style in every department: the
large-appliance brands an earlier cut of this slice used moved the Office pens, pencils and
notebooks of gen#969. No template carries an extra brand either (`test_retail_scale.py`). The
three types are kinds of the kitchen family (`line_grammar_families/kitchen.py`), so a derived
title reads brand, model, design and type (`Lanternby Saute Stainless Cold Brew Coffee Maker`),
never a range name before the brand.

Each style is sold in red, blue, green, yellow, black and white (ruling 2026-10-13, gen#275), its
first color the hero the image shows.

**Drawings.** `kit_kitchen_appliances.py` draws three shapes, each taking `kind`, the lower-cased
type value, so a derived style that swaps the value is drawn true (gen#512). `coffee_maker` draws
a drip machine with its carafe, an espresso machine with a portafilter and steam wand, a pod
machine, a bean-to-cup machine with its hopper, or a cold-brew tower. `air_fryer` draws a single
basket, two baskets side by side, a basket with a window, or an oven-style rotisserie fryer.
`blender` draws a jug on its motor base, a personal blender with its cup, or a stick hand
blender. A compact air fryer is a small square box with a knob over one drawer. All three are upright (`orientation.UPRIGHT`).

**Decoys.** Each type carries two text-match decoys (ruling 2026-10-14, gen#309): a word naming
something the product is not in a title (`… for Whole Coffee Beans`, `… with Recipe Cookbook
Booklet`, `… with a Travel Bottle Lid`), and another type's name in a feature (`… with a Teapot
Spout Carafe`, `… with a Toaster Oven Rack`, `… with a Mixer Paddle`). None is a range name: a
place range such as `Teapot Lane` already has its one brand (`place_ranges.py`). The structured
fields tell the truth.

**Measured** (ceiling build, seed 0, with slice 2): `Home` holds more than the slice's
24,000-SKU floor (`retail_figures.figures()` reads the total). Coffee Maker 971 SKUs in 225
styles, Air Fryer 1,738 in 186, Blender 762 in 170 (215, 178 and 160 of them derived); every
other style keeps its id, title and brand. Bedding and storage (slice 2: bed sheets, pillows, food storage
containers) merged first, in `bedding-storage-963.md`. Floor care and furniture (slice 3: vacuum
cleaners, desks, wall art) is the last slice of gen#963. The guards are in
`tests/test_retail_small_appliances_963.py`.

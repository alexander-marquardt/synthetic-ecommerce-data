# Small kitchen appliances, slice 1 (gen#963)

`Home > Small Appliances` held only kettles and toasters, both templates the scaled build never
derives, so a search for `air fryer`, `coffee maker` or `blender` found nothing. Slice 1 adds
three derivable types, each a spec of its own:

| Type | Spec | Path | Templates | Type values (drawn) | Second axis | SKU axis |
|---|---|---|---|---|---|---|
| Coffee Maker | `type_specs/coffee_maker.py` | Home > Small Appliances > Coffee Makers | 13, one per brand, and 2 decoys | Drip, Espresso, Pod, Bean to Cup, Cold Brew | design (Classic, Retro, Compact, Digital, Slimline) | the six main colors |
| Air Fryer | `type_specs/air_fryer.py` | Home > Small Appliances > Air Fryers | 13 and 2 decoys | Single Basket, Dual Basket, Viewing Window, Rotisserie | controls (Digital, Dial, Smart, Touchscreen) | the six main colors times two capacities in litres (`capacity_l`), each at its price |
| Blender | `type_specs/blender.py` | Home > Small Appliances > Blenders | 13 and 2 decoys | Jug, Personal, Hand | design | the six main colors |

The shared pieces (the path, the brands, the six colors, `litres()`, `row()`, `table()` and
`decoy()`) are in `kitchen_appliance_rows.py`. `table()` makes one template per brand and cycles
the type value and the second axis through the brands, so every value is on a template. The
brands are invented (ruling 2026-10-30, gen#720): the six Home brands the kettles and toasters
already carry and seven large-appliance brands, each with an owner, a mark and a house style
already. The scaled build makes one style per brand and title, so these thirteen brands bound
each type's depth. Each style is sold in red, blue, green, yellow, black and white (ruling
2026-10-13, gen#275), its first color the hero the image shows.

**Drawings.** `kit_kitchen_appliances.py` draws three shapes, each taking `kind`, the lower-cased
type value, so a derived style that swaps the value is drawn true (gen#512). `coffee_maker` draws
a drip machine with its carafe, an espresso machine with a portafilter and steam wand, a pod
machine, a bean-to-cup machine with its hopper, or a cold-brew tower. `air_fryer` draws a single
basket, two baskets side by side, a basket with a window, or an oven-style rotisserie fryer.
`blender` draws a jug on its motor base, a personal blender with its cup, or a stick hand
blender. All three are upright (`orientation.UPRIGHT`).

**Decoys.** Each type carries two text-match decoys (ruling 2026-10-14, gen#309): a word naming
something the product is not in a title (`… for Whole Coffee Beans`, `… with Recipe Cookbook
Booklet`, `… with a Travel Bottle Lid`), and another type's name in a range name (`Teapot Lane`
coffee maker, `Toaster Hill` air fryer, `Mixer Hill` blender). The structured fields tell the
truth.

**Measured** (ceiling build, seed 0): `Home` holds 18,404 SKUs, from 14,059 on main. Coffee
Maker 1,454 SKUs in 324 styles, Air Fryer 1,986 in 210, Blender 905 in 196 (309, 195 and 181 of
them derived). Bedding and storage (slice 2: bed sheets, pillows, food storage containers) and
floor care and furniture (slice 3: vacuum cleaners, desks, wall art) are later slices of gen#963,
which together reach its 23,750 floor. The guards are in
`tests/test_retail_small_appliances_963.py`.

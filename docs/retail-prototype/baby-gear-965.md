# Baby gear, slice 1 (gen#965)

Kids > Baby sold clothing only, so a search for `diapers`, `baby wipes` or a `glass baby bottle`
found nothing. Slice 1 adds the first three gear types under it, each a spec of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Diapers | `type_specs/diapers.py` | Kids > Baby > Diapering > Diapers | Tape, Pull-Up | Size 1 to Size 6 (`diaper_size`) |
| Baby Wipes | `type_specs/baby_wipes.py` | Kids > Baby > Diapering > Baby Wipes | Flip Top, Resealable | Single, 3, 6 and 12 pack (`pack_size`) |
| Baby Bottle | `type_specs/baby_bottle.py` | Kids > Baby > Feeding > Baby Bottles | Plastic, Glass, Silicone | color x 150, 260, 330 ml (`capacity_ml`) |

The build record's `department` is `Home`, as for the nursery types and the baby beakers
(`babywear_rows.py`), which keys the brand pools; the store's department is the top of the path,
`Kids`. The shared pieces (the paths, the brands, the pack colors, `packs()`, `row()` and
`decoy()`) are in `baby_gear_rows.py`. The brands are the invented baby and nursery brands already
on the catalogue, each with a house style.

**Colors.** Diapers and wipes are `colorless`: a pack is not sold in colors, and its one pack
color is the fill the drawing takes. A bottle is sold in a color, and its six templates spread the
six main colors of gen#275 (red, blue, green, yellow, black, white).

**Sizes.** A bottle's capacity is its size axis (`size_axes.AXES`), so a 330 ml bottle is drawn
larger than a 150 ml one. A diaper size is a fit (`size_axes.NOT_SIZES`): the baby's weight band,
on a pack drawn the same. A wipes pack is a pack (`pack_size`), drawn by `pack_scale`.

**Drawings.** `kit_baby_gear.py` draws three shapes. `diaper_pack` takes `diaper_style` (tape,
pull-up), which draws one diaper in the pack's window: tabs on its sides, or a pull-up's elastic
waist. `wipes_pack` takes `lid` (flip top, resealable): a hinged hard lid, or an oval peel-back
flap with a pull tab. `baby_bottle` takes `material` (plastic, glass, silicone), which draws the
body tinted plastic, clear glass or a soft silicone bulge, with the bottle's color on the screw
collar. Each param is the lower-cased attribute value, so a derived style
that swaps the value is drawn true (gen#512). `orientation.py` lists the three shapes as upright.

**Titles.** The three kinds are in the soft family of the line grammar
(`line_grammar_families/soft.py`, beside the changing mat and the baby blanket), so a derived
style's title leads with its brand and a soft model word ("Snug", "Lull", "Cuddle"), never with an
invented range name that reads as a second brand (gen#664).

**Breadth.** The three types are derivable. A derived style's twin key is its leaf, brand and
title, so a type yields at most (title-shown value combinations x brands) styles per title
pattern. Each type's last two templates widen both the value pools (Extra Absorbent and
Hypoallergenic diapers, Coconut and Calendula wipes, Easy Grip and Fast Flow bottles) and the
brand pools, which takes the slice past its floor of 1,100 SKUs.

**Decoys.** Each type carries two text-match decoys: a class 2 or class 1 (a word for another
category or color, such as `changing bag` or a pink teat cover on a blue bottle) and a class 6
(a word in a range name, such as `Swim Club` diapers that are not swim diapers, or `Red Fox`
bottles that are white).

**Measured** (ceiling build, seed 0): the slice's size, its styles per type and the authored and
derived split are read from the build (`retail_figures`), never typed here. High chairs,
strollers, car seats, nursery furniture and baby monitors are later slices of gen#965. The guards
are in `tests/test_retail_baby_gear_965.py`.

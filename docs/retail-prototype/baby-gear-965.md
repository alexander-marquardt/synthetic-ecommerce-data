# Baby gear, slices 1 and 2 (gen#965)

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
derived split are read from the build (`retail_figures`), never typed here. Strollers, car seats
and high chairs are slice 2 (below); nursery furniture and baby monitors are a later slice of
gen#965. The guards are in `tests/test_retail_baby_gear_965.py`.

## Slice 2: strollers, car seats and high chairs

A search for `stroller`, `car seat` or `high chair` found nothing either. Slice 2 adds the three
under two nodes: `Travel` (new) and `Feeding` (beside the bottles).

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Stroller | `type_specs/stroller.py` | Kids > Baby > Travel > Strollers | Compact, Full-Size, Jogging (`stroller_style`) | color |
| Car Seat | `type_specs/car_seat.py` | Kids > Baby > Travel > Car Seats | Infant Carrier, Convertible, High-Back Booster (`seat_type`) | color |
| High Chair | `type_specs/high_chair.py` | Kids > Baby > Feeding > High Chairs | Wooden, Folding, Pedestal (`frame`) | color |

**Colors.** Each is sold in colors and in no size: one SKU per color (`baby_gear_rows.gear_row`).
The fabric of a stroller and a car seat, and the tray and seat pad of a high chair, take the
SKU's color. The templates' colors spread the six main colors of gen#275.

**Drawings.** `kit_baby_gear.py` draws three more shapes, each a param per template above, the
lower-cased attribute value, so a derived style that swaps it is drawn true (gen#512). `stroller`
is drawn from the side: a deep seat under a big hood on four wheels (full-size), a slim frame with
a small hood and twin wheels (compact), or a three-wheeler on large air tyres (jogging). `car_seat`
draws a rear-facing carrier with a carry handle, a harnessed seat on a base (convertible), or a
booster with a high back, side wings and armrests. `high_chair` stands on four splayed wooden
legs, a folding X-frame on wheels, or one pedestal on a round foot. `orientation.py` lists the three as upright.

**Titles.** The three kinds are a family of their own in the line grammar,
`line_grammar_families/baby_gear.py`: the soft family's lead words are all dealt to its brands, so
a thirteenth brand there breaks its assert, and a stroller named "Doze" reads as bedding. Its lead
words are plain English words of going out ("Saunter", "Rover", "Voyager"), so a title reads
"Emberly Home Saunter Side Impact Convertible Car Seat". A description uses no word that is the
lead of any family: a lead word in a description of another kind is read as that family's model.

**Decoys.** Each type carries two: a class 2 (a word for another category: a stroller that takes
a `car seat` on adapters, a car seat that is `stroller` compatible, a high chair with a `baby
bottle` holder) and a class 1 or 6 (a red-padded car seat that is not red; a `Green Meadow`
stroller that is black, a `Yellow Finch` high chair that is not yellow).

**Breadth.** The three are derivable, as in slice 1, and take the slice past its floor of 1,100
SKUs at the ceiling build.

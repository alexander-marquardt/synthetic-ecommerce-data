# Steam irons, vacuum cleaners and microwaves (#1116)

The catalog sold no clothes iron, vacuum or microwave, so each of these words met only another
meaning. `steam iron` and `iron` met iron minerals, cast iron pans, kettlebells and golf irons.
`vacuum cleaner` met liquid floor cleaner, and `vacuum` met nothing. `microwave` met ready meals
and porridge that say "microwave" on the pack. This slice adds three types under
`Home > Small Appliances`, each in a leaf of its own, beside the kettles, toasters and air fryers
(gen#963). That is where UK retailers shelve a worktop microwave:

| Type (leaf) | Kinds (type key) | Design key | Spec | Drawing |
|---|---|---|---|---|
| Steam Iron (`Irons`) | Standard, Cordless, Steam Generator, Travel (`iron_type`) | `soleplate` | `type_specs/steam_iron.py` | `kit_household_appliances.steam_iron` (`kind`) |
| Vacuum Cleaner (`Vacuum Cleaners`) | Upright, Cylinder, Cordless Stick, Handheld, Robot (`vacuum_type`) | `design` | `type_specs/vacuum_cleaner.py` | `kit_household_appliances.vacuum_cleaner` (`kind`) |
| Microwave (`Microwaves`) | Solo, Grill, Combination (`microwave_type`) | `design` | `type_specs/microwave.py` | `kit_household_appliances.microwave` (`kind`) |

The rows come from `kitchen_appliance_rows.table`, like the gen#963 types. There is one style per
brand, kind or design (six of each type), and each style is sold in the six main colors. A
microwave is also sold by its capacity in litres (`capacity_l`, a declared size axis). The brands
are the four Home brands of the small kitchen appliances, so no deal moves elsewhere. The three
types join the kitchen family of the line grammar. They are not derivable: the scaled build
copies them as authored and draws no more, so no other department's share or golden moves. The
drawing follows the `kind` param, the lower-cased type value. A steam generator iron stands on
its water tank, a cordless one on its charging base. A robot vacuum is seen from above. A grill
microwave shows its element, and a combination one shows its fan ring as well.

Each type has one category decoy. Its title names a product the record is not: an iron "for
ironing boards", an upright that needs "no vacuum bags", a microwave with a "rice cooking
setting".

The queries, on the no-policy baseline ranker (`tests/test_retail_clash_appliances_1116.py`):
`steam iron` finds only steam irons in its top five. `vacuum cleaner`, `cordless vacuum` and
`microwave` each find their own type in their top five. `combination microwave` finds the
combination microwaves before the combination locks. The bare `iron` meets steam irons and the
metal-iron products together in its top ten: a category policy, not the data, picks the intent.

Two slices of the issue are left. Slice 2 is the cooker hood, the deeper laundry and freezer
kinds, and `washer` in the laundry titles. Slice 3 is the department at 1,700+ SKUs and the
ten-query table without and with a policy.

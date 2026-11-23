# Cooking appliances, slice 1 (#1116)

`Home > Large Appliances` held fridges, dishwashers and laundry only, so the catalog sold no
cooker, oven or hob. The query `range` met baby monitors, water guns and jeans ("range" as a
signal range or a product line), and `range cooker 90cm` met no cooker at all. Slice 1 adds three
types, each in a leaf of its own, six models of every kind, one model a brand of the six:

| Type (leaf) | Kinds (`appliance_type`) | Spec | Drawing |
|---|---|---|---|
| Range Cooker (`Range Cookers`) | Range Cooker (Dual Fuel), Range Cooker (Induction) | `type_specs/range_cooker.py` | `kit_cooking.range_cooker` (`kind`, `width`, `ovens`) |
| Built-in Oven (`Built-in Ovens`) | Single Oven, Double Oven | `type_specs/built_in_oven.py` | `kit_cooking.built_in_oven` (`kind`) |
| Hob (`Hobs`) | Induction Hob, Ceramic Hob, Gas Hob | `type_specs/hob.py` | `kit_cooking.hob` (`kind`, `width`, `zones`), seen from above |

A range cooker is 90, 100 or 110 cm wide (six of the twelve at 90 cm) with two or three ovens;
its fuel, width, oven count and energy rating are structured. An oven states its capacity in
litres (a double oven's is both cavities together) and its 60 cm width. A hob states its width
(60 to 90 cm) and its cooking zones. The drawing reads the same values: a 110 cm range is drawn
wider than a 90 cm one, a three-oven range has three doors, a hob's zones are as many as it has.

Model numbers follow gen#622 (`appliance_model_numbers.py`, see
[machine-model-numbers-622.md](machine-model-numbers-622.md)). The new kind letters are `G`
(dual fuel range), `N` (induction range), `O` (single oven), `E` (double oven), `X`, `Y`, `Z`
(induction, ceramic, gas hob). A range or a hob takes the new digit group `width`: three digits of
cm (`090`), and its title states `90cm` between the model number and the kind; an oven takes the
`litres` group like a fridge. `large_appliance_rows.identify` reads `item_width` only when no
load, capacity or place-settings entry holds, so a dishwasher's number is unchanged.

Colors (`type_colors.py`): a range comes in white, black, silver, red, blue or green, an oven or a
hob in white, black or silver, so the main-color completion (gen#275) adds no yellow range and no
red oven. Each type has one class-1 color decoy: a black range with red enamel knobs (`RCR001`), a
stainless oven with a black glass door (`OVK001`) and a stainless gas hob with black pan supports
(`HBK001`).

The queries, on the no-policy baseline ranker (`tests/test_retail_cooking_1116.py`):
`range cooker 90cm` finds only 90 cm range cookers in its top five; `induction hob`, `gas hob`,
`double oven`, `built-in single oven` and `dual fuel range cooker` each find their own type
first. The bare `range` meets range cookers and the signal-range products both in its top ten: a
category policy, not the data, picks the intent.

Slices 2 and 3 of the issue are still to come: steam irons, vacuum cleaners and microwaves; then
the cooker hood, the deeper laundry and freezer kinds and the department's SKU count.

# Large appliances (gen#334)

Home > Large Appliances holds 102 products in three leaves, each type at least six models and a
color or finish a SKU: Fridges & Freezers (fridge freezers 70/30 and 50/50, American style,
under-counter, larder, chest, upright and integrated), Dishwashers (full size, slimline,
integrated, table-top) and Laundry (washing machines, condenser, heat pump and vented tumble
dryers, washer dryers). Three specs (`type_specs/fridge_freezer.py`, `dishwasher.py`,
`laundry_appliance.py`) read `large_appliance_rows.py`; `kit_large_appliances.py` draws them.
Capacity, `item_width`, energy rating, place settings, noise and load are structured entries.
Dishwashers and laundry are white, black or silver (`type_colors.py`); the retro 50/50 fridges
carry the six main colors.

The word decoys of the dishwasher, the washing machine and the fridge are in
`feature_decoys/large_appliances.py` and listed in
[retail-product-word-decoys.md](../retail-product-word-decoys.md): "dishwasher" meets tablets, salt
and rinse aid, "washing machine" its cleaner, descaler and pods, and "fridge" storage boxes, a
lunch cooler and cheese crisps. The mugs, lunch boxes and cutlery whose descriptions say
"dishwasher safe" were already in the catalog and stay reachable through text. Three more words
need a product type the catalog lacked, so each is a spec with one ordinary product and its decoy
(`type_specs/fridge_magnets.py`, `fridge_thermometer.py`, `anti_vibration_mat.py`; ids `DT32` to
`DT34`, the `category` policy). The color decoys are a "Black Edition" fridge freezer that is
stainless steel and a washing machine with a "Red Spot" dial that is white.
`tests/test_retail_large_appliances_334.py` holds the depth and the decoys.

Series and model numbers (gen#622). A series belongs to exactly one brand across every kind
(`appliance_model_numbers.SERIES`: five a brand, thirty in all), and the document's
`product_line` is the series (`Row.product_line`), which export reads as the top-level `series`
field (an attribute keyed `series` would shadow it, which the output standard refuses). A large
appliance's title reads brand, series, model number, spec, then the kind: "Frostholm Arden
FW712BW 7kg 1200 Spin Washing Machine". The model number is built by the brand's own scheme
(its lead letters, a kind letter moved along the alphabet, a separator, and the generation before
or after the digits) from the kind, the capacity, the spin speed, the generation and the color, so
`FW` + `7` + `12` + `D` + `W` is `FW712DW`; `decode` reads it back. Each SKU states
the code of its own color as its `model_number` option, so a query for `FW712BB` finds the black
one; the product-level code (the title's) is the first color's, and the `base_model` attribute is
the same code without its color letter, which names the product in every color. Model number, generation, capacity
and spin speed are each their own attribute. Two washing machines carry the second title form,
"Washing Machine from Tavorne, Model TVD-914CW". The generation letters are B to F, never "A"
or "I" (a word-like value is contradicted by any description that opens "A ..."); the decoys
carry generation "H", which no authored model takes.
`tests/test_retail_appliance_model_numbers_622.py` holds it.

The beach towels (`type_specs/beach_towel.py`, gen#624) are twelve authored rows that replace the one
derived "Cotton Velour Beach Towel": material, weave, feature and size vary, and the titles are 7
to 12 words so the beach towel decoys compete. Design and the measured top 12 are in
[retail-beach-towels.md](../retail-beach-towels.md); `tests/test_retail_beach_towels_624.py` holds them.

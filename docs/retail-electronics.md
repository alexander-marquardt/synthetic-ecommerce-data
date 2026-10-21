# Electronics: phones, computers, tablets and their accessories (gen#332)

The department has 15 product types in `prototypes/retail_drawings/type_specs/` (one spec each) and
154 template styles: 66 devices (smartphones, basic phones, laptops, desktops, tablets, e-readers)
and 88 accessories (phone cases, screen protectors, chargers, cables, earbuds, laptop sleeves,
mice, keyboards, monitors). The rows are in `electronics_rows.py`; the drawings are in
`kit_electronics.py` (a house-style drawing per type). Prices, specs and stock are synthetic.

## Tree

`Electronics > Phones > {Smartphones, Basic Phones}`, `Computers > {Laptops, Desktops}`,
`Tablets > {Tablets, E-readers}` and `Accessories > <leaf>`. Each type nests under its generic node
and no sibling label is a word-suffix of another (`tree_guard`).

## Real names (Apple, iPhone, iPad only)

The maintainer's two rulings (2026-10-15) are quoted in the README. Apple devices are iPhone and
iPad models with their public line names (`iPhone 15`, `iPad Air`); the Apple house style has the
mark `none`, so no drawing carries a logo or a trade dress. Every other brand is invented: 13 in
`electronics_brand_styles.py`, each with its own mark. `real_brands.ALLOWED` is Nike, Apple, iPhone
and iPad; `KNOWN_REAL` refuses the other phone, computer and accessory makers. The web check of the
13 invented names could not be run from the build host (the search returned unrelated pages), so it
is still to do by hand before the names are relied on.

## Decoys

- A case, screen protector or charger names the phone it fits ("Case for iPhone 15"): the
  model-word decoy. A query for `iphone 15` meets more accessories than phones.
- In-department decoys (gen#294, `electronics_rows.DECOY_ROWS`): class 1, the Blue Glow Keyboard
  (white, "blue" in a range name); class 5, a case whose text names red ("Trim Edge Case for
  iPhone 14"); class 4, the bare model-line query "iphone 15" (Pocket Wallet Case for iPhone 15);
  class 7, a charger that names Apple only as the brand it fits ("Compatible USB-C Wall Charger").
- Class 8 (gen#326), `feature_decoys/electronics.py`, rows DY700 to DY718, each with
  `device_type` (the Electronics type whose word the title holds): `mouse` (a trap, a cushion and a
  throw), `tablet` (dishwasher tablets, Scottish tablet), `monitor` (baby monitors, a lizard
  cushion), `mobile` (cot mobiles, a mobile coat stand), `charger` (battery chargers, the charger
  plate) and `apple` (the fruit, its juice, a candle and the tree). The table is in
  [retail-product-word-decoys.md](retail-product-word-decoys.md).

## Release

Ships with the next retail catalogue re-release (the batch rule), not as its own ingest.

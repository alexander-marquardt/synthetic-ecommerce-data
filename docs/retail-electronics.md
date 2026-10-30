# Electronics: phones, computers, tablets, TVs and their accessories (gen#332, #721, #724)

The department has 16 product types in `src/synthetic_ecommerce_data/domains/retail/type_specs/` (one spec each) and
210 template styles: 97 devices (smartphones, basic phones, laptops, desktops, tablets, e-readers,
TVs) and 113 accessories (phone cases, screen protectors, chargers, cables, earbuds, laptop sleeves,
mice, keyboards, monitors). The rows are in `electronics_rows.py`; the drawings are in
`kit_electronics.py` (a house-style drawing per type). Prices, specs and stock are synthetic.

## Tree

`Electronics > Phones > {Smartphones, Basic Phones}`, `Computers > {Laptops, Desktops}`,
`Tablets > {Tablets, E-readers}`, `TVs` and `Accessories > <leaf>`. Each type nests under its generic node
and no sibling label is a word-suffix of another (`tree_guard`).

## Every brand is invented (gen#720)

The maintainer's ruling (2026-10-30) replaces the two of 2026-10-15 that let Apple, iPhone and iPad
in as real names: "there are some proprietary brands in the synthetic data which we should remove ..
iphone which is now GrapePhone", and "Can we create a synthetic computer called "grape computer" ..
and also create products called GrapePhone". A public catalogue and a commercial demo should not sell
invented products under a real company's name at invented prices.

`Grape Computer` sells the ten devices that were Apple's, with the same type, price, colors and
specs: `GrapePhone 15`, `GrapePhone SE` and the rest, and `GrapePad`, `GrapePad Air`, `GrapePad Pro`
and `GrapePad mini`. They run `Grape OS`. `GrapePad` is ours: the maintainer named only GrapePhone.

Every brand of the department is invented: 17 in `electronics_brand_styles.py`, each with its own
mark. Grape Computer's is `vine`, a sprig that is not the `grapes` mark of Stonepine Estate, and its
drawings carry its name as any invented brand's do. `real_brands.ALLOWED` is empty (Nike left with gen#722). `KNOWN_REAL`
refuses iPhone, iPad and the other phone, computer and accessory makers in the brand, title and
description. `BRAND_ONLY` refuses Apple in the `brand` field alone, because `apple` is a fruit word
from here on.

The clash the old ruling wanted survives: `grape` meets the brand and the fruit (its juices and
sweets). `GrapePhone` is one word to a search, so `grape` finds the devices by their `brand` field.

The web check of 2026-10-30 searched each exact name and found no company or product called
Grape Computer, GrapePhone, GrapePad or Grape OS. Near names exist: Grape Systems Inc. and Grape Lab
Inc. hold computing and accessory trademarks, Grapes Mobile sold phones in India, and GrandPad is a
tablet. The check of the other 15 invented names could not be run from the build host (the search
returned unrelated pages), so it is still to do by hand before those names are relied on.

The brands that cross departments (Grape Computer, GoodLook, SingingSam, PackingHarder and Xell)
are in [retail-prototype/cross-category-brands-721.md](retail-prototype/cross-category-brands-721.md).

## A maker's own accessories beside compatible ones (#724)

The maintainer, 2026-10-30: "SingingSam compatible phone case from FlyingFoo .. or whatever .. same
for the grapephone .. some grapephone branded accesories, but also compatible versions .. just like
we see for iphone , or for samsung". The redirect demo does not stop at the phone: the accessory query
that follows it lands on the maker's own rows and on compatible rows from other brands.

| Brand | Own accessories | Third-party accessories that name it |
|---|---|---|
| `Grape Computer` | 5 cases (3 GrapePhone, 2 GrapePad), 2 keyboards (GrapePhone 16, GrapePad Pro) | the rows #720 renamed, and a case and a protector from Cindrel or FlyingFoo for the GrapePhone 16, which had none |
| `SingingSam` | 3 cases (Aria 9, Aria 5), a keyboard (Aria 9) | 5 cases and 4 protectors from FlyingFoo, Boltwick, Cindrel and Wexmoor |

- An own-brand title opens with the brand (`Grape Computer Clear Case for GrapePhone 16`), and a
  keyboard that names a device carries `compatible_with` as a case does. The other keyboards fit no
  one device and stay as they were.
- `FlyingFoo` is the maintainer's example of a third-party brand. It sells cases and screen
  protectors only, with its own mark, `wing`. Two web searches of 2026-10-30 on the exact name found
  no such brand or trademark; near names are Flywoo (drone parts) and Flykangaroo.
- A GrapePad case is in `Phone Cases`, with no new leaf, as a GrapePad protector is in `Screen
  Protectors`.
- `tests/test_own_brand_accessories_724.py` holds the rows.

## Decoys

- A case, screen protector or charger names the phone it fits ("Case for GrapePhone 15"): the
  model-word decoy. A query for `grapephone 15` meets more accessories than phones.
- In-department decoys (gen#294, `electronics_rows.DECOY_ROWS`): class 1, the Blue Glow Keyboard
  (white, "blue" in a range name); class 5, a case whose text names red ("Trim Edge Case for
  GrapePhone 14"); class 4, the bare model-line query "grapephone 15" (Pocket Wallet Case for
  GrapePhone 15); class 7, a charger that names Grape Computer only as the brand it fits ("Compatible
  USB-C Wall Charger").
- Class 8 (gen#326), `feature_decoys/electronics.py`, 15 rows (DY701 to DY705, DY708, DY711, DY714, DY719 to DY725), each with
  `device_type` (the Electronics type whose word the title holds): `mouse` (a cushion, a
  throw and a basket), `tablet` (dishwasher tablets, Scottish tablet), `monitor` (a lizard cushion,
  throw and basket), `mobile` (a coat stand, a clothes rack and a basket on wheels) and `charger` (three
  charger plates). The table is in
  [retail-product-word-decoys.md](retail-product-word-decoys.md).
- The apple juice, the Apple Blossom Candle and the crab apple tree (DY716 to DY718,
  `feature_decoys.electronics.FRUIT_ROWS`) were class 8 decoys against the brand. They are ordinary
  products now and left the table.

## Release

Ships with the next retail catalogue re-release (the batch rule), not as its own ingest.

# Electronics: phones, computers, tablets, TVs and their accessories (gen#332, #721, #724)

The department has 17 product types in `src/synthetic_ecommerce_data/domains/retail/type_specs/` (one spec each,
besides the breadth leaf Batteries) and 212 template styles (before gen#1117's phone range, below): 96 devices (smartphones, basic phones, laptops,
desktops, tablets, e-readers, TVs) and 116 accessories (phone cases, screen protectors, chargers, cables, earbuds,
laptop sleeves, mice, keyboards, monitors, memory cards). The rows are in `electronics_rows.py`; the drawings are in
`kit_electronics.py` (a house-style drawing per type). Prices, specs and stock are synthetic.

## Tree

`Electronics > Phones > {Smartphones, Basic Phones}`, `Computers > {Laptops, Desktops}`,
`Tablets > {Tablets, E-readers}`, `TVs`, `Audio > {Headphones, Portable Speakers, Soundbars}`
(gen#956, see [retail-prototype/electronics-audio-956.md](retail-prototype/electronics-audio-956.md)),
`Smart Home > {Smart Plugs, Smart Bulbs, Doorbell Cameras}`
(gen#956, see [retail-prototype/electronics-smart-home-956.md](retail-prototype/electronics-smart-home-956.md)),
`Gaming > {Game Controllers, Gaming Headsets}`
(gen#956, see [retail-prototype/electronics-gaming-956.md](retail-prototype/electronics-gaming-956.md)),
`Gaming > {Video Games, Consoles}`
(gen#1120, see [retail-prototype/video-games-1120.md](retail-prototype/video-games-1120.md)),
`Accessories > Power Banks`, `Computers > Webcams`, `Wearables > Smartwatches` (gen#956's gadgets, see
[retail-prototype/electronics-gadgets-956.md](retail-prototype/electronics-gadgets-956.md)),
`Printers > {Printers, Ink Cartridges}` (gen#956, see
[retail-prototype/electronics-printers-956.md](retail-prototype/electronics-printers-956.md))
and `Accessories > <leaf>`. Each type nests under its generic node
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

## The phone range (gen#1117)

The range was thin (265 smartphone SKUs, 89 cases, 21 screen protectors), so `phone_range_rows.py`
adds 24 invented handsets and the accessories for every model; the gen#332 rows stay as they were.

- A new smartphone (`BRD-EPR001` to `BRD-EPR024`) is sold by storage, color and `network_lock`
  (`Unlocked` or `Carrier-locked`, the third SKU axis; a locked one costs 10% less). Its screen
  size is an attribute.
- Every smartphone, old or new, has a clear, a rugged and a wallet case (`BRD-ECR...`) and a
  clear, a matte and a privacy screen protector (`BRD-ESR...`). A row is added only where that
  model has none of that style.
- `compatible_with` is the phone's `model_line`, our own model id, so a filter on it joins the
  phone to its accessories, and the title ends `for <model line>`.
- Each new phone has its own charger (`BRD-ECG...`: wall, wireless or car in turn). Six more
  cables (`BRD-ECL...`) carry no model. Automotive's phone mounts gain a magnetic wireless
  charging mount and a long-arm windshield mount, from each of their three brands.

The range adds 1,204 SKUs over the issue's count: Smartphone 265 to 653, Phone Case 89 to 637,
Screen Protector 21 to 167, Charger 35 to 91, Cable 88 to 142 and Phone Mount 52 to 64.

Search demo: `"case for Halvern Arc 6"`. The words also match the cases of the Halvern Arc 6 Pro,
the near-miss family: only the three whose `compatible_with` is `Halvern Arc 6` are right, and a
filter on `compatible_with` (or a policy that reads the model from the query) leaves them.
`tests/test_phone_range_1117.py` holds the counts, the per-model accessories and the demo.

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
- Memory cards (gen#796), `Accessories > Memory Cards`: microSD and SD cards sold by capacity
  (`storage_gb`), with `card_format` and `speed_class`. Their class 8 decoys are in
  `feature_decoys/memory_card_796.py` (DY7960, DY7961, `device_type` `Memory Card`): a memory card
  storage wallet (a Travel Case, dropped by the department policy) and a laptop sleeve with a card
  pocket (in Electronics, dropped by the category policy). See
  [memory-card-796.md](retail-product-word-decoys/memory-card-796.md).
- The apple juice, the Apple Blossom Candle and the crab apple tree (DY716 to DY718,
  `feature_decoys.electronics.FRUIT_ROWS`) were class 8 decoys against the brand. They are ordinary
  products now and left the table.

## Release

Ships with the next re-release of the retail products (the batch rule), not as its own ingest.

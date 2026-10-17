# Retail toys depth: kites, play kitchens, dolls' houses, card games, marble runs, water guns (gen#424)

The Toys department held a few of each of these under other leaves and drew none as its own
shape. Six type specs under `prototypes/retail_drawings/type_specs/` add them; `kit_toys_play.py`
draws them and `toys_play_common.py` holds the shared helpers. None is derived: authored rows only.

| Type | Path | Style axis | SKU axis | Key attributes |
|---|---|---|---|---|
| Kite | Toys > Outdoor Toys > Kites | diamond, delta, parafoil, stunt | color (eight) | span (cm), age range |
| Play Kitchen | Toys > Pretend Play > Play Kitchens | sink, oven door | color (eight) | height (cm), material, sink, oven door, lights and sounds |
| Dolls' House | Toys > Dolls & Accessories > Dolls' Houses | wood or plastic, rooms, floors | style (four finishes) | rooms, floors, furniture included, material |
| Card Game | Toys > Games > Card Games | family, party, strategy | edition (standard, travel, deluxe) | minimum and maximum players, play time (minutes) |
| Marble Run | Toys > Building & Construction > Marble Runs | wood or plastic, tiers | piece count | material, age range |
| Water Gun | Toys > Outdoor Toys > Water Toys | pistol, blaster, backpack | color (eight) | tank capacity (ml), range (m) |

The six together build 150 or more SKUs. A kite, a play kitchen and a water gun offer the six
main colors (gen#275); the other three have no color selector. No drawing prints a number: a
style's sizes share one image.

## Cross-department decoys (class 8 of gen#326)

A shopper's "toy kitchen", "card game" and "water gun" also match ordinary products of other
departments. Each is the `decoys=` of the spec of its own type (`type_specs/kitchen_roll.py` and
its five neighbours, codes `DT01` to `DT07`, class 8 of gen#326, made by
`word_decoy_types.word_decoy`; drawn by `kit_toy_word_decoys.py`, and a kitchen roll reuses the
wrapping paper shape):

| Query word | Decoy | Department |
|---|---|---|
| kitchen | Kitchen Roll, Digital Kitchen Scales | Home |
| card | Birthday Greeting Card, Plastic Gift Card | Gifts |
| gun | Hot Glue Gun, Caulking Gun | Home |

The department policy of the All Departments persona drops them. The checks are
`tests/test_retail_toys_depth_424.py`.

## Text-match decoys of the toy types (classes 4, 6 and 7 of gen#294)

The standing rule of gen#294 and gen#311 is that every type carries text-match decoys, the subtle
incidental-word ones included. Each toy spec declares four in its own `decoys=`, made by
`toys_play_common.toy_decoy` (a clone of one of its styles, in one color, coded `DT08` to
`DT31`; the table of codes, classes and queries is `DECOY_PINS` in the test file):

| Class | What the title holds | Example (kite) | Policy |
|---|---|---|---|
| 6, a color word | a range name with a color the product lacks | Red Tarn Kite, sold in blue (query "red kite") | generic |
| 6, a toy word | another toy's word as a range name | Card Game Ridge Kite (query "card game") | generic |
| 4, absent | a material or look the product does not have | Silk-Look Kite, ripstop nylon (query "silk kite") | special: material claim |
| 7, brand | another toy's word in an invented brand | Marble Run Co Stunt Kite (query "marble run") | generic |

All of them stay in the Toys department and in their own leaf, so the department policy keeps
them and the type policy has them to repair. Classes 1, 2, 3 and 5 (a trim names a color, a
garment noun as a modifier, an audience cut of a sibling, a shade written in the description
only) are the garment classes of gen#311 and are not authored for the toys. The test file
holds each decoy by code, class and query, and ranks each for its query.

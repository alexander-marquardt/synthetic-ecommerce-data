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
departments. `decoy_product_words.py` plants them (codes `DT01` to `DT06`, drawn by
`kit_toy_word_decoys.py`; a kitchen roll reuses the wrapping paper shape):

| Query word | Decoy | Department |
|---|---|---|
| kitchen | Kitchen Roll, Digital Kitchen Scales | Home |
| card | Birthday Greeting Card, Plastic Gift Card | Gifts |
| gun | Hot Glue Gun, Caulking Gun | Home |

The department policy of the All Departments persona drops them. The checks are
`tests/test_retail_toys_depth_424.py` and `tests/test_retail_product_word_decoys_326.py`.

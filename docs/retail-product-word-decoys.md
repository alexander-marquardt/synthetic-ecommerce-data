# Retail class-8 decoys: the shopper's product noun on a different product (gen#326)

A class-8 decoy has a title that holds the product word of a demo query ("dress", "sofa",
"jumper", "tie") while the product is something else: Dress for Success shoes, a sofa cover,
jumper cables, bow tie pasta. The structured fields tell the truth (category path, product type,
color, drawing). A title names at most the misleading color ("Sofa Cushion, Blue Trim" is a
cream cushion piped in blue; "Dress for Success, Red Laces" are black shoes with red laces) and
the drawing renders that detail. The rows are generated from
`prototypes/retail_drawings/decoy_product_words.py` and pinned by
`tests/test_retail_product_word_decoys_326.py`. A new decoy set is one file,
`feature_decoys/<topic>.py`; `decoy_contract.violations` (run by `tests/test_feature_decoys_513.py`)
checks every row of it: the id is unique, the title carries a word of the query, a structured
field contradicts it, the policy exists, and the drawing renders.

The fixing policy is the one that reads the structured fields: `category` (the noun's own node,
for example Dresses, drops the row), `department` (a cross-department row sits in another root,
so the All Departments persona drops it), `color` (the brand rows in every color but blue).
Rows the English stemmer would match ("dressing" for dress, "coated" for coat) are not planted:
the prototype search folds a plural only, and no row that does not rank is counted. Blue Bull is a
class-7 color-word brand on footwear with its own house style.

Each new real type carries a floor of three ordinary products, listed in `FLOOR`.

**A care cream for jumpers (gen#309).** "cream jumper" also meets a product that says both words
and is neither: `PLT-DY494`, Jumper and Knitwear Softening Cream, a white tub in Cleaning > Laundry >
Fabric Softener, an existing type with products of its own. Its color is White, so the color policy
drops it for the shade Cream, the category policy (Jumpers) drops it, and the department policy
(Cleaning & Janitorial) drops it. `tests/test_retail_knitwear_care_cream_309.py` pins the row, its
fields and its place in the baseline top 10.

**Sports & Outdoors (gen#368).** Every Sports & Outdoors type carries at least two decoys: a product
of another department, an existing type of the catalog, whose title holds the shopper's word for the
sports product (a block-heel shoe for "yoga block", a lantern-sleeve blouse for "camping lantern", a
crystal tennis bracelet for "tennis racket"). A row names its sports type in `target`, holds no
color word in its title or description, and is fixed by the department policy (the `Sports & Outdoors`
department drops it). `tests/test_retail_sports_decoys_368.py` walks the live catalog's Sports &
Outdoors types, so a new type reds until it has two decoys or an entry in `SPORTS_EXEMPT` that names
its follow-up issue. `SPORTS_EXEMPT` has been empty since gen#375 gave the seven first-increment types
(tents, sleeping bags, camping chairs, yoga mats, dumbbells, kettlebells, foam rollers) their two
decoys each, in `feature_decoys/sports_first_increment.py` (a tent dress and a tent stitch cushion,
a sleeping cat cushion and a sleeping beauty doll, camping club and camping trip rows, yoga leggings
and a yoga candle, dumbbell and kettlebell prints, a foam hand wash and foam sole sandals), and a test
pins it empty. The prototype's plural strip reads
"tennis" as "tenni", so the noun of those two rows is `tenni`. The picnic blanket of gen#217 (Camping)
carries two rows of its own (`picnic`), beside the two decoys of `decor_rows.py`.

**Cups (gen#620).** A bare `cup` meets drinkware and the cup of a bra. The real cups carry realistic
titles of six to ten words (material, size, use) and a drawing of their own, so a short bra title
outscores them in the baseline: seven rows, `PLT-DY620` to `PLT-DY626`, are bras named for their cup
("Full Cup Bra", "Demi Cup Bra", "Moulded Cup Bra", "Quarter Cup Bra", "Soft Cup Bra", "Spacer Cup
Bra", "Cotton Full Cup Bra"), in `feature_decoys/cups_620.py`. Each sits under the Bras leaf its title
names (gen#165: bra styles are facets, so a Full Cup Bra is in Full Cup Bras), and the fields tell the
truth (a bra by department, path, product type and drawing); only the title holds `cup`. The category
policy of the cups (gen#125 class 15) drops them. Related: gen#520 and gen#508, the plural-cups bras.
`tests/test_retail_cups_620.py` holds the rule and the ranking.

**Cycling accessories (gen#625).** The chain lube, bike bottles, saddles and pedals of gen#625 are
true types of their own Cycling leaves, short-titled so that a bare `bicycle` or `bike` ranks them
above the bikes. Each also gets two print decoys of another department, `PLT-DY6251` to
`PLT-DY6258` in `feature_decoys/cycling_accessories.py`, the rule of gen#352's
`feature_decoys/cycling_wheeled.py`.

**Gifts (gen#425).** The five Gifts types of the mug, greeting card, notebook, money box and pamper
hamper issue carry two decoys each: a wall mug rack and a microwave mug cake for "mug", a card holder
case and card-making paper for "card", a notebook computer sleeve and tote for "notebook", a lockable
storage box and chocolate coins in a box for "money box", a laundry hamper and a wicker storage hamper
for "hamper". A row names its Gifts type in `gift_type`, holds no color word in its title or
description, and is fixed by the department policy (the paper row sits in Gifts, so the category
policy fixes it). `tests/test_retail_gifts_425.py` holds the census.

**Gift card (gen#437).** The gift card has a home since gen#424 (Gifts > Cards > Gift Cards), so it
carries two decoys of its own: a gift card holder case (Travel Cases) and gift card wrapping sheets
(Wrapping Paper, in Gifts, so the category policy fixes it). Both name `Gift Card` in `gift_type`,
hold "gift card" in the title, and a "gift card" search and a "greeting card" search each rank the
intended Gifts type first once the policy applies. `tests/test_retail_gift_card_decoys_437.py` holds
the checks. The memory card, the other "card" example of gen#425, needs a storage or memory-card type
of the Electronics department (gen#332), which this build lacks; gen#437 stays open for it, with the
card reader and the card-slot phone case as its incidental-word decoys.

**Seed phrases (gen#460).** The homepage seed queries are two or three words ("leather boots", "skinny
jeans", "tea dress") and the Best tier requires every term, so a decoy with the bare noun never meets
them. Thirty-four rows serve thirteen seeds of Womens, Mens and Kids clothing and shoes, at least
three products each, and every row holds every word of each phrase it serves in its title or text: a
slim belt cut for high rise jeans, a jersey jegging with the skinny jeans look, clip hangers for jeans,
a fashion doll in barrel trousers, a garment bag for a tea dress, a boot care kit, waxed laces,
a mesh bag for running shoes. A row names the phrases in `seeds` and keeps its true type, so the
department policy drops a Home or Toys row and the category policy a Womens one. A color word is the
product's own (a navy bag for navy dresses), never a stray one. The bare seed `boot` keeps its
class-8 rows. `tests/test_retail_seed_phrase_decoys_460.py` holds the census: two decoy products
in the first 12 for each seed with policies off, every query word required, the rank of the
prototype's baseline; the live number is read on the next loaded index.

**The table of every decoy** (query, noun, product id, title, true type and fixing policy) is
built, not committed: `uv run python scripts/build_derived.py --out build/derived` writes
`docs/retail-product-word-decoys-table.md` from `decoy_product_words.TABLE`, and CI uploads it in
the `derived` artifact. Every decoy PR pasted the whole table here, so any two conflicted (gen#513);
`scripts/check_no_registry_append.py` refuses a table line added to this page.

# The retail prototype: distractors, footwear, grocery, the output standard and the catalog at a size

This page holds the retail prototype's reference sections, moved out of
[README.md](../README.md) verbatim (#240) because the README was over the file-size cap
(`scripts/file_size_cap.txt`). The type batches add their listing line here, to
"The retail catalog at a size", not to the README.

## Planted distractors (retail prototype)

The retail prototype in `prototypes/retail_drawings/` plants ordinary products
that win a query's top results on text alone, so a demo can show what a policy
fixes. `distractors.py` holds the table; `distractors.check()` refuses a
distractor that cannot outrank the best intended product (BM25 over title plus
description). A class's *tail* is further products the query matches that need
not outrank. Every name is invented but Nike (text only, no logo; gen#341, [docs/retail-nike.md](retail-nike.md)).

Every product is drawn as its own kind: a bouquet as roses in a paper cone,
socks as socks, a bed as a bed. A generic shape (`box`, `box_wide`,
`round_produce`, `pouch`, `top`) is allowed only in the categories listed in
`HONEST_FOR` in `test_shape_honesty.py` (packaged food in a box, loose produce
as round produce). A style that uses one anywhere else fails that test, and the
failure names the row. A new kind gets its own shape in `kit_more.py`, whose
docstring lists every shape and its params.

A garment is drawn as the garment its leaf names (gen#447): `leaf_shapes.RULES` lists the leaves
(bomber, puffer, polo, long sleeve, shirt dress, cargo trousers, pyjama shorts, knee boots) with
the shape and parameters that draw them, `leaf_shapes.apply` sets them in `scale.templates()`
before the decoys clone their exemplars, and `test_shape_honesty.py` fails a template of a listed
leaf drawn another way. A "Checked" or "Striped" title carries a gingham or stripe swatch, and a
"Boxers" decoy never clones a brief exemplar. The parts a title names (a bra band, a blouse
collar, a bow, "with Blue Collar") are the next slice.

`tests/test_retail_drawing_honesty.py` holds the ceiling build to the same rule:
the toilet cleaners draw as an angled-neck bottle or a hanging rim block (two units
for a twin pack, shapes in `kit_cleaning.py`), a `tub` only holds a tub of something,
a mug or cup draws as a `mug`, and a label is the title's product noun. The label
pairs not yet fixed are `LABEL_DEBT` there: it may only shrink. A changed drawing is a
new image digest, so the retail image bundle is re-released after the merge.

A mattress topper is drawn thin, on a faint mattress outline (#581): its thickness is its stated
`depth` at 2.5 px per cm, the scale of the 25 cm mattress under it, so a 5 cm topper is a fifth
of its mattress and a 10 cm one is visibly thicker (`kit_home.py`, `test_mattress_topper.py`).
The mattress protector still draws its deep mattress, which suits a fitted cover.

| Class | Query → intended | Distractors that outrank without a policy | Fixed by |
|---|---|---|---|
| Print, flavour and scent words | *lemon* → fresh lemons | lemons-print dress, a lemon-colored tee, lemons-print duvet cover, lemon cake, lemon shower gel, lemon cleaners | department or persona boost |
| Fruit words as prints and colors | *oranges* → fresh oranges | orange graphic tee, a bright orange tee, oranges-print tea towels, orange graphic mug | department or persona boost |
| Complements and accessories | *jeans* → a pair of jeans | jeans belt, denim jacket, jeans hanger, a jeans & tee set | category intent; product-type demotion |
| Bedding types | *duvet* → a duvet | duvet covers, duvet sets (one a kids' dinosaurs print) | type-exact intent |
| Motif words on kids' clothes | *dinosaur* → a dinosaur toy | kids' dinosaur graphic tee and sweatshirt, kids' dinosaurs-print pyjamas | department boost: Toys |
| Complements and accessories | *boots* → a pair of boots | car boot organiser, boot polish & brush kit, welly boot socks | category intent: Boots; product-type demotion; department boost |
| Gift words on gift-packed products | *gift bag* → a gift bag (gift wrap) | 3 beauty bundles named "... Gift Bag", a wash bag, a make-up bag with a gift badge, a hospital bag kit, 2 gift sets "with Limited Edition ... Bag", a travel and a summer bag set; tail: 2 wallet gift sets, 2 hampers, 2 letterbox gifts, a plant "in Hessian Gift Bag", a "Gift Boxed" keyring | category boost: Gift Wrap |

The print distractors come from the print range (`prints.py`), whose titles
follow one naming rule: the motif's noun is singular iff one copy is drawn. A
placement graphic draws one (*Wrench Graphic Tee*); a scatter (3 to 6 copies
per repeat) or an all-over half-drop says the plural (*Wrenches Print Tee*,
*Oranges Print Tea Towels*). One field, the print's count, drives the drawing,
the title and the `motif_count` attribute; `motif` is always the singular lemma.
Every fruit and tool motif is sold in both numbers, and no category path is
more than 25% prints.

The real gift bag (one product, `GFT-KRAFT`, whose nine SKUs are three sizes
of three prints) says *bag* once and never *gift*: the word lives only in its
category. `corpus(duplicate_listing=True)`
(or `build_preview4.py --duplicate-listing --ndjson PATH`) publishes one
product id a second time under another category, which a search shows twice
unless it collapses on `product_id`.

### Footwear

`footwear_rows.py` holds fifty-five shoe styles (thirty-three women's, fourteen men's,
eight kids'), one document per style with its color x width x size SKUs
nested. A size is three fields, `size_uk`, `size_eu` and `size_us`, read from
one chart row of the audience, so they never disagree; half sizes exist only
where a shoe is cut in them, and a wide fit only in the sizes it names. A ring's UK
letter and US number are other kinds of value, so they sit under `ring_size_uk` and
`ring_size_us` (gen#249), never these keys. Each
color names its upper material, which both the `upper_material` facet and the
drawing read. The style lists each material once, in its own Title Case `upper_material`
entry (`Leather`, `Suede`, `Patent`; gen#472), never one joined string, and each SKU names its
own material in the same case. The key stays a shoe's own: it does not join the `fabric`
facet, whose marker reads `fabric` only (gen#187). `kit_footwear.py` draws the shoe from the side in twenty-five
kinds (court, kitten and block heels, ballet pumps, loafers, brogues,
trainers, running shoes, slippers, sandals, ankle, Chelsea, chukka, knee-high,
walking and safety boots, wellies, and since gen#216 plimsolls, clogs, wedges,
espadrilles, platform trainers, mules, jelly shoes and barefoot shoes), with the
material's texture and the closure. Each of the eight newer kinds has variant
axes that are drawing params read from the attribute they draw (`kit_footwear.AXES`:
a wedge's `heel` in mm, a platform trainer's `platform`, a clog's `strap` and
`body`, a mule's `heel` and `toe`, an espadrille's `heel`, a jelly shoe's `style`
and `glitter`, a barefoot shoe's `sole`), so two styles that differ on one draw
differently. The platform trainer's product type is `Platform Trainers` but its category
leaf is `Platform Shoes`, on purpose: beside `Trainers` the leaf breaks the head-noun rule,
and nested under `Trainers` it would make a leaf a parent. The boots row above is checked over the round 4 corpus plus
footwear (`footwear_rows.catalog()`). Footwear is not in the Elasticsearch
proof corpus.

### Grocery

`grocery.py` (data in `grocery_rows.py`, gen#154) builds Food & Drink styles
whose SKUs are flavor x pack size: `python3 prototypes/retail_drawings/grocery.py
--skus 10000 --out DIR` writes `nested.jsonl` and `flat.jsonl`, both in the output
standard. Its styles, SKUs and each family's share are `templates.grocery` and
`grocery_families` in `retail_figures.figures()` (below); it covers the food leaves, plus a
kitchen-cleaner leaf and a body-lotion leaf for the overlaps. Each SKU states
`contains` and `may_contain` over seven allergens (peanuts, tree nuts,
milk, gluten, soy, egg, fish), its `dietary` labels (Vegan, Vegetarian, Gluten Free,
Nut Free, Organic), `pack_size`, `units_per_pack` and its net weight or volume.

The 50K tier (gen#376): a build of more than the 10K target is the tier, `python3
prototypes/retail_drawings/grocery.py --skus 50000 --out DIR`. A title is a range name plus a
flavor, so the 10K build's range names ran out for a family at this size and it stopped short
of its budget. The tier adds range names (`grocery_rows.TIER_LINES`) and new invented brands per
family group (`grocery_rows.TIER_BRANDS`; each has an `OWNERS` entry and a `house_styles` row
with its own mark, in `grocery_brand_styles.py`), shares the target over every family (depth
families too, so the total is the target) and draws from a stream of its own, so
`grocery.build()` and any build of the target or fewer read none of it and no 10K style, id or
draw moves. The tier's styles, SKUs, brands and each family's share are `grocery_tier_50k` in
`retail_figures.figures()` (and in the derived `golden-retail/stats.json`);
`tests/test_grocery_50k_tier_376.py` holds them.

Food SKUs also carry a top-level `ingredients` list (5 to 20 invented items in label
order, never in conflict with `contains`, which names the allergens the list holds a source
of); the flat file carries each SKU's own list. A product's list is the base recipe all its flavors share, so it
may be shorter than 5. Fresh whole fruit and vegetables carry no list: the field is
optional. A pizza is chilled and always contains gluten (a Vegan Garden style and a
Four Cheese style are pinned), and a honey jar is drawn with a Honey label.

At product level, `contains` and `may_contain` are the union over the product's
variants and `dietary` the intersection. There is no `free_from` field: "free from
peanuts" is a query (exclude peanuts from `contains`, and from `may_contain` when
strict), not data.

The flat file exposes four food facts as facets, because a hard filter can only
target a facet: `facets.ingredients` (the SKU's label list), `facets.contains` (the
allergens its ingredients name), `facets.may_contain` (factory traces) and
`facets.dietary` (pack claims: Vegan, Vegetarian, Gluten Free, Nut Free, Organic),
each a keyword list (`facets.ingredient_base` is the normalised head of each: [docs/retail-catalog-batch-1.md](retail-catalog-batch-1.md)). `contains`, `may_contain` and `dietary` are warnings and claims,
not description, so they stay out of the flat `text`: a "peanut" query cannot match a
product only through an allergen warning
(`tests/test_grocery_ingredients_154.py`). Open Food Facts (ODbL) inspired only the shape: the category
tree, the allergen and label model, and rough distributions. Every name is
invented.

The planted cases are:

- chocolate that contains peanuts, chocolate that may contain them, and chocolate
  that does neither (the "free from peanuts" query);
- Nut Free chocolate and Vegan chocolate;
- lemon, orange and mint as a food and as a cleaner scent;
- honey and coconut as a food and as a body milk scent;
- "lemon" and "honey" as a scent in dozens of SKUs, not one: lemon-scented dish soap, glass,
  floor, bathroom and laundry cleaners, hand wash and shower gel, and honey-scented hand wash
  and shower gel. Each carries `scent` as its own attribute (never a flavor) beside its
  product type, on the leaf the hand-written rows use, so a policy routes on the pair. These
  "depth" families are drawn from their own stream, so no core style moves
  (`tests/test_grocery_scent_depth_154.py`). The hand-written breadth rows still key their
  scent as `fragrance`, not `scent`;
- milk as dairy milk, milk chocolate and a body milk;
- the failure class "oranges" (`tests/test_grocery_beer_oranges_161.py`): the leaf
  `Food & Drink > Fruit & Vegetables > Fresh Fruit > Citrus Fruit > Oranges` holds oranges,
  blood oranges, orange segments and easy peelers (no "orange" in the title: a type match),
  while a chocolate orange, a cranberry & orange panettone, orange shortbread, orange
  drinking chocolate, chocolate & orange cookies, a marmalade and a juice carry the word
  in other categories; Lemons and Apples have bare-noun leaves too (no banana: the kit has
  no banana to draw);
- the failure class "beer": `Food & Drink > Beer, Wine & Spirits > Beer` with five leaves
  (Lager, Pale Ale, Sour Beer, Fruit Beer, Alcohol Free). Every beer has an `abv`
  attribute and a volume in ml, about half the titles end in the strength (" 4.8%"), a
  lager need not say "beer", and every beer contains gluten. The word is also a ginger or
  root beer (soft drinks), a beer battered haddock or cod (frozen, gluten, not
  vegetarian), a malted beer loaf, a cider vinegar and a wine gum;
- one category path per product, and one path per leaf label: `category_path` and
  `category_leaf` are the retailer's breadcrumb (the `grocery_rows` docstring has the rule),
  so a category route reaches all of a leaf's products; honey is its own leaf, not Jam
  (`tests/test_one_path_per_leaf_330.py`; Open Food Facts names the nodes, no tag is copied).

`tests/test_grocery_154.py` pins each case. The new pack shapes are `bar`, `bag`,
`butter_block` (a foil-wrapped block) and `lidded_tub` (ice cream, a spread), in
`kit_grocery.py`. The build makes one drawing per style. A pack's label is the
title's product noun (`grocery.pack_label`), and its panel also carries the range
name and a band of the style's flavor colors (`kit._panel` reads them from the
drawing's `line` and `chips` params). The range-name text tells siblings of a family
apart; the flavor band is not seen by the grid-clone gate (it reads the leaf, hero picture and price).
The grocery styles are held to the honesty tests of the main catalog and to a
grid-clone cap (`GROCERY_GRID_CLONES`).

The grocery styles are also the LAST templates of the main retail build
(`scale.templates()`, so `scale.py`, `image_release.py --skus N` and the flat export
carry them: Food & Drink at grocery depth in the one catalog, their drawings in the
same image archive). A build under the other templates' SKUs (`templates.before_grocery`) is what it was.
No style is derived from a grocery style, whose allergen, dietary and ingredient facts
are its own. The main build's own Food & Drink styles (`templates.main_food`: honey, jam, tea, coffee,
chutney, ...) stay, since the failure classes and the proof corpus pin them; no title or
product id repeats between them and the grocery styles. The main build's one honey jar
(`PLT-HONBLS`) stays and is derived from no further; grocery plants the other honeys. The ceiling's styles, SKUs and images, Food & Drink's
share of them (by category tree) and the grid-clone and near-duplicate rates are
`ceiling` and `near_duplicates` in `retail_figures.figures()`. The 15% grid-clone gate
(`scale.grid_clones`) is held over the non-grocery styles only: grocery has its own cap
(`GROCERY_GRID_CLONES`, 2%): its styles draw a tile of their own since gen#160.
`tests/test_retail_grocery_in_scale_154.py` pins it.

**The retail totals are build output (gen#162, gen#536).** The build's measured totals (styles,
SKUs, per-department and per-grocery-family counts, the grocery attribute-value counts and the
near-duplicate rate) are measured from the tree by `retail_figures.figures()` (seed 0, every
template exhausted, once per test run) and not committed: `scripts/build_derived.py` writes them
to `golden-retail/stats.json` and `docs/figures.md` in the `derived` CI artifact. The tests read
them with `figures()` and `tests/test_retail_figures_162.py` refuses a test, this README or a
docstring that restates one, so a grocery or type PR has no file of totals to conflict on. The
invariants keep their own asserts: no twins in a family, every allergen derived from the
ingredients, the near-duplicate and grid-clone caps.

### Observed failure classes 2 to 15, before and after on Elasticsearch

`real_classes.py` rebuilds thirteen query shapes observed by hand on a live
retail site (every name invented, the brands from `house_styles.py`). The
record model (`Style`, `Policy`, `ClassRow`, the closed lists) is in
`class_model.py` and the rows themselves are data in `class_rows.py`. Its records
carry the fields a policy reads and a title never states: `product_type`,
`audience` (adult, kids, baby), `size_range` (regular, petite, tall, plus),
`neckline`, `pattern`, `leg_style`, a `was_price` on a sale item only,
popularity (`sold_last_5_days`, `bestseller_rank`) and a pooled `rating` and
`review_count`. The round 4 records above are unchanged and carry none of
them.

Every record, round 4's included, is one document per STYLE (the gen#125
ruling, built by `variants.product`): a product with a color selector and a
size selector. Every color x size combination the style is sold in is a SKU
nested in `skus`, with its own `sku` id (`<product_id>-001` on), `color`,
size per size system, `price` and `in_stock`. No document carries a color
family (gen#186): it listed the same products as `color` under a second
facet, and grouping shades ("navy" covering Navy and Navy Check) is a PRISM
vocabulary group, which a merchandiser can see and change. The product's
`color_options` (one swatch per color: `color`, `hex`, `pattern`, `family`;
that `family` stays in the build, where the scaled catalog reads it to tell
styles apart, and is not exported) and `size_options` are derived from its SKUs, never authored, so they cannot
disagree with them; `sku_count` is the number of SKUs. Products = styles,
SKUs = nested rows: the crew-neck tee `PLT-CRWTEE` in Navy and White (S to XL)
and Heather Grey (S to L) is ONE product holding 11 SKUs. Rating, review count
and popularity are the style's: `sold_last_5_days` is the sales of every
color, summed. Legwear SKUs are color x waist x `inside_leg` with `in_stock`
per SKU, and jeans and trousers carry `rise`. Bedding SKUs are bed sizes whose
label carries the dimension ("Double (4 ft 6)"), each with its own price.
Beauty shades are the SKU colors of one product with `unit_size` in g or ml ([net volumes](retail-net-volume.md)).
`price_min` and `price_max` come from the SKUs, and `price` is the cheapest
SKU. `size_range` is a list; for legwear it is derived from the in-stock lengths
(Extra Short and Short/Petite give `petite`), never declared, so the flat
`size_range` filter of class 6 means "has an in-stock petite SKU".

Every class doc also carries the tile signals: `promotion` (a was-price gives
"On sale"; see below), `discount_pct` (derived, sale docs only),
`trending`, `online_only`, a `brand_owner` (own or third party; a brand has one
owner in every row, an own-label name `own` and an independent maker's name
`third_party`, pinned by
`test_every_brand_has_exactly_one_owner_across_the_templates_and_the_ceiling`; third-party
brands lead the offers, some with a `sub_collection` label such as "The
Active Edit"), and `badges` in one order (Bestseller for the top 15,
Trending, Online Only). Every doc has a full `category_path` of clean shopper
terms (at least three levels, no merchandising bucket such as Sale or Petite,
no leaf that is also a parent, one depth per node name) and its
`category_leaf`; the index adds `category_path_joined`, every ancestor joined
with "/", so a policy can route to a node. Food and furniture are colorless
(no color facet, no swatches); beer carries `abv` as an attribute; beds carry
nested SKUs from the shared five-size bed vocabulary with `width_cm` and
`length_cm`. The SKUs of a metal good (jewellery, watches, lighting, tech)
carry a `finish` equal to their color (Rose Gold, Yellow Gold, White Gold,
Silver).

Classes 10 to 12 are fixed by a route: the node's docs are recalled even when
their text misses (an easy peeler that never says "orange") and boosted.
Class 13 (mild) filters one in-stock nested SKU on `bed_size`. Class 14 reads
"rose gold" as ONE color value, as a color vocabulary filled by a terms
aggregation over the color field holds it, and filters one in-stock nested
SKU on it: rose bouquets with gold foliage and gold-plated rose quartz drop
out.

A color filter or facet goes through the nested SKUs: a product matches when
at least one in-stock SKU has the color, and the facet counts products
(`reverse_nested`), not SKUs. `es_proof.py` also runs the ruling's color
search (`real_classes.COLOR_QUERY`, "tee" with color Navy) and records it under
`color_search` in the proof. The nested filter returns each matching tee
once, and its `inner_hits` name exactly that tee's in-stock Navy SKUs, so a UI
can preselect Navy and show its swatch. The plain text query also finds tees,
but its response names no SKU: nothing to preselect. Since the print range
(`prints.py`) added its men's and women's tees, "tee" matches ten products
with a Navy SKU, the ruling's `PLT-CRWTEE` among them: the facet over
the result reads (SKUs / products) Navy 48 / 10, White 9 / 2, Grey 5 / 1, Heather
Grey 3 / 1.

`es_proof.py --host URL` loads the round 4 corpus plus these records into a
run-named index, runs each query twice, writes `real_classes_proof.json` and
deletes the index. The baseline is BM25 over title (x2) and description
times a popularity boost (`log1p(sold_last_5_days)`, x1.5 for the top 15
bestsellers), with a search-time synonym `balloon => balloon, barrel`: it
mimics the live site. The policy column is the fix approximated in raw
Elasticsearch. A target is in bold. A test checks that the proof was taken
over the current records, that no target is in a baseline top 3 (class 15 instead claims that a bra is: an espresso cup is a cup and may lead too), that the
policy top 3 is all targets, and that this table is the proof's.

The pre-merge run does not collect `prototypes/`, so `tests/test_real_classes_proof_fresh_479.py`
holds the proof's fingerprint and its claim to the records the build makes now. A change to an
indexed field of the corpus is red there until `es_proof.py` is run and the proof committed (the
drawing is not indexed and does not count). `real_classes_proof.json` stays in git for now: it is
an Elasticsearch recording and CI has no Elasticsearch to rebuild it (gen#536 follow-up).

| # | Class | Query | Baseline top 5 (BM25 x popularity) | With the policy: top 5 | Policy (raw ES) |
|---|---|---|---|---|---|
| 2 | Sibling types share a head word | *mattress topper* | 1. Quilted Mattress Protector `PLT-MTPQLT`<br>2. Waterproof Mattress Protector `PLT-MTPWTP`<br>3. Deep Fill Mattress Topper Protector `PLT-MTPTOP`<br>4. Cool Touch Mattress Protector `PLT-MTPCOL`<br>5. Pocket Sprung Mattress `PLT-MTRPKT` | 1. **Memory Foam Mattress Topper `PLT-MTTMEM`**<br>2. **Hollowfibre Mattress Topper `PLT-MTTFIB`**<br>3. **Wool Mattress Topper `PLT-MTTWOL`**<br>4. Memory Foam 5cm Mattress Topper `BED-TOPMEM`<br>5. Quilted Mattress Protector `PLT-MTPQLT` | product_type = Mattress Topper x10; product_type = Mattress Protector or Mattress or Pillow Protector x0.2 |
| 3 | Over-broad style synonym plus a bestseller boost | *balloon jeans* | 1. Mid Rise Barrel Jeans `PLT-BRLMID`<br>2. High Rise Barrel Jeans `PLT-BRLHIG`<br>3. Girls' Barrel Jeans (6-16 Yrs) `PLT-BRLKID`<br>4. Barrel Leg Trousers `PLT-BRLTRS`<br>5. Straight Leg Jeans `PLT-STRJNS` | 1. **Balloon Leg Jeans `PLT-BLNLEG`**<br>2. **Cropped Balloon Jeans `PLT-BLNCRP`**<br>3. **High Waisted Balloon Jeans `PLT-BLNHIW`**<br>4. Mid Rise Barrel Jeans `PLT-BRLMID`<br>5. High Rise Barrel Jeans `PLT-BRLHIG` | leg_style = balloon x10 |
| 4 | A neckline word matched as a keyword | *womens boat neck top* | 1. Womens High Neck Ribbed Top `PLT-HNRIBT`<br>2. Womens Crew Neck Cotton Top `PLT-CNCOTT`<br>3. Womens Round Neck Jersey Top `PLT-RNJERS`<br>4. Womens Tie Neck Top and Trousers Set `PLT-NTSETS`<br>5. Womens Collared Jersey Top `PLT-COLTOP` | 1. **Striped Boat Neck Top `PLT-BNTSTR`**<br>2. **Boat Neck Jersey Top `PLT-BNTJER`**<br>3. **Slash Neck Long Sleeve Top `PLT-SNTLNG`**<br>4. Womens High Neck Ribbed Top `PLT-HNRIBT`<br>5. Womens Crew Neck Cotton Top `PLT-CNCOTT` | filter product_type = Top; neckline = boat or slash x10 |
| 5 | Product type, pattern and audience not enforced | *check contrast bomber jacket* | 1. Cord Bomber Jacket `PLT-BMBCRD`<br>2. Wool Blend Bomber Jacket `PLT-BMBWOL`<br>3. Check Suit Jacket `PLT-SUITCK`<br>4. Boys' Bomber Jacket (2-8 Yrs) `PLT-KIDBMB`<br>5. Baby Bomber Jacket (3-36 Mths) `PLT-BABBMB` | 1. **Check Bomber Jacket with Contrast Collar `PLT-CKBCON`**<br>2. **Wool Check Bomber Jacket `PLT-CKBWOL`**<br>3. **Padded Check Bomber `PLT-CKBPAD`**<br>4. Cord Bomber Jacket `PLT-BMBCRD`<br>5. Wool Blend Bomber Jacket `PLT-BMBWOL` | filter product_type = Bomber Jacket; filter audience = adult; pattern = check x5 |
| 6 | Size range and sale state not extracted | *petite sale* | 1. Tapered Trousers `PLT-TAPTRS`<br>2. Wide Leg Trousers `PLT-WIDTRS`<br>3. Straight Leg Jeans `PLT-STRJNS`<br>4. Slim Jeans `PLT-SLMJNS`<br>5. **Petite Straight Jeans `PLT-PETJNS`** | 1. **Petite Straight Jeans `PLT-PETJNS`**<br>2. **Petite Wrap Midi Dress `PLT-PETDRS`**<br>3. **Petite Wide Leg Trousers `PLT-PETTRS`** | filter size_range = petite; filter on sale (price < was_price) |
| 7 | Sale word ignored | *womens sale dresses* | 1. Womens Linen Midi Dress `PLT-FPLINN`<br>2. Womens Smocked Mini Dress `PLT-FPSMOK`<br>3. Womens Jersey T-Shirt Dress `PLT-FPTEES`<br>4. Womens Satin Slip Dress `PLT-FPSLIP`<br>5. Womens High Neck Ribbed Top `PLT-HNRIBT` | 1. **Womens Wrap Dress `PLT-SDWRAP`**<br>2. **Womens Tiered Maxi Dress `PLT-SDMAXI`**<br>3. **Womens Shirt Dress `PLT-SDSHRT`**<br>4. **Petite Wrap Midi Dress `PLT-PETDRS`** | filter product_type = Dress; filter audience = adult; filter on sale (price < was_price) |
| 9 | Pack count only in title spellings | *5 pack socks* | 1. Cotton Rich Socks 7 Pack `PLT-SK7PKC`<br>2. Striped Socks 3 Pack `PLT-SK3PKS`<br>3. Kids' School Socks 5 Pack (6-16 Yrs) `PLT-SK5KID`<br>4. **Bamboo Socks, Pack of 5 `PLT-SK5BMB`**<br>5. Wool Walking Socks `PLT-SK1WAL` | 1. **Bamboo Socks, Pack of 5 `PLT-SK5BMB`**<br>2. **Sports Trainer Socks 5 Pack `PLT-SK5SPT`**<br>3. **Cotton Rich Ankle Socks 5pk `PLT-SK5PKC`** | filter units_per_pack = 5; filter audience = adult |
| 10 | A food word inside compounds and modifiers | *beer* | 1. Fiery Ginger Beer `PLT-GNGBER`<br>2. Cloudy Root Beer `PLT-RTBEER`<br>3. Beer Battered Haddock Fillets `PLT-BBHADD`<br>4. Malted Beer Bread `PLT-BRBRED`<br>5. Beer Battered Chunky Chips `PLT-BBCHIP` | 1. **Golden Table Beer `PLT-BRTABL`**<br>2. **4.8% Tropical Pineapple Sour Beer `PLT-BRTROP`**<br>3. **5.5% Hazy Wheat Beer `PLT-BRWHET`**<br>4. Fiery Ginger Beer `PLT-GNGBER`<br>5. Cloudy Root Beer `PLT-RTBEER` | route to Food & Drink/Beer, Wine & Spirits/Beer (recalled, boosted) |
| 11 | A fruit plural read as a flavour and a color | *oranges* | 1. Cranberry & Orange Panettone `PLT-PANCRO`<br>2. Chocolate & Orange Cookies `PLT-CKCORA`<br>3. Orange Hot Chocolate `PLT-HCORNG`<br>4. Orange Rose Bouquet `PLT-BQORNG`<br>5. Orange Graphic Tee `PLT-TEEW-ORANGE` | 1. **Blood Oranges `PLT-ORBLOD`**<br>2. **Navel Oranges `PLT-ORNAVL`**<br>3. **Seedless Easy Peelers `PLT-OREASY`**<br>4. **Valencia Oranges, Pack of 5 `PLT-ORANGS`**<br>5. Cranberry & Orange Panettone `PLT-PANCRO` | route to Food & Drink/Fruit & Vegetables/Fresh Fruit/Citrus Fruit/Oranges (recalled, boosted) |
| 12 | A type word that is also a color and a line name | *face cream* | 1. SPF 50 Face Sun Cream `PLT-SPFFCE`<br>2. Nourishing Face Oil `PLT-FCEOIL`<br>3. Loose Face Powder `PLT-PWDLSE`<br>4. Tinted Face Gel `PLT-TNTGEL`<br>5. Velvetmere Cream Body Oil Spray `PLT-VLCOIL` | 1. **Daily Hydrating Face Cream `PLT-FCDAYC`**<br>2. **Calming Face Cream `PLT-FCCALM`**<br>3. **Rich Night Cream `PLT-FCNGHT`**<br>4. SPF 50 Face Sun Cream `PLT-SPFFCE`<br>5. Nourishing Face Oil `PLT-FCEOIL` | route to Beauty/Skincare/Creams/Face Creams (recalled, boosted) |
| 13 | A size word not applied (mild) | *single bed* | 1. Single Cube Chairbed `PLT-CHRCUB`<br>2. Ottoman Storage Bed `PLT-BDOTTO`<br>3. Upholstered Sleigh Bed `PLT-BDSLGH`<br>4. Panelled Wooden Bed `PLT-BDPANL`<br>5. Two Seater Sofa Bed `PLT-SOFBED` | 1. **Metal Spindle Bed `PLT-BDMETL`**<br>2. **Shaker Wooden Bed Frame `PLT-BDSHKR`**<br>3. **Upholstered Bed Frame `PLT-BDUPHL`**<br>4. Single Cube Chairbed `PLT-CHRCUB`<br>5. Memory Foam Mattress Topper `PLT-MTTMEM` | filter an in-stock SKU with bed_size = Single (3 ft); product_type = Bed x10 |
| 14 | A two-word color split into words | *rose gold* | 1. Blush Rose & Gold Eucalyptus Bouquet `PLT-BQBLSH`<br>2. White Rose Bouquet with Gold Foliage `PLT-BQWHGF`<br>3. Gold Plated Rose Quartz Hoop Earrings `PLT-RQHOOP`<br>4. Classic Red Rose Bouquet `PLT-BQREDR`<br>5. Orange Rose Bouquet `PLT-BQORNG` | 1. **Cubic Zirconia Stud Earrings `PLT-RGSTUD`**<br>2. **Slim Mesh Strap Watch `PLT-RGMESH`**<br>3. **Wireless Charging Pad `PLT-RGCHRG`**<br>4. **Glow Powder Highlighter `PLT-RGHLIT`**<br>5. **Touch Dimmable Table Lamp `PLT-RGLAMP`** | filter an in-stock SKU with color = Rose Gold |
| 15 | One word, a sense in two departments | *cups* | 1. **Espresso Cup `PLT-MUG7`**<br>2. Moulded Cup T-Shirt Bra `PLT-CUPMLD`<br>3. Lace Demi Cup Bra A-E `PLT-CUPDEM`<br>4. Smooth Full Cup Bra B-G `PLT-CUPFUL`<br>5. **Leakproof Travel Cup `PLT-DRKTRV`** | 1. **Espresso Cup `PLT-MUG7`**<br>2. **Leakproof Travel Cup `PLT-DRKTRV`**<br>3. **Set of 4 Espresso Cups `PLT-DRKSET`**<br>4. **Fine Bone China Cup and Saucer `PLT-DRKSAU`**<br>5. **Apple Graphic Mug `PLT-MUG-APPLE`** | route to Home/Kitchen & Dining/Drinkware (recalled, boosted); off when the query says bra, demi, balcony or a cup size |
| 15 (control) | The other sense stays reachable: a bra | *d cup bra* | 1. **Moulded Cup T-Shirt Bra `PLT-CUPMLD`**<br>2. **Lace Demi Cup Bra A-E `PLT-CUPDEM`**<br>3. **Smooth Full Cup Bra B-G `PLT-CUPFUL`**<br>4. **Padded Balcony Bra `PLT-CUPBAL`**<br>5. Espresso Cup `PLT-MUG7` | 1. **Moulded Cup T-Shirt Bra `PLT-CUPMLD`**<br>2. **Lace Demi Cup Bra A-E `PLT-CUPDEM`**<br>3. **Smooth Full Cup Bra B-G `PLT-CUPFUL`**<br>4. **Padded Balcony Bra `PLT-CUPBAL`**<br>5. Espresso Cup `PLT-MUG7` | the same policy, off for this query |

Class 15 is a word with a sense in two departments: a bare *cups* is
drinkware in Home, and the cup of a bra (or a cup size) in Lingerie. Bras
titled "... Cup Bra" outsell the drinkware, and most drinkware says "Mug" or
"Tumbler", so without a policy the bras win. The policy routes a bare cup(s)
to the Drinkware node (recalling a mug that never says cup) and is off when
the query holds a bra word (`class_rows.BRA_WORDS`: bra, demi, balcony, a cup
size such as "D cup", "34DD" or "A-E"). Its control row, *d cup bra*, runs
with the same policy on and must still return bras: `ClassRow.controls` holds
such queries, and the proof records them under `controls`. The collision is
also a row of `class_rows.COLLISIONS`, with both meanings and the shopper
each one belongs to.

The cross-cutting patterns show in the table: the barrel bestseller leads
the balloon baseline (one tile however many colors it has: no collapse is
needed when a style is one document); kids and baby bombers enter an adult query;
and popularity lifts every distractor above a better text match. Class 9 is
an on-stage demo case: the pack count is a style attribute
(`units_per_pack`, a numeric count in `C62`, as industrial states a package
quantity) and the titles spell it "5 Pack", "5pk" and "Pack of 5", so the
"5pk" pack never matches the text. Class 8 (food words) is not planted: the
live site now redirects it.

### The output standard, and the retail export

Every domain's nested documents meet one output standard (gen#125):
`src/synthetic_ecommerce_data/core/standard.py` names its fields (exactly the
ones `emit.NESTED_MAPPING` declares) and `check_catalog()` validates a catalog
against it; `tests/test_output_standard.py` runs it over a fresh industrial
build, `golden-catalog/nested.jsonl` and the retail export, and over planted
defects. One attribute key has one class: `check_catalog(..., one_class_per_key=True)`
(on for retail, in `scale.py` and the test) refuses a key that carries a `unit_code` on
some entries and none on others, which the Engine refuses to start on. A measured value
(`5 ft`, which the core reads as a length) goes under its own key (a tree's `item_height`),
never under `size`. One concept has one key (gen#227): a measured height is `item_height`
(beside `item_width`, `item_depth` and `item_length`) on a sofa, a lamp, a doll, an olive tree and a
Christmas tree alike, and a furniture piece's storage is `storage_feature` (`Lift-Top`, `Shelf`,
`Drawer`, or `None` for no storage). `prototypes/retail_drawings/key_guard.py` names each concept, its
winning key and the keys that are another concept by design (`heel_height`, a grocery's `storage`),
and `tests/test_retail_attribute_keys_227.py` refuses a second key for a concept. The metric,
`key_guard.keys_per_concept`, is 1 for every concept. A new concept that two types could name
differently is added to `CONCEPTS`, with its winner and why. The text agreement check (`text_contradictions`, on by default) runs
on industrial too (gen#139). It reads a title or description as contradicting a value only when
the text names another value of the key's leaf pool and none of the document's own, and it
leaves out: a pool value whose words sit inside one of the document's own values ("Steel" on
18-8 Stainless Steel), a comparison or an equivalence to the end of its sentence ("Higher
strength than Grade 5.", "Equivalent to DIN 912 / ISO 4762.") and a parenthesised tolerance
class ("(ISO 492 Normal class)"). Industrial's hammer text-match decoys (gen#294) name a handle
or kind their attributes do not hold, by design: `hammers.decoy_ids(docs)` is their
`text_exempt`, by id, never a looser rule. A variant's `price` is in its `currency` (ISO 4217), never converted:
industrial writes `USD` and keeps `price_usd` beside it for its loader, retail
writes `GBP`. Availability is the `in_stock` yes/no; `stock`, the count, is
written only by a domain that models one (industrial). Industrial also writes two
plain fields on every SKU (gen#14), `pricing_unit` (`Each`, or `Per Pack` when the SKU
publishes a `Units per Pack` above 1) and `order_multiple` (a whole number, 1 today):
they are fields beside `price_usd`, never variants or facets. A field marked optional
(`series`, `ingredients`, `description`, `price_usd`, `stock`, `pricing_unit`,
`order_multiple`) is absent, never null,
on a document that has none; the grocery's food-only `ingredients` is one. A domain
may keep an entry out of the flat `text` while it stays a facet
(`standard.flat_documents(..., text_skip=...)`; the grocery's allergen warnings and
dietary claims).

`prototypes/retail_drawings/export.py` turns the 352-style build into that
standard: `skus` become `variants`, each SKU option a variant-level attribute
entry (a measurement split into `value`, `unit_code` and `value_canonical`);
color and size options, the `promotion` and other flags, rating and the other
retail-only fields become product-level entries (no `department`: see below); `image_id` is
`<product type>/<product id>/<drawing spec digest>`, one per style and
colorway, served under `/images/retail` from the image release
([The retail image release](../README.md#the-retail-image-release)). Every record states
its own `product_type` and `category_leaf` (the jeans, bra, bedding, beauty
and planted single-SKU records gained theirs in the record builders). A
percent (ABV, discount) is a plain number with `(%)` in its name: prism
spells no percent unit, so `P1` is not a unit code here and the validator
refuses it.

**`promotion`, label "Sale" (gen#189).** It replaced the boolean `offer`
("Offer: yes / no"). It is a multi-valued keyword, so a new campaign is a new
value and needs no remapping. Every product with a `was_price` carries "On sale";
a product in the seeded campaign (one reduced product in three, "Christmas
promotion") also carries the campaign's name, which never replaces "On sale".
A product with no `was_price` has no `promotion` entry at all, so the facet
never shows a "Not on sale" row. `was_price` and `discount_pct` stay. Multi-buy
is out of scope and becomes its own field later. The values and the rule are in
`prototypes/retail_drawings/promotion.py`; `tests/test_retail_promotion_189.py`
checks every layer. A loader that read `offer` (a facet config, a field map)
reads `promotion` instead; the catalog is reloaded once with #186 to #189.

**A share of every people department is reduced (gen#359).** Only Womens
products were reduced, so "mens sale shirts" and "kids sale shoes" found nothing
once `sale` became the exact filter `promotion` = "On sale". Now a share of each
department's SKUs has a `was_price`, with `discount_pct` and `promotion`: Womens
and Mens 8%, Kids 10% and Baby 25% (Baby has about 1,400 SKUs, and the ask is a
few hundred reduced SKUs across at least three product types in each of the
four). The shares and the rule are in `prototypes/retail_drawings/sale_share.py`,
chosen by a hash of the style id and not by the build's random generator, so no
other style moves. A petite style, a planted decoy and a failure-class row are
never reduced, which keeps "petite sale" a pair only a policy may honour.
`tests/test_retail_sale_share_359.py` checks the counts and that a reduced
document is marked the same way whoever made it. The was-price is taken off the
dearest SKU, so every size of a reduced style is under it (`price < was_price`);
`discount_pct` states the cheapest SKU's discount.

The retail build also writes industrial's **flat** shape, one document per
SKU, which is what elastic/prism-industrial-products loads (as its
`catalog.ndjson`, from `golden-catalog/flat.jsonl`); no loader reads the
nested shape yet. `standard.flat_documents()` projects a nested document to
it: the SKU's own attributes replace the product's under the same key, and
`facets_num` holds every measured value and the facts the domain names as
numbers (retail's rating, bestseller rank, was price, ABV and discount), so
those can be range-filtered. The keys and types are industrial's except that
retail has `price`, `currency` and `in_stock` where industrial has
`price_usd`, `stock`, `pricing_unit` and `order_multiple`, and no `dimension_provenance` or `spec_quality`
(`tests/test_output_standard.py` pins that list). To write both files:

    uv run python prototypes/retail_drawings/export.py OUTDIR   # nested.jsonl, flat.jsonl

**The Combined loader takes every SKU of it.** The loader projects the flat export before it
writes (`combined_catalog.py` in elastic/prism-industrial-products) and refuses a SKU whose
`size` is in no size system, or whose bare `length` or `width` would be renamed onto a
`garment_length` or `fit_width` the SKU already writes (gen#279: a handbag's `Mini`, and a
skirt's Petite/Regular/Long axis, now `fit_length`). `tests/test_retail_combined_loader_279.py`
runs both checks over every authored SKU. A new size shape or a new rename in the projection is a
row added to its mirror there; a key a SKU axis shares with a style attribute is named apart.

### The merchandising score

Every product, Retail and Industrial, carries `merchandising_score`: an integer 0 to 100, the
retailer's own blended ranking preference (gen#182). The nested product has it top-level
(optional in the standard, range-checked by `check_catalog`); every flat document has it as
`facets_num.merchandising_score`, so a field map can point at it. It is a ranking signal, not a
shopper facet: it is in no `facets`, `attributes` or `text`.

`src/synthetic_ecommerce_data/core/merchandising.py` derives it from a SHA-256 of the
product's id and the product's own signal, so it draws nothing from the generator's stream (no
other value of a build moved), the same seed gives the same scores, and a product scores the
same in a one-type build, any subset and the whole catalog (gen#183). Half the score follows the product's signal
and half is an independent draw, so boosting on it reorders a page that popularity alone
ranked. Of the products whose signal is weak, one in five is a "strategic push" scoring 80 or
more: a few percent of the catalog, high score on weak popularity. Retail's signal blends
`sold_last_5_days`, `rating` and `discount` (`export.merchandising`); a style with none of
them (round 4's) takes the independent draw alone and is never a push. Industrial models
neither margin nor popularity, so a line's signal is its SKUs' mean `stock`, and every SKU of
a line shares the line's score. `tests/test_merchandising_score_182.py` pins determinism, the
range, full coverage, a rank-correlation band against popularity and the push share.

### Variant axes

Every product, Retail and Industrial, states `variant_axes` (gen#47): the ordered list of the
attribute keys a shopper selects on the product page, coarsest first (`["color", "size_uk"]`,
`["length"]`), `[]` for a single SKU. It is top-level on the nested product and on every flat
document, the same on every SKU of a `product_id`, and each key is the one the flat document
stores the attribute under (`facets`), so a consumer looks up each hit's values by key. It
carries no display names: a consumer's field map names each key.

`core/variant_axes.py` derives it from the SKUs the generator emitted: the attributes that vary
across the product, less the *derived* ones (a nut's width across flats follows its thread size,
a UK size follows the US size), in the generator's own order. What remains names exactly one
SKU. `tests/test_variant_axes_47.py` pins the issue's five invariants on both builds, each with a
planted failure. Not every combination exists, so a consumer limits a dropdown to the
combinations the product's SKUs offer.

### The retail catalog at a size: `scale.py --skus N`

**The audience facet and the spelling of a facet**. The tree keeps its Womens, Mens
and Kids roots, and every SKU of a worn department (Clothing, Footwear, Lingerie & Nightwear),
or under a Womens, Mens or Kids root, also carries exactly one `audience`: `Womens`, `Mens`,
`Girls`, `Boys`, `Baby` or `Unisex` (`audience.py`; a template's own value wins, `Kids/Girls`
is Girls, `Kids/Boys` is Boys, `Kids/Baby` is Baby, the rest of Kids is Unisex). A product type has one name:
"Tee" is written "T-Shirt" (`export.PRODUCT_TYPE_FOLDS`; the image ids keep the authored type,
so none is re-rendered); `export.VALUE_CASE` writes `pattern` lower case and `rise` as `High`, `Mid` or `Low`.
`tests/test_retail_audience.py` refuses a facet with two values that differ only in case.
The roots are `Mens`, `Womens` and `Kids`, spelled as shoppers say them (gen#304; they were `Men` and
`Women`): the department, read from the top level, moves with them, and
`tests/test_retail_mens_womens_roots_304.py` fails if a whole node `Men` or `Women` returns at any layer.
The generator derives no spelling variants of a node (mens, men's, men): the catalogue repo's
vocabularies own those.
"Cleaning & Janitorial" is a department, not a root: its kitchen cleaners sit under `Cleaning`.

**There is no top-level `Accessories` root** (gen#248). Every accessory leaf sits under a
department as `<Department> > Accessories > <leaf>`: `Mens > Accessories > Belts`,
`Beauty > Accessories > Wash Bags`, and the bags, purses and umbrellas under `Womens > Accessories`
(`Bags > Handbags`, `Bags > Backpacks`, `Bags > Tote Bags`, `Purses & Wallets > Purses`,
`Umbrellas`). A root would show as a separate department in the store's department filter. The
unisex goods (backpack, tote, umbrella) stay one product in one place, under the department whose
shoppers the generator targets for bags; the `audience` facet says `Unisex`, the path does not.
`tests/test_retail_accessories_under_departments_248.py` guards it.

**Worn accessories (gen#422)**: the issue lists belts, hats and caps, scarves, gloves, sunglasses
and wallets under `Accessories > ...`; with no root they sit under `Womens > Accessories` (a belt
or a wallet for men under `Mens > Accessories`), each a spec under `type_specs/` with its own
drawing shape registered in the spec module. Done: sunglasses (`type_specs/sunglasses.py`: five
frames, three lenses, UV400, the six main colors; its decoys are a UV400 name on a pair with no
UV protection, a blue tint in the text of a black frame, a color word and a category noun in a range name
and another brand's name in the text).
Belts (`type_specs/belt.py`, shape `belt_buckled`: four materials, three buckles, the waist in
inches as a measured SKU axis), hats and caps (`type_specs/hat_cap.py`: five kinds in one size,
S/M and L/XL) and gloves (`type_specs/gloves.py`: four kinds, a lining, S to XL, whose SKU axis is `glove_size_letter`: the baseball glove's `glove_size` is in inches) follow
the same way, each with the six main colors, two brands and decoys of classes 4, 5, 6 (two: a color
word and another category's noun in a range name) and 7. Every spec decoy is exempt from the output
standard's text check (`scale.TEXT_EXEMPT`), as the other text-match decoys are. Belt left the
legacy type list, so `LEGACY_CEILING` is one lower. Scarf and wallet are still to do.

**The store's department is the top level of `category_path`, and no document states one**
(gen#281). The retail tree has exactly eleven roots: Womens, Mens, Kids, Food & Drink, Home,
Beauty, Cleaning, Toys, Gifts, Garden and Sports & Outdoors (gen#265). Food sits under Food &
Drink, Baby under Kids (`Kids > Baby > ...`) and Electricals under Home (`Home > Electricals >
...`), each with its subtree intact; a product still sits in one place. The documents carry no
`department` attribute or flat column (its values mixed audience, Clothing, with product kind,
Footwear): the one fact it held that no other attribute does, the safety boot's Workwear & PPE,
is carried by its `safety_rating` and `toe_cap`. A consumer reads the department from
`category_path[0]`. The build records keep a `department` of their own (`departments.py`'s
closed list), an internal classification the ceiling build's brand pools, floors and share
read; `export.DROPPED` keeps it out of every document.

**A type sits under its generic category** (gen#283). `Sofas` holds `Corner Sofas`, `Recliner Sofas`,
`Modular Sofas`, `Chaise Sofas` and `Sofa Beds`, so a filter on `Home/Furniture/Sofas` takes every sofa
and "corner sofa" can still narrow to its own child. The same holds for `Tables` (coffee, dining, side),
`Lighting > Lamps` and `Lighting > Lights`, `Fans`, `Drills`, `Tool Sets`, `Skincare > Creams`,
`Kitchen & Surfaces > Cleaners`, `Milk > Plant Milk`, `Biscuits & Snacks > Crisps`, `Bedding > Kids' Bedding`
and `Beer, Wine & Spirits > Beer`. `prototypes/retail_drawings/tree_guard.py` states three rules and
`tests/test_retail_tree_nesting_283.py` runs them over the shipped documents, not the build
records: (a) no node has a sibling whose label is a word-suffix of another's (`Sofas` beside `Corner Sofas`,
`Skinny Jeans` beside `Super Skinny Jeans`); (b) three or more siblings that share a head noun sit under a parent that names it, or are listed in the guard's `EXCEPTIONS` with a reason; (c) a product whose
title names a more specific node of its own department sits in that node. Two siblings (`Bath Towels`,
`Beach Towels`) need no parent. A product still sits in exactly one place.
`tests/test_retail_departments_281.py` holds the root list at every layer, and
`retail_figures.figures()` records the ceiling's styles and SKUs per top level
(`ceiling.top_levels`).

**A fit or a bra style is a filter, not a leaf**. A jean sits at `<Root>/Jeans` and a pair of
trousers at `<Root>/Trousers`, its fit in `leg_fit` alone (the failure-class rows' `leg_style`
is folded into it). A bra sits at `Womens/Lingerie/Bras`, unless it is a Sports, Nursing, Sleep,
Post-Surgery or Mastectomy bra, whose node stays; its old style leaf is split into `bra_shape`,
`padding`, `back_style` and `fabric` (`facet_leaves.BRA_LEAVES`). `fabric` is the fibre or weave a
shopper names (Cotton, Linen, Denim, Oxford, Silk, Nylon), from one closed list. A grade or blend
("98% Cotton, 2% Elastane") leaves its fibre as the fabric and becomes the document's
`fibre_content`, a detail in no facet (`facet_leaves.FABRIC_MOVES`, gen#187; no `composition`). A blend names fibres:
"Cotton Blend" leaves Cotton as the fabric and "Cotton Jersey" leaves Jersey (gen#258); the tailored shorts' "Polyester Blend" is Suiting by their text, a move keyed by (product type, value) in `facet_leaves.TYPED_FABRIC_MOVES` (gen#291). A fabric has one name (Faux Leather, not also Leather-Look or Leather Look), and a use, a pocket style or a fit is never a
fabric: sports leggings are Knitted with a Compression `leg_fit`, cargo joggers are Twill with
cargo pockets, and cycling shorts carry the Compression `leg_fit` and no fabric. The list also holds the fibres a
shopper types before a garment (Leather, Suede, Faux Suede, Wool, Cashmere, Crochet, Muslin, Voile,
Brushed Cotton; gen#187's coverage review): skirts carry the first seven. Any other garment with no
`fabric` of its own also carries the fibres its `material` names (`facet_leaves.MATERIAL_FABRICS`, exact rows,
the `material` kept: a Dress "Linen blend" is Linen, a Polo Shirt "Cotton" is Cotton, a coat "Wool Cashmere
blend" is Wool and Cashmere) and its title names (`facet_leaves.stated_fabrics`: "Cotton Crew Neck Tee",
"Wool Check Bomber Jacket", "Boat Neck Jersey Top"). A fibre followed by a hyphen is no claim ("Leather-Look",
"Cashmere-Feel", "Wool-Free", "Fleece-Lined"): those titles are the text-match decoys. A brushed cotton
flannel is Flannel and Brushed Cotton (`facet_leaves.FABRIC_ALSO`). Viscose joined the list. A new garment
`material` that names a listed fibre is a row in the table or a reason in `MATERIAL_NOT_FABRIC`, and the
tests fail until it is. Only a garment gets this: a bag, a belt, a watch, jewellery, a shoe and homeware
(`facet_leaves.NON_TEXTILE_TYPES`, and every department but Clothing and Lingerie & Nightwear) keep their own
`material` or `upper_material` ("leather", "suede", Leather, Faux Leather), so one concept has one facet and
the fabric marker reads `fabric` alone; a retailer who wants "leather boots" or "leather sofa" to match adds
`upper_material` and `material` as marker sources on the catalogue side. Homeware keeps its own `material`
facet (Seagrass, Bone China, Melamine, Stainless Steel, Cast Iron). A skirt that only names a fibre in a
trim, a lining or a belt is a text-match decoy for it (gen#294). Only the document changes (`export.standard_document`):
the build record keeps its leaf, so the derivation and every image id are what they were, and a
title keeps its words ("Skinny Jeans"). `tests/test_retail_facet_leaves.py` refuses a node
under Jeans, Trousers or Bras that names one of those values, a `fabric` holding a percentage,
a comma-joined fibre list or a fibre alone, a jean without a `leg_fit` or a
bra without a `bra_shape`, and a facet with two values that differ only in case or hyphenation.

`prototypes/retail_drawings/scale.py --skus 20000 --out retail.jsonl` builds the
retail catalog to a target SKU count, writes it in the standard, and prints a
report:
- the coverage (styles, SKUs per department, products per leaf, attribute fill
  per type, image ids and distinct drawings);
- the distinctness (duplicate titles, clones, and same-leaf near-duplicate
  listings on a sample);
- the grid clones: the share of styles that share their leaf, hero picture and
  price with another style, which is what a results grid shows (the gate: at most
  15%), and the distinct prices per leaf (min and median);
- the `check_catalog` problem count, the build time and the peak memory.

The templates (`templates` in `retail_figures.figures()`) come first: the authored
styles, then the deep-SKU jeans,
bras and shoes that only the scaled catalog carries (`scale_rows.py`), then the toys,
garden, gifts, cleaning, food, beauty and home styles that hold every department at
at least its floor of styles (`breadth_rows.py`, below), then one or two plain products in each of a first increment of new leaves (`BREADTH_34`, gen#34: cutlery sets, dinner sets, claw hammers, perfume, seeds, oven cleaners (cherries moved to the grocery `CHY` family, gen#445); every set carries a `piece_count` (a C62 count, agreeing with its title and rising with its price) and every cordless drill a `voltage_v` (unit code VLT), gen#173; more leaves are further rows there, and `tests/test_retail_breadth_34.py` holds that each is a leaf no other template uses), then the furniture (`furniture_rows.py`, gen#199: dining tables by seat count, top outline and top material (a glass top draws translucent, a marble-effect top veined, gen#226) with their sizes in `item_width` and `item_length`, dining chairs sold single or as a set with `units_per_pack`, coffee and side tables, bookcases with their height in `item_height`, wardrobes, chests of drawers and mirrors, each drawn by its own shape in `kit_furniture.py`; no derived style copies one, and `tests/test_retail_furniture_199.py` holds the range and `tests/test_retail_furniture_drawings_226.py` that a White piece draws white), then the styles that
three failure classes need (`distractor_rows.py`; `baseline_rank.py` ranks a build
without a policy, and `tests/test_retail_distractors.py` holds the result): mattress
protectors, mattresses and pillow protectors that out-sell the toppers; bestselling
barrel-leg jeans whose text says balloon; 150 petite styles with a minority on sale,
and 60 sale styles that never say petite, and the steak class (gen#264: seven steak-knife styles, a steak plate, board and cast-iron weight that lead `steak`, each with a material and none derived (gen#268), with the beef steaks and tinned tuna steaks the grocery build adds as families `SKS` to `SKW` and `TUS`), then the shirts (`shirt_rows.py`: Oxford,
Flannel, Linen and Denim, for Mens and Womens, under `Tops/Shirts`, typed `Shirt`;
no derived style copies one), then the living-room seating (`sofa_rows.py`, gen#196:
sofas sold as 2, 2.5, 3 and 4 seaters, left- and right-hand corner and chaise sofas,
modular, recliner and sofa-bed sofas, armchairs and footstools, each drawn by its own
shape in `kit_seating.py`; a sofa, corner sofa and chaise sofa is drawn with exactly the whole seat
cushions its `seat_count` states (a corner sofa's return and corner seats are counted in it), a chaise has its
back along the whole rear, and a sofa bed's and a topper's `depth` is a bare number in `CMT` with a millimeter
canonical value (gen#225, `tests/test_retail_seating_225.py`); no derived style copies one, and
`tests/test_retail_seating_196.py` holds the range), then the household styles (`household_rows.py`, gen#200:
saucepans, frying pans, casserole dishes, kitchen bins, storage boxes, laundry baskets,
clothes airers and mops, each drawn by `kit_household.py` with the count its record states
(pans in a set, bin lids, basket compartments, airer tiers); no derived style copies one,
and `tests/test_retail_household_200.py` holds them), then the lower-body styles (`lowerbody_rows.py`,
gen#206: leggings, joggers, shorts, cycling shorts, tracksuits and skirts, each drawn by `kit_lowerbody.py`
with the marks its record states (pockets, cargo pockets, belt loops, pieces, tiers, a pad); no derived
style copies one, and `tests/test_retail_lowerbody_206.py` holds them), then the small appliances (`appliance_rows.py`, gen#202:
desk, pedestal, tower, ceiling and handheld fans, heaters, kettles
and toasters, each drawn by `kit_appliances.py`; none is derived from), then the underwear and nightwear (`underwear_rows.py`, gen#208: knickers,
tights, vests, slips, shapewear, dressing gowns and boxers with a pack axis,
drawn by `kit_underwear.py`; none is derived), then the swimwear (nine specs under `type_specs/`, rows in `swimwear_rows.py`, gen#212: swimsuits (cut, tummy control, padded cups, leg cut, a cup axis), bikini tops and bottoms sold as separates (top shape, rise, tie side), tankinis, swim shorts, kids' and baby swimsuits (UPF, sleeve, nappy friendly), period swimwear (absorbency), cover-ups and kaftans and changing robes under the `Swimwear` node of Womens, Mens and Kids, each its own shape in `kit_swimwear.py` with the marks its record states, the six main colors and apparel text-match decoys; copied by no derived style, `tests/test_retail_swimwear_212.py`), then the toys (`toys_rows.py`, gen#201: building sets, jigsaws, board games, dolls, wooden toys, role play toys, arts and crafts kits and ride-ons, drawn by `kit_toys.py`; every style carries an `age_range` and most a `toy_type`, a jigsaw's finished size is its `item_length` and `item_width` in `CMT` (canonical value in millimeters) beside the `finished_size` text (gen#261), four invented character ranges (`line`) each span several kinds, and a counted mark in the drawing equals the count the record states, `tests/test_retail_toys_201.py`; a toy vehicle or ride-on whose paint is a free choice is sold in ten colors, one SKU and drawing each, a bike or trike in wheel sizes (the `wheel_size` axis, drawn to scale), and a style whose color is its identity (a police car, a taxi, a fire engine, bare wood) keeps one and says why in its `fixed_color`, `tests/test_retail_toy_vehicle_colors_271.py`; no derived style copies one; kites, play kitchens, dolls' houses, card games, marble runs and water guns have their own specs and drawings, [retail-toys-depth.md](retail-toys-depth.md), gen#424; babywear and nursery types, sleepsuits to nursery storage, have their own specs and shapes too, [retail-babywear.md](retail-babywear.md), gen#213), then the lighting (`lighting_rows.py`, gen#197: floor,
table, desk, ceiling and wall lights and lampshades under `Home/Lighting` (`Lamps`, `Lights`), each typed by
its name; a SKU is a color times a finish, a shade color or a diameter, and its image draws
that SKU's own value; a light's color temperature is a kelvin count with unit code `KEL` under the one key `color_temperature`, never `3000K` in the value, gen#232; a tunable desk lamp holds its two ends as two entries under that same key, 2700 and 6500, and no minimum or maximum key exists, gen#498; only a light whose source comes with it states one, a bulb or a lamp with an `Integrated LED` fitting, and a fitting that takes a replaceable bulb (E27, E14, GU10, B22) states none; `Home/Lighting/Light Bulbs` (`type_specs/light_bulb.py`, gen#498) holds 32 LED bulbs, a GLS, candle or spotlight in each of the four fittings, two wattages each, a listing for each of 2700K Warm White, 3000K Soft White, 4000K Cool White and 6500K Daylight, with the box name and the kelvin in the title, drawn by `kit_lighting.light_bulb` in the glow of its temperature, and 12 text-match decoys (paints, scented candles, towels, face cloths, a cushion, a shirt and skin creams), `tests/test_retail_light_bulbs_498.py`), then the bags, umbrellas and jewelry (`accessory_rows.py`,
gen#207; likewise copied by no derived style), then the Sports & Outdoors styles (`sports_rows.py`, gen#265 and gen#368: camping, yoga & fitness, cycling pumps, baseball, swimming, team and racket sports, drawn by `kit_sports.py`, copied by no derived style; leaves, filters and types not built in [docs/retail-sports-tree.md](retail-sports-tree.md), `tests/test_retail_sports_265.py`), then the school uniform styles (`school_rows.py`, gen#205, first increment: school trousers, skirts, pinafores and shirts under `Kids/School Uniform`; drawn by `kit_school.py`, school-age sizes `3-4 Yrs` to `15-16 Yrs`, fit, adjustable waist, style, sleeve and pack as structured attributes, decoys from `decoy_apparel.py`, copied by no derived style, `tests/test_retail_school_205.py`), then the garden machines (`garden_rows.py`, gen#203, first increment: lawn mowers, robot mowers, grass trimmers and barbecues under `Garden`, drawn by `kit_garden.py`, with text-match decoys, [docs/retail-garden.md](retail-garden.md); copied by no derived style), then the garden hoses (`type_specs/garden_hose.py`, gen#292: a reinforced and an expandable hose under `Garden/Watering/Garden Hoses`, drawn by `kit_garden.py`, a SKU axis in metres (`item_length`) and the six main colors, with 15 text-match decoys in `garden_rows.py`, copied by no derived style, `tests/test_retail_garden_292.py`), then the gifts (`gifts_rows.py` and `type_specs/gift_mug.py`, `greeting_card.py`, `notebook.py`, `money_box.py`, `gift_hamper.py`, gen#425: 26 styles and 180 SKUs of mugs, greeting cards, notebooks, money boxes and pamper hampers under `Gifts`, each drawn by its own shape in `kit_gifts.py`, the six main colors, ten text-match decoys in `decoy_product_words.py` ([docs/retail-product-word-decoys.md](retail-product-word-decoys.md)), copied by no derived style, `tests/test_retail_gifts_425.py`), then the home accessories and decor (`type_specs/clock.py`, `ornament.py`, `artificial_flowers.py`, `decorative_tray.py`, `door_stop.py`, `wallpaper.py`, `diary.py` and `picnic_blanket.py`, gen#217: clocks (wall, mantel and alarm), ornaments, artificial flowers and stems (loose or in a vase), decorative and trinket trays, door stops, wallpaper, diaries and picnic blankets under `Home`, `Gifts` and `Sports & Outdoors`, each drawn by its own shape in `kit_decor.py` (the picnic blanket in `kit_sports.py`, with the Sports & Outdoors types, its two decoys in `decoy_product_words.py`) with the variant axis as a drawing param, a SKU axis in centimetres or metres (`export.OPTIONS` gains `roll_length_m`) and the six main colors, with 18 text-match decoys of other departments in `decor_rows.py` and a digital watch that names an alarm clock in `type_specs/digital_watch.py`; greeting cards are gen#425's; copied by no derived style, `tests/test_retail_decor_217.py`), then jewellery and watches (`type_specs/hoop_earrings.py`, `drop_earrings.py`, `analog_watch.py`, `digital_watch.py`, `fitness_band.py`, gen#423: five new types beside the legacy `Earrings` and `Watch`, drawn by `kit_jewellery.py`; earrings vary by metal, a watch or band by strap color times a case diameter in millimetres (`case_diameter`), with a strap, water resistance in metres and an audience as attributes, and two text-match decoys per type; copied by no derived style, `tests/test_retail_jewellery_watches_423.py`), then the near-white apparel and main-color bras (`colorgroup_rows.py`, gen#302, [docs/retail-color-group.md](retail-color-group.md); copied by no derived style), then the grocery styles (below, `grocery.py`, gen#154). Further styles are
derived from them, deterministically by `--seed`, and a smaller build is a prefix of a larger one.
The ten beauty depth types (mascara to sun cream, gen#214) are specs under `type_specs/` and are not derived from; see [retail-beauty-depth.md](retail-beauty-depth.md).
Lingerie and swimwear that name their cups in the plural (`cups_plural_rows.py` and `swimwear_rows.py`, gen#508): thirteen bras (bralettes, sports bras, T-shirt bras) titled "... with Removable Cups", "Padded Cups" or "Moulded Cups", and four swimsuits and four bikini tops "with Padded Cups", so a bare *cups* with the policy off meets lingerie as well as drinkware (class 15). Each title is true to its record (`padding` for a bra, `padded` Yes for swimwear), none names drinkware, and none is copied by a derived style; `tests/test_retail_plural_cups_508.py`. The eight swimwear rows are in type specs; the thirteen bras are not, because `Bra` is one product type whose rows sit in `class_rows.py`, `variants.py` and the lingerie rows, and `test_a_spec_type_has_no_row_outside_its_spec_file` refuses a spec for a type with a row outside it: a spec for the thirteen alone fails, and moving every bra into one spec is a migration of its own.
Every top, dress and knit states a `neckline`, and boat and slash tops are held in depth with the neighbouring necklines (`neckline_rows.py`, gen#181; none is derived); see [retail-neckline-depth.md](retail-neckline-depth.md). A style word in a title (coat, shirt, maxi, polo) agrees with the neckline, length, sleeves and material; see [retail-garment-styles.md](retail-garment-styles.md).
The seven luggage and travel types (suitcase to neck pillow, gen#209) are specs under `type_specs/` too, likewise not derived from; see [retail-luggage-209.md](retail-luggage-209.md).
Each derived style gets a new range name and a brand from its type's pool. It
also differs from its template and from every sibling in a value its title shows
or in its hero color family: a rename alone is not a style. When only the hero
color sets it apart, its title ends with that color ("..., Dark Indigo"), and
that hero is its only colorway. A
changed motif is redrawn in the picture and the title, and the description is
rebuilt around it; a "Shown in" color names the hero. It takes a subset
of the template's colorways and keeps the template's size run, and a count of
colorways its text states ("in 12 washes") is its own: "in one wash" for a
colorway alone. A changed value its SKUs also carry (a shoe's `upper_material`)
is rewritten on every SKU, and the style lists only the values its kept SKUs
hold (a shoe drops the `upper_material` entry of a material no kept SKU holds). Its price is
re-drawn inside its leaf's band, as a function of the values it changed (a
premium material costs more; a plate's material is not drawn, so its price, bone china above porcelain above stoneware above enamel above melamine, is what keeps two plates of one finish off one grid tile, gen#229, `PLATES_GRID_CLONES`). A draw whose title or description contradicts an
attribute is refused, and `check_catalog` refuses such text too. The module
docstring has the rules. A description's closure and a style's pattern are held to its attributes ([gen#250](retail-attribute-text.md)). Today's templates run out at `ceiling` in
`retail_figures.figures()` (with and without the grocery styles), and the CLI exits 2 past that. Raise the ceiling with data: more title-visible
values per leaf, more colorways, and more templates.
`--flat PATH` also writes the flat file (one document per SKU, `ingredients` top-level on a
food SKU). `tests/test_retail_scale.py` holds it at the templates' SKUs plus 4,500 (its
`TARGET`, pinned to the template total so new templates never empty the
derived-style sample), and holds the ceiling's grid clones at 15% or under too.

**One `pack_size` vocabulary for a count** (gen#246). A pack of identical or different items is
`Single` or `N pack` (`2 pack`, `4 pack`, `10 pack`) in every department: underwear, school,
home (dining chairs, tableware), grocery and the planted distractors alike, so the `pack_size`
facet lists one spelling. A title keeps natural wording ("Set of 4 Espresso Cups"); the value
does not. A net weight or volume (`400g`, `4 x 35g`, `2 pint`, `12 inch`) is a measure and
stays. `tests/test_pack_size_values_246.py` reads every `pack_size` of the authored build.

**Each department has a floor of its own** (gen#220). At the ceiling, every department holds
at least `breadth_rows.DEPARTMENT_FLOOR` derivable styles (150; the smallest today is Beauty
at 212). It is a count per department, not a share of the total, so a batch PR that adds
types to one department (the Home, Clothing and other type batches, gen#196-#217) never lowers
another department's standing: do not add rows to an unrelated department to pass it.
`test_every_department_holds_its_floor_of_styles` holds the floor,
`test_the_department_floor_is_not_lowered` holds the floor itself at or above 150 (gen#234), and
`test_growing_one_department_never_starves_another` builds the ceiling with 200 more Home
templates and holds every other department at its floor. A batch that removes or narrows a
department's own rows below the floor still fails: raise that department with rows of its own.

### Womens sizes above UK 16 (gen#434)

The Womens UK size run stopped at 16 (some styles at 18 or 20), so a query for a dress in size 22
read the size and found no dress that carried it. `plus_sizes.py` runs over `scale.templates()`:
three in five of the Womens styles whose SKUs carry a bare number `size` (dresses, tops) or
`size_uk` (jeans, with its EU and US sizes at UK + 28 and UK - 4) are carried on to UK 24.
Trousers measure by `waist` and knitwear is letter-sized, so neither is changed.
Each new SKU copies the largest-size SKU of its color; the new SKUs are appended, so no SKU id
moves, and a derived style inherits the longer run. Decoys of `decoy_rows.py` and
`decoy_product_words.py` keep their run. `tests/test_retail_plus_sizes_434.py` pins at least 30
Womens dresses at UK 22 and the chart.

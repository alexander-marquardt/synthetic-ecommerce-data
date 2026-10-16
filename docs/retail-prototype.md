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

`tests/test_retail_drawing_honesty.py` holds the ceiling build to the same rule:
the toilet cleaners draw as an angled-neck bottle or a hanging rim block (two units
for a twin pack, shapes in `kit_cleaning.py`), a `tub` only holds a tub of something,
a mug or cup draws as a `mug`, and a label is the title's product noun. The label
pairs not yet fixed are `LABEL_DEBT` there: it may only shrink. A changed drawing is a
new image digest, so the retail image bundle is re-released after the merge.

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

`footwear_rows.py` holds thirty-one shoe styles (sixteen women's, ten men's,
five kids'), one document per style with its color x width x size SKUs
nested. A size is three fields, `size_uk`, `size_eu` and `size_us`, read from
one chart row of the audience, so they never disagree; half sizes exist only
where a shoe is cut in them, and a wide fit only in the sizes it names. A ring's UK
letter and US number are other kinds of value, so they sit under `ring_size_uk` and
`ring_size_us` (gen#249), never these keys. Each
color names its upper material, which both the `upper_material` facet and the
drawing read. `kit_footwear.py` draws the shoe from the side in seventeen
kinds (court, kitten and block heels, ballet pumps, loafers, brogues,
trainers, running shoes, slippers, sandals, ankle, Chelsea, chukka, knee-high,
walking and safety boots, wellies), with the material's texture and the
closure. The boots row above is checked over the round 4 corpus plus
footwear (`footwear_rows.catalog()`). Footwear is not in the Elasticsearch
proof corpus.

### Grocery

`grocery.py` (data in `grocery_rows.py`, gen#154) builds Food & Drink styles
whose SKUs are flavor x pack size: `python3 prototypes/retail_drawings/grocery.py
--skus 10000 --out DIR` writes `nested.jsonl` and `flat.jsonl`, both in the output
standard. Its styles, SKUs and each family's share are `templates.grocery` and
`grocery_families` in `golden-retail/stats.json` (below); it covers the food leaves, plus a
kitchen-cleaner leaf and a body-lotion leaf for the overlaps. Each SKU states
`contains` and `may_contain` over seven allergens (peanuts, tree nuts,
milk, gluten, soy, egg, fish), its `dietary` labels (Vegan, Vegetarian, Gluten Free,
Nut Free, Organic), `pack_size`, `units_per_pack` and its net weight or volume.

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
`ceiling` and `near_duplicates` in `golden-retail/stats.json`. The 15% grid-clone gate
(`scale.grid_clones`) is held over the non-grocery styles only: grocery has its own cap
(`GROCERY_GRID_CLONES`, 2%): its styles draw a tile of their own since gen#160.
`tests/test_retail_grocery_in_scale_154.py` pins it.

**The retail totals are build output (gen#162).** The build's measured totals (styles, SKUs,
per-department and per-grocery-family counts, the grocery attribute-value counts and the
near-duplicate rate) are in `golden-retail/stats.json`, which
`python3 prototypes/retail_drawings/retail_figures.py` rewrites (seed 0, every template
exhausted). The tests read them there and `tests/test_retail_figures_162.py` refuses a test,
this README or a docstring that restates one, so a grocery or type PR changes them only in that
file: after merging `main`, rebuild it, never keep either side of a conflict in it. The
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
`trending`, `online_only`, a `brand_owner` (own or third party; third-party
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
(`5 ft`, which the core reads as a length) goes under its own key (a tree's `height`),
never under `size`. A variant's `price` is in its `currency` (ISO 4217), never converted:
industrial writes `USD` and keeps `price_usd` beside it for its loader, retail
writes `GBP`. Availability is the `in_stock` yes/no; `stock`, the count, is
written only by a domain that models one (industrial). A field marked optional
(`series`, `ingredients`, `description`, `price_usd`, `stock`) is absent, never null,
on a document that has none; the grocery's food-only `ingredients` is one. A domain
may keep an entry out of the flat `text` while it stays a facet
(`standard.flat_documents(..., text_skip=...)`; the grocery's allergen warnings and
dietary claims).

`prototypes/retail_drawings/export.py` turns the 328-style build into that
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

The retail build also writes industrial's **flat** shape, one document per
SKU, which is what elastic/prism-industrial-products loads (as its
`catalog.ndjson`, from `golden-catalog/flat.jsonl`); no loader reads the
nested shape yet. `standard.flat_documents()` projects a nested document to
it: the SKU's own attributes replace the product's under the same key, and
`facets_num` holds every measured value and the facts the domain names as
numbers (retail's rating, bestseller rank, was price, ABV and discount), so
those can be range-filtered. The keys and types are industrial's except that
retail has `price`, `currency` and `in_stock` where industrial has
`price_usd` and `stock`, and no `dimension_provenance` or `spec_quality`
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
`golden-retail/stats.json` records the ceiling's styles and SKUs per top level
(`ceiling.top_levels`).

**A fit or a bra style is a filter, not a leaf**. A jean sits at `<Root>/Jeans` and a pair of
trousers at `<Root>/Trousers`, its fit in `leg_fit` alone (the failure-class rows' `leg_style`
is folded into it). A bra sits at `Womens/Lingerie/Bras`, unless it is a Sports, Nursing, Sleep
or Post-Surgery bra, whose node stays; its old style leaf is split into `bra_shape`,
`padding`, `back_style` and `fabric` (`facet_leaves.BRA_LEAVES`). `fabric` is the fibre or weave a
shopper names (Cotton, Linen, Denim, Oxford, Silk, Nylon), from one closed list. A grade or blend
("98% Cotton, 2% Elastane") leaves its fibre as the fabric and becomes the document's
`fibre_content`, a detail in no facet (`facet_leaves.FABRIC_MOVES`, gen#187; no `composition`). A blend names fibres:
"Cotton Blend" leaves Cotton as the fabric and "Cotton Jersey" leaves Jersey (gen#258); the tailored shorts' "Polyester Blend" is Suiting by their text, a move keyed by (product type, value) in `facet_leaves.TYPED_FABRIC_MOVES` (gen#291). A fabric has one name (Faux Leather, not also Leather-Look or Leather Look), and a use, a pocket style or a fit is never a
fabric: sports leggings are Knitted with a Compression `leg_fit`, cargo joggers are Twill with
cargo pockets, and cycling shorts carry the Compression `leg_fit` and no fabric. Only the document changes (`export.standard_document`):
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

The templates (`templates` in `golden-retail/stats.json`) come first: the authored
styles, then the deep-SKU jeans,
bras and shoes that only the scaled catalog carries (`scale_rows.py`), then the toys,
garden, gifts, cleaning, food, beauty and home styles that hold every department at
at least its floor of styles (`breadth_rows.py`, below), then one or two plain products in each of a first increment of new leaves (`BREADTH_34`, gen#34: cutlery sets, dinner sets, claw hammers, perfume, seeds, cherries, oven cleaners; every set carries a `piece_count` (a C62 count, agreeing with its title and rising with its price) and every cordless drill a `voltage_v` (unit code VLT), gen#173; more leaves are further rows there, and `tests/test_retail_breadth_34.py` holds that each is a leaf no other template uses), then the furniture (`furniture_rows.py`, gen#199: dining tables by seat count, top outline and top material (a glass top draws translucent, a marble-effect top veined, gen#226) with their sizes in `item_width` and `item_length`, dining chairs sold single or as a set with `units_per_pack`, coffee and side tables, bookcases with their height in `item_height`, wardrobes, chests of drawers and mirrors, each drawn by its own shape in `kit_furniture.py`; no derived style copies one, and `tests/test_retail_furniture_199.py` holds the range and `tests/test_retail_furniture_drawings_226.py` that a White piece draws white), then the styles that
three failure classes need (`distractor_rows.py`; `baseline_rank.py` ranks a build
without a policy, and `tests/test_retail_distractors.py` holds the result): mattress
protectors, mattresses and pillow protectors that out-sell the toppers; bestselling
barrel-leg jeans whose text says balloon; 150 petite styles with a minority on sale,
and 60 sale styles that never say petite, and the steak class (gen#264: seven steak-knife styles, a steak plate, board and cast-iron weight that lead `steak`, each with a material and none derived (gen#268), with the beef steaks and tinned tuna steaks the grocery build adds as families `SKS` to `SKW` and `TUS`), then the shirts (`shirt_rows.py`: Oxford,
Flannel, Linen and Denim, for Mens and Womens, under `Tops/Shirts`, typed `Shirt`;
no derived style copies one), then the living-room seating (`sofa_rows.py`, gen#196:
sofas sold as 2, 2.5, 3 and 4 seaters, left- and right-hand corner and chaise sofas,
modular, recliner and sofa-bed sofas, armchairs and footstools, each drawn by its own
shape in `kit_seating.py`; no derived style copies one, and
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
drawn by `kit_underwear.py`; none is derived), then the toys (`toys_rows.py`, gen#201: building sets, jigsaws, board games, dolls, wooden toys, role play toys, arts and crafts kits and ride-ons, drawn by `kit_toys.py`; every style carries an `age_range` and most a `toy_type`, a jigsaw's finished size is its `item_length` and `item_width` in `CMT` (canonical value in millimeters) beside the `finished_size` text (gen#261), four invented character ranges (`line`) each span several kinds, and a counted mark in the drawing equals the count the record states, `tests/test_retail_toys_201.py`; a toy vehicle or ride-on whose paint is a free choice is sold in ten colors, one SKU and drawing each, a bike or trike in wheel sizes (the `wheel_size` axis, drawn to scale), and a style whose color is its identity (a police car, a taxi, a fire engine, bare wood) keeps one and says why in its `fixed_color`, `tests/test_retail_toy_vehicle_colors_271.py`; no derived style copies one), then the lighting (`lighting_rows.py`, gen#197: floor,
table, desk, ceiling and wall lights and lampshades under `Home/Lighting` (`Lamps`, `Lights`), each typed by
its name; a SKU is a color times a finish, a shade color or a diameter, and its image draws
that SKU's own value), then the bags, umbrellas and jewelry (`accessory_rows.py`,
gen#207; likewise copied by no derived style), then the Sports & Outdoors styles (`sports_rows.py`, gen#265 and gen#368: camping, yoga & fitness, cycling pumps, baseball, swimming, team and racket sports, drawn by `kit_sports.py`, copied by no derived style; leaves, filters and types not built in [docs/retail-sports-tree.md](retail-sports-tree.md), `tests/test_retail_sports_265.py`), then the school uniform styles (`school_rows.py`, gen#205, first increment: school trousers, skirts, pinafores and shirts under `Kids/School Uniform`; drawn by `kit_school.py`, school-age sizes `3-4 Yrs` to `15-16 Yrs`, fit, adjustable waist, style, sleeve and pack as structured attributes, decoys from `decoy_apparel.py`, copied by no derived style, `tests/test_retail_school_205.py`), then the garden machines (`garden_rows.py`, gen#203, first increment: lawn mowers, robot mowers, grass trimmers and barbecues under `Garden`, drawn by `kit_garden.py`, with text-match decoys, [docs/retail-garden.md](retail-garden.md); copied by no derived style), then the garden hoses (`type_specs/garden_hose.py`, gen#292: a reinforced and an expandable hose under `Garden/Watering/Garden Hoses`, drawn by `kit_garden.py`, a SKU axis in metres (`item_length`) and the six main colors, with 15 text-match decoys in `garden_rows.py`, copied by no derived style, `tests/test_retail_garden_292.py`), then the near-white apparel and main-color bras (`colorgroup_rows.py`, gen#302, [docs/retail-color-group.md](retail-color-group.md); copied by no derived style), then the grocery styles (below, `grocery.py`, gen#154). Further styles are
derived from them, deterministically by `--seed`, and a smaller build is a prefix of a larger one.
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
hold. Its price is
re-drawn inside its leaf's band, as a function of the values it changed (a
premium material costs more). A draw whose title or description contradicts an
attribute is refused, and `check_catalog` refuses such text too. The module
docstring has the rules. A description's closure and a style's pattern are held to its attributes ([gen#250](retail-attribute-text.md)). Today's templates run out at `ceiling` in
`golden-retail/stats.json` (with and without the grocery styles), and the CLI exits 2 past that. Raise the ceiling with data: more title-visible
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

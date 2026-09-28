# synthetic-industrial-products

A generated product catalog for the industrial-supply vertical (cutting tools,
fasteners, abrasives, hand tools, bearings), built to exercise structured facet
extraction in search: 10,080 SKUs over 5,403 products in 16 product types,
from 45 invented brands -- and, with one flag, about 100,000 SKUs
([The 100K catalog](#the-100k-catalog)).

**Every product in this repository is synthetic.** No record here describes a
real product offered by any retailer, and no retailer's catalog content is
redistributed.

## Why this exists

Search demos in this vertical need one specific property that is hard to
fabricate convincingly: **attribute-role ambiguity**. The same dimension token
legitimately appears in different roles on one product — a `3/8"` that is the
cutting diameter on one tool and the shank diameter on another. A query for
`3/8 end mill` matches both on full text and should return neither. Proving a
search engine handles that requires a catalog whose dimensions are internally
coherent and whose collisions occur at a realistic rate.

## Provenance

The **schema** and the **statistical distributions** are derived from observing
publicly archived pages of real catalogs: which attribute names the industry
uses, which dimension combinations are physically real, how often roles
collide, how titles are constructed, and how often records are internally
inconsistent. Those are facts about the domain.

The **products** are generated. They are not real records with the names
changed.

That distinction is enforced, not asserted: no generated record may match a
reference record on its full attribute tuple, and the test suite checks it.

The check compares **hashes** of reference attribute tuples, not the tuples.
The corpus still ships nowhere; a hash cannot be read back into a record, but
it is enough to prove the property. The comparison is over the *full* tuple
rather than field by field, and that matters: a generated `#10-32` flat head
cap screw publishes `Head Dia. = 0.411 in`, and so does every real one, because
that is what `ASME B18.3.2` says a `#10` flat head is. Agreeing with a standard
is not copying. Reproducing a compilation is, and a compilation is what a full
attribute tuple describes.

### Where the dimensions come from

Two different answers, and the catalog says which is which on every product
line:

| | |
|---|---|
| **Fasteners** | dimensions are **standards-derived**. Each line carries the standard designation its dimensions came from — `ASME B18.3`, `ASME B18.3.2`, `ASME B18.3.3A`, `ASME B18.3.1G`, `ISO 4762`, `ISO 10642`, `ISO 7380-1`, `DIN 7984`, `ISO 4014`, `ISO 4017`, `DIN 933`, `ISO 7089`. |
| **Newer types** (hex nuts, radial ball bearings, depressed-center wheels, hex keys; elastic/prism-industrial-products#103) | dimensions are **generated** from conventional sizes -- nut widths across flats, the 60/62/63 bearing series boundary sizes, stocked wheel diameters, hex key sizes. They follow the familiar ladders but were not extracted from an open dataset, so the provenance field says "generated" and no standard is claimed. |
| **Cutting tools** | dimensions are **generated** from the conventional series. No open dimensional source for end mills exists, so nothing here claims a standard, and the provenance field says so in words. The metric series carries 11, 15 and 25 mm, which are ordinary stocked sizes and were missing — an artifact of how the list was first written, not a statement about the market. |

That asymmetry is deliberate. A cap screw's head is fixed by a published
standard and a catalog that disagrees with it is wrong; an end mill's length of
cut is a manufacturer's choice within a conventional range.

Fastener dimensions were extracted from open sources rather than transcribed by
hand:

* **[FreeCAD FastenersWB](https://github.com/shaise/FreeCAD_FastenersWB)**
  (GPL-2.0-or-later) — the primary source for every standard used.
* **[BOLTS](https://github.com/boltsparts/boltsparts)** (fastener collections,
  LGPL-2.1+) — corroboration only, and the sole source for DIN 912, which
  FastenersWB does not carry. It was deliberately **not** consulted for
  ISO 10642 (it conflates that standard with DIN 7991) nor for washer inner
  diameter or thickness (it is wrong at M10 and at M42 and above), and
  `profile_hollow.blt` was never opened, since it transcribes a paid EN
  standard.
* **Unified Thread Standard** fine-series pitches (`#10-32` and its siblings)
  appear in no open dimensional dataset; the handful used are transcribed from
  Wikipedia's Unified Thread Standard table (CC BY-SA 4.0). The standard itself
  is ASME B1.1, and each entry is really its own designation — `#10-32` states
  32 threads per inch in the name.

`src/synthetic_industrial_products/data/fastener_standards.json` is that
extraction, unmodified, and carries its own provenance block naming each
repository, its licence and the commit it was read at. Only the sizes this
catalog offers were taken; the upstream compilations are not redistributed.
Values the sources do not carry are recorded as absent rather than filled in —
there is no `#10` hex bolt here, because ASME B18.2.1 hex head screws begin at
1/4", and no `M20` button head, because ISO 7380-1 in the source stops at M16.

The sizes taken are listed in the extraction's own `requested_sizes` block:
`M3 M4 M5 M6 M8 M10 M12 M16 M20` and `#6 #8 #10 1/4 5/16 3/8 7/16 1/2 5/8`.
**`7/16` was added after the reference distributor's own parametric example turned out to
name it** — `hex head cap screw: 7/16-14, 1-3/4" length under head, grade 8
steel, zinc finish` — and every other component of that query already
resolved. It is present in the source for all five inch standards, so nothing
had to be invented: the pitch column gives 14 threads per inch exactly, which
is what makes the designation `7/16-14`, and the offered lengths are the
workbench's own list filtered to the per-size range, which includes
`1 3/4in`.

### Four screw styles, and the three lengths each of them publishes

A shopper's screw query is `<thread size> ( x ) <length> <screw type>` —
`5/16-18 x 3/4 button head cap screw`, `1/4 x 3 1/4 cap screws`. Two things
have to exist in the catalog for that to have a correct answer: the style, and
the length it names.

**The styles.** Four hexagon socket screw lines, each with its own standard in
each system, its own category leaf and its own drawing:

| line | metric | inch | head |
|---|---|---|---|
| `screw_socket_head` | `ISO 4762` | `ASME B18.3` | cylinder |
| `screw_flat_head` | `ISO 10642` | `ASME B18.3.2` | countersunk cone |
| `screw_button_head` | `ISO 7380-1` | `ASME B18.3.3A` | shallow dome |
| `screw_low_head` | `DIN 7984` | `ASME B18.3.1G` | squat cylinder |

**The length.** A screw publishes three of them and they are three different
measurements:

| attribute | what it measures |
|---|---|
| `Length` | the nominal length — measured **over** the head on a countersunk screw and under it on every other style |
| `Length under Head` | the whole shank, head excluded (the census's casing) |
| `Thread Length` | how much of that shank carries thread |

`x 3/4` in the reference distributor's pattern is the second of those. Binding it to
`Thread Length` would return confidently wrong results — a 3/4" screw and a
screw with 3/4" of thread on it are different products — and on a countersunk
screw binding it to `Length` is wrong by a head height. So the attribute is
published rather than approximated by a neighbour, and the drawing dimensions
it: on a flat head socket cap screw the two length dimensions on the elevation
visibly end a head height apart.

## What ships, and what does not

| | |
|---|---|
| **Ships** | the generator, the extracted standards tables, hashes of the reference tuples, and the built catalog itself — checked in at `golden-catalog/`, see [The built catalog is committed](#the-built-catalog-is-committed-in-golden-catalog) |
| **Never ships** | the reference corpus of captured pages, and the rendered drawings — both reproducible, see `.gitignore`. The drawings are rebuilt from the committed catalog into a pinned bundle (`sip-generate images`, see [Images](#images)); `images.jsonl` records each one's sha256, and nothing else about them is committed |

## Contributing

Install both hook types once per clone: `pre-commit install` (the config sets
`default_install_hook_types: [pre-commit, commit-msg]`). The commit-msg hook
(`scripts/check_commit_msg.py`) refuses a message that credits an AI tool or a
bot. Its patterns are the core repository's AI-attribution family, vendored
with the commit it came from, plus this repository's additions. CI runs the
same check over every commit a pull request adds, so a clone without hooks
cannot skip it. Git's `#` help lines are skipped only by the hook, because a recorded
message keeps any `#` line it was given. Messages are folded before matching:
look-alike letters, invisible and bidirectional characters, and a phrase
wrapped across two lines are all caught. The pre-commit hooks run `ruff check` and the whitespace
fixers, which leave `golden-catalog/` alone.

## Generating a catalog

```sh
uv sync
uv run sip-generate build --out out/catalog
uv run sip-generate report                      # the measured-vs-target table only
```

Everything is parameterised, because the point of the catalog is to be dialled
until something breaks:

```sh
uv run sip-generate build --lines 900               # a bigger or smaller catalog (THE size knob)
uv run sip-generate build --sparsity 0.4             # raggeder attribute coverage
uv run sip-generate build --defects 0.0              # a catalog with no contradictions
uv run sip-generate build --seed 7                   # a different catalog
```

The generator is deterministic: one seed produces one catalog, byte for byte.

`--lines` is the ONE size knob. It sets the products of the original twelve
types, and the four newer types (hex nuts, radial ball bearings, depressed
center wheels, hex keys) take a fixed SHARE of it (`new_type_share`,
700/2600 each: the ratio the default catalog was built with), so every type
grows together. There is deliberately no second `--scale` flag.

### The 100K catalog

```sh
uv run sip-generate build --lines 25850 --out out/catalog-100k
uv run sip-generate images --catalog out/catalog-100k --out out/images-100k --archive out/images-100k.tar.gz
```

`--lines 25850` (`config.HUNDRED_K_LINES`) is the value that lands at about
100,000 SKUs. Measured on this commit, in about 22 s:

| type | SKUs | | type | SKUs |
|---|--:|---|---|--:|
| end_mill_square | 9,283 | | washer_flat | 2,699 |
| end_mill_ball | 5,360 | | hammer_ball_pein | 1,947 |
| drill_jobber | 5,333 | | abrasive_flap_disc | 2,437 |
| tap_spiral_point | 3,457 | | nut_hex | 13,349 |
| screw_socket_head | 5,924 | | bearing_radial_ball | 12,269 |
| screw_flat_head | 3,358 | | wheel_depressed_center | 13,114 |
| screw_button_head | 2,398 | | hex_key | 12,984 |
| screw_low_head | 1,961 | | bolt_hex | 4,333 |

**100,206 SKUs over 53,517 products.** Duplicate SKU ids: 0. Same-product
duplicates (the rule below): 0. Every SKU has its own drawing: 100,206
drawings, 207 MB unpacked, a 21.4 MB `images.tar.gz`, every sha256 matching
`images.jsonl`. Every must-stock example is stocked. Two builds of the same
commit are byte-identical (the sha256 of each of the seven output files
compared equal).

The files are far too large to commit (`flat.jsonl` is 266 MB, `nested.jsonl`
146 MB). The industrial demo serves this size from a **pinned release asset**
on elastic/prism-industrial-products, the same pattern as the drawings, and
this repository commits the default-size catalog only.

What moves at 100K, measured against the census targets (`sip-generate
report`), with the default catalog beside it:

| measured property | target | 10K | 100K |
|---|--:|--:|--:|
| shank == cutting diameter | 0.6489 | 0.6433 | 0.6581 |
| length of cut > overall length | 0.0829 | 0.0831 | 0.0815 |
| angle carries a length unit | 0.0469 | 0.0412 | 0.0484 |
| declared system contradicts units | 0.0323 | 0.0316 | 0.0307 |
| unit mixing within one record | 0.0222 | 0.0159 | 0.0165 |
| title dimension token unlabelled | 0.4667 | 0.4674 | 0.4662 |
| title dimension token not the primary | 0.1714 | 0.1112 | 0.1008 |
| attributes per record (mean) | 13.12 | 12.36 | 12.38 |

Drift, stated: the not-the-primary token rate sits below its target because a
title now names a secondary dimension only when the record PUBLISHES it (see
[Brand voice](#brand-voice-titles-and-descriptions)); before that rule it was
0.127 on the default catalog. The flute label spelling is 0.49 `FL`, 0.44
`Flutes`, 0.07 `Fl` at 100K against the census's 0.66 / 0.28 / 0.06: each brand
now spells a label ONE way, so the catalog-wide mix is quantised by brand.

## Brands

Forty-five manufacturers, all invented, in one table (`catalog/brands.py`):
their product families, market weight, house style and title voice.

* **A long tail, not ten equal houses.** Three broad-line houses make
  something in every family; the rest make one to three families. At 100K the
  largest brand carries 9.0% of SKUs and the smallest 0.4%; a test pins both
  ends (at most 10%, at least 0.3%). Ten brands that each made all sixteen
  types would have put ~10,000 SKUs under every brand.
* **Every name is invented, and was checked.** Each name added for the 100K
  catalog was web-searched against real industrial, tool, fastener, abrasive
  and bearing companies and trademarks; names that turned up a real company of
  any kind were dropped.
* **Some names are ordinary words** on purpose (`Vantage Edge`, `Lark &
  Lathe`, `Tall Mast`, `Salt Meadow Works`, `Morrow Anvil`, `Crooked Birch`,
  `Quiet River`, `Plumb Orchard`): a brand filter has to tell a brand from a
  word, and a catalog without such a name never makes it.
* **House style.** Twelve inks and four frame treatments; each brand owns one
  (ink, frame) PAIR, unique across the book and read back by
  `drawing.style.brand_for_house_style`. Within a brand every drawing looks
  the same; between brands, the ink, the paper tint or the frame differ.

## Every SKU is different

**No two SKUs may be identical on (product_type, brand, every attribute),
ignoring the identifier fields (sku, product_id, List Number, image ids and
urls) and the commercial fields (price, stock). Brand counts as a difference,
so the same standard part from two different makers is allowed.**

The generator guarantees it by construction: each (type, brand) draws specs
WITHOUT replacement -- a spec that brand has already stocked is spent, and a
draft SKU carrying it is not made. When a brand has drawn a type's whole spec
space, it stops getting SKUs of that type. Headroom keeps that rare: flat
washers come in five materials (each with the finishes it is really sold in:
only steel is plated, oxided or galvanized), and ball pein hammers in twelve
head weights and four handles. `tests/test_catalog_brands_voice.py` asserts
zero duplicates on the committed catalog and on a fresh 100K build, with a
planted duplicate that goes red. Distinct specs over SKUs, per type, stay at
or above a stated floor at 100K (flat washers 0.70: ISO 7089 fixes nine sizes,
so many makers sell the same washer; hammers 0.94; every other type 0.98+).

## Brand voice: titles and descriptions

A brand's catalog section reads uniformly, and two brands read slightly
differently (`catalog/voice.py`).

* **The title's core is the census structure** -- `<Item>, <key dim> <role>,
  <material>, <coating>, <flutes>...` -- and stays the backbone. A brand's
  template chooses only among census-observed variants (descriptive or terse,
  the brand name first or not, one label spelling per attribute, where a tight
  delimiter falls), and adds words AROUND the core: a qualifier before the
  item (non-factual words only: "Industrial", "Shop", "General Purpose"...) or
  the brand's name, and a trailing pack segment only when the record publishes
  `Package Quantity`.
* **Descriptions** keep the spec clause and add the brand's template: a use
  line true of every product of the type, a family line naming the brand, its
  range and series, a generic benefit of a material or finish the record
  carries, and a pack line with the record's own quantity.
* **No text states what the record cannot back.** Every number in a title or
  description traces to a value the record publishes (the only exceptions are
  records carrying a MODELLED defect -- a length of cut rewritten past the
  overall length, mixed units -- whose title keeps the pre-defect value, the
  realistic variant this catalog exists to exhibit; bounded at 2% and measured
  at 0.6%). A title names a descriptor or secondary dimension only when the
  record publishes it.

Measured, and reported rather than forced: product names are unique within
every type (0 clashes over 53,517 products); SKU titles are 0.72 distinct on
the default catalog and 0.45 at 100K -- identical titles across products are
the same spec from brands whose template omits the brand name, which is how a
marketplace reads; descriptions are 1.00 distinct at both sizes.

### The data model

**A parent is one product. Its children are its purchasable variants (SKUs).**
The shape is core's nested variant model (elastic/prism#9141): today's ungrouped
view serves one document per SKU, and the grouped view will serve one per
product with its variants nested, from the same data.

```
parent    Corvane K663 -- High Speed Steel Square End Mill
          product-CONSTANT attributes: brand, series, material, coating,
          flute count, end type, helix angle
children  the SKUs, varying: milling diameter, length of cut, overall
          length, shank diameter, price, stock -- each with its own drawing
```

**How many variants a product has** is ONE knob, `variants_per_product`: about
half of products are single-SKU and the rest have 2 to 5, skewed small, as on a
marketplace (maintainer, 2026-09-27). A product never offers more variants than
its series has members. Two deliberately awkward cases are built in, so a
grouped view is proven on more than the well-formed shapes: a single variant
that carries **no** variant-scope attribute (`zero_axis_share`), and variants
whose sparsity leaves one without an attribute its siblings carry.

**Attribute names are the census's generic ones.** A concept is one name across
types -- `Material` on an end mill, a drill and a screw alike -- because that is
how the reference census names it (160 of 496 records), and on a nested index
every per-type spelling would be a facet of its own. `catalog/names.py` is the
gate: every name is census-verbatim, on the names-only reference spec-table
list (`reference-statistics/R1_reference_spec_table_names.json`), or a justified
exception. No name may contain the record's OWN product noun, a noun of its
category path, anywhere (`End Mill Material` on an end mill, `Hex Nut Material`
on a nut, `Cap Screw Type` on a screw). The census's own one-record
type-qualified names are refused, not allow-listed. A noun naming a mating or
contained part is allowed, because it is a different measurement: a washer's
`For Bolt Size`, a tap's `Drill Size`, `Insert Screw`. And no name may be a
census name in another casing (`Length Under Head` for `Length under Head`),
since a keyword facet is case-sensitive. It replaced a rule that forced the
vocabularies to be disjoint.

**The newer types spell lengths the way their brand's feed does** -- one brand
`3/8"`, another `3/8 in`, another `0.375"` -- consistent within a brand and
different across brands, the variation between supplier feeds the census
records (maintainer ruling, 2026-09-28). The original twelve keep one spelling.

Attributes are nested key-value at **both** levels, in **one** array rather
than separate keyword and numeric arrays:

```json
{"name": "Milling Dia.", "value": "3/8\"", "value_num": 0.375}
```

A dimension needs both representations on the same entry — a shopper filters on
the published text and ranges over the number — and splitting them into two
arrays loses the fact that they are one attribute. `value_num` is **parsed back
out of** `value` rather than carried beside it, so the two can never disagree:
`3/8"` has no exact two-decimal millimetre spelling, and a number computed from
the original magnitude would quietly differ from the string actually published.
An attribute that is not a measurement omits `value_num` entirely rather than
carrying a null, and so does a measurement whose value is deliberately
malformed — a record publishing `Helix Angle = 42"` has no angle to put there.

Products are never grouped across brands. Two manufacturers' tools at the same
nominal geometry are different products.

#### Three tiers say what makes a SKU different

A shopper meets one product line as a screenful of near-identical cards, and
what separates them has to be legible at three different depths. The source
this catalog is modelled on does exactly this, and the three tiers carry
deliberately overlapping content:

| tier | job | content |
|---|---|---|
| `title` | tell them apart **at a glance** | the one main distinguishing attribute |
| `description` | tell them apart **while scanning** | the distinguishing attributes, with context |
| attribute block | tell them apart **precisely** | every published attribute |

```
sku          69PU63
title        Vantage Edge Hex Head Bolt,7/16-14, 1" L, Grade 8
description  Vantage Edge Hex Head Bolt,7/16-14, 1" L, Grade 8 - 1" Length
             Under Head, 1" Thread Length, 5/8" Width Across Flats, 19/64"
             Head Height, 5/8" Head Dia., Vantage Edge ASMEB18.2.1-32
```

**The description opens with the title verbatim and then continues after a
` - `.** That repetition is the source's own convention rather than something
to tidy away — a marketplace listing repeats its size in the title, in the
variant selector and twice in the specification table, because each tier is
read at a different moment.

Two properties are asserted over the whole catalog, derived from the data
rather than spot-checked:

* **no two SKUs within a product line share a title, and none share a
  description.** Measured before this existed: 176 of 500 lines published a
  title two of their SKUs shared, over 1,214 SKUs, and *all* 500 published one
  description for every SKU under them — the description was the line title,
  which restates the brand, the series and the product type and says nothing
  about the SKU;
* **every title names a value that is that SKU's alone within its line**,
  per attribute rather than per value, since the same string legitimately
  appears on two SKUs in two different roles — and as a VALUE rather than as a
  substring of one, because `…, 1/4-20, …` is not a statement that the screw
  is 1/4" long.

The second is the one that bites, and the two weaker ways of asking it both
leak. Titles carry the brand about a third of the time and their labels in one
of several abbreviations, so on the catalog this replaced, asking only that a
line's titles differ as whole strings left **1,913** SKUs naming nothing of
their own, and a bare substring test left **1,932** — 19 of those passing on a
coincidence rather than on a value.

The coincidence outlives a catalog that has otherwise been repaired, which is
why the distinction is worth a rule rather than a remark: on the first pass at
this work the whole-string and substring counts had both reached zero while the
standalone-token count was still **10**. One of the ten was
`Button Head Socket Cap Screw, 1/4-20, Alloy Steel`, credited with naming a
`Length under Head` of `1/4` — which is the first half of a thread designation
and says nothing about how long the screw is. On the committed catalog all
three counts are zero.

Which attribute is "the" distinguishing one is **derived, not listed per
product type**: it is the attribute published on every SKU of the line, with
pairwise distinct values, whose magnitudes spread furthest. For an end mill
that is the cutting diameter, which its titles already carried — so the
end-mill titles are unchanged, which is the control for the whole rule. For a
screw it is the length, and a screw's thread size is line-constant, which is
why a title built around it read the same on every SKU of the line.

### Two shapes, one catalog

`sip-generate build` writes both serialisations from the same generated
objects, so any difference between what they return is a property of the shape
and not of the data.

| file | shape |
|---|---|
| `nested.jsonl` | parent + nested SKUs + nested key-value attributes. The target shape: the only one in which "how many *products* have this value" is answerable, via `reverse_nested`. |
| `flat.jsonl` | one document per SKU, attributes denormalised. Loadable today. Its attribute array is a plain `object`, so `name` and `value` become two independent multi-valued fields and the correlation between them is lost. |
| `render.jsonl` | the same SKUs in the shape `sip-render batch` already reads, for the per-record dimensioned renderer. The catalog's cards do not use it: every product and variant carries an `image_id` naming its own product line's drawing. |
| `images.jsonl` | one row per image — one per product line — with its product type, the shape it is drawn as, its path under the image base URL at both profiles, and how many products point at it |
| `stats.json` | what was generated, measured against the statistics it reproduces |

Both shapes publish a SKU's own `description` beside its `title`. The line's
title ships too, as `parent_title` — it is what a grouped card will be headed
with — but it is no longer what renders under a SKU's title.

The flat shape also carries a sanitised `facets` object, because `Milling Dia.`
cannot be an Elasticsearch field name — the trailing dot makes it an invalid
path. The three spellings of the measurement-system attribute deliberately
sanitise to three different keys rather than being folded into one: folding
them here would hide the problem a field map exists to solve.

## The built catalog is committed, in `golden-catalog/`

`sip-generate build` is reproducible, but its output is checked in anyway, at
`golden-catalog/`:

| file | |
|---|---|
| `flat.jsonl` | 26.7 MB — 10,080 SKU documents |
| `nested.jsonl` | 14.7 MB — 5,403 products, nested variants and key-value attributes |
| `render.jsonl` | 2.1 MB — the original twelve types' SKUs, for the per-record dimensioned renderer |
| `mapping.flat.json`, `mapping.nested.json` | the Elasticsearch mappings for each shape |
| `images.jsonl` | 3.9 MB — one row per SKU drawing: its path in the bundle, its URL, the sha256 of its bytes |
| `stats.json` | the measured defect rates, and the config that produced them |

About 45 MiB in the working tree. **Plain NDJSON — deliberately not gzipped
and not git-LFS.** The whole reason to commit generated output is that a
change to the generator shows up as a readable diff in review, and both of
those hide it. Records drawn from one naming grammar pack small. Above roughly
30K SKUs a file outgrows what GitHub accepts; the ruling for that size (D5 on
elastic/prism-industrial-products#103) is a pinned release asset, which is how
the industrial demo now serves [the 100K catalog](#the-100k-catalog).

It also means the catalog is inspectable, and citable, without installing the
generator: a reviewer reading a PR, or anyone asking what a record actually
looks like, opens a file rather than running a build.

### Regenerating it

```sh
uv run sip-generate build --out golden-catalog
```

That is the whole command — the default configuration, the default seed. Then
commit whatever changed, `src/prism_synthetic_industrial/data/field_weights/`
included, since the same build regenerates the PRISM field map.

**You are expected to run it in the same commit as any generator change that
moves the output** — a new attribute, a changed distribution, a different image
assignment, a renamed field, a new emitted file. `tests/test_catalog_golden.py`
compares every committed file against a fresh build by sha256 and fails naming
the file and the line counts, so the CI red tells you which one you forgot.

Do **not** regenerate to make that test go green without reading the diff.
Two different things turn it red, and only one of them is fixed by committing:

* **you changed the generator** — expected; regenerate, commit, review the diff;
* **the generator became nondeterministic** — a bug. One seed is supposed to
  produce one catalog, byte for byte.

Tell them apart by building twice into two fresh directories and diffing those
against each other, with no edits in between. Clean means the first; any
difference means the second, and the golden files must not be updated until it
is found. The test's failure message says all of this too, with the commands.

Alongside the hashes, the same test asserts the headline numbers directly
against the committed files — 10,080 SKU documents over 5,403 distinct
`product_id`, a non-empty `image_url` and `image_detail_url` on every product,
variant and flat document, and 5,403 nested products whose variant counts sum
to 10,080. Those hold independently of the generator, so a careless
regenerate-and-commit from a broken build is still red.

## Every requirement example is stocked

The search requirements the catalog is used against come with example
queries, and each one must find a product that exists: an example judged
against an empty result proves nothing about the search. So the generator
carries a **must-stock list** (`catalog/muststock.py`, maintainer ruling on
elastic/prism-industrial-products#103): one entry per requirement example, naming
the product type(s) it may be and the published values a SKU must carry --
`Milling Dia.` `1/2"` with `Length of Cut` `1"`, a `bolt_hex` in `7/16-14`
with `Length under Head` `1-3/4"`, `Grade 8` and `Zinc Plated`, and 22 more.

It runs after the main generation and changes nothing the main generation
drew. For each entry no SKU already satisfies, it builds lines with that
type's own builder -- so titles, names and derived dimensions follow the
same rules as every other line -- from a stream seeded by the entry alone,
until one carries a matching SKU, and adds that line whole, with the 1-5
variants its builder drew. Where the builder's series cannot reach an
example (the end-mill length-of-cut multiples are 1.5x, 3x and 4x, and
`1/2" x 1"` is 2x) the entry pins that one choice for its own lines.
On the committed catalog 19 of the 24 examples were already stocked and 5
lines were added. `tests/test_catalog_must_stock.py` asserts every entry is
stocked, that removing an entry unstocks its example, that the pass moves no
earlier line, and that an entry no builder can reach fails the build.

## Serving it with PRISM

`src/prism_synthetic_industrial/` is a PRISM customization that serves the
**flat** shape. The package name is fixed by PRISM's loader, which globs
`src/prism_*/data/customization.yaml` and requires exactly one match.

Flat, not nested, because the Engine cannot emit nested facet queries today.
That is also what makes this the demo's "before" half: the shopper sees one
product row per SKU.

```sh
# 1. build the catalog and regenerate the field map from it
uv run sip-generate build --out out/catalog

# 2. load the flat shape into a LOCAL TEST cluster
python scripts/load_prism_catalog.py --host http://127.0.0.1:9201

# 3. from a PRISM checkout, with this repo installed (`uv pip install -e <here>`)
PRISM_CUSTOMIZATION_PATH=<this repo> PRISM_RUNTIME_MODE=dev \
  PRISM_ELASTICSEARCH_URL=http://127.0.0.1:9201 \
  uv run prism-engine validate-customization
```

### The field map is derived, never written

The catalog publishes **84 distinct attribute names** across 16 product types.
A hand-maintained list of 84 declarations drifts from the generator the first
time either side moves, and it drifts *silently*: a field map naming an
attribute the catalog no longer publishes does not raise, it just stops
faceting, and "no product has that value" looks exactly like "the field map is
wrong".

So `data/field_weights/synthetic_industrial_flat.yaml` is **generated** from
the emitted documents, as a step of `sip-generate build`, and
`tests/test_prism_field_map_drift.py` fails if the committed file and a fresh
derivation disagree. Editing either side alone reds it; both directions are
planted in `scripts/mutation_check.py`.

### Which attributes become facets

Not all 84. Three measured gates, applied to the emitted documents:

| gate | rule | why |
|---|---|---|
| **discriminating** | at least 2 distinct values | a facet with one value cannot narrow anything — it is a control that does nothing |
| **characteristic** | present on ≥50% of the documents of the product types that publish it *at all* | the denominator is per-attribute: an attribute carried by one of twelve types can never exceed ~10% of the catalog, yet may be the primary facet for its own category |
| **not an identifier** | a **terms** attribute carries ≤25 distinct values | `Dia./Thread Size` is the first thing a shopper filters on; `List Number` publishes 574 values over 1,100 documents and is a part reference nobody browses. Numeric attributes are exempt — a range control's cost does not grow with cardinality |

An attribute is **numeric** (a range facet over `facets_num.*`) when ≥50% of
the documents publishing it carry a parsed `value_num`, and **terms**
otherwise. The catalog deliberately emits values that do not parse, so the
test is a majority rather than "all".

**An attribute whose key is a column's name is namespaced, never dropped.**
Real feeds publish attributes named like a catalog's own columns -- the census
carries `Series` (25 records), `Product Type` (15) and `Brand` (1) as
attributes -- and a bearing's `Series` (`62`) is not its product's `series`
column. So `field_map.canonical_name` gives such an attribute the entry name
`attr_<key>` (here `attr_series`, over `facets.series`) and leaves the
structural entry pointing at the column; a namespaced name that would itself
collide is refused. The nested shape needs none of this: there an attribute is
data, `{name, value}`, not a field name.

Attributes that fail a gate are still **declared**, with `facet: false` — they
stay searchable and stay available as filter and policy targets, they are just
not offered as sidebar controls.

What that yields, measured:

| | |
|---|---|
| attributes declared | 84 |
| **fields in the field map** | **101** (67 faceted terms entries, 26 declared with `facet: false`, and the structural ones) |
| **leaf fields in the Elasticsearch index** | **141** — the 21 the mapping declares, plus one per distinct `facets.*` key (84) and `facets_num.*` key (36) the dynamic templates create |
| facets in a category's sidebar | 8–15 |

The per-category figure is above the five-to-eight a real sidebar carries.
That is honest rather than tuned: a socket screw genuinely publishes five
dimension ranges (head diameter, head height, length, length under head,
thread length) beside material, finish and grade. Trimming to eight would mean dropping a control a shopper
uses, and PRISM has no authorable "top N" — terms facets always aggregate at
1000 and truncation is reported, not configured.

### Proving PRISM actually serves it

A field map that validates is not a served catalog.

```sh
python scripts/verify_prism_serves.py --studio http://127.0.0.1:8477
```

Every number PRISM reports is compared against one computed independently in
Python from the same in-memory catalog objects — the same discipline
`verify_elasticsearch.py` uses, and for the same reason: an aggregation that
agrees with itself proves nothing.

* a search returns products, and every id is a SKU the generator produced
* a terms facet's counts equal the generated counts
* a numeric range facet on a dimension carries the catalog's true min and max,
  and a range filter returns exactly the matching documents
* **every sampled facet count equals what clicking it returns** — a count that
  does not match its click is a blocking defect, not a note
* every product type returns its own documents, in the generated count
* the demo case: `3/8" end mill` returns products whose **shank** carries that
  value, and adding the structured `milling_dia` filter excludes them

### What the flat shape costs

The flat shape's `attributes` array is a plain object, so `name` and `value`
become two independent multi-valued fields. Filtering it for
*name = Shank Dia. AND value = 3/8"* matches **236** documents; only **141**
actually publish a 3/8" shank. The other 95 carry a 3/8" belonging to a
different attribute (counted from `golden-catalog/flat.jsonl`).

That is why the field map facets the sanitised per-attribute `facets.*` /
`facets_num.*` keys, where the pairing cannot come apart, rather than the
`attributes` array. It is also the measurement that argues for the nested
shape: `reverse_nested` answers "how many *products*", and flat cannot.

## Verification

```sh
python scripts/verify_elasticsearch.py --host http://127.0.0.1:9201
```

Loads both shapes into a local test cluster, proves the properties below, and
deletes its indices. **Every number Elasticsearch returns is compared against
one computed independently in Python from the same in-memory objects** — an
aggregation that agrees with itself proves nothing, since a wrong query can
return a self-consistent wrong answer.

* a nested key-value facet count equals what clicking that facet returns
* the multi-valued attribute over-reports without `reverse_nested` and is
  correct with it, with a single-valued attribute as the control
* facet discovery scoped to one product type returns exactly that type's
  attribute names
* a numeric range on the shared `value_num`, scoped by attribute name, is
  correct — and widens when the name filter is dropped
* a full-text query for a dimension token returns products whose **shank**
  carries that value, and the structured attribute filter excludes them
* the flat shape over-matches the same name+value filter, and the nested shape
  does not

```sh
python scripts/mutation_check.py
```

Breaks the code each new test guards, in both directions where a property has
two, and reports any mutation that reds nothing as a zero. Three of the image
mutations came back green the first time they were run and each named a real
gap — a generic drawing that could be swapped for another type's, an attribute
that was validated but not drawn, and a control whose mutation text no longer
matched the code it was supposed to break. All three are fixed rather than
removed; a mutation that reds nothing is the point of running them.

**The harness cannot find the defect the line drawings exist to prevent, and
that is why the tests do not rely on it.** An attribute published on every
record and read by nothing has no code path to plant a defect in, which is how
`End Mill Style` drew 473 ball nose mills square through 39 mutations with no
zeros. What the harness *can* plant is the other half — a channel that reads
its attribute, validates it, and then draws something else — so every marking
mutation is that shape, and the coverage question is answered from the data
side instead, in `tests/test_derivation.py` (the dimensioned renderer) and
`tests/test_sku_drawings.py` (the catalog's own drawings).

Two of the harness's own defects surfaced while the marking mutations were
added, both of which manufacture a false "not caught": a selector's `-k` filter
was split on whitespace, so `-k "x or y"` reached pytest as three arguments and
a stray quote; and a selector naming two files with a `-k` each silently kept
only the last filter, running one file with a filter that matched nothing in
it. The selector is parsed with `shlex` now, and the two-filter shape raises.

## Images

**One drawing per SKU, drawn from that SKU's own values, with no text in it.**
The rulings are on elastic/prism-industrial-products#103 (2026-09-26 to -28):

* **One image per SKU**, so two lengths of one screw look different, and a
  grouped view can switch the picture when a variant is selected.
* **No text of any kind** -- no dimension, callout, label, brand name or SKU.
  The words are on the record (title, description, attributes); the drawing
  reflects the specifications **visually**: a longer length of cut is drawn
  longer, a finer thread with more crests, a flat head is a cone and a button
  head a dome, a sealed bearing is closed and an open one shows its balls.
  The gate is an **allow-list**, not a list of text forms
  (`drawing.svg_problems`):
  - every element must be one the figures emit (`svg, rect, defs, pattern, g,
    path, circle`), and there is no nested `<svg>`;
  - every attribute must be one they use, and every attribute VALUE must fit
    its grammar: a paint is a colour, `none` or a same-file hatch reference,
    never an external or `data:` URL;
  - every id is a hatch pattern's own;
  - no element may carry character data;
  - no comment, processing instruction, doctype or entity reference may
    appear.

  One thing no structural check can catch: a glyph's outline drawn as a plain
  path is indistinguishable from any other outline. The review's plants
  -- `<title>`, `<desc>`, `aria-label`, a comment, `<metadata>`,
  `<foreignObject>`, an embedded raster, `@font-face`, a glyph path from any
  font -- each red `tests/test_sku_drawings.py`.
* **Brands visibly different**, by house style: each brand owns one (ink,
  frame) pair -- twelve inks, four frame treatments, a faint paper tone of the
  ink -- consistent within a brand, never random per product ([Brands](#brands)).
* **Finish and material** are the part's fill (the finish's colour, else the
  bare material's) and its section hatch.
* **Small SVG**, written directly rather than through a figure library:
  measured on the committed catalog, 10,080 drawings, 21.1 MB unpacked
  (2.09 KB a drawing on average), and a 2.23 MB `images.tar.gz`. Every root
  declares `width="200" height="300"` beside its viewBox: an `<img>` sized only
  by max-width/max-height in a flex item that does not grow renders a
  viewBox-only SVG at 0 x 0.

The drawing is a pure function of `(product type, brand, published attributes)`
(`src/synthetic_industrial_products/drawing/`). It reads the SKU's geometry
through the same `geometry_from_record` functions the dimensioned renderer in
`render/` uses, so the two cannot disagree about what a record says.

**Sizes are visible.** The scale is one constant per product type: sheet units
per inch are the usable sheet over the type's largest drawn extent, declared
per type in `drawing/figures.py`. There is no exception to it: a part too
small to read is not drawn larger, it is shown through a **magnifier**
(maintainer ruling on elastic/prism-industrial-products#103, 2026-09-28):

* a part is **too small to see** when it is drawn at most 1/5 of the sheet's
  width (40 units) AND at most 1/6 of its height (50), and such a part ALWAYS
  gets a lens (the refined ruling of 2026-09-28, with the edge cases settled at
  1/5 wide so socket screws drawn just over 1/6 are lensed); every other part
  is drawn plain, centred;
* the lensed part is drawn at its type's scale near the bottom of the sheet,
  horizontally centred, with no circle around it, and the lens above it shows
  the same figure enlarged so its bounding box's diagonal spans 92% of the lens;
* the lens is a magnifying glass in the icon's shape (a ring, a thin shaft and a
  grip twice the shaft's width, round caps, the handle at 45 degrees to the
  bottom-right), stroked at 35% of the icon's weight in the brand's ink, when
  that glass enlarges the part at least 2.5 times; otherwise it is a larger
  HANDLE-LESS lens -- the same thin ring and white interior -- sized to the
  sheet's width at an 8-unit side margin (the smallest that clears every brand
  frame by at least a unit). That lens is WIDTH-BOUND, so it cannot grow further:
  at the rule's extreme (a part drawn 40 x 50) it enlarges only ~x2.42, below
  the x2.5 the handled glass guarantees;
* the whole glyph is horizontally centred and as large as fits; the space above
  it equals the space below the part, with a 14-unit gap between them;
* no outline is thinner than 2.3 sheet units (~2 px on a 180 px-wide
  thumbnail), so a hairline part -- a 1/16" drill is under one unit wide at its
  type's scale -- is visible with or without a lens. Interior detail lines
  (flutes, threads, hatch) are texture and keep their finer weight.

On the committed catalog 1,284 SKUs are too small to see: 162 get the handled
glass (x2.53 to x3.77) and 1,122 the handle-less lens (x2.53 to x4.03). The
lowest enlargement any committed lens gives is x2.53; no committed part reaches
the rule's 40 x 50 extreme. No drawing
carries text; the magnifier adds only paths and circles, and
`stroke-linecap="round"` to the allow-list.

What `tests/test_sku_drawings.py` proves over the committed catalog:

* **One scale per type.** Every product is drawn at its type's scale, so any
  two parts of a type are in true proportion, and a head, a thread or a bore
  siblings share is drawn identically on each (measured on the true-scale
  part of every drawing: screws' heads and bearings' outer rings).
* **The magnifier:**
  * a lens appears on exactly the SKUs drawn at most 1/5 of the sheet's width
    and 1/6 of its height, over every committed SKU;
  * the handle-less lens is used exactly where the handled glass cannot reach
    x2.5; the committed catalog's lowest enlargement is pinned at x2.52 (its
    measured minimum, rounded down), and the rule's extreme (40 x 50) at
    x2.41 to x2.5 -- below x2.5 because the lens is width-bound;
  * the handle-less lens clears the brand frame (8 units in, frames at 6 with
    strokes at most 2 wide);
  * each dimension binds on its own (planted: 41 x 5 and 5 x 50.5 plain,
    39 x 5 and 5 x 49 lensed); long thin parts never get a lens;
  * the lens shows the same part: the same shapes, scaled about the two
    centres by the layout's enlargement, and inside the lens;
  * the space above the glyph equals the space below the part, the gap is
    14 units, and the glyph and the part are centred, for both kinds of lens;
  * the ring, shaft and grip are in the brand's ink; the handle-less lens has no
    shaft or grip;
  * no outline, glyph stroke included, is thinner than 2.3 units (the hairline
    drill 93TD57, under two units wide, is pinned).
* **Other properties:**
  * no product exceeds its type's extent;
  * no drawing leaves its sheet;
  * no two siblings draw alike unless they differ only in values no figure
    draws.

An M3 washer's true-scale drawing is exactly 7/30 of an M16's diameter.

A record whose geometry cannot be read as published -- an attribute absent, a
value that does not parse, a pair that contradicts itself -- is drawn with its
kind's **nominal** proportions for the missing or conflicting values, and
`images.jsonl` says so per SKU (`geometry`: `record`, `partial` or `nominal`).
A drawing with no text states no number, so a nominal proportion cannot
contradict a published value; a consistent published value always wins.
`tests/test_sku_drawings.py` asserts the parts that are drawn from the record
are drawn to exactly its published length.

### Where a record points, and the bundle

Every SKU's `image_id` is `<product type>/<product id>/<sku>`; its `image_url`
is `/images/industrial/<image_id>.svg`, and `image_detail_url` names the same
file (one SVG serves both views). A product shows its first variant's drawing.
The URL is relative on purpose: the demo serves the bundle's folder itself
(elastic/prism#9770), and nothing points at a third-party host.

```sh
uv run sip-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz
```

rebuilds every drawing from the **committed** catalog, refuses unless each one's
sha256 equals the one `images.jsonl` records, and writes the files and a
deterministic archive (sorted members, zeroed times and owners, a gzip header
without a timestamp).

**Layout.** Every member is `industrial/<type>/<product>/<sku>.svg`: the
archive carries its own top-level `industrial/` folder, so a customization
unpacks it into its images folder, the demo serves that folder at `/images`
(elastic/prism#9770), and `image_url` -- `/images/industrial/...` -- resolves
with no per-deployment mount. A test pins that every member is exactly its
`image_url` under `/images`.

**The pin is of the content, not the compressed bytes.** gzip output depends on
the zlib build, so the archive's own sha256 is only stable on one toolchain.
What a customization pins is the **content digest**: the sha256 of the sorted
`<member path>\t<file sha256>` lines, printed by `sip-generate images` and
written beside the archive as `.content-sha256`. It is derivable from the
committed `images.jsonl` alone (`bundle.manifest_digest`), and the installer
recomputes it after unpacking. `out/` is ignored by git, and a test asserts it,
so a drawing can never be committed here.

```sh
uv run python scripts/contact_sheet.py --catalog golden-catalog --out out/contact-sheets
```

writes an HTML contact sheet of real catalog SKUs -- one screw across its
lengths for two brands, flat washers across sizes, materials and brands, and
twenty SKUs of every type -- for judging the drawings by eye.

### The older renderers in `render/`

`render/` still holds the matplotlib renderers: the twelve type drawings, the
per-line marking, and the per-record **dimensioned** drawings (`sip-render`).
They carry text -- callouts and stamps -- and the catalog no longer uses any of
them; their geometry parsing is what the catalog's drawings read. Retiring them
-- extracting the shared geometry first -- is #27.

## Realism

The generator reproduces the defect classes found in real catalogs rather than
smoothing them away: inconsistent unit formatting within a single record,
ragged attribute coverage, and occasional internally impossible dimensions.
A catalog where every field is populated and every value is well-formed does
not look like a real one, and does not exercise a search engine like one.

Each rate is measured, and each defect class is reproduced against **its own
denominator** — the records that actually carry the attribute pair it needs,
which is how the source statistics measure them. `sip-generate report` prints
the achieved figures beside their targets, so the claim is checkable rather
than asserted.

| property | target | achieved |
|---|---|---|
| shank diameter == cutting diameter | 0.6489 | 0.6612 |
| length of cut > overall length | 0.0829 | 0.0886 |
| an angle attribute carrying a length unit | 0.0469 | 0.0412 |
| declared measurement system contradicts the value's units | 0.0323 | 0.0319 |
| unit mixing within one record | 0.0222 | 0.0159 |
| title dimension token carries no label | 0.4667 | 0.4672 |
| title dimension token is not the primary dimension | 0.1714 | 0.1028 |
| title label truncated at the length cap | 0.0323 | **0.0000, deliberately** |
| image reference missing | 0.1089 | **0.0000, deliberately** |
| image id is shared, not the product's own | 0.7353 | **0.0000, deliberately** |
| attributes per record (mean) | 13.12 | 12.2914 |

Two notes on reading that table honestly. The angle defect is **clustered**:
the attribute is line-constant, so one bad row reaches every SKU under that
line — which is how these arrive in a real catalog, and is visible in the
source corpus too, where the same wrong value repeats across a whole series.
Its per-record rate therefore swings much more between seeds than the others.
And attributes per record sits about 6% below its target because the
reference mean is over a different mixture of product families than this
catalog contains; the per-family shape is reproduced, the mixture is not the
same one. It moved when the newer types arrived (hex nuts and hex keys publish
fewer attributes than end mills), which is the mixture changing rather than
any per-family rate doing so. For the same reason the "not the primary
dimension" title rate sits below its target: the newer types publish no
secondary dimension a title could name instead of the primary one.

The two image rows are **deliberate deviations, not misses**, and the target
column shows what this catalog aims at rather than what the corpus measures —
printing the corpus figure there would show a permanent, meaningless shortfall.
The corpus measures 10.89% of records carrying no parseable image reference;
this catalog gives every product and every variant one, because it is used as a
demo and a product with no image reads there as a broken page rather than as
realism about supplier data. The corpus measures 73.5% of references pointing
at an image that is not the product's own; this catalog deviates the other
way, because every SKU carries a drawing of its own (a generated drawing costs
nothing per size, and a variant's picture should show that variant). Both measured figures are kept in `GeneratorConfig` as
`measured_image_missing` and `measured_image_sku_diverges`, and a test sets the
missing-image rate back and checks the behaviour returns, so the deviation has
not quietly become a limitation.

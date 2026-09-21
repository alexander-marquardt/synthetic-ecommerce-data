# synthetic-industrial-products

A generated product catalog for the industrial-supply vertical (cutting tools,
fasteners), built to exercise structured facet extraction in search.

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
**`7/16` was added after the customer's own parametric example turned out to
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
| `Length Under Head` | the whole shank, head excluded |
| `Thread Length` | how much of that shank carries thread |

`x 3/4` in the customer's pattern is the second of those. Binding it to
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
| **Never ships** | the reference corpus of captured pages, and the rendered images — both reproducible, see `.gitignore`. The images are about a thousand PNGs and 15 MiB published, so hosting them is a copy, not a build |

## Generating a catalog

```sh
uv sync
uv run sip-generate build --out out/catalog
uv run sip-generate report                      # the measured-vs-target table only
```

Everything is parameterised, because the point of the catalog is to be dialled
until something breaks:

```sh
uv run sip-generate build --lines 900 --skus 6 24    # more, wider product lines
uv run sip-generate build --sparsity 0.4             # raggeder attribute coverage
uv run sip-generate build --defects 0.0              # a catalog with no contradictions
uv run sip-generate build --seed 7                   # a different catalog
```

The generator is deterministic: one seed produces one catalog, byte for byte.

### The data model

**A parent is one manufacturer's product line. Its children are the individual
purchasable SKUs.**

```
parent    Corvane K663 -- High Speed Steel Square End Mill
          line-CONSTANT attributes: brand, series, material, coating,
          flute count, end type, helix angle
children  the SKUs, varying: milling diameter, length of cut, overall
          length, shank diameter, price, stock
```

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

Lines are never grouped across brands. Two manufacturers' tools at the same
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
`Length Under Head` of `1/4` — which is the first half of a thread designation
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
| `flat.jsonl` | 13.6 MB — 4,689 SKU documents |
| `nested.jsonl` | 5.3 MB — 500 product lines, nested variants and key-value attributes |
| `render.jsonl` | 2.0 MB — the same 4,689 SKUs for the per-record dimensioned renderer |
| `mapping.flat.json`, `mapping.nested.json` | the Elasticsearch mappings for each shape |
| `images.jsonl` | the 500 drawings — one per product line — and how many products point at each |
| `stats.json` | the measured defect rates, and the config that produced them |

20.2 MiB in the working tree. **Plain NDJSON — deliberately not gzipped and
not git-LFS.** The whole reason to commit generated output is that a change to
the generator shows up as a readable diff in review, and both of those hide it.
The cost is small: the seven blobs occupy **906 KiB in the pack** (measured
with `git cat-file --batch-check='%(objectsize:disk)'` after a `git gc`), a
21× saving, because records drawn from one naming grammar share most of their
bytes. `flat.jsonl` alone is 12.1 MiB stored in 549 KiB.

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
against the committed files — 4,689 SKU documents over 500 distinct
`product_id`, a non-empty `image_url` and `image_detail_url` on every product
line, variant and flat document, and 500 nested lines whose variant counts sum
to 4,689. Those hold independently of the generator, so a careless
regenerate-and-commit from a broken build is still red.

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

The catalog publishes **77 distinct attribute names** across 12 product types.
A hand-maintained list of 77 declarations drifts from the generator the first
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

Not all 77. Three measured gates, applied to the emitted documents:

| gate | rule | why |
|---|---|---|
| **discriminating** | at least 2 distinct values | a facet with one value cannot narrow anything — it is a control that does nothing |
| **characteristic** | present on ≥50% of the documents of the product types that publish it *at all* | the denominator is per-attribute: an attribute carried by one of twelve types can never exceed ~10% of the catalog, yet may be the primary facet for its own category |
| **not an identifier** | a **terms** attribute carries ≤25 distinct values | `Thread Size` publishes 19 values over 331 documents and is the first thing a shopper filters on; `List Number` publishes 110 and is a part reference nobody browses. Numeric attributes are exempt — a range control's cost does not grow with cardinality |

An attribute is **numeric** (a range facet over `facets_num.*`) when ≥50% of
the documents publishing it carry a parsed `value_num`, and **terms**
otherwise. The catalog deliberately emits values that do not parse, so the
test is a majority rather than "all".

Attributes that fail a gate are still **declared**, with `facet: false` — they
stay searchable and stay available as filter and policy targets, they are just
not offered as sidebar controls.

What that yields, measured:

| | |
|---|---|
| attributes declared | 77 |
| offered as facets | 58 (27 numeric ranges, 31 terms) |
| declared, not faceted | 19 |
| **fields in the field map** | **93** |
| **leaf fields in the Elasticsearch index** | **126** — the 20 the mapping declares, plus one per distinct `facets.*` key (77) and `facets_num.*` key (29) the dynamic templates create |
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
* all 12 product types return their own documents, in the generated count
* the demo case: `3/8" end mill` returns products whose **shank** carries that
  value, and adding the structured `milling_dia` filter excludes them

### What the flat shape costs

The flat shape's `attributes` array is a plain object, so `name` and `value`
become two independent multi-valued fields. Filtering it for
*name = Shank Dia. AND value = 3/8"* matches **87** documents; only **51**
actually publish a 3/8" shank. The other 36 carry a 3/8" belonging to a
different attribute.

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
side instead, in `tests/test_line_drawings.py`.

Two of the harness's own defects surfaced while the marking mutations were
added, both of which manufacture a false "not caught": a selector's `-k` filter
was split on whitespace, so `-k "x or y"` reached pytest as three arguments and
a stray quote; and a selector naming two files with a `-k` each silently kept
only the last filter, running one file with a filter that matched nothing in
it. The selector is parsed with `shlex` now, and the two-filter shape raises.

## Images

**Every product and every variant has an image, and there is one image per
product line** — about 500 of them, each shared by that line's 4 to 20 SKUs.
That is not a cheap approximation of what a catalog does; it is what a catalog
does. A category listing of four end mills from one manufacturer's series at
1/2, 3/8, 1/4 and 1/8 inch shows the same photograph four times, and 73.5% of
the archived reference records point at an image whose id is not the product's
own. A distributor does not photograph every length of the same screw.

Per-SKU images would undercut the variant-grouping story the nested shape
exists to demonstrate, where N SKUs are *one* product. One image per product
type, which is what this replaced — ten of them then, twelve now — went too far
the other way: an
Osterlund K663 HSS AlTiN mill and a competitor's carbide TiCN mill rendered
identically.

| behind one drawing | lines | variants |
|---|---|---|
| `end_mill_square` | 95 | 759 |
| `screw_socket_head` | 60 | 693 |
| `end_mill_ball` | 55 | 413 |
| `drill_jobber` | 55 | 592 |
| `bolt_hex` | 45 | 496 |
| `tap_spiral_point` | 35 | 331 |
| `screw_flat_head` | 35 | 390 |
| `washer_flat` | 30 | 236 |
| `screw_button_head` | 25 | 291 |
| `abrasive_flap_disc` | 25 | 144 |
| `screw_low_head` | 20 | 203 |
| `hammer_ball_pein` | 20 | 148 |

### The drawing is the record, drawn

There are only **twelve shapes**, one per product type. What differs between
two lines of one type is the *marking*, and **every visual channel is a
function of a published attribute** — never of the product id, the SKU or the
series.

Twelve rather than ten because the catalog gained two screw styles whose heads
really are different shapes: a button head is a dome and a low head socket cap
screw is a squat cylinder, and neither is a socket head cap screw drawn
smaller. A style that drew as another style's picture is the `Screw Head Type`
defect over again — `Socket` and `Hex` once produced the same picture, and 524
hex bolts were drawn with round heads.

| channel | driven by | why this pairing |
|---|---|---|
| outline colour | `brand` | what colour does in real catalogs; ten hues stay legible, and the map is invertible so the brand reads back off the page |
| fill tint | the coating/finish attribute, under any of its four spellings | physically true — TiAlN is violet-grey, TiN gold, black oxide dark, bright steel silver |
| section hatch | the material attribute, under any of its six spellings | engineering drawings already denote material by hatch |
| flutes drawn | `Number of Flutes` | not styling: a 3-flute tap genuinely differs from a 2-flute, and the count is what a reader counts |
| flute and thread hand | the direction attribute, under any of its three spellings | a left-hand tool is a different product |
| specification stamp | **every** published attribute, verbatim | a spec-sheet convention, and the record's own text |

**Rotation and tilt were considered and rejected.** They map to no product
property, so they would add variance that asserts nothing — and a reader who
sees two mills drawn differently concludes the difference is real. Driven by
the record, that conclusion is correct.

The stamp is what carries the *ragged tail*. The attribute sets are ragged by
design — one line publishes `Tap Material`, another `Tap Finish`, another
neither — and an encoding built from the attributes common to a product type
collapses to almost nothing: measured, it manufactures about 226 false
collisions. Five geometric channels are also simply finite; brand, finish,
material, flutes and standards alone leave 27 of the 500 lines colliding. The
stamp closes that gap with the record's own text.

**498 of 500 lines get a drawing of their own.** The two that do not are flat
washers — two pairs of lines, each pair publishing identical attribute sets —
and a flat washer is genuinely almost nothing but dimensions, so drawing them
alike is the correct answer, not a failure of the encoding. `tests/test_line_drawings.py` asserts that
number exactly, in both directions: lines that draw alike publish alike, and
lines that publish alike draw alike.

### What no drawing carries

**No dimension, no callout, no number read off a size, and no SKU.** Every
channel reads a `line`-scope attribute, constant over the whole line. A line's
SKUs span a median 5.5x range of sizes, so a drawing that stated a size would
be wrong for most of the line it stands behind. The sizes are on the record and
render beside the image, where they are the record's own values — so a drawing
here cannot contradict the record it appears against, structurally rather than
by anyone remembering to check.

```sh
uv sync
uv run sip-render generics --out out              # the twelve SHAPES, unmarked
python scripts/render_catalog.py out/catalog --out out/images
```

A thousand files — 500 drawings at two profiles — and about 15 MiB published
after compression (median 6.9 KiB a card, 24.3 KiB a detail sheet).
`scripts/render_catalog.py` also audits the result in three directions: every
product and variant must reference a file that exists **and is not empty**,
every file written must be referenced by something, and the number of lines
that share a drawing is reported per product type. The first failing is a
broken image on a demo page, the second is dead weight in the repository that
hosts them, and the third is variety quietly disappearing; none shows up in a
count of files.

### The per-record dimensioned drawings

A second renderer draws **one record to scale from that record's own attribute
values**, with every dimension on the page restating a value the record
publishes. It is not what the catalog's cards use — a dimensioned drawing per
SKU is both more expensive and less faithful than a shared one — but it is the
right thing for a detail view of a handful of demo products, where the point
being made is that cutting diameter and shank diameter are different
measurements.

```sh
uv run sip-render fixtures --out out              # every bundled record
uv run sip-render sku 26VW40 --profile card --out out
uv run sip-render batch out/catalog/render.jsonl --out out
```

**Some records cannot be drawn to scale, and that is the renderer working.** It
refuses a record whose dimensions are missing or contradict each other rather
than defaulting a value, so the share it refuses tracks the sparsity and defect
rates the catalog reproduces. A run that drew 100% of this catalog *to scale*
would mean the renderer had started inventing numbers. Measured over the
default 500-line catalog:

| product type | variants | drawn to scale | |
|---|---|---|---|
| `bolt_hex` | 471 | 100% | |
| `screw_button_head` | 294 | 100% | |
| `screw_flat_head` | 370 | 100% | |
| `screw_low_head` | 190 | 100% | |
| `screw_socket_head` | 702 | 100% | |
| `washer_flat` | 247 | 100% | ISO 7089 publishes all three dimensions on every size |
| `abrasive_flap_disc` | 147 | 90% | `Disc Dia.` sometimes published without a unit |
| `end_mill_ball` | 445 | 65% | |
| `end_mill_square` | 748 | 65% | |
| `tap_spiral_point` | 292 | 43% | |
| `drill_jobber` | 632 | 24% | `Shank Dia.` is published on 43% of them |
| `hammer_ball_pein` | 151 | 0% | see below |
| **all** | **4,689** | **73.7%** | 890 missing an attribute, 171 self-contradictory, 151 hammers, 21 unreadable |

Every row of that table moved with the 2026-09-21 regeneration and none of
them had been re-measured: it read 4,662 variants at 71%, with the five
fastener types between 97% and 100%. **The five fasteners are now all 100%**,
and the reason is the regeneration itself — one spelling per magnitude left no
dimension the parser cannot read, so `DimensionParseError` fell from 181 to 21
and the refusals that remain are absences and contradictions rather than
spellings. The figures above are measured on the committed `render.jsonl`
through the production `draw_record`.

A record the dimensioned renderer refuses falls back to its generic drawing, so
a refusal costs the scale, never the image.

**A ball pein hammer gets no dimensioned drawing at all, and that is the
correct outcome rather than a gap.** A hammer record publishes a head weight,
an overall length, a face diameter and a handle length. Every view of a hammer
needs an extent none of those gives: the side elevation needs the head's length
along its own axis, and the face view needs the width of the handle. Deriving a
head length from the weight would mean assuming a shape and a density, which is
a different thing from the countersink angle a cap screw's three published
lengths determine by trigonometry. `render/hammer.py` says so at length, where
anyone looking for the hammer renderer will find it.

### Where the images are published, and how a record points at one

`sip-generate build` writes `images.jsonl` — one row per image, with its
product type, the shape it is drawn as and the URLs it is served from at both
profiles — and every record in `flat.jsonl` and `nested.jsonl` carries
`image_url` beside `image_id`:

```json
{"sku": "60EX58", "product_type": "end_mill_square",
 "image_id": "end_mill_square/OST-K663-0001",
 "image_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/OST-K663-0001/card.png",
 "image_detail_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/OST-K663-0001/detail.png"}
```

`--image-base-url` moves the host.

**One directory per product type, one per product line inside it, one file per
profile inside that.** The product type is the category: the published tree is
an index of types, and under each one the lines it holds. The image id already
reads `<product type>/<product id>`, so `emit.image_path()` appends the profile
and validates — it does not look the directory up. A second table mapping ids
to directories is exactly how a record's URL and the manifest's path would come
to disagree, which is the defect `images.jsonl` exists to prevent. An id that
is not of that shape, or whose first segment is not a product type, raises
instead of being filed under a guessed category that would silently move later.

**The URL is built from the image id, never from the product's own SKU.** The
two are never the same — a whole line shares one drawing — so a URL assembled
from `sku` is a dead link for every product in the catalog, and dead in a way
that spot-checking a handful of records will not reveal because every record
looks equally plausible. An image id naming no product line raises rather than
publishing a URL that cannot be fetched: a bare id does not claim to resolve,
and a URL does.

`images.jsonl` exists so that whatever hosts the files reads the paths off the
generator's own output instead of re-deriving them with a second copy of the
naming rule, which is how the two would come to disagree.

Two profiles, both sized from where the image is displayed:

| profile | pixels | why |
|---|---|---|
| `card` | 600 × 880 | the catalog card's 150 × 220 box at 4× for high-density displays |
| `detail` | 1400 × 1400 | the detail view's 350 × 350 square box at 4× |

Tools are drawn standing up, shank above and cutting end below. That is how
the industry draws them, and it is the only orientation in which a long thin
tool fills a portrait card instead of floating in the middle of it.

### Publishing them, and the gate that couples the two

A regeneration mints new product ids, so new image ids, so a new set of URLs —
and the previous generation's files keep resolving while not one record points
at them any more. Publishing is therefore **part of a regeneration, not a
separate errand**, and the order matters:

```sh
# 1. render every line at both profiles, from the committed catalog
uv run python scripts/render_catalog.py golden-catalog --out out/images

# 2. publish, from a checkout of the asset host
python3 scripts/import_industrial_images.py \
    --manifest <this repo>/golden-catalog/images.jsonl \
    --images   <this repo>/out/images
# then commit and push; the host deploys from `main`

# 3. only now land the catalog
uv run python scripts/verify_published_assets.py
```

`scripts/verify_published_assets.py` is step 3's gate and it runs in CI. It
compares the **whole** set of files `images.jsonl` publishes against the file
list of the host repository, fetched in one git-trees request, and exits
non-zero if any referenced file is absent. A regeneration PR stays red until
its drawings are live.

**That coupling did not exist, and its absence shipped.** The 2026-09-21
regeneration went green with 499 of its 500 image ids dead on the host —
4,680 of 4,689 products rendering a broken image placeholder — because every
check on either side of the seam was looking at its own half. `render_catalog.py`
audits the files a render run just wrote, which says nothing about what is
published; the host's tests audit the site build, which says nothing about what
the catalog references.

**And the cheap version of this check would have passed it.** One image per
product type is the obvious sample, and the one id that survived the
regeneration was an `end_mill_square` — the first type a sampler reaches. It
would have reported `end_mill_square` healthy and eleven types dead, against a
truth of 499 ids dead out of 500. So the check is a set comparison, and
`tests/test_published_asset_gate.py` reconstructs that exact state and shows
the sample passing it while the set comparison fails.

Two things the gate deliberately does **not** do:

* **It does not fail on hosted files nothing references.** Earlier generations
  are kept on the host on purpose: the documented rollback for a catalog change
  is to revert it, which re-binds the previous generation's index, and those
  records point at those files. Pruning them would trade one broken demo for
  another.
* **It does not sweep the URLs over HTTP by default.** The host is GitHub Pages
  behind a CDN and it answers a concurrent sweep with 404s for files that
  exist: measured, a 16-way `HEAD` sweep of these 1,000 URLs returned 998 404s
  and 2 200s against a host that was *already* serving every file present, and
  fetching the same URLs one at a time agreed with the repository listing
  exactly. A prober that was believed would report a catastrophe on a healthy
  host. `--probe-http` keeps the serialised version for confirming a publish by
  hand.

### What the renderer will not do

The drawing may only contain numbers the record contains, so:

* A value that cannot be read **raises**. There is no fallback dimension,
  because a defaulted dimension produces a drawing that disagrees with its own
  record and nothing downstream can tell.
* A record whose dimensions contradict each other — a length of cut longer
  than the tool — is **refused** rather than drawn. The defect stays in the
  data; silently clamping it would draw a tool that exists and publish a record
  saying otherwise, and the picture would then look like corroboration.
* Geometry that no attribute implies is **left out**, not invented. The depth
  of a socket drive is not published, so the drawing shows the opening the
  socket makes in the head's top face and its true across-flats shape in the
  end view, and stops there. A Torx or cross recess is not drawn at all: one
  across-size does not determine a lobed shape. A tap's drive square is not
  drawn on the elevation, because neither its across-flats nor its length
  follows from any attribute. A flap disc gets no edge view, because no record
  publishes a thickness.
* A **form the record leaves open** sends the record to its generic drawing
  rather than to a guess. `End Mill Style` decides whether the cutting end is
  square or a ball nose and is required; the four observed reference end mills
  do not carry it and are therefore no longer drawn to scale.

Some numbers that look like table lookups are not: the countersink angle of
the reference cap screw is computed from its head diameter, head height and
thread size, and lands on 82°, which is what the inch flat-head standard
specifies. The minor diameter of its thread comes from the 60° thread form and
lands on the published 0.1517". Those agreements are checks on the attributes,
not values borrowed from elsewhere.

### Every attribute has to reach the drawing, or say why it cannot

`End Mill Style` was published on every generated end mill and read by nothing,
so all 486 ball nose mills were drawn with a square end — a picture
contradicting its own record. The suite had 39 mutations and no zeros at the
time, and could not have caught it: **mutation testing can only mutate code
that exists**, and an attribute nobody consumes has no code path to plant a
defect in.

The check that finds that class of defect starts from the record instead. For
every attribute a record publishes, changing it must change the rendered
output — or the attribute must be named in `render/attrs.py`'s `NOT_DRAWN`
with the reason a drawing cannot show it. Both directions are asserted: an
attribute that is neither read nor declared fails, and an attribute declared
not-drawn that *does* move the output fails too, so the declarations cannot go
stale. The sweep runs over a generated catalog's richest record of each product
type as well as over the bundled fixtures, which makes it a statement about the
vocabulary rather than about eighteen hand-picked records.

Seven attributes are declared: the measurement-system attribute under all three
of its spellings, `Standards`, `List Number`, `End Mill Application` and
`Material Grade - Machining`. `Length Under Head` is not among them: it is a
dimension LINE on the elevation, spanning the shank the record says is under
the head, and not only a row in the attribute table — a printed value makes no
claim the drawing could contradict, and a span does. A standard a product conforms to and a use it is
sold for are not shapes, and a drawing of the product has nothing to show for
them.

One subtlety the mutation harness found rather than the design: changing an
attribute to something unreadable and watching the renderer *refuse* is not
proof that the drawing uses it, because a renderer that validates a value and
then ignores it refuses just the same. So the check tries valid alternatives
first and falls back to the refusal only when every value it has is refused.
Tightening it that way immediately found a second instance of the same class:
`Screw Head Type` moved nothing in a socket cap screw's drawing, because
`Socket` and `Hex` produced the same picture — a hex head's *elevation* across
the flats really is the rectangle a cylindrical head gives, but its end view is
six flats, and 524 hex bolts were being drawn with a round head. Fixing that
turned up a third defect a few lines away: the length dimension ran tip to top
on every style, so a socket cap screw's drawing put the label `1/2 in` against
a span of half an inch *plus the head height*. A countersunk length is measured
over the head and every other style's is measured under it; `total_height` had
always known that and the dimension line had not.

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
| shank diameter == cutting diameter | 0.6489 | 0.5946 |
| length of cut > overall length | 0.0829 | 0.0742 |
| an angle attribute carrying a length unit | 0.0469 | 0.0602 |
| declared measurement system contradicts the value's units | 0.0323 | 0.0269 |
| unit mixing within one record | 0.0222 | 0.0238 |
| title dimension token carries no label | 0.4667 | 0.4796 |
| title dimension token is not the primary dimension | 0.1714 | 0.1609 |
| title label truncated at the length cap | 0.0323 | 0.0390 |
| image reference missing | 0.1089 | **0.0000, deliberately** |
| image id is shared, not the product's own | 0.7353 | **1.0000, deliberately** |
| attributes per record (mean) | 13.12 | 13.5180 |

Two notes on reading that table honestly. The angle defect is **clustered**:
the attribute is line-constant, so one bad row reaches every SKU under that
line — which is how these arrive in a real catalog, and is visible in the
source corpus too, where the same wrong value repeats across a whole series.
Its per-record rate therefore swings much more between seeds than the others.
And attributes per record sits about 2.6% above its target because the
reference mean is over a different mixture of product families than this
catalog contains; the per-family shape is reproduced, the mixture is not the
same one. It moved across the target — it used to sit 2% below — when the four
socket-screw lines gained `Length Under Head` and two of them became product
types of their own, which is the mixture changing rather than any per-family
rate doing so.

The two image rows are **deliberate deviations, not misses**, and the target
column shows what this catalog aims at rather than what the corpus measures —
printing the corpus figure there would show a permanent, meaningless shortfall.
The corpus measures 10.89% of records carrying no parseable image reference;
this catalog gives every product and every variant one, because it is used as a
demo and a product with no image reads there as a broken page rather than as
realism about supplier data. The corpus measures 73.5% of references pointing
at an image that is not the product's own; this catalog goes further than the
rate, because one generic drawing per product type and style means *every*
reference is shared. Both measured figures are kept in `GeneratorConfig` as
`measured_image_missing` and `measured_image_sku_diverges`, and a test sets the
missing-image rate back and checks the behaviour returns, so the deviation has
not quietly become a limitation.

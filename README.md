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
| **Fasteners** | dimensions are **standards-derived**. Each line carries the standard designation its dimensions came from — `ASME B18.3`, `ISO 4762`, `ISO 10642`, `ISO 4014`, `ISO 4017`, `DIN 933`, `ISO 7089`. |
| **Cutting tools** | dimensions are **generated** from the conventional series. No open dimensional source for end mills exists, so nothing here claims a standard, and the provenance field says so in words. |

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
1/4".

## What ships, and what does not

| | |
|---|---|
| **Ships** | the generator, the extracted standards tables, hashes of the reference tuples, the synthetic catalog |
| **Never ships** | the reference corpus of captured pages, and the rendered images — both reproducible, see `.gitignore` |

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

### Two shapes, one catalog

`sip-generate build` writes both serialisations from the same generated
objects, so any difference between what they return is a property of the shape
and not of the data.

| file | shape |
|---|---|
| `nested.jsonl` | parent + nested SKUs + nested key-value attributes. The target shape: the only one in which "how many *products* have this value" is answerable, via `reverse_nested`. |
| `flat.jsonl` | one document per SKU, attributes denormalised. Loadable today. Its attribute array is a plain `object`, so `name` and `value` become two independent multi-valued fields and the correlation between them is lost. |
| `render.jsonl` | the same SKUs in the shape `sip-render batch` already reads |
| `stats.json` | what was generated, measured against the statistics it reproduces |

The flat shape also carries a sanitised `facets` object, because `Milling Dia.`
cannot be an Elasticsearch field name — the trailing dot makes it an invalid
path. The three spellings of the measurement-system attribute deliberately
sanitise to three different keys rather than being folded into one: folding
them here would hide the problem a field map exists to solve.

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

The catalog publishes **76 distinct attribute names** across 10 product types.
A hand-maintained list of 76 declarations drifts from the generator the first
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

Not all 76. Three measured gates, applied to the emitted documents:

| gate | rule | why |
|---|---|---|
| **discriminating** | at least 2 distinct values | a facet with one value cannot narrow anything — it is a control that does nothing |
| **characteristic** | present on ≥50% of the documents of the product types that publish it *at all* | the denominator is per-attribute: an attribute carried by one of ten types can never exceed ~10% of the catalog, yet may be the primary facet for its own category |
| **not an identifier** | a **terms** attribute carries ≤25 distinct values | `Thread Size` publishes 19 values over 1,576 documents and is the first thing a shopper filters on; `List Number` publishes 126 and is a part reference nobody browses. Numeric attributes are exempt — a range control's cost does not grow with cardinality |

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
| attributes declared | 76 |
| offered as facets | 56 (26 numeric ranges, 30 terms) |
| declared, not faceted | 20 |
| **fields in the field map** | **92** |
| **leaf fields in the Elasticsearch index** | **125** |
| facets in a category's sidebar | 8–14 |

The per-category figure is above the five-to-eight a real sidebar carries.
That is honest rather than tuned: fasteners genuinely publish four dimension
ranges (head diameter, head height, length, thread length) beside material,
finish and grade. Trimming to eight would mean dropping a control a shopper
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
* all 10 product types return their own documents, in the generated count
* the demo case: `3/8" end mill` returns products whose **shank** carries that
  value, and adding the structured `milling_dia` filter excludes them

### What the flat shape costs

The flat shape's `attributes` array is a plain object, so `name` and `value`
become two independent multi-valued fields. Filtering it for
*name = Shank Dia. AND value = 3/8"* matches **114** documents; only **65**
actually publish a 3/8" shank. The other 49 carry a 3/8" belonging to a
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
two, and reports any mutation that reds nothing as a zero.

## Images

Product images are **dimensioned technical drawings rendered from each
product's own attribute values**, not photographs and not model-generated
imagery. A drawing derived from the data cannot contradict the data — and a
dimensioned drawing shows the reader that cutting diameter and shank diameter
are different measurements, which is the point the catalog exists to make.

### Rendering

```sh
uv sync
uv run sip-render fixtures --out out              # every bundled reference record
uv run sip-render sku 4LU10 --profile card --out out
uv run sip-render batch records.jsonl --out out   # one JSON record per line
```

For a whole generated catalog, which needs per-record error handling:

```sh
python scripts/render_catalog.py out/catalog/render.jsonl --out out/images
```

**Some of the catalog cannot be drawn, and that is the renderer working.** It
refuses a record whose dimensions are missing or contradict each other rather
than defaulting a value, so the share it refuses tracks the sparsity and defect
rates the catalog reproduces. A run that drew 100% of this catalog would mean
the renderer had started inventing numbers. On the default 500-line catalog,
2,834 of 4,480 SKUs carry attributes a renderer recognises at all (a hammer
carries none), and of those 2,417 are drawn and 417 refused:

| refusal | count | why |
|---|---|---|
| `MissingAttributeError` | 227 | the record does not publish a dimension the drawing needs — `Helix Angle` is present on 88% of end mills, because it is present on 88% of real ones |
| `DimensionParseError` | 116 | the published value carries no unit, and a bare number is ambiguous |
| `ImpossibleGeometryError` | 74 | length of cut longer than the tool, the largest measured defect class |

Two profiles, both sized from where the image is displayed:

| profile | pixels | why |
|---|---|---|
| `card` | 600 × 880 | the catalog card's 150 × 220 box at 4× for high-density displays |
| `detail` | 1400 × 1400 | the detail view's 350 × 350 square box at 4× |

Tools are drawn standing up, shank above and cutting end below. That is how
the industry draws them, and it is the only orientation in which a long thin
tool fills a portrait card instead of floating in the middle of it. The card
carries the silhouette and the two diameter callouts and nothing else — at
150 CSS pixels wide there is room for one idea, and the two diameters are it.
The detail profile adds full dimensioning, an end view, and the attribute
table.

### What the renderer will not do

The drawing may only contain numbers the record contains, so:

* A value that cannot be read **raises**. There is no fallback dimension,
  because a defaulted dimension produces a drawing that disagrees with its own
  record and nothing downstream can tell.
* A record whose dimensions contradict each other — a length of cut longer
  than the tool — is **refused** rather than drawn.
* Geometry that no attribute implies is **left out**, not invented. The depth
  of a socket drive is not published, so the drawing shows the opening the
  socket makes in the head's top face and its true across-flats shape in the
  end view, and stops there. A Torx or cross recess is not drawn at all: one
  across-size does not determine a lobed shape. A head style whose profile
  does not follow from `Head Dia.` and `Head Height` — a button head's dome,
  for instance — is refused.

Some numbers that look like table lookups are not: the countersink angle of
the reference cap screw is computed from its head diameter, head height and
thread size, and lands on 82°, which is what the inch flat-head standard
specifies. The minor diameter of its thread comes from the 60° thread form and
lands on the published 0.1517". Those agreements are checks on the attributes,
not values borrowed from elsewhere.

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
| shank diameter == cutting diameter | 0.6489 | 0.6579 |
| length of cut > overall length | 0.0829 | 0.0779 |
| an angle attribute carrying a length unit | 0.0469 | 0.0535 |
| declared measurement system contradicts the value's units | 0.0323 | 0.0291 |
| unit mixing within one record | 0.0222 | 0.0181 |
| title dimension token carries no label | 0.4667 | 0.4622 |
| title dimension token is not the primary dimension | 0.1714 | 0.1669 |
| title label truncated at the length cap | 0.0323 | 0.0301 |
| image reference missing | 0.1089 | 0.1116 |
| image SKU differs from product SKU | 0.7353 | 0.7275 |
| attributes per record (mean) | 13.12 | 12.89 |

Two notes on reading that table honestly. The angle defect is **clustered**:
the attribute is line-constant, so one bad row reaches every SKU under that
line — which is how these arrive in a real catalog, and is visible in the
source corpus too, where the same wrong value repeats across a whole series.
Its per-record rate therefore swings much more between seeds than the others.
And attributes per record sits about 2% below its target because the reference
mean is over a different mixture of product families than this catalog
contains; the per-family shape is reproduced, the mixture is not the same one.

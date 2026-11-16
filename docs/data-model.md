# The data model, and the two shapes one build writes

Moved out of the README with its text unchanged (#1034), so the README keeps headroom under the
file-size cap; the [README](../README.md) keeps a short `### The data model` that links here.

## The data model

**A parent is one product. Its children are its purchasable variants (SKUs).**
The shape is core's nested variant model (elastic/prism#9141): today's ungrouped
view serves one document per SKU, and the grouped view will serve one per
product with its variants nested, from the same data.

```
parent    Dravenholt K663 -- High Speed Steel Square End Mill
          product-CONSTANT attributes: brand, series, material, coating,
          flute count, end type, helix angle
children  the SKUs, varying: milling diameter, length of cut, overall
          length, shank diameter, price, stock -- each with its own drawing
```

**How many variants a product has** is ONE knob, `variants_per_product`: about
half of products are single-SKU and the rest have 2 to 5, skewed small, as on a
marketplace (maintainer, 2026-09-27). A product never offers more variants than
its series has members. Threaded fasteners and end mills also carry grouped product
families beside those, with 6 to 15 variants each: see [Grouped product families](../README.md#grouped-product-families).
Two deliberately awkward cases are built in, so a grouped view is proven on more than the well-formed
shapes: a single variant that carries **no** variant-scope attribute (`zero_axis_share`), whose values
move onto its product while its description still states them (#87), and variants whose sparsity
leaves one without an attribute its siblings carry.

**Attribute names are the census's generic ones.** A concept is one name across
types -- `Material` on an end mill, a drill and a screw alike -- because that is
how the reference census names it (160 of 496 records), and on a nested index
every per-type spelling would be a facet of its own. `domains/industrial/names.py` is the
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
than separate keyword and numeric arrays. Each entry follows the data contract
of elastic/prism#9935:

```json
{"key": "milling_dia", "name": "Milling dia.", "value": "3/8", "unit_code": "INH", "value_canonical": 9.525}
```

* `key` is required: the machine name the Engine discovers an attribute by,
  namespaced as `attr_<key>` when it is a column's name (see below). It is
  `sanitize(name)` unless the type declares its own: a roller chain's `Pitch`
  (the distance between pin centres) has the key `chain_pitch`, apart from a
  metric tap's `Thread Pitch` (its thread pitch), whose key is `thread_pitch`.
  One quantity has one display label and two quantities never share one, so a
  name has one key catalog-wide. So read `key`,
  never derive it from `name`. `name` is the display name.
* A **measured** value is fully split. `value` is the bare magnitude with no
  unit marker and no thousands separator, `unit_code` (UN/CEFACT: `INH`, `MMT`,
  `FOT` for a chain's length in feet,
  `DD`, `ONZ`, `LBR`, `C78`, `RPM`, `TPI`, and `C62` for a count) is the only
  place the unit lives, and `value_canonical` is the magnitude in the kind's
  canonical unit (millimetres, grams, degrees, one, rpm, pound-force), computed
  exactly and rounded to a float once, as PRISM does it: elastic/prism's
  `rewrite/measurement_values.py` and elastic/prism-industrial-products' `nested.py`
  take the product with `fractions.Fraction` and apply `float(...)` last.
* Thread spacing is published under two keys, as real catalogs publish it: a
  metric tap's `Thread Pitch` (`thread_pitch`, `MMT`, `0.5`) and an inch tap's `Threads per
  Inch` (`threads_per_inch`, `TPI`, `32`). `TPI` is a LENGTH written as a count
  per inch (ruled on elastic/prism#9877): `value` stays the count and
  `value_canonical` is the pitch in millimetres, `127/5 / n`, so `32` TPI is
  `0.79375` and `20` TPI is `1.27`. `13` TPI (127/65 mm) does not terminate and
  is the nearest float, like `3/8"` (9.525 mm). The contract test reads each
  unit's kind and size from a pinned copy of the industrial deployment's
  `canonical_units` block (`tests/data/industrial_canonical_units.yaml`; see
  [The pinned unit declaration](../README.md#the-pinned-unit-declaration)). No key's
  measured entries mix quantity kinds, with no exception, checked on a fresh
  SMALL build, a fresh default build and the committed golden (#79).
* Anything else stays unitless text, including composite designators such as
  `1/4-20` and `M10x1.5`.

The split is **read back out of** the published string, never computed from
the generator's magnitude, so the two can never disagree: `3/8"` has no exact
two-decimal millimetre spelling, and a number computed from the original
magnitude would quietly differ from the string actually published. The mark
decides the unit and nothing repairs it, so a value of the wrong kind for its
key would show: the generator writes none (#404). It used to write inch lengths
(`2"`, `1-5/8"`, `42"`) under `point_angle` and `helix_angle`, 963 rows on one
load, where a facet offered them beside `118` and `135`; a real retailer would
fix that row, so the step is gone and `tests/test_no_wrong_kind_values_404.py`
holds every angle key to angles, in the flat spelling and in the nested entry,
over a sample of every product type at the measured defect rates and at their
ceiling, and a part to its whole and a declared system to its units. The flat
`facets_num` carries the same number as the nested entry,
taken from the same rule (`entry.split`) (#120). An attribute that
is not a measurement omits `unit_code` and `value_canonical` rather than
carrying nulls.

A nested entry therefore carries **no published spelling**: `3/8 in.` and
`1,070 lbf` live once, unchanged, in the flat document's `facets`. A consumer
that prints the spelling -- the drawing bundle's card stamp, the contact sheet,
the tests that compare a title with its attributes -- reads it from
`flat.jsonl`, joined on `sku` (`catalog.entry.published`), so every such
consumer is given `flat.jsonl` beside `nested.jsonl`. A test holds that the
join accounts for every flat value and that each spelling, read by the test's
own parser rather than by `split()`, gives exactly the nested entry's
magnitude, unit and `value_canonical`; a bare number takes its unit from its
key, never from the entry. A hand-worked table of published spellings pins
`split()` itself, so `1/2"` published as `0.5` is red even in a catalog
regenerated from that broken split.

Products are never grouped across brands. Two manufacturers' tools at the same
nominal geometry are different products.

### Three tiers say what makes a SKU different

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
sku          7159421039
title        Druvanholm Hex Head Bolt, 1/2-13 Dia./Thread Size, 1-1/4" L, Grade 5
description  Druvanholm Hex Head Bolt, 1/2-13 Dia./Thread Size, 1-1/4" L, Grade 5
             - 1-1/4" Thread Length, 3/4" Width
             Across Flats, 11/32" Head Height, 3/4" Head Dia., Druvanholm
             ASMEB18.2.1-78. ...
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
line's titles differ as whole strings left **about 1,900** SKUs naming nothing of
their own, and a bare substring test left 19 more of them passing on a
coincidence rather than on a value.

The coincidence outlives a catalog that has otherwise been repaired, which is
why the distinction is worth a rule rather than a remark: on the first pass at
this work the whole-string and substring counts had both reached zero while the
standalone-token count was still **10**. One of the ten was
`Button Head Socket Cap Screw, 1/4-20, Alloy Steel`, credited with naming a
length of `1/4` (then published as `Length under Head`) — which is the first half of a thread designation
and says nothing about how long the screw is. On the committed catalog all
three counts are zero.

Which attribute is "the" distinguishing one is **derived, not listed per
product type**: it is the attribute published on every SKU of the line, with
pairwise distinct values, whose magnitudes spread furthest. For an end mill
that is the cutting diameter, which its titles already carried — so the
end-mill titles are unchanged, which is the control for the whole rule. For a
screw it is the length, and a screw's thread size is line-constant, which is
why a title built around it read the same on every SKU of the line.

## Two shapes, one catalog

`ecom-generate build` writes both serialisations from the same generated
objects, so any difference between what they return is a property of the shape
and not of the data.

| file | shape |
|---|---|
| `nested.jsonl` | parent + nested SKUs + nested key-value attributes. The target shape: the only one in which "how many *products* have this value" is answerable, via `reverse_nested`. |
| `flat.jsonl` | one document per SKU, attributes denormalised. Loadable today. Its attribute array is a plain `object`, so `name` and `value` become two independent multi-valued fields and the correlation between them is lost. |
| `images.jsonl` | one row per image — one per product line — with its product type, the shape it is drawn as, its path under the image base URL at both profiles, and how many products point at it |
| `stats.json` | what was generated, measured against the statistics it reproduces |

Both shapes publish a SKU's own `description` beside its `title`. An industrial
SKU also publishes its manufacturer part number, `mfr_part_number` (#937): a
`keyword`, never equal to the `sku`, and the last token of the description. The line's
title ships too, as `parent_title` — it is what a grouped card will be headed
with — but it is no longer what renders under a SKU's title.

The flat shape also carries a sanitised `facets` object, because `Milling dia.`
cannot be an Elasticsearch field name — the trailing dot makes it an invalid
path. The three spellings of the measurement-system attribute deliberately
sanitise to three different keys rather than being folded into one: folding
them here would hide the problem a field map exists to solve.

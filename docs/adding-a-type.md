# How to add a product type

A product type is one leaf of the category tree, such as `screw_socket_head` or
`ball_stock_precision`. Each type is declared in a module of its own under
`src/synthetic_industrial_products/product_types/`. A breadth type is one new
file plus the generated output; a modelled type still edits some shared files,
listed under [What is still shared](#what-is-still-shared) (#48).

The build finds the modules by walking the package
(`catalog/typespec.py`, `discover`). The first read of any shared, type-keyed
table (`LEAVES`, `DRAWING`, `VOCAB`, `STANDARDS_FAMILY`, `USE_LINES`,
`FIGURES`, or the breadth rows through `breadth.rows()`) registers every module
into those tables, so no caller has to call a registration step before it
reads them. A type module can also be the first thing a process imports, which
is what a builder's own test does.

## The files

| File | When |
|---|---|
| `product_types/<family>/<type_key>.py` | Every type. The file name must equal the key, or discovery refuses it. |
| `product_types/<family>/__init__.py` | Once per family, with a one-line docstring. |
| `catalog/names.py` head-noun list | Only when the leaf's last word (`Ball`, `Bar`, `Screw`) is not listed yet. |
| `golden-catalog/*` and `src/prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml` | Every new type. Both are written by the build; never edit them by hand. |

A module declares one `SPEC = TypeSpec(...)`, of one of two kinds:

* **Breadth type.** One `BreadthRow`, with the same fields as a row file
  `data/breadth_categories/<type_key>.yaml`. The leaf, the drawing, the vocabulary and
  the brand family all follow from the row. `shape` is one of the six plain
  shapes in `drawing/breadth_shapes.py`: `sphere`, `cylinder`, `block`,
  `disc`, `tube` or `bracket`. Example:
  `product_types/raw_materials/ball_stock_precision.py`.
* **Modelled type.** `category`, `standards_family`, `vocab`, `figure` and
  `extent`, `make`, `share`, `price` and `key_attributes`, the facts the tests
  hold it to (step 5 below), and optionally `use_lines`. `make` is the
  builder: `make(gen, type_key, category)` drafts one line. A module must
  never import `catalog/generate.py` at module level (that is an import
  cycle); a builder that needs `LineDraft`, `ChildDraft` or `BRANDS` imports
  them inside the function. Examples:
  `product_types/fasteners/lock_nuts_nylon_insert.py` (its own builder, the
  pattern for a deepened type) and
  `product_types/fasteners/screw_socket_head.py` (a family builder on
  `Generator`).

`part_number_block` is left unset unless `sip-generate block` says otherwise
(step 2 below).

The types in `catalog/newtypes.py` (`NEW_TYPES`) are a third kind that no
module can declare yet. They stay where they are for now.

## Where a modelled type's builder lives

**A deepened type, or any type whose family has no builder yet, keeps its
builder in its own module.** `lock_nuts_nylon_insert.py` is the pattern: its
spec space (the series tables, the stocked combinations, the vocabulary) and
its `build` function are module-level, and `SPEC.make = build`. Nothing in
`catalog/generate.py` changes. Write a new `Generator` method only when two or
more types share one builder.

A module builder calls only this generator API, which is what the lock-nut
builder uses. Several names are private (leading underscore) because the API
was written for `generate.py`; a module may call them, and should call nothing
else private:

| Name | What it does |
|---|---|
| `gen.rng` | The type's own random stream. The ONLY source of randomness: never the module-level `random`, and never iterate a `set` (its order follows `PYTHONHASHSEED`, so only a check run in a fresh process sees the drift: `type_gates.builds_under_two_hash_seeds` builds the type in two processes, under `PYTHONHASHSEED` 0 and 1, and the `two_builds` gate compares them with `type_gates.difference`, which compares sha256 digests first and walks the records only on a mismatch to name the first differing SKU, so a new type's gates use it rather than a bare `==`; the golden slice sees it too). |
| `brands.pick_brand(gen.rng, type_key, gen._exhausted)` | The line's brand, skipping a brand whose spec space for the type is spent. |
| `gen._rotate(key, count)` | The next index of a deterministic rotation; use it, not `rng.choice`, for any choice the catalog must cover in full (a range, a size window's start). Each type has its own `Generator`, so the key only has to be unique within the type. |
| `gen._variant_count()` | How many SKUs the next line offers. |
| `gen._publish(inches, style)` | A length published in the brand's feed style; `style` is `newtypes.feed_style(brand, system, BRANDS)`. |
| `newtypes._window(gen, key, rows, count)` | A contiguous run of `count` rows at a rotating start. |
| `newtypes._weighted(gen.rng, table)` | One value from `((value, weight), ...)`. |
| `newtypes._nominal(thread)` | `M12x1.75` to `M12`, `1/2-13` to `1/2`. |
| `newtypes.table_provenance(...)`, `newtypes.GENERATED_PROVENANCE`, `newtypes.MM_PER_INCH` | The provenance string for dimensions read from a standard's table (`table_provenance` pairs each dimension with its standard), the one for generated rows (see [Sources](#sources-and-provenance)), the unit factor. |
| `model.keyword_attribute`, `model.length_attribute` | The attribute constructors. |
| `generate.LineDraft`, `generate.ChildDraft`, `generate.BRANDS` | The draft types and the brand list, imported inside the builder. |

A module may also import a sibling family's data table from
`catalog/newtypes.py` (the lock nut reads `_NUT_UNC`, the hex nut's inch
widths across flats) rather than copy it.

**A sibling of an existing family builder** uses that builder. Only the
socket-screw family takes its type's details from the module: its builder,
`Generator._build_socket_screw`, reads one `standards.SocketScrewLine` (the
metric and inch standards, the head style and name, the head accessor, and
whether length is measured over the head). `screw_socket_head.py` declares its
own as `LINE` and passes it through `make`. A sibling socket screw does the
same and edits nothing in `generate.py`.

Every other family's builder still branches on the type key inside
`catalog/generate.py`, so a new sibling of that family also edits the
builder's type-keyed tables and conditions (for example
`END_MILL_SERIES_LETTERS[type_key]`, `taxonomy.END_MILL_MATERIALS[type_key]`,
`type_key == "end_mill_ball"`).

A type built to a standard that has no extraction yet also needs that
standard's rows in `data/fastener_standards.json`; until then the build stops
with `StandardsDataError: no extraction for '<standard>'`. A module may
instead carry the table itself, as the lock nut does (see
[Sources](#sources-and-provenance)).

A threaded type that publishes `dia_thread_size` and whose standard has no
extraction declares the sizes that standard offers in its `SPEC`, as
`sizes={standard: (size, ...)}`, stated apart from its table. The thread-size
sweep in `tests/test_catalog_coverage.py` reads only that facet. It holds every
declared size to reaching a document, and it fails, rather than skips, a
standard that has neither an extraction nor a declaration. A type that
publishes `thread_size` instead, such as the lock nut, is not swept yet: see
issue #68. When the
type's `dimension_provenance` is a sentence rather than a bare standard name,
it also declares `line_standard`, which reads a record's standard back from
its published attributes. `set_screws_hex_socket` does both.

## The steps

### A new type

1. Write the module. Copy the example of the matching kind and change every
   field.
2. Check the type's part-number block: `uv run sip-generate block <type_key>`.
   It prints the block the key derives and, when another type already uses it,
   the first free block. In that case set `part_number_block=<block>` on the
   new type's `TypeSpec` (not on its `BreadthRow`): about one new type in 135
   collides at today's 68 types. Another open pull request can take the same
   block; `scripts/merge_pr.sh` re-checks it on the merged tree.
3. If the leaf's head noun is new, add it to `PRODUCT_NOUNS` in
   `catalog/names.py`.
4. Build the catalog and regenerate the committed one:
   `uv run sip-generate build --out golden-catalog`. Only the new type's
   records, the totals in `stats.json` and the field-weights YAML should
   change. The independence tests below enforce this.
5. A modelled type only: declare the type's size and facts on its
   `TypeSpec` (#61). The tests read them from there, so no test file and no
   shared table is edited. `register` writes each one into its table and
   refuses a key that a table also lists:
   * `default_lines` and `default_skus`: the type's product lines and SKUs in
     the regenerated catalog, counting only its documents whose
     `spec_quality` is not `fast_and_cheap`. `tests/catalog_size.py` sums
     them, and `test_each_types_declared_size_is_its_size_in_the_committed_catalog`
     holds each type to its count. This prints the pair for `KEY`:

     ```sh
     KEY=<type_key> python3 -c "import json, os; k = os.environ['KEY']; q = lambda f: sum(d['product_type'] == k and d['spec_quality'] != 'fast_and_cheap' for d in map(json.loads, open(f'golden-catalog/{f}'))); print(f'default_lines={q(\"nested.jsonl\")}, default_skus={q(\"flat.jsonl\")}')"
     ```

   * `claims`: the standards a line claims, as
     `claims(facts, *, metric, provenance, standard)`; `conformance.applicable`
     calls it. Leave it unset for a type that claims nothing.
   * `may_claim`: every standard a record may claim, each one cited in the
     module; `frozenset()` for a type that claims none.
     `test_every_claimed_standard_applies_to_the_part` holds each published
     `Standards` value to it. The build never reads it, so a `claims` that
     returns a standard missing from it reds.
   * `key_attributes`: the type's key dimension, normally its size attribute.
     The price census keys the type on it (`price.KEY_ATTRIBUTES`) and every
     title names it (`test_every_title_names_its_key_dimension`). `register`
     refuses a modelled type without one. When one line can hold two SKUs
     that share the key dimension (key stock's square bar and the rectangular
     bar of its width), the builder sets `ChildDraft.also` to the second
     dimension on the SKU that needs it, and that SKU's title names both.
   * `title_attributes`: only for a type whose title names another attribute
     than its price key; the title test then reads it in place of
     `key_attributes`. An O-ring is priced on its cross-section (`Width`) and
     titled by its nominal `Size`.
   * `threaded`, `fastener` and `unit_primary`: the description sentences the
     type joins ([Family tables](#family-tables)).

   The type's `share` is its own and is added on top
   ([Share](#share)): never lower another type's share to make room, because
   that moves the other type's output and breaks byte-identity. The size test
   (`test_the_catalog_is_the_size_it_was_asked_for`) sums every modelled
   share, so a total above 1.0 is expected. A breadth type edits no pinned
   count: the breadth part of the catalog's size is read from the rows.
6. A modelled type only: copy `tests/test_type_lock_nuts_nylon_insert.py` to
   `tests/test_type_<type_key>.py` and change `KEY` and `DEFAULT_SKU_FLOOR`
   ([SKU floor](#sku-floor)). It is the per-type gate template: uniqueness,
   census names, determinism, a committed golden slice, and independence from
   every other type. Write the slice with
   `uv run python tests/test_type_<type_key>.py`.
7. Declare a price model (`price=` on the `TypeSpec`; `register` refuses a
   modelled type without one). It is keyed on `key_attributes` (step 5). A
   type that publishes its material under another name than `Material` names
   it in `MATERIAL_ATTRIBUTES` in `catalog/price.py` (a wheel's is its
   `Abrasive Material`), since the census spec is the key in one material. A
   type the census has no prices
   for declares `measured=False`; one it has prices for restates its census
   rows and is fitted ([Price](#price)).
8. Restate the published figures the type moves
   ([Figures to restate](#figures-to-restate)).
9. Run the checks.
10. Merge with `scripts/merge_pr.sh <PR number>`, never with the GitHub button
   or `gh pr merge` (see [Merging](#merging-every-type-pr-goes-through-merge_prsh)).

### Deepening an existing breadth type

A breadth key (a row file in `data/breadth_categories/` or a breadth module)
becomes a modelled type with many SKUs. The other types must stay
byte-identical; only this type's records change. Each step below names the
rule it follows; the rules are in
[The rules a deepened type follows](#the-rules-a-deepened-type-follows).

1. Survey the spec space before writing code: the series a distributor
   stocks, the standard or table each series' dimensions come from
   ([Sources](#sources-and-provenance)), and the stocked material, finish and
   grade combinations of each.
2. Write the modelled module under the same key, with its own builder
   ([Where a modelled type's builder lives](#where-a-modelled-types-builder-lives)).
   Example: `product_types/fasteners/lock_nuts_nylon_insert.py`. Carry over
   what the breadth row fixes ([What to keep from the breadth row](#what-to-keep-from-the-breadth-row)),
   Name each attribute as the census does: `vocab` names must pass
   `test_every_published_name_passes_the_census_gate` (look a name up in
   `reference-statistics/00_attribute_name_census.json`), and a name may not
   repeat the leaf's own noun (the lock nut publishes `Type`, because
   `Nut Style` is refused). Set the share ([Share](#share)), the figure and `extent`
   ([Figure and extent](#figure-and-extent)) and the price model
   ([Price](#price)).
3. Delete the key's breadth row file (or breadth module). The key keeps its
   derived part-number block, so `sip-generate block <type_key>` says to leave
   `part_number_block` unset.
4. Declare `claims`, `may_claim`, `key_attributes` and the family sentences
   it qualifies for on the `TypeSpec` (step 5 of [A new type](#a-new-type));
   `key_attributes` is the breadth row's `size_attr`. Then add the type to the
   family builder tables it needs ([What is still shared](#what-is-still-shared)).
5. Do steps 3 to 9 of [A new type](#a-new-type).
6. Check that every other type is byte-identical, at both sizes, with the
   command in [Comparing the other types](#comparing-the-other-types). Only
   the deepened key may differ.
7. Put the measured facts in the pull request body: the type's SKUs and
   products at both sizes, the line fill ([Share](#share)), the breadth
   row's sizes found ([What to keep](#what-to-keep-from-the-breadth-row)),
   the price rows for a measured type ([Price](#price)) and the comparison's
   output.

### Moving an existing type into its own module

The output must stay byte-identical.

1. Find every entry for the key:
   `grep -rn '<type_key>' src/synthetic_industrial_products/catalog src/synthetic_industrial_products/drawing src/synthetic_industrial_products/data`.
   For a modelled type, the entries are in `LEAVES`, `DRAWING` (identity
   pairs), `VOCAB`, `STANDARDS_FAMILY`, `FIGURES`, `USE_LINES`,
   `Generator._BUILDERS`, the `config.type_weights` share, and for a socket
   screw its `_SOCKET_SCREW_LINES` row. A modelled type also has entries in
   `conformance._shared_claims` (when it claims a standard),
   `price.KEY_ATTRIBUTES`, `noise.THREADED`, `noise.FASTENERS` and
   `noise.UNIT_PRIMARY`, and a row in each table of `tests/type_facts.py`
   (`SHARED_MAY_CLAIM`, `SHARED_TITLE_KEY`, `SHARED_SIZE`). These become
   `claims`, `key_attributes`, `threaded`, `fastener`, `unit_primary`,
   `may_claim` and `default_lines`/`default_skus` (step 5 of
   [A new type](#a-new-type)). For a breadth type, the entry is its row file
   `data/breadth_categories/<type_key>.yaml`.
2. Move each entry into the module's `SPEC`, and delete it from the shared
   table. A key that is declared in both places is refused.
3. Build into a scratch directory and compare:
   `uv run sip-generate build --out /tmp/out && diff -rq golden-catalog /tmp/out`.
   The diff must print nothing.

No test table is edited: the discovery, fresh-reader and first-import tests
are parametrized over `typespec.discover()`, so they pick up the moved module
on their own.

### Table types

Use a table type (`catalog/tabletype.py`, #101) when a type does not parameterise easily: a dozen real sizes from one published chart, a few materials, a few packs. Examples: `product_types/fasteners/cotter_pins.py` and `retaining_rings_external.py`. A type exists once, so delete its breadth row file in the same PR.

* **Fields.** `columns` (the published name of each chart column, the size first) and `rows` (one real size per row, rising); `variants` (material, finish, price factor, cheapest first at 1.0); `packs`; `base_price`, `size_slope`, `pack_slope`; `draw` and `extent`; `share`, `default_lines`, `default_skus`; `unit` (`"mm"`, or `"in"` for an inch chart). `spec(TABLE)` refuses a table that breaks an order.
* **Facts.** Publish only what the chart gives, and cite the chart and the day it was read in the module docstring. Say so if the standard itself was not read. A column the chart lacks (a cotter pin's length) is not published.
* **A column another type publishes.** Use that type's name and spelling (a sprocket's `Pitch` is the roller chain's). Every column is a length of this type only: the unit-mixing defect reads a type's own lengths, so a name that is a length here and not there moves nothing there. `others_moved_from_the_golden` in `tests/type_gates.py` is the gate.
* **Attributes the table cannot state.** A `Variant` is a material. For a style with its own columns (a turnbuckle's end fittings, a shackle's body), wrap the `make` of `spec(TABLE)` with `dataclasses.replace` and add the attributes there, as `turnbuckles.py` does. The type is still a table type: `tabletype.tables()` records it by its key, so nothing else is written. A measurement two types publish under one name carries one unit in both (`Load Capacity` is in lbf): `tests/test_nested_entry_contract.py` is the gate.
* **Price.** A declared estimate, not a measurement: `base_price` is the first row in the first material and pack, a larger size costs more, a later material costs its factor, and a larger pack costs more in total and less a piece. There is no census row, no borrowed model, no noise and no fit.
* **Drawing.** `draw(values)` gets each column's length in inches from the SKU's own record and returns a `Figure` scaled from them. It carries no text; a proportion no column gives is a named constant in the module.
* **Share.** Two rules, both at the default build, where a type's product count is its `default_lines` and its SKU count its `default_skus`:
  * **At least 5 SKUs per table row.** A size column no other type publishes has a dispersion of rows / SKUs, and a dozen sizes over too few SKUs reads as a continuum to the facet rule (at 13 products the sizes measured 0.44 to 0.48 against the 0.50 threshold).
  * **At least 40 products.** `smallest_faceted` in `prism/derive.py` pins the faceted quantity on the fewest products (a roller chain's Roller Dia., on 30), with ties broken by attribute key order. A type at 40 or more never takes that pin, so it is one shared line fewer to edit.
  * A share of 0.016 gives 42 products and suits a table of up to about 13 rows. A 20-row table needs about 60 products, a share of about 0.023.
* **Tests.** Copy `tests/test_type_cotter_pins.py`, restate the table in it, and write the slice with `uv run python tests/test_type_<key>.py`. `tests/table_gates.py` holds the shared size, price-order and drawing gates.

**What a table type's PR edits.** Its own files, which no other PR touches:

* `src/synthetic_industrial_products/product_types/<family>/<key>.py` (new)
* `tests/test_type_<key>.py` (new)
* `tests/data/golden_slices/<key>.jsonl` (new, written by the test module)
* `src/synthetic_industrial_products/data/breadth_categories/<key>.yaml` (deleted, when the type had a breadth row)

Generated files. Rebuild them with `uv run sip-generate build --out golden-catalog`; `scripts/merge_pr.sh` rebuilds them again at merge, so a conflict in one is never resolved by hand:

* `golden-catalog/*`
* `src/prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml`

Shared files, edited by hand:

* `src/synthetic_industrial_products/prism/derive.py`: `faceted_low` in `MEASURED_DISPERSION`. Every table type moves it, because each adds products to `Package Quantity`.
* `tests/test_facet_control_rule.py`: the quantitative and faceted counts in `test_the_measured_figures_describe_a_catalog_that_exists`, one more of each per column name no other type publishes.
* `src/synthetic_industrial_products/catalog/names.py`: a `NAME_EXCEPTIONS` row for each column name the census lacks. Use a census name and there is no edit.

The first two are measurements of the whole catalog, so two table-type PRs each write a value and the truth after both is a third. After merging `main` into the branch, rebuild, run `tests/test_facet_control_rule.py` and write what it measures. Never keep either side of a conflict in those lines.

Nothing else is edited. A table type is found from the registry (`tabletype.tables()`), so it is not added to `NOT_MEASURED` in `tests/test_price.py` and has no row in `DISTINCT_SPEC_FLOOR` in `tests/test_catalog_brands_voice.py`. The `table:` rows in `scripts/mutation_check.py` cover the mechanism; a type adds none. The type counts in `README.md` and `docs/drawings.md` are read by no test and are restated once after a batch of types, not in each type's PR.

## The rules a deepened type follows

Each rule is what the first deepened type, `lock_nuts_nylon_insert` (#53),
did, with the command that settles it. The commands run from the repository
root.

### Share

Aim for about 1,000 SKUs at `--lines 39000` (maintainer ruling, 2026-10-07,
#53). That is a share of about 0.012 to 0.02, depending on how many SKUs a
line holds: pick one in that range, build at `--lines 39000`, and adjust it
toward 1,000. When the real spec space runs out first, fewer SKUs are fine;
never invent sizes or combinations to reach the figure. The types deepened
before the ruling (the lock nut and the set screw, at 0.1) keep their share,
because changing it moves their output. State the share and the SKU counts at
both sizes in the pull request body.

The share is a ceiling, not a guarantee: a line whose every SKU its brand has
already made builds nothing. The fill is lines built over lines drafted, and
`lines_by_type` in `stats.json` has the lines built (set `SHARE` to the
type's share):

```sh
SHARE=<share> python3 -c "import json, os; s = json.load(open('golden-catalog/stats.json')); print(s['lines_by_type']['<type_key>'], 'of', round(float(os.environ['SHARE']) * s['config']['lines']), 'lines;', s['skus_by_type']['<type_key>'], 'SKUs')"
```

Run the same command on the `--lines 39000` build's `stats.json` for the
large figures. A much lower fill means the module models too little of the
spec space: add series or combinations; never raise the share to hide it.

### SKU floor

`DEFAULT_SKU_FLOOR` in the type's gate file is two thirds of the type's
default SKU count, rounded down to a ten: a type at the ruled share builds
only about 60 to 100 SKUs at the default size, so rounding to a hundred would
give it a floor of zero. It catches a collapse back to a breadth row's one or
two SKUs; it is not a target. The count is `skus_by_type` in the command
under [Share](#share). The two existing gate files,
`test_type_lock_nuts_nylon_insert.py` and `test_type_set_screws_hex_socket.py`,
keep their floor of 300, as they keep their share.

### Figure and extent

**Figure.** Reuse the family's figure when it draws the part (the lock nut
uses `hex_nut`). Otherwise write one in `drawing/figures.py`, following
[Adding a drawing for a new type](drawings.md#adding-a-drawing-for-a-new-type):
the signature is `figure(record: dict[str, str]) -> Drawn`, where `record`
maps each published attribute name of the SKU to its value. A breadth shape
will not do: it draws every SKU `nominal`, and
`test_nominal_geometry_stays_rare` allows a modelled type at most 10%.

**Extent.** The `(width, height)`, in inches, of the largest bounding box
the figure draws for any SKU of the type: the whole drawing, not the part's
own size. `hex_nut` draws the face (its height is the width across corners)
above the side view, with a gap of 0.3 times the corners between them, so a
nut's drawing is `1.3 x corners + height` tall: the M36 ISO 7040 nut is
2.50" across corners and 1.53" high, and its drawing 4.78" tall. Measure it
on the default build and on the `--lines 39000` build, take the larger of
each side, add 0.1" and round to 0.05": the lock nut's 2.50 x 4.78 gives
`extent=(2.6, 4.9)`.

```sh
CAT=golden-catalog KEY=<type_key> uv run python - <<'PY'
import json, os
from pathlib import Path
from synthetic_industrial_products.catalog import bundle
from synthetic_industrial_products.drawing.figures import FIGURES
cat, key = Path(os.environ["CAT"]), os.environ["KEY"]
facets = bundle.flat_facets(cat)
figure, extent = FIGURES[key]
w = h = 0.0
for line in (cat / "nested.jsonl").read_text("utf-8").splitlines():
    parent = json.loads(line)
    if parent["product_type"] == key:
        for record in bundle.records(parent, facets):
            x0, y0, x1, y1 = figure(record).figure.bounds()
            w, h = max(w, x1 - x0), max(h, y1 - y0)
print(f"{key}: largest drawn {w:.2f} x {h:.2f} in; declared extent {extent}")
PY
```

Set `CAT` to the `--lines 39000` build's directory for the second
measurement. Any positive extent builds, so measure with a placeholder such
as `extent=(1.0, 1.0)` first; `test_no_product_exceeds_its_types_extent`
fails until the measured one is set.

### What to keep from the breadth row

| Row field | In the modelled module |
|---|---|
| `key` | The same key: the module's file name and `SPEC`'s first argument. |
| `category` | `category=`, unchanged. |
| `family` | `standards_family=`, unchanged: it picks the type's brands and standards pool. |
| `item` | The `Item` attribute and `LineDraft.item`, unchanged. |
| `size_attr` | The SKU's `primary` attribute, same name; it is the type's `key_attributes=` on its `TypeSpec`. |
| `size_values`, `featured_sizes` | Every value must be offered by the spec space and appear at the default size. The row's `reason` names the reference queries they serve. |
| `attributes` | Replaced by the type's own vocabulary. A value may become more specific (`Stainless Steel` became `18-8 Stainless Steel` and `316 Stainless Steel`). |
| `descriptor_attr` | The title descriptor, `LineDraft.descriptors` (the lock nut's is `Material`). |
| `shape` | Replaced by `figure` and `extent`. |
| `price_range` | Not read. A modelled type is priced by its `price=` model ([Price](#price)). |
| `skus`, `reason` | Dropped. |

No test checks the sizes yet. This prints how many SKUs carry each of the
row's `size_values` in the committed slice; every count must be above 0:

```sh
python3 -c "import json, sys, collections; c = collections.Counter(a['value'] for l in open('tests/data/golden_slices/<type_key>.jsonl') for a in json.loads(l)['attributes'] if a['name'] == sys.argv[1]); print({v: c[v] for v in sys.argv[2:]})" '<size_attr>' <size_value> <size_value> ...
```

The lock nut's row asked for `1/4-20 5/16-18 3/8-16 7/16-14 1/2-13 M8x1.25
M10x1.5`; the slice has 8, 11, 9, 7, 9, 15 and 14 SKUs of them.

### Sources and provenance

Every published dimension is read from a table a reviewer can open: a
standard's rows extracted into `data/fastener_standards.json`, or a table in
the module whose comment names the source file and the commit it was read
from (the lock nut's metric rows: FastenersWB `iso7040def.csv`,
`iso10512def.csv`, `iso10511def.csv` and `nyloc_def.csv`, at the commit that
`data/fastener_standards.json` records, and the column each value is, such
as `s_max` or `h_max`). A conventional size ladder with no dimensional table
is allowed (the inch lock nuts), but:

* a dimension no readable source gives is **not published**: the inch lock
  nut publishes no `Height`. Never scale or interpolate it from a neighbour;
* a line claims a dimensional standard (`LineDraft.standard`) only when every
  row it offers was read from that standard's table; otherwise
  `standard=""`.

A row whose dimensions were read from a standard's table publishes
`dimension_provenance` from `newtypes.table_provenance(...)`, which names the
table each dimension was read from (the hex nut and the lock nut do this).
`newtypes.GENERATED_PROVENANCE` is only for rows whose dimensions are
generated. `type_gates.provenance_problems` checks that every published
dimensional claim is named.

### Price

A modelled type is priced by the `PriceModel` it declares as `price=` on its
`TypeSpec` (`catalog/price.py`; the README's "Price" section under
"Realism" says what the terms are). Which kind of model it declares depends
on whether the price census
(`reference-statistics/P2_price_census.json`, `deep_types`) has the type
with 30 or more priced rows.

**No census rows: `measured=False`.** Declare the model with
`measured=False` and a comment that says where its level comes from and that
it is NOT MEASURED; the ball-pein hammer's is an example. Such a type gets
no price rows, so nothing checks its prices against a census. To give it
census rows, measure them as #69 did for the lock nut and the set screw:
extend `scripts/price_census_collect.py` and `scripts/price_census_parse.py`
(archive.org only, serial) and let the parser write the entry. Once its entry has landed, restate it in
`price.CENSUS` (and `ENDINGS`, `LENGTH_CENSUS`), run
`scripts/fit_price_model.py --write` and leave `measured` at its default, as
the lock nut and the set screw did in #69's second part. A type with no census rows of its own
that prices as a sibling does is listed in `price.BORROWS` instead (the
button, flat and low-head socket screws borrow the socket head's model). A
type module declares that with `borrows="<census type>"` in place of
`price=`; declaring both is refused at registration. A borrower's key is
held to the span its model was fitted over when `price.MEASURED_SPANS`
records one, so a larger part is never priced on the model's run-out slope:
the O-rings borrow the flat washer's model, keyed on the cross-section
(`Width`) and clamped below at the M3 washer's 0.126". Say in the module
that the borrowed price is generated, not measured.

**A type sold as a set of other types' parts: price it from its contents.**
A kit's census key (`Number of Pieces`) says how many pieces it holds, not
what they are, so its price is keyed on what they cost instead: list it in
`price.CONTENTS_PRICED`, and `price.price_key` reads `price.kit_contents`,
each piece priced on its own type's curve at that type's census per-piece
share (`price.PER_PIECE`). Its slope is then 1.0 and the fit gives it no
group noise. `KIT_PARTS` is read from `newtypes.KITS`, so a new kit kind of
an existing part type needs no price change; a kit of a new part type needs
that part's `PER_PIECE` row, which
`test_each_kit_part_is_priced_at_its_census_per_piece_share` checks against
the census.

**Census rows: restate them, then fit.**

1. Restate the type's census figures in `catalog/price.py`, copied from the
   census file, never retyped from elsewhere: its `CENSUS` row (n, p10, p50,
   p90, the key-dimension slope and its pair shares), its `ENDINGS` mix, and,
   where the census measures them, its `LENGTH_CENSUS`, `BRAND_CENSUS` and
   `TYPE_TIER_CENSUS` rows. `tests/test_price.py` checks each against the
   file, and `test_every_type_with_30_census_rows_is_restated` fails until
   every type with 30 rows is in `CENSUS`.
2. Fit the anchor and the noise:

   ```sh
   uv run python scripts/fit_price_model.py           # print the fit and every row at both sizes
   uv run python scripts/fit_price_model.py --write   # and write the literals between the fit markers
   ```

   It builds the default catalog and the 100K one (`--lines 39000`) and
   scores every row at both; about 2 minutes. It writes the literals between
   the `# @fit-begin` and `# @fit-end` markers of `catalog/price.py`'s
   `MODELS` table and of the socket head screw's module. A measured type
   declared in its own module needs the same markers around its fitted
   fields, and a branch in the script's `main` that writes them there and
   leaves it out of the `price.py` table, as it does for `SOCKET_PY`.
3. Rebuild `golden-catalog/` and the slice, then run `tests/test_price.py`.
   Every price row of the type must land in its band at both sizes, or be
   declared below.

**A row that leaves its band is declared, never given a wider band.** The
bands are `price_report`'s (`P50_BAND`, `SPREAD_BAND`, `MONOTONE_BAND`, and
three census standard errors where the census sample is small), one rule for
every type. When the fit says a row cannot reach its band, find the
cause, then declare it in `catalog/price.py` with that cause and the issue
that fixes it:

* **A pin**, for a row the cause holds on one side of its band: its reason in
  `PINNED_SHORTFALLS` and its figures at both sizes, as the fit prints
  them, in `PINNED_FIGURES`. At each size the row may then move no further
  out than that size's figure, within `PIN_TOLERANCE`, and must stay on its
  side (the wheel brand spread, #66; the kit
  p90/p10, #76). A figure a reason quotes is read from `PINNED_FIGURES` in
  an f-string, never typed, so a refit cannot leave it stale. A figure that
  states the cause, such as what the wheel's brand tiers alone give, is held
  by a test that measures it
  (`test_the_wheel_pin_reason_quotes_what_the_brand_tiers_alone_give`).
  There is no looser declaration: a row that lands on either side of its
  band from one build to the other has a model to fix, as the kit p50 did
  (#71: a kit was one group draw per page, so its few pages moved its median
  with the build's size; it is now priced from its contents).
* **Each record is the build's own figure.**
  `test_each_recorded_figure_is_the_figure_its_build_produces` holds every
  `PINNED_FIGURES` entry equal to its row's figure at
  that size (a dollar p50 to the cent, a ratio to three places), so a record
  is never loosened by hand, nor left loose after the row improves. The fit
  flags a stale one "re-record" with the figures to write.
* **A slope cut**, where the census slope alone spreads the shown price
  wider than the census p90/p10: its reason in `SLOPE_CUTS`. The fit refuses
  to lower any other type's slope.
* **A size noise**, where one spec's brands must sit close while its size
  pairs invert: its reason in `SIZE_NOISE`.

The fit exits 1, before it writes, on an undeclared row out of band or a pin
that no longer holds. A pin that moves further out is re-recorded by hand,
with its cause re-read. Put
the type's rows (census, default, 100K, band) in the pull request body,
from the fit's output.

### Family tables

`catalog/noise.py` adds a sentence to a record's description by family
table. A type joins a table when the sentence is true of every SKU it
publishes:

* `THREADED` (type key to its thread-size attribute) writes
  `Not for M10 or M16 threads.`, the neighbouring diameters. A type sold by
  one thread designation joins it, with `threaded=` on its `TypeSpec`.
  `tests/test_compatibility_text.py` reads the specs, and then requires
  every thread to be a real designation that agrees with `Thread Type`, and
  the type to offer Metric Coarse, Metric Fine, UNC and UNF. A pitch that
  test's tables lack is added there from the one table they cite.
* `FASTENERS` writes what the part is not (`Zinc-plated steel (not
  stainless).`). A fastener that publishes `Material` and `Finish` joins it,
  with `fastener=True`.
* `UNIT_PRIMARY` writes a unit equivalent of the type's primary length. A
  type whose primary attribute is a length (a `Size` or a `Diameter`) joins
  it, with `unit_primary=`; a thread designation is not a length.

Each record's sentences draw from its own stream (`noise.record_rng`), so
joining moves only this type's records. `tests/test_noise_text.py` checks
every sentence against its tables; run it after joining. The lock nut
joins `THREADED` and `FASTENERS`; a type that qualifies should do the same.

### Comparing the other types

Build `main` and the branch at both sizes, and compare each emitted file
type by type. `main` builds in its own checkout, so the branch's working tree
is not touched:

```sh
git fetch origin main
git worktree add --detach /tmp/sip-main origin/main
for size in 2600 39000; do
  uv run --directory /tmp/sip-main sip-generate build --lines $size --out /tmp/sip-cmp/main-$size
  uv run sip-generate build --lines $size --out /tmp/sip-cmp/head-$size
  python3 - /tmp/sip-cmp/main-$size /tmp/sip-cmp/head-$size <<'PY'
import hashlib, json, sys
from collections import defaultdict
from pathlib import Path
base, head = Path(sys.argv[1]), Path(sys.argv[2])
moved = set()
for name in ("flat.jsonl", "nested.jsonl", "images.jsonl", "render.jsonl"):
    sides = []
    for root in (base, head):
        by_type = defaultdict(hashlib.sha256)
        for line in (root / name).read_text("utf-8").splitlines():
            by_type[json.loads(line)["product_type"]].update(line.encode() + b"\n")
        sides.append({k: h.hexdigest() for k, h in by_type.items()})
    for key in sorted(sides[0].keys() | sides[1].keys()):
        if sides[0].get(key) != sides[1].get(key):
            moved.add(key)
            print(f"{name}: {key} differs")
for name in ("mapping.flat.json", "mapping.nested.json"):
    if (base / name).read_bytes() != (head / name).read_bytes():
        print(f"{name}: differs (expected only for a new attribute name)")
print("types that moved:", sorted(moved) or "none")
PY
done
git worktree remove /tmp/sip-main
```

For the lock nut, both sizes print `types that moved:
['lock_nuts_nylon_insert']` and no mapping line. The default size is
`--lines 2600`. The two builds at 39000 take about 45 s each.

### Figures to restate

A type that changes the catalog's size moves figures the README and
`docs/drawings.md` publish. Restate each from its command, never by hand
arithmetic:

| Figure | Where | Command |
|---|---|---|
| SKUs, products, depth and breadth type counts | README, first paragraph | `skus`, `lines` in `golden-catalog/stats.json`; the type counts with the command under it |
| Drawings, bytes unpacked, archive size | README "Small SVG"; `docs/drawings.md` "The magnifier" | `uv run sip-generate images --catalog golden-catalog --out /tmp/img --archive /tmp/img.tar.gz` |
| Lensed SKUs, by lens | README "Sizes are visible"; `docs/drawings.md` "The magnifier" | the command in `docs/drawings.md` "The magnifier" |
| `record` / `partial` / `nominal` | `docs/drawings.md` "Provenance" | the command there |
| The large build's per-type table and totals | README "The 100K catalog" | `uv run sip-generate build --lines 39000 --out /tmp/c39k`, then the `skus_by_type`, `skus` and `lines` of its `stats.json` |

#62 renames the large build and generates its figures; until it lands, its
table gets a row for each deepened type.

## The commands

```sh
uv run sip-generate block <type_key>                # the block to declare, if any
uv run sip-generate build --out /tmp/out            # about 8 s
diff -rq golden-catalog /tmp/out                    # empty for a move
uv run python scripts/fit_price_model.py            # a measured type's price fit, both sizes, about 2 min
uv run pytest -q tests/test_type_seam.py tests/test_breadth.py
uv run ruff check . && uv run ruff format --check <your module>
uv run pytest -q                                    # the full suite, about 5 min
scripts/merge_pr.sh --dry-run <PR number>           # the merge check, without merging
scripts/merge_pr.sh <PR number>                     # the only way a type PR merges
```

`ruff format --check` is scoped to the files you wrote: CI runs only
`ruff check`, and a few existing files are not in `ruff format` style.

## The checks

| What goes wrong | What refuses it |
|---|---|
| The module name is not the key, or the module has no `SPEC` | `discover` raises `TypeModuleError`, naming the module |
| The module fails to import | `TypeModuleError`, naming the dotted path |
| A modelled type leaves `category`, `standards_family`, `vocab`, `figure`, `extent`, `make` or `share` unset | `register` raises, naming the missing fields; an unset `share` would otherwise build one line, and an unset `extent` (either side zero) would draw at no size |
| A breadth type's row has a different key from its `SPEC` | `register` raises `TypeModuleError`, naming both keys |
| The key is declared twice (in a module and a table, or in two modules) | `TypeCollisionError`, naming the key (and both modules, or the YAML table, where it can) |
| Two types derive the same part-number block | The build refuses, names both types and the first free block. Set `part_number_block` on the **new** type: re-blocking a type that has already shipped renumbers every SKU it published. |
| A type's output depends on another type | `test_removing_a_type_leaves_every_other_type_byte_identical` and the resize and YAML-edit variants in `tests/test_type_seam.py` |
| The leaf's head noun is not registered | `test_every_category_leaf_ends_in_its_own_product_noun` |
| A reader cannot see a type in its own module | `test_a_fresh_reader_sees_a_migrated_type_without_registering_it`, and one first-read test per table read method |
| A type module imported first in a process breaks registration | `tests/test_a_type_module_imported_first.py` |
| Two pull requests merge cleanly but leave the merged catalog, field-weights YAML or blocks wrong | `scripts/merge_pr.sh` before the merge; the `main-merged-tree` CI job on every push to `main` after it |

`uv run python scripts/mutation_check.py --only "type seam:"` plants a defect
in each of these hooks and refusals and checks that the named test goes red.

## What is still shared

**Breadth types can be built in parallel.** Two breadth-type pull requests
share only these, and each has a mechanical resolution:

* **The committed output**: `golden-catalog/*` (the records, `images.jsonl`
  and the totals in `stats.json`) and the field-weights YAML. Two types whose
  keys sort next to each other conflict in the `.jsonl` files. The totals
  often do NOT conflict: every breadth row adds exactly one line and one or
  two SKUs, so both sides often write the same new totals, and git takes the
  identical hunk once. `stats.json` and the field-weights YAML then merge
  cleanly with totals that count only one of the two types. Rebuilding fixes
  it: `uv run sip-generate build --out golden-catalog`. Until then the golden
  test and `tests/test_prism_field_map_drift.py` are red, but only on a tree
  that holds both changes. A modelled type built from the per-type gate
  template also commits its own records as a slice under
  `tests/data/golden_slices/`, which no other type's pull request touches.
* **The part-number blocks.** Two pull requests can derive the same block,
  or both be told the same first free block by `sip-generate block`, which
  sees only its own branch. The build refuses the collision, naming both
  types, again only on the merged tree. Re-block the type that merges second.
* **The head-noun list** in `catalog/names.py`, when both add a new noun at
  the end of the list. This is the only file that reliably conflicts. Keep
  both nouns.

Measured with two toy breadth types on separate branches: only `names.py`
conflicted. The `.jsonl` files merged correctly, and `stats.json` merged with
wrong totals. On the merged tree the golden, field-map drift and `stats.json`
checks were red; after one rebuild they, the title, facet and seam tests
passed with no test edit.

### Merging: every type PR goes through `merge_pr.sh`

This repository has no branch protection (its plan answers 403), so GitHub
has no merge queue and no "require the branch to be up to date". A pull
request's green comes from a CI run against `main` as it was then. When
another type lands after that run, the two can merge without a conflict and
leave `main` red. So every merge, by every builder, is:

```sh
scripts/merge_pr.sh <PR number>
```

It clones the PR head into a temporary directory and merges current `main`
into it. A conflict in a file the rebuild rewrites (`scripts/merge_pr.sh
--print-generated` lists the eight) is left for the rebuild; any other
conflict, `names.py` or a file under `golden-catalog/` that the build does not
write, is handed back to you. It then rebuilds `golden-catalog/` with
`uv run --locked` (a stale `uv.lock` is refused, not re-locked), commits only
the generated files, and runs the drift, golden and seam tests
(`--print-checks` lists them), refusing a run in which no test passed. It
pushes the merged tree to the PR branch if it differs from the head, waits
for every CI check on exactly that commit (`--print-ci`; a failed, missing or
unexpectedly skipped check refuses), and squash-merges. Before every merge
attempt it re-reads `main` and the PR head, and refuses if either moved.
`--dry-run` does all of it except the push, the CI wait and the merge.

That re-read narrows the race with another merge but cannot close it: GitHub
has no compare-and-swap on the base. The `main-merged-tree` CI job runs the
same tests on every push to `main`, so a merge that raced, or skipped the
script, is red within minutes.

**Modelled types can be built in parallel too (#48, #61).** A modelled
type's claims, key dimension, description sentences, claimable standards and
size are on its `TypeSpec`, and each breadth row is a file of its own, so a
type that only uses an existing family builder edits no shared file.
Measured with two toy deepened types (`bar_stock_hex`, `bar_stock_round`,
each a module plus its deleted row file) on separate branches: merged in
either order, they conflicted only in the eight generated files; after one
rebuild the two orders gave the same tree, every other type's records were
byte-identical to the base (207 of 207 file-and-type digests), and the
golden, facts, seam, registration, breadth and thread tests passed with no
test edit. Before this change the same pair conflicted in six hand-kept
files. Each type's `share` is its own: the original types' `type_weights`
in `catalog/config.py` sum to 1.0, each new or deepened type adds its share
on top, and `test_the_catalog_is_the_size_it_was_asked_for` sums every
modelled share. Never take share from another type: that moves its output.

What a modelled type can still edit in a shared file, and so conflict on:

* `generate.KEY_DIMENSIONS`, for a type whose titles must name a key
  dimension that is not its variant axis (a bearing's number, a wheel's
  diameter).
* The family builder in `catalog/generate.py` (see
  [above](#modelled-types-what-the-family-builder-still-needs)), and the
  standards extraction in `data/fastener_standards.json`.
* Type-keyed tables a family may need. Find them with
  `grep -rn "'<sibling_key>'\|\"<sibling_key>\"" src scripts tests --include=*.py | grep -v product_types/`:
  `render/kinds.py` (`TYPE_KIND`), `render/generic.py`, `catalog/compat.py`,
  `catalog/muststock.py`, `catalog/newtypes.py` (`_KIT_MATERIAL`,
  `_KIT_FINISH`), `scripts/verify_elasticsearch.py`, and for the socket-screw
  family `test_the_catalog_offers_all_four_socket_screw_styles` in
  `tests/test_catalog_generate.py`.

## Measured costs

Wall-clock times from #48:

| Step | Time | Lines |
|---|---|---|
| One-time wiring: `all_type_keys` and its readers | about 3.5 min | 4 files, +45 / -22 |
| Move 1, `screw_socket_head` (modelled), warm | about 0.6 min | +37 / -10: a 36-line module, a 1-line family `__init__`, and one entry removed from each of 8 tables |
| Move 2, `ball_stock_precision` (breadth), cold | 0.45 min to a byte-identical `diff -rq`, 1.2 min to green seam and breadth tests | +48 / -37: a 47-line module, a 1-line family `__init__`, and a 36-line YAML row removed (today, the row's own file is deleted) |

A cold move also spends 1 to 2 minutes on the `grep -n` step for a modelled
type, whose entries are spread over 8 tables. A breadth type has one row, so
that step is quick. Each build-and-diff takes about 8 s.

As a guide to size, a breadth type takes about 45 lines and a modelled type
about 35, not counting a new builder, figure or vocabulary.

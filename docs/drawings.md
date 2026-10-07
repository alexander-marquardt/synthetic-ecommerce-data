# The drawings: how a SKU record becomes an SVG

This is the developer's view of `src/synthetic_industrial_products/drawing/`:
what runs, in what order, and where to change it. The README's
[Images](../README.md#images) section states what the drawings promise. The
rulings behind them (one drawing per SKU, no text, one scale per type, the
magnifier) are on
[elastic/prism-industrial-products#103](https://github.com/elastic/prism-industrial-products/issues/103),
and this page does not argue them again.

Paths below are relative to `src/synthetic_industrial_products/` unless they
start with `tests/` or `scripts/`.

## The pipeline

```
SKU record (attribute name -> published string)
  -> FIGURES[product_type]                       drawing/figures.py
       -> figure function, e.g. fastener()
            -> render/<kind>.geometry_from_record()   (six kinds, see below)
            -> Figure: polygons, discs, lines, dots, in INCHES   drawing/model.py
  -> type_scale(extent)                          drawing/sheet.py
  -> paint(figure, house_style, fill, hatch, scale)
       -> magnifier(...) decides plain or lensed
       -> drawing.svg.Svg collects the elements and writes bytes
  -> (svg_bytes, source)   source is "record", "partial" or "nominal"
```

Step by step:

1. **The record.** `catalog/emit.py` `drawing_record()` builds the input from
   the catalog: the product's and the SKU's published attributes merged, name
   to value, with a multi-valued attribute joined by `", "`. The bundle
   rebuild (`catalog/bundle.py` `_record()`) builds the same dict from the
   committed `nested.jsonl`. The two must agree byte for byte, because the
   digests they produce are compared (see [Determinism](#determinism-and-the-publish-gate)).
2. **Dispatch.** `drawing.draw_product(product_type, brand, records)` looks
   the type up in `FIGURES` and draws every SKU of one product at one scale.
   `draw_sku()` is the same call for a single SKU. Both live in
   `drawing/__init__.py`.
3. **Geometry.** The figure function reads the dimensions it draws. For six
   kinds it does not parse anything itself. It calls the
   `geometry_from_record()` of the matching module in `render/` (`endmill`,
   `drill`, `tap`, `fastener`, `washer` and `flapdisc`), the same function the
   older dimensioned renderer uses, so the two cannot read one record two ways.
   The hammer, the five types added under #103 (`hex_nut`, `bearing`,
   `depressed_wheel`, `hex_key`, `kit`) and the breadth shapes have no
   `render/` geometry. The nut, bearing, wheel and hex key read their lengths
   inline with `_length_or()` in `figures.py` (a `dimensions.parse_length`
   wrapper). The hammer parses its face and handle lengths with its own
   helper, the kit draws one slot per size it counts, and the breadth shapes
   read nothing (see [Breadth types](#breadth-types-six-fixed-shapes)).
4. **Figure.** The function returns a `Drawn(figure, source)`. A `Figure`
   (`drawing/model.py`) holds shapes in **inches**: `Poly` (also used for
   rectangles), `Disc`, `Lines` (line work: flutes, thread crests) and `Dots`
   (grit texture), plus `size_in`. Each `Poly` and `Disc` has a paint *role*:
   `part`, `plain`, `hole`, `dark`, `handle` or `grip`. Geometry stays in real
   units until the last step, so "a longer length of cut is drawn longer" holds
   by construction.
5. **Scale and layout.** `drawing/sheet.py` `type_scale()` turns the type's
   declared extent into sheet units per inch. `paint()` draws the brand frame,
   registers the material's hatch pattern, then either centres the figure on
   the sheet or, when `magnifier()` says the part is too small to see, draws
   it at true scale near the bottom with an enlarged copy inside a lens.
6. **Style.** `drawing/style.py` supplies the brand's house style (`ink`,
   `paper`, `frame`, from the brand book in `catalog/brands.py`), the part fill
   (the published finish's colour, else the bare material's) and the section
   hatch (the material's). A brand, finish or material with no entry raises
   `UnknownStyleError` instead of falling back to a default colour.
7. **SVG bytes.** `drawing/svg.py` is the writer. It uses no figure library
   and no XML library: `Svg` keeps an ordered list of element strings plus a
   `<defs>` map, and `to_bytes()` joins them into UTF-8 bytes. The module
   docstring says why matplotlib was dropped. Every coordinate goes through
   `num()` (one decimal, no trailing `.0`, no `-0`). Attributes are written in
   sorted order and `<defs>` entries sorted by key, so call-site keyword order
   cannot change the bytes. The root always carries `width="200"
   height="300" viewBox="0 0 200 300"`. The only XML library involved is the
   checker: `svg_problems()` in `drawing/__init__.py` parses the output with
   `xml.etree.ElementTree` to apply the allow-list.

## The registry and dispatch

`FIGURES` in `drawing/figures.py` maps a product type key to
`(figure_function, (width_in, height_in))`. The pair is the type's largest
drawn bounding box, in inches, with a little headroom.

* `_FIGURES` holds eleven of the original twelve types. The screw and bolt
  types go through `_broken(width, height)`, which wraps `fastener()` with the
  type's extent height so an overlong part is drawn broken (below).
* `FIGURES.update(...)` below `kit()` adds the five types from #103:
  `kit_assortment`, `nut_hex`, `bearing_radial_ball`,
  `wheel_depressed_center` and `hex_key`.
* A type declared in its own module (`product_types/`) is **not written in
  `figures.py`**: its `TypeSpec` carries `figure` and `extent`, and
  `typespec.register` writes the pair into `FIGURES`. `screw_socket_head`
  (the twelfth original type) and `lock_nuts_nylon_insert` (which reuses
  `hex_nut`) are declared this way.
* The 46 breadth types are not written in `figures.py` either.
  `catalog/breadth.py` `register()` adds one `FIGURES` entry per breadth row,
  pointing at one of the six fixed shapes in `drawing/breadth_shapes.py`. It
  also fills `taxonomy.LEAVES`, `taxonomy.DRAWING`, `STANDARDS_FAMILY` and
  `VOCAB`.
  `FIGURES` is a `RegistryTable`: its first read registers every type module
  and breadth row, so a script that imports only
  `synthetic_industrial_products.drawing` still sees all 67 types.

Dispatch is a dictionary lookup (`_figure()` in `drawing/__init__.py`). An
unknown type raises `UnknownTypeError`. Nothing falls back to a generic shape.
`tests/test_sku_drawings.py::test_every_product_type_has_a_figure` holds that
`FIGURES` and `VOCAB` have the same keys.

## Walkthrough: one socket head cap screw

SKU `7CJ54` in the committed catalog, product `TER-ASMEB18.3-85-1258`, brand
Tervasko. The figures below were measured by calling the code on that record.
The record, as the drawing receives it:

```
Head Type          Socket            Dia./Thread Size   5/16-18
Drive Type         Hex Socket        Length             1/2"
Material           Grade 12.9 Alloy Steel               Length under Head  1/2"
Finish             Black Oxide       Thread Length      1/2"
Head Dia.          0.4690"           Head Height        0.3090"
Drive Size         1/4"              (plus Item, Type, Thread Type, Meets/Exceeds)
```

`FIGURES["screw_socket_head"]` is `_broken(2.75, 5.95)`, so `fastener(record,
max_height=5.95)` runs. It calls `render/fastener.geometry_from_record()`,
which reads the record into a `FastenerGeometry`:

| attribute | geometry | what it becomes in the drawing |
|---|---|---|
| `Head Type` = Socket | `head_style`, in the `CYLINDRICAL` set | a rectangular head. `Flat` is a cone, `Button` a dome, `Hex` a rectangle plus a hexagon end view |
| `Dia./Thread Size` = 5/16-18 | `thread.major` 0.3125 in, `thread.pitch_in` 1/18 in | shank half-width 0.15625 in; one thread crest every 0.0556 in; the end chamfer is one pitch |
| `Length` = 1/2" | `length` 0.5 in | `total_height` = length + head height = 0.809 in, because a socket screw's length is measured under the head (a countersunk one's is over it) |
| `Thread Length` = 1/2" | `threaded_length` = min(thread length, shank) = 0.5 in | threaded all the way up to the head: no plain shank section |
| `Head Dia.` = 0.4690" | `head_dia` | head width; also the end-view disc's diameter |
| `Head Height` = 0.3090" | `head_height` | head height |
| `Drive Size` = 1/4" | `drive_size` | a hexagon of that size across the flats, in the `dark` role, inside the end view |
| `Length under Head` = 1/2" | `length_under_head` | not drawn. It is checked: if it differs from total height minus head height by more than 0.01 in, `ImpossibleGeometryError` is raised and the record falls down the [provenance ladder](#provenance-record-partial-nominal) |
| `Material` = Grade 12.9 Alloy Steel | | section hatch, from `style.MATERIAL_HATCH` |
| `Finish` = Black Oxide | | part fill, from `FINISH_TINT` |

The figure has the head at y = 0 and the threaded shank below it, with the end
view of the head beside it at x = max(head dia., major) x 1.25. Its bounding
box is 1.055 in wide and 0.809 in tall.

The type's extent is (2.75, 5.95) in, so its scale is
`min((200 - 36) / 2.75, (300 - 36) / 5.95)` = 44.37 sheet units per inch. Every
`screw_socket_head` SKU is drawn at that scale. This one is 46.8 x 35.9 sheet
units. That is wider than the magnifier's 40-unit threshold, so it is drawn
plain and centred. The output is 1,470 bytes. Its sha256 (`c88e5450...`) equals
the `images.jsonl` row for `7CJ54`, and drawing the record twice gives the same
bytes. Its sibling `27ED43` publishes `Length` 3/4", so it is drawn longer at
the same scale and has a different digest.

## Scale, the magnifier, and no text

**One scale per type.** `type_scale(extent)` is the usable sheet (200 x 300
minus an 18-unit margin on every side) over the type's extent: the smaller of
the width and height ratios. `product_scale_for()` ignores the records it is
given, so nothing about a particular product can change a type's scale. Two
parts of one type are therefore in true proportion, and a head or bore that
siblings share is drawn identically.

**Overlong fasteners are broken, not shrunk.** When a screw or bolt's total
height exceeds 90% of its type's extent height (`BREAK_START`), `fastener()`
draws the shank cut between two zigzag break lines. The visible height still
grows with the true length, up to 97% of the extent (`BREAK_VISIBLE`), so two
lengths never draw alike. The extents are the pre-100K ones on purpose; the
comment above `FIGURES` explains why.

**The magnifier.** `sheet.magnifier(width, height)` takes the part's drawn size
in sheet units. It returns `None` (draw plain) unless the part is at most 1/5
of the sheet's width **and** at most 1/6 of its height. A lensed part is drawn
at true scale near the bottom, and the same `Figure` is painted a second time,
`k` times larger, inside a white lens. The handled glass is used when it
reaches `MIN_ENLARGEMENT` (x2.5); otherwise the larger, handle-less lens. The
README's [Images](../README.md#images) section has the full rule. Measured on
the committed catalog: 1,699 of 10,775 drawings are lensed, 525 with the
handled glass and 1,174 with the handle-less lens. This command prints the
counts and the enlargement range of each lens:

```sh
uv run --directory tests python -c "
from test_sku_drawings import _golden_skus, _drawn_size
from synthetic_industrial_products.drawing.sheet import magnifier
lens = [m for m in (magnifier(*_drawn_size(p['product_type'], r)) for p, _, r in _golden_skus()) if m]
for kind in (True, False):
    k = [m.k for m in lens if m.handle is kind]
    print('handled' if kind else 'handle-less', len(k), f'x{min(k):.2f} to x{max(k):.2f}')"
```

**No text.** Figures only have `Poly`, `Disc`, `Lines` and `Dots` to draw with,
and nothing in `sheet.py` or `svg.py` emits a `<text>` element. The gate is
`svg_problems()`, an allow-list of elements, attributes and attribute-value
grammars that also refuses comments, processing instructions, entities and
character data. Its own docstring states the one gap: a letter's outline drawn
as a plain `<path>` would pass.

## Provenance: record, partial, nominal

Every figure returns a `source` alongside the figure, and `images.jsonl` records
it per SKU as `geometry`. A drawing has no text, so a nominal proportion never
prints a number that contradicts the record. The source field is there so the
share of guessed geometry is visible.

For the six kinds that use `render/` geometry, `_read()` in `figures.py` tries
these in order and stops at the first that parses:

1. **The record as published.** `record`.
2. **Absent attributes filled in** from the kind's `*_DEFAULTS`, each a
   proportion of the record's own primary dimension (an end mill's missing
   length of cut is 2.5 x its diameter). `partial`.
3. **Every defaultable attribute rebuilt** from the defaults, published or
   not, for when a published value contradicts another (a length of cut
   longer than the overall length). `partial`.
4. **Only the primary dimension kept** (`Milling Dia.`, `Size`, `Thread Size`
   or `Dia./Thread Size`), everything else from the kind's `*_NOMINAL` shape,
   for when some other published value is the conflict (a ball nose with a
   corner radius). Siblings of different sizes still draw different sizes.
   `partial`.
5. **The nominal shape.** `nominal`. This is the only rung where the record's
   primary dimension itself could not be used.

A "contradiction" is any exception in `render/attrs.py` `REFUSALS`:
`MissingAttributeError`, `ImpossibleGeometryError`, `UnsupportedFeatureError`
and `DimensionParseError`.

The figures without `render/` geometry decide per attribute. `_length_or()`
returns the parsed value or a proportional fallback. The result is `record` if
every drawn value parsed, `partial` if the primary parsed, and `nominal` if it
did not. The hammer is never `nominal`: a missing face or length makes it
`partial`. Its head weight is not drawn (`hammer()`'s docstring explains why).
A kit is `record` when it publishes `Sizes Included`, `partial` otherwise. The
breadth shapes are always `nominal`.

Measured on the committed catalog's `images.jsonl`: 8,327 `record`, 2,367
`partial`, 81 `nominal`. All 81 `nominal` rows are breadth SKUs; no depth SKU
falls back to nominal geometry. The counts are
`python3 -c "import json, collections; print(collections.Counter(json.loads(l)['geometry'] for l in open('golden-catalog/images.jsonl')))"`.

## Breadth types: six fixed shapes

The 46 breadth categories (rows of `data/breadth_categories.yaml` and breadth modules; every
breadth line is published with `spec_quality: "fast_and_cheap"`, set by
`catalog/breadth.py` `SPEC_QUALITY`) draw one of six shapes from
`drawing/breadth_shapes.py`: `sphere`, `cylinder`, `block`, `disc`, `tube`
and `bracket`. Each YAML row names its shape with `shape:`. A shape function
discards the record (`del record`) and returns the same geometry every time, with its own fixed
extent in `BREADTH_SHAPES`. Brand, material and finish still apply, because
they come from `paint()` and not from the figure, so the outline is fixed but
the colours are not. Two SKUs of one breadth product therefore draw
identically, and `tests/test_sku_drawings.py` exempts breadth from the
"siblings must differ" and "nominal stays rare" checks.

## Determinism and the publish gate

A drawing is a pure function of `(product_type, brand, record)`. It does not
read the SKU, the product id or the title, and it uses no randomness, clock or
host state. The bytes are fixed by the writer as well: one-decimal
coordinates, sorted attributes, sorted `<defs>`, and hatch ids derived from
the hatch and ink (`h0-90s5` + the ink's hex). The same record therefore gives
byte-identical SVG on any machine. Two SKUs that publish the same drawn values
give the same bytes too, and that is correct, because the picture has nothing
to tell them apart by.

The drawings are not committed. What is committed is the digest:

* `sip-generate build` writes `images.jsonl` (`catalog/emit.py`
  `iter_image_manifest()`), one row per SKU with `image_id`, `path`, `url`,
  `sha256`, `bytes` and `geometry`.
* `tests/test_catalog_golden.py` regenerates the catalog and compares every
  committed file by sha256, `images.jsonl` included. A change that moves any
  drawing turns it red until `golden-catalog/` is regenerated in the same
  commit.
* `sip-generate images --catalog golden-catalog ...` (`catalog/bundle.py`
  `rebuild()`) redraws every SKU from the committed `nested.jsonl` and raises
  `BundleMismatchError` unless each drawing's sha256 equals its
  `images.jsonl` row, and every row names a SKU. Only then does it write the
  files and a deterministic archive (sorted members, zeroed times and owners,
  a gzip header without a timestamp).
* What a consumer pins is the **content digest**: the sha256 of the sorted
  `<member path>\t<file sha256>` lines (`bundle.content_digest()`). It can be
  computed from `images.jsonl` alone (`bundle.manifest_digest()`), and it does
  not depend on the zlib build, whereas the archive's own sha256 does.
* `scripts/check_determinism.py --images` builds twice in fresh interpreters
  with different `PYTHONHASHSEED` values and compares every emitted file,
  including the archive.

## How `tests/test_sku_drawings.py` enforces accuracy

The module builds two corpora. `DRAWINGS` is a freshly generated `SMALL`
catalog (160 lines plus the newer types and breadth). `GOLDEN_PRODUCTS` and
the other golden-catalog tests read the committed `golden-catalog/`. The tests
that matter most when you change a figure:

| test | what it holds | corpus |
|---|---|---|
| `test_elongated_parts_are_drawn_to_their_published_length` | for socket and flat screws, hex bolts, square end mills and drills drawn from the `record`, the on-axis extent equals the `render/` geometry's length to 1e-6 | SMALL |
| `test_a_drawn_dimension_changes_the_drawing` / `test_an_attribute_no_drawing_shows_does_not_change_it` | a 9" screw draws differently; adding `Standards` changes no byte | SMALL |
| `test_siblings_whose_drawn_values_differ_never_draw_alike` | variants whose drawn values differ never share bytes. Attributes in `NOT_DRAWN_BY_ANY_FIGURE` are ignored, and breadth is exempt | golden |
| `test_no_product_exceeds_its_types_extent` / `test_every_drawing_fits_its_sheet` | the `FIGURES` extent really is the type's maximum, so its scale is a constant | golden |
| `test_siblings_are_drawn_at_one_scale_...` / `test_within_a_type_every_part_is_drawn_in_true_proportion` / `test_an_m3_washer_is_drawn_smaller_than_an_m16_in_true_proportion` | one scale per type, measured on the true-scale copy (an M3 washer is 7/30 of an M16) | golden + planted |
| the `test_the_lens_*` and `test_*lens*` tests, `test_no_outline_is_thinner_than_the_minimum_stroke` | the magnifier rule, enlargement floor (pinned at the catalog's measured x2.52), balance, ink and minimum stroke | golden + planted |
| `test_a_part_longer_than_its_extent_is_drawn_broken_and_fits`, `test_no_fastener_is_drawn_smaller_because_of_an_outlier` | the break convention | planted |
| `test_no_drawing_carries_any_text`, `test_the_allow_list_refuses_every_planted_text_form` | the allow-list, against planted `<title>`, `aria-label`, comments, rasters, `@font-face`, glyph paths | SMALL + planted |
| `test_nominal_geometry_stays_rare` | at most 10% `nominal` per depth type | SMALL |
| `test_the_committed_catalog_rebuilds_into_its_recorded_drawings` and the bundle/digest tests | the publish gate above | golden |

`tests/test_breadth.py` runs every breadth drawing through `svg_problems()`.
No test draws two breadth records with different dimensions and compares the
bytes. The fixed-shape property holds by construction (`del record`) and is not
pinned by a test.

## Adding a drawing for a new type

1. **Write the figure function** in `drawing/figures.py`:
   `def my_type(record: Record) -> Drawn`. Draw in inches with `Figure`'s
   `poly`, `rect`, `disc`, `lines` and `dots`, and set `size_in`. If `render/`
   already has a `geometry_from_record` for the kind, call it through `_read()`
   with a `*_DEFAULTS`, a `*_NOMINAL` and the primary attribute. Otherwise
   parse with `_length_or()`. Return `record`, `partial` or `nominal`
   truthfully.
2. **Declare it with its extent.** A type in its own module sets
   `figure=<function>` and `extent=(width, height)` on its `TypeSpec`; a type
   still in the shared tables gets a `FIGURES` entry. The extent is the
   largest bounding box any product of the type will draw, plus headroom: the
   measuring command and the headroom rule are in
   [How to add a product type](adding-a-type.md#the-rules-a-deepened-type-follows),
   "Figure and extent". Too small and `test_no_product_exceeds_its_types_extent`
   fails. Far too large and every part of the type is drawn needlessly small,
   or lensed. A breadth shape will not do for a modelled type: it draws every
   SKU `nominal`, and `test_nominal_geometry_stays_rare` allows a modelled
   type at most 10%.
3. **Keep the type keys in step.** A module's `TypeSpec` fills `DRAWING` and
   `VOCAB` itself; a type in the shared tables needs an entry in
   `catalog/taxonomy.py` `DRAWING` and in `catalog/vocab.py` `VOCAB`. The
   generator must build lines of it: `test_every_product_type_has_a_figure`
   requires `FIGURES` and `VOCAB` to have the same keys AND the generated
   `SMALL` catalog to draw every `VOCAB` type. This checklist covers the
   drawing only; the type's generator comes first.
4. **Give every published `Material` and `Finish` a colour and a hatch**
   (`drawing/style.py` `MATERIAL_FILL`, `MATERIAL_HATCH`, `EXTRA_FINISH_TINT`,
   and `render/marking.py` `FINISH_TINT`), or
   drawing raises `UnknownStyleError`.
   `test_every_published_finish_and_material_has_a_colour_and_a_hatch` sweeps
   the data.
5. **Do not widen the allow-list casually.** A new element or attribute in
   `svg_problems()` reopens a route for text. If one is truly needed, add a
   value grammar for it and keep the planted-text tests red-capable.
6. **Make every drawn attribute move the picture.** If siblings differ only in
   a value the figure ignores, either draw it or add it to
   `NOT_DRAWN_BY_ANY_FIGURE` with a reason. For a long part, add the type to
   `test_elongated_parts_are_drawn_to_their_published_length`.
7. **Regenerate and verify.** Run `uv run sip-generate build --out golden-catalog`
   (the `images.jsonl` digests move), then
   `uv run sip-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz`
   and `uv run python scripts/check_determinism.py --images`.
8. **Look at it.** `uv run python scripts/contact_sheet.py --catalog golden-catalog --out out/contact-sheets`
   puts twenty SKUs of every type on one HTML page.

A new **breadth** category needs no figure code: add a row to
`data/breadth_categories.yaml` with one of the six `shape:` values, give any new
`Material`/`Finish` a colour and hatch (step 4), regenerate `golden-catalog/`,
and commit it. No pinned count moves: the golden test's expected size
(`tests/catalog_size.py`) reads one line and `breadth.sku_count(row)` SKUs
from each row.

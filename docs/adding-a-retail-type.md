# Adding a retail product type: the map

Read this before you open `scale.py`, `export.py` or the test suite. It says where each piece of
a new type goes and which test refuses it when it is wrong. The mechanics of the one spec file
(scaffold, rows, decoys, regenerate) are in [new-type-quick-path.md](new-type-quick-path.md);
this page is the rest of the map. Every file, module name and command below is checked by
`tests/test_adding_a_retail_type_210.py`, so a rename reds there, not in your context.

Paths are relative to `prototypes/retail_drawings/` unless they start with `tests/`, `docs/`,
`golden-retail/` or `scripts/`. A `module.NAME` is a name in that module.

## 1. The row

* A style is a `breadth_rows.Row` in `type_specs/<key>.py`: its colors times its sizes are its
  SKUs. Use it as it is when a SKU differs only by `color` and one size name.
* Subclass it when a SKU carries more. `furniture_rows.FurnitureRow` takes a size as
  `(name, price, ((field, value), ...))`, so `160 x 90 cm` also writes `width_cm` 90 and
  `length_cm` 160 on the SKU, which the export turns into a range filter. `lowerbody_rows.LRow`
  adds a third SKU axis (`sold_as`). Other subclasses (`appliance_rows`, `toys_rows`,
  `household_rows`) are the same idea: copy the nearest one, do not invent a new `skus()`.
* A new SKU field is useless until the export names it (section 4).

## 2. Drawn attributes: `scale.FROZEN_KEYS`

The scaled build derives further styles from a `derivable=True` type by swapping attribute
values (`scale.derivable`; a `derivable=False` type is left out by `type_registry.left_out_ids`).
A key whose value the drawing or a measured SKU follows must never be swapped: a derived style
would otherwise change Round to Rectangular and keep the drawn round table and its `160 x 90 cm`
SKUs (a hypothetical: furniture is left out of `scale.derivable`). Most specs are not
`derivable` (the default is `False`), so a new type can usually skip this section. Add the key to `scale.FROZEN_KEYS` (today a lamp's `ip_rating` and `fitting`, a plate's
`plate_type`, a pattern's `motif_count`).
A value with a unit, or one that names the leaf, is already never changed
(`tests/test_retail_scale.py::test_only_a_value_free_of_the_leaf_the_unit_and_a_longer_word_may_vary`).

## 3. Units and what `check_catalog` expects

* A measured value is published as the shopper reads it (`90`, in `cm`) with its unit code
  (`CMT`) and a `value_canonical` in the core's canonical unit, which for a length is
  millimeters: 90 cm is 900.0. `furniture_rows._cm` writes the tuple
  `(key, name, "90", "CMT", 900.0)`; a SKU field goes through `export.OPTIONS` and
  `synthetic_ecommerce_data.core.entry.split` computes the pair for you.
* `synthetic_ecommerce_data.core.standard.check_catalog` (run by `tests/test_output_standard.py`
  with `one_class_per_key=True` for retail) refuses: a `unit_code` without a `value_canonical`
  or the reverse, an unknown unit code, a value that is not a bare number, a canonical that is
  not the value converted, and a key that has a unit on some entries and none on others.
* One key per concept: every measured height is `item_height`, never a second spelling
  (`key_guard.py`, gen#227). Values of two kinds (a garment size `M`, a thread size) do not
  share a key.

## 4. Export SKU options: `export.OPTIONS`

One line per SKU field: `field -> (key, name, unit code or None)`, for example
`"width_cm": ("item_width", "Item width", "CMT")`. A SKU field that `export.OPTIONS` does not
name is a `KeyError` at export, not a silent skip. Add the line for each new unit field, and use
the existing line when the concept already has one.

## 5. Color words

A color value is a plain word from `colorwords.COLOR_WORDS` (`Natural`, `Brown`, `White`), with
optional `colorwords.MODIFIERS` (`Dark` is a modifier, so `Dark Brown` is a modifier plus a color
word, not a `COLOR_WORDS` member). `variants.cw` maps an authored shade through `colorwords.PLAIN`
first: `cw("Oak", ...)` gives `Brown` and `cw("Walnut", ...)` gives `Dark Brown`, so authoring those
does not red. A shade `PLAIN` does not map (`Hazelwood`) stays as written, is not plain, and
`tests/test_retail_color_words.py::test_every_color_value_is_a_color_word_a_qualifier_or_a_shade_code`
refuses it: add it to `colorwords.PLAIN` or use a plain word. The material goes in its own `material` attribute (`a("material", "Material", "Oak")`).
Every color-bearing type also carries red, blue, green, yellow, black and white somewhere, or a
reasoned line in `main_colors.EXCEPTIONS` (`tests/test_retail_main_colors_275.py`).

## 6. Brands: `breadth_rows.OWNERS` and house styles

* Who owns a brand: `owners=(("Brand", "own"),)` in the spec when no module states it yet
  (`type_registry.TypeSpec`); an older module adds the brand to `breadth_rows.OWNERS`. A row
  whose brand has no owner is a `SpecError` from `type_registry.validate` for a spec row, and a `KeyError` when an older module's document is built.
* Every brand also needs one row in `house_styles.HOUSE_STYLES` (the paper, frame, outline and
  its own mark), or its image cannot render:
  `tests/test_retail_scale.py::test_every_brand_in_the_build_has_a_house_style`.
  `test_house_styles.py` refuses a duplicate mark or lockup, so choose a mark no other brand has.
  Prefer a brand that already has a row.

## 7. Where a row goes in `scale.templates()`, and smaller builds

`scale.templates` lists the authored documents in a fixed order: the preview samples, the
`*_rows` modules, `type_registry.docs()` (every spec, in key order), the needs and color-word
rows, the apparel decoys, and last the grocery styles. `scale.build(skus)` takes templates in
that order until their SKUs reach the target, and only then derives more. A build smaller than
the template list therefore stops partway: a type late in the list is absent from a small build,
and its decoys are too. A spec needs no edit to `templates()`; a module of the older kind is
added to the list by hand, and the later it sits the fewer small builds hold it. To see a build, run
`uv run python prototypes/retail_drawings/scale.py --skus 2000`.

## 8. Images: one per style and colorway

`export.image_id` is `<type>/<product id>/<digest of the drawing spec>`, and
`export.drawing_spec` is the style's drawing in the SKU's color swatch plus the SKU's own value
of each drawing param. So a style yields one image per colorway, and a drawing param that varies
by SKU (a lamp's `finish`) yields one per value. Sizes alone add none. If two things must look
different on the sheet (a two-seat and a three-seat sofa), they are two styles.
`image_release.image_files` renders them, and `tests/test_retail_image_release.py` refuses an id
that names two drawings.

## 9. Rebuild the figures and run the tests

There are no figures to rebuild or commit (gen#536). A test reads a total with
`retail_figures.figures()` (`retail_figures.py`), which measures your tree once per test run. To see the figures, the
apparel decoy table and the samples your build makes, run
`uv run python scripts/build_derived.py --out build/derived`: it writes `golden-retail/stats.json`,
`docs/figures.md` and `docs/retail-apparel-decoys.md` under `build/derived` (CI uploads the same as
the `derived` artifact). Never commit them: the `no-derived-files` job refuses a PR that does.

Run, with your own test file: `tests/test_retail_type_specs_351.py`,
`tests/test_output_standard.py`, `tests/test_retail_scale.py`, `tests/test_retail_breadth_34.py`,
`tests/test_retail_drawing_honesty.py`, `tests/test_retail_image_release.py`, `tests/test_retail_figures_162.py`,
`tests/test_retail_color_words.py`, `tests/test_retail_main_colors_275.py`,
`tests/test_us_spelling.py`, `prototypes/retail_drawings/test_shape_honesty.py` and
`prototypes/retail_drawings/test_house_styles.py`. Name them in the command: a bare `pytest` runs
the whole suite.

## 10. Looking at the SVGs

ImageMagick's SVG renderer drops strokes, so rods, outlines and drawer fronts are missing and
a drawing that looks wrong there may be right. On macOS use
`qlmanage -t -s 400 -o <dir> <file>.svg`, or a browser. Where `rsvg-convert` is installed,
`rsvg-convert -o x.png x.svg` draws strokes too (the quick path uses it).

## 11. Shared files: a file, never a line

A feature never appends to a registry that other features append to. The decoy tables read the
modules of `feature_decoys/`, the scaled build reads `type_specs/`, and the mutant harness reads
`scripts/mutation_rows_*.py`, each by walking or globbing: add a file there. The table of the
shared files and of what replaces a line in each is in
[new-type-quick-path.md](new-type-quick-path.md#shared-files-add-a-file-never-a-line), and the
`no-derived-files` job's `scripts/check_no_registry_append.py` fails a diff that appends one.

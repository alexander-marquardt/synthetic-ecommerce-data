# Add a retail product type: the quick path (one file)

The common case is rows plus a drawing shape the kit already has. You edit ONE file. A type
with a shape of its own and cross-department decoys is the second half of this page.
What else a type touches (units, `FROZEN_KEYS`, brand owners and house styles, images, the tests)
is in [adding-a-retail-type.md](adding-a-retail-type.md).
The long reference for the industrial catalog is [adding-a-type.md](adding-a-type.md); read it
only when this page does not cover what you need.

1. Scaffold the spec (about 10 s):
   `uv run python scripts/new_type.py <key> --kind clothing|beauty --product-type "<Type>"`
   It writes `prototypes/retail_drawings/type_specs/<key>.py`: one `SPEC = TypeSpec(...)` with a
   working example row. `<key>` is lower-case words joined by underscores and is the file name.
   The row code is the key cut to six letters, with a digit at the end when a registered spec
   already builds that id (two keys that start `specimen_` would build one `BRD-SPECIM`);
   `--code ABCXYZ` sets it. A code a row still outside the registry uses is refused by the
   build, which names the id: give the new row another code.
2. Edit that file. Replace the example with the type's real rows:
   * a style is a `Row` (or an `LRow`, which adds a third SKU axis such as `sold_as`): its
     colors times its sizes are its SKUs; `path` is the category leaf, `shape` an existing
     drawing shape (`kit.SHAPES`), `attrs` the shopper attributes (`a(key, name, value)`);
   * `derivable=True` lets the scaled build draw more styles from the rows (a breadth type);
     False keeps them as templates only;
   * a brand no module states yet goes in `owners=(("Brand", "own"),)`;
   * a SKU quantity the type varies by (a length in metres) goes in `options=(Option("size_key",
     "id", "Name", "UNIT"),)`: the SKU field, the entry's key and name, and its unit code or
     none (gen#413). `type_registry.option_table` merges every spec's options with
     `export.SHARED_OPTIONS`; a key with two names, or an option declared two ways, fails
     `tests/test_retail_type_options_413.py` and stops the build. Two specs may declare one
     option alike, and one key may carry two units (`item_length` in cm or m);
   * a hand-authored text-match decoy (gen#294) is a `Decoy(class 1-7, query, policy, row)` in
     `decoys=`; it is never derived and never takes a color completion;
     the output standard's text check leaves a class 1 to 7 decoy out by itself:
     `scale.TEXT_EXEMPT` is computed from the registry over every department
     (`type_registry.text_match_decoy_ids()`, gen#452), so no list in `scale.py` is edited. An id
     no spec owns is declared with its reason in `type_registry.ONE_OFF_TEXT_EXEMPT`;
     `tests/test_retail_text_exempt_452.py` fails a stale or redundant entry;
   * a clothing, footwear or lingerie type (Womens, Mens or Kids) carries its apparel decoy plan
     (gen#311) in the same file: the scaffold writes `apparel=ApparelPlan(compounds=...)` with
     one placeholder compound to edit (three decoys per class; `ApparelPlan(family, per_class,
     compounds)` picks the word family `a` garment, `b` bra, `u` underwear, `s` shoe, `k` sock,
     and more per class; `compounds` are the type's real class 2 names, each `(word, phrase)`
     such as `("vest", "Knitted Vest Top")`, never an invented one; add each new phrase to `REAL_COMPOUNDS` in `tests/test_retail_apparel_decoys_311.py` after the same review, or the census reds). A type that should carry none says
     why: `apparel_exempt="<reason>"` in place of the plan. A beauty type carries neither.
   Worked examples: `type_specs/tracksuit.py` (clothing, an `LRow` with a SKU axis) and
   `type_specs/shampoo.py` (beauty, a derivable breadth type).
3. Check it: `uv run pytest tests/test_retail_type_specs_351.py` (every spec is held to the same
   checks: key equals file name, rows match the type and department, brands have an owner, codes
   are unique, also across specs, the documents meet the output standard).
4. Rebuild the figures (the build writes them; never edit by hand):
   `uv run python prototypes/retail_drawings/retail_figures.py`. It writes
   `golden-retail/stats.json` and `docs/retail-apparel-decoys.md` (the table of the apparel
   decoys, which now lists the new type's). Commit neither: both are rolled by `scripts/merge_pr.sh`
   when the PR merges (README; the `stats-roll` job refuses them), so put them back with
   `git checkout origin/main -- golden-retail/stats.json docs/retail-apparel-decoys.md`.

No edit to `scale.py`, `export.py`, `retail_figures.py`, `decoy_apparel.py`, the registry or any
test is needed, for a beauty type or a clothing one: the registry (`type_registry.py`) finds the
module and feeds the scaled build, the figures and the apparel decoys, and
`tests/test_retail_type_specs_351.py` fails a type that is registered anywhere but a spec file.
`tests/test_retail_type_specs_351.py::test_a_real_scaffolded_clothing_and_beauty_type_pass_the_apparel_census`
puts a scaffolded Kaftan and a scaffolded beauty type into the registry and runs the census of
gen#311 on them, so this claim is measured.

`type_specs/legacy_types.txt` lists the types still registered the old way. It only shrinks:
`type_registry.LEGACY_CEILING` is its exact length, so a line appended to it, or a type moved out
of it without lowering the number, reds `registration_problems`. A migration deletes the type's
line, lowers `LEGACY_CEILING` by one and removes the old row. A clothing type already planned
in `decoy_apparel` (Tracksuit) keeps its plan there: its decoy ids are numbered by place in that
plan, and moving it would renumber the 60 types after it. A new type is numbered by its key.

A type whose product no kit shape draws, or whose decoys sit in another department, follows
[A type with its own drawing shape](#a-type-with-its-own-drawing-shape) below.

## A type with its own drawing shape

Use this when no shape in `kit.SHAPES` draws the product (a garden hose, a yoga block) or when its
text-match decoys are products of other departments. Read this section and ONE worked example, not
the repository:

* `prototypes/retail_drawings/type_specs/garden_hose.py` (commit `bb49c3f`, PR #293): one spec,
  its drawing `garden_hose` in `kit_garden.py`, a measured length axis, decoys in `garden_rows.py`;
* `prototypes/retail_drawings/type_specs/yoga_block.py` (commit `49438fc`, PR #374): seventeen
  Sports & Outdoors types, each a spec of two styles, its drawing in `kit_sports.py`, two
  cross-department decoys each in `decoy_product_words.py`.

There is no part-number block to pick. `ecom-generate block <type_key>` belongs to the industrial
catalog (`docs/adding-a-type.md`); a retail product id is `BRD-<row code>`, one per style, and
`type_registry.specs()` refuses two rows that build one id (the scaffold's `--code` picks another).

### The files

| File | Why |
|---|---|
| `prototypes/retail_drawings/type_specs/<key>.py` | The spec: the rows, the brands' owners, the in-department decoys. Start from a copy of the worked example; the file name is the key. |
| `prototypes/retail_drawings/kit_garden.py` | The drawing function and its place in `SHAPES`, for a Garden type; the same job as the next row for another department (`kit_home.py`, `kit_toys.py`, `kit_household.py`). |
| `prototypes/retail_drawings/kit_sports.py` | The same job for a Sports & Outdoors type; also exports the helpers (`_ell`, `_rect`, `_label`) the garden kit imports. A department with no kit file gets a new `kit_<department>.py`. |
| `prototypes/retail_drawings/export.py` | Read only: `SHARED_OPTIONS` holds the options the types not yet moved into spec files share. A new SKU quantity is declared by the spec (`options=(Option("size_key", "id", "Name", "UNIT"),)`), and a key already in the table is reused. |
| `prototypes/retail_drawings/main_color_hex.py` | Read only: the six main colors (gen#275) every color-bearing type offers across its styles, as plain swatches. |
| `prototypes/retail_drawings/main_colors.py` | `EXCEPTIONS`: one line with a reason, only when the color IS the material (cut flowers, steel cutlery); `complete()` otherwise adds a missing main color as copied SKUs. |
| `prototypes/retail_drawings/tree_guard.py` | Read only: the rules the category path must meet (the type nests under its generic node; no sibling whose label is a word-suffix of another). |
| `prototypes/retail_drawings/decoy_product_words.py` | Class 8 (gen#326): a product of another department whose title holds the shopper's word, one `_s(...)` row per decoy and a `KINDS` entry when its product is not there yet. |
| `prototypes/retail_drawings/garden_rows.py` | Where the Garden department keeps its decoys (gen#294): add the new type's `_QUERY` and `_ABSENT` entries (its query words and the absent word its decoys carry); another department keeps them in its own `*_rows.py`. |
| `prototypes/retail_drawings/retail_figures.py` | Run it, never edit it: it rewrites the two generated files below. |
| `golden-retail/stats.json` | The measured figures of the build; generated, and NOT committed by a PR: `scripts/merge_pr.sh` rolls it at the merge and CI rewrites it before the tests (gen#373). |
| `docs/retail-apparel-decoys.md` | The apparel decoy table; generated, and NOT committed by a PR: it is rolled at the merge and CI rewrites it before the tests (gen#373), whether or not your type is apparel. |
| `docs/retail-product-word-decoys.md` | The class-8 table, pasted from `decoy_product_words.table_markdown()`; `tests/test_retail_product_word_decoys_326.py` holds it verbatim. |
| `docs/retail-sports-tree.md` | The department's tree note (for Garden, `docs/retail-garden.md`); `tests/test_retail_sports_tree_note_290.py` holds that note to the leaves of the Sports rows. |
| `tests/test_retail_type_specs_351.py` | Run, do not edit: every spec meets the same checks (key equals file name, rows match the type, brands have owners, ids are unique). |
| `tests/test_retail_main_colors_275.py` | Run, do not edit: it lists every color-bearing type that lacks a main color without an exception. |
| `tests/test_retail_tree_nesting_283.py` | Run, do not edit: it runs the rules of `tree_guard.py` over the built tree. |
| `tests/test_retail_figures_162.py` | Run, do not edit: it holds `golden-retail/stats.json` to a fresh measurement. |
| `tests/test_retail_sports_265.py` | Add the new type to `KEYS` and `AXES` in this file (a copied type reds two ids until it is there): the Sports department's checks (every type has its range, draws its own shape, carries the six main colors, reaches the scaled build). |
| `tests/test_retail_sports_decoys_368.py` | The decoy census of Sports & Outdoors: a type with fewer than two decoys and no `SPORTS_EXEMPT` entry reds. Garden's is `tests/test_retail_garden_203.py` (`-k at_least_three_decoys`). |
| `scripts/mutation_rows_<topic>.py` | New file: one row per planted defect in the decoys, the drawing or the rule, each naming the test that must go red. The file exposes `PREFIX` (the text before `: ` in each row's name) and `rows()` (a list of `mutation_row.Row`); `scripts/mutation_row.py` finds it by glob, so nothing is imported or listed in `scripts/mutation_check.py` and `tests/test_mutation_rows_glob_506.py` fails if a script names a rows file. |

Not touched: `scale.py`, the registry and `type_specs/legacy_types.txt`. The registry finds the
module and feeds the scaled build; nothing is added to the legacy list.

### In order

1. **Draw it.** A shape is `def name(paint, fill, label, <param>="<first reading>") -> list[str]`
   in the department's kit file: `paint` is what the product's main surface is painted with, `fill.base`
   its color, and `label` goes last (`_label(out, label)` in `kit_sports.py`, `_panel` in
   `kit_garden.py`). A style picks a reading through
   `Row.params=(("style", "coiled"),)`; the default parameter is the first reading, and a test
   (the `test_a_param_changes_the_drawing` pattern) renders two readings and asserts they differ.
   Add it to the file's `SHAPES` dict; the `register(SHAPES)` call at the foot of the file puts the
   dict into `kit.SHAPES`. The spec imports the kit module (`import kit_garden  # noqa: F401 --
   registers garden_hose`), so the shape exists before the row is built. Look at it (import the kit module first, with
   `prototypes/retail_drawings` on `sys.path`): `kit.render("name", kit.Fill("solid", "#c8312e"),
   params={...})`, write the SVG to a file and `rsvg-convert -o shape.png shape.svg`.
2. **Write the rows** in the spec: each style is a `Row` of colors times a SKU axis (`sizes`, or
   the measured `size_key` axis with its unit in the spec's `options=`). The six main colors are spread
   across the styles (every type has red, blue, green, yellow, black and white somewhere, gen#275;
   `tests/test_retail_main_colors_275.py` fails the type that lacks one). The `path` nests under
   the generic category (gen#283). `derivable=False` unless the scaled build should invent styles.
3. **Write the decoys** (gen#294, gen#311, gen#326). Every type carries text-match decoys, and
   among them the subtle ones whose words match by accident ("Red Kite Lawn Mower": a kite on a
   mower's title). Two homes, because a spec's decoys must share the spec's department and
   product type (`type_registry.validate`):
   * the same department and type, classes 1 to 7 (`DECOY_CLASSES` in `type_registry.py`): a
     `Decoy(cls, query, policy, row)` in the spec's `decoys=`; its fields tell the truth and only
     the title or description misleads;
   * another department, class 8: an `_s(n, kind, title, desc, color, noun, target)` row in
     `decoy_product_words.py` with the next free `DY` number, a title that holds the shopper's
     word, no color word in its title or description, and `target` set to your product type. Then
     paste `decoy_product_words.table_markdown()` into `docs/retail-product-word-decoys.md`.
   How many: Sports & Outdoors at least two per type (`SPORTS_EXEMPT` only with an issue named);
   Garden at least three of each of five classes (`garden_rows.py`); Clothing, Footwear and
   Lingerie by their `ApparelPlan`. Elsewhere no test counts them: say in the PR how many you
   planted and why that suffices.
4. **Regenerate** with `uv run python prototypes/retail_drawings/retail_figures.py`, and update
   the department note.
5. **Pin it** with a test file of its own, copied from `tests/test_retail_garden_292.py`: the
   title and department, two styles from two brands, the unit on every SKU, a param that changes
   the drawing, the six colors, the decoys, and no derived copy of a template. Write it first and
   commit it red.

### Tests to run

`tests/test_retail_type_specs_351.py tests/test_retail_main_colors_275.py
tests/test_retail_tree_nesting_283.py tests/test_retail_figures_162.py
tests/test_retail_drawing_honesty.py tests/test_retail_product_word_decoys_326.py
tests/test_retail_sports_265.py`, your own test
file, and the department's census (`tests/test_retail_sports_decoys_368.py` or
`tests/test_retail_garden_292.py`). `tests/test_new_type_quick_path_428.py` fails when a file named
on this page is renamed or removed: fix the page in the same pull request.

## Sizing rule for an issue

At most three types per issue. Split a bigger one: an agent that adds more than three types in
one run has stopped at its context ceiling before (#351: 10 beauty types, no PR).

## Metric

Tokens per type added (about 55K before this page), measured on the next three type issues.

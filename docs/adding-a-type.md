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

* **Breadth type.** One `BreadthRow`, with the same fields as a row of
  `data/breadth_categories.yaml`. The leaf, the drawing, the vocabulary and
  the brand family all follow from the row. `shape` is one of the six plain
  shapes in `drawing/breadth_shapes.py`: `sphere`, `cylinder`, `block`,
  `disc`, `tube` or `bracket`. Example:
  `product_types/raw_materials/ball_stock_precision.py`.
* **Modelled type.** `category`, `standards_family`, `vocab`, `figure` and
  `extent`, `make`, `share`, and optionally `use_lines`. The builder (`make`),
  the vocabulary and the figure usually belong to a family and are shared with
  sibling types. A module must never import `catalog/generate.py` (that is an
  import cycle), so `make` calls the family builder through the generator it
  is handed. Example: `product_types/fasteners/screw_socket_head.py`.

`part_number_block` is left unset unless `sip-generate block` says otherwise
(step 2 below).

The types in `catalog/newtypes.py` (`NEW_TYPES`) are a third kind that no
module can declare yet. They stay where they are for now.

## Modelled types: what the family builder still needs

Only the socket-screw family takes its type's details from the module. Its
builder, `Generator._build_socket_screw`, reads one `standards.SocketScrewLine`
(the metric and inch standards, the head style and name, the head accessor,
and whether length is measured over the head). `screw_socket_head.py` declares
its own as `LINE` and passes it through `make`. A sibling socket screw does
the same and edits nothing in `generate.py`.

Every other family's builder still branches on the type key inside
`catalog/generate.py`, so a new type of that family also edits:

* the builder's type-keyed tables and conditions (for example
  `END_MILL_SERIES_LETTERS[type_key]`, `taxonomy.END_MILL_MATERIALS[type_key]`,
  `type_key == "end_mill_ball"`);
* a new family needs a new builder method on `Generator`, called from the
  module's `make`.

A type built to a standard that has no extraction yet also needs that
standard's rows in `data/fastener_standards.json`; until then the build stops
with `StandardsDataError: no extraction for '<standard>'`.

## The steps

### A new type

1. Write the module. Copy the example of the matching kind and change every
   field.
2. Check the type's part-number block: `uv run sip-generate block <type_key>`.
   It prints the block the key derives and, when another type already uses it,
   the first free block. In that case set `part_number_block=<block>` on the
   new type's `TypeSpec` (not on its `BreadthRow`): about one new type in 135
   collides at today's 67 types. Another open pull request can take the same
   block; `scripts/merge_pr.sh` re-checks it on the merged tree.
3. If the leaf's head noun is new, add it to `PRODUCT_NOUNS` in
   `catalog/names.py`.
4. Build the catalog and regenerate the committed one:
   `uv run sip-generate build --out golden-catalog`. Only the new type's
   records, the totals in `stats.json` and the field-weights YAML should
   change. The independence tests below enforce this.
5. A modelled type only: restate `DEPTH_LINES` and `DEPTH_SKUS` in
   `tests/catalog_size.py` by direct count of the modelled documents, and fix
   the `type_weights` shares (see [What is still shared](#what-is-still-shared)).
   A breadth type edits no pinned count: the breadth part of the catalog's
   size is read from the rows.
6. Run the checks.
7. Merge with `scripts/merge_pr.sh <PR number>`, never with the GitHub button
   or `gh pr merge` (see [Merging](#merging-every-type-pr-goes-through-merge_prsh)).

### Moving an existing type into its own module

The output must stay byte-identical.

1. Find every entry for the key:
   `grep -rn '<type_key>' src/synthetic_industrial_products/catalog src/synthetic_industrial_products/drawing src/synthetic_industrial_products/data`.
   For a modelled type, the entries are in `LEAVES`, `DRAWING` (identity
   pairs), `VOCAB`, `STANDARDS_FAMILY`, `FIGURES`, `USE_LINES`,
   `Generator._BUILDERS`, the `config.type_weights` share, and for a socket
   screw its `_SOCKET_SCREW_LINES` row. For a breadth type, the entry is its
   row in `data/breadth_categories.yaml`.
2. Move each entry into the module's `SPEC`, and delete it from the shared
   table. A key that is declared in both places is refused.
3. Build into a scratch directory and compare:
   `uv run sip-generate build --out /tmp/out && diff -rq golden-catalog /tmp/out`.
   The diff must print nothing.

No test table is edited: the discovery, fresh-reader and first-import tests
are parametrized over `typespec.discover()`, so they pick up the moved module
on their own.

## The commands

```sh
uv run sip-generate block <type_key>                # the block to declare, if any
uv run sip-generate build --out /tmp/out            # about 8 s
diff -rq golden-catalog /tmp/out                    # empty for a move
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
  that holds both changes. Per-type golden slices, which give each type its
  own committed records, are planned for the next part of #48.
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
into it. A conflict confined to the generated files is resolved by the
rebuild; any other conflict (`names.py`) is handed back to you. It then
rebuilds `golden-catalog/`, runs the drift, golden and seam tests
(`scripts/merge_pr.sh --print-checks` lists them), pushes the merged tree to
the PR branch if it differs from the head, and squash-merges only when those
tests are green on that tree, the PR head is still the commit it checked, and
`main` has not moved since the merge. `--dry-run` does all of it except the
push and the merge.

The `main-merged-tree` CI job runs the same tests on every push to `main`, so
a merge that skipped the script is red within minutes.

**Modelled types land one at a time.** Besides the files above, a modelled
type edits shared state that two pull requests cannot both change safely:

* `DEPTH_LINES` and `DEPTH_SKUS` in `tests/catalog_size.py`.
* The `type_weights` shares in `catalog/config.py` together with the modules'
  `share`. They sum to 1.0; `test_the_catalog_is_the_size_it_was_asked_for`
  allows 12 lines of slack and reds once the sum goes further above 1.0, so
  two types each taking share from the others collide.
* `KEY` in `tests/test_catalog_facts.py`.
* The family builder in `catalog/generate.py` (see
  [above](#modelled-types-what-the-family-builder-still-needs)), and the
  standards extraction in `data/fastener_standards.json`.
* Type-keyed tables a family may need. Find them with
  `grep -rn "'<sibling_key>'\|\"<sibling_key>\"" src scripts tests --include=*.py | grep -v product_types/`:
  `render/kinds.py` (`TYPE_KIND`), `render/generic.py`, `catalog/noise.py`
  (`THREADED`), `catalog/conformance.py`, `catalog/compat.py`,
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
| Move 2, `ball_stock_precision` (breadth), cold | 0.45 min to a byte-identical `diff -rq`, 1.2 min to green seam and breadth tests | +48 / -37: a 47-line module, a 1-line family `__init__`, and a 36-line YAML row removed |

A cold move also spends 1 to 2 minutes on the `grep -n` step for a modelled
type, whose entries are spread over 8 tables. A breadth type has one row, so
that step is quick. Each build-and-diff takes about 8 s.

As a guide to size, a breadth type takes about 45 lines and a modelled type
about 35, not counting a new builder, figure or vocabulary.

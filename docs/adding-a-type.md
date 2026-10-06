# How to add a product type

A product type is one leaf of the category tree, such as `screw_socket_head` or
`ball_stock_precision`. Each type is declared in a module of its own under
`src/synthetic_industrial_products/product_types/`. Adding a type adds a file
and edits no shared list, apart from the one exception under
[What is still shared](#what-is-still-shared) (#48).

The build finds the modules by walking the package
(`catalog/typespec.py`, `discover`). The first read of any shared, type-keyed
table (`LEAVES`, `DRAWING`, `VOCAB`, `STANDARDS_FAMILY`, `USE_LINES`,
`FIGURES`) registers every module into those tables, so no caller has to call
a registration step before it reads them.

## The files

| File | When |
|---|---|
| `product_types/<family>/<type_key>.py` | Every type. The file name must equal the key, or discovery refuses it. |
| `product_types/<family>/__init__.py` | Once per family, with a one-line docstring. |
| `catalog/names.py` head-noun list | Only when the leaf's last word (`Ball`, `Bar`, `Screw`) is not listed yet. |

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
  sibling types. Example: `product_types/fasteners/screw_socket_head.py`,
  whose `make` calls `gen._build_socket_screw` through the generator. A module
  must never import `catalog/generate.py`.

`part_number_block` is left unset unless the collision check asks for it (see
[The checks](#the-checks)).

The types in `catalog/newtypes.py` (`NEW_TYPES`) are a third kind that no
module can declare yet. They stay where they are for now.

## The steps

### A new type

1. Write the module. Copy the example of the matching kind and change every
   field.
2. If the leaf's head noun is new, add it to `catalog/names.py`.
3. Build the catalog and regenerate the committed one:
   `uv run sip-generate build --out golden-catalog`. Only the new type's
   records should appear in the diff. The independence tests below enforce
   this.
4. Run the checks.

### Moving an existing type into its own module

The output must stay byte-identical.

1. Find every entry for the key:
   `grep -rn '<type_key>' src/synthetic_industrial_products/catalog src/synthetic_industrial_products/drawing src/synthetic_industrial_products/data`.
   For a modelled type, the entries are in `LEAVES`, `DRAWING` (identity
   pairs), `VOCAB`, `STANDARDS_FAMILY`, `FIGURES`, `USE_LINES`,
   `Generator._BUILDERS`, and the `config.type_weights` share. For a breadth
   type, the entry is its row in `data/breadth_categories.yaml`.
2. Move each entry into the module's `SPEC`, and delete it from the shared
   table. A key that is declared in both places is refused.
3. Build into a scratch directory and compare:
   `uv run sip-generate build --out /tmp/out && diff -rq golden-catalog /tmp/out`.
   The diff must print nothing.
4. If the key is listed in `NOT_YET_MIGRATED` in `tests/test_type_seam.py`,
   remove it. That case is a strict xfail, so it fails until the entry is
   removed.

## The commands

```sh
uv run sip-generate build --out /tmp/out            # about 8 s
diff -rq golden-catalog /tmp/out                    # empty for a move
uv run pytest -q tests/test_type_seam.py tests/test_breadth.py
uv run ruff check . && uv run ruff format --check src tests
uv run pytest -q                                    # the full suite, about 5 min
```

## The checks

| What goes wrong | What refuses it |
|---|---|
| The module name is not the key, or the module has no `SPEC` | `discover` raises `TypeModuleError`, naming the module |
| The module fails to import | `TypeModuleError`, naming the dotted path |
| A modelled type is missing `category`, `vocab`, `figure`, `make` or `standards_family` | `register` raises, naming the missing fields |
| The key is declared twice (in a module and a table, or in two modules) | `TypeCollisionError`, naming the key (and both modules, or the YAML table, where it can) |
| Two types derive the same part-number block | The build refuses and names both types. Set `part_number_block` on the **new** type: re-blocking a type that has already shipped renumbers every SKU it published. |
| A type's output depends on another type | `test_removing_a_type_leaves_every_other_type_byte_identical` and the resize and YAML-edit variants in `tests/test_type_seam.py` |
| The leaf's head noun is not registered | `test_every_category_leaf_ends_in_its_own_product_noun` |
| A reader cannot see a type that has moved | `test_a_fresh_reader_sees_a_migrated_type_without_registering_it` |

## What is still shared

* **The head-noun list** in `catalog/names.py`, when the noun is new.
* **The committed catalog.** `golden-catalog/` holds one file per output
  shape for all types, so two pull requests that each add a type both rewrite
  the same files. Per-type golden slices, which give each type its own
  committed records, are planned for the next part of #48 and are not done yet.

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

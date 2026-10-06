"""The type seam: adding a product type is a new file, and its output is its own.

Several builders add types in parallel pull requests (#34), so a type must
not depend on any other type: not on a shared random stream walked in type
order, not on a shared sequence for part numbers or product ids, not on a
hand-listed registry. Each test here pins one half of that promise
(#48, #27).
"""

from __future__ import annotations

import dataclasses
import json
import random
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from synthetic_industrial_products.catalog import breadth, emit, generate, typespec
from synthetic_industrial_products.catalog.config import SMALL, small
from synthetic_industrial_products.catalog.model import Catalog

#: The two types this seam was proven on: a depth type with its own figure,
#: and a breadth type.
MIGRATED = {
    "screw_socket_head": "fasteners",
    "ball_stock_precision": "raw_materials",
}

#: A type still built from the shared tables: removing a type must leave it
#: unchanged too, or a migration PR would move every unmigrated type.
UNMIGRATED = "end_mill_square"


def _by_type(lines) -> dict[str, list[str]]:
    """Each type's records, serialised exactly as the nested shape publishes them."""
    out: dict[str, list[str]] = {}
    for line in lines:
        docs = emit.iter_nested(Catalog(lines=(line,)), emit.DEFAULT_IMAGE_BASE_URL)
        out.setdefault(line.type_key, []).extend(json.dumps(d, sort_keys=True) for d in docs)
    return out


def _moved_by_removing(removed: str) -> list[str]:
    """Every type whose records change when ``removed`` is left out of the build.

    Each side is built from its own ``small()``: from one shared config, a
    write ``removed`` makes into it reaches both sides and they agree.
    """
    keys = generate.all_type_keys()
    full = _by_type(generate.generate(small()).lines)
    reduced = _by_type(generate.generate(small(), types=[k for k in keys if k != removed]).lines)
    assert removed in full, f"{removed} built nothing at all"
    assert removed not in reduced, f"{removed} was still built after it was removed"
    return sorted(k for k in full if k != removed and full[k] != reduced.get(k))


def _moved_by_changing(changed: str, before: Catalog, after: Catalog) -> list[str]:
    """Every type other than ``changed`` whose records differ between two builds.

    ``changed`` itself must differ, or the edit under test did nothing and the
    empty answer would prove nothing.
    """
    full, edited = _by_type(before.lines), _by_type(after.lines)
    assert full.get(changed) != edited.get(changed), f"the edit did not change {changed}"
    assert set(full) == set(edited), "an edit to one type added or removed another"
    return sorted(k for k in full if k != changed and full[k] != edited[k])


# -- discovery ---------------------------------------------------------------


def _plant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, files: dict[str, str]) -> None:
    """A throwaway type package ``planted_types`` with one family, ``widgets``."""
    family = tmp_path / "planted_types" / "widgets"
    family.mkdir(parents=True)
    (tmp_path / "planted_types" / "__init__.py").write_text("")
    (family / "__init__.py").write_text("")
    for name, text in files.items():
        (family / name).write_text(text)
    monkeypatch.syspath_prepend(str(tmp_path))
    for name in [m for m in sys.modules if m.split(".")[0] == "planted_types"]:
        monkeypatch.delitem(sys.modules, name)


_SPEC = "from synthetic_industrial_products.catalog.typespec import TypeSpec\n"


def test_a_type_module_is_discovered_by_its_dotted_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _plant(tmp_path, monkeypatch, {"blue_widget.py": _SPEC + "SPEC = TypeSpec('blue_widget')\n"})
    specs = typespec.discover("planted_types")
    assert list(specs) == ["blue_widget"]
    assert specs["blue_widget"].module == "planted_types.widgets.blue_widget"


@pytest.mark.parametrize(
    ("text", "refusal"),
    [
        ("X = 1\n", r"planted_types\.widgets\.blue_widget declares no SPEC"),
        (_SPEC + "SPEC = TypeSpec('red_widget')\n", r"blue_widget declares 'red_widget'"),
    ],
)
def test_a_type_module_without_its_own_spec_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str, refusal: str
) -> None:
    _plant(tmp_path, monkeypatch, {"blue_widget.py": text})
    with pytest.raises(typespec.TypeModuleError, match=refusal):
        typespec.discover("planted_types")


#: Every type module, discovered: a new or moved type is covered by the
#: discovery and fresh-reader tests below without an entry in any test table.
DISCOVERED = typespec.discover()


@pytest.mark.parametrize("key", sorted(DISCOVERED))
def test_a_type_module_is_its_types_only_declaration(key: str) -> None:
    module = DISCOVERED[key].module
    family = module.removeprefix(f"{typespec.TYPES_PACKAGE}.").split(".")
    assert len(family) == 2 and family[1] == key, f"{module} is not <family>.{key}"
    # Declared once: its module is the only declaration, not a second copy.
    assert key not in generate.Generator._BUILDERS, f"{key} is still in Generator._BUILDERS"
    assert key not in {row.key for row in breadth.load_rows()}, f"{key} is still a YAML row"


#: Modules that used to register the type modules for every reader after them;
#: a fresh reader that imports none of them must still see a migrated type.
_REGISTERING_CALLERS = (
    "synthetic_industrial_products.catalog.generate",
    "synthetic_industrial_products.catalog.bundle",
)

_FRESH_READER = """
import sys
from synthetic_industrial_products.catalog.taxonomy import LEAVES, drawing_for
from synthetic_industrial_products.catalog.vocab import VOCAB
from synthetic_industrial_products.drawing import FIGURES
key, callers = sys.argv[1], sys.argv[2:]
drawing_for(key), FIGURES[key], LEAVES[key], VOCAB[key]
print([name for name in callers if name in sys.modules])
"""


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", script, *args], capture_output=True, text=True, check=False
    )


@pytest.mark.parametrize("key", sorted(DISCOVERED))
def test_a_fresh_reader_sees_a_migrated_type_without_registering_it(key: str) -> None:
    """The tables register the type modules on their first read, so no caller must.

    Run in a subprocess: in this process something has already read the tables.
    The script imports no caller that used to register (the generator, the image
    bundle; the contact-sheet script is not importable), and checks it did not.
    """
    result = _run(_FRESH_READER, key, *_REGISTERING_CALLERS)
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.strip() == "[]", "the fresh reader imported a registering caller"


#: Each way to read a table, as the FIRST read in a fresh process. A read
#: that skips registration answers from the tables without the type modules.
_READS = {
    "__getitem__": "[LEAVES[k] for k in keys]",
    "get": "[LEAVES.get(k) for k in keys]",
    "__contains__": "[k in LEAVES for k in keys]",
    "__iter__": "sorted(iter(LEAVES))",
    "__len__": "len(LEAVES)",
    "keys": "sorted(LEAVES.keys())",
    "values": "sorted(map(repr, LEAVES.values()))",
    "items": "sorted(map(repr, LEAVES.items()))",
}

_FIRST_READ = """
import sys
from synthetic_industrial_products.catalog import typespec
from synthetic_industrial_products.catalog.taxonomy import LEAVES
keys = sys.argv[2:]
assert not typespec._REGISTRATION["done"], "importing the table registered already"
first = eval(sys.argv[1])
typespec.registered()
assert first == eval(sys.argv[1]), "the first read answered before registering"
"""


@pytest.mark.parametrize("method", sorted(_READS))
def test_every_read_of_a_table_registers_before_it_answers(method: str) -> None:
    result = _run(_FIRST_READ, _READS[method], *sorted(DISCOVERED))
    assert result.returncode == 0, f"{method}: {result.stderr[-1500:]}"


def test_every_read_method_of_a_table_is_one_the_first_read_test_covers() -> None:
    """A read method added to RegistryTable without a hook, or without a case above."""
    overridden = {
        name for name in vars(typespec.RegistryTable) if callable(getattr(dict, name, None))
    }
    assert overridden == set(_READS)


def test_every_shared_type_table_registers_on_read() -> None:
    from synthetic_industrial_products.catalog import taxonomy, vocab, voice
    from synthetic_industrial_products.drawing.figures import FIGURES

    tables = {
        "LEAVES": taxonomy.LEAVES,
        "DRAWING": taxonomy.DRAWING,
        "VOCAB": vocab.VOCAB,
        "STANDARDS_FAMILY": vocab.STANDARDS_FAMILY,
        "USE_LINES": voice.USE_LINES,
        "FIGURES": FIGURES,
        "DECLARED_BLOCKS": typespec.DECLARED_BLOCKS,
    }
    plain = [
        name for name, table in tables.items() if not isinstance(table, typespec.RegistryTable)
    ]
    assert not plain, f"tables a reader can read before registration: {plain}"


_ROWS_FIRST = """
import sys
from synthetic_industrial_products.catalog import breadth, typespec
assert not typespec._REGISTRATION["done"], "importing breadth registered already"
missing = set(sys.argv[1:]) - {row.key for row in breadth.rows()}
assert not missing, f"rows() missed the type modules' rows: {sorted(missing)}"
"""


def test_the_breadth_rows_include_the_type_modules_rows_on_a_first_read() -> None:
    modules = [key for key, spec in DISCOVERED.items() if spec.breadth is not None]
    assert modules, "no breadth type module to read"
    result = _run(_ROWS_FIRST, *modules)
    assert result.returncode == 0, result.stderr[-1500:]


_YAML_ROWS_FIRST = """
import sys
from synthetic_industrial_products.catalog import typespec
# No type module at all, so none imports breadth on registration's behalf.
typespec.discover = lambda package=typespec.TYPES_PACKAGE: {}
from synthetic_industrial_products.catalog.taxonomy import LEAVES
assert "synthetic_industrial_products.catalog.breadth" not in sys.modules
assert sys.argv[1] in LEAVES, "a YAML breadth row is missing from a fresh read"
"""


def test_registration_brings_in_the_yaml_rows_without_any_type_module() -> None:
    result = _run(_YAML_ROWS_FIRST, breadth.load_rows()[0].key)
    assert result.returncode == 0, result.stderr[-1500:]


_READ_DURING_REGISTRATION = """
import sys
from synthetic_industrial_products.catalog import typespec
from synthetic_industrial_products.catalog.taxonomy import LEAVES
found = typespec.discover
def discover(package=typespec.TYPES_PACKAGE):
    # What a type module that reads a shared table at import (a sibling
    # type's vocabulary, say) does while registration is importing it.
    len(LEAVES)
    return found(package)
typespec.discover = discover
LEAVES[sys.argv[1]]
"""


def test_a_table_read_while_registration_runs_is_refused_naming_the_reader() -> None:
    """Mid-registration a table holds only the types registered so far.

    Answering would hand the reader an answer that depends on import order
    (a sibling type's vocabulary missing, a derived block instead of the
    declared one), so the read is refused, naming the line that made it, and
    registration is not started a second time.
    """
    result = _run(_READ_DURING_REGISTRATION, sorted(DISCOVERED)[0])
    assert result.returncode != 0
    assert "RegistrationReadError" in result.stderr, result.stderr[-1500:]
    assert "while the type modules are being registered" in result.stderr
    assert "read at <string>:9" in result.stderr, result.stderr[-1500:]
    assert "RecursionError" not in result.stderr


#: A sibling type module that reads a block at import, as discover imports it
#: (the round-3 review of #54 got 6675 here during registration, 1234 after).
_BLOCK_OF_DURING_REGISTRATION = """
import dataclasses
from synthetic_industrial_products.catalog import breadth, typespec
row = dataclasses.replace(breadth.load_rows()[0], key="planted_rod", part_number_block=None)
spec = typespec.TypeSpec("planted_rod", breadth=row, module="x.planted_rod", part_number_block=1234)
seen = []
def discover(package=typespec.TYPES_PACKAGE):
    try:
        seen.append(typespec.block_of("planted_rod"))
    except Exception as refused:
        seen.append(f"{type(refused).__name__}: {refused}")
    return {"planted_rod": spec}
typespec.discover = discover
seen.append(typespec.block_of("planted_rod"))
print(repr(seen))
"""


def test_block_of_read_during_registration_is_refused_not_answered_by_import_order() -> None:
    assert typespec.part_number_block("planted_rod") != 1234
    result = _run(_BLOCK_OF_DURING_REGISTRATION)
    assert result.returncode == 0, result.stderr[-1500:]
    during, after = eval(result.stdout)  # noqa: S307 - our own repr of two values
    assert isinstance(during, str) and during.startswith("RegistrationReadError"), (
        f"block_of answered {during!r} during registration"
    )
    assert after == 1234


@pytest.mark.parametrize(
    "key",
    sorted(
        key
        for key, spec in DISCOVERED.items()
        if spec.breadth is None and key not in SMALL.type_weights
    ),
)
def test_a_type_modules_share_sizes_its_type(key: str) -> None:
    """With no ``type_weights`` entry, the module's ``share`` is the type's weight.

    Without that fallback the type builds only its must-stock lines, and every
    other check still passes.
    """
    built = generate.generate(SMALL, types=[key]).lines
    assert len(built) >= round(SMALL.lines * DISCOVERED[key].share)


@pytest.mark.parametrize(
    "key", sorted(key for key, spec in DISCOVERED.items() if spec.breadth is None)
)
def test_a_modelled_module_is_registered_into_every_table(key: str) -> None:
    from synthetic_industrial_products.catalog import price, taxonomy, vocab, voice
    from synthetic_industrial_products.drawing.figures import FIGURES

    spec = DISCOVERED[key]
    assert taxonomy.LEAVES[key] == (spec.category,)
    assert taxonomy.DRAWING[key] == key
    assert vocab.VOCAB[key] == spec.vocab
    assert vocab.STANDARDS_FAMILY[key] == spec.standards_family
    assert FIGURES[key] == (spec.figure, spec.extent)
    assert voice.USE_LINES.get(key) == (spec.use_lines or None)
    assert price.MODELS[key] == spec.price


# -- the refusals docs/adding-a-type.md promises ------------------------------


def _modelled(**changes) -> typespec.TypeSpec:
    """A complete modelled spec for a type no table holds, with ``changes``."""
    base = dataclasses.replace(
        DISCOVERED["screw_socket_head"], key="planted_widget", module="planted.planted_widget"
    )
    return dataclasses.replace(base, **changes)


@pytest.mark.parametrize(
    ("field", "unset"),
    [
        ("category", ()),
        ("standards_family", ""),
        ("vocab", ()),
        ("figure", None),
        ("extent", (0.0, 0.0)),
        # Half-zero: one unset side draws every SKU flat, as silently as both.
        ("extent", (2.75, 0.0)),
        ("extent", (0.0, 2.75)),
        ("make", None),
        ("share", 0.0),
        ("price", None),
    ],
)
def test_a_modelled_spec_missing_a_field_is_refused_naming_it(field: str, unset: object) -> None:
    with pytest.raises(typespec.TypeModuleError, match=rf"planted_widget declares no {field}\b"):
        typespec.register(_modelled(**{field: unset}))


def test_a_breadth_spec_whose_row_has_another_key_is_refused() -> None:
    row = breadth.row_for("shaft_collars")
    spec = typespec.TypeSpec("planted_widget", breadth=row, module="planted.planted_widget")
    with pytest.raises(
        typespec.TypeModuleError, match=r"'planted_widget' with a breadth row for 'shaft_collars'"
    ):
        typespec.register(spec)


def test_a_type_module_row_that_repeats_a_yaml_row_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(breadth, "_ROWS", breadth.rows())
    with pytest.raises(typespec.TypeCollisionError, match=r"'shaft_collars' is declared both"):
        breadth.add_row(breadth.row_for("shaft_collars"))


def test_every_type_is_built_once() -> None:
    keys = generate.all_type_keys()
    assert len(keys) == len(set(keys))
    assert set(DISCOVERED) <= set(keys)
    assert UNMIGRATED in keys


def test_a_type_module_that_fails_to_import_names_itself(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _plant(tmp_path, monkeypatch, {"broken_widget.py": "raise RuntimeError('planted')\n"})
    with pytest.raises(typespec.TypeModuleError, match=r"planted_types\.widgets\.broken_widget"):
        typespec.discover("planted_types")


# -- per-type determinism ----------------------------------------------------


def test_part_number_block_is_a_function_of_the_type_key_alone() -> None:
    block = typespec.part_number_block("screw_socket_head")
    assert 1000 <= block <= 9999
    assert block == typespec.part_number_block("screw_socket_head")
    assert block != typespec.part_number_block("screw_flat_head")


def test_a_declared_block_replaces_the_derived_one() -> None:
    """The fix a collision refusal asks for: the type states its own block."""
    assert typespec.part_number_block("er_collets") == typespec.part_number_block(
        "tap_spiral_point"
    )
    assert typespec.block_of("er_collets") != typespec.block_of("tap_spiral_point")


def _yaml_declared_blocks() -> dict[str, int]:
    text = (Path(breadth.__file__).parent.parent / "data" / "breadth_categories.yaml").read_text()
    return {
        raw["key"]: raw["part_number_block"]
        for raw in yaml.safe_load(text)
        if "part_number_block" in raw
    }


_BLOCK_OF_FIRST = """
import sys
from synthetic_industrial_products.catalog import typespec
# No type module at all, so none imports breadth on block_of's behalf.
typespec.discover = lambda package=typespec.TYPES_PACKAGE: {}
assert "synthetic_industrial_products.catalog.breadth" not in sys.modules
print(typespec.block_of(sys.argv[1]))
"""


@pytest.mark.parametrize("key", sorted(_yaml_declared_blocks()))
def test_block_of_as_a_first_read_sees_a_yaml_declared_block(key: str) -> None:
    """Not only when some type module happens to import ``breadth`` first."""
    result = _run(_BLOCK_OF_FIRST, key)
    assert result.returncode == 0, result.stderr[-1500:]
    assert int(result.stdout) == _yaml_declared_blocks()[key]
    assert int(result.stdout) != typespec.part_number_block(key)


_MODULE_BLOCK = """
import dataclasses, sys
from synthetic_industrial_products.catalog import breadth, typespec
row = dataclasses.replace(breadth.load_rows()[0], key="planted_rod", part_number_block=None)
spec = typespec.TypeSpec("planted_rod", breadth=row, module="planted.planted_rod")
if sys.argv[1] == "row":
    spec = dataclasses.replace(spec, breadth=dataclasses.replace(row, part_number_block=1234))
else:
    spec = dataclasses.replace(spec, part_number_block=1234)
typespec.discover = lambda package=typespec.TYPES_PACKAGE: {"planted_rod": spec}
print(typespec.block_of("planted_rod"))
"""


@pytest.mark.parametrize("declared_on", ["row", "spec"])
def test_a_breadth_modules_declared_block_is_its_block(declared_on: str) -> None:
    """On its ``BreadthRow`` or on its ``TypeSpec``: both are the type's block."""
    assert typespec.part_number_block("planted_rod") != 1234
    result = _run(_MODULE_BLOCK, declared_on)
    assert result.returncode == 0, result.stderr[-1500:]
    assert result.stdout.strip() == "1234"


@pytest.mark.parametrize(
    ("start", "used", "free"),
    [
        (4321, {1000, 9999}, 4321),
        (4321, {4321, 4322}, 4323),
        (9998, {9998, 9999, 1000}, 1001),
    ],
    ids=["start-is-free", "skips-taken", "wraps-past-9999"],
)
def test_first_free_block_is_the_first_unused_block_at_or_after_start(
    start: int, used: set[int], free: int
) -> None:
    assert typespec.first_free_block(start, used) == free


def test_first_free_block_refuses_when_every_block_is_used() -> None:
    with pytest.raises(typespec.TypeCollisionError, match=r"all 9000 part-number blocks"):
        typespec.first_free_block(4321, range(1000, 10000))


def _block_command(key: str, capsys: pytest.CaptureFixture[str]) -> str:
    from synthetic_industrial_products.catalog import cli

    assert cli.main(["block", key]) == 0
    return capsys.readouterr().out.strip()


def _blocks_in_use(*, besides: str) -> set[int]:
    return {typespec.block_of(key) for key in generate.all_type_keys() if key != besides}


def test_the_block_command_says_a_free_derived_block_is_free(
    capsys: pytest.CaptureFixture[str],
) -> None:
    key = "planted_widget"
    assert typespec.part_number_block(key) not in _blocks_in_use(besides=key)
    out = _block_command(key, capsys)
    assert out == (
        f"{key}: derived block {typespec.part_number_block(key):04d} is free; "
        "leave part_number_block unset"
    )


def test_the_block_command_names_the_owner_and_a_really_free_block(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A key that collides today: its derived block is ``ball_stock_precision``'s."""
    key = "shim_stock_precision"
    derived = typespec.part_number_block(key)
    assert derived == typespec.block_of("ball_stock_precision")
    used = _blocks_in_use(besides=key)
    out = _block_command(key, capsys)
    assert f"derived block {derived:04d} is taken by ball_stock_precision;" in out
    told = int(out.split("declare part_number_block=")[1].split(",")[0])
    assert told not in used, f"told to declare {told}, which a type already uses"
    assert all(block in used for block in range(derived, told)), "not the FIRST free block"


def test_the_block_command_reports_a_block_already_declared(
    capsys: pytest.CaptureFixture[str],
) -> None:
    declared = _yaml_declared_blocks()["er_collets"]
    out = _block_command("er_collets", capsys)
    assert out == f"er_collets: already declares part_number_block={declared:04d}"


def test_every_types_skus_and_product_ids_carry_its_own_block() -> None:
    for line in generate.generate(SMALL).lines:
        block = f"{typespec.block_of(line.type_key):04d}"
        assert f"-{block}-" in line.product_id, (line.type_key, line.product_id)
        for child in line.children:
            assert child.sku.startswith(block), (line.type_key, child.sku)


# -- independence ------------------------------------------------------------


@pytest.mark.parametrize("removed", [*sorted(MIGRATED), UNMIGRATED])
def test_removing_a_type_leaves_every_other_type_byte_identical(removed: str) -> None:
    moved = _moved_by_removing(removed)
    assert not moved, f"removing {removed} changed {len(moved)} other type(s): {moved[:8]}"


@pytest.mark.parametrize(
    ("resized", "knob"),
    [(UNMIGRATED, "type_weights"), ("nut_hex", "new_type_share")],
)
def test_resizing_a_type_leaves_every_other_type_byte_identical(resized: str, knob: str) -> None:
    """A type's size is its own share of ``lines``, never a share of a total
    that every other type's share is also part of (config.py)."""
    shares = getattr(SMALL, knob)
    bigger = dataclasses.replace(SMALL, **{knob: {**shares, resized: shares[resized] * 1.3}})
    moved = _moved_by_changing(resized, generate.generate(SMALL), generate.generate(bigger))
    assert not moved, f"resizing {resized} changed {len(moved)} other type(s): {moved[:8]}"


def test_editing_one_yaml_row_leaves_every_other_type_byte_identical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A breadth row's edit is that row's alone, like a type module's."""
    edited = "shaft_collars"
    before = generate.generate(SMALL)
    rows = tuple(
        dataclasses.replace(row, price_range=(40.0, 90.0)) if row.key == edited else row
        for row in breadth.rows()
    )
    assert rows != breadth.rows(), f"no {edited} row to edit"
    monkeypatch.setattr(breadth, "_ROWS", rows)
    moved = _moved_by_changing(edited, before, generate.generate(SMALL))
    assert not moved, f"editing the {edited} row changed {len(moved)} other type(s): {moved[:8]}"


def test_a_planted_shared_random_stream_is_caught(monkeypatch: pytest.MonkeyPatch) -> None:
    """The independence check bites: one stream shared by every type moves them all."""
    shared = random.Random(SMALL.seed)
    # The planted stream is reseeded once per BUILD, not per type, so a type's
    # draws depend on every type built before it.
    calls = {"n": 0}

    def once_per_build(seed, key):
        if calls["n"] == 0:
            shared.seed(seed)
        calls["n"] += 1
        return shared

    monkeypatch.setattr(typespec, "type_rng", once_per_build)
    keys = generate.all_type_keys()
    assert keys, "no types to build"
    first = keys[0]
    calls["n"] = 0
    full = _by_type(generate.generate(SMALL).lines)
    calls["n"] = 0
    reduced = _by_type(generate.generate(SMALL, types=[k for k in keys if k != first]).lines)
    moved = [k for k in full if k != first and full[k] != reduced.get(k)]
    assert moved, "a stream shared across types went unnoticed by the independence check"


def test_the_whole_build_is_the_per_type_builds_concatenated() -> None:
    """Why one process per type is safe: assembling the parts gives the whole."""
    whole = generate.generate(SMALL).lines
    keys = generate.all_type_keys()
    parts = [line for key in keys for line in generate.generate_type(SMALL, key)]
    assert [line.product_id for line in whole] == [line.product_id for line in parts]
    assert _by_type(whole) == _by_type(parts)


# -- collisions --------------------------------------------------------------


def test_two_types_with_one_block_are_refused_naming_both() -> None:
    with pytest.raises(typespec.TypeCollisionError, match=r"alpha_widget.*beta_widget"):
        typespec.check_collisions({"alpha_widget": 4321, "beta_widget": 4321, "gamma": 1234})


def test_a_build_whose_types_collide_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(typespec, "block_of", lambda key: 4321)
    with pytest.raises(typespec.TypeCollisionError) as refused:
        generate.generate(SMALL)
    named = [key for key in generate.all_type_keys() if key in str(refused.value)]
    assert len(named) >= 2, f"the refusal must name both types: {refused.value}"


def test_a_collision_refusal_says_where_each_kind_of_type_is_fixed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A YAML type is re-blocked on its row, a code type in its module, and the
    refusal steers the fix onto the NEW type: re-blocking a shipped one
    renumbers every SKU it has published."""
    derived = typespec.block_of
    clash = {"shaft_collars", UNMIGRATED}
    monkeypatch.setattr(typespec, "block_of", lambda key: 4321 if key in clash else derived(key))
    with pytest.raises(typespec.TypeCollisionError) as refused:
        generate.generate(SMALL)
    text = str(refused.value)
    assert "part_number_block: <block> on the shaft_collars row of" in text
    assert "data/breadth_categories.yaml" in text
    assert f"TypeSpec('{UNMIGRATED}', ...) in {typespec.TYPES_PACKAGE}" in text
    assert "NEWLY ADDED" in text


def _raw_row(key: str) -> dict:
    text = (Path(breadth.__file__).parent.parent / "data" / "breadth_categories.yaml").read_text()
    return next(raw for raw in yaml.safe_load(text) if raw["key"] == key)


def test_a_quoted_yaml_block_is_refused_naming_its_row() -> None:
    raw = {**_raw_row("shaft_collars"), "part_number_block": "4659"}
    with pytest.raises(typespec.TypeCollisionError, match=r"the shaft_collars row of .*'4659'"):
        breadth._row_from_dict(raw)


def test_a_non_integer_block_is_a_named_refusal_not_a_type_error() -> None:
    blocks: dict = {"alpha_widget": 4321, "beta_widget": "4659"}
    with pytest.raises(
        typespec.TypeCollisionError, match=r"beta_widget's part-number block '4659'"
    ):
        typespec.check_collisions(blocks)


def test_a_builder_needs_a_known_type() -> None:
    """No builder draws from a stream or block the collision check never saw."""
    with pytest.raises(TypeError):
        generate.Generator(SMALL)  # type: ignore[call-arg]
    for key in ("", "no_such_widget"):
        with pytest.raises(ValueError, match="no product type"):
            generate.Generator(SMALL, key)

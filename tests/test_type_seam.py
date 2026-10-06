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
import sys
from pathlib import Path

import pytest
import yaml

from synthetic_industrial_products.catalog import breadth, emit, generate, typespec
from synthetic_industrial_products.catalog.config import SMALL
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
    """Every type whose records change when ``removed`` is left out of the build."""
    keys = generate.all_type_keys()
    full = _by_type(generate.generate(SMALL).lines)
    reduced = _by_type(generate.generate(SMALL, types=[k for k in keys if k != removed]).lines)
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


#: Types in :data:`MIGRATED` whose module is not written yet. Strict, so the
#: migration that writes one turns its case red until it leaves this set.
NOT_YET_MIGRATED = {"ball_stock_precision"}


@pytest.mark.parametrize(
    ("key", "family"),
    [
        pytest.param(
            key,
            family,
            marks=[pytest.mark.xfail(strict=True, reason="its module is the next step of #48")]
            if key in NOT_YET_MIGRATED
            else [],
        )
        for key, family in sorted(MIGRATED.items())
    ],
)
def test_a_migrated_type_is_discovered_from_its_own_module(key: str, family: str) -> None:
    specs = typespec.discover()
    assert key in specs, f"{key} is not discovered under {typespec.TYPES_PACKAGE}"
    assert specs[key].module == f"{typespec.TYPES_PACKAGE}.{family}.{key}"
    # Declared once: its module is the only declaration, not a second copy.
    assert key not in generate.Generator._BUILDERS, f"{key} is still in Generator._BUILDERS"
    assert key not in {row.key for row in breadth.load_rows()}, f"{key} is still a YAML row"


def test_every_type_is_built_once() -> None:
    keys = generate.all_type_keys()
    assert len(keys) == len(set(keys))
    assert set(MIGRATED) <= set(keys)
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
        for row in breadth.ROWS
    )
    assert rows != breadth.ROWS, f"no {edited} row to edit"
    monkeypatch.setattr(breadth, "ROWS", rows)
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

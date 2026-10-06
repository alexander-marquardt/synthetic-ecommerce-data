"""The type seam: adding a product type is a new file, and its output is its own.

Several builders add types in parallel pull requests (#34), so a type must
not depend on any other type: not on a shared random stream walked in type
order, not on a shared sequence for part numbers or product ids, not on a
hand-listed registry. Each test here pins one half of that promise
(#48, #27).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pytest

from synthetic_industrial_products.catalog import emit, generate, typespec
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

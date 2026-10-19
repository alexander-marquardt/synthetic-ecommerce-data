"""The 26 footwear types register as type specs, not on the legacy list (gen#427).

Footwear was the one family kept on ``type_specs/legacy_types.txt``, because a ``FootwearStyle``
(a size chart per audience, an upper per color, ``axes()`` drawing params) is not a spec ``Row``.
A ``FootwearRow(Row)`` carries the style, as ``LRow`` carries a third SKU axis, so the shoe types
register like any other and ``LEGACY_CEILING`` drops by their 26. The three care products
(Shoe Care Kit, Shoe Laces, Shoe Polish) are not shoes and stay where they were.

The refactor changes no document: the spec rows build the same documents as
``footwear_rows.docs()``, and the scaled build may still derive from them.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import footwear_rows as fw  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402
from breadth_rows import Row  # noqa: E402

#: The product types of the 26 shoe kinds, spelled out so a kind dropped from ``TYPES`` is seen.
SHOE_TYPES = (
    "Ankle Boots", "Ballet Pumps", "Barefoot Shoes", "Block Heels", "Brogues", "Chelsea Boots",
    "Chukka Boots", "Clogs", "Court Shoes", "Espadrilles", "Jelly Shoes", "Kitten Heels",
    "Knee High Boots", "Loafers", "Mules", "Platform Trainers", "Plimsolls", "Running Shoes",
    "Safety Boots", "Sandals", "School Shoes", "Slippers", "Trainers", "Walking Boots", "Wedges",
    "Wellies",
)  # fmt: skip
CARE_TYPES = ("Shoe Care Kit", "Shoe Laces", "Shoe Polish")
#: The legacy list held 333 types before; the 26 shoe types leave it.
CEILING = 333 - 26


def _spec_for(ptype: str):
    return next(
        (s for s in type_registry.specs().values()
         if (s.department, s.product_type) == ("Footwear", ptype)),
        None,
    )  # fmt: skip


def _json(doc: dict) -> str:
    return json.dumps(doc, sort_keys=True, ensure_ascii=False)


def test_the_shoe_types_are_the_26_kinds() -> None:
    assert sorted(t[0] for t in fw.TYPES.values()) == sorted(SHOE_TYPES)


@pytest.mark.parametrize("ptype", SHOE_TYPES)
def test_a_shoe_type_is_a_spec_and_not_on_the_legacy_list(ptype: str) -> None:
    assert ("Footwear", ptype) not in type_registry.legacy_types(), ptype
    spec = _spec_for(ptype)
    assert spec is not None, f"{ptype} has no spec file"
    assert spec.rows, ptype
    assert all(r.product_type == ptype for r in spec.rows), ptype


@pytest.mark.parametrize("ptype", CARE_TYPES)
def test_a_care_product_stays_on_the_legacy_list(ptype: str) -> None:
    assert ("Footwear", ptype) in type_registry.legacy_types()
    assert _spec_for(ptype) is None


def test_the_ceiling_dropped_by_the_26_shoe_types_and_stays_exact() -> None:
    legacy = type_registry.legacy_types()
    assert type_registry.LEGACY_CEILING == CEILING
    assert len(legacy) == CEILING
    built = {(str(d["department"][0]), str(d["product_type"]))
             for d in scale.templates(baseline=False)}  # fmt: skip
    assert type_registry.registration_problems(built) == []


def test_a_footwear_row_is_a_spec_row_that_carries_its_style() -> None:
    cls = getattr(fw, "FootwearRow", None)
    assert cls is not None, "footwear_rows has no FootwearRow"
    assert issubclass(cls, Row)
    style = fw.FOOTWEAR[0]
    row = cls.of(style)
    assert (row.code, row.department, row.product_type) == (
        style.code, "Footwear", fw.TYPES[style.kind][0])
    assert row.skus() == style.skus()
    assert row.product_id == f"FTW-{style.code}"


def test_the_spec_rows_build_the_documents_footwear_rows_built() -> None:
    """Every style's document is the same byte for byte: the rank and badges included."""
    wanted = {d["product_id"]: _json(d) for d in fw.docs()}
    got = {
        d["product_id"]: _json(d)
        for d in type_registry.docs()
        if d["product_id"].startswith("FTW-")
    }
    assert got == wanted
    assert len(got) == len(fw.FOOTWEAR) == 55


def test_the_docs_are_the_callers_own_copies() -> None:
    spec = _spec_for("Trainers")
    assert spec is not None
    first = spec.docs()[0]
    pristine = copy.deepcopy(first)
    first["title"] = "changed"
    first["skus"].clear()
    assert spec.docs()[0] == pristine


def test_the_footwear_ids_are_built_once_and_stay_derivable() -> None:
    ids = {f"FTW-{s.code}" for s in fw.FOOTWEAR}
    owned = set()
    for ptype in SHOE_TYPES:
        spec = _spec_for(ptype)
        assert spec is not None, ptype
        assert spec.derivable, ptype
        owned |= type_registry.ids_of(spec)
    assert owned == ids
    assert not ids & type_registry.left_out_ids()
    tpls = scale.templates(baseline=False)
    type_registry.check_unique_ids(tpls)
    assert ids <= {r["product_id"] for r in scale.derivable(tpls)}

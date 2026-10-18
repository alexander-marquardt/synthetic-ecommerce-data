"""The retail export loads whole into the Combined index (gen#279).

The Combined loader (``scripts/load_combined_catalog.py`` in prism-industrial-products)
projects the retail flat export through ``combined_catalog.retail_document`` before it
writes, and REFUSES a SKU the projection cannot place. A scaled export built at 110,428
SKUs lost 363 of them to two refusals, both written at the source here:

* a handbag's size ``Mini`` is no size system (``retail_size_key``: ``matches no size
  system``);
* a skirt's ``length`` variant axis (Short/Petite, Regular, Long) is renamed to
  ``garment_length`` by the projection, where the style already wrote ``garment_length``
  = ``Midi`` (``retail_renamed``: ``a renamed retail key would write``).

This file holds the two checks the projection runs, as functions of a flat document, and
runs them over every authored style's SKUs. The projection is another repository, so
``SIZE_SHAPES`` and ``RENAMED_KEYS`` below are a MIRROR of its ``_SIZE_SYSTEMS`` and
``RENAMED_RETAIL_KEYS`` (and the dimension, height and amount shapes beside them), as of
prism-industrial-products ``combined_catalog.py``. A shape the projection learns is a row
added here with it; a shape missing here only makes this check stricter than the loader.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core import standard  # noqa: E402

#: The bare retail keys the projection renames, and what each becomes.
RENAMED_KEYS = {"length": "garment_length", "width": "fit_width"}

#: Every value shape a retail ``size`` may take: the projection's size systems (letter,
#: tights span, age, UK dress or bra, towel), then a ``dimensions``, a height and an amount.
SIZE_SHAPES = tuple(
    re.compile(p)
    for p in (
        r"^(XXS|XS|S|M|L|XL|XXL|XXXL|Small|Medium|Large)$",
        r"^(S/M|M/L|L/XL)$",
        r"^\d{1,2}(-\d{1,2})? Yrs$",
        # A baby's age in months (gen#213): NOT yet a size system of the projection, which
        # refuses it until it learns the row (prism-industrial-products#592).
        r"^(Newborn|\d{1,2}-\d{1,2} Mths)$",
        r"^(\d{1,2}|\d{2}[A-K]{1,2})$",
        r"^(Hand Towel|Bath Towel|Bath Sheet)$",
        r"^\d+(\.\d+)? x \d+(\.\d+)? ?(cm|in)$",
        r"^\d+(\.\d+)? ?(cm|m)$",
        r"^(\d+ x )?\d+(\.\d+)? ?(g|kg|ml|L)$",
    )
)


def refused_sizes(flat: Mapping[str, Any]) -> list[str]:
    """The SKU's ``size`` values that match no size system: the projection refuses each."""
    return [
        str(a["value"])
        for a in flat["attributes"]
        if a["key"] == "size" and not any(p.match(str(a["value"])) for p in SIZE_SHAPES)
    ]


def colliding_renames(flat: Mapping[str, Any]) -> list[str]:
    """What the projection's rename would write over a key the SKU already writes
    differently: ``length`` becomes ``garment_length``, so a SKU with both is refused."""
    values: dict[str, set[str]] = {}
    for a in flat["attributes"]:
        values.setdefault(a["key"], set()).add(str(a["value"]))
    out = []
    for old, new in RENAMED_KEYS.items():
        if old in values and new in values and values[old] != values[new]:
            out.append(f"{old}={sorted(values[old])} would overwrite {new}={sorted(values[new])}")
    return out


def _flat(attributes: Iterable[tuple[str, str]]) -> dict[str, Any]:
    return {"attributes": [{"key": k, "name": k, "value": v} for k, v in attributes]}


@pytest.fixture(scope="module")
def flat_documents() -> list[dict[str, Any]]:
    """One flat document per SKU of every authored style: the shape the loader reads."""
    docs = [export.standard_document(rec) for rec in scale.templates()]
    return [row for doc in docs for row in standard.flat_documents(doc, export.NUMERIC_FACTS)]


def test_the_size_check_refuses_a_bag_size_and_passes_the_sizes_other_bags_use() -> None:
    assert refused_sizes(_flat([("size", "Mini")])) == ["Mini"]
    for size in ("Small", "Medium", "M", "10", "32B", "Bath Towel", "1.2 m", "18 x 23 cm"):
        assert refused_sizes(_flat([("size", size)])) == [], size


def test_the_rename_check_refuses_a_second_garment_length_and_passes_an_equal_one() -> None:
    both = _flat([("garment_length", "Midi"), ("length", "Short/Petite")])
    assert len(colliding_renames(both)) == 1
    assert colliding_renames(_flat([("garment_length", "Midi"), ("length", "Midi")])) == []
    assert colliding_renames(_flat([("garment_length", "Midi"), ("fit_length", "Long")])) == []
    assert len(colliding_renames(_flat([("fit_width", "Slim"), ("width", "Wide")]))) == 1


def test_no_authored_sku_has_a_size_the_combined_loader_refuses(
    flat_documents: list[dict[str, Any]],
) -> None:
    refused: dict[str, set[str]] = {}
    for flat in flat_documents:
        for size in refused_sizes(flat):
            refused.setdefault(size, set()).add(flat["product_id"])
    assert refused == {}, {size: sorted(ids) for size, ids in refused.items()}


def test_no_authored_sku_writes_a_renamed_key_twice(
    flat_documents: list[dict[str, Any]],
) -> None:
    clashes = {}
    for flat in flat_documents:
        found = colliding_renames(flat)
        if found:
            clashes[flat["product_id"]] = found
    assert clashes == {}, clashes

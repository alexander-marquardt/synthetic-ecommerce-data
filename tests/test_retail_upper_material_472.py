"""A shoe's ``upper_material`` is one Title Case entry per material (gen#472).

The style used to carry ONE attribute, ``leather, suede, patent``: a facet listed that string as a
value, so a shopper who filtered on Leather did not find the ballet shoe with a leather color, and
the value was lowercase beside the Title Case values of every other key. Each material is now its
own entry, in the style's attributes and on its SKUs alike.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core import standard  # noqa: E402
from test_retail_scale import TARGET  # noqa: E402  (TEMPLATE_SKUS + DERIVED_SKUS)

KEY = "upper_material"

#: The five styles the issue names, which carry two or three materials among their colors.
MIXED = {
    "FTW-WBALLT": {"Leather", "Suede", "Patent"},
    "FTW-WCRTST": {"Patent", "Suede"},
    "FTW-WBLKAS": {"Suede", "Leather"},
    "FTW-MSAFS3": {"Leather", "Nubuck"},
    "FTW-KSCHLL": {"Leather", "Patent"},
}


@pytest.fixture(scope="module")
def documents() -> list[dict]:
    """The authored export, then the derived styles of a build sized to the derived range
    (TARGET = every template SKU plus the derived ones; a smaller build is a prefix of the
    templates and derives nothing): a derived shoe copies its template's materials, so the
    derivation is held to the rule too."""
    built = scale.build(TARGET).records[len(scale.templates()) :]
    derived = [export.standard_document(r) for r in built]
    return [*export.documents(), *derived]


def test_the_derived_part_of_the_build_holds_shoes(documents):
    """A floor, so a build that shrinks back into the templates fails loudly instead of
    leaving the derived half of the checks above with nothing to check."""
    authored = {d["product_id"] for d in export.documents()}
    derived_shoes = [d for d in documents if d["product_id"] not in authored and _style_values(d)]
    assert len(derived_shoes) >= 30


def _style_values(doc: dict) -> list[str]:
    return [a["value"] for a in doc["attributes"] if a["key"] == KEY]


def _sku_values(doc: dict) -> list[str]:
    return [a["value"] for v in doc["variants"] for a in v["attributes"] if a["key"] == KEY]


def test_no_upper_material_value_holds_a_comma_or_starts_lowercase(documents):
    bad = []
    seen = 0
    for d in documents:
        for v in (*_style_values(d), *_sku_values(d)):
            seen += 1
            if "," in v or not v[:1].isupper():
                bad.append((d["product_id"], v))
    assert seen >= 55
    assert bad == []


def test_a_style_lists_one_entry_per_material_its_skus_carry(documents):
    wrong = []
    shoes = 0
    for d in documents:
        entries = _style_values(d)
        if not entries:
            continue
        shoes += 1
        if sorted(entries) != sorted(set(_sku_values(d))):
            wrong.append((d["product_id"], entries, sorted(set(_sku_values(d)))))
    assert shoes >= 55
    assert wrong == []


@pytest.mark.parametrize("pid", sorted(MIXED))
def test_the_named_style_carries_each_of_its_materials_as_its_own_entry(documents, pid):
    doc = next(d for d in documents if d["product_id"] == pid)
    assert len(_style_values(doc)) == len(MIXED[pid])
    assert set(_style_values(doc)) == MIXED[pid]


def test_the_check_catalog_text_check_passes_on_the_authored_export():
    assert standard.check_catalog(
        export.documents(), one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT
    ) == []

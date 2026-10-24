"""Every retail type that carries a net volume offers several (gen#347).

A "Net volume" facet with one option demos nothing, and a title that states a volume the
record does not carry drops the product from the facet. Both are counted over the authored
templates of ``scale.templates()``: a derived style keeps its template's volume, so a type
with three volumes among its templates has them at every size the build reaches.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from functools import cache
from pathlib import Path

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402

#: The fewest distinct net volumes a type that carries the field offers.
MINIMUM = 3

#: category path -> why one fixed size is genuinely how the type is sold. Empty on purpose: a
#: type that is not here offers MINIMUM volumes, and an entry that the catalogue outgrows is
#: refused below, so the list cannot rot.
EXCEPTIONS: dict[tuple[str, ...], str] = {}

#: A volume a title states: "500ml", "1.5L", "1L". Deliberately not imported from
#: ``net_volume.py``: this copy is the guard's independent oracle, so do not merge the two.
TITLE_VOLUME = re.compile(r"\b(\d+(?:\.\d+)?) ?(ml|L)\b")


@cache
def docs() -> tuple[dict, ...]:
    return tuple(scale.standard_document(r) for r in scale.templates())


def volumes(doc: dict) -> set[float]:
    """The net volumes (ml) a document states on the product or on any of its variants."""
    entries = [*doc["attributes"], *(e for v in doc["variants"] for e in v["attributes"])]
    return {float(e["value"]) for e in entries if e["key"] == "net_volume"}


@cache
def per_type() -> dict[tuple[str, ...], set[float]]:
    held: dict[tuple[str, ...], set[float]] = defaultdict(set)
    for d in docs():
        if found := volumes(d):
            held[tuple(d["category_path"])] |= found
    return dict(held)


def test_a_type_that_carries_a_net_volume_offers_at_least_three() -> None:
    thin = {
        " > ".join(path): sorted(vs)
        for path, vs in per_type().items()
        if len(vs) < MINIMUM and path not in EXCEPTIONS
    }
    assert not thin, f"{len(thin)} types offer fewer than {MINIMUM} net volumes: {thin}"


@cache
def per_family() -> dict[str, set[float]]:
    """Net volumes by grocery family (the ``GRC-<family>-`` product id prefix). A path hides a
    thin family behind a sibling that sells the third size, and a shopper searching one
    product sees only that product's sizes."""
    held: dict[str, set[float]] = defaultdict(set)
    for d in docs():
        if (found := volumes(d)) and (m := re.match(r"GRC-([A-Z0-9]+)-", d["product_id"])):
            held[m.group(1)] |= found
    return dict(held)


def test_a_grocery_family_that_carries_a_net_volume_offers_at_least_three() -> None:
    thin = {code: sorted(vs) for code, vs in per_family().items() if len(vs) < MINIMUM}
    assert not thin, f"{len(thin)} families offer fewer than {MINIMUM} net volumes: {thin}"


def test_a_declared_exception_is_still_thin_and_says_why() -> None:
    for path, reason in EXCEPTIONS.items():
        assert reason.strip(), f"{path}: an exception names its reason"
        assert len(per_type().get(path, ())) < MINIMUM, f"{path}: now offers {MINIMUM}, drop it"


def test_a_title_that_states_a_volume_carries_that_net_volume() -> None:
    wrong = []
    for d in docs():
        for m in TITLE_VOLUME.finditer(d["title"]):
            ml = float(m.group(1)) * (1000 if m.group(2) == "L" else 1)
            if ml not in volumes(d):
                wrong.append(f"{d['product_id']} {d['title']!r}: {sorted(volumes(d))}")
    assert not wrong, f"{len(wrong)} titles disagree with their net volume: {wrong[:8]}"


def test_aftershave_and_body_mist_offer_the_common_small_size_too() -> None:
    """Beauty depth (gen#214): aftershave is sold from 30 ml and a body mist from 50 ml."""
    held = per_type()
    assert 30.0 in held[("Beauty", "Fragrance", "Aftershave")]
    assert 50.0 in held[("Beauty", "Fragrance", "Body mists")]


#: Leaf -> the volumes (ml) a shopper expects it in (gen#356). A volume-sold product carries
#: ``net_volume`` on every SKU, never a free-text ``size``, so the Net volume facet finds it.
VOLUME_SOLD = {
    "Shampoo": {250.0, 400.0, 500.0},
    "Conditioner": {250.0, 400.0, 500.0},
    "Perfume": {30.0, 50.0, 100.0},
    "Olive oil": {500.0, 750.0, 1000.0},
}

#: A size spelled as a volume: "250ml", "30 ml", "1L".
SIZE_AS_VOLUME = re.compile(r"\d+(?:\.\d+)? ?(?:ml|L)", re.IGNORECASE)


def volume_sold(leaf: str) -> list[dict]:
    return [d for d in docs() if d["category_path"][-1].lower() == leaf.lower()]


def test_the_volume_sold_leaves_are_in_the_catalogue() -> None:
    for leaf in VOLUME_SOLD:
        assert volume_sold(leaf), f"{leaf}: no template, so the guards below check nothing"


def test_every_product_of_a_volume_sold_leaf_offers_at_least_three_volumes() -> None:
    thin = {
        d["product_id"]: sorted(volumes(d))
        for leaf in VOLUME_SOLD
        for d in volume_sold(leaf)
        if len(volumes(d)) < MINIMUM
    }
    assert not thin, f"{len(thin)} products offer fewer than {MINIMUM} net volumes: {thin}"


def test_a_volume_sold_leaf_never_carries_its_volume_as_a_free_text_size() -> None:
    wrong = [
        f"{d['product_id']} size={e['value']!r}"
        for leaf in VOLUME_SOLD
        for d in volume_sold(leaf)
        for e in [*d["attributes"], *(e for v in d["variants"] for e in v["attributes"])]
        if e["key"] == "size" and SIZE_AS_VOLUME.fullmatch(str(e["value"]))
    ]
    assert not wrong, f"{len(wrong)} volumes sit under size, not net_volume: {wrong[:6]}"


def test_a_volume_sold_leaf_offers_its_usual_volumes() -> None:
    missing = {
        leaf: sorted(want - {v for d in volume_sold(leaf) for v in volumes(d)})
        for leaf, want in VOLUME_SOLD.items()
    }
    assert not any(missing.values()), f"volumes no product of the leaf offers: {missing}"

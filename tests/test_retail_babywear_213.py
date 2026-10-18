"""Retail babywear and nursery (gen#213): sleepsuits, baby bodysuits, snowsuits, puddlesuits,
all-in-ones, baby blankets, changing mats, nappy caddies and nursery storage.

Each type is a spec under ``type_specs/`` and :mod:`kit_baby` draws it. These checks hold what the
issue asked for: every type has three styles from three invented brands, a product type that
names it, a category path under its department, its own drawing shape, each key attribute as a
structured export entry, a drawing that shows what the record states, text-match decoys, and a
place in the 100k build.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import kit  # noqa: E402
import kit_baby  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

CLOTHING, NIGHT, HOME = "Clothing", "Lingerie & Nightwear", "Home"
_WORN = {"size", "color", "audience"}
YES = {"Yes": "yes", "No": "no"}

#: key -> (department, product type, path prefix, shape, key attributes, drawn pairs). A pair is
#: (attribute key, drawing param, attribute value -> param value): the drawing must show it.
TYPES = {
    "sleepsuit": (CLOTHING, "Sleepsuit", ("Kids", "Baby"), "sleepsuit",
                  {"feet", "sleeve", "fastening", "fabric", "pack_size", "season"} | _WORN, [
        ("feet", "feet", {"Footed": "footed", "Footless": "footless"}),
        ("sleeve", "sleeve", {"Long": "long", "Short": "short"}),
        ("fastening", "fastening", {"Poppers": "poppers", "Zip": "zip"})]),
    "baby_bodysuit": (CLOTHING, "Baby Bodysuit", ("Kids", "Baby"), "baby_bodysuit",
                      {"sleeve", "neck", "fabric", "pack_size", "season"} | _WORN, [
        ("sleeve", "sleeve", {"Long": "long", "Short": "short"}),
        ("neck", "neck", {"Envelope": "envelope", "Crew": "crew"})]),
    "snowsuit": (CLOTHING, "Snowsuit", ("Kids", "Baby"), "snowsuit",
                 {"fill", "hood", "fold_over_mitts", "fold_over_feet", "season"} | _WORN, [
        ("hood", "hood", YES), ("fold_over_mitts", "mitts", YES),
        ("fold_over_feet", "feet", YES)]),
    "puddlesuit": (CLOTHING, "Puddlesuit", ("Kids", "Baby"), "puddlesuit",
                   {"waterproof_rating", "lining", "hood", "season"} | _WORN, [
        ("hood", "hood", YES),
        ("lining", "lining", {"Fleece-Lined": "fleece", "Unlined": "none"})]),
    "all_in_one": (NIGHT, "All-in-One", None, "all_in_one",
                   {"fabric", "hood", "season"} | _WORN, [
        ("hood", "hood", YES),
        ("fabric", "fabric", {"Fleece": "fleece", "Teddy": "teddy", "Jersey": "jersey"})]),
    "baby_blanket": (HOME, "Baby Blanket", ("Home", "Nursery"), "baby_blanket",
                     {"blanket_type", "blanket_size", "fabric", "color"}, [
        ("blanket_type", "type", {"Cellular": "cellular", "Fleece": "fleece", "Knitted": "knit",
                                  "Swaddle": "swaddle"}),
        ("blanket_size", "size", {"Pram": "pram", "Cot": "cot"})]),
    "changing_mat": (HOME, "Changing Mat", ("Home", "Nursery"), "changing_mat",
                     {"wipe_clean", "compartments", "mat_size", "color"}, [
        ("wipe_clean", "wipe_clean", YES), ("compartments", "compartments", None)]),
    "nappy_caddy": (HOME, "Nappy Caddy", ("Home", "Nursery"), "nappy_caddy",
                    {"compartments", "wipe_clean", "caddy_size", "color"}, [
        ("compartments", "compartments", None)]),
    "nursery_storage": (HOME, "Nursery Storage", ("Home", "Nursery"), "nursery_storage",
                        {"storage_type", "fabric", "color"}, [
        ("storage_type", "kind",
         {"Basket": "basket", "Cube": "cube", "Hanging Organizer": "hanging"})]),
}  # fmt: skip
KEYS = sorted(TYPES)
#: The drawing parameters of each shape that change how it looks, with two readings of each.
READINGS = {
    "sleepsuit": {"feet": ("footed", "footless"), "sleeve": ("long", "short"),
                  "fastening": ("poppers", "zip")},
    "baby_bodysuit": {"sleeve": ("long", "short"), "neck": ("envelope", "crew")},
    "snowsuit": {"hood": ("yes", "no"), "mitts": ("yes", "no"), "feet": ("yes", "no")},
    "puddlesuit": {"hood": ("yes", "no"), "lining": ("fleece", "none")},
    "all_in_one": {"hood": ("yes", "no"), "fabric": ("fleece", "teddy")},
    "baby_blanket": {"type": ("cellular", "knit"), "size": ("pram", "cot")},
    "changing_mat": {"wipe_clean": ("yes", "no"), "compartments": ("0", "2")},
    "nappy_caddy": {"compartments": ("2", "4")},
    "nursery_storage": {"kind": ("basket", "cube")},
}  # fmt: skip


def _spec(key: str) -> type_registry.TypeSpec:
    spec = type_registry.specs().get(key)
    assert spec is not None, f"no type spec {key!r}"
    return spec


def _attr(row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _svg(shape: str, params: dict[str, str]) -> str:
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


@pytest.mark.parametrize("key", KEYS)
def test_the_type_has_three_styles_from_three_brands_under_its_path(key: str) -> None:
    dept, ptype, prefix, _shape, _keys, _pairs = TYPES[key]
    spec = _spec(key)
    assert (spec.department, spec.product_type) == (dept, ptype)
    styles = [r for r in spec.rows]
    assert len(styles) >= 3 and len({r.brand for r in styles}) >= 3
    bad = {r.code: r.path for r in styles if prefix and r.path[: len(prefix)] != prefix}
    assert bad == {}
    assert {r.product_type for r in styles} == {ptype}


@pytest.mark.parametrize("key", KEYS)
def test_every_style_draws_as_the_types_own_shape(key: str) -> None:
    shape = TYPES[key][3]
    assert shape in kit_baby.SHAPES and shape in kit.SHAPES
    spec = _spec(key)
    assert {r.code: r.shape for r in spec.rows if r.shape != shape} == {}
    assert shape not in ("box", "box_wide")


@pytest.mark.parametrize("key", KEYS)
def test_a_param_changes_the_drawing(key: str) -> None:
    shape = TYPES[key][3]
    for param, (one, other) in READINGS[key].items():
        assert _svg(shape, {param: one}) != _svg(shape, {param: other}), (shape, param)


@pytest.mark.parametrize("key", KEYS)
def test_every_key_attribute_is_a_structured_entry_in_the_export(key: str) -> None:
    keys = TYPES[key][4]
    missing = {}
    for row in _spec(key).rows:
        doc = export.standard_document(row.doc())
        got = {e["key"] for e in doc["attributes"]}
        got |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if keys - got:
            missing[row.code] = sorted(keys - got)
    assert missing == {}


@pytest.mark.parametrize("key", KEYS)
def test_the_drawing_shows_what_the_record_states(key: str) -> None:
    wrong = {}
    for row in _spec(key).rows:
        params = dict(row.params)
        for attr_key, param, mapping in TYPES[key][5]:
            (value,) = _attr(row, attr_key)
            want = str(int(value)) if mapping is None else mapping[value]
            if params.get(param) != want:
                wrong[(row.code, param)] = (value, params.get(param))
    assert wrong == {}


@pytest.mark.parametrize("key", KEYS)
def test_each_drawn_reading_is_stocked_by_some_style(key: str) -> None:
    """Both readings of a drawn attribute exist in the range, so a filter shows a difference."""
    rows = _spec(key).rows
    thin = {}
    for attr_key, _param, _mapping in TYPES[key][5]:
        seen = {_attr(r, attr_key)[0] for r in rows}
        if len(seen) < 2:
            thin[attr_key] = sorted(seen)
    assert thin == {}


@pytest.mark.parametrize("key", KEYS)
def test_the_type_carries_text_match_decoys_that_are_not_its_styles(key: str) -> None:
    spec = _spec(key)
    if spec.department == HOME:
        assert len(spec.decoys) >= 3
        assert len({d.cls for d in spec.decoys}) >= 3
    else:
        assert spec.apparel is not None and spec.apparel.compounds
    assert not {d.row.code for d in spec.decoys} & {r.code for r in spec.rows}


def test_a_pack_states_its_unit_count_and_a_bigger_pack_costs_less_per_unit() -> None:
    for key, packs in (("sleepsuit", {1, 2, 3}), ("baby_bodysuit", {3, 5, 7})):
        for row in _spec(key).rows:
            by: dict[tuple, dict[int, float]] = {}
            for s in row.skus():
                n = s["units_per_pack"]
                assert s["pack_size"] == ("Single" if n == 1 else f"{n} pack")
                by.setdefault((s["color"], s["size"]), {})[n] = s["price"] / n
            for per in by.values():
                assert set(per) <= packs
                units = [per[n] for n in sorted(per)]
                assert all(b <= a for a, b in zip(units, units[1:], strict=False))


def test_no_baby_drawing_prints_a_size_or_a_pack_count() -> None:
    for key in KEYS:
        for row in _spec(key).rows:
            assert "<text" not in _svg(row.shape, dict(row.params)), row.code


@pytest.mark.timeout(300)
def test_every_babywear_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    want = {f"BRD-{r.code}" for k in KEYS for r in _spec(k).rows}
    assert sorted(want - got) == []
    mine = [d for d in docs if d["product_id"] in want]
    assert len(mine) == len(want)
    assert check_catalog(mine, one_class_per_key=True) == []


#: Material and property words a title can claim (a decoy's trigger word is one of these).
CLAIMS = (
    "waterproof", "water-resistant", "wipe-clean", "wipeable", "leather", "suede", "cashmere",
    "wooden", "wood", "cotton", "fleece", "quilted", "padded", "insulated", "organic", "cot bed",
)  # fmt: skip
_DENIAL = r"\b(?:not|no|isn't|never|without|non)[\s-]+(?:[\w']+[\s-]+){0,2}?"


def _denied_claims(title: str, description: str) -> list[str]:
    """The claims the title makes that its own description denies. A ``-Look``, ``-Feel``,
    ``Look`` or ``Style`` claim is a claim about appearance, which the description may confirm."""
    low, desc = title.lower(), description.lower()
    out = []
    for claim in CLAIMS:
        at = re.search(rf"(?<![\w-]){re.escape(claim)}(?![\w])", low)
        if at is None or re.match(r"[\s-]*(?:look|feel|style)\b", low[at.end():]):
            continue
        if re.search(_DENIAL + re.escape(claim) + r"(?![\w-])", desc):
            out.append(claim)
    return out


@pytest.mark.parametrize("key", KEYS)
def test_a_decoys_title_claim_is_never_denied_by_its_own_description(key: str) -> None:
    """gen#404: no deliberately wrong data. A decoy's trigger word must be true of a real part
    of the product (a waterproof pouch) or of the shown brand, so the description that follows
    the title never says the title's claim is false."""
    denied = {
        d.row.code: (d.row.title, claims)
        for d in _spec(key).decoys
        if (claims := _denied_claims(d.row.title, d.row.description))
    }
    assert denied == {}


def test_the_waterproof_decoys_name_a_waterproof_part_the_description_confirms() -> None:
    by_code = {d.row.code: d.row for k in KEYS for d in _spec(k).decoys}
    for code in ("DB06", "DB10"):
        row = by_code[code]
        assert " with " in row.title.lower(), row.title
        assert "waterproof" in row.title.lower().split(" with ")[1], row.title
        assert re.search(r"\bwaterproof\b", row.description.lower()), row.description

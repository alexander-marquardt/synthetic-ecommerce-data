"""Every noise sentence is true, attributes do not move, and kits are not groups.

The copy's noise (``catalog/noise.py``) is checked here sentence type by
sentence type, against tables written out in this file and against the
record and its siblings -- never against the module that wrote it.
"""

from __future__ import annotations

import collections
import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from compat_text import NOISE, noise_sentences
from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.dimensions import parse_length

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"
MM = 25.4

METRIC_SERIES = ["M3", "M4", "M5", "M6", "M8", "M10", "M12", "M16", "M20", "M24"]
INCH_SERIES = ["#6", "#8", "#10", '1/4"', '5/16"', '3/8"', '7/16"', '1/2"', '5/8"', '3/4"', '1"']
#: What a tool of each material cuts (common machining practice).
CUTS = {
    "High Speed Steel": {"aluminum", "brass", "mild steel"},
    "Powdered Metal": {"aluminum", "mild steel", "stainless steel"},
    "Cobalt": {"aluminum", "brass", "mild steel", "stainless steel"},
    "Solid Carbide": {
        "aluminum", "brass", "mild steel", "stainless steel", "cast iron", "hardened steel",
    },
}  # fmt: skip
#: Same-dimension standards, and grade ordering (ISO 898-1/-2, SAE J429).
SAME_DIMENSIONS = {("DIN 912", "ISO 4762"), ("DIN 125-A", "ISO 7089")}
WEAKER = {"Class 10.9": "Class 8.8", "Grade 8": "Grade 5", "Class 10": "Class 8"}
#: ISO 492 Normal class bore tolerance (mm) by bore range (over, up to].
BORE_TOL = [(2.5, 10, 0.008), (10, 18, 0.008), (18, 30, 0.010), (30, 50, 0.012)]
ISO_7089 = {"M3", "M4", "M5", "M6", "M8", "M10", "M12", "M16", "M20"}
THREAD_ATTRIBUTE = ("Dia./Thread Size", "Thread Size")


@pytest.fixture(scope="module")
def golden() -> list[dict]:
    return [json.loads(line) for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()]


@pytest.fixture(scope="module")
def fresh() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig())))


@pytest.fixture(scope="module")
def clean() -> list[dict]:
    return list(emit.iter_flat(generate(GeneratorConfig(noise=0))))


@pytest.fixture(scope="module", params=["golden", "fresh"])
def docs(request) -> list[dict]:
    return request.getfixturevalue(request.param)


def _values(doc: dict) -> dict[str, str]:
    return {a["name"]: a["value"] for a in doc["attributes"]}


def _all_values(doc: dict) -> set[str]:
    return {a["value"] for a in doc["attributes"]}


def _inches(value: str) -> float:
    return parse_length(value).inches


def _diameter(designation: str) -> str:
    if designation.startswith("M"):
        return designation.split("x")[0]
    head = designation.split("-")[0]
    return head if head.startswith("#") else f'{head}"'


def _holds(match: re.Match[str], doc: dict, siblings: list[dict]) -> bool:  # noqa: C901, PLR0911, PLR0912
    g = {k: v for k, v in match.groupdict().items() if v is not None}
    values = _values(doc)
    kind = doc["product_type"]
    if "not_threads" in g:
        thread = next((values[n] for n in THREAD_ATTRIBUTE if n in values), None)
        if thread is None:
            return False
        own = _diameter(thread)
        series = METRIC_SERIES if own.startswith("M") else INCH_SERIES
        named = g["not_threads"].split(" or ")
        i = series.index(own)
        return all(n != own and n in series and abs(series.index(n) - i) == 1 for n in named)
    if "not_socket" in g:
        return kind == "hex_key" and _inches(g["not_socket"]) < _inches(values["Size"]) - 1e-6
    if "siblings" in g:
        # The product's variant axes: attributes whose value differs across its
        # SKUs. A named size is a sibling's value on such an axis, and not this
        # record's own value there.
        group = [doc, *siblings]
        axes = {
            name
            for name in set().union(*(_values(d) for d in group))
            if len({_values(d).get(name) for d in group}) > 1
        }
        named = g["siblings"].split(" / ")
        return bool(named) and all(
            any(
                _values(s).get(axis) == n and values.get(axis) != n
                for s in siblings
                for axis in axes
            )
            for n in named
        )
    if "eq_value" in g:
        value = g["eq_value"]
        if value not in _all_values(doc):
            return False
        size = _inches(value)
        if value.endswith("mm"):
            return Fraction(g["eq_other"].rstrip('"')) == Fraction(round(size * 64), 64)
        return g["eq_other"] == f"{size * MM:.1f}mm"
    if "bore_low" in g:
        bore_mm = _inches(values["Bore"]) * MM
        tol = next(t for lo, hi, t in BORE_TOL if lo < bore_mm <= hi)
        return (
            abs(float(g["bore_high"]) - bore_mm) < 1e-3
            and abs(float(g["bore_high"]) - float(g["bore_low"]) - tol) < 1e-6
        )
    if "pair_thread" in g:
        if g["pair_thread"] != values.get("Dia./Thread Size"):
            return False
        if "pair_key" in g:
            return abs(_inches(g["pair_key"]) - _inches(values["Drive Size"])) < 1e-4
        if "pair_washer" in g:
            return g["pair_washer"] == _diameter(g["pair_thread"]) and g["pair_washer"] in ISO_7089
        return True
    if "contrast" in g:
        text = g["contrast"]
        material, finish = values.get("Material", ""), values.get("Finish", "")
        if text.endswith("(not stainless)"):
            return "Stainless" not in material and finish == "Zinc Plated"
        if text.endswith("(not plated)"):
            return text.startswith(material) and "Stainless" in material and finish in ("", "Plain")
        if text == "Brass (not steel)":
            return material == "Brass"
        return text == "Note: not alloy steel" and material == "Steel"
    if "cuts" in g:
        named = {c.strip() for c in re.split(r",| and ", g["cuts"]) if c.strip()}
        return named <= CUTS.get(values.get("Material", ""), set())
    if "equivalent" in g:
        return (g["equivalent"], g["standard"]) in SAME_DIMENSIONS and doc[
            "dimension_provenance"
        ] == g["standard"]
    if "weaker" in g:
        return WEAKER.get(values.get("Grade", "")) == g["weaker"]
    if "application" in g:
        return kind == "hex_key"
    return False


def noise_errors(docs: list[dict]) -> tuple[list[tuple[str, str]], collections.Counter]:
    by_product: dict[str, list[dict]] = collections.defaultdict(list)
    for doc in docs:
        by_product[doc["product_id"]].append(doc)
    bad: list[tuple[str, str]] = []
    kinds: collections.Counter = collections.Counter()
    for doc in docs:
        siblings = [d for d in by_product[doc["product_id"]] if d["sku"] != doc["sku"]]
        for match in noise_sentences(doc["description"]):
            kinds[next(k for k, v in match.groupdict().items() if v is not None)] += 1
            if not _holds(match, doc, siblings) or match.group(0) not in doc["text"]:
                bad.append((doc["sku"], match.group(0)))
    return bad, kinds


def test_every_noise_sentence_is_true(docs):
    bad, kinds = noise_errors(docs)
    assert bad == [], bad[:10]
    for kind in (
        "not_threads", "not_socket", "siblings", "eq_value", "bore_low", "pair_thread",
        "contrast", "cuts", "equivalent", "weaker", "application",
    ):  # fmt: skip
        assert kinds[kind] > 5, (kind, kinds)


def test_a_planted_false_noise_sentence_is_caught(golden):
    doc = next(
        d for d in golden if "Suitable for aluminum, brass and mild steel." in d["description"]
    )
    planted = dict(
        doc,
        description=doc["description"].replace(
            "Suitable for aluminum, brass and mild steel.",
            "Suitable for aluminum, brass and hardened steel.",
        ),
    )
    planted["text"] = planted["description"]
    assert noise_errors([planted])[0]
    screw = next(
        d
        for d in golden
        if re.search(r"Not for M\d+ or M\d+ threads\.", d["description"])
        and "Dia./Thread Size" in _values(d)
    )
    own = _diameter(_values(screw)["Dia./Thread Size"])
    wrong = dict(
        screw,
        description=re.sub(r"Not for M\d+ or", f"Not for {own} or", screw["description"]),
    )
    wrong["text"] = wrong["description"]
    assert noise_errors([wrong])[0]


def test_noise_never_moves_an_attribute_or_a_title(fresh, clean):
    """The knob off and on: every record identical but for its copy."""
    assert [d["sku"] for d in fresh] == [d["sku"] for d in clean]
    for noisy, plain in zip(fresh, clean, strict=True):
        assert noisy["attributes"] == plain["attributes"], noisy["sku"]
        assert noisy["title"] == plain["title"], noisy["sku"]
        stripped = re.sub(r"\s*(?:" + NOISE.pattern + r")", "", noisy["description"])
        assert stripped == plain["description"], noisy["sku"]
    assert not any(noise_sentences(d["description"]) for d in clean)


def test_unit_equivalents_are_a_minority_within_their_bound(docs):
    """15-20% of the records that could carry one (maintainer ruling): the
    facets expand units themselves, so most results must be found through them."""
    primary = {
        "end_mill_square": "Milling Dia.",
        "end_mill_ball": "Milling Dia.",
        "drill_jobber": "Size",
        "hex_key": "Size",
        "bearing_radial_ball": "Bore",
        "wheel_depressed_center": "Diameter",
        "abrasive_flap_disc": "Diameter",
    }
    eligible = carrying = 0
    for doc in docs:
        name = primary.get(doc["product_type"])
        value = _values(doc).get(name) if name else None
        if value is None:
            continue
        try:
            _inches(value)
        except Exception:  # noqa: BLE001 -- an unparseable defect row is not eligible
            continue
        eligible += 1
        carrying += any(m.group("eq_value") for m in noise_sentences(doc["description"]))
    share = carrying / eligible
    assert 0.15 <= share <= 0.20, (carrying, eligible, round(share, 3))


# --- assortment kits ---------------------------------------------------------------


def _kits(docs):
    return [d for d in docs if d["product_type"] == "kit_assortment"]


def _contents(doc: dict) -> list[str]:
    return [a["value"] for a in doc["attributes"] if a["name"] == "Sizes Included"]


def test_a_kit_is_one_sku_of_its_own_product(docs):
    kits = _kits(docs)
    assert len(kits) >= 30
    kit_products = {d["product_id"] for d in kits}
    assert len(kit_products) == len(kits), "a kit product has more than one SKU"
    parts = {d["product_id"] for d in docs if d["product_type"] != "kit_assortment"}
    assert not kit_products & parts


def test_a_kits_piece_count_is_its_contents(docs):
    """``Number of Pieces`` is a real count: one per size in a set, a whole
    number per size in an assortment; never a figure the contents cannot give."""
    counted = 0
    for doc in _kits(docs):
        values, contents = _values(doc), _contents(doc)
        if "Number of Pieces" not in values or not contents:
            continue
        pieces = int(values["Number of Pieces"])
        assert pieces % len(contents) == 0, doc["sku"]
        if "Assortment" not in values.get("Type", ""):
            assert pieces == len(contents), doc["sku"]
        counted += 1
    assert counted >= 30, counted


def test_kits_and_grouping_are_different_mechanisms(docs):
    """Some hex key sizes are sold only in a set, some only singly, some both.

    Measured on the sizes' magnitudes: a grouped product sells its sizes as
    separate variants; a kit sells its contents together as one item.
    """

    def mm(value: str) -> float:
        return round(_inches(value) * MM, 2)

    single = {
        mm(_values(d)["Size"])
        for d in docs
        if d["product_type"] == "hex_key" and "Size" in _values(d)
    }
    in_kits = {
        mm(v) for d in _kits(docs) if _values(d).get("Type") == "Hex Key Set" for v in _contents(d)
    }
    assert in_kits - single, "no size is sold only in a set"
    assert single - in_kits, "no size is sold only singly"
    assert single & in_kits, "no size is sold both ways"

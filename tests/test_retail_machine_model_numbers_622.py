"""Model numbers of the small machines (gen#622, in the scheme of gen#625).

Every authored kettle, toaster, garden machine and drill driver leads its title with its brand,
then the series, then the brand's model number, then the spec and its own words: "Hearth & Table
Brew Max HTKT30S-26 3000W Rapid Boil Jug Kettle". The code is built from the kind, a variant, a
measure and the model year, and decodes back to the row's own attributes. The text decoys of the
same kinds carry no code: the exact number finds the machine, and nothing else can match it.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import line_grammar, scale
from synthetic_ecommerce_data.domains.retail import machine_model_numbers as mmn

#: The authored rows of each kind: the kinds' other rows are decoys.
AUTHORED = {
    "Kettle": ("KTLJUG", "KTLQUI", "KTLDOM", "KTLGLS", "KTLTMP", "KTLTRV"),
    "Toaster": ("TSTGLS", "TSTSTL", "TSTRET", "TSTLNG"),
    "Lawn Mower": ("MWRCLP", "MWRCSP", "MWRPET", "MWRELC"),
    "Robot Mower": ("ROBWIR", "ROBGPS", "ROBCMP"),
    "Grass Trimmer": ("TRMCRD", "TRMPET", "TRMELC"),
    "Hedge Trimmer": ("HDGCRD", "HDGELC", "HDGPET"),
    "Drill Driver": ("DRLCRD", "DRLCMP", "DRLDD20", "DRLDD18", "DRLDD12"),
}
_IDS = {f"BRD-{code}" for codes in AUTHORED.values() for code in codes}


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def machines(templates) -> list[dict]:
    found = [r for r in templates if r["product_id"] in _IDS]
    assert {r["product_id"] for r in found} == _IDS
    return found


@pytest.fixture(scope="module")
def decoys(templates) -> list[dict]:
    found = [r for r in templates if r["product_type"] in AUTHORED and r["product_id"] not in _IDS]
    assert len(found) >= 40
    return found


def _attrs(record: dict) -> dict[str, str]:
    return {a["key"]: a["value"] for a in record["attributes"]}


# -- the scheme ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("args", "code"),
    [
        (("Hearth & Table", "Kettle", "Standard", 3000), "HTKT30S-26"),
        (("Calderby & Lune", "Toaster", "Brushed", 7), "CL-TS26B07"),
        (("Emberly Home", "Kettle", "Standard", 2200), "EMKTS2226"),
        (("Lanternby", "Kettle", "Standard", 3000), "LB26KT30S"),
        (("Larchwood Living", "Toaster", "Matte", 7), "LWTS-07M26"),
        (("Cobble & Kiln", "Kettle", "Travel", 1000), "CK10KTV-26"),
        (("Thistle & Wren", "Lawn Mower", "Cordless Battery", 40), "TWLMB-40-26"),
        (("Fenwold Nursery", "Robot Mower", "Wire-Free GPS", 45), "FN26RMG45"),
        (("Harbour & Pine", "Grass Trimmer", "Petrol", 150), "HP26GT150P"),
        (("Wrenfield", "Hedge Trimmer", "Corded Electric", 20), "HG20-E-26"),
        (("Torvane Tools", "Drill Driver", "Brushed", 20), "TTDD20B26"),
        (("Harkwell Works", "Drill Driver", "Brushless", 18), "HK-DDL18-26"),
        (("Marlowick", "Drill Driver", "Brushed", 12), "MW26-DD12B"),
    ],
)
def test_each_scheme_builds_its_code_from_kind_variant_measure_and_year(args, code):
    assert mmn.encode(*args) == code
    brand, kind, variant, measure = args
    want = {"brand": brand, "kind": kind, "variant": variant, "measure": measure, "year": 2026}
    assert mmn.decode(code) == want


@pytest.mark.parametrize(
    "code",
    [
        "HTKT30S",  # the year is gone
        "XXKT30S-26",  # no brand leads with XX
        "HTXX30S-26",  # no kind is XX
        "HTKT30Z-26",  # a kettle has no variant Z
        "HTKT3S-26",  # one digit is too few
    ],
)
def test_a_code_no_scheme_builds_decodes_to_nothing(code):
    assert mmn.decode(code) is None


def test_the_same_machine_from_each_brand_gets_a_code_only_that_brand_builds():
    codes = {b: mmn.encode(b, "Lawn Mower", "Petrol", 60) for b in mmn.SCHEMES}
    assert len(set(codes.values())) == len(codes)
    for brand, code in codes.items():
        assert mmn.decode(code)["brand"] == brand


def test_a_series_name_and_its_lead_word_belong_to_one_brand():
    names = [(b, s) for b, kinds in mmn.SERIES.items() for s in kinds.values()]
    assert len({s for _, s in names}) == len(names)
    owners = {}
    for brand, series in names:
        assert owners.setdefault(series.split()[0], brand) == brand, series


def test_every_series_is_a_model_of_its_kinds_family():
    for brand, kinds in mmn.SERIES.items():
        for kind, series in kinds.items():
            fam = line_grammar.FAMILIES[kind]
            assert line_grammar.is_model(fam, brand, series), (kind, series)


def test_a_brand_has_a_series_only_for_a_kind_the_scheme_reads():
    assert set(mmn.SERIES) == set(mmn.SCHEMES)
    assert {k for kinds in mmn.SERIES.values() for k in kinds} == set(mmn.KINDS)


def test_the_spec_states_the_measure_and_a_drill_title_states_its_own():
    assert mmn.spec("Kettle", 3000) == "3000W"
    assert mmn.spec("Robot Mower", 35) == "35% Slope"
    assert mmn.spec("Drill Driver", 18) == ""


# -- the rows -----------------------------------------------------------------------------------


def test_every_machine_title_leads_with_brand_series_and_code(machines):
    for r in machines:
        a = _attrs(r)
        assert "model_number" in a, r["product_id"]
        lead = f"{r['brand']} {r['product_line']} {a['model_number']} "
        assert r["title"].startswith(lead), r["title"]


def test_every_machine_row_decodes_to_its_own_attributes(machines):
    for r in machines:
        a = _attrs(r)
        assert "model_number" in a, r["product_id"]
        got = mmn.decode(a["model_number"])
        kind = mmn.KINDS[r["product_type"]]
        assert got is not None, a["model_number"]
        assert got["brand"] == r["brand"]
        assert got["kind"] == r["product_type"]
        assert got["variant"] == a[kind.variant]
        assert got["measure"] == int(a[kind.measure])
        assert got["year"] == int(a["model_year"])
        assert r["product_line"] == mmn.SERIES[r["brand"]][r["product_type"]]


def test_no_machine_row_repeats_a_code_and_every_sku_carries_its_rows(machines):
    codes = [_attrs(r).get("model_number") for r in machines]
    assert None not in codes
    assert len(codes) == len(set(codes))
    for r in machines:
        assert {s.get("model_number") for s in r["skus"]} == {_attrs(r)["model_number"]}


def test_no_machine_code_is_a_code_of_another_kind(templates, machines):
    mine = {r["product_id"] for r in machines}
    others = {
        v
        for r in templates
        if r["product_id"] not in mine
        for v in (_attrs(r).get("model_number"), *(s.get("model_number") for s in r["skus"]))
    }
    codes = {_attrs(r).get("model_number") for r in machines}
    assert None not in codes
    assert not codes & others


def test_a_text_decoy_of_these_kinds_carries_no_code(decoys):
    for r in decoys:
        assert "model_number" not in _attrs(r), r["title"]
        assert not r.get("product_line"), r["title"]
        assert all("model_number" not in s for s in r["skus"]), r["title"]


def test_a_full_model_number_finds_its_machine_first(templates, machines):
    index = br.Index(templates)
    for r in machines:
        code = _attrs(r).get("model_number")
        assert code, r["product_id"]
        assert br.rank(index, code, 1, popular=False)[0]["product_id"] == r["product_id"], code

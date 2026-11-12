"""The stress catalog (gen#948): numbered copies of each product's attributes, off by default.

One small build (``--lines 40``, the default seed) with the flag off, one with ``--stress-keys
0``, and two with a 500-key target; every assertion reads those builds' files.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data import generate_cli, stress

LINES = "40"
TARGET = 500
COPIES = 2  # below C (500 // the base keys), so the cap of N copies is seen
COPY_KEY = re.compile(r"^(?P<base>.+)_(?P<number>\d{4})$")


def _build(out: Path, *extra: str) -> None:
    assert generate_cli.main(["build", "--lines", LINES, "--out", str(out), *extra]) == 0


def _files(directory: Path) -> dict[str, bytes]:
    return {path.name: path.read_bytes() for path in sorted(directory.iterdir())}


def _nested(directory: Path) -> list[dict]:
    return _jsonl(directory / "nested.jsonl")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines()]


@pytest.fixture(scope="module")
def builds(tmp_path_factory) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("stress948")
    stress_args = ("--stress-keys", str(TARGET), "--stress-copies", str(COPIES))
    _build(root / "standard")
    _build(root / "off", "--stress-keys", "0")
    _build(root / "stress_a", *stress_args)
    _build(root / "stress_b", *stress_args)
    return {name: root / name for name in ("standard", "off", "stress_a", "stress_b")}


def _lists(doc: dict) -> list[list[dict]]:
    """The product's entries, then each variant's: the lists a copy is added to."""
    return [doc["attributes"], *(variant["attributes"] for variant in doc["variants"])]


def _keys(docs: list[dict]) -> set[str]:
    return {e["key"] for doc in docs for entries in _lists(doc) for e in entries}


def _value(entry: dict) -> dict:
    """An entry less its key and name: the value, unit and canonical value a copy keeps."""
    return {k: v for k, v in entry.items() if k not in ("key", "name")}


def test_flag_off_is_byte_identical(builds):
    standard, off = _files(builds["standard"]), _files(builds["off"])
    assert standard == off
    assert stress.CENSUS not in standard


def test_copy_names_follow_attribute_and_four_digits(builds):
    base = _keys(_nested(builds["standard"]))
    copies = TARGET // len(base)
    assert copies > COPIES
    added = _keys(_nested(builds["stress_a"])) - base
    assert added, "the stress build added no keys"
    for key in added:
        match = COPY_KEY.fullmatch(key)
        assert match, key
        assert match["base"] in base, key
        assert 1 <= int(match["number"]) <= copies, key


def test_originals_kept_and_copies_are_subsets(builds):
    standard = {doc["product_id"]: doc for doc in _nested(builds["standard"])}
    for doc in _nested(builds["stress_a"]):
        before = standard[doc["product_id"]]
        assert {k: v for k, v in doc.items() if k not in ("attributes", "variants")} == {
            k: v for k, v in before.items() if k not in ("attributes", "variants")
        }
        for entries, originals in zip(_lists(doc), _lists(before), strict=True):
            assert entries[: len(originals)] == originals, doc["product_id"]
            for entry in entries[len(originals) :]:
                match = COPY_KEY.fullmatch(entry["key"])
                assert match, entry["key"]
                own = [e for e in originals if e["key"] == match["base"]]
                assert _value(entry) in [_value(e) for e in own], entry["key"]
                assert entry["name"] == f"{own[0]['name']} {match['number']}"


def test_no_more_than_n_copies_of_an_attribute(builds):
    standard = {doc["product_id"]: doc for doc in _nested(builds["standard"])}
    for doc in _nested(builds["stress_a"]):
        numbers: dict[str, set[str]] = {}
        for entries in _lists(doc):
            for entry in entries:
                match = COPY_KEY.fullmatch(entry["key"])
                if match:
                    numbers.setdefault(match["base"], set()).add(match["number"])
        assert set(numbers) == _keys([standard[doc["product_id"]]]), doc["product_id"]
        assert all(1 <= len(found) <= COPIES for found in numbers.values()), doc["product_id"]


def test_two_runs_are_identical(builds):
    assert _files(builds["stress_a"]) == _files(builds["stress_b"])


def test_census_is_written_and_printed(builds, capsys, tmp_path):
    census = json.loads((builds["stress_a"] / stress.CENSUS).read_text("utf-8"))["census"]
    docs = _nested(builds["stress_a"])
    assert census["products"] == len(docs)
    keys = _keys(docs)
    assert census["distinct_keys"] == len(keys)
    assert set(census["products_per_key"]) == {"min", "p50", "p90", "p99", "max"}
    assert census["values_per_key"]["max"] >= census["values_per_key"]["min"] >= 1
    carriers = [sum(1 for doc in docs if key in _keys([doc])) for key in keys]
    assert census["products_per_key"]["max"] == max(carriers)
    assert census["keys_on_fewer_than_5_products"] == sum(1 for n in carriers if n < 5)
    _build(tmp_path / "printed", "--stress-keys", str(TARGET), "--stress-copies", str(COPIES))
    printed = capsys.readouterr().out
    assert f"{census['products']} products, {census['distinct_keys']} distinct keys" in printed
    for label in ("products per key:", "values per key:", "keys on fewer than 5 products:"):
        assert label in printed


def test_never_written_over_a_standard_build(builds, capsys):
    with pytest.raises(SystemExit):
        generate_cli.main(
            ["build", "--lines", LINES, "--out", str(builds["standard"]), "--stress-keys", "500"]
        )
    assert "holds a standard build" in capsys.readouterr().err
    assert stress.CENSUS not in _files(builds["standard"])


def test_flat_documents_carry_the_copies(builds):
    flat = _jsonl(builds["stress_a"] / "flat.jsonl")
    assert len(flat) == sum(len(doc["variants"]) for doc in _nested(builds["stress_a"]))
    assert any(COPY_KEY.fullmatch(key) for doc in flat for key in doc["facets"])

"""``ecom-generate compose``: the domains' builds as ONE catalog (gen#125, slice 4 of the
2026-10-28 ruling).

Compose reads each domain's finished build (``nested.jsonl`` and ``flat.jsonl``), checks the
union of their nested documents against the output standard, and writes every domain's flat
file, byte for byte and in the order given, as one ``catalog.ndjson`` with a ``provenance.json``
that says where each domain's lines sit. A refused union writes nothing.

The industrial input is the committed ``golden-catalog/``; the retail one is the retail export,
written once per module.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from synthetic_ecommerce_data import compose, generate_cli

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "golden-catalog"
RELEASE = ROOT / ".github" / "workflows" / "release.yaml"


def _lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    path.write_text(text, encoding="utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture(scope="module")
def retail_build(tmp_path_factory) -> Path:
    from synthetic_ecommerce_data.domains.retail import export  # noqa: PLC0415

    out = tmp_path_factory.mktemp("retail")
    _write(out / "nested.jsonl", export.documents())
    _write(out / "flat.jsonl", export.flat_documents())
    return out


@pytest.fixture(scope="module")
def small_industrial(tmp_path_factory) -> Path:
    """The golden's first 300 products and their SKUs: a refusal needs no whole catalog."""
    out = tmp_path_factory.mktemp("industrial")
    nested = _lines(GOLDEN / "nested.jsonl")[:300]
    ids = {d["product_id"] for d in nested}
    _write(out / "nested.jsonl", nested)
    _write(out / "flat.jsonl", [r for r in _lines(GOLDEN / "flat.jsonl") if r["product_id"] in ids])
    return out


def _run(tmp_path: Path, *domains: str) -> int:
    argv = [a for d in domains for a in ("--domain", d)] + ["--out", str(tmp_path / "out")]
    return compose.main(argv)


def test_compose_writes_each_domains_flat_file_in_order_with_its_provenance(tmp_path, retail_build):
    assert _run(tmp_path, f"industrial={GOLDEN}", f"retail={retail_build}") == 0
    catalog = tmp_path / "out" / compose.CATALOG
    assert catalog.is_file(), "compose wrote no catalog"
    halves = [(GOLDEN / "flat.jsonl").read_bytes(), (retail_build / "flat.jsonl").read_bytes()]
    assert catalog.read_bytes() == b"".join(halves)

    products = [len(_lines(GOLDEN / "nested.jsonl")), len(_lines(retail_build / "nested.jsonl"))]
    counts = [half.count(b"\n") for half in halves]
    provenance = json.loads((tmp_path / "out" / compose.PROVENANCE).read_text(encoding="utf-8"))
    assert provenance == {
        "catalog": compose.CATALOG,
        "documents": sum(counts),
        "content_sha256": _sha(catalog.read_bytes()),
        "domains": [
            {
                "domain": "industrial",
                "first_line": 1,
                "documents": counts[0],
                "products": products[0],
                "content_sha256": _sha(halves[0]),
            },
            {
                "domain": "retail",
                "first_line": counts[0] + 1,
                "documents": counts[1],
                "products": products[1],
                "content_sha256": _sha(halves[1]),
            },
        ],
    }


def test_the_cli_runs_compose(tmp_path, small_industrial, retail_build):
    argv = ["compose", "--domain", f"retail={retail_build}"]
    argv += ["--domain", f"industrial={small_industrial}", "--out", str(tmp_path / "out")]
    assert generate_cli.main(argv) == 0
    catalog = tmp_path / "out" / compose.CATALOG
    assert catalog.is_file(), "compose wrote no catalog"
    # the order given is the order written: retail first here
    halves = [retail_build / "flat.jsonl", small_industrial / "flat.jsonl"]
    assert catalog.read_bytes() == b"".join(p.read_bytes() for p in halves)


def _copy(src: Path, dst: Path) -> Path:
    for name in ("nested.jsonl", "flat.jsonl"):
        (dst / name).parent.mkdir(parents=True, exist_ok=True)
        (dst / name).write_bytes((src / name).read_bytes())
    return dst


def _rewrite(build: Path, name: str, change) -> None:
    rows = _lines(build / name)
    change(rows)
    _write(build / name, rows)


def _shared_sku(industrial: Path, retail: Path) -> str:
    sku = _lines(industrial / "flat.jsonl")[0]["sku"]
    old = _lines(retail / "flat.jsonl")[0]["sku"]

    def nested(rows):
        for doc in rows:
            for variant in doc["variants"]:
                if variant["sku"] == old:
                    variant["sku"] = sku

    def flat(rows):
        rows[0]["sku"] = sku

    _rewrite(retail, "nested.jsonl", nested)
    _rewrite(retail, "flat.jsonl", flat)
    return f"sku {sku} is not unique (2 times)"


def _shared_product(industrial: Path, retail: Path) -> str:
    pid = _lines(industrial / "nested.jsonl")[0]["product_id"]
    old = _lines(retail / "nested.jsonl")[0]["product_id"]

    def change(rows):
        for row in rows:
            if row["product_id"] == old:
                row["product_id"] = pid

    _rewrite(retail, "nested.jsonl", change)
    _rewrite(retail, "flat.jsonl", change)
    return f"product_id {pid} is not unique (2 times)"


def _two_names(industrial: Path, retail: Path) -> str:
    entry = next(e for d in _lines(industrial / "nested.jsonl") for e in d["attributes"])

    def change(rows):
        rows[0]["attributes"].append({"key": entry["key"], "name": "Planted name", "value": "x"})

    _rewrite(retail, "nested.jsonl", change)
    return f"key {entry['key']!r} names"


def _flat_short(industrial: Path, retail: Path) -> str:
    _rewrite(retail, "flat.jsonl", lambda rows: rows.pop())
    return "retail: flat.jsonl and nested.jsonl are not one build"


def _no_final_newline(industrial: Path, retail: Path) -> str:
    flat = retail / "flat.jsonl"
    flat.write_bytes(flat.read_bytes().rstrip(b"\n"))
    return "retail: flat.jsonl does not end in a newline"


#: A planted defect in the retail build -> the start of the problem compose names.
PLANTS = {
    "a flat file with no final newline": _no_final_newline,
    "a sku industrial also has": _shared_sku,
    "a product_id industrial also has": _shared_product,
    "a key industrial names otherwise": _two_names,
    "a flat file one SKU short of its nested file": _flat_short,
}


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_a_union_that_breaks_the_standard_is_refused_and_nothing_written(
    plant, tmp_path, capsys, small_industrial, retail_build
):
    retail = _copy(retail_build, tmp_path / "retail")
    expected = PLANTS[plant](small_industrial, retail)
    assert _run(tmp_path, f"industrial={small_industrial}", f"retail={retail}") == 1
    assert expected in capsys.readouterr().err
    assert not (tmp_path / "out" / compose.CATALOG).exists()
    assert not (tmp_path / "out" / compose.PROVENANCE).exists()


@pytest.mark.parametrize(
    ("domains", "expected"),
    [
        (("toys={i}",), "unknown domain 'toys'"),
        (("industrial={i}", "industrial={i}"), "domain 'industrial' is named twice"),
        (("industrial",), "is not <domain>=<build directory>"),
        (("industrial={i}/absent",), "industrial: no nested.jsonl in"),
        ((), "no --domain given"),
    ],
    ids=[
        "an unknown domain",
        "a domain named twice",
        "no build directory",
        "a directory with no build",
        "no domain",
    ],
)
def test_an_unknown_repeated_or_malformed_domain_is_refused(
    domains, expected, tmp_path, capsys, small_industrial
):
    given = [d.format(i=small_industrial) for d in domains]
    try:
        code = _run(tmp_path, *given)
    except Exception as error:  # a refusal is an exit code and a message, never a traceback
        raise AssertionError(f"compose crashed instead of refusing: {error!r}") from error
    assert code == 1
    assert expected in capsys.readouterr().err
    assert not (tmp_path / "out" / compose.CATALOG).exists()


def _step(name: str) -> str:
    steps = yaml.safe_load(RELEASE.read_text(encoding="utf-8"))["jobs"]["release"]["steps"]
    found = [s["run"] for s in steps if s.get("name", "").startswith(name)]
    assert found, f"release.yaml has no step {name!r}"
    return found[0]


def test_the_release_ships_the_composed_catalog_as_its_one_catalog_asset():
    composed = "build/release/catalog/catalog.ndjson"
    # the retail half is built as a domain build: its nested and its flat file in one directory
    retail = _step("Build the retail ceiling")
    assert "--out build/release/retail/nested.jsonl" in retail
    assert "--flat build/release/retail/flat.jsonl" in retail
    step = _step("Compose the one catalog")
    for part in (
        "ecom-generate compose --domain industrial=build/release/industrial",
        "--domain retail=build/release/retail --out build/release/catalog",
        f"gzip -n -9 -c {composed} > build/release/catalog.ndjson.gz",
    ):
        assert part in step, part
    pin_bump = _step("The pin-bump")
    assert f"--catalog {composed}" in pin_bump
    assert "build/release/catalog/provenance.json" in pin_bump.split("gh release create", 1)[1]

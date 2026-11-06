"""The planted proof of #50, on a real catalog: a regeneration restates every pin, and a catalog
without a rule's SKU stops the script naming the rule.

``tests/test_golden_pins_50.py`` holds the pin machinery on stubs. These cases build the catalog
with another seed, so every SKU code moves, and run ``scripts/measure_pins.py`` on it:

* every pin is restated, each pinned SKU moved with the seed and still fits its rule;
* with every SKU of the ``drill`` rule taken out of that catalog, the script exits 1, names the
  rule and writes nothing: it does not fall back to a weaker SKU.
"""

from __future__ import annotations

import functools
import json
import shutil
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data import generate_cli as cli
from synthetic_ecommerce_data.core.config import GeneratorConfig

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import golden_pins  # noqa: E402  (scripts/ is not a package)
import measure_pins  # noqa: E402

#: Not the committed catalog's seed, so every SKU code the fixture pins moves.
SEED = GeneratorConfig.seed + 1


@pytest.fixture(scope="module")
def reseeded(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One ``ecom-generate build --seed SEED``; its field map goes to a temporary path, not the
    source tree (see ``tests/test_catalog_golden.py::fresh_build``)."""
    out = tmp_path_factory.mktemp("reseeded")
    field_map = tmp_path_factory.mktemp("field_map") / "field_map.json"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(cli, "field_map_target", lambda: field_map)
        code = cli.main(["build", "--out", str(out), "--seed", str(SEED)])
    assert code == 0, "ecom-generate build failed; its own audits print to stderr"
    return out


def _measure(golden: Path, out: Path, *flags: str) -> int:
    return measure_pins.main(
        ["--golden", str(golden), "--seed", str(SEED), "--out", str(out), *flags]
    )


def _lines(golden: Path) -> list[dict]:
    return [json.loads(line) for line in (golden / "nested.jsonl").read_text("utf-8").splitlines()]


def _fits(rule: golden_pins.SkuRule, parent: dict, variant: dict) -> bool:
    if parent["product_type"] != rule.product_type:
        return False
    if rule.attribute is None:
        return True
    key, value = rule.attribute
    return any(a["key"] == key and a["value"] == value for a in variant["attributes"])


def test_a_catalog_built_with_another_seed_has_every_pin_restated(
    reseeded: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "golden_pins.json"
    # The ``--check`` run at the end asks whether the script compares with the file ``--out``
    # names; measuring the same catalog and seed a second time was 25 s of the same figures
    # (#790), so it reads the first run's. Each measure's own stability is held where it is
    # pinned: the default build's figures by the tests that read them from the fixture.
    monkeypatch.setattr(golden_pins, "measure_all", functools.cache(golden_pins.measure_all))
    assert _measure(reseeded, out) == 0
    assert out.is_file(), "the script did not write the fixture --out names"
    pins = json.loads(out.read_text("utf-8"))
    committed = golden_pins.load()
    assert sorted(pins) == sorted(committed)

    skus = pins["lens"]["skus"]
    unmoved = sorted(key for key, sku in skus.items() if sku == committed["lens"]["skus"][key])
    assert unmoved == [], (
        f"the pins {unmoved} did not move with the seed: the script measured the committed "
        "catalog, not the one it was given"
    )
    assert pins["anchor"]["product_id"] != committed["anchor"]["product_id"]
    assert pins["titles"]["documents"] != committed["titles"]["documents"], (
        "the title counts are the default seed's: the title cut did not build with --seed"
    )

    variants = {v["sku"]: (parent, v) for parent in _lines(reseeded) for v in parent["variants"]}
    for rule in golden_pins.SKU_RULES:
        assert skus[rule.key] in variants, f"{rule.key}: {skus[rule.key]} is not in the catalog"
        assert _fits(rule, *variants[skus[rule.key]]), f"{rule.key} does not fit: {rule.statement}"

    assert _measure(reseeded, out, "--check") == 0


def _without(golden: Path, rule: golden_pins.SkuRule) -> set[str]:
    """Take every SKU that could fit ``rule`` out of the catalog; the SKUs taken out."""
    removed: set[str] = set()
    kept_lines = []
    for parent in _lines(golden):
        kept = [v for v in parent["variants"] if not _fits(rule, parent, v)]
        removed |= {v["sku"] for v in parent["variants"]} - {v["sku"] for v in kept}
        if kept:
            kept_lines.append(json.dumps({**parent, "variants": kept, "variant_count": len(kept)}))
    (golden / "nested.jsonl").write_text("\n".join(kept_lines) + "\n", "utf-8")
    flat = (golden / "flat.jsonl").read_text("utf-8").splitlines()
    kept_flat = [line for line in flat if json.loads(line)["sku"] not in removed]
    (golden / "flat.jsonl").write_text("\n".join(kept_flat) + "\n", "utf-8")
    return removed


def test_a_catalog_without_the_rules_sku_fails_naming_the_rule_and_writes_nothing(
    reseeded: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rule = next(rule for rule in golden_pins.SKU_RULES if rule.key == "drill")
    golden = tmp_path / "catalog"
    shutil.copytree(reseeded, golden)
    assert _without(golden, rule), f"the reseeded catalog holds no SKU to remove: {rule.statement}"
    out = tmp_path / "golden_pins.json"
    assert _measure(golden, out) == 1
    err = capsys.readouterr().err
    assert repr(rule.key) in err and rule.statement in err, err
    assert not out.exists(), "the script wrote a fixture for a rule no SKU satisfies"

"""A family that sizes its own pack is a module, found by walking its package (#1151).

``pack_scale.py`` kept the shapes that draw their own size in one set and the shapes with their
own floor in one table, each family with a docstring bullet, so three PRs of one week (#1140,
#1141, #1148) conflicted on the file. Each family is now ``pack_scale_families/<family>.py`` with
``SELF_SIZED`` and/or ``FLOORS``, and ``pack_scale`` builds both tables from the package. The
tests plant a probe module in a throwaway directory put on the package path, in a subprocess so
the import-time tables are built fresh, then hold the contract.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from synthetic_ecommerce_data.domains.retail import pack_scale

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src/synthetic_ecommerce_data/domains/retail/pack_scale_families"

#: The tables on main before the split (d96084e3), plus the shapes added since (#1125):
#: the move changes no shape and no floor.
SELF_SIZED_BEFORE = frozenset(
    {
        "produce_pile",
        "wine_bottle",
        "soft_drink",
        "beer",
        "milk_jug",
        "milk_carton",
        "yogurt",
        "chocolate_bar",
        "chocolate_box",
        "chocolate_bag",
        "hot_chocolate",
        "chocolate_orange",
    }
)
SHAPE_FLOORS_BEFORE = {"loaf": 0.9}

REPORT = """
import json
from synthetic_ecommerce_data.domains.retail import pack_scale_families
pack_scale_families.__path__.append({extra!r})
from synthetic_ecommerce_data.domains.retail import pack_scale
rec = {{"category_path": ["Food & Drink"], "title": "Probe Tub", "drawing": {{"shape": "zz_tub"}},
        "skus": [{{"net_weight_g": 100}}, {{"net_weight_g": 800}}]}}
floored = {{**rec, "drawing": {{"shape": "zz_slab"}}}}
print(json.dumps({{
    "self_sized": "zz_tub" in pack_scale.SELF_SIZED,
    "factor": pack_scale.factor(rec, rec["skus"][0]),
    "floor": pack_scale.SHAPE_FLOORS.get("zz_slab"),
    "floored": pack_scale.factor(floored, floored["skus"][0]),
    "kept": "wine_bottle" in pack_scale.SELF_SIZED and pack_scale.SHAPE_FLOORS["loaf"] == 0.9,
}}))
"""

ERROR = """
from synthetic_ecommerce_data.domains.retail import pack_scale_families
pack_scale_families.__path__.append({extra!r})
from synthetic_ecommerce_data.domains.retail import pack_scale  # noqa: F401
"""


def _run(tmp_path: Path, template: str, modules: dict[str, str]) -> subprocess.CompletedProcess:
    extra = tmp_path / "extra"
    extra.mkdir()
    for name, text in modules.items():
        (extra / f"{name}.py").write_text(text, encoding="utf-8")
    code = template.format(extra=str(extra))
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


def test_the_split_keeps_every_self_sized_shape_and_floor_of_main():
    assert pack_scale.SELF_SIZED == SELF_SIZED_BEFORE
    assert pack_scale.SHAPE_FLOORS == SHAPE_FLOORS_BEFORE


def test_a_probe_family_module_is_read_with_no_shared_file_edited(tmp_path):
    probe = 'SELF_SIZED = ("zz_tub",)\nFLOORS = {"zz_slab": 0.95}\n'
    done = _run(tmp_path, REPORT, {"zz_probe": probe})
    assert done.returncode == 0, done.stderr
    got = json.loads(done.stdout)
    assert got["self_sized"] is True and got["factor"] is None, "a self-sized shape takes none"
    assert got["floor"] == 0.95 and got["floored"] == 0.95, "the module's floor is the factor's"
    assert got["kept"] is True, "the shipped families are still read"


def test_a_module_that_defines_neither_table_is_refused(tmp_path):
    done = _run(tmp_path, ERROR, {"zz_empty": "X = 1\n"})
    assert done.returncode != 0
    assert "zz_empty" in done.stderr and "SELF_SIZED" in done.stderr


def test_a_shape_two_modules_claim_is_refused(tmp_path):
    done = _run(tmp_path, ERROR, {"zz_twin": 'FLOORS = {"wine_bottle": 0.7}\n'})
    assert done.returncode != 0
    assert "wine_bottle" in done.stderr and "zz_twin" in done.stderr
    assert "pack_scale_families.drinks" in done.stderr


def test_pack_scale_names_no_family_shape():
    text = (PACKAGE.parent / "pack_scale.py").read_text(encoding="utf-8")
    for shape in (*SELF_SIZED_BEFORE, *SHAPE_FLOORS_BEFORE):
        assert f'"{shape}"' not in text and f"``{shape}``" not in text, shape

"""The redraw sweep of gen#1182 (slice 3): every turned product with a shadow, by kit.

``scripts/shadow_sweep_1182.py`` counts the turned products that stand on a shadow and how many of
those shadows still turn with the product. The fixtures are the served SVGs of the Blood Oranges of
the maintainer's report and of a shoe (a kit whose shadow was unlabelled), recorded at the commit
before slice 1 (``dbdc94bf``) and after slice 2: the sweep reads the old shadow as turned and the
new one as flat.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import image_release, scale

_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "shadow_sweep_1182", _ROOT / "scripts" / "shadow_sweep_1182.py"
)
assert _spec is not None and _spec.loader is not None
sweep = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = sweep
_spec.loader.exec_module(sweep)

FIXTURES = _ROOT / "tests" / "fixtures" / "flat_shadow_1182"
PRODUCTS = ("PLT-ORBLOD", "FTW-WTRCNV")


@pytest.mark.parametrize("pid", PRODUCTS)
def test_the_sweep_reads_a_shadow_from_before_the_fix_as_turned(pid: str) -> None:
    assert sweep.shadows((FIXTURES / f"{pid}-before.svg").read_text()) == (1, 1)


@pytest.mark.parametrize("pid", PRODUCTS)
def test_the_sweep_reads_the_shared_steps_shadow_as_flat(pid: str) -> None:
    assert sweep.shadows((FIXTURES / f"{pid}-after.svg").read_text()) == (1, 0)


def test_a_product_with_no_shadow_counts_none() -> None:
    red = '<ellipse cx="1" cy="1" rx="2" ry="1" fill="#ff0000"/>'
    svg = f'<svg><g transform="rotate(12)">{red}</g></svg>'
    assert sweep.shadows(svg) == (0, 0)


def test_a_shadow_is_turned_only_inside_a_rotating_group() -> None:
    shadow = '<ellipse class="ground" cx="1" cy="1" rx="2" ry="1"/>'
    moved = f'<g transform="translate(1 1)">{shadow}</g>'
    svg = f'<svg><g transform="rotate(5)"><g/></g>{shadow}{moved}</svg>'
    assert sweep.shadows(svg) == (2, 0)


def test_each_shape_is_counted_under_its_kit() -> None:
    assert sweep.kit_of("produce_pile") == "produce"
    assert sweep.kit_of("shoe") == "footwear"


def test_the_table_counts_by_kit_and_totals() -> None:
    rows = {
        ("produce", "produce_pile"): [3, 3, 0],
        ("dairy", "milk_jug"): [2, 1, 1],
        ("dairy", "milk_carton"): [1, 1, 0],
        ("home", "rug"): [4, 0, 0],
    }
    text = sweep.table(rows)
    assert "| dairy | 3 | 2 | 1 | milk_carton 1, milk_jug 1 |" in text
    assert "| produce | 3 | 3 | 0 | produce_pile 3 |" in text
    assert "| home |" not in text  # a kit with no turned shadow is left off
    assert text.splitlines()[-1] == "| **all** | 6 | 5 | 1 | |"


def test_the_served_blood_oranges_stand_on_one_flat_shadow() -> None:
    (rec,) = [r for r in scale.templates() if r["product_id"] == sweep.ORANGES]
    assert sweep.shadows(image_release.render(rec, rec["skus"][0]).decode()) == (1, 0)


def test_the_sheet_draws_each_product_with_its_caption() -> None:
    out = sweep.sheet([sweep.ORANGES, "FTW-WTRCNV"], "t")
    assert out.count('<svg x="') == 2
    assert "PLT-ORBLOD produce 12°" in out and "FTW-WTRCNV footwear 15°" in out

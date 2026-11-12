"""Every material and finish a build of any size publishes has a fill and a hatch (#949).

``test_sku_drawings.py`` sweeps the default build's records. A value the generator draws only
at a larger size escapes that sweep: roll pins take (Material, Finish) from
``roll_pins.COMBOS`` by a rotation keyed per (standard, size), and the third combo,
``420 Stainless Steel``, is reached only when one key gets a third line. No key does at 2600
lines; one does at 4000, and 209 SKUs at the release size (39,000 lines) publish it.
With no hatch for it, ``ecom-generate build --lines 4000`` and the release build both stopped
while drawing ``images.jsonl``.

So the sweep here reads the release-size build (one shared file, made once in CI by the
``hundred_k`` leg), and every table that a rotation draws from is checked too, whatever size
reaches its last entry.
"""

from __future__ import annotations

import pytest

from shared_builds import hundred_k_drawn_styles
from synthetic_ecommerce_data.core.drawing.style import Hatch, material_hatch, part_fill
from synthetic_ecommerce_data.domains.industrial.product_types.fasteners import roll_pins


@pytest.fixture(scope="module")
def release_size_styles() -> dict[str, dict[str, int]]:
    return hundred_k_drawn_styles()


def _unstyled_materials(materials) -> list[str]:
    missing = []
    for material in sorted(materials):
        try:
            hatch = material_hatch(material)
            part_fill(None, material)
        except Exception:  # noqa: BLE001 -- the sweep names every miss, not the first
            missing.append(material)
            continue
        if not isinstance(hatch, Hatch):
            missing.append(material)
    return missing


def test_every_material_the_release_size_build_publishes_has_a_fill_and_a_hatch(
    release_size_styles,
):
    materials = release_size_styles["materials"]
    assert len(materials) > 50, materials  # the sweep read a real catalog
    missing = _unstyled_materials(materials)
    assert not missing, {m: materials[m] for m in missing}


def test_every_finish_the_release_size_build_publishes_has_a_color(release_size_styles):
    finishes = release_size_styles["finishes"]
    assert finishes
    missing = []
    for finish in sorted(finishes):
        try:
            part_fill(finish, None)
        except Exception:  # noqa: BLE001 -- the sweep names every miss, not the first
            missing.append(finish)
    assert not missing, {f: finishes[f] for f in missing}


@pytest.mark.parametrize("material, finish", roll_pins.COMBOS)
def test_every_roll_pin_combo_draws_with_a_fill_and_a_hatch(material, finish):
    """The table the rotation draws from, entry by entry: its last entry needs a large build."""
    assert isinstance(material_hatch(material), Hatch)
    assert part_fill(None, material)
    assert part_fill(finish, material)

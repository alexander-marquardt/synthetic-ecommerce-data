"""Frozen battered fish is drawn as a flat bag with fish on it (gen#610), not as the kit's carton.

The BBF family drew the generic upright ``box``, the same tall carton a cereal box has. It now
draws the ``fish_bag`` pack shape: a flat pillow bag, wider than it is tall, with battered fish
pieces on the front. The range name and the flavour-color band (the brand band) stay.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import grocery  # noqa: E402
import kit  # noqa: E402
import sheet_extent  # noqa: E402

BBF = next(f for f in grocery.FAMILIES if f.code == "BBF")
FILL = kit.Fill("solid", "#d8a548", "#ffffff")


def render(shape: str = "fish_bag", **marks: str) -> str:
    return kit.render(shape, FILL, "Battered Fish", params=marks or None)


def size(shape: str) -> tuple[float, float]:
    """The width and height of the pack alone, without the sheet's paper and frame."""
    pack = "".join(kit.SHAPES[shape]("#d8a548", FILL, "Battered Fish"))
    left, top, right, bottom = sheet_extent.reach(f'<svg xmlns="http://www.w3.org/2000/svg">{pack}</svg>')
    return right - left, bottom - top


def test_the_battered_fish_family_has_its_own_container() -> None:
    assert BBF.shape == "fish_bag"
    assert BBF.shape != "box"
    assert "fish_bag" in kit.SHAPES


def test_no_battered_fish_flavour_resolves_to_the_carton() -> None:
    """Guard: a per-flavour override in grocery.SHAPES must not put a BBF back in the box."""
    for flavor in BBF.flavors:
        assert grocery.SHAPES.get((BBF.code, flavor.name), BBF.shape) != "box", flavor.name


def test_every_built_battered_fish_style_draws_the_bag() -> None:
    recs = [r for r in grocery.build(grocery.TARGET) if r["product_id"].startswith("GRC-BBF-")]
    assert recs
    assert {r["drawing"]["shape"] for r in recs} == {"fish_bag"}


def test_the_bag_is_flat_not_an_upright_carton() -> None:
    width, height = size("fish_bag")
    assert width > height * 1.1
    box_width, box_height = size("box")
    assert box_height > box_width  # the carton it replaces is the tall one


def test_the_pack_shows_the_fish_pieces() -> None:
    svg = render()
    assert len(re.findall(r'<path class="fish"', svg)) >= 3
    assert 'class="fish"' not in render("box")


def test_the_brand_band_and_label_stay() -> None:
    svg = render(line="Barrowby Kitchen", chips="#d8a548,#8c3b2a")
    assert "Battered Fish" in svg and "Barrowby Kitchen" in svg
    assert "#8c3b2a" in svg

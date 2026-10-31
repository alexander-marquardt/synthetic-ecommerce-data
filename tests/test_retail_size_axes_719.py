"""Every product whose SKUs differ by a size draws each size at its own scale (gen#719).

The ladder of gen#339 read only the worn departments, so a bike, a kettle, a rug and a mattress
drew one image for every size. A type now declares its size axis (``size_axes.AXES``) and one rank
rule scales them all, the toy bikes included. Pack counts, fits and a product of one size stay one
image. These tests read the built templates, so a new type or SKU key has to declare itself.
"""

from __future__ import annotations

import inspect

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    kit_toys,
    pack_scale,
    scale,
    size_axes,
    size_ladder,
)

RECS = scale.templates()
#: Keys that say nothing about the SKU's size or kind: an id, its price, its color.
BOOKKEEPING = {"sku", "price", "in_stock", "color"}
#: The types the issue names; the census below must reach each.
NAMED = ("Bicycle", "Ride-On Toy", "Cable", "Kettle", "Backpack", "Mattress", "Rug", "Towel")


def _varies(rec: dict, key: str) -> bool:
    return len({str(s[key]) for s in rec["skus"] if key in s}) > 1


def _axis(rec: dict) -> str | None:
    """The first declared key that varies within the product, read from the declaration here."""
    return next((k for k in size_axes.AXES.get(rec["product_type"], ()) if _varies(rec, k)), None)


def _rungs(rec: dict, key: str) -> dict[str, set]:
    """``value of the axis -> the scales its SKUs are drawn at``."""
    out: dict[str, set] = {}
    for sku in rec["skus"]:
        out.setdefault(str(sku[key]), set()).add(size_ladder.size_scale(rec, sku))
    return out


SIZED = [(rec, key) for rec in RECS if (key := _axis(rec)) is not None]


def test_the_census_reaches_every_type_the_issue_names():
    assert {rec["product_type"] for rec, _ in SIZED} >= set(NAMED)


def test_each_type_on_a_declared_axis_draws_its_smallest_and_largest_rung_apart():
    wrong: dict[str, str] = {}
    for rec, key in SIZED:
        scales = {s for rung in _rungs(rec, key).values() for s in rung}
        if None in scales or min(scales) != size_ladder.BOTTOM or max(scales) != size_ladder.TOP:
            wrong[rec["product_type"]] = f"{rec['product_id']} {key}: {sorted(scales, key=str)}"
    assert not wrong


def test_each_rung_has_one_scale_and_a_color_one_image_a_rung():
    for rec, key in SIZED:
        assert {len(v) for v in _rungs(rec, key).values()} == {1}, rec["product_id"]
    rec = next(r for r, k in SIZED if r["product_type"] == "Rug" and k == "width_cm")
    color = rec["skus"][0]["color"]
    skus = [s for s in rec["skus"] if s["color"] == color]
    assert len({export.drawing_id(rec, s) for s in skus}) == len({s["width_cm"] for s in skus}) > 1


def test_every_varying_sku_key_is_a_declared_axis_or_named_as_no_size():
    undeclared: set[tuple[str, str]] = set()
    for rec in RECS:
        keys = {k for s in rec["skus"] for k in s} - BOOKKEEPING
        for key in keys:
            if not _varies(rec, key) or isinstance(rec["skus"][0].get(key), (list, dict)):
                continue
            if key in size_axes.AXES.get(rec["product_type"], ()) or key in size_axes.NOT_SIZES:
                continue
            if key == "size" and rec["product_type"] in size_axes.PACK_SIZED:
                continue
            if size_axes.DRAWN_TO_SIZE.get(rec["product_type"]) == key:
                continue
            undeclared.add((rec["product_type"], key))
    assert not undeclared


def test_no_declared_type_names_a_key_no_sku_carries():
    carried = {(r["product_type"], k) for r in RECS for s in r["skus"] for k in s}
    garments = set(size_axes.GARMENT_TYPES)
    stale = {(t, k) for t, keys in size_axes.AXES.items() if t not in garments
             for k in keys if (t, k) not in carried}  # fmt: skip
    assert not stale


def test_a_size_never_shrinks_on_top_of_its_pack_factor():
    both = {r["product_id"] for r in RECS for s in r["skus"]
            if pack_scale.factor(r, s) and size_ladder.size_scale(r, s)}  # fmt: skip
    assert not both


@pytest.mark.parametrize("key", ["units_per_pack", "pack_size"])
def test_a_pack_count_alone_is_not_scaled(key):
    packs = [r for r in RECS if _varies(r, key) and _axis(r) is None]
    assert packs
    assert not [r["product_id"] for r in packs for s in r["skus"] if size_ladder.size_scale(r, s)]


@pytest.mark.parametrize(
    ("key", "rung"),
    [("inside_leg", "waist"), ("inside_leg_in", "size"), ("cup_size", "size"),
     ("fit_length", "size"), ("width", "size_uk")],
)  # fmt: skip
def test_a_fit_shares_its_rung_image(key, rung):
    fitted = [r for r in RECS if _varies(r, key) and _varies(r, rung)]
    assert fitted
    for rec in fitted[:40]:
        assert {len(v) for v in _rungs(rec, rung).values()} == {1}, rec["product_id"]


def test_a_product_of_one_size_is_not_scaled():
    rec = next(r for r in RECS if r["product_type"] == "Kettle" and _axis(r) is None
               and any("capacity_l" in s for s in r["skus"]))  # fmt: skip
    assert {size_ladder.size_scale(rec, s) for s in rec["skus"]} == {None}


def test_an_undeclared_type_is_not_scaled():
    rec = next(r for r in RECS if r["product_type"] == "Heater" and _varies(r, "wattage"))
    assert {size_ladder.size_scale(rec, s) for s in rec["skus"]} == {None}


#: ``(type, the axis, its values smallest first)``: written out here, not read from the code.
ORDERS = [
    pytest.param("Mattress", "bed_size",
                 ["Single (3 ft)", "Double (4 ft 6)", "King Size (5 ft)", "Super King Size (6 ft)"],
                 id="bed-words"),
    pytest.param("Towel", "size", ["Hand Towel", "Bath Towel", "Bath Sheet"], id="towel-words"),
    pytest.param("Plant", "size", ["60 cm", "90 cm", "1.2 m"], id="metres-over-centimeters"),
    pytest.param("Pillowcase", "size_eu", ["50 x 75 cm", "65 x 65 cm", "50 x 90 cm"],
                 id="dimensions-by-area"),
    pytest.param("Gift Bag", "size", ["Small", "Medium", "Large"], id="size-words"),
    pytest.param("Bicycle", "frame_cm", ["50", "54", "58"], id="frame"),
    pytest.param("Storage Jar", "size", ["0.5 L", "1 L", "2 L"], id="liters"),
]  # fmt: skip


@pytest.mark.parametrize(("ptype", "key", "values"), ORDERS)
def test_the_rungs_of_an_axis_climb_in_size_order(ptype, key, values):
    rec = next(r for r in RECS if r["product_type"] == ptype
               and {str(s.get(key)) for s in r["skus"]} >= set(values))  # fmt: skip
    rungs = _rungs(rec, key)
    scales = [next(iter(rungs[v])) for v in values]
    assert None not in scales
    assert scales == sorted(set(scales)), scales


def test_a_value_with_no_place_on_a_ladder_is_refused():
    rec = {"product_type": "Towel", "department": ["Home"], "product_id": "X",
           "skus": [{"size": "Huge"}, {"size": "Bath Sheet"}]}  # fmt: skip
    with pytest.raises(ValueError, match="no place on a size ladder"):
        size_ladder.size_scale(rec, rec["skus"][0])


def test_the_first_key_that_varies_is_the_axis():
    skus = [{"width_cm": "117", "drop_cm": "137"}, {"width_cm": "117", "drop_cm": "183"}]
    rec = {"product_type": "Curtains", "department": ["Home"], "product_id": "X", "skus": skus}
    assert size_ladder.primary(rec, rec["skus"][1]) == ("drop_cm", "183")


def test_the_toy_scaler_is_folded_into_the_ladder():
    assert not hasattr(kit_toys, "_size_scale")
    assert "wheel_size_in" not in inspect.signature(kit_toys.ride_on).parameters
    bikes = [r for r in RECS if r["product_type"] == "Ride-On Toy" and _varies(r, "wheel_size_in")]
    assert bikes
    for rec in bikes:
        assert "wheel_size_in" not in rec["drawing"]["params"], rec["product_id"]
        scales = [next(iter(v)) for k, v in sorted(
            _rungs(rec, "wheel_size_in").items(), key=lambda kv: int(kv[0]))]  # fmt: skip
        assert scales == sorted(set(scales)), rec["product_id"]
        color = rec["skus"][0]["color"]
        svgs = {image_release.render(rec, s) for s in rec["skus"] if s["color"] == color}
        assert len(svgs) == len(scales), rec["product_id"]


def test_a_scaled_drawing_of_a_new_type_is_wrapped_about_its_floor():
    rec = next(r for r, k in SIZED if r["product_type"] == "Bicycle" and k == "frame_cm")
    color = rec["skus"][0]["color"]
    skus = sorted((s for s in rec["skus"] if s["color"] == color), key=lambda s: int(s["frame_cm"]))
    svgs = [image_release.render(rec, s) for s in skus]
    assert b'class="size"' in svgs[0]
    assert b'class="size"' not in svgs[-1]

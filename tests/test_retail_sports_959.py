"""Sports & Outdoors: fishing and golf, then fitness, team and racket sports (gen#959).

The retail Sports & Outdoors department held 1,093 SKUs at the ceiling build against the 11,000
of the #837 mix, and no fishing or golf product, so a search for ``golf balls`` or ``fishing reel``
found nothing. Slice 1 adds a Fishing family (rods, reels, tackle boxes) and a Golf family (clubs,
balls, gloves), each type a derivable spec of its own in ``type_specs/`` drawn by
:mod:`kit_fishing_golf`. These checks hold the slice's Done-when: the ceiling build has at least
3,000 SKUs under the department; each new type's styles have unique ids, titles, twin keys and
SKUs; the rows and their drawings are the same on every call; and a golden slice pins each type's
first derived styles, so a change that moves them shows here.

Slice 2 adds exercise bikes, weight plates and weight benches under Yoga & Fitness, and
basketballs, volleyballs, shin guards, hockey sticks, pickleball paddles and table tennis bats under
Team & Racket Sports, drawn by :mod:`kit_fitness_team`, and raises the floor to 7,000 SKUs.

Slice 3, the last, adds hiking backpacks under a new Hiking family, coolers and insulated water
bottles under Camping, bike lights and bike locks under Cycling, and sleds, snowboards and ski
goggles under a new Winter Sports family, drawn by :mod:`kit_outdoor_winter`, and raises the floor
to the issue's own: 10,450 SKUs, 95% of the 11,000 target.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry
from synthetic_ecommerce_data.domains.retail.sports_helpers import DEPARTMENT

TYPES = (
    "Fishing Rod",
    "Fishing Reel",
    "Tackle Box",
    "Golf Club",
    "Golf Ball",
    "Golf Glove",
    "Exercise Bike",
    "Weight Plate",
    "Weight Bench",
    "Basketball",
    "Volleyball",
    "Shin Guard",
    "Hockey Stick",
    "Pickleball Paddle",
    "Table Tennis Bat",
    "Hiking Backpack",
    "Cooler",
    "Insulated Water Bottle",
    "Bike Light",
    "Bike Lock",
    "Sled",
    "Snowboard",
    "Ski Goggles",
)
KEYS = {
    "Fishing Rod": "fishing_rod",
    "Fishing Reel": "fishing_reel",
    "Tackle Box": "tackle_box",
    "Golf Club": "golf_club",
    "Golf Ball": "golf_ball",
    "Golf Glove": "golf_glove",
    "Exercise Bike": "exercise_bike",
    "Weight Plate": "weight_plate",
    "Weight Bench": "weight_bench",
    "Basketball": "basketball",
    "Volleyball": "volleyball",
    "Shin Guard": "shin_guard",
    "Hockey Stick": "hockey_stick",
    "Pickleball Paddle": "pickleball_paddle",
    "Table Tennis Bat": "table_tennis_bat",
    "Hiking Backpack": "hiking_backpack",
    "Cooler": "cooler",
    "Insulated Water Bottle": "insulated_water_bottle",
    "Bike Light": "bike_light",
    "Bike Lock": "bike_lock",
    "Sled": "sled",
    "Snowboard": "snowboard",
    "Ski Goggles": "ski_goggles",
}
#: The issue's floor at the ceiling build, 95% of the 11,000 target (gen#959's Done-when; slice 1's
#: was 3,000 and slice 2's 7,000).
FLOOR = 10_450


@pytest.fixture(scope="module")
def sports() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == DEPARTMENT]


def test_the_ceiling_build_holds_the_slice_floor_of_sports_skus(sports) -> None:
    skus = sum(r["sku_count"] for r in sports)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(sports) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in sports if r["product_id"] in derived}
    assert set(TYPES) <= kinds, sorted(set(TYPES) - kinds)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(sports, ptype) -> None:
    mine = [r for r in sports if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert spec.derivable
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


def _golden(sports: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in sports if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Fishing Rod": [
        ("BRD-090958B9198F", "Chelthorpe Medium Fiberglass Spinning Fishing Rod", 12, 41.0),
        ("BRD-0D5F1D0F2695", "Ellerhurst Medium Fiberglass Casting Fishing Rod", 6, 63.0),
        ("BRD-0EB768D023F8", "Corley Heavy Fiberglass Fly Fishing Rod", 6, 79.0),
    ],
    "Fishing Reel": [
        ("BRD-062CA0F7D510", "Bramshaw Aluminum 3 Bearing Spinning Fishing Reel", 12, 42.0),
        ("BRD-0654A32212EB", "Huldale Aluminum 5 Bearing Baitcasting Fishing Reel", 12, 17.0),
        ("BRD-08D13BABC85D", "Alwham Graphite 5 Bearing Spinning Fishing Reel", 12, 55.0),
    ],
    "Tackle Box": [
        ("BRD-048D1B5CA18B", "Darcombe 2 Tray Drawer Tackle Box", 8, 18.5),
        ("BRD-05D95C54AC61", "Alwbeck 2 Tray Hip Roof Tackle Box", 4, 25.0),
        ("BRD-06A41B8EA7EC", "Alwstone 3 Tray Drawer Tackle Box", 4, 16.0),
    ],
    "Golf Club": [
        ("BRD-061454920FCD", "Caldham Graphite Driver Golf Club", 8, 62.0),
        ("BRD-084930823321", "Hazley Steel Fairway Wood Golf Club", 6, 79.0),
        ("BRD-0D1525BCCAE1", "Ramside Steel Driver Golf Club", 8, 65.0),
    ],
    "Golf Ball": [
        ("BRD-08134E2AC941", "Haling Urethane 4-Piece Golf Balls", 12, 10.5),
        ("BRD-0E9B6CA81DA4", "Alwthwaite Urethane 2-Piece Golf Balls", 12, 11.0),
        ("BRD-10BDF9821931", "Bixhaugh Urethane 4-Piece Golf Balls", 12, 12.0),
    ],
    "Golf Glove": [
        ("BRD-100228D32570", "Clayborough Cabretta Leather Golf Glove, Left Hand", 16, 17.0),
        ("BRD-145EDF083F79", "Weston Synthetic Golf Glove, Right Hand", 16, 11.0),
        ("BRD-24BC6EB2F440", "Ormthwaite Synthetic Golf Glove, Left Hand", 12, 11.5),
    ],
    "Exercise Bike": [
        ("BRD-07D4885AEAD5", "Ormden Air Folding Exercise Bike with LCD Console", 12, 415.0),
        ("BRD-097F350FD5C5", "Chapwell Friction Upright Exercise Bike with LCD Console", 6, 230.0),
        (
            "BRD-16BFEEA8934B",
            "Holborough Magnetic Folding Exercise Bike with LCD Console",
            6,
            365.0,
        ),
    ],
    "Weight Plate": [
        ("BRD-064B72660B80", "Haling Rubber Coated Olympic Dual-Grip Weight Plate", 8, 9.5),
        ("BRD-150C93EB061D", "Rystead Cast Iron Olympic Tri-Grip Weight Plate", 16, 8.0),
        ("BRD-1E14BEBFA232", "Kelridge Rubber Coated Standard Dual-Grip Weight Plate", 12, 23.0),
    ],
    "Weight Bench": [
        ("BRD-084DC6EDC9C2", "Ramside Commercial Decline Weight Bench with Canvas Pad", 12, 69.0),
        ("BRD-09AC876BFE46", "Woldsbeck Home Flat Weight Bench with Canvas Pad", 6, 110.0),
        ("BRD-09C43470398A", "Reedgate Home Adjustable Weight Bench with Canvas Pad", 6, 61.0),
    ],
    "Basketball": [
        ("BRD-0B0C9DB6B5D2", "Woldsbeck Training Rubber Indoor Basketball", 6, 57.0),
        ("BRD-0BDA01929CA1", "Oldwood Official Composite Outdoor Basketball", 15, 14.5),
        ("BRD-11DB9C56896B", "Sandcliffe Training Rubber Outdoor Basketball", 6, 20.0),
    ],
    "Volleyball": [
        ("BRD-09887005B08D", "Trentlow Recreational Rubber Beach Volleyball", 8, 11.5),
        ("BRD-0B5ACB8B29E0", "Oldwood Recreational Synthetic Beach Volleyball", 4, 11.5),
        ("BRD-0B665262AD3C", "Stavham Official Synthetic Beach Volleyball", 8, 20.0),
    ],
    "Shin Guard": [
        ("BRD-004E62E62DD5", "Ormden Reinforced Plastic Slip-In Shin Guards", 12, 27.0),
        ("BRD-058936D49688", "Stanmere Low-Profile Fiberglass Ankle Shin Guards", 8, 53.0),
        ("BRD-17C0F2F03FEF", "Stanmere Reinforced Plastic Slip-In Shin Guards", 8, 31.0),
    ],
    "Hockey Stick": [
        ("BRD-01F2E7647BC5", "Sandcliffe Fiberglass Ice Hockey Stick with Heel Curve", 4, 40.0),
        ("BRD-07CD62CF36CB", "Torton Fiberglass Ice Hockey Stick with Heel Curve", 4, 38.0),
        ("BRD-09B6FAEA9975", "Warhill Wood Street Hockey Stick with Toe Curve", 6, 31.0),
    ],
    "Pickleball Paddle": [
        (
            "BRD-0FBA1A54AC46",
            "Ellerhurst Lightweight Carbon Fiber Elongated Pickleball Paddle",
            9,
            47.0,
        ),
        (
            "BRD-14F93D3A7068",
            "Ribgarth Heavyweight Carbon Fiber Widebody Pickleball Paddle",
            6,
            85.0,
        ),
        (
            "BRD-161C543DBA51",
            "Lamthwaite Lightweight Fiberglass Widebody Pickleball Paddle",
            9,
            44.0,
        ),
    ],
    "Table Tennis Bat": [
        (
            "BRD-06B9F1E4C580",
            "Branhill Offensive Table Tennis Bat with Wood Blade and Pimpled Rubber",
            8,
            21.0,
        ),
        (
            "BRD-0D49C524A04C",
            "Garton Control Table Tennis Bat with Wood Blade and Pimpled Rubber",
            8,
            18.5,
        ),
        (
            "BRD-0E503A99E6DB",
            "Ribgarth Allround Table Tennis Bat with Carbon Blade and Tacky Rubber",
            6,
            39.0,
        ),
    ],
    "Hiking Backpack": [
        (
            "BRD-0217148FF5B8",
            "Yeldridge Waxed Canvas Internal Frame Hiking Backpack with Roll Top",
            9,
            70.0,
        ),
        (
            "BRD-03CA2B20B102",
            "Holborough Ripstop Nylon Internal Frame Hiking Backpack with Roll Top",
            6,
            115.0,
        ),
        (
            "BRD-072824B1E9FE",
            "Hazley Waxed Canvas External Frame Hiking Backpack with Top Lid",
            6,
            125.0,
        ),
    ],
    "Cooler": [
        ("BRD-02BE3D68D706", "Ravwick Camp Hard Cooler with 2-Day Ice Retention", 4, 44.0),
        ("BRD-03F1C748468E", "Holness Beach Hard Cooler with 2-Day Ice Retention", 9, 36.0),
        ("BRD-06DC4AF8B6DE", "Otdale Marine Wheeled Cooler with 2-Day Ice Retention", 6, 185.0),
    ],
    "Insulated Water Bottle": [
        (
            "BRD-03A2A43A0DD9",
            "Foxfell Gloss Enamel Wide Mouth Insulated Water Bottle with Straw Lid",
            4,
            16.0,
        ),
        (
            "BRD-0697172B2FFD",
            "Weston Powder-Coated Narrow Mouth Insulated Water Bottle with Chug Lid",
            8,
            23.0,
        ),
        (
            "BRD-0AF7B984DC76",
            "Garton Gloss Enamel Narrow Mouth Insulated Water Bottle with Chug Lid",
            12,
            28.0,
        ),
    ],
    "Bike Light": [
        ("BRD-009486C91E1D", "Malwood Battery-Powered Rear Bike Light with 7 Modes", 6, 19.5),
        ("BRD-079D9EA7DDD2", "Halstead USB Rechargeable Rear Bike Light with 3 Modes", 4, 9.5),
        (
            "BRD-07D2AB778C0B",
            "Brockwick Battery-Powered Twin-Pack Bike Light with 3 Modes",
            12,
            20.0,
        ),
    ],
    "Bike Lock": [
        ("BRD-00C9F1091995", "Caldham Heavy-Duty Chain Bike Lock with Combination", 6, 14.0),
        ("BRD-0135703F7B58", "Brackham Heavy-Duty Shackle Bike Lock with Key", 6, 38.0),
        (
            "BRD-038FFF88B966",
            "Bradborough Lightweight Shackle Bike Lock with Combination",
            12,
            15.0,
        ),
    ],
    "Sled": [
        ("BRD-030D8D94AC4E", "Eskcombe Foam 1-Person Toboggan Sled", 6, 39.0),
        ("BRD-17E2A72D21DC", "Reaholme Inflatable 2-Person Toboggan Sled", 6, 29.0),
        ("BRD-193F65DA4C58", "Morlow Molded Plastic 2-Person Steerable Sled", 8, 37.0),
    ],
    "Snowboard": [
        ("BRD-077A266A64B8", "Foxwick Freeride Directional Snowboard with Flat Profile", 12, 270.0),
        (
            "BRD-0B9DF312903E",
            "Ribmoor All-Mountain Directional Snowboard with Flat Profile",
            12,
            345.0,
        ),
        ("BRD-0D170785626A", "Kelridge Freeride True Twin Snowboard with Flat Profile", 12, 325.0),
    ],
    "Ski Goggles": [
        (
            "BRD-07D14410FE27",
            "Ellerfield Polarized Cylindrical Ski Goggles with Over-the-Glasses Fit",
            6,
            88.0,
        ),
        (
            "BRD-0B14C998E7BA",
            "Walbank Polarized Cylindrical Ski Goggles with Regular Fit",
            9,
            115.0,
        ),
        (
            "BRD-126E1E56D41E",
            "Kelridge Mirrored Toric Ski Goggles with Over-the-Glasses Fit",
            12,
            105.0,
        ),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(sports, ptype) -> None:
    assert _golden(sports, ptype) == GOLDEN[ptype]

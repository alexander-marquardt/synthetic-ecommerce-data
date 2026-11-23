"""The redraw order of the product pictures, from the fill sweep and the demo's top 12 (gen#1129).

    uv run python scripts/picture_fill_1129.py --out .agent/fill-1129
    uv run python scripts/redraw_order_1129.py --rows .agent/fill-1129/rows.json

A product type is in the order when it is in scope and its picture fills less than gen#1111's
floor (``FLOOR``, half the product area). A type drawn to scale is out of scope and never in it.
The groups come in three tiers: the redraws the maintainer named, with their own issues
(``NAMED``); the retail groups, by the slots their types fill in the top 12 of the R&I demo's seed
queries (``tests/data/seed_top12_1129.json``), then by worst median area; and the realistic
industrial groups, in the same way. It changes no drawing:
docs/retail-prototype/picture-fill-1129.md.
"""

from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

HITS = Path(__file__).resolve().parents[1] / "tests" / "data" / "seed_top12_1129.json"
#: gen#1111's fill test: a picture under this share of the product area needs a redraw.
FLOOR = 0.50
NAMED_TIER, RETAIL_TIER, INDUSTRIAL_TIER = 1, 2, 3


@dataclass(frozen=True)
class Group:
    """The kits one redraw issue covers. A kit may be ``kit:shape`` (one shape of a kit that
    holds several kinds); ``types`` claims a product type wherever it is drawn."""

    title: str
    kits: tuple[str, ...]
    issue: int = 0  # 0: not filed yet
    tier: int = RETAIL_TIER
    types: tuple[str, ...] = ()


#: The redraws the maintainer named (2026-11-21), in the order the issue lists them.
NAMED = (
    Group("Loose fruit and vegetables", ("kit_produce",), 1111, NAMED_TIER),
    Group("Chocolate", ("kit_chocolate",), 1125, NAMED_TIER, ("Chocolate Box", "Chocolate Bar")),
    Group("Bread", ("kit_bread",), 1126, NAMED_TIER),
    Group(
        "Wine, beer and soft drinks",
        ("kit_drinks", "kit_beer", "kit_soft_drinks"),
        1127,
        NAMED_TIER,
        (
            "Wine",
            "Champagne",
            "Fortified Wine",
            "Beer",
            "Cider",
            "Perry",
            "Soft Drink",
            "Root Beer",
            "Ginger Beer",
        ),
    ),
    Group("Milk and yoghurt", ("kit_dairy",), 1128, NAMED_TIER),
)

APPAREL = ("kit:tshirt", "kit:dress", "kit:blouse")
#: One redraw issue each.
GROUPS = (
    Group("Shoes and boots", ("kit_footwear",)),
    Group(
        "Dresses, tops, jeans and trousers",
        (*APPAREL, "kit_garments", "kit_lowerbody", "mens_pants"),
    ),
    Group("Sweatshirts, pyjamas, sheets, mugs and aprons", ("kit_surfaces",)),
    Group("Underwear and swimwear", ("kit:bra", "kit_underwear", "kit_swimwear")),
    Group(
        "Coats, suits and school uniform",
        ("kit:coat", "kit_coats", "kit_outerwear", "kit_suits", "kit_suit_sets", "kit_school"),
    ),
    Group(
        "Accessories, jewellery and luggage",
        (
            "kit_accessories",
            "kit_jewellery",
            "belt",
            "gloves",
            "hat_cap",
            "scarf",
            "wallet",
            "sunglasses",
            "kit_luggage",
        ),
    ),
    Group("Baby clothes and baby gear", ("kit_baby", "kit_baby_gear")),
    Group(
        "Beauty, hair, grooming and health",
        (
            "kit_beauty",
            "kit_beauty_cotton",
            "kit_skin",
            "kit_grooming",
            "kit_hair",
            "kit_health",
            "kit_health_care",
            "kit_health_feminine",
        ),
    ),
    Group("Bottles and jars (the shared packs)", ("kit_packs",)),
    Group(
        "Grocery packs, cakes and trays",
        (
            "kit:tin",
            "kit:tub",
            "kit:carton",
            "kit:tray",
            "kit:box",
            "kit:box_wide",
            "kit:cake",
            "kit:crisps_bag",
            "kit_grocery",
            "kit_biscuits",
            "kit_punnet",
        ),
    ),
    Group(
        "Cleaning and paper goods",
        ("kit_cleaning", "kit_cleaning_care", "kit_paper", "kit_bags_wrap"),
    ),
    Group(
        "Bedding, towels and soft furnishings", ("kit_home", "kit_softfurn", "kit_bedding_storage")
    ),
    Group("Furniture and sofas", ("kit_furniture", "kit_seating", "kit_storage_furniture")),
    Group("Beds, plants, socks and the other kit_more shapes", ("kit_more",)),
    Group("Gift bags, gifts and party goods", ("kit_round4", "kit_gifts", "kit_party", "stickers")),
    Group("Picture motifs", ("kit_motifs",)),
    Group("Tableware and kitchenware", ("kit_tableware", "kit_cups", "kit_household")),
    Group("Appliances", ("kit_kitchen_appliances", "kit_appliances", "kit_large_appliances")),
    Group(
        "Electronics and office",
        (
            "kit_electronics",
            "kit_audio",
            "kit_gadgets",
            "kit_gaming",
            "kit_printers",
            "kit_smart_home",
            "kit_office",
        ),
    ),
    Group(
        "Garden and patio",
        ("kit_garden", "kit_garden_care", "kit_garden_yard", "kit_patio", "kit_outdoor"),
    ),
    Group(
        "Sports and outdoors",
        ("kit_sports", "kit_fitness_team", "kit_fishing_golf", "kit_cycling", "kit_outdoor_winter"),
    ),
    Group(
        "Car care and car accessories",
        ("kit_automotive", "kit_automotive_electrics", "kit_automotive_interior"),
    ),
    Group("Pets", ("kit_pet_care", "kit_pet_gear", "kit_pets")),
    Group(
        "Toys",
        (
            "kit_toys",
            "kit_toys_craft",
            "kit_toys_learning",
            "kit_toys_play",
            "kit_toys_figures",
            "kit_toy_word_decoys",
        ),
    ),
    Group("Lighting and decor", ("kit_lighting", "kit_decor")),
    Group("Household goods and sewing", ("kit_goods", "kit_plain_goods", "kit_sewing")),
    Group(
        "Drills, hammers, tool sets and ladders",
        (
            "kit_drills",
            "industrial/figures",
            "industrial/household_tool_sets",
            "industrial/picture_hangers",
        ),
        0,
        INDUSTRIAL_TIER,
    ),
    Group(
        "Safety glasses and cut-resistant gloves",
        ("industrial/safety_glasses", "industrial/cut_resistant_gloves"),
        0,
        INDUSTRIAL_TIER,
    ),
    Group(
        "Industrial breadth types (storage, workwear, hand tools, vises and the rest)",
        ("industrial/breadth_shapes", "industrial/kit_assortment"),
        0,
        INDUSTRIAL_TIER,
    ),
)


def group_of(
    row: dict, named: tuple[Group, ...] = NAMED, groups: tuple[Group, ...] = GROUPS
) -> Group:
    """The one group a type row belongs to; a row of no group raises, so no picture is dropped."""
    for g in named:
        if row["type"] in g.types or row["kit"] in g.kits:
            return g
    for g in groups:
        if row["kit"] in g.kits or f"{row['kit']}:{row['shape']}" in g.kits:
            return g
    raise KeyError(f"no redraw group holds {row['kit']} {row['type']} ({row['shape']})")


def redraws(types: list[dict]) -> list[dict]:
    """The rows that need a redraw: in scope, and under the fill floor."""
    return [r for r in types if r["in_scope"] and r["area"] < FLOOR]


def slots(hits: dict) -> collections.Counter:
    """Top-12 slots per (product type, shape) over every seed query."""
    out: collections.Counter = collections.Counter()
    for rows in hits["queries"].values():
        for _domain, ptype, shape, n in rows:
            out[(ptype, shape)] += n
    return out


def order(
    types: list[dict],
    hits: dict,
    named: tuple[Group, ...] = NAMED,
    groups: tuple[Group, ...] = GROUPS,
) -> list[dict]:
    """One row per group with a type to redraw (and every named one), in redraw order."""
    filled = slots(hits)
    members: dict[Group, list[dict]] = collections.defaultdict(list)
    for r in redraws(types):
        members[group_of(r, named, groups)].append(r)
    rows = []
    for i, g in enumerate((*named, *groups)):
        rs = members.get(g, [])
        if not rs and g.tier != NAMED_TIER:
            continue
        rows.append(
            {
                "group": g,
                "types": rs,
                "slots": sum(filled[(r["type"], r["shape"])] for r in rs),
                "skus": sum(r["skus"] for r in rs),
                "area": statistics.median(r["area"] for r in rs) if rs else None,
                "named": i if g.tier == NAMED_TIER else 0,
            }
        )
    return sorted(
        rows,
        key=lambda r: (
            (r["group"].tier, r["named"])
            if r["group"].tier == NAMED_TIER
            else (r["group"].tier, -r["slots"], r["area"], r["group"].title)
        ),
    )


def order_table(rows: list[dict]) -> str:
    lines = [
        "| # | redraw | issue | kits | types under 50% | SKUs | median area % | top-12 slots |",
        "|" + "---|" * 8,
    ]
    for i, r in enumerate(rows, 1):
        g = r["group"]
        issue = f"gen#{g.issue}" if g.issue else "to file"
        area = "-" if r["area"] is None else f"{r['area']:.0%}"
        kits = ", ".join(f"`{k}`" for k in sorted({t["kit"] for t in r["types"]}) or g.kits)
        lines.append(
            f"| {i} | {g.title} | {issue} | {kits} | {len(r['types'])} | {r['skus']:,} "
            f"| {area} | {r['slots']} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--rows", type=Path, required=True, help="the sweep's rows.json")
    parser.add_argument("--hits", type=Path, default=HITS, help="the recorded top 12")
    args = parser.parse_args(argv)
    types = json.loads(args.rows.read_text(encoding="utf-8"))["types"]
    hits = json.loads(args.hits.read_text(encoding="utf-8"))
    sys.stdout.write(order_table(order(types, hits)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

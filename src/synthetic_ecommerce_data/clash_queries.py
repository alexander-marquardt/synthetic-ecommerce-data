"""The search-demo clash queries of the large appliances, without and with a policy (gen#1116).

Ten queries whose words name an appliance and something else (``washer`` is a laundry machine and a
flat washer), or that name one thing only (``m8 washer``). Each :class:`Clash` states its families,
the policy that settles it and what the policy is meant to do. A policy is a filter or a boost on a
structured field, the shape R&I's policies take, applied to the no-policy ranker of
``domains/retail/baseline_rank.py`` (text score, no popularity). It is the generator's measurement
of what the data can support, not a policy anyone authored in R&I.

:func:`catalog` is the retail templates and the default industrial build, as the combined catalog
holds them. A domain reaches core only, never another domain (#125), so this module, which needs
both builds, is above ``domains/`` like :mod:`rule_rowsets`. ``python -m
synthetic_ecommerce_data.clash_queries`` prints the table of
``docs/retail-prototype/clash-queries-1116.md``; ``--ceiling`` measures the scaled retail build in
place of the templates. Standard library only.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field

from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.domains.industrial import generate
from synthetic_ecommerce_data.domains.retail import baseline_rank as br
from synthetic_ecommerce_data.domains.retail import scale
from synthetic_ecommerce_data.domains.retail.distractors import tokens

#: What a boosted record's text score is multiplied by.
BOOST = 10.0
SIZE = 10
#: The ``product_type`` condition that any record of the industrial build meets.
INDUSTRIAL = "(industrial)"

Where = Mapping[str, tuple[str, ...]]
"""``product_type`` or an attribute key to the values that meet it; every key must be met."""

WASHERS: Where = {"appliance_type": ("Washing Machine", "Washer Dryer")}
DRYERS: Where = {"appliance_type": ("Tumble Dryer (Heat Pump)", "Tumble Dryer (Condenser)",
                                    "Tumble Dryer (Vented)")}  # fmt: skip
FLAT: Where = {"product_type": ("washer_flat",)}
COOKERS: Where = {"product_type": ("Range Cooker",)}
IRONS: Where = {"product_type": ("Steam Iron",)}
FREEZERS: Where = {"appliance_type": ("Chest Freezer", "Upright Freezer")}


@dataclass(frozen=True)
class Clash:
    """One query: its families by name, the policy (a filter, a boost) and the issue's Expected."""

    query: str
    families: Mapping[str, Where]
    expected: str
    filter: Where = field(default_factory=dict)
    boost: Where = field(default_factory=dict)

    def policy(self) -> str:
        parts = [f"filter {_says(self.filter)}"] if self.filter else []
        parts += [f"{_says(self.boost)} x{BOOST:g}"] if self.boost else []
        return "; ".join(parts)


CLASHES: tuple[Clash, ...] = (
    Clash("washer", {"washing machines": WASHERS, "flat washers": FLAT,
                     "washer fluid": {"product_type": ("Windshield Washer Fluid",)}},
          "Both families; a policy can rank by department intent.", boost=WASHERS),
    Clash("washer 8kg", {"washing machines": WASHERS}, "Laundry only (kg load).",
          filter={**WASHERS, "load": ("8",)}),
    Clash("m8 washer", {"flat washers": FLAT}, "Fasteners only (thread size).",
          filter={**FLAT, "size": ("M8",)}),
    Clash("dryer", {"tumble dryers": DRYERS,
                    "hair dryers": {"product_type": ("Hair Dryer",)}},
          "Both families.", boost=DRYERS),
    Clash("heat pump dryer", {"tumble dryers": DRYERS}, "Laundry only.",
          filter={"appliance_type": ("Tumble Dryer (Heat Pump)",)}),
    Clash("range", {"range cookers": COOKERS,
                    "signal and firing range": {"product_type": ("Baby Monitor", "Water Gun")}},
          "Range cookers first for a kitchen intent.", boost=COOKERS),
    Clash("range cooker 90cm", {"range cookers": COOKERS}, "Cookers only (width).",
          filter={**COOKERS, "item_width": ("90",)}),
    Clash("iron", {"clothes irons": IRONS, "industrial iron": {"product_type": (INDUSTRIAL,)}},
          "Both; a policy decides.", boost=IRONS),
    Clash("steam iron", {"clothes irons": IRONS}, "Irons only.", filter=IRONS),
    Clash("freezer", {"freezers": FREEZERS,
                      "freezer bags": {"product_type": ("Food Storage Bags",)}},
          "Appliances first; freezer bags as the second family.", boost=FREEZERS),
)  # fmt: skip


def _says(where: Where) -> str:
    return ", ".join(f"{key} = {' or '.join(values)}" for key, values in where.items())


def meets(record: dict, where: Where) -> bool:
    for key, values in where.items():
        if key == "product_type":
            if INDUSTRIAL in values and record.get("industrial"):
                continue
            if record["product_type"] not in values:
                return False
        else:
            held = {str(a["value"]) for a in record["attributes"] if a["key"] == key}
            if not held & set(values):
                return False
    return True


def industrial_records() -> list[dict]:
    """The default industrial build in the retail record's shape."""
    built = generate.generate(generate.GeneratorConfig())
    return [
        {"title": d["title"], "description": d.get("description", ""),
         "product_id": str(d["sku"]), "product_type": d["product_type"], "industrial": True,
         "attributes": [{"key": k, "value": v} for k, vs in d["facets"].items() for v in vs]}
        for line in built.lines
        for d in emit.flat_documents(built, line)
    ]  # fmt: skip


def catalog(retail: list[dict] | None = None) -> list[dict]:
    return [*(scale.templates() if retail is None else retail), *industrial_records()]


def hits(index: br.Index, clash: Clash, *, policy: bool) -> list[dict]:
    """Every record the query's words find, best first; with the policy when asked."""
    words = tokens(clash.query)
    scored = []
    for i in index.candidates(words):
        record = index.catalog[i]
        if policy and clash.filter and not meets(record, clash.filter):
            continue
        factor = BOOST if policy and clash.boost and meets(record, clash.boost) else 1.0
        scored.append((index.text_score(i, words) * factor, record))
    scored.sort(key=lambda s: (-s[0], s[1]["product_id"]))
    return [record for _, record in scored]


def families(found: list[dict], clash: Clash) -> dict[str, tuple[int, int]]:
    """Each family's count in ``found`` and the place of its first record (0: none)."""
    out = {}
    for name, where in clash.families.items():
        places = [n for n, record in enumerate(found, 1) if meets(record, where)]
        out[name] = (len(places), places[0] if places else 0)
    return out


def _label(record: dict) -> str:
    for attribute in record["attributes"]:
        if attribute["key"] == "appliance_type":
            return str(attribute["value"])
    return record["product_type"]


def _top(found: list[dict]) -> str:
    counts = Counter(_label(r) for r in found[:SIZE])
    return ", ".join(f"{name} {n}" for name, n in counts.most_common())


def _present(found: list[dict], clash: Clash) -> str:
    return ", ".join(
        f"{name} {n} (first at {first})" if n else f"{name} none"
        for name, (n, first) in families(found, clash).items()
    )


def table(index: br.Index) -> str:
    rows = [
        "| Query | Expected | Families found without a policy | Top 10 without a policy "
        "| Policy | Families found with it | Top 10 with it |",
        "|---|---|---|---|---|---|---|",
    ]
    for clash in CLASHES:
        off, on = hits(index, clash, policy=False), hits(index, clash, policy=True)
        rows.append(
            f"| `{clash.query}` | {clash.expected} | {_present(off, clash)} | {_top(off)} "
            f"| {clash.policy()} | {_present(on, clash)} | {_top(on)} |"
        )
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--ceiling", action="store_true", help="the scaled retail build")
    retail = None
    if parser.parse_args(argv).ceiling:
        from synthetic_ecommerce_data.domains.retail import retail_figures  # noqa: PLC0415

        retail = retail_figures.ceiling().records
    print(table(br.Index(catalog(retail))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

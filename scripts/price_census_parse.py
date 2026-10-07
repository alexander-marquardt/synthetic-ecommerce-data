"""Parse the pages ``scripts/price_census_collect.py`` cached into the
lock-nut and set-screw entries of ``reference-statistics/P2_price_census.json``
(#69), following the census ``method`` block.

    uv run python scripts/price_census_parse.py          # print the two entries
    uv run python scripts/price_census_parse.py --write  # and write them in

Sources. Nylon-insert lock nuts come from product-group pages, as #57's deep
types do: a page is kept when its group specs say ``Nylon Insert``. Hex
socket set screws have no archived group pages, so they come from category
list pages, where each row gives a brand, a full spec description, the shown
price and the sale unit; a cell is then built from brand plus equal
non-dimension specs instead of from one page. The locknut category pages the
collector also fetched are not used: every row on them is the same label the
group pages carry, and their list markup does not pair a row's brand with its
description reliably.

Three rules the ``method`` block does not spell out, stated here so a rerun
reproduces them:

* A row showing a clearance price beside its regular price is priced at the
  regular price, the structure the census measures; the share of such rows is
  recorded as ``clearance_rows_priced_at_regular``.
* Quantiles are linear-interpolated (type 7), rounded to 4 decimals; slopes
  and shares to 3, as #57's figures are.
* ``brand_price_index`` is per brand: the median, over the specs it shares,
  of its median per-piece price over the spec's geometric mean.
"""

from __future__ import annotations

import html
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from synthetic_industrial_products.catalog.price import ending_class
from synthetic_industrial_products.dimensions import (
    DimensionParseError,
    parse_length,
    parse_thread,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "price_census"
CENSUS = ROOT / "reference-statistics" / "P2_price_census.json"

#: Where an entry this script writes came from: not the run behind #57.
COLLECTED_BY = (
    "scripts/price_census_collect.py and scripts/price_census_parse.py (#69); "
    "MANIFEST.json P2_price_census.extension_69 holds the run's constraints and accounting"
)
#: The distributor's own labels, for ``house_label_over_other_brands``.
HOUSE_LABELS = frozenset({"GRAINGER APPROVED"})
#: Group-page attributes that name the size, so a cell does not hold them
#: equal. Every other attribute, the pack quantity among them, is held.
SIZE_ATTRIBUTES = frozenset(
    {"Thread Size", "Dia./Thread Size", "Width", "Height", "Max. Height", "Thickness"}
)
QUANTILES = (("p10", 0.10), ("p25", 0.25), ("p50", 0.50), ("p75", 0.75), ("p90", 0.90))
#: Words a list description puts before the material: a thread series or line.
SERIES = frozenset({"Coarse", "Fine", "Mil Spec"})
#: A list row's non-dimension specs: a cell and a brand-spread spec hold them equal.
HELD_LIST_SPECS = ("Series", "Material", "Finish", "Point Type")
#: Drives that make a set screw another type than hex socket.
OTHER_DRIVE = re.compile(r"spline|torx|slotted|square head|knurled|assortment|kit", re.I)


@dataclass(frozen=True)
class Row:
    sku: str
    brand: str
    captured: str  # the capture timestamp, YYYYMMDDhhmmss
    page: str
    price: float  # the price used: the regular price when a clearance one is shown
    clearance: bool
    pack: int  # 1 for a row sold each
    sale_unit: str  # "each" or "pack"
    key: float  # the key dimension, inches
    length: float | None  # inches; set screws only
    held: tuple[tuple[str, str], ...]  # the non-dimension specs a cell holds equal

    @property
    def per_piece(self) -> float:
        return self.price / self.pack


# --- reading values -----------------------------------------------------------


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def thread_inches(value: str) -> float | None:
    """A thread's major diameter in inches (``method.key_dimension``).

    A bare ``N-T`` is a #-gauge screw number when T is 24 or more (the coarsest
    gauge thread is #12-24, the finest whole-inch one 1-14), so ``8-32`` is
    #8, not 8 inches; an M-size is millimetres whatever pitch follows it.
    """
    value = value.replace(chr(0x2033), '"').strip()  # a double prime for inches
    metric = re.match(r"M(\d+(?:\.\d+)?)", value, re.I)
    if metric:
        return float(metric.group(1)) / 25.4
    gauge = re.fullmatch(r"#?(\d+)-(\d+)", value)
    if gauge and (value.startswith("#") or int(gauge.group(2)) >= 24):
        return 0.060 + 0.013 * int(gauge.group(1))
    try:
        return parse_thread(value).major.inches
    except DimensionParseError:
        return None


def length_inches(value: str) -> float | None:
    """A length in inches: ``1 1/2 In``, ``3/8 In.``, ``3/8"`` or ``6mm``."""
    value = re.sub(r"(\d) (\d+/\d+)", r"\1-\2", value.strip())
    value = re.sub(r"\s*In\.?$", '"', value)
    try:
        return parse_length(value).inches
    except DimensionParseError:
        return None


def sale_unit(unit: str) -> tuple[str, int] | None:
    """``("each", 1)`` or ``("pack", N)`` from ``/ each`` or ``/ pkg. of N``."""
    unit = unit.strip().lower()
    if unit.endswith("each"):
        return "each", 1
    pack = re.search(r"of\s+([\d,]+)", unit)
    if pack:
        return "pack", int(pack.group(1).replace(",", ""))
    return None


def _price(block: str) -> tuple[float, str, bool] | None:
    """The price used, its sale unit text, and whether a clearance price was
    shown beside it."""
    reduced = re.search(r'gcprice-reduced-value"[^>]*>\s*\$([\d,.]+).*?'
                        r'gcprice-reduced-unit"[^>]*>([^<]*)', block, re.S)
    if reduced:
        return float(reduced.group(1).replace(",", "")), reduced.group(2), True
    shown = re.search(r'gcprice-value"[^>]*>\s*\$([\d,.]+).*?gcprice-unit"[^>]*>([^<]*)',
                      block, re.S)
    if shown is None:
        shown = re.search(r'class="price"[^>]*>\s*\$([\d,.]+).*?class="bottomText"[^>]*>([^<]*)',
                          block, re.S)
    if shown is None:
        return None
    return float(shown.group(1).replace(",", "")), shown.group(2), False


# --- the two page kinds -------------------------------------------------------


def group_rows(page: str, captured: str, name: str) -> list[Row] | None:
    """A product-group page's rows, or ``None`` when it is not a nylon-insert
    locknut page."""
    brand = re.search(r'class="brand-container"[^>]*>(.*?)</', page, re.S)
    rows = []
    for block in page.split('class="childProductContainer"')[1:]:
        block = block.split('class="table-row')[0]
        names = [_text(n) for n in re.findall(r'class="techSpecName"[^>]*>(.*?)</', block, re.S)]
        values = [_text(v) for v in re.findall(r'class="techSpecValue"[^>]*>(.*?)</', block, re.S)]
        specs = dict(zip(names, values, strict=False))
        if "nylon insert" not in specs.get("Type", "").lower():
            continue
        sku = re.search(r'childProductData item".*?(?:childDataValue"[^>]*>|&nbsp;)\s*([A-Z0-9]+)',
                        block, re.S)
        priced = _price(block)
        size = specs.get("Thread Size") or specs.get("Dia./Thread Size")
        key = thread_inches(size) if size else None
        unit = sale_unit(priced[1]) if priced else None
        if sku is None or priced is None or key is None or unit is None:
            continue
        held = tuple(sorted((k, v) for k, v in specs.items() if k not in SIZE_ATTRIBUTES))
        rows.append(Row(sku.group(1), _text(brand.group(1)) if brand else "", captured, name,
                        priced[0], priced[2], unit[1], unit[0], key, None, held))
    return rows if rows else None


def _described(description: str) -> dict[str, str]:
    """A list row's description as attributes: the material is the first
    piece after the item name, and ``Plain Finish`` / ``Cup Point`` are read as
    ``Finish`` / ``Point Type`` so both description styles agree."""
    pieces = [p.strip() for p in description.split(",")]
    out = {"Item": pieces[0]}
    # "Standard" says nothing; a thread series or a line may stand before the material.
    rest = [p for p in pieces[1:] if p != "Standard"]
    if rest and rest[0] in SERIES:
        out["Series"] = rest.pop(0)
    if rest:
        out["Material"] = rest[0]
    for piece in rest[1:]:
        keyed = re.match(r"(Finish|Point Type|Thread Size|Overall Length|Length|Package Quantity|"
                         r"Package Qty|Package|Drive Type)\s+(.+)", piece)
        if keyed:
            out[keyed.group(1)] = keyed.group(2)
        elif piece.endswith(" Finish"):
            out["Finish"] = piece[: -len(" Finish")]
        elif piece.endswith(" Point") and "Dia" not in piece:
            out["Point Type"] = piece[: -len(" Point")]
        elif piece == "Hex Socket":
            out["Drive Type"] = piece
    return out


def list_rows(page: str, captured: str, name: str) -> list[Row]:
    """A category list page's hex socket set screw rows."""
    rows = []
    for block in page.split('class="productBrand"')[1:]:
        brand = _text(block[: block.find("</")].lstrip(">"))
        ld = re.search(r'class="LD hidden"[^>]*>(.*?)</', block, re.S)
        sku = re.search(r"Item #.*?productInfoValueList\"[^>]*>\s*([A-Z0-9]+)", block, re.S)
        priced = _price(block)
        if ld is None or sku is None or priced is None:
            continue
        description = _text(ld.group(1))
        spec = _described(description)
        if "Set Screw" not in spec["Item"] or OTHER_DRIVE.search(description):
            continue
        if "Socket" not in spec["Item"] and spec.get("Drive Type") != "Hex Socket":
            continue
        key = thread_inches(spec.get("Thread Size", ""))
        length = length_inches(spec.get("Overall Length") or spec.get("Length") or "")
        unit = sale_unit(priced[1])
        if key is None or length is None or unit is None:
            continue
        held = tuple(sorted((k, spec[k]) for k in HELD_LIST_SPECS if k in spec))
        rows.append(Row(sku.group(1), brand, captured, name, priced[0], priced[2], unit[1],
                        unit[0], key, length, held))
    return rows


# --- the figures --------------------------------------------------------------


def quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    pos = q * (len(ordered) - 1)
    low = math.floor(pos)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (pos - low) * (ordered[high] - ordered[low])


def quantiles(values: Sequence[float]) -> dict[str, float] | None:
    if not values:
        return None
    return {name: round(quantile(values, q), 4) for name, q in QUANTILES}


def ordered_pairs(cells: Iterable[list[tuple[float, float]]]) -> dict:
    """``method.slope`` over cells of ``(x, per_piece)``: the pooled
    within-cell log-log slope and every pair whose x differs."""
    sxy = sxx = 0.0
    n_cells = n_skus = more = less = equal = 0
    for cell in cells:
        if len({x for x, _ in cell}) < 2:
            continue
        n_cells += 1
        n_skus += len(cell)
        lx = [math.log(x) for x, _ in cell]
        ly = [math.log(y) for _, y in cell]
        mx, my = statistics.fmean(lx), statistics.fmean(ly)
        sxy += sum((a - mx) * (b - my) for a, b in zip(lx, ly, strict=True))
        sxx += sum((a - mx) ** 2 for a in lx)
        for i, (xi, yi) in enumerate(cell):
            for xj, yj in cell[i + 1:]:
                if xi == xj:
                    continue
                (_, small), (_, large) = sorted([(xi, yi), (xj, yj)])
                more += large > small
                less += large < small
                equal += large == small
    pairs = more + less + equal
    return {
        "loglog_slope": round(sxy / sxx, 3) if sxx else None,
        "n_cells": n_cells,
        "n_skus_in_cells": n_skus,
        "n_pairs": pairs,
        "share_larger_costs_more": round(more / pairs, 3) if pairs else None,
        "share_larger_costs_less": round(less / pairs, 3) if pairs else None,
        "share_equal_price": round(equal / pairs, 3) if pairs else None,
    }


def _cells(rows: Iterable[Row], cell_of: Callable[[Row], tuple], x_of: Callable[[Row], float]):
    cells: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        cells[cell_of(row)].append((x_of(row), row.per_piece))
    return cells.values()


def _spec(row: Row) -> tuple:
    return (row.key, row.length, row.held)


def brand_spread(rows: Sequence[Row]) -> dict:
    """``method.brand_spread``, or why it cannot be measured."""
    brands = {row.brand for row in rows}
    if len(brands) < 2:
        return {"not_measured": "every priced row carries one label (the distributor's own), "
                                "so no spec is offered by two brands and no brand spread, "
                                "brand price index or house-label ratio exists"}
    by_spec: dict[tuple, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        by_spec[_spec(row)][row.brand].append(row.per_piece)
    shared = {s: {b: statistics.median(v) for b, v in per.items()}
              for s, per in by_spec.items() if len(per) >= 2}
    if not shared:
        return {"not_measured": f"{len(brands)} brands, but no spec is offered by two of them"}
    materials = {dict(spec[2]).get("Material") for spec in shared}
    if len(materials) == 1:
        # One material line is not the type: its spread and tier say nothing of the rest.
        pair = {b for medians in shared.values() for b in medians}
        return {
            "n_specs_with_2plus_brands": len(shared),
            "not_measured": f"every spec two brands share is {materials.pop()} "
                            f"({len(pair)} brands); no other material is offered by two "
                            "brands, so a spread, brand index or house-label ratio would "
                            "describe that one line, not the type",
        }
    ratios, house, index = [], [], defaultdict(list)
    for medians in shared.values():
        ratios.append(max(medians.values()) / min(medians.values()))
        geo = math.exp(statistics.fmean(math.log(v) for v in medians.values()))
        for brand, value in medians.items():
            index[brand].append(value / geo)
        own = [v for b, v in medians.items() if b in HOUSE_LABELS]
        other = [v for b, v in medians.items() if b not in HOUSE_LABELS]
        if own and other:
            house.append(statistics.median(own) / statistics.median(other))
    return {
        "n_specs_with_2plus_brands": len(shared),
        "max_over_min_ratio": quantiles(ratios),
        "n_brands_indexed": len(index),
        "brand_price_index_quantiles": quantiles([statistics.median(v) for v in index.values()]),
        "house_label_over_other_brands": (
            {"n_specs": len(house), "quantiles": quantiles(house)} if house else None
        ),
        "low_confidence": len(shared) < 30,
    }


def pack_vs_each(rows: Sequence[Row]) -> dict:
    packs = [r for r in rows if r.sale_unit == "pack"]
    each = [r for r in rows if r.sale_unit == "each"]
    units = Counter(r.sale_unit for r in rows)
    lx = [math.log(r.pack) for r in rows]
    ly = [math.log(r.price) for r in rows]
    slope = None
    if len(set(lx)) > 1:
        mx, my = statistics.fmean(lx), statistics.fmean(ly)
        slope = round(sum((a - mx) * (b - my) for a, b in zip(lx, ly, strict=True))
                      / sum((a - mx) ** 2 for a in lx), 3)
    by_spec: dict[tuple, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        by_spec[(row.brand, *_spec(row))][row.pack].append(row.per_piece)
    larger = []
    for sizes in by_spec.values():
        if len(sizes) >= 2:
            small, large = min(sizes), max(sizes)
            larger.append(statistics.median(sizes[large]) / statistics.median(sizes[small]))
    return {
        "sale_unit_share": {k: round(v / len(rows), 3) for k, v in units.most_common()},
        "pack_quantity_counts": {
            str(k): v for k, v in sorted(Counter(r.pack for r in packs).items())
        },
        "pack_price_quantiles": quantiles([r.price for r in packs]),
        "pack_per_piece_quantiles": quantiles([r.per_piece for r in packs]),
        "each_price_quantiles": quantiles([r.price for r in each]),
        "pooled_loglog_slope_price_on_pack_qty": slope,
        "same_spec_larger_pack_per_piece_ratio": (
            {"n": len(larger), "quantiles": quantiles(larger)} if larger else None
        ),
    }


def endings(rows: Sequence[Row]) -> dict:
    classes = Counter(ending_class(r.price) for r in rows)
    digits = Counter(round(r.price * 100) % 10 for r in rows)
    return {
        "n": len(rows),
        "class_share": {k: round(v / len(rows), 4) for k, v in classes.most_common()},
        "last_cent_digit_share": {str(d): round(digits[d] / len(rows), 4) for d in range(10)},
    }


def entry(rows: Sequence[Row], pages: dict[str, int], key_attribute: str, *,
          length_held: bool) -> dict:
    """One ``deep_types`` entry, in #57's field order."""
    def slope_cell(row: Row) -> tuple:
        return (row.page if not length_held else row.brand, row.held, row.pack, row.length)

    def length_cell(row: Row) -> tuple:
        return (row.brand, row.held, row.pack, row.key)

    return {
        "n": len(rows),
        "low_confidence": len(rows) < 30,
        "n_brands": len({r.brand for r in rows}),
        "capture_years": dict(sorted(Counter(r.captured[:4] for r in rows).items())),
        "price_quantiles_usd": quantiles([r.price for r in rows]),
        "per_piece_quantiles_usd": quantiles([r.per_piece for r in rows]),
        "key_dimension_attribute": key_attribute,
        "price_vs_key_dimension": ordered_pairs(_cells(rows, slope_cell, lambda r: r.key)),
        "brand_spread_same_spec": brand_spread(rows),
        "price_vs_length_at_fixed_diameter": (
            ordered_pairs(_cells(rows, length_cell, lambda r: r.length)) if length_held else None
        ),
        "pack_vs_each": pack_vs_each(rows),
        "endings": endings(rows),
        "clearance_rows_priced_at_regular": round(sum(r.clearance for r in rows) / len(rows), 3),
        "pages": pages,
        "collected_by": COLLECTED_BY,
    }


def latest(rows: Iterable[Row]) -> list[Row]:
    """``method.dedupe``: one record per SKU, the latest capture wins."""
    best: dict[str, Row] = {}
    for row in rows:
        if row.sku not in best or row.captured > best[row.sku].captured:
            best[row.sku] = row
    return sorted(best.values(), key=lambda r: r.sku)


def measure(raw: Path = RAW) -> dict[str, dict]:
    pages = json.loads((raw / "pages.json").read_text())
    groups: list[Row] = []
    listed: list[Row] = []
    tally = {kind: Counter() for kind in ("locknut_group", "setscrew_category")}
    for page in pages:
        kind = page["kind"]
        if kind not in tally:
            continue
        tally[kind]["pages_fetched"] += 1
        if page["file"] is None:
            tally[kind]["pages_not_archived"] += 1
            continue
        body = (raw / page["file"]).read_text(encoding="utf-8", errors="replace")
        captured = page["timestamp"]
        if kind == "locknut_group":
            found = group_rows(body, captured, page["file"])
            if found is None:
                tally[kind]["pages_not_nylon_insert_or_no_priced_rows"] += 1
                continue
            groups += found
        else:
            found = list_rows(body, captured, page["file"])
            if not found:
                tally[kind]["pages_no_priced_rows"] += 1
                continue
            listed += found
        tally[kind]["pages_used"] += 1
    return {
        "lock_nuts_nylon_insert": entry(latest(groups), dict(tally["locknut_group"]),
                                        "Thread Size", length_held=False),
        "set_screws_hex_socket": entry(latest(listed), dict(tally["setscrew_category"]),
                                       "Thread Size", length_held=True),
    }


def request_accounting(raw: Path = RAW) -> dict:
    log = [json.loads(line) for line in (raw / "requests.jsonl").read_text().splitlines()]
    return {
        "total_http_requests": len(log),
        "status_codes": dict(sorted(Counter(str(r["status"]) for r in log).items())),
        "requests_by_phase": dict(Counter(r["phase"] for r in log)),
    }


def main(argv: list[str]) -> None:
    entries = measure()
    print(json.dumps({"deep_types": entries, "request_accounting": request_accounting()},
                     indent=1))
    if "--write" in argv:
        census = json.loads(CENSUS.read_text())
        census["deep_types"].update(entries)
        CENSUS.write_text(json.dumps(census, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])

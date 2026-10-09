"""The retail catalog in the one output standard (gen#125, :mod:`..core.standard`).

:func:`documents` turns each record of the 328-style build
(:func:`build_preview4.samples`) into the nested document the industrial domain
emits, and :func:`synthetic_ecommerce_data.core.standard.check_catalog` passes it
(``tests/test_output_standard.py``):

- ``skus`` become ``variants``; each SKU option (color, sizes, leg length, ...)
  becomes a variant-level attribute entry (:data:`OPTIONS`), a measurement split
  into magnitude, ``unit_code`` and ``value_canonical`` by the core's own
  :func:`~synthetic_ecommerce_data.core.entry.split`;
- ``price`` stays the GBP amount, ``currency`` says GBP; ``in_stock`` stays the
  yes/no (the build models no stock count, so no ``stock`` is written);
- the retail-only top-level facts (department, color and size options, offer
  flags, rating, ...) become product-level attribute entries (:data:`FACTS`);
- ``image_id`` is ``<product type>/<product id>/<drawing spec digest>``: one
  image per distinct drawing (a SKU's drawing is its product's with the SKU's
  color swatch), stable for a given spec. The SVGs are rendered later.

Fields the standard derives itself (``price_min``/``price_max``, ``sku_count``)
or carries nowhere (``drawing``) are dropped (:data:`DROPPED`). A field this
module does not name is a KeyError, never a silent skip.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from build_preview4 import samples

from synthetic_ecommerce_data.core import standard
from synthetic_ecommerce_data.core.emit import write_jsonl
from synthetic_ecommerce_data.core.entry import split

#: The image package's top-level folder (:mod:`image_release`), served beside the
#: industrial bundle's under one images mount, so a URL is ``/images/<root>/<path>``.
IMAGE_ROOT = "retail"
IMAGE_BASE_URL = f"/images/{IMAGE_ROOT}"

#: SKU option -> (key, name, unit): one variant-level entry each; a unit splits it.
OPTIONS: dict[str, tuple[str, str, str | None]] = {
    "color": ("color", "Color", None),
    "color_family": ("color_family", "Color family", None),
    "size": ("size", "Size", None),
    "size_uk": ("size_uk", "Size (UK)", None),
    "size_eu": ("size_eu", "Size (EU)", None),
    "size_us": ("size_us", "Size (US)", None),
    "length": ("length", "Length", None),
    "inside_leg": ("inside_leg", "Inside leg", None),
    "inside_leg_in": ("inside_leg_length", "Inside leg length", "INH"),
    "waist": ("waist", "Waist", None),
    "bed_size": ("bed_size", "Bed size", None),
    "width": ("width", "Width", None),
    "upper_material": ("upper_material", "Upper material", None),
    "finish": ("finish", "Finish", None),
    "dimensions": ("dimensions", "Dimensions", None),
    "length_cm": ("item_length", "Item length", "CMT"),
    "width_cm": ("item_width", "Item width", "CMT"),
    # The grocery build's flavor x pack SKUs (grocery.py, gen#154); a list option
    # (an allergen list, the dietary labels) is one entry per value.
    "flavor": ("flavor", "Flavor", None),
    "scent": ("scent", "Scent", None),
    "variety": ("variety", "Variety", None),
    "pack_size": ("pack_size", "Pack size", None),
    "units_per_pack": ("units_per_pack", "Units per pack", "C62"),
    "net_weight_g": ("net_weight", "Net weight", "GRM"),
    "net_volume_ml": ("net_volume", "Net volume", "MLT"),
    "contains": ("contains", "Contains", None),
    "may_contain": ("may_contain", "May contain", None),
    "dietary": ("dietary", "Dietary", None),
}
#: The SKU fields that are columns of the variant, not options.
SKU_COLUMNS = frozenset({"sku", "price", "in_stock", "ingredients"})

#: Top-level retail fact -> (key, name, unit): product-level entries, one per value.
FACTS: dict[str, tuple[str, str, str | None]] = {
    "department": ("department", "Department", None),
    "collections": ("collection", "Collection", None),
    "sub_collection": ("sub_collection", "Sub-collection", None),
    "audience": ("age_group", "Age group", None),
    "brand_owner": ("brand_owner", "Brand owner", None),
    "size_range": ("size_range", "Size range", None),
    "neckline": ("neckline", "Neckline", None),
    "leg_style": ("leg_style", "Leg style", None),
    "rise": ("rise", "Rise", None),
    "pattern": ("pattern", "Pattern", None),
    "units_per_pack": ("units_per_pack", "Units per pack", "C62"),
    "offer": ("offer", "Offer", None),
    "online_only": ("online_only", "Online only", None),
    "new_in": ("new_in", "New in", None),
    "trending": ("trending", "Trending", None),
    "badges": ("badge", "Badge", None),
    "rating": ("rating", "Rating", None),
    "review_count": ("review_count", "Review count", "C62"),
    "sold_last_5_days": ("sold_last_5_days", "Sold in the last 5 days", "C62"),
    "bestseller_rank": ("bestseller_rank", "Bestseller rank", None),
    "was_price": ("was_price", "Was price", None),
    # A percent is a plain number with "(%)" in its name: prism spells no percent
    # unit (the build record names ABV the same way, class_model.py).
    "discount_pct": ("discount", "Discount (%)", None),
}
#: The unitless facts that are numbers: the flat document's ``facets_num`` holds
#: them, so "4 stars and up" or a was-price range is a range filter.
NUMERIC_FACTS = frozenset({"rating", "bestseller_rank", "was_price", "abv", "discount"})
#: ``unit_size`` in ``unit_measure``: a pack's net content, keyed by its kind.
NET_CONTENT = {"ml": ("net_volume", "Net volume", "MLT"), "g": ("net_weight", "Net weight", "GRM")}
#: Top-level fields that become standard columns rather than entries.
COLUMNS = frozenset({"product_id", "product_type", "title", "brand", "category_path",
                     "category_leaf", "description", "attributes", "currency", "skus",
                     "product_line", "color_options", "size_options", "unit_size",
                     "unit_measure", "ingredients"})  # fmt: skip
#: Fields left out: the standard derives them from the variants, (the drawing)
#: they are the render's input, reached through ``image_id``, or (``abv``) the
#: record's own ``attributes`` already carry them as an entry.
DROPPED = frozenset({"price", "price_min", "price_max", "sku_count", "drawing", "abv"})


def _spelling(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _entry(key: str, name: str, unit: str | None, value: Any) -> dict[str, Any]:
    return {"key": key, "name": name, **split(name, _spelling(value), bare_unit=unit)}


def _entries(spec: tuple[str, str, str | None], value: Any) -> list[dict[str, Any]]:
    values = value if isinstance(value, list) else [value]
    return [_entry(*spec, v) for v in values]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def drawing_spec(rec: dict, sku: dict) -> dict:
    """What one SKU's image draws: its product's drawing in the SKU's color swatch."""
    swatch = next((c for c in rec.get("color_options", ()) if c["color"] == sku.get("color")), None)
    return {"drawing": rec["drawing"], "swatch": swatch}


def image_id(rec: dict, sku: dict) -> str:
    """``<product type>/<product id>/<digest of the drawing spec>``: equal specs, one image."""
    blob = json.dumps(drawing_spec(rec, sku), sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode()).hexdigest()[:12]
    return f"{_slug(rec['product_type'])}/{rec['product_id']}/{digest}"


def _url(image: str) -> str:
    return f"{IMAGE_BASE_URL}/{image}.svg"


def _product_attributes(rec: dict) -> list[dict[str, Any]]:
    out = list(rec["attributes"])
    have = {(e["key"], e["value"]) for e in out}
    for field in rec:
        if field not in FACTS and field not in COLUMNS and field not in DROPPED:
            raise KeyError(f"{rec['product_id']}: no standard home for {field!r}")
    facts = [e for f, spec in FACTS.items() if f in rec for e in _entries(spec, rec[f])]
    facts += [_entry("color", "Color", None, c["color"]) for c in rec.get("color_options", ())]
    families = dict.fromkeys(c["family"] for c in rec.get("color_options", ()) if "family" in c)
    facts += [_entry("color_family", "Color family", None, f) for f in families]
    for option, values in rec.get("size_options", {}).items():
        facts += _entries(OPTIONS[option], values)
    if "unit_size" in rec:
        facts.append(_entry(*NET_CONTENT[rec["unit_measure"]], rec["unit_size"]))
    for e in facts:
        if (e["key"], e["value"]) not in have:
            have.add((e["key"], e["value"]))
            out.append(e)
    return out


def _variant(rec: dict, sku: dict) -> dict[str, Any]:
    image = image_id(rec, sku)
    options = [k for k in sku if k not in SKU_COLUMNS]
    return {
        "sku": sku["sku"],
        "title": rec["title"],
        "description": rec["description"],
        "price": float(sku["price"]),
        "currency": rec["currency"],
        "in_stock": sku["in_stock"],
        "image_id": image,
        "image_url": _url(image),
        "image_detail_url": _url(image),
        **({"ingredients": sku["ingredients"]} if "ingredients" in sku else {}),
        "attributes": [e for k in options for e in _entries(OPTIONS[k], sku[k])],
    }


def standard_document(rec: dict) -> dict[str, Any]:
    """One build record as the standard's nested product document."""
    variants = [_variant(rec, sku) for sku in rec["skus"]]
    path = list(rec["category_path"])
    doc: dict[str, Any] = {
        "product_id": rec["product_id"],
        "product_type": rec["product_type"],
        "title": rec["title"],
        "brand": rec["brand"],
    }
    if "product_line" in rec:
        doc["series"] = rec["product_line"]
    return doc | {
        "category_path": path,
        "category_leaf": rec["category_leaf"],
        "category_depth": len(path),
        "image_id": variants[0]["image_id"],
        "image_url": variants[0]["image_url"],
        "image_detail_url": variants[0]["image_detail_url"],
        **({"ingredients": rec["ingredients"]} if "ingredients" in rec else {}),
        "attributes": _product_attributes(rec),
        "variant_count": len(variants),
        "variants": variants,
    }


def documents() -> list[dict[str, Any]]:
    """The whole retail build, one standard document per style, in build order."""
    return [standard_document(rec) for recs in samples().values() for rec in recs]


def flat_documents() -> list[dict[str, Any]]:
    """The whole retail build, one flat document per SKU: the shape industrial's
    loader reads (:func:`synthetic_ecommerce_data.core.standard.flat_documents`)."""
    return [row for doc in documents() for row in standard.flat_documents(doc, NUMERIC_FACTS)]


def main(argv: list[str] | None = None) -> int:
    """``python prototypes/retail_drawings/export.py OUTDIR``: write ``nested.jsonl``
    and ``flat.jsonl`` (the file a loader takes as ``catalog.ndjson``) into OUTDIR."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("outdir", type=Path)
    args = ap.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    nested = write_jsonl(iter(documents()), args.outdir / "nested.jsonl")
    flat = write_jsonl(iter(flat_documents()), args.outdir / "flat.jsonl")
    print(f"wrote {nested} nested and {flat} flat documents to {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
- the retail-only top-level facts (color and size options, the ``promotion`` and other
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

import colorwords
import facet_leaves
from audience import audience_of
from build_preview4 import samples
from promotion import CAMPAIGN  # noqa: F401 -- the seeded campaign, read through this module

from synthetic_ecommerce_data.core import standard
from synthetic_ecommerce_data.core.emit import write_jsonl
from synthetic_ecommerce_data.core.entry import split
from synthetic_ecommerce_data.core.merchandising import SEED as MERCHANDISING_SEED
from synthetic_ecommerce_data.core.merchandising import blend, log_signal, merchandising_score
from synthetic_ecommerce_data.core.variant_axes import profile, variant_axes

#: The image package's top-level folder (:mod:`image_release`), served beside the
#: industrial bundle's under one images mount, so a URL is ``/images/<root>/<path>``.
IMAGE_ROOT = "retail"
IMAGE_BASE_URL = f"/images/{IMAGE_ROOT}"

#: The one casing of a key's values whatever the authored row spelled ("plain" and "Plain"
#: were two buckets of one facet, gen#255): the casing the catalogue repo reads, ``pattern``
#: lower case and ``rise`` High/Mid/Low.
VALUE_CASE = {"pattern": str.lower, "rise": str.title}

#: Authored product types that are one concept with another, written as the second: "Tee" is a
#: "T-Shirt", the name of its category node. Only the document's ``product_type`` is folded;
#: the image id keeps the authored type, so the 561 tees keep their ``tee/...`` image ids.
PRODUCT_TYPE_FOLDS = {"Tee": "T-Shirt"}

#: SKU option -> (key, name, unit): one variant-level entry each; a unit splits it.
OPTIONS: dict[str, tuple[str, str, str | None]] = {
    "color": ("color", "Color", None),
    "size": ("size", "Size", None),
    "size_uk": ("size_uk", "Size (UK)", None),
    "size_eu": ("size_eu", "Size (EU)", None),
    "size_us": ("size_us", "Size (US)", None),
    # A ring's UK letter and US number are not the garment and footwear sizes, which are
    # numbers of their own scales: a key is shared only when its values are one kind (gen#249).
    "ring_size_uk": ("ring_size_uk", "Ring size (UK)", None),
    "ring_size_us": ("ring_size_us", "Ring size (US)", None),
    "length": ("length", "Length", None),
    "inside_leg": ("inside_leg", "Inside leg", None),
    # A skirt's Petite/Regular/Long fit; not ``length``, which the Combined projection renames to
    # the style's ``garment_length`` (gen#279).
    "fit_length": ("fit_length", "Fit length", None),
    "inside_leg_in": ("inside_leg_length", "Inside leg length", "INH"),
    "waist": ("waist", "Waist", None),
    "bed_size": ("bed_size", "Bed size", None),
    "width": ("width", "Width", None),
    "height": ("height", "Height", None),
    "upper_material": ("upper_material", "Upper material", None),
    "finish": ("finish", "Finish", None),
    "dimensions": ("dimensions", "Dimensions", None),
    "length_cm": ("item_length", "Item length", "CMT"),
    "width_cm": ("item_width", "Item width", "CMT"),
    # A pan's diameter and a bin's or a box's capacity (household_rows.py, gen#200).
    "diameter_cm": ("diameter", "Diameter", "CMT"),
    "capacity_l": ("capacity", "Capacity", "LTR"),
    # A mirror's glass and a bookcase's height (furniture_rows.py, gen#199).
    "height_cm": ("item_height", "Item height", "CMT"),
    "blade_length_cm": ("blade_length", "Blade length", "CMT"),
    # Bags, umbrellas and jewelry (accessory_rows.py, gen#207): a backpack's capacity, an
    # umbrella's canopy, a necklace's length (item_length), a jewelry SKU's metal.
    "canopy_cm": ("canopy_diameter", "Canopy diameter", "CMT"),
    # A parasol's canopy is sold in metres, an umbrella's in centimetres: one key, one kind of
    # value, the unit says which (garden_outdoor specs, gen#203). A furniture set's seats.
    "canopy_m": ("canopy_diameter", "Canopy diameter", "MTR"),
    "seats": ("seats", "Seats", "C62"),
    "metal": ("metal", "Metal", None),
    # A watch's or fitness band's case, in millimetres (jewellery_rows.py, gen#423).
    "case_mm": ("case_diameter", "Case diameter", "MMT"),
    # A building set's sizes, a board game's editions and a craft kit's themes
    # (toys_rows.py, gen#201).
    "piece_count": ("piece_count", "Piece count", "C62"),
    "edition": ("edition", "Edition", None),
    # A dolls' house is sold in three styles (type_specs/dolls_house.py, gen#424).
    "house_style": ("style", "Style", None),
    "theme": ("theme", "Theme", None),
    # The grocery build's flavor x pack SKUs (grocery.py, gen#154); a list option
    # (an allergen list, the dietary labels) is one entry per value.
    "flavor": ("flavor", "Flavor", None),
    "scent": ("scent", "Scent", None),
    "variety": ("variety", "Variety", None),
    "skin_concern": ("skin_concern", "Skin concern", None),
    "pack_size": ("pack_size", "Pack size", None),
    # A table lamp's shade color; a lampshade's diameter is the household pan's (gen#197).
    "shade_color": ("shade_color", "Shade color", None),
    # A recliner sofa's manual or power recline (sofa_rows.py, gen#196).
    "recline": ("recline", "Recline", None),
    # How a tracksuit is sold: the set or either piece (lowerbody_rows.py, gen#206).
    "sold_as": ("sold_as", "Sold as", None),
    "units_per_pack": ("units_per_pack", "Units per pack", "C62"),
    "net_weight_g": ("net_weight", "Net weight", "GRM"),
    "net_volume_ml": ("net_volume", "Net volume", "MLT"),
    "contains": ("contains", "Contains", None),
    "may_contain": ("may_contain", "May contain", None),
    "dietary": ("dietary", "Dietary", None),
    # A fan's blade size or span, a kettle's capacity, a heater's wattage and fins, a toaster's
    # slots (appliance_rows.py, gen#202). A wattage is a plain number named in watts.
    "blade_size_in": ("blade_size", "Blade size", "INH"),
    "blade_span_cm": ("blade_span", "Blade span", "CMT"),
    "wattage": ("wattage", "Wattage (W)", None),
    "fin_count": ("fin_count", "Fin count", "C62"),
    "slots": ("slots", "Slots", "C62"),
    # A balance bike's and a trike's wheel size (toys_rows.py, gen#271): its own attribute,
    # never the garment ``size``, whose S/M/L is another kind of value.
    "wheel_size_in": ("wheel_size", "Wheel size", "INH"),
    # A tent's berth, a mat's thickness and a dumbbell's or kettlebell's weight
    # (sports_rows.py, gen#265).
    "berth": ("berth", "Berth", "C62"),
    "thickness_mm": ("thickness", "Thickness", "MMT"),
    "weight_kg": ("weight", "Weight", "KGM"),
    # A body mist's fragrance, beside its size (beauty_depth.py, gen#214).
    "fragrance": ("fragrance", "Fragrance", None),
    # A sun cream's protection factor, beside its size (type_specs/sun_cream.py, gen#214).
    "spf": ("spf", "SPF", None),
    # A garden hose's length (garden_rows.py, gen#292): the hose is cut and sold in metres.
    "length_m": ("item_length", "Item length", "MTR"),
    # The second increment (sports_rows.py, gen#368): a block's height (item_height) and a strap's,
    # bat's and kickboard's length (item_length) reuse the keys above; the rest are new.
    "glove_size_in": ("glove_size", "Glove size", "INH"),
    "head_cm": ("head_circumference", "Head circumference", "CMT"),
    "max_load_kg": ("max_load_kg", "Maximum load", "KGM"),
    "ball_size": ("ball_size", "Ball size", "C62"),
    "players": ("players", "Players", "C62"),
    "resistance": ("resistance_level", "Resistance level", None),
    "brightness_lm": ("brightness", "Brightness (lm)", None),
    "grip": ("grip_size", "Grip size", None),
    # A mower's or trimmer's cutting width and a robot mower's lawn area (garden_rows.py,
    # gen#203); the area is a plain number named in square metres, as a wattage is in watts.
    "cutting_width_cm": ("cutting_width", "Cutting width", "CMT"),
    "lawn_area_m2": ("lawn_area", "Lawn area (sq m)", None),
}
#: The SKU fields that are columns of the variant, not options.
SKU_COLUMNS = frozenset({"sku", "price", "in_stock", "ingredients"})

#: Top-level retail fact -> (key, name, unit): product-level entries, one per value.
FACTS: dict[str, tuple[str, str, str | None]] = {
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
    # Every reduced product: "On sale", plus a campaign name (promotion.py, gen#189).
    "promotion": ("promotion", "Sale", None),
    "online_only": ("online_only", "Online only", None),
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
COLUMNS = frozenset({"product_id", "product_type", "product_type_label", "title", "brand",
                     "category_path", "category_leaf", "description", "attributes", "currency",
                     "skus", "product_line", "color_options", "size_options", "unit_size",
                     "unit_measure", "ingredients"})  # fmt: skip
#: Fields left out: the standard derives them from the variants, (the drawing)
#: they are the render's input, reached through ``image_id``, or (``abv``) the
#: record's own ``attributes`` already carry them as an entry, or (``department``, gen#281) the
#: store's department is the top level of ``category_path``, which the downstream reads.
DROPPED = frozenset(
    {"price", "price_min", "price_max", "sku_count", "drawing", "abv", "department"}
)


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
    """What one SKU's image draws: its product's drawing in the SKU's color swatch, and the
    SKU's own value of each drawing param it carries (a lamp's ``finish``, a lampshade's
    ``diameter_cm``: gen#197). A SKU that carries no param key adds nothing, so its image id
    is what it was."""
    swatch = next((c for c in rec.get("color_options", ()) if c["color"] == sku.get("color")), None)
    spec = {"drawing": rec["drawing"], "swatch": swatch}
    own = {k: str(sku[k]) for k in rec["drawing"].get("params") or {} if k in sku}
    return spec | {"params": own} if own else spec


def image_id(rec: dict, sku: dict) -> str:
    """``<product type>/<product id>/<digest of the drawing spec>``: equal specs, one image."""
    blob = json.dumps(drawing_spec(rec, sku), sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode()).hexdigest()[:12]
    return f"{_slug(rec['product_type'])}/{rec['product_id']}/{digest}"


def _url(image: str) -> str:
    return f"{IMAGE_BASE_URL}/{image}.svg"


def _color_entries(authored: str) -> list[dict[str, Any]]:
    """The ``color`` entry of an authored shade, and its ``pattern`` entry when it has one.

    "Navy Stripe" is color Navy and pattern Stripe (gen#188): the color facet holds colors only,
    so a "navy" filter finds the striped shirt and a "stripe" filter finds it too."""
    color, pattern = colorwords.split(authored)
    out = [_entry("color", "Color", None, color)]
    if pattern is not None:
        out.append(_entry(*FACTS["pattern"], pattern))
    return out


def _product_attributes(rec: dict) -> list[dict[str, Any]]:
    out = list(rec["attributes"])
    have = {(e["key"], e["value"]) for e in out}
    for field in rec:
        if field not in FACTS and field not in COLUMNS and field not in DROPPED:
            raise KeyError(f"{rec['product_id']}: no standard home for {field!r}")
    facts = [e for f, spec in FACTS.items() if f in rec for e in _entries(spec, rec[f])]
    for c in rec.get("color_options", ()):
        facts += _color_entries(c["color"])
    for option, values in rec.get("size_options", {}).items():
        facts += _entries(OPTIONS[option], values)
    if "unit_size" in rec:
        facts.append(_entry(*NET_CONTENT[rec["unit_measure"]], rec["unit_size"]))
    who = audience_of(rec)
    if who is not None:
        facts.append(_entry("audience", "Audience", None, who))
    for e in facts:
        if (e["key"], e["value"]) not in have:
            have.add((e["key"], e["value"]))
            out.append(e)
    return _one_case(out)


def _one_case(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """``entries`` with each :data:`VALUE_CASE` key's value in its one casing, a repeat dropped.

    The authored rows spell ``pattern`` and ``rise`` both ways ("plain", "Plain"), which split
    one facet's bucket in two; every other facet already has one spelling
    (``tests/test_retail_audience.py`` checks them all)."""
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for e in entries:
        if e["key"] in VALUE_CASE and isinstance(e["value"], str):
            e = e | {"value": VALUE_CASE[e["key"]](e["value"])}
        if (e["key"], e["value"]) not in seen:
            seen.add((e["key"], e["value"]))
            out.append(e)
    return out


def _splits(rec: dict) -> bool:
    """Whether any SKU of the style has a pattern split out of its authored color."""
    return any(colorwords.split(s["color"])[1] for s in rec["skus"] if "color" in s)


def _own_pattern(rec: dict, sku: dict) -> list[dict[str, Any]]:
    """A SKU's pattern entry in a style where any SKU splits: its split pattern, else the
    style's drawn pattern, else Plain. Every variant states its own, so a SKU never reads a
    sibling's pattern off the style's list, and pattern joins ``variant_axes`` where it varies."""
    pattern = colorwords.split(sku["color"])[1] if "color" in sku else None
    if pattern is not None:
        return [_entry(*FACTS["pattern"], pattern)]
    drawn = rec.get("pattern", "Plain")
    return _entries(FACTS["pattern"], drawn)


def _variant(rec: dict, sku: dict) -> dict[str, Any]:
    image = image_id(rec, sku)
    options = [k for k in sku if k not in SKU_COLUMNS]
    own = _own_pattern(rec, sku) if _splits(rec) else []
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
        "attributes": [
            e
            for k in options
            for e in (_color_entries(sku[k]) if k == "color" else _entries(OPTIONS[k], sku[k]))
            if not (own and e["key"] == "pattern")
        ]
        + _one_case(own),
    }


#: The sales (``sold_last_5_days``) at which the volume signal reaches 1.0 (past the p95).
SALES_CEILING = 250


def merchandising(rec: dict) -> int:
    """The record's 0-100 ``merchandising_score`` (:mod:`..core.merchandising`).

    Its signal blends what the record states of its popularity: sales (weight 6), the rating
    (1) and the discount (2). A record that states none (round 4's) has no signal."""
    sold, rating, off = (rec.get(k) for k in ("sold_last_5_days", "rating", "discount_pct"))
    signal = blend(
        [
            (6.0, None if sold is None else log_signal(sold, SALES_CEILING)),
            (1.0, None if rating is None else min(1.0, max(0.0, (rating - 3.0) / 2.0))),
            (2.0, None if off is None else min(off / 50.0, 1.0)),
        ]
    )
    return merchandising_score(MERCHANDISING_SEED, rec["product_id"], signal)


def _variant_axes(attributes: list[dict[str, Any]], variants: list[dict[str, Any]]) -> list[str]:
    """The style's ordered ``variant_axes`` (:mod:`..core.variant_axes`): over each SKU's
    attributes as its flat document states them (the style's, less what the SKU restates)."""
    profiles = []
    for variant in variants:
        own = {e["key"] for e in variant["attributes"]}
        kept = [e for e in attributes if e["key"] not in own]
        profiles.append(profile(kept + variant["attributes"]))
    return variant_axes(profiles)


def standard_document(rec: dict) -> dict[str, Any]:
    """One build record as the standard's nested product document.

    A jean's fit and a bra's style leaf collapse into facets (:mod:`facet_leaves`); the record
    keeps its leaf, so its drawing and image id do not move."""
    variants = [_variant(rec, sku) for sku in rec["skus"]]
    path = list(rec["category_path"])
    attributes = _product_attributes(rec)
    if _splits(rec) and all(colorwords.split(s["color"])[1] for s in rec["skus"]):
        # Every SKU states its own split pattern: the style lists the union of those, and a
        # drawn pattern no SKU states (the "Plain" default, a "Striped" drawing) describes none.
        stated = {e["value"] for v in variants for e in v["attributes"] if e["key"] == "pattern"}
        attributes = [
            e for e in attributes if e["key"] != "pattern" or e["value"] in stated
        ]
    blend = facet_leaves.fibre_content(attributes, rec["product_type"])
    added, replaced = facet_leaves.leaf_facets(rec, attributes)
    if replaced:
        path = facet_leaves.collapsed_path(path, rec["product_type"])
        attributes = [e for e in attributes if e["key"] not in replaced]
        attributes += [_entry(key, name, None, value) for key, name, value in added]
    product_type = PRODUCT_TYPE_FOLDS.get(rec["product_type"], rec["product_type"])
    doc: dict[str, Any] = {
        "product_id": rec["product_id"],
        "product_type": product_type,
        # A retail type is already a display name, so its label is that name (gen#331).
        "product_type_label": product_type,
        "title": rec["title"],
        "brand": rec["brand"],
    }
    if "product_line" in rec:
        doc["series"] = rec["product_line"]
    if blend:
        doc["fibre_content"] = blend
    return doc | {
        "category_path": path,
        "category_leaf": path[-1],
        "category_depth": len(path),
        "image_id": variants[0]["image_id"],
        "image_url": variants[0]["image_url"],
        "image_detail_url": variants[0]["image_detail_url"],
        **({"ingredients": rec["ingredients"]} if "ingredients" in rec else {}),
        "merchandising_score": merchandising(rec),
        "variant_axes": _variant_axes(attributes, variants),
        "attributes": attributes,
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

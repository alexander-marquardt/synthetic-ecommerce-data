"""The retail catalog at any size: a target SKU count, reached from the templates (gen#125).

Usage::

    python3 prototypes/retail_drawings/scale.py --skus 20000 [--seed 0] [--out PATH] [--report PATH]

prints the coverage and distinctness report as JSON, checks every document
against the output standard (:func:`synthetic_ecommerce_data.core.standard.check_catalog`)
and, with ``--out``, writes the standard nested documents as JSONL.

:func:`build` keeps the hand-authored styles first, as templates: the round 4
preview's authored styles (:func:`build_preview4.samples`), then the deep-SKU jeans and bras
only the scaled catalog carries (:mod:`scale_rows`), then the toys, garden, gifts,
cleaning, food, beauty and home styles that give every department its share
(:mod:`breadth_rows`); both are data only.
It derives further styles until the SKUs reach the target.
A derived style copies one template and changes, deterministically from the seed:

- its **range name** (:data:`RANGE_NAMES`): the ``product_line``, the template's
  ``line`` attribute and the title head ("The Harrow ..." -> "The Ashcombe ...");
- its **brand**, from the brands of the same type's templates plus the department's
  :data:`EXTRA_BRANDS` (:func:`brand_pools`);
- its **attribute values**, each drawn from the values the same leaf's templates
  carry (:func:`value_pools`). A value never changes when it names the leaf, the
  path or the type ("Skinny" in "Skinny Jeans"), when its key is
  :data:`FROZEN_KEYS`, when it has a unit, or when the title or description holds
  it inside a longer word ("5" in "5pk"). A changed value is rewritten in the
  title, the description, the drawing params, the same-named top-level field and
  every SKU that carries its key (a shoe's ``upper_material``, :func:`_sku_values`).
  A changed ``motif`` is redrawn: the drawing takes the motif and inks of a
  template that draws it ("Cherry" -> ``cherries``, :func:`_redraw_motif`), the
  title's plural follows ("Lemons Print" -> "Oranges Print"), and the description
  is rebuilt from the product noun after "Graphic" or "Print" in the title, with
  no color words. Count and placement are frozen;
- its **colorways**, a hero color, then a subset of the template's other colors;
  a style whose title names its color (see below) carries that hero colorway
  alone. Its SKUs are the template's own size run times those colors, hero first
  (:func:`variants.product`): no SKU is invented. Each SKU's price is the
  template's times the style's price ratio (see below). A description's
  "Shown in cream" names the hero, the color the picture shows, and its count
  of colorways ("in 12 washes", "in three prints") is the style's own, "one wash"
  when it has one (:func:`_restate_color_count`);
- its rating, review count and sales, redrawn; a bestseller rank and the
  Bestseller badge stay with the authored styles.

Two styles are clones when they share the leaf, the brand, the attributes (the
range name aside) and the title without the range name (:func:`clone_key`).
The build makes no clone, nor any twin: a second style with the same leaf, brand
and title without the range name (:func:`twin_key`), which reads as the same
listing. A derived title never repeats one already made.
Departments get styles by :data:`DEPARTMENT_SHARE`, and leaves within a
department by a Zipf weight, so leaf sizes keep a long tail. A template whose
draws keep colliding is exhausted and leaves the pool.

**A style, not a rename.** A derived style takes a :func:`signature` (the values of
the keys its title shows, and its hero color family) that neither its template nor
any sibling has. When its title-shown values are ones the template or an earlier
sibling already shows, the hero color alone sets it apart, so its title ends with
it in the listing convention ("The Elmsett High Rise Straight Jeans, Dark Indigo").
Its price is re-drawn: the template's, times :func:`price_factor`
of the values it changed, times a seeded :data:`JITTER`, inside the leaf's
:data:`PRICE_BAND`, on a :func:`price_point`, never the template's own. A value
another attribute of the record shares never varies ("Leather" on a leather-soled
leather loafer). A draw whose title or description contradicts an attribute
(:func:`synthetic_ecommerce_data.core.standard.text_contradictions`) is refused.
:func:`grid_clones` measures what is left: styles sharing leaf, hero picture and
price with another.

**Capacity.** Signatures bound the build: per template, the shown values its leaf
offers times its color families. With today's templates every template is
exhausted at the ceiling's SKUs and styles (``ceiling`` in ``golden-retail/stats.json``,
with and without the grocery styles). Past that, the CLI reports
``reached_target: false`` and exits 2. To grow it, add data, not code: more values
per leaf that the title shows, more colorways, and more templates, deep-SKU ones
above all.

Images: a derived style keeps its template's drawing (params and a changed motif
aside), so the distinct drawings (:func:`coverage` ``images.distinct_drawings``)
stay near the template count. ``export.image_id`` still embeds the product id, so
``images.image_ids`` is one per product and colorway, and
``image_release.py --skus N`` renders this build's images (1,348 for the 20,002
SKUs of ``--skus 20000``).
"""

from __future__ import annotations

import argparse
import collections
import copy
import functools
import json
import random
import re
import resource
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import accessory_rows  # noqa: E402
import appliance_rows  # noqa: E402
import breadth_rows  # noqa: E402
import color_word_brand_rows  # noqa: E402
import colorgroup_rows  # noqa: E402
import decor_rows  # noqa: E402
import decoy_apparel  # noqa: E402
import decoy_product_words  # noqa: E402
import decoy_rows  # noqa: E402
import distractor_rows  # noqa: E402
import footwear_rows  # noqa: E402
import furniture_rows  # noqa: E402
import garden_rows  # noqa: E402
import grocery  # noqa: E402
import household_rows  # noqa: E402
import knit_sleeves  # noqa: E402
import knitwear_rows  # noqa: E402
import leaf_shapes  # noqa: E402
import lighting_rows  # noqa: E402
import lowerbody_rows  # noqa: E402
import main_colors  # noqa: E402
import mens_depth_rows  # noqa: E402
import neckline_rows  # noqa: E402
import needs_rows  # noqa: E402
import net_volume  # noqa: E402
import nike_rows  # noqa: E402
import plus_sizes  # noqa: E402
import scale_rows  # noqa: E402
import school_rows  # noqa: E402
import seasonal_rows  # noqa: E402
import shirt_rows  # noqa: E402
import sofa_rows  # noqa: E402
import sports_rows  # noqa: E402
import thin_leaf_rows  # noqa: E402
import toys_rows  # noqa: E402
import type_registry  # noqa: E402
import underwear_rows  # noqa: E402
import womens_depth_rows  # noqa: E402
from build_preview4 import samples  # noqa: E402
from export import drawing_spec, image_id, standard_document  # noqa: E402
from variants import product  # noqa: E402

from synthetic_ecommerce_data.core.standard import (  # noqa: E402
    text_contradictions,
    words,
)
from synthetic_ecommerce_data.core.standard import value_pools as text_pools  # noqa: E402

#: Invented range names; a derived style's ``product_line`` and title head.
RANGE_NAMES = (
    "Abberley", "Alnmoor", "Ardley", "Ashcombe", "Barrowden", "Belstone", "Brisley",
    "Caddon", "Calver", "Corrow", "Dalesby", "Dellow", "Dunsop", "Elmsett", "Elvet",
    "Eskerby", "Fenmoss", "Fothery", "Gorran", "Greyholt", "Haskett", "Hurlow",
    "Ilsley", "Kelderby", "Kittow", "Lathom", "Lowick", "Marden", "Morwick",
    "Nettlebed", "Norley", "Ockley", "Orrell", "Pellow", "Penwith", "Quarley",
    "Rathby", "Redesdale", "Rillaton", "Selwood", "Sorrel", "Stennis", "Tarrow",
    "Thurlby", "Torrin", "Ulverby", "Vellan", "Wenlow", "Whitsby", "Yarrowby",
    "Yelden", "Zennor", "Brantham", "Copley", "Cawdell", "Feltwick", "Holmbury",
    "Kimble", "Langrick", "Merrow",
)  # fmt: skip

#: Invented brands a department's derived styles may carry, beside its template brands.
EXTRA_BRANDS: dict[str, tuple[str, ...]] = {
    "Clothing": ("Marrowgate", "Pellbrook", "Osier & Vane", "Tallow Street"),
    "Lingerie & Nightwear": ("Dovecote Lane", "Hushwell"),
    "Home": ("Larchwood Living", "Emberly Home", "Cobble & Kiln"),
    "Beauty": ("Brightwater Botanics", "Orrin Skin"),
    "Food & Drink": ("Mossgill Dairy", "Wheatsheaf Lane", "Barrowby Kitchen"),
    "Footwear": ("Cobbleway", "Treadmoor"),
    "Garden": ("Rookery Garden Co.",),
    "Gifts": ("Ribbonvale",),
    "Toys": ("Pipwick Toys",),
    "Cleaning & Janitorial": ("Clearbrook Household", "Soapwell"),
}

#: The share of derived styles per department; the rest split by template count.
DEPARTMENT_SHARE = {
    "Clothing": 0.44, "Lingerie & Nightwear": 0.04, "Footwear": 0.10,
    "Home": 0.20, "Beauty": 0.08,
}  # fmt: skip

#: Keys whose value never changes: who it is for, its name, its size range, the
#: pattern the drawing shows, how many motifs it prints where (the drawing's
#: ``count`` and ``placement``, which the description's wording follows), a
#: light's build (gen#197): a wall light's ``ip_rating`` (a bathroom light's text says
#: where it may go) and what a lampshade's ring fits (``fitting``).
#: A tableware kind (gen#198) fixes the drawn profile and the measured size beside it, so a
#: 27 cm dinner plate never becomes a side plate.
FROZEN_KEYS = frozenset(
    {"audience", "line", "size_range", "pattern", "motif_count", "print_placement",
     "ip_rating", "fitting",
     "plate_type", "bowl_type", "cutlery_type", "knife_type", "glass_type", "utensil_type"}
)  # fmt: skip

#: Leaf weight within a department: 1 / rank ** ZIPF_S.
ZIPF_S = 1.0

#: Draws per template before it counts as exhausted.
ATTEMPTS = 40

#: Fields :func:`variants.product` derives from the SKUs; never copied.
DERIVED_FIELDS = ("product_id", "price", "sku_count", "skus", "color_options", "size_options")

#: The plural nouns a template's text counts its colorways in ("in 12 washes", "in three
#: prints"), each with its singular. A derived style keeps a subset of the colorways, so
#: :func:`_restate_color_count` rewrites the count to the style's own (gen#143).
COLOR_COUNT_NOUNS = {
    "washes": "wash", "prints": "print", "colors": "color", "colorways": "colorway",
    "shades": "shade",
}  # fmt: skip
#: The counts a template spells out ("three prints"); index i is the word for i.
NUMBER_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve",
)  # fmt: skip
_COLOR_COUNT = re.compile(
    rf"\b(\d+|{'|'.join(NUMBER_WORDS[2:])})\s+({'|'.join(COLOR_COUNT_NOUNS)})\b", re.IGNORECASE
)


@dataclass
class Scaled:
    """A build: its records in order, and each derived record's template product id."""

    records: list[dict]
    template_of: dict[str, str]

    @property
    def skus(self) -> int:
        return sum(r["sku_count"] for r in self.records)


#: A grocery style's product id prefix (:mod:`grocery`): the templates no style derives from.
GROCERY_PREFIX = "GRC-"


SHIRT_IDS = frozenset(f"PLT-{s.code}" for s in shirt_rows.STYLES)
#: The bag, umbrella and jewelry styles (:mod:`accessory_rows`, gen#207), left out of the
#: derivation as the shirts are.
ACCESSORY_IDS = frozenset(f"BRD-{r.code}" for r in accessory_rows.ROWS)
#: The camping and fitness styles (:mod:`sports_rows`, gen#265), left out of the derivation as
#: the accessories are: the Sports & Outdoors department grows by authored rows.
SPORTS_IDS = frozenset(f"BRD-{r.code}" for r in sports_rows.ROWS)
#: The lawn mower, trimmer and barbecue styles and their decoys (:mod:`garden_rows`, gen#203),
#: templates only: the Garden department grows by authored rows.
GARDEN_IDS = frozenset(f"BRD-{r.code}" for r in garden_rows.ROWS)
#: The text-match decoys of the decor types (:mod:`decor_rows`, gen#217): templates only. The
#: types themselves are specs and the registry leaves them out of the derivation.
DECOR_IDS = decor_rows.decoy_ids()
#: The school uniform styles (:mod:`school_rows`, gen#205): templates only, as the sports rows are.
SCHOOL_IDS = frozenset(f"BRD-{r.code}" for r in school_rows.ROWS)
#: The steak plate, board and weight (:mod:`distractor_rows`, gen#268). Each carries a material, so
#: a derived copy would re-draw it ("Porcelain Steak Plate", "Nylon Steak Weight") and add steak
#: rows the failure class does not count: they stay templates.
STEAK_WARE_IDS = frozenset(f"PLT-{s.code}" for s in distractor_rows.STEAK_WARE)
#: The underwear and nightwear styles (:mod:`underwear_rows`, gen#208), left out of the
#: derivation as the shirts are.
UNDERWEAR_IDS = frozenset(f"BRD-{r.code}" for r in underwear_rows.ROWS)
#: The small appliance styles (:mod:`appliance_rows`, gen#202), left out of the derivation as
#: the shirts are.
APPLIANCE_IDS = frozenset(f"BRD-{r.code}" for r in appliance_rows.ROWS)
#: The seating styles (:mod:`sofa_rows`, gen#196), left out of the derivation as the shirts are.
SOFA_IDS = frozenset(f"BRD-{r.code}" for r in sofa_rows.ROWS)
#: The furniture (gen#199): templates, never copied. Each draw would be a style the fairness
#: floor counts against Food & Drink, which sits within two styles of it at the ceiling.
FURNITURE_IDS = frozenset(f"BRD-{r.code}" for r in furniture_rows.ROWS)
#: The household styles (:mod:`household_rows`, gen#200), left out of the derivation as the
#: shirts are.
HOUSEHOLD_IDS = frozenset(f"BRD-{r.code}" for r in household_rows.ROWS)
#: The toy styles (:mod:`toys_rows`, gen#201), left out of the derivation as the shirts are.
TOY_IDS = frozenset(f"BRD-{r.code}" for r in toys_rows.ROWS)
#: The seasonal, color and character styles (:mod:`seasonal_rows`, gen#195): templates only.
SEASONAL_IDS = frozenset(f"BRD-{r.code}" for r in seasonal_rows.ROWS)
#: The near-white apparel and main-color bras (:mod:`colorgroup_rows`, gen#302): templates only.
COLORGROUP_IDS = colorgroup_rows.product_ids()
#: The color-word brand rows (:mod:`color_word_brand_rows`, gen#312): templates only.
COLORWORD_IDS = color_word_brand_rows.product_ids()
#: The lower-body styles (:mod:`lowerbody_rows`, gen#206), left out the same way.
LOWER_IDS = frozenset(f"BRD-{r.code}" for r in lowerbody_rows.ROWS)
#: The Mens clothing depth (:mod:`mens_depth_rows`, gen#310): templates only.
MENS_DEPTH_IDS = mens_depth_rows.product_ids()
#: The Womens clothing depth (:mod:`womens_depth_rows`, gen#310): templates only.
WOMENS_DEPTH_IDS = womens_depth_rows.product_ids()
#: The knitwear depth (:mod:`knitwear_rows`, gen#309): templates only.
KNITWEAR_IDS = knitwear_rows.product_ids()
#: The neckline depth (:mod:`neckline_rows`, gen#181): templates only.
NECKLINE_IDS = neckline_rows.product_ids()
#: The Nike styles and the decoys that name Nike (:mod:`nike_rows`, gen#341): templates only.
NIKE_IDS = nike_rows.product_ids()
#: The types the failure classes need (:mod:`needs_rows`, gen#329): templates only.
NEEDS_IDS = needs_rows.product_ids()
#: The ids the type specs (:mod:`type_registry`, gen#351) keep out of the derivation: a spec that
#: is not ``derivable`` and every spec decoy. No type edits this line: the registry finds them.
SPEC_IDS = type_registry.left_out_ids()


# Text-match decoys (gen#294, gen#311) are exempt from the output standard's text check: they
# exist to confuse a plain text search (the maintainer ruling on #311).
DECOY_IDS = (decoy_rows.IDS | decoy_apparel.IDS | garden_rows.decoy_ids()
             | decor_rows.decoy_ids() | neckline_rows.decoy_ids())
# The class-8 product-word decoys (gen#326) name a detail color on purpose in some rows only:
# those rows join the exemption, by id, and the rest of the class is checked like any product.
# Every registered type's text-match decoys, of every department, join by registering
# (:func:`type_registry.text_match_decoy_ids`, gen#452); an id no spec owns is declared with its
# reason in :data:`type_registry.ONE_OFF_TEXT_EXEMPT`. :func:`exempt_problems` finds a stale one.
def text_exempt() -> frozenset[str]:
    """The ids the output standard's text check leaves out, computed from the registry."""
    return (
        DECOY_IDS
        | decoy_product_words.TEXT_EXEMPT
        | type_registry.text_match_decoy_ids()
        | frozenset(type_registry.ONE_OFF_TEXT_EXEMPT)
    )


TEXT_EXEMPT = text_exempt()


def exempt_problems() -> list[str]:
    """What is wrong with the exemption: an id the catalog no longer builds, a declared one-off
    with no reason, and a one-off the registry already knows."""
    built = {d["product_id"] for d in templates(baseline=False)}
    known = type_registry.text_match_decoy_ids()
    out = [f"{i}: exempt but not in the catalog" for i in sorted(text_exempt() - built)]
    for pid, reason in sorted(type_registry.ONE_OFF_TEXT_EXEMPT.items()):
        if not reason.strip():
            out.append(f"{pid}: a declared one-off with no reason")
        if pid in known:
            out.append(f"{pid}: a declared one-off the registry already knows as a decoy")
    return out


def templates(baseline: bool = True) -> list[dict]:
    """The authored styles, then :mod:`scale_rows`, :mod:`breadth_rows` and
    :mod:`distractor_rows`, :mod:`shirt_rows`, :mod:`sofa_rows`, :mod:`household_rows`,
    :mod:`appliance_rows`, :mod:`underwear_rows`, :mod:`toys_rows`, :mod:`lowerbody_rows`
    and :mod:`lighting_rows` (gen#197), then the plain styles of :mod:`main_colors`,
    then the :mod:`grocery` styles (gen#154), in build order.

    ``baseline`` adds the plain styles a pattern-only (type, audience) needs and each group's
    missing main colors (:mod:`main_colors`, gen#275).

    Grocery is last, so a build under the other templates' SKUs is what it was. The main
    build's own 55 Food & Drink styles stay (the failure classes and the Elasticsearch proof
    corpus pin them); no title or product id repeats between the two.

    The population gates in tests/test_retail_scale.py run over :func:`derivable`; grocery has
    its own in that module (``test_the_grocery_styles_hold_their_own_near_duplicate_cap``,
    ``test_grocery_tiles_are_measured_apart_from_the_clothing_gate``,
    ``test_grocery_style_attributes_list_the_values_of_their_skus``,
    ``test_no_grocery_title_or_description_names_a_value_no_sku_carries``)."""
    authored = (r for recs in samples().values() for r in recs)
    body = [
        *authored, *scale_rows.docs(), *breadth_rows.docs(), *distractor_rows.docs(),
        *decoy_rows.docs(), *decoy_product_words.docs(),
        *shirt_rows.docs(), *accessory_rows.docs(), *sports_rows.docs(),
        *school_rows.docs(), *sofa_rows.docs(), *household_rows.docs(),
        *appliance_rows.docs(), *underwear_rows.docs(), *toys_rows.docs(),
        *lowerbody_rows.docs(), *lighting_rows.docs(), *seasonal_rows.docs(),
        *garden_rows.docs(), *decor_rows.docs(), *colorgroup_rows.docs(), *mens_depth_rows.docs(),
        *womens_depth_rows.docs(),
        *nike_rows.docs(), *knitwear_rows.docs(), *type_registry.docs(), *needs_rows.docs(),
        *color_word_brand_rows.docs(), *neckline_rows.docs(), *thin_leaf_rows.docs(),
    ]  # fmt: skip
    body = plus_sizes.extend_all(body, decoy_rows.IDS | decoy_product_words.IDS)  # gen#434
    body = leaf_shapes.apply(body)  # gen#447: a bomber is drawn as a bomber, before decoys clone it
    body = knit_sleeves.complete(body)  # gen#434: a sleeve on every knit, before decoys
    body += decoy_apparel.docs(body)  # gen#311: clones of the styles above, appended last
    body = neckline_rows.complete(body)  # gen#181: every top, dress and knit states its neckline
    body = net_volume.state_title_volumes(body)  # gen#347: a volume the title states is the field
    if baseline:
        body = main_colors.author_plain(body)
    tpls = [*body, *grocery.build()]
    type_registry.check_unique_ids(tpls)
    skip = (mens_depth_rows.decoy_ids() | COLORWORD_IDS | garden_rows.decoy_ids()
            | decor_rows.decoy_ids() | NIKE_IDS | type_registry.decoy_ids() | needs_rows.decoy_ids()
            | knitwear_rows.decoy_ids() | neckline_rows.decoy_ids())
    return main_colors.complete(tpls, skip) if baseline else tpls


def derivable(tpls: list[dict]) -> list[dict]:
    """The templates a derived style may come from: not a grocery style, whose allergen,
    dietary and ingredient facts are the grocery build's own and would not follow a re-draw, nor
    a shirt (:mod:`shirt_rows`), an accessory style (:mod:`accessory_rows`), a seating
    style (:mod:`sofa_rows`), a piece of furniture (:mod:`furniture_rows`), a household
    style (:mod:`household_rows`), an appliance (:mod:`appliance_rows`),
    an underwear style (:mod:`underwear_rows`), a toy (:mod:`toys_rows`) or a lower-body
    style (:mod:`lowerbody_rows`), left out so the seeded derivation is what it was. A boat
    or slash neck top is a failure-class row too (gen#125): a derived copy of it would hand
    the no-policy baseline the neckline, so it stays a template."""
    left_out = (KNITWEAR_IDS | NECKLINE_IDS | thin_leaf_rows.IDS | SHIRT_IDS | SOFA_IDS
                | FURNITURE_IDS | HOUSEHOLD_IDS
                | APPLIANCE_IDS | UNDERWEAR_IDS | TOY_IDS | LOWER_IDS | ACCESSORY_IDS | SPORTS_IDS
                | SCHOOL_IDS
                | SEASONAL_IDS | COLORGROUP_IDS | MENS_DEPTH_IDS | WOMENS_DEPTH_IDS
                | GARDEN_IDS | DECOR_IDS | NIKE_IDS
                | NEEDS_IDS
                | SPEC_IDS | decoy_rows.IDS | COLORWORD_IDS
                | decoy_apparel.IDS | decoy_product_words.IDS | STEAK_WARE_IDS)
    return [r for r in tpls if not r["product_id"].startswith(GROCERY_PREFIX)
            and r["product_id"] not in left_out
            and r.get("neckline") not in ("boat", "slash")]  # fmt: skip


def _words(text: str) -> str:
    return words(text)


def _has_word(text: str, value: str) -> bool:
    return f" {_words(value).strip()} " in _words(text)


def value_pools(recs: list[dict]) -> dict[tuple[str, str], tuple[str, ...]]:
    """(leaf, key) -> the unit-free values the leaf's templates carry, in first-seen order."""
    pools: dict[tuple[str, str], dict[str, None]] = collections.defaultdict(dict)
    for r in recs:
        for a in r["attributes"]:
            if "unit_code" not in a:
                pools[(r["category_leaf"], a["key"])][str(a["value"])] = None
    return {k: tuple(v) for k, v in pools.items()}


def variable_keys(rec: dict, pools: dict[tuple[str, str], tuple[str, ...]]) -> list[str]:
    """The attribute keys a style derived from ``rec`` may change (see the module doc)."""
    names = " ".join([*rec["category_path"], rec["category_leaf"], rec["product_type"]])
    counts = collections.Counter(a["key"] for a in rec["attributes"])
    shared = collections.Counter(str(a["value"]).lower() for a in rec["attributes"])
    out = []
    for a in rec["attributes"]:
        key, value = a["key"], str(a["value"])
        if key in FROZEN_KEYS or "unit_code" in a or counts[key] > 1 or shared[value.lower()] > 1:
            continue
        if len(pools.get((rec["category_leaf"], key), ())) < 2 or _has_word(names, value):
            continue
        if any(value.lower() in t.lower() and not _has_word(t, value)
               for t in (rec["title"], rec["description"])):  # fmt: skip
            continue
        out.append(key)
    return out


def _line(rec: dict) -> str | None:
    if rec.get("product_line"):
        return str(rec["product_line"])
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == "line"), None)


def clone_key(rec: dict) -> tuple:
    """Leaf, brand, attributes and title, the range name taken out of both."""
    title, name = rec["title"], _line(rec)
    if name:
        title = re.sub(rf"\b{re.escape(name)}\b ?", "", title)
    attrs = tuple(
        sorted((a["key"], str(a["value"])) for a in rec["attributes"] if a["key"] != "line")
    )
    return (rec["category_leaf"], rec["brand"], attrs, title.strip())


def twin_key(rec: dict) -> tuple:
    """Leaf, brand and title without the range name: two styles that share it read as one
    listing whatever their unseen attributes, so the build makes no second (clones included)."""
    leaf, brand, _, title = clone_key(rec)
    return (leaf, brand, title)


def _parts(value: str) -> list[str]:
    """A comma-joined attribute value's parts: "patent, suede" -> ["patent", "suede"]."""
    return [p.strip() for p in value.split(",")]


def _part_swaps(old: str, new: str) -> dict[str, str]:
    """Each part of ``old`` (lowercased) -> the part of ``new`` at its place, which a SKU
    holding that part takes; a shorter ``new`` gives its last part to the rest."""
    o, n = _parts(old), _parts(new)
    return {p.lower(): n[min(i, len(n) - 1)] for i, p in enumerate(o)}


def _sku_values(rec: dict, skus: list[dict], swaps: dict[str, dict[str, str]]) -> None:
    """Each SKU takes the values ``derive`` drew for a key it carries (``swaps``), then
    each style attribute whose key the SKUs carry lists only the parts they still hold:
    a shoe kept in its suede colors alone no longer says "patent, suede" (gen#145), and a
    title or description that names a dropped part names the first kept one instead
    ("Soft leather ballet flats" -> "Soft patent ballet flats", gen#148)."""
    for s in skus:
        for key, swap in swaps.items():
            if key in s:
                s[key] = swap.get(str(s[key]).lower(), s[key])
    for key in dict.fromkeys(a["key"] for a in rec["attributes"]):
        held = {str(s[key]).lower() for s in skus if key in s}
        if not held:
            continue
        entries = [a for a in rec["attributes"] if a["key"] == key]
        kept = [p for a in entries for p in _parts(str(a["value"])) if p.lower() in held]
        dropped = [p for a in entries for p in _parts(str(a["value"])) if p.lower() not in held]
        for a in entries:
            a["value"] = ", ".join(p for p in _parts(str(a["value"])) if p.lower() in held)
        if kept:  # an entry for a material no kept SKU holds goes (a style lists the ones it sells)
            rec["attributes"] = [a for a in rec["attributes"] if a["key"] != key or a["value"]]
        for part in dropped if kept else ():
            for text in ("title", "description"):
                rec[text] = _swap(rec[text], part, kept[0])


def _swap(text: str, old: str, new: str) -> str:
    """``old`` -> ``new`` as a whole word in any case, each occurrence keeping its case
    and an "a"/"an" before it agreeing with ``new`` (:func:`_article`):
    lower stays lower, a capital first letter stays capital, otherwise ``new`` as given.
    Its words match across a space or a hyphen, and ``&`` and "and" match each other, so
    "Hook & Loop" rewrites "hook and loop"."""
    body = re.sub(r"(?<![A-Za-z])and(?![A-Za-z])", r"\\&", re.escape(old))
    body = body.replace(r"\&", "(?:&|and)").replace(r"\-", r"[\s-]").replace(r"\ ", r"[\s-]+")
    pattern = r"(?:(?<![A-Za-z0-9])([Aa]n?) )?(?<![A-Za-z0-9])(" + body + r")(?![A-Za-z0-9])"

    def cased(m: re.Match[str]) -> str:
        article, hit = m.group(1), m.group(2)
        if hit.islower():
            word = new.lower()
        elif hit[0].isupper() and (len(hit) == 1 or hit[1:].islower()):
            word = new[0].upper() + new[1:]
        else:
            word = new
        if article is None:
            return word
        # An article just before the word agrees with the word that replaces it.
        fixed = _article(word)
        return f"{fixed.capitalize() if article[0].isupper() else fixed} {word}"

    return re.sub(pattern, cased, text, flags=re.IGNORECASE)


def _title(tpl: dict, name: str) -> str:
    old = _line(tpl)
    if old and re.search(rf"\b{re.escape(old)}\b", tpl["title"]):
        return re.sub(rf"\b{re.escape(old)}\b", name, tpl["title"], count=1)
    if tpl["title"].startswith("The "):
        return f"The {name} {tpl['title'][4:]}"
    return f"{name} {tpl['title']}"


#: The drawing fields that follow a changed ``motif``; ``count`` and ``placement`` never
#: change (:data:`FROZEN_KEYS`).
MOTIF_FIELDS = ("motif", "accent", "third")


@functools.cache
def _motif_inks() -> dict[str, dict[str, Any]]:
    """A ``motif`` attribute value -> the drawing's ``motif``, ``accent`` and ``third`` of the
    first template that draws it ("Cherry" -> ``cherries`` in cherry red)."""
    out: dict[str, dict[str, Any]] = {}
    for t in templates():
        for a in t["attributes"]:
            if a["key"] == "motif" and "motif" in t["drawing"]:
                out.setdefault(str(a["value"]), {k: t["drawing"][k] for k in MOTIF_FIELDS})
    return out


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def _plural(word: str) -> str:
    if re.search(r"[^aeiou]y$", word):
        return word[:-1] + "ies"
    return word + ("es" if re.search(r"(s|x|z|ch|sh)$", word) else "s")


def _redraw_motif(rec: dict, old: str, new: str) -> None:
    """The motif ``old`` -> ``new`` in the picture, the title's plural ("Lemons Print") and
    the description, which is rebuilt: the template's names the old motif and its colors.

    The new text names the product noun after "Graphic" or "Print" in the title, and the
    count and placement the drawing keeps."""
    d = rec["drawing"]
    d.update(_motif_inks()[new])
    rec["title"] = _swap(rec["title"], _plural(old), _plural(new))
    m = re.search(r"\b(?:Graphic|Print)\s+([^,]+)", rec["title"])
    noun = (m.group(1) if m else rec["title"].split()[-1]).strip().lower()
    on = noun if re.search(r"[^s]s$", noun) else f"{_article(noun)} {noun}"
    low = new.lower()
    if d.get("count") == 1:
        rec["description"] = f"A big {low} graphic on {on}."
    else:
        spread = "scattered on" if d.get("placement") == "scatter" else "all over"
        lead = f"{_article(low).capitalize()} {low} print"
        rec["description"] = f"{lead}: {_plural(low)} {spread} {on}."


def _restate_color_count(text: str, n: int) -> str:
    """``text`` with each colorway count ("in 12 washes", "in three prints") made ``n``:
    "one wash" for a single colorway, else ``n`` in the template's own form (digits
    or a word). A title-cased noun ("3 Washes") stays title-cased ("One Wash")."""

    def restate(m: re.Match[str]) -> str:
        plural = m.group(2)
        if n == 1:
            phrase = f"one {COLOR_COUNT_NOUNS[plural.lower()]}"
            return phrase.title() if plural[0].isupper() else phrase
        if m.group(1).isdigit() or n >= len(NUMBER_WORDS):
            return f"{n} {plural}"
        word = NUMBER_WORDS[n]
        return f"{word.capitalize() if m.group(1)[0].isupper() else word} {plural}"

    return _COLOR_COUNT.sub(restate, text)


def derive(tpl: dict, pid: str, name: str, brand: str, values: dict[str, str],
           colors: list[str], owners: dict[str, str], rng: random.Random,
           ratio: float = 1.0) -> dict:  # fmt: skip
    """One style from ``tpl``: the given range name, brand, attribute values and colors
    (the first is the hero), each SKU's price times ``ratio`` on a price point."""
    rec = {k: copy.deepcopy(v) for k, v in tpl.items() if k not in DERIVED_FIELDS}
    rec.pop("price_min", None)
    rec.pop("price_max", None)
    rec.pop("bestseller_rank", None)
    # A derived style's price is redrawn, so the template's was_price is not its own; a petite
    # copy that kept it would let a no-policy baseline satisfy "petite sale", the pair only a
    # policy may honour (gen#125, gen#275).
    rec.pop("was_price", None)
    rec.pop("promotion", None)  # it follows the was_price (promotion.py, gen#189)
    if "badges" in rec:
        rec["badges"] = [b for b in rec["badges"] if b != "Bestseller"]
    old_line = _line(tpl)
    rec["title"] = _title(tpl, name)
    if old_line:
        rec["description"] = _swap(rec["description"], old_line, name)
    rec["product_line"] = name
    sku_swaps: dict[str, dict[str, str]] = {}  # a changed key the SKUs carry: see _sku_values
    for a in rec["attributes"]:
        if a["key"] == "line":
            a["value"] = name
        if a["key"] in values and values[a["key"]] != str(a["value"]):
            old, new = str(a["value"]), values[a["key"]]
            a["value"] = new
            sku_swaps[a["key"]] = _part_swaps(old, new)
            rec["title"] = _swap(rec["title"], old, new)
            rec["description"] = _swap(rec["description"], old, new)
            if rec.get(a["key"]) == old:
                rec[a["key"]] = new
            params = rec["drawing"].get("params") or {}
            for p, v in params.items():
                if isinstance(v, str) and v.lower() == old.lower():
                    params[p] = new.lower() if v == old.lower() else new
            if isinstance(rec["drawing"].get("label"), str):  # a duvet's "13.5 Tog"
                rec["drawing"]["label"] = _swap(rec["drawing"]["label"], old, new)
            if a["key"] == "motif" and "motif" in rec["drawing"]:
                _redraw_motif(rec, old, new)
    lighting_rows.fit_ceiling_form(rec)  # a flush light has no drop (gen#237)
    footwear_rows.fit_axes(rec)  # a clog's "Back strap" is drawn as `back` (gen#512)
    if colors:  # "Shown in cream" names the color the picture shows: the hero
        names = "|".join(re.escape(c["color"]) for c in tpl.get("color_options", ()))
        rec["description"] = re.sub(
            rf"\b(shown in )(?:{names})\b",
            lambda m: m.group(1) + colors[0].lower(),
            rec["description"],
            flags=re.IGNORECASE,
        )
    if brand != tpl["brand"]:
        rec["title"] = rec["title"].replace(tpl["brand"], brand)
        rec["description"] = rec["description"].replace(tpl["brand"], brand)
        rec["brand"] = brand
        if "brand_owner" in rec:
            rec["brand_owner"] = owners.get(brand, "third_party")
    if "rating" in rec:
        rec["rating"] = round(rng.uniform(3.4, 4.9), 1)
    if "review_count" in rec:
        rec["review_count"] = int(rng.lognormvariate(3.2, 1.1))
    if "sold_last_5_days" in rec:
        rec["sold_last_5_days"] = int(rng.lognormvariate(3.5, 1.2))
    swatches = {c["color"]: c for c in tpl.get("color_options", ())}
    rank = {c: i for i, c in enumerate(colors)}
    skus = [{k: v for k, v in s.items() if k != "sku"} for s in tpl["skus"]
            if "color" not in s or s["color"] in rank]  # fmt: skip
    skus.sort(key=lambda s: rank.get(s.get("color"), 0))
    _sku_values(rec, skus, sku_swaps)
    if colors:
        kept = len({s["color"] for s in skus if "color" in s})
        rec["title"] = _restate_color_count(rec["title"], kept)
        rec["description"] = _restate_color_count(rec["description"], kept)
    for s in skus:
        s["price"] = price_point(s["price"] * ratio)
    out = product(pid, skus, swatches, **rec)
    if "price_min" in tpl:
        out["price_min"] = min(s["price"] for s in out["skus"])
        out["price_max"] = max(s["price"] for s in out["skus"])
    return out


def _department(rec: dict) -> str:
    return str(rec["department"][0])


def _plan(tpls: list[dict], rng: random.Random) -> dict[str, dict[str, list[dict]]]:
    """department -> leaf -> its templates, leaves in a seeded Zipf rank order."""
    plan: dict[str, dict[str, list[dict]]] = collections.defaultdict(dict)
    for r in tpls:
        plan[_department(r)].setdefault(r["category_leaf"], []).append(r)
    for dept, leaves in plan.items():
        order = sorted(leaves)
        rng.shuffle(order)
        plan[dept] = {leaf: leaves[leaf] for leaf in order}
    return plan


def brand_pools(tpls: list[dict]) -> dict[tuple[str, str], list[str]]:
    """(department, product type) -> the brands its templates carry, then the department's
    :data:`EXTRA_BRANDS`: a denim label never sells a car coat."""
    out: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for r in tpls:
        pool = out[(_department(r), r["product_type"])]
        if r["brand"] not in pool:
            pool.append(r["brand"])
    for (dept, _), pool in out.items():
        pool += [b for b in EXTRA_BRANDS.get(dept, ()) if b not in pool]
    return dict(out)


def _department_weights(plan: dict[str, dict[str, list[dict]]]) -> dict[str, float]:
    rest = [d for d in plan if d not in DEPARTMENT_SHARE]
    left = 1.0 - sum(DEPARTMENT_SHARE[d] for d in plan if d in DEPARTMENT_SHARE)
    sizes = {d: sum(len(t) for t in plan[d].values()) for d in rest}
    total = sum(sizes.values()) or 1
    return {d: DEPARTMENT_SHARE.get(d, left * sizes.get(d, 0) / total) for d in plan}


def build(skus: int, seed: int = 0) -> Scaled:
    """Styles until their SKUs reach ``skus``: the templates first, then derived ones."""
    tpls = templates()
    records: list[dict] = []
    for r in tpls:
        if sum(x["sku_count"] for x in records) >= skus:
            return Scaled(records, {})
        records.append(r)
    rng = random.Random(seed)
    base = derivable(tpls)
    pools = value_pools(base)
    # Every template, grocery too: a derived style that draws a grocery brand (EXTRA_BRANDS)
    # keeps that brand's owner, not the third-party default (gen#236).
    owners = {r["brand"]: r["brand_owner"] for r in tpls if "brand_owner" in r}
    brands = brand_pools(base)
    plan = _plan(base, rng)
    weights = _department_weights(plan)
    used = {twin_key(r) for r in tpls}
    titles = {r["title"] for r in tpls}
    ctx = _Context(pools, text_pools(standard_document(r) for r in base), _bands(base), {})
    for r in tpls:
        ctx.authored.setdefault(r["category_leaf"], []).append(r)
    template_of: dict[str, str] = {}
    total = sum(r["sku_count"] for r in records)
    serial = 0
    while total < skus and plan:
        depts = list(plan)
        dept = rng.choices(depts, [weights[d] for d in depts])[0]
        leaves = list(plan[dept])
        leaf = rng.choices(leaves, [1 / (i + 1) ** ZIPF_S for i in range(len(leaves))])[0]
        tpl = rng.choice(plan[dept][leaf])
        pool = brands[(dept, tpl["product_type"])]
        made = _draw(tpl, serial, ctx, pool, owners, used, titles, rng)
        if made is None:
            plan[dept][leaf].remove(tpl)
            if not plan[dept][leaf]:
                del plan[dept][leaf]
            if not plan[dept]:
                del plan[dept]
            continue
        serial += 1
        records.append(made)
        template_of[made["product_id"]] = tpl["product_id"]
        total += made["sku_count"]
    return Scaled(records, template_of)


@dataclass
class _Context:
    pools: dict[tuple[str, str], tuple[str, ...]]
    text_pools: dict[tuple[str, str], set[str]]
    bands: dict[str, tuple[float, float]]
    #: template product id -> the signatures (:func:`signature`) no style has taken yet
    open: dict[str, list[tuple]]
    #: template product id -> the title-shown values its own title and its styles' show
    shown: dict[str, set[tuple]] = field(default_factory=dict)
    #: leaf -> the listing words (:func:`listing_tokens`) of every style drawn or authored there
    listed: dict[str, list[frozenset[str]]] = field(default_factory=dict)
    #: leaf -> the authored styles there, which a drawn style must also differ from
    authored: dict[str, list[dict]] = field(default_factory=dict)


def _bands(tpls: list[dict]) -> dict[str, tuple[float, float]]:
    prices: dict[str, list[float]] = collections.defaultdict(list)
    for r in tpls:
        prices[r["category_leaf"]].append(r["price"])
    lo, hi = PRICE_BAND
    return {leaf: (lo * min(p), hi * max(p)) for leaf, p in prices.items()}


def _family(swatch: dict | None) -> str | None:
    return None if swatch is None else str(swatch.get("family", swatch["color"]))


def shown_keys(tpl: dict, keys: list[str]) -> list[str]:
    """The variable keys whose value the template's title shows."""
    values = {a["key"]: str(a["value"]) for a in tpl["attributes"]}
    return [k for k in keys if _has_word(tpl["title"], values[k])]


def signature(rec: dict, shown: list[str]) -> tuple:
    """What tells a style from its template and siblings at a glance: the values of the
    title-shown keys and the hero color family."""
    values = {a["key"]: str(a["value"]) for a in rec["attributes"]}
    return (tuple(values[k] for k in shown), _family((rec.get("color_options") or [None])[0]))


def _signatures(tpl: dict, shown: list[str], pools: dict) -> list[tuple]:
    """Every signature a style derived from ``tpl`` may take, the template's own aside."""
    leaf = tpl["category_leaf"]
    combos: list[tuple] = [()]
    for k in shown:
        combos = [(*c, v) for c in combos for v in pools[(leaf, k)]]
    families = list(dict.fromkeys(_family(c) for c in tpl.get("color_options", ()))) or [None]
    mine = signature(tpl, shown)
    return [(c, f) for c in combos for f in families if (c, f) != mine]


def _colors(tpl: dict, family: str | None, rng: random.Random) -> list[str]:
    """A hero color of ``family``, then a seeded subset of the rest in template order."""
    swatches = tpl.get("color_options", ())
    if not swatches:
        return []
    hero = rng.choice([c["color"] for c in swatches if _family(c) == family])
    rest = [c["color"] for c in swatches if c["color"] != hero]
    keep = set(rng.sample(rest, rng.randint(0, len(rest))))
    return [hero, *(c for c in rest if c in keep)]


def _draw(tpl: dict, serial: int, ctx: _Context, brands: list[str], owners: dict[str, str],
          used: set, titles: set, rng: random.Random) -> dict | None:  # fmt: skip
    """A new style from ``tpl`` with a signature no style of it has, or None when none is
    left or ATTEMPTS draws all repeat a title or contradict their text.

    A style whose title-shown values the template or an earlier sibling already shows
    differs in its hero color alone, so its title names it: "…, Sage"."""
    leaf = tpl["category_leaf"]
    keys = variable_keys(tpl, ctx.pools)
    shown = shown_keys(tpl, keys)
    left = ctx.open.setdefault(tpl["product_id"], _signatures(tpl, shown, ctx.pools))
    pid = f"{tpl['product_id'].split('-')[0]}-{serial + 1:06d}"
    old = {a["key"]: str(a["value"]) for a in tpl["attributes"]}
    taken = ctx.shown.setdefault(tpl["product_id"], {tuple(old[k] for k in shown)})
    lo, hi = ctx.bands[leaf]
    for _ in range(ATTEMPTS):
        if not left:
            return None
        sig = rng.choice(left)
        values = dict(zip(shown, sig[0], strict=True))
        values |= {k: rng.choice(ctx.pools[(leaf, k)]) for k in keys if k not in shown}
        colors = _colors(tpl, sig[1], rng)
        if sig[0] in taken:  # the title names the color: the style IS that color
            colors = colors[:1]
        brand, name = rng.choice(brands), rng.choice(RANGE_NAMES)
        changes = {k: (old[k], v) for k, v in values.items() if v != old[k]}
        price = tpl["price"] * price_factor(changes) * rng.uniform(*JITTER)
        target = price_point(min(max(price, lo), hi), lo, hi)
        if target == tpl["price"]:  # a re-drawn price is never the template's own
            up = target + _step(target)
            target = up if up <= hi else price_point(target - _step(target), lo, hi)
        ratio = target / tpl["price"]
        rec = derive(tpl, pid, name, brand, values, colors, owners, rng, ratio)
        if sig[0] in taken and colors:
            rec["title"] = f"{rec['title']}, {colors[0]}"
        if twin_key(rec) in used or rec["title"] in titles:
            continue
        if text_contradictions(standard_document(rec), ctx.text_pools):
            continue
        words = listing_tokens(rec)
        seen = ctx.listed.get(leaf)
        if seen is None:
            seen = ctx.listed[leaf] = [listing_tokens(t) for t in ctx.authored.get(leaf, ())]
        if any(len(words & o) / len(words | o) >= NEAR_DUPLICATE_JACCARD for o in seen):
            continue  # a listing a shopper reads as another style's
        seen.append(words)
        left.remove(sig)
        taken.add(sig[0])
        used.add(twin_key(rec))
        titles.add(rec["title"])
        return rec
    return None


def coverage(recs: list[dict]) -> dict[str, Any]:
    """Styles, SKUs, products per leaf, attribute fill per type and the image counts."""
    per_leaf = collections.Counter(r["category_leaf"] for r in recs)
    sizes = sorted(per_leaf.values(), reverse=True)
    top = max(1, len(sizes) // 10)
    by_type: dict[str, list[dict]] = collections.defaultdict(list)
    for r in recs:
        by_type[r["product_type"]].append(r)
    fill = {}
    for ptype, rows in sorted(by_type.items()):
        keys = {a["key"] for r in rows for a in r["attributes"]}
        have = [{a["key"] for a in r["attributes"]} for r in rows]
        share = [sum(k in h for h in have) / len(rows) for k in keys]
        fill[ptype] = {"products": len(rows), "keys": len(keys),
                       "fill": round(sum(share) / len(share), 3) if share else 1.0}  # fmt: skip
    depts: dict[str, list[int]] = collections.defaultdict(list)
    for r in recs:
        depts[_department(r)].append(r["sku_count"])
    specs = {json.dumps(drawing_spec(r, s), sort_keys=True) for r in recs for s in r["skus"]}
    return {
        "styles": len(recs),
        "skus": sum(r["sku_count"] for r in recs),
        "skus_per_style_by_department": {
            d: {"styles": len(v), "skus": sum(v), "per_style": round(sum(v) / len(v), 1)}
            for d, v in sorted(depts.items())
        },
        "leaves": len(per_leaf),
        "products_per_leaf": dict(per_leaf.most_common()),
        "leaf_size": {
            "max": sizes[0],
            "median": sizes[len(sizes) // 2],
            "min": sizes[-1],
            "top_decile_share": round(sum(sizes[:top]) / len(recs), 3),
        },  # fmt: skip
        "attribute_fill": fill,
        "images": {
            "image_ids": len({image_id(r, s) for r in recs for s in r["skus"]}),
            "distinct_drawings": len(specs),
        },
    }


#: A derived style's price stays in [low * the leaf's cheapest template, high * its dearest].
PRICE_BAND = (0.75, 1.35)


#: A derived style's seeded spread around its template's price, before the band.
JITTER = (0.85, 1.2)

#: The price weight of a word in a value: a premium material costs more, a cheap one less.
#: A value's weight is the product of its words' (1.0 when none is listed).
PREMIUM = {
    "cashmere": 1.6, "silk": 1.4, "goose": 1.3, "merino": 1.3, "leather": 1.3,
    "down": 1.25, "suede": 1.25, "wool": 1.2, "egyptian": 1.2, "velvet": 1.15,
    "linen": 1.15, "organic": 1.1, "canvas": 0.9, "faux": 0.85, "rubber": 0.85,
    "nylon": 0.85, "microfibre": 0.85, "synthetic": 0.8, "polyester": 0.8,
    "acrylic": 0.8, "hollowfibre": 0.8, "plastic": 0.8,
    "bone": 2.0, "porcelain": 1.4, "enamel": 0.75, "melamine": 0.5,
}  # fmt: skip


def _weight(value: str) -> float:
    out = 1.0
    for w in words(value).split():
        out *= PREMIUM.get(w, 1.0)
    return out


def price_factor(changes: dict[str, tuple[str, str]]) -> float:
    """The price multiplier of attribute changes ``key -> (old, new)``: each new value's
    :data:`PREMIUM` weight over the old one's."""
    out = 1.0
    for old, new in changes.values():
        out *= _weight(new) / _weight(old)
    return out


def _step(price: float) -> float:
    return 0.05 if price < 5 else 0.5 if price < 20 else 1.0 if price < 100 else 5.0


def price_point(price: float, lo: float | None = None, hi: float | None = None) -> float:
    """``price`` on the nearest retail price point (5p under £5, 50p under £20, £1 under
    £100, then £5), moved one point inward when that leaves ``[lo, hi]``."""
    step = _step(price)
    n = round(price / step)
    if lo is not None and n * step < lo - 1e-9:
        n += 1
    if hi is not None and n * step > hi + 1e-9:
        n -= 1
    return round(max(n, 1) * step, 2)


def grid_tile(rec: dict) -> tuple:
    """What a results grid shows of a style: its leaf, its hero picture and its price."""
    hero = rec["skus"][0]
    spec = json.dumps(drawing_spec(rec, hero), sort_keys=True)
    return (rec["category_leaf"], spec, hero["price"])


def grid_clones(recs: list[dict]) -> dict[str, Any]:
    """The styles that share their grid tile (:func:`grid_tile`) with another style."""
    tiles = collections.Counter(grid_tile(r) for r in recs)
    shared = sum(n for n in tiles.values() if n > 1)
    return {
        "styles": len(recs),
        "grid_clones": shared,
        "grid_clone_rate": round(shared / len(recs), 4),
        "largest_group": max(tiles.values()),
    }


def prices_per_leaf(recs: list[dict]) -> dict[str, Any]:
    """Distinct style prices per leaf: each leaf's count, then the min and the median."""
    prices: dict[str, set[float]] = collections.defaultdict(set)
    for r in recs:
        prices[r["category_leaf"]].add(r["price"])
    counts = sorted(len(v) for v in prices.values())
    return {
        "distinct": {leaf: len(v) for leaf, v in sorted(prices.items())},
        "min": counts[0],
        "median": counts[len(counts) // 2],
    }


#: The word overlap (Jaccard, over brand and title) at which two same-leaf listings read as one.
NEAR_DUPLICATE_JACCARD = 0.8


def listing_tokens(rec: dict) -> frozenset[str]:
    """The words a shopper and the index read on a listing: the brand and the title."""
    return frozenset(_words(f"{rec['brand']} {rec['title']}").split())


def distinctness(
    recs: list[dict], sample: int = 500, seed: int = 0, jaccard: float = NEAR_DUPLICATE_JACCARD
) -> dict[str, Any]:
    """Duplicate titles and clones over all styles (excess copies: a pair is 1), and on a
    seeded sample the share of styles with a same-leaf listing at ``jaccard`` or above."""
    titles = collections.Counter(r["title"] for r in recs)
    clones = collections.Counter(clone_key(r) for r in recs)
    by_leaf: dict[str, list[tuple[int, frozenset[str]]]] = collections.defaultdict(list)
    for i, r in enumerate(recs):
        by_leaf[r["category_leaf"]].append((i, listing_tokens(r)))
    picked = random.Random(seed).sample(range(len(recs)), min(sample, len(recs)))
    near = 0
    for i in picked:
        mine = listing_tokens(recs[i])
        for j, other in by_leaf[recs[i]["category_leaf"]]:
            if j != i and len(mine & other) / len(mine | other) >= jaccard:
                near += 1
                break
    n = len(recs)
    dup = sum(c - 1 for c in titles.values())
    clone = sum(c - 1 for c in clones.values())
    return {
        "duplicate_titles": dup,
        "duplicate_title_rate": round(dup / n, 4),
        "clones": clone,
        "clone_rate": round(clone / n, 4),
        "near_duplicate_rate": round(near / len(picked), 4),
        "near_duplicate_sample": len(picked),
        "near_duplicate_jaccard": jaccard,
    }


def documents(scaled: Scaled) -> list[dict[str, Any]]:
    """The build as the output standard's nested documents."""
    return [standard_document(r) for r in scaled.records]


def flat(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One flat document per SKU, the file a loader takes as ``catalog.ndjson``
    (:func:`grocery.flat`: a grocery SKU states its own allergens, and carries its own
    ``ingredients`` top-level)."""
    return grocery.flat(docs)


#: ``--skus ceiling``: every SKU the build can make, whatever that count is (gen#536). A release
#: asks for this rather than a number, so it never asks for more than the frozen build holds.
CEILING = "ceiling"


def _target(text: str) -> int:
    if text == CEILING:
        return sys.maxsize
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("--skus must be at least 1")
    return value


def main(argv: list[str] | None = None) -> int:
    from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: PLC0415

    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument(
        "--skus",
        type=_target,
        required=True,
        help="target SKU count; the build stops at the first style past it. "
        f"'{CEILING}' builds every SKU the templates can make and is never short",
    )
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--out", type=Path, help="write the standard nested documents here, one JSON per line"
    )
    ap.add_argument("--flat", type=Path, help="write one flat document per SKU here (:func:`flat`)")
    ap.add_argument("--report", type=Path, help="write the report JSON here as well as to stdout")
    args = ap.parse_args(argv)
    start = time.perf_counter()
    scaled = build(args.skus, args.seed)
    docs = documents(scaled)
    built = time.perf_counter() - start
    problems = check_catalog(docs, one_class_per_key=True, text_exempt=TEXT_EXEMPT)
    if args.out:
        with args.out.open("w", encoding="utf-8") as handle:
            for d in docs:
                handle.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n")
    if args.flat:
        with args.flat.open("w", encoding="utf-8") as handle:
            for row in flat(docs):
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    ceiling = args.skus == sys.maxsize  # --skus ceiling: the target is what the build made
    report = {
        "target_skus": scaled.skus if ceiling else args.skus,
        "reached_target": ceiling or scaled.skus >= args.skus,
        "seed": args.seed,
        "coverage": coverage(scaled.records),
        "distinctness": distinctness(scaled.records, seed=args.seed),
        "templates_distinctness": distinctness(templates(), seed=args.seed),
        "grid_clones": grid_clones(scaled.records),
        "prices_per_leaf": {
            k: v for k, v in prices_per_leaf(scaled.records).items() if k != "distinct"
        },  # fmt: skip
        "standard_problems": len(problems),
        "build_seconds": round(built, 2),
    }
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report["peak_rss_mb"] = round(rss / (1 << 20 if sys.platform == "darwin" else 1 << 10))
    text = json.dumps(report, indent=1)
    if args.report:
        args.report.write_text(text + "\n", encoding="utf-8")
    print(text)
    for p in problems[:20]:
        print(p, file=sys.stderr)
    if problems:
        return 1
    if not report["reached_target"]:
        print(
            f"short: {scaled.skus} SKUs of {args.skus}; every template is exhausted",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

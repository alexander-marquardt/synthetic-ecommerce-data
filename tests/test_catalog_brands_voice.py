"""The brand book, each brand's voice, and the rule that every SKU is different.

Maintainer rulings for the 100K catalog (elastic/prism-industrial-products,
2026-09-28):

* **Each SKU has something different from every other SKU.** No two SKUs may
  be identical on (product_type, brand, every attribute), ignoring the
  identifier fields (sku, product_id, List Number, image ids and urls) and
  the commercial fields (price, stock). Brand counts as a difference.
* **A brand's catalog section reads uniformly**: every product of one brand
  follows that brand's title and description template; a different brand
  reads slightly differently. Titles keep the census structure as the core.
* **No text states a fact the record cannot back.** Every number in a title
  or description traces to a value the record publishes.
* **Brands look different in the drawings**, and the same within a brand.

The checks here read the EMITTED documents with their own string logic --
they do not call the generator's spec key or voice functions to decide what
a document should say, so a defect in that machinery cannot hide itself.
"""

from __future__ import annotations

import collections
import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from compat_text import without_compatibility
from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.brands import (
    BRAND_BOOK,
    BRANDS,
    FRAMES,
    INKS,
    PRODUCT_WORDS,
)
from synthetic_industrial_products.catalog.config import HUNDRED_K_LINES, GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.muststock import MUST_STOCK
from synthetic_industrial_products.dimensions import parse_length

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"

#: The fields that identify or price a SKU rather than describe it.
IDENTIFIER_ATTRIBUTES = {"List Number"}


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines()]


@pytest.fixture(scope="module")
def golden() -> list[dict]:
    return _read(GOLDEN / "flat.jsonl")


@pytest.fixture(scope="module")
def hundred_k() -> list[dict]:
    """The full 100K build, emitted in memory (about 30 s)."""
    catalog = generate(GeneratorConfig(lines=HUNDRED_K_LINES))
    return list(emit.iter_flat(catalog))


# --- every SKU is different ---------------------------------------------------


def _spec(doc: dict) -> frozenset:
    """A SKU's published spec; a repeated name (Standards) is one joined value."""
    values: dict[str, list[str]] = collections.defaultdict(list)
    for a in doc["attributes"]:
        if a["name"] not in IDENTIFIER_ATTRIBUTES:
            values[a["name"]].append(a["value"])
    return frozenset((name, "|".join(v)) for name, v in values.items())


#: What a SKU of each type IS, for bucketing the subset search: two SKUs can
#: only differ by a dropped attribute if they agree on these (every one is
#: published on every SKU of its type).
_BUCKET = (
    "Item",
    "Size",
    "Thread Size",
    "Dia./Thread Size",
    "Bearing Number",
    "Milling Dia.",
    "Diameter",
    "Head Weight",
    "Grit",
)


def same_product_duplicates(docs: list[dict]) -> list[tuple[str, str]]:
    """SKU pairs of one (type, brand) that are NOT different.

    Identical on every non-identifier attribute, OR differing only in that one
    lacks an attribute the other carries (a sparsity drop is not a difference
    a shopper can see as one). Checked pairwise within buckets, independently
    of the generator's own index.
    """
    buckets: dict[tuple, list[tuple[frozenset, str]]] = collections.defaultdict(list)
    for doc in docs:
        spec = _spec(doc)
        core = frozenset(pair for pair in spec if pair[0] in _BUCKET)
        buckets[(doc["product_type"], doc["brand"], core)].append((spec, doc["sku"]))
    duplicates = []
    for members in buckets.values():
        for i, (a, sku_a) in enumerate(members):
            for b, sku_b in members[i + 1 :]:
                if a <= b or b <= a:
                    duplicates.append((sku_a, sku_b))
    return duplicates


def test_no_two_committed_skus_are_the_same_product(golden):
    assert same_product_duplicates(golden) == []


def test_no_two_skus_of_the_100k_catalog_are_the_same_product(hundred_k):
    assert same_product_duplicates(hundred_k) == []


def test_a_planted_duplicate_is_caught(golden):
    """The control: the check above fires on a real duplicate."""
    twin = dict(golden[0], sku="ZZ0000", product_id="ZZZ-0000", price_usd=1.0, stock=0)
    assert same_product_duplicates([*golden, twin]) == [(golden[0]["sku"], "ZZ0000")]


def test_a_planted_sparsity_drop_is_caught(golden):
    """A copy that only LACKS one attribute is not a different product."""
    doc = next(d for d in golden if len(d["attributes"]) > 3)
    dropped = dict(doc, sku="ZZ0002", attributes=doc["attributes"][:-1])
    assert same_product_duplicates([doc, dropped]) == [(doc["sku"], "ZZ0002")]


def test_the_same_part_from_two_brands_is_two_products(golden):
    """Brand IS a difference: re-branding a copy is not a duplicate."""
    other = next(b for b in BRANDS if b != golden[0]["brand"])
    rebranded = dict(golden[0], sku="ZZ0001", brand=other)
    assert same_product_duplicates([golden[0], rebranded]) == []


#: The per-type floor on DISTINCT specs over SKUs, across brands, at 100K.
#: Identical specs across brands are realistic (one standard part, many
#: makers), so this is a floor rather than 1.0. Measured on the 100K build and
#: rounded down to 0.05: flat washers 0.70 -- ISO 7089 fixes nine sizes, so
#: many makers sell the same washer -- ball pein hammers 0.94, every other
#: type 0.98 or more.
DISTINCT_SPEC_FLOOR = {"washer_flat": 0.65, "hammer_ball_pein": 0.90}
DEFAULT_DISTINCT_SPEC_FLOOR = 0.95


def test_each_type_keeps_its_distinct_spec_floor_at_100k(hundred_k):
    specs: dict[str, set] = collections.defaultdict(set)
    skus: collections.Counter = collections.Counter()
    for doc in hundred_k:
        specs[doc["product_type"]].add(
            tuple(
                sorted(
                    (a["name"], a["value"])
                    for a in doc["attributes"]
                    if a["name"] not in IDENTIFIER_ATTRIBUTES
                )
            )
        )
        skus[doc["product_type"]] += 1
    for type_key, count in skus.items():
        floor = DISTINCT_SPEC_FLOOR.get(type_key, DEFAULT_DISTINCT_SPEC_FLOOR)
        assert len(specs[type_key]) / count >= floor, (type_key, len(specs[type_key]), count)


def test_every_must_stock_example_is_stocked_at_100k(hundred_k):
    for entry in MUST_STOCK:
        assert any(
            entry.matches(doc["product_type"], {a["name"]: a["value"] for a in doc["attributes"]})
            for doc in hundred_k
        ), entry.example


@pytest.mark.parametrize("which", ["golden", "hundred_k"])
def test_no_two_products_share_a_product_name_catalog_wide(which, request):
    products = {d["product_id"]: d["parent_title"] for d in request.getfixturevalue(which)}
    names = collections.Counter(products.values())
    assert [n for n, c in names.items() if c > 1] == []


@pytest.mark.parametrize("which", ["golden", "hundred_k"])
def test_every_bearing_is_a_real_table_entry_with_its_own_dimensions(which, request):
    """A bearing number names a bore, OD and width. The first version of the
    uniqueness walk renumbered 11,784 bearings to numbers that are not
    bearings, keeping another number's sizes."""
    from synthetic_industrial_products.catalog.newtypes import _BEARINGS_INCH, _BEARINGS_METRIC

    table = {n: (b / 25.4, o / 25.4, w / 25.4) for n, b, o, w in _BEARINGS_METRIC}
    table |= {n: (b, o, w) for n, b, o, w in _BEARINGS_INCH}
    checked = 0
    for doc in request.getfixturevalue(which):
        if doc["product_type"] != "bearing_radial_ball":
            continue
        a = {x["name"]: x["value"] for x in doc["attributes"]}
        assert a.get("Bearing Number") in table, (doc["sku"], a.get("Bearing Number"))
        for name, expected in zip(
            ("Bore", "Outside Dia.", "Width"), table[a["Bearing Number"]], strict=True
        ):
            if name in a:
                assert abs(parse_length(a[name]).inches - expected) < 0.002, (doc["sku"], name)
        checked += 1
    assert checked > 1000


def test_the_series_walk_changes_no_attribute_but_an_identifier():
    """The walk renumbers the series and List Number; a value that merely
    EQUALS the series -- here a planted 'Bearing Number' -- never moves."""
    from synthetic_industrial_products.catalog.config import SMALL
    from synthetic_industrial_products.catalog.generate import Generator, LineDraft
    from synthetic_industrial_products.catalog.model import Attribute

    gen = Generator(SMALL)
    first = LineDraft(item="x", brand=BRANDS[0], series="K100", category=("a",))
    gen._unique_series(first, [])
    fact = Attribute("Bearing Number", "K100")
    ident = Attribute("List Number", "K100")
    second = LineDraft(item="x", brand=BRANDS[0], series="K100", category=("a",))
    second.line_attrs = [fact, ident]
    published = [fact, ident]
    gen._unique_series(second, published)
    assert second.series == "K101"
    assert published == [fact, Attribute("List Number", "K101")]
    assert second.line_attrs == [fact, Attribute("List Number", "K101")]


# --- the brand book -----------------------------------------------------------


def test_every_brand_has_a_unique_name_and_id_code():
    assert len(set(BRANDS)) == len(BRANDS)
    assert len({b.code for b in BRAND_BOOK}) == len(BRAND_BOOK)


def test_the_brand_pool_is_a_long_tail_and_a_few_names_are_ordinary_words(hundred_k):
    """A few broad houses, many small makers; no brand near a tenth of 100K."""
    share = collections.Counter(doc["brand"] for doc in hundred_k)
    total = sum(share.values())
    assert set(share) == set(BRANDS), set(BRANDS) - set(share)
    assert max(share.values()) / total <= 0.10
    assert min(share.values()) / total >= 0.003
    ordinary = {
        "Iron Heron",
        "Lantern Rock",
        "Stone Wicket",
        "Tin Kestrel",
        "Lark & Lathe",
        "Tall Mast",
        "Salt Meadow Works",
        "Wendlow Tool",
    }
    assert ordinary <= set(BRANDS)


def test_not_every_brand_makes_every_type():
    families = [b.families for b in BRAND_BOOK]
    assert sum(len(f) == 1 for f in families) >= len(BRAND_BOOK) // 2


# --- house styles -------------------------------------------------------------


def _contrast(ink: str, paper: str) -> float:
    def lum(colour: str) -> float:
        channels = [int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    hi, lo = sorted((lum(ink), lum(paper)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_every_brand_has_exactly_one_house_style_and_no_two_share_it():
    from synthetic_industrial_products.drawing.style import brand_for_house_style, house_style

    styles = {brand: house_style(brand) for brand in BRANDS}
    pairs = {(s.ink, s.frame) for s in styles.values()}
    assert len(pairs) == len(BRANDS)
    assert len({(s.ink, s.paper, s.frame) for s in styles.values()}) == len(BRANDS)
    # Brands sharing an ink differ in paper as well as in frame.
    for ink in {s.ink for s in styles.values()}:
        papers = [s.paper for s in styles.values() if s.ink == ink]
        assert len(set(papers)) == len(papers), ink
    worst = min((_contrast(s.ink, s.paper), b) for b, s in styles.items())
    assert worst[0] >= 3.0, worst
    for brand, style in styles.items():
        assert brand_for_house_style(style.ink, style.frame) == brand
    assert {s.frame for s in styles.values()} == set(FRAMES)
    assert {s.ink for s in styles.values()} == set(INKS)


#: How each frame shows in the SVG: the sheet border sits 6 units in.
_FRAME_MARK = {
    "rule": re.compile(r'<rect x="6" y="6" width="\d+" height="\d+" fill="none"'),
    "rounded": re.compile(r'<rect x="6" y="6" [^>]*rx="14"'),
    "corners": re.compile(r'<path d="M6 24L6 6M6 6L24 6'),
}


def _frames_in(svg: str) -> set[str]:
    return {name for name, mark in _FRAME_MARK.items() if mark.search(svg)}


def test_every_sampled_drawing_is_in_its_own_brands_house_style():
    """One SKU per (brand, type) of the committed catalog, drawn and read back."""
    from synthetic_industrial_products.catalog import bundle
    from synthetic_industrial_products.drawing import draw_sku
    from synthetic_industrial_products.drawing.style import house_style

    seen = set()
    for line in (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        key = (parent["brand"], parent["product_type"])
        if key in seen:
            continue
        seen.add(key)
        variant = parent["variants"][0]
        data, _ = draw_sku(parent["product_type"], parent["brand"], bundle._record(parent, variant))
        svg = data.decode()
        style = house_style(parent["brand"])
        assert style.ink in svg and f'fill="{style.paper}"' in svg, key
        frames = _frames_in(svg)
        expected = set() if style.frame == "none" else {style.frame}
        assert frames == expected, (key, frames)
    assert len(seen) > 100


# --- each brand's voice -------------------------------------------------------


def _opening(doc: dict) -> str:
    """What a title says before its item: the brand, a qualifier, or nothing."""
    item = next(a["value"] for a in doc["attributes"] if a["name"] == "Item")
    title = doc["title"]
    return title[: title.index(item)] if item in title else "<no item>"


def _about(sentence: str, facts: str) -> bool:
    """Whether a sentence names something the record publishes.

    A word of the record's values (``TiN``), a five-letter stem of one
    (``galvanizing`` for ``Galvanized``), or one of its numbers.
    """
    fact_words = {w.lower() for w in re.findall(r"[A-Za-z]{3,}", facts)} - {"the", "and", "for"}
    stems = {w[:5] for w in fact_words if len(w) >= 5}
    numbers = set(re.findall(r"\d+", facts))
    words = re.findall(r"[A-Za-z]{3,}|\d+", sentence)
    return any(
        w in numbers or w.lower() in fact_words or (len(w) >= 5 and w[:5].lower() in stems)
        for w in words
    )


def voice_deviations(docs: list[dict]) -> list[tuple]:
    """(brand, type) groups whose titles or descriptions break one template.

    Machinery-free: a brand's titles of one type must all open the same way,
    and its descriptions of one type must share their use line and the
    series-masked family line, in one order.
    """
    openings = collections.defaultdict(set)
    tails = collections.defaultdict(list)
    for doc in docs:
        key = (doc["brand"], doc["product_type"])
        openings[key].add(_opening(doc))
        marker = f"{doc['brand']} {doc['series']}. "
        description = without_compatibility(doc["description"])
        tail = description.split(marker, 1)[1] if marker in description else ""
        sentences = [s.replace(doc["series"], "{S}") for s in re.split(r"(?<=\.) ", tail) if s]
        facts = " ".join(a["value"] for a in doc["attributes"])
        tails[key].append((sentences, facts))
    bad = [(key, "title", sorted(o)) for key, o in openings.items() if len(o) != 1]
    for key, groups in tails.items():
        # The template is what EVERY description of the group says: the use
        # line and the series-masked family line, in one order. A sentence
        # beyond it must be about a fact of that record (a benefit names the
        # material or finish; a pack line carries the quantity).
        common = set.intersection(*(set(sentences) for sentences, _ in groups))
        orders = {tuple(x for x in sentences if x in common) for sentences, _ in groups}
        family = any("{S}" in x for x in common)
        if len(common) < 2 or not family or len(orders) != 1:
            bad.append((key, "description", sorted(common)))
            continue
        for sentences, facts in groups:
            stray = [x for x in sentences if x not in common and not _about(x, facts)]
            if stray:
                bad.append((key, "description", stray))
                break
    return bad


@pytest.mark.parametrize("which", ["golden", "hundred_k"])
def test_every_brand_follows_one_template_per_type(which, request):
    """On the committed file AND on a fresh build, so a generator change reds
    here before a regeneration hides it in the golden."""
    assert voice_deviations(request.getfixturevalue(which)) == []


def test_a_planted_off_template_title_and_description_are_caught(golden):
    doc = next(d for d in golden if not d["title"].startswith(d["brand"]))
    off_title = dict(doc, title=f"{doc['brand']} {doc['title']}")
    assert any(v[1] == "title" for v in voice_deviations([*golden, off_title]))
    marker = f"{doc['brand']} {doc['series']}. "
    head, tail = doc["description"].split(marker, 1)
    off_description = dict(
        doc, description=head + marker + "Great value. " + tail[tail.index(" ") :]
    )
    assert any(v[1] == "description" for v in voice_deviations([*golden, off_description]))


def test_two_brands_of_a_type_do_not_all_read_alike(golden):
    """Between brands the template differs: more than one opening per type."""
    openings = collections.defaultdict(set)
    for doc in golden:
        openings[doc["product_type"]].add(_opening(doc).replace(doc["brand"], "<brand>"))
    assert all(len(o) >= 2 for o in openings.values()), openings


def test_every_qualifier_is_non_factual(golden):
    """No qualifier carries a digit, a material, a finish, a grade or 'heavy',
    and none is a VALUE any attribute of its family publishes -- a title word
    that is also a value could contradict the record that carries another."""
    banned = re.compile(r"\d|steel|carbide|cobalt|brass|nylon|zinc|grade|heavy|iso|ansi|din", re.I)
    assert not [w for words in PRODUCT_WORDS.values() for w in words if banned.search(w)]
    from synthetic_industrial_products.catalog.vocab import STANDARDS_FAMILY

    values = collections.defaultdict(set)
    for doc in golden:
        family = STANDARDS_FAMILY[doc["product_type"]]
        values[family].update(a["value"].lower() for a in doc["attributes"])
    clashes = [
        (family, word)
        for family, words in PRODUCT_WORDS.items()
        for word in words
        if any(word.lower() in value for value in values[family])
    ]
    assert clashes == []


# --- no text states what the record does not publish ------------------------

_NUMBER = re.compile(r"\d+(?:[./]\d+)*")
_PAIRS = (
    ("Length of Cut", "Overall Length"),
    ("Flute Length", "Overall Length"),
    ("Thread Length", "Length"),
    ("Thread Length", "Overall Length"),
    ("Thread Length", "Length under Head"),
)


def _defect_signature(attributes: dict[str, str]) -> bool:
    """A record the generator's MODELLED defects rewrote after its title.

    A cut, flute or thread length longer than the part (the census's 8.29%
    LOC > OAL class and its fastener analogue), or a record mixing inch and
    metric units (2.22%). Their titles carry the value before the defect --
    the realistic variant this catalog exists to exhibit -- so a title token
    need not equal the rewritten attribute.
    """

    def length(name):
        try:
            return parse_length(attributes[name]).inches
        except Exception:
            return None

    for short, whole in _PAIRS:
        a, b = length(short), length(whole)
        if a is not None and b is not None and a > b:
            return True
    units = " ".join(attributes.values())
    inch = '"' in units or " in" in units
    metric = "mm" in units
    # Mixed units, or a declared system its values contradict (3.23%).
    declared = " ".join(
        v
        for k, v in attributes.items()
        if k in ("Dimension Type", "Measurement System", "System of Measurement")
    )
    return (inch and metric) or ("Inch" in declared and metric) or ("Metric" in declared and inch)


def _lengths_in(values) -> list[float]:
    """Every published length, in inches and in millimetres."""
    out: list[float] = []
    for value in values:
        try:
            inches = parse_length(value).inches
        except Exception:  # noqa: BLE001 -- not a length
            continue
        out.extend((inches, inches * 25.4))
    return out


def _same_quantity(token: str, lengths: list[float]) -> bool:
    try:
        number = float(Fraction(token)) if "/" in token else float(token)
    except (ValueError, ZeroDivisionError):
        return False
    return any(abs(number - m) <= 0.002 * m for m in lengths if m > 0)


def untraced_numbers(docs: list[dict]) -> tuple[list, int]:
    """(docs with a number no field backs, count excused as modelled defects)."""
    bad, excused = [], 0
    for doc in docs:
        attributes = {a["name"]: a["value"] for a in doc["attributes"]}
        # Every value of every attribute: a multi-valued one (a kit's ``Sizes
        # Included``) is several entries under one name.
        every_value = [a["value"] for a in doc["attributes"]]
        backed = set(_NUMBER.findall(" ".join([*every_value, doc["series"], doc["brand"]])))
        # The cross-reference sentence's numbers are the OTHER product's (the
        # M12 a key drives) and trace to a standard's table instead;
        # ``test_compatibility_text`` checks every one of them there.
        description = without_compatibility(doc["description"])
        stated = set(_NUMBER.findall(doc["title"])) | set(_NUMBER.findall(description))
        # A title composed before the unit-mixing defect names a length in
        # the system it was built in (``4.20mm``) beside the value republished
        # in the other (``0.1654"``). The same quantity is not an invented fact.
        lengths = _lengths_in(attributes.values())
        stated = {n for n in stated - backed if not _same_quantity(n, lengths)} | (stated & backed)
        if stated - backed:
            if _defect_signature(attributes):
                excused += 1
            else:
                bad.append((doc["sku"], sorted(stated - backed)))
    return bad, excused


@pytest.mark.parametrize("which", ["golden", "hundred_k"])
def test_every_number_in_the_text_traces_to_a_field(which, request):
    docs = request.getfixturevalue(which)
    bad, excused = untraced_numbers(docs)
    assert bad == [], bad[:10]
    # Excused only on records carrying a modelled defect, and bounded by the
    # defect rates: measured 0.6% of SKUs on both builds.
    assert excused <= 0.02 * len(docs), excused


def test_a_planted_unbacked_number_is_caught(golden):
    doc = next(
        d for d in golden if not _defect_signature({a["name"]: a["value"] for a in d["attributes"]})
    )
    planted = dict(doc, description=doc["description"] + " Rated to 9999 hours.")
    assert untraced_numbers([planted])[0] == [(doc["sku"], ["9999"])]


def test_a_pack_quantity_is_only_ever_the_records_own(golden):
    pack = re.compile(
        r"(\d+) (?:per Pack|Pk|Pack)\b|[Pp]ack of (\d+)|packs of (\d+)|(\d+) per pack"
    )
    for doc in golden:
        quantity = next(
            (a["value"] for a in doc["attributes"] if a["name"] == "Package Quantity"), None
        )
        for match in pack.finditer(doc["title"] + " " + doc["description"]):
            assert quantity is not None and quantity in match.groups(), (doc["sku"], match.group(0))


def test_every_drawing_declares_its_intrinsic_size():
    """``width="200" height="300"`` on the root, beside the viewBox.

    A viewBox-only SVG in an <img> sized only by max-width/max-height inside a
    non-growing flex item renders at 0 x 0. Checked on one drawing per
    (brand, type) of the committed catalog and on the root of every one.
    """
    from synthetic_industrial_products.catalog import bundle

    files = bundle.rebuild(GOLDEN)
    root = re.compile(
        rb'^<svg xmlns="http://www.w3.org/2000/svg" width="200" height="300" viewBox="0 0 200 300">'
    )
    bad = [path for path, data in files if not root.match(data)]
    assert files and bad == [], bad[:5]

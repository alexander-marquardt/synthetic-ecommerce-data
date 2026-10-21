"""Every product is drawn as its own kind, never as a generic stand-in outside its categories.

The shape audit of the 179-product preview found 36 products drawn with a
generic or borrowed shape: rose bouquets as fruit (``round_produce``), socks
and wallets as a ``box``, beds as ``box_wide``, table lamps as a ``box``
although ``table_lamp`` exists. A generic shape is honest for a few
categories only (packaged food in a box, a storage organiser as a wide box).
:data:`HONEST_FOR` is that allow-list; a sample that uses a generic shape
outside it fails, and the failure names the row. A new product kind gets its
own shape (``kit_more.py`` holds the ones the audit asked for).
"""

from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_preview4 as bp4  # noqa: E402
import kit  # noqa: E402
import kit_more  # noqa: E402,F401 -- registers the shapes below

#: Generic shape -> the category paths (``" > "`` joined, matched as a
#: prefix) where it draws the product honestly.
HONEST_FOR: dict[str, tuple[str, ...]] = {
    "box": ("Food & Drink",),
    # A storage organiser is a fabric box with compartments, so a wide box is its kind.
    "box_wide": ("Food & Drink > Hampers & Gifts", "Home > Storage"),
    # Still generic, honest nowhere now: loose fruit draws as its own
    # ``produce_pile`` (kit_produce.py), so any round_produce use fails.
    "round_produce": (),
    "pouch": (
        "Beauty > Accessories",
        "Beauty > Gift Sets > Make-Up Gift Sets",
        "Beauty > Mother & Baby > Hospital Bags",
        "Beauty > Suncare > Summer Sets",
        "Beauty > Travel & Minis",
    ),
    "top": (
        "Mens > Tops",
        "Womens > Tops > T-Shirts",
        "Womens > Tops > Jersey Tops",
        "Womens > Tops > Long Sleeve Tops",
        "Womens > Knitwear > Jumpers",
    ),
    # A kind's own shape lent to a neighbour the audit also caught.
    "cake": ("Food & Drink > Bakery > Cakes",),
    "gift_bag": ("Beauty > Gift Sets", "Gifts > Gift Wrap"),
    "moisturiser_jar": ("Beauty > Skincare",),
    "mattress_topper": ("Home > Bedding > Mattress Toppers",),
}

#: The shapes the audit asked for, each drawn in the record's fill.
NEW_SHAPES = (
    "bouquet", "socks", "bed_frame", "watch", "earrings", "compact", "cardigan",
    "bodysuit", "wallet", "keyring", "charging_pad", "chairbed", "mattress",
    "potted_tree", "pudding", "panettone", "trophy",
)  # fmt: skip

SAMPLES = [rec for recs in bp4.samples().values() for rec in recs]


def _path(rec: dict) -> str:
    return " > ".join(rec["category_path"])


def _honest(shape: str, path: str) -> bool:
    return any(path == p or path.startswith(p + " > ") for p in HONEST_FOR[shape])


def test_no_generic_shape_outside_the_categories_where_it_is_honest() -> None:
    offenders = [
        f"{rec['product_id']} {rec['title']!r} ({_path(rec)}) is drawn as {rec['drawing']['shape']}"
        for rec in SAMPLES
        if rec["drawing"]["shape"] in HONEST_FOR
        and not _honest(rec["drawing"]["shape"], _path(rec))
    ]
    assert offenders == []


def test_every_allow_list_entry_is_used_by_a_sample() -> None:
    """The allow-list stays exact: an entry no sample needs is removed, not kept 'just in case'."""
    used = {
        (rec["drawing"]["shape"], p)
        for rec in SAMPLES
        for p in HONEST_FOR.get(rec["drawing"]["shape"], ())
        if _path(rec) == p or _path(rec).startswith(p + " > ")
    }
    unused = [(s, p) for s, ps in HONEST_FOR.items() for p in ps if (s, p) not in used]
    assert unused == []


def test_table_lamps_are_drawn_as_a_table_lamp() -> None:
    lamps = [rec for rec in SAMPLES if rec["category_path"][-1] == "Table Lamps"]
    assert [rec["drawing"]["shape"] for rec in lamps] == ["table_lamp"]


@pytest.mark.parametrize("shape", NEW_SHAPES)
def test_a_new_shape_paints_the_records_color_and_pattern(shape: str) -> None:
    assert shape in kit.SHAPES
    solid = kit.render(shape, kit.Fill("solid", "#123456", "#654321"), uid="a")
    striped = kit.render(shape, kit.Fill("stripe", "#abcdef", "#fedcba"), uid="b")
    assert "#123456" in solid
    assert "url(#fill-b)" in striped


@pytest.mark.parametrize("shape", NEW_SHAPES)
def test_a_new_shape_is_used_by_a_sample(shape: str) -> None:
    assert shape in {rec["drawing"]["shape"] for rec in SAMPLES}


def test_a_sock_drawing_shows_the_packs_pair_count() -> None:
    socks = [rec for rec in SAMPLES if rec.get("product_type") == "Socks"]
    assert len(socks) == 7
    for rec in socks:
        n = rec["units_per_pack"]
        assert rec["drawing"]["shape"] == "socks", rec["title"]
        assert rec["drawing"].get("params", {}).get("pairs") == str(n), rec["title"]
        svg = bp4.drawing_svg(rec)
        # One pair is two socks; a pack fans one sock per pair under a band naming the count.
        assert svg.count('class="sock"') == (2 if n == 1 else n), rec["title"]
        assert (f"{n} pairs" in svg) == (n > 1), rec["title"]


@pytest.mark.parametrize("stems", [5, 7, 9])
def test_a_bouquet_draws_its_stem_count_with_its_foliage(stems: int) -> None:
    assert "bouquet" in kit.SHAPES
    svg = kit.render(
        "bouquet", kit.Fill("solid", "#b0182f"), params={"stems": str(stems), "foliage": "#d4af37"}
    )
    assert svg.count('class="bloom"') == stems
    assert len(re.findall(r'class="leaf" fill="#d4af37"', svg)) >= 4


def test_bouquet_records_carry_their_foliage() -> None:
    """A bouquet's foliage color comes from its record: gold eucalyptus is drawn gold."""
    foliage = {
        rec["title"]: rec["drawing"].get("params", {}).get("foliage")
        for rec in SAMPLES
        if rec["category_path"][-1] == "Bouquets"
    }
    assert foliage == {
        "Orange Rose Bouquet": None,
        "Blush Rose & Gold Eucalyptus Bouquet": "#d4af37",
        "Classic Red Rose Bouquet": None,
        "White Rose Bouquet with Gold Foliage": "#d4af37",
    }


def test_round_produce_stays_registered_as_honest_nowhere() -> None:
    """Without its empty entry a round_produce use would pass unchecked."""
    assert HONEST_FOR["round_produce"] == ()
    assert not _honest("round_produce", "Food & Drink > Fruit & Veg > Fruit")


# --- gen#447: the leaf names the garment, so the drawing is that garment -----------------------

import image_release  # noqa: E402
import leaf_shapes  # noqa: E402
import scale  # noqa: E402

#: The reported products: id -> (shape, the parameters its drawing must carry).
EXAMPLES: dict[str, tuple[str, dict[str, str]]] = {
    "PLT-DA02102": ("bomber_jacket", {}),
    "PLT-DA13202": ("puffer", {}),
    "PLT-DXP05": ("puffer", {}),
    "PLT-DXH05": ("shirt_dress", {}),
    "PLT-DA22501": ("top", {"sleeve": "long"}),
    "PLT-DSL029": ("top", {"sleeve": "long"}),
    "BRD-MDPS240": ("top", {"kind": "polo", "neckline": "polo", "sleeve": "short"}),
    "BRD-NXMET041": ("trousers", {"cargo": "yes"}),
    "PLT-OFRPJS": ("shorts", {"style": "sweat", "pocket": "no"}),
    "PLT-DA36301": ("shoe", {"kind": "knee_boot"}),
}


@pytest.fixture(scope="module")
def tpls() -> list[dict]:
    return scale.templates()


def _example(tpls: list[dict], pid: str) -> dict:
    """The template of a reported product. A decoy's ``PLT-DA`` id is its row's position, so it
    moves when a sibling slice adds rows (gen#486): the examples name the hand-named ids."""
    found = [t for t in tpls if t["product_id"] == pid]
    assert found, f"{pid} is not a product of the build: name the reported product's current id"
    return found[0]


@pytest.mark.parametrize("rule", [r.name for r in leaf_shapes.RULES])
def test_a_listed_leaf_is_drawn_as_its_rule(tpls: list[dict], rule: str) -> None:
    mine = [t for t in tpls if getattr(leaf_shapes.rule_for(t), "name", None) == rule]
    assert mine, f"no template falls under the {rule!r} rule"
    wrong = [v for v in leaf_shapes.violations(tpls) if f"({rule})" in v]
    assert not wrong, "\n".join(wrong[:10])


@pytest.mark.parametrize("pid", sorted(EXAMPLES))
def test_a_reported_product_is_drawn_as_its_title(tpls: list[dict], pid: str) -> None:
    shape, params = EXAMPLES[pid]
    tpl = _example(tpls, pid)
    drawing = tpl["drawing"]
    assert drawing["shape"] == shape, tpl["title"]
    for key, value in params.items():
        assert (drawing.get("params") or {}).get(key) == value, f"{tpl['title']}: {key}"


@pytest.mark.parametrize("pid", sorted(EXAMPLES))
def test_a_reported_product_renders(tpls: list[dict], pid: str) -> None:
    tpl = _example(tpls, pid)
    assert len(image_release.render(tpl, tpl["skus"][0], styled=False)) > 1000


def test_a_decoy_titled_boxers_is_not_drawn_as_briefs(tpls: list[dict]) -> None:
    briefs = [
        t["title"]
        for t in tpls
        if t["product_type"] == "Boxers"
        and t["title"].startswith("Boxers")
        and (t["drawing"].get("params") or {}).get("fit") == "brief"
    ]
    assert not briefs, briefs


def test_a_title_that_says_checked_or_striped_is_drawn_so(tpls: list[dict]) -> None:
    bad = []
    for t in tpls:
        pattern = (
            "gingham" if "Checked" in t["title"]
            else "stripe" if "Striped" in t["title"] and t["drawing"]["shape"] == "top"
            else None
        )  # fmt: skip
        if pattern and any(c.get("pattern") != pattern for c in t.get("color_options") or []):
            bad.append(f"{t['product_id']} {t['title']}")
    assert not bad, bad[:10]
    blazer = next(t for t in tpls if t["product_id"] == "BRD-MFBL017")
    assert {c["pattern"] for c in blazer["color_options"]} == {"gingham"}


# --- gen#447: each new part is drawn by its kit function, against the same call without it ---

import kit_garments  # noqa: E402
import kit_outerwear  # noqa: E402


def _svg(parts: list[str]) -> str:
    return "".join(parts)


def test_a_new_garment_part_is_drawn_by_its_kit_function() -> None:
    """Fixed fill, no template build: polo collar, cargo pockets, puffer baffles, dress placket."""
    fill = kit.Fill()
    kw = {"neckline": "polo", "sleeve": "short"}
    tee = _svg(kit_garments.top("#7a8fb5", fill, None, kind="tee", **kw))
    polo = _svg(kit_garments.top("#7a8fb5", fill, None, kind="polo", **kw))
    assert polo.count("<circle") == tee.count("<circle") + 2, "the placket buttons"
    assert polo.count("<path") > tee.count("<path"), "the folded collar and placket"

    plain = _svg(kit_garments.trousers("#7a8fb5", fill, None, style="chino", cargo=""))
    cargo = _svg(kit_garments.trousers("#7a8fb5", fill, None, style="chino", cargo="yes"))
    assert cargo.count("<path") > plain.count("<path"), "the two flapped pockets"
    assert cargo.count("<circle") > plain.count("<circle"), "the pocket buttons"

    baffle = "M126,112 Q200,124 274,112"
    assert baffle in _svg(kit_outerwear.puffer_jacket("#7a8fb5", fill, None))
    assert baffle not in _svg(kit_outerwear.bomber_jacket("#7a8fb5", fill, None))

    dress = _svg(kit_garments.shirt_dress("#7a8fb5", fill, None))
    assert dress.count("<circle") == 6, "six buttons"
    assert "M200,100 L200,364" in dress, "the center placket"
    assert "M200,100 L200,364" not in _svg(kit.SHAPES["dress"]("#7a8fb5", fill, None))


# --- gen#447 part 2: a title that names a part draws that part --------------------------------

import details  # noqa: E402
import named_parts  # noqa: E402

#: The reported products: id -> (the part its title names, the shape that shows it).
NAMED_EXAMPLES: dict[str, tuple[str, str]] = {
    "PLT-DXB04": ("band", "bra"),
    "PLT-DXH03": ("pocket", "blouse"),
    "BRD-KDW012": ("hem", "top"),
    "BRD-MDST611": ("cuffs", "suit_trousers"),
    "BRD-NXMET012": ("waistband", "trousers"),
}


def test_every_apparel_title_that_names_a_part_draws_it(tpls: list[dict]) -> None:
    bad = named_parts.violations(tpls)
    assert not bad, f"{len(bad)} titles name a part that is not drawn:\n" + "\n".join(bad[:12])


@pytest.mark.parametrize("pid", sorted(NAMED_EXAMPLES))
def test_a_reported_title_names_a_part_its_drawing_shows(tpls: list[dict], pid: str) -> None:
    part, shape = NAMED_EXAMPLES[pid]
    tpl = next(t for t in tpls if t["product_id"] == pid)
    color, named_part = named_parts.named(tpl["title"]) or ("", "")
    assert named_part == part, tpl["title"]
    assert tpl["drawing"]["shape"] == shape, tpl["title"]
    assert tpl["drawing"].get("detail") == {"part": part, "color": named_parts.DETAIL_HEX[color]}
    svg = image_release.render(tpl, tpl["skus"][0], styled=False).decode()
    assert f'data-part="{part}"' in svg, f"{tpl['title']}: the {part} is not in the image"


#: Parts a garment's kit has to draw for the rows that name them (shape -> parts).
NEW_PARTS = {
    "bra": ("band", "cups"),
    "blouse": ("collar", "buttons", "pocket"),
    "dinner_suit": ("cuffs",),
}


@pytest.mark.parametrize(("shape", "part"), [(s, p) for s, ps in NEW_PARTS.items() for p in ps])
def test_a_new_part_is_one_the_shape_shows(shape: str, part: str) -> None:
    assert part in details.parts_of(shape)
    fill = kit.Fill(detail=(part, "#c8322b"))
    drawn = kit.SHAPES[shape]("#7a8fb5", fill, None)
    svg = details.overlay(shape, fill, drawn, "#7a8fb5", "t")
    assert f'data-part="{part}"' in svg and "#c8322b" in svg


def test_the_guard_refuses_a_part_not_drawn_and_a_trim_too_fine(tpls: list[dict]) -> None:
    """The guard itself: the build holds no such title, so it is shown on edited copies."""
    tpl = copy.deepcopy(_example(tpls, "PLT-DXH03"))
    assert named_parts.violations([tpl]) == []
    for title in ("Navy Blouse with Red Stitching", "Navy Blouse with Red Piping"):
        assert "too fine" in "".join(named_parts.violations([{**tpl, "title": title}])), title
    tpl["drawing"].pop("detail")
    assert "not drawn" in "".join(named_parts.violations([tpl]))
    tpl["drawing"]["detail"] = {"part": "pocket", "color": "#2a2a2e"}  # drawn, in the wrong color
    assert "not drawn" in "".join(named_parts.violations([tpl]))


def test_a_trim_is_picked_from_the_shape_a_leaf_rule_draws(monkeypatch: pytest.MonkeyPatch) -> None:
    """Today every rule's shape shows the parts its authored one did, so the rule is made to
    differ: a trim is a part of the DRAWN shape."""
    monkeypatch.setattr(leaf_shapes, "shape_of", lambda ptype, shape: "bra")
    assert named_parts.trim_part("Polo Shirt", "tshirt", 0) in {"Straps", "Band", "Cups", "Bow"}


def test_a_trim_part_is_one_the_shape_shows() -> None:
    """A row's trim is picked from the parts its (leaf-rule) shape draws, never one it cannot."""
    for ptype, shape in (("Polo Shirt", "tshirt"), ("Chinos", "trousers"), ("Socks", "socks")):
        part = named_parts.trim_part(ptype, shape, 1).lower()
        assert part in details.parts_of(leaf_shapes.shape_of(ptype, shape)), (ptype, part)
    assert leaf_shapes.shape_of("Polo Shirt", "tshirt") == "top"
    assert [named_parts.trim_part("Polo Shirt", "tshirt", i) for i in (0, 1, 2)] == [
        "Hem", "Collar", "Hem"]  # the i-th part of the shape, wrapping round

"""Motif prints, the print range and multi-fruit produce (gen#125).
Run: ``uv run pytest prototypes/retail_drawings/test_motifs.py``.
"""

# ruff: noqa: E501 -- parametrize rows read better whole.

from __future__ import annotations

import dataclasses
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_preview4  # noqa: E402,F401 -- registers every shape the build draws, so the shape sweep sees them run alone
import distractors as dz  # noqa: E402
import kit_motifs  # noqa: E402
import motifs  # noqa: E402
import prints  # noqa: E402
import samples  # noqa: E402
from build_preview import drawing_svg  # noqa: E402
from class_model import Style  # noqa: E402
from kit import PLACEMENTS, SHAPES, Fill, render  # noqa: E402
from kit_produce import FRUIT, fruit_count, jitter  # noqa: E402
from real_classes import class_docs  # noqa: E402
from variants import cw  # noqa: E402

CORPUS = dz.corpus()
MOTIFS = sorted(kit_motifs.CATEGORY)
NUM = r"(-?[\d.]+(?:e-?\d+)?)"


#: The copies a print of each placement draws when a test does not care.
COUNT = {"placement": 1, "all-over": 2, "scatter": 3}


def _print(motif: str, placement: str, scale: float, spacing: float = 0, count: int | None = None) -> Fill:
    return Fill("print", "#ffffff", "#f28c28", motif=motif, placement=placement, scale=scale,
                spacing=spacing, count=COUNT[placement] if count is None else count)  # fmt: skip


# --------------------------------------------------------------------------
# The registry and rendering
# --------------------------------------------------------------------------


def test_the_registry_is_every_kit_shape_and_every_motif_has_a_known_category() -> None:
    reg = motifs.registry()
    assert list(reg) == list(SHAPES)
    assert set(kit_motifs.CATEGORY.values()) <= set(motifs.CATEGORIES)
    assert len(MOTIFS) == 26
    assert reg["tshirt"].category == "product"
    assert reg["hammer"].category == "tools"
    with pytest.raises(ValueError, match="no kit shape draws it"):
        motifs.motif("unicorn")


@pytest.mark.parametrize("placement", PLACEMENTS)
def test_every_motif_renders_in_every_placement(placement: str) -> None:
    for name in MOTIFS:
        fill = _print(name, placement, 0.6) if placement == "placement" else _print(
            name, placement, 0.1, 120)
        svg = render("tshirt", fill, uid=f"t-{name}")
        ET.fromstring(svg)
        assert f'data-motif="{name}"' in svg, (name, placement)


def test_an_all_over_tile_is_as_wide_as_its_spacing_and_holds_the_half_drop() -> None:
    fill = _print("lemon", "all-over", 0.1, 64)
    tile = motifs.print_defs(fill, "p")
    assert re.search(r'<pattern id="p"[^>]* width="64" height="64"', tile)
    # Two motifs and the copies that wrap in from the neighbouring tiles.
    assert tile.count('class="motif"') == len(motifs.tile_spots(fill)) >= 2
    assert motifs.print_defs(_print("lemon", "placement", 0.6), "p") == ""


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"pattern": "print"}, "names its motif"),
        ({"pattern": "print", "motif": "lemon", "placement": "border", "scale": 0.5}, "unknown placement"),
        ({"pattern": "print", "motif": "lemon", "placement": "placement", "scale": 0}, "not in"),
        ({"pattern": "print", "motif": "lemon", "placement": "placement", "scale": 1.2}, "not in"),
        ({"pattern": "print", "motif": "lemon", "placement": "placement", "scale": 0.6,
          "spacing": 40}, "no repeat spacing"),
        ({"pattern": "print", "motif": "lemon", "placement": "all-over", "scale": 0.2,
          "spacing": 60, "count": 2}, "too large"),
        ({"pattern": "solid", "motif": "lemon"}, "carries no motif"),
    ],
)  # fmt: skip
def test_a_malformed_print_fill_is_refused(kwargs: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Fill(**kwargs)


def test_a_placement_on_a_surface_without_one_or_beyond_its_print_area_is_refused() -> None:
    with pytest.raises(ValueError, match="takes no 'placement' print"):
        motifs.check_surface("dress", "placement")
    with pytest.raises(ValueError, match="not a printable surface"):
        motifs.check_surface("kettle", "all-over")
    # A motif too wide to cover the share asked spans the area's width, never more.
    _, _, w, _ = motifs.PRINT_BOX["tshirt"]
    x0, _, x1, _ = _placed(render("tshirt", _print("car", "placement", 1.0), uid="t"), "car")
    assert x1 - x0 == pytest.approx(w, abs=0.5)


def _placed(svg: str, name: str) -> tuple[float, float, float, float]:
    """The motif's drawn box on the sheet, read from the transform the render wrote."""
    m = re.search(
        rf'data-motif="{name}" transform="translate\({NUM} {NUM}\) rotate\(0\) '
        rf'scale\({NUM}\) translate\({NUM} {NUM}\)"',
        svg,
    )
    assert m, name
    tx, ty, k, ox, oy = map(float, m.groups())
    x0, y0, x1, y1 = motifs.drawn_box(name)
    return (x0 + ox) * k + tx, (y0 + oy) * k + ty, (x1 + ox) * k + tx, (y1 + oy) * k + ty


def test_a_large_placement_fills_55_to_65_percent_of_the_chest_print_area() -> None:
    """Maintainer feedback: a hammer, a drill or a lemon on a tee read as too small."""
    assert "tshirt" in motifs.PRINT_BOX
    cx, cy, w, h = motifs.PRINT_BOX["tshirt"]
    # The chest print area lies on the tee's body, below the neck and between the arms.
    assert cx - w / 2 >= 108 and cx + w / 2 <= 292 and cy - h / 2 >= 100 and cy + h / 2 <= 345
    assert w >= 150
    lo, hi = motifs.LARGE
    assert (lo, hi) == (0.55, 0.65)
    compact = 0
    for name in MOTIFS:
        svg = render("tshirt", _print(name, "placement", motifs.LARGE_SCALE), uid="t")
        x0, y0, x1, y1 = _placed(svg, name)
        share = (x1 - x0) * (y1 - y0) / (w * h)
        # A long or tall motif (a car, a carrot) spans the area's width or height instead.
        spans = x1 - x0 >= w - 0.5 or y1 - y0 >= h - 0.5
        assert lo <= share <= hi or (spans and share < lo), (name, round(share, 3))
        compact += lo <= share <= hi
        assert cx - w / 2 - 0.5 <= x0 and x1 <= cx + w / 2 + 0.5, name
        assert cy - h / 2 - 0.5 <= y0 and y1 <= cy + h / 2 + 0.5, name
    assert compact >= 20
    # The previewed graphics are compact: each covers the share outright.
    for name in ("hammer", "drill", "lemon", "orange", "dinosaur"):
        x0, y0, x1, y1 = _placed(render("tshirt", _print(name, "placement", 0.6), uid="t"), name)
        assert (x1 - x0) * (y1 - y0) / (w * h) == pytest.approx(0.6, abs=0.01), name


def test_every_placement_surface_has_a_print_box_and_every_kit_shape_a_drawn_box() -> None:
    placed = {s for s, (places, _) in motifs.SURFACES.items() if "placement" in places}
    assert placed == set(motifs.PRINT_BOX)
    for name in SHAPES:
        x0, y0, x1, y1 = motifs.drawn_box(name)
        assert 0 <= x0 < x1 <= 400 and -60 <= y0 < y1 <= 460, name


# --------------------------------------------------------------------------
# What may be printed where
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("group", "audience", "range_", "name", "ok"),
    [
        ("tops", "men", "core", "hammer", False),
        ("tops", "men", "novelty", "hammer", True),
        ("bedding", "adult", "novelty", "drill", False),
        ("mugs", "adult", "gift", "tshirt", True),
        ("mugs", "adult", "core", "tshirt", False),
        ("bedding", "kids", "core", "dinosaur", True),
        ("dresses", "women", "core", "dinosaur", False),
        ("tops", "women", "core", "lemon", True),
    ],
)  # fmt: skip
def test_the_allow_list(group: str, audience: str, range_: str, name: str, ok: bool) -> None:
    assert motifs.allowed(group, audience, range_, name) is ok


def test_an_unknown_range_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown range"):
        motifs.allowed("tops", "men", "outlet", "star")


# --------------------------------------------------------------------------
# The print range
# --------------------------------------------------------------------------


def test_every_line_prints_allowed_motifs_on_a_surface_that_takes_them() -> None:
    assert len(prints.LINES) == 12
    for line in prints.LINES:
        assert line.prints and line.plains, line.code
        for p in line.prints:
            assert motifs.allowed(line.group, line.audience, line.range_, p.motif), (line.code, p)
            motifs.check_surface(line.shape, p.placement)
            if p.placement == "placement":
                assert p.scale == motifs.LARGE_SCALE, (line.code, p.motif)
    prints.check_range()


def test_one_style_per_motif_in_a_line() -> None:
    keys = [prints.style_key(line, p) for line in prints.LINES for p in line.prints]
    assert len(keys) == len(set(keys)) == 26
    two = next(line for line in prints.LINES if len(line.prints) == 2)
    a, b = two.prints
    assert prints.style_key(two, a) != prints.style_key(two, b)
    twice = dataclasses.replace(two, prints=(a, dataclasses.replace(a, placement="scatter",
                                                                     scale=0.1, spacing=90)))
    with pytest.raises(ValueError, match="one style per motif"):
        prints.check_range((twice,))


def test_a_motif_its_range_may_not_print_is_refused() -> None:
    core = [x for x in prints.LINES if x.range_ == "core" and x.group == "tops"]
    assert core
    line = core[0]
    bad = dataclasses.replace(line, prints=(dataclasses.replace(line.prints[0], motif="hammer"),))
    with pytest.raises(ValueError, match="may not print 'hammer'"):
        prints.check_range((bad,))


def test_a_print_doc_carries_its_print_and_its_ground_is_the_sku_color() -> None:
    docs = prints.docs()
    printed = [d for d in docs if prints.is_print(d)]
    assert len(printed) == 26 and len(docs) == 102
    for d in printed:
        draw = d["drawing"]
        assert d["pattern"] == "print" and draw["pattern"] == "print"
        named = {a["key"]: a["value"] for a in d["attributes"]}
        assert named["motif"] == motifs.motif(draw["motif"]).label
        assert named["print_placement"] == draw["placement"]
        assert d["color_options"][0]["hex"] == draw["base"]
        assert {s["color"] for s in d["skus"]} == {o["color"] for o in d["color_options"]}
        svg = drawing_svg(d)
        ET.fromstring(svg)
        assert f'data-motif="{draw["motif"]}"' in svg, d["product_id"]
    assert {d["product_id"] for d in docs} <= {d["product_id"] for d in CORPUS}


def test_no_category_is_more_than_a_quarter_prints() -> None:
    assert prints.MAX_PRINT_SHARE == 0.25
    share = prints.print_share(CORPUS)
    assert share and max(share.values()) <= prints.MAX_PRINT_SHARE
    prints.check_share(CORPUS)
    # One more print in a category at the cap tips it over, and is named.
    full = next(p for p, s in share.items() if s == prints.MAX_PRINT_SHARE)
    extra = next(d for d in CORPUS if prints.is_print(d) and tuple(d["category_path"]) == full)
    with pytest.raises(ValueError, match=re.escape(" > ".join(full))):
        prints.check_share([*CORPUS, {**extra, "product_id": "PLT-EXTRA"}])


# --------------------------------------------------------------------------
# Planted distractors that are prints
# --------------------------------------------------------------------------


def _row(query: str) -> dz.Row:
    rows = [r for r in dz.TABLE if r.query == query]
    assert len(rows) == 1, query
    return rows[0]


def test_the_lemon_dress_and_kids_duvet_set_are_real_prints_from_the_range() -> None:
    ranged = {d["product_id"]: d for d in prints.docs()}
    for pid, motif in (("PLT-LEMDRS", "lemon"), ("PLT-DUVKID", "dinosaur")):
        assert pid in ranged and ranged[pid]["drawing"]["motif"] == motif
    lemon = {x.doc["product_id"]: x.doc for x in _row("lemon").distractors}
    assert lemon["PLT-LEMDRS"] is ranged["PLT-LEMDRS"]
    covers = [d for d in lemon.values() if d["category_path"][-1] == "Duvet Covers"]
    assert [d["drawing"].get("motif") for d in covers] == ["lemon"]
    tees = [d for d in lemon.values() if d["category_path"][-1] == "T-Shirts"]
    assert len(tees) == 1 and not prints.is_print(tees[0]) and "Lemon" in tees[0]["title"]


def test_the_oranges_and_dinosaur_rows() -> None:
    oranges = [x.doc for x in _row("oranges").distractors]
    assert sorted(d["category_path"][-1] for d in oranges) == ["Mugs", "T-Shirts", "T-Shirts",
                                                                "Tea Towels"]
    assert sum(d["drawing"].get("motif") == "orange" for d in oranges) == 3
    dino = _row("dinosaur")
    assert [x.doc["drawing"].get("motif") for x in dino.distractors] == ["dinosaur"] * 3
    toys = [d for d in CORPUS if dino.is_intended(d)]
    assert len(toys) == 1 and toys[0]["department"] == ["Toys"]
    assert toys[0]["drawing"]["shape"] == "dinosaur"


# --------------------------------------------------------------------------
# The title's number is the number of copies drawn (maintainer ruling)
# --------------------------------------------------------------------------

#: The motif categories sold in both numbers: one graphic and a repeat.
NUMBERED = ("fruit", "tools")


def _says(title: str, noun: str) -> bool:
    return re.search(rf"\b{re.escape(noun)}\b", title) is not None


def test_the_plural_table_spells_every_fruit_and_tool_motif() -> None:
    nouns = {m.name: (m.label, m.plural) for m in motifs.registry().values() if m.category in NUMBERED}
    assert nouns == {
        "orange": ("Orange", "Oranges"), "lemon": ("Lemon", "Lemons"), "apple": ("Apple", "Apples"),
        "strawberry": ("Strawberry", "Strawberries"), "cherries": ("Cherry", "Cherries"),
        "hammer": ("Hammer", "Hammers"), "wrench": ("Wrench", "Wrenches"),
        "screwdriver": ("Screwdriver", "Screwdrivers"), "drill": ("Drill", "Drills"),
        "screw": ("Screw", "Screws"),
    }


@pytest.mark.parametrize(
    ("placement", "count", "ok"),
    [("placement", 1, True), ("placement", 2, False), ("scatter", 3, True), ("scatter", 6, True),
     ("scatter", 2, False), ("scatter", 7, False), ("all-over", 2, True), ("all-over", 1, False)],
)  # fmt: skip
def test_a_print_draws_exactly_its_count(placement: str, count: int, ok: bool) -> None:
    scale, spacing = (0.6, 0) if placement == "placement" else (0.1, 140)
    if not ok:
        with pytest.raises(ValueError, match="copies"):
            _print("wrench", placement, scale, spacing, count)
        return
    fill = _print("wrench", placement, scale, spacing, count)
    if placement == "placement":
        drawn = render("tshirt", fill, uid="t").count('class="motif"')
    else:
        drawn = len(motifs.layout(fill))
        # Every spot of the repeat is drawn, plus the copies wrapping in from a neighbour.
        base = {(x, y) for x, y, _, _ in motifs.tile_spots(fill) if 0 <= x < spacing and 0 <= y < spacing}
        assert len(base) == count
    assert drawn == count


def test_the_title_is_singular_iff_one_copy_is_drawn() -> None:
    printed = [d for d in prints.docs() if prints.is_print(d)]
    assert printed
    for d in printed:
        draw = d["drawing"]
        named = {a["key"]: a["value"] for a in d["attributes"]}
        m = motifs.motif(draw["motif"])
        count = draw.get("count")
        assert named["motif"] == m.label, d["product_id"]  # the singular lemma, whatever the count
        assert named.get("motif_count") == str(count), d["product_id"]
        fill = Fill("print", draw["base"], draw["accent"], motif=draw["motif"],
                    placement=draw["placement"], scale=draw["scale"], spacing=draw["spacing"],
                    count=count)  # fmt: skip
        assert len(motifs.layout(fill)) == count, d["product_id"]
        assert _says(d["title"], m.label) == (count == 1), d["title"]
        assert _says(d["title"], m.plural) == (count > 1), d["title"]


def test_every_fruit_and_tool_motif_is_sold_singular_and_plural() -> None:
    forms: dict[str, set[bool]] = {}
    for d in prints.docs():
        if prints.is_print(d):
            forms.setdefault(d["drawing"]["motif"], set()).add(d["drawing"].get("count") == 1)
    for m in motifs.registry().values():
        if m.category in NUMBERED:
            assert forms.get(m.name) == {True, False}, m.name


# --------------------------------------------------------------------------
# Produce: the number of fruits drawn comes from the record
# --------------------------------------------------------------------------


def test_fruit_count_reads_the_count_or_the_weight_and_clamps() -> None:
    assert fruit_count("lemon", count=4) == 4
    assert fruit_count("orange", grams=1000) == 5
    assert fruit_count("orange", grams=200) == 3
    assert fruit_count("clementine", grams=1200) == 7
    with pytest.raises(ValueError, match="unknown fruit"):
        fruit_count("kiwi", count=3)
    with pytest.raises(ValueError, match="count or its weight"):
        fruit_count("lemon")


def test_the_fresh_oranges_draw_as_many_fruits_as_their_weight_holds() -> None:
    by_id = {d["product_id"]: d for d in class_docs()}
    for code in ("PLT-ORBLOD", "PLT-ORNAVL", "PLT-OREASY"):
        d = by_id[code]
        params = d["drawing"].get("params", {})
        assert d["drawing"]["shape"] == "produce_pile", code
        assert params["count"] == fruit_count(params["fruit"], grams=d["unit_size"]), code
        assert params["seed"] == code
    assert by_id["PLT-ORNAVL"]["drawing"]["params"]["count"] == 5


def test_a_style_passes_its_weight_into_the_pile_once() -> None:
    def doc(grams: float) -> dict:
        return Style("PILE", "Navel Oranges", "Goldfield Farms", "Food & Drink",
                     ("Food & Drink", "Fresh Produce"), 1.0, "Oranges.", "Oranges", "produce_pile",
                     ((cw("Pack", "#f08a24"), 1),), params=(("fruit", "orange"),),
                     unit=(grams, "g"), colorless=True).doc()  # fmt: skip

    assert doc(1000.0)["drawing"].get("params", {}).get("count") == 5
    assert doc(600.0)["drawing"].get("params", {}).get("count") == 3


def test_the_lemons_and_the_clementines_draw_their_pack() -> None:
    lemons = dz.LEMONS
    pack = {a["key"]: a["value"] for a in lemons["attributes"]}.get("pack_size")
    assert pack is None or pack == "4"
    assert lemons["drawing"]["shape"] == "produce_pile"
    assert lemons["drawing"]["params"]["count"] == 4
    clem = next(r for r in samples.FOOD if r["title"] == "Easy Peeler Clementines 600g")
    grams = float(next(a["value"] for a in clem["attributes"] if a["key"] == "pack_size"))
    assert clem["drawing"]["shape"] == "produce_pile"
    assert clem["drawing"]["params"]["count"] == fruit_count("clementine", grams=grams) == 7


def test_a_pile_is_the_same_on_every_build_and_differs_between_products() -> None:
    assert jitter("PLT-ORNAVL", 0) == jitter("PLT-ORNAVL", 0)
    assert jitter("PLT-ORNAVL", 0) != jitter("PLT-ORBLOD", 0)
    assert set(FRUIT) == {
        "orange", "clementine", "lemon", "apple", "lime", "strawberry", "blackberry",
        "blueberry", "grapefruit", "mandarin", "raspberry", "satsuma", "grape",
    }


# --------------------------------------------------------------------------
# The contact sheet, drawn from catalog records
# --------------------------------------------------------------------------


def test_motif_sheet_writes_twelve_record_drawings_and_a_contact_sheet(tmp_path: Path) -> None:
    out = subprocess.run(
        [sys.executable, str(HERE / "motif_sheet.py"), "--out-dir", str(tmp_path)],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert out.returncode == 0, out.stderr[-2000:]
    names = sorted(p.stem for p in tmp_path.glob("*.svg"))
    assert "contact_sheet" in names and len(names) == 13
    ids = {d["product_id"] for d in (*CORPUS, *class_docs())}
    assert sorted(set(names) - {"contact_sheet"} - ids) == []
    sheet = (tmp_path / "contact_sheet.svg").read_text(encoding="utf-8")
    ET.fromstring(sheet)
    assert sheet.count('viewBox="0 0 400 400"') == 12
    for motif in ("hammer", "drill", "lemon", "orange", "dinosaur"):
        assert f'data-motif="{motif}"' in sheet, motif
    assert sheet.count('class="fruit"') >= 9
    # A singular/plural pair is captioned side by side.
    assert sheet.index(">Wrench Graphic Tee<") < sheet.index(">Wrenches Print Tee<")

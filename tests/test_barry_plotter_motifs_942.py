"""Each Barry Plotter motif prints its own emblem, and the range has 15 motifs (gen#942).

All 8 motifs of gen#925 printed one emblem (gen#928), so `green barry plotter cup` showed the
same mug once per motif: the titles differed and the pictures did not. These tests pin that the
range sells 15 motifs, one product of each kind per motif; that one SKU per motif renders 15
different badges, each drawn inside its disc; and that no motif word is a word of the catalogue's
product types, categories, colors, patterns or materials, so a motif never makes a product
match a search for another kind.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from collections import Counter

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import (
    barry_plotter,
    class_model,
    film_emblems,
    image_release,
    kit,
    scale,
)

#: The motifs the range sells (gen#942: 8 grew to 15).
MOTIFS = 15
#: How far a badge's drawing may reach from its center: the inner edge of the disc's ring
#: (radius 1, stroke 0.09, ``film_emblems._DISC``).
INSIDE = 1 - 0.09 / 2


def _motif_of(title: str) -> str:
    """The motif a range product's title names."""
    (motif,) = [m for m in barry_plotter.MOTIFS if m in title]
    return motif


def _one_row_per_motif(product_type: str = "Mug") -> list:
    return [r for r in barry_plotter.ROWS if r.product_type == product_type]


def test_the_range_sells_15_motifs_one_product_of_each_kind_per_motif() -> None:
    assert len(barry_plotter.MOTIFS) == MOTIFS
    by_kind = Counter(r.code[3:5] for r in barry_plotter.ROWS)
    sets = len(barry_plotter.SET_SIZES)
    assert by_kind == {**dict.fromkeys(barry_plotter.KINDS, MOTIFS), "BS": MOTIFS * sets}
    for code, kind in barry_plotter.KINDS.items():
        rows = [r for r in barry_plotter.ROWS if r.code[3:5] == code]
        assert sorted(_motif_of(r.title) for r in rows) == sorted(barry_plotter.MOTIFS), code
        for r in rows:  # sizes and colors as gen#925 set them
            assert tuple(s for s, _ in r.sizes) == kind.sizes, r.code
            assert set(r.colors) <= set(kind.colors), r.code
            assert len(r.colors) == min(kind.per_product, len(kind.colors)), r.code


@pytest.fixture(scope="module")
def one_sku_per_motif() -> dict[str, tuple[str, str]]:
    """Per motif, its stoneware mug's first SKU image: ``motif -> (product id, svg)``."""
    mugs = {r.product_id for r in _one_row_per_motif()}
    docs = [d for d in scale.templates() if d["product_id"] in mugs]
    out = {}
    for d in docs:
        svg = image_release.render(d, d["skus"][0]).decode()
        out[_motif_of(d["title"])] = (d["product_id"], svg)
    return out


def test_one_sku_per_motif_renders_15_distinct_emblems(one_sku_per_motif) -> None:
    assert len(one_sku_per_motif) == MOTIFS
    badges = set()
    for motif, (pid, svg) in one_sku_per_motif.items():
        emblem = film_emblems.emblem_of_id(pid)
        product = svg.split('<g class="brand">')[0]
        assert film_emblems.badge(emblem) in product, (motif, pid)
        badges.add(film_emblems.badge(emblem))
    assert len(badges) == MOTIFS, len(badges)


# -- every badge inside its disc --------------------------------------------------------------

_Affine = tuple[float, float, float, float, float, float]
_NUMBER = r"-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?"


def _compose(m: _Affine, n: _Affine) -> _Affine:
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (
        a * a2 + c * b2, b * a2 + d * b2, a * c2 + c * d2, b * c2 + d * d2,
        a * e2 + c * f2 + e, b * e2 + d * f2 + f,
    )  # fmt: skip


def _transform(text: str) -> _Affine:
    m: _Affine = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\(([^)]*)\)", text):
        v = [float(x) for x in re.findall(_NUMBER, args)]
        assert name in ("translate", "scale"), f"a badge transform the bound reads: {name}"
        if name == "translate":
            m = _compose(m, (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0))
        else:
            m = _compose(m, (v[0], 0, 0, v[-1], 0, 0))
    return m


def _farthest(svg: str) -> list[tuple[float, str]]:
    """How far each drawn element of a badge reaches from its center, outline included: a path's
    every point and control point (a curve stays inside its control points' hull, and the disc
    is convex), a circle's or an ellipse's center plus its largest radius."""
    reach: list[tuple[float, str]] = []

    def walk(el: ET.Element, m: _Affine) -> None:
        m = _compose(m, _transform(el.get("transform", "")))
        k = math.sqrt(abs(m[0] * m[3] - m[1] * m[2]))
        tag = el.tag.split("}")[-1]
        stroked = el.get("stroke", "none") != "none"
        pad = k * float(el.get("stroke-width", 0)) / 2 if stroked else 0.0
        at = lambda x, y: (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])  # noqa: E731
        if tag == "circle" and (el.get("cx"), el.get("cy"), el.get("r")) == ("0", "0", "1"):
            pass  # the disc itself
        elif tag in ("circle", "ellipse"):
            x, y = at(float(el.get("cx", 0)), float(el.get("cy", 0)))
            r = max(float(el.get(a, 0)) for a in ("r", "rx", "ry"))
            reach.append((math.hypot(x, y) + k * r + pad, ET.tostring(el, "unicode")[:80]))
        elif tag == "path":
            d = el.get("d", "")
            assert not re.search(r"[^MLQCZ\d\s,.e-]", d), f"a path the bound cannot read: {d[:60]}"
            nums = [float(x) for x in re.findall(_NUMBER, d)]
            for x, y in zip(nums[::2], nums[1::2], strict=True):
                px, py = at(x, y)
                reach.append((math.hypot(px, py) + pad, d[:60]))
        for child in el:
            walk(child, m)

    walk(ET.fromstring(svg), (1, 0, 0, 1, 0, 0))
    return reach


def test_every_motif_badge_stays_inside_its_disc() -> None:
    rows = _one_row_per_motif()
    assert len(rows) == MOTIFS
    for r in rows:
        badge = film_emblems.badge(film_emblems.emblem_of_id(r.product_id))
        out = [(round(far, 3), what) for far, what in _farthest(badge) if far > INSIDE + 1e-9]
        assert out == [], (r.title, out[:3])


def test_the_disc_bound_finds_a_drawing_that_leaves_the_disc() -> None:
    """The bound can fail: a path, a circle and a translated group that cross the ring."""
    path = '<g><path d="M0,0 L0.9,0.2" stroke="#000" stroke-width="0.1"/></g>'
    assert max(far for far, _ in _farthest(path)) > INSIDE
    circle = '<g><circle cx="0.5" cy="0" r="0.5" fill="#fff"/></g>'
    assert max(far for far, _ in _farthest(circle)) > INSIDE
    dot = '<circle cx="0" cy="0" r="0.8" fill="#fff"/></g>'
    moved = '<g transform="translate(0.6 0) scale(0.5)">' + dot
    assert max(far for far, _ in _farthest(moved)) == pytest.approx(1.0)
    inside = '<g transform="translate(0.4 0) scale(0.5)">' + dot
    assert max(far for far, _ in _farthest(inside)) <= INSIDE


# -- no motif word is a catalogue word --------------------------------------------------------


def _stem(word: str) -> str:
    """A word without its plural ``s``, so ``seeds`` and ``seed`` meet."""
    w = word.lower()
    return w[:-1] if w.endswith("s") and not w.endswith("ss") else w


def _words(text: object) -> set[str]:
    return {_stem(w) for w in re.findall(r"[a-z]+", str(text).lower())}


def catalogue_words(records: list[dict]) -> dict[str, str]:
    """Every word of the catalogue's product types, category paths, colors, patterns and
    materials, each with where it was first found."""
    found: dict[str, str] = {}

    def add(text: object, where: str) -> None:
        for w in _words(text):
            found.setdefault(w, where)

    for p in (*kit.PATTERNS, *class_model.PATTERNS):
        add(p, f"pattern {p}")
    for r in records:
        add(r["product_type"], f"type {r['product_type']}")
        for c in r.get("category_path", ()):
            add(c, f"category {c}")
        for c in r.get("color_options", ()):
            add(c.get("color"), f"color {c.get('color')}")
            add(c.get("pattern"), f"pattern {c.get('pattern')}")
        for a in r.get("attributes", ()):
            if any(k in a["key"] for k in ("color", "pattern", "material", "fabric")):
                add(a.get("value"), f"{a['key']} {a.get('value')}")
        for s in r["skus"]:
            for k, v in s.items():
                if k in ("color", "pattern"):
                    add(v, f"{k} {v}")
    return found


def clashes(motifs: dict[str, str], words: dict[str, str]) -> dict[str, str]:
    """Each motif word that is a catalogue word, with where the catalogue has it."""
    return {w: words[w] for m in motifs for w in _words(m) if w in words}


@pytest.fixture(scope="module")
def words() -> dict[str, str]:
    return catalogue_words(ceiling_build().records)


def test_no_motif_word_is_a_type_category_color_pattern_or_material_word(words) -> None:
    assert clashes(barry_plotter.MOTIFS, words) == {}


def test_the_word_check_finds_a_planted_color_word(words) -> None:
    """The check can fail: a motif named with a color word of the catalogue (`stone`), a type
    word (`lantern`) or a category word in its plural (`seed`, of Seeds) is found."""
    planted = {**barry_plotter.MOTIFS, "Stone Toad": "", "Lantern Walk": "", "Magic Seed": ""}
    found = clashes(planted, words)
    assert found.keys() >= {"stone", "lantern", "seed"}, found
    assert found["stone"].startswith("color"), found["stone"]

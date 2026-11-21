"""Every bread SKU is a baked loaf of its own crust and form, filling its picture (gen#1126).

Before gen#1126, every bread line was one flat ``loaf`` outline in its flavour's colour, at 0.29
(400g) and 0.46 (800g) of the product area. Fill here is #1111's measure: the share of the plain
sheet's product area (``TURN_AREA``) that the loaf's own ``bread`` group paints in
``image_release.render``'s SVG, so the sheet, the brand tag and the ground shadow are not counted.
The forms are written here from the words a line's name carries, not read from the code under test.
"""

from __future__ import annotations

import functools
import xml.etree.ElementTree as ET

from synthetic_ecommerce_data.domains.retail import grocery, image_release, pack_scale, sheet_cover
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA

FLOOR = 0.5
DRAWN = ("path", "rect", "circle", "ellipse")
CRUSTS = ("White", "Wholemeal", "Seeded", "Sourdough", "Gluten Free Brown", "Malted Beer")
#: A line word -> the loaf it names. Sliced lines are tin loaves (their bag is gen#1126 slice 2).
FORM_WORDS = {
    "Hand Shaped": "boule",
    "Crusty": "boule",
    "Oven Bottom": "oven bottom",
    "Stonebaked": "stonebaked",
    "Thick Sliced": "tin",
    "Medium Sliced": "tin",
    "Farmhouse": "tin",
}


@functools.cache
def _breads() -> tuple[dict, ...]:
    """Every bread line: the grocery build's GRC-BRD lines and the authored ones (PLT-BRBRED)."""
    recs = [r for r in grocery.build() if r["product_type"] == "Bread"]
    ids = {r["product_id"] for r in recs}
    recs += [
        r
        for r in image_release.records()
        if r["product_type"] == "Bread" and r["product_id"] not in ids
    ]
    return tuple(recs)


@functools.cache
def _served(pid: str, sku_id: str) -> str:
    rec = next(r for r in _breads() if r["product_id"] == pid)
    sku = next(s for s in rec["skus"] if s["sku"] == sku_id)
    return image_release.render(rec, sku, styled=False).decode()


def _bread_only(svg: str) -> str:
    """``svg`` with every painted shape outside the ``bread`` group made invisible."""
    root = ET.fromstring(svg)

    def hide(el: ET.Element, inside: bool) -> None:
        inside = inside or "bread" in (el.get("class") or "").split()
        if not inside and el.tag.rsplit("}", 1)[-1] in DRAWN:
            el.set("opacity", "0")
        for child in el:
            hide(child, inside)

    hide(root, False)
    return ET.tostring(root, encoding="unicode")


def _fill(svg: str) -> float:
    return sheet_cover.cover(_bread_only(svg), TURN_AREA, step=4.0)


def _crust(svg: str) -> ET.Element | None:
    """The loaf's crust outline (``class="crust"``), or None when nothing draws one."""
    return next((el for el in ET.fromstring(svg).iter() if el.get("class") == "crust"), None)


def _form(rec: dict) -> str:
    line = (rec["drawing"].get("params") or {}).get("line", "")
    return next((form for word, form in FORM_WORDS.items() if word in line), "")


def test_the_build_sells_every_crust_at_400g_and_800g() -> None:
    flavors = {s["flavor"] for r in _breads() for s in r["skus"] if "flavor" in s}
    assert flavors == set(CRUSTS)
    sizes = {
        s.get("pack_size")
        for r in _breads()
        if r["product_id"].startswith("GRC-")
        for s in r["skus"]
    }
    assert sizes == {"400g", "800g"}


def test_every_bread_sku_fills_half_its_product_area() -> None:
    under = {
        (r["product_id"], s.get("pack_size")): round(share, 3)
        for r in _breads()
        for s in r["skus"]
        if (share := _fill(_served(r["product_id"], s["sku"]))) < FLOOR
    }
    assert not under, f"under {FLOOR:.0%} of the product area: {under}"


def test_the_800g_loaf_is_drawn_larger_than_its_400g() -> None:
    for rec in _breads():
        shares = {
            s.get("pack_size"): _fill(_served(rec["product_id"], s["sku"])) for s in rec["skus"]
        }
        if {"400g", "800g"} <= set(shares):
            assert shares["800g"] > shares["400g"] >= FLOOR, (rec["product_id"], shares)


def test_a_400g_loaf_is_drawn_at_nine_tenths_of_its_800g() -> None:
    """The cube root (0.794) left a 400g loaf under half the product area; a loaf's floor is 0.9."""
    for rec in _breads():
        for sku in rec["skus"]:
            want = 0.9 if sku.get("pack_size") == "400g" and len(rec["skus"]) > 1 else None
            assert pack_scale.factor(rec, sku) == want, (rec["product_id"], sku.get("pack_size"))


def _by_crust(form: str) -> dict[str, str]:
    """Crust -> the served SVG of its first line drawn in ``form``, at 800g."""
    out: dict[str, str] = {}
    for rec in _breads():
        sku = next((s for s in rec["skus"] if s.get("pack_size") == "800g"), None)
        if sku and _form(rec) == form:
            out.setdefault(sku["flavor"], _served(rec["product_id"], sku["sku"]))
    return out


def _rgb(hex_: str) -> tuple[int, ...]:
    return tuple(int(hex_[i : i + 2], 16) for i in (1, 3, 5))


def test_each_of_the_six_crusts_has_its_own_colour_and_texture() -> None:
    drawn = _by_crust("tin")
    assert sorted(drawn) == sorted(CRUSTS)
    looks = {}
    for flavor, svg in drawn.items():
        crust = _crust(svg)
        textures = [
            el.get("class")
            for el in ET.fromstring(svg).iter()
            if "texture" in (el.get("class") or "")
        ]
        looks[flavor] = (crust.get("fill") if crust is not None else None, tuple(textures))
    assert all(fill for fill, _ in looks.values()), looks
    for a in CRUSTS:
        for b in CRUSTS:
            if a < b:
                far = (
                    sum(
                        (x - y) ** 2
                        for x, y in zip(_rgb(looks[a][0]), _rgb(looks[b][0]), strict=True)
                    )
                    ** 0.5
                )
                assert far >= 20, (a, b, looks[a][0], looks[b][0])
                assert looks[a][1] != looks[b][1], (a, b, looks[a][1])


def test_each_form_draws_its_own_outline_and_every_loaf_has_a_highlight_and_shade() -> None:
    outlines: dict[str, set[str]] = {}
    for rec in _breads():
        form = _form(rec)
        if not form:
            continue
        svg = _served(rec["product_id"], rec["skus"][-1]["sku"])
        crust = _crust(svg)
        outlines.setdefault(form, set()).add(crust.get("d") if crust is not None else "")
        assert 'class="gloss"' in svg and 'class="ground"' in svg, rec["product_id"]
    assert sorted(outlines) == sorted(set(FORM_WORDS.values()))
    assert all(len(ds) == 1 for ds in outlines.values()), {f: len(ds) for f, ds in outlines.items()}
    assert len({next(iter(ds)) for ds in outlines.values()}) == len(outlines), (
        "two forms share an outline"
    )

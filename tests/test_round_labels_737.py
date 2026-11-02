"""A label on a round container wraps round it (gen#737): it is not a flat sticker.

On ``tin``, ``bottle``, ``jar`` and ``tub`` (the pot) the label's top and bottom edges are arcs
of the container's rim ellipse; on the tin that is its own ``A88,20`` rim. The pot narrows to its
foot, so its label's sides lean in with it. Flat packs and clothing draw the same bytes as before.
"""

from __future__ import annotations

import hashlib
import re

import pytest

from synthetic_ecommerce_data.domains.retail import kit

FILL = kit.Fill(base="#c0392b")
ROUND = ("tin", "bottle", "jar", "tub")
#: The label panel's outline, as ``kit._panel`` draws it.
LABEL = f'fill="#ffffff" stroke="{kit.INK}" stroke-width="{kit.LW_DETAIL}"'
ARC = re.compile(r"A([\d.]+),([\d.]+) 0 0 ([01]) ([\d.]+),([\d.]+)")


def label(shape: str) -> str:
    return next(e for e in kit.SHAPES[shape](FILL.base, FILL, "Soup") if LABEL in e)


def corners(d: str) -> list[tuple[float, float]]:
    """The outline's corners clockwise from top left: a path's move, then each arc's or line's
    end; a flat ``<rect>``'s four corners."""
    if d.startswith("<rect "):
        x, y, w, h = (
            float(re.search(f' {k}="([\\d.]+)"', d).group(1)) for k in ("x", "y", "width", "height")
        )
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    return [
        (float(x), float(y))
        for x, y in re.findall(r"[MLA](?:[\d.]+,[\d.]+ 0 0 [01] )?([\d.]+),([\d.]+)", d)
    ]


@pytest.mark.parametrize("shape", ROUND)
def test_a_round_containers_label_has_arced_top_and_bottom_edges(shape):
    el = label(shape)
    assert el.startswith("<path "), el
    arcs = ARC.findall(el)
    assert len(arcs) == 2, el
    (top_rx, top_ry, top_sweep, *_), (bot_rx, bot_ry, bot_sweep, *_) = arcs
    # both edges sag toward the viewer: left to right on top, right to left below
    assert (top_sweep, bot_sweep) == ("0", "1"), el
    # one rim's perspective: the tin's 20 over 88
    for rx, ry in ((top_rx, top_ry), (bot_rx, bot_ry)):
        assert float(ry) / float(rx) == pytest.approx(20 / 88, abs=0.01), el


def test_the_tins_label_edges_are_its_rim_arc():
    el = label("tin")
    assert [a[:2] for a in ARC.findall(el)] == [("88", "20"), ("88", "20")], el


@pytest.mark.parametrize("shape", ROUND)
def test_the_word_sits_in_the_middle_of_the_band_below_its_top_edge(shape):
    """The word is centered between the top edge's lowest point and the bottom corners."""
    el = label(shape)
    (x0, y0), (x1, _), _, (_, y3) = corners(el)
    rx, ry = (float(v) for v in ARC.findall(el)[0][:2])
    half = (x1 - x0) / 2
    sag = ry * (1 - (1 - (half / rx) ** 2) ** 0.5)
    drawn = "".join(kit.SHAPES[shape](FILL.base, FILL, "Soup"))
    text = re.search(r'<text x="[\d.]+" y="([\d.]+)"[^>]*font-size="([\d.]+)"[^>]*>Soup<', drawn)
    middle = float(text.group(1)) - float(text.group(2)) * 0.35
    assert middle == pytest.approx((y0 + sag + y3) / 2, abs=0.1), shape


def test_the_pots_label_stays_inside_the_pot():
    """The pot's sides run from (112,118) to (138,356); the label leans in with them."""
    (x0, y0), (x1, _), (x2, y2), (x3, y3) = corners(label("tub"))

    def left(y: float) -> float:
        return 112 + (y - 118) * 26 / 238

    for x, y in ((x0, y0), (x3, y3)):
        assert x >= left(y), (x, y)
    for x, y in ((x1, y0), (x2, y2)):
        assert x <= 400 - left(y), (x, y)
    assert x3 - x0 == pytest.approx(x1 - x2) and x3 > x0
    # the bottom edge is the pot's narrower rim: its half width shrinks by the same lean
    (top_rx, *_), (bot_rx, *_) = ARC.findall(label("tub"))
    assert float(bot_rx) == pytest.approx(float(top_rx) - (x3 - x0))


#: sha256 of each kit shape's plain and marked drawing, taken on main before gen#737: the
#: flat packs that carry a ``_panel`` and some clothing. The kit's own functions are drawn, not
#: ``SHAPES``, which another module may override (``kit_garments`` redraws ``jeans_straight``).
UNCHANGED = {
    "box": "0f69b42a5d696978323706f6e74541e78db964ad3c311e712c8ff340bc76cc22",
    "box_wide": "1b95690ddf781a4350e9a75d519f5d74d30514567d4383d78a7a6926b96ecf55",
    "carton": "cd1690be65e0ea0c3e349cf3a2d8da123fbee3665a997cbfe8368451c13707db",
    "crisps_bag": "35822e795e33386b68adb76cb5a6d506eb2b31f0564e77f260a7eea310b14864",
    "tray": "fe1b5e7b1b307367a8a9ce8b7891456c5d1ae16b33519670351d9c0ad3076278",
    "loaf": "e49c37b6b3c1d2f4de539b17cc8fbafea9095a9bd171a6fab4ad9fa95c5ed8ef",
    "cake": "36f09290b4cd1c45bd06bc1032164b749ecbf449d2b169ea2c54ae0a7f60c2d6",
    "round_produce": "d7ade352b0a115205aeac829d46b62a13e60589998fba858862153f002015dec",
    "tshirt": "e0a099ceda8617959450ef947ad0991f46351d121c0ab2d7563a8ca0fa5b6140",
    "dress": "d23d2f26fa6c20aedf1fa4a0a3f7a3c36aec9a2e5f3ed204f11b849d117ec454",
    "jeans_straight": "7d85ff1aac925524cd51e37e2399c86ce7252b3f3d6493c5c9bb1db5cdd26052",
    "coat": "c96c32c9397b41c01aaa8aca943342e54ab032ee33fae3185d5349b0317fc176",
}
MARKS = {"line": "Classic", "chips": "#ff0000,#00ff00"}


@pytest.mark.parametrize("shape", UNCHANGED)
def test_flat_packs_and_clothing_draw_the_same_bytes(shape):
    draw = getattr(kit, shape)
    plain = "".join(kit._drawn(draw, FILL.base, FILL, "Soup", None))
    marked = "".join(kit._drawn(draw, FILL.base, FILL, "Soup", MARKS))
    assert hashlib.sha256((plain + marked).encode()).hexdigest() == UNCHANGED[shape]

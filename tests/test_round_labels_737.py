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
def test_the_word_sits_inside_the_band(shape):
    el = label(shape)
    (x0, y0), (x1, _), _, (_, y3) = corners(el)
    rx, ry = (float(v) for v in ARC.findall(el)[0][:2])
    half = (x1 - x0) / 2
    sag = ry * (1 - (1 - (half / rx) ** 2) ** 0.5)
    drawn = "".join(kit.SHAPES[shape](FILL.base, FILL, "Soup"))
    y = float(re.search(r'<text x="[\d.]+" y="([\d.]+)"[^>]*>Soup<', drawn).group(1))
    assert y0 + sag < y < y3, (shape, y0 + sag, y, y3)


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


#: sha256 of each shape's plain and marked drawing, taken on main before gen#737.
UNCHANGED = {
    "box": "207491e3cdbff1e622be0991d953816566ad722178579c401b4c298ed01e1c2c",
    "box_wide": "d419b39ead33972ca09224eb2209aaf5a38e0ab87882286525e0300b60eab7f8",
    "carton": "222706a481cd8f94a69baa640130db92bc135e30831a454d93279b938be4aaac",
    "tray": "3cfc3c886a2c950cdfda4910983644f53e075981aba089ebf762877cabc1bd1e",
    "tshirt": "38f72c02dc62e9e526f65e6f6056a48d67f2f781d3bd1b66d2521375c56340aa",
    "dress": "b9c05959ccc64a564f6190d01ab2de7e0f2cfac8506d6cb80432174cda1c8eba",
    "jeans_straight": "eeb24150ceea0208e95ca55739a113833a03c4c8e5c13b5113d23f91de5d04a2",
}


@pytest.mark.parametrize("shape", UNCHANGED)
def test_flat_packs_and_clothing_draw_the_same_bytes(shape):
    plain = kit.render(shape, FILL, label="Soup", brand="Acme")
    marked = kit.render(
        shape, FILL, label="Soup", params={"line": "Classic", "chips": "#ff0000,#00ff00"}
    )
    assert hashlib.sha256((plain + marked).encode()).hexdigest() == UNCHANGED[shape]

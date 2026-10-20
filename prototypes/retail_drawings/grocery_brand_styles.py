"""Marks and house styles of the 22 invented grocery brands of the 50K tier (gen#376).

Each brand of :data:`grocery_rows.TIER_BRANDS` has a mark no other brand uses and a literal style row
(a lockup or a mark in a corner with a tag). :mod:`house_styles` imports this module last, so the marks
join ``MARKS`` and the styles join ``HOUSE_STYLES`` whichever module is imported first.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

import house_styles as hs
from house_styles import H, _dot, _hexagon, _ring, _stroke


def m_furrow(c: str) -> list[str]:
    """Three wavy furrows."""
    return [
        _stroke("M-.8,-.4 Q-.4,-.7 0,-.4 T.8,-.4", 0.12, c),
        _stroke("M-.8,0 Q-.4,-.3 0,0 T.8,0", 0.12, c),
        _stroke("M-.8,.4 Q-.4,.1 0,.4 T.8,.4", 0.12, c),
    ]


def m_heron(c: str) -> list[str]:
    """A long-necked bird: a curved neck on a dot."""
    return [_stroke("M-.4,.8 L-.4,-.1 Q-.4,-.8 .2,-.7 L.7,-.6", 0.12, c), _dot(-0.4, 0.8, 0.1, c)]


def m_oak_cask(c: str) -> list[str]:
    """A barrel: a rounded body with two hoops."""
    return [
        f'<rect x="-.6" y="-.7" width="1.2" height="1.4" rx=".35" fill="none" stroke="{c}" stroke-width=".12"/>',
        _stroke("M-.6,-.25 L.6,-.25 M-.6,.25 L.6,.25", 0.1, c),
    ]


def m_trellis(c: str) -> list[str]:
    """A lattice of crossing canes."""
    return [
        _stroke("M-.7,-.7 L.7,.7 M-.7,0 L0,.7 M0,-.7 L.7,0", 0.1, c),
        _stroke("M.7,-.7 L-.7,.7 M.7,0 L0,.7 M0,-.7 L-.7,0", 0.1, c),
    ]


def m_plum(c: str) -> list[str]:
    """A fruit with a stalk and one leaf."""
    return [
        _dot(0, 0.2, 0.6, c),
        _stroke("M0,-.4 L0,-.8", 0.1, c),
        f'<path d="M0,-.7 Q.4,-.95 .6,-.6 Q.2,-.45 0,-.7 Z" fill="{c}"/>',
    ]


def m_saltmarsh(c: str) -> list[str]:
    """A ring over three grains."""
    return [
        _ring(0, -0.25, 0.5, 0.1, c),
        _dot(-0.4, 0.55, 0.14, c),
        _dot(0, 0.65, 0.14, c),
        _dot(0.4, 0.55, 0.14, c),
    ]


def m_ladle(c: str) -> list[str]:
    """A ladle: a bowl on a long handle."""
    return [_ring(-0.35, 0.35, 0.4, 0.12, c), _stroke("M-.1,.1 L.7,-.7", 0.14, c)]


def m_droplets(c: str) -> list[str]:
    """Three drops falling."""
    return [
        f'<path d="M-.5,-.1 Q-.2,.35 -.5,.5 Q-.8,.35 -.5,-.1 Z" fill="{c}"/>',
        f'<path d="M.1,-.7 Q.45,-.2 .1,.1 Q-.25,-.2 .1,-.7 Z" fill="{c}"/>',
        f'<path d="M.5,.2 Q.75,.55 .5,.8 Q.25,.55 .5,.2 Z" fill="{c}"/>',
    ]


def m_pretzel(c: str) -> list[str]:
    """Two linked rings."""
    return [_ring(-0.35, 0, 0.5, 0.12, c), _ring(0.35, 0, 0.5, 0.12, c)]


def m_crimp(c: str) -> list[str]:
    """A crimped edge over a bar."""
    return [
        _stroke("M-.8,-.2 L-.5,-.5 L-.2,-.2 L.1,-.5 L.4,-.2 L.7,-.5", 0.12, c),
        _stroke("M-.8,.3 L.8,.3", 0.16, c),
    ]


def m_cocoa_pod(c: str) -> list[str]:
    """A pod with a seam."""
    return [
        f'<ellipse cx="0" cy="0" rx=".42" ry=".85" fill="none" stroke="{c}" stroke-width=".12"/>',
        _stroke("M0,-.8 L0,.8", 0.08, c),
    ]


def m_comb_cell(c: str) -> list[str]:
    """A hexagon with a dot."""
    return [
        f'<path d="{_hexagon(0, 0, 0.75)}" fill="none" stroke="{c}" stroke-width=".12"/>',
        _dot(0, 0, 0.2, c),
    ]


def m_churn(c: str) -> list[str]:
    """A churn: a tapering body with a lid."""
    return [
        f'<path d="M-.5,-.5 L.5,-.5 L.35,.8 L-.35,.8 Z" fill="{c}"/>',
        _stroke("M-.65,-.65 L.65,-.65", 0.14, c),
    ]


def m_lantern(c: str) -> list[str]:
    """A hanging lamp."""
    return [
        _stroke("M0,-.9 L0,-.55", 0.1, c),
        f'<rect x="-.45" y="-.55" width=".9" height="1.3" rx=".2" fill="none" stroke="{c}" stroke-width=".12"/>',
        _dot(0, 0.1, 0.18, c),
    ]


def m_loaf(c: str) -> list[str]:
    """A loaf with three slashes."""
    return [
        f'<path d="M-.8,.5 Q-.8,-.6 0,-.6 Q.8,-.6 .8,.5 Z" fill="{c}"/>',
        _stroke("M-.4,-.1 L-.25,.3 M0,-.2 L.15,.2 M.4,-.1 L.55,.3", 0.08, "#ffffff"),
    ]


def m_hearth(c: str) -> list[str]:
    """An arch with a flame dot."""
    return [_stroke("M-.7,.8 L-.7,-.1 A.7,.7 0 0 1 .7,-.1 L.7,.8", 0.13, c), _dot(0, 0.45, 0.2, c)]


def m_lotus(c: str) -> list[str]:
    """Three petals on a base line."""
    return [
        f'<path d="M0,.5 Q-.35,0 0,-.7 Q.35,0 0,.5 Z" fill="{c}"/>',
        _stroke("M-.1,.5 Q-.7,.3 -.8,-.3", 0.12, c),
        _stroke("M.1,.5 Q.7,.3 .8,-.3", 0.12, c),
        _stroke("M-.6,.8 L.6,.8", 0.1, c),
    ]


def m_fern(c: str) -> list[str]:
    """A frond: a stem with paired leaflets."""
    return [
        _stroke("M0,.85 L0,-.8", 0.1, c),
        _stroke("M0,.4 L-.5,.1 M0,.4 L.5,.1 M0,-.1 L-.45,-.4 M0,-.1 L.45,-.4", 0.1, c),
    ]


def m_sheaf(c: str) -> list[str]:
    """A fan of stalks tied at the base."""
    return [
        _stroke("M0,.6 L-.6,-.7 M0,.6 L-.3,-.8 M0,.6 L0,-.85 M0,.6 L.3,-.8 M0,.6 L.6,-.7", 0.09, c),
        _stroke("M-.3,.35 L.3,.35", 0.14, c),
    ]


def m_pippin(c: str) -> list[str]:
    """A half fruit with a seed."""
    return [
        f'<path d="M-.7,0 A.7,.7 0 0 0 .7,0 Z" fill="{c}"/>',
        _stroke("M-.7,0 L.7,0", 0.1, c),
        _stroke("M0,0 L0,-.6", 0.1, c),
    ]


def m_tea_leaves(c: str) -> list[str]:
    """Two tea leaves from one bud."""
    return [
        f'<path d="M0,.7 Q-.8,.2 -.55,-.65 Q.1,-.3 0,.7 Z" fill="{c}"/>',
        f'<path d="M0,.7 Q.8,.2 .55,-.65 Q-.1,-.3 0,.7 Z" fill="{c}" fill-opacity=".6"/>',
    ]


def m_roast_ring(c: str) -> list[str]:
    """A ring broken by a bean slit."""
    return [_ring(0, 0, 0.7, 0.14, c), _stroke("M-.2,-.35 Q.15,0 -.2,.35", 0.1, c)]


hs.MARKS.update(
    {
        "furrow": m_furrow,
        "heron": m_heron,
        "oak_cask": m_oak_cask,
        "trellis": m_trellis,
        "plum": m_plum,
        "saltmarsh": m_saltmarsh,
        "ladle": m_ladle,
        "droplets": m_droplets,
        "pretzel": m_pretzel,
        "crimp": m_crimp,
        "cocoa_pod": m_cocoa_pod,
        "comb_cell": m_comb_cell,
        "churn": m_churn,
        "lantern": m_lantern,
        "loaf": m_loaf,
        "hearth": m_hearth,
        "lotus": m_lotus,
        "fern": m_fern,
        "sheaf": m_sheaf,
        "pippin": m_pippin,
        "tea_leaves": m_tea_leaves,
        "roast_ring": m_roast_ring,
    }
)

# fmt: off
#: Brand -> house style.
STYLES = {
    "Marlpit Growers": H("#f1eff9", "diagonal", "double", "#813c51", "#361129", 1.11, False, "round", "furrow", "mark_left", "bottom_right", "none", "humanist", 400, "smallcaps", 0.0, True),
    "Heronsgate Fresh": H("#e5faed", "lines", "heavy", "#58a99c", "#112711", 1.29, False, "round", "heron", "mark_only", "bottom_left", "rect", "sans", 700, "title", 0.0),
    "Tamsworth Cellars": H("#fcebf3", "lines", "rounded", "#be9727", "#374124", 1.19, True, "round", "oak_cask", "pill", "bottom_right", "none", "mono", 700, "caps", 2.0),
    "Ovenden Vineyards": H("#eef7fa", "lines", "none", "#2eb470", "#3c2336", 0.89, False, "round", "trellis", "mark_only", "top_left", "stamp", "sans", 700, "caps", 0.5),
    "Plumtree Larder": H("#e7fcee", "none", "ticks", "#434c81", "#11132c", 1.12, True, "round", "plum", "mark_right", "top_right", "none", "humanist", 700, "caps", 0.5, True),
    "Saltmarsh Preserves": H("#eff6f8", "hatch", "heavy", "#89324a", "#173825", 0.96, True, "round", "saltmarsh", "mark_only", "bottom_right", "stamp", "serif", 700, "title", 1.5),
    "Hobsworth Kitchen": H("#e8f1f3", "hatch", "heavy", "#219c53", "#122531", 1.18, True, "sharp", "ladle", "mark_left", "bottom_right", "none", "mono", 700, "caps", 0.5),
    "Brindlemere Drinks": H("#e2f0f3", "diagonal", "rounded", "#a7297f", "#18182d", 1.31, False, "round", "droplets", "mark_only", "top_right", "flag", "serif", 400, "caps", 0.5),
    "Thistlemoor Snacks": H("#def4e8", "diagonal", "none", "#aa527f", "#1c162e", 0.98, False, "sharp", "pretzel", "band_top", "top_center", "none", "mono", 400, "caps", 0.0),
    "Pellam Crisps": H("#f4f4e7", "diagonal", "rounded", "#279222", "#353720", 1.22, False, "sharp", "crimp", "mark_only", "top_left", "rect", "mono", 700, "caps", 2.0),
    "Dellwick Chocolatiers": H("#e4e0f4", "lines", "ticks", "#5c3eba", "#2e1930", 1.13, False, "round", "cocoa_pod", "mark_left", "bottom_right", "none", "sans", 700, "title", 2.0),
    "Honeysett Sweets": H("#eef4ea", "none", "double", "#bf5a46", "#421c29", 1.21, False, "sharp", "comb_cell", "mark_only", "bottom_right", "tab", "serif", 700, "caps", 2.0),
    "Wetherly Creamery": H("#f2e3f5", "diagonal", "none", "#791f58", "#310f2f", 1.03, True, "sharp", "churn", "badge", "bottom_center", "none", "serif", 400, "title", 1.0, True),
    "Larchfield Home Care": H("#f9ebe3", "hatch", "thin", "#993831", "#1d3b29", 1.36, False, "sharp", "lantern", "mark_only", "top_left", "underline", "humanist", 700, "title", 0.5),
    "Dunnock Bakehouse": H("#f6e2e1", "none", "none", "#97387c", "#23223a", 1.23, True, "sharp", "loaf", "mark_left", "bottom_right", "none", "sans", 400, "lower", 1.5),
    "Cobbleby Kitchen": H("#fbeffb", "dots", "heavy", "#48bd9b", "#1f143c", 1.09, False, "round", "hearth", "mark_only", "bottom_right", "stamp", "sans", 700, "smallcaps", 1.0),
    "Wyncote Skin": H("#f0f4fa", "lines", "thin", "#2f9d9a", "#280d21", 1.26, False, "sharp", "lotus", "mark_left", "top_center", "none", "mono", 400, "caps", 1.5),
    "Ledwick Botanics": H("#f2fafb", "diagonal", "double", "#b36b60", "#403625", 1.24, True, "round", "fern", "mark_only", "bottom_left", "tab", "serif", 700, "smallcaps", 1.5),
    "Oakenshaw Mills": H("#f8e8fc", "grid", "double", "#398379", "#39153e", 1.39, False, "round", "sheaf", "mark_left", "top_right", "none", "mono", 400, "title", 1.0),
    "Pippinfold Cider Co.": H("#f3f8ef", "none", "thin", "#89367a", "#19240e", 1.01, False, "round", "pippin", "mark_only", "top_right", "outline", "humanist", 400, "caps", 2.0, True),
    "Marrowdale Tea Co.": H("#f4f2fb", "diagonal", "ticks", "#37538c", "#171935", 0.99, False, "sharp", "tea_leaves", "mark_right", "top_left", "none", "sans", 700, "smallcaps", 2.0, True),
    "Fellbeck Roasters": H("#e9f2ee", "hatch", "ticks", "#ba635f", "#1d1f31", 1.06, True, "sharp", "roast_ring", "mark_only", "bottom_left", "flag", "serif", 700, "lower", 2.0),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)

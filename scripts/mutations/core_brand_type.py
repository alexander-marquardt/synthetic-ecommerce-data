"""Mutations that plant a defect in the retail brand type (#412) and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob. Each row plants one defect in
``core/drawing/brand_type.py`` or in the retail prototype's logo layout and names the test of
``tests/test_retail_brand_type_412.py`` that has to see it.
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

T = "tests/test_retail_brand_type_412.py"
PROTO = "prototypes/retail_drawings/house_styles.py"

MUTATIONS: list[Mutation] = [
    Mutation(
        "hold a small-caps name to a full capital's height",
        "core/drawing/brand_type.py",
        '    return cap * SMALL_CAP if style.case == "smallcaps" else cap',
        "    return cap",
        f"{T} -k small_caps",
        "A",
        "no retail wordmark renders under 10 px at the Studio tile",
    ),
    Mutation(
        "start the size search at the cap, under a face's least legible size",
        "core/drawing/brand_type.py",
        "        size = fit_size(style, lines, room, max(max_size, least))",
        "        size = fit_size(style, lines, room, max_size)",
        f"{T} -k under_10px",
        "A",
        "no retail wordmark renders under 10 px at the Studio tile",
    ),
    Mutation(
        "never break a long name into two lines",
        "core/drawing/brand_type.py",
        "        options.append(split)",
        "        pass",
        f"{T} -k breaks_at_its_space",
        "A",
        "a name too long for one line is broken, never shrunk or shortened",
    ),
    Mutation(
        "leave a wordmark's width unpinned",
        "core/drawing/brand_type.py",
        "        f'textLength=\"{width(style, line, size):.1f}\"',\n",
        "",
        (f"{T} -k pinned_to_a_width", f"{T} -k width_pinned"),
        "A",
        "a retail wordmark is pinned to the core's measured width",
    ),
    Mutation(
        "let a sans-bold name be wider than the core's table says",
        "core/drawing/brand_type.py",
        '    "sans": Family("Helvetica, Arial, sans-serif", 0.716, 0.935, 1.0),',
        '    "sans": Family("Helvetica, Arial, sans-serif", 0.716, 0.935, 0.8),',
        f"{T} -k measured_by_the_core",
        "B",
        "retail keeps no second text-width table",
    ),
    Mutation(
        "keep the product's scale when the logo leaves it less room",
        PROTO,
        "    s = min(s0, (hi - lo) / PRODUCT_SPAN)",
        "    s = s0",
        f"{T} -k product_clears_every_logo",
        "A",
        "the product clears every logo's text",
        root=".",
    ),
]

"""Mutation rows for the text-free style levers and the distinguishability rule (gen#55), kept out
of ``mutation_check.py``.

Each row plants one defect and names the test that must go red. ``mutation_check.py`` turns them
into ``Mutation`` rows named ``style levers: ...`` (``--only "style levers:"`` re-runs them). A row
is ``(name, file, old, new, test, property, root)``; ``file`` hangs off the generator package.
"""

# ruff: noqa: E501 -- a row's old and new text are source lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

D = "core/drawing/distinguish.py"
S = "core/drawing/sheet.py"
T = "tests/test_house_style_levers_55.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the frame stops being a strong lever",
        D,
        "if a.frame != b.frame or a.mark != b.mark:",
        "if a.mark != b.mark:",
        f'{T} -k "the_distinguishability_rule and frame"',
        "two brands whose frames differ are visibly different",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the mark stops being a strong lever",
        D,
        "if a.frame != b.frame or a.mark != b.mark:",
        "if a.frame != b.frame:",
        f'{T} -k "the_distinguishability_rule and mark"',
        "two brands whose marks differ are visibly different",
        "src/synthetic_ecommerce_data",
    ),
    (
        "two weak levers are enough",
        D,
        "WEAK_LEVERS_NEEDED = 3",
        "WEAK_LEVERS_NEEDED = 2",
        f'{T} -k "the_distinguishability_rule and two"',
        "two weak levers are not a visible difference",
        "src/synthetic_ecommerce_data",
    ),
    (
        "three weak levers are not enough",
        D,
        "WEAK_LEVERS_NEEDED = 3",
        "WEAK_LEVERS_NEEDED = 4",
        f'{T} -k "the_distinguishability_rule and three"',
        "three weak levers are a visible difference",
        "src/synthetic_ecommerce_data",
    ),
    (
        "every ink pair counts as an ink difference",
        D,
        "MIN_INK_DELTA_E = 15.0",
        "MIN_INK_DELTA_E = 0.0",
        f'{T} -k "the_distinguishability_rule and confusable and alone"',
        "an ink pair a color-blind reader cannot tell apart is no ink difference",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the ink check leaves out protanopia",
        D,
        'VISION: tuple[str, ...] = ("none", "prot", "deut", "trit")',
        'VISION: tuple[str, ...] = ("none", "deut", "trit")',
        f"{T} -k red_and_green_are_confusable",
        "ink distance is the least over all four kinds of vision",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the pack takes every style, clashing or not",
        D,
        "if all(visibly_different(candidate, other) for other in chosen):",
        "if True:",
        f"{T} -k the_pack_is_a_set_of_pairwise_visibly_different_styles",
        "the counted capacity is a set of pairwise visibly different styles",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the dash lever draws a solid line",
        S,
        "                **dash,\n",
        "",
        f'{T} -k "each_lever and dash"',
        "a dash pattern reaches the drawing",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the outline lever strokes the floor weight",
        S,
        '"stroke_width": svg.num(house.stroke),',
        '"stroke_width": LW_PART,',
        f'{T} -k "each_lever and outline"',
        "an outline weight reaches the drawing",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the margin lever is ignored by the frame",
        S,
        "ink, m = house.ink, house.margin",
        "ink, m = house.ink, 6.0",
        f"{T} -k a_margin_moves_every_frame_but_none",
        "a frame margin moves the frame",
        "src/synthetic_ecommerce_data",
    ),
    (
        "a texture is never drawn",
        S,
        'if house.texture == "plain":',
        'if house.texture:',
        f'{T} -k "each_lever and texture"',
        "a texture reaches the drawing",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the chamfer cuts into the plate",
        S,
        "CHAMFER = 7.0",
        "CHAMFER = 12.0",
        f"{T} -k the_chamfer_frame_is_a_closed_polygon",
        "the chamfered frame keeps clear of the brand plate",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the allow-list takes any dash array",
        "core/drawing/__init__.py",
        '"^(?:" + "|".join(re.escape(d) for d in brands.DASHES if d) + ")$"',
        '"^.*$"',
        f"{T} -k the_allow_list_refuses_a_dash_or_texture",
        "the allow-list refuses a dash array the book does not declare",
        "src/synthetic_ecommerce_data",
    ),
    (
        "the book's margin index is read as the default",
        "core/brands.py",
        "MARGINS[book.margin]",
        "MARGINS[0]",
        f"{T} -k a_margin_moves_every_frame_but_none",
        "a brand's declared margin reaches its house style",
        "src/synthetic_ecommerce_data",
    ),
]

PREFIX = "style levers"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]

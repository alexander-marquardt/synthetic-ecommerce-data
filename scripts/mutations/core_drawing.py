"""Mutations that plant a defect in the drawing helpers of the generator core and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- the marking is a function of the RECORD, never of the identity ---
    #
    # These are the checks the issue exists for. The defect class is an
    # attribute published on every record and read by nothing -- which a
    # mutation harness structurally cannot find, since an unread input has no
    # code to mutate. What CAN be planted is the other half: a channel that
    # reads its attribute, validates it, and then draws something else. Every
    # A-direction mutation below is that shape.
    Mutation(
        "make reading a color back resolve to whichever brand comes first",
        "core/drawing/style.py",
        "        if brands.ink_of(brand).lower() == lowered and brands.frame_of(brand) == frame:\n            return brand",
        "        if lowered or brands.ink_of(brand).lower() == lowered and brands.frame_of(brand) == frame:\n            return brand",
        "tests/test_marking.py -k brand",
        "B",
        "the outline color is the brand, and reads back as the brand",
    ),
    # ---- the per-SKU drawings carry no text, and every channel is real ----
    Mutation(
        "print the SKU's size on its drawing",
        "core/drawing/svg.py",
        '        tail = "</svg>"',
        '        tail = \'<text x="10" y="290">1/4"</text></svg>\'',
        "tests/test_sku_drawings.py -k no_drawing_carries_any_text",
        "A",
        "no drawing carries any text but its brand's wordmark",
    ),
    # ---- the brand plate (#132): legible, distinct, and the only text -----
    Mutation(
        "plate: hold the name to a 10 px font size, not a 10 px cap height",
        "core/drawing/sheet.py",
        "NAME_MIN = math.ceil(MIN_NAME_PX / (brand_mark.CAP_HEIGHT * TILE_PX_PER_UNIT) * 10) / 10",
        "NAME_MIN = MIN_NAME_PX / TILE_PX_PER_UNIT",
        "tests/test_brand_marks.py -k 10px_cap_height",
        "A",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "plate: claim the face's capitals are taller than Arial Bold's",
        "core/drawing/brand_mark.py",
        "CAP_HEIGHT, DESCENDER = 0.716, 0.21",
        "CAP_HEIGHT, DESCENDER = 0.8, 0.21",
        "tests/test_brand_marks.py -k 10px_cap_height",
        "A",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "plate: take the first layout whatever size it sets the name at",
        "core/drawing/brand_mark.py",
        "        if found is not None and found.size >= min_size:",
        "        if found is not None:",
        (
            "tests/test_brand_marks.py -k no_layout_sets_legibly",
            "tests/test_brand_marks.py -k 10px_cap_height",
        ),
        "B",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "plate: drop the split-under layout",
        "core/drawing/brand_mark.py",
        'LAYOUTS: tuple[str, ...] = ("beside", "two_beside", "split_under", "under")',
        'LAYOUTS: tuple[str, ...] = ("beside", "two_beside", "under")',
        "tests/test_brand_marks.py -k halves_do_not_both_fit",
        "B",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "let a two-line name's descender hang below the plate",
        "core/drawing/brand_mark.py",
        "        first = min(cy + block / 2 + DESCENDER * size, y1) - DESCENDER * size - block",
        "        first = cy + block / 2 - block",
        "tests/test_brand_marks.py -k inside_the_plate",
        "A",
        "the plate's name stays inside the plate",
    ),
    Mutation(
        "count the pixels either mark inks, not the ones only one inks",
        "core/drawing/brand_mark.py",
        "    return int(np.count_nonzero(mark_bitmap(a, px) ^ mark_bitmap(b, px)))",
        "    return int(np.count_nonzero(mark_bitmap(a, px) | mark_bitmap(b, px)))",
        "tests/test_brand_marks.py -k counts_the_pixels",
        "A",
        "two brands' marks differ visibly",
    ),
    Mutation(
        "let the gate pass any words in a <text>",
        "core/drawing/__init__.py",
        '    if words and " ".join(words) not in _wordmarks():',
        "    if False:",
        (
            'tests/test_brand_marks.py -k "gate_refuses and size"',
            'tests/test_brand_marks.py -k "gate_refuses and half"',
        ),
        "A",
        "a drawing's only text is a brand's wordmark",
    ),
    Mutation(
        "let a font attribute sit on any element",
        "core/drawing/__init__.py",
        '            if name not in ALLOWED_ATTRIBUTES or (name in _TEXT_ONLY and local != "text"):',
        "            if name not in ALLOWED_ATTRIBUTES:",
        (
            'tests/test_brand_marks.py -k "gate_refuses and font"',
            'tests/test_brand_marks.py -k "gate_refuses and circle"',
        ),
        "A",
        "a drawing's only text is a brand's wordmark",
    ),
    Mutation(
        "let a character reference spell the ampersand",
        "core/drawing/__init__.py",
        '    if b"&" in svg.replace(b"&amp;", b""):',
        '    if b"&" in svg.replace(b"&amp;", b"").replace(b"&#38;", b""):',
        'tests/test_brand_marks.py -k "gate_refuses and ampersand"',
        "A",
        "a drawing's only text is a brand's wordmark",
    ),
    Mutation(
        "let the figure area run into the plate",
        "core/drawing/sheet.py",
        "    aw, ah = svg.WIDTH - 2 * MARGIN, FIGURE_HEIGHT - 2 * MARGIN",
        "    aw, ah = svg.WIDTH - 2 * MARGIN, svg.HEIGHT - 2 * MARGIN",
        "tests/test_brand_marks.py -k reaches_the_plate",
        "A",
        "no figure reaches the plate",
    ),
    Mutation(
        "let the handled glass size itself to the whole sheet, plate and all",
        "core/drawing/sheet.py",
        "    by_height = (FIGURE_HEIGHT - 2 * GLYPH_MARGIN - GLYPH_GAP - height) / (-left1 + bottom1)",
        "    by_height = (svg.HEIGHT - 2 * GLYPH_MARGIN - GLYPH_GAP - height) / (-left1 + bottom1)",
        "tests/test_sku_drawings.py -k lens_enlarges_at_least_the_measured_floor",
        "A",
        "no figure reaches the plate",
    ),
    Mutation(
        "draw every brand in one ink",
        "core/drawing/style.py",
        "    ink = brands.ink_of(brand)\n",
        '    ink = brands.ink_of(brand) and "#1b1b1b"\n',
        "tests/test_sku_drawings.py -k brand",
        "A",
        "the brand is the house style",
    ),
    Mutation(
        "draw every product at one fixed scale instead of its type's",
        "core/drawing/__init__.py",
        "    return type_scale(extent)",
        "    return 60.0",
        "tests/test_sku_drawings.py -k true_proportion",
        "A",
        "sizes are visible: one scale per type",
    ),
    Mutation(
        "magnify a part that is small in only one dimension",
        "core/drawing/sheet.py",
        "    if width > svg.WIDTH * MAGNIFY_WIDTH_SHARE or height > svg.HEIGHT * MAGNIFY_HEIGHT_SHARE:",
        "    if width > svg.WIDTH * MAGNIFY_WIDTH_SHARE and height > svg.HEIGHT * MAGNIFY_HEIGHT_SHARE:",
        "tests/test_sku_drawings.py -k ONE_dimension",
        "A",
        "the magnifier applies only when both dimensions are small",
    ),
    Mutation(
        "draw the lens's part at true scale instead of enlarged",
        "core/drawing/sheet.py",
        "    _figure_at(page, figure, house, fill, hatch_id, scale * mag.k, mag.lens)",
        "    _figure_at(page, figure, house, fill, hatch_id, scale, mag.lens)",
        "tests/test_sku_drawings.py -k same_part_enlarged",
        "A",
        "the lens shows the same part enlarged",
    ),
    Mutation(
        "draw the magnifier in black",
        "core/drawing/sheet.py",
        "    _glyph(page, mag, house.ink)",
        '    _glyph(page, mag, "#000000")',
        "tests/test_sku_drawings.py -k brand_ink",
        "A",
        "the magnifier is in the brand ink",
    ),
    Mutation(
        "always use the handled glass, even where it cannot reach x2.5",
        "core/drawing/sheet.py",
        "    if k >= MIN_ENLARGEMENT:",
        "    if True:",
        "tests/test_sku_drawings.py -k handle_less_only",
        "A",
        "every lens enlarges at least x2.5; handle-less only when it must be",
    ),
    Mutation(
        "draw outlines at the old hairline weight",
        "core/drawing/sheet.py",
        "MIN_STROKE = 2.3",
        "MIN_STROKE = 1.6",
        "tests/test_sku_drawings.py -k minimum_stroke",
        "A",
        "no outline is thinner than the minimum stroke",
    ),
    Mutation(
        "pin the magnifier to the top instead of balancing the sheet",
        "core/drawing/sheet.py",
        "    top = (FIGURE_HEIGHT - (glyph_h + GLYPH_GAP + height)) / 2",
        "    top = GLYPH_MARGIN",
        "tests/test_sku_drawings.py -k space_above",
        "A",
        "the magnified sheet is vertically balanced",
    ),
    Mutation(
        "let a drawing carry a title element",
        "core/drawing/__init__.py",
        '    {"svg", "rect", "defs", "pattern", "g", "path", "circle", "text"}',
        '    {"svg", "rect", "defs", "pattern", "g", "path", "circle", "text", "title"}',
        "tests/test_sku_drawings.py -k title",
        "A",
        "no drawing carries any text",
    ),
    Mutation(
        "let a paint reference any url",
        "core/drawing/__init__.py",
        '            elif name != "id" and not (_VALUE_GRAMMAR.get(name) or _NUMERIC).match(value):',
        "            elif False:",
        "tests/test_sku_drawings.py -k paint",
        "A",
        "no drawing carries any text",
    ),
]

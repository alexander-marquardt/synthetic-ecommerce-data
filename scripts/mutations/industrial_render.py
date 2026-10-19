"""Mutations that plant a defect in the industrial renderers (``domains/industrial/render``) and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- the generic images carry no dimension, both directions ----------
    Mutation(
        "put a diameter callout on a generic drawing",
        "domains/industrial/render/generic.py",
        "    _bar(ax, half, body_bottom, cut_top, mark)",
        '    _bar(ax, half, body_bottom, cut_top, mark)\n    cv.diameter_callout(\n        ax, -0.2, half * 2, "Ø1/4\\"", "milling", side=1, overhang=0.02, gap=0.02\n    )',
        "tests/test_generic.py",
        "A",
        "a generic drawing carries no dimension",
    ),
    Mutation(
        "stop DIM being a distinct color, blinding the whole measurement",
        "domains/industrial/render/canvas.py",
        'DIM = "#b03a2e"',
        'DIM = "white"',
        "tests/test_generic.py",
        "B",
        "a generic drawing carries no dimension",
    ),
    # ---- the generic image is not derived from the record, both ways ------
    Mutation(
        "print the SKU on the generic image, as the old fallback did",
        "domains/industrial/render/generic.py",
        "    return render(drawing_for_record(record), path, profile)",
        '    fig, ax = build(drawing_for_record(record), profile)\n    ax.text(0, BOTTOM - 0.04, str(record.get("sku", "")), ha="center", color=cv.MUTED)\n    return cv.save(fig, path, profile)',
        "tests/test_generic.py",
        "A",
        "the generic image is the same file whatever the record says",
    ),
    Mutation(
        "make a dimensioned drawing ignore its diameter, blinding the control",
        "domains/industrial/render/endmill.py",
        '        cut_d=parse_length(require(record, "Milling Dia.")),',
        '        cut_d=parse_length(\'1/4"\') if require(record, "Milling Dia.") else None,',
        "tests/test_generic.py",
        "B",
        "the generic image is the same file whatever the record says",
    ),
    # ---- End Mill Style is read, both directions -------------------------
    Mutation(
        "draw every end mill with a square end, whatever the record says",
        "domains/industrial/render/endmill.py",
        '    published = str(stated if stated else require(record, "End Mill Style")).strip().lower()\n    try:\n        return END_STYLES[published]',
        '    published = str(stated if stated else require(record, "End Mill Style")).strip().lower()\n    try:\n        return "square" if published else END_STYLES[published]',
        "tests/test_endmill.py tests/test_derivation.py",
        "A",
        "the cutting end comes from the record",
    ),
    Mutation(
        "a generic end mill with no style attribute is refused instead of drawn from its type",
        "domains/industrial/render/generic.py",
        '        STYLE_OF_TYPE.get(str(record.get("product_type")))\n        if kind == END_MILL',
        "        None\n        if kind == END_MILL",
        "tests/test_derivation.py",
        "A",
        "the cutting end comes from the product type once the style attribute is gone (#497)",
    ),
    Mutation(
        "draw every GENERIC end mill with a ball nose, whatever it is of",
        "domains/industrial/render/generic.py",
        "    body_bottom = BOTTOM + (half if ball else 0.0)",
        "    ball = True\n    body_bottom = BOTTOM + (half if ball else 0.0)",
        "tests/test_generic.py",
        "B",
        "the cutting end comes from the record",
    ),
    # ---- a hex head is drawn hexagonal, both directions -------------------
    Mutation(
        "draw a hex head's end view as a circle",
        "domains/industrial/render/fastener.py",
        "    if geom.hex_headed:\n        # Six flats, to the published across-flats dimension.",
        "    if False:\n        # Six flats, to the published across-flats dimension.",
        "tests/test_fastener.py",
        "A",
        "a hex head is drawn hexagonal and a socket head round",
    ),
    Mutation(
        "draw EVERY head's end view as a hexagon",
        "domains/industrial/render/fastener.py",
        'HEX_HEADED = {"hex", "hex head", "hexagon"}',
        "HEX_HEADED = CYLINDRICAL | COUNTERSUNK",
        "tests/test_fastener.py",
        "B",
        "a hex head is drawn hexagonal and a socket head round",
    ),
    # ---- the length dimension spans the published length, both ways -------
    Mutation(
        "measure a cylindrical head's length OVER the head",
        "domains/industrial/render/fastener.py",
        "        return self.length.inches\n\n    @property\n    def length_witness_radius",
        "        return self.total_height\n\n    @property\n    def length_witness_radius",
        "tests/test_fastener.py",
        "A",
        "the length dimension spans the published length",
    ),
    Mutation(
        "measure a countersunk head's length UNDER the head",
        "domains/industrial/render/fastener.py",
        "        return self.length.inches\n\n    @property\n    def length_witness_radius",
        "        return self.shank_length\n\n    @property\n    def length_witness_radius",
        "tests/test_fastener.py",
        "B",
        "the length dimension spans the published length",
    ),
    # ---- the flute slope is the helix, both directions --------------------
    Mutation(
        "draw the flute rise from the diameter, not the circumference",
        "domains/industrial/render/endmill.py",
        "        return self.helix_lead / 2.0",
        "        return self.cut_d.inches / math.tan(math.radians(self.helix_deg))",
        "tests/test_endmill.py",
        "A",
        "one flute rises half a helix lead across the visible face",
    ),
    Mutation(
        "draw the flute rise as a WHOLE lead instead of half of one",
        "domains/industrial/render/endmill.py",
        "        return self.helix_lead / 2.0",
        "        return self.helix_lead",
        "tests/test_endmill.py",
        "B",
        "one flute rises half a helix lead across the visible face",
    ),
    # ---- every published attribute reaches the drawing, both directions ---
    Mutation(
        "ignore which hand the record says the helix is, while still listing it",
        "domains/industrial/render/endmill.py",
        "        hand=HANDS.get(hand_raw, 1),",
        "        hand=1,",
        "tests/test_endmill.py",
        "",
        "the hand of the helix comes from the record",
    ),
    Mutation(
        "drop an attribute from the drawing AND from the sheet",
        "domains/industrial/render/endmill.py",
        '        ("Coolant Fed", record.get("Coolant Fed", "")),\n',
        "",
        "tests/test_derivation.py",
        "A",
        "every published attribute reaches the drawing or is declared",
    ),
    Mutation(
        "declare an attribute NOT DRAWN that the drawing does draw",
        "domains/industrial/render/attrs.py",
        "NOT_DRAWN: dict[str, str] = {\n    # The measurement-system attribute",
        'NOT_DRAWN: dict[str, str] = {\n    "Helix Angle": "a claim that nothing in the drawing depends on it",\n    # The measurement-system attribute',
        "tests/test_derivation.py",
        "B",
        "every published attribute reaches the drawing or is declared",
    ),
    # ---- a renderer refuses rather than defaulting, both directions -------
    Mutation(
        "default a drill's shank diameter to its nominal size",
        "domains/industrial/render/drill.py",
        '        shank_d=parse_length(require(record, "Shank Dia.")),',
        '        shank_d=parse_length(record.get("Shank Dia.") or record["Size"]),',
        "tests/test_refusals.py",
        "A",
        "a dimension is refused, never defaulted",
    ),
    Mutation(
        "clamp a self-contradictory washer instead of refusing it",
        "domains/industrial/render/washer.py",
        "    if geom.inside_d.inches >= geom.outside_d.inches:",
        "    if False:",
        "tests/test_refusals.py",
        "B",
        "a dimension is refused, never defaulted",
    ),
    # ---- the head style decides the SHAPE, both directions ---------------
    Mutation(
        "draw a button head as the cylinder a socket head cap screw has",
        "domains/industrial/render/fastener.py",
        "    @property\n    def domed(self) -> bool:\n        return self.head_style.strip().lower() in DOMED",
        "    @property\n    def domed(self) -> bool:\n        return False",
        (
            "tests/test_fastener.py -k each_head_style",
            "tests/test_fastener.py -k button_head",
        ),
        "A",
        "each head style draws the shape its record names",
    ),
    Mutation(
        "dome every head that is not countersunk, so socket and button agree again",
        "domains/industrial/render/fastener.py",
        "    @property\n    def domed(self) -> bool:\n        return self.head_style.strip().lower() in DOMED",
        "    @property\n    def domed(self) -> bool:\n        return not self.countersunk",
        "tests/test_fastener.py -k each_head_style",
        "B",
        "each head style draws the shape its record names",
    ),
    # ---- and it decides which line drawing a LINE gets, both directions ---
    Mutation(
        "give the low head drawing a full socket head's height",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.062",
        "    head_half, head_h = 0.105, 0.115",
        (
            "tests/test_generic.py -k drawn_lower",
            "tests/test_generic.py -k DIFFERENT",
        ),
        "A",
        "the new screw silhouettes are drawn to the proportions their standards give them",
    ),
    # ---- the button head is a DOME, and not a bar, both directions -------
    #
    # The first metric here counted rows wider than the shank, which a dome's
    # height does not drive monotonically. All four of these came back GREEN
    # against it -- including the last, which is the whole shape -- and the
    # measurement in test_generic.py was rewritten for them.
    Mutation(
        "draw the button head's dome as the plain rectangle a bar head has",
        "domains/industrial/render/generic.py",
        "                dome_profile(head_half, head_h, seat),",
        "                [(-head_half, seat), (-head_half, _HEAD_TOP), "
        "(head_half, _HEAD_TOP), (head_half, seat)],",
        (
            "tests/test_generic.py -k dome",
            "tests/test_generic.py -k head_measurement",
        ),
        "A",
        "a button head is drawn as a dome and a socket head as a bar",
    ),
    Mutation(
        "dome the socket head cap screw, so the shape no longer names the style",
        "domains/industrial/render/generic.py",
        "    _bar(ax, head_half, seat, _HEAD_TOP, mark)\n    # The socket, drawn as the opening",
        "    _hatched(\n        ax,\n        ax.add_patch(\n            Polygon(\n"
        "                dome_profile(head_half, head_h, seat),\n                closed=True,\n"
        "                fc=mark.tint or cv.BODY_FILL,\n                ec=mark.ink,\n"
        "                lw=cv.LW_BODY,\n                zorder=5,\n            )\n        ),\n"
        "        mark,\n    )\n    # The socket, drawn as the opening",
        (
            "tests/test_generic.py -k dome",
            "tests/test_generic.py -k head_measurement",
        ),
        "B",
        "a button head is drawn as a dome and a socket head as a bar",
    ),
    # ---- the button head is drawn LOWER than a socket head, both ways -----
    Mutation(
        "draw the button head taller than the socket head cap screw",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.112, 0.056",
        "    head_half, head_h = 0.112, 0.200",
        'tests/test_generic.py -k "drawn_lower"',
        "A",
        "a button head is drawn lower than a socket head cap screw",
    ),
    Mutation(
        "flatten the socket head cap screw to the button head's height",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.105, 0.056",
        'tests/test_generic.py -k "drawn_lower"',
        "B",
        "a button head is drawn lower than a socket head cap screw",
    ),
    # ---- and WIDER than one, both ways -----------------------------------
    Mutation(
        "give the button head the socket head cap screw's own width",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.112, 0.056",
        "    head_half, head_h = 0.105, 0.056",
        'tests/test_generic.py -k "drawn_wider"',
        "A",
        "a button head is drawn wider than a socket head cap screw",
    ),
    Mutation(
        "widen the socket head cap screw past the button head",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.130, 0.115",
        'tests/test_generic.py -k "drawn_wider"',
        "B",
        "a button head is drawn wider than a socket head cap screw",
    ),
    # ---- the dome arc is the cap the two numbers name, both directions ----
    Mutation(
        "take the rim angle with asin, which draws the minor arc on a tall dome",
        "domains/industrial/render/fastener.py",
        "    half_angle = math.atan2(r_head, radius - rise)",
        "    half_angle = math.asin(min(1.0, r_head / radius))",
        'tests/test_fastener.py -k "dome"',
        "A",
        "the dome is the cap its chord and rise name, at any rise",
    ),
    Mutation(
        "strike the dome about the chord's own half-width instead of the sphere",
        "domains/industrial/render/fastener.py",
        "    radius = (r_head * r_head + rise * rise) / (2 * rise)",
        "    radius = r_head",
        'tests/test_fastener.py -k "dome"',
        "B",
        "the dome is the cap its chord and rise name, at any rise",
    ),
    Mutation(
        "flatten the socket head cap screw to a low head's height",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.105, 0.062",
        (
            "tests/test_generic.py -k drawn_lower",
            "tests/test_generic.py -k DIFFERENT",
        ),
        "B",
        "the new screw silhouettes are drawn to the proportions their standards give them",
    ),
    # ---- a published value is a token, not prose, both directions ---------
    Mutation(
        "let the stamp break a published value at its hyphen",
        "domains/industrial/render/marking.py",
        "        return tuple(textwrap.wrap(text, width=columns, break_on_hyphens=False)) if text else ()",
        "        return tuple(textwrap.wrap(text, width=columns, break_on_hyphens=True)) if text else ()",
        "tests/test_marking.py -k hyphen",
        "A",
        "the card stamp sets every published value and nothing else",
    ),
    Mutation(
        "draw two brands with one mark",
        "domains/industrial/drawing/brand_marks.py",
        '    "checker": (\n        Poly(((-0.9, -0.9), (0, -0.9), (0, 0), (-0.9, 0))),\n        Poly(((0, 0), (0.9, 0), (0.9, 0.9), (0, 0.9))),\n    ),',
        '    "checker": (Poly(((-0.3, -0.95), (0.3, -0.95), (0.3, -0.3), (0.95, -0.3), (0.95, 0.3), (0.3, 0.3), (0.3, 0.95), (-0.3, 0.95), (-0.3, 0.3), (-0.95, 0.3), (-0.95, -0.3), (-0.3, -0.3))),),',
        "tests/test_brand_marks.py -k differ_visibly",
        "B",
        "two brands' marks differ visibly",
    ),
    Mutation(
        "draw a screw without reading its length",
        "domains/industrial/drawing/figures.py",
        "    fig = Figure(size_in=visible if broken else total)",
        "    fig = Figure(size_in=visible if broken else total)\n    total = hh + 4 * major",
        "tests/test_sku_drawings.py -k published_length",
        "A",
        "a drawn dimension changes the drawing",
    ),
]

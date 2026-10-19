"""Mutation rows for the drawing primitives and their declarative layer (#74).

Each row plants one plausible defect in ``primitives.py``, ``compose.py`` or the figures built
on them and names the test that must go red. ``mutation_check.py --only "drawing primitives:"``
re-runs them. A row is ``(name, file, old, new, tests, property)``.
"""

from __future__ import annotations

from mutation_row import Row

T = "tests/test_drawing_primitives_74.py -k"
PRIM = "domains/industrial/drawing/primitives.py"
COMP = "domains/industrial/drawing/compose.py"
FIG = "domains/industrial/drawing/figures.py"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "a hex body is drawn across its flats",
        PRIM,
        "across_corners = across_flats * 2 / math.sqrt(3)",
        "across_corners = across_flats",
        f'{T} "hex_body_is_as_wide"',
        "a hex body is as wide as its corners",
    ),
    (
        "a chamfer widens the end instead of narrowing it",
        PRIM,
        "(r - cut, y1 - drop)",
        "(r + cut, y1 - drop)",
        f'{T} "chamfer_narrows"',
        "a chamfer cuts the far end in by its inset",
    ),
    (
        "thread crests run into the chamfer",
        PRIM,
        "y1 - chamfer_length, pitch",
        "y1, pitch",
        f'{T} "thread_crests_stop"',
        "crests stop where the chamfer starts",
    ),
    (
        "a pan head has no straight wall",
        PRIM,
        "crown = PAN_CROWN * height",
        "crown = height",
        f'{T} "pan_head"',
        "a pan head differs from a button head",
    ),
    (
        "the drive recess is drawn at the corner size",
        PRIM,
        "hex_face(fig, centre, key / math.sqrt(3)",
        "hex_face(fig, centre, key",
        f'{T} "drive_recess_is_a_dark"',
        "a recess's flats are the key size",
    ),
    (
        "flutes are spaced by the whole lead",
        PRIM,
        "pitch = lead / flutes",
        "pitch = lead",
        f'{T} "same_svg_bytes"',
        "flute spacing is the lead over the flute count",
    ),
    (
        "a tube has one wall",
        PRIM,
        'fig.rect(r_in, y0, r_out, y1, "plain")',
        'fig.rect(r_in, y0, r_in, y1, "plain")',
        f'{T} "tube_is_two_walls"',
        "both walls are drawn",
    ),
    (
        "a spec's source never says nominal",
        COMP,
        "elif read and read[0]:",
        "elif read:",
        f'{T} "nothing_readable"',
        "the source says nominal when the primary dimension is not read",
    ),
    (
        "a contradicting pair is drawn as published",
        COMP,
        "dim.above is not None and got <= values[dim.above]",
        "False",
        f'{T} "contradicts_itself"',
        "an impossible pair falls back to nominal",
    ),
    (
        "a missing primitive parameter is not refused",
        COMP,
        "inspect.signature(fn).bind(None",
        "inspect.signature(fn).bind_partial(None",
        f'{T} "wrong_parameters"',
        "a spec giving a primitive the wrong parameters is refused",
    ),
    (
        "an omitted dimension takes zero",
        COMP,
        "values[dim.name] = float(evaluate(dim.nominal, values))",
        "values[dim.name] = 0.0",
        f'{T} "record_omits"',
        "an omitted dimension takes its nominal proportion",
    ),
    (
        "the drill is drawn with four flutes",
        FIG,
        "flutes=2,",
        "flutes=4,",
        f'{T} "same_svg_bytes"',
        "the moved drill draws the bytes it drew before",
    ),
    (
        "a screw's thread end is chamfered on every section",
        FIG,
        "chamfer if b >= total else 0.0,",
        "chamfer,",
        f'{T} "same_svg_bytes"',
        "the moved screw draws the bytes it drew before",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "drawing primitives"


def rows() -> list[Row]:
    return [Row(n, f, o, w, t, p) for n, f, o, w, t, p in ROWS]

"""Mutation rows for the footwear styles (gen#216), kept out of ``mutation_check.py``.

Each row plants one defect that makes a variant axis of a new shoe kind stop changing the
drawing, or lets a drawing param drift from the attribute it draws, and names the tests that
must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``footwear styles: ...`` (``--only "footwear styles:"`` re-runs them). A row is
``(name, file, old, new, test, property)``; the root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_footwear_styles_216.py"
_AXIS = f"{_T}::test_the_variant_axis_that_changes_the_look_changes_the_drawing"
_AGREE = f"{_T}::test_a_drawing_param_agrees_with_the_attribute_it_draws"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "every wedge is drawn at the default heel",
        "kit_footwear.py",
        'k = _fit(k, rise, inst, heel=_px(got["heel"]))',
        'k = _fit(k, rise, inst, heel=_px("60"))',
        _AXIS,
        "a higher wedge draws higher",
    ),
    (
        "every platform trainer is drawn on the default platform",
        "kit_footwear.py",
        'k = _fit(k, rise, inst, sole=_px(got["platform"]))',
        'k = _fit(k, rise, inst, sole=_px("40"))',
        _AXIS,
        "a taller platform draws taller",
    ),
    (
        "every barefoot shoe is drawn with the default sole",
        "kit_footwear.py",
        'sole=max(3, round(float(got["sole"])))',
        'sole=5',
        _AXIS,
        "a thicker barefoot sole draws thicker",
    ),
    (
        "a wedge espadrille is drawn flat",
        "kit_footwear.py",
        'heel=0 if got["heel"] == "flat" else 40',
        'heel=0',
        _AXIS,
        "a wedge espadrille has a wedge",
    ),
    (
        "a block heel mule is drawn as a kitten heel",
        "kit_footwear.py",
        '"block": (56, "block")',
        '"block": (34, "kitten")',
        _AXIS,
        "each mule heel draws its own",
    ),
    (
        "an open toe mule is drawn closed",
        "kit_footwear.py",
        'elif kind == "mule" and axes["toe"] == "open":',
        'elif kind == "mule" and axes["toe"] == "never":',
        _AXIS,
        "an open toe mule leaves the toe open",
    ),
    (
        "a clog has no back strap",
        "kit_footwear.py",
        'axes.get("strap") == "back"',
        'axes.get("strap") == "never"',
        _AXIS,
        "a back strap clog draws its strap",
    ),
    (
        "a wood clog is drawn with the foam sole",
        "kit_footwear.py",
        'sole_style="wood" if got["body"] == "wood" else "eva"',
        'sole_style="eva"',
        _AXIS,
        "a wood clog draws a wooden sole",
    ),
    (
        "a glitter jelly shoe is drawn plain",
        "kit_footwear.py",
        'if axes.get("glitter") == "yes":',
        'if axes.get("glitter") == "never":',
        _AXIS,
        "a glitter jelly shoe sparkles",
    ),
    (
        "a sandal jelly shoe is drawn as a ballet shoe",
        "kit_footwear.py",
        'if kind == "sandal" or (kind == "jelly" and axes["style"] == "sandal"):',
        'if kind == "sandal":',
        _AXIS,
        "a sandal jelly shoe is a sandal",
    ),
    (
        "a mules heel param is read from its toe",
        "footwear_rows.py",
        'return {"heel": e["heel_type"].lower(), "toe": e["toe_style"].lower()}',
        'return {"heel": e["toe_style"].lower(), "toe": e["toe_style"].lower()}',
        _AGREE,
        "a mule's heel param is its heel attribute",
    ),
    (
        "an espadrille heel param is always flat",
        "footwear_rows.py",
        'return {"heel": e["heel_type"].lower()}',
        'return {"heel": "flat"}',
        _AGREE,
        "an espadrille's heel param is its heel attribute",
    ),
    (
        "a jelly shoe glitter param is always no",
        "footwear_rows.py",
        '"glitter": e["glitter"].lower()}',
        '"glitter": "no"}',
        _AGREE,
        "a jelly shoe's glitter param is its glitter attribute",
    ),
    (
        "a barefoot sole param is always 5",
        "footwear_rows.py",
        'return {"sole": str(e["sole_thickness"])}',
        'return {"sole": "5"}',
        _AGREE,
        "a barefoot shoe's sole param is its sole thickness",
    ),
    (
        "a clog's strap param is always none",
        "footwear_rows.py",
        '{"strap": "back" if e["strap"] == "Back strap" else "none",',
        '{"strap": "none",',
        _AGREE,
        "a clog's strap param is its strap attribute",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "footwear styles"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]

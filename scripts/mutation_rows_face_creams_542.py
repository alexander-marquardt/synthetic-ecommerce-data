"""Mutation rows for the face cream range (gen#542).

They are kept out of ``mutation_check.py``. Each row plants one defect in the range, its brand
styles or its registration, and names the test that must go red. ``mutation_row.discover`` finds
this file by glob and the harness names the rows ``face creams: ...`` (``--only "face creams:"``
re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- a row quotes the source line it plants in, whole.

from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"
_T = "tests/test_retail_face_creams_542.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a mid-tier line is priced linearly by volume",
        "type_specs/face_cream.py",
        '"Normal", "Dullness", (22.0, 32.0, 52.0), PACK_SAND),',
        '"Normal", "Dullness", (22.0, 36.0, 73.0), PACK_SAND),',
        f"{_T} -k price_per_ml_falls_as_volume_rises",
        "a bigger pot costs less per ml in every series of the type",
        _R,
    ),
    (
        "a premium line's 100 ml pot costs more per ml than its 50 ml one",
        "type_specs/face_cream.py",
        '"Dry", "Fine Lines", (64.0, 92.0, 138.0), PACK_INK),',
        '"Dry", "Fine Lines", (64.0, 92.0, 190.0), PACK_INK),',
        f"{_T} -k price_per_ml_falls_as_volume_rises",
        "a bigger pot costs less per ml in every series of the type",
        _R,
    ),
    (
        "an SPF line loses its SPF option, so its two SPFs share one SKU series",
        "type_specs/face_cream.py",
        'PACK, spf=("30", "50")),\n    _line("FCPLSN"',
        'PACK, spf=("30", "30")),\n    _line("FCPLSN"',
        f"{_T} -k price_per_ml_falls_as_volume_rises",
        "two SKUs of one series at one volume are not a price that falls",
        _R,
    ),
    (
        "one brand's SPF line is no longer an SPF line",
        "type_specs/face_cream.py",
        '"Day Face Cream SPF 30", "Cleary Dew"',
        '"Day Face Cream", "Cleary Dew"',
        f"{_T} -k each_new_brand_sells_a_day_a_night_and_an_spf_line",
        "each of the five new brands sells a day, a night and an SPF line",
        _R,
    ),
    (
        "one brand drops its 100 ml size",
        "type_specs/face_cream.py",
        'sizes = tuple(zip(("30", "50", "100"), prices, strict=True))',
        'sizes = tuple(zip(("30", "50", "100"), prices, strict=True)) if prices[0] > 10 else tuple(zip(("30", "50"), prices))',
        f"{_T} -k each_new_brand_sells_a_day_a_night_and_an_spf_line",
        "each of the five new brands sells all of 30, 50 and 100 ml",
        _R,
    ),
    (
        "the five brands lose their house styles",
        "house_styles.py",
        "\nimport face_cream_brand_styles  # noqa",
        "\n# import face_cream_brand_styles  # noqa",
        "tests/test_retail_scale.py -k every_brand_in_the_build_has_a_house_style",
        "every brand in the build has a house style",
        _R,
    ),
    (
        "two face cream brands share a mark",
        "face_cream_brand_styles.py",
        '"Wyncombe Skin":  H("#f6f4ec", "lines", "rounded", "#6d8a3c", "#2c3a18", 0.95, False, "round", "fern",  ',
        '"Wyncombe Skin":  H("#f6f4ec", "lines", "rounded", "#6d8a3c", "#2c3a18", 0.95, False, "round", "swirl", ',
        f"{_T} -k house_style_and_a_mark_of_its_own",
        "every brand of the type has a mark of its own",
        _R,
    ),
    (
        "Face Cream is on the legacy list again, beside its spec",
        "type_specs/legacy_types.txt",
        "Beauty|Eye Cream\n",
        "Beauty|Eye Cream\nBeauty|Face Cream\n",
        "tests/test_retail_type_specs_351.py -k every_type_is_registered_through_a_spec_or_the_legacy_list",
        "a type is registered through a spec or the legacy list, never both",
        _R,
    ),
    (
        "a brand's owner is left out of the spec",
        "type_specs/face_cream.py",
        '        ("Sorrene Atelier", "third_party"),\n',
        "",
        "tests/test_retail_type_specs_351.py -k spec",
        "every brand of a spec has a declared owner",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "face creams"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]

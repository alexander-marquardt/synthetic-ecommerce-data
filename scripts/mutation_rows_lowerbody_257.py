"""Mutation rows for the lower-body drawing params (gen#257), kept out of ``mutation_check.py``.

Each row changes one drawing param of a shorts, cycling-shorts or tracksuit row while the record
still states the old value, and names the test that must go red. ``mutation_check.py`` turns them
into ``Mutation`` rows named ``lower-body params: ...`` (``--only "lower-body params:"`` re-runs
them). A row is ``(name, file, old, new, test, property)``; the root is
``prototypes/retail_drawings``.
"""

from __future__ import annotations

_T = "tests/test_retail_lowerbody_206.py"
_SHORTS = f"{_T} -k a_shorts_states_the_length_and_the_style"
_CYCLING = f"{_T} -k a_cycling_shorts_states_the_length_and_the_rise"
_TRACK = f"{_T} -k a_tracksuit_states_the_top_and_the_fit"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the Bermuda shorts draw a mini length while the record states Knee Length",
        "lowerbody_rows.py",
        'params=_shp("knee", "bermuda")',
        'params=_shp("mini", "bermuda")',
        _SHORTS,
        "a shorts record states the length its drawing shows",
    ),
    (
        "the women's sweat shorts draw a denim style while the record states Sweat",
        "lowerbody_rows.py",
        'params=_shp("mini", "sweat")',
        'params=_shp("mini", "denim")',
        _SHORTS,
        "a shorts record states the style its drawing shows",
    ),
    (
        "the compression cycling shorts draw a knee length while the record states Mini",
        "lowerbody_rows.py",
        'params=_cyp("mini", "high", "no", "no")',
        'params=_cyp("knee", "high", "no", "no")',
        _CYCLING,
        "a cycling-shorts record states the length its drawing shows",
    ),
    (
        "the padded cycling shorts draw a mid rise while the record states High",
        "lowerbody_rows.py",
        'params=_cyp("mid", "high", "yes", "no")',
        'params=_cyp("mid", "mid", "yes", "no")',
        _CYCLING,
        "a cycling-shorts record states the rise its drawing shows",
    ),
    (
        "the half-zip tracksuit draws a zip top while the record states Half-Zip",
        "type_specs/tracksuit.py",
        '_drawn("half_zip", 2, "slim")',
        '_drawn("zip", 2, "slim")',
        _TRACK,
        "a tracksuit record states the top its drawing shows",
    ),
    (
        "the velour tracksuit draws a regular fit while the record states Slim",
        "type_specs/tracksuit.py",
        '_drawn("zip", 2, "slim")',
        '_drawn("zip", 2, "regular")',
        _TRACK,
        "a tracksuit record states the fit its drawing shows",
    ),
]

"""Mutation rows for the kit fit on freshly fitted parts (gen#94), out of ``mutation_check.py``.

Each row plants one defect in how ``fit_price_model.py`` reads a kit's contents on the part models
the same run fitted, and names the test that must go red. ``mutation_check.py`` turns them into
``Mutation`` rows named ``kit fit: ...`` (``--only "kit fit:"`` re-runs them). A row is
``(name, file, old, new, test, direction, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

SRC = "src/synthetic_ecommerce_data"

ROWS: list[tuple[str, str, str, str, str, str, str, str]] = [
    (
        "the kit is fitted on the parts as they stood before the run",
        "fit_price_model.py",
        "(collected, rekey_contents(recorded, fitted))",
        "(collected, recorded)",
        "tests/test_fit_price_model.py -k one_run_fits_the_kit",
        "A",
        "one run fits the kit on the parts it just fitted",
        "scripts",
    ),
    (
        "the kit is fitted before the parts",
        "fit_price_model.py",
        "key=lambda type_key: type_key in price.CONTENTS_PRICED)",
        "key=lambda type_key: type_key not in price.CONTENTS_PRICED)",
        "tests/test_fit_price_model.py -k one_run_fits_the_kit",
        "A",
        "one run fits the kit on the parts it just fitted",
        "scripts",
    ),
    (
        "the contents read the unfitted parts whatever models they are given",
        "core/price.py",
        "    source = MODELS if models is None else models",
        "    source = MODELS",
        "tests/test_fit_price_model.py -k rekeying_reads_each_kit",
        "A",
        "a kit's key is read on the refitted part models",
        SRC,
    ),
    (
        "the draw terms are taken out at the key read again",
        "fit_price_model.py",
        "            - r.draw.model.slope * r.baked_log_key",
        "            - r.draw.model.slope * r.log_key",
        "tests/test_fit_price_model.py -k leaves_the_draw_terms",
        "A",
        "the terms a kit was built with stay",
        "scripts",
    ),
    (
        "a kit is shown at the key it was built with",
        "fit_price_model.py",
        "            - old.slope * rec.baked_log_key",
        "            - old.slope * rec.log_key",
        "tests/test_fit_price_model.py -k shown_at_the_price",
        "A",
        "a kit is shown at the price of the refitted parts",
        "scripts",
    ),
    (
        "a rekeyed record forgets the key its draw holds",
        "fit_price_model.py",
        "            drawn_log_key=rec.baked_log_key,",
        "            drawn_log_key=None,",
        "tests/test_fit_price_model.py -k leaves_the_draw_terms",
        "A",
        "the terms a kit was built with stay",
        "scripts",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "kit fit"


def rows() -> list[Row]:
    return [Row(n, f, o, w, t, p, root, d) for n, f, o, w, t, d, p, root in ROWS]

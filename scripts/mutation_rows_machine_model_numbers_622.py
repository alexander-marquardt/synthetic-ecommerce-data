"""Mutation rows for the small machines' model numbers (gen#622).

Each row plants one defect in the scheme, a machine's title or the rows that take a code and names
the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``machinecode: ...`` (``--only "machinecode:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- a row's old and new text are source lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

_R = "src/synthetic_ecommerce_data/domains/retail"
_T = "tests/test_retail_machine_model_numbers_622.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a code holds the whole measure, not its steps",
        "machine_model_numbers.py",
        'd=f"{measure // k.step:02d}"',
        'd=f"{measure:02d}"',
        f'{_T} -k "builds_its_code_from_kind_variant_measure_and_year"',
        "a kettle's digits count hundreds of watts",
        _R,
    ),
    (
        "a variant no kind has decodes",
        "machine_model_numbers.py",
        "if variant is None:\n            continue",
        "if False:\n            continue",
        f'{_T} -k "no_scheme_builds_decodes_to_nothing"',
        "a code no scheme builds decodes to nothing",
        _R,
    ),
    (
        "decode reads the model year as two digits",
        "machine_model_numbers.py",
        '"year": 2000 + int(m["y"])',
        '"year": int(m["y"])',
        f'{_T} -k "builds_its_code_from_kind_variant_measure_and_year"',
        "a code decodes back to the machine's model year",
        _R,
    ),
    (
        "the title puts the model number before the series",
        "machine_model_numbers.py",
        "head = (row.brand, series, code, spec(",
        "head = (row.brand, code, series, spec(",
        f'{_T} -k "title_leads_with_brand_series_and_code"',
        "a machine title reads brand, series, model number",
        _R,
    ),
    (
        "the SKUs state no model number",
        "machine_model_numbers.py",
        "color_codes=tuple((c[0], code) for c in row.colors)",
        "color_codes=()",
        f'{_T} -k "every_sku_carries_its_rows"',
        "every SKU of a machine states its row's code",
        _R,
    ),
    (
        "a row states last year while its code says this year",
        "machine_model_numbers.py",
        '("model_year", "Model year", str(MODEL_YEAR))',
        '("model_year", "Model year", str(MODEL_YEAR - 1))',
        f'{_T} -k "decodes_to_its_own_attributes"',
        "a code decodes to its row's model year",
        _R,
    ),
    (
        "two brands share a series' lead word",
        "machine_model_numbers.py",
        '"Lanternby": {"Kettle": "Simmer Lite"}',
        '"Lanternby": {"Kettle": "Brew Lite"}',
        f'{_T} -k "series_name_and_its_lead_word_belong_to_one_brand"',
        "a series and its lead word belong to one brand",
        _R,
    ),
    (
        "the kettles and toasters are sold unnumbered",
        "appliance_rows.py",
        "*numbered((*KETTLES, *TOASTERS))",
        "*KETTLES, *TOASTERS",
        f'{_T} -k "title_leads_with_brand_series_and_code"',
        "a kettle and a toaster carry a model number",
        _R,
    ),
    (
        "the mowers and grass trimmers are sold unnumbered",
        "garden_rows.py",
        "ROWS = (*numbered((*LAWN_MOWERS, *ROBOT_MOWERS, *GRASS_TRIMMERS)), ",
        "ROWS = (*LAWN_MOWERS, *ROBOT_MOWERS, *GRASS_TRIMMERS, ",
        f'{_T} -k "title_leads_with_brand_series_and_code"',
        "a garden machine carries a model number",
        _R,
    ),
    (
        "the hedge trimmer decoys are copied from the numbered rows",
        "garden_rows.py",
        "*hedge_trimmer.ROWS, *garden_furniture_set",
        "*hedge_trimmer.SPEC.rows, *garden_furniture_set",
        f'{_T} -k "text_decoy_of_these_kinds_carries_no_code"',
        "a decoy carries no code",
        _R,
    ),
    (
        "the hedge trimmers are sold unnumbered",
        "type_specs/hedge_trimmer.py",
        "rows=numbered(ROWS),",
        "rows=ROWS,",
        f'{_T} -k "title_leads_with_brand_series_and_code"',
        "a hedge trimmer carries a model number",
        _R,
    ),
    (
        "the drill drivers are sold unnumbered",
        "type_specs/drill_driver.py",
        'rows=numbered(ROWS) + color_word_brand_rows',
        'rows=ROWS + color_word_brand_rows',
        f'{_T} -k "title_leads_with_brand_series_and_code"',
        "a drill driver carries a model number",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "machinecode"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]

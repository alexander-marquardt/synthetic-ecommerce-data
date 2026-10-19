"""Mutation rows for the Kids dresses and coats (gen#310), in their own file.

Each row plants one defect in ``kids_depth_rows.py``, ``scale.py`` or ``decoy_apparel.py`` and
names the test that must go red. ``mutation_row.discover`` finds this file by glob and the harness
names the rows ``kids_depth: ...`` (``--only "kids_depth:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- mutation text is a whole source line.

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_kids_depth_310.py"
_R = "prototypes/retail_drawings"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the girls' coats lose a third of their rows",
        "kids_depth_rows.py",
        '*_coats("Girls", "KDG", _GIRLS_COAT, 30, 24.0),',
        '*_coats("Girls", "KDG", _GIRLS_COAT, 20, 24.0),',
        f"{_T} -k floor_without_decoys",
        "Kids Girls Coats & Jackets holds its floor of thirty products",
        _R,
    ),
    (
        "the boys' coats lose a third of their rows",
        "kids_depth_rows.py",
        '*_coats("Boys", "KDB", _BOYS_COAT, 30, 24.0),',
        '*_coats("Boys", "KDB", _BOYS_COAT, 20, 24.0),',
        f"{_T} -k floor_without_decoys",
        "Kids Boys Coats & Jackets holds its floor of thirty real products",
        _R,
    ),
    (
        "the dresses are dropped from the Kids rows",
        "kids_depth_rows.py",
        "    *_dresses(),\n",
        "",
        f"{_T} -k floor_without_decoys",
        "Kids Girls Dresses holds its floor of thirty products",
        _R,
    ),
    (
        "a new dress states a crew neck whatever its description says",
        "kids_depth_rows.py",
        '(("neckline", NECKS[neck][0]),)))',
        '(("neckline", "crew"),)))',
        f"{_T} -k states_the_neckline_its_description_names",
        "a Kids dress states the neckline its description names",
        _R,
    ),
    (
        "a new dress states a short sleeve whatever its title says",
        "kids_depth_rows.py",
        '("sleeve_length", "Sleeve length", sleeve))',
        '("sleeve_length", "Sleeve length", "Short"))',
        f"{_T} -k sleeve_the_title_names",
        "the sleeve a title names is the sleeve_length value",
        _R,
    ),
    (
        "the Kids rows join the seeded derivation",
        "scale.py",
        "                | KIDS_DEPTH_IDS\n",
        "",
        f"{_T} -k left_out_of_the_derivation",
        "the template-only Kids rows stay out of scale.derivable",
        _R,
    ),
    (
        "the Kids rows become exemplars for the Dress and Coat decoys",
        "decoy_apparel.py",
        '            and d["product_id"] not in kids_depth_rows.product_ids()'
        "  # gen#310: see ``build``\n",
        "",
        f"{_T} -k take_no_text_match_decoys",
        "the Womens dresses keep the Dress decoys, the Kids leaves take none",
        _R,
    ),
    (
        "every coat states Cotton as its material",
        "kids_depth_rows.py",
        '("material", "Material", f.replace(" Blend", " blend")), ("sleeve_length", "Sleeve length", "Long"))',
        '("material", "Material", "Cotton"), ("sleeve_length", "Sleeve length", "Long"))',
        f"{_T} -k material_a_product_states",
        "the material a product states is in its title",
        _R,
    ),
    (
        "every coat states a Regular fit whatever its description says",
        "kids_depth_rows.py",
        'attrs = (("fit", "Fit", fit), ("material", "Material", f.replace(" Blend", " blend")), ("sleeve_length", "Sleeve length", "Long"))',
        'attrs = (("fit", "Fit", "Regular"), ("material", "Material", f.replace(" Blend", " blend")), ("sleeve_length", "Sleeve length", "Long"))',
        f"{_T} -k fit_a_product_states",
        "the fit a product states is the fit its description names",
        _R,
    ),
    (
        "every coat description says short sleeves while the attribute says Long",
        "kids_depth_rows.py",
        'items = ["long sleeves",',
        'items = ["short sleeves",',
        f"{_T} -k sleeve_a_description_names",
        "the sleeve a description names is the sleeve_length value",
        _R,
    ),
    (
        "a coat description drops the closing and before a pea coat's last item",
        "kids_depth_rows.py",
        'rest = ", ".join([*items, st.tail]) if " and " in st.tail else f"{\', \'.join(items)} and {st.tail}"',
        'rest = ", ".join([*items, st.tail])',
        f"{_T} -k list_ends_it_with_and",
        "a coat description with a list closes it with and",
        _R,
    ),
    (
        "the boys' coats lose two rows, still above the leaf floor",
        "kids_depth_rows.py",
        '*_coats("Boys", "KDB", _BOYS_COAT, 30, 24.0),',
        '*_coats("Boys", "KDB", _BOYS_COAT, 28, 24.0),',
        f"{_T} -k adds_thirty_rows",
        "the module adds thirty rows to each leaf",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "kids_depth"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]

"""Mutation rows for the per-type color allow-list, Material vs Finish and the template grammar
(gen#448), kept out of ``mutation_check.py``.

Each row plants one defect in a line the gen#448 change added and names the test that must go
red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``real attributes 448: ...``
(``--only "real attributes 448:"`` re-runs them). A row is
``(name, file, old, new, test, property)``.
"""

from __future__ import annotations

_T = "tests/test_retail_real_attributes_448.py"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the color completion ignores the allow-list",
        "main_colors.py",
        'fit = [r for r in styles if type_colors.permits(r["category_path"], color)]',
        "fit = list(styles)",
        f"{_T} -k a_missing_color_only_to_a_style",
        "complete() adds only a color the type comes in",
    ),
    (
        "a restricted group is asked for a color it never comes in",
        "main_colors.py",
        '                 and any(type_colors.permits(r["category_path"], c) for r in styles)]',
        "                 ]",
        f"{_T} -k a_restricted_group_is_asked",
        "the main-color gate asks a restricted type for the colors it comes in only",
    ),
    (
        "a decoy clone is picked in a color the type never comes in",
        "decoy_apparel.py",
        'if (type_colors.permits(ex["category_path"], o["color"])  # gen#448\n',
        "if (True  # gen#448\n",
        f"{_T} -k decoy_clone_picker",
        "the decoy clone picker reads the allow-list",
    ),
    (
        "Black Leather is counted as a color of its own",
        "main_colors.py",
        'return {type_colors.base_color(c["color"]) for r in styles for c in r["color_options"]}',
        'return {c["color"] for r in styles for c in r["color_options"]}',
        f"{_T} -k a_color_with_a_material_is_that_color",
        "a color with its material is that color",
    ),
    (
        "a finish stays in the Material attribute",
        "mens_depth_rows.py",
        "    if key in type_colors.CARRIED_AS:\n",
        "    if False:\n",
        f"{_T} -k material_values",
        "Material holds a cloth, never a finish or a pattern",
    ),
    (
        "a sourcing claim stays in the Material attribute",
        "mens_depth_rows.py",
        "    if key in type_colors.MATERIAL_OF:\n",
        "    if False:\n",
        f"{_T} -k material_values",
        "Recycled is a sourcing claim, carried inside a true material",
    ),
    (
        "a plural noun takes an article",
        "mens_depth_rows.py",
        'return word.endswith("s") and not word.endswith(("ss", "us"))',
        "return False",
        f"{_T} -k plural_noun_takes_no_article",
        "no 'A navy elasticated trousers'",
    ),
    (
        "the class 4 description loses the hyphen of x-free",
        "mens_depth_rows.py",
        "that {'are' if _plural(n4) else 'is'} {f.lower()}: made in ",
        "that {'are' if _plural(n4) else 'is'} {f.lower().replace('-', ', ')}: made in ",
        f"{_T} -k wool_free",
        "'wool-free: made in cotton' reads as a sentence",
    ),
    (
        "the description noun is the kind's, not the leaf's",
        "mens_depth_rows.py",
        "noun = detail.lower() if kind.item else (leaf.noun or kind.noun).lower()",
        "noun = detail.lower() if kind.item else kind.noun.lower()",
        f"{_T} -k description_noun_is_the_leaf_noun",
        "formal trousers are described as formal trousers, not chinos",
    ),
    (
        "shoe polish is filed in another department than the kit beside it",
        "decoy_product_words.py",
        '    "polish": Kind(\n        "Footwear",',
        '    "polish": Kind(\n        "Home",',
        f"{_T} -k shoe_care_is_one_node",
        "one category path has one department",
    ),
]

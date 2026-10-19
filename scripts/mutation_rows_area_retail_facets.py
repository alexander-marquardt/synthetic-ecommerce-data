"""Mutation rows for retail facets and loaders: scent depth, the Leather Look guard, jean and bra facets, the Combined loader.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- retail: scent depth for "lemon" and "honey" (gen#154) ----
    *(
        Mutation(f"scent depth: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a depth family is sized against the whole weight, so every core budget moves",
                "grocery.py",
                "sum(f.weight for f in FAMILIES if not f.depth)",
                "sum(f.weight for f in FAMILIES)",
                "tests/test_grocery_scent_depth_154.py -k core_styles_do_not_move",
                "adding a scent family leaves the core grocery styles as built",
            ),
            (
                "a floor cleaner is too small a family to show a lemon",
                "grocery_rows.py",
                '_HOME_BRANDS, 0.016, axis="scent",\n           department="Cleaning & Janitorial", noun="concentrated',
                '_HOME_BRANDS, 0.001, axis="scent",\n           department="Cleaning & Janitorial", noun="concentrated',
                "tests/test_grocery_scent_depth_154.py -k lemon_is_a_scent",
                "lemon is a scent in dozens of SKUs of each type",
            ),
            (
                "a dish soap holds its scent as a flavor",
                "grocery_rows.py",
                '_HOME_SCENTS, _HOME_BRANDS, 0.01, axis="scent",\n           department="Cleaning & Janitorial", noun="washing-up',
                '_HOME_SCENTS, _HOME_BRANDS, 0.01, axis="flavor",\n           department="Cleaning & Janitorial", noun="washing-up',
                "tests/test_grocery_scent_depth_154.py -k told_apart_by_attribute",
                "a scented SKU carries scent, never flavor",
            ),
            (
                "a depth description falls back to the multi-surface spray",
                "grocery.py",
                "noun = fam.noun or (",
                "noun = (",
                "tests/test_grocery_scent_depth_154.py -k describes_its_own_product",
                "a scent style describes its own product",
            ),
        ]
    ),
    # ---- the Leather Look guard reads both spellings (gen#291) ----
    Mutation(
        "the Leather Look guard reads only the hyphen",
        "tests/test_retail_facet_leaves.py",
        'LEATHER_LOOK = re.compile(r"leather[\\s-]*look", re.IGNORECASE)',
        'LEATHER_LOOK = re.compile(r"leather-look", re.IGNORECASE)',
        "tests/test_retail_facet_leaves.py -k leather_look_guard_reads_both_spellings",
        "",
        "both spellings are read",
        root=".",
    ),
    # ---- retail: a jean's fit and a bra's style are facets, not leaves ----
    *(
        Mutation(f"facet leaves: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a jean keeps its fit leaf",
                "facet_leaves.py",
                "        return path[:-1]\n    if product_type",
                "        return path\n    if product_type",
                "tests/test_retail_facet_leaves.py -k end_at_their_kind_node",
                "a fit is not a category leaf",
            ),
            (
                "a purpose bra loses its node",
                "facet_leaves.py",
                "return path if path[-1] in PURPOSE_BRAS else path[:-1]",
                "return path[:-1]",
                "tests/test_retail_facet_leaves.py -k purpose_nodes_are_the_only_children",
                "the purpose nodes stay",
            ),
            (
                "a title's own bra facet is dropped",
                "facet_leaves.py",
                "for key, value in stated_bra_facets(rec[\"title\"])",
                "for key, value in []",
                "tests/test_retail_facet_leaves.py -k every_value_its_title_names",
                "a bra carries what its title says",
            ),
            (
                "leg_style is not folded into leg_fit",
                "facet_leaves.py",
                '        fit = fit or LEG_STYLE_FITS.get(have.get("leg_style", ""))\n',
                "",
                "tests/test_retail_facet_leaves.py -k every_jean_has_a_leg_fit",
                "every jean has a leg_fit",
            ),
            (
                "wide trousers are written Wide",
                "facet_leaves.py",
                '    "wide": "Wide Leg",',
                '    "wide": "Wide",',
                "tests/test_retail_facet_leaves.py -k keeps_the_fit_its_old_leaf_named",
                "the fit is the old leaf's",
            ),
            (
                "bra_style stays beside the split facets",
                "facet_leaves.py",
                'return out, {"bra_style", "fabric"}',
                'return out, {"fabric"}',
                "tests/test_retail_facet_leaves.py -k bra_style_and_leg_style_are_gone",
                "bra_style is gone",
            ),
            (
                "the fibre-content detail is dropped",
                "export.py",
                "        doc[\"fibre_content\"] = blend\n",
                "        pass\n",
                "tests/test_retail_facet_leaves.py -k blend_is_a_detail",
                "the blend is a detail",
            ),
            (
                "a wool material is not also the wool fabric",
                "facet_leaves.py",
                "    if \"fabric\" in have or not is_textile(rec):",
                "    if True:",
                "tests/test_retail_facet_leaves.py -k material_that_names_wool",
                "a named fibre is a fabric",
            ),
            (
                "a leather skirt is faux leather",
                "lowerbody_rows.py",
                '_sk("Pencil", "Mini", "Leather", "Zip", "Polyester")',
                '_sk("Pencil", "Mini", "Faux Leather", "Zip", "Polyester")',
                "tests/test_retail_facet_leaves.py -k coverage_review_value",
                "leather is a fabric value",
            ),
            (
                "a fabric move ignores the product type",
                "facet_leaves.py",
                "    return TYPED_FABRIC_MOVES.get((product_type, value)) or FABRIC_MOVES.get(value)",
                "    return next((m for (_, v), m in TYPED_FABRIC_MOVES.items() if v == value), None)"
                " or FABRIC_MOVES.get(value)",
                "tests/test_retail_facet_leaves.py -k fabric_move_is_keyed_by_product_type",
                "a typed move reads the type",
            ),
            (
                "the laptop backpack is titled Leather Look again",
                "accessory_rows.py",
                '"Faux Leather Laptop Backpack"',
                '"Leather Look Laptop Backpack"',
                "tests/test_retail_facet_leaves.py -k never_titled_leather_look",
                "a fabric has one name in a title",
            ),
            (
                "a retail message spells center the British way",
                "house_styles.py",
                'raise ValueError("a band sits at the top or bottom center")',
                'raise ValueError("a band sits at the top or bottom centre")',
                "tests/test_us_spelling.py -k retail_source_spells_center",
                "center is spelt one way",
            ),
            (
                "one bra spells Lightly Lined with a hyphen",
                "facet_leaves.py",
                '"Spacer Cup Bras": ("T-Shirt", "Lightly Lined", None, None),',
                '"Spacer Cup Bras": ("T-Shirt", "Lightly-Lined", None, None),',
                "tests/test_retail_facet_leaves.py -k differ_only_in_case_or_hyphenation",
                "one spelling per facet value",
            ),
            (
                "a convertible bra is only Multiway",
                "facet_leaves.py",
                '("Multiway", "Halterneck", "Cross Back")',
                '"Multiway"',
                "tests/test_retail_audience.py -k cleaning_root",
                "no text contradicts a bra facet",
            ),
            (
                "a cropped balloon jean is not Cropped",
                "facet_leaves.py",
                "            fits.append(CROPPED)\n",
                "            pass\n",
                "tests/test_retail_facet_leaves.py -k text_says_cropped",
                "a jean whose text says cropped is cropped",
            ),
        ]
    ),
    # ---- retail: the Combined loader takes every authored SKU (gen#279) ----
    # Every name starts "combined loader:", so `--only "combined loader:"` re-runs them.
    *(
        Mutation(f"combined loader: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a crossbody bag is sold in a Mini size, which is no size system",
                "accessory_rows.py",
                '_sizes(("Small", 28.0), ("Medium", 34.0))',
                '_sizes(("Mini", 28.0), ("Small", 34.0))',
                "tests/test_retail_combined_loader_279.py -k has_a_size_the_combined_loader_refuses",
                "every size is in a size system the loader declares",
            ),
            (
                "a skirt's fit axis is the bare length the loader renames onto garment_length",
                "lowerbody_rows.py",
                'axis_key="fit_length", axis=_legs()',
                'axis_key="length", axis=_legs()',
                "tests/test_retail_combined_loader_279.py -k writes_a_renamed_key_twice",
                "no SKU writes a renamed key twice",
            ),
        ]
    ),
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: retail facets"


def rows() -> list[Mutation]:
    return MUTATIONS

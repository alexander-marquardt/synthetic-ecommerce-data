"""Mutations that plant a defect in the retail prototype (``prototypes/retail_drawings``) and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- retail: scent depth for "lemon" and "honey" (gen#154) ----
    *(
        Mutation(
            f"scent depth: {name}",
            file,
            old,
            new,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, file, old, new, test, prop in [
            (
                "a depth family is sized against the whole weight, so every core budget moves",
                "grocery.py",
                "sum(f.weight for f in FAMILIES if skus > TARGET or not f.depth)",
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
    # ---- retail: a jean's fit and a bra's style are facets, not leaves ----
    *(
        Mutation(
            f"facet leaves: {name}",
            file,
            old,
            new,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
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
                'for key, value in stated_bra_facets(rec["title"])',
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
                '        doc["fibre_content"] = blend\n',
                "        pass\n",
                "tests/test_retail_facet_leaves.py -k blend_is_a_detail",
                "the blend is a detail",
            ),
            (
                "a wool material is not also the wool fabric",
                "facet_leaves.py",
                '    if "fabric" in have or not is_textile(rec):',
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
        Mutation(
            f"combined loader: {name}",
            file,
            old,
            new,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
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
    # ---- retail: text-match decoys (gen#294) ----
    *(
        Mutation(
            f"text-match decoys: {name}",
            file,
            old,
            new,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, file, old, new, test, prop in [
            (
                "a decoy is color-completed",
                "main_colors.py",
                ' and r["product_id"] not in _PLANTED',
                "",
                "tests/test_retail_text_match_decoys_294.py -k never_copied_or_color_completed",
                "no color completion gives a decoy the query's color",
            ),
            (
                "a decoy is copied by the derivation",
                "scale.py",
                "| SPEC_IDS | decoy_rows.IDS | COLORWORD_IDS\n",
                "| SPEC_IDS | COLORWORD_IDS\n",
                "tests/test_retail_text_match_decoys_294.py -k never_copied_or_color_completed",
                "a decoy stays a template",
            ),
            (
                "a decoy sells nothing, so it cannot compete",
                "decoy_rows.py",
                "one(color, self.sold)",
                "one(color, 1)",
                "tests/test_retail_text_match_decoys_294.py -k decoys_lead_the_top_10",
                "the decoys reach the baseline top 10",
            ),
            (
                "a class 7 decoy loses its ingredients",
                "decoy_rows.py",
                "        if row.ingredients:\n",
                "        if False:\n",
                "tests/test_retail_text_match_decoys_294.py -k hold_the_word_only_in_the_ingredients",
                "the word is on the label",
            ),
            (
                "a part decoy gets the query's color in its color field",
                "decoy_rows.py",
                '"A blue velvet sofa finished with red piping along the seams.", "Blue", 1',
                '"A blue velvet sofa finished with red piping along the seams.", "Red", 1',
                "tests/test_retail_text_match_decoys_294.py -k decoy_is_a_hit",
                "a decoy's fields tell the truth",
            ),
            (
                "the docs table is not the generated one",
                "decoy_rows.py",
                '"true hit" if d.true_hit else "decoy"',
                '"decoy" if d.true_hit else "true hit"',
                "tests/test_retail_text_match_decoys_294.py -k docs_table_is_generated",
                "the docs table is generated",
            ),
            (
                "a guard loses its color word",
                "decoy_rows.py",
                '"Green Tea, 40 Bags"',
                '"Tea, 40 Bags"',
                "tests/test_retail_text_match_decoys_294.py -k guard_holds_every_word",
                "a guard holds its query's words and ranks first",
            ),
            (
                "a decoy's ingredient has no base row",
                "grocery_ingredients.py",
                "lentils: lentil\n",
                "",
                "tests/test_grocery_ingredient_base_295.py -k scale_build_with_the_decoys",
                "every label of the scale build has a base row",
            ),
        ]
    ),
    # ---- retail: the steak plate, board and weight carry a material, never derived (gen#268) ----
    *(
        Mutation(
            f"steak ware: {name}",
            file,
            old,
            new_,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, file, old, new_, test, prop in [
            (
                "the steak weight loses its material",
                "distractor_rows.py",
                '                 ("material", "Material", "Cast Iron"))),',
                "                 )),",
                "tests/test_retail_distractors.py -k carry_a_material_like_their_siblings",
                "the steak weight carries a material like the other utensils",
            ),
            (
                "the steak board loses its material",
                "distractor_rows.py",
                '          extra=(("material", "Material", "Wood"),),\n',
                "",
                "tests/test_retail_distractors.py -k carry_a_material_like_their_siblings",
                "the steak board carries the material of the other boards",
            ),
            (
                "the steak ware is copied by the derivation",
                "scale.py",
                " | STEAK_WARE_IDS)",
                ")",
                "tests/test_retail_distractors.py -k steak_ware_is_never_derived",
                "the steak plate, board and weight stay templates",
            ),
        ]
    ),
    # ---- retail: school uniform, the record names the drawing it draws (gen#205) ----
    *(
        Mutation(
            f"school uniform: {name}",
            "school_rows.py",
            old,
            new_,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, old, new_, test, prop in [
            (
                "every skirt is drawn at knee length",
                '("length", length.lower())))  # fmt: skip',
                '("length", "knee")))  # fmt: skip',
                "tests/test_retail_school_205.py -k a_skirt_draws_the_folds",
                "a skirt's drawing carries the length its record states",
            ),
            (
                "every pinafore is drawn as a pinafore",
                '(("style", style.lower().replace(" ", "_")),))  # fmt: skip',
                '(("style", "pinafore"),))  # fmt: skip',
                "tests/test_retail_school_205.py -k a_pinafore_row_draws",
                "a pinafore's drawing carries the style its record states",
            ),
        ]
    ),
    # ---- retail: text-match decoys on every clothing type (gen#311) ----
    *(
        Mutation(
            f"apparel decoys: {name}",
            file,
            old,
            new,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, file, old, new, test, prop in [
            (
                "an apparel decoy is color-completed",
                "main_colors.py",
                "decoy_rows.IDS | decoy_apparel.IDS",
                "decoy_rows.IDS",
                "tests/test_retail_apparel_decoys_311.py -k never_copied_or_color_completed",
                "no color completion gives an apparel decoy the query's color",
            ),
            (
                "an apparel decoy is copied by the derivation",
                "scale.py",
                "                | decoy_apparel.IDS | decoy_product_words.IDS | STEAK_WARE_IDS)",
                "                | decoy_product_words.IDS | STEAK_WARE_IDS)",
                "tests/test_retail_apparel_decoys_311.py -k never_copied_or_color_completed",
                "an apparel decoy stays a template",
            ),
            (
                "a class 4 decoy names a material the style holds",
                "decoy_apparel.py",
                "            if word not in held:\n",
                "            if True:\n",
                "tests/test_retail_apparel_decoys_311.py -k fields_contradict",
                "the absent material is absent from every field",
            ),
            (
                "a class 6 category word is one the path holds",
                "decoy_apparel.py",
                "            if not path_has(name.split()[0].lower()):\n",
                "            if True:\n",
                "tests/test_retail_apparel_decoys_311.py -k fields_contradict",
                "a category-word range is not the product's own category",
            ),
            (
                "the decoy exemption from the text check is removed",
                "scale.py",
                "DECOY_IDS = (decoy_rows.IDS | decoy_apparel.IDS | garden_rows.decoy_ids()\n             | decor_rows.decoy_ids() | neckline_rows.decoy_ids())\n",
                "DECOY_IDS = frozenset()\n",
                "tests/test_retail_apparel_decoys_311.py -k misleading_color",
                "a decoy naming only another color passes the standard by its id",
            ),
            (
                "the decoy exemption widens to every id",
                "scale.py",
                "DECOY_IDS = (decoy_rows.IDS | decoy_apparel.IDS | garden_rows.decoy_ids()\n             | decor_rows.decoy_ids() | neckline_rows.decoy_ids())\n",
                'DECOY_IDS = type("All", (frozenset,), {"__contains__": lambda self, x: True})()\n',
                "tests/test_retail_apparel_decoys_311.py -k two_tables",
                "no real product is exempt from the text check",
            ),
            (
                "a part is drawn without its color",
                "details.py",
                '<path d="{d}" fill="{color}" stroke="{INK}" stroke-width="1.6"',
                '<path d="{d}" fill="#ffffff" stroke="{INK}" stroke-width="1.6"',
                "tests/test_retail_apparel_decoys_311.py -k named_part_is_drawn",
                "the named part carries the named color",
            ),
            (
                "a hem band moves to the top of the garment",
                "details.py",
                'TORSO_HEM = band((0.0, 0.89, 1.0, 1.0), "torso")',
                'TORSO_HEM = band((0.0, 0.0, 1.0, 0.11), "torso")',
                "tests/test_retail_apparel_decoys_311.py -k sits_where_the_part_sits",
                "a hem is drawn at the bottom of the garment",
            ),
            (
                "a sole is drawn across the shoe's upper",
                "details.py",
                '"shoe": {"sole": marked("sole")},',
                '"shoe": {"sole": band((0.0, 0.62, 1.0, 0.92), "all")},',
                "tests/test_retail_apparel_decoys_311.py -k sits_where_the_part_sits",
                "a sole is drawn on the kit's own sole path",
            ),
            (
                "a hem band paints the sleeve cuffs",
                "details.py",
                'TORSO_HEM = band((0.0, 0.89, 1.0, 1.0), "torso")',
                "TORSO_HEM = band((0.0, 0.89, 1.0, 1.0))",
                "tests/test_retail_apparel_decoys_311.py -k torsos_and_does_not_color",
                "a sleeve's cuff is not part of the hem",
            ),
        ]
    ),
    # ---- retail: product-word decoys (gen#326) ----
    *(
        Mutation(
            f"product-word decoys: {name}",
            file,
            old,
            new,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, file, old, new, test, prop in [
            (
                "a class-8 decoy is color-completed",
                "main_colors.py",
                'r["product_id"] not in _PLANTED',
                'r["product_id"] not in decoy_rows.IDS',
                "tests/test_retail_product_word_decoys_326.py -k templates_no_derived",
                "no color completion gives a decoy the query's color",
            ),
            (
                "a class-8 decoy is copied by the derivation",
                "scale.py",
                "| decoy_apparel.IDS | decoy_product_words.IDS | STEAK_WARE_IDS)",
                "| decoy_apparel.IDS | STEAK_WARE_IDS)",
                "tests/test_retail_product_word_decoys_326.py -k templates_no_derived",
                "a decoy stays a template",
            ),
            (
                "a class-8 decoy sells little, so it cannot lead",
                "decoy_product_words.py",
                "    sold: int = 2000",
                "    sold: int = 1",
                "tests/test_retail_product_word_decoys_326.py -k baseline_top_10",
                "the decoys reach the baseline top 10",
            ),
            (
                "a decoy's detail color is dropped from its drawing",
                "decoy_product_words.py",
                "params = k.params + (((self.detail_param, COLORS[self.detail]),) if self.detail else ())",
                "params = k.params",
                "tests/test_retail_product_word_decoys_326.py -k drawing_shows",
                "the drawing renders the named detail",
            ),
            (
                "the docs table drops the policy column",
                "decoy_product_words.py",
                'f"| {r.policy} |"',
                'f"| |"',
                "tests/test_retail_product_word_decoys_326.py -k docs_table",
                "the docs table lists each row with its policy",
            ),
        ]
    ),
    Mutation(
        "product-word decoys: the detail-color rows lose their exemption",
        "scale.py",
        "    | decoy_product_words.TEXT_EXEMPT",
        "",
        "tests/test_retail_scale.py -k 20k_build_meets_the_output_standard",
        "A",
        "a class-8 row that names a detail color on purpose passes the text check by its id",
        root="prototypes/retail_drawings",
    ),
    Mutation(
        "product-word decoys: the standard's retail catalog test loses the exempt ids",
        "scale.py",
        "    | decoy_product_words.TEXT_EXEMPT",
        "",
        "tests/test_merchandising_score_182.py -k retail_every_product_carries_it",
        "A",
        "the full retail catalog passes the standard with the class-8 detail-color ids exempt",
        root="prototypes/retail_drawings",
    ),
    # ---- retail: color-word brands beyond clothing (gen#312) ----
    # Every name starts "color-word brands:", so `--only "color-word brands:"` re-runs them.
    *(
        Mutation(f"color-word brands: {name}", file, old, new, test, "", prop, root=root)
        for name, file, old, new, test, prop, root in [
            (
                "the black-named drill is really black",
                "color_word_brand_rows.py",
                '_in("#e8741e", "#2a2a2e", "Orange"),\n        (*_a1("battery_type", "Battery type", "Lithium-Ion"), *_volts(18)),',
                '_in("#2a2a2e", "#e8741e", "Black"),\n        (*_a1("battery_type", "Battery type", "Lithium-Ion"), *_volts(18)),',
                "tests/test_color_word_brands_312.py -k test_no_attribute_states_the_color_word",
                "the color attribute differs from the color word",
                "prototypes/retail_drawings",
            ),
            (
                "the completer is not told to skip the decoys",
                "scale.py",
                "| COLORWORD_IDS | garden_rows.decoy_ids()",
                "| garden_rows.decoy_ids()",
                "tests/test_color_word_brands_312.py -k test_a_built_decoy_offers_exactly_its_one_true_color",
                "a decoy offers more than its one true color",
                "prototypes/retail_drawings",
            ),
            (
                "a brand's wordmark is set in capitals, not as the brand field",
                "color_word_brand_styles.py",
                '"humanist", 700, "title",     0.5)',
                '"humanist", 700, "caps",      0.5)',
                "tests/test_color_word_brands_312.py -k test_a_drawing_lockup_text_equals_the_brand_field",
                "the lockup text equals the brand",
                "prototypes/retail_drawings",
            ),
            (
                "a title runs past five words",
                "color_word_brand_rows.py",
                '"Green Harrow Sweetcorn Kernels"',
                '"Green Harrow Golden Sweetcorn Kernels in Water"',
                "tests/test_color_word_brands_312.py -k test_the_color_word_sits_in_a_short_title",
                "the color word sits in a short title",
                "prototypes/retail_drawings",
            ),
            (
                "the garden loses its bulbs",
                "color_word_brand_rows.py",
                '_TULIP = ("Garden", "Bulbs", "Tulip Bulbs")',
                '_TULIP = ("Home", "Bulbs", "Tulip Bulbs")',
                "tests/test_color_word_brands_312.py -k test_each_department_has_at_least_three_decoys",
                "each department has three decoys",
                "prototypes/retail_drawings",
            ),
            (
                "the standard reads the brand as a claim",
                "core/standard.py",
                'values.add(str(doc["brand"]))',
                "pass",
                "tests/test_color_word_brands_312.py -k test_the_standard_reads_a_brand_as_a_name",
                "a brand is a name, not a claim",
                "src/synthetic_ecommerce_data",
            ),
        ]
    ),
    # ---- retail: the product types the failure classes need (gen#329) ----
    # Every name starts "needs rows:", so `--only "needs rows:"` re-runs them.
    *(
        Mutation(
            f"needs rows: {name}", file, old, new, test, "", prop, root="prototypes/retail_drawings"
        )
        for name, file, old, new, test, prop in [
            (
                "the derivation copies the needs rows as styles",
                "scale.py",
                "| DECOR_IDS | NIKE_IDS\n                | NEEDS_IDS | CUPS_PLURAL_IDS\n",
                "| DECOR_IDS | NIKE_IDS\n                | CUPS_PLURAL_IDS\n",
                "tests/test_retail_elasticated_waist_329.py -k every_row_is_a_template",
                "the needs rows stay templates",
            ),
            (
                "the elastic-waist decoys are filed under cargo trousers",
                "needs_rows.py",
                'spread=(("Mens", "Trousers", "Elasticated Waist Trousers"),),',
                "spread=(),",
                "tests/test_retail_elasticated_waist_329.py -k decoy_is_a_mens_trouser_true_in_its_fields",
                "a decoy sits in the leaf its title and fields name",
            ),
            (
                "a product of the leaf states a drawstring waist, not an elastic one",
                "needs_rows.py",
                'waist="Elastic", extra_price=2.0)',
                'waist="Drawstring", extra_price=2.0)',
                "tests/test_retail_elasticated_waist_329.py -k every_product_in_the_leaf_states_an_elastic_waist",
                "the attribute says what the title says",
            ),
            (
                "the leaf is drawn with a plain waistband",
                "mens_depth_rows.py",
                'params += (("waist", "elasticated"),)',
                "params += ()",
                "tests/test_retail_elasticated_waist_329.py -k drawn_with_an_elasticated_waist",
                "the picture shows the gathered band",
            ),
            (
                "a class 4 decoy states an elastic waist, so it is no near miss",
                "needs_rows.py",
                'absent_attrs=(m._a("waist_type", "Waist type", "Belted"),)',
                'absent_attrs=(m._a("waist_type", "Waist type", "Elastic"),)',
                "tests/test_retail_elasticated_waist_329.py -k class_4_names_an_elastic",
                "the word elasticated on a product whose waist is not elastic",
            ),
            (
                "a decoy class is cut to two decoys",
                "mens_depth_rows.py",
                "        for i in range(3):\n            w = _MAIN_WORDS",
                "        for i in range(2):\n            w = _MAIN_WORDS",
                "tests/test_retail_elasticated_waist_329.py -k three_decoys_of_each_class",
                "three decoys of each of the seven classes",
            ),
        ]
    ),
    # ---- retail: Nike is a real brand, text only (gen#341) ----
    *(
        Mutation(f"nike: {name}", file, old, new, test, "", prop, root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a real brand draws its logo",
                "house_styles.py",
                "    if style.mark == NO_MARK:  # a real brand",
                "    if False:  # a real brand",
                "tests/test_retail_nike_341.py -k carries_no_logo_mark_or_name",
                "a real brand is text only: no drawing carries its logo",
            ),
            (
                "Nike leaves the allow-list",
                "real_brands.py",
                'ALLOWED: tuple[str, ...] = ("Nike",)',
                "ALLOWED: tuple[str, ...] = ()",
                "tests/test_retail_nike_341.py -k guard_allows_nike",
                "the guard allows the ruled-in brand",
            ),
            (
                "the guard stops refusing Puma",
                "real_brands.py",
                '"Adidas", "Puma", ',
                '"Adidas", ',
                "tests/test_retail_nike_341.py -k refuses_any_other_real_brand",
                "the guard refuses every other real brand",
            ),
            (
                "the guard refuses Nike too",
                "real_brands.py",
                '"Adidas", "Puma", ',
                '"Nike", "Adidas", "Puma", ',
                "tests/test_retail_nike_341.py -k allow_list_and_the_refused_list",
                "the allow-list and the refused list do not overlap",
            ),
            (
                "an apparel decoy may clone a Nike style",
                "decoy_apparel.py",
                '            and d["brand"] not in real_brands.ALLOWED',
                "            and True",
                "tests/test_retail_nike_341.py -k every_nike_title_names_it",
                "a real brand is never cloned into a decoy that hides its name",
            ),
            (
                "a Nike style enters the seeded derivation",
                "scale.py",
                "| GARDEN_IDS | DECOR_IDS | NIKE_IDS",
                "| GARDEN_IDS | DECOR_IDS",
                "tests/test_retail_nike_341.py -k leave_the_derivation",
                "the Nike rows are templates only",
            ),
            (
                "Nike leaves the owner table",
                "class_model.py",
                '"Nike")  # fmt: skip',
                '"Coat Crake")  # fmt: skip',
                "tests/test_retail_nike_341.py -k third_party_brand",
                "Nike is another house's make",
            ),
        ]
    ),
    # ---- retail: a garden decoy title names a color only when its drawing shows it (gen#203, the #311 ruling) ----
    # Every name starts "garden decoy color:", so `--only "garden decoy color:"` re-runs them.
    *(
        Mutation(
            f"garden decoy color: {name}",
            file,
            old,
            new,
            test,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, file, old, new, test, prop in [
            (
                "a named part is drawn in its default color",
                "kit_garden.py",
                "        return self.hex if self.part == name else default",
                "        return default",
                "tests/test_retail_garden_203.py -k a_decoy_title_names_a_color_only_when_the_drawing_shows_it",
                "a title's color is drawn on its part",
            ),
            (
                "a named part is not marked",
                "kit_garden.py",
                '        return el.replace("/>", f\' data-part="{name}"/>\', 1) if self.part == name else el',
                "        return el",
                "tests/test_retail_garden_203.py -k a_decoy_title_names_a_color_only_when_the_drawing_shows_it",
                "a title's color is drawn on its part",
            ),
            (
                "every part takes the color, not only the named one",
                "kit_garden.py",
                "        return self.hex if self.part == name else default",
                "        return self.hex if self.part else default",
                "tests/test_retail_garden_203.py -k a_decoy_title_names_a_color_only_when_the_drawing_shows_it",
                "the named color is on the named part and nothing else",
            ),
            (
                "a short title's color is drawn in another color",
                "garden_rows.py",
                '        return (("part", kit_garden.PARTS[shape][0]), ("part_color", m.group(1).lower()))',
                '        return (("part", kit_garden.PARTS[shape][0]), ("part_color", "red"))',
                "tests/test_retail_garden_203.py -k a_decoy_title_names_a_color_only_when_the_drawing_shows_it",
                "a title's color is drawn on its part",
            ),
            (
                "a secondary title draws no part",
                "garden_rows.py",
                '        return (("part", m.group(2).lower().replace(" ", "-")), ("part_color", m.group(1).lower()))',
                "        return ()",
                "tests/test_retail_garden_203.py -k a_decoy_title_names_a_color_only_when_the_drawing_shows_it",
                "a title's color is drawn on its part",
            ),
            (
                "a short-title decoy loses its color word",
                "garden_rows.py",
                '"Black Pearl Robot Mower", "ROBWIR", "white"',
                '"Violet Pearl Robot Mower", "ROBWIR", "white"',
                "tests/test_retail_garden_203.py -k decoys_that_name_a_color",
                "twelve secondary and eight short-title decoys name a color",
            ),
        ]
    ),
    # ---- retail: promotion replaces the boolean offer (gen#189) ----
    *(
        Mutation(
            f"promotion: {name}", file, old, new, test, "", prop, root="prototypes/retail_drawings"
        )
        for name, file, old, new, test, prop in [
            (
                "a campaign replaces On sale",
                "promotion.py",
                "return [ON_SALE, CAMPAIGN] if in_campaign",
                "return [CAMPAIGN] if in_campaign",
                "tests/test_retail_promotion_189.py -k campaign_exists_and_every_carrier",
                "a campaign value never replaces On sale",
            ),
            (
                "every reduced product is in the campaign",
                "promotion.py",
                "CAMPAIGN_ONE_IN = 3",
                "CAMPAIGN_ONE_IN = 1",
                "tests/test_retail_promotion_189.py -k campaign_exists_and_every_carrier",
                "the campaign is a subset of the reduced products",
            ),
            (
                "no product is in the campaign",
                "promotion.py",
                "% CAMPAIGN_ONE_IN == 0",
                "% CAMPAIGN_ONE_IN == 3",
                "tests/test_retail_promotion_189.py -k campaign_exists_and_every_carrier",
                "at least one campaign value exists",
            ),
            (
                "a derived style keeps the promotion of a was-price it lost",
                "scale.py",
                '    rec.pop("promotion", None)  # it follows',
                "    # it follows",
                "tests/test_retail_promotion_189.py -k an_unreduced_document_has_no_promotion_key",
                "no was-price, no promotion key",
            ),
            (
                "a decoy clone keeps the promotion of a was-price it lost",
                "decoy_apparel.py",
                '"discount_pct", "promotion", "pattern",',
                '"discount_pct", "pattern",',
                "tests/test_retail_promotion_189.py -k a_decoy_clone_of_a_reduced_style",
                "no was-price, no promotion key",
            ),
            (
                "a footwear sale loses On sale",
                "footwear_rows.py",
                '            rec["promotion"] = promotion_values(f"FTW-{self.code}")',
                '            rec["promotion"] = []',
                "tests/test_retail_promotion_189.py -k every_reduced_document_carries_on_sale",
                "every reduced product is On sale",
            ),
            (
                "a class-row sale loses On sale",
                "class_model.py",
                '            rec["promotion"] = promotion_values(f"PLT-{self.code}")',
                '            rec["promotion"] = []',
                "tests/test_retail_promotion_189.py -k class_docs_and_their_mapping",
                "every reduced class doc is On sale",
            ),
            (
                "the facet label is Offer again",
                "export.py",
                '"promotion": ("promotion", "Sale", None),',
                '"promotion": ("promotion", "Offer", None),',
                "tests/test_retail_promotion_189.py -k labelled_sale",
                "the shopper label is Sale",
            ),
            (
                "a class doc keeps the boolean offer in its mapping",
                "real_classes.py",
                'BOOLEANS = ("online_only", "trending")',
                'BOOLEANS = ("offer", "online_only", "trending")',
                "tests/test_retail_promotion_189.py -k class_docs_and_their_mapping",
                "offer is gone from the mapping",
            ),
            (
                "the class mapping loses the promotion keyword",
                "real_classes.py",
                '"promotion", "category_path_joined"',
                '"category_path_joined"',
                "tests/test_retail_promotion_189.py -k class_docs_and_their_mapping",
                "promotion is a keyword",
            ),
        ]
    ),
    # ---- retail: a drawing param may be named shape (gen#259) ----
    *(
        Mutation(
            f"drawing params: {name}",
            "variants.py",
            old,
            new,
            tests,
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, old, new, tests, prop in [
            (
                "the drawing's first parameter is named shape again",
                "def drawing(shape_name: str, color: Color, label: str | None = None, **params)"
                " -> dict:",
                "def drawing(shape: str, color: Color, label: str | None = None, **params)"
                " -> dict:\n    shape_name = shape",
                (
                    "tests/test_retail_lowerbody_206.py -k takes_a_param_named_shape",
                    "tests/test_retail_lowerbody_206.py -k without_stripping_its_shape_param",
                ),
                "a param named shape reaches the drawing's params",
            ),
        ]
    ),
    # ---- retail: a jigsaw's finished size is two CMT entries (gen#261) ----
    *(
        Mutation(
            f"jigsaw size: {name}",
            "toys_rows.py",
            old,
            new,
            "tests/test_retail_toys_201.py -k jigsaws_finished_size",
            "",
            prop,
            root="prototypes/retail_drawings",
        )
        for name, old, new, prop in [
            (
                "the length is no longer in centimeters",
                'return (key, name, str(v), "CMT", float(v * 10))  # canonical length is millimeters\n\n\ndef _jig',
                'return (key, name, str(v), "MMT", float(v * 10))  # canonical length is millimeters\n\n\ndef _jig',
                "a size carries its unit code",
            ),
            (
                "the canonical value is not in millimeters",
                'return (key, name, str(v), "CMT", float(v * 10))  # canonical length is millimeters\n\n\ndef _jig',
                'return (key, name, str(v), "CMT", float(v))  # canonical length is millimeters\n\n\ndef _jig',
                "a size carries its canonical value",
            ),
            (
                "the width entry is dropped",
                '_cm("item_length", "Item length", length), _cm("item_width", "Item width", width),',
                '_cm("item_length", "Item length", length),',
                "length and width are both entries",
            ),
            (
                "the width entry repeats the length",
                '_cm("item_width", "Item width", width),',
                '_cm("item_width", "Item width", length),',
                "the width entry is the width",
            ),
            (
                "the text says another size than the entries",
                'f"{length} x {width} cm"',
                'f"{width} x {width} cm"',
                "the text and the entries state one size",
            ),
        ]
    ),
]

"""Mutation rows for retail decoys: text-match, apparel, product-word, color-word brands, Nike and the garden color.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- retail: text-match decoys (gen#294) ----
    *(
        Mutation(f"text-match decoys: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
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
    # ---- retail: text-match decoys on every clothing type (gen#311) ----
    *(
        Mutation(f"apparel decoys: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
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
                'TORSO_HEM = band((0.0, 0.89, 1.0, 1.0))',
                "tests/test_retail_apparel_decoys_311.py -k torsos_and_does_not_color",
                "a sleeve's cuff is not part of the hem",
            ),
        ]
    ),
    # ---- retail: product-word decoys (gen#326) ----
    *(
        Mutation(f"product-word decoys: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a class-8 decoy is color-completed",
                "main_colors.py",
                "r[\"product_id\"] not in _PLANTED",
                "r[\"product_id\"] not in decoy_rows.IDS",
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
                "f\"| {r.policy} |\"",
                "f\"| |\"",
                "tests/test_retail_product_word_decoys_326.py -k docs_table",
                "the docs table lists each row with its policy",
            ),
        ]
    ),
    Mutation(
        "product-word decoys: the text check ignores the exempt list",
        "core/standard.py",
        'if doc.get("product_id") not in text_exempt',
        "if True",
        "tests/test_retail_scale.py -k 20k_build_meets_the_output_standard",
        "A",
        "a decoy's misleading detail color is exempt from the text check, nothing else is",
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
    Mutation(
        "product-word decoys: an ordinary product naming another color is exempt too",
        "core/standard.py",
        'if doc.get("product_id") not in text_exempt',
        "if True",
        "tests/test_retail_product_word_decoys_326.py -k exempt_by_decoy",
        "A",
        "only a declared decoy id is exempt; an ordinary id naming Red with color Black is refused",
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
    # ---- retail: Nike is a real brand, text only (gen#341) ----
    *(
        Mutation(f"nike: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
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
        Mutation(f"garden decoy color: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
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
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: retail decoys"


def rows() -> list[Mutation]:
    return MUTATIONS

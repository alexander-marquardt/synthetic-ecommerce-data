"""Mutation rows for retail types and rules: the steak ware, school uniform, failure-class types, promotion, drawing params and jigsaw size.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- retail: the steak plate, board and weight carry a material, never derived (gen#268) ----
    *(
        Mutation(f"steak ware: {name}", file, old, new_, test, "", prop,
                 root="prototypes/retail_drawings")
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
        Mutation(f"school uniform: {name}", "school_rows.py", old, new_, test, "", prop,
                 root="prototypes/retail_drawings")
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
    # ---- retail: the product types the failure classes need (gen#329) ----
    # Every name starts "needs rows:", so `--only "needs rows:"` re-runs them.
    *(
        Mutation(f"needs rows: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
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
    # ---- retail: promotion replaces the boolean offer (gen#189) ----
    *(
        Mutation(f"promotion: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
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
                '    # it follows',
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
        Mutation(f"drawing params: {name}", "variants.py", old, new, tests, "", prop,
                 root="prototypes/retail_drawings")
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
    # Every name starts "variant bounds doc:", so `--only "variant bounds doc:"`
    # re-runs the rows that hold docs/adding-a-type.md to the build's bounds (#252).
    Mutation(
        "variant bounds doc: the knob's maximum moves off the doc's",
        "domains/industrial/product_split.py",
        "    ceiling = table[-1][0]\n",
        "    ceiling = table[-1][0] + 1\n",
        "tests/test_variant_bounds_doc_252.py::test_the_doc_states_the_maximum_skus_per_product",
        "",
        "the doc states the most SKUs a product may have",
    ),
    Mutation(
        "variant bounds doc: the median bound moves off the doc's",
        "domains/industrial/product_split.py",
        "        if running >= 0.75:\n",
        "        if running >= 0.9:\n",
        "tests/test_variant_bounds_doc_252.py::test_the_doc_states_the_median_bound",
        "",
        "the doc states the largest median of a deep type",
    ),
    Mutation(
        "variant bounds doc: the product floor moves off the doc's",
        "domains/industrial/product_split.py",
        "MEDIAN_MIN_PRODUCTS = 20\n",
        "MEDIAN_MIN_PRODUCTS = 25\n",
        "tests/test_variant_bounds_doc_252.py::test_the_doc_states_the_product_floor_of_the_median_check",
        "",
        "the doc states the product floor of the median check",
    ),
    # ---- retail: a jigsaw's finished size is two CMT entries (gen#261) ----
    *(
        Mutation(f"jigsaw size: {name}", "toys_rows.py", old, new,
                 "tests/test_retail_toys_201.py -k jigsaws_finished_size", "", prop,
                 root="prototypes/retail_drawings")
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

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: retail types"


def rows() -> list[Mutation]:
    return MUTATIONS

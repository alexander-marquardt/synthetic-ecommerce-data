"""Mutation rows for the committed catalog and the structural guards run against the committed data.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- the structural-collision guard ---------------------------------
    Mutation(
        "let a catalog attribute claim a structural field name",
        "core/entry.py",
        '        "attribute_names",\n        "fulltext",',
        '        "attribute_names",\n        "fulltext",\n        "item",',
        "tests/test_prism_field_map_drift.py",
        "",
        "no attribute silently redefines a structural field",
    ),
    # ---- the committed catalog is what the generator writes --------------
    #
    # Two ROOTS, because the golden test has two independent halves and each
    # one has to be proven from its own side. Mutating the GENERATOR proves
    # the sha256 comparison notices a build that moved; mutating the COMMITTED
    # DATA proves the headline invariants notice a corrupted regeneration on
    # their own, without the hashes' help -- which is the whole reason they
    # are asserted against the committed bytes rather than the fresh build.
    Mutation(
        "move the image host without regenerating the catalog",
        "core/emit.py",
        'IMAGE_ROOT = "industrial"',
        'IMAGE_ROOT = "moved"',
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "A",
        "the committed catalog is byte-identical to a fresh build",
    ),
    Mutation(
        "emit an eighth file the build does not commit",
        "generate_cli.py",
        '    (out / "mapping.flat.json").write_text(',
        '    (out / "mapping.extra.json").write_text("{}\\n", encoding="utf-8")\n'
        '    (out / "mapping.flat.json").write_text(',
        "tests/test_catalog_golden.py::test_golden_directory_holds_exactly_the_build_output",
        "B",
        "the committed catalog is byte-identical to a fresh build",
    ),
    Mutation(
        "change the default seed and leave the catalog on the old one",
        "core/config.py",
        "    seed: int = 20260917",
        "    seed: int = 20260918",
        "tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed",
        "",
        "the committed catalog is the DEFAULT configuration",
    ),
    # ---- figures: the measured figures are build output (#103) -----------
    # A figure the build miscounts reds the rebuild comparison; a doc that
    # quotes one again reds the docs scan.
    Mutation(
        "figures: brands counted as product types",
        "generate_cli.py",
        '"brands": len({doc["brand"] for doc in flat}),',
        '"brands": len({doc["product_type"] for doc in flat}),',
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "",
        "the measured figures are the committed catalog's",
    ),
    Mutation(
        "figures: the dispersion band's densest end taken over every quantity",
        "prism/derive.py",
        "        densest = max(faceted, key=lambda s: s.dispersion)",
        "        densest = max(quantitative, key=lambda s: s.dispersion)",
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "",
        "the measured figures are the committed catalog's",
    ),
    Mutation(
        "figures: the README quotes the brand count again",
        "README.md",
        "[breadth categories](#catalog-breadth), one product each, from invented",
        "[breadth categories](#catalog-breadth), one product each, from 45 invented",
        "tests/test_measured_figures.py::test_no_doc_restates_a_figure_the_build_measures",
        "",
        "no doc restates a measured figure",
        root=".",
    ),
    # ---- the headline invariants, mutated in the COMMITTED DATA ----------
    Mutation(
        "blank one card image url in the committed catalog",
        "flat.jsonl",
        '"stock": 191, "pricing_unit": "Each", "order_multiple": 1, "image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg"',
        '"stock": 191, "pricing_unit": "Each", "order_multiple": 1, "image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": ""',
        "tests/test_catalog_golden.py::test_every_flat_document_carries_an_image_url",
        "A",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    Mutation(
        "drop the detail image url from one committed nested variant",
        "nested.jsonl",
        '"stock": 191, "pricing_unit": "Each", "order_multiple": 1, '
        '"image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg", '
        '"image_detail_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg"',
        '"stock": 191, "pricing_unit": "Each", "order_multiple": 1, '
        '"image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg"',
        "tests/test_catalog_golden.py::test_every_nested_line_and_variant_carries_an_image_url",
        "B",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    # THE REPLACEMENT SKU HAS TO EXIST, which is the whole mutation and is
    # what this row got wrong. It rewrote ``97NR28`` as ``80FY44`` -- a sku
    # the catalog does not carry -- so it RENAMED a document instead of
    # duplicating one, every sku stayed distinct, and
    # ``test_flat_holds_one_document_per_sku`` passed for the correct reason
    # while the table read it as proof. ``51RE59`` is CRE-G246-0001's own
    # second variant, so the mutation now really does publish one sku twice.
    # The alexander-marquardt/synthetic-ecommerce-data#39 regeneration
    # (Corner Radius/Neck Length applied once instead of twice) is what took
    # the previous anchor sku, ``6DT18``, out of the catalog.
    # alexander-marquardt/synthetic-ecommerce-data#48 renumbered every
    # sku as a part number, so the golden rows re-anchor on the first committed
    # product line with more than one variant, TAN-FD580-1609-0003; its second
    # variant, ``1609562324``, is the sku this row duplicates.
    Mutation(
        "duplicate a sku in the committed flat catalog",
        "flat.jsonl",
        '{"sku": "1609171743", "product_id": "TAN-FD580-1609-0003"',
        '{"sku": "1609562324", "product_id": "TAN-FD580-1609-0003"',
        "tests/test_catalog_golden.py::test_flat_holds_one_document_per_sku",
        "",
        "flat.jsonl is one document per distinct sku",
        root="golden-catalog",
    ),
    Mutation(
        "point one committed document at a product line that does not exist",
        "flat.jsonl",
        '{"sku": "1609171743", "product_id": "TAN-FD580-1609-0003"',
        '{"sku": "1609171743", "product_id": "TAN-FD580-1609-9999"',
        "tests/test_catalog_golden.py::test_flat_covers_exactly_the_product_lines",
        "",
        "the catalog spans exactly the committed number of products",
        root="golden-catalog",
    ),
    Mutation(
        "publish a variant_count that disagrees with its own variants array",
        "nested.jsonl",
        '"variant_count": 3, "variants": [{"sku": "1609171743", "title": "Shop Flap Disc',
        '"variant_count": 4, "variants": [{"sku": "1609171743", "title": "Shop Flap Disc',
        "tests/test_catalog_golden.py::test_nested_lines_account_for_every_sku",
        "",
        "the nested lines account for every sku",
        root="golden-catalog",
    ),
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: committed catalog"


def rows() -> list[Mutation]:
    return MUTATIONS

"""Mutations that plant a defect in the committed golden catalogue files and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
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

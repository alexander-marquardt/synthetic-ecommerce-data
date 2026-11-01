"""Class-8 decoys of the plain query "socks" (gen#774): the plural on products that are not socks.

The top 24 products of a plain match for ``socks`` were all real socks. A boot sock's ``text`` says
the word three times, in its title and in two category nodes, and it is short, so one mention in a
title never reached it. Each row here is a real product a shop names for socks: a foot treatment
worn like one, a bag and a drawer divider made to hold them, a puppet kit that starts from one, a
grip that an electrician pulls cable with. Five of the six say the word three times in a short
description, the shape that reaches the top of a plain match, and a real sock's title is long
(:mod:`sock_titles`), so ``text`` no longer fills the first places on length alone.

Each is filed in its true leaf, drawn as what it is, and sits under no Socks node, so the category
policy drops every one when interpretation is on. The seventh decoy of the issue, the absorbent
spill socks, is an industrial type (``domains/industrial/product_types/safety/spill_socks.py``).
``tests/test_retail_socks_decoys_774.py`` holds the proof.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.decoy_kind import Kind

_FOOT = ("Beauty", "Skincare", "Creams", "Foot Creams")

KINDS = {
    "sk_gel_socks": Kind("Beauty", _FOOT, "Foot Cream", "socks", "Saltmarsh", 8.0, params=(("pairs", "1"),)),
    "sk_peel_socks": Kind("Beauty", _FOOT, "Foot Cream", "pouch", "Saltmarsh", 7.0),
    "sk_organiser": Kind(
        "Home", ("Home", "Storage", "Garment Storage"), "Storage Boxes", "storage_box", "Brackenmere Home", 11.0,
        params=(("form", "box"), ("lid", "no")),
    ),
    "sk_puppet_kit": Kind(
        "Toys", ("Toys", "Arts & Crafts", "Craft Kits"), "Arts and Crafts Kit", "craft_kit", "Little Fernby", 9.0,
        audience="kids", colorless=True, params=(("kind", "bead"), ("counts", "4,2,1")),
    ),
    "sk_cable_grip": Kind("Electronics", ("Electronics", "Accessories", "Cables"), "Cable", "mesh_bag", "Wrenfield", 14.0),
}  # fmt: skip

#: Rows of (number, kind, title, description, color).
_ROWS = (
    (7740, "sk_gel_socks", "Moisturising Gel Socks", "Gel socks for dry feet. Wear the socks overnight, then rinse the socks.", "White"),
    (7741, "sk_peel_socks", "Exfoliating Foot Peel Socks", "Peel socks for hard skin. Wear the socks an hour, then bin the socks.", "Green"),
    (7742, "wash_bag", "Mesh Wash Bag for Socks", "A zip mesh bag for socks: wash socks in it and never lose socks.", "White"),
    (7743, "sk_organiser", "Socks and Underwear Drawer Organiser", "Fabric dividers for a drawer: socks in rows, socks by pair, socks in sight.", "Grey"),
    (7744, "sk_puppet_kit", "Socks Puppet Craft Kit", "Turn old socks into puppets. Felt, eyes and glue for socks; socks not included.", "Blue"),
    (7745, "sk_cable_grip", "Cable Pulling Socks", "Steel mesh socks that grip a cable end and draw it through conduit.", "Grey"),
)  # fmt: skip


def word_rows(d):
    # Sold below the table's default, so that the rows do not lead the queries for their true types.
    return tuple(
        d(n, kind, title, desc, color, "socks", "sock", "category", sold=600)
        for n, kind, title, desc, color in _ROWS
    )

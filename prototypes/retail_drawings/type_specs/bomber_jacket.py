"""Bomber Jackets (gen#434 gap 3, a spec by #645): Womens > Coats & Jackets > Bomber Jackets.

The leaf held three Womens check bombers (``PLT-CKBCON``, ``PLT-CKBWOL``, ``PLT-CKBPAD``, which
the committed Elasticsearch proof names, so they stay in ``class_rows``: ``tests/test_retail_type_specs_351.py``,
``PROOF_PINNED_CLASS_ROWS``). Thirteen more check bombers (``pattern = check``) bring it to
sixteen. A check bomber is drawn as a check: its colorway is a gingham swatch of the stated
colors, never a plain one. The rows are templates only (``derivable`` False).

The type's text-match decoys (gen#311) are planned in ``decoy_apparel``, which already carries
"Bomber Jacket"; the spec adds no plan of its own.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from type_registry import BRAND_OWNER, Home, LRow, TypeSpec, cw

#: The brands these rows sell, owned as the rest of the clothing tree states.
BRANDS = ("Calderby & Lune", "Harbour & Pine", "Larkmoor", "Wrenfield", "Bramblewood")
_PATH = ("Womens", "Coats & Jackets", "Bomber Jackets")
_SIZES = ("XS", "S", "M", "L", "XL")

#: The check colors: (base, accent).
_CHECKS = {
    "Brown": ("#7a5a3c", "#3b2a1c"), "Grey": ("#9a9a9a", "#2a2a2e"), "Navy": ("#26365c", "#c8312e"),
    "Green": ("#4d6b45", "#e8dfcc"), "Red": ("#a8322e", "#2a2a2e"), "Black": ("#2a2a2e", "#8a8a8a"),
    "Blue": ("#4a6a94", "#e8dfcc"), "Camel": ("#b5835a", "#5a3426"),
}  # fmt: skip

#: (code, title, brand, price, material, description, check color)
_BOMBERS = (
    ("CKQUIL", "Small Check Bomber Jacket", BRANDS[0], 64.0, "Polyester", "A bomber in a small check, with ribbed cuffs and hem.", "Brown"),
    ("CKCROP", "Cropped Check Bomber Jacket", BRANDS[1], 55.0, "Cotton blend", "A short, boxy bomber in a bold check with a zip front.", "Grey"),
    ("CKOVRS", "Oversized Check Bomber Jacket", BRANDS[2], 72.0, "Wool blend", "A relaxed oversized bomber in a woolly check, with deep pockets.", "Navy"),
    ("CKREVS", "Two Sided Check Bomber Jacket", BRANDS[3], 79.0, "Polyester", "A bomber that wears check on one side and plain on the other.", "Green"),
    ("CKHOOD", "Hooded Check Bomber Jacket", BRANDS[4], 68.0, "Cotton blend", "A hooded bomber in a brushed check, with a zip front and ribbed cuffs.", "Red"),
    ("CKFLCE", "Fleece Lined Check Bomber Jacket", BRANDS[0], 82.0, "Polyester", "A check bomber with a soft fleece lining for the colder months.", "Black"),
    ("CKTWDE", "Tweed Check Bomber Jacket", BRANDS[1], 89.0, "Wool blend", "A bomber in a textured tweed check with a contrast rib collar.", "Camel"),
    ("CKFLNL", "Flannel Check Bomber Jacket", BRANDS[2], 58.0, "Cotton", "A soft brushed flannel check bomber, zip front, with two pockets.", "Blue"),
    ("CKLGHT", "Lightweight Check Bomber Jacket", BRANDS[3], 49.0, "Polyester", "A light, unlined bomber in a fine check, for spring evenings.", "Grey"),
    ("CKSATN", "Satin Trim Check Bomber Jacket", BRANDS[4], 76.0, "Wool blend", "A check bomber with satin trim at the collar, cuffs and hem.", "Navy"),
    ("CKBCLE", "Boucle Check Bomber Jacket", BRANDS[0], 85.0, "Boucle", "A bomber in a soft boucle check, with a zip front and ribbed hem.", "Camel"),
    ("CKTWIL", "Cotton Twill Check Bomber Jacket", BRANDS[1], 62.0, "Cotton", "A cotton twill bomber in a classic check with a snap pocket.", "Green"),
    ("CKPADD", "Gingham Check Bomber Jacket", BRANDS[2], 70.0, "Polyester", "A bomber in a small gingham check, with a zip front and a contrast lining.", "Red"),
)  # fmt: skip


def _row(code, title, brand, price, material, desc, check) -> LRow:
    base, accent = _CHECKS[check]
    return LRow(
        code, title, brand, "Clothing", _PATH, "Bomber Jacket", price, "coat", desc,
        (cw(f"{check} Check", base, "gingham", accent),),
        (("material", "Material", material), ("fit", "Fit", "Regular")),
        tuple((s, price) for s in _SIZES), size_key="size",
        facts=(("pattern", "check"), ("size_range", ["regular"])),
    )  # fmt: skip


SPEC = TypeSpec(
    key="bomber_jacket",
    homes=(Home("samples", True), Home("decoy_product_words", False)),
    department="Clothing",
    product_type="Bomber Jacket",
    owners=tuple((b, BRAND_OWNER[b]) for b in BRANDS),
    rows=tuple(_row(*b) for b in _BOMBERS),
)

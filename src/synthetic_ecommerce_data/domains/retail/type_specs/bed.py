"""Beds (gen#434 gap 3, a spec by #645): Home > Furniture > Beds.

The leaf held six beds (``PLT-BDSHKR``, ``PLT-BDMETL``, ``PLT-BDUPHL``, ``PLT-BDOTTO``,
``PLT-BDSLGH``, ``PLT-BDPANL``, which the committed Elasticsearch proof names, so they stay in
``class_rows``: ``tests/test_retail_type_specs_351.py``, ``PROOF_PINNED_CLASS_ROWS``). Ten
more frames, each sold in the sizes it is made in, bring it to sixteen.

Every bed states its size: one SKU per size, with the shared vocabulary of
``class_model.BED_SIZE_DIMS`` (``bed_size``, with the mattress ``width_cm`` and ``length_cm``)
and the price stepping up a fifth of the base price per size, as the class rows do.
:class:`BedRow` is a :class:`type_registry.Row` that adds the two dimensions to each SKU. The
rows are templates only (``derivable`` False), so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.class_model import BED_SIZE_DIMS
from synthetic_ecommerce_data.domains.retail.type_registry import (
    BRAND_OWNER,
    Home,
    Row,
    TypeSpec,
    cw,
)

#: The brands these rows sell, owned as the rest of the tree states.
BRANDS = ("Brackenmere Home", "Quillon Sleep")
SIZES = tuple(BED_SIZE_DIMS)
_PATH = ("Home", "Furniture", "Beds")


@dataclass(frozen=True)
class BedRow(Row):
    """A bed frame: one SKU per size it is made in, with its mattress width and length."""

    def skus(self) -> list[dict]:
        step = round(self.price / 5)
        return [
            {"bed_size": s, "width_cm": BED_SIZE_DIMS[s][0], "length_cm": BED_SIZE_DIMS[s][1],
             "price": float(self.price + n * step), "in_stock": True}
            for n, (s, _) in enumerate(self.sizes)
        ]  # fmt: skip


#: (code, title, brand, price, description, headboard, sizes, frame color)
_BEDS = (
    ("BDOAKS", "Solid Oak Bed Frame", BRANDS[0], 449.0, "A solid oak bed frame with a plain headboard, made in every size from single to super king.", "shaker", SIZES, "#a98355"),
    ("BDWALN", "Walnut Panel Bed Frame", BRANDS[1], 529.0, "A walnut veneer bed frame with a panelled headboard, in small double to super king.", "panel", SIZES[1:], "#5b4030"),
    ("BDWHTS", "White Painted Shaker Bed", BRANDS[0], 279.0, "A white painted wooden bed with a shaker headboard, in single to king size.", "shaker", SIZES[:4], "#f0ede6"),
    ("BDBLKM", "Black Metal Spindle Bed Frame", BRANDS[1], 169.0, "A black metal bed with a spindle head end, in single, small double and double.", "spindle", SIZES[:3], "#2d2d2f"),
    ("BDBRSS", "Brass Finish Spindle Bed", BRANDS[0], 239.0, "A bed with a brass finish metal frame and a spindle head end, in single to king size.", "spindle", SIZES[:4], "#b5a14a"),
    ("BDGRYV", "Grey Velvet Upholstered Bed", BRANDS[1], 479.0, "A bed upholstered in soft grey velvet, in small double to super king.", "upholstered", SIZES[1:], "#7b7d86"),
    ("BDNVYB", "Navy Buttoned Upholstered Bed", BRANDS[0], 519.0, "A buttoned navy upholstered bed with a tall headboard, in double to super king.", "upholstered", SIZES[2:], "#26365c"),
    ("BDCRMS", "Cream Boucle Sleigh Bed", BRANDS[1], 1049.0, "A scrolled sleigh bed in cream boucle, in king and super king.", "sleigh", SIZES[3:], "#e7ddc9"),
    ("BDGRYO", "Grey Fabric Ottoman Bed", BRANDS[0], 949.0, "A lift up ottoman bed in grey fabric with deep storage, in double, king and super king.", "ottoman", SIZES[2:], "#8a8a90"),
    ("BDPINE", "Pine Panel Bed Frame", BRANDS[1], 199.0, "A pine bed frame with a panelled headboard, in single, small double and double.", "panel", SIZES[:3], "#c8a96a"),
)  # fmt: skip


def _row(code, title, brand, price, desc, head, sizes, color) -> BedRow:
    return BedRow(
        code, title, brand, "Home", _PATH, "Bed", price, "bed_frame", desc,
        (cw("Frame", color),), (), tuple((s, price) for s in sizes), size_key="bed_size",
        colorless=True, params=(("head", head),),
    )  # fmt: skip


SPEC = TypeSpec(
    key="bed",
    homes=(Home("samples", True),),
    department="Home",
    product_type="Bed",
    owners=tuple((b, BRAND_OWNER[b]) for b in BRANDS),
    rows=tuple(_row(*b) for b in _BEDS),
)

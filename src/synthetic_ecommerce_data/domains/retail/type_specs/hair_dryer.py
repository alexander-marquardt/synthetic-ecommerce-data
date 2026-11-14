"""Hair dryers (gen#957): Beauty > Hair Care > Hair Dryers.

A breadth type: ``derivable`` True, so the scaled build draws more dryers from these four by the
values their titles show (the technology and the form). The body is the SKU's color; the
technology draws the badge and the form the handle (:func:`kit_hair.hair_dryer`). Each SKU is a
color with or without its attachments.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.hair_rows import (
    BLACK,
    DEPARTMENT,
    DRYERS,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a


def _dryer(technology: str, form: str) -> tuple[tuple, ...]:
    return (a("technology", "Technology", technology), a("form", "Form", form))


def _kit(price: float) -> tuple[tuple[str, float], ...]:
    return (("Dryer only", price), ("With diffuser", price + 6.0),
            ("With diffuser and concentrator", price + 9.0))  # fmt: skip


def _params(technology: str, form: str) -> tuple[tuple[str, str], ...]:
    return (("technology", technology.lower()), ("form", form.lower()))


ROWS = (
    row(
        "HDRION",
        "Ionic Salon Hair Dryer",
        "Hollin Hair",
        DRYERS,
        "Hair Dryer",
        "hair_dryer",
        "A powerful ionic dryer with three heat settings, a cool shot and a long cord for a salon-smooth blow-dry.",
        _dryer("Ionic", "Salon"),
        _kit(49.0),
        _params("Ionic", "Salon"),
        "attachments",
    ),
    row(
        "HDRCER",
        "Ceramic Compact Hair Dryer",
        "Veilmoor",
        DRYERS,
        "Hair Dryer",
        "hair_dryer",
        "A light ceramic dryer with an even, gentle heat that dries fine hair without frizz.",
        _dryer("Ceramic", "Compact"),
        _kit(32.0),
        _params("Ceramic", "Compact"),
        "attachments",
    ),
    row(
        "HDRTOU",
        "Tourmaline Travel Hair Dryer",
        "Fenmere",
        DRYERS,
        "Hair Dryer",
        "hair_dryer",
        "A small tourmaline dryer with dual voltage that packs flat in a weekend bag.",
        _dryer("Tourmaline", "Travel"),
        _kit(24.0),
        _params("Tourmaline", "Travel"),
        "attachments",
    ),
    row(
        "HDRINF",
        "Infrared Folding Hair Dryer",
        "Aldermist",
        DRYERS,
        "Hair Dryer",
        "hair_dryer",
        "An infrared dryer whose handle folds against the body, warming hair from within for a glossy finish.",
        _dryer("Infrared", "Folding"),
        _kit(39.0),
        _params("Infrared", "Folding"),
        "attachments",
    ),
)

SPEC = TypeSpec(
    key="hair_dryer",
    department=DEPARTMENT,
    product_type="Hair Dryer",
    derivable=True,
    rows=ROWS,
    owners=(("Hollin Hair", "third_party"), ("Veilmoor", "third_party"), ("Fenmere", "third_party"), ("Aldermist", "third_party")),
    options=(Option("attachments", "attachments", "Attachments"),),
    decoys=(
        Decoy(4, "red hair dryer", "vocabulary", decoy(ROWS[0], "HDRRDD", "Ionic Hair Dryer with Red Diffuser",
              "An ionic hair dryer in black, sold with a red diffuser for curls.", BLACK)),
        Decoy(6, "green hair dryer", "generic", decoy(ROWS[1], "HDRGRL", "Green Lane Ceramic Hair Dryer",
              "From the Green Lane range: a compact ceramic dryer in white.", WHITE)),
    ),
)  # fmt: skip

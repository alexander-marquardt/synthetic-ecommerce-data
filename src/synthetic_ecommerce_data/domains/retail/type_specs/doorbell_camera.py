"""Doorbell cameras (gen#956): Electronics > Smart Home > Doorbell Cameras.

A breadth type: ``derivable`` True, so the scaled build draws more doorbells from these rows by
the values their titles show (a power and a feature, a video quality, a power or a feature).
The faceplate is the SKU's color; ``doorbell_power`` draws a battery gauge or two wires out of the foot
(:func:`kit_smart_home.doorbell_camera`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    BOLTWICK,
    ELECTRONICS_OWNERS,
    HALVERN,
    MERVANE,
    NIMBREL,
    QUORRIN,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.smart_home_rows import (
    BLACK,
    DOORBELLS,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _db(code: str, title: str, brand: str, price: float, description: str, power: str,
        quality: str, feature: str) -> object:  # fmt: skip
    attrs = (a("doorbell_power", "Power", power), a("video_quality", "Video quality", quality),
             a("doorbell_feature", "Doorbell feature", feature))  # fmt: skip
    return row(code, title, brand, DOORBELLS, "Doorbell Camera", "doorbell_camera", price,
               description, attrs, (("doorbell_power", power.lower()),))  # fmt: skip


ROWS = (
    _db("SMD001", "Wired Video Doorbell with Night Vision", HALVERN, 129.0,
        "A sharp picture of the porch after dark, powered by the old bell wires.", "Wired", "2K", "Night Vision"),
    _db("SMD002", "Battery Video Doorbell with Package Detection", ARDMOOR, 89.0,
        "A message when a parcel is left at the door, and six months per charge.", "Battery", "1080p", "Package Detection"),
    _db("SMD003", "2K Smart Doorbell Camera", TORVANE, 109.0,
        "Head-to-toe video in high detail, with a quick-release battery.", "Battery", "2K", "Night Vision"),
    _db("SMD004", "1080p Smart Doorbell Camera", MERVANE, 59.0,
        "A wide view of the step and the path, recorded when someone comes near.", "Wired", "1080p", "Two-Way Talk"),
    _db("SMD005", "Battery Doorbell Camera with App Alerts", NIMBREL, 69.0,
        "See who is at the door from a phone anywhere, and fit it with two screws.", "Battery", "1080p", "Two-Way Talk"),
    _db("SMD006", "Wired Doorbell Camera with App Alerts", BOLTWICK, 79.0,
        "Infrared night vision and a chime that plugs into any socket.", "Wired", "1080p", "Night Vision"),
    _db("SMD007", "Video Doorbell Camera with Two-Way Talk", QUORRIN, 119.0,
        "Speak to a visitor with clear sound and see their face in high detail.", "Wired", "2K", "Two-Way Talk"),
    _db("SMD008", "Video Doorbell Camera with Package Detection", WEXMOOR, 99.0,
        "Tells a person from a parcel and sends a clip of each delivery.", "Battery", "1080p", "Package Detection"),
)  # fmt: skip

SPEC = TypeSpec(
    key="doorbell_camera",
    department=DEPARTMENT,
    product_type="Doorbell Camera",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "blue doorbell", "vocabulary", decoy(ROWS[0], "SMDBRL", "Wired Video Doorbell with Night Vision and Blue Ring Light",
              "A black video doorbell with a blue light ring around its button.", BLACK)),
        Decoy(6, "green doorbell", "generic", decoy(ROWS[4], "SMDGLN", "Green Lane Battery Doorbell Camera with App Alerts",
              "From the Green Lane range: a battery video doorbell in white.", WHITE)),
    ),
)  # fmt: skip

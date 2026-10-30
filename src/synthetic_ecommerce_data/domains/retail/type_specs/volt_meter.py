"""Volt meters (#721): handheld and clamp meters in Home > DIY & Tools > Volt Meters.

PackingHarder's meters put a computer brand on the tool shelf. The title says ``Volt Meter`` and
the description ``voltmeter``, so both spellings find the type. Drawing: ``kit_drills``.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import diy_tools as d
from synthetic_ecommerce_data.domains.retail.electronics_rows import PACKINGHARDER
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec, a


def _attrs(volts: int, form: str, rating: str) -> tuple:
    return (
        a("measuring_range", "Measuring range (V)", str(volts)),
        a("meter_form", "Form", form),
        a("safety_rating", "Safety rating", rating),
    )


ROWS = d.styles(
    (
        ("VLTPH1", "PackingHarder Digital Volt Meter", PACKINGHARDER, 34.0, "A handheld digital voltmeter that reads AC and DC up to 600 volts, with two probe leads.", _attrs(600, "Handheld", "CAT III"), (("form", "handheld"),)),
        ("VLTPH2", "PackingHarder Auto-Ranging Volt Meter and Multimeter", PACKINGHARDER, 69.0, "An auto-ranging voltmeter and multimeter that also reads resistance and continuity, up to 1000 volts.", _attrs(1000, "Handheld", "CAT IV"), (("form", "handheld"),)),
        ("VLTPH3", "PackingHarder Clamp Volt Meter", PACKINGHARDER, 89.0, "A clamp voltmeter whose jaw closes round a cable, up to 600 volts.", _attrs(600, "Clamp", "CAT III"), (("form", "clamp"),)),
        ("VLTSTO", "Stonemarsh Pocket Volt Meter", d.STO, 19.0, "A pocket voltmeter for batteries and sockets, up to 300 volts.", _attrs(300, "Handheld", "CAT II"), (("form", "handheld"),)),
        ("VLTHAR", "Harkwell Works Clamp Volt Meter", d.HAR, 59.0, "A clamp voltmeter with a backlit display, up to 600 volts.", _attrs(600, "Clamp", "CAT III"), (("form", "clamp"),)),
        ("VLTTOR", "Torvane Tools Digital Volt Meter", d.TOR, 44.0, "A digital voltmeter with a kickstand and a data hold button, up to 600 volts.", _attrs(600, "Handheld", "CAT III"), (("form", "handheld"),)),
    ),
    "Volt Meter",
    "volt_meter",
    (*d.DIY, "Volt Meters"),
)

SPEC = TypeSpec(
    key="volt_meter",
    department=d.HOME,
    product_type="Volt Meter",
    owners=(*d.OWNERS, (PACKINGHARDER, "third_party")),
    rows=ROWS,
    decoys=d.decoys(
        ROWS[0],
        "digital volt meter",
        ("VMTDY1", "PackingHarder Digital Volt Meter with Carry Case", "volt meter carry case"),
    ),
)

"""Laundry (gen#334): washing machines, heat pump, condenser and vented tumble dryers, washer dryers.

Six models of each kind in Home > Large Appliances > Laundry, drawn by
:func:`kit_large_appliances.washing_machine`, ``tumble_dryer`` and ``washer_dryer``. A model's load,
spin speed and energy rating are structured; its finish is the SKU's color. The washing machine
cleaner, descaler and laundry pods are class-8 decoys
(``feature_decoys/large_appliances.py``), and a white machine with a "Red Spot" dial is a color
decoy. Every brand is invented. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

import large_appliance_rows as rows
from type_registry import Decoy, TypeSpec, a

SPEC = TypeSpec(
    key="laundry_appliance",
    department="Home",
    product_type="Laundry Appliance",
    owners=rows.OWNERS,
    rows=rows.laundry_rows(),
    decoys=(
        Decoy(1, "red washing machine", "color", rows.decoy_row(
            "LRS001", "Washing Machine with Red Spot Dial", rows.BRANDS[2], rows.LAUNDRY,
            "Laundry Appliance", 349.0, "washing_machine",
            "A front-loading washing machine in white. The Red Spot dial on its panel picks the "
            "programme.", (rows.WHITE,),
            (a("appliance_type", "Type", "Washing Machine"), rows._kg("load", "Load capacity", 8),
             a("spin_rpm", "Spin speed (rpm)", "1200"), rows.a("energy_rating", "Energy rating", "B")))),
    ),
)

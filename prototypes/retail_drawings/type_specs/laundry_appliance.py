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

from dataclasses import replace

import large_appliance_rows as lar
from breadth_rows import Row
from type_registry import Decoy, TypeSpec, a

#: The laundry: (load kg, spin rpm or dry kg, price)
_LAUNDRY_KINDS = (
    ("LWM", "washing_machine", "", "Washing Machine", "Washing Machine", "A front-loading washing machine",
     ((7, 1200, 279), (8, 1400, 329), (9, 1400, 379), (10, 1400, 429), (10, 1600, 499), (12, 1600, 599))),
    ("LTH", "tumble_dryer", "heat_pump", "Heat Pump Tumble Dryer", "Tumble Dryer (Heat Pump)", "A heat pump tumble dryer",
     ((7, 0, 379), (8, 0, 429), (8, 0, 479), (9, 0, 529), (9, 0, 599), (10, 0, 699))),
    ("LTC", "tumble_dryer", "condenser", "Condenser Tumble Dryer", "Tumble Dryer (Condenser)", "A condenser tumble dryer",
     ((7, 0, 249), (8, 0, 279), (8, 0, 299), (9, 0, 329), (9, 0, 359), (10, 0, 399))),
    ("LTV", "tumble_dryer", "vented", "Vented Tumble Dryer", "Tumble Dryer (Vented)", "A vented tumble dryer with a hose for the window",
     ((6, 0, 179), (7, 0, 199), (7, 0, 219), (8, 0, 239), (8, 0, 259), (9, 0, 289))),
    ("LWD", "washer_dryer", "", "Washer Dryer", "Washer Dryer", "A washer dryer that washes and dries in one drum",
     ((8, 1400, 399), (8, 1400, 449), (9, 1400, 499), (9, 1600, 549), (10, 1600, 629), (10, 1600, 699))),
)  # fmt: skip


#: The washing machines titled "Washing Machine from <brand>, Model <code>", the second form.
_FROM_FORM = (2, 5)


def _from_form(r: Row) -> Row:
    code = next(x[2] for x in r.attrs if x[0] == "model_number")
    return replace(r, title=f"Washing Machine from {r.brand}, Model {code}")


def laundry_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, kind, title, kind_name, lead, models in _LAUNDRY_KINDS:
        def make(i, models=models, lead=lead, kind_name=kind_name, pre=pre):
            load, spin, price = models[i]
            rating = lar.RATINGS[(i + len(pre)) % 5]
            what = f"takes a {load} kg load" + (f" and spins at {spin} rpm" if spin else "")
            desc = f"{lead}. It {what}, energy rating {rating}."
            attrs = [a("appliance_type", "Type", kind_name), lar.kg("load", "Load capacity", load)]
            if spin:
                attrs.append(a("spin_rpm", "Spin speed (rpm)", str(spin)))
            attrs.append(a("energy_rating", "Energy rating", rating))
            return float(price), desc, lar.PALETTES[i % 3], tuple(attrs)
        params = (("kind", kind),) if kind else ()
        rows = lar.kind_rows(pre, 6, lar.LAUNDRY, "Laundry Appliance", shape, params, title, make)
        if pre == "LWM":
            rows = tuple(_from_form(r) if i in _FROM_FORM else r for i, r in enumerate(rows))
        out += rows
    return tuple(out)


SPEC = TypeSpec(
    key="laundry_appliance",
    department="Home",
    product_type="Laundry Appliance",
    owners=lar.OWNERS,
    rows=laundry_rows(),
    decoys=(
        Decoy(1, "red washing machine", "color", lar.decoy_row(
            "LRS001", "Washing Machine with Red Spot Dial", lar.BRANDS[2], lar.LAUNDRY,
            "Laundry Appliance", 349.0, "washing_machine",
            "A front-loading washing machine in white. The Red Spot dial on its panel picks the "
            "programme.", (lar.WHITE,),
            (a("appliance_type", "Type", "Washing Machine"), lar.kg("load", "Load capacity", 8),
             a("spin_rpm", "Spin speed (rpm)", "1200"), a("energy_rating", "Energy rating", "B")))),
    ),
)

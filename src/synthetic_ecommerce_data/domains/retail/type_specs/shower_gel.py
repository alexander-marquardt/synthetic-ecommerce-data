"""Shower Gel (Beauty), registered by its spec (gen#537), with body wash rows of its own
(gen#1112, slice 3).

The older rows stay in the shared row modules named by ``homes``; ``derivable`` there says
whether the scaled build draws more of them. The spec's own rows are body washes: the title
shows the scent and the ``wash_finish`` (creamy, foaming, exfoliating, silky), the scaled build
draws more by swapping them (``derivable``), and a SKU is a bottle of 250 to 750 ml
(``net_volume_ml``). The drawing is :func:`kit_bath_shave.body_wash_bottle`. Add rows of this
type here, and a new type as its own spec file with its rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bath_shave_rows import (
    ALDERMIST,
    BLUSH,
    CREAM,
    FENMERE,
    FERN,
    OWNERS,
    PEARLBROOK,
    SHOWER_GEL,
    VEILMOOR,
    row,
    sizes,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec, a


def _wash(code, title, brand, scent, finish, skus, desc, color) -> object:  # noqa: ANN001
    attrs = (a("scent", "Scent", scent), a("wash_finish", "Wash finish", finish))
    return row(code, title, brand, SHOWER_GEL, "Shower Gel", "body_wash_bottle", desc, attrs,
               skus, "net_volume_ml", color, "Body Wash")  # fmt: skip


ROWS = (
    _wash("BWSCCO", "Creamy Coconut Body Wash", ALDERMIST, "Coconut", "Creamy",
          sizes((250, 3.5), (500, 6.0), (750, 8.0)), "A rich wash that lathers on a sponge and leaves the skin soft after the shower.", CREAM),
    _wash("BWSSLV", "Silky Lavender Body Wash", PEARLBROOK, "Lavender", "Silky",
          sizes((250, 4.0), (500, 6.75), (750, 9.0)), "A wash for the evening shower, in a bottle that stands on its cap.", BLUSH),
    _wash("BWSEHN", "Exfoliating Honey Body Wash", FENMERE, "Honey", "Exfoliating",
          sizes((250, 4.5), (500, 7.5), (750, 10.0)), "A wash for the knees, elbows and heels, worked in with a cloth.", CREAM),
    _wash("BWSFMN", "Foaming Mint Body Wash", VEILMOOR, "Mint", "Foaming",
          sizes((250, 3.0), (500, 5.25), (750, 7.0)), "A wash for after the gym that rinses off quickly and leaves no film.", FERN),
    _wash("BWSCVN", "Creamy Vanilla Body Wash", PEARLBROOK, "Vanilla", "Creamy",
          sizes((250, 3.75), (500, 6.25), (750, 8.5)), "A warm, sweet wash for a long shower, thick enough to use without a sponge.", CREAM),
    _wash("BWSSAL", "Silky Almond Body Wash", ALDERMIST, "Almond", "Silky",
          sizes((250, 4.25), (500, 7.0), (750, 9.5)), "A wash with almond oil for dry skin, rinsing off without the tight feel of soap.", BLUSH),
    _wash("BWSFEU", "Foaming Eucalyptus Body Wash", FENMERE, "Eucalyptus", "Foaming",
          sizes((250, 3.25), (500, 5.5), (750, 7.5)), "A fresh wash for the morning shower, pumped straight into the hand as foam.", FERN),
)  # fmt: skip

SPEC = TypeSpec(
    key="shower_gel",
    department="Beauty",
    product_type="Shower Gel",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    homes=(
        Home("samples", True),
        Home("breadth_rows", False),
        Home("decoy_rows", False),
        Home("grocery", False),
    ),
)

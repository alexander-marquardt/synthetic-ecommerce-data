"""Camping and fitness templates for the scaled retail catalog (gen#265): data only.

The catalog had no sports department. This is its first increment: the **Sports & Outdoors**
root with two families, Camping (tents, sleeping bags, camping chairs) and Yoga & Fitness
(yoga mats, dumbbells, kettlebells, foam rollers). The second increment (gen#368) adds yoga blocks
and straps, resistance bands, lanterns, roll mats, bike pumps (Cycling), the Baseball family (bats,
gloves, balls, batting helmets), Swimming (goggles, caps, kickboards, armbands) and Team & Racket
Sports (footballs, tennis rackets, badminton sets). All 24 types are one spec file each in
``type_specs/`` (gen#351, gen#455), built from :mod:`sports_helpers`; this module only lists
their rows as :data:`ROWS` for the checks over the department. Each type is a leaf with its own
drawing (:mod:`kit_sports`), its shopper attributes as structured entries, and SKUs over its color
and its own axis: a tent's berth, a sleeping bag's length in centimetres, a mat's thickness, a
weight's kilograms, a roller's length.

The tree follows the shape the maintainer's guidance asked for (department, then sport, then
equipment, with the filters each leaf carries), and every name here is invented. No leaf was
checked against a retailer's tree: ``docs/retail-sports-tree.md`` lists the filters per leaf, says
so, and gives each type not built an issue or a reason (gen#290).

Every type offers the six main colors across its styles (gen#275). A measured axis (``berth``,
``thickness_mm``, ``weight_kg``, ``length_cm``) is on the SKUs alone, which the export states
with its unit (``export.OPTIONS``). These styles are templates only: :func:`scale.derivable`
leaves them out, as it does the accessory and household rows, so the department grows by
authored rows.
"""

from __future__ import annotations

import kit_sports  # noqa: F401 -- registers tent, sleeping_bag, camp_chair, yoga_mat, ...
import type_registry
from sports_helpers import DEPARTMENT

#: Every Sports & Outdoors row of the registry, in key order, so the checks over :data:`ROWS`
#: read the department whole.
ROWS = tuple(
    row for _, spec in sorted(type_registry.specs().items()) if spec.department == DEPARTMENT
    for row in spec.rows
)  # fmt: skip

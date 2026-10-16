"""A title that states a volume carries that net volume (gen#347).

A cleaner titled "Glass Cleaner 500ml" is a 500 ml product: without the field it drops out of
the Net volume facet while the title says otherwise. :func:`state_title_volumes` is the one
place the volume of a record that states it only in its title becomes the record's
``unit_size``; a record that already carries a volume, on the product or on its SKUs, keeps it.
"""

from __future__ import annotations

import re
from typing import Any

#: A volume a title states: "500ml", "1.5L", "1L".
TITLE_VOLUME = re.compile(r"\b(\d+(?:\.\d+)?) ?(ml|L)\b")


def title_volume_ml(title: str) -> float | None:
    """The first volume ``title`` states, in ml; ``None`` when it states none."""
    found = TITLE_VOLUME.search(title)
    if found is None:
        return None
    return float(found.group(1)) * (1000 if found.group(2) == "L" else 1)


def state_title_volumes(recs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """``recs``, each one whose title states a volume and which carries none replaced by a copy
    that has its ``unit_size`` in ml. A record is never changed in place: ``samples()`` hands
    the same dicts to :func:`export.documents`, so a change here would show in the export only
    after ``scale.templates()`` had run (the export's identity test failed on that order)."""
    out = []
    for rec in recs:
        carries = "unit_size" in rec or any("net_volume_ml" in s for s in rec.get("skus", ()))
        if not carries and (ml := title_volume_ml(rec["title"])) is not None:
            rec = {**rec, "unit_size": ml, "unit_measure": "ml"}
        out.append(rec)
    return out

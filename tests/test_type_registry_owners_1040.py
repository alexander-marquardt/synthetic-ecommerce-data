"""A spec's brands are known to ``breadth_rows.OWNERS`` once the registry holds it (gen#1040).

``Row.doc()`` reads the brand's owner from ``breadth_rows.OWNERS``. A spec states the owners of
its new brands in ``TypeSpec.owners``. When only ``TypeSpec.docs()`` wrote them, a test that built
``spec.rows`` straight from ``type_registry.specs()`` passed after a build had run in the same
process and raised ``KeyError`` before one, which turned main red when the CI shard plan
reordered the food pantry tests (gen#1040). This check runs in a fresh interpreter, so that no
earlier test's build can fill the table for it.
"""

from __future__ import annotations

import json
import subprocess
import sys

_PROBE = """
import json
from synthetic_ecommerce_data.domains.retail import type_registry
from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS
specs = type_registry.specs()
rows = [r for s in specs.values() for r in (*s.rows, *(d.row for d in s.decoys))]
print(json.dumps(sorted({r.brand for r in rows} - OWNERS.keys())))
"""


def test_every_spec_brand_has_an_owner_before_any_build() -> None:
    out = subprocess.run(
        [sys.executable, "-c", _PROBE], capture_output=True, text=True, check=True, timeout=120
    )
    assert json.loads(out.stdout) == [], "spec brands with no owner before a build"

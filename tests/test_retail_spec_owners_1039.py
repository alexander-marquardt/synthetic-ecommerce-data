"""Every registered spec's rows give their documents in a fresh interpreter (gen#1039).

``Row.doc()`` reads a brand's owner from ``breadth_row.OWNERS``, which modules fill as they are
imported. ``type_specs/granola.py`` and ``flour.py`` (gen#988) state their brands' owners on the
spec (``owners=``), and ``type_registry.specs()`` did not register them: in a fresh interpreter,
``specs()["granola"].rows[i].doc()`` raised ``KeyError: 'Goldfield Farms'``.
``tests/test_retail_food_pantry_964.py`` passed alone (building the ceiling registers the brand)
and failed in CI on a worker where nothing had (``tests (12)`` of synth#1020). This test runs in a
new interpreter, so what other test files imported first cannot hide a spec whose rows need an
owner that loading the registry does not give.
"""

from __future__ import annotations

import subprocess
import sys

#: Loads the registry and nothing else, then asks every row and decoy of every spec for its
#: document; prints one line per row that fails.
PROBE = """
from synthetic_ecommerce_data.domains.retail import type_registry

failed = []
for key, spec in type_registry.specs().items():
    for row in [*spec.rows, *(d.row for d in spec.decoys)]:
        try:
            row.doc()
        except Exception as exc:
            failed.append(f"{key} {row.code}: {type(exc).__name__}: {exc}")
print("\\n".join(failed) or "ok")
"""


def test_every_spec_row_gives_its_document_in_a_fresh_interpreter() -> None:
    done = subprocess.run(
        [sys.executable, "-c", PROBE], capture_output=True, text=True, timeout=300, check=False
    )
    assert done.returncode == 0, done.stderr[-2000:]
    assert done.stdout.strip() == "ok", done.stdout[-2000:]

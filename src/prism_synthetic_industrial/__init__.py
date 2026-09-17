"""PRISM customization for the synthetic industrial catalog.

The package name is not a style choice: PRISM's loader globs
``src/prism_*/data/customization.yaml`` inside whatever
``PRISM_CUSTOMIZATION_PATH`` points at, and requires exactly one match. The
directory has to be called ``prism_<something>`` or the Engine finds nothing.

Everything under ``data/field_weights/`` is GENERATED from the catalog by
``sip-generate build``. See ``synthetic_industrial_products.prism.field_map``.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["CUSTOMIZATION_ROOT", "FIELD_MAP_PATH", "PERSONA", "FLAT_INDEX"]

#: The directory PRISM globs.
CUSTOMIZATION_ROOT = Path(__file__).resolve().parent / "data"

#: The generated field map, as referenced from ``customization.yaml``.
FIELD_MAP_PATH = CUSTOMIZATION_ROOT / "field_weights" / "synthetic_industrial_flat.yaml"

#: The single persona declared in ``customization.yaml``.
PERSONA = "Industrial"

#: The index that persona searches. Test-cluster naming (``test-<date>-*``) is
#: deliberate and matches ``scripts/verify_elasticsearch.py``: this catalog is
#: synthetic and its index is only ever loaded into a local test cluster.
FLAT_INDEX = "test-2026-09-17-sip-flat"

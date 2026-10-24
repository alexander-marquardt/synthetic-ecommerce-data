"""noun -> the category node of the product the noun really names, one module per topic (gen#659).

The class-8 test (``test_retail_product_word_decoys_326.py``) needs, for each product noun a
decoy title holds, the node of the product the noun really names: a decoy never sits in it. The
rows were one dict in that test, so every feature that added a decoy noun edited it and any two
conflicted. Each topic is now a module of this package with a ``NODES`` dict; a new topic is a new
file, found here by its name, and nothing is listed. A noun two modules map differently raises.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path


def _load() -> dict[str, str]:
    merged: dict[str, str] = {}
    owner: dict[str, str] = {}
    for info in sorted(pkgutil.iter_modules([str(Path(__file__).parent)]), key=lambda i: i.name):
        nodes = importlib.import_module(f"{__name__}.{info.name}").NODES
        for noun, node in nodes.items():
            if merged.setdefault(noun, node) != node:
                raise ValueError(
                    f"{noun!r}: {owner[noun]} says {merged[noun]!r}, {info.name} says {node!r}"
                )
            owner.setdefault(noun, info.name)
    return merged


TRUE_NODE: dict[str, str] = _load()

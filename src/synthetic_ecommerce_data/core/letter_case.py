"""One letter case for every category node and attribute display name (gen#499): the stub.

The red commit of gen#499: the guard (``tests/test_letter_case_499.py``) imports this module and
the module does nothing yet. The next commit replaces it with the sentence-case rule.
"""

from __future__ import annotations

from typing import Any

PROPER_NOUNS: dict[str, str] = {}


def sentence_case(name: str) -> str:
    return name


def apply(doc: dict[str, Any]) -> dict[str, Any]:
    return dict(doc)

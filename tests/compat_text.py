"""Recognise the cross-reference sentences a record's copy carries.

Written here, from the six sentence shapes, rather than imported from
:mod:`synthetic_industrial_products.catalog.compat`: the tests that check the
sentences must not find them with the machinery that wrote them.
"""

from __future__ import annotations

import re

#: One alternative per sentence shape, in the order :func:`compat.sentence_for`
#: dispatches: hex key, socket screw, tap, drill, nut, washer.
COMPATIBILITY = re.compile(
    r"For (?P<screws>.+?) socket head cap screws \((?P<standard>ISO 4762|ASME B18\.3)\)\."
    r"|Takes a (?P<key>\S+) hex key\."
    r"|For (?P<tapped>\S+) threads(?:; tap drill (?P<tap_drill>\S+))?\."
    r"|Tap drill for (?P<drilled>.+?) threads\."
    r"|Fits (?P<nut>\S+) bolts and screws\."
    r"|For (?P<washer>M\d+) bolts and screws\."
)


def compatibility_sentences(description: str) -> list[re.Match[str]]:
    return list(COMPATIBILITY.finditer(description))


def without_compatibility(description: str) -> str:
    """The description with its cross-reference sentence (and its space) removed."""
    return re.sub(r"\s*(?:" + COMPATIBILITY.pattern + r")", "", description)

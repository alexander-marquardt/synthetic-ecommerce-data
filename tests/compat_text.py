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


#: The noise sentences (``catalog/noise.py``), one alternative per type.
NOISE = re.compile(
    r"Not for (?P<not_threads>.+?) threads\."
    r"|Will not fit (?P<not_socket>\S+) sockets\."
    r"|Also available in (?P<siblings>.+?) sizes\."
    r"|(?P<eq_value>\S+(?: mm| in\.?)?) \(approx\. (?P<eq_other>\S+)\)\."
    r"|Bore (?P<bore_low>[\d.]+)-(?P<bore_high>[\d.]+)mm \(ISO 492 Normal class\)\."
    r"|Pair with (?P<pair_thread>\S+) hex nuts"
    r"(?: and a (?P<pair_key>\S+) hex key| and (?P<pair_washer>M\d+) flat washers)?\."
    r"|(?P<contrast>(?:Zinc-plated (?:steel|alloy steel) \(not stainless\)"
    r"|(?<!\S)[\w-][\w -]*?Stainless Steel \(not plated\)"
    r"|Brass \(not steel\)|Note: not alloy steel))\."
    r"|Suitable for (?P<cuts>[a-z ,]+)\."
    r"|Equivalent to (?P<equivalent>DIN [\w-]+) / (?P<standard>ISO \d+)\."
    r"|Higher strength than (?P<weaker>(?:Class|Grade) [\d.]+)\."
    r"|(?P<application>For use with socket cap screws)\."
)


def noise_sentences(description: str) -> list[re.Match[str]]:
    return list(NOISE.finditer(description))


def compatibility_sentences(description: str) -> list[re.Match[str]]:
    return list(COMPATIBILITY.finditer(description))


def without_compatibility(description: str) -> str:
    """The description with its cross-reference and noise sentences (and their
    spaces) removed: what the brand template and the spec clause say alone."""
    stripped = re.sub(r"\s*(?:" + COMPATIBILITY.pattern + r")", "", description)
    return re.sub(r"\s*(?:" + NOISE.pattern + r")", "", stripped)

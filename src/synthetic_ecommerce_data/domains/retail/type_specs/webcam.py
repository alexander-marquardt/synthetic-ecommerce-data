"""Webcams (gen#956, slice 3a): Electronics > Computers > Webcams.

A breadth type: ``derivable`` True, so the scaled build draws more webcams from these rows by the
values their titles show (a resolution, a feature, a use, or a resolution and a use). The
resolutions are ``Full HD`` and ``4K``, never ``1080p``: a swap reads an all-lowercase word
such as ``1080p`` as lower case and would write ``4k``. The body is the SKU's color. ``webcam_use`` draws a round streaming camera or a wide conference bar with
speaker grilles, and ``webcam_feature`` draws a ring light around the lens or a privacy shutter
above it (:func:`kit_gadgets.webcam`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    CINDREL,
    DASKEL,
    DUNVALE,
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    NIMBREL,
    PELLIMAR,
    QUORRIN,
)
from synthetic_ecommerce_data.domains.retail.gadgets_rows import (
    BLACK,
    WEBCAMS,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _wc(code: str, title: str, brand: str, price: float, description: str, resolution: str,
        use: str, feature: str) -> object:  # fmt: skip
    attrs = (a("webcam_resolution", "Webcam resolution", resolution),
             a("webcam_use", "Webcam use", use),
             a("webcam_feature", "Webcam feature", feature))  # fmt: skip
    return row(code, title, brand, WEBCAMS, "Webcam", "webcam", price, description, attrs,
               (("webcam_use", use.lower()), ("webcam_feature", feature.lower())))  # fmt: skip


ROWS = (
    _wc("WBC001", "4K Webcam", HALVERN, 99.0,
        "Sharp, true-color video for calls and recordings, with autofocus on your face.", "4K", "Streaming", "Privacy Shutter"),
    _wc("WBC002", "Full HD Webcam", CINDREL, 35.0,
        "Full HD video and a clip that fits any laptop lid or monitor.", "Full HD", "Streaming", "Privacy Shutter"),
    _wc("WBC003", "Webcam with Ring Light", NIMBREL, 59.0,
        "A dimmable ring of light around the lens keeps your face lit at night.", "Full HD", "Streaming", "Ring Light"),
    _wc("WBC004", "Webcam with Privacy Shutter", DUNVALE, 39.0,
        "Slide the cover over the lens when the call ends, and no one can see in.", "Full HD", "Conference", "Privacy Shutter"),
    _wc("WBC005", "Streaming Webcam", QUORRIN, 79.0,
        "Sixty frames a second and a wide lens for live streams and game play.", "4K", "Streaming", "Ring Light"),
    _wc("WBC006", "Conference Webcam", MARRICK, 129.0,
        "A wide lens and two microphones that pick up a whole meeting room table.", "Full HD", "Conference", "Privacy Shutter"),
    _wc("WBC007", "4K Streaming Webcam", DASKEL, 119.0,
        "Ultra HD streams with a built-in light and a mount for a tripod.", "4K", "Streaming", "Ring Light"),
    _wc("WBC008", "Full HD Conference Webcam", PELLIMAR, 89.0,
        "A bar camera with speakers on both ends for small meeting rooms.", "Full HD", "Conference", "Privacy Shutter"),
)  # fmt: skip

SPEC = TypeSpec(
    key="webcam",
    department=DEPARTMENT,
    product_type="Webcam",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "blue webcam", "vocabulary", decoy(ROWS[0], "WBCBSL", "4K Webcam with Blue Status Light",
              "A black 4K webcam with a small blue light that shows when it is on.", BLACK)),
        Decoy(6, "yellow webcam", "generic", decoy(ROWS[5], "WBCYBK", "Yellow Brook Conference Webcam",
              "From the Yellow Brook range: a conference webcam in white.", WHITE)),
    ),
)  # fmt: skip

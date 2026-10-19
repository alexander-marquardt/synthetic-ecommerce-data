"""A derived style draws what its attributes state, and the kit draws every one (gen#512).

``scale.derive`` swaps a changed attribute value into the drawing's params. A clog's ``strap``
attribute reads "Back strap" or "None" while the drawing's ``strap`` param is the kit's word
("back" or "none"), so the swap wrote ``strap='back strap'`` into a derived clog's drawing, which
``image_release.py --skus 200000`` could not render, and left a clog that states "Strap: None"
drawn with a back strap.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import image_release  # noqa: E402
import scale  # noqa: E402

#: The kit's word for each strap attribute value: written here, not read from the source.
STRAP_DRAWN = {"Back strap": "back", "None": "none"}
#: (clog template, the strap value it is derived to): each differs from the template's own.
CLOG_STRAPS = [
    ("FTW-WCLEVA", "None"),
    ("FTW-MCLWOD", "Back strap"),
    ("FTW-WCLFLC", "Back strap"),
]


def _derive(tpl: dict, values: dict[str, str]) -> dict:
    colors = [c["color"] for c in tpl.get("color_options", ())][:1]
    owners = {tpl["brand"]: "own"}
    return scale.derive(
        tpl, "BRD-TEST", "Ashcombe", tpl["brand"], values, colors, owners, random.Random(0)
    )


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.derivable(scale.templates())


@pytest.mark.parametrize(("pid", "strap"), CLOG_STRAPS)
def test_a_derived_clog_draws_the_strap_its_attribute_states(templates, pid, strap):
    tpl = next(t for t in templates if t["product_id"] == pid)
    rec = _derive(tpl, {"strap": strap})
    states = {a["key"]: a["value"] for a in rec["attributes"]}
    assert states["strap"] == strap
    assert rec["drawing"]["params"]["strap"] == STRAP_DRAWN[strap]
    image_release.image_files([rec])  # the kit draws it: the release stops on a refusal


def test_every_value_the_scale_can_derive_to_is_one_the_kit_draws(templates):
    """The class behind the clog: a style the scale derives to a value the drawing refuses stops
    the release at the build's tail (``--skus 200000``), so each template is derived to each
    value of its pools here and every image it names is rendered."""
    pools = scale.value_pools(templates)
    derived = 0
    for tpl in templates:
        if not tpl["drawing"].get("params"):
            continue
        for key in scale.variable_keys(tpl, pools):
            own = next(str(a["value"]) for a in tpl["attributes"] if a["key"] == key)
            for value in pools[(tpl["category_leaf"], key)]:
                if value == own:
                    continue
                rec = _derive(tpl, {key: value})
                try:
                    image_release.image_files([rec])
                except ValueError as err:
                    raise AssertionError(f"{tpl['product_id']} {key}={value!r}: {err}") from err
                derived += 1
    assert derived >= 300, "the sweep reached too few derived styles to guard the class"

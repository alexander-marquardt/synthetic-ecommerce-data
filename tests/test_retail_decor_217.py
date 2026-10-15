"""Home accessories and decor (gen#217): clocks, ornaments, artificial flowers, trays, door stops,
wallpaper, greeting cards, diaries and picnic blankets.

:mod:`decor_rows` holds the styles and :mod:`kit_decor` draws them. These checks hold what the
issue asked for: every type has its range (three styles from three brands), each draws as its own
shape with the params listed, each key attribute is a structured entry in the export, a coloured
type offers the six main colors, every type carries text-match decoys whose fields tell the truth,
and the rows are templates the derivation leaves alone.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decor_rows  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_decor  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

TYPE_ROWS = decor_rows.TYPE_ROWS
#: Each type and the key attributes every one of its styles states (the issue's table).
KEYS = {
    "Clock": {"clock_type", "finish", "silent_movement", "diameter", "color"},
    "Ornament": {"material", "occasion", "form", "color"},
    "Artificial Flowers": {"flower", "holder", "item_height", "color"},
    "Decorative Tray": {"material", "tray_shape", "color"},
    "Door Stop": {"material", "weight", "color"},
    "Wallpaper": {"pattern", "finish", "roll_length", "color"},
    "Greeting Card": {"occasion", "card_size", "design"},
    "Diary": {"diary_year", "page_layout", "color"},
    "Picnic Blanket": {"waterproof_backing", "dimensions", "color"},
}
#: The shape of each type and the param that changes its picture, with two readings.
PARAMS = {
    "clock": ("type", "wall", "alarm"),
    "ornament": ("form", "vase", "bird"),
    "stems": ("flower", "eucalyptus", "pampas"),
    "trinket_tray": ("outline", "round", "rectangular"),
    "wallpaper": ("finish", "matt", "metallic"),
    "greeting_card": ("design", "balloons", "cake"),
    "diary": ("band", "no", "yes"),
    "picnic_blanket": ("backing", "plain", "waterproof"),
    "door_stop": ("kind", "wedge", "weighted"),
}
TITLE_WORD = {
    "Clock": "clock", "Ornament": "ornament", "Artificial Flowers": "stems",
    "Decorative Tray": "tray", "Door Stop": "door stop", "Wallpaper": "wallpaper",
    "Greeting Card": "card", "Diary": "diary", "Picnic Blanket": "picnic blanket",
}  # fmt: skip


def _keys(row) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


def _by_type() -> dict[str, list]:
    out: dict[str, list] = collections.defaultdict(list)
    for r in TYPE_ROWS:
        out[r.product_type].append(r)
    return out


def test_every_type_is_there_with_three_styles_from_three_brands() -> None:
    styles = _by_type()
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()
            if len(rs) < 3 or len({r.brand for r in rs}) < 3}  # fmt: skip
    assert thin == {}


def test_every_style_draws_as_its_own_registered_shape() -> None:
    assert {r.code: r.shape for r in TYPE_ROWS if r.shape not in kit_decor.SHAPES} == {}
    assert {r.shape for r in TYPE_ROWS} == set(PARAMS)
    assert {r.shape for r in TYPE_ROWS} & {"box", "box_wide"} == set()


@pytest.mark.parametrize("row", TYPE_ROWS, ids=lambda r: r.code)
def test_each_key_attribute_is_a_structured_entry_in_the_export(row) -> None:
    assert KEYS[row.product_type] <= _keys(row), row.code


@pytest.mark.parametrize("shape", sorted(PARAMS))
def test_a_param_changes_the_drawing(shape: str) -> None:
    param, one, other = PARAMS[shape]
    fill = kit.Fill("solid", "#c8312e", "#ffffff", "#f2d14b")

    def svg(**params) -> str:
        return kit.render(shape, fill, None, params=params)

    assert svg(**{param: one}) != svg(**{param: other})
    assert svg() == svg(**{param: one}), "the default is the first reading"


def test_a_card_sku_draws_its_own_design() -> None:
    row = next(r for r in TYPE_ROWS if r.code == "GRCBDY")
    designs = [s["design"] for s in row.skus()]
    assert len(set(designs)) == len(designs) >= 2
    fill = kit.Fill("solid", "#f4f1ea", "#9a9ca0", "#f2d14b")
    drawn = {kit.render("greeting_card", fill, None, params={"design": d}) for d in designs}
    assert len(drawn) == len(designs)


def test_a_coloured_type_offers_the_six_main_colors() -> None:
    styles = {t: [r.doc() for r in rs] for t, rs in _by_type().items() if t != "Greeting Card"}
    lacking = {}
    for ptype, docs in styles.items():
        offered = main_colors.offered(docs)
        lacking[ptype] = [c for c in main_colors.MAIN_COLORS if c not in offered]
    assert {t: c for t, c in lacking.items() if c} == {}


def test_every_type_carries_text_match_decoys_that_tell_the_truth() -> None:
    """A decoy's title holds the type's word while its own type is another (gen#294)."""
    decoys = collections.defaultdict(list)
    for d in decor_rows.DECOYS:
        for ptype, word in TITLE_WORD.items():
            if word in d.title.lower() or (word == "stems" and "stem" in d.title.lower()):
                decoys[ptype].append(d)
    assert {t: len(decoys[t]) for t in KEYS if len(decoys[t]) < 2} == {}
    assert not {d.product_type for d in decor_rows.DECOYS} & set(KEYS)
    assert all(len(d.title.split()) <= 5 for d in decor_rows.DECOYS)
    assert all(len(d.colors) == 1 for d in decor_rows.DECOYS)


def test_the_decor_rows_are_templates_and_the_decoys_are_exempt_from_the_text_check() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert scale.DECOR_IDS and not (scale.DECOR_IDS & kept)
    assert decor_rows.decoy_ids() <= scale.DECOY_IDS


def test_the_rows_meet_the_output_standard_and_the_tree_rules() -> None:
    docs = [d for d in scale.templates() if d["product_id"] in scale.DECOR_IDS]
    assert len(docs) == len(decor_rows.ROWS)
    standard = [export.standard_document(d) for d in docs]
    assert check_catalog(standard, one_class_per_key=True, text_exempt=scale.DECOY_IDS) == []
    paths = [tuple(r.path) for r in TYPE_ROWS]
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert {p[-1] for p in paths} >= {"Wall Clocks", "Mantel Clocks", "Alarm Clocks", "Wallpaper"}

"""Home accessories and decor (gen#217): clocks, ornaments, artificial flowers, trays, door stops,
wallpaper, diaries and picnic blankets.

Each type is a spec under ``type_specs/`` (gen#351) and :mod:`kit_decor` draws it; :mod:`decor_rows`
holds the shared parts and the text-match decoys of other departments. These checks hold what the
issue asked for: every type has its range (three styles from three brands), each draws as its own
shape with the params listed, each key attribute is a structured entry in the export, a colored
type offers the six main colors, every type carries text-match decoys whose fields tell the truth,
and the decoys are templates the derivation leaves alone. Greeting cards came with gen#425.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

#: Each spec key with the key attributes every one of its styles states (the issue's table).
KEYS = {
    "clock": {"clock_type", "finish", "silent_movement", "diameter", "color"},
    "ornament": {"material", "occasion", "form", "color"},
    "artificial_flowers": {"flower", "holder", "item_height", "color"},
    "decorative_tray": {"material", "tray_shape", "color"},
    "door_stop": {"material", "weight", "color"},
    "wallpaper": {"pattern", "finish", "roll_length", "color"},
    "diary": {"diary_year", "page_layout", "color"},
    "picnic_blanket": {"waterproof_backing", "dimensions", "color"},
}
#: The shape of each type and the params that change its picture, each with two readings.
PARAMS = {
    "clock": (("type", "wall", "alarm"),),
    "ornament": (("form", "vase", "bird"),),
    "stems": (("flower", "eucalyptus", "pampas"), ("holder", "loose", "vase")),
    "trinket_tray": (("outline", "round", "rectangular"),),
    "wallpaper": (("finish", "matt", "metallic"),),
    "diary": (("band", "no", "yes"),),
    "picnic_blanket": (("backing", "plain", "waterproof"),),
    "door_stop": (("kind", "wedge", "weighted"),),
}
#: A shape a spec draws with no param: one fixed picture (the seasonal pumpkin ornament, #565).
FIXED_SHAPES = {"pumpkin"}
#: The word a shopper types for each product type, and the decoys' title must hold.
TITLE_WORD = {
    "Clock": "clock", "Ornament": "ornament", "Artificial Flowers": "stems",
    "Decorative Tray": "tray", "Door Stop": "door stop", "Wallpaper": "wallpaper",
    "Greeting Card": "card", "Diary": "diary", "Picnic Blanket": "picnic blanket",
}  # fmt: skip


def _specs():
    registry = type_registry.specs()
    return {k: registry.get(k) for k in KEYS}


def _rows():
    return [r for s in _specs().values() if s for r in s.rows]


def _keys(row) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


def test_every_type_is_a_spec_with_three_styles_from_three_brands() -> None:
    specs = _specs()
    assert [k for k, s in specs.items() if s is None] == []
    thin = {k: (len(s.rows), len({r.brand for r in s.rows})) for k, s in specs.items()
            if len(s.rows) < 3 or len({r.brand for r in s.rows}) < 3}  # fmt: skip
    assert thin == {}


def test_every_style_draws_as_its_own_registered_shape() -> None:
    rows = _rows()
    assert {r.code: r.shape for r in rows if r.shape not in kit.SHAPES} == {}
    assert {r.shape for r in rows} == set(PARAMS) | FIXED_SHAPES
    assert {r.shape for r in rows} & {"box", "box_wide"} == set()


def test_a_style_names_the_reading_its_params_pick() -> None:
    """Two styles that differ on the variant axis carry different params, so they draw apart."""
    rows = _rows()
    for shape in PARAMS:
        picked = {tuple(r.params) for r in rows if r.shape == shape}
        assert len(picked) >= 2, shape


def test_each_key_attribute_is_a_structured_entry_in_the_export() -> None:
    by_key = {k: s for k, s in _specs().items() if s}
    missing = {r.code: sorted(KEYS[k] - _keys(r)) for k, s in by_key.items() for r in s.rows
               if KEYS[k] - _keys(r)}  # fmt: skip
    assert missing == {}
    assert len(by_key) == len(KEYS)


@pytest.mark.parametrize("shape", sorted(PARAMS))
def test_a_param_changes_the_drawing(shape: str) -> None:
    fill = kit.Fill("solid", "#c8312e", "#ffffff", "#f2d14b")

    def svg(**params) -> str:
        return kit.render(shape, fill, None, params=params)

    for param, one, other in PARAMS[shape]:
        assert svg(**{param: one}) != svg(**{param: other}), param
        assert svg() == svg(**{param: one}), "the default is the first reading"


def test_a_colored_type_offers_the_six_main_colors() -> None:
    lacking = {}
    for key, spec in _specs().items():
        if spec is None:
            lacking[key] = list(main_colors.MAIN_COLORS)
            continue
        offered = main_colors.offered([r.doc() for r in spec.rows])
        lacking[key] = [c for c in main_colors.MAIN_COLORS if c not in offered]
    assert {k: c for k, c in lacking.items() if c} == {}


def test_every_type_carries_text_match_decoys_that_tell_the_truth() -> None:
    """A decoy's title holds the type's word while its own type is another (gen#294)."""
    import decor_rows

    decoys = collections.defaultdict(list)
    for d in decor_rows.DECOYS:
        for ptype, word in TITLE_WORD.items():
            if word in d.title.lower() or (word == "stems" and "stem" in d.title.lower()):
                decoys[ptype].append(d)
    assert {t: len(decoys[t]) for t in TITLE_WORD if len(decoys[t]) < 2} == {}
    assert not {d.product_type for d in decor_rows.DECOYS} & set(TITLE_WORD)
    assert all(len(d.title.split()) <= 5 for d in decor_rows.DECOYS)
    assert all(len(d.colors) == 1 for d in decor_rows.DECOYS)


def test_a_watch_carries_the_word_clock_and_is_still_a_watch() -> None:
    """The issue's watch-against-clock decoy: a digital watch with an alarm clock mode."""
    spec = type_registry.specs()["digital_watch"]
    decoy = next(d.row for d in spec.decoys if "clock" in d.row.title.lower())
    assert decoy.product_type == "Digital Watch"
    assert "clock" in decoy.title.lower()


def test_the_decoys_are_templates_and_exempt_from_the_text_check() -> None:
    import decor_rows

    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert decor_rows.decoy_ids() and not (decor_rows.decoy_ids() & kept)
    assert decor_rows.decoy_ids() <= scale.DECOY_IDS
    built = {r["product_id"] for r in scale.templates()}
    assert decor_rows.decoy_ids() <= built


def test_the_types_reach_the_scaled_build_and_meet_the_standard_and_the_tree_rules() -> None:
    ids = frozenset().union(*(type_registry.ids_of(s) for s in _specs().values() if s))
    docs = [d for d in scale.templates() if d["product_id"] in ids]
    assert len(docs) == len(ids) > 0
    standard = [export.standard_document(d) for d in docs]
    assert check_catalog(standard, one_class_per_key=True, text_exempt=scale.DECOY_IDS) == []
    paths = [tuple(r.path) for r in _rows()]
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert {p[-1] for p in paths} >= {"Wall Clocks", "Mantel Clocks", "Alarm Clocks", "Wallpaper"}
    assert not ids & {r["product_id"] for r in scale.derivable(scale.templates())}

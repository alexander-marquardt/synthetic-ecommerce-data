"""One quantity has one display label, and two quantities never share one.

Real distributor catalogs label a thread pitch, a bore, a head, an inside and an
outside diameter the same way wherever they appear, and keep a roller chain's
link ``Pitch`` apart from a tap's ``Thread Pitch``. A type word is kept only for
a closed per-type vocabulary or a mixed-category facet, so these five labels
carry none of their own. The machine key derives from the label, so the keys
move with the labels.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog.config import SMALL
from synthetic_industrial_products.catalog.entry import entry_key
from synthetic_industrial_products.catalog.generate import generate


def _published() -> dict[str, set[tuple[str, str]]]:
    """Per type, the ``(name, key)`` pairs its lines publish, children included."""
    found: dict[str, set[tuple[str, str]]] = {}
    for line in generate(SMALL).lines:
        pairs = found.setdefault(line.type_key, set())
        for owner in (line, *line.children):
            pairs.update((a.name, a.key or entry_key(a.name)) for a in owner.attributes)
    return found


PUBLISHED = _published()


def _types_with(label: str) -> set[str]:
    return {t for t, pairs in PUBLISHED.items() if any(name == label for name, _ in pairs)}


@pytest.mark.parametrize(
    "old,new,key,types",
    [
        ("Pitch", "Thread Pitch", "thread_pitch", {"tap_spiral_point"}),
        ("Bore", "Bore Dia.", "bore_dia", {"bearing_radial_ball", "pillow_block_bearings"}),
        ("Head Diameter", "Head Dia.", "head_dia", {"cotter_pins"}),
        ("Inside Diameter", "Inside Dia.", "inside_dia", {"retaining_rings_external"}),
        ("Outside Diameter", "Outside Dia.", "outside_dia", {"roller_chain_sprockets"}),
    ],
)
def test_the_renamed_label_is_published_under_its_new_key(old, new, key, types):
    for type_key in types:
        pairs = PUBLISHED[type_key]
        assert (new, key) in pairs, (type_key, sorted(pairs))
        assert old not in {name for name, _ in pairs}, (type_key, old)


def test_no_type_publishes_one_of_the_retired_labels():
    retired = {"Bore", "Head Diameter", "Inside Diameter", "Outside Diameter"}
    stale = {t: sorted(retired & {n for n, _ in pairs}) for t, pairs in PUBLISHED.items()}
    assert {t: names for t, names in stale.items() if names} == {}


def test_only_chain_and_sprockets_publish_the_bare_pitch():
    assert _types_with("Pitch") == {
        "roller_chain",
        "roller_chain_links",
        "roller_chain_sprockets",
    }


def test_one_label_means_one_machine_key_and_back():
    """Across every type: a name has one key, and a key has one name."""
    keys_of: dict[str, set[str]] = {}
    names_of: dict[str, set[str]] = {}
    for pairs in PUBLISHED.values():
        for name, key in pairs:
            keys_of.setdefault(name, set()).add(key)
            names_of.setdefault(key, set()).add(name)
    split_names = {n: sorted(k) for n, k in keys_of.items() if len(k) != 1}
    shared_keys = {k: sorted(n) for k, n in names_of.items() if len(n) != 1}
    assert split_names == {}
    assert shared_keys == {}

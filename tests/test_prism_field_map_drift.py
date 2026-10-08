"""The committed PRISM field map must match what this catalog produces.

The catalog publishes 77 distinct attribute names across 12 product types. A
field map is a declaration of every attribute PRISM should search, filter and
facet, so a hand-maintained one is 77 statements that have to stay true of
generated data -- and it drifts the first time either side moves. The drift is
silent in the direction that matters: a field map naming an attribute the
catalog no longer publishes does not raise, it just stops faceting, and "no
product has that value" looks identical to "the field map is wrong".

So the field map is generated, and this test is the gate. It fails if:

  * the committed file is edited by hand, or
  * the generator changes what it emits and nobody re-ran the build.

Both directions are proven by ``scripts/mutation_check.py``.
"""

from __future__ import annotations

import pytest

from prism_synthetic_industrial import FIELD_MAP_PATH
from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.prism.field_map import STRUCTURAL_NAMES, render

REBUILD = "uv run ecom-generate build --out out/catalog"


@pytest.fixture(scope="module")
def flat_rows() -> list[dict]:
    """The DEFAULT catalog -- the one the committed field map describes.

    Deliberately not parameterised. The committed artifact describes one
    catalog, and checking it against a different one would be checking the
    wrong thing.
    """
    return list(emit.iter_flat(generate(GeneratorConfig())))


def test_committed_field_map_matches_a_fresh_derivation(flat_rows: list[dict]) -> None:
    expected = render(flat_rows)
    actual = FIELD_MAP_PATH.read_text(encoding="utf-8")
    if actual == expected:
        return

    # A whole-file diff of a 550-line generated YAML is unreadable. Report the
    # first differing line and the line counts, which is what tells the reader
    # whether an entry moved, was added, or had a number change.
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    first = next(
        (i for i, (a, b) in enumerate(zip(actual_lines, expected_lines, strict=False)) if a != b),
        min(len(actual_lines), len(expected_lines)),
    )
    context = "\n".join(
        f"  {label}: {line}"
        for label, line in (
            ("committed", actual_lines[first] if first < len(actual_lines) else "<EOF>"),
            ("derived  ", expected_lines[first] if first < len(expected_lines) else "<EOF>"),
        )
    )
    pytest.fail(
        f"{FIELD_MAP_PATH} disagrees with a fresh derivation from the catalog.\n"
        f"committed {len(actual_lines)} lines, derived {len(expected_lines)} lines; "
        f"first difference at line {first + 1}:\n{context}\n\n"
        f"The field map is GENERATED. If the generator changed, rebuild it:\n"
        f"    {REBUILD}\n"
        f"If you edited the field map by hand, move the change into "
        f"synthetic_ecommerce_data/prism/field_map.py instead."
    )


def test_every_declared_source_exists_in_the_emitted_documents(flat_rows: list[dict]) -> None:
    """A declared ``source`` PRISM cannot find is a boot failure against a live
    index, and this catches it without a cluster.

    The engine's own ``validate_field_maps_against_es_startup`` makes the same
    check against the live mapping. That one needs Elasticsearch; this one
    needs only the emitted documents, so it runs in CI.
    """
    yaml = pytest.importorskip("yaml")
    field_map = yaml.safe_load(FIELD_MAP_PATH.read_text(encoding="utf-8"))

    from synthetic_ecommerce_data.prism.index import (
        CATEGORY_PATH_FIELD,
        project,
    )

    emitted: set[str] = set()
    for row in flat_rows:
        projected = project(row)
        for key, value in projected.items():
            emitted.add(key)
            if key in ("facets", "facets_num"):
                emitted.update(f"{key}.{sub}" for sub in value)

    # Sub-fields the index mapping adds that no document carries as a key.
    emitted.update({"brand.text", "series.text", CATEGORY_PATH_FIELD})

    missing = sorted(
        entry["source"] for entry in field_map["fields"] if entry["source"] not in emitted
    )
    assert not missing, (
        f"the field map declares source(s) no emitted document carries: {missing}. "
        f"PRISM refuses to boot on a source absent from the index mapping."
    )


def test_field_map_declares_exactly_one_id_entry() -> None:
    """PRISM requires exactly one ``type: id`` entry and refuses otherwise."""
    yaml = pytest.importorskip("yaml")
    field_map = yaml.safe_load(FIELD_MAP_PATH.read_text(encoding="utf-8"))
    ids = [e["name"] for e in field_map["fields"] if e["type"] == "id"]
    assert ids == ["id"], f"expected exactly one id entry, found {ids}"


def test_no_attribute_silently_redefines_a_structural_field(flat_rows: list[dict]) -> None:
    """An attribute whose key is a structural name is NAMESPACED, never shadowing it.

    The catalog really carries one: a bearing's ``Series`` (``62``) sanitises
    to ``series``, the product line's own column. The structural ``series``
    entry must still point at the column, and the attribute must get its own
    ``attr_series`` entry over ``facets.series`` -- the general rule in
    ``field_map.canonical_name``, since real feeds publish ``Series``,
    ``Product Type`` and ``Brand`` as attributes too.
    """
    import yaml

    from synthetic_ecommerce_data.prism.derive import measure
    from synthetic_ecommerce_data.prism.field_map import canonical_name

    colliding = sorted(set(measure(flat_rows)) & STRUCTURAL_NAMES)
    assert colliding == ["series"], colliding
    fields = {f["name"]: f for f in yaml.safe_load(render(flat_rows))["fields"]}
    assert fields["series"]["source"] == "series", "the structural column was shadowed"
    assert fields[canonical_name("series")]["source"].endswith(".series")
    assert canonical_name("series") == "attr_series"
    assert canonical_name("thread_size") == "thread_size"


def test_namespacing_that_would_itself_collide_is_refused() -> None:
    """``attr_series`` published as an attribute too would clash with the namespaced one."""
    rows = [
        {
            "sku": "A",
            "product_id": "P",
            "product_type": "t",
            "attributes": [
                {"name": "Series", "value": "62"},
                {"name": "attr series", "value": "x"},
            ],
            "facets": {"series": ["62"], "attr_series": ["x"]},
            "facets_num": {},
        }
    ]
    with pytest.raises(ValueError, match="collide"):
        render(rows)


def test_filter_routing_hard_matches_the_derived_range_facets(flat_rows: list[dict]) -> None:
    """``filter_routing.hard`` is the other place the derivation has to reach.

    A RANGE facet absent from ``filter_routing.hard`` renders no range
    selector -- the Engine warns once per facet at boot and the sidebar simply
    has no control for that dimension. The list lives in ``customization.yaml``,
    which is hand-written, so this is the gate that keeps it honest: add a
    range attribute to the catalog and forget to route it, and this reds.

    The OTHER direction is worse than a warning and is why this must track
    CONTINUITY rather than numeracy (elastic/prism#9285): a name here that no
    longer resolves as a range axis makes both Engine and Studio REFUSE TO
    BOOT (#7114). Every dimensional attribute became a discrete list, so the
    routed set is now ``price`` alone -- and leaving the old 27 in place would
    have been a boot failure rather than a missing slider.

    ``price`` is in the routed set but is not a catalog attribute -- it is a
    first-class column -- so it is excluded from the comparison rather than
    asserted into the derivation.
    """
    yaml = pytest.importorskip("yaml")

    from prism_synthetic_industrial import CUSTOMIZATION_ROOT
    from synthetic_ecommerce_data.prism.derive import decide, measure

    config = yaml.safe_load((CUSTOMIZATION_ROOT / "customization.yaml").read_text("utf-8"))
    routed = set(config["filter_routing"]["hard"])

    derived = {
        decision.stats.key
        for decision in (decide(s) for s in measure(flat_rows).values())
        if decision.facet and decision.stats.is_continuous
    }

    missing = sorted(derived - routed)
    extra = sorted(routed - derived - {"price"})
    assert not missing, (
        f"numeric facet(s) {missing} are not in filter_routing.hard — "
        f"their range selector will not render. Add them to customization.yaml."
    )
    assert not extra, (
        f"filter_routing.hard routes {extra}, which the catalog does not derive "
        f"as a numeric facet. Every routed name must resolve as a range axis or "
        f"the Engine and Studio both refuse to boot."
    )

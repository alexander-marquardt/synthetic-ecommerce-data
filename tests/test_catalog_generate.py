"""The generator's contract: shape, determinism, and the measured rates.

The rate assertions carry deliberately wide bounds. These are sampled
quantities, and several of them are *clustered* -- a line-constant attribute
such as Helix Angle carries its defect to every SKU under that line, so the
per-record rate swings with how big the unlucky lines happened to be. A tight
bound on a clustered rate is a flaky test, not a strict one. What the bounds
are tight enough to catch is the failure that matters: a rate that has gone to
zero, or to one, because the mechanism stopped working.
"""

from __future__ import annotations

import pytest

from synthetic_industrial_products.catalog import taxonomy
from synthetic_industrial_products.catalog.config import SMALL, GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.catalog.measure import measure
from synthetic_industrial_products.catalog.vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    STANDARDS_NAME,
    VOCAB,
)


@pytest.fixture(scope="module")
def config():
    return GeneratorConfig(lines=200, seed=99)


@pytest.fixture(scope="module")
def catalog(config):
    return generate(config)


@pytest.fixture(scope="module")
def stats(catalog, config):
    return measure(catalog, config)


def test_the_same_seed_produces_the_same_catalog():
    left = generate(SMALL)
    right = generate(SMALL)
    assert [line.product_id for line in left.lines] == [line.product_id for line in right.lines]
    assert [c.sku for _, c in left.all_skus()] == [c.sku for _, c in right.all_skus()]
    assert [c.title for _, c in left.all_skus()] == [c.title for _, c in right.all_skus()]


def test_a_different_seed_produces_a_different_catalog():
    left = generate(SMALL)
    right = generate(SMALL.with_(seed=SMALL.seed + 1))
    assert [c.sku for _, c in left.all_skus()] != [c.sku for _, c in right.all_skus()]


def test_the_catalog_is_the_size_it_was_asked_for(stats):
    assert stats["lines"] == pytest.approx(200, abs=12)
    assert 1200 <= stats["skus"] <= 4000


def test_every_product_type_is_represented(stats):
    assert set(stats["lines_by_type"]) == set(VOCAB)
    for type_key, count in stats["lines_by_type"].items():
        assert count > 0, type_key


def test_every_sku_code_is_unique(catalog):
    codes = [child.sku for _, child in catalog.all_skus()]
    assert len(codes) == len(set(codes))


def test_a_child_never_redefines_a_name_its_line_already_carries(catalog):
    """The flat shape concatenates parent and child attributes.

    If a child could redefine a name the line already publishes, that
    concatenation would emit the same attribute twice with two values and
    every consumer would have to guess which one wins.
    """
    for line in catalog.lines:
        line_names = line.attribute_names()
        for child in line.children:
            overlap = line_names & child.attribute_names()
            assert not overlap, f"{line.product_id}/{child.sku} redefines {overlap}"


def test_every_line_carries_line_constant_attributes_and_every_child_varies(catalog):
    for line in catalog.lines:
        assert line.attributes, line.product_id
        assert line.children
        for child in line.children:
            assert child.attributes, child.sku


def test_the_category_tree_is_used_and_is_three_or_four_deep(catalog):
    depths = {len(line.category) for line in catalog.lines}
    assert depths <= {3, 4}
    assert depths == taxonomy.tree_depths()


def test_the_multivalued_attribute_exists_and_really_is_multivalued(stats):
    """Without this shape the reverse_nested case cannot be demonstrated."""
    assert stats["standards_present"] > 0
    assert stats["standards_multivalued"] > 0
    assert stats["multivalued_attribute_names"].get(STANDARDS_NAME, 0) > 0
    # More values than records carrying the attribute: that difference IS the
    # over-count a naive nested aggregation reports.
    assert stats["standards_total_values"] > stats["standards_present"]


def test_the_multivalued_attribute_spans_product_types(catalog):
    types_with = {
        line.type_key
        for line in catalog.lines
        if any(a.name == STANDARDS_NAME for a in line.attributes)
    }
    assert len(types_with) >= 6, types_with


def test_attribute_names_are_disjoint_across_unrelated_types_in_the_output(stats):
    """The vocabularies are disjoint by construction; check the OUTPUT is too."""
    screw = set(stats["attribute_names_by_type"]["screw_socket_head"])
    hammer = set(stats["attribute_names_by_type"]["hammer_ball_pein"])
    # The measurement-system attribute is shared on purpose -- it is the one
    # idea every family describes, under three different names. Everything
    # else a threaded fastener and a striking tool publish is disjoint.
    allowed = {"Item", STANDARDS_NAME, *(name for name, _ in MEASUREMENT_SYSTEM_NAMES)}
    assert screw & hammer <= allowed


def test_the_measurement_system_attribute_appears_under_more_than_one_spelling(stats):
    names = stats["measurement_system_names"]
    assert len(names) >= 2, names
    assert "Dimension Type" in names


def test_both_the_role_ambiguity_cases_occur(stats):
    """Shank equal to cutting diameter, and shank different: both, at rate."""
    row = next(c for c in stats["comparisons"] if c.name == "shank == cutting diameter")
    assert row.denominator > 200
    assert 0.55 <= row.achieved <= 0.75, row
    assert row.numerator < row.denominator, "some tools must have differing diameters"


@pytest.mark.parametrize(
    "metric,low,high",
    [
        ("length of cut > overall length", 0.03, 0.16),
        ("angle attribute carries a length unit", 0.005, 0.14),
        ("declared system contradicts value units", 0.005, 0.08),
        ("unit mixing within one record", 0.005, 0.05),
        ("title dimension token unlabelled", 0.38, 0.55),
        ("title dimension token is not the primary dimension", 0.10, 0.25),
    ],
)
def test_each_measured_rate_is_reproduced(stats, metric, low, high):
    row = next(c for c in stats["comparisons"] if c.name == metric)
    assert row.denominator > 0, f"{metric} has an empty denominator"
    assert low <= row.achieved <= high, row


def test_no_title_label_is_truncated(stats):
    """0, exactly -- the one measured rate this catalog declines to reproduce.

    It is asserted rather than dropped from the table, and the denominator is
    asserted non-empty first, because "no truncated titles" and "no titles
    examined" produce the same numerator. The measurement that justified the
    old 3.23% still stands in ``P1_title_grammar.json`` and is still carried
    on ``GeneratorConfig.measured_title_label_truncation``; what changed is
    the decision to reproduce it (elastic/prism#9284).
    """
    row = next(c for c in stats["comparisons"] if c.name == "title label truncated")
    assert row.denominator > 0, "no titles were examined, so a zero proves nothing"
    assert row.numerator == 0, row
    assert row.achieved == 0.0, row


def test_attributes_per_record_is_close_to_the_measured_mean(stats):
    row = next(c for c in stats["comparisons"] if c.name == "attributes per record (mean)")
    assert 11.5 <= row.achieved <= 14.5, row


def test_turning_the_defect_rate_off_produces_a_clean_catalog():
    """The control case: a catalog with no internal contradictions at all.

    It is not what a real catalog looks like, which is the point -- the knob
    exists so a consumer can tell which of their results depend on the noise.
    """
    config = GeneratorConfig(lines=120, seed=5, defect_scale=0.0)
    stats = measure(generate(config), config)
    for name in (
        "length of cut > overall length",
        "angle attribute carries a length unit",
        "declared system contradicts value units",
        "unit mixing within one record",
    ):
        row = next(c for c in stats["comparisons"] if c.name == name)
        assert row.numerator == 0, row


def test_the_sparsity_knob_moves_the_attribute_count():
    ragged = GeneratorConfig(lines=120, seed=5, sparsity_scale=0.3)
    full = GeneratorConfig(lines=120, seed=5, sparsity_scale=1.0)

    def mean_attrs(config):
        stats = measure(generate(config), config)
        return next(
            c for c in stats["comparisons"] if c.name == "attributes per record (mean)"
        ).achieved

    assert mean_attrs(ragged) < mean_attrs(full) - 1.0


def test_the_line_and_sku_count_knobs_move_the_catalog_size():
    small = measure(generate(GeneratorConfig(lines=50, seed=3)))
    large = measure(generate(GeneratorConfig(lines=150, seed=3)))
    assert large["lines"] > small["lines"] * 2
    assert large["skus"] > small["skus"] * 2

    narrow = measure(generate(GeneratorConfig(lines=60, seed=3, skus_per_line=(2, 3))))
    wide = measure(generate(GeneratorConfig(lines=60, seed=3, skus_per_line=(15, 20))))
    assert wide["skus"] > narrow["skus"] * 2


def test_every_child_has_a_title_and_a_price(catalog):
    for _, child in catalog.all_skus():
        assert child.title
        assert child.price_usd > 0
        assert child.stock >= 0


def test_fasteners_carry_their_standard_as_provenance_and_tools_do_not(catalog):
    for line in catalog.lines:
        if line.type_key in ("screw_socket_head", "screw_flat_head", "bolt_hex", "washer_flat"):
            assert any(token in line.dimension_provenance for token in ("ISO", "ASME", "DIN")), (
                f"{line.product_id}: {line.dimension_provenance!r}"
            )
        if line.type_key.startswith("end_mill"):
            assert "generated" in line.dimension_provenance
            assert "ISO" not in line.dimension_provenance
            assert "ASME" not in line.dimension_provenance


def test_every_product_line_and_every_variant_carries_an_image(catalog):
    """100% coverage, asserted on the catalog rather than on the render run.

    The renderer can only draw what the catalog asks for, so the guarantee has
    to start here: a variant with no reference is a blank card however many
    images were rendered.
    """
    lineless = [line.product_id for line in catalog.lines if not line.image_id]
    childless = [child.sku for _, child in catalog.all_skus() if not child.image_id]
    assert lineless == []
    assert childless == []


def test_every_image_reference_names_one_of_the_catalogs_own_product_lines(catalog):
    """Both directions: no dead reference, and no drawing nothing points at."""
    owned = {line.image_id for line in catalog.lines}
    referenced = {line.image_id for line in catalog.lines}
    referenced |= {child.image_id for _, child in catalog.all_skus()}
    assert referenced <= owned, "a reference no line owns is a dead link"
    assert referenced == owned, "a drawing nothing references is dead weight"


def test_every_product_line_has_an_image_of_its_own(catalog):
    """One drawing per line -- not one per type, and not one per SKU.

    The count is the assertion. One per type is what this replaced: the whole
    catalog behind ten pictures, where an Osterlund HSS AlTiN mill and a
    competitor's carbide TiCN mill rendered identically. One per SKU would
    undercut the variant grouping the nested shape exists to demonstrate, where
    N SKUs are ONE product. Either mistake leaves every other check here green.
    """
    ids = [line.image_id for line in catalog.lines]
    assert len(set(ids)) == len(catalog.lines) > 1
    assert catalog.sku_count > len(ids), "a drawing per SKU is not a family sharing one"


def test_a_product_and_its_variants_show_the_same_image(catalog):
    """A family shares one image: that is the measured behaviour being modelled.

    A category listing of four end mills from one series at four diameters
    shows the same photograph four times, and 73.5% of the archived reference
    records point at an image whose id is not the product's own.
    """
    for line in catalog.lines:
        assert line.image_id == taxonomy.image_id_for(line.type_key, line.product_id)
        for child in line.children:
            assert child.image_id == line.image_id


def test_the_image_reference_is_decided_by_the_product_line_alone(catalog):
    """Which is what makes 500 images enough for four thousand products."""
    by_line: dict[str, set[str]] = {}
    for line, child in catalog.all_skus():
        by_line.setdefault(line.product_id, set()).add(child.image_id)
    assert all(len(ids) == 1 for ids in by_line.values()), by_line


def test_no_record_points_at_an_image_of_a_different_kind_of_product(catalog):
    """The drawing has to be a drawing of the thing.

    Reuse inside a product line is a family sharing one image. Reuse across
    types would be a flat washer showing a picture of an end mill, which is not
    image reuse but the wrong picture -- and the product type is the first
    segment of the image id, so this reads it back off the published id rather
    than off the field it was built from.
    """
    for line, child in catalog.all_skus():
        assert taxonomy.product_type_for_image(child.image_id) == line.type_key
        assert line.drawing == taxonomy.DRAWING[line.type_key]


def test_the_two_measured_image_rates_are_recorded_even_though_neither_is_reproduced():
    """A deviation that is not written down is indistinguishable from a bug."""
    assert SMALL.measured_image_missing == 0.1089
    assert SMALL.measured_image_sku_diverges == 0.7353


# --- the three lengths, and the four socket screw styles -------------------
#
# Issue #8: three of the reference distributor's five screw examples had no correct answer
# in the catalog -- not because ranking was wrong, but because the attribute or
# the product did not exist. These are the checks that it does. They are about
# the CATALOG rather than about a renderer, which is where the gap was.


def _fastener_types() -> tuple[str, ...]:
    """Every product type whose vocabulary carries the screw/bolt lengths.

    Derived from the vocabulary rather than listed, so a style added to the
    catalog is checked the day it appears rather than the day someone
    remembers to add it here.
    """
    from synthetic_industrial_products.catalog.vocab import names_for

    return tuple(
        key for key in VOCAB if {"Length", "Length Under Head"} <= set(names_for(key))
    )


def test_every_screw_and_bolt_line_publishes_a_length_under_head(catalog):
    """On every style, in both systems, unconditionally.

    ``Length`` and ``Thread Length`` were both present before this and neither
    is the measurement a shopper's "x 3/4" names: thread length is how much of
    the shank is threaded, and a countersunk screw's length is measured over
    its head. Binding the token to either would return confidently wrong
    results rather than an empty set.
    """
    types = _fastener_types()
    assert len(types) >= 5, types
    seen_systems: dict[str, set[str]] = {}
    for line, child in catalog.all_skus():
        if line.type_key not in types:
            continue
        names = {a.name for a in child.attributes}
        assert "Length Under Head" in names, f"{child.sku} ({line.type_key}) publishes {names}"
        value = next(a.value for a in child.attributes if a.name == "Length Under Head")
        seen_systems.setdefault(line.type_key, set()).add("mm" if "mm" in value else "in")
    assert set(seen_systems) == set(types), sorted(set(types) - set(seen_systems))
    assert {system for systems in seen_systems.values() for system in systems} == {"in", "mm"}


def test_the_length_under_head_is_shorter_than_the_length_on_a_countersunk_screw(catalog):
    """And equal to it on every other style, which is what makes it a real attribute.

    A flat head sinks into the work, so its published length is measured over
    the head; every other style's is measured under it. If the two attributes
    agreed everywhere, one of them would be a second spelling of the other.
    """
    from synthetic_industrial_products.dimensions import DimensionParseError, parse_length

    shorter = same = 0
    for line, child in catalog.all_skus():
        values = {a.name: a.value for a in child.attributes}
        if "Length Under Head" not in values or "Length" not in values:
            continue
        try:
            length = parse_length(values["Length"]).inches
            under = parse_length(values["Length Under Head"]).inches
        except DimensionParseError:
            continue
        if line.type_key == "screw_flat_head":
            assert under < length, f"{child.sku}: {values}"
            shorter += 1
        else:
            # Tolerant of the last published decimal, and of nothing else: the
            # unit-mixing defect republishes one dimension of a record in the
            # other system, so a 20 mm length can appear beside a 0.7874" one.
            assert under == pytest.approx(length, abs=0.001), f"{child.sku}: {values}"
            same += 1
    assert shorter > 50 and same > 200, (shorter, same)


def test_the_catalog_offers_all_four_socket_screw_styles(catalog):
    """Button head and low head are products, not spellings.

    Each is its own product type with its own category leaf, its own extracted
    standard in each system and its own drawing -- because the head really is a
    different shape, and a style drawn as another style's picture is the
    ``Screw Head Type`` defect over again.
    """
    styles: dict[str, set[str]] = {}
    standards: dict[str, set[str]] = {}
    for line in catalog.lines:
        if not line.type_key.startswith("screw_"):
            continue
        values = {a.name: a.value for a in line.attributes}
        styles.setdefault(line.type_key, set()).add(values["Screw Head Type"])
        standards.setdefault(line.type_key, set()).add(line.dimension_provenance)
    assert styles == {
        "screw_socket_head": {"Socket"},
        "screw_flat_head": {"Flat"},
        "screw_button_head": {"Button"},
        "screw_low_head": {"Low Socket"},
    }
    assert standards["screw_button_head"] == {"ISO 7380-1", "ASME B18.3.3A"}
    assert standards["screw_low_head"] == {"DIN 7984", "ASME B18.3.1G"}


def test_a_button_head_and_a_low_head_have_the_head_their_standard_gives_them(catalog):
    """Measured against the socket head cap screw of the same thread size.

    Both are lower, and only the button head is wider -- which is what the
    extracted tables say and is not what you would guess: DIN 7984's head
    diameter EQUALS ISO 4762's at every metric size here, and ASME B18.3.1G's
    is a few thousandths under ASME B18.3's, so a low head is a full head's
    diameter at half its height. If the generator were scaling one head table
    for all four styles, every one of these comparisons would come out equal.
    """
    from synthetic_industrial_products.dimensions import parse_length

    heads: dict[tuple[str, str], tuple[float, float]] = {}
    for line, child in catalog.all_skus():
        values = {a.name: a.value for a in child.attributes}
        size = values.get("Dia./Thread Size")
        if size is None or "Head Dia." not in values or "Head Height" not in values:
            continue
        try:
            dia = parse_length(values["Head Dia."]).inches
            height = parse_length(values["Head Height"]).inches
            heads.setdefault((line.type_key, size), (dia, height))
        except Exception:  # a deliberately malformed value; another SKU will do
            continue
    shared = {
        size
        for key, size in heads
        if key == "screw_socket_head"
        and ("screw_low_head", size) in heads
        or key == "screw_socket_head"
        and ("screw_button_head", size) in heads
    }
    assert shared, "no thread size is offered by both a socket head and one of the new styles"
    for size in shared:
        full_dia, full_height = heads[("screw_socket_head", size)]
        for style in ("screw_low_head", "screw_button_head"):
            if (style, size) not in heads:
                continue
            dia, height = heads[(style, size)]
            assert height < full_height, (style, size, height, full_height)
            if style == "screw_button_head":
                assert dia > full_dia, (style, size, dia, full_dia)
            else:
                assert dia <= full_dia + 1e-9, (style, size, dia, full_dia)


# -- the category tree has the real catalog's shape -------------------------
#
# elastic/prism-industrial-products#77, read off the real distributor's own
# breadcrumbs and category facet: the leaf is a self-describing plural product
# type, specifications are never path levels, and the roots are the
# distributor's own. The earlier tree ended its end mills at a MATERIAL
# (``Milling / End Mills / Square End Mills / Cobalt``) and filed drills under
# a ``Drilling`` root the real catalog does not have; each test below reds on
# that tree.

#: The real catalog's top-level menu ("Shop All Products"), verbatim, as the
#: maintainer supplied it on elastic/prism-industrial-products#77 (2026-09-25).
#: Evidence, not configuration: a root outside it is a root we invented.
REAL_CATALOG_ROOTS = frozenset(
    {
        "Abrasives",
        "Clamping, Workholding & Positioning",
        "Fasteners",
        "Fleet Maintenance",
        "HVAC",
        "Hand Tools",
        "Hardware",
        "Holemaking",
        "Hose, Tube, Fittings & Valves",
        "Indexable Cutting Tools",
        "Janitorial & Facility Maintenance",
        "Lighting & Electrical",
        "Lubricants, Coolants & Fluids",
        "Machinery",
        "Marking & Labeling",
        "Material Handling & Storage",
        "Measuring & Inspecting",
        "Milling",
        "Motion Control & Fluid Power",
        "Plumbing, Pumps & Filtration",
        "Power Tools",
        "Raw Materials",
        "Safety",
        "Saw Blades",
        "Shipping & Office Supplies",
        "Tapes & Adhesives",
        "Threading",
        "Tool Holding",
        "Turning & Boring",
        "Welding & Soldering",
    }
)


def _published_values(line) -> set[str]:
    """Every attribute value a line publishes, on the line or any of its SKUs."""
    values: set[str] = set()
    for attribute in (*line.attributes, *(a for c in line.children for a in c.attributes)):
        if attribute.values is not None:
            values.update(attribute.values)
        else:
            values.add(attribute.value)
    return values


def test_no_category_level_is_a_value_the_line_publishes_as_an_attribute(catalog):
    """A specification is an attribute, never a path level.

    Measured on the lines, not on the taxonomy table: a path segment that
    equals a value the same line publishes (``Cobalt`` under ``End Mill
    Material: Cobalt``) is a specification filed as a category, whichever
    table it came from.
    """
    offenders = {
        (line.product_id, segment)
        for line in catalog.lines
        for segment in line.category
        if segment in _published_values(line)
    }
    assert not offenders, sorted(offenders)[:10]


def test_every_root_is_one_of_the_real_catalogs_roots():
    roots = {path[0] for path in taxonomy.all_paths()}
    assert roots <= REAL_CATALOG_ROOTS, sorted(roots - REAL_CATALOG_ROOTS)


def test_every_leaf_is_its_types_own_self_describing_plural(catalog):
    """One path per product type, and the leaf names the type, in the plural.

    One path per type is what makes the leaf the type: a type spread over
    several leaves is being split by something that is not its type. The
    plural is the real catalog's spelling (``Square End Mills``, never
    ``Square End Mill`` and never ``Square``), and a leaf of one word cannot
    say what the product is out of context (``Cobalt``, ``Square``).
    """
    for type_key, paths in taxonomy.LEAVES.items():
        assert len(paths) == 1, (type_key, paths)
        leaf = paths[0][-1]
        assert leaf.endswith("s"), (type_key, leaf)
        assert len(leaf.split()) >= 2, (type_key, leaf)
    leaves = [paths[0][-1] for paths in taxonomy.LEAVES.values()]
    assert len(leaves) == len(set(leaves)), "two product types share a leaf name"
    assert {line.category for line in catalog.lines} == set(taxonomy.all_paths())


def test_every_end_mill_publishes_its_material(catalog):
    """Material left the path, so the attribute must carry it on every end mill.

    Otherwise the lines whose material the path used to state would carry it
    nowhere -- the information the restructure was not allowed to lose.
    """
    missing = [
        line.product_id
        for line in catalog.lines
        if line.type_key in taxonomy.END_MILL_MATERIALS
        and not any(a.name == "End Mill Material" for a in line.attributes)
    ]
    assert not missing, missing[:10]

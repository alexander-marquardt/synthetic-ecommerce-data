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

from dataclasses import replace

import pytest

from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.config import SMALL, GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import all_type_keys, generate
from synthetic_ecommerce_data.domains.industrial.measure import measure
from synthetic_ecommerce_data.domains.industrial.vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    STANDARDS_NAME,
    VOCAB,
)


def _without_breadth(catalog):
    """``catalog``, minus its fixed breadth lines (:mod:`.breadth`).

    Breadth is a constant ~50-category addition, deliberately independent of
    every depth knob (``lines``, ``variants_per_product``, ``new_type_share``)
    -- that is the whole point of it (alexander-marquardt/synthetic-ecommerce-data#34).
    A test of what those knobs do to the DEPTH-scaling machinery has to look
    past it, the same way it already looks past ``must_stock``'s fixed lines.
    """
    kept = tuple(line for line in catalog.lines if line.spec_quality != "fast_and_cheap")
    return replace(catalog, lines=kept)


@pytest.fixture(scope="module")
def config():
    return GeneratorConfig(
        lines=600,
        seed=99,
        new_type_share={key: 0.1 for key in GeneratorConfig().new_type_share},
    )


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


def _modelled_share(config) -> float:
    """Every modelled type's share of ``lines``, summed.

    The original types' shares sum to 1.0. A deepened type adds its own share
    on top and takes none from the others, which would move their output, so
    the sum is above 1.0 by the deepened types' shares.
    """
    modules = typespec.modelled()
    return sum(
        config.type_weights.get(key, modules[key].share if key in modules else 0.0)
        for key in all_type_keys("modelled")
    )


def test_the_catalog_is_the_size_it_was_asked_for(stats, config):
    # Breadth (:mod:`.breadth`) adds a fixed ~50 lines on top, independent of
    # every depth knob -- alexander-marquardt/synthetic-ecommerce-data#34.
    asked = (
        round(config.lines * _modelled_share(config))
        + sum(config.new_type_products.values())
        + len(all_type_keys("breadth"))
    )
    assert stats["lines"] == pytest.approx(asked, abs=12)
    # About 1.9 variants per product under the default distribution; a product
    # never offers more variants than its series has members.
    assert 1.5 * stats["lines"] <= stats["skus"] <= 2.3 * stats["lines"]


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
    """Except the deliberate zero-axis case: a product's ONLY variant, carrying nothing."""
    zero_axis = 0
    for line in catalog.lines:
        assert line.attributes, line.product_id
        assert line.children
        for child in line.children:
            if not child.attributes:
                assert len(line.children) == 1, f"{child.sku} has siblings and no attributes"
                zero_axis += 1
    assert zero_axis > 0, "the zero-axis awkward case never occurred"


def test_a_variant_can_lack_an_attribute_its_siblings_carry(catalog):
    """The ragged-variant awkward case: a grouped selector must survive a gap."""
    ragged = 0
    for line in catalog.lines:
        names = [{a.name for a in child.attributes} for child in line.children]
        if len(names) > 1 and len(set(map(frozenset, names))) > 1:
            ragged += 1
    assert ragged > 0


def test_the_category_tree_is_used_and_is_three_to_five_deep(catalog):
    depths = {len(line.category) for line in catalog.lines}
    assert depths <= {3, 4, 5}
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


def test_unrelated_types_share_only_generic_concepts_in_the_output(stats):
    """A threaded fastener and a striking tool share what the census shares.

    The item name, the measurement-system attribute (one idea under three
    spellings), the standards, and ``Material`` -- one generic name across
    types since elastic/prism-industrial-products#103, where it used to be a
    per-type name. Nothing else.
    """
    screw = set(stats["attribute_names_by_type"]["screw_socket_head"])
    hammer = set(stats["attribute_names_by_type"]["hammer_ball_pein"])
    allowed = {
        "Item",
        "Material",
        STANDARDS_NAME,
        *(name for name, _ in MEASUREMENT_SYSTEM_NAMES),
    }
    assert screw & hammer <= allowed
    assert "Material" in screw & hammer


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
        # Lower than the corpus's 0.17: the newer types publish no secondary
        # dimension a title could name instead of the primary one.
        ("title dimension token is not the primary dimension", 0.05, 0.25),
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
    none = {key: 0.0 for key in GeneratorConfig().new_type_share}
    small_cfg = GeneratorConfig(lines=50, seed=3, new_type_share=none)
    large_cfg = GeneratorConfig(lines=150, seed=3, new_type_share=none)
    small = measure(_without_breadth(generate(small_cfg)))
    large = measure(_without_breadth(generate(large_cfg)))
    # Not quite twice: a bigger catalog draws more specs a brand has already
    # made, and the uniqueness rule rejects them (measured 296 vs 152 lines).
    assert large["lines"] > small["lines"] * 1.8
    assert large["skus"] > small["skus"] * 1.8

    narrow_cfg = GeneratorConfig(lines=60, seed=3, variants_per_product=((1, 1.0),))
    wide_cfg = GeneratorConfig(lines=60, seed=3, variants_per_product=((5, 1.0),))
    narrow = measure(_without_breadth(generate(narrow_cfg)))
    wide = measure(_without_breadth(generate(wide_cfg)))
    assert narrow["skus"] == narrow["lines"], "one variant per product, exactly"
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


def test_every_sku_has_an_image_of_its_own(catalog):
    """One drawing per SKU, drawn from its own values (elastic/prism-industrial-products#103).

    The count is the assertion: one per product line is what this replaced,
    where six lengths of one screw showed one picture.
    """
    ids = [child.image_id for _, child in catalog.all_skus()]
    assert len(set(ids)) == len(ids) == catalog.sku_count
    for line, child in catalog.all_skus():
        assert child.image_id == taxonomy.image_id_for(line.type_key, line.product_id, child.sku)


def test_a_product_shows_its_first_variants_image(catalog):
    for line in catalog.lines:
        assert line.image_id == line.children[0].image_id


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
    from synthetic_ecommerce_data.domains.industrial.vocab import names_for

    return tuple(key for key in VOCAB if {"Length", "Length under Head"} <= set(names_for(key)))


def test_every_screw_and_bolt_line_publishes_a_length_under_head(catalog):
    """On every style but the countersunk one, in both systems, unconditionally.

    ``Length`` and ``Thread Length`` were both present before this and neither
    is the measurement a shopper's "x 3/4" names: thread length is how much of
    the shank is threaded, and a countersunk screw's length is measured over
    its head. Binding the token to either would return confidently wrong
    results rather than an empty set.
    """
    types = _fastener_types()
    # Socket, button and low head screws and the hex bolt; the flat head is
    # sold by its length over the head and publishes none (see below).
    assert len(types) >= 4 and "screw_flat_head" not in types, types
    seen_systems: dict[str, set[str]] = {}
    for line, child in catalog.all_skus():
        if line.type_key not in types:
            continue
        names = {a.name for a in child.attributes}
        assert "Length under Head" in names, f"{child.sku} ({line.type_key}) publishes {names}"
        value = next(a.value for a in child.attributes if a.name == "Length under Head")
        seen_systems.setdefault(line.type_key, set()).add("mm" if "mm" in value else "in")
    assert set(seen_systems) == set(types), sorted(set(types) - set(seen_systems))
    assert {system for systems in seen_systems.values() for system in systems} == {"in", "mm"}


def test_the_length_under_head_is_the_stocked_length_and_a_countersunk_screw_has_none(catalog):
    """On every style that publishes it, the length under the head IS the
    stocked nominal length; the countersunk line does not publish it.

    A flat head is sold by its length OVER the head (ISO 10642, ASME B18.3), so
    its "x 3/4" is its ``Length``. Publishing length-less-head-height for it
    put values no distributor lists -- 12.56mm, 1.3910" -- in the facet.
    """
    from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length

    same = flat = 0
    for line, child in catalog.all_skus():
        values = {a.name: a.value for a in child.attributes}
        if line.type_key == "screw_flat_head":
            assert "Length under Head" not in values, f"{child.sku}: {values}"
            flat += 1
            continue
        if "Length under Head" not in values or "Length" not in values:
            continue
        try:
            length = parse_length(values["Length"]).inches
            under = parse_length(values["Length under Head"]).inches
        except DimensionParseError:
            continue
        # Tolerant of the last published decimal, and of nothing else: the
        # unit-mixing defect republishes one dimension of a record in the
        # other system, so a 20 mm length can appear beside a 0.7874" one.
        assert under == pytest.approx(length, abs=0.001), f"{child.sku}: {values}"
        same += 1
    assert flat > 30 and same > 150, (flat, same)


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
        styles.setdefault(line.type_key, set()).add(values["Head Type"])
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
    from synthetic_ecommerce_data.core.dimensions import parse_length

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
                # 1e-4, not 1e-9: ``heads`` takes the first-seen record per
                # (type, size), parsed back from its PUBLISHED string, and
                # the first M20x2.5 of one style can be styled in inches
                # (``Head Dia.`` printed "1.1811"", 4 decimal places) while
                # the first of the other is styled in mm ("30mm", parsed back
                # at full precision). The two are the same head diameter --
                # display rounding, not a real geometric difference, and a
                # few thousandths under a real diameter (this docstring's own
                # "ASME B18.3.1G's is a few thousandths under ASME B18.3's")
                # is two orders of magnitude bigger than this tolerance.
                assert dia <= full_dia + 1e-4, (style, size, dia, full_dia)


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
    shared_leaves = taxonomy.SHARED_LEAVES
    for type_key, paths in taxonomy.LEAVES.items():
        assert len(paths) == 1, (type_key, paths)
        if paths[0] in shared_leaves:
            continue
        leaf = paths[0][-1]
        assert leaf.endswith("s"), (type_key, leaf)
        assert len(leaf.split()) >= 2, (type_key, leaf)
    own = [p[0][-1] for p in taxonomy.LEAVES.values() if p[0] not in shared_leaves]
    assert len(own) == len(set(own)), "two product types share a leaf name"
    # A shared leaf (#305) is the node of several kinds, and only a declared one may be.
    shared = [p[0] for p in taxonomy.LEAVES.values() if p[0] in shared_leaves]
    assert set(shared) == shared_leaves
    assert len(shared) >= 6
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
        and not any(a.name == "Material" for a in line.attributes)
    ]
    assert not missing, missing[:10]


@pytest.fixture(scope="module")
def end_mill_lines():
    """A catalog weighted toward end mills, to measure presence rates on.

    Not the ``catalog``/``stats`` fixtures above: their default type mix
    leaves too few end mills to measure a ~20% presence rate without sampling
    noise swallowing a real defect
    (alexander-marquardt/synthetic-ecommerce-data#39).
    """
    config = GeneratorConfig(
        lines=1500,
        seed=123,
        new_type_share={key: 0.12 for key in GeneratorConfig().new_type_share},
    )
    end_mill_types = ("end_mill_square", "end_mill_ball")
    lines = [line for line in generate(config).lines if line.type_key in end_mill_types]
    assert len(lines) > 300, "not enough end-mill lines to measure presence rates on"
    return lines


@pytest.mark.parametrize(
    "spec",
    [spec for spec in VOCAB["end_mill_square"] if spec.presence < 1.0],
    ids=lambda spec: spec.name,
)
def test_every_sparsity_controlled_end_mill_attribute_is_applied_once(end_mill_lines, spec):
    """Every optional end-mill attribute is dropped at its OWN declared rate,
    once -- never at that rate a second time.

    Corner Radius and Neck Length used to be gated twice: once in the
    builder, at the same probability VOCAB independently declares for it, and
    again in ``_apply_sparsity`` (the shared post-pass every other optional
    attribute goes through exactly once). Applying one probability twice
    squares it: Neck Length fell to ~3% of end mills and Corner Radius to
    ~5%, against the 27%/40% the reference census measures and VOCAB now
    declares (#39). Squaring any presence rate this table carries (all below
    0.92) moves it far outside a tolerance wide enough for this sample's
    ordinary noise -- which is what makes a reintroduced double application
    red here, for whichever attribute it is reintroduced on.
    """
    population = (
        end_mill_lines
        if spec.scope == "line"
        else [child for line in end_mill_lines for child in line.children]
    )
    present = sum(1 for r in population if any(a.name == spec.name for a in r.attributes))
    rate = present / len(population)
    assert abs(rate - spec.presence) <= 0.10, (spec.name, spec.scope, rate, spec.presence)

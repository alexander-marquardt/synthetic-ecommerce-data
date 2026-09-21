"""One drawing per product line, and every difference in it is a difference in a record.

What this file exists to catch
------------------------------
The defect class is ``End Mill Style``: an attribute published on every record,
read by nothing, which drew 473 ball nose mills with square ends through a
39-mutation suite with no escapes. **Mutation testing cannot catch it**, because
an input nobody consumes has no code path to plant a defect in. So every check
here starts from the RECORD -- take what the catalog actually publishes, change
it, and require the picture to notice.

The stamp is the trap in this suite, and it is worth being explicit about.
Every published value is set as text on the drawing, so *any* comparison of
whole files moves when *any* attribute changes -- including for a channel that
is defined in :mod:`~synthetic_industrial_products.render.marking` and never
drawn. A file-level test therefore cannot tell "the coating tints the part"
from "the coating is printed under the part". Each geometric channel is
measured on the DRAWING REGION ONLY -- the axes box, which excludes the card's
stamp band and the detail sheet's title block -- so the stamp cannot answer
for it.

The four acceptance criteria, and where each one is:

1. changing any encoded attribute changes the bytes --
   :func:`test_changing_any_published_attribute_changes_the_drawing`, with the
   attribute list taken from the records rather than written out;
2. no two lines of a type render identically unless their attributes are
   identical -- :func:`test_the_lines_that_draw_alike_are_the_ones_that_publish_alike`
   and :func:`test_exactly_two_lines_do_not_get_a_drawing_of_their_own`;
3. the encoding is reversible --
   :func:`test_the_brand_is_readable_off_the_rendered_drawing`;
4. coverage stays 100%, asserted non-empty --
   :func:`test_every_line_and_every_sku_resolves_to_a_non_empty_file`.
"""

from __future__ import annotations

import json

import numpy as np
import pytest
from matplotlib.text import Text

from helpers import colour_mask, figure_pixels
from synthetic_industrial_products.catalog import emit
from synthetic_industrial_products.catalog.config import SMALL, GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate
from synthetic_industrial_products.render import CARD, DETAIL, batch, generic
from synthetic_industrial_products.render import canvas as cv
from synthetic_industrial_products.render.marking import (
    BRAND_INK,
    DIRECTION_ATTRIBUTES,
    FINISH_ATTRIBUTES,
    FINISH_TINT,
    FLUTES_ATTRIBUTE,
    MATERIAL_ATTRIBUTES,
    MATERIAL_HATCH,
    brand_for_ink,
    marking_for_line,
)

SMALL_CATALOG = generate(SMALL)
SMALL_LINES = list(emit.iter_nested(SMALL_CATALOG))
SMALL_FLAT = list(emit.iter_flat(SMALL_CATALOG))

#: The shipped catalog, whose collision count the issue states exactly. Built
#: once: it is 500 lines and 4,662 SKUs.
FULL_CATALOG = generate(GeneratorConfig())
FULL_LINES = list(emit.iter_nested(FULL_CATALOG))


def _by_type(lines):
    out: dict[str, list[dict]] = {}
    for line in lines:
        out.setdefault(line["product_type"], []).append(line)
    return out


BY_TYPE = _by_type(FULL_LINES)
ONE_PER_TYPE = {key: lines[0] for key, lines in BY_TYPE.items()}

#: The line of each type publishing the most attributes. The sweep in
#: :func:`test_changing_any_published_attribute_changes_the_drawing` runs over
#: these, so it covers as much of each type's ragged vocabulary as the
#: generated catalog offers rather than whatever the first line happened to
#: carry.
RICHEST = {
    key: max(lines, key=lambda line: len(line["attributes"])) for key, lines in BY_TYPE.items()
}


def _publishing(type_key: str, names) -> dict | None:
    """The richest line of ``type_key`` that publishes one of ``names``.

    Selected rather than assumed. The richest line of a type does not
    necessarily carry any particular attribute -- the catalog is ragged by
    design -- and a channel test that skipped whenever it did not would report
    a silent coverage hole as a green run. Measured: picking the richest line
    alone skipped the coating channel for flat head screws and the material
    channel for square end mills and taps, all three of which publish it.
    """
    wanted = set(names)
    candidates = [
        line
        for line in BY_TYPE[type_key]
        if any(entry["name"] in wanted for entry in line["attributes"])
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda line: len(line["attributes"]))


PUBLISHED = sorted(
    (key, entry["name"]) for key, line in RICHEST.items() for entry in line["attributes"]
)


# --- measuring a drawing ---------------------------------------------------


def _drawing(line: dict, profile=CARD):
    """The pixels of the DRAWING, with the stamp cropped off.

    Everything measured through this is a statement about the picture. A test
    that compared whole figures would be answered by the stamp text, which is
    exactly the confusion this suite has to avoid.
    """
    fig, ax = generic.build_line(line, profile)
    image = figure_pixels(fig)
    height = image.shape[0]
    box = ax.bbox
    return image[
        max(int(height - box.y1), 0) : int(np.ceil(height - box.y0)),
        max(int(box.x0), 0) : int(np.ceil(box.x1)),
    ]


def _bytes(line: dict, profile=CARD) -> bytes:
    return batch.draw_line(line, profile)


def _with(line: dict, name: str, value: str) -> dict:
    """``line`` with one published attribute changed."""
    attributes = [
        {**entry, "value": value, "values": [value]} if entry["name"] == name else entry
        for entry in line["attributes"]
    ]
    return {**line, "attributes": attributes}


def _lean(mask: np.ndarray, distance: int = 5) -> int:
    """Which way a pattern of parallel lines leans: +1 up to the right, -1 down.

    Measured by how the pattern overlaps itself under a diagonal shift, which
    needs no knowledge of where the renderer put any particular line. The two
    overlaps come out as roughly (0, N) and (N, 0), so the sign is not a close
    call.
    """
    down = int((mask[:-distance, :-distance] & mask[distance:, distance:]).sum())
    up = int((mask[:-distance, distance:] & mask[distance:, :-distance]).sum())
    return 1 if up > down else -1


def _alternative(name: str, current: str) -> str:
    """Another value this attribute could publish.

    Derived from the channel tables rather than hand-listed per attribute, so
    an attribute added to the vocabulary is swept the day it appears. A change
    to something the channel would REFUSE is not usable here: a renderer that
    validates a value and then ignores it refuses just the same, and the
    refusal would read as "the drawing depends on it".
    """
    if name in FINISH_ATTRIBUTES:
        return next(v for v in sorted(FINISH_TINT) if v != current)
    if name in MATERIAL_ATTRIBUTES:
        return next(v for v in sorted(MATERIAL_HATCH) if v != current)
    if name in DIRECTION_ATTRIBUTES:
        return "Left Hand" if current == "Right Hand" else "Right Hand"
    if name == FLUTES_ATTRIBUTE:
        return "3" if current.strip() != "3" else "4"
    if name in generic.STYLE_DRAWINGS:
        # The style picks which of the twelve SHAPES the line is drawn as, so
        # an alternative has to be another style the drawings cover; anything
        # else is refused, and a refusal would read as "the drawing depends on
        # it" for a renderer that validated the value and then ignored it.
        #
        # It also has to be a style naming a DIFFERENT shape. Several spellings
        # name one -- "button" and "button head" are the same picture -- and
        # taking the next value along would compare a drawing with itself and
        # be answered by the stamp, which is the one thing this suite exists
        # not to let happen.
        drawings = generic.STYLE_DRAWINGS[name]
        mine = drawings[current.strip().lower()]
        return next(v for v, drawing in sorted(drawings.items()) if drawing != mine)
    return f"{current} (a different value)"


# --- criterion 4: coverage, asserted non-empty ----------------------------


def test_every_line_and_every_sku_resolves_to_a_non_empty_file(tmp_path):
    """Present-and-empty is the failure a key check cannot see.

    A zero-byte PNG satisfies "the id resolves to a path" and every record
    pointing at it is a broken image. Both directions are asserted, because a
    rendered file nothing references is dead weight in the repository that
    hosts them.
    """
    written = batch.render_lines(SMALL_LINES, tmp_path, ("card", "detail"))
    for profile, results in written.items():
        for image_id, drawn in results.items():
            path = tmp_path / image_id / f"{profile}.png"
            assert path.exists(), f"{image_id} {profile} was not written"
            assert path.stat().st_size > 0, f"{image_id} {profile} is an empty file"
            assert drawn.size == path.stat().st_size

        on_disk = set(results)
        assert {line["image_id"] for line in SMALL_LINES} == on_disk
        assert {row["image_id"] for row in SMALL_FLAT} <= on_disk
        assert all(row["image_id"] for row in SMALL_FLAT)


def test_every_sku_resolves_to_its_own_lines_drawing():
    """Not just to A drawing -- to the one its parent shows.

    A SKU pointing at some other line's image would still resolve, still be
    non-empty, and still be a picture of the right kind of product. It would
    just be the wrong product's picture.
    """
    of_line = {line["product_id"]: line["image_id"] for line in SMALL_LINES}
    for row in SMALL_FLAT:
        assert row["image_id"] == of_line[row["product_id"]]


# --- criterion 1: every published attribute reaches the drawing -----------


@pytest.mark.parametrize(("type_key", "attribute"), PUBLISHED, ids=lambda v: str(v))
def test_changing_any_published_attribute_changes_the_drawing(type_key, attribute):
    """Read it, or it is being published against a picture that ignores it.

    The pairs are derived from a generated catalog, so an attribute that starts
    being published is covered the day it appears rather than the day somebody
    remembers to add it here. That is the whole reason this check exists: the
    defect it is named for was an attribute nobody had thought to look for.
    """
    line = RICHEST[type_key]
    current = next(e["value"] for e in line["attributes"] if e["name"] == attribute)
    changed = _with(line, attribute, _alternative(attribute, current))
    assert _bytes(changed) != _bytes(line), (
        f"a {type_key} publishes {attribute!r} and its drawing does not change when it does"
    )


def test_the_same_line_always_draws_the_same_bytes():
    """The control. Without it every comparison above could be noise."""
    for line in ONE_PER_TYPE.values():
        assert _bytes(line) == _bytes(line)
        assert _bytes(line, DETAIL) == _bytes(line, DETAIL)


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_the_drawing_is_not_a_function_of_the_product_id(type_key):
    """The prohibition the whole encoding is built around.

    A hash of the product id would produce exactly as much variety as this
    encoding and would assert nothing -- worse, a reader seeing two mills in
    different colours concludes the difference is real. So identity has to be
    invisible: same brand, same attributes, different id, series and title ->
    the same file, byte for byte.

    This is also the control for the sweep above, which otherwise passes for a
    renderer that ignores attributes and hashes the record.
    """
    line = ONE_PER_TYPE[type_key]
    renamed = {
        **line,
        "product_id": "ZZZ-NOPE-9999",
        "image_id": f"{line['product_type']}/ZZZ-NOPE-9999",
        "series": "NOPE",
        "title": "Something Else Entirely",
        "variants": [],
        "variant_count": 0,
    }
    assert _bytes(renamed) == _bytes(line)
    assert _bytes(renamed, DETAIL) == _bytes(line, DETAIL)


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_no_sku_of_the_line_reaches_the_line_drawing(type_key):
    """One drawing stands behind SKUs whose sizes span a median 5.5x.

    A drawing that read any of them would be wrong for most of the line it
    stands behind, and wrong in a way nothing downstream could detect: the
    picture would simply disagree with the record beside it.
    """
    line = ONE_PER_TYPE[type_key]
    assert line["variants"], "the fixture has no variants, so this proves nothing"
    mangled = {
        **line,
        "variants": [
            {
                **variant,
                "attributes": [
                    {**entry, "value": "999 mm", "value_num": 999.0}
                    for entry in variant["attributes"]
                ],
            }
            for variant in line["variants"]
        ],
    }
    assert _bytes(mangled) == _bytes(line)
    assert _bytes(mangled, DETAIL) == _bytes(line, DETAIL)


# --- criterion 3: the encoding is reversible ------------------------------


@pytest.mark.parametrize("brand", sorted(BRAND_INK))
def test_the_brand_is_readable_off_the_rendered_drawing(brand):
    """Not off the table -- off the pixels.

    ``test_marking.py`` round-trips the colour through ``brand_for_ink``, and
    that would pass just as well for a channel defined and never drawn. This
    renders the line, finds the brand colour actually on the page, and reads
    it back. Every other brand's colour must be absent, or the readback would
    be a coincidence of whichever one was checked first.
    """
    line = {**ONE_PER_TYPE["end_mill_square"], "brand": brand}
    region = _drawing(line)
    counts = {name: int(colour_mask(region, ink).sum()) for name, ink in BRAND_INK.items()}
    assert counts[brand] > 100, f"{brand}'s outline colour is not on its own drawing"
    others = {name: n for name, n in counts.items() if name != brand and n > 0}
    assert others == {}, f"{brand}'s drawing also carries {others}"
    assert brand_for_ink(BRAND_INK[brand]) == brand


# --- the geometric channels, measured on the drawing and not on the stamp --


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_the_brand_changes_the_drawing_and_not_only_its_stamp(type_key):
    line = ONE_PER_TYPE[type_key]
    other = next(b for b in sorted(BRAND_INK) if b != line["brand"])
    assert not np.array_equal(_drawing(line), _drawing({**line, "brand": other}))


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_the_coating_changes_the_fill_of_the_drawing(type_key):
    """The tint is the coating's real colour, so it has to be ON the part."""
    line = _publishing(type_key, FINISH_ATTRIBUTES)
    if line is None:
        pytest.skip(f"no {type_key} in this catalog publishes a coating")
    name = next(e["name"] for e in line["attributes"] if e["name"] in FINISH_ATTRIBUTES)
    current = next(e["value"] for e in line["attributes"] if e["name"] == name)
    other = next(v for v in sorted(FINISH_TINT) if v != current)
    region = _drawing(line)
    assert colour_mask(region, FINISH_TINT[current]).sum() > 100, (
        f"{current!r} is published and its own colour is not on the part"
    )
    changed = _drawing(_with(line, name, other))
    assert colour_mask(changed, FINISH_TINT[other]).sum() > 100
    for alternative in sorted(FINISH_TINT):
        if alternative == current:
            continue
        assert not np.array_equal(region, _drawing(_with(line, name, alternative))), (
            f"{current!r} and {alternative!r} fill the part the same way"
        )


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_the_material_changes_the_section_hatch(type_key):
    """Two materials that hatch the same are two materials the drawing conflates."""
    line = _publishing(type_key, MATERIAL_ATTRIBUTES)
    if line is None:
        pytest.skip(f"no {type_key} in this catalog publishes a material")
    name = next(e["name"] for e in line["attributes"] if e["name"] in MATERIAL_ATTRIBUTES)
    current = next(e["value"] for e in line["attributes"] if e["name"] == name)
    region = _drawing(line)
    assert colour_mask(region, cv.HATCH).sum() > 50, "the section is not hatched at all"
    for other in sorted(MATERIAL_HATCH):
        if other == current:
            continue
        assert not np.array_equal(region, _drawing(_with(line, name, other))), (
            f"{current!r} and {other!r} draw the same section"
        )


FLUTED = ("end_mill_square", "end_mill_ball", "tap_spiral_point")


@pytest.mark.parametrize("count", [2, 3, 4, 6])
@pytest.mark.parametrize("type_key", FLUTED)
def test_the_published_flute_count_is_the_number_of_flutes_drawn(type_key, count):
    """Counted off the picture, not compared between pictures.

    A renderer that drew a different-looking tool for each count without
    drawing the right NUMBER of flutes would pass any before-and-after
    comparison. This crosses the tool at its centre line and counts how many
    flutes it meets, which is the same thing a reader does.
    """
    line = _with(ONE_PER_TYPE[type_key], FLUTES_ATTRIBUTE, str(count))
    if not any(e["name"] == FLUTES_ATTRIBUTE for e in line["attributes"]):
        line = {
            **line,
            "attributes": [
                *line["attributes"],
                {"name": FLUTES_ATTRIBUTE, "value": str(count)},
            ],
        }
    assert marking_for_line(line["brand"], line["attributes"]).flutes == count

    fig, ax = generic.build_line(line, CARD)
    image = figure_pixels(fig)
    height = image.shape[0]
    column = int(round(ax.transData.transform((0.0, 0.0))[0]))
    strip = colour_mask(image, cv.FLUTE)[:, column - 1 : column + 2].any(axis=1)
    edges = np.diff(np.concatenate(([0], strip.astype(np.int8), [0])))
    assert int((edges == 1).sum()) == count, (
        f"a {type_key} publishing {count} flutes draws "
        f"{int((edges == 1).sum())} across its centre line"
    )
    del height


@pytest.mark.parametrize("type_key", FLUTED)
def test_a_flute_count_the_record_does_not_publish_is_not_invented(type_key):
    """Silence draws a fluted surface with no count on it, not a guessed count.

    The alternative -- defaulting to four -- is a positive claim about the
    product that nothing downstream could tell from a published one.
    """
    line = ONE_PER_TYPE[type_key]
    silent = {
        **line,
        "attributes": [e for e in line["attributes"] if e["name"] != FLUTES_ATTRIBUTE],
    }
    assert marking_for_line(silent["brand"], silent["attributes"]).flutes is None
    quiet = _drawing(silent)
    for count in (2, 3, 4, 6):
        stated = _with(line, FLUTES_ATTRIBUTE, str(count))
        if not any(e["name"] == FLUTES_ATTRIBUTE for e in stated["attributes"]):
            stated = {
                **stated,
                "attributes": [
                    *stated["attributes"],
                    {"name": FLUTES_ATTRIBUTE, "value": str(count)},
                ],
            }
        assert not np.array_equal(quiet, _drawing(stated))


@pytest.mark.parametrize("type_key", FLUTED + ("drill_jobber",))
def test_a_left_hand_tool_leans_the_other_way(type_key):
    """The direction is drawn, and drawn the way the record says.

    Two assertions, because they fail differently: that the drawing changes at
    all catches a direction that is published and ignored, and that the lean
    follows the value catches a drawing that leans every tool the same way and
    prints the direction underneath.
    """
    line = _publishing(type_key, DIRECTION_ATTRIBUTES)
    assert line is not None, f"no {type_key} publishes a direction, so this proves nothing"
    name = next(e["name"] for e in line["attributes"] if e["name"] in DIRECTION_ATTRIBUTES)
    right = _drawing(_with(line, name, "Right Hand"))
    left = _drawing(_with(line, name, "Left Hand"))
    assert not np.array_equal(right, left)
    assert _lean(colour_mask(right, cv.FLUTE)) == 1
    assert _lean(colour_mask(left, cv.FLUTE)) == -1


@pytest.mark.parametrize("attribute", sorted(generic.STYLE_VALUES))
def test_two_styles_draw_alike_exactly_when_they_name_the_same_shape(attribute):
    """The style channel, measured on the drawing region like the others.

    ``Screw Head Type`` is the attribute whose last defect was exactly this:
    ``Socket`` and ``Hex`` produced the same picture, and 524 hex bolts were
    drawn with round heads while the value sat correctly in the stamp
    underneath. So the claim is made about the DRAWING, in both directions --
    two spellings of one shape draw alike, and two shapes do not -- and the
    values come from ``generic.STYLE_DRAWINGS`` rather than a list here, so a
    style added to the vocabulary is swept the day it appears.
    """
    line = next(
        (
            candidate
            for type_key in sorted(BY_TYPE)
            if (candidate := _publishing(type_key, (attribute,))) is not None
        ),
        None,
    )
    assert line is not None, f"no line publishes {attribute}, so this proves nothing"

    regions: dict[str, list[tuple[str, np.ndarray]]] = {}
    for value, drawing in sorted(generic.STYLE_DRAWINGS[attribute].items()):
        regions.setdefault(drawing, []).append((value, _drawing(_with(line, attribute, value))))
    assert len(regions) > 1, f"{attribute} names one shape; there is nothing to tell apart"

    for drawing, drawn in regions.items():
        first_value, first = drawn[0]
        for value, region in drawn[1:]:
            assert np.array_equal(first, region), (
                f"{value!r} and {first_value!r} are both {drawing} and draw differently"
            )
    for drawing, drawn in regions.items():
        for other, other_drawn in regions.items():
            if other == drawing:
                continue
            assert not np.array_equal(drawn[0][1], other_drawn[0][1]), (
                f"{drawn[0][0]!r} draws {drawing} and {other_drawn[0][0]!r} draws {other}, "
                "and the two are the same picture"
            )


# --- the stamp is the whole record, and only the record -------------------


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_the_card_stamp_sets_every_published_value_and_nothing_else(type_key):
    """Nothing dropped to make it fit, and nothing added that the record does not say.

    A stamp that silently stopped part-way would quietly reduce variety -- two
    lines differing only past the cut would start drawing alike -- and the
    collision count is the only other thing that would notice.
    """
    line = RICHEST[type_key]
    fig, _ = generic.build_line(line, CARD)
    texts = [t.get_text() for t in fig.findobj(Text) if t.get_text().strip()]
    printed = " ".join(" ".join(texts).split())
    expected = " ".join(" · ".join(entry["value"] for entry in line["attributes"]).split())
    assert printed == expected


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_the_detail_sheet_names_every_published_attribute(type_key):
    line = RICHEST[type_key]
    fig, _ = generic.build_line(line, DETAIL)
    texts = {t.get_text().strip() for t in fig.findobj(Text) if t.get_text().strip()}
    for entry in line["attributes"]:
        assert entry["name"] in texts, f"{entry['name']} is not named on the sheet"
    fixed = {generic.NOT_TO_SCALE, generic.STAMP_HEADING}
    published = {entry["value"] for entry in line["attributes"]}
    labels = {image.label for image in generic.IMAGES.values()}
    unaccounted = {
        text
        for text in texts
        if text not in fixed
        and text not in labels
        and text not in published
        and text not in {entry["name"] for entry in line["attributes"]}
        and not any(text in value for value in published)
    }
    assert unaccounted == set(), f"text on the sheet the record does not publish: {unaccounted}"


def test_a_line_drawing_carries_no_sku_and_no_price():
    """One picture stands behind a whole line; a SKU on it is wrong for all but one."""
    line = RICHEST["end_mill_square"]
    for profile in (CARD, DETAIL):
        fig, _ = generic.build_line(line, profile)
        printed = " ".join(t.get_text() for t in fig.findobj(Text))
        for variant in line["variants"]:
            assert variant["sku"] not in printed
            assert f"{variant['price_usd']}" not in printed
        assert line["product_id"] not in printed


@pytest.mark.parametrize("type_key", sorted(ONE_PER_TYPE))
def test_the_card_and_the_detail_of_one_line_are_different_drawings(type_key):
    line = ONE_PER_TYPE[type_key]
    assert _bytes(line, CARD) != _bytes(line, DETAIL)


# --- criterion 2: variety, asserted exactly -------------------------------


def _collision_groups(lines, profile):
    digests = batch.digests(lines, profile)
    of_type = {line["image_id"]: line["product_type"] for line in lines}
    groups: dict[tuple[str, str], list[str]] = {}
    for image_id, digest in digests.items():
        groups.setdefault((of_type[image_id], digest), []).append(image_id)
    return {key: sorted(members) for key, members in groups.items() if len(members) > 1}


#: What the issue measured and what this must keep measuring. Stated as the
#: number of lines that DO NOT get a drawing of their own, per product type.
EXPECTED_COLLISIONS = {"screw_socket_head": 1, "washer_flat": 2}


@pytest.mark.parametrize("profile", ["card", "detail"])
def test_exactly_two_lines_do_not_get_a_drawing_of_their_own(profile):
    """Asserted exactly, because a regression here reduces variety QUIETLY.

    An encoding that collapsed -- a channel dropped, a stamp truncated, a
    signature built from the attributes common to a type rather than from each
    line's own ragged set -- still renders 500 files, still covers every SKU,
    and still passes every other check in this suite. The only thing it moves
    is this number, and only if the number is pinned rather than bounded.

    Three PAIRS, re-measured after the catalog was regenerated on canonical
    values (elastic/prism#9284). ``VAN-W220-0438``/``VAN-W445-0426`` and
    ``OST-W473-0454``/``OST-W525-0449`` are flat washers, which are almost
    nothing but dimensions -- brand, material, finish and washer type, with
    every dimension on the SKUs where a shared drawing must not read them.
    ``COR-ASMEB18.3-60-0266``/``COR-ASMEB18.3-88-0282`` are Corvane socket
    head cap screws to one standard whose line-scope values coincide. Every
    pair is two different products, and every attribute they differ on is
    SKU-scope.

    The count rose from two to three, and the reason is the change itself
    rather than drift: collapsing several spellings of one magnitude into one
    makes two lines that were always the same product MORE likely to publish
    the same line-scope strings. That is the canonicalisation working, and it
    is why the companion test below -- lines drawing alike must publish alike
    -- is the half that actually guards the encoding. The companion
    test below is the half that says so: lines drawing alike have to publish
    alike.

    The number moves when the catalog is regenerated, because WHICH lines
    happen to publish identically is a property of the draw rather than of the
    encoding -- it has read two washers, then one hex bolt pair, and now these
    two. It is re-measured each time rather than adjusted to fit, and what has
    to stay true is that every pair it counts publishes identically.
    """
    groups = _collision_groups(FULL_LINES, profile)
    collisions: dict[str, int] = {}
    for (type_key, _), members in groups.items():
        collisions[type_key] = collisions.get(type_key, 0) + len(members) - 1
    assert collisions == EXPECTED_COLLISIONS


@pytest.mark.parametrize("profile", ["card", "detail"])
def test_the_lines_that_draw_alike_are_the_ones_that_publish_alike(profile):
    """The other half of criterion 2, and the half a count cannot express.

    The count could stay where it is while the lines it counts moved somewhere
    else entirely, which would be a different and worse catalog passing the
    test above. So every line that shares a drawing must publish exactly the same
    brand and the same attributes -- and the converse, that lines publishing
    the same thing do share a drawing, is what makes the drawing a rendering
    of the record rather than a decoration on it.
    """
    signature = {
        line["image_id"]: (
            line["brand"],
            tuple(sorted((e["name"], e["value"]) for e in line["attributes"])),
        )
        for line in FULL_LINES
    }
    for (type_key, _), members in _collision_groups(FULL_LINES, profile).items():
        distinct = {signature[image_id] for image_id in members}
        assert len(distinct) == 1, (
            f"{type_key}: {members} draw the same picture and publish different things"
        )

    digests = batch.digests(FULL_LINES, profile)
    same: dict[tuple, set[str]] = {}
    for image_id, sig in signature.items():
        same.setdefault(sig, set()).add(digests[image_id])
    for sig, seen in same.items():
        assert len(seen) == 1, f"lines publishing {sig} draw {len(seen)} different pictures"


def test_the_channel_sweeps_skip_only_where_the_vocabulary_has_no_channel():
    """Guards the sweeps themselves: a skip must mean "no such attribute exists".

    A skip reads as "not applicable" and is indistinguishable from "the fixture
    happened not to carry it", which is a whole channel silently untested for
    a product type. So the set of types that skip is asserted against the
    VOCABULARY rather than against the fixture.
    """
    from synthetic_industrial_products.catalog.vocab import names_for

    for type_key in sorted(BY_TYPE):
        published = set(names_for(type_key))
        for channel, names in (
            ("coating", FINISH_ATTRIBUTES),
            ("material", MATERIAL_ATTRIBUTES),
            ("direction", DIRECTION_ATTRIBUTES),
        ):
            in_vocabulary = bool(published & set(names))
            found = _publishing(type_key, names) is not None
            assert found == in_vocabulary, (
                f"{type_key}: the vocabulary {'has' if in_vocabulary else 'has no'} a "
                f"{channel} attribute and the sweep {'found' if found else 'found none'}"
            )


def test_the_full_catalog_really_is_the_one_the_issue_measured():
    """Guards the two tests above: they are about a 500-line catalog, not any catalog."""
    assert len(FULL_LINES) == 500
    assert FULL_CATALOG.sku_count == 4689
    assert len({line["image_id"] for line in FULL_LINES}) == 500


def test_the_type_drawings_behind_them_are_still_only_twelve():
    """The shapes did not multiply; the markings did.

    500 drawings of twelve shapes is the decision. 500 SHAPES would be a
    different repository, and one shape re-tinted 500 ways would be the
    hash-driven variety this encoding exists not to be.

    Twelve rather than ten because the catalog gained two product types whose
    heads are genuinely different shapes -- a button head's dome and a low
    head's squat cylinder -- and a style that drew as another style's picture
    is the ``Screw Head Type`` defect over again.
    """
    assert len(generic.IMAGE_IDS) == 12
    assert {line.drawing for line in FULL_CATALOG.lines} == set(generic.IMAGE_IDS)


def test_the_manifest_and_the_rendered_files_agree(tmp_path):
    """The seam the site's importer reads. Both sides are generated here.

    The importer is documented to write each file at the manifest's own
    ``path``, so a renderer that wrote somewhere else would publish a catalog
    of dead links while every test on either side of the seam stayed green.
    """
    batch.render_lines(SMALL_LINES, tmp_path, ("card", "detail"))
    for row in emit.iter_image_manifest(SMALL_CATALOG):
        assert (tmp_path / row["path"]).exists()
        assert (tmp_path / row["detail_path"]).exists()
        assert row["url"].endswith(row["path"])
        assert row["detail_url"].endswith(row["detail_path"])


def test_the_drawings_stay_small_enough_to_publish(tmp_path):
    """A thousand files are committed to the site repository and cloned on every build.

    Not a style rule: the per-file ceilings are what keep the published set to
    single-digit megabytes after compression, and a change that made every
    drawing twice the size would otherwise be found by whoever next cloned the
    site.
    """
    written = batch.render_lines(SMALL_LINES, tmp_path, ("card", "detail"))
    ceilings = {"card": 120_000, "detail": 280_000}
    for profile, results in written.items():
        biggest = max(drawn.size for drawn in results.values())
        assert biggest < ceilings[profile], (
            f"the largest {profile} is {biggest} bytes before compression"
        )


def test_the_catalog_the_renderer_reads_is_the_one_the_generator_writes(tmp_path):
    """The shapes have to match, and they are produced by different modules.

    ``build_line`` reads ``brand``, ``attributes`` and ``image_id`` off a
    nested document. Nothing else asserts that the nested document the
    generator emits still carries those under those names.
    """
    path = tmp_path / "nested.jsonl"
    path.write_text(
        "".join(json.dumps(doc) + "\n" for doc in emit.iter_nested(SMALL_CATALOG)),
        encoding="utf-8",
    )
    reloaded = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(reloaded) == len(SMALL_LINES)
    for line in reloaded:
        assert _bytes(line)

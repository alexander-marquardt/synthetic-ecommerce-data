"""Mutation rows for the Sports & Outdoors second increment and its tree note.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- the Sports & Outdoors second increment (gen#368) ----
    Mutation(
        "sports rows: a football style loses its yellow and its white",
        "prototypes/retail_drawings/type_specs/football.py",
        '_PRIMARY, (_a("cover", "Cover", "Polyurethane")',
        '(RED, BLUE, GREEN, GREEN), (_a("cover", "Cover", "Polyurethane")',
        "tests/test_retail_sports_265.py::test_every_type_offers_the_six_main_colors_with_no_exception[Football]",
        "",
        "yellow is offered by one football style",
        root=".",
    ),
    Mutation(
        "sports rows: a football's ball size is stored without its unit",
        "prototypes/retail_drawings/type_specs/football.py",
        'Option("ball_size", "ball_size", "Ball size", "C62")',
        'Option("ball_size", "ball_size", "Ball size", None)',
        "tests/test_retail_sports_265.py::test_a_measured_axis_is_on_every_sku_with_its_unit[Football]",
        "",
        "the ball size carries its unit",
        root=".",
    ),
    Mutation(
        "sports drawing: a ringed yoga strap draws as a clipped one",
        "prototypes/retail_drawings/kit_sports.py",
        'if buckle.lower() == "clip":',
        'if True:',
        "tests/test_retail_sports_265.py::test_a_param_changes_the_drawing[yoga_strap]",
        "",
        "the buckle param changes the strap",
        root=".",
    ),
    Mutation(
        'sports decoys: a type loses one of its two decoys',
        'prototypes/retail_drawings/decoy_product_words.py',
        '    _s(44, "s_blocks", "Building Blocks Set",\n       "A set of chunky building blocks for toddlers to stack, with a loose brick to start.",\n       "Blue", "block", "Yoga Block"),\n',
        '',
        'tests/test_retail_sports_decoys_368.py::test_a_second_increment_type_has_at_least_two_decoys',
        "",
        'every second-increment type carries two decoys',
        root=".",
    ),
    Mutation(
        "sports decoys: a decoy's target points at another type",
        'prototypes/retail_drawings/decoy_product_words.py',
        '"badminton", "Badminton Set"),\n    _s(76',
        '"badminton", "Tennis Racket"),\n    _s(76',
        'tests/test_retail_sports_decoys_368.py::test_a_second_increment_type_has_at_least_two_decoys',
        "",
        'a decoy misleads the type its target names',
        root=".",
    ),
    Mutation(
        'sports decoys: a live type is exempted with no decoys',
        'prototypes/retail_drawings/decoy_product_words.py',
        '"Dumbbell", "Kettlebell",\n              "Foam Roller")',
        '"Dumbbell", "Kettlebell",\n              "Foam Roller", "Football")',
        'tests/test_retail_sports_decoys_368.py::test_every_sports_type_is_planned_or_exempt',
        "",
        'a sports type is planned or exempt, never silently both',
        root=".",
    ),
    Mutation(
        'sports decoys: an exemption names no follow-up issue',
        'prototypes/retail_drawings/decoy_product_words.py',
        '"decoys are tracked in #375"',
        '"decoys are tracked later"',
        'tests/test_retail_sports_decoys_368.py::test_every_sports_type_is_planned_or_exempt',
        "",
        'an exemption names its issue',
        root=".",
    ),
    Mutation(
        'sports decoys: a later type is added to the exempt set',
        'prototypes/retail_drawings/decoy_product_words.py',
        '"Dumbbell", "Kettlebell",\n              "Foam Roller")',
        '"Dumbbell", "Kettlebell",\n              "Foam Roller", "Kickboard")',
        'tests/test_retail_sports_decoys_368.py::test_the_exempt_set_is_the_seven_first_increment_types',
        "",
        'the exempt set is the seven first-increment types, nothing else',
        root=".",
    ),
    Mutation(
        'sports decoys: a live type outside the hand-written tuple has one decoy',
        'prototypes/retail_drawings/decoy_product_words.py',
        '    _s(68, "s_scooter3", "Kickboard Scooter, Three Wheels",\n       "A kids\' scooter with three wheels and a wide kickboard deck.", "Blue", "kickboard",\n       "Kickboard"),\n',
        '',
        'tests/test_retail_sports_decoys_368.py::test_every_live_non_exempt_sports_type_has_at_least_two_decoys',
        "",
        'every live non-exempt sports type carries two decoys',
        root=".",
    ),
    # ---- the Sports & Outdoors tree note (gen#290) ----
    Mutation(
        "sports note: a Not built row is deleted",
        "docs/retail-sports-tree.md",
        "| Camping stoves | Camping | #352 |\n",
        "",
        "tests/test_retail_sports_tree_note_290.py::test_every_type_not_built_has_an_open_issue_or_a_reason",
        "",
        "every expected type has a Not built row",
        root=".",
    ),
    Mutation(
        "sports note: a leaf verdict claims a retailer tree",
        "docs/retail-sports-tree.md",
        "Dome Tents | berth, season_rating, hydrostatic_head, tent_type, material, color | tent capacity, season rating | none |",
        "Dome Tents | berth, season_rating, hydrostatic_head, tent_type, material, color | tent capacity, season rating | matches the Decathlon tree |",
        "tests/test_retail_sports_tree_note_290.py::test_a_leaf_never_claims_a_retailer_tree_that_was_not_compared",
        "",
        "a verdict is none or a checkable comparison",
        root=".",
    ),
    Mutation(
        "sports note: a disposition is a placeholder",
        "docs/retail-sports-tree.md",
        "| Bicycles | Cycling | #352 |",
        "| Bicycles | Cycling | not reached |",
        "tests/test_retail_sports_tree_note_290.py::test_every_type_not_built_has_an_open_issue_or_a_reason",
        "",
        "a Not built disposition is an issue or a reason",
        root=".",
    ),
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: sports"


def rows() -> list[Mutation]:
    return MUTATIONS

"""The hammer kinds: one builder, one vocabulary, one category (#305).

Every hammer lives under ``Hand Tools > Hammers`` (the combined tree reads
``Tools > Hand Tools > Hammers``) and is told from its siblings by its
``product_type``, a snake_case id ``hammer_<kind>``. A kind is a
:class:`HammerKind`: the draw it adds to the one builder, :func:`build`.

The kinds and their sizes are the ones hardware listings carry. Head weights
are in ounces (a 16 lb sledge is 256 oz) so a facet on ``Head Weight`` reads
across every kind. The ball pein kind keeps the draws it always made, in the
order it made them, so its products keep their ids.

The price is GENERATED, not measured: the price census has no hammers.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial import series
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.drawing.figures import hammer as figure
from synthetic_ecommerce_data.domains.industrial.vocab import HAMMER_VOCAB

#: The one node every hammer lives under.
CATEGORY: tuple[str, ...] = ("Hand Tools", "Hammers")

#: A handle, and the grips each is sold with: a wood handle is sold bare, a
#: fiberglass or steel one with a grip or without.
HAMMER_GRIPS: dict[str, tuple[str, ...]] = {
    "Hickory": ("None",),
    "Ash": ("None",),
    "Fiberglass": ("Rubber", "Vinyl", "None"),
    "Steel": ("Rubber", "Vinyl", "None"),
}

PROVENANCE = "generated; no dimensional standard applies"

#: The noun a kind goes by, as another kind's range name borrows it (class 2 below).
KIND_NOUN: dict[str, str] = {
    "hammer_ball_pein": "Ball Pein",
    "hammer_claw": "Claw",
    "hammer_framing": "Framing",
    "hammer_club": "Club",
    "hammer_sledge": "Sledge",
    "hammer_rubber_mallet": "Mallet",
    "hammer_dead_blow": "Dead Blow",
}

#: Handles a title can name without the line having one (classes 4 and 6 below).
ABSENT_HANDLES: tuple[str, ...] = ("Hickory", "Ash", "Fiberglass")
PLACES: tuple[str, ...] = ("Creek", "Ridge", "Lane", "Hollow")


#: The misleading phrase of a class-4 decoy: ``word`` is the handle material it names.
INCIDENTAL_PHRASE = re.compile(rf"\b(?P<word>{'|'.join(ABSENT_HANDLES)}) (?:{'|'.join(PLACES)})\b")
_INCIDENTAL_TITLE = re.compile(rf"^[A-Z][A-Za-z ]+, {INCIDENTAL_PHRASE.pattern}$")


def is_incidental_decoy_title(title: str) -> bool:
    """Whether ``title`` is a class-4 decoy title (the item and the word alone).

    The one predicate the decoy table's guards and the facts and voice gates share.
    """
    return _INCIDENTAL_TITLE.match(title) is not None


#: The misleading phrase of a class-0 decoy (another kind's noun as a range name) and of a
#: class-2 decoy (a handle material the line does not have).
_CATEGORY_WORD = re.compile(rf"\b(?:{'|'.join(KIND_NOUN.values())}) Series\b")
_MATERIAL_LOOK = re.compile(rf"\b(?:{'|'.join(ABSENT_HANDLES)})-Look\b")


def is_decoy_title(title: str) -> bool:
    """Whether ``title`` carries the misleading phrase of a decoy of any class (0, 2 or 4).

    A brand's voice may put words before the item, so each phrase is searched for.
    """
    return any(p.search(title) for p in (_CATEGORY_WORD, _MATERIAL_LOOK, INCIDENTAL_PHRASE))


def decoy_ids(docs: Iterable[Mapping[str, Any]]) -> frozenset[str]:
    """The ``product_id`` of each hammer document whose title is a decoy.

    The ids a catalog check exempts from the title-against-attribute check
    (``standard.check_catalog(text_exempt=...)``): a decoy names a material or kind its
    attributes do not hold, by design.
    """
    return frozenset(
        str(d["product_id"])
        for d in docs
        if d.get("category_leaf") == CATEGORY[-1] and is_decoy_title(str(d.get("title") or ""))
    )


#: Text-match decoys (gen#294): three lines in every ``DECOY_PERIOD`` of a kind carry a
#: title word that misleads a text search while its attributes stay true. The position in the period
#: names the class: 0 a category word (another kind's noun as a range name: "Claw Hammer,
#: Sledge Series"), 2 a material named but absent ("Claw Hammer, Hickory-Look" on a steel
#: handle), 4 an incidental word in a short title ("Claw Hammer, Hickory Creek"): the whole
#: indexed title, with no brand, qualifier or size (gen#320, 5 words or fewer).
DECOY_PERIOD = 6
DECOY_CLASSES: dict[int, str] = {
    0: "category word",
    2: "material named but absent",
    4: "incidental word",
}


def decoy_item(gen: Any, kind: HammerKind, handle: str) -> tuple[str, bool]:
    """The item as the title says it, and whether that is the whole title (class 4).

    Plain, or with the line's decoy words after it.

    After, so a brand's title template (what opens the title) stays one per type.
    """
    slot = gen._rotate(f"hammer_decoy:{kind.key}", DECOY_PERIOD)
    if slot not in DECOY_CLASSES:
        return kind.item, False
    if slot == 0:
        nouns = [n for k, n in KIND_NOUN.items() if k != kind.key]
        noun = nouns[gen._rotate(f"hammer_decoy_noun:{kind.key}", len(nouns))]
        return f"{kind.item}, {noun} Series", False
    absent = next(h for h in ABSENT_HANDLES if h != handle)
    if slot == 2:
        return f"{kind.item}, {absent}-Look", False
    place = PLACES[gen._rotate(f"hammer_decoy_place:{kind.key}", len(PLACES))]
    return f"{kind.item}, {absent} {place}", True


@dataclass(frozen=True)
class HammerKind:
    """What one kind draws: its noun, its head, its handles and its sizes."""

    key: str
    item: str
    series: str
    material: str
    faces: tuple[str, ...]
    handles: tuple[str, ...]
    ounces: tuple[int, ...]
    #: Overall length is ``oal_base + ounces * oal_per_oz`` inches; the face
    #: is ``face_base + ounces * face_per_oz`` inches across.
    oal_base: float
    oal_per_oz: float
    face_base: float
    face_per_oz: float
    #: What the head takes off the overall length to give the handle length.
    head_trim: float
    #: Shown price (USD) of a standard-tier hammer at 16 oz.
    price: float
    use_lines: tuple[str, ...]
    #: The largest drawn ``(width, height)`` in inches of any product of the kind, with a
    #: little headroom (``tests/test_sku_drawings.py`` holds every drawing to it).
    extent: tuple[float, float] = (5.8, 18.25)
    #: The standard the kind claims (``ASME B107.400`` is for ball pein hammers).
    standard: str = ""


def build(kind: HammerKind):
    """The builder of ``kind``: ``make(generator, type_key, category)``."""

    def make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
        # Imported here: generate imports the type tables, which discover the kinds.
        from synthetic_ecommerce_data.core.brands import pick_brand
        from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

        rng = gen.rng
        brand = pick_brand(rng, type_key, gen._exhausted)
        handle = rng.choice(kind.handles)
        item, bare = decoy_item(gen, kind, handle)
        draft = LineDraft(
            item=item,
            brand=brand,
            series=f"{kind.series}{rng.randint(10, 99)}",
            category=category,
            provenance=PROVENANCE,
            bare_title=bare,
        )
        face_type = kind.faces[0] if len(kind.faces) == 1 else None
        draft.line_attrs = [
            retired(keyword_attribute("Item", kind.item)),  # keeps the stream stable for #497
            keyword_attribute("Material", kind.material),
            keyword_attribute("Handle Material", handle),
            keyword_attribute("Handle Grip Material", rng.choice(HAMMER_GRIPS[handle])),
            keyword_attribute("Face Type", face_type or rng.choice(kind.faces)),
        ]
        draft.descriptors = [("Handle Material", handle)]

        weights = list(kind.ounces)
        rng.shuffle(weights)
        count = min(gen._variant_count(), len(weights))
        if draft.bare_title:
            # One SKU: a bare title cannot tell sibling SKUs apart (gen#320).
            count = 1
        for ounces in sorted(weights[:count]):
            style = gen._style("in")
            child = ChildDraft(system="in")
            oal_in = float(series.snap_imperial(kind.oal_base + ounces * kind.oal_per_oz, 16))
            child.primary = numeric_attribute("Head Weight", f"{ounces} oz", float(ounces))
            overall = gen._length("Overall Length", oal_in, style)
            child.attrs = [
                child.primary,
                overall,
                gen._length("Face Dia.", kind.face_base + ounces * kind.face_per_oz, style),
                gen._length("Handle Length", oal_in - kind.head_trim, style),
            ]
            child.secondary = {"other_length": overall}
            draft.children.append(child)
        return draft

    return make


def price_model(kind: HammerKind) -> PriceModel:
    """GENERATED, NOT MEASURED: a hammer costs about its weight to the 0.6 power."""
    return PriceModel(kind.price, 16.0, 0.6, 0.25, 0.12, measured=False)


def spec(kind: HammerKind) -> TypeSpec:
    """The type module's ``SPEC`` for ``kind``."""
    return TypeSpec(
        kind.key,
        category=CATEGORY,
        standards_family="hand_tool",
        vocab=HAMMER_VOCAB,
        figure=figure,
        extent=kind.extent,
        make=build(kind),
        share=0.012,
        price=price_model(kind),
        may_claim=frozenset(),
        key_attributes=("Head Weight",),
        use_lines=kind.use_lines,
        # A hammer is not sold to fit a part: no cross-reference to write.
        compat=False,
    )


#: The seven kinds, ball pein first (it predates the others and is built by
#: ``generate``'s own table).
BALL_PEIN = HammerKind(
    key="hammer_ball_pein",
    item="Ball Pein Hammer",
    series="BP",
    material="Forged Steel",
    faces=("Ball Pein",),
    handles=("Hickory", "Ash", "Fiberglass", "Steel"),
    ounces=series.HAMMER_HEAD_OUNCES,
    oal_base=10.0,
    oal_per_oz=0.16,
    face_base=0.6,
    face_per_oz=0.02,
    head_trim=1.5,
    price=82.8,
    use_lines=(),
    standard="ASME B107.400",
)

CLAW = HammerKind(
    key="hammer_claw",
    item="Claw Hammer",
    series="CH",
    material="Forged Steel",
    faces=("Smooth", "Milled"),
    handles=("Hickory", "Ash", "Fiberglass", "Steel"),
    ounces=(8, 10, 12, 13, 16, 20, 24),
    oal_base=11.0,
    oal_per_oz=0.14,
    face_base=0.7,
    face_per_oz=0.02,
    head_trim=1.5,
    price=24.0,
    use_lines=(
        "Drives nails with the face and pulls them with the curved claw.",
        "The general carpentry hammer for trim, repairs and light framing.",
    ),
    extent=(4.4, 14.6),
)

FRAMING = HammerKind(
    key="hammer_framing",
    item="Framing Hammer",
    series="FH",
    material="Forged Steel",
    faces=("Milled", "Smooth"),
    handles=("Hickory", "Fiberglass", "Steel"),
    ounces=(20, 22, 24, 28, 32),
    oal_base=12.0,
    oal_per_oz=0.18,
    face_base=0.75,
    face_per_oz=0.02,
    head_trim=1.5,
    price=42.0,
    use_lines=(
        "A long, heavy hammer for driving framing nails in a few swings.",
        "The face grips the nail head; the straight claw pries and pulls.",
    ),
    extent=(5.1, 18.0),
)

CLUB = HammerKind(
    key="hammer_club",
    item="Club Hammer",
    series="LH",
    material="Forged Steel",
    faces=("Smooth",),
    handles=("Hickory", "Fiberglass"),
    ounces=(32, 40, 48, 64),
    oal_base=8.5,
    oal_per_oz=0.04,
    face_base=1.1,
    face_per_oz=0.012,
    head_trim=2.0,
    price=30.0,
    use_lines=(
        "A short-handled lump hammer for striking chisels, drills and stakes.",
        "Drives masonry nails and breaks brick with a heavy head on a short handle.",
    ),
    extent=(6.9, 13.2),
)

SLEDGE = HammerKind(
    key="hammer_sledge",
    item="Sledge Hammer",
    series="SH",
    material="Forged Steel",
    faces=("Smooth",),
    handles=("Hickory", "Fiberglass", "Steel"),
    ounces=(80, 96, 128, 160),
    oal_base=22.0,
    oal_per_oz=0.09,
    face_base=1.4,
    face_per_oz=0.01,
    head_trim=2.0,
    price=48.0,
    use_lines=(
        "Swung with both hands to drive stakes and break up masonry.",
        "A heavy head on a long handle, for demolition and driving posts.",
    ),
    extent=(11.0, 36.6),
)

RUBBER_MALLET = HammerKind(
    key="hammer_rubber_mallet",
    item="Rubber Mallet",
    series="RM",
    material="Rubber",
    faces=("Flat",),
    handles=("Hickory", "Fiberglass"),
    ounces=(8, 12, 16, 24, 32),
    oal_base=10.0,
    oal_per_oz=0.12,
    face_base=1.3,
    face_per_oz=0.03,
    head_trim=1.5,
    price=14.0,
    use_lines=(
        "Taps parts, tiles and pavers into place without marking them.",
        "A soft face for assembling flat-pack furniture and seating trim.",
    ),
    extent=(8.3, 14.0),
)

DEAD_BLOW = HammerKind(
    key="hammer_dead_blow",
    item="Dead Blow Hammer",
    series="DB",
    material="Urethane",
    faces=("Flat",),
    handles=("Steel", "Fiberglass"),
    ounces=(16, 20, 24, 32, 48),
    oal_base=11.0,
    oal_per_oz=0.10,
    face_base=1.2,
    face_per_oz=0.015,
    head_trim=1.5,
    price=26.0,
    use_lines=(
        "A shot-filled head that does not rebound, for seating parts without marring.",
        "Strikes with full force and no bounce on machine setups and assemblies.",
    ),
    extent=(7.1, 16.0),
)

KINDS: dict[str, HammerKind] = {
    k.key: k for k in (BALL_PEIN, CLAW, FRAMING, CLUB, SLEDGE, RUBBER_MALLET, DEAD_BLOW)
}

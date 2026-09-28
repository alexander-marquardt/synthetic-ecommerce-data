"""Build product titles the way the catalog builds them.

The measured grammar is short::

    TITLE   := ITEM (DELIM SEGMENT)*
    SEGMENT := VALUE LABEL?

and the load-bearing detail is that **the value precedes its label** --
``1/2" Milling Dia.``, not ``Milling Dia. 1/2"``. A parser written the other
way round reads every title backwards.

Three measured hazards are reproduced here, because they are the reason a
title cannot be trusted as a source of structured data:

**The label is often missing.** 49 of 105 title dimension tokens (46.7%) carry
no label at all. ``End Mill, Carbide, 1/8, 4 FL, SGL Sq End`` states a
dimension and never says which one.

**The dimension in the title is sometimes not the one you would assume.** 18 of
105 tokens (17.1%) are not the milling diameter: 7 some other length, 5 the
length of cut, 4 a neck length, 2 a flute length. A title reading
``0.31mm Neck L`` sits on a tool whose milling diameter is 5/16".

**Those two hazards do not overlap.** The corpus contains zero tokens that are
both unlabelled *and* not the milling diameter
(:file:`P1_title_grammar.json`, ``cases_unlabelled_and_not_milling_dia`` is
empty). So an unlabelled token is the primary dimension, and a token that is
*not* the primary dimension always says so -- quietly, in an abbreviation.
The generator reproduces them as disjoint rather than sampling them
independently, which would invent a fourth case the corpus does not contain.

Labels are also abbreviated (``FL``, ``Neck L``, ``Cut L``, ``Overall Lg``)
and, in 3.2% of titles, cut off entirely where the title hits its length cap
(``Milling Di``).
"""

from __future__ import annotations

from dataclasses import dataclass

#: The delimiter between segments. The corpus writes ", " most of the time and
#: occasionally elides the space (``3/8,4 FL``).
DELIMITER = ", "
TIGHT_DELIMITER = ","

#: How a label may be written, per attribute, with the weights the measured
#: lexicon gives. The first entry of each list is the unabbreviated form.
#: Counts in the comments are occurrences in P1_title_grammar.json.
LABEL_FORMS: dict[str, tuple[tuple[str, float], ...]] = {
    # FL 50, Flutes 20, Fl 2
    "Number of Flutes": (("Flutes", 0.28), ("FL", 0.66), ("Fl", 0.06)),
    # Cut L 4, Length of Cut 2
    "Length of Cut": (("Length of Cut", 0.34), ("Cut L", 0.66)),
    # Neck L 4
    "Neck Length": (("Neck Length", 0.2), ("Neck L", 0.8)),
    # Overall Lg 6, Lg 4, L 18
    "Overall Length": (
        ("Overall Length", 0.18),
        ("Overall Lg", 0.22),
        ("Lg", 0.20),
        ("L", 0.40),
    ),
    # Milling Dia 2, Milling Di 2 (truncated), dia 9, D 13
    "Milling Dia.": (
        ("Milling Dia.", 0.30),
        ("Milling Dia", 0.14),
        ("dia.", 0.28),
        ("D", 0.28),
    ),
    # SHK 2
    "Shank Dia.": (("Shank Dia.", 0.4), ("Shank", 0.3), ("SHK", 0.3)),
    "Length": (("Length", 0.3), ("L", 0.7)),
    "Finish": (("Finish", 1.0),),
    "Size": (("Size", 1.0),),
    "Flute Length": (("Flute Length", 0.5), ("Flute L", 0.5)),
    "Thread Size": (("Thread Size", 0.6), ("Size", 0.4)),
    "Head Dia.": (("Head Dia.", 1.0),),
    "Grit": (("Grit", 1.0),),
    "Head Weight": (("Head Weight", 0.5), ("Wt", 0.5)),
    "Diameter": (("Dia.", 0.6), ("dia.", 0.4)),
    "Outside Dia.": (("Outside Dia.", 0.5), ("Outside Dia", 0.5)),
    "Width Across Flats": (("Width Across Flats", 0.5), ("A/F", 0.5)),
}

#: Value-side abbreviations, from the measured token table. These appear in
#: the terse style, where a segment is a bare abbreviated value with no label:
#: ``SGL Sq End`` is "Single Square End".
VALUE_ABBREVIATIONS: dict[str, str] = {
    "Square": "Sq",
    "Single": "SGL",
    "Single End": "SGL",
    "Double End": "DBL",
    "High Speed Steel": "HSS",
    "Right Hand": "RH",
    "Left Hand": "LH",
    "Standard": "Std",
    "Cobalt": "Co",
    "Stainless Steel": "SS",
    "Upcut": "Up",
    "Downcut": "Dn",
    "Straight": "STR",
    "Center Cutting": "CC",
    "Non-Center Cutting": "NC",
    "Bright": "Bright",
    "Carbide": "Carbide",
}


class TitleError(ValueError):
    """A title could not be built from the segments supplied."""


@dataclass(frozen=True)
class Segment:
    """One comma-delimited piece of a title: a value, then maybe a label."""

    value: str
    label: str | None = None
    #: The attribute this segment was built from, kept so a test can ask what
    #: a title actually claims rather than re-parsing the string.
    attribute: str | None = None
    #: True when the label is a strict prefix of the attribute name, i.e. the
    #: title was cut at its length cap.
    truncated: bool = False

    def text(self) -> str:
        if self.label is None:
            return self.value
        return f"{self.value} {self.label}"


@dataclass(frozen=True)
class Title:
    item: str
    segments: tuple[Segment, ...]
    text: str
    truncated: bool
    #: Which delimiter was written tight (``3/8,4 FL``), if any. Kept so a
    #: title can be REASSEMBLED with one more segment without re-rolling it
    #: and without silently losing the tight comma.
    tight_delimiter_at: int | None = None

    @property
    def segment_count(self) -> int:
        """Counting the ITEM, as the measured segment_count_distribution does."""
        return 1 + len(self.segments)

    def attribute_names(self) -> frozenset[str]:
        """Which attributes this title actually names.

        Read off the segments rather than by parsing the assembled string: a
        title is built from structured segments and re-reading the text would
        be a second, worse answer to a question the object already knows.
        The description uses it to avoid restating what the title just said.
        """
        return frozenset(segment.attribute for segment in self.segments if segment.attribute)


def abbreviate_value(value: str) -> str:
    """The catalog's short form of a value, when it has one."""
    return VALUE_ABBREVIATIONS.get(value, value)


def label_is_prefix_of(label: str, attribute: str) -> bool:
    """Whether ``label`` is the truncation signature: a strict prefix."""
    return label != attribute and attribute.startswith(label)


#: Characters that CONTINUE a value token. A catalog dimension is written out
#: of digits, fraction and decimal marks, unit marks and letters, so a match
#: with one of these on either side is a match found INSIDE a longer value
#: rather than a statement of this one.
_VALUE_CHARACTERS = frozenset(
    "0123456789./-\"'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
)


def states_value(text: str, value: str) -> bool:
    """Whether ``text`` STATES ``value``, rather than merely containing it.

    A bare ``value in text`` reads the title::

        Button Head Socket Cap Screw, 1/4-20, Alloy Steel

    as naming a ``Length Under Head`` of ``1/4``. It does not: the ``1/4`` it
    contains is the first half of a thread designation, and the screw's length
    appears nowhere. Measured, 10 of 4,729 SKUs satisfied "this title names a
    value that is this SKU's alone" on exactly that accident -- and because
    the repair and the test that checks it both asked the question with ``in``,
    the repair declined to fire and the test declined to notice.

    A match counts when neither neighbouring character could be part of the
    same value. ``1/4`` in ``1/4-20`` is followed by ``-`` and does not count;
    ``1/4`` in ``1/4 in L`` is followed by a space and does.
    """
    if not value:
        return False
    at = text.find(value)
    while at != -1:
        before = text[at - 1] if at else ""
        after = text[at + len(value) : at + len(value) + 1]
        if before not in _VALUE_CHARACTERS and after not in _VALUE_CHARACTERS:
            return True
        at = text.find(value, at + 1)
    return False


def build_title(
    item: str,
    segments: tuple[Segment, ...],
    *,
    cap: int = 100,
    tight_delimiter_at: int | None = None,
) -> Title:
    """Join the segments, dropping whole trailing ones to stay under the cap.

    The cap is real -- a title has a budget and the reference corpus shows
    titles written to one. What changed with the ruling on elastic/prism#9284
    is WHERE the budget is taken from. This used to cut the assembled string
    at the cap, which lands mid-word: **70 of the default catalog's 10,080
    titles** (67 of 4,689 before it grew) would end ``...Solid Carbide, U``
    or ``...SGL Sq En``. That is
    the same defect class as the label truncation removed from the generator,
    arriving by a second door, and removing only the first would have left
    about 1% of titles truncated while the change claimed none were.

    THAT FIGURE IS RE-DERIVED, NOT REMEMBERED. It stood at "97 of 4,688" and
    did not reproduce under any reading: 4,688 is the previous generation's
    document count, and 97 is not the mid-word count of either generation.
    ``tests/test_catalog_titles.py`` now reconstructs the old behaviour --
    assembling every segment and slicing at the cap -- and counts the titles
    that land inside a word, so the number above is measured on every run.

    So a title that does not fit sheds its LAST SEGMENT, and then the one
    before it, until it fits. Every segment that survives is whole, which is
    what the reference distributor's own titles look like -- the grammar drops the least
    identifying attribute rather than publishing half of it. The item segment
    is never dropped: a title has to name the product, and one that cannot do
    that inside the cap is a genuine refusal rather than something to trim to
    nothing.

    The cut is not applied to the segment LIST, so the structured record still
    knows what the title was trying to say.
    """
    if not item:
        raise TitleError("a title needs an ITEM segment")

    def assemble(keep: int) -> str:
        pieces = [item]
        for index, segment in enumerate(segments[:keep]):
            delimiter = TIGHT_DELIMITER if index == tight_delimiter_at else DELIMITER
            pieces.append(delimiter + segment.text())
        return "".join(pieces)

    kept = len(segments)
    text = assemble(kept)
    while kept > 0 and len(text) > cap:
        kept -= 1
        text = assemble(kept)

    truncated = any(segment.truncated for segment in segments[:kept])
    if len(text) > cap:
        # Only reachable when the ITEM alone exceeds the cap. Nothing is cut
        # mid-word to hide it: the title is published whole and flagged, so a
        # reader meets an over-long title rather than a mutilated one.
        truncated = True
    return Title(
        item=item,
        segments=segments,
        text=text,
        truncated=truncated,
        tight_delimiter_at=tight_delimiter_at,
    )


def truncate_label(attribute: str, keep: int) -> str:
    """``Milling Dia.`` kept to 10 characters is ``Milling Di``."""
    if keep <= 0 or keep >= len(attribute):
        raise TitleError(f"{keep} is not a truncation of {attribute!r}")
    return attribute[:keep]

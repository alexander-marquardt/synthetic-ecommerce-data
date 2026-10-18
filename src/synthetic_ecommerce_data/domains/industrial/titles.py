"""A product's title and description: the style a brand lists a type in, the
dimension segments, the repair that makes sibling titles distinct, and the
description sentence.

Split from :mod:`.generate` (elastic/prism-industrial-products#266): the
:class:`~.generate.Generator` inherits :class:`TitleMixin`, and every method
here reads the generator's own state through ``self``.
"""

from __future__ import annotations

import hashlib

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.model import (
    Attribute,
)
from synthetic_ecommerce_data.core.naming import (
    LABEL_FORMS,
    Segment,
    Title,
    abbreviate_value,
    build_title,
    states_value,
    thread_parts,
)
from synthetic_ecommerce_data.core.voice import description_tail
from synthetic_ecommerce_data.domains.industrial.drafts import (
    END_SHAPE_OF_TYPE,
    END_SHAPE_WORD,
    KEY_DIMENSIONS,
    ChildDraft,
    LineDraft,
    _weighted,
)
from synthetic_ecommerce_data.domains.industrial.vocab import (
    STANDARDS_FAMILY,
)


class TitleMixin:
    """Title and description assembly, mixed into :class:`~.generate.Generator`."""

    #: A (brand, type)'s title style, drawn ONCE per pair: "unlabelled" names
    #: the key dimension bare, "labelled" with its label, "secondary" labels it
    #: and adds a labelled secondary dimension. One maker lists one type one
    #: way; the census mix is reproduced ACROSS brands, not per SKU.
    TITLE_STYLES = ("unlabelled", "secondary", "labelled")

    def _title_style(self, brand: str, type_key: str) -> str:
        """The (brand, type)'s style: fixed per pair, and the census mix is hit
        ACROSS the type's makers by their market weight.

        The makers of a type are put in a seeded order and each takes the style
        its slice of the type's market weight falls in: the first 46.7% of
        weight unlabelled, the next 17.1% secondary, the rest labelled. A
        brand's share of a type's SKUs follows its weight, so the per-title
        mix approximates the census while every brand keeps one style. (A
        per-pair coin flip did not: 250 pairs weighted by SKU count drifted to
        0.35 / 0.26 against 0.47 / 0.17.)
        """
        cfg = self.config
        key = (brand, type_key)
        style = self._title_styles.get(key)
        if style is None:
            makers = sorted(
                brands.brands_for(type_key),
                key=lambda b: hashlib.sha256(
                    f"{cfg.seed}:title:{b.name}:{type_key}".encode()
                ).hexdigest(),
            )
            total = sum(b.weight for b in makers)
            cumulative = 0.0
            for maker in makers:
                middle = (cumulative + maker.weight / 2) / total
                cumulative += maker.weight
                if middle < cfg.title_token_unlabelled:
                    choice = "unlabelled"
                elif middle < cfg.title_token_unlabelled + cfg.title_token_not_primary:
                    choice = "secondary"
                else:
                    choice = "labelled"
                self._title_styles[(maker.name, type_key)] = choice
            style = self._title_styles.get(key, "labelled")
        return style

    def _dimension_segments(self, draft: LineDraft, child: ChildDraft) -> list[Segment]:
        """The title's dimension segments, in the (brand, type)'s ONE style.

        The key dimension (the child's primary, the axis the line varies on)
        is ALWAYS named; the style decides only whether it carries a label and
        whether a labelled secondary dimension follows it. A secondary is named
        only when the record PUBLISHES it -- a title naming a length the
        attribute block does not carry states a spec the record cannot back.
        """
        primary = child.primary
        if primary is None:
            return []
        style = self._title_style(draft.brand, draft.type_key)
        self._bump("title_token")
        # Named only when the record publishes it, like a secondary.
        also = (
            [
                Segment(
                    value=child.also.value,
                    label=self._label_for(child.also.name),
                    attribute=child.also.name,
                )
            ]
            if child.also is not None and child.also.name in self._published
            else []
        )
        if style == "unlabelled":
            self._bump("title_token_unlabelled")
            return [Segment(value=primary.value, label=None, attribute=primary.name), *also]
        segments = [
            Segment(
                value=primary.value, label=self._label_for(primary.name), attribute=primary.name
            ),
            *also,
        ]
        if style == "secondary":
            # The pair's secondary dimension, fixed like its style: the pair
            # ranks the secondary classes once, and each title names the
            # first one THIS record publishes. It used to pick by
            # ``digest % len(classes this child has)``, so an end mill with a
            # neck and one without picked different classes -- and a pick the
            # record did not publish left that title with no secondary, while
            # its siblings had one. A title names a secondary whenever the
            # record publishes one, or never (a "labelled" pair).
            attribute = next(
                (
                    child.secondary[k]
                    for k in self._secondary_order(draft.brand, draft.type_key)
                    if k in child.secondary
                    and child.secondary[k].name in self._published
                    and child.secondary[k].name != primary.name
                ),
                None,
            )
            if attribute is not None:
                self._bump("title_token_not_primary")
                segments.append(
                    Segment(
                        value=attribute.value,
                        label=self._label_for(attribute.name),
                        attribute=attribute.name,
                    )
                )
        return segments

    def _secondary_order(self, brand: str, type_key: str) -> list[str]:
        """The (brand, type)'s ranking of the secondary classes: the census mix,
        rotated by a seeded digest of the pair so makers lead with different
        ones."""
        classes = list(self.config.title_secondary_mix)
        digest = hashlib.sha256(f"{self.config.seed}:secondary:{brand}:{type_key}".encode())
        start = int(digest.hexdigest()[:8], 16) % len(classes)
        return classes[start:] + classes[:start]

    def _label_for(self, attribute_name: str) -> str:
        forms = LABEL_FORMS.get(attribute_name)
        if not forms:
            return attribute_name
        if self._voice is None:
            return str(_weighted(self.rng, forms))
        # The BRAND's spelling: every title one maker lists spells a label
        # the same way (:mod:`.voice`).
        return self._voice.labels[attribute_name]

    def _build_line_title(self, draft: LineDraft, child: ChildDraft) -> Title:
        """A SKU title, in one of the two measured styles: the brand's."""
        voice = self._voice
        assert voice is not None, "a title is composed inside _finish_line"
        descriptive = voice.descriptive
        segments: list[Segment] = []
        if draft.bare_title:
            return build_title(
                draft.item, (), cap=self.config.title_length_cap, tight_delimiter_at=None
            )

        # The type's KEY dimension, when the variant axis is something else
        # (a bearing's closure, a wheel's grit): the census core of a title
        # names what the part IS, so a bearing title carries its number and a
        # wheel its diameter. Only a value the record publishes.
        key_values = {a.name: a.value for a in (*draft.line_attrs, *child.attrs)}
        for name in KEY_DIMENSIONS.get(draft.type_key, ()):
            if name in self._published and name in key_values:
                segments.append(Segment(value=key_values[name], label=None, attribute=name))

        segments.extend(self._dimension_segments(draft, child))

        for name, value in draft.descriptors:
            # A descriptor the record does not publish (sparsity dropped it)
            # is not stated: measured, 27 bearing titles named a ring
            # material their attribute block did not carry.
            if name not in self._published:
                continue
            text = value if descriptive else abbreviate_value(value)
            segments.append(Segment(value=text, label=None, attribute=name))

        flutes = next(
            (
                a
                for a in draft.line_attrs
                if a.name == "Number of Flutes" and a.name in self._published
            ),
            None,
        )
        if flutes is not None:
            label = self._label_for("Number of Flutes")
            segments.append(Segment(value=flutes.value, label=label, attribute=flutes.name))

        if not descriptive:
            end = next(
                (a for a in draft.line_attrs if a.name == "Single End/Double End"),
                None,
            )
            # The end SHAPE is the mill's own style: "SGL Sq End" on a square
            # end mill, "SGL Ball End" on a ball nose one. It used to say
            # "Sq End" on every end mill, ball nose included.
            shape = END_SHAPE_OF_TYPE.get(draft.type_key)
            if end is not None and shape is not None:
                segments.append(
                    Segment(
                        value=f"{abbreviate_value(end.value)} {END_SHAPE_WORD[shape]} End",
                        label=None,
                    )
                )

        # NO label is cut off here any more. This block used to fire at the
        # measured 3.23% and publish titles ending "Dia./Thread Siz" or
        # "Number of Flut". The reference distributor's real titles carry none of it --
        # measured 24/24 clean on the scraped sample -- so it was a defect
        # class we invented, and it reads to a viewer as our rendering bug
        # rather than as a fact about catalog data. Removed by the ruling on
        # elastic/prism#9284, which is the same call already made for missing
        # product images: reproduce the defects the demo is meant to EXPOSE,
        # not the ones that merely make it look unfinished.
        #
        # ``truncate_label`` and ``Segment.truncated`` stay in naming.py: the
        # honest-rendering property they exist for is now proven by a test
        # fixture (elastic/prism#9288) rather than by shipped catalog data.

        # The pack segment, last so the cap sheds it first -- and ONLY with the
        # record's own Package Quantity; no quantity is ever stated unbacked.
        quantity = self._line_facts.get("Package Quantity")
        if quantity is not None and voice.pack_label is not None:
            segments.append(
                Segment(value=quantity, label=voice.pack_label, attribute="Package Quantity")
            )

        tight = (
            min(int(voice.tight_at * len(segments)), len(segments) - 1)
            if segments and voice.tight_at is not None
            else None
        )
        qualifier = voice.qualifier[STANDARDS_FAMILY[draft.type_key]]
        item = f"{qualifier} {draft.item}" if qualifier else draft.item
        return build_title(
            f"{draft.brand} {item}" if voice.brand_first else item,
            tuple(segments),
            cap=self.config.title_length_cap,
            tight_delimiter_at=tight,
        )

    def _identifying_attribute(self, published: list[list[Attribute]]) -> str | None:
        """The ONE attribute that tells every SKU of a line apart, or None.

        Derived from the line's own records, never listed per product type: a
        hand-maintained per-type enumeration has gone stale in this repository
        twice already, and the data answers the question exactly. An attribute
        whose value is the same on every SKU distinguishes nothing -- a shopper
        choosing between six alloy-steel screws is not choosing the material,
        and ``Fastener Material: Alloy Steel`` belongs in the attribute block.

        Two conditions, and both are needed for the answer to be USABLE in a
        title. The attribute has to be on EVERY record (one carried by a fifth
        of them cannot name the other four fifths), and its published values
        have to be pairwise DISTINCT (a thread length that saturates at
        2D + 1/2" varies across the line and is still the same string on ten
        of twelve SKUs). An attribute failing either is not an identifier,
        whatever its spread.

        Among the ones that qualify, the widest RELATIVE variation wins, max
        over min of the parsed magnitudes: a line's SKUs are one product in
        several sizes, and the size that spreads furthest is the one being
        chosen between. Ties keep the attribute the type builder published
        first, so the answer never depends on dictionary ordering.

        Measured against what the records PUBLISH -- after sparsity has
        dropped what it drops and after the defect injection has rewritten
        what it rewrites -- rather than against the drafts. An attribute
        chosen off the drafts can be absent from the record by the time it is
        emitted, and a title naming a value its own attribute block does not
        carry is the defect this is here to remove, not a fix for it.
        Measured: 52 titles named a draft value the record had since lost.
        """
        if len(published) < 2:
            return None
        values: dict[str, list[str]] = {}
        numbers: dict[str, list[float]] = {}
        order: list[str] = []
        for attributes in published:
            for attribute in attributes:
                if attribute.name not in values:
                    values[attribute.name] = []
                    numbers[attribute.name] = []
                    order.append(attribute.name)
                values[attribute.name].append(attribute.value)
                if attribute.value_num is not None:
                    numbers[attribute.name].append(attribute.value_num)

        best: str | None = None
        best_spread = -1.0
        for name in order:
            seen = values[name]
            if len(seen) != len(published) or len(set(seen)) != len(published):
                continue
            magnitudes = [value for value in numbers[name] if value > 0]
            spread = max(magnitudes) / min(magnitudes) if len(magnitudes) > 1 else 0.0
            if spread > best_spread + 1e-9:
                best, best_spread = name, spread
        return best

    def _disambiguate_titles(
        self,
        titles: list[Title],
        published: list[list[Attribute]],
        identifying: str | None,
    ) -> list[Title]:
        """Give two SKUs of one line that share a title the thing that differs.

        This is the defect a shopper meets on the first screen: six cards
        reading ``Socket Head Cap Screw, M6x1, Alloy Steel`` at $2.10, $2.48,
        $4.85, $8.00, $8.34 and $10.42, identical in every visible respect.
        They are not duplicates -- they are 12, 16, 30 and 45 mm long -- and a
        thread size is LINE-constant, so a title built around it says the same
        thing on every SKU under the line. Measured before this: 176 of 500
        lines published a title two of their SKUs shared, over 1,214 SKUs.

        Repair rather than prevention, and deliberately so. The measured title
        grammar contains two hazards worth more than tidiness -- a dimension
        token with no label (46.7%) and a token that is NOT the primary
        dimension (17.1%) -- and composing every title around the identifying
        attribute would erase both. So the titles are composed as measured,
        and only the ones that actually collide are given one more segment.
        An end mill's title is untouched by this: its cutting diameter varies
        down the line, so its titles were already distinct.

        The segment goes in SECOND, right after the dimension token, so the
        100-character cap can never be what removes it -- and the title is
        reassembled from the segments it already had rather than rebuilt, so
        no measured choice is re-rolled.

        The trigger is NOT "two titles are the same string". That was the
        first formulation and it is too weak by a factor of five: a title
        carries the brand about a third of the time and a label in one of
        several abbreviations, so ``Hex Head Bolt, 7/16-14, Grade 8`` and
        ``Vellinhorst Hex Head Bolt, 7/16-14, Grade 8`` are different strings that
        tell a shopper apart by the brand name of the line they are both in.
        Measured, 705 SKUs passed a string-equality check while naming nothing
        that was theirs. The trigger is the PROPERTY instead: a title has to
        name a value this SKU publishes and its siblings do not.
        """
        if identifying is None or len(published) < 2:
            return titles
        by_name = [{a.name: a.value for a in attributes} for attributes in published]
        for index, title in enumerate(titles):
            mine = by_name[index]
            # Per ATTRIBUTE, not per value: the same string legitimately
            # appears on two SKUs of one line in two different roles -- a 3/8"
            # that is one tool's cutting diameter and another's shank -- and
            # that collision is what this catalog exists to exhibit.
            alone = [
                value
                for name, value in mine.items()
                if not any(
                    other.get(name) == value
                    for position, other in enumerate(by_name)
                    if position != index
                )
            ]
            if any(states_value(title.text, value) for value in alone):
                continue
            # No exemption for a title that already NAMES the identifying
            # attribute. It can name it and still be carrying a value the
            # record no longer publishes: a title is composed before the
            # defect injection, so a unit-mixing defect leaves a title reading
            # ``3/8"`` on a record publishing ``9.52mm``, and a shopper
            # scanning the card cannot tell that apart from a third size.
            # Measured at 8 rows on the 4,688-document generation that
            # preceded this catalog, and NOT re-derived here -- the
            # denominator names the catalog the figure belongs to rather
            # than being renumbered to this one's 4,689 on the assumption
            # that the numerator held. The published value goes in regardless,
            # and the stale token stays where it was -- mixed units inside one
            # record are a defect class this catalog carries on purpose, not
            # one to quietly repair.
            attribute = next((a for a in published[index] if a.name == identifying), None)
            if attribute is not None:
                segment = Segment(
                    value=attribute.value,
                    label=self._label_for(attribute.name),
                    attribute=attribute.name,
                )
                at = min(1, len(title.segments))
                segments = (*title.segments[:at], segment, *title.segments[at:])
                tight = title.tight_delimiter_at
                if tight is not None and tight >= at:
                    tight += 1
                titles[index] = build_title(
                    title.item,
                    segments,
                    cap=self.config.title_length_cap,
                    tight_delimiter_at=tight,
                )
                self._bump("title_disambiguated")
        return titles

    def _build_description(
        self,
        draft: LineDraft,
        title: Title,
        attributes: list[Attribute],
        compatibility: str = "",
    ) -> str:
        """The description, in the grammar the real rows use.

            <title clause> - <the dimensions the title had no room for>,
            <line descriptors>, <brand line>

        Measured over the 24 real rows this catalog is modelled against, 24 of
        24 compose exactly that way::

            TITLE        Square End Mill: 3/4" Dia, 1-1/2" LOC
            DESCRIPTION  Square End Mill: 3/4" Dia, 1-1/2" LOC - 4" OAL,
                         3/4" Shank Dia, 40 deg Helix, AlTiN Finish, ...

        Three properties are load-bearing, and none of them is an accident:

        * **The title is the description's opening clause, verbatim.** The
          overlap is the SOURCE's own convention rather than duplication to be
          tidied away -- a marketplace listing repeats its size in the title,
          in the variant selector and twice in the specification table,
          because each tier is read at a different moment. Removing the
          overlap would be improving away the thing being reproduced.
        * **After the dash is what the title had no room for**: the attributes
          this SKU actually publishes, with their units, so that a shopper
          scanning six neighbouring cards can see what separates them without
          opening any of them.
        * **The brand line stays, at the end.** It is what the description
          used to be in its entirety -- ``Ingleward ISO4762-64 -- Socket
          Head Cap Screw`` -- which restated the title, the brand and the
          product type and said nothing at all about this SKU. It earns a
          place; it does not earn the whole field.

        Composed from the attributes the record PUBLISHES, after sparsity and
        after defect injection, so the description and the attribute block
        cannot disagree about a value.
        """
        named = title.attribute_names()
        details: list[str] = []
        for attribute in attributes:
            # Skipped only when the title states THIS value. A title composed
            # before the unit-mixing defect can name the attribute with its
            # pre-defect token (``5-5/16"`` beside a published ``134.94mm``);
            # the description then has to carry the value the record publishes.
            if attribute.name in named and (
                attribute.values is not None or states_value(title.text, attribute.value)
            ):
                continue
            if attribute.values is not None:
                details.append(", ".join(attribute.values))
            else:
                details.append(f"{attribute.value} {attribute.name}")
        published = {*self._line_facts, *(a.name for a in attributes)}
        details.extend(
            value
            for name, value in draft.descriptors
            if name in published and not states_value(title.text, value)
        )
        # A glued size the title or the spec clause names is one token to the
        # analyzer, so its parts are written out as well (#33).
        details.extend(thread_parts(f"{title.text} {', '.join(details)}"))
        details.append(f"{draft.brand} {draft.series}")
        facts = {**self._line_facts, **{a.name: a.value for a in attributes}}
        tail = description_tail(draft.brand, draft.series, draft.type_key, facts)
        # The cross-reference sentence (:mod:`.compat`) sits between the spec
        # clause and the brand's template, where a distributor prints "for M12
        # socket head cap screws".
        middle = f"{compatibility} " if compatibility else ""
        return f"{title.text} - {', '.join(details)}. {middle}{tail}"

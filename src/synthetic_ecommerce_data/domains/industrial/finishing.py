"""Line finishing and attribute assembly: sparsity, the measurement-system and
standards attributes, series uniqueness, the finished line and its price draw.

Split from :mod:`.generate` (elastic/prism-industrial-products#266): the
generator inherits :class:`FinishMixin` and these methods read its state
through ``self``.
"""

from __future__ import annotations

import functools

from synthetic_ecommerce_data.core import brands, noise, price
from synthetic_ecommerce_data.core.model import (
    Attribute,
    ProductLine,
    Sku,
    keyword_attribute,
    multi_attribute,
    pricing_unit_for,
)
from synthetic_ecommerce_data.core.naming import (
    Title,
)
from synthetic_ecommerce_data.core.voice import product_name, voice_for
from synthetic_ecommerce_data.domains.industrial import (
    compat,
    conformance,
)
from synthetic_ecommerce_data.domains.industrial.drafts import (
    MAX_MISSES,
    LineDraft,
    RetiredAttribute,
    _weighted,
)
from synthetic_ecommerce_data.domains.industrial.taxonomy import drawing_for, image_id_for
from synthetic_ecommerce_data.domains.industrial.type_labels import label_for
from synthetic_ecommerce_data.domains.industrial.vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    MEASUREMENT_SYSTEM_PRESENCE,
    MEASUREMENT_SYSTEM_VALUES,
    STANDARDS_FAMILY,
    STANDARDS_NAME,
    STANDARDS_PRESENCE,
    VOCAB,
)


class FinishMixin:
    """Attribute assembly and line finishing, mixed into :class:`~.generate.Generator`."""

    # -- the shared post-pass --------------------------------------------

    def _apply_sparsity(self, type_key: str, attrs: list[Attribute], scope: str) -> list[Attribute]:
        """Drop optional attributes at their measured presence rate."""
        return self._sparsify(type_key, attrs, scope)[0]

    def _sparsify(
        self, type_key: str, attrs: list[Attribute], scope: str
    ) -> tuple[list[Attribute], list[Attribute]]:
        """The published attributes, and the retired ones whose draw kept them.

        A retired attribute (#497) takes the draw its published self took, so no
        later draw moves, and is never published; the second list holds those
        the draw would have kept, which the "already made" check still counts.
        """
        rates = {spec.name: spec for spec in VOCAB[type_key] if spec.scope == scope}
        kept: list[Attribute] = []
        ghosts: list[Attribute] = []
        for attribute in attrs:
            if isinstance(attribute, RetiredAttribute):
                if self.rng.random() <= self.config.scaled_presence(attribute.presence):
                    ghosts.append(attribute)
                continue
            spec = rates.get(attribute.name)
            if spec is None:
                kept.append(attribute)
                continue
            if self.rng.random() <= self.config.scaled_presence(spec.presence):
                kept.append(attribute)
        return kept, ghosts

    def _standards_attribute(self, type_key: str, draft: LineDraft) -> Attribute | None:
        """The standards this LINE conforms to, from :mod:`.conformance`'s
        truth table -- never a draw from a pool of standards for other parts."""
        if self.rng.random() > STANDARDS_PRESENCE:
            return None
        pool = conformance.applicable(
            type_key,
            {a.name: a.value for a in draft.line_attrs},
            metric=bool(draft.children) and draft.children[0].system == "mm",
            provenance=draft.provenance,
            standard=draft.standard,
        )
        if not pool:
            return None
        how_many = self.rng.choices((1, 2, 3), weights=(0.45, 0.35, 0.20), k=1)[0]
        values = tuple(sorted(self.rng.sample(list(pool), k=min(how_many, len(pool)))))
        self._bump("standards_present")
        if len(values) > 1:
            self._bump("standards_multivalued")
        self._bump("standards_values", len(values))
        return multi_attribute(STANDARDS_NAME, values)

    def _measurement_system(
        self, system: str, name: str, *, count: bool = True
    ) -> tuple[Attribute | None, bool]:
        """The measurement-system attribute, under the spelling its LINE uses.

        The spelling is chosen once per product line, not once per record. A
        line is one supplier's feed, and a supplier is internally consistent
        about what it calls this field; the inconsistency is BETWEEN families,
        which is exactly the case a field map has to absorb. Drawing it per
        record instead put all three spellings inside every product type,
        which is both less realistic and useless as a test of scoping.

        Returns the attribute and whether its declared value contradicts the
        units actually used in the record -- a measured defect class, so the
        contradiction is produced here rather than patched in afterwards.
        """
        if self.rng.random() > MEASUREMENT_SYSTEM_PRESENCE:
            return None, False
        truthful = (
            "Metric" if system == "mm" else str(_weighted(self.rng, MEASUREMENT_SYSTEM_VALUES))
        )
        if truthful == "Metric" and system == "in":
            truthful = "Fractional Inch"
        contradicts = self.rng.random() < self.config.scaled_defect(
            self.config.defect_system_contradicts_units
        )
        if contradicts:
            value = "Fractional Inch" if system == "mm" else "Metric"
            if count:
                self._bump("defect_system_contradicts")
        else:
            value = truthful
        if count:
            self._bump("measurement_system_present")
        return keyword_attribute(name, value), contradicts

    #: spec a SKU must not share with another of its brand and type.
    IDENTIFIER_ATTRIBUTES = frozenset({"List Number"})
    #: What makes a SKU different is SUBSTANCE, never metadata: the
    #: measurement-system attribute (three spellings of one fact about the
    #: record's units) and the standards claimed are not what a shopper tells
    #: two parts apart by. Left out of both uniqueness checks, with the
    #: identifiers (the review of the 100K catalog: washers differing only by
    #: "Dimension Type" vs "System of Measurement").
    METADATA_ATTRIBUTES = frozenset(
        {STANDARDS_NAME, *(name for name, _ in MEASUREMENT_SYSTEM_NAMES)}
    )
    NOT_SUBSTANCE = IDENTIFIER_ATTRIBUTES | METADATA_ATTRIBUTES

    @classmethod
    def _spec_key(cls, type_key: str, brand: str, attributes: list[Attribute]) -> tuple:
        """What makes two SKUs the same product: type, brand, every attribute.

        Identifiers (``List Number``) are left out, and so is everything that
        is not an attribute -- the SKU, the product id, the image, the price
        and the stock. Brand is IN: the same standard part from two makers is
        two products, as on any marketplace.
        """
        spec = tuple(
            sorted(
                (a.name, a.value if a.values is None else "|".join(a.values))
                for a in attributes
                if a.name not in cls.NOT_SUBSTANCE
            )
        )
        return (type_key, brand, spec)

    def _unique_series(self, draft: LineDraft, line_attrs: list[Attribute]) -> None:
        """Give the product a series no other product of its brand has in this type.

        The set walked here is the type's own (:mod:`.typespec`), so it never
        sees another type's series. Names stay unique across types only
        because each type's series shape is disjoint from every other's
        (``BR###``, ``FD###``, ``ISO4017-``, ...). Nothing here enforces that;
        ``test_no_two_products_share_a_product_name_catalog_wide`` catches a
        clash after the fact.

        A drawn series already taken walks its trailing number up, one step at
        a time, to the first free one -- deterministic, and never a re-draw.
        The walk touches the series and the IDENTIFIER attributes that publish
        it (``List Number``) and NOTHING else: a value that carries meaning --
        a bearing number, a size -- is never rewritten, even when it equals the
        series (the first version walked 11,784 bearing numbers to numbers that
        are not bearings; tests/test_catalog_brands_voice.py now holds every
        bearing to its table entry).
        """
        taken = self._used_series
        series = draft.series
        while (draft.brand, series) in taken:
            head = series.rstrip("0123456789")
            tail = series[len(head) :]
            series = f"{head}{int(tail) + 1}" if tail else f"{series}1"
        taken.add((draft.brand, series))
        if series != draft.series:
            self._bump("series_walked")
            old = draft.series
            draft.series = series

            def walked(attribute: Attribute) -> Attribute:
                if attribute.name in self.IDENTIFIER_ATTRIBUTES and attribute.value == old:
                    return Attribute(attribute.name, series)
                return attribute

            line_attrs[:] = [walked(a) for a in line_attrs]
            draft.line_attrs = [walked(a) for a in draft.line_attrs]

    @functools.cache  # noqa: B019 - a pure function of the config and the type
    def _always_published(self, type_key: str) -> frozenset[str]:
        """The attributes sparsity never drops for this type (presence 1.0)."""
        return frozenset(
            spec.name
            for spec in VOCAB[type_key]
            if self.config.scaled_presence(spec.presence) >= 1.0
        )

    def _differs_only_by_a_drop(
        self,
        type_key: str,
        brand: str,
        published: list[Attribute],
        retired_always: frozenset[str] = frozenset(),
    ) -> bool:
        """Whether a published spec is a subset or superset of one already made.

        Two SKUs whose published attributes differ only in that one lacks an
        attribute the other carries are NOT different to a shopper, whatever
        the dropped value was (measured on the first 100K build: 3,212 such
        SKUs). Compared within the bucket of SKUs that agree on every
        always-published attribute -- the only place a subset can live -- so
        the check stays cheap at 100K. Records the spec when it is new.
        """
        spec = frozenset(
            (a.name, a.value if a.values is None else "|".join(a.values))
            for a in published
            if a.name not in self.NOT_SUBSTANCE
        )
        always = self._always_published(type_key) | retired_always
        bucket = (type_key, brand, tuple(sorted(x for x in spec if x[0] in always)))
        made = self._published_specs.setdefault(bucket, [])
        if any(spec <= other or other <= spec for other in made):
            return True
        made.append(spec)
        return False

    def _finish_line(self, type_key: str, draft: LineDraft, index: int) -> ProductLine | None:
        rng = self.rng
        line_attrs, line_ghosts = self._sparsify(type_key, draft.line_attrs, "line")
        # One spelling of the measurement-system attribute per line.
        system_name = str(_weighted(rng, MEASUREMENT_SYSTEM_NAMES))
        standards_attr = self._standards_attribute(type_key, draft)
        # A builder may state the standard its own table is (a socket screw's
        # ASME B18.3): that is the SAME attribute as the conformance draw, so
        # the two are one list of distinct values, never two entries (#497).
        stated = [a for a in line_attrs if a.name == STANDARDS_NAME]
        if stated:
            line_attrs = [a for a in line_attrs if a.name != STANDARDS_NAME]
            union = list(
                dict.fromkeys(
                    v
                    for a in (*stated, *([standards_attr] if standards_attr else []))
                    for v in (a.values or (a.value,))
                )
            )
            standards_attr = multi_attribute(STANDARDS_NAME, tuple(union))
        if standards_attr is not None:
            line_attrs = [*line_attrs, standards_attr]

        draft.type_key = type_key
        self._unique_series(draft, line_attrs)
        self._voice = voice_for(draft.brand)
        self._line_facts = {a.name: a.value for a in line_attrs}

        # The product id is built before the SKUs, because every SKU's image
        # id names it: one drawing per SKU, filed under its product.
        product_id = self.minter.product_id(brands.BY_NAME[draft.brand].code, draft.series, index)

        # Composed first, for every SKU, because whether a title needs the
        # thing that differs is a question about the LINE and cannot be
        # answered one SKU at a time.
        built: list[tuple[str, list[Attribute], float, int]] = []
        titles: list[Title] = []
        line_system: tuple[tuple[Attribute | None, bool]] | None = None
        if len({c.system for c in draft.children}) > 1:
            raise ValueError(f"{type_key}: a product's SKUs are in one measurement system")
        for child in draft.children:
            attrs, sku_ghosts = self._sparsify(type_key, list(child.attrs), "sku")
            if not attrs and not child.zero_axis:
                continue
            attrs = self._inject_defects(
                child, attrs, tuple(a for a in child.attrs if isinstance(a, RetiredAttribute))
            )
            # The measurement system is the PRODUCT's (gen#63): the first SKU's draw
            # decides whether it is published, its value and whether it contradicts
            # the units, and every SKU of the line carries that one attribute. The
            # later SKUs still take their draws (uncounted), so no other value in
            # the build moves.
            drawn = self._measurement_system(child.system, system_name, count=line_system is None)
            line_system = line_system or (drawn,)
            (system_attr, _) = line_system[0]
            if system_attr is not None and not child.zero_axis:
                attrs = [*attrs, system_attr]
            # Each SKU is different from every other SKU of its brand and type.
            # A membership check, i.e. rejection: a draft whose UNSPARSIFIED
            # spec this brand has already made, or whose published spec differs
            # from one already made only by a dropped attribute, is not made.
            unsparsified = [
                *draft.line_attrs,
                *([standards_attr] if standards_attr is not None else []),
                *child.attrs,
                *([system_attr] if system_attr is not None else []),
            ]
            key = self._spec_key(type_key, draft.brand, unsparsified)
            # What #497 retired still tells two specs apart while its draw kept
            # it, as it did when it was published (see :class:`.RetiredAttribute`).
            retired = [*line_ghosts, *sku_ghosts]
            if key in self._drawn_specs or self._differs_only_by_a_drop(
                type_key,
                draft.brand,
                [*line_attrs, *attrs, *retired],
                frozenset(a.name for a in retired if a.always),
            ):
                self._bump("spec_already_drawn")
                continue
            self._drawn_specs.add(key)

            sku = self.minter.new_sku()
            self._published = {a.name for a in (*line_attrs, *attrs)}
            titles.append(self._build_line_title(draft, child))
            # One draw, where the uniform multiplier this replaced drew one, so
            # every later draw (stock and on) is the draw it always was.
            sku_u = rng.random()
            shown = price.shown_price(
                self._price_draw(type_key, draft.brand, unsparsified, draft.line_attrs, sku, sku_u)
            )
            stock = rng.choices(
                (0, rng.randint(1, 40), rng.randint(40, 900)), weights=(0.08, 0.42, 0.5)
            )[0]
            built.append((sku, attrs, shown, stock))

        # A (type, brand) that drafts line after line and makes nothing has
        # spent its spec space: after MAX_MISSES in a row it stops getting
        # products of that type (``brands.pick_brand`` excludes it).
        pair = (type_key, draft.brand)
        if not built:
            self._misses[pair] = self._misses.get(pair, 0) + 1
            if self._misses[pair] >= MAX_MISSES:
                self._exhausted.add(pair)
                self._bump("brand_type_exhausted")
            return None
        self._misses[pair] = 0

        published = [attrs for _, attrs, _, _ in built]
        titles = self._disambiguate_titles(
            titles, published, self._identifying_attribute(published)
        )

        # The variant axis: what "also available in" names the siblings by.
        axis = draft.children[0].primary.name if draft.children else None
        siblings = [
            next((a.value for a in attrs if a.name == axis), "") for _, attrs, _, _ in built
        ]
        children: list[Sku] = []
        for (sku, attrs, shown, stock), title in zip(built, titles, strict=True):
            # From the PUBLISHED values, after sparsity and defects, so the
            # sentence can never disagree with the record it sits on.
            values = {a.name: a.value for a in (*line_attrs, *attrs)}
            compatibility = compat.sentence_for(type_key, values) or ""
            noise_text = " ".join(
                noise.sentences(
                    type_key,
                    values,
                    sku=sku,
                    seed=self.config.seed,
                    noise=self.config.noise,
                    provenance=draft.provenance,
                    primary=values.get(axis) if axis else None,
                    siblings=siblings,
                )
            )
            extra = " ".join(part for part in (compatibility, noise_text) if part)
            children.append(
                Sku(
                    sku=sku,
                    title=title.text,
                    description=self._build_description(draft, title, attrs, extra),
                    attributes=tuple(attrs),
                    price_usd=shown,
                    stock=stock,
                    image_id=image_id_for(type_key, product_id, sku),
                    compatibility=compatibility,
                    noise=noise_text,
                    pricing_unit=pricing_unit_for(values.get("Units per Pack")),
                )
            )
            self._bump("skus")

        parent_title = product_name(
            draft.brand, draft.series, draft.item, STANDARDS_FAMILY[type_key]
        )
        return ProductLine(
            product_id=product_id,
            type_key=type_key,
            title=parent_title,
            brand=draft.brand,
            series=draft.series,
            category=draft.category,
            attributes=tuple(line_attrs),
            children=tuple(children),
            dimension_provenance=draft.provenance,
            # A grouped card shows its first variant's drawing until one is
            # selected; the product has no drawing of its own to disagree.
            image_id=children[0].image_id,
            drawing=drawing_for(type_key),
            type_label=label_for(type_key),
        )

    def _price_draw(
        self,
        type_key: str,
        brand: str,
        attributes: list[Attribute],
        line_attributes: list[Attribute],
        sku: str,
        sku_u: float,
    ) -> price.Draw:
        """What a SKU's shown price is computed from (:mod:`.price`), read off
        its unsparsified attributes, so a dropped or defective published value
        never moves its price. Its group (:func:`.price.group_draw`) is read
        off the line attributes sparsity never drops."""
        model = price.model_for(type_key)
        facts = {a.name: a for a in attributes}
        material = price.material_of(type_key, facts)
        pack = None
        if model.pack_attribute is not None and model.pack_attribute in facts:
            pack = facts[model.pack_attribute].value_num
        key = price.price_key(type_key, facts)
        struct = price.structure(
            model,
            key,
            material,
            brands.tier_of(brand, type_key),
            pack,
            price.length_of(facts) if type_key in price.LENGTH_HELD else None,
            facts[model.option_attribute].value if model.option_attribute in facts else None,
        )
        seed = self.config.seed
        always = self._always_published(type_key)
        group_u = price.group_draw(
            seed,
            type_key,
            brand,
            (
                a
                for a in line_attributes
                if a.name in always or (isinstance(a, RetiredAttribute) and a.always)
            ),
        )
        size_u = price.size_draw(seed, type_key, key, material)
        return price.Draw(model, struct, group_u, sku_u, price.ending_draw(seed, sku), size_u)

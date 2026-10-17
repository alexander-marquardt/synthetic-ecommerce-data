"""Defect injection: the internal contradictions real catalogs carry.

Each class is drawn against its own denominator, on a record that was correct
a moment earlier (see :mod:`.generate`). Split from it
(elastic/prism-industrial-products#266): the generator inherits
:class:`DefectMixin` and these methods read its state through ``self``.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.core.formats import (
    canonical_style,
)
from synthetic_ecommerce_data.core.model import (
    Attribute,
    length_attribute,
)
from synthetic_ecommerce_data.domains.industrial.drafts import (
    UNIT_SPLIT_KEYS,
    ChildDraft,
)
from synthetic_ecommerce_data.domains.industrial.vocab import (
    VOCAB,
)


class DefectMixin:
    """The post-pass defects, mixed into :class:`~.generate.Generator`."""

    def _inject_defects(self, child: ChildDraft, attrs: list[Attribute]) -> list[Attribute]:
        """Reproduce the measured internal contradictions.

        Each class is drawn against its own denominator: only a record that
        actually carries the attribute pair is eligible, which is how the
        reference statistics measure these rates.
        """
        cfg = self.config
        rng = self.rng
        by_name = {a.name: i for i, a in enumerate(attrs)}
        out = list(attrs)

        # Class 1: length of cut longer than overall length.
        loc_names = ("Length of Cut", "Flute Length", "Thread Length")
        loc_index = next((by_name[n] for n in loc_names if n in by_name), None)
        oal_index = by_name.get("Overall Length") or by_name.get("Length")
        if "Overall Length" in by_name:
            oal_index = by_name["Overall Length"]
        elif "Length" in by_name:
            oal_index = by_name["Length"]
        else:
            oal_index = None
        if loc_index is not None and oal_index is not None:
            self._bump("eligible_loc_oal")
            if rng.random() < cfg.scaled_defect(cfg.defect_loc_exceeds_oal):
                oal = out[oal_index]
                loc = out[loc_index]
                if oal.value_num and loc.value_num:
                    # Publish a cut longer than the tool, the way the corpus
                    # does: the same "3 in" against a shorter overall length.
                    inflated = oal.value_num * rng.uniform(1.2, 2.5)
                    # In the record's OWN system: publishing the inflated value
                    # in the other unit would inject a second defect class
                    # (unit mixing) as a side effect, and the two rates are
                    # measured separately.
                    # The record's OWN system, in the catalog's ONE spelling
                    # for it. This used to pick its own style -- " in" at two
                    # decimals -- which published "2.25 in" beside the
                    # "2-1/4"" every other row of the same column carried, and
                    # split that size across two facet buckets. The DEFECT
                    # here is the value (a cut longer than the tool); its
                    # spelling was never part of it. Keep the bad value, drop
                    # the bad spelling (elastic/prism#9284).
                    style = canonical_style(child.system)
                    out[loc_index] = length_attribute(loc.name, self._publish(inflated, style))
                    self._bump("defect_loc_exceeds_oal")

        # Class 2 (the angular attribute carrying a length unit) is declined: a
        # length under an angle key is a value of the wrong kind, which this
        # generator does not write (#404, ``measured_angle_carries_length_unit``).

        # Class 3: unit mixing inside one record -- one dimension published in
        # the other system.
        # LENGTHS only. "Unit mixing" is a record describing itself in two
        # measurement systems; a grit number, a flute count or an ounce weight
        # is in neither, and moving one produced "Grit: 1524mm" -- not a
        # modelled defect class, just a wrong value in a column that has no
        # measurement system to mix. Measured before this: 2 of the 6 Grit
        # values and 1 of the 8 Head Weight values were millimetre strings.
        # This type's OWN lengths. One name is a length in one type and not
        # in another (a sprocket's Pitch, a roller chain's): read from every
        # type's vocabulary, declaring a type would change what another builds.
        length_names = {spec.name for spec in VOCAB[self.type_key] if spec.kind == "length"}
        dimension_indexes = [
            i for i, a in enumerate(out) if a.value_num is not None and a.name in length_names
        ]
        if len(dimension_indexes) >= 2:
            self._bump("eligible_unit_mixing")
            if rng.random() < cfg.scaled_defect(cfg.unit_mixing_within_record):
                index = rng.choice(dimension_indexes)
                other = "mm" if child.system == "in" else "in"
                # The OTHER system, in that system's one canonical spelling.
                # The defect is that this row is in the wrong unit for its
                # record -- not that it is spelled unusually within that unit.
                style = canonical_style(other)
                attribute = out[index]
                assert attribute.value_num is not None
                # The key travels with the unit: a name two types use for two
                # quantities (a sprocket's Pitch, a tap's) is told apart by it,
                # and a restated value under the name's default key would join
                # the other type's facet.
                if attribute.facet_key not in UNIT_SPLIT_KEYS:
                    out[index] = replace(
                        length_attribute(attribute.name, self._publish(attribute.value_num, style)),
                        key=attribute.key,
                    )
                    self._bump("defect_unit_mixing")
        return out

    #: Attributes that identify a SKU rather than describe it, left out of the

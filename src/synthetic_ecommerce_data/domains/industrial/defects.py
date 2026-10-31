"""Defect injection: the unit mixing real catalogs carry.

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

    def _inject_defects(
        self, child: ChildDraft, attrs: list[Attribute], retired: tuple[Attribute, ...] = ()
    ) -> list[Attribute]:
        """Reproduce the measured unit mixing.

        The class is drawn against its own denominator: only a record that
        actually carries two lengths is eligible, which is how the reference
        statistics measure the rate.
        """
        cfg = self.config
        rng = self.rng
        out = list(attrs)

        # A cut longer than its part and a length under an angle key are declined:
        # each is a value the generator knows is wrong, which it does not write
        # (#404, ``measured_loc_exceeds_oal``, ``measured_angle_carries_length_unit``).
        # The draws the cut took still stand (nothing is written), so no other value
        # in the build moves.
        by_name = {a.name: a for a in attrs}
        loc_names = ("Length of Cut", "Flute Length", "Thread Length")
        loc = next((by_name[n] for n in loc_names if n in by_name), None)
        oal = by_name.get("Overall Length") or by_name.get("Length")
        if (
            loc is not None
            and oal is not None
            and rng.random() < cfg.scaled_defect(cfg.measured_loc_exceeds_oal)
            and oal.value_num
            and loc.value_num
        ):
            rng.uniform(1.2, 2.5)

        # Unit mixing inside one record -- one dimension published in the other
        # system: the right length, in the other spelling.
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
        # A retired length (#497) still stands in the pick, so the draw has the
        # range it had and the random stream is stable; it is never restated.
        dimension_indexes += [
            len(out) + i for i, a in enumerate(retired) if a.value_num is not None
        ]
        if len(dimension_indexes) >= 2:
            self._bump("eligible_unit_mixing")
            if rng.random() < cfg.scaled_defect(cfg.unit_mixing_within_record):
                index = rng.choice(dimension_indexes)
                if index >= len(out):
                    return out
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

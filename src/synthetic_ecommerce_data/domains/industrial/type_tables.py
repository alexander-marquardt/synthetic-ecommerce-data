"""The industrial tables a type spec fills, written for core's type registry (#128).

:func:`..core.typespec.register` writes core's own tables (price, noise, voice) and
hands each industrial spec to :func:`register_type`, which the domain registers with
core as its writer: a breadth spec's row goes to :mod:`.breadth`, and a modelled
spec's category, vocabulary, standards family, figure, claims and cross-reference
go to the tables below. Core imports none of them, so a second domain's types fill
its own tables and none of these.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeModuleError, TypeSpec, refuse_redeclared
from synthetic_ecommerce_data.domains.industrial import (
    breadth,
    compat,
    conformance,
    taxonomy,
    vocab,
)
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES
from synthetic_ecommerce_data.domains.industrial.type_labels import declare_label


def register_type(spec: TypeSpec) -> None:
    """Write ``spec`` into the industrial tables, refusing first what they refuse.

    Core has checked the fields every modelled spec declares; the checks here
    are the ones only these tables can make.
    """
    if spec.breadth is not None:
        declare_label(spec)
        breadth.add_row(spec.breadth)
        return
    if isinstance(spec.compat, tuple) and (
        len(spec.compat) != 2 or spec.compat[0] not in compat.KINDS
    ):
        raise TypeModuleError(
            f"type module {spec.module} declares compat={spec.compat!r}; "
            f"a relation is (kind, attribute) with kind one of {sorted(compat.KINDS)}"
        )
    own = {
        "conformance.CLAIMS": (conformance.CLAIMS, spec.claims),
        "compat.RELATIONS": (compat.RELATIONS, spec.compat or None),
        "compat.NEAR_MISS_PERIOD": (compat.NEAR_MISS_PERIOD, spec.near_miss_period),
    }
    refuse_redeclared(spec, own)
    declare_label(spec)
    for table, value in own.values():
        if value is not None:
            table[spec.key] = value
    taxonomy.LEAVES[spec.key] = (spec.category,)
    taxonomy.DRAWING[spec.key] = spec.key
    vocab.VOCAB[spec.key] = spec.vocab
    vocab.STANDARDS_FAMILY[spec.key] = spec.standards_family
    FIGURES[spec.key] = (spec.figure, spec.extent)

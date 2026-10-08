"""The index the PRISM customization serves, and the projection that fills it.

PRISM runs here in DIRECT-INDEX mode: it queries an index this repo creates
and loads, rather than re-ingesting through a PRISM pipeline. That makes the
index mapping part of the customization, and it has to say two things the
generic flat mapping does not.

**Analysed copies of the keyword columns.** ``brand`` and ``series`` are
keywords so they can be faceted and filtered exactly. A full-text query has to
reach them too, and a ``multi_match`` against a keyword field only matches the
whole value verbatim -- a shopper typing one word of a two-word brand gets
nothing. Each grows a ``.text`` sub-field, and the field map points the
searchable entry at the sub-field and the facet entry at the keyword.

**A cumulative category path.** ``emit.flat_documents`` writes
``category_path`` as an ARRAY of segments, which is the right shape for a
keyword filter and the wrong shape for a hierarchy facet. PRISM's
``hierarchy`` type reads ``/``-joined strings and requires the CUMULATIVE
breadcrumb: a product in ``Fasteners/Screws/Socket Head Cap Screws`` must also
carry ``Fasteners`` and ``Fasteners/Screws`` in the same multi-valued field, so
that every ancestor is a real bucket a shopper can click.

Emitting only the leaf is what a first attempt produces, and the engine says
so at boot rather than serving a broken tree::

    category_paths_not_a_forest
      broken_properties = ['cumulative paths']
      missing_ancestors = [{'ancestor': 'Fasteners', 'orphans': [...]}, ...]

It BOOTS anyway, with the tree-shape audit ABSTAINING -- which is the
dangerous outcome, because an abstained audit is not a failed one and the
facet degrades quietly. Expanding the prefixes at load time is a projection,
not a change to the catalog: the segment array ships unchanged beside it.

Nothing here edits ``emit.FLAT_MAPPING``. It is deep-copied and patched, so
the base mapping stays single-sourced in ``emit`` and a change there reaches
this index without being retyped.
"""

from __future__ import annotations

import copy
from collections.abc import Iterable, Iterator
from typing import Any

from ..catalog.emit import FLAT_MAPPING

#: Separator for the joined category path. Must match ``path_separator`` in
#: the field map's ``categories`` entry.
PATH_SEPARATOR = "/"

#: The cumulative-path field the hierarchy facet reads.
CATEGORY_PATH_FIELD = "category_path_joined"


def cumulative_paths(segments: list[str]) -> list[str]:
    """``[A, B, C]`` -> ``[A, A/B, A/B/C]``.

    Every ancestor becomes its own value, which is what makes each level of
    the breadcrumb a clickable bucket and what PRISM's forest audit checks.
    """
    return [PATH_SEPARATOR.join(segments[: i + 1]) for i in range(len(segments))]


def flat_index_body() -> dict[str, Any]:
    """The mapping and settings for the flat catalog index."""
    body = copy.deepcopy(FLAT_MAPPING)
    properties = body["mappings"]["properties"]

    # Analysed copies for full-text reach; the keyword stays the facet source.
    for column in ("brand", "series"):
        properties[column] = {
            "type": "keyword",
            "fields": {"text": {"type": "text"}},
        }

    properties[CATEGORY_PATH_FIELD] = {"type": "keyword"}

    body["settings"] = {
        "number_of_shards": 1,
        # A single-node test cluster cannot allocate a replica, and an index
        # that asks for one sits YELLOW forever. Nothing here needs one.
        "number_of_replicas": 0,
    }
    return body


def project(row: dict[str, Any]) -> dict[str, Any]:
    """Add the fields the field map reads that ``emit`` does not write."""
    projected = dict(row)
    projected[CATEGORY_PATH_FIELD] = cumulative_paths(row["category_path"])
    return projected


def projected_documents(rows: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for row in rows:
        yield project(row)

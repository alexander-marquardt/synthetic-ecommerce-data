"""The duplicate-key-REJECTING YAML loader every engine YAML reader loads through.

Introduced for ``customization.yaml`` (#5182); widened to the rest of the
engine's YAML readers by #5219.

Why this exists
---------------
PyYAML's ``safe_load`` builds a mapping by assigning keys in document order, so
a repeated key silently LAST-WINS and the earlier value is discarded without a
warning::

    policies_indices:
      prism_policies: {policy_id_namespace: en}
      prism_policies: {policy_id_namespace: none}
    -> {'prism_policies': {'policy_id_namespace': 'none'}}

The ``policies_indices:`` block (#5176 phase 1) keys the policy-ID namespace by
the exact policies-index NAME precisely so that "one index, two disagreeing
namespaces" stops being representable rather than merely being caught by a
validator. That guarantee rests entirely on mapping-key uniqueness — which the
parser above does not enforce — so without this loader the guarantee is
aspirational: a duplicated index key would load as a well-formed config whose
namespace was decided by which line came last.

Scope: every YAML reader in the engine (#5219)
----------------------------------------------
#5182 wired this into ONE reader and recorded WHY the rest were left permissive —
blast radius, not immunity. In particular the FIELD MAPS are hand-authored
retailer files carrying exactly the same silent last-wins exposure: a duplicated
canonical-field key drops a mapping without a word, in the artifact a retailer
edits most. #5219 closed that gap after sweeping this repo and both customization
repos for a pre-existing duplicate (none found, so no deployment turned into a
boot refusal). The readers that load through here now:

* ``customization.yaml`` — :func:`prism_engine.config._read_config_file`
  (#5182). ``policies_indices`` and ``personas`` both key by name.
* Field maps — :func:`prism_engine.field_mapping._read_field_map_file`, the
  entry map and every ``$include`` part, plus the plugin-import pre-scan in
  :func:`prism_engine.customization_install._validate_field_map_plugin_imports`.
* Policies dumps, curated vocab, boost config and merchandiser settings —
  :func:`prism_engine.rewrite.io_common.parse_yaml_content`, the one door all
  four share (CLI import, the upload endpoint, and the versioned-config
  adapters).
* The engine's packaged seed markers —
  :mod:`prism_engine.rewrite.markers`.
* ``logging.yaml`` — :mod:`prism_engine.logging_config`.
* User-profile seed files — :mod:`prism_engine.personalization.cli`.

Two readers stay permissive, both outside the engine package and both stating
the reason at the call site: ``scripts/migrate_v4_to_v5.py`` (dead v4-era legacy
that only runs against a config the current engine already refuses) and
``scripts/check_compose_dockerfiles.py`` (a pre-commit hook whose isolated env
carries pyyaml alone — #5241 MEASURED that reaching this loader by installing the
engine costs ~1.6s→~17-20s and 3→43 packages of unrelated deps per cold cache,
and confirmed the duplicate-key gap there is already closed by the ``check-yaml``
hook's ruamel loader, so it stays permissive rather than vendoring a second copy).

The refusal is a hard error, never a warning: a duplicate key means the operator
believes something the file does not say, and every value that follows is
decided by line order.
"""

from __future__ import annotations

from os import PathLike
from typing import IO, Any

import yaml


class DuplicateYamlKeyError(yaml.YAMLError):
    """A YAML mapping declared the same key twice.

    A :class:`yaml.YAMLError` so callers that already funnel parse failures
    through one ``except yaml.YAMLError`` lane keep working unchanged.
    """


class _NoDuplicateKeySafeLoader(yaml.SafeLoader):
    """``SafeLoader`` that refuses a mapping with a repeated key.

    ``prism_source`` carries the caller-supplied filename into the constructor,
    which PyYAML only ever hands the loader instance and the node. Named with a
    project prefix so it cannot collide with a PyYAML attribute.
    """

    #: Human-readable origin of the document, prefixed onto the refusal. ``None``
    #: for an anonymous string (the message then carries positions only).
    prism_source: str | None = None


def _construct_mapping_no_duplicates(
    loader: _NoDuplicateKeySafeLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    """Build a mapping, raising on the SECOND occurrence of any AUTHORED key.

    Mirrors ``SafeConstructor.construct_mapping`` but checks membership before
    assigning, so the error names the key and the line/column of BOTH the
    original declaration and the duplicate — the operator needs to see which two
    lines collided, not just that they did. When the caller passed a ``source``
    the message is prefixed with it, so the operator also sees WHICH file: with
    #5219 the same loader now serves field maps, policies dumps, vocab, boost
    config, markers, logging and user-profile seeds, and "line 12 and line 40" is
    not actionable without the filename.

    Merge keys (``<<: *anchor``) are SUPPORTED, and getting that right is the
    reason this function is longer than a membership check:

    * ``flatten_mapping`` is the first thing the real ``construct_mapping``
      does, and it is what gives ``tag:yaml.org,2002:merge`` a meaning. Omitting
      it does not make merge keys "unsupported" — it makes them a
      ``ConstructorError`` reading "could not determine a constructor for the
      tag", i.e. a document that stock ``safe_load`` merges correctly turns into
      a boot refusal wearing a SYNTAX-error message. Anchors plus merge are the
      natural DRY idiom in a hand-authored field map, so that is a live
      regression, not a theoretical one.
    * But ``flatten_mapping`` SPLICES the anchor's pairs into ``node.value``,
      and a merged key that an authored key then overrides is the whole POINT of
      the idiom — ``{<<: *base, a: 9}`` must yield ``a == 9``. Duplicate-checking
      the flattened list would refuse that, which is a FALSE refusal and strictly
      worse than the silence this module exists to end.

    So the authored key nodes are captured BEFORE flattening and the duplicate
    check runs only over those, by node identity. Authored-vs-authored collides;
    authored-over-merged overrides, exactly as YAML defines.
    """
    # Identity, not equality: two authored `a:` keys construct to the same object
    # but are distinct nodes, and that distinction is precisely what separates
    # "declared twice" from "overrides the anchor".
    authored_key_nodes = {
        id(key_node)
        for key_node, _ in node.value
        if getattr(key_node, "tag", None) != "tag:yaml.org,2002:merge"
    }
    loader.flatten_mapping(node)

    mapping: dict[Any, Any] = {}
    first_seen: dict[Any, yaml.Node] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found unhashable key ({exc})",
                key_node.start_mark,
            ) from exc
        authored = id(key_node) in authored_key_nodes
        if key in mapping and authored and id(first_seen[key]) in authored_key_nodes:
            original = first_seen[key]
            where = f"{loader.prism_source}: " if loader.prism_source else ""
            raise DuplicateYamlKeyError(
                f"{where}duplicate key {key!r} in a YAML mapping: first declared at "
                f"line {original.start_mark.line + 1}, column "
                f"{original.start_mark.column + 1}, and again at line "
                f"{key_node.start_mark.line + 1}, column "
                f"{key_node.start_mark.column + 1}. A repeated key is not an "
                f"override — the parser keeps only the LAST value and discards "
                f"the first silently, so the file does not say what it appears "
                f"to say. Delete one of the two entries."
            )
        first_seen[key] = key_node
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_NoDuplicateKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_no_duplicates,
)


def safe_load_strict(
    stream: str | bytes | IO[str] | IO[bytes],
    *,
    source: str | PathLike[str] | None = None,
) -> Any:
    """``yaml.safe_load`` that REFUSES a duplicate mapping key.

    Raises :class:`DuplicateYamlKeyError` (a :class:`yaml.YAMLError`) naming the
    key and both source positions; otherwise identical to ``yaml.safe_load``.

    Args:
        stream: The YAML text, bytes, or open file object.
        source: Where the document came from — a path, or a description for a
            document with no path (an uploaded file, an index document). Prefixed
            onto the refusal so the operator is told WHICH file to edit. Pass it
            whenever the caller knows; the ONE error format for every reader
            lives here rather than being re-assembled per call site.

    Drives the loader directly rather than through ``yaml.load(..., Loader=…)``
    — same construction ``safe_load`` performs, and it keeps the SAFE-by-
    construction property legible at the call site (the only loader this module
    can ever instantiate is the ``SafeLoader`` subclass above).
    """
    loader = _NoDuplicateKeySafeLoader(stream)
    loader.prism_source = str(source) if source is not None else None
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()

"""The retail tree nests a product type under its generic category (gen#283).

A type that sits BESIDE its generic category hides from it: a hierarchy filter on ``Sofas``
dropped ``Corner Sofas`` (a sibling under ``Home/Furniture``), so a shopper who asked for a red
sofa saw only the plain sofas. A retailer nests the type: ``Home > Furniture > Sofas > Corner
Sofas``, so the generic node includes every sofa and the specific query still narrows to its own
child. Three rules over the built tree keep it that way:

* (a) :func:`sibling_head_noun_findings` -- no node has a sibling whose label is a word-suffix of
  its own (``Sofas`` beside ``Corner Sofas``, ``Skinny Jeans`` beside ``Super Skinny Jeans``).
* (b) :func:`headless_group_findings` -- three or more siblings that share a head noun
  (``Desk Lamps``, ``Floor Lamps``, ``Table Lamps``) sit under a parent that names that noun, or
  carry a declared exception in :data:`EXCEPTIONS` with its reason.
* (c) :func:`misplaced_title_findings` -- a product whose title names a more specific node of its
  own department (``Four Seater Corner Sofa``) sits in that node, not in the generic one.
* (d) :func:`bare_label_findings` (gen#299) -- a label is read right without its breadcrumb: the
  category vocabulary reads a label on its own, so ``Orange`` under ``Juice`` would name the
  fruit and the color. A label that is another node's or a color names the product
  (``Orange Juice``), or carries a declared reason in :data:`LABEL_EXCEPTIONS`.

The functions take plain paths and ``(product id, title, path)`` rows, so the test can feed them a
tree it breaks on purpose (the mutant: ``Corner Sofas`` back beside ``Sofas``).
"""

from __future__ import annotations

import collections
import re
from collections.abc import Iterable, Sequence

Path = tuple[str, ...]

#: Groups of three or more siblings that share a head noun, with no parent that names it, and a
#: reason each is right as it is. Key: (the parent's path, the head noun, singular). Empty: every
#: group the build has is nested. An entry that no longer fires is itself a finding.
EXCEPTIONS: dict[tuple[Path, str], str] = {}

#: A group of this many siblings with one head noun needs a parent of that name.
GROUP_SIZE = 3


def singular(word: str) -> str:
    """A plural folded to its singular, by the same rule for a label and a title."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith(("ses", "xes", "ches", "shes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def words(text: str) -> list[str]:
    """The lowercase singular words of a label or a title (``&`` and punctuation dropped)."""
    found = re.findall(r"[^\W_](?:[^\s&,()/]*[^\W_])?", text.lower().replace("’", "'"))
    return [singular(w) for w in found if w != "s"]


def head_noun(label: str) -> str:
    """The last word of a label, singular: ``Corner Sofas`` -> ``sofa``."""
    return words(label)[-1]


def nodes(paths: Iterable[Sequence[str]]) -> set[Path]:
    """Every node the paths pass through, a path and each of its prefixes."""
    found: set[Path] = set()
    for path in paths:
        for depth in range(1, len(path) + 1):
            found.add(tuple(path[:depth]))
    return found


def children(tree: set[Path]) -> dict[Path, list[Path]]:
    by_parent: dict[Path, list[Path]] = collections.defaultdict(list)
    for node in sorted(tree):
        by_parent[node[:-1]].append(node)
    return by_parent


def is_specific_of(label: str, generic: str) -> bool:
    """``label`` is a more specific form of ``generic``: its words end in the generic's words and
    it has more of them (``Corner Sofas`` of ``Sofas``, ``Super Skinny Jeans`` of ``Skinny Jeans``).
    """
    specific, plain = words(label), words(generic)
    return bool(plain) and len(specific) > len(plain) and specific[-len(plain) :] == plain


def sibling_head_noun_findings(paths: Iterable[Sequence[str]]) -> list[str]:
    """Rule (a): ``parent: 'Sofas' sits beside 'Corner Sofas'`` for each such pair.

    A node whose label is a word-suffix of a sibling's label is that sibling's generic parent,
    whether it is one word (``Sofas``) or several (``Skinny Jeans`` for ``Super Skinny Jeans``).
    """
    found = []
    for parent, kids in children(nodes(paths)).items():
        for kid in kids:
            for other in kids:
                if other != kid and is_specific_of(kid[-1], other[-1]):
                    where = " > ".join(parent) or "(root)"
                    found.append(f"{where}: {other[-1]!r} sits beside {kid[-1]!r}")
    return sorted(found)


def nested_pairs(paths: Iterable[Sequence[str]]) -> list[tuple[Path, Path]]:
    """Every (generic node, specific child) pair: the child's label ends in the parent's words."""
    pairs = [
        (parent, kid)
        for parent, kids in children(nodes(paths)).items()
        if parent
        for kid in kids
        if is_specific_of(kid[-1], parent[-1])
    ]
    return sorted(pairs)


def headless_group_findings(
    paths: Iterable[Sequence[str]],
    exceptions: dict[tuple[Path, str], str] | None = None,
) -> list[str]:
    """Rule (b): a group of three or more siblings with one head noun and no parent naming it."""
    declared = EXCEPTIONS if exceptions is None else exceptions
    found = []
    for parent, kids in children(nodes(paths)).items():
        groups: dict[str, list[str]] = collections.defaultdict(list)
        for kid in kids:
            noun = head_noun(kid[-1])
            if words(kid[-1]) != [noun]:  # a bare ``Sofas`` is the parent, not a member
                groups[noun].append(kid[-1])
        for noun, labels in sorted(groups.items()):
            named = bool(parent) and noun in words(parent[-1])
            if len(labels) >= GROUP_SIZE and not named and (parent, noun) not in declared:
                where = " > ".join(parent) or "(root)"
                found.append(f"{where}: {sorted(labels)} share the head noun {noun!r}, no parent")
    return sorted(found)


def stale_exception_findings(
    paths: Iterable[Sequence[str]], exceptions: dict[tuple[Path, str], str]
) -> list[str]:
    """A declared exception that has no reason, or whose group is now nested or gone."""
    undeclared = headless_group_findings(paths, exceptions={})
    found = []
    for (parent, noun), reason in sorted(exceptions.items()):
        where = " > ".join(parent)
        if not reason.strip():
            found.append(f"{where}: exception for {noun!r} has no reason")
        if not any(line.startswith(f"{where}: ") and f"{noun!r}" in line for line in undeclared):
            found.append(f"{where}: exception for {noun!r} no longer applies")
    return found


def misplaced_title_findings(
    rows: Iterable[tuple[str, str, Sequence[str]]],
) -> list[str]:
    """Rule (c): ``(product id, title, path)`` rows whose title names a more specific node.

    A node is *more specific* than the product's own when its label ends in the product's node
    label and has more words (``Corner Sofas`` for ``Sofas``). Only nodes under the same
    top-level department count: ``Girls' Barrel Jeans`` in Kids is not a Women's barrel jean.
    """
    rows = list(rows)
    tree = nodes(path for _, _, path in rows)
    label_words = {node: words(node[-1]) for node in tree}
    by_root: dict[str, list[Path]] = collections.defaultdict(list)
    for node in tree:
        by_root[node[0]].append(node)
    found = set()
    for product_id, title, path in rows:
        own = tuple(path)
        own_words = label_words[own]
        title_words = words(title)
        for node in by_root[own[0]]:
            named = label_words[node]
            if len(named) <= len(own_words) or named[-len(own_words) :] != own_words:
                continue
            span = len(named)
            if any(title_words[i : i + span] == named for i in range(len(title_words) - span + 1)):
                found.add(
                    f"{product_id} {title!r} sits in {' > '.join(own)}, names {' > '.join(node)}"
                )
    return sorted(found)


#: Labels rule (d) would refuse that still name what they hold, each with its reason. Key: the
#: node's path as shipped (sentence case). An entry that no longer fires is itself a finding.
LABEL_EXCEPTIONS: dict[Path, str] = {
    ("Garden", "Plants", "Lavender"): "a lavender plant is a lavender: gen#509 made the node so "
    "that a shopper's 'lavender' has a plant to route to",
}


def named_nodes(paths: Iterable[Sequence[str]], query: str) -> set[Path]:
    """The nodes a query names when a label is read on its own: the same words, plural folded."""
    want = words(query)
    return {node for node in nodes(paths) if words(node[-1]) == want}


def _reads(title: list[str], phrase: list[str]) -> bool:
    span = len(phrase)
    return any(title[i : i + span] == phrase for i in range(len(title) - span + 1))


def bare_label_findings(
    rows: Iterable[tuple[str, str, str, Sequence[str]]],
    colors: Iterable[str],
    exceptions: dict[Path, str] | None = None,
) -> list[str]:
    """Rule (d), gen#299: a label that needs its breadcrumb to be read right.

    ``rows`` are ``(product id, title, product type, path)``. A node's label *collides* when,
    after the plural rule, it is another node's label (``Orange`` and the fruit's ``Oranges``) or
    a color value. A colliding label is a finding when it does not name the product: its titles
    read it before its parent's noun (``Orange`` under ``Juice`` holds "Smooth Orange Juice"), so
    the product is the two words and the label alone is the other sense. ``Orange Juice`` names
    the product, and so do ``Oranges`` and ``Accessories``, whose titles never read "orange
    fruit" or "accessory accessory".
    """
    declared = LABEL_EXCEPTIONS if exceptions is None else exceptions
    held: dict[Path, list[list[str]]] = collections.defaultdict(list)
    for _, title, _, path in rows:
        said = words(title)
        for depth in range(1, len(path) + 1):
            held[tuple(path[:depth])].append(said)
    by_label: dict[tuple[str, ...], list[Path]] = collections.defaultdict(list)
    for node in held:
        by_label[tuple(words(node[-1]))].append(node)
    color_labels = {tuple(words(c)) for c in colors}
    found = []
    for node in sorted(held):
        label = words(node[-1])
        others = [" > ".join(o) for o in sorted(by_label[tuple(label)]) if o != node]
        if len(node) < 2 or node in declared or not (others or tuple(label) in color_labels):
            continue
        product = [*label, head_noun(node[-2])]
        if any(_reads(title, product) for title in held[node]):
            clash = f"is also {others[0]!r}" if others else "is a color"
            found.append(f"{' > '.join(node)}: {node[-1]!r} {clash}, and its titles read "
                         f"{' '.join(product)!r}: name the product")  # fmt: skip
    return found

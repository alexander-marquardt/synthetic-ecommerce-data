#!/usr/bin/env python3
"""A docs page's index entry as a comment on its first line (#16477, step 1 of #16006).

A page carries its docs index entry in the page itself, as an invisible comment on
its first line; it is the index's one source (#16479)::

    <!-- docs-index: section=si/orient order=200 summary="the short entry point ..." -->

``section``
    The list the page sits in: ``<audience>`` or ``<audience>/<group>`` for a
    chapter, ``<audience>/appendix`` or ``<audience>/reference`` for the others.
``order``
    Its place in that list, smallest first: a whole number.
``summary``
    Optional, quoted: the text after the ``—``. ``\\"`` is a quote, ``\\\\`` a backslash.
``title``
    Optional, quoted: the link text, when it is not the page's ``# `` heading.
``borrowed_into``
    Optional, chapters only: the other audiences whose path lists it, comma-separated
    (``borrowed_into=si`` or ``borrowed_into=si,internals``).

The fields are the design of #15875 and #16006. ``scripts/render_docs_index.py``
reads them and renders the index. This module only reads and writes the comment
line; the render checks what the fields name. Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PREFIX = "<!-- docs-index: "
SUFFIX = " -->"
_COMMENT = re.compile(r"^<!-- docs-index: (?P<body>.*) -->$")
_FIELD = re.compile(
    r'(?P<key>[a-z_]+)=(?:"(?P<quoted>(?:[^"\\]|\\.)*)"|(?P<bare>[^\s"]+))(?:\s+|$)'
)
_REQUIRED = ("section", "order")
FIELDS = frozenset({"section", "order", "summary", "title", "borrowed_into"})
_ORDER = re.compile(r"-?[0-9]+")
_FENCE = re.compile(r"^\s*(```|~~~)")


class CommentError(ValueError):
    """A docs-index comment that cannot be read, or a value it cannot hold."""


@dataclass(frozen=True)
class Comment:
    """A comment's fields; ``title`` is ``""`` when the page's heading is the title."""

    section: str
    order: int
    summary: str = ""
    title: str = ""
    borrowed_into: tuple[str, ...] = ()


def _quote(value: str) -> str:
    if "\n" in value or "-->" in value:
        raise CommentError(f"{value!r}: a comment value is one line holding no `-->`")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def format_comment(comment: Comment) -> str:
    """The first line a page carries for ``comment``, its fields in a fixed order."""
    parts = [f"section={comment.section}", f"order={comment.order}"]
    if comment.title:
        parts.append(f"title={_quote(comment.title)}")
    if comment.summary:
        parts.append(f"summary={_quote(comment.summary)}")
    if comment.borrowed_into:
        parts.append("borrowed_into=" + ",".join(comment.borrowed_into))
    return PREFIX + " ".join(parts) + SUFFIX


def _fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    pos = 0
    while pos < len(body):
        field = _FIELD.match(body, pos)
        if field is None:
            raise CommentError(
                f"cannot read its docs-index comment from {body[pos : pos + 30]!r}: "
                'a field is key=value or key="quoted value"'
            )
        key = field["key"]
        if key in fields:
            raise CommentError(f"its docs-index comment gives `{key}` twice")
        quoted = field["quoted"]
        fields[key] = (
            re.sub(r"\\(.)", r"\1", quoted) if quoted is not None else field["bare"]
        )
        pos = field.end()
    return fields


def read(text: str) -> Comment | None:
    """The comment on ``text``'s first line; ``None`` when that line is not one."""
    match = _COMMENT.match(text.split("\n", 1)[0].rstrip("\r"))
    if match is None:
        return None
    fields = _fields(match["body"])
    unknown = sorted(set(fields) - FIELDS)
    missing = [k for k in _REQUIRED if k not in fields]
    if unknown or missing:
        raise CommentError(
            f"its docs-index comment has unknown field(s) {unknown} or lacks "
            f"{missing}; the fields are {sorted(FIELDS)}"
        )
    if not _ORDER.fullmatch(fields["order"]):
        raise CommentError(f"order={fields['order']} is not a whole number")
    borrowed = tuple(b for b in fields.get("borrowed_into", "").split(",") if b)
    return Comment(
        section=fields["section"],
        order=int(fields["order"]),
        summary=fields.get("summary", ""),
        title=fields.get("title", ""),
        borrowed_into=borrowed,
    )


def carries(text: str) -> bool:
    """Whether ``text``'s first line is a docs-index comment, readable or not."""
    return _COMMENT.match(text.split("\n", 1)[0].rstrip("\r")) is not None


def prose(text: str) -> str:
    """``text`` with a first-line docs-index comment emptied: the page a prose scan reads.

    The comment is the page's index entry, not its prose, so a test that holds the
    page's routes or code-font names to the code reads past it (#16478). The line
    stays, empty, so a line number the scan reports is still the file's.
    """
    if not carries(text):
        return text
    return text[len(text.split("\n", 1)[0]) :]


def heading_title(text: str) -> str:
    """The page's first ``# `` heading outside a fence, or ``""``."""
    fenced = False
    for line in text.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
        elif not fenced and line.startswith("# "):
            return line[2:].strip()
    return ""

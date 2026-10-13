#!/usr/bin/env python3
"""One tree for the enumeration and for the read (#8040).

``git ls-files`` answers out of the **INDEX**. ``Path.read_text()`` answers out of
the **DISK**. Those are two different trees, and a path in one but not the other is
an ORDINARY working-tree state — an unstaged ``rm``, a ``git rm --cached``, a
tracked directory replaced by a file, a file whose parent directory is not
readable. Every gate in this repository that enumerates its subject from the first
and reads its bytes from the second has to say what it does about that gap, and
this module is the one place that says it.

## Why this is a module and not a rule written four times

The same defect was found and fixed independently in ``#7961``
(``tests/test_rewrite/test_sphinx_role_targets_4867.py``), in ``#7980``/``#8036``
(``scripts/check_cross_document_fragments.py``, which alone had two reachable
sites — fixing the first only moved the crash to the second), and the reviews of
``#8036`` then found the same class three more times inside its own remediation:
at the read handler, one level up in the ``is_file()`` filter the fix introduced,
and finally in the test layer, where a binding was asserted at one consumer of the
filter and not at its sibling. A rule applied at the site you are looking at,
rather than at every site that decides the same thing, is not a rule — so the
predicate lives here, ``tests/test_index_disk_enumeration_split_8040.py`` fails any
new site that hand-rolls it, and the prose has one home to be wrong in.

## The three failure modes, in descending order of how quietly they fail

1. **A silent total pass.** A broad ``except OSError: continue`` at the read
   reports a clean tree it never read. Measured on ``#8036``'s intermediate head:
   ``chmod 000`` on one page with a planted dead pointer took the run from ``rc=1``
   naming the anchor to **``rc=0`` with no output at all**, dropping 23 pointers
   and one real finding. Nothing vanished and no race occurred.
2. **A silent drop at the enumeration.** ``Path.is_file()`` and ``Path.exists()``
   answer a BOOLEAN, so for the errnos they absorb, "cannot be reached" and "is not
   there" come back as the same answer with nobody told. ``.exists()`` is therefore
   not a guard. Which errnos those are is INTERPRETER-DEPENDENT — see
   :func:`in_this_checkout`, which has the measurement — and on the older of the two
   versions this repository supports the same line fails as mode 3 instead.
3. **A crash with no verdict.** Where nothing absorbs it, the read raises and the
   contributor gets a traceback in place of a PASS/FAIL line and a remedy. For a
   module that enumerates at IMPORT time this is a collection abort:
   ``tests/test_rewrite/test_markdown_construct_citations_7876.py``'s 313
   assertions stop existing rather than one going red.

Mode 1 is strictly worse than mode 3, which is why the remedy is never "widen the
``except OSError``".
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

__all__ = [
    "git_binary",
    "in_this_checkout",
    "ls_files",
    "read_bytes_if_present",
    "read_if_present",
    "working_tree_files",
]

#: Absolute path, resolved once — a bare ``argv[0]`` is resolved through ``PATH`` at
#: exec time (bandit S607).
_GIT_BINARY = shutil.which("git")


def git_binary() -> str:
    """The git binary, or a loud failure.

    Deliberately NOT a skip and NOT a warning-and-continue. A caller of this module
    enumerates its subject through git, so without git it can report nothing — and a
    gate that passes when it could not run is the vacuous pass the whole gate family
    exists to prevent (#3485/#4654).
    """
    if _GIT_BINARY is None:
        raise RuntimeError(
            "git is not on PATH, so the subject of this gate cannot be enumerated. "
            "It refuses to report green rather than passing vacuously over an empty "
            "subject — install git to run it."
        )
    return _GIT_BINARY


def ls_files(*pathspecs: str, root: Path) -> list[str]:
    """Repo-relative paths matching *pathspecs* in *root*'s INDEX.

    The raw index answer, ``-z`` so a name carrying a special character arrives
    verbatim rather than C-quoted. Callers that go on to READ these paths want
    :func:`working_tree_files` instead; this is exported for the callers that
    compare the index against something else and never open a byte.
    """
    out = subprocess.run(  # noqa: S603  # fixed non-shell argv of trusted literals (the resolved git path, the caller's root and its own pathspec constants)
        [git_binary(), "-C", str(root), "ls-files", "-z", *pathspecs],
        capture_output=True,
        # ``surrogateescape`` rather than the default strict decode: a tracked name
        # carrying bytes that are not valid UTF-8 is a name this repository can hold,
        # and a decode error here would report the whole subject as underivable
        # instead of that one path. It round-trips back to the same bytes when the
        # path is opened.
        encoding="utf-8",
        errors="surrogateescape",
        check=True,
    )
    return [entry for entry in out.stdout.split("\0") if entry]


def in_this_checkout(path: str | Path, *, root: Path) -> bool:
    """Is *path* a thing this checkout HAS? ENOENT says no; nothing else does.

    The admission half of the errno rule, spelled out here rather than delegated to
    ``Path.is_file()``. That call answers the wrong question, and — this is the part
    #8040's own issue text got wrong and the correction is load-bearing — it answers
    it DIFFERENTLY depending on the interpreter. Probed directly, one directory
    holding one instance of each divergence:

    ==========================  ==========================  ==========  ==========
    path                        ``stat()``                  3.12.10     3.14.2
    ==========================  ==========================  ==========  ==========
    absent / dangling symlink   ``FileNotFoundError`` (2)   ``False``   ``False``
    under a dir replaced by a
    file                        ``NotADirectoryError``(20)  ``False``   ``False``
    self-referential symlink    ``OSError`` ELOOP (62)      ``False``   ``False``
    under an unreadable dir     ``PermissionError`` (13)    **RAISES**  ``False``
    ==========================  ==========================  ==========  ==========

    The last row is the one nobody expects. CPython 3.12's ``pathlib`` absorbs only
    ``_IGNORED_ERRNOS = (ENOENT, ENOTDIR, EBADF, ELOOP)`` and PROPAGATES everything
    else; 3.14 dropped that set and returns ``False`` for every ``OSError``. This
    repository declares ``requires-python = ">=3.12"``, so BOTH are supported and
    the identical ``is_file()`` line is a silent drop (mode 2) on one and an uncaught
    ``PermissionError`` at the enumeration (mode 3) on the other.

    What was measured, and where the line between measurement and inference falls:
    the table above is a direct probe on both interpreters, and the END-TO-END run
    was made on 3.12 only — ``chmod 000`` on a tracked directory took the pre-fix
    ``check_derived_set_floors.py --census`` from 240 rows to a bare
    ``PermissionError`` traceback out of ``Path.is_file()``, with no verdict. The
    3.14 end-to-end run is INFERRED from the table's last row rather than executed,
    and is stated as such. The rows that are the same on both versions — ENOTDIR and
    ELOOP — are what every fail-before measurement for this change was built on, so
    no piece of the evidence rests on the version-dependent errno.

    So the claim to make about ``is_file()`` is not "it swallows every ``OSError``" —
    that is false on 3.12 — but the weaker one that is true of both: **it cannot
    report anything**. It returns a boolean, and whichever way a given interpreter
    resolves a given errno, the caller is never told which of the two questions it
    answered. This function answers only the question it was asked.

    Keeping the last three rows is the point. Something is at, or in the way of,
    that path, so it stays in the subject and the reader opens it, fails, and reports
    the errno. Dropping them is the silence above.

    Do NOT narrow the keep-set. ENOTDIR(20) and ENAMETOOLONG(63) are reachable as
    ordinary unstaged divergences; adding either to the drop set re-opens this class
    for real states.

    ``stat()`` follows symlinks, so a DANGLING link raises ENOENT and is excluded
    here, which is what lets a caller's read handler drop ``FileNotFoundError``
    honestly rather than by luck: once this function has admitted a path, ENOENT at
    the read cannot mean "the link was always broken" — every non-ENOENT reason to
    fail has been admitted rather than dropped — so it can only mean the path went
    away in between.
    """
    try:
        (root / path).stat()
    except FileNotFoundError:
        return False
    except OSError:
        # PRESENT and unstattable. Admitted deliberately, so the reader reports it
        # with its errno instead of this line deciding, silently, that a path the
        # tree still holds is one nobody needs to hear about.
        return True
    return True


def read_if_present(
    path: str | Path,
    *,
    root: Path | None = None,
    encoding: str = "utf-8",
    errors: str = "strict",
) -> str | None:
    """The text at *path*, or ``None`` if the path was NOT THERE when it was read.

    The READ half of this module's rule, and the half that had no home until #9378.
    :func:`in_this_checkout` decides what enters a subject; this decides what a
    reader does when a member of that subject turns out not to be there any more.
    Callers that hold a repo-relative path pass *root*; callers that already hold an
    absolute one (an ``rglob`` walk) pass the path alone.

    ## What ``None`` means, and why it is honest rather than lucky

    ENOENT, and ONLY ENOENT, becomes ``None``. Every other ``OSError`` is raised, so
    a caller keeps whatever loud answer it already gives an unreadable file.

    An enumeration of a working tree is a SNAPSHOT of a directory that is still
    live. Between the listing and the read a developer can save over a file, an
    editor can replace it by rename, a ``git switch`` can remove it, and — the way
    #9378 reached this repository — a concurrently running test module can plant a
    probe file and delete it again. A path that is gone by the time it is opened is
    an ORDINARY working-tree state, not a defect in the reader, and a traceback in
    place of a verdict is the wrong answer to it.

    ``None`` is not "nothing to see here": it is the reader being told which of the
    two questions was answered, which is the thing ``Path.exists()`` and
    ``Path.is_file()`` cannot do (see :func:`in_this_checkout`). A caller that needs
    to ACT on the drop — count it, name it, refuse on it — can, because it is
    returned rather than swallowed.

    ## What a dropped file does to a verdict — decide this per caller

    Sound for a CONTENT sweep, which is what every caller in this repository is: the
    question is "does any file in the tree say X", and a file the tree no longer
    holds says nothing. The count it feeds is a count of what the tree contains, and
    a vanished file is not contained.

    NOT sound for a gate whose verdict is that a path EXISTS or that a subject has a
    given SIZE. Two properties keep those separate rather than luck: a floor over the
    enumeration is evaluated before any read, so a read-side drop cannot move it
    (``check_cross_document_fragments.py``'s ``MIN_PAGES`` is the worked example);
    and a gate comparing two enumerations never reaches this function at all,
    because it opens no bytes. A gate that wants to assert presence asserts it —
    with :func:`in_this_checkout`, which answers exactly that question — and does not
    infer it from a read that happened to succeed.

    ## Why it is not ``except OSError``

    Widening the drop is failure mode 1 of #8040 and is strictly worse than the
    crash it replaces: measured on that issue's intermediate head, ``chmod 000`` on
    one page took a run from ``rc=1`` naming a real finding to **``rc=0`` with no
    output at all**. EACCES, ELOOP, EIO, EISDIR and ENOTDIR all reach a reader
    DETERMINISTICALLY, with nothing vanished and no race, and they share no remedy
    with each other or with this one. They are raised.

    ``stat()`` follows symlinks, so a DANGLING link is already excluded by
    :func:`in_this_checkout` rather than arriving here — which is what makes the drop
    honest for a caller that enumerated through :func:`working_tree_files`: every
    non-ENOENT reason to fail was admitted rather than filtered out upstream, so
    ENOENT here can only mean the path went away in between. A caller that
    enumerated with a bare ``rglob`` has no such upstream, and for it ENOENT covers
    one further case — a dangling symlink the walk yielded. That file has no bytes
    to scan either, so the answer is the same; it is named here so the difference
    between the two callers is written down rather than assumed away.
    """
    target = Path(path) if root is None else root / path
    try:
        return target.read_text(encoding=encoding, errors=errors)
    except FileNotFoundError:
        return None


def read_bytes_if_present(
    path: str | Path, *, root: Path | None = None
) -> bytes | None:
    """The bytes at *path*, or ``None`` if it was NOT THERE when it was read.

    :func:`read_if_present` for a caller that decides something about the raw bytes —
    a binary sniff, a hash — before any decoding. Identical contract: ENOENT and only
    ENOENT becomes ``None``, every other ``OSError`` is raised, and the reasoning for
    both halves is on :func:`read_if_present` rather than repeated here.
    """
    target = Path(path) if root is None else root / path
    try:
        return target.read_bytes()
    except FileNotFoundError:
        return None


def working_tree_files(*pathspecs: str, root: Path) -> list[str]:
    """Repo-relative paths matching *pathspecs* that this checkout ACTUALLY HOLDS.

    ONE tree for the enumeration, for the reading and for the resolution. This is
    the call a gate wants whenever the paths it enumerates are the paths it will
    open: it removes failure mode 2 outright (the drop is ENOENT and only ENOENT,
    and an ENOENT drop is honest — a path the checkout does not hold carries no
    bytes to judge) and it removes the ORDINARY half of failure mode 3, leaving the
    read to raise only on a path something is genuinely wrong with.

    UNTRACKED files are deliberately NOT unioned in. Whether they belong depends on
    which side of the gate they land on — in ``#7961`` they widen the set of
    DEFINITIONS a role may resolve against, so including them removes false reds,
    while in ``#7980`` they would widen the SUBJECT, which ADDS findings on a
    scratch note the author never intends to commit. A caller that wants them says
    so in its own words, with its own measurement, by calling :func:`ls_files` with
    ``--others --exclude-standard`` and unioning explicitly.
    """
    return [
        path
        for path in ls_files(*pathspecs, root=root)
        if in_this_checkout(path, root=root)
    ]

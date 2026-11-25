"""``scale.templates()`` computed once per worker, a fresh copy for each caller (#1035).

A call takes 7 to 8 s and 139 test files make 200 of them, 40% of the retail tests' time.
``tests/conftest.py`` installs this over ``scale.templates`` in a test process: the first call
computes, and each call unpickles a list of its own (0.15 s), so no caller sees another's edit.
While a ``MonkeyPatch`` holds an edit, the call computes and nothing is kept: a test that
changes what the templates are made of reads what it made.
``tests/test_templates_memo_1035.py`` holds the copy to a computation in another process, so a
test that compares two calls to prove determinism loses nothing.
"""

from __future__ import annotations

import functools
import pickle
import sys

import pytest

_SCALE = "synthetic_ecommerce_data.domains.retail.scale"
_EDITS = ("setattr", "delattr", "setitem", "delitem")

#: The ``MonkeyPatch`` objects that hold an edit not undone yet.
_live: set[pytest.MonkeyPatch] = set()


def patched() -> bool:
    return bool(_live)


def watch() -> None:
    """Note each ``MonkeyPatch`` edit until its undo (``setenv`` is a ``setitem``)."""
    if hasattr(pytest.MonkeyPatch.undo, "__wrapped__"):
        return
    for name in _EDITS:
        setattr(pytest.MonkeyPatch, name, _noted(getattr(pytest.MonkeyPatch, name)))
    undo = pytest.MonkeyPatch.undo

    @functools.wraps(undo)
    def undone(self):
        try:
            return undo(self)
        finally:
            _live.discard(self)

    pytest.MonkeyPatch.undo = undone


def _noted(edit):
    @functools.wraps(edit)
    def noted(self, *args, **kwargs):
        # pytest's own tmp_path plugins hold an edit of the Config for the whole session.
        if not (args and isinstance(args[0], pytest.Config)):
            _live.add(self)
        return edit(self, *args, **kwargs)

    return noted


def memo(real):
    """``real`` kept per ``baseline``; ``__wrapped__`` is the function itself."""
    kept: dict[bool, bytes] = {}

    @functools.wraps(real)
    def templates(baseline: bool = True) -> list[dict]:
        if patched():
            return real(baseline)
        if baseline not in kept:
            kept[baseline] = pickle.dumps(real(baseline), pickle.HIGHEST_PROTOCOL)
        return pickle.loads(kept[baseline])

    templates.is_memo = True
    return templates


def install() -> None:
    """Put the memo over ``scale.templates`` once ``scale`` is imported and nothing is patched."""
    scale = sys.modules.get(_SCALE)
    if scale is None or patched() or getattr(scale.templates, "is_memo", False):
        return
    scale.templates = memo(scale.templates)

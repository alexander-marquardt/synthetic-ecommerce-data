"""The mutation bed itself: every planted defect still plants.

``scripts/mutation_check.py`` reports a mutation whose anchor text is no
longer in the file as ``MUTATION DID NOT APPLY``, which is honest -- but only
if somebody reads the report. Five of its mutations are planted in
``golden-catalog/`` and quote a document VERBATIM, so **every regeneration of
the golden data breaks all five at once**, silently, and the next person to
run the bed gets five entries that prove nothing about the tests they name.
That is exactly what happened when this catalog was last regenerated, and it
was found by hand rather than by anything here.

So the bed is checked like any other artifact: each anchor has to occur
exactly once in the file it is planted in, and each mutation has to actually
change something. This does not run the mutations -- it says they are still
plantable, which is the property that rots.
"""

from __future__ import annotations

import importlib.util
import shlex
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _mutations():
    """Load the harness by path: ``scripts/`` is not an importable package."""
    spec = importlib.util.spec_from_file_location(
        "mutation_check", REPO / "scripts" / "mutation_check.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # The harness defines a dataclass, and ``@dataclass`` resolves its own
    # annotations through ``sys.modules[cls.__module__]`` -- so the module has
    # to be registered there BEFORE it is executed, or the decorator raises.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return list(module.MUTATIONS)


MUTATIONS = _mutations()


def test_the_bed_is_not_empty() -> None:
    assert len(MUTATIONS) > 100


@pytest.mark.parametrize("mutation", MUTATIONS, ids=lambda m: m.name)
def test_every_mutation_still_plants(mutation) -> None:
    path = REPO / mutation.root / mutation.file
    assert path.exists(), f"{mutation.name}: {path} does not exist"
    occurrences = path.read_text(encoding="utf-8").count(mutation.old)
    assert occurrences == 1, (
        f"{mutation.name}: its anchor occurs {occurrences} time(s) in "
        f"{mutation.root}/{mutation.file}, so the harness reports "
        f"{'MUTATION DID NOT APPLY' if not occurrences else 'MUTATION TEXT IS AMBIGUOUS'} "
        f"instead of testing anything. Re-anchor it against the file as it "
        f"now reads."
    )


@pytest.mark.parametrize("mutation", MUTATIONS, ids=lambda m: m.name)
def test_every_mutation_changes_something(mutation) -> None:
    assert mutation.new != mutation.old, f"{mutation.name} plants the text it replaces"


@pytest.mark.parametrize("mutation", MUTATIONS, ids=lambda m: m.name)
def test_every_mutation_names_a_test_file_that_exists(mutation) -> None:
    """The selector's first token, which is always the file under pytest."""
    target = shlex.split(mutation.tests)[0].split("::")[0]
    assert (REPO / target).exists(), f"{mutation.name} names {target}, which does not exist"

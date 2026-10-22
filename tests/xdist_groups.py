"""Which xdist group a test module's tests run in (#348).

``scripts/merge_pr.sh --local-ci`` runs the suite with ``-n auto --dist loadgroup``.
Left alone, xdist scatters one module's tests over every worker, and each worker then
rebuilds the module's fixtures: a 100K catalog is 45 to 60 s, and the suite has 137
module-scoped fixtures. Measured on the 48-core agent VM (load average 20 to 33 from other
agents), the whole suite grouped by module took 637 s and 729 s on 12 workers; a worker
ends at up to 4.3 GB because it keeps what each module it ran built. Those figures were taken
before #442: the group mark was added after xdist read the markers, so no module was grouped
(``tests/test_xdist_group_honoured_442.py`` checks it through a real ``--dist loadgroup`` run).

A module whose tests build their own world (no shared fixture, minutes in total) sets
``XDIST_SPREAD = True`` so its tests spread over the workers: ``tests/test_merge_pr.py``
is 1,000+ s of independent tests, which on one worker would be the whole run.
"""

from __future__ import annotations


def group_for(module: object) -> str | None:
    """The group a module's tests share, or None for a module that asks to be spread."""
    if getattr(module, "XDIST_SPREAD", False):
        return None
    return str(module.__name__)  # type: ignore[attr-defined]

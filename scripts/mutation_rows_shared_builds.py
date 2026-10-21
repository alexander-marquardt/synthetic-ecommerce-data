"""Mutation rows for the shared 100K builds (gen#140), kept out of ``mutation_check.py``.

Each row plants one defect in ``tests/shared_builds.py`` (or in what the guards read) and
names the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows
named ``shared builds: ...`` (``--only "shared builds:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``; ``root`` is the directory ``file`` hangs
off, relative to the repository.
"""

from __future__ import annotations

from mutation_row import Row

GUARD = "tests/test_shared_builds_140.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the build lock is not taken",
        "shared_builds.py",
        "        fcntl.flock(handle, fcntl.LOCK_EX)",
        "        pass",
        f"{GUARD} -k test_two_processes_asking_at_once_build_once",
        "two workers that both miss the file build it one after the other, never together",
        "tests",
    ),
    (
        "a process that waited for the lock builds anyway",
        "shared_builds.py",
        "    with _one_build_at_a_time(directory):\n        found = _read(path)",
        "    with _one_build_at_a_time(directory):\n        found = None",
        f"{GUARD} -k test_two_processes_asking_at_once_build_once",
        "a process that waited for the lock reads what the first one wrote",
        "tests",
    ),
    (
        "the file is never read",
        "shared_builds.py",
        "            return pickle.load(handle)",
        "            return None",
        f"{GUARD} -k test_a_second_ask_for_unchanged_inputs_reads_the_file",
        "an unchanged source reads the file instead of building again",
        "tests",
    ),
    (
        "the name ignores the generator's source",
        "shared_builds.py",
        "inputs_digest(roots) + _code_of(build)",
        "_code_of(build)",
        f"{GUARD} -k test_a_changed_source_is_never_served_the_old_file",
        "a changed source is never served the old file",
        "tests",
    ),
    (
        "the price tests build the catalog in the worker",
        "shared_builds.py",
        '    return cached("hundred_k_prices", _hundred_k_prices_build)',
        "    return _hundred_k_prices_build()",
        f"{GUARD} -k test_a_worker_that_reads_the_shared_100k_file_holds_under_500_mb",
        "a worker that reads the shared 100K file holds under 500 MB",
        "tests",
    ),
    (
        "a module names the 100K size and builds its own",
        "test_price.py",
        "CENSUS_FILE = (",
        "LARGE_BUILD_LINES = 39000\nCENSUS_FILE = (",
        f"{GUARD} -k test_no_test_module_builds_a_whole_100k_catalog_of_its_own",
        "no test module builds a whole 100K catalog of its own",
        "tests",
    ),
    (
        "the default dist mode scatters a module over the workers",
        "pyproject.toml",
        'addopts = "--dist loadgroup"',
        'addopts = ""',
        f"{GUARD} -k test_the_default_dist_mode_keeps_a_module_on_one_worker",
        "a plain -n 2 keeps a module on one worker",
        ".",
    ),
    (
        "the cache directory made first is left without a .gitignore",
        "shared_builds.py",
        "        if not ignore.exists():",
        "        if False:",
        f"{GUARD} -k test_a_cache_directory_made_before_pytests_own_is_still_ignored_by_git",
        "a cache directory made before pytest's own is still ignored by git",
        "tests",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "shared builds"


def rows() -> list[Row]:
    return [Row(n, f, o, w, t, p, root) for n, f, o, w, t, p, root in ROWS]

"""A change to an industrial type module selects no test file that reads no type table (#1035).

``scripts/ci_type_free.json`` lists the files a run saw read none. ``scripts/ci_select.py`` does
not follow a listed file through the imports that run only when a table is read, and
``tests/type_reads.py`` fails a listed file that reads one.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ci_select = _load("ci_select")
ci_type_free = _load("ci_type_free")

TYPE_MODULE = "src/synthetic_ecommerce_data/domains/industrial/product_types/fasteners/bolt_hex.py"
LISTED = json.loads((REPO / "scripts" / "ci_type_free.json").read_text(encoding="utf-8"))

_READ = "from synthetic_ecommerce_data.domains.industrial.taxonomy import DRAWING"

_READERS = {
    "a table read": f"""
        {_READ}

        def test_reads():
            assert len(DRAWING)
    """,
    "a read at import": f"""
        {_READ}
        KEYS = list(DRAWING)

        def test_uses_it():
            assert KEYS
    """,
    "a read through discover": """
        from synthetic_ecommerce_data.core import typespec

        def test_reads():
            assert typespec.modelled()
    """,
}


def _run(tmp_path: Path, files: dict[str, str], listed: list[str]):
    """The planted files run by pytest with the recorder, and what it wrote."""
    for name, body in files.items():
        (tmp_path / name).write_text(textwrap.dedent(body), encoding="utf-8")
    table, out = tmp_path / "type_free.json", tmp_path / "reads.json"
    table.write_text(json.dumps(listed), encoding="utf-8")
    (tmp_path / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    env = {
        **{k: v for k, v in os.environ.items() if not k.startswith("PYTEST_")},
        "PYTHONPATH": os.pathsep.join([str(REPO / "src"), str(REPO / "tests")]),
        "TYPE_FREE_FILE": str(table),
        "TYPE_READS_OUT": str(out),
    }
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "type_reads", "-p", "no:cacheprovider", *files],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=300, check=False,
    )  # fmt: skip
    return done, json.loads(out.read_text(encoding="utf-8"))


@pytest.mark.parametrize("kind", sorted(_READERS))
def test_a_listed_file_that_reads_a_table_fails(tmp_path, kind):
    done, seen = _run(tmp_path, {"test_planted.py": _READERS[kind]}, ["test_planted.py"])
    assert done.returncode == 1, done.stdout + done.stderr
    assert "test_planted.py is listed in scripts/ci_type_free.json" in done.stdout
    assert seen == {"ran": ["test_planted.py"], "read": ["test_planted.py"]}


def test_an_unlisted_file_that_reads_a_table_passes_and_is_recorded(tmp_path):
    done, seen = _run(tmp_path, {"test_planted.py": _READERS["a table read"]}, [])
    assert done.returncode == 0, done.stdout + done.stderr
    assert seen["read"] == ["test_planted.py"]


def test_a_listed_file_that_reads_no_table_passes(tmp_path):
    body = """
        from synthetic_ecommerce_data.domains.retail import scale

        def test_reads_none():
            assert scale
    """
    done, seen = _run(tmp_path, {"test_planted.py": body}, ["test_planted.py"])
    assert done.returncode == 0, done.stdout + done.stderr
    assert seen == {"ran": ["test_planted.py"], "read": []}


def test_a_hit_on_a_cache_a_read_filled_is_a_read_of_the_file_that_hit_it(tmp_path):
    """``test_b`` reads nothing itself: ``test_a`` filled the cache in the same process."""
    files = {
        "shared_rows.py": f"""
            import functools

            {_READ}

            @functools.cache
            def rows():
                return tuple(DRAWING)

            @functools.cache
            def plain():
                return 1
        """,
        "test_a.py": """
            import shared_rows

            def test_fills():
                assert shared_rows.rows() and shared_rows.plain()
        """,
        "test_b.py": """
            import shared_rows

            def test_hits():
                assert shared_rows.rows()
        """,
        "test_c.py": """
            import shared_rows

            def test_hits_a_cache_that_reads_none():
                assert shared_rows.plain()
        """,
    }
    done, seen = _run(tmp_path, files, ["test_b.py", "test_c.py"])
    assert seen["read"] == ["test_a.py", "test_b.py"], done.stdout + done.stderr
    assert done.returncode == 1
    assert "test_b.py is listed" in done.stdout
    assert "test_c.py is listed" not in done.stdout


def test_a_product_module_reads_no_table_when_it_is_imported():
    """Nor do the retail builds a worker shares: a read there would count for one file only."""
    code = """
        import importlib, json, pkgutil
        import synthetic_ecommerce_data as package
        from synthetic_ecommerce_data.core import typespec

        names, read = [], []
        for part in ("core", "domains.retail"):
            root = importlib.import_module(f"{package.__name__}.{part}")
            for found in pkgutil.walk_packages(root.__path__, root.__name__ + "."):
                if found.name.endswith("__main__"):
                    continue
                importlib.import_module(found.name)
                names.append(found.name)
                if typespec._REGISTRATION["done"] and not read:
                    read.append(found.name)
        from synthetic_ecommerce_data.domains.retail import scale
        scale.templates()
        scale.build(2000)
        print(json.dumps([len(names), read, typespec._REGISTRATION["done"]]))
    """
    done = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        capture_output=True, text=True, timeout=300, check=False,
        env={**os.environ, "PYTHONPATH": str(REPO / "src")},
    )  # fmt: skip
    assert done.returncode == 0, done.stderr
    count, read, registered = json.loads(done.stdout.splitlines()[-1])
    assert count > 100
    assert read == [], "importing this module reads a type table; read it inside a function"
    assert not registered, "scale.templates() or scale.build() reads a type table"


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("import json\n", True),
        ("import subprocess\n", False),
        ("from multiprocessing import Process\n", False),
        ("from synthetic_ecommerce_data.core import typespec\n", False),
        ("from shared_builds import cached\n", False),
        ("import helper\n", False),
        ("import quiet\n", True),
    ],
)
def test_eligible(tmp_path, body, expected):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "helper.py").write_text("import quiet\nimport subprocess\n", encoding="utf-8")
    (tests / "quiet.py").write_text("import helper_of_none\n", encoding="utf-8")
    (tests / "test_x.py").write_text(body, encoding="utf-8")
    assert ci_type_free.eligible("tests/test_x.py", tmp_path) is expected


def test_refreshed_adds_what_ran_and_drops_what_read_and_what_is_gone(tmp_path):
    (tmp_path / "tests").mkdir()
    for name in ("kept", "new", "reads"):
        (tmp_path / "tests" / f"test_{name}.py").write_text("import json\n", encoding="utf-8")
    runs = [
        {"ran": ["tests/test_new.py", "tests/test_reads.py"], "read": []},
        {"ran": ["tests/test_reads.py"], "read": ["tests/test_reads.py"]},
    ]
    old = ["tests/test_gone.py", "tests/test_kept.py", "tests/test_reads.py"]
    assert ci_type_free.refreshed(old, runs, tmp_path) == [
        "tests/test_kept.py",
        "tests/test_new.py",
    ]


def test_every_listed_file_is_one_the_recorder_can_follow():
    assert sorted(set(LISTED)) == LISTED
    refused = [file for file in LISTED if not ci_type_free.eligible(file)]
    assert refused == [], "run scripts/ci_type_free.py --refresh, which drops them"


_LAZY = "src/synthetic_ecommerce_data/domains/industrial/__init__.py"
_PLANTED = {
    "src/synthetic_ecommerce_data/__init__.py": (
        "from synthetic_ecommerce_data.domains import industrial\n"
    ),
    "src/synthetic_ecommerce_data/domains/__init__.py": "",
    _LAZY: (
        "def _figures():\n"
        "    from synthetic_ecommerce_data.domains.industrial import figures\n"
        "    return figures\n\n"
        "def _load_types():\n"
        "    from synthetic_ecommerce_data.domains.industrial import types\n"
    ),
    "src/synthetic_ecommerce_data/domains/industrial/figures.py": "F = 1\n",
    "src/synthetic_ecommerce_data/domains/industrial/types.py": "T = 1\n",
    "src/synthetic_ecommerce_data/retail.py": "R = 1\n",
    "tests/test_listed.py": "from synthetic_ecommerce_data import retail\n",
    "tests/test_unlisted.py": "from synthetic_ecommerce_data import retail\n",
    "tests/test_direct.py": "from synthetic_ecommerce_data.domains.industrial import types\n",
    "scripts/ci_type_free.json": '["tests/test_direct.py", "tests/test_listed.py"]\n',
}


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ("types.py", {"tests/test_direct.py", "tests/test_unlisted.py"}),
        ("figures.py", {"tests/test_direct.py", "tests/test_listed.py", "tests/test_unlisted.py"}),
    ],
)
def test_only_a_listed_file_is_not_followed_into_the_loaders(tmp_path, change, expected):
    for name, text in _PLANTED.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    planted = ci_select.Tree(tmp_path)
    changed = str(Path(_LAZY).with_name(change))
    chosen, _ = ci_select.select([changed], planted)
    assert set(chosen) & set(_PLANTED) == expected


def test_a_list_that_cannot_be_read_drops_nothing(tmp_path):
    for name, text in {**_PLANTED, "scripts/ci_type_free.json": "not json"}.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    assert ci_select.Tree(tmp_path).type_free == frozenset()


@pytest.fixture(scope="module")
def tree():
    return ci_select.Tree(REPO)


@pytest.fixture(scope="module")
def by_type_module(tree):
    return ci_select.select([TYPE_MODULE], tree)[0]


def test_every_loader_name_is_in_the_file_it_is_named_for(tree):
    """A renamed loader would be followed again, and the list would drop nothing."""
    for path, names in ci_select.TYPE_LOADERS.items():
        missing = [
            n for n in names if not any(ci_select._defines(x, (n,)) for x in tree.trees[path].body)
        ]
        assert missing == []
        assert tree.unloaded[path] < tree.edges[path]


def test_a_type_module_drops_the_listed_files_and_keeps_the_rest(tree, by_type_module):
    dropped = set(LISTED) - set(by_type_module)
    assert len(dropped) >= 30, "the table drops almost nothing"
    assert tree.type_free == frozenset(LISTED)
    for kept in ("tests/test_type_seam.py", "tests/test_declared_copy_roles_75.py"):
        assert kept in by_type_module
        assert kept not in LISTED


@pytest.mark.parametrize("part", ["domains/retail/scale.py", "core/typespec.py"])
def test_a_listed_file_is_selected_by_the_modules_it_does_reach(tree, by_type_module, part):
    listed = "tests/test_retail_outerwear_211.py"
    chosen, _ = ci_select.select([f"src/synthetic_ecommerce_data/{part}"], tree)
    assert listed in chosen
    assert listed in LISTED
    assert listed not in by_type_module

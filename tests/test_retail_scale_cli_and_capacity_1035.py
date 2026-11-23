"""The retail scale CLI and the build at its capacity (gen#125, gen#220), apart from
``tests/test_retail_scale.py`` (#1035).

These tests read no build of that module's own (its ``built`` at ``TARGET``): they run the CLI
in a subprocess or on the shared ceiling build, or make a build past the ceiling. Together they
were about two of that file's seven minutes on CI, and one module is the floor of a shard's
time (docs/ci-sharding.md), so they are a file of their own.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from retail_ceiling import ceiling_build, templates
from synthetic_ecommerce_data.domains.retail import scale
from synthetic_ecommerce_data.domains.retail.retail_figures import figures
from test_retail_scale import starved, styles_by_department

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "src" / "synthetic_ecommerce_data" / "domains" / "retail"

#: The ceiling build's (styles, SKUs), as ``retail_figures.figures()`` measures it.
CAPACITY = (figures()["ceiling"]["styles"], figures()["ceiling"]["skus"])


@pytest.fixture(scope="module")
def ceiling() -> scale.Scaled:
    """Every template exhausted (gen#513: shared)."""
    return ceiling_build()


def test_the_cli_refuses_a_target_below_one():
    done = subprocess.run(
        [sys.executable, str(RETAIL / "scale.py"), "--skus", "0"],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert done.returncode == 2
    assert "--skus must be at least 1" in done.stderr


def test_the_cli_writes_the_report_and_the_documents(tmp_path):
    out, report = tmp_path / "retail.jsonl", tmp_path / "report.json"
    argv = ["--skus", "8000", "--out", str(out), "--report", str(report)]
    done = subprocess.run(
        [sys.executable, str(RETAIL / "scale.py"), *argv],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    got = json.loads(report.read_text(encoding="utf-8"))
    assert got["reached_target"] is True
    assert got["standard_problems"] == 0
    assert got["coverage"]["skus"] >= 8000
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == got["coverage"]["styles"]
    assert sum(json.loads(line)["variant_count"] for line in lines) == got["coverage"]["skus"]


def test_a_target_past_the_capacity_stops_there_and_the_cli_says_so(
    tmp_path, monkeypatch, capsys, ceiling
):
    """The CLI's own run, in process, on the shared ceiling build (#790): a target past the
    capacity takes ``build``'s loop to the same end as the ceiling's own target, so the build
    the CLI would make is the one already made, and a subprocess building it again was a minute
    of the same work. The ceiling build itself is that loop running out of templates."""
    PAST = CAPACITY[1] + 20000  # the ceiling moves with the data: a fixed target fell under it
    asked: list[tuple[int, int]] = []

    def shared(skus: int, seed: int = 0) -> scale.Scaled:
        asked.append((skus, seed))
        return ceiling

    monkeypatch.setattr(scale, "build", shared)
    report = tmp_path / "report.json"
    code = scale.main(["--skus", str(PAST), "--report", str(report)])
    stderr = capsys.readouterr().err
    assert asked == [(PAST, 0)], "the CLI did not ask the build for its target on seed 0"
    assert code == 2, stderr[-2000:]
    assert f"short: {CAPACITY[1]} SKUs of {PAST}" in stderr
    got = json.loads(report.read_text(encoding="utf-8"))
    assert got["reached_target"] is False
    assert got["standard_problems"] == 0
    assert (got["coverage"]["styles"], got["coverage"]["skus"]) == CAPACITY


#: The Home templates :func:`test_growing_one_department_never_starves_another` adds: a
#: batch the size of the Home types the open batches plan (gen#196-#217).
SYNTHETIC_HOME = 210


def test_growing_one_department_never_starves_another(ceiling, monkeypatch):
    """A batch that adds templates to one department leaves every other department's floor
    where it was (gen#220): each Home batch failed the old rule (half an even split of the
    total, which the batch itself inflates) and padded unrelated departments with filler rows.
    The build here adds :data:`SYNTHETIC_HOME` Home templates (copies of today's under new ids
    and titles) before the grocery styles, at the ceiling."""
    tpls = templates()
    home = [r for r in scale.derivable(tpls) if scale._department(r) == "Home"]
    extra = []
    for i in range(SYNTHETIC_HOME):
        r = copy.deepcopy(home[i % len(home)])
        old_id = r["product_id"]
        r["product_id"] += f"-SYN{i}"
        for s in r["skus"]:
            s["sku"] = r["product_id"] + s["sku"][len(old_id) :]
        r["title"] += f" Set {i + 2}"
        extra.append(r)
    grocery = [r for r in tpls if r["product_id"].startswith(scale.GROCERY_PREFIX)]
    rest = [r for r in tpls if not r["product_id"].startswith(scale.GROCERY_PREFIX)]
    monkeypatch.setattr(scale, "templates", lambda: [*rest, *extra, *grocery])
    grown = styles_by_department(scale.build(CAPACITY[1] * 4).records)
    before = styles_by_department(ceiling.records)
    assert grown["Home"] >= before["Home"] + SYNTHETIC_HOME
    assert starved(grown) == {}

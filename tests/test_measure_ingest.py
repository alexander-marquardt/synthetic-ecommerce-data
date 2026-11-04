"""``scripts/measure_ingest.py`` reads ingest cost from Elasticsearch's own responses (#838).

The responses under ``tests/fixtures/ingest_cost/`` were recorded from a local
Elasticsearch 9.2.1 container with a 512 MB heap, so these tests run with no
cluster.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import emit

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "ingest_cost"


def _script():
    spec = importlib.util.spec_from_file_location(
        "measure_ingest", ROOT / "scripts" / "measure_ingest.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


measure_ingest = _script()


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_the_heap_reading_is_the_nodes_used_and_max_heap():
    assert measure_ingest.heap_reading(_fixture("node_stats_jvm.json")) == (239788240, 536870912)


def test_the_primary_store_is_read_for_the_named_index():
    stats = _fixture("index_stats_store.json")
    assert measure_ingest.primary_store(stats, "test-838-probe") == {
        "lucene_docs": 1,
        "store_bytes": 3560,
    }


@pytest.mark.parametrize(("system", "expected"), [("Linux", 100 * 1024), ("Darwin", 100)])
def test_peak_rss_is_kibibytes_on_linux_and_bytes_on_macos(system, expected):
    assert measure_ingest.peak_rss_bytes(100, system) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("max\n", None), ("1687552000\n", 1687552000)],
    ids=["no-limit", "bytes"],
)
def test_a_cgroup_memory_file_reads_as_bytes_or_no_limit(text, expected):
    assert measure_ingest.cgroup_bytes(text) == expected


def test_the_sampler_keeps_every_reading_and_takes_one_more_on_exit():
    readings = iter([(10, 512), (30, 512), (20, 512), (5, 512)])
    sampler = measure_ingest.HeapSampler(lambda: next(readings), interval=3600)
    with sampler:
        pass
    assert sampler.used == [10, 30]
    assert sampler.max_bytes == 512


def test_the_settled_heap_is_the_lowest_reading_of_the_window():
    readings = iter([(40, 512), (25, 512), (31, 512)])
    assert (
        measure_ingest.settle(lambda: next(readings), seconds=0, interval=0, clock=lambda: 5.0)
        == 40
    )
    readings = iter([(40, 512), (25, 512), (31, 512)])
    clock = iter([0.0, 0.5, 1.0, 9.0])
    assert (
        measure_ingest.settle(
            lambda: next(readings), seconds=2, interval=0, clock=lambda: next(clock, 9.0)
        )
        == 25
    )


def test_the_nested_body_asks_for_no_replica_and_leaves_the_mapping_alone():
    body = measure_ingest.nested_index_body()
    assert body["settings"]["number_of_replicas"] == 0
    assert "number_of_replicas" not in emit.NESTED_MAPPING["settings"]
    assert body["mappings"] == emit.NESTED_MAPPING["mappings"]


@pytest.mark.parametrize(
    ("host", "index"),
    [("http://127.0.0.1:9200", "test-x"), ("http://127.0.0.1:9211", "products")],
)
def test_the_live_cluster_and_a_non_test_index_are_refused(host, index):
    with pytest.raises(SystemExit):
        measure_ingest.refuse_unsafe(host, (index,))


def test_a_test_index_on_a_test_cluster_is_allowed():
    measure_ingest.refuse_unsafe("http://127.0.0.1:9211", ("test-x",))


def test_the_merged_store_waits_for_the_force_merge_then_reads_the_store(monkeypatch):
    still_running = {**_fixture("forcemerge_task_completed.json"), "completed": False}
    answers = {
        "POST": iter([_fixture("forcemerge_started.json")]),
        "GET /_tasks": iter([still_running, _fixture("forcemerge_task_completed.json")]),
        "GET stats": iter([_fixture("index_stats_store_merged.json")]),
    }
    calls = []

    def fake_request(host, method, path, body=None):
        calls.append((method, path))
        if method == "POST":
            return next(answers["POST"])
        return next(answers["GET /_tasks" if path.startswith("/_tasks/") else "GET stats"])

    monkeypatch.setattr(measure_ingest, "request", fake_request)
    assert measure_ingest.merged_store("http://127.0.0.1:9211", "test-838-probe", poll=0) == 3706
    assert calls == [
        ("POST", "/test-838-probe/_forcemerge?max_num_segments=1&wait_for_completion=false"),
        ("GET", "/_tasks/uKsMCB9kRd2DNivBuTxPAw:335"),
        ("GET", "/_tasks/uKsMCB9kRd2DNivBuTxPAw:335"),
        ("GET", "/test-838-probe/_stats/store,docs"),
    ]

"""Measure what serving a build costs: ingest time, index size and Elasticsearch heap.

    python scripts/measure_ingest.py --host http://127.0.0.1:9211 --lines 39000 \\
        --container ingest-es --machine "agent VM" --out .agent/ingest.jsonl

Builds ``--lines``, loads both shapes into a LOCAL TEST cluster the way
``scripts/load_prism_catalog.py`` and ``scripts/verify_elasticsearch.py`` do
(the served flat index and the nested one), and prints one JSON record:

* ``generate_s``, ``ingest_s`` and ``end_to_end_s``: building the catalog,
  then creating, bulk-loading and refreshing both indices, then both;
* ``indices``: each index's documents, Lucene documents and primary store bytes;
* ``heap``: Elasticsearch heap sampled from ``_nodes/_local/stats/jvm`` during
  the ingest (``peak_bytes``) and over a quiet window after it
  (``settled_bytes``, the window's lowest reading), against ``max_bytes``;
* ``container_peak_bytes``: the Elasticsearch container's cgroup
  ``memory.peak`` when ``--container`` names a docker container started for
  this run (it counts from the container's start, so one run per container);
* ``loader_peak_rss_bytes``: this process's own peak resident memory, the
  generator's catalog included;
* ``machine``: the label, host memory and CPU count it ran on.

``docs/ingest-cost.md`` holds the figures and how they were taken. The
indices are deleted at the end unless ``--keep`` is given.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import platform
import resource
import subprocess
import sys
import threading
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_elasticsearch import FORBIDDEN_PORTS, bulk_load, request  # noqa: E402

from prism_synthetic_industrial import FLAT_INDEX  # noqa: E402
from synthetic_ecommerce_data.core import emit  # noqa: E402
from synthetic_ecommerce_data.core.config import GeneratorConfig  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.generate import generate  # noqa: E402
from synthetic_ecommerce_data.prism.index import (  # noqa: E402
    flat_index_body,
    projected_documents,
)

NESTED_INDEX = "test-2026-09-17-sip-nested"

#: Seconds between heap readings during the ingest and the settle window.
SAMPLE_INTERVAL_S = 0.25

JVM_STATS_PATH = "/_nodes/_local/stats/jvm?filter_path=nodes.*.jvm.mem"


def heap_reading(node_stats: dict[str, Any]) -> tuple[int, int]:
    """``(heap used, heap max)`` in bytes from a one-node ``_nodes/stats/jvm`` response."""
    (node,) = node_stats["nodes"].values()
    mem = node["jvm"]["mem"]
    return mem["heap_used_in_bytes"], mem["heap_max_in_bytes"]


def primary_store(index_stats: dict[str, Any], index: str) -> dict[str, int]:
    """An index's primary Lucene document count and store bytes from ``_stats/store,docs``.

    A nested entry is a Lucene document of its own, so ``lucene_docs`` is above the
    product count for the nested index; ``_count`` gives the top-level documents.
    """
    primaries = index_stats["indices"][index]["primaries"]
    return {
        "lucene_docs": primaries["docs"]["count"],
        "store_bytes": primaries["store"]["size_in_bytes"],
    }


def peak_rss_bytes(ru_maxrss: int, system: str) -> int:
    """``getrusage``'s ``ru_maxrss`` in bytes: kibibytes on Linux, bytes on macOS."""
    return ru_maxrss if system == "Darwin" else ru_maxrss * 1024


def cgroup_bytes(text: str) -> int | None:
    """A cgroup v2 memory file's value; ``max`` (no limit) is ``None``."""
    value = text.strip()
    return None if value == "max" else int(value)


def nested_index_body() -> dict[str, Any]:
    """The nested mapping, with no replica: a single-node test cluster cannot allocate one."""
    body = copy.deepcopy(emit.NESTED_MAPPING)
    body["settings"]["number_of_replicas"] = 0
    return body


def refuse_unsafe(host: str, indices: tuple[str, ...]) -> None:
    for port in FORBIDDEN_PORTS:
        if port in host:
            raise SystemExit(f"refusing {host}: {port} is the live demo cluster")
    for index in indices:
        if not index.startswith("test-"):
            raise SystemExit(f"refusing index {index!r}: only test-* indices are created here")


class HeapSampler:
    """Reads the heap every ``interval`` seconds on a thread and keeps the readings."""

    def __init__(self, read: Callable[[], tuple[int, int]], interval: float = SAMPLE_INTERVAL_S):
        self._read = read
        self._interval = interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.used: list[int] = []
        self.max_bytes = 0

    def _sample(self) -> None:
        used, max_bytes = self._read()
        self.used.append(used)
        self.max_bytes = max_bytes

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            self._sample()

    def __enter__(self) -> HeapSampler:
        self._sample()
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        self._thread.join()
        self._sample()


def settle(
    read: Callable[[], tuple[int, int]],
    seconds: float,
    interval: float,
    clock: Callable[[], float] = time.monotonic,
) -> int:
    """The lowest heap reading over a quiet window of ``seconds`` after the ingest."""
    readings = [read()[0]]
    deadline = clock() + seconds
    while clock() < deadline:
        time.sleep(interval)
        readings.append(read()[0])
    return min(readings)


def container_peak(container: str) -> int | None:
    out = subprocess.run(
        ["docker", "exec", container, "cat", "/sys/fs/cgroup/memory.peak"],
        capture_output=True,
        text=True,
        check=True,
    )
    return cgroup_bytes(out.stdout)


def machine(label: str) -> dict[str, Any]:
    pages = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    return {
        "label": label,
        "system": platform.system(),
        "memory_bytes": pages,
        "cpus": os.cpu_count(),
    }


def merged_store(host: str, index: str, poll: float = 2.0) -> int:
    """The index's primary store bytes once force-merged to one segment.

    The store read straight after the ingest still holds segments Elasticsearch
    has not merged yet, so two runs of one build differ; the merged size does not.
    """
    merge = f"/{index}/_forcemerge?max_num_segments=1&wait_for_completion=false"
    task = request(host, "POST", merge)["task"]
    while not request(host, "GET", f"/_tasks/{task}").get("completed"):
        time.sleep(poll)
    stats = request(host, "GET", f"/{index}/_stats/store,docs")
    return primary_store(stats, index)["store_bytes"]


def jvm_reader(host: str) -> Callable[[], tuple[int, int]]:
    def read() -> tuple[int, int]:
        with urllib.request.urlopen(f"{host}{JVM_STATS_PATH}", timeout=30) as response:
            return heap_reading(json.loads(response.read()))

    return read


def measure(args: argparse.Namespace) -> dict[str, Any]:
    read = jvm_reader(args.host)
    info = request(args.host, "GET", "/")

    started = time.perf_counter()
    catalog = generate(GeneratorConfig(seed=args.seed, lines=args.lines))
    generated = time.perf_counter()

    shapes = (
        (NESTED_INDEX, nested_index_body(), lambda: emit.iter_nested(catalog), "product_id"),
        (
            FLAT_INDEX,
            flat_index_body(),
            lambda: projected_documents(emit.iter_flat(catalog)),
            "sku",
        ),
    )
    with HeapSampler(read) as sampler:
        for index, body, rows, id_field in shapes:
            request(args.host, "DELETE", f"/{index}?ignore_unavailable=true")
            request(args.host, "PUT", f"/{index}", body)
            bulk_load(args.host, index, rows(), id_field)
    ingested = time.perf_counter()

    settled = settle(read, args.settle, SAMPLE_INTERVAL_S)
    stats = request(args.host, "GET", f"/{NESTED_INDEX},{FLAT_INDEX}/_stats/store,docs")
    indices = {
        index: {
            **primary_store(stats, index),
            "documents": request(args.host, "GET", f"/{index}/_count")["count"],
            "merged_store_bytes": merged_store(args.host, index),
        }
        for index, *_ in shapes
    }
    record = {
        "lines": args.lines,
        "seed": args.seed,
        "skus": catalog.sku_count,
        "products": len(catalog.lines),
        "elasticsearch": info["version"]["number"],
        "generate_s": round(generated - started, 1),
        "ingest_s": round(ingested - generated, 1),
        "end_to_end_s": round(ingested - started, 1),
        "indices": indices,
        "heap": {
            "peak_bytes": max(sampler.used),
            "settled_bytes": settled,
            "max_bytes": sampler.max_bytes,
        },
        "container_peak_bytes": container_peak(args.container) if args.container else None,
        "loader_peak_rss_bytes": peak_rss_bytes(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, platform.system()
        ),
        "machine": machine(args.machine),
    }
    if not args.keep:
        for index, *_ in shapes:
            request(args.host, "DELETE", f"/{index}")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", default="http://127.0.0.1:9201")
    parser.add_argument("--lines", type=int, default=GeneratorConfig.lines)
    parser.add_argument("--seed", type=int, default=GeneratorConfig.seed)
    parser.add_argument(
        "--container", help="the docker container Elasticsearch runs in, for its memory.peak"
    )
    parser.add_argument(
        "--machine", default=platform.node(), help="the machine's name in the record"
    )
    parser.add_argument(
        "--settle", type=float, default=30.0, help="seconds of quiet after the ingest"
    )
    parser.add_argument("--out", type=Path, help="append the record to this JSONL file")
    parser.add_argument("--keep", action="store_true", help="do not delete the test indices")
    args = parser.parse_args(argv)

    refuse_unsafe(args.host, (NESTED_INDEX, FLAT_INDEX))
    record = measure(args)
    line = json.dumps(record, sort_keys=True)
    print(line)
    if args.out:
        with args.out.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

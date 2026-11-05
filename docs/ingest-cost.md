# What serving a build costs in Elasticsearch

Before a build larger than the 100K one (`--lines 39000`) is served, measure
its ingest time, its index size and Elasticsearch's heap at that size, and
compare them with the rows below (#838, plan step 5 of #53). The host has run
out of memory before (#53), so a larger build is served only once these
figures say it fits.

This page is a dated record, not a live figure: each row names the commit,
machine and command it came from. Add a row when a new size is measured.
Never edit an old row.

## How it is measured

`scripts/measure_ingest.py` builds `--lines`. It loads both shapes into a
local test cluster with the loaders `scripts/verify_elasticsearch.py` uses:
the served flat index (`flat_index_body`, the projected documents
`scripts/load_prism_catalog.py` loads) and the nested one. It then prints one
JSON record.

| field | what it is |
|---|---|
| `generate_s` | building the catalog in memory |
| `ingest_s` | creating, bulk-loading and refreshing both indices |
| `end_to_end_s` | the two together |
| `indices.*.store_bytes` | primary store straight after the ingest; it still holds unmerged segments, so two runs of one build differ |
| `indices.*.merged_store_bytes` | primary store once force-merged to one segment: the size to compare against |
| `heap.peak_bytes` | the highest of the heap readings from `_nodes/_local/stats/jvm`, taken every 0.25 s during the ingest |
| `heap.settled_bytes` | the lowest reading over 30 quiet seconds after the ingest |
| `container_peak_bytes` | the Elasticsearch container's cgroup `memory.peak`, page cache included |
| `loader_peak_rss_bytes` | the loader's own peak resident memory, the generated catalog included |

Each build gets a fresh container, so `memory.peak` is that build's alone:

```sh
docker run -d --name ingest-es -p 127.0.0.1:9211:9200 \
  -e discovery.type=single-node -e xpack.security.enabled=false \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -e cluster.routing.allocation.disk.threshold_enabled=false \
  docker.elastic.co/elasticsearch/elasticsearch:9.2.1
uv run python scripts/measure_ingest.py --host http://127.0.0.1:9211 \
  --lines 156000 --container ingest-es --machine "agent VM" --out ingest.jsonl
docker rm -f ingest-es
```

The heap is the one elastic/prism's local `docker-compose.yaml` gives
Elasticsearch on the laptop (`-Xms512m -Xmx512m`), and the image is that
compose file's default version.

## The machine

The agent VM that also hosts this repository's self-hosted CI runners:
Linux, 32 CPUs, 58.8 GiB (`machine.memory_bytes` 63,183,056,896). It was
running other jobs' CI shards during every run, so the seconds are a
contended host's. Two runs of the 39,000-line build ingested in 74 s and
92 s.

All rows below were measured on 2026-11-04 on main `a7281ab5`. MB is 10^6
bytes.

## Free runs: no memory limit

Measured with the command above, with no limit on the container or the
loader.

| `--lines` | SKUs | products | generate s | ingest s | end to end s | flat merged MB | nested merged MB | heap peak / settled MB | container peak MB | loader peak MB |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 2,600 (default) | 13,620 | 6,932 | 8.6 | 9.6 | 18.2 | 18 | 14 | 362 / 265 | 1,784 | 107 |
| 39,000 (100K build) | 140,603 | 42,874 | 92.6 | 86.9 | 179.6 | 169 | 110 | 449 / 221 | 2,876 | 463 |
| 78,000 | 242,648 | 71,026 | 150.7 | 151.0 | 301.7 | 293 | 191 | 464 / 317 | 3,505 | 744 |
| 156,000 | 419,039 | 117,331 | 379.1 | 265.5 | 644.6 | 512 | 337 | 468 / 190 | 3,320 | 1,242 |

Every heap reading is against a 512 MiB maximum (536,870,912 bytes).

The issue counted the 100K build at 138,082 SKUs. On `a7281ab5` it is
140,603, because types deepened since then add their share of `--lines`.

What the rows show:

- **Index size grows in step with the build.** The flat index takes about
  1.2 KB per SKU and the nested one 2.6 to 2.9 KB per product. The unmerged
  store read straight after the ingest is larger and varies between runs:
  870 MB and 500 MB for the flat index of the 156,000-line build.
- **The heap does not grow with the build.** The peak sits under the 512 MiB
  maximum at every size, and the settled heap stays between 190 and 317 MB.
  Bulk indexing is bounded by Elasticsearch's indexing buffer, a share of the
  heap, and not by the document count.
- **The loader grows with the build.** It holds the whole generated catalog
  in memory: about 3 KB per SKU, 1.24 GB at 419,039 SKUs.
- **The container's `memory.peak` is not what the container needs.** It
  counts page cache, which the kernel reclaims under a limit. The capped runs
  below are the evidence for what fits.

## Capped runs: the CI runner's memory

A self-hosted `synth-ci` runner is a container with a 6 GiB `memory.max` and
4 CPUs ([docs/ci-sharding.md](ci-sharding.md)). The capped runs split those
6 GiB between the two processes:

- Elasticsearch gets 2 GiB with no swap (`docker run --memory 2g --memory-swap 2g`, the rest as above);
- the loader gets 4 GiB with no swap (`systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=0 uv run python scripts/measure_ingest.py ...`).

The CPUs were not capped, so these runs' seconds are not the runner's.

| `--lines` | SKUs | ingest s | end to end s | flat MB (unmerged) | nested MB (unmerged) | heap peak / settled MB | container peak MB | loader peak MB | result |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| 39,000 | 140,603 | 73.8 | 149.3 | 166 | 111 | 456 / 227 | 2,148 (the cap) | 464 | loaded, no OOM kill |
| 156,000 | 419,039 | 226.5 | 557.1 | 500 | 386 | 468 / 289 | 2,148 (the cap) | 1,255 | loaded, no OOM kill |

The container reached its cap and kept running: what it gave up was page
cache. The capped runs predate `merged_store_bytes`, so their sizes are the
unmerged store.

## The largest build that fits

| machine | memory | largest build that fits | how it is known |
|---|---|---|---|
| CI runner (`synth-ci`) | 6 GiB `memory.max`, 4 CPUs | 156,000 lines, 419,039 SKUs: the largest measured, so no limit was reached | the capped runs: 2 GiB Elasticsearch plus 4 GiB loader, both loaded with no OOM kill |
| laptop | 512 MiB Elasticsearch heap (elastic/prism `docker-compose.yaml`) | 156,000 lines, 419,039 SKUs, when 6 GiB are free for Elasticsearch and the loader together | not run on the laptop, which the VM cannot reach; the heap is the laptop's own 512 MiB and stays under it at every size, and the capped runs show 6 GiB is enough |

419,039 SKUs is above the roughly 350K ceiling that the 2026-10-06 survey on
#53 puts on a fully deepened build. So any target #837 names fits both
machines by these figures. Measure it again at its own size before it is
served all the same: the rows above are this commit's types, and a new type
moves the bytes per SKU.

None of this covers serving: query-time heap under search load is not
measured here.

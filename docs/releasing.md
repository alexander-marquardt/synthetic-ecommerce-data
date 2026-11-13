# Releasing the generator

A merged decoy or product used to reach the catalogue repository only by hand: the generator had
no releases, and the catalogue pins `catalog_release.json` and `images_release.json` by
digest (gen#536). The image pin is ONE set for the combined catalog, industrial and retail
together, one file per SKU (gen#706), and it ships as its own release, tagged
`images-<count>-<YYYYMMDD>` (gen#804). A release is a `v*` tag.

## What a tag does

`.github/workflows/release.yaml` runs on a pushed `v*` tag and:

1. builds the retail ceiling (`python -m synthetic_ecommerce_data.domains.retail.scale --skus ceiling
   --out build/release/retail/nested.jsonl --flat build/release/retail/flat.jsonl`, the build run to
   its ceiling);
2. builds the industrial large catalog (`ecom-generate build --lines 39000`, `config.LARGE_BUILD_LINES`),
   then sweeps the build sizes (gen#949): `ecom-generate build` at `--lines` 2600, 4000 and 10000
   into `build/sweep/<lines>`, and checks that each of those builds and the large build wrote
   `nested.jsonl`, `flat.jsonl`, `images.jsonl` and `stats.json`. A value only a larger build
   draws once stopped the 4000-line build part-way while the default build passed. The sweep is
   too slow for CI (2 to 4 minutes), which keeps the per-material test
   (`tests/test_material_styles_949.py`); `RELEASE_SWEEP_LINES` names other sizes;
3. composes the two into the ONE catalog (`ecom-generate compose --domain industrial=... --domain
   retail=...`, gen#125): `build/release/catalog/catalog.ndjson`, industrial's flat file then
   retail's, byte for byte, and `provenance.json`, where each domain's lines sit and each part's
   sha256. A union the output standard refuses (a `sku` or `product_id` two domains share, a key
   two domains name differently) fails the tag. It is gzipped as `catalog.ndjson.gz`;
4. builds the one image bundle (`python -m synthetic_ecommerce_data.domains.retail.image_release
   --skus ceiling --industrial-catalog ...`) as
   `images.tar.gz`: both halves' drawings, a file per SKU, refused if two SKUs share a file or a
   SKU has none;
5. uploads the catalog and its provenance to the tag's release with
   `catalog.ndjson.gz.content-sha256` (`<sha256>  <count>`);
6. uploads the bundle to its own release, `images-<count>-<YYYYMMDD>` (the archive's file count
   from `images.tar.gz.content-sha256` and the UTC day of the run, gen#804), with that sidecar and
   `images.tar.gz.sha256`. The images release holds `images.tar.gz` and nothing of the catalog.
   A second `v*` tag the same day whose archive has the same count reuses that release when its
   `images.tar.gz.content-sha256` is the same, and fails when it differs;
7. runs `scripts/open_pin_bump_pr.py --images-tag images-<count>-<YYYYMMDD>`, which writes the two
   pin files with the new digests and opens a pull request in `elastic/prism-retail-and-industrial`:
   `catalog_release.json` names the `v*` tag, `images_release.json` the images tag. The catalog
   pin's digest is of the UNCOMPRESSED composed documents (a gzip's bytes depend on the
   toolchain); the image pin's is the content digest `image_release.py` prints. The script refuses
   an `--images-tag` that is not `images-<count>-<YYYYMMDD>`, names no real date, or counts other
   than the archive's files.

## Composing locally

```sh
uv run ecom-generate compose --domain industrial=out/catalog --domain retail=out/retail --out out/combined
```

Each `--domain` is a domain's finished build (a directory holding its `nested.jsonl` and
`flat.jsonl`). `compose` writes `catalog.ndjson` (every domain's flat file byte for byte, in the
order given) and `provenance.json`, and writes nothing when the union breaks the output standard.

## The build's memory

The release runner is `ubuntu-latest` (16 GB), so the industrial build's peak memory decides
how large a catalogue it can make (gen#952). These are peak RSS and wall time, measured by
`/usr/bin/time -v ecom-generate build --lines N` on a 32-vCPU Linux machine:

| `--lines` | SKUs | before gen#952 | passes fixed (gen#977) | one type at a time |
|---|---|---|---|---|
| 2,600 | 14,559 | 354 MiB, 24 s | 118 MiB, 18 s | 63 MiB |
| 10,000 | 49,378 | 1,114 MiB, 69 s | 307 MiB, 44 s | 93 MiB |
| 39,000 | 176,348 | 3,866 MiB, 197 s | 790 MiB, 155 s | 268 MiB |

The last column was measured on a loaded machine, so it gives no wall time. Its CPU time at
10,000 lines is the same as the column before it (62 s and 64 s of user time, side by side).
Each step leaves the output byte for byte the same.

Two passes held the catalogue a second time, and neither does now:

- The price census (`price_report.collect`) stored every within-cell SKU pair. A cell's pairs
  grow with the square of its members, so they took 2.2 GiB at 39,000 lines and would take about
  17.7 GiB at 500K SKUs. `CellPairs` now keeps each cell's members once and generates the pairs
  each time a price row counts them.
- The figures pass (`generate_cli._measured_figures`) read `flat.jsonl` back as one list of
  dicts, which took 3.3 GiB. It now reads each file one line at a time.

`tests/test_build_peak_memory_952.py` fails if either pass holds such a list again.

The build then held the catalogue object itself, about 2.7 KB per SKU, about 1.4 GiB at 500K
SKUs. Now it builds one product type at a time (`generate.iter_types`). It builds a type,
audits it, writes its lines and drops it before it builds the next, so the peak grows with the
largest type and not with the catalogue. What it keeps across types:

- tallies and per-type summaries (`measure.Measurement`);
- the price census's per-SKU ids and keys (`price_report.PriceTally`);
- the non-copying audit's collisions.

The figures pass (`prism.derive.measure`) counts each product's (product, value) pairs when it
reaches the product's last document and then drops them. A product's documents come one after
another; if a product appears again after another one, the pass refuses rather than counting it
twice. The build writes into a temporary directory beside `--out` and moves the files into
`--out` once every audit has passed, so a refusal after some types were written still leaves
`--out` untouched (gen#253).

`tests/test_build_streams_by_type_952.py` holds this:

- When `--lines` doubles from 2,600 to 5,200, the peak RSS may grow by at most 25 MiB. It grows
  by about 5 MiB. Holding the catalogue whole, it grew by 70 MiB.
- No earlier type's products are alive when the next type is built.
- The files are those the whole catalogue writes.

The `--stress-keys` build still holds every nested document at once (gen#952 slice 3).

## The dry run

A manual run of the workflow (Actions, Release, Run workflow, with a `tag` such as `v0.0.0-dryrun`)
builds the same assets, prints the pin-bump pull request body (`scripts/open_pin_bump_pr.py
--dry-run`) and uploads the assets and the body as the `release-dry-run` artifact. It creates no
release and opens no pull request, so it runs on a fork. Locally, with the two built files:

```sh
python3 scripts/open_pin_bump_pr.py --tag v0.0.0-dryrun --catalog build/release/catalog/catalog.ndjson \
    --images-sidecar build/release/images.tar.gz.content-sha256 --dry-run
```

## The token

The real run needs a repository secret `PIN_BUMP_TOKEN`: a token scoped to contents and pull
requests of `elastic/prism-retail-and-industrial` and nothing else. The script reads it from the
environment and never prints it; without it, and without `--dry-run`, it exits 2.

`release.yaml` is not a pull-request check: `scripts/local_ci_jobs.py` (`NOT_A_CHECK`) leaves it
out of `merge_pr.sh --local-ci`.

## The flat document's price and rating shapes

A flat document states its price as `price` in `currency` (`USD`) and its
availability as `in_stock`, the same columns the nested variant and the retail
flat document carry, so the composed catalog (`ecom-generate compose`) has one
price shape. `price_usd` and the `stock` count stay beside them for the
industrial loader. On the retail side, a `rating` entry carries its number as
`value_canonical` with no unit (a score, `core/standard.py` `SCORE_KEYS`), and a
shoe's fit is `fit_width`. Both are shapes the catalogue repo's Combined
projection used to make (gen#125).

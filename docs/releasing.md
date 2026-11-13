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
   too slow for CI (about 3.5 minutes), which keeps the per-material test
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

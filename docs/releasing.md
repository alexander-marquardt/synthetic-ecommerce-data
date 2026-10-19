# Releasing the generator

A merged decoy or product used to reach the catalogue repository only by hand: the generator had
no releases, and the catalogue pins `catalog_release.json` and `images_release_retail.json` by
digest (gen#536). A release is a `v*` tag.

## What a tag does

`.github/workflows/release.yaml` runs on a pushed `v*` tag and:

1. builds the ceiling export (`prototypes/retail_drawings/scale.py --skus ceiling --flat ...`,
   the build run to its ceiling) and gzips it as `catalog.ndjson.gz`;
2. builds the retail image bundle (`image_release.py --skus ceiling`) as `retail-images.tar.gz`;
3. uploads both to the tag's release with their sidecars: `catalog.ndjson.gz.content-sha256` and
   `retail-images.tar.gz.content-sha256` (`<sha256>  <count>`), and `retail-images.tar.gz.sha256`;
4. runs `scripts/open_pin_bump_pr.py`, which writes the two pin files with the new digests and
   opens a pull request in `elastic/prism-retail-and-industrial`. The catalog pin's digest is of
   the UNCOMPRESSED documents (a gzip's bytes depend on the toolchain); the image pin's is the
   content digest `image_release.py` prints.

## The dry run

A manual run of the workflow (Actions, Release, Run workflow, with a `tag` such as `v0.0.0-dryrun`)
builds the same assets, prints the pin-bump pull request body (`scripts/open_pin_bump_pr.py
--dry-run`) and uploads the assets and the body as the `release-dry-run` artifact. It creates no
release and opens no pull request, so it runs on a fork. Locally, with the two built files:

```sh
python3 scripts/open_pin_bump_pr.py --tag v0.0.0-dryrun --catalog build/release/catalog.ndjson \
    --images-sidecar build/release/retail-images.tar.gz.content-sha256 --dry-run
```

## The token

The real run needs a repository secret `PIN_BUMP_TOKEN`: a token scoped to contents and pull
requests of `elastic/prism-retail-and-industrial` and nothing else. The script reads it from the
environment and never prints it; without it, and without `--dry-run`, it exits 2.

`release.yaml` is not a pull-request check: `scripts/local_ci_jobs.py` (`NOT_A_CHECK`) leaves it
out of `merge_pr.sh --local-ci`.

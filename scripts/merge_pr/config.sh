# The lists scripts/merge_pr.sh works from: what it checks, what it rebuilds, what it waits for.
# shellcheck shell=bash disable=SC2034  # read by the files that source this one

#: The tests that see what a textually clean merge can still get wrong. The README
#: size test is one: two PRs each under the cap can sum to more than it (#700), and
#: the file-size job compares each PR with its own merge base, so only the merged
#: tree shows the sum.
CHECKS=(
  tests/test_prism_field_map_drift.py
  tests/test_catalog_golden.py
  tests/test_type_seam.py
  tests/test_a_type_module_imported_first.py
  tests/test_readme_split_240.py
)
# tests/test_merge_pr.py narrows them, to prove this script's control flow
# with one fast check; nothing else should set it.
if [ -n "${MERGE_PR_CHECKS:-}" ]; then
  read -r -a CHECKS <<<"$MERGE_PR_CHECKS"
fi

#: Exactly the files rebuild_generated rewrites (the build, the measured builds and the
#: golden pins), so a conflict in one is resolved by a rebuild. Any other conflict, under golden-catalog/ or not, goes back to the
#: builder. Pinned to the builds by tests/test_merge_pr.py.
GENERATED=(
  golden-catalog/authored_names.json
  golden-catalog/flat.jsonl
  golden-catalog/images.jsonl
  golden-catalog/mapping.flat.json
  golden-catalog/mapping.nested.json
  golden-catalog/nested.jsonl
  golden-catalog/stats.json
  src/synthetic_ecommerce_data/core/data/measured_builds.json
  src/prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml
  tests/data/golden_pins.json
)

#: The tests whose red means "a generated file is stale", as the test runner names
#: them in its FAILED/ERROR summary lines (parameters dropped). A local CI that is
#: red on these alone is regenerated (#440). Pinned to real tests by tests/test_merge_pr.py.
FRESHNESS_TESTS=(
  tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build
  tests/test_catalog_golden.py::test_golden_directory_holds_exactly_the_build_output
  tests/test_prism_field_map_drift.py::test_committed_field_map_matches_a_fresh_derivation
  tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed
)

#: The GENERATED files the code reads at import, so a conflicted copy (markers in it) stops the
#: very build that would rewrite it. The merge drops such a file before the rebuild.
READ_AT_IMPORT=(
  src/synthetic_ecommerce_data/core/data/measured_builds.json
)

#: The command that rewrites the pinned price figures and the 100K build's sizes
#: (gen#85), the one measured_builds.py names as REBUILD, which
#: tests/test_merge_pr.py pins. It builds the default and the 100K catalog,
#: about a minute.
BUILDS_REBUILD=(python -m synthetic_ecommerce_data.domains.industrial.measured_builds)

#: The command that re-measures the pins the tests read on the catalog (gen#50): every catalog
#: PR moves them, so two such PRs conflict in the fixture (gen#513). It reads the rebuilt catalog.
PINS_REBUILD=(python scripts/measure_pins.py)

#: The jobs of .github/workflows/ci.yaml, by the check-run name GitHub gives
#: them (a matrix job's name carries its shard: ``tests (3)``, and a required name
#: stands for every ``<name> (...)``). A pull request's commit must carry each
#: REQUIRED_CI check, green; a SKIPPED_BY_DESIGN_CI check may also be skipped:
#: ci.yaml's push-only job, and review-verdict.yaml's review-verdict-rerun, which
#: runs only on a Review-Verdict: comment or review event, never on the PR's own
#: run (#708). Pinned to the workflows by tests/test_merge_pr.py.
REQUIRED_CI=(lint ceiling-catalogue tests commit-messages file-size red-commit-proof customer-name-check no-derived-files)
SKIPPED_BY_DESIGN_CI=(main-merged-tree review-verdict-rerun)

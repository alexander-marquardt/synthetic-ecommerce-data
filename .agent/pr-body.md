<!-- pr-body-for: branch=issue-98 -->
Closes #98

Roller chain's distinct-spec floor was 0.30. The offers are widened from nine to fourteen, read off a distributor's published chain chart, and the floor is raised to what the wider offer holds.

## What changed

- `roller_chain.OFFERS`: the heavy series (40H-240H single, 60H-160H double), the four strand chart (60-120) and the zinc plated finish (35-100 single, 40-80 double). 94 size-and-offer pairs against 63. A heavy chain is priced 1.15 times the standard chain of its number (`HEAVY_FACTOR`), a four strand chain 3.7 times a single strand one (`STRAND_FACTORS`).
- `DISTINCT_SPEC_FLOOR["roller_chain"]`: 0.30 to 0.70.
- The strand-order test reads each set within one brand, because a brand's strand counts of a spec share one price draw while across-brand medians are noise at a few lines. Its set counts are 13 (default) and 105 (39000 lines).
- `scripts/mutations/industrial.py`: the two stale strand rows are replaced, and rows are added for the heavy, four strand and zinc offers and the five new offer lines.
- Regenerated: golden catalog, `field_weights` yaml, the roller chain golden slice and the golden pins.

## Measured

- At `--lines 39000` the type holds 609 SKUs and 439 distinct specs over 369 lines, 0.7209; main holds 509 and 334, 0.656. Command: `.venv/bin/python .agent/measure_distinct.py` (a build at `--lines 39000` with `types=["roller_chain"]`, counting distinct authored specs outside List Number, Standards and Measurement System, as the floor test does), and `tests/test_type_roller_chain.py::test_the_distinct_spec_floor_holds_at_100k` holds it.
- The price band stays inside roller chain's census band (p90/p10 7.82-13.87): four strand at 60-120 gives 12.24. Command: `agent_pytest tests/test_price_census_bands_69b.py tests/test_price_census_69.py`.
- The issue's struck line: its 0.34 at 39000 lines was stale; main already measured 509 SKUs and 334 distinct specs, 0.656. Command: the same measure script on main.

## Tests

- Red commit 0786c3e7 (`Red-Test:` lines in its message): the six ids fail on main's source. Command: `agent_pytest` on those ids at 0786c3e7 with the source unchanged.
- `agent_pytest tests/test_type_roller_chain.py` passes (34 of 34); the wider targeted batch (roller chain, sprockets, links, brand voice, golden, measured figures, price) passes 541 of 542 before the strand-order test was read per brand, and passes after.
- `scripts/mutation_check.py --only "roller chain"`: 10 of 10 mutations caught by every test they name, suite green before and after.

Docs-Impact: README.md updated in this PR (the per-type count 609, the 609-over-369 figure, the strand-factor text and the strand-set counts).

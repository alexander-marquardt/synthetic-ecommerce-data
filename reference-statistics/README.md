# Reference statistics

Derived measurements from a corpus of **496 archived product records** (742 requests,
zero rate-limit events). These are the numbers the generator targets — the rates in
`catalog/config.py` cite these files by name.

**What is here:** counts, rates, distributions, vocabularies, and the title grammar.
Facts about how the industry models this data.

**What is NOT here, by design:** the corpus itself. The raw captures are analysis input
and are excluded by `.gitignore` (`raw/`, `corpus/`, `reference/`). Illustrative records
inside these files are **capped at two per pattern** — enough to show what a statistic
describes, not enough to reconstitute the source. The un-capped working copies existed
only on the machine that produced them.

**Provenance:** `MANIFEST.json` carries the request accounting, the capture-era handling,
and the priority ordering the collection ran under.

**Why they are checked in:** the generator's targets are meaningless without the
measurements behind them, and a number whose source lives only in a temporary directory
cannot be re-derived or challenged. `00_attribute_name_census.json` carries all 585
observed attribute names; that breadth is the point and is not capped. Its `n_records` is
per-record presence, the same count as `n` in `06_attribute_sparsity.json`: a name repeated on
several rows of one specification table counts once per record (#367), and
`tests/test_census_agrees_with_sparsity_367.py` holds the two files to one figure per name.

**`R1_reference_spec_table_names.json` is a different kind of file.** It is not derived
from the archived corpus: it lists attribute NAMES read off the reference distributor's
product-page spec tables, as quoted in elastic/prism-industrial-products#103, for the
families the census does not cover (grinding wheels, bearings, valves, calipers). Names
only; no values, no products. The generator's name gate (`catalog/names.py`) accepts a
name found here or in the census.

**`P2_price_census.json` measures price** (alexander-marquardt/synthetic-industrial-products#52,
step 1). It comes from a second collection run under the same constraints: 538 requests, one
HTTP 502 and no 429s. That run read archived product-group pages, where each page lists one series
with a shown price and a sale unit per row, and end-mill item pages. It holds 5,975 priced SKUs:
14 deep types and 19 breadth categories. For each type it gives price quantiles, the log-log slope
of price against the key dimension, the share of size pairs where the larger size costs more, the
max/min price ratio between brands on the same spec, a brand price index, sale-unit (pack versus
each) figures, and the mix of price endings. Each type also carries its capture years and `n`.
Prices are nominal for their capture year, which is mostly 2015. Any type with `n` < 30 is flagged
`low_confidence`, and so is any brand spread drawn from fewer than 30 shared specs. The census
holds no page, SKU, title or brand name.

Two deep types were added later (#69): nylon-insert lock nuts (n = 100) and hex socket set screws
(n = 510), from a third run of 50 requests under the same constraints but a user agent that
carries no email address. Unlike the run above, its collector and parser are committed:
`scripts/price_census_collect.py` caches what it fetches under `raw/price_census/`, and
`scripts/price_census_parse.py` writes the two entries. Neither entry carries a brand spread or a
tier figure. Every lock nut is one label, and the only specs two set-screw brands share are nylon
ones. Each entry's `brand_spread_same_spec` says why. `MANIFEST.json`
(`P2_price_census.extension_69`) records the run and the rules the census `method` block leaves
open.

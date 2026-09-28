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
observed attribute names; that breadth is the point and is not capped.

**`R1_reference_spec_table_names.json` is a different kind of file.** It is not derived
from the archived corpus: it lists attribute NAMES read off the reference distributor's
product-page spec tables, as quoted in elastic/prism-industrial-products#103, for the
families the census does not cover (grinding wheels, bearings, valves, calipers). Names
only; no values, no products. The generator's name gate (`catalog/names.py`) accepts a
name found here or in the census.

# synthetic-ecommerce-data

Write-up: [Generating a synthetic industrial product catalog for search demos](https://alexmarquardt.com/data-generation/synthetic-industrial-product-catalog/).

![Four search results for "car" in a demo search UI: a checked car coat, a car boot organiser, and a wooden racing car in red and in blue. Every picture is a generated drawing.](docs/images/search-car-cards.png)

**The pictures are drawn by code.** Each is written straight to SVG, from the
SKU's own attributes, by a small writer in this repository: no image model and
no photographs. A drawing is deterministic and costs nothing per variant, and it
is parameterised by product type, brand house style and attributes (color,
pattern, size). Measured on an Apple M3 Pro laptop, `draw_product` drew every
SKU of `golden-catalog/` at roughly 7,000 drawings a
second (0.14 ms each, one core; three runs, 6,900 to 7,400 per second).
That times the industrial drawing step only, with the records already loaded.

A generated product catalog for the industrial-supply vertical (cutting tools,
fasteners, abrasives, hand tools, bearings), built to exercise structured facet
extraction in search: modelled depth types plus
[breadth categories](#catalog-breadth), one product each, from invented
brands -- and, with one flag, about 100K SKUs
([The 100K catalog](#the-100k-catalog); its name and figures are #62's).

The default build's figures are build output, in `golden-catalog/stats.json`:
`skus` and `lines` (per type: `skus_by_type`, `lines_by_type`), and under
`figures` the type and brand counts (`catalog`), the drawings' count and bytes
(`drawings`) and the facet rule's figures (`dispersion`).
`uv run ecom-generate build --out golden-catalog` rewrites them, and no doc
restates one (`tests/test_measured_figures.py`), so a pull request that adds a
type changes them only in the file the merge script rebuilds (#103).

**Renamed from `synthetic-industrial-products`** (#125), so that one generator
can build catalogs beyond industrial supply. The distribution is
`synthetic-ecommerce-data`, the package `synthetic_ecommerce_data`, and the
commands `ecom-generate` and `ecom-render`. For one release cycle the old names
still work and are deprecated: `import synthetic_industrial_products...`
resolves to the same modules with a `DeprecationWarning`, and `sip-generate`
and `sip-render` run the new commands after a note on stderr. The output is
byte-identical under either name.

**Layout** (#125 step 2). `src/synthetic_ecommerce_data/core/` holds the
domain-neutral machinery: the model and attribute entries, config, formats
and dimensions, brands, copy noise, titles and voice, price, emit, the image
bundle, the non-copying check, the breadth row table and the drawing
framework. `src/synthetic_ecommerce_data/domains/industrial/` holds
everything industrial: the generator, the types, vocabularies, standards,
taxonomy, figures, renderers, census measurement and data. The commands
compose a domain with core, so they stay at the top level beside `prism/`:
`generate_cli.py` (`ecom-generate`) and the per-record `cli.py`
(`ecom-render`). Some core modules still hold industrial tables next to their
machinery; every way core reaches outside itself (an import, relative or
absolute, or a module named in a string) is listed in
`tests/test_core_extraction_125.py`, and that list only shrinks. Old `synthetic_industrial_products.catalog.*`
import paths resolve to the moved modules.

**Every product in this repository is synthetic.** No record here describes a
real product offered by any retailer, and no retailer's catalog content is
redistributed.

## Why this exists

Search demos in this vertical need one specific property that is hard to
fabricate convincingly: **attribute-role ambiguity**. The same dimension token
legitimately appears in different roles on one product — a `3/8"` that is the
cutting diameter on one tool and the shank diameter on another. A query for
`3/8 end mill` matches both on full text and should return neither. Proving a
search engine handles that requires a catalog whose dimensions are internally
coherent and whose collisions occur at a realistic rate.

## Provenance

The **schema** and the **statistical distributions** are derived from observing
publicly archived pages of real catalogs: which attribute names the industry
uses, which dimension combinations are physically real, how often roles
collide, how titles are constructed, and how often records are internally
inconsistent. Those are facts about the domain.

The **products** are generated. They are not real records with the names
changed.

That distinction is enforced, not asserted: no generated record may match a
reference record on its full attribute tuple, and the test suite checks it.

The check compares **hashes** of reference attribute tuples, not the tuples.
The corpus still ships nowhere; a hash cannot be read back into a record, but
it is enough to prove the property. The comparison is over the *full* tuple
rather than field by field, and that matters: a generated `#10-32` flat head
cap screw publishes `Head Dia. = 0.411 in`, and so does every real one, because
that is what `ASME B18.3.2` says a `#10` flat head is. Agreeing with a standard
is not copying. Reproducing a compilation is, and a compilation is what a full
attribute tuple describes.

### Where the dimensions come from

Two different answers, and the catalog says which is which on every product
line:

| | |
|---|---|
| **Fasteners** | dimensions are **standards-derived**. Each line carries the standard designation its dimensions came from — `ASME B18.3`, `ASME B18.3.2`, `ASME B18.3.3A`, `ASME B18.3.1G`, `ISO 4762`, `ISO 10642`, `ISO 7380-1`, `DIN 7984`, `ISO 4014`, `ISO 4017`, `DIN 933`, `ISO 7089`. |
| **Newer types** (hex nuts, radial ball bearings, depressed-center wheels, hex keys; elastic/prism-industrial-products#103) | dimensions are **generated** from conventional sizes -- nut widths across flats, the 60/62/63 bearing series boundary sizes (ISO 15's bore, outside diameter and width per diameter series, 5 mm through 100 mm bore, checked against a table restated in `tests/test_catalog_facts.py`), stocked wheel diameters, hex key sizes. They follow the familiar ladders but were not extracted from an open dataset, so the provenance field says "generated". The one standard claimed is a hex nut's, and only where every row of its line IS that standard's row -- see [Facts a record states are real](#facts-a-record-states-are-real). |
| **Cutting tools** | dimensions are **generated** from the conventional series. No open dimensional source for end mills exists, so nothing here claims a standard, and the provenance field says so in words. The metric series carries 11, 15 and 25 mm, which are ordinary stocked sizes and were missing — an artifact of how the list was first written, not a statement about the market. |

That asymmetry is deliberate. A cap screw's head is fixed by a published
standard and a catalog that disagrees with it is wrong; an end mill's length of
cut is a manufacturer's choice within a conventional range.

Fastener dimensions were extracted from open sources rather than transcribed by
hand:

* **[FreeCAD FastenersWB](https://github.com/shaise/FreeCAD_FastenersWB)**
  (GPL-2.0-or-later) — the primary source for every standard used.
* **[BOLTS](https://github.com/boltsparts/boltsparts)** (fastener collections,
  LGPL-2.1+) — corroboration only, and the sole source for DIN 912, which
  FastenersWB does not carry. It was deliberately **not** consulted for
  ISO 10642 (it conflates that standard with DIN 7991) nor for washer inner
  diameter or thickness (it is wrong at M10 and at M42 and above), and
  `profile_hollow.blt` was never opened, since it transcribes a paid EN
  standard.
* **Unified Thread Standard** fine-series pitches (`#10-32` and its siblings)
  appear in no open dimensional dataset; the handful used are transcribed from
  Wikipedia's Unified Thread Standard table (CC BY-SA 4.0). The standard itself
  is ASME B1.1, and each entry is really its own designation — `#10-32` states
  32 threads per inch in the name.

`src/synthetic_ecommerce_data/core/standards_library/tables/fastener_standards.json` is that
extraction, unmodified apart from the library's `_library` citation block, and carries its own provenance block naming each
repository, its licence and the commit it was read at. Only the sizes this
catalog offers were taken; the upstream compilations are not redistributed.
Values the sources do not carry are recorded as absent rather than filled in —
there is no `#10` hex bolt here, because ASME B18.2.1 hex head screws begin at
1/4", and no `M20` button head, because ISO 7380-1 in the source stops at M16.

**The standards library (#73).** Every size table the catalog reads from a standard is one
JSON file in `src/synthetic_ecommerce_data/core/standards_library/tables/`, with a `_library`
block naming its `standards`, `edition`, `source` and `kind`, and a rule of its own in
`tests/test_standards_library.py`. A type reads a table by name
(`standards_library.table("asme_b1_1_unified_threads").select(["#10", "1/4"])`) and takes only
the sizes it stocks; `select` refuses a size the table lacks. A new table is a new file, never
an edit to a shared list, so two type PRs that each add one do not collide. The library moves
SIZE tables; what a type claims to conform to stays in `conformance.py` (#61).

The sizes taken are listed in the extraction's own `requested_sizes` block:
`M3 M4 M5 M6 M8 M10 M12 M16 M20` and `#6 #8 #10 1/4 5/16 3/8 7/16 1/2 5/8`.
**`7/16` was added after the reference distributor's own parametric example turned out to
name it** — `hex head cap screw: 7/16-14, 1-3/4" length under head, grade 8
steel, zinc finish` — and every other component of that query already
resolved. It is present in the source for all five inch standards, so nothing
had to be invented: the pitch column gives 14 threads per inch exactly, which
is what makes the designation `7/16-14`, and the offered lengths are the
workbench's own list filtered to the per-size range, which includes
`1 3/4in`.

### Four screw styles, and the three lengths each of them publishes

A shopper's screw query is `<thread size> ( x ) <length> <screw type>` —
`5/16-18 x 3/4 button head cap screw`, `1/4 x 3 1/4 cap screws`. Two things
have to exist in the catalog for that to have a correct answer: the style, and
the length it names.

**The styles.** Four hexagon socket screw lines, each with its own standard in
each system, its own category leaf and its own drawing:

| line | metric | inch | head |
|---|---|---|---|
| `screw_socket_head` | `ISO 4762` | `ASME B18.3` | cylinder |
| `screw_flat_head` | `ISO 10642` | `ASME B18.3.2` | countersunk cone |
| `screw_button_head` | `ISO 7380-1` | `ASME B18.3.3A` | shallow dome |
| `screw_low_head` | `DIN 7984` | `ASME B18.3.1G` | squat cylinder |

**The length.** A screw publishes two of them and they are two different
measurements (`Length under Head` was a third until #497: on every screw but a
countersunk one it repeated `Length` to the digit, so it was folded into it):

| attribute | what it measures |
|---|---|
| `Length` | the nominal length — measured **over** the head on a countersunk screw and under it on every other style |
| `Thread Length` | how much of that shank carries thread |

`x 3/4` in the reference distributor's pattern is the first of those. Binding it to
`Thread Length` would return confidently wrong results — a 3/4" screw and a
screw with 3/4" of thread on it are different products — and on a countersunk
screw binding it to `Length` is wrong by a head height. So the attribute is
published rather than approximated by a neighbour, and the drawing dimensions
it: on a flat head socket cap screw the two length dimensions on the elevation
visibly end a head height apart.

## What ships, and what does not

| | |
|---|---|
| **Ships** | the generator, the extracted standards tables, hashes of the reference tuples, and the built catalog itself — checked in at `golden-catalog/`, see [The built catalog is committed](#the-built-catalog-is-committed-in-golden-catalog) |
| **Never ships** | the reference corpus of captured pages, and the rendered drawings — both reproducible, see `.gitignore`. The drawings are rebuilt from the committed catalog into a pinned bundle (`ecom-generate images`, see [Images](#images)); `images.jsonl` records each one's sha256, and nothing else about them is committed |

## Contributing

To add a product type, or move one into its own module, see
[How to add a product type](docs/adding-a-type.md).

Merge every pull request with `scripts/merge_pr.sh <PR number>`, not the
GitHub button: this repository has no branch protection, so a green from an
older `main` can merge and turn `main` red. The script merges current `main`
in, rebuilds `golden-catalog/` and merges only when the drift, golden and seam
tests pass on that tree.
`tests/test_merge_pr.py` builds its planted worlds with `UV_OFFLINE=1` and name
resolution blocked, so it needs uv's cache (warm once `uv sync` has run in this
checkout) but not the network. When a real merge's build fails on a dropped
lookup, the script says "the build failed on the network" apart from the build
refusing the tree; rerun it.

**What a feature PR commits, and what it never commits (gen#536).** A PR commits its
sources, its tests and its docs, and the golden files its change moves in `golden-catalog/`
(`flat.jsonl`, `nested.jsonl`, `images.jsonl`, `render.jsonl`, `stats.json`, the mappings). It
never commits build output: the retail totals (`golden-retail/stats.json`), the figures page
`docs/figures.md`, the apparel decoy table `docs/retail-apparel-decoys.md` and the sneak-peek
samples and previews. They moved with every type or grocery PR, so every merge conflicted the
rest, and a merge that did not roll them left `main` red. CI builds them once per run and uploads
them as the `derived` artifact (`scripts/build_derived.py`; run it yourself, `uv run python
scripts/build_derived.py --out build/derived`, to see yours), a test reads a total with
`retail_figures.figures()` and never compares against a committed number, and the
`no-derived-files` job (`scripts/check_no_derived_files.py`) fails a PR whose tree tracks one,
naming `git rm --cached <file>`. The figures page is the `derived` artifact's `docs/figures.md`.

GitHub Actions is billing-blocked here, so run CI locally: `scripts/merge_pr.sh
--local-ci <PR number>` (the default when `GEN_LOCAL_CI=1`) runs every job of
`.github/workflows/*.yml` on that merged tree, prints each job's verdict and
log path, and refuses the merge unless all pass; no GitHub check is read. A red job
prints its FAILED/ERROR lines (up to 20) and its log is copied to
`<the directory the script says it left>/.git/ci-logs/`, so the failing test is named
without a re-run.

Install the hook types once per clone: `pre-commit install` (the config sets `default_install_hook_types: [pre-commit, commit-msg, pre-push]`; the pre-push gate runs the cheap CI jobs before review, [docs/pre-push-gate.md](docs/pre-push-gate.md)). The commit-msg hook
(`scripts/check_commit_msg.py`) refuses a message that credits an AI tool or a
bot. Its patterns are the core repository's AI-attribution family, vendored
with the commit it came from, plus this repository's additions. CI runs the
same check over every commit a pull request adds, so a clone without hooks
cannot skip it. Git's `#` help lines are skipped only by the hook, because a recorded
message keeps any `#` line it was given. Messages are folded before matching:
look-alike letters, invisible and bidirectional characters, and a phrase
wrapped across two lines are all caught. The capitalised agent-instructions file name, alone or in a path, is masked first so a commit that edits it may name it; a vendor name beside it still fails. The pre-commit hooks run `ruff check` and the whitespace
fixers, which leave `golden-catalog/` alone.

Run the test suite with `uv run pytest`. The whole suite takes about 27
minutes serially, or about 22 on two workers with `uv run pytest -n 2`
(`pytest-xdist` is a dev dependency; it needs about 4.3 GB at peak), so for a change run the modules that name what you changed, and leave the whole
suite to CI. `merge_pr.sh --local-ci` runs it on several workers, with the count capped by cores and memory ([docs/adding-a-type.md](docs/adding-a-type.md#merging-every-type-pr-goes-through-merge_prsh)); never use `-n auto` by hand on a many-core machine (16 workers took 38 GB in three minutes on the agent VM). Only some product types have a `tests/test_type_<type_key>.py` (for example `test_type_o_rings.py`, `test_type_shackles.py`); the rest are covered by shared modules such as `test_type_facts.py` and `test_type_registration.py` and by tests named for the feature. The grep finds the tests that name a type or module:

```sh
uv run pytest $(grep -l '<changed module or type key>' tests/test_*.py)
```

Every test has a 300-second limit, fixture setup included (`timeout` under
`[tool.pytest.ini_options]` in `pyproject.toml`, enforced by `pytest-timeout`).
A test that hangs, or grows its memory without end, fails at that limit instead
of holding the machine. A test that is slow for a reason raises its own limit
with `@pytest.mark.timeout(<seconds>)`; the default does not move.

## Generating a catalog

```sh
uv sync
uv run ecom-generate build --out out/catalog
uv run ecom-generate report                      # the measured-vs-target table only
```

Everything is parameterised, because the point of the catalog is to be dialled
until something breaks:

```sh
uv run ecom-generate build --lines 900               # a bigger or smaller catalog (THE size knob)
uv run ecom-generate build --sparsity 0.4             # raggeder attribute coverage
uv run ecom-generate build --defects 0.0              # a catalog with no contradictions
uv run ecom-generate build --seed 7                   # a different catalog
```

The generator is deterministic: one seed produces one catalog, byte for byte.
`scripts/check_determinism.py [--lines N] [--images]` proves it: it builds
twice, each in a fresh interpreter with a different `PYTHONHASHSEED`, and
compares the sha256 of every emitted file (the PRISM field map included, copied
out of the source tree after each build, and, with `--images`, the drawings
archive). It refuses a build that leaves any expected file missing. Measured on `a91482e` at the default size: 10 files byte-identical,
the archive included. Run it at `--lines 39000` before publishing a 100K build
(elastic/prism-industrial-products#129). It proves independence from the seed
and the hash seed on one machine; it cannot see a date-only timestamp,
filesystem listing order, locale or timezone, or the zlib build.

`--lines` is the ONE size knob. It sets the products of the original twelve
types, and the four newer types (hex nuts, radial ball bearings, depressed
center wheels, hex keys) take a fixed SHARE of it (`new_type_share`,
700/2600 each: the ratio the default catalog was built with), so every type
grows together. A breadth category deepened into a modelled type (#53, the
first is `lock_nuts_nylon_insert`) drafts its own `share` of `--lines`
(`TypeSpec.share`, 0.1) on top of the original twelve's 1.0, so each one makes
the catalog larger and moves no other type's output. There is deliberately no second `--scale` flag. The
[breadth categories](#catalog-breadth) are the one exception: one FIXED
line each, independent of `--lines`, because breadth is not depth (see that
section for why).

### The 100K catalog

```sh
uv run ecom-generate build --lines 39000 --out out/catalog-100k
uv run ecom-generate images --catalog out/catalog-100k --out out/images-100k --archive out/images-100k.tar.gz
```

`--lines 39000` (`config.HUNDRED_K_LINES`) is the value that lands at about
100,000 SKUs. Each deepened type adds its own share on top, so the build
grows with every one; #62 renames it by what it holds and generates these
figures. Measured with the first command above (about 45 s wall time), per
type from `skus_by_type` in its `stats.json`:

| type | SKUs | | type | SKUs |
|---|--:|---|---|--:|
| end_mill_square | 13,852 | | washer_flat | 978 |
| end_mill_ball | 8,110 | | hammer_ball_pein | 861 |
| drill_jobber | 7,307 | | abrasive_flap_disc | 2,460 |
| tap_spiral_point | 3,512 | | nut_hex | 12,044 |
| screw_socket_head | 7,727 | | bearing_radial_ball | 11,340 |
| screw_flat_head | 4,752 | | wheel_depressed_center | 11,495 |
| screw_button_head | 3,439 | | hex_key | 6,466 |
| screw_low_head | 2,692 | | bolt_hex | 5,934 |
| kit_assortment | 695 | | lock_nuts_nylon_insert | 4,513 |
| set_screws_hex_socket | 7,061 | | dowel_pins | 1,004 |
| cotter_pins | 803 | | retaining_rings_external | 694 |
| roller_chain | 509 | | turnbuckles | 385 |
| shackles | 373 | | pillow_block_bearings | 269 |
| roller_chain_sprockets | 200 | | roller_chain_links | 769 |
| o_rings | 1,040 | | key_stock | 965 |
| the breadth categories | 75 (1-3 each) | | | |

The mix is not the one a proportional scale would give, and that is the
uniqueness rule at work: a type whose spec space is small (ISO 7089 fixes a
washer's nine sizes; a hammer is its head weight and handle) runs out of
SKUs its makers have not already made, so it grows less. It was about 28 thousand
lines for 100K until uniqueness stopped counting metadata as a difference.

**122,324 SKUs over 70,776 products** (`skus` and `lines` in `stats.json`),
4,513 of them lock nuts over 2,714 products, 7,061 set screws over 3,786,
1,004 dowel pins over 535, 509 roller chains over 328, 803 cotter pins over
463 and 694 external retaining rings over 413 (the last two are the first
table types, #101). The next five table types add 1,996 SKUs over 1,237
products and moved no other type: 385 turnbuckles over 244, 373 shackles over
246, 269 pillow block bearings over 168, 200 roller chain sprockets over 129
and 769 roller chain links over 450. O-rings are 1,040 over 565:
`o_rings` was a breadth category of 2 SKUs; deepened from the AS568 table
(#53), it took no SKU from any other type. Key stock is 965 bars over 560
(#108, a new type with its own share), and moved none either. Bearings widened from 27 numbers to 75 (#64), so fewer bearing
lines repeat a number a maker already sells: 11,340 bearings where there were
7,516, and no other type moved. `lock_nuts_nylon_insert`,
`set_screws_hex_socket`, `dowel_pins` and `roller_chain` became deep types
(#53), each with its own share of `--lines`, as each table type has, and took
none from the others (the dowel pins', the roller chain's and the two table
types' breadth rows and their SKUs left the breadth set), so every
other type's SKU count but the bearings' is the one measured on `95a9ed0` (the set screws' small
sockets add a true sentence to some hex key copy, not a SKU), when
the build gave 99,929 SKUs over 57,985 products. On `95a9ed0`: SKUs that are
not different (the rule below): 0. Every bearing number is a real table entry
with its own bore, OD and width. Product names: 0 clashes catalog-wide.
Every must-stock example is stocked. (Those four are the 100K tests in
`tests/test_catalog_brands_voice.py`.) Since key stock,
`scripts/check_determinism.py --lines 39000`: all 7 emitted files
byte-identical across two builds. The drawings, built with the second command
above: 122,324 drawings, 261.3 MB unpacked, a 28.2 MB `images.tar.gz`, every
sha256 matching `images.jsonl` (the counts the command prints). The 100K
catalog is still not published while the spec is iterated at the default
size.

The files are far too large to commit uncompressed (`flat.jsonl` is ~330 MB).
This repository commits the default-size catalog only; the industrial demo
serves that one, from a pinned release, and the 100K build is a capability
kept tested (`tests/test_catalog_brands_voice.py` builds it) rather than a
published artifact.

What moves at 100K, measured against the census targets (`ecom-generate
report`), with the default catalog beside it:

| measured property | target | 100K |
|---|--:|--:|
| shank == cutting diameter | 0.6489 | 0.6895 |
| length of cut > overall length | 0.0829 | 0.0829 |
| angle carries a length unit | 0.0469 | **0.0000, deliberately** (#404) |
| declared system contradicts units | 0.0323 | 0.0331 |
| unit mixing within one record | 0.0222 | 0.0185 |
| title dimension token unlabelled | 0.4667 | 0.4598 |
| title names a secondary dimension too | 0.1714 | 0.1203 |
| attributes per record (mean) | 13.12 | 13.07 |

Drift, stated: every title now names its key dimension, so the census's
"token is not the primary" case is a title that names a secondary dimension
BESIDE the key one; that rate sits below its target because a title names a
secondary dimension only when the record PUBLISHES it, and the newer types
have none to name. The shank rate sits above its target because a shank is
never thinner than its cutter any more: the census's 0.833 and 0.75 ratios
become the next shank up, and above the largest stocked shank it is the
cutter's own size; and an oversize shank is at most three times its cutter,
or 6 mm under a metric cutter below 6 mm (see
[Brand voice](#brand-voice-titles-and-descriptions)). Label spellings are
quantised by brand (each brand spells a label one way), so e.g. the flute
label mix differs from the census's 0.66 / 0.28 / 0.06.

## Brands

Forty-five manufacturers, all invented, in one table (`core/brands.py`):
their product families, market weight, house style and title voice.

* **A long tail, not ten equal houses.** Three broad-line houses make
  something in every family; the rest make one to three families. At 100K the
  largest brand carries 8.0% of SKUs and the smallest 0.5%; a test pins both
  ends (at most 10%, at least 0.3%).
* **Some names contain an ordinary word** on purpose (`Iron Heron`, `Lantern
  Rock`, `Stone Wicket`, `Tin Kestrel`, `Lark & Lathe`, `Tall Mast`, `Salt
  Meadow Works`, `Wendlow Tool`, `Quillon Carbide`, ...): a brand filter has to
  tell a brand from a word, and a catalog without such a name never makes it.
* **House style.** Twelve inks, six paper tints and four frame treatments. Each
  brand owns one (ink, frame) pair, read back by
  `drawing.style.brand_for_house_style`, and its paper is chosen independently
  of its ink, so brands that share an ink also differ in background. Every
  (ink, paper, frame) triple is unique and every ink is at least 3:1 against
  its paper (the lowest is 4.4:1).
* **Brand mark** (#132). Each brand declares a `motif` and an `enclosure`
  (`core/brands.py`): fifteen machine-shop motifs
  (`domains/industrial/drawing/brand_marks.py`) in three enclosures (bare, in
  a ring, knocked out of a badge), one pair per brand. That is room for 45
  brands, exactly the book; a new motif that passes the distinguishability
  test ([Images](#images)) adds room for three more.

**Every name is invented, and each was checked.** Method: a web search for
`"<name>"` and a second for `"<name>" tools OR industrial OR company`; a name
that turned up a real company or trademark of ANY kind, in any industry, was
replaced. An independent review of the first book found twelve real names
(RolVane hydraulic motors, Ferrox Group / FEROX tooling, Vantage Tools / the
Iteris Vantage line, Tyndall Company, Halstead Machine, and Corvane, Velbrook,
Kinnerly, Orbelle, Crooked Birch, Fallowmere, Kelbrook outside industry);
re-checking all 45 the same way found twelve more (Bracknell ~ Brecknell
scales, Redmoor Ltd, Österlund, Marrow MFG, Boltrane ~ Boltra tools, Dunmere
Ltd, Nethercott companies, Emberlin companies, Quiet River companies, Plumb
hand tools, Morrow Equipment, Maddox Industries). All 24 were replaced.

| result | names |
|---|---|
| both searches clean | Dravenholt, Hollisdane, Varnstrom, Druvanholm, Estrimore, Iron Heron, Kessingmoor, Ingleward, Tervasko, Vellinhorst, Quillon Carbide, Tessaly Cutters, Orrinford, Pellanor, Varrick Precision (fictional "Varrick" only), Lark & Lathe, Rivenhall, Cobbet & Pryce, Lintmoor, Selvanock, Tall Mast, Brennavik, Salt Meadow Works, Ashcombe Forge, Pennock & Hale, Brindlecote, Lantern Rock, Quarrenby, Quennick, Lorcastle, Spindlewick (street names only), Harnell (surname only), Crennick Works |
| both clean, a similar real name exists | Kaldermark (Kalmark Integrated Systems), Wendlow Tool (Wendel tools), Tannerby (Tanner Fasteners), Grisenne (none exact; Grizzly Industrial nearest) |
| **ONE search only** (the session's search budget ran out) | Caddernook, Pellwarren, Morvennick, Braddlestow, Quellmarsh, Stone Wicket, Tin Kestrel, Ivenhoft |

## Facts a record states are real

An independent review of the 100K catalog found facts the generator had
invented; each is now read from a table and checked by
`tests/test_catalog_facts.py` against tables written out apart from the
generator's rules (a type's claimable standards and key dimension are declared
on its `TypeSpec`, or in `tests/type_facts.py` for a type still in the
shared tables):

* **Bearing ratings** are a table per bearing number
  (`newtypes.BEARING_RATINGS`): dynamic and static load and the limiting
  speed of the open bearing -- every metric row from one maker on one basis,
  SKF's deep groove ball bearing product pages
  (`skf.com/group/products/rolling-bearings/ball-bearings/deep-groove-ball-bearings/productid-<number>`,
  retrieved 2026-10-07), since two makers' speed ratings put side by side
  invert the series' order at the seam (a number SKF does not publish open,
  628, is not stocked, never patched), and within a diameter series no larger
  bore is rated higher in speed or lower in load (`tests/test_catalog_facts.py`);
  distributor listings for the inch R series -- with a contact seal at 70% of
  the open speed. No jitter: two bearings of one number are rated alike,
  whoever makes them, and a rating never makes two SKUs different. (A formula
  had put a 6000 at about three times its published rating.)
* **Standards** are a truth table by what the line IS (`domains/industrial/conformance.py`):
  a socket head cap screw may claim ISO 4762 / DIN 912 / ASME B18.3 / ASTM
  A574, a flat washer ISO 7089 / DIN 125-A, a metric radial bearing ISO 15 /
  ISO 492 / ABMA 20, and so on; a line with nothing applicable claims
  nothing. They used to be drawn from a pool per type family, so a washer
  could claim DIN 912. One spelling per designation, in the attribute and in
  the copy.
* **A hex nut claims the dimensional standard its rows ARE, or none.** A
  finished hex nut is ISO 4032 (coarse) or ISO 8673 (fine) or ASME B18.2.2
  (inch, #6 up); a jam nut takes its own standard's height -- ISO 4035 /
  ISO 8675, and B18.2.2's jam column from 1/4" -- and claims it; a #6-#10 jam
  nut keeps a derived height and claims none. A heavy hex nut's sizes are
  derived from the finished nut's, match neither ISO 4033 nor the structural
  heavy hex series, and claim no dimensional standard. The rows were checked
  against FreeCAD_FastenersWB at the commit `fastener_standards.json`
  records (`iso4032def.csv`, `iso4035def.csv`, `iso8673def.csv`,
  `iso8675def.csv`, `asmeb18.2.2.1def.csv`, `asmeb18.2.2.4def.csv`).
  The review of 7dac659 found 29 metric heavy hex nuts claiming ISO 4032 and
  53 fine-pitch nuts claiming coarse-thread standards; the check that replaced
  it found 224 wrong claims on that golden, the inch heavy hex and every jam
  nut's derived height included.
* **An inch R-series bearing claims no standard.** ABMA 20 is the METRIC
  design standard ("Radial Bearings of Ball, Cylindrical Roller and Spherical
  Roller Types -- Metric Design"), so the 112 inch bearings that claimed it
  were wrong; no inch-series designation could be confirmed from a readable
  source, so none is claimed.
* **Finish and hardness follow material and grade**: an 18-8 stainless socket
  screw is plain at Rockwell B80, alloy steel is black oxide or zinc at C38
  (12.9 at C39); the top strength grade is named on its own system's scale --
  `Grade 12.9` (ISO 898-1) on a metric socket, flat, button or low head
  screw, `Grade 8` (SAE J429, C36) on an inch one, never the reverse, which
  a whole-catalog test over every published string of every document holds
  (#17); a graded hex bolt's material follows its grade, and hot-dip
  galvanizing is kept off Grade 8 / Class 10.9 (ASTM F2329); nACo and AlTiN
  are carbide coatings, black oxide an HSS treatment.
* **An end mill's shank is never thinner than its cutter, and never more than
  three times it** -- unless the smallest stocked shank above the cutter is
  already more. 43 of the 46 differing records in
  `reference-statistics/04_shank_dia_vs_milling_dia.json` are at or under
  3.0x, the 2.667x and 3.0x ones included; the census's 4.0 ratio had put a
  5/32" cutter on a 5/8" shank. A metric cutter below 6 mm with an oversize
  shank sits on the 6 mm DIN 6535 shank, whatever the ratio (1 mm on 6 mm is
  6.0x). That is a catalog convention the #33 review proposed, not yet
  confirmed against a standard's diameter table (#87); it leaves the
  3, 4 and 5 mm DIN 6535 shanks undrawn for an oversize cutter. Under the
  earlier 2x cap, 48 of the 54 such cutters on a2a55cc's golden sat on another
  shank, most of them on 3 mm. Above the largest stocked shank the shank is
  the cutter's own size.
* **A terse end mill title names the mill's own end**: `SGL Sq End` on a
  square end mill, `SGL Ball End` on a ball nose one (168 of 568 ball end
  mills said `Sq End`).
* **Every title names the type's key dimension** -- the thread size of a
  fastener, the size of a hex key, the cutting diameter of an end mill or
  drill, the bore and number of a bearing -- and a (brand, type) fixes its
  title style ONCE (key bare, key labelled, or key labelled plus a labelled
  secondary dimension). A secondary-style (brand, type) ranks the secondary
  dimensions once and each title names the first its record publishes, so a
  title names one whenever its record publishes one. The census mix is
  reproduced ACROSS a type's makers by market weight: 0.456 unlabelled and
  0.122 secondary against the census's 0.467 and 0.171.

## Every SKU is different

**No two SKUs may be identical on (product_type, brand, every attribute),
ignoring the identifier fields (sku, product_id, List Number, image ids and
urls) and the commercial fields (price, stock). Brand counts as a difference,
so the same standard part from two different makers is allowed.** Two SKUs
that differ only in that one LACKS an attribute the other publishes (a
sparsity drop) are NOT different either. What counts is SUBSTANCE:
the measurement-system attribute (three spellings of one fact about the
record's units) and the standards claimed are metadata and never make two
SKUs different.

How it is held: a **membership check, i.e. rejection**, at the moment a SKU is
made. A draft SKU is not made when its UNSPARSIFIED spec (every attribute the
builder drew, before sparsity) is one its brand already made for the type, or
when its published spec is a subset or superset of one already made. When a
(type, brand) drafts 20 lines in a row that make nothing, its spec space
counts as spent and that brand stops getting products of that type
(`MAX_MISSES`); at 100K 114 (type, brand) pairs reached it and 52,830 draft
SKUs were rejected over the whole build. Washers come in five materials, each with the finishes
it is really sold in, and ball pein hammers in twelve head weights and four
handles, which keeps rejection rare. The series walk that keeps product names
unique renumbers only the series and `List Number`; a value that carries
meaning (a bearing number) is never touched, and a test holds every bearing
to its table entry. `tests/test_catalog_brands_voice.py` asserts zero
not-different pairs on the committed catalog and on a fresh 100K build, with
planted duplicate and planted-drop cases that go red. Distinct specs over
SKUs ACROSS brands, per type, at 100K (identical parts from two makers are
allowed): flat washers 0.15, hammers 0.72, bolts 0.76, flap discs 0.79, kits
0.84, hex keys 0.88, nuts 0.90, every other type 0.93 or more.

## Brand voice: titles and descriptions

A brand's catalog section reads uniformly, and two brands read slightly
differently (`core/voice.py`).

* **The title's core is the census structure** -- `<Item>, <key dim> <role>,
  <material>, <coating>, <flutes>...`. A type whose variant axis is not its
  size still names its key dimension (`KEY_DIMENSIONS`): a bearing its bearing
  number, a wheel and a flap disc their diameter. A brand's template chooses
  only among census-observed variants and adds words AROUND the core: a
  non-factual qualifier or the brand's name, and a trailing pack segment.
* **Pack wording is allowed only where a pack field exists.** The maintainer's
  ruling: pack wording is fine when the record actually carries a pack field.
  `Units per Pack` (the census's `Package Quantity`) exists on hex nuts and depressed-center wheels, and every
  pack word in a title or description equals that field; no other type
  carries pack wording.
* **Pricing unit and order multiple** (gen#14) are two plain fields on every SKU, `pricing_unit`
  (`Each`, or `Per Pack` when the record publishes a `Units per Pack` above 1) and
  `order_multiple` (1: a pack is ordered whole). They are not variants and not facets. The second
  variant axis (a sparse set of packs per size, a SKU and an image for each existing pair) is the
  rest of gen#14 and is not built yet.
* **Descriptions** keep the spec clause and add the brand's template: a use
  line true of every product of the type, a family line naming the brand, its
  range and series, a generic benefit of a material or finish the record
  carries, and a pack line with the record's own quantity.
* **No text states what the record cannot back.** Every number in a title or
  description traces to a value the record publishes (records carrying a
  MODELLED defect are excused, bounded at 2%) -- except the one
  cross-reference sentence below, whose numbers are the OTHER product's and
  trace to a standard's table instead.

## Cross-references and near-miss threads

A size query on a real distributor is ambiguous: `m12 socket cap screws` also
matches the hex key that drives an M12 socket head, the M12 nuts and washers,
the M12 taps and the drill that makes an M12x1.75 hole. The facets are what
separate them. A catalog whose text named only each product's own attributes
answered every size query with one product type on its words alone, and the
facets had nothing to do. Two changes make the search realistically ambiguous
without stating anything false (`domains/industrial/compat.py`):

* **One cross-reference sentence**, in the description AND in the searchable
  `text`, never as an attribute (a hex key does not acquire a thread size, so
  the text match brings it in and the facets take it out). Each is read from a
  table, about the record's own PUBLISHED value, and written only when that
  value is exactly a table entry:

  | type | sentence | table |
  |---|---|---|
  | hex key | `For M12 socket head cap screws (ISO 4762).` | the key-to-screw table read from the extracted ISO 4762 / ASME B18.3 rows |
  | socket screws | `Takes a 10mm hex key.` | the screw's own `Drive Size` |
  | tap | `For M12x1.75 threads; tap drill 10.2mm.` | the metric chart (D - P to the stocked tenth) and the Unified 75%-thread chart |
  | jobber drill | `Tap drill for M12x1.75 threads.` | the same charts, read backwards |
  | hex nut | `Fits M12x1.75 bolts and screws.` | the nut's own thread |
  | flat washer | `For M12 bolts and screws.` | ISO 7089's sizes |

  A value the table does not have (a 1.5mm key: the extracted rows start at
  M3) gets no sentence. `tests/test_compatibility_text.py` checks every
  sentence against tables written out from the standards in the test itself,
  and against the record; a planted wrong sentence reds.
* **Near-miss threads.** A diameter that has fine pitches is built to one on
  every third socket-screw line of that size and every fifth hex-bolt line
  (five, because the bolt's finish wheel is three long and would otherwise
  alias): ISO 262's M8x1, M10x1.25/1, M12x1.5/1.25, M16x1.5, M20x1.5/2 and the
  Unified fine series. Taps and hex nuts come in a fine-pitch range a quarter
  of the time. A fine metric socket screw keeps its standard's head but claims
  no standard (ISO 4762 and its siblings are coarse-thread standards); a fine
  metric hex bolt is ISO 8765 / ISO 8676 / DIN 961. Every published thread is
  a real designation and its `Thread Type` says which series it is.
* **Metric drills.** A third of the jobber-drill lines are metric (DIN 338
  sizes, with the tap-drill sizes a distributor stocks), and the fractional
  series is the full 1/64 progression -- a tap-drill chart names 10.2mm and
  27/64", and a catalog of 1/32" steps had no such part.

* **A metric designation is searchable by its diameter.** `M12x1.75` is one
  token to the standard analyzer, so the searchable `text` also carries `M12`
  beside it; without that, `m12 socket cap screws` reached the hex keys whose
  copy names M12 screws and not a single screw.
* **A glued size is also written in its parts, in the description**
  (#33). Wherever a title or description glues a size, the description
  writes it out too: the record's own sizes as `M12 thread, 1.75 mm pitch`
  in the spec clause, and a size a sentence names for another product in
  brackets after it -- `Tap drill for M12x1.75 threads (M12 thread, 1.75 mm
  pitch).`, `Also available in M8x1.25 / M10x1.5 sizes (M8 thread, 1.25 mm
  pitch; M10 thread, 1.5 mm pitch).` On the golden before this change, 1,930
  records glued a size their description never wrote in parts, and the
  jobber drills whose only M12 was the tap-drill sentence were not returned
  for `m12`. `tests/test_glued_thread_sizes.py` reads the description's
  tokens with its own pattern, and checks that every part written stands
  beside a size the record glues.

## Copy noise

A distributor's copy mentions sizes a product does NOT fit, the siblings it
is also sold in, the unit a shopper might have typed, what it pairs with and
what it cuts. Every one of those words is searchable, so a query matches more
than the products it names, and the policies and facets are what narrow the
page back down (`core/noise.py`). Every sentence is TRUE of its record --
read from its own published values, its siblings, or a table -- and the
attributes are never touched, so the facets can always separate the noise out.

| type | example | from |
|---|---|---|
| negative fit | `Not for M10 or M16 threads.` / `Will not fit 5/32" sockets.` | the neighbouring diameters; the next smaller key |
| siblings | `Also available in 3/16" / 7/32" sizes.` / `Also available in M12x1.25 sizes (M12 thread, 1.25 mm pitch).` | the product's other SKUs, on its variant axis |
| unit equivalent | `12mm (approx. 15/32").` | the published value, to the nearest 64th or 0.1mm |
| fit / pairing | `Bore 11.992-12.000mm (ISO 492 Normal class).` / `Pair with M12x1.75 hex nuts and a 10mm hex key.` | ISO 492 bore tolerances; the record's thread and drive |
| material contrast | `Zinc-plated steel (not stainless).` / `18-8 Stainless Steel (not plated).` | the record's material and finish |
| work material | `Suitable for aluminum, brass and mild steel.` | what the tool's material cuts, by common practice |
| standards | `Equivalent to DIN 912 / ISO 4762.` / `Higher strength than Class 8.8.` | same-dimension standards; ISO 898 / SAE J429 grades |
| application | `For use with socket cap screws.` | hex keys |

**One knob:** `GeneratorConfig.noise` (`--noise`) scales every rate; 1.0 is
the realistic default and 0 a clean catalog. Each record draws from its own
stream (catalog seed + SKU), so the clean and the noisy build have IDENTICAL
attributes and titles, record for record -- `tests/test_noise_text.py`
builds both and compares. **Unit equivalents are held to a minority**:
15-20% of the records that could carry one (measured 18.0% on the golden,
1,043 of 5,792),
because the facets expand units themselves and a result should show the facet
working, not text luck. Every sentence type has a checker in that test
against tables written out there, a planted false sentence reds, and five
mutation rows prove the checks bite.

## Assortment kits

`kit_assortment` is a seventeenth product type: ONE SKU per kit, its
contents a multi-valued field of its own (`Sizes Included`), its piece count
a real number (`Piece Count`, the census's `Number of Pieces`, so pack wording may name it), never
sharing a product id with the individual parts. The sets are the
conventional ones -- ISO 2936 and ASME B18.3 hex key sets, fractional
(29/21/13-piece) and metric jobber drill indexes, socket head cap screw
assortments and tap sets -- and a set is not a grouping of the parts: a
grouped product sells its sizes as separately purchasable variants, a kit
sells them together as one item. So some hex key sizes are sold only in a set
(0.7, 0.9, 1.3mm; 0.028", 0.035"), some only singly (12mm), most both, and a
test holds all three to non-empty. A kit's title says what it is ("Socket
Head Cap Screw Assortment Kit, 240 pcs", "Hex Key Set, 9 pcs"); its `Item`
is the one facet value "Assortment Kit" and its kind is `Type`. 59 kits on
the default build, 695 at 100K. A kit's price is its contents' price times
one fitted factor, its material and its tier ([Price](#price)).

Two derivation artefacts went with it: the drive size is published as the
nominal key (`10mm`), not the extracted socket's toleranced across-flats
(`10.07mm`), and the countersunk screw publishes no length under the head -- it
is sold by its length over the head, and length-less-head-height put 12.56mm
and 1.3910" beside the stocked lengths.

Measured, reported rather than forced. Product names are unique catalog-wide.
SKU titles are 0.58 distinct at 100K (0.45 before the key-dimension fix);
identical titles across products are the same spec from brands whose template
omits the brand name. Per type at 100K, before -> after the key-dimension
fix: bearings 0.01 -> 0.28, wheels 0.06 -> 0.38, flap discs 0.22 -> 0.53;
hex keys (0.18) and drills already name their size and are left alone (drills
are 0.57 since the metric sizes and the full 1/64 series were added).
Descriptions are 1.00 distinct.

### The data model

**A parent is one product. Its children are its purchasable variants (SKUs).**
The shape is core's nested variant model (elastic/prism#9141): today's ungrouped
view serves one document per SKU, and the grouped view will serve one per
product with its variants nested, from the same data.

```
parent    Dravenholt K663 -- High Speed Steel Square End Mill
          product-CONSTANT attributes: brand, series, material, coating,
          flute count, end type, helix angle
children  the SKUs, varying: milling diameter, length of cut, overall
          length, shank diameter, price, stock -- each with its own drawing
```

**How many variants a product has** is ONE knob, `variants_per_product`: about
half of products are single-SKU and the rest have 2 to 5, skewed small, as on a
marketplace (maintainer, 2026-09-27). A product never offers more variants than
its series has members. Two deliberately awkward cases are built in, so a
grouped view is proven on more than the well-formed shapes: a single variant
that carries **no** variant-scope attribute (`zero_axis_share`), and variants
whose sparsity leaves one without an attribute its siblings carry.

**Attribute names are the census's generic ones.** A concept is one name across
types -- `Material` on an end mill, a drill and a screw alike -- because that is
how the reference census names it (160 of 496 records), and on a nested index
every per-type spelling would be a facet of its own. `domains/industrial/names.py` is the
gate: every name is census-verbatim, on the names-only reference spec-table
list (`reference-statistics/R1_reference_spec_table_names.json`), or a justified
exception. No name may contain the record's OWN product noun, a noun of its
category path, anywhere (`End Mill Material` on an end mill, `Hex Nut Material`
on a nut, `Cap Screw Type` on a screw). The census's own one-record
type-qualified names are refused, not allow-listed. A noun naming a mating or
contained part is allowed, because it is a different measurement: a washer's
`For Bolt Size`, a tap's `Drill Size`, `Insert Screw`. And no name may be a
census name in another casing (`Length Under Head` for `Length under Head`),
since a keyword facet is case-sensitive. It replaced a rule that forced the
vocabularies to be disjoint.

**The newer types spell lengths the way their brand's feed does** -- one brand
`3/8"`, another `3/8 in`, another `0.375"` -- consistent within a brand and
different across brands, the variation between supplier feeds the census
records (maintainer ruling, 2026-09-28). The original twelve keep one spelling.

Attributes are nested key-value at **both** levels, in **one** array rather
than separate keyword and numeric arrays. Each entry follows the data contract
of elastic/prism#9935:

```json
{"key": "milling_dia", "name": "Milling dia.", "value": "3/8", "unit_code": "INH", "value_canonical": 9.525}
```

* `key` is required: the machine name the Engine discovers an attribute by,
  namespaced as `attr_<key>` when it is a column's name (see below). It is
  `sanitize(name)` unless the type declares its own: a roller chain's `Pitch`
  (the distance between pin centres) has the key `chain_pitch`, apart from a
  metric tap's `Thread Pitch` (its thread pitch), whose key is `thread_pitch`.
  One quantity has one display label and two quantities never share one, so a
  name has one key catalog-wide. So read `key`,
  never derive it from `name`. `name` is the display name.
* A **measured** value is fully split. `value` is the bare magnitude with no
  unit marker and no thousands separator, `unit_code` (UN/CEFACT: `INH`, `MMT`,
  `FOT` for a chain's length in feet,
  `DD`, `ONZ`, `LBR`, `C78`, `RPM`, `TPI`, and `C62` for a count) is the only
  place the unit lives, and `value_canonical` is the magnitude in the kind's
  canonical unit (millimetres, grams, degrees, one, rpm, pound-force), computed
  exactly and rounded to a float once.
* Thread spacing is published under two keys, as real catalogs publish it: a
  metric tap's `Thread Pitch` (`thread_pitch`, `MMT`, `0.5`) and an inch tap's `Threads per
  Inch` (`threads_per_inch`, `TPI`, `32`). `TPI` is a LENGTH written as a count
  per inch (ruled on elastic/prism#9877): `value` stays the count and
  `value_canonical` is the pitch in millimetres, `127/5 / n`, so `32` TPI is
  `0.79375` and `20` TPI is `1.27`. `13` TPI (127/65 mm) does not terminate and
  is the nearest float, like `3/8"` (9.525 mm). The contract test reads each
  unit's kind and size from a pinned copy of the industrial deployment's
  `canonical_units` block (`tests/data/industrial_canonical_units.yaml`; see
  [The pinned unit declaration](#the-pinned-unit-declaration)). No key's
  measured entries mix quantity kinds, with no exception, checked on a fresh
  SMALL build, a fresh default build and the committed golden (#79).
* Anything else stays unitless text, including composite designators such as
  `1/4-20` and `M10x1.5`.

The split is **read back out of** the published string, never computed from
the generator's magnitude, so the two can never disagree: `3/8"` has no exact
two-decimal millimetre spelling, and a number computed from the original
magnitude would quietly differ from the string actually published. The mark
decides the unit and nothing repairs it, so a value of the wrong kind for its
key would show: the generator writes none (#404). It used to write inch lengths
(`2"`, `1-5/8"`, `42"`) under `point_angle` and `helix_angle`, 963 rows on one
load, where a facet offered them beside `118` and `135`; a real retailer would
fix that row, so the step is gone and `tests/test_no_wrong_kind_values_404.py`
holds every angle key to angles, in the flat spelling and in the nested entry,
over a sample of every product type at the measured defect rates and at their
ceiling. The flat `facets_num` carries the same number as the nested entry,
taken from the same rule (`entry.split`) (#120). An attribute that
is not a measurement omits `unit_code` and `value_canonical` rather than
carrying nulls.

A nested entry therefore carries **no published spelling**: `3/8 in.` and
`1,070 lbf` live once, unchanged, in the flat document's `facets`. A consumer
that prints the spelling -- the drawing bundle's card stamp, the contact sheet,
the tests that compare a title with its attributes -- reads it from
`flat.jsonl`, joined on `sku` (`catalog.entry.published`), so every such
consumer is given `flat.jsonl` beside `nested.jsonl`. A test holds that the
join accounts for every flat value and that each spelling, read by the test's
own parser rather than by `split()`, gives exactly the nested entry's
magnitude, unit and `value_canonical`; a bare number takes its unit from its
key, never from the entry. A hand-worked table of published spellings pins
`split()` itself, so `1/2"` published as `0.5` is red even in a catalog
regenerated from that broken split.

Products are never grouped across brands. Two manufacturers' tools at the same
nominal geometry are different products.

#### Three tiers say what makes a SKU different

A shopper meets one product line as a screenful of near-identical cards, and
what separates them has to be legible at three different depths. The source
this catalog is modelled on does exactly this, and the three tiers carry
deliberately overlapping content:

| tier | job | content |
|---|---|---|
| `title` | tell them apart **at a glance** | the one main distinguishing attribute |
| `description` | tell them apart **while scanning** | the distinguishing attributes, with context |
| attribute block | tell them apart **precisely** | every published attribute |

```
sku          7159421039
title        Druvanholm Hex Head Bolt, 1/2-13 Dia./Thread Size, 1-1/4" L, Grade 5
description  Druvanholm Hex Head Bolt, 1/2-13 Dia./Thread Size, 1-1/4" L, Grade 5
             - 1-1/4" Thread Length, 3/4" Width
             Across Flats, 11/32" Head Height, 3/4" Head Dia., Druvanholm
             ASMEB18.2.1-78. ...
```

**The description opens with the title verbatim and then continues after a
` - `.** That repetition is the source's own convention rather than something
to tidy away — a marketplace listing repeats its size in the title, in the
variant selector and twice in the specification table, because each tier is
read at a different moment.

Two properties are asserted over the whole catalog, derived from the data
rather than spot-checked:

* **no two SKUs within a product line share a title, and none share a
  description.** Measured before this existed: 176 of 500 lines published a
  title two of their SKUs shared, over 1,214 SKUs, and *all* 500 published one
  description for every SKU under them — the description was the line title,
  which restates the brand, the series and the product type and says nothing
  about the SKU;
* **every title names a value that is that SKU's alone within its line**,
  per attribute rather than per value, since the same string legitimately
  appears on two SKUs in two different roles — and as a VALUE rather than as a
  substring of one, because `…, 1/4-20, …` is not a statement that the screw
  is 1/4" long.

The second is the one that bites, and the two weaker ways of asking it both
leak. Titles carry the brand about a third of the time and their labels in one
of several abbreviations, so on the catalog this replaced, asking only that a
line's titles differ as whole strings left **about 1,900** SKUs naming nothing of
their own, and a bare substring test left 19 more of them passing on a
coincidence rather than on a value.

The coincidence outlives a catalog that has otherwise been repaired, which is
why the distinction is worth a rule rather than a remark: on the first pass at
this work the whole-string and substring counts had both reached zero while the
standalone-token count was still **10**. One of the ten was
`Button Head Socket Cap Screw, 1/4-20, Alloy Steel`, credited with naming a
length of `1/4` (then published as `Length under Head`) — which is the first half of a thread designation
and says nothing about how long the screw is. On the committed catalog all
three counts are zero.

Which attribute is "the" distinguishing one is **derived, not listed per
product type**: it is the attribute published on every SKU of the line, with
pairwise distinct values, whose magnitudes spread furthest. For an end mill
that is the cutting diameter, which its titles already carried — so the
end-mill titles are unchanged, which is the control for the whole rule. For a
screw it is the length, and a screw's thread size is line-constant, which is
why a title built around it read the same on every SKU of the line.

### Two shapes, one catalog

`ecom-generate build` writes both serialisations from the same generated
objects, so any difference between what they return is a property of the shape
and not of the data.

| file | shape |
|---|---|
| `nested.jsonl` | parent + nested SKUs + nested key-value attributes. The target shape: the only one in which "how many *products* have this value" is answerable, via `reverse_nested`. |
| `flat.jsonl` | one document per SKU, attributes denormalised. Loadable today. Its attribute array is a plain `object`, so `name` and `value` become two independent multi-valued fields and the correlation between them is lost. |
| `render.jsonl` | the same SKUs in the shape `ecom-render batch` already reads, for the per-record dimensioned renderer. The catalog's cards do not use it: every product and variant carries an `image_id` naming its own product line's drawing. |
| `images.jsonl` | one row per image — one per product line — with its product type, the shape it is drawn as, its path under the image base URL at both profiles, and how many products point at it |
| `stats.json` | what was generated, measured against the statistics it reproduces |

Both shapes publish a SKU's own `description` beside its `title`. The line's
title ships too, as `parent_title` — it is what a grouped card will be headed
with — but it is no longer what renders under a SKU's title.

The flat shape also carries a sanitised `facets` object, because `Milling dia.`
cannot be an Elasticsearch field name — the trailing dot makes it an invalid
path. The three spellings of the measurement-system attribute deliberately
sanitise to three different keys rather than being folded into one: folding
them here would hide the problem a field map exists to solve.

## Catalog breadth

alexander-marquardt/synthetic-ecommerce-data#34: the 20 depth types give
this catalog DEPTH -- hundreds of products in each -- but not BREADTH. A
comparison the issue makes: a real industrial storefront returns 51 items
across 9 categories for `1/2 ball` (tooling balls, rubber balls, ball stock in
three materials, gage balls, ...); this catalog's twelve original types return
488 across 3 (ball end mills, ball-end hex keys, radial bearings), because
description noise (above) adds hits WITHIN a type and cannot add a category.

**One row per breadth category, 1-3 SKUs each, one generic loop.** Most rows
are in one table, `src/synthetic_ecommerce_data/domains/industrial/data/breadth_categories/`,
one file per row so two pull requests never edit the same file; a type in
its own module declares the same row there (`ball_stock_precision`, see
[How to add a product type](docs/adding-a-type.md)). For each row: a category path, a shape name, an item noun, 3-5
line-scoped attributes with short value lists, one size (variant) attribute,
and a one-line reason naming the customer query it joins. `domains/industrial/breadth.py`
turns a row into a product line, reusing the catalog's brand machinery
(`brands.pick_brand`), its description grammar
(`Generator._build_description`) and its noise generator (`noise.sentences`)
exactly as the depth types do -- but NOT its sparsity, defect injection or
`Standards` claim: every declared attribute is always published, and no
breadth SKU ever claims a false spec. There is no per-category code: adding,
changing or removing a row is the whole change.

**Titles are short and realistic**, not the depth types' multi-segment census
grammar: `<descriptor> <item>, <size>` (`Stainless Steel Ball, 1/2 in`,
`Hex Bar Stock, 1/2 in`) -- close to what plain BM25 text matching favours,
which is deliberate (maintainer, 2026-09-30): with policies off this can pull
a breadth SKU toward the top of a query it only loosely matches; with policies
on, the filters move it back out of Best. That gap is the demo case breadth
exists to make visible, not a defect to hide.

**Marked, and cheaply removable.** Every breadth SKU carries a TOP-LEVEL
`spec_quality: "fast_and_cheap"` (the depth types carry `"realistic"`),
alongside `dimension_provenance`. Deliberately NOT a nested attribute: a
nested attribute becomes a facet and searchable text on the industrial
deployment, and this marker must be neither -- it is a maintainer removal
handle, not something a shopper filters on. Emptying the breadth rows
(the YAML table's and the type modules') removes every breadth SKU and nothing else
(`tests/test_breadth.py` proves it); nothing else in the generator
constructs a `fast_and_cheap` line.

**Drawings are six fixed plain shapes**, not dimensioned per SKU -- see
[Images](#images) for why and how.

**Exempt from the realism truth tables and mutation rows**
(`tests/test_catalog_facts.py`, `tests/test_sku_drawings.py`): those check the
depth types' materials, finishes, hardnesses and titles against reference
tables built from the census this catalog otherwise reproduces, and breadth's
short value lists were never measured against it.

This round is the GENERATOR only. Hiding facets carried by too few results,
re-pinning releases, re-deriving the CI subset and the customer-facing
requirement-query before/after tables are the industrial side
(elastic/prism-industrial-products), a separate round.

## The retail prototype

The retail prototype's reference (planted distractors, footwear, grocery, the failure-class proofs, the output standard and the retail export, the merchandising score, variant axes, and the retail catalog at a size with the per-type listing) is in [docs/retail-prototype.md](docs/retail-prototype.md).

## The built catalog is committed, in `golden-catalog/`

`ecom-generate build` is reproducible, but its output is checked in anyway, at
`golden-catalog/`:

| file | |
|---|---|
| `flat.jsonl` | about 30 MB — one document per SKU |
| `nested.jsonl` | about 18 MB — one document per product, nested variants and key-value attributes |
| `render.jsonl` | 2.1 MB — the original twelve types' SKUs, for the per-record dimensioned renderer |
| `mapping.flat.json`, `mapping.nested.json` | the Elasticsearch mappings for each shape; the nested one maps `attributes.value` with a `value.normalized` keyword sub-field (lowercase + asciifolding) for Prism's `value_normalized_field` (elastic/prism#10648) |
| `images.jsonl` | 4.0 MB — one row per SKU drawing: its path in the bundle, its URL, the sha256 of its bytes |
| `authored_names.json` | 16 KB — per product type, each attribute's published sentence-case name beside the name its type authored; the image bundle rebuild reads it ([One letter case](#one-letter-case-for-names)) |
| `stats.json` | the measured defect rates, and the config that produced them |

About 45 MiB in the working tree. **Plain NDJSON — deliberately not gzipped
and not git-LFS.** The whole reason to commit generated output is that a
change to the generator shows up as a readable diff in review, and both of
those hide it. Records drawn from one naming grammar pack small. Above roughly
30K SKUs a file outgrows what GitHub accepts; the ruling for that size (D5 on
elastic/prism-industrial-products#103) is a pinned release asset, which is how
the industrial demo serves this default-size catalog that way; [the 100K
catalog](#the-100k-catalog) is built on demand.

It also means the catalog is inspectable, and citable, without installing the
generator: a reviewer reading a PR, or anyone asking what a record actually
looks like, opens a file rather than running a build.

### One letter case for names

Every category node and every attribute display name is **sentence case**, industrial and
retail alike (gen#499): `Handle material`, `Bore dia.`, `Hose, tube, fittings & valves > Seals &
gaskets > O-ring seals`. One normaliser, `core/letter_case.py`, runs at export on the finished
document (`emit.nested_document`, `emit.flat_documents`, retail's `export.standard_document`);
the authored literals are not edited. A machine `key` is never touched, and neither is a value.

A word keeps its capitals when it is an acronym (`ER`, `RPM`, `(UK)`), carries a digit
(`AS568`), has a capital inside it (`iPhone`), is a lone capital letter (`T-slot`, `V-belts`),
or is on the exception list, `letter_case.PROPER_NOUNS` (a trade name or a brand: `Torx`, `Nike`,
`Apple`). Add a word there with its reason. `tests/test_letter_case_499.py` fails when a category
node or a display name in either build or in `golden-catalog/` is not its own sentence-case
form, or when one key carries two display names.

The drawing code looks an attribute up by the name its type authored (`r["Milling Dia."]`), so
`ecom-generate build` also writes `authored_names.json` and `core/bundle.py` reads the drawing
input back through it: a drawing is the same bytes, and `images.jsonl` keeps its digests. A
consumer that matches on a display name or a category path (a policy, a vocabulary seed) reads
the sentence-case form.

### Regenerating it

```sh
uv run ecom-generate build --out golden-catalog
```

That is the whole command — the default configuration, the default seed. Then
commit whatever changed, `src/prism_synthetic_industrial/data/field_weights/`
included, since the same build regenerates the PRISM field map.

**You are expected to run it in the same commit as any generator change that
moves the output** — a new attribute, a changed distribution, a different image
assignment, a renamed field, a new emitted file. `tests/test_catalog_golden.py`
compares every committed file against a fresh build by sha256 and fails naming
the file and the line counts, so the CI red tells you which one you forgot.

Do **not** regenerate to make that test go green without reading the diff.
Two different things turn it red, and only one of them is fixed by committing:

* **you changed the generator** — expected; regenerate, commit, review the diff;
* **the generator became nondeterministic** — a bug. One seed is supposed to
  produce one catalog, byte for byte.

Tell them apart by building twice into two fresh directories and diffing those
against each other, with no edits in between. Clean means the first; any
difference means the second, and the golden files must not be updated until it
is found. The test's failure message says all of this too, with the commands.

Alongside the hashes, the same test asserts the headline numbers directly
against the committed files — as many SKU documents and distinct
`product_id` values as `tests/catalog_size.py` expects, a non-empty
`image_url` and `image_detail_url` on every product, variant and flat
document, and nested products whose variant counts sum to the SKU count.
The expected counts are the modelled types' measured figures plus each
breadth row's own, read from the rows, so adding a breadth type edits no
pinned number. Those hold independently of the generator, so a careless
regenerate-and-commit from a broken build is still red.

## Every requirement example is stocked

The search requirements the catalog is used against come with example
queries, and each one must find a product that exists: an example judged
against an empty result proves nothing about the search. So the generator
carries a **must-stock list** (`domains/industrial/muststock.py`, maintainer ruling on
elastic/prism-industrial-products#103): one entry per requirement example, naming
the product type(s) it may be and the published values a SKU must carry --
`Milling Dia.` `1/2"` with `Length of Cut` `1"`, a `bolt_hex` in `7/16-14`
with `Length` `1-3/4"`, `Grade 8` and `Zinc Plated`, and 22 more.

It runs after the main generation and changes nothing the main generation
drew. For each entry no SKU already satisfies, it builds lines with that
type's own builder -- so titles, names and derived dimensions follow the
same rules as every other line -- from a stream seeded by the entry alone,
until one carries a matching SKU, and adds that line whole, with the 1-5
variants its builder drew. Where the builder's series cannot reach an
example (the end-mill length-of-cut multiples are 1.5x, 3x and 4x, and
`1/2" x 1"` is 2x) the entry pins that one choice for its own lines.
On the committed catalog 19 of the 24 examples were already stocked and 5
lines were added. `tests/test_catalog_must_stock.py` asserts every entry is
stocked, that removing an entry unstocks its example, that the pass moves no
earlier line, and that an entry no builder can reach fails the build.

## Serving it with PRISM

`src/prism_synthetic_industrial/` is a PRISM customization that serves the
**flat** shape. The package name is fixed by PRISM's loader, which globs
`src/prism_*/data/customization.yaml` and requires exactly one match.

Flat, not nested, because the Engine cannot emit nested facet queries today.
That is also what makes this the demo's "before" half: the shopper sees one
product row per SKU.

```sh
# 1. build the catalog and regenerate the field map from it
uv run ecom-generate build --out out/catalog

# 2. load the flat shape into a LOCAL TEST cluster
python scripts/load_prism_catalog.py --host http://127.0.0.1:9201

# 3. from a PRISM checkout, with this repo installed (`uv pip install -e <here>`)
PRISM_CUSTOMIZATION_PATH=<this repo> PRISM_RUNTIME_MODE=dev \
  PRISM_ELASTICSEARCH_URL=http://127.0.0.1:9201 \
  uv run prism-engine validate-customization
```

### The field map is derived, never written

The catalog publishes **about 90 distinct attribute names** across its depth
types and breadth categories. A hand-maintained list of that many
declarations drifts from the generator the first time either side moves, and
it drifts *silently*: a field map naming an
attribute the catalog no longer publishes does not raise, it just stops
faceting, and "no product has that value" looks exactly like "the field map is
wrong".

So `data/field_weights/synthetic_industrial_flat.yaml` is **generated** from
the emitted documents, as a step of `ecom-generate build`, and
`tests/test_prism_field_map_drift.py` fails if the committed file and a fresh
derivation disagree. Editing either side alone reds it; both directions are
planted in `scripts/mutations/` (run by `scripts/mutation_check.py`).

### Which attributes become facets

Not all 94. Three measured gates, applied to the emitted documents:

| gate | rule | why |
|---|---|---|
| **discriminating** | at least 2 distinct values | a facet with one value cannot narrow anything — it is a control that does nothing |
| **characteristic** | present on ≥50% of the documents of the product types that publish it *at all* | the denominator is per-attribute: an attribute carried by one of twelve types can never exceed ~10% of the catalog, yet may be the primary facet for its own category |
| **not an identifier** | not one the generator declares a part code (`List Number`), and a **terms** attribute's values repeat across products: fewer than 0.5 distinct values per distinct (product, value) pair, or fewer than 250 distinct products to judge by | the generator knows `List Number` is a part code, so the field map reads that rather than measuring it: its 9,000-code pool would read as a facet from about 62,000 lines. For everything else, a ratio, not a count, so a ladder stays a facet however large the catalog grows: `Thread Size` repeats each of its values across dozens of products and is the first thing a shopper filters on. An absolute cap of 25 values withheld `Thread Size` and `Standards` once the catalog grew (#31). The floor counts products because a kit lists a dozen sizes on one product, and at 250 no decision moves between `--lines 200` and `39000`. Numeric attributes are exempt: a measured quantity is not an identifier at any cardinality |

An attribute is **numeric** (a range facet over `facets_num.*`) when ≥50% of
the documents publishing it carry a parsed number in `facets_num`, and **terms**
otherwise. The catalog deliberately emits values that do not parse, so the
test is a majority rather than "all".

**An attribute whose key is a column's name is namespaced, never dropped.**
Real feeds publish attributes named like a catalog's own columns -- the census
carries `Series` (25 records), `Product Type` (15) and `Brand` (1) as
attributes -- and a bearing's `Series` (`62`) is not its product's `series`
column. So `catalog.entry.canonical_name` gives such an attribute the entry name
`attr_<key>` (here `attr_series`, over `facets.series`) and leaves the
structural entry pointing at the column; a namespaced name that would itself
collide is refused. A nested entry's `key` applies the same rule, so the
entry's key and the field map's name cannot drift.

Attributes that fail a gate are still **declared**, with `facet: false` — they
stay searchable and stay available as filter and policy targets, they are just
not offered as sidebar controls.

What that yields, measured:

| | |
|---|---|
| attributes declared | 94 |
| **fields in the field map** | **112** (71 faceted attribute entries, 23 attribute entries declared with `facet: false`, and 18 structural ones) |
| **leaf fields in the Elasticsearch index** | **141** — the 21 the mapping declares, plus one per distinct `facets.*` key (84) and `facets_num.*` key (36) the dynamic templates create |
| facets in a category's sidebar | 8–15 |

The per-category figure is above the five-to-eight a real sidebar carries.
That is honest rather than tuned: a socket screw genuinely publishes five
dimension ranges (head diameter, head height, length, length under head,
thread length) beside material, finish and grade. Trimming to eight would mean dropping a control a shopper
uses, and PRISM has no authorable "top N" — terms facets always aggregate at
1000 and truncation is reported, not configured.

### Proving PRISM actually serves it

A field map that validates is not a served catalog.

```sh
python scripts/verify_prism_serves.py --studio http://127.0.0.1:8477
```

Every number PRISM reports is compared against one computed independently in
Python from the same in-memory catalog objects — the same discipline
`verify_elasticsearch.py` uses, and for the same reason: an aggregation that
agrees with itself proves nothing.

* a search returns products, and every id is a SKU the generator produced
* a terms facet's counts equal the generated counts
* a numeric range facet on a dimension carries the catalog's true min and max,
  and a range filter returns exactly the matching documents
* **every sampled facet count equals what clicking it returns** — a count that
  does not match its click is a blocking defect, not a note
* every product type returns its own documents, in the generated count
* the demo case: `3/8" end mill` returns products whose **shank** carries that
  value, and adding the structured `milling_dia` filter excludes them

### What the flat shape costs

The flat shape's `attributes` array is a plain object, so `name` and `value`
become two independent multi-valued fields. Filtering it for
*name = Shank dia. AND value = 3/8"* matches **236** documents; only **141**
actually publish a 3/8" shank. The other 95 carry a 3/8" belonging to a
different attribute (counted from `golden-catalog/flat.jsonl`).

That is why the field map facets the sanitised per-attribute `facets.*` /
`facets_num.*` keys, where the pairing cannot come apart, rather than the
`attributes` array. It is also the measurement that argues for the nested
shape: `reverse_nested` answers "how many *products*", and flat cannot.

## Verification

```sh
python scripts/verify_elasticsearch.py --host http://127.0.0.1:9201
```

Loads both shapes into a local test cluster, proves the properties below, and
deletes its indices. **Every number Elasticsearch returns is compared against
one computed independently in Python from the same in-memory objects** — an
aggregation that agrees with itself proves nothing, since a wrong query can
return a self-consistent wrong answer.

* a nested key-value facet count equals what clicking that facet returns
* the multi-valued attribute over-reports without `reverse_nested` and is
  correct with it, with a single-valued attribute as the control
* facet discovery scoped to one product type returns exactly that type's
  attribute names
* a numeric range on the shared `value_canonical` (millimetres), scoped by
  key, is correct — and widens when the key filter is dropped
* a full-text query for a dimension token returns products whose **shank**
  carries that value, and the structured attribute filter excludes them
* the flat shape over-matches the same name+value filter, and the nested shape
  does not

```sh
python scripts/mutation_check.py
```

Breaks the code each new test guards, in both directions where a property has
two, and reports any mutation that reds nothing as a zero. Three of the image
mutations came back green the first time they were run and each named a real
gap — a generic drawing that could be swapped for another type's, an attribute
that was validated but not drawn, and a control whose mutation text no longer
matched the code it was supposed to break. All three are fixed rather than
removed; a mutation that reds nothing is the point of running them.

**The harness cannot find the defect the line drawings exist to prevent, and
that is why the tests do not rely on it.** An attribute published on every
record and read by nothing has no code path to plant a defect in, which is how
`End Mill Style` (removed in #497: the category leaf says it) drew 473 ball nose mills square through 39 mutations with no
zeros. What the harness *can* plant is the other half — a channel that reads
its attribute, validates it, and then draws something else — so every marking
mutation is that shape, and the coverage question is answered from the data
side instead, in `tests/test_derivation.py` (the dimensioned renderer) and
`tests/test_sku_drawings.py` (the catalog's own drawings).

Two of the harness's own defects surfaced while the marking mutations were
added, both of which manufacture a false "not caught": a selector's `-k` filter
was split on whitespace, so `-k "x or y"` reached pytest as three arguments and
a stray quote; and a selector naming two files with a `-k` each silently kept
only the last filter, running one file with a filter that matched nothing in
it. The selector is parsed with `shlex` now, and the two-filter shape raises.

### The pinned unit declaration

```sh
uv run python scripts/check_industrial_unit_pin.py            # compare the pin with its source
uv run python scripts/check_industrial_unit_pin.py --refresh  # rewrite the pin from it
```

`tests/data/industrial_canonical_units.yaml` is a verbatim copy of the
industrial deployment's `canonical_units:` block, and the contract test takes
every unit's kind and size from it. Its source is a private repository that
this repository's CI cannot read, so the comparison is a script run by hand,
through an authenticated `gh`, never a pytest that could only skip in CI. **Run
it whenever the deployment's `canonical_units` changes, and before a 100-type
build.** It exits 0 on a match, 1 on a mismatch (naming whether the pin was
edited, misnames its commit, or the source has moved on), and 2 when it cannot
read the source; it never passes a comparison it could not make.

The pin records the source commit, the file's blob and the sha256 of its own
block. `tests/test_industrial_unit_pin.py` checks that digest on every run, in
CI included, so a hand edit to the pin is red. The pin is only ever written by
`--refresh`, which copies the block from the newest commit that touched the
source file. After a refresh that changes the block, rebuild and rerun the
suite: the contract test reads the new sizes.

## Images

The picture and the drawing speed are at the [top of this page](#synthetic-ecommerce-data).

**One drawing per SKU, drawn from that SKU's own values, with no text in it but
its brand's name.** The rulings are on elastic/prism-industrial-products#103
(2026-09-26 to -28); the brand plate is #132 (2026-10-08).
How the code does it -- record to figure to SVG bytes, the registry, the
provenance ladder, the publish gate, and a checklist for adding a type -- is in
[docs/drawings.md](docs/drawings.md).

**Exception: the [breadth categories](#catalog-breadth) draw one of six
FIXED plain shapes** (sphere, cylinder, block, disc, tube, bracket --
`domains/industrial/drawing/breadth_shapes.py`), never scaled or dimensioned from the SKU's own
published values. The "drawn from its own dimensions" rule above does not
apply to them: they are filler to give a facet something to show, not a
figure meant to survive a close look (maintainer, 2026-09-30). They still go
through the same text allow-list, brand plate, house style and material/finish fill as
every other drawing -- only the GEOMETRY is fixed.

* **One image per SKU**, so two lengths of one screw look different, and a
  grouped view can switch the picture when a variant is selected.
* **A brand plate under the figure** (#132): the brand's mark beside its
  name, in a strip at the foot of the sheet (`core/drawing/sheet.py`,
  `PLATE_BOX`). The figure is drawn in the sheet above it, so the plate never
  covers a dimension, a head or a thread of any type; an engineering
  drawing's maker sits in its title block the same way. Legible at the
  Studio grid tile (180 px for the 300-unit sheet, 0.6 px a unit): no
  name's capitals render under 10 px tall there. The full name is set beside
  the mark, on two lines beside it, split around it, or under it, whichever
  comes first at that size; a name none of them fits is refused, never
  shortened. The plate is 56 units tall, so the figure has the 236 units
  above it. Every SKU of a brand carries the same plate.
* **No other text** -- no dimension, callout, label or SKU.
  The words are on the record (title, description, attributes); the drawing
  reflects the specifications **visually**: a longer length of cut is drawn
  longer, a finer thread with more crests, a flat head is a cone and a button
  head a dome, a sealed bearing is closed and an open one shows its balls.
  The gate is an **allow-list**, not a list of text forms
  (`drawing.svg_problems`):
  - every element must be one the figures emit (`svg, rect, defs, pattern, g,
    path, circle`, and the plate's `text`), and there is no nested `<svg>`;
  - the `<text>` elements' words, joined, must be a brand's wordmark, and
    the font attributes appear on `<text>` only;
  - every attribute must be one they use, and every attribute VALUE must fit
    its grammar: a paint is a color, `none` or a same-file hatch reference,
    never an external or `data:` URL;
  - every id is a hatch pattern's own;
  - no element but `<text>` may carry character data;
  - no comment, processing instruction, doctype or entity reference may
    appear, but the `&amp;` of a name like `Lark & Lathe`.

  One thing no structural check can catch: a glyph's outline drawn as a plain
  path is indistinguishable from any other outline. The review's plants
  -- `<title>`, `<desc>`, `aria-label`, a comment, `<metadata>`,
  `<foreignObject>`, an embedded raster, `@font-face`, a glyph path from any
  font -- each red `tests/test_sku_drawings.py`.
* **Brands visibly different**, by house style and by mark: each brand owns
  one (ink, frame) pair and an independent paper tint -- twelve inks, six
  papers, four frames -- and one mark, consistent within a brand, never
  random per product ([Brands](#brands)). Any two brands' marks, rasterised
  at the tile's 19 px, differ in at least 24 pixels
  (`tests/test_brand_marks.py`; the closest pair measures 25).
* **A part longer than its type's extent is drawn BROKEN**, not shrunk: the
  shank is shortened between two drafting break lines, head and thread end
  kept, to a height that still grows with the true length. The screw and bolt
  extents are the pre-100K ones, so one 14-5/8" outlier no longer draws every
  socket screw 2.5x smaller.
* **Finish and material** are the part's fill (the finish's color, else the
  bare material's) and its section hatch.
* **Small SVG**, written directly rather than through a figure library:
  about 2 KB a drawing. `figures.drawings` in `golden-catalog/stats.json` has
  the committed catalog's count, total and largest bytes and the largest's
  type; `uv run ecom-generate images --catalog golden-catalog --out /tmp/img
  --archive /tmp/img.tar.gz` prints them with the archive's size. Every root
  declares `width="200" height="300"` beside its viewBox: an `<img>` sized only
  by max-width/max-height in a flex item that does not grow renders a
  viewBox-only SVG at 0 x 0.

The drawing is a pure function of `(product type, brand, published attributes)`
(`src/synthetic_ecommerce_data/core/drawing/`). For the six kinds the
dimensioned renderer in `domains/industrial/render/` also draws (end mills, drills, taps, screws
and bolts, washers, flap discs) it reads the SKU's geometry through the same
`geometry_from_record` functions, so the two cannot disagree about what a
record says; the other depth types read their few values inline, and the breadth
shapes read none.

**Sizes are visible.** The scale is one constant per product type: sheet units
per inch are the usable sheet over the type's largest drawn extent, declared
per type in `domains/industrial/drawing/figures.py`. There is no exception to it: a part too
small to read is not drawn larger, it is shown through a **magnifier**
(maintainer ruling on elastic/prism-industrial-products#103, 2026-09-28):

* a part is **too small to see** when it is drawn at most 1/5 of the sheet's
  width (40 units) AND at most 1/6 of its height (50), and such a part ALWAYS
  gets a lens (the refined ruling of 2026-09-28, with the edge cases settled at
  1/5 wide so socket screws drawn just over 1/6 are lensed); every other part
  is drawn plain, centred;
* the lensed part is drawn at its type's scale near the bottom of the sheet,
  horizontally centred, with no circle around it, and the lens above it shows
  the same figure enlarged so its bounding box's diagonal spans 92% of the lens;
* the lens is a magnifying glass in the icon's shape (a ring, a thin shaft and a
  grip twice the shaft's width, round caps, the handle at 45 degrees to the
  bottom-right), stroked at 35% of the icon's weight in the brand's ink, when
  that glass enlarges the part at least 2.5 times; otherwise it is a larger
  HANDLE-LESS lens -- the same thin ring and white interior -- sized to the
  sheet's width at an 8-unit side margin (the smallest that clears every brand
  frame by at least a unit), or to the 236-unit figure area above the brand
  plate where that is tighter. It cannot grow further: at the rule's extreme
  (a part drawn 40 x 50) it is height-bound and enlarges only ~x2.05, below
  the x2.5 the handled glass guarantees;
* the whole glyph is horizontally centred and as large as fits; the space above
  it equals the space below the part, with a 14-unit gap between them;
* no outline is thinner than 2.3 sheet units (~2 px on a 180 px-wide
  thumbnail), so a hairline part -- a 1/16" drill is under one unit wide at its
  type's scale -- is visible with or without a lens. Interior detail lines
  (flutes, threads, hatch) are texture and keep their finer weight.

How many committed SKUs are too small to see, how many of them get the handled
glass and how many the handle-less lens, with each lens's enlargement range, is
what the command in [docs/drawings.md](docs/drawings.md#scale-the-magnifier-and-the-only-text) prints. The
lowest enlargement any committed lens gives is x2.46, a width-bound
handle-less lens (below); no committed part reaches
the rule's 40 x 50 extreme. No drawing
carries text; the magnifier adds only paths and circles, and
`stroke-linecap="round"` to the allow-list.

What `tests/test_sku_drawings.py` proves over the committed catalog:

* **One scale per type.** Every product is drawn at its type's scale, so any
  two parts of a type are in true proportion, and a head, a thread or a bore
  siblings share is drawn identically on each (measured on the true-scale
  part of every drawing: screws' heads and bearings' outer rings).
* **The magnifier:**
  * a lens appears on exactly the SKUs drawn at most 1/5 of the sheet's width
    and 1/6 of its height, over every committed SKU;
  * the handle-less lens is used exactly where the handled glass cannot reach
    x2.5; the committed catalog's lowest enlargement is pinned at x2.12 (its
    measured minimum, rounded down), and the rule's extreme (40 x 50) at
    x2.05 to x2.5 -- below x2.5 because the lens is height-bound in the
    236-unit figure area above the brand plate (#132);
  * the handle-less lens clears the brand frame (8 units in, frames at 6 with
    strokes at most 2 wide);
  * each dimension binds on its own (planted: 41 x 5 and 5 x 50.5 plain,
    39 x 5 and 5 x 49 lensed); long thin parts never get a lens;
  * the lens shows the same part: the same shapes, scaled about the two
    centres by the layout's enlargement, and inside the lens;
  * the space above the glyph equals the space below the part, the gap is
    14 units, and the glyph and the part are centred, for both kinds of lens;
  * the ring, shaft and grip are in the brand's ink; the handle-less lens has no
    shaft or grip;
  * no outline, glyph stroke included, is thinner than 2.3 units (the hairline
    drill 93TD57, under two units wide, is pinned).
* **Other properties:**
  * no product exceeds its type's extent;
  * no drawing leaves its sheet;
  * no two siblings draw alike unless they differ only in values no figure
    draws.

An M3 washer's true-scale drawing is exactly 7/30 of an M16's diameter.

A record whose geometry cannot be read as published -- an attribute absent, a
value that does not parse, a pair that contradicts itself -- is drawn with its
kind's **nominal** proportions for the missing or conflicting values, and
`images.jsonl` says so per SKU (`geometry`: `record`, `partial` or `nominal`).
A drawing with no text states no number, so a nominal proportion cannot
contradict a published value; a consistent published value always wins.
`tests/test_sku_drawings.py` asserts the parts that are drawn from the record
are drawn to exactly its published length.

### Where a record points, and the bundle

Every SKU's `image_id` is `<product type>/<product id>/<sku>`; its `image_url`
is `/images/industrial/<image_id>.svg`, and `image_detail_url` names the same
file (one SVG serves both views). A product shows its first variant's drawing.
The URL is relative on purpose: the demo serves the bundle's folder itself
(elastic/prism#9770), and nothing points at a third-party host.

```sh
uv run ecom-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz
```

rebuilds every drawing from the **committed** catalog (`nested.jsonl`, with each
SKU's published spelling read from `flat.jsonl`), refuses unless each one's
sha256 equals the one `images.jsonl` records, and writes the files and a
deterministic archive (sorted members, zeroed times and owners, a gzip header
without a timestamp).

**Layout.** Every member is `industrial/<type>/<product>/<sku>.svg`: the
archive carries its own top-level `industrial/` folder, so a customization
unpacks it into its images folder, the demo serves that folder at `/images`
(elastic/prism#9770), and `image_url` -- `/images/industrial/...` -- resolves
with no per-deployment mount. A test pins that every member is exactly its
`image_url` under `/images`.

**The pin is of the content, not the compressed bytes.** gzip output depends on
the zlib build, so the archive's own sha256 is only stable on one toolchain.
What a customization pins is the **content digest**: the sha256 of the sorted
`<member path>\t<file sha256>` lines, printed by `ecom-generate images` and
written beside the archive as `.content-sha256`. It is derivable from the
committed `images.jsonl` alone (`bundle.manifest_digest`), and the installer
recomputes it after unpacking. `out/` is ignored by git, and a test asserts it,
so a drawing can never be committed here.

```sh
uv run python scripts/contact_sheet.py --catalog golden-catalog --out out/contact-sheets
```

writes an HTML contact sheet of real catalog SKUs -- one screw across its
lengths for two brands, flat washers across sizes, materials and brands, and
twenty SKUs of every type -- for judging the drawings by eye.

### The retail image release

```sh
uv run python prototypes/retail_drawings/image_release.py --out out/retail-images --archive out/retail-images.tar.gz
```

renders every image the retail export references and packages it in the
industrial bundle's shape, so the same installer takes it: members
`retail/<image_id>.svg` under the archive's own `retail/` folder, every
`image_url` that member under `/images/`, the same deterministic archive, and
the content digest and file count printed and written beside it as
`.content-sha256`. Images are keyed per style and colorway, never per SKU:
every size of one color shares an image, drawn in that color's swatch (base,
pattern and accent). The authored-styles build is `templates.authored_images` images for
`templates.authored` SKUs (`retail_figures.figures()`).
`--skus N` releases the scaled build instead (`scale.py`'s, the 20K catalog's
input): `--skus 20000` is 1,348 images for 20,002 SKUs.
There is no committed manifest to check against (the retail build is code, not
a committed catalog); the command refuses an `image_id` that names two
different drawings instead. `tests/test_retail_image_release.py` pins the
keying, that every document's image URL resolves to a packaged file, and the
package shape.

A `v*` tag builds the ceiling export and this bundle, uploads them to a release with their
`.content-sha256`, and opens the pin-bump pull request in the catalogue repository
([docs/releasing.md](docs/releasing.md), gen#536); a manual run of the workflow is the dry run.

### The older renderers in `domains/industrial/render/`

`domains/industrial/render/` still holds the matplotlib renderers: the twelve type drawings, the
per-line marking, and the per-record **dimensioned** drawings (`ecom-render`).
They carry text -- callouts and stamps -- and the catalog no longer uses any of
them; their geometry parsing is what the catalog's drawings read. Retiring them
-- extracting the shared geometry first -- is #27.

## Realism

The generator reproduces the defect classes found in real catalogs rather than
smoothing them away: inconsistent unit formatting within a single record,
ragged attribute coverage, and occasional internally impossible dimensions.
A catalog where every field is populated and every value is well-formed does
not look like a real one, and does not exercise a search engine like one.

Each rate is measured, and each defect class is reproduced against **its own
denominator** — the records that actually carry the attribute pair it needs,
which is how the source statistics measure them. `ecom-generate report` prints
the achieved figures beside their targets, so the claim is checkable rather
than asserted.

| property | target | achieved |
|---|---|---|
| shank diameter == cutting diameter | 0.6489 | 0.6992 |
| length of cut > overall length | 0.0829 | 0.0805 |
| an angle attribute carrying a length unit | 0.0469 | **0.0000, deliberately** (#404) |
| declared measurement system contradicts the value's units | 0.0323 | 0.0289 |
| unit mixing within one record | 0.0222 | 0.0166 |
| a parent repeating a (name, value) pair, over parents carrying `Standards` | 0.0085 | 0.0082 |
| title dimension token carries no label | 0.4667 | 0.4648 |
| title dimension token is not the primary dimension | 0.1714 | 0.1179 |
| title label truncated at the length cap | 0.0323 | **0.0000, deliberately** |
| image reference missing | 0.1089 | **0.0000, deliberately** |
| image id is shared, not the product's own | 0.7353 | **0.0000, deliberately** |
| attributes per record (mean) | 13.12 | 12.3887 |

Measured on `95a9ed0` with `uv run ecom-generate build` (the default catalog,
identical to `golden-catalog/`).

The repeated-pair row is the shape the `reverse_nested` trap needs (#1): a
repeated attribute NAME with distinct values (`Standards = [ISO, DIN]`) makes
every bucket agree with or without `reverse_nested`, while the same value twice
on one parent (`Standards = [ISO, ISO]`) over-reports it. The multi-valued
`Standards` stays; on 27 of the 3,307 golden parents that carry it, one value
is published twice (`parent repeats a (name, value) pair` in `stats.json`).
The target, `GeneratorConfig.defect_repeated_pair`, is set so the share of ALL
parents (about 0.43%) matches the 87 in 20,000 documents measured on a live
retail catalog. It is a defect class, so `--defects 0.0` removes it and
`--defects N` scales it; the draw has its own stream per product, so changing
it moves no other value in the catalog.

Two notes on reading that table honestly. The angle row is **deliberately zero**:
the corpus measures 0.0469, and the generator declines to write a length under an
angle key (#404; `GeneratorConfig.measured_angle_carries_length_unit` keeps the
measurement). And attributes per record sits about 6% below its target because the
reference mean is over a different mixture of product families than this
catalog contains; the per-family shape is reproduced, the mixture is not the
same one. It moved when the newer types arrived (hex nuts and hex keys publish
fewer attributes than end mills), which is the mixture changing rather than
any per-family rate doing so. For the same reason the "not the primary
dimension" title rate sits below its target: the newer types publish no
secondary dimension a title could name instead of the primary one.

The two image rows are **deliberate deviations, not misses**, and the target
column shows what this catalog aims at rather than what the corpus measures —
printing the corpus figure there would show a permanent, meaningless shortfall.
The corpus measures 10.89% of records carrying no parseable image reference;
this catalog gives every product and every variant one, because it is used as a
demo and a product with no image reads there as a broken page rather than as
realism about supplier data. The corpus measures 73.5% of references pointing
at an image that is not the product's own; this catalog deviates the other
way, because every SKU carries a drawing of its own (a generated drawing costs
nothing per size, and a variant's picture should show that variant). Both measured figures are kept in `GeneratorConfig` as
`measured_image_missing` and `measured_image_sku_diverges`, and a test sets the
missing-image rate back and checks the behaviour returns, so the deviation has
not quietly become a limitation.

### Price

Prices are generated from a measured price census
(`reference-statistics/P2_price_census.json`: priced SKUs on archived pages
of a large US industrial distributor), not from a flat multiplier. The
census figures are restated in `core/price.py`, because the census file
does not ship in the wheel, and `tests/test_price.py` checks every restated
figure against the file.

**What a price is made of.** In logs, a modelled SKU's shown price is
(`price.shown_price`):

| term | source |
|---|---|
| anchor: the price at a reference key dimension | fitted |
| slope on the key dimension (a bore, a diameter, a thread size), and on length for hex bolts and socket screws | census, cut only for a reason `price.SLOPE_CUTS` records |
| material | **not measured**: general-knowledge ratios in `price.MATERIAL_FACTORS`, since the census holds material equal on a page |
| brand tier (economy, standard, premium) | census: the bearing, jobber drill, ball end mill, socket head screw, spiral point tap and depressed-center wheel use their own figures (`price.TYPE_TIER_CENSUS`); every other type uses the jobber drill's. That includes the hex nut, though the census measures its same-spec brand spread: on its 6 shared specs the house label is the dearer brand (5.58x the others, p50), so it gives no economy figure |
| pack quantity (hex nuts, socket screws) | census pooled pack slope (`price.PACK_SLOPES`); the socket screw's pack falls as its size grows (`price.pack_quantity`) |
| pack quantity (hex bolts) | a group page's pack, independent of the size, so a size comes in several packs (`price.page_pack`); priced within a size on the elasticity the census's same-spec larger-pack ratio gives (`price.PACK_ELASTICITY`, 0.659: a 5x pack costs 0.5778 per piece). Because the pack adds its own spread, the bolt's slopes are cut to `price.SLOPE_CUT_AIMS` (shown p90/p10 10.0, inside the row's band) rather than to the census's 8.21, which would leave no size slope. Prices exist to show range filters, sorting and facets, not to match the census exactly (#86) |
| group noise, one draw per census-style page (one brand, the line attributes a page holds equal) | fitted sigma |
| SKU noise, one draw per SKU | fitted sigma |
| size noise, one draw per spec that every brand shares (taps, socket screws, set screws and depressed-center wheels only, `price.SIZE_NOISE`, each with its reason) | fitted sigma |

**A kit is priced from what it holds** (`price.CONTENTS_PRICED`). Its key is
not one dimension but its contents' price (`price.kit_contents`): each size
in `Sizes Included` priced on its part type's own curve (standard tier, no
material, no noise), at the census per-piece share of that part's shown price
(`price.PER_PIECE`: per-piece p50 over shown p50, since a census socket screw
is always sold by the pack and a third of hex keys are), times how many of
each size the kit holds. The slope on that key is 1.0, so a kit costs its
contents times one fitted factor (1.009 on the current fit), its material and
its tier, with SKU noise and no group noise: the default build's 15-piece inch
hex key sets, about $98 of keys, sold for $9.55 to $1,525.45 when a kit was
one group draw per page. Every kit now lands within 0.97x to 1.06x of its
contents' price times its material and tier on the default build, and 0.94x
to 1.08x at 100K (`test_each_kit_price_tracks_its_contents_at_both_builds`).
The census has no kit-versus-parts price figure, so the factor claims neither a
discount nor a premium: it is fitted to the census median kit price and moves
when #76 widens the kit kinds. Kit contents are computed from the part types'
fitted models, and one fit run fits the kit last, on the part models that run
just fitted (#94), so a run that also refits a part type a kit holds needs no
second run.

The price is then rounded to an ending (.99, .00, .50 ...) drawn from the
type's census endings mix; taps also snap to a fitted list-price ladder.
Finish does not enter the price. The types the census has no prices for are
declared `measured=False`: the ball-pein hammer, whose archived pages are script
shells; its figures are hand-set, NOT MEASURED, and no band holds them. The
nylon-insert lock nuts and the hex socket set screws are fitted to their own
census entries (#69) and scored like the other census types. This prints a type's SKU count, median, minimum
and maximum; feed it `git show ba90b5e:golden-catalog/flat.jsonl` (the last
uniform-multiplier catalog) for the earlier figures:

```sh
python3 -c "import json, statistics as s, sys; p = [r['price_usd'] for r in map(json.loads, sys.stdin) if r['product_type'] == sys.argv[1]]; print(len(p), s.median(p), min(p), max(p))" lock_nuts_nylon_insert < golden-catalog/flat.jsonl
```

The button, flat and low-head socket screws price as the socket head
screw does (`price.BORROWS`). The census has no O-rings, so they borrow
the flat washer's model (`TypeSpec.borrows`), keyed on the cross-section
and held to the inside-diameter span the washer model was fitted over
(`price.MEASURED_SPANS`: ISO 7089 M3 to M20, 0.126" to 0.827"); their
prices are generated, not measured. Keyed on the inside diameter instead,
even clamped to that span, the washer's noise put a simulated largest ring at
195 to 285 USD. A breadth category the census measures is
priced across its census p10, p50 and p90 (`price.BREADTH_CENSUS`); any
other breadth row draws from its own `price_range`. A measured breadth
category deepened into a modelled type keeps its census row
(`price.DEEPENED_CENSUS`, the roller chain's 71 prices), and its own fitted
model is held to that row's p50 and p90/p10 bands at both sizes. The census
has no within-page pairs for it, so its slopes are GENERATED, not measured:
the roller chain's on pitch (1.2) and on length (0.93). So is what its strand
count multiplies the price by (`roller_chain.STRAND_FACTORS`: double 1.9x and
triple 2.8x the single strand chain; the census's 71 prices are not split by
strand count). One brand's single, double and triple strand chains share
their price noise (`PriceModel.option_attribute`), so the multiplier is what
separates them: in every chain number offered in more than one strand count
in one material and length, the median price rises with the strand count (10
such sets on the golden catalog, 13 at `--lines 39000`; a #40 steel 10 ft
chain's medians there are 162.00, 341.25 and 502.00 USD).

**How it is checked.** `ecom-generate report` prints one row per measured
figure: each type's p50 and p90/p10, the share of within-page size pairs
whose larger size costs more, longer costs more (bolts and socket screws),
equal prices across a size pair (taps), how often a smaller SKU of one
product costs twice the larger, the same-spec brand spread, economy brands
against the rest, and the .99/.00/.50 endings. A spec is the census's: the
key dimension in one material (`price.material_of`). A wheel publishes its
material as its abrasive (`price.MATERIAL_ATTRIBUTES`), and
`test_every_brand_census_types_spec_holds_a_material_or_names_why_not` fails
a type whose specs hold no material. Each row has a band
(`price_report.P50_BAND`, `SPREAD_BAND`, `MONOTONE_BAND`, and three census
standard errors where the census sample is small: `share_band`,
`brand_spread_band`). Every row is scored at the default size and at 100K
(`--lines 39000`, `config.HUNDRED_K_LINES`), and must land in band, or be
pinned below, at both:
`test_every_price_row_is_within_its_band_or_pinned_at_the_default_size` and
`test_each_price_row_is_within_its_band_or_its_pin_holds_at_100k`.

The default-size figures, bands and reasons are committed: the `comparisons`
entries of `golden-catalog/stats.json` whose `name` starts with `price `
(`achieved`, `band`, and the reason in `note`). This counts them:

```sh
python3 -c "import json; r = [c for c in json.load(open('golden-catalog/stats.json'))['comparisons'] if c['name'].startswith('price ')]; print(len(r), 'rows,', sum(c['band'][0] <= c['achieved'] <= c['band'][1] for c in r), 'in band')"
```

It prints `72 rows, 70 in band`; the other two are the pins.
`uv run python scripts/fit_price_model.py` prints every row at both sizes
side by side (about 2 minutes).

**Pins.** A row that no model of this shape holds is declared with its
reason and the issue that fixes it, and stays bounded:

| row | kind | why | bound |
|---|---|---|---|
| wheel brand spread | pin, above band at 100K only (the default build is in band, its record `None`) | the brand tiers alone, every noise off, put the 100K build above band: 3 of the 12 wheel brands are economy, and the row's sampled brands take one on more than half its specs, where the census measures its house label on 4 of its 12; the wheel's p90/p10 is carried by noise one spec shares across its brands (`size_sigma`), so no per-brand group noise adds to it (#66, #272) | at 100K no further above than the figure `price.PINNED_FIGURES` records, within `PIN_TOLERANCE`; on the default build in band |
| kit p90/p10 | pin, below band | a kit is priced from its contents, and the catalog's kit kinds hold about $36 to $130 of parts, so with material and tier its prices span about 4x against the census's 114x, whose kits run from packs of 12 and 15 at about $4.50 to a p90 of $629; group noise loud enough to make up the rest would spread a kit's price about 79x on its own, so a kit draws none (widen the kit range: #76) | no further below than the figure `price.PINNED_FIGURES` records for each size, within `PIN_TOLERANCE` |

The full reasons are `price.PINNED_SHORTFALLS`, and `stats.json` carries
them in each row's `note`. A pin is never a wider band: a row that leaves its
band is declared, with a cause, or the model is fixed.
`scripts/fit_price_model.py` refuses to write a fit that leaves a row out of
band undeclared, or a pin that no longer holds. The tests hold the same two at
both sizes, and `uv run python scripts/mutation_check.py --only "price:"`
plants a defect in each price gate, the pin bounds among them, and checks
that its test goes red; `--only "kit:"` runs the kit-contents rows alone.

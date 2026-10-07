# synthetic-industrial-products

A generated product catalog for the industrial-supply vertical (cutting tools,
fasteners, abrasives, hand tools, bearings), built to exercise structured facet
extraction in search: 10,650 SKUs over 5,814 products in 19 depth types plus
48 [breadth categories](#catalog-breadth), one product each -- from 45
invented brands -- and, with one flag, about 100,000 SKUs
([The 100K catalog](#the-100k-catalog); its name and figures are #62's).

The SKU and product counts are `skus` and `lines` in
`golden-catalog/stats.json` (per type: `skus_by_type`, `lines_by_type`). The
type counts are
`uv run python -c "from synthetic_industrial_products.catalog.generate import all_type_keys as k; print(len(k('modelled')) + len(k('new')), len(k('breadth')))"`.

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
| **Newer types** (hex nuts, radial ball bearings, depressed-center wheels, hex keys; elastic/prism-industrial-products#103) | dimensions are **generated** from conventional sizes -- nut widths across flats, the 60/62/63 bearing series boundary sizes, stocked wheel diameters, hex key sizes. They follow the familiar ladders but were not extracted from an open dataset, so the provenance field says "generated". The one standard claimed is a hex nut's, and only where every row of its line IS that standard's row -- see [Facts a record states are real](#facts-a-record-states-are-real). |
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

`src/synthetic_industrial_products/data/fastener_standards.json` is that
extraction, unmodified, and carries its own provenance block naming each
repository, its licence and the commit it was read at. Only the sizes this
catalog offers were taken; the upstream compilations are not redistributed.
Values the sources do not carry are recorded as absent rather than filled in —
there is no `#10` hex bolt here, because ASME B18.2.1 hex head screws begin at
1/4", and no `M20` button head, because ISO 7380-1 in the source stops at M16.

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

**The length.** A screw publishes three of them and they are three different
measurements:

| attribute | what it measures |
|---|---|
| `Length` | the nominal length — measured **over** the head on a countersunk screw and under it on every other style |
| `Length under Head` | the whole shank, head excluded (the census's casing) |
| `Thread Length` | how much of that shank carries thread |

`x 3/4` in the reference distributor's pattern is the second of those. Binding it to
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
| **Never ships** | the reference corpus of captured pages, and the rendered drawings — both reproducible, see `.gitignore`. The drawings are rebuilt from the committed catalog into a pinned bundle (`sip-generate images`, see [Images](#images)); `images.jsonl` records each one's sha256, and nothing else about them is committed |

## Contributing

To add a product type, or move one into its own module, see
[How to add a product type](docs/adding-a-type.md).

Merge every pull request with `scripts/merge_pr.sh <PR number>`, not the
GitHub button: this repository has no branch protection, so a green from an
older `main` can merge and turn `main` red. The script merges current `main`
in, rebuilds `golden-catalog/` and merges only when the drift, golden and seam
tests pass on that tree.

Install both hook types once per clone: `pre-commit install` (the config sets
`default_install_hook_types: [pre-commit, commit-msg]`). The commit-msg hook
(`scripts/check_commit_msg.py`) refuses a message that credits an AI tool or a
bot. Its patterns are the core repository's AI-attribution family, vendored
with the commit it came from, plus this repository's additions. CI runs the
same check over every commit a pull request adds, so a clone without hooks
cannot skip it. Git's `#` help lines are skipped only by the hook, because a recorded
message keeps any `#` line it was given. Messages are folded before matching:
look-alike letters, invisible and bidirectional characters, and a phrase
wrapped across two lines are all caught. The pre-commit hooks run `ruff check` and the whitespace
fixers, which leave `golden-catalog/` alone.

Run the test suite with plain `uv run pytest`, with no `-n`: the project does
not install `pytest-xdist`.

## Generating a catalog

```sh
uv sync
uv run sip-generate build --out out/catalog
uv run sip-generate report                      # the measured-vs-target table only
```

Everything is parameterised, because the point of the catalog is to be dialled
until something breaks:

```sh
uv run sip-generate build --lines 900               # a bigger or smaller catalog (THE size knob)
uv run sip-generate build --sparsity 0.4             # raggeder attribute coverage
uv run sip-generate build --defects 0.0              # a catalog with no contradictions
uv run sip-generate build --seed 7                   # a different catalog
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
uv run sip-generate build --lines 39000 --out out/catalog-100k
uv run sip-generate images --catalog out/catalog-100k --out out/images-100k --archive out/images-100k.tar.gz
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
| screw_socket_head | 7,727 | | bearing_radial_ball | 7,516 |
| screw_flat_head | 4,752 | | wheel_depressed_center | 11,495 |
| screw_button_head | 3,439 | | hex_key | 6,466 |
| screw_low_head | 2,692 | | bolt_hex | 5,934 |
| kit_assortment | 695 | | lock_nuts_nylon_insert | 4,513 |
| set_screws_hex_socket | 7,061 | | 48 breadth categories | 85 (1-3 each) |

The mix is not the one a proportional scale would give, and that is the
uniqueness rule at work: a type whose spec space is small (ISO 7089 fixes a
washer's nine sizes; a hammer is its head weight and handle) runs out of
SKUs its makers have not already made, so it grows less. It was 28,300
lines for 100K until uniqueness stopped counting metadata as a difference.

**111,499 SKUs over 64,483 products** (`skus` and `lines` in `stats.json`),
4,513 of them lock nuts over 2,714 products and 7,061 set screws over 3,786.
`lock_nuts_nylon_insert` and `set_screws_hex_socket` became deep types (#53),
each with its own share of `--lines`, and took none from the others, so every
other type's SKU count is the one measured on `95a9ed0` (the set screws' small
sockets add a true sentence to some hex key copy, not a SKU), when
the build gave 99,929 SKUs over 57,985 products. On `95a9ed0`: SKUs that are
not different (the rule below): 0. Every bearing number is a real table entry
with its own bore, OD and width. Product names: 0 clashes catalog-wide.
Every must-stock example is stocked. (Those four are the 100K tests in
`tests/test_catalog_brands_voice.py`.) Since set screws,
`scripts/check_determinism.py --lines 39000`: all 7 emitted files
byte-identical across two builds. The drawings, built with the second command
above: 111,499 drawings, 230.1 MB unpacked, a 25.8 MB `images.tar.gz`, every
sha256 matching `images.jsonl` (the counts the command prints). The 100K
catalog is still not published while the spec is iterated at the default
size.

The files are far too large to commit uncompressed (`flat.jsonl` is ~330 MB).
This repository commits the default-size catalog only; the industrial demo
serves that one, from a pinned release, and the 100K build is a capability
kept tested (`tests/test_catalog_brands_voice.py` builds it) rather than a
published artifact.

What moves at 100K, measured against the census targets (`sip-generate
report`), with the default catalog beside it:

| measured property | target | 100K |
|---|--:|--:|
| shank == cutting diameter | 0.6489 | 0.6895 |
| length of cut > overall length | 0.0829 | 0.0829 |
| angle carries a length unit | 0.0469 | 0.0451 |
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
cutter's own size; and an oversize shank is at most twice its cutter (see
[Brand voice](#brand-voice-titles-and-descriptions)). Label spellings are
quantised by brand (each brand spells a label one way), so e.g. the flute
label mix differs from the census's 0.66 / 0.28 / 0.06.

## Brands

Forty-five manufacturers, all invented, in one table (`catalog/brands.py`):
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
`tests/test_catalog_facts.py` against tables written out in the test:

* **Bearing ratings** are a table per bearing number
  (`newtypes.BEARING_RATINGS`): dynamic and static load and the limiting
  speed of the open bearing -- SKF's published figures for 60/62/63,
  distributor listings for the inch R series -- with a contact seal at 70% of
  the open speed. No jitter: two bearings of one number are rated alike,
  whoever makes them, and a rating never makes two SKUs different. (A formula
  had put a 6000 at 3,110 lbf against a published 1,068.)
* **Standards** are a truth table by what the line IS (`catalog/conformance.py`):
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
  (12.9 at C39); a graded hex bolt's material follows its grade, and hot-dip
  galvanizing is kept off Grade 8 / Class 10.9 (ASTM F2329); nACo and AlTiN
  are carbide coatings, black oxide an HSS treatment.
* **An end mill's shank is never thinner than its cutter, and never more than
  twice it** -- unless the smallest stocked shank above the cutter is already
  more (a 1mm cutter sits on a 3mm shank). A reduced/oversize shank is the
  next stocked shank up; above the largest stocked shank it is the cutter's
  own size. The census's 3.0 and 2.667 ratios had put a 5/32" cutter on a
  5/8" shank; 46 end mills on 7dac659's golden were over that ceiling.
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
differently (`catalog/voice.py`).

* **The title's core is the census structure** -- `<Item>, <key dim> <role>,
  <material>, <coating>, <flutes>...`. A type whose variant axis is not its
  size still names its key dimension (`KEY_DIMENSIONS`): a bearing its bearing
  number, a wheel and a flap disc their diameter. A brand's template chooses
  only among census-observed variants and adds words AROUND the core: a
  non-factual qualifier or the brand's name, and a trailing pack segment.
* **Pack wording is allowed only where a pack field exists.** The maintainer's
  ruling: pack wording is fine when the record actually carries a pack field.
  `Package Quantity` exists on hex nuts and depressed-center wheels, and every
  pack word in a title or description equals that field; no other type
  carries pack wording.
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
without stating anything false (`catalog/compat.py`):

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

## Copy noise

A distributor's copy mentions sizes a product does NOT fit, the siblings it
is also sold in, the unit a shopper might have typed, what it pairs with and
what it cuts. Every one of those words is searchable, so a query matches more
than the products it names, and the policies and facets are what narrow the
page back down (`catalog/noise.py`). Every sentence is TRUE of its record --
read from its own published values, its siblings, or a table -- and the
attributes are never touched, so the facets can always separate the noise out.

| type | example | from |
|---|---|---|
| negative fit | `Not for M10 or M16 threads.` / `Will not fit 5/32" sockets.` | the neighbouring diameters; the next smaller key |
| siblings | `Also available in M8 / M10 / M16 sizes.` | the product's other SKUs, on its variant axis |
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
a real number (`Number of Pieces`, so pack wording may name it), never
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
the default build, 695 at 100K.

Two derivation artefacts went with it: the drive size is published as the
nominal key (`10mm`), not the extracted socket's toleranced across-flats
(`10.07mm`), and the countersunk screw publishes no `Length under Head` -- it
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
every per-type spelling would be a facet of its own. `catalog/names.py` is the
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
{"key": "milling_dia", "name": "Milling Dia.", "value": "3/8", "unit_code": "INH", "value_canonical": 9.525}
```

* `key` is required: the machine name the Engine discovers an attribute by,
  `sanitize(name)`, namespaced as `attr_<key>` when it is a column's name (see
  below). `name` is the display name.
* A **measured** value is fully split. `value` is the bare magnitude with no
  unit marker and no thousands separator, `unit_code` (UN/CEFACT: `INH`, `MMT`,
  `DD`, `ONZ`, `LBR`, `C78`, `RPM`, `TPI`, and `C62` for a count) is the only
  place the unit lives, and `value_canonical` is the magnitude in the kind's
  canonical unit (millimetres, grams, degrees, one, rpm, pound-force), computed
  exactly and rounded to a float once.
* Thread spacing is published under two keys, as real catalogs publish it: a
  metric tap's `Pitch` (`pitch`, `MMT`, `0.5`) and an inch tap's `Threads per
  Inch` (`threads_per_inch`, `TPI`, `32`). `TPI` is a LENGTH written as a count
  per inch (ruled on elastic/prism#9877): `value` stays the count and
  `value_canonical` is the pitch in millimetres, `127/5 / n`, so `32` TPI is
  `0.79375` and `20` TPI is `1.27`. `13` TPI (127/65 mm) does not terminate and
  is the nearest float, like `3/8"` (9.525 mm). The contract test reads each
  unit's kind and size from a pinned copy of the industrial deployment's
  `canonical_units` block (`tests/data/industrial_canonical_units.yaml`; see
  [The pinned unit declaration](#the-pinned-unit-declaration)). No key's
  measured entries mix quantity kinds, with one exception: the modelled angle
  defect below, matched on its inch unit and its five values.
* Anything else stays unitless text, including composite designators such as
  `1/4-20` and `M10x1.5`.

The split is **read back out of** the published string, never computed from
the generator's magnitude, so the two can never disagree: `3/8"` has no exact
two-decimal millimetre spelling, and a number computed from the original
magnitude would quietly differ from the string actually published. A defective
spelling splits as written: `Helix Angle = 42"` becomes `42` `INH`, keeping the
bad value and dropping the bad spelling (elastic/prism#9284). An attribute that
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
             - 1-1/4" Length under Head, 1-1/4" Thread Length, 3/4" Width
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
line's titles differ as whole strings left **1,913** SKUs naming nothing of
their own, and a bare substring test left **1,932** — 19 of those passing on a
coincidence rather than on a value.

The coincidence outlives a catalog that has otherwise been repaired, which is
why the distinction is worth a rule rather than a remark: on the first pass at
this work the whole-string and substring counts had both reached zero while the
standalone-token count was still **10**. One of the ten was
`Button Head Socket Cap Screw, 1/4-20, Alloy Steel`, credited with naming a
`Length under Head` of `1/4` — which is the first half of a thread designation
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

`sip-generate build` writes both serialisations from the same generated
objects, so any difference between what they return is a property of the shape
and not of the data.

| file | shape |
|---|---|
| `nested.jsonl` | parent + nested SKUs + nested key-value attributes. The target shape: the only one in which "how many *products* have this value" is answerable, via `reverse_nested`. |
| `flat.jsonl` | one document per SKU, attributes denormalised. Loadable today. Its attribute array is a plain `object`, so `name` and `value` become two independent multi-valued fields and the correlation between them is lost. |
| `render.jsonl` | the same SKUs in the shape `sip-render batch` already reads, for the per-record dimensioned renderer. The catalog's cards do not use it: every product and variant carries an `image_id` naming its own product line's drawing. |
| `images.jsonl` | one row per image — one per product line — with its product type, the shape it is drawn as, its path under the image base URL at both profiles, and how many products point at it |
| `stats.json` | what was generated, measured against the statistics it reproduces |

Both shapes publish a SKU's own `description` beside its `title`. The line's
title ships too, as `parent_title` — it is what a grouped card will be headed
with — but it is no longer what renders under a SKU's title.

The flat shape also carries a sanitised `facets` object, because `Milling Dia.`
cannot be an Elasticsearch field name — the trailing dot makes it an invalid
path. The three spellings of the measurement-system attribute deliberately
sanitise to three different keys rather than being folded into one: folding
them here would hide the problem a field map exists to solve.

## Catalog breadth

alexander-marquardt/synthetic-industrial-products#34: the 19 depth types give
this catalog DEPTH -- hundreds of products in each -- but not BREADTH. A
comparison the issue makes: a real industrial storefront returns 51 items
across 9 categories for `1/2 ball` (tooling balls, rubber balls, ball stock in
three materials, gage balls, ...); this catalog's twelve original types return
488 across 3 (ball end mills, ball-end hex keys, radial bearings), because
description noise (above) adds hits WITHIN a type and cannot add a category.

**One row per breadth category, 1-3 SKUs each, one generic loop.** Most rows
are in one table, `src/synthetic_industrial_products/data/breadth_categories.yaml`;
a type in its own module declares the same row there (`ball_stock_precision`, see
[How to add a product type](docs/adding-a-type.md)). For each row: a category path, a shape name, an item noun, 3-5
line-scoped attributes with short value lists, one size (variant) attribute,
and a one-line reason naming the customer query it joins. `catalog/breadth.py`
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

## The built catalog is committed, in `golden-catalog/`

`sip-generate build` is reproducible, but its output is checked in anyway, at
`golden-catalog/`:

| file | |
|---|---|
| `flat.jsonl` | about 30 MB — one document per SKU |
| `nested.jsonl` | about 18 MB — one document per product, nested variants and key-value attributes |
| `render.jsonl` | 2.1 MB — the original twelve types' SKUs, for the per-record dimensioned renderer |
| `mapping.flat.json`, `mapping.nested.json` | the Elasticsearch mappings for each shape |
| `images.jsonl` | 4.0 MB — one row per SKU drawing: its path in the bundle, its URL, the sha256 of its bytes |
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

### Regenerating it

```sh
uv run sip-generate build --out golden-catalog
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
carries a **must-stock list** (`catalog/muststock.py`, maintainer ruling on
elastic/prism-industrial-products#103): one entry per requirement example, naming
the product type(s) it may be and the published values a SKU must carry --
`Milling Dia.` `1/2"` with `Length of Cut` `1"`, a `bolt_hex` in `7/16-14`
with `Length under Head` `1-3/4"`, `Grade 8` and `Zinc Plated`, and 22 more.

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
uv run sip-generate build --out out/catalog

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
the emitted documents, as a step of `sip-generate build`, and
`tests/test_prism_field_map_drift.py` fails if the committed file and a fresh
derivation disagree. Editing either side alone reds it; both directions are
planted in `scripts/mutation_check.py`.

### Which attributes become facets

Not all 84. Three measured gates, applied to the emitted documents:

| gate | rule | why |
|---|---|---|
| **discriminating** | at least 2 distinct values | a facet with one value cannot narrow anything — it is a control that does nothing |
| **characteristic** | present on ≥50% of the documents of the product types that publish it *at all* | the denominator is per-attribute: an attribute carried by one of twelve types can never exceed ~10% of the catalog, yet may be the primary facet for its own category |
| **not an identifier** | a **terms** attribute carries ≤25 distinct values | `Dia./Thread Size` is the first thing a shopper filters on; `List Number` publishes 574 values over 1,100 documents and is a part reference nobody browses. Numeric attributes are exempt — a range control's cost does not grow with cardinality |

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
| attributes declared | 84 |
| **fields in the field map** | **101** (67 faceted terms entries, 26 declared with `facet: false`, and the structural ones) |
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
*name = Shank Dia. AND value = 3/8"* matches **236** documents; only **141**
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
`End Mill Style` drew 473 ball nose mills square through 39 mutations with no
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

**One drawing per SKU, drawn from that SKU's own values, with no text in it.**
The rulings are on elastic/prism-industrial-products#103 (2026-09-26 to -28).
How the code does it -- record to figure to SVG bytes, the registry, the
provenance ladder, the publish gate, and a checklist for adding a type -- is in
[docs/drawings.md](docs/drawings.md).

**Exception: the [breadth categories](#catalog-breadth) draw one of six
FIXED plain shapes** (sphere, cylinder, block, disc, tube, bracket --
`drawing/breadth_shapes.py`), never scaled or dimensioned from the SKU's own
published values. The "drawn from its own dimensions" rule above does not
apply to them: they are filler to give a facet something to show, not a
figure meant to survive a close look (maintainer, 2026-09-30). They still go
through the same no-text allow-list, house style and material/finish fill as
every other drawing -- only the GEOMETRY is fixed.

* **One image per SKU**, so two lengths of one screw look different, and a
  grouped view can switch the picture when a variant is selected.
* **No text of any kind** -- no dimension, callout, label, brand name or SKU.
  The words are on the record (title, description, attributes); the drawing
  reflects the specifications **visually**: a longer length of cut is drawn
  longer, a finer thread with more crests, a flat head is a cone and a button
  head a dome, a sealed bearing is closed and an open one shows its balls.
  The gate is an **allow-list**, not a list of text forms
  (`drawing.svg_problems`):
  - every element must be one the figures emit (`svg, rect, defs, pattern, g,
    path, circle`), and there is no nested `<svg>`;
  - every attribute must be one they use, and every attribute VALUE must fit
    its grammar: a paint is a colour, `none` or a same-file hatch reference,
    never an external or `data:` URL;
  - every id is a hatch pattern's own;
  - no element may carry character data;
  - no comment, processing instruction, doctype or entity reference may
    appear.

  One thing no structural check can catch: a glyph's outline drawn as a plain
  path is indistinguishable from any other outline. The review's plants
  -- `<title>`, `<desc>`, `aria-label`, a comment, `<metadata>`,
  `<foreignObject>`, an embedded raster, `@font-face`, a glyph path from any
  font -- each red `tests/test_sku_drawings.py`.
* **Brands visibly different**, by house style: each brand owns one (ink,
  frame) pair and an independent paper tint -- twelve inks, six papers, four
  frames -- consistent within a brand, never random per product ([Brands](#brands)).
* **A part longer than its type's extent is drawn BROKEN**, not shrunk: the
  shank is shortened between two drafting break lines, head and thread end
  kept, to a height that still grows with the true length. The screw and bolt
  extents are the pre-100K ones, so one 14-5/8" outlier no longer draws every
  socket screw 2.5x smaller.
* **Finish and material** are the part's fill (the finish's colour, else the
  bare material's) and its section hatch.
* **Small SVG**, written directly rather than through a figure library:
  measured on the committed catalog, 10,650 drawings, 21.0 MB unpacked
  (1.97 KB a drawing on average), and a 2.23 MB `images.tar.gz` (the count,
  bytes and archive size `uv run sip-generate images --catalog golden-catalog
  --out /tmp/img --archive /tmp/img.tar.gz` prints). Every root
  declares `width="200" height="300"` beside its viewBox: an `<img>` sized only
  by max-width/max-height in a flex item that does not grow renders a
  viewBox-only SVG at 0 x 0.

The drawing is a pure function of `(product type, brand, published attributes)`
(`src/synthetic_industrial_products/drawing/`). For the six kinds the
dimensioned renderer in `render/` also draws (end mills, drills, taps, screws
and bolts, washers, flap discs) it reads the SKU's geometry through the same
`geometry_from_record` functions, so the two cannot disagree about what a
record says; the other depth types read their few values inline, and the breadth
shapes read none.

**Sizes are visible.** The scale is one constant per product type: sheet units
per inch are the usable sheet over the type's largest drawn extent, declared
per type in `drawing/figures.py`. There is no exception to it: a part too
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
  frame by at least a unit). That lens is WIDTH-BOUND, so it cannot grow further:
  at the rule's extreme (a part drawn 40 x 50) it enlarges only ~x2.42, below
  the x2.5 the handled glass guarantees;
* the whole glyph is horizontally centred and as large as fits; the space above
  it equals the space below the part, with a 14-unit gap between them;
* no outline is thinner than 2.3 sheet units (~2 px on a 180 px-wide
  thumbnail), so a hairline part -- a 1/16" drill is under one unit wide at its
  type's scale -- is visible with or without a lens. Interior detail lines
  (flutes, threads, hatch) are texture and keep their finer weight.

On the committed catalog 1,598 SKUs are too small to see: 449 get the handled
glass (x2.53 to x9.29) and 1,149 the handle-less lens (x2.46 to x4.05), as the
command in [docs/drawings.md](docs/drawings.md#scale-the-magnifier-and-no-text) prints. The
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
    x2.5; the committed catalog's lowest enlargement is pinned at x2.52 (its
    measured minimum, rounded down), and the rule's extreme (40 x 50) at
    x2.41 to x2.5 -- below x2.5 because the lens is width-bound;
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
uv run sip-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz
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
`<member path>\t<file sha256>` lines, printed by `sip-generate images` and
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

### The older renderers in `render/`

`render/` still holds the matplotlib renderers: the twelve type drawings, the
per-line marking, and the per-record **dimensioned** drawings (`sip-render`).
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
which is how the source statistics measure them. `sip-generate report` prints
the achieved figures beside their targets, so the claim is checkable rather
than asserted.

| property | target | achieved |
|---|---|---|
| shank diameter == cutting diameter | 0.6489 | 0.6992 |
| length of cut > overall length | 0.0829 | 0.0805 |
| an angle attribute carrying a length unit | 0.0469 | 0.0448 |
| declared measurement system contradicts the value's units | 0.0323 | 0.0289 |
| unit mixing within one record | 0.0222 | 0.0166 |
| title dimension token carries no label | 0.4667 | 0.4648 |
| title dimension token is not the primary dimension | 0.1714 | 0.1179 |
| title label truncated at the length cap | 0.0323 | **0.0000, deliberately** |
| image reference missing | 0.1089 | **0.0000, deliberately** |
| image id is shared, not the product's own | 0.7353 | **0.0000, deliberately** |
| attributes per record (mean) | 13.12 | 12.3887 |

Measured on `95a9ed0` with `uv run sip-generate build` (the default catalog,
identical to `golden-catalog/`).

Two notes on reading that table honestly. The angle defect is **clustered**:
the attribute is line-constant, so one bad row reaches every SKU under that
line — which is how these arrive in a real catalog, and is visible in the
source corpus too, where the same wrong value repeats across a whole series.
Its per-record rate therefore swings much more between seeds than the others.
And attributes per record sits about 6% below its target because the
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
census figures are restated in `catalog/price.py`, because the census file
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
| pack quantity (hex nuts) | census pack slope |
| group noise, one draw per census-style page (one brand, the line attributes a page holds equal) | fitted sigma |
| SKU noise, one draw per SKU | fitted sigma |
| size noise, one draw per spec that every brand shares (taps and socket screws only, `price.SIZE_NOISE`, each with its reason) | fitted sigma |

The price is then rounded to an ending (.99, .00, .50 ...) drawn from the
type's census endings mix; taps also snap to a fitted list-price ladder.
Finish does not enter the price. The types the census has no prices for are
declared `measured=False`: the ball-pein hammer, the nylon-insert lock nuts
and the hex socket set screws. Their figures are hand-set, NOT MEASURED,
each module's comment saying where they come from, and they do not keep the
level the catalog had before: their median prices on the golden catalog are
72.62, 2.28 and 2.48 USD, against 65.17, 1.86 and 1.80 under the uniform
multiplier (+11%, +23%, +38%). No band holds them until #69 gives them
census-backed price bands. This prints a type's SKU count, median, minimum
and maximum; feed it `git show ba90b5e:golden-catalog/flat.jsonl` (the last
uniform-multiplier catalog) for the earlier figures:

```sh
python3 -c "import json, statistics as s, sys; p = [r['price_usd'] for r in map(json.loads, sys.stdin) if r['product_type'] == sys.argv[1]]; print(len(p), s.median(p), min(p), max(p))" lock_nuts_nylon_insert < golden-catalog/flat.jsonl
```

The button, flat and low-head socket screws price as the socket head
screw does (`price.BORROWS`). A breadth category the census measures is
priced across its census p10, p50 and p90 (`price.BREADTH_CENSUS`); any
other breadth row draws from its own `price_range`.

**How it is checked.** `sip-generate report` prints one row per measured
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
pinned or excepted below, at both:
`test_every_price_row_is_within_its_band_or_pinned_at_the_default_size` and
`test_each_price_row_is_within_its_band_or_its_pin_holds_at_100k`.

The default-size figures, bands and reasons are committed: the `comparisons`
entries of `golden-catalog/stats.json` whose `name` starts with `price `
(`achieved`, `band`, and the reason in `note`). This counts them:

```sh
python3 -c "import json; r = [c for c in json.load(open('golden-catalog/stats.json'))['comparisons'] if c['name'].startswith('price ')]; print(len(r), 'rows,', sum(c['band'][0] <= c['achieved'] <= c['band'][1] for c in r), 'in band')"
```

It prints `61 rows, 57 in band`; the other four are the two pins and the two
kit exceptions. `uv run python scripts/fit_price_model.py` prints every row
at both sizes side by side (about 2 minutes). At 100K the kit p90/p10 lands
in band.

**Declared exceptions and pins.** A row that no model of this shape holds
is declared with its reason and the issue that fixes it, and stays bounded:

| row | kind | why | bound |
|---|---|---|---|
| bearing p90/p10 | pin, below band | catalog bores span far less than the census's, and the census's own small brand spread leaves no group noise to make up the rest (widen the bore range: #64) | no further below than the figure `price.PINNED_FIGURES` records for each size, within `PIN_TOLERANCE` |
| wheel brand spread | pin, above band | the brand tiers alone, every noise off, put it above band: 3 of the 12 wheel brands are economy, and the row's sampled brands take one on more than half its specs, where the census measures its house label on 4 of its 12; the per-brand group noise then spreads one spec's brands further (#66) | as above |
| kit p50 and kit p90/p10 | exception, either side | a kit's price is one group draw per page, not the sum of its contents, so its few pages move the median and the p90/p10 with the build's size (price a kit from its contents: #71) | a band miss no more than `price.EXCEPTION_DRIFT` times the one `price.EXCEPTED_FIGURES` records, at each size |

The full reasons are `price.PINNED_SHORTFALLS` and `price.ROW_EXCEPTIONS`,
and `stats.json` carries them in each row's `note`. A pin or an exception
is never a wider band: a row that leaves its band is declared, with a cause,
or the model is fixed. `scripts/fit_price_model.py` refuses to write a fit
that leaves a row out of band undeclared, a pin that no longer holds, or an
exception past its bound. The tests hold the same three at both sizes, and
`uv run python scripts/mutation_check.py --only "price:"` plants a defect in
each price gate, the pin and exception bounds among them, and checks that its
test goes red.

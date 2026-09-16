# synthetic-industrial-products

A generated product catalog for the industrial-supply vertical (cutting tools,
fasteners), built to exercise structured facet extraction in search.

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

Dimension values follow published ANSI/ISO tooling series, which are standards
rather than any retailer's property.

## What ships, and what does not

| | |
|---|---|
| **Ships** | the generator, derived statistics, the synthetic catalog, rendered images |
| **Never ships** | the reference corpus of captured pages (see `.gitignore`) |

## Images

Product images are **dimensioned technical drawings rendered from each
product's own attribute values**, not photographs and not model-generated
imagery. A drawing derived from the data cannot contradict the data — and a
dimensioned drawing shows the reader that cutting diameter and shank diameter
are different measurements, which is the point the catalog exists to make.

### Rendering

```sh
uv sync
uv run sip-render fixtures --out out              # every bundled reference record
uv run sip-render sku 4LU10 --profile card --out out
uv run sip-render batch records.jsonl --out out   # one JSON record per line
```

Two profiles, both sized from where the image is displayed:

| profile | pixels | why |
|---|---|---|
| `card` | 600 × 880 | the catalog card's 150 × 220 box at 4× for high-density displays |
| `detail` | 1400 × 1400 | the detail view's 350 × 350 square box at 4× |

Tools are drawn standing up, shank above and cutting end below. That is how
the industry draws them, and it is the only orientation in which a long thin
tool fills a portrait card instead of floating in the middle of it. The card
carries the silhouette and the two diameter callouts and nothing else — at
150 CSS pixels wide there is room for one idea, and the two diameters are it.
The detail profile adds full dimensioning, an end view, and the attribute
table.

### What the renderer will not do

The drawing may only contain numbers the record contains, so:

* A value that cannot be read **raises**. There is no fallback dimension,
  because a defaulted dimension produces a drawing that disagrees with its own
  record and nothing downstream can tell.
* A record whose dimensions contradict each other — a length of cut longer
  than the tool — is **refused** rather than drawn.
* Geometry that no attribute implies is **left out**, not invented. The depth
  of a socket drive is not published, so the drawing shows the opening the
  socket makes in the head's top face and its true across-flats shape in the
  end view, and stops there. A Torx or cross recess is not drawn at all: one
  across-size does not determine a lobed shape. A head style whose profile
  does not follow from `Head Dia.` and `Head Height` — a button head's dome,
  for instance — is refused.

Some numbers that look like table lookups are not: the countersink angle of
the reference cap screw is computed from its head diameter, head height and
thread size, and lands on 82°, which is what the inch flat-head standard
specifies. The minor diameter of its thread comes from the 60° thread form and
lands on the published 0.1517". Those agreements are checks on the attributes,
not values borrowed from elsewhere.

## Realism

The generator reproduces the defect classes found in real catalogs rather than
smoothing them away: inconsistent unit formatting within a single record,
ragged attribute coverage, and occasional internally impossible dimensions.
A catalog where every field is populated and every value is well-formed does
not look like a real one, and does not exercise a search engine like one.

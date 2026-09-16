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

## Realism

The generator reproduces the defect classes found in real catalogs rather than
smoothing them away: inconsistent unit formatting within a single record,
ragged attribute coverage, and occasional internally impossible dimensions.
A catalog where every field is populated and every value is well-formed does
not look like a real one, and does not exercise a search engine like one.

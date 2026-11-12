# The stress catalog: 10K–50K attribute keys (gen#948)

The stress catalog shows that PRISM's attribute code works at 10K–50K attribute keys, each with
several values, and measures how it scales. It is written and loaded **separately** from the
standard catalog and served by its own persona (elastic/prism-retail-and-industrial#1781). The
products do not need to be realistic, so the generator change is one expansion function,
`src/synthetic_ecommerce_data/stress.py`. It is off unless `--stress-keys` is given.

```sh
uv run ecom-generate build --stress-keys 50000 --out out/stress      # --stress-copies 3 is the default
```

## What the expansion does

It runs on each finished product document (the nested shape):

1. **Fixed names.** Each base attribute has C numbered copies: `color_0001` … `color_<C>`,
   `length_0001` …. C is `--stress-keys` divided by the number of base attribute keys in the
   catalog. A copy's display name is the base's name plus the number (`Color 0007`).
2. **Up to N copies per product.** For each attribute a product has, the original stays and 1 to N
   copies are added (N is `--stress-copies`), their numbers drawn from 1..C.
3. **Values come from the product itself.** Each copy holds a random subset (at least one) of the
   product's own entries for the base attribute, with the same unit and canonical value. A key a
   variant states (a SKU's diameter) gets its copies on that variant, from the variant's entries,
   under the same copy numbers as the product.
4. **Reproducible.** Every draw comes from an RNG seeded by the product id, so two runs give the
   same output.

No category rules, frequency weighting, hashing, word lists or pathological variant (the
maintainer, 2026-11-12).

## What it writes

Without `--stress-keys` (or with `--stress-keys 0`) the build is byte-identical to the standard
one. With it, the build runs the standard audits, then writes only these files into `--out`
(default `out/stress`):

| file | |
|---|---|
| `nested.jsonl` | one document per product, the copies after the originals |
| `flat.jsonl` | one document per SKU, from the expanded nested document by `core/standard.py`'s `flat_documents` |
| `mapping.nested.json`, `mapping.flat.json` | the standard mappings |
| `stress.json` | the census below, and the config (target, N, base keys, C) |

There is no `images.jsonl`: a stress document keeps its standard image ids, and the standard image
bundle serves them. The flat mapping maps each `facets.<key>` as its own field, so at this scale
load the nested shape or a mapping that does not do that. The build refuses an `--out` that holds a
standard build (its `stats.json`), so it is never written over `golden-catalog/`.

## The census

The build prints, and writes to `stress.json`, the product count, the distinct keys, products per
key and distinct values per key (min, p50, p90, p99, max), and the keys on fewer than 5 products.
That last line shows whether C is too high for the product count.

Measured on the default catalog (`--lines 2600`, seed default), on one machine:

| `--stress-keys` | C | distinct keys | products per key p50 / p90 | keys on < 5 products | `nested.jsonl` | build |
|---|---|---|---|---|---|---|
| 10,000 | 72 | 8,306 | 10 / 43 | 2,974 | 47 MB | 12 s |
| 50,000 | 364 | 29,922 | 3 / 11 | 18,749 | 47 MB | 12 s |
| 100,000 | 729 | 48,130 | 2 / 7 | 38,889 | 47 MB | 12 s |
| 200,000 | 1,459 | 71,001 | 1 / 4 | 64,627 | 47 MB | 12 s |

7,360 products, 137 base keys, N = 3; the standard `nested.jsonl` is about 18 MB. The size and
the build time follow N, not the target: a product gets the same number of copies whatever C is.

The base keys are uneven: a key on a few products has few copy numbers drawn, so the distinct keys
fall short of the target. About 50K distinct keys takes `--stress-keys 100000` at this size, and
most of them are then on fewer than 5 products. The census says what a run gave.

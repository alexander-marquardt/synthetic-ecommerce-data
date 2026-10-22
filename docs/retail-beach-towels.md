# The real beach towels (gen#624)

The catalog had one beach towel, "Cotton Velour Beach Towel", and the derivation copied it into
thirteen rows (`<Name> Cotton Velour Beach Towel, <Color>`): one material, one weave, four to seven
words. A real shop mixes them, and a short decoy title ("Beach Towel Stripe Top") beat every one of
them on a text score. The twelve real towels are now authored rows in
`prototypes/retail_drawings/type_specs/beach_towel.py`, under `Home > Bathroom > Beach Towels`.

## What varies

| Component | Values in use |
| --- | --- |
| Material | cotton, organic cotton, polyester, microfibre, cotton polyester blend |
| Weave | terry, velour, waffle, Turkish peshtemal, sand free |
| Feature | quick dry, extra absorbent, oversized, double sided, hooded, extra soft, fade resistant, super absorbent |
| Size | centimetres, as the attribute `dimensions` ("90 x 170 cm") |

Each of material, weave, feature and size is a structured attribute, and the first three are named
in the title, so a filter and the title say the same thing. A title is 7 to 12 words. Six rows
name the one color or print the style comes in ("Extra Absorbent Organic Cotton Terry Beach
Towel, Navy Stripe"); the others leave the color to their SKUs. The color and pattern split is
the one in [retail-color-pattern.md](retail-color-pattern.md): "Navy Stripe" is the color Navy
and the pattern stripe, so no separate pattern entry is authored. One row, "Sun Lounger Towel",
holds no "beach": a shopper's other word for it.

The towels are templates only. `scale.derivable` leaves them out (`BEACH_TOWEL_IDS`), as it does
the decor rows, so no derived style copies a title, and the old `BCHTWL` row of
`breadth_rows.py` is gone. The brands are the catalog's invented ones; no range name is put in front
of a title.

## What is measured

`beach towel` over the ceiling build with [#617](https://github.com/alexander-marquardt/synthetic-ecommerce-data/pull/617)'s
eight decoys merged, ranked by `baseline_rank.rank` (BM25 over the title twice and the
description, `popular=False`), first real towel at rank 9, eight decoys above it:

```
 1 decoy PLT-DY6052   Beach Towel Stripe Top
 2 decoy PLT-DY6050   Beach Towel Stripe Shorts
 3 decoy PLT-DY6051   Beach Towel Stripe Shirt
 4 decoy PLT-DY6054   Kids Beach Towel Robe
 5 decoy PLT-DY6057   Beach Towel Tote Bag
 6 decoy PLT-DY6055   Baby Beach Towel Robe
 7 decoy PLT-DY6056   Beach Towel & Shorts Set
 8 decoy PLT-DY6053   Kids Hooded Beach Towel Poncho
 9 REAL  BRD-BCHXSV   Extra Soft Cotton Velour Beach Towel, Coral
10 REAL  BRD-BCHDWF   Double Sided Cotton Polyester Blend Waffle Beach Towel
11 REAL  BRD-BCHOPV   Oversized Quick Dry Polyester Velour Beach Towel, Pink Stripe
12 REAL  BRD-BCHSAM   Super Absorbent Microfibre Terry Beach Towel with Zip Pocket
```

With the popularity boost (the default of `rank`) the top 12 are the eight decoys, then four towels
that are not beach towels ("Quick-Dry Swim Towel", "Cream Face Towel", "Tea Towel Hook Rail", "Tea
Towel Hanger, 4 Pack"); the first real towel is at rank 13. Inside the Home department (the
interpreted view, where the decoys are dropped), the first real towel is at rank 5, behind those
four short-titled towel products.

## Depends on, and open

* The decoys are #617's (`feature_decoys/beach_towel.py`). Without them the measure above has
  nothing to rank against, so `tests/test_retail_beach_towels_624.py` pins the towels' own titles
  and attributes and does not rank.
* The one-brand rule for name words (#623) is not on main; the towels carry no range name, so
  there is nothing for it to move.
* `tests/test_retail_beach_towel_decoys_605.py` (on #617) asserts a real towel in the raw top 12
  and a real towel first in the Home view. Both hold only while the real titles are short. With
  these titles they do not, so the one of the two PRs that merges second must change those two
  assertions to the ranks above.

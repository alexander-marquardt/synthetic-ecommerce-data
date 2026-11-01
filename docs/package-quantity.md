# Package quantity: the second variant dimension

A distributor sells one end mill loose, in a 2-pack and in a 5-pack, and not every size in
every pack. So on square end mills, ball end mills and foam ear plugs (`pack.AXES` in
`domains/industrial/pack.py`) a product's variants run over two dimensions: its size and
its `Units per Pack` (gen#14). Each (size, quantity) pair that exists is a child SKU with
its own price, title and card image. `variant_axes` names both.

| type | quantities | products | SKUs at a quantity above 1 |
|---|---|---|---|
| Square end mills | 1, 2, 5, 10 | 16 | 130 |
| Ball end mills | 1, 2, 5, 10 | 9 | 70 |
| Foam ear plugs | 1, 10, 25, 50 | 1 | 3 |

Only those products are packed. Every other end mill stays a run of single sizes, and a
hex bolt's `Units per Pack` stays what it was: a value on the line, drawn nowhere.

## The matrix is sparse

Quantity 1 offers every size. Each quantity above it offers half the sizes of the one before
(`pack.offered`), as one contiguous run of sizes that starts at a random place. Eight sizes
give 4 at the first pack, 2 at the second and 1 at the third, so the top of the ladder may sell
only a single size, and a search for a size at a quantity the product does not offer finds
nothing.

## Price, title and description

A pack is cheaper per piece. Its price is `price * quantity ** 0.79` (`price.pack_price`), so
a 5-pack costs 3.56 singles, then takes the catalog's pooled price endings: the pack price is
never a linear multiple of the single's.

The title leads with the count, `5PCS ` followed by the single's title. A title that would
pass 100 characters drops its last whole `, ` segment, so a value is never cut in half. The
description opens with that title and every SKU on the axis, a single too, says how many it
holds: `5 per pack.` or `1 per pack.`.

Foam ear plugs are sold by the box, and their sizes spread over the whole range the census
measured for the type. So a plug's single reads down the same curve from the mean of the
line's boxed prices, at quantity 50 (`pack.PRICED_AT`). A Corded and an Uncorded plug then
cost about the same a piece.

## The card shows the pack, the detail sheet shows the part

A pack's card (`image_url`) is its own drawing, with the count read from the published
`Units per Pack`: one part whole and upright, in front of a fan of the other N - 1 as tilted
outlines, leaning to alternate sides (`drawing.model.fan`). A different count draws different
bytes. Rotation is allowed here and nowhere else in the drawings.

Its detail sheet (`image_detail_url`) is the single's drawing, the same file the single
serves. Only a pair that exists has a card, and `core/emit.py` refuses a detail image from
another product. `images.jsonl` keeps one row per SKU.

The ear plug ladder stops at 50 because a fan of a hundred outlines inks over into a solid
wedge, and the count has to be seen.

## Filtering on quantity

`Units per Pack` is the one tabled quantity offered as a range: a shopper asks for
`quantity > 10`, and a list of ladder values cannot answer a threshold (`RANGE_QUANTITIES` in
`prism/derive.py`). The value is on `facets_num.units_per_pack`, so this returns the 50-pack
and the 25-pack of a plug and not its 10-pack:

```json
{"range": {"facets_num.units_per_pack": {"gt": 10}}}
```

Every breadth `Units per Pack` is numeric too, so the filter covers the types that publish it
on the line.

## Building it

The pass is additive, like the [grouped products](../README.md#grouped-product-families):
the pack products run last, from streams of their own (`key:pack`), so no line built before
them moves. The ear plug line takes the axis in place, as the one breadth row that has one.
`GeneratorConfig(pack_axis=False)` builds the catalog without any of it.

`tests/test_pack_axis_14.py` holds all of this. Its drawing test counts the outlines on a card
against the published quantity, so it fails if a card draws too few as well as too many.

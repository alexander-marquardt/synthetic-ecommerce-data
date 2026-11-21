# Produce that fills its picture (gen#1111)

A pack of loose fruit or vegetables (`kit_produce.produce_pile`: loose, in a net or in a
clear bag) is drawn big, round and fresh. Each layout in `PILES` (1 to 7 fruits) gives its
fruits one size, and every fruit is scaled to the same painted area at that size whatever its
own shape's size, so a lemon and a grape fill the same space. Each fruit carries a gloss (a
radial highlight up-left and a shade down-right over its body), and the pile stands on a
`class="ground"` shadow. The bag and the net are enlarged round the bigger pile.

**Fill is measured against the product area**, the plain sheet's 344 x 334 box
(`house_styles.TURN_AREA`), and counts only the fruits (`<g class="fruit">`): a bag's film, a
net, a tag and the shadow do not count. `sheet_cover.cover` rasterizes the SVG on a grid and
returns the painted share of a box. A share of the whole 400 x 400 image cannot reach one half
for a round fruit once a house style frames it, so the contact sheets report both.

| shapes | floor | measured (counts 3-7, and 1-2 for a round body) |
|---|---|---|
| orange, lemon, apple, strawberry, tomato, onion, potato | 0.50 | 0.52 to 0.79 |
| banana, carrot, cherries | 0.25 (slice 3 raises it to 0.50) | 0.38 to 0.57 |

`tests/test_produce_fill_1111.py` pins the floors over every `FRUIT` x pack form x count, the
gloss on each fruit and the ground shadow. A banana, a carrot or a cherry pile needs its own
arrangement (a hand, a bunch, a heap) to fill a square, which slice 3 draws.

**Each SKU draws its own pack (slice 2).** A grocery line's drawing is made from its first
pack, and before slice 2 every other SKU kept it: a Single lemon drew a pile of 3, a 1 kg bag
drew the Single's 3 loose fruit, and a 4 pack lay loose. `kit_produce.sku_pile` now reads a pack's
form and count from its own `pack_size` (`pack_form`: a Single lies loose, a count pack is netted,
a weight is bagged) and its `units_per_pack` or `net_weight_g`; `grocery._drawing` uses it for the
first pack and `pack_copies.pile_count` for every other. `fruit_count` draws a count pack from 1
(a Single is one fruit) and clamps only a weight to 3-7. `pack_scale.factor` gives a
`produce_pile` no factor: its count shows its size, where a factor set a Single's count of 1
against 1 kg's 1000 g and drew the one fruit at 0.6.

A product of one pack (PLT-LEMONS, the class-model and authored piles) keeps its own pile.
A line whose weight packs all hold 7 or more fruits (grapes, berries, cherries, carrots) draws
one 7-fruit bag at each weight; slice 3's heaps are where they can differ.

`tests/test_produce_served_1111.py` pins it over `image_release.render`'s plain-sheet output for
the lemon, orange, apple and onion lines and PLT-LEMONS: each pack's own count and form, a
different count per pack of a line, no `pack_scale` factor, and fruit over half the product area.

| SKU | before slice 2: fruits, factor, product area | after |
|---|---|---|
| GRC-LEM-0001 Single / 4 pack / 1kg | 3 at 0.6, 21% / 4 at 0.6, 26% / 3, 58% | 1, 56% / 4 netted, 71% / 7 bagged, 61% |
| GRC-ORA-0001 Single / 4 pack / 1kg | 3 at 0.6, 23% / 4 at 0.6, 26% / 3, 64% | 1, 58% / 4 netted, 73% / 5 bagged, 68% |
| GRC-APP-0001 Single / 4 pack / 1kg | 3 at 0.6, 24% / 4 at 0.6, 26% / 3, 66% | 1, 59% / 4 netted, 73% / 6 bagged, 74% |
| GRC-ONI-0001 500g / 1kg | 3 at 0.79, 39% / 3, 61% | 3, 61% / 7, 66% |
| PLT-LEMONS (a bag of 4) | 68% | 68% (unchanged) |

Served before and after slice 2 (house style on, captions give both shares):

![Served produce before gen#1111 slice 2](../images/produce-served-1111-before.png)

![Served produce after gen#1111 slice 2](../images/produce-served-1111-after.png)

Slice 1's served images (`image_release.render`), share of the whole image the fruit paints:

| SKU | before | after slice 1 |
|---|---|---|
| GRC-LEM-0011 Single / 4 pack / 1kg | 1.6% / 2.2% / 4.4% | 10.8% / 13.2% / 29.9% |
| GRC-ORA-0001 Single / 4 pack / 1kg | 1.9% / 2.5% / 5.1% | 12.8% / 14.5% / 35.3% |
| PLT-LEMONS (a bag of 4) | 4.9% | 30.5% |

Before:

![Produce piles before gen#1111](../images/produce-fill-1111-before.png)

After slice 1:

![Produce piles after gen#1111 slice 1](../images/produce-fill-1111-after.png)

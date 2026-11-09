# Barry Plotter, an invented franchise range named only in the text (gen#925)

The invented kids' films ([kids-films-887.md](kids-films-887.md)) sell about 30 SKUs each, from
one brand at one price per type, so a film phrase with a filter (`under 30`, `age 8`, `on sale`)
leaves one product or none. Barry Plotter is large enough to filter. It is an invented
book-and-film series about a boy gardener and his enchanted allotment, sold in six groups by
fourteen existing houses at a value, a standard and a premium price
(`src/synthetic_ecommerce_data/domains/retail/barry_plotter.py`).

The name is a play on a famous name, and nothing else of the original appears. The range has its
own motifs, one per design:

- Talking Scarecrow
- Moonlit Glasshouse
- Enchanted Allotment
- Hatchlings (creatures that hatch from enchanted packets)
- Snail Parade
- Compost Dragon
- Potting Shed
- Wheelbarrow Race

No motif word is a product type, a category or a color word of the catalogue, and no description
says "Barry's": the output standard would read its "s" as the size S.

As with the films, the name lives only in the title and the description. Each product keeps the
brand of the house that makes it, carries no `product_line` and sits in the category of its
type, and no attribute names the range (`barry_plotter.structured_names`). Every description says
the product is "from the Barry Plotter films".

## The range

Counted on the `--skus ceiling` build (`tests/test_barry_plotter_925.py` checks these figures):

| Group | Types | Brands | Products | SKUs |
|---|---|---|---|---|
| Building sets | building set | Pipwick Toys | 40 | 40 |
| Kids' clothing | tee, sweatshirt, hoodie, pyjamas, fleece all-in-one | Little Fernby, Wrenfield, Larkmoor, Pipwick Toys, Puddlecombe Toys, Quillon Sleep | 40 | 200 |
| Adult clothing | tee, pullover hoodie, knitted jumper, lounge joggers, socks | Harbour & Pine, Larkmoor, Wrenfield, Calderby & Lune | 40 | 184 |
| Accessories | backpack, lunch box, drinks bottle, beanie, knitted scarf | Larkmoor, Harbour & Pine, Hearth & Table, Little Fernby, Brackenmere Home, Wrenfield | 40 | 80 |
| Home | mug, duvet set, cushion, star night light | Brackenmere Home, Hearth & Table, Thistle & Wren, Little Fernby, Quillon Sleep, Lanternby, Calderby & Lune, Puddlecombe Toys | 32 | 56 |
| Party and stationery | party bags, paper party cups, birthday cake, A5 notebook, sticker sheets | Lanternby, Thistle & Wren, Cobble & Kiln, Crofter's Bakehouse, Hearth & Table, Calderby & Lune, Little Fernby, Pipwick Toys | 40 | 48 |
| **Total** | | | 232 | 608 |

Each type sells one product per motif. The motifs take the value, standard and premium price in
turn and the type's houses in turn, so `barry plotter hoodie` lists products from several brands
at several prices:

| Type | Prices (value, standard, premium) | Sizes |
|---|---|---|
| Kids' tee | £7, £10, £14 | 3-4 to 9-10 Yrs |
| Kids' sweatshirt | £18, £24, £32 | 3-4 to 9-10 Yrs |
| Kids' hoodie | £22, £30, £36 | 3-4 to 9-10 Yrs |
| Kids' pyjamas | £16, £22, £30 | 3-4 to 9-10 Yrs |
| Kids' fleece all-in-one | £22, £30, £36 | 3-4 to 9-10 Yrs |
| Adult tee | £16, £24, £32 | XS to XL |
| Pullover hoodie | £30, £40, £55 | XS to XL |
| Knitted jumper | £32, £38, £48 | XS to XL |
| Lounge joggers | £26, £32, £40 | XS to XL |
| Socks, pack of 3 | £6, £8, £12 | S/M, M/L, L/XL |
| Backpack | £24, £34, £45 | |
| Lunch box | £6, £9, £14 | |
| Drinks bottle | £8, £12, £18 | |
| Beanie | £8, £12, £16 | One Size |
| Knitted scarf | £14, £20, £30 | |
| Mug | £7, £10, £14 | |
| Duvet set | £25, £38, £105 | |
| Cushion | £16, £24, £32 | 45 x 45cm |
| Star night light | £12, £18, £24 | |
| Party bags | £4, £6, £8 | |
| Paper party cups | £3, £4, £6 | |
| Birthday cake | £14, £20, £32 | |
| A5 notebook | £4, £7, £12 | |
| Sticker sheets | £3, £4, £5 | |

The building sets come in five piece counts per motif, each a SKU of its own: 60 pieces (ages 4
and up, £4.99 to £6.99), 220 (6 and up, £12.99 to £16.99), 520 (8 and up, £24.99 to £34.99),
1,100 (12 and up, £44.99 to £59.99) and 2,500 (adult builders, £99.99 to £149.99).

Clothing comes in several colors, so a color filter on the range still returns results. The
kids' hoodies sit in a leaf of their own, Kids > Tops > Hoodies. The issue named a few kinds no
type of the catalogue sells: pencil cases, posters and dressing-up costumes are left out, a
onesie is the All-in-One type, lounge pants are Joggers, a bottle is the Travel Cup type (titled
"Drinks Bottle") and a cap is a beanie of the Hat type.

## What a filter on the range returns

Each figure is a count of SKUs, the hits of an ungrouped search:

| Filter on the range | SKUs | Asked for |
|---|---|---|
| under £30 | 377 (62%) | 150 or more, about 60% |
| on sale | 154 (58 of 232 products, 25%) | 80 or more, about 25% |
| hoodies | 80, from 6 brands | 15 or more, from 3 brands or more |
| kids' pyjamas in 7-8 Yrs | 16 | 10 or more |
| building sets under £50 | 30 | 15 or more |

A quarter of the range is on sale, against about 8% of the catalogue. The range takes no
department's share: one product in four of each type is reduced, in a pass of its own
(`barry_plotter.SALE`, `barry_plotter.on_sale`), and the department sale passes leave it out.

## What a search meets

- **The name is in the title and description only.** Five products name it in the description
  only (`barry_plotter.DESCRIPTION_ONLY`): the Talking Scarecrow kids' pyjamas, pullover hoodie,
  mug, A5 notebook and 60-piece building set. A search can rank a description-only match against
  a title match.
- **Words the range shares with the rest of the catalogue:**

  | Word | What the rest of the catalogue holds |
  |---|---|
  | `barry` | No other product. It is one letter from `berry`, so a spelling corrector may rewrite it. |
  | `berry` | A word of eight other products' text in the templates (five meads, oranges, a cake, a body mist), and inside a word of many more (strawberry, raspberry, blueberry). |
  | `plotter` | No other product: the catalogue sells no pen plotter. |
  | `plot` | Fenwold Nursery's "Plot" garden series, derived in the scaled builds (plants, trees, bulbs: "Fenwold Nursery Plot Woolly Thyme Plant"). A stemmer that takes `plotter` to `plot` meets them. |

  Phrase matching has to keep the name together: elastic/prism-retail-and-industrial gets a
  special-phrase row for it (filed with this issue).

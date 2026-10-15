# Retail clothing depth: the Mens slice (gen#310)

`prototypes/retail_drawings/mens_depth_rows.py` adds Mens trousers and chinos, shirts, polo
shirts, coats and jackets, suits and tailoring, underwear and socks as distinct products, each
with fit, material and, where it applies, collar and sleeve length. The floors are pinned by
`tests/test_retail_mens_depth_310.py` over `scale.templates()`. Knitwear is gen#309; Womens and
Kids are later slices.

## Text-match decoys (gen#294)

Every added type carries three decoys of each of seven classes, 168 in all. Until gen PR #306
(`decoy_rows.TABLE`) merges they are registered in `mens_depth_rows.TABLE`, with the class, the
misleading word, the query it targets and the policy that repairs it.

A decoy sits in a leaf its fields agree with (a "Wool-Free Coat" is not in Wool Coats), spread
over the type's sibling leaves, and carries the sleeve length of its leaf. Its color field is its
one true color: `main_colors.complete` skips decoys, and the real Socks rows offer Yellow. The
product floors count decoys; the tests also hold a floor without them.

| Class | Decoy | Example |
|---|---|---|
| 1 color | a trim names another color | "Mens White Chinos with Red Stripes" is white |
| 2 category word | another category's noun as a modifier | "Mens Shirt Collar Blazer" |
| 3 audience word | a sibling cut | "Mens Boyfriend Fit Chinos" |
| 4 feature absent | a feature named and missing | "Mens Wool-Free Coat" |
| 5 shade in the description | a fancy title, the shade in the text | "Mens Moonbeam Chinos" are Ivory |
| 6 incidental word | a range name, carried as a `range` attribute | "Mens Red Tarn Chinos" are not red |
| 7 invented brand | a brand holding a color or category word | "Black Curlew", "Yellow Plover", "Jacket Wren" |

The three class 7 brands each have a house style whose lockup text is the brand name. The text
agreement check (`standard.text_contradictions`) treats the document's brand as its own value, so
a brand such as "Black Curlew" is not read as naming a color.

## Suits and tailoring (gen#215)

`Mens/Suits & Tailoring` holds five product types, each drawn as its own shape by
`prototypes/retail_drawings/kit_suits.py` (`suit_jacket`, `suit_trousers`, `waistcoat`,
`dinner_suit`, `formal_accessory`), and each carrying its own decoys (the same seven classes):

| Type (`product_type`) | Leaf | Key attributes (structured) | Shape params |
|---|---|---|---|
| Suit Jacket | Suit Jackets, Blazers | `fit`, `material`, `lapel`, `buttons`, `occasion` | `fit`, `lapel`, `buttons` (two or three) |
| Suit Trousers | Suit Trousers | `fit`, `material`, `leg_length` | `fit`, `leg` |
| Waistcoat | Waistcoats | `fit`, `material`, `buttons` | `fit`, `buttons` |
| Dinner Suit | Dinner Suits | `fit`, `material`, `lapel` | `fit`, `lapel` |
| Formal Accessories | Formal Accessories | `material`, `accessory_type` (tie, bow tie, braces, cummerbund, pocket square) | `item` |

The kit draws three cuts (slim, tailored, regular), so a record of fit `Relaxed` is drawn regular.

A matching set is a jacket, trousers and waistcoat sharing one `suit_set` name, one brand, one
cloth (`material`), one fit and the same colors (`mens_depth_rows.SETS`, ten sets). Not yet here:
the women's trouser suit and the boys' suit (age sizes, two or three pieces), which need the
Womens and Kids roots and their own decoy plan (`decoy_apparel.TYPES`), and the jacket length and
trouser leg as SKU axes (the leg length is a style attribute for now).

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

| Class | Decoy | Example |
|---|---|---|
| 1 colour | a trim names another colour | "Mens White Chinos with Red Stripes" is white |
| 2 category word | another category's noun as a modifier | "Mens Shirt Collar Blazer" |
| 3 audience word | a sibling cut | "Mens Boyfriend Fit Chinos" |
| 4 feature absent | a feature named and missing | "Mens Wool-Free Coat" |
| 5 shade in the description | a fancy title, the shade in the text | "Mens Moonbeam Chinos" are Ivory |
| 6 incidental word | a range name, carried as a `range` attribute | "Mens Red Tarn Chinos" are not red |
| 7 invented brand | a brand holding a colour or category word | "Black Curlew", "Yellow Plover", "Jacket Wren" |

The three class 7 brands each have a house style whose lockup text is the brand name. The text
agreement check (`standard.text_contradictions`) treats the document's brand as its own value, so
a brand such as "Black Curlew" is not read as naming a colour.

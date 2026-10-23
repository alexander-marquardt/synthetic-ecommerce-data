# Womens sizes above UK 16 (gen#434)

The Womens UK size run stopped at 16 (some styles at 18 or 20), so a query for a dress in size 22
read the size and found no dress that carried it. `plus_sizes.py` runs over `scale.templates()`:
three in five of the Womens styles whose SKUs carry a bare number `size` (dresses, tops) or
`size_uk` (jeans, with its EU and US sizes at UK + 28 and UK - 4) are carried on to UK 24.
Trousers measure by `waist` and knitwear is letter-sized, so neither is changed.
Each new SKU copies the largest-size SKU of its color; the new SKUs are appended, so no SKU id
moves, and a derived style inherits the longer run. Decoys of `decoy_rows.py` and
`decoy_product_words.py` keep their run. `tests/test_retail_plus_sizes_434.py` pins at least 30
Womens dresses at UK 22 and the chart.

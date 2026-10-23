# Womens dresses in UK numeric sizes 6 to 20 (gen#621)

"size 20 dress" filters the dresses by `facets.size_uk: 20`, but the dresses sized by number stored
a bare `size`, so none carried `size_uk`. The discounted regular-range dresses of
`distractor_rows.py` (`DSL`, the Wrap Midi, Shirt and Maxi dresses) now run UK 6 to 20 with
`Style(uk_chart=True)`: each SKU stores `size_uk`, `size_eu` and `size_us` from the Womens chart
(`variants.WOMENS_WAIST`, UK 20 = EU 48 = US 16) the way the jeans do, one variant per color and
size, and `size_options` lists the three. `plus_sizes.py` carries three in five of them on to
UK 24 in the same keys. The petite dresses and the tops keep a bare `size`.
`tests/test_retail_dress_uk_sizes_621.py` pins the dresses, the 6 to 20 run and the UK 20 row.

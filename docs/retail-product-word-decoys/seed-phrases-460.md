# Seed phrases (gen#460)

The homepage seed queries are two or three words ("leather boots", "skinny
jeans", "tea dress") and the Best tier requires every term, so a decoy with the bare noun never meets
them. Thirty-four rows serve thirteen seeds of Womens, Mens and Kids clothing and shoes, at least
three products each, and every row holds every word of each phrase it serves in its title or text: a
slim belt cut for high rise jeans, a jersey jegging with the skinny jeans look, clip hangers for jeans,
a fashion doll in barrel trousers, a garment bag for a tea dress, a boot care kit, waxed laces,
a mesh bag for running shoes. A row names the phrases in `seeds` and keeps its true type, so the
department policy drops a Home or Toys row and the category policy a Womens one. A color word is the
product's own (a navy bag for navy dresses), never a stray one. The bare seed `boot` keeps its
class-8 rows. `tests/test_retail_seed_phrase_decoys_460.py` holds the census: two decoy products
in the first 12 for each seed with policies off, every query word required, the rank of the
prototype's baseline; the live number is read on the next loaded index.

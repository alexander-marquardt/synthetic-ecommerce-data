# Retail class-8 decoys: the shopper's product noun on a different product (gen#326)

A class-8 decoy has a title that holds the product word of a demo query ("dress", "sofa",
"jumper", "tie") while the product is something else: Dress for Success shoes, a sofa cover,
jumper cables, bow tie pasta. The structured fields tell the truth (category path, product type,
color, drawing). A title names at most the misleading color ("Sofa Cushion, Blue Trim" is a
cream cushion piped in blue; "Dress for Success, Red Laces" are black shoes with red laces) and
the drawing renders that detail. The rows are generated from
`src/synthetic_ecommerce_data/domains/retail/decoy_product_words.py` and pinned by
`tests/test_retail_product_word_decoys_326.py`. A new decoy set is one file,
`feature_decoys/<topic>.py`; `decoy_contract.violations` (run by `tests/test_feature_decoys_513.py`)
checks every row of it: the id is unique, the title carries a word of the query, a structured
field contradicts it, the policy exists, and the drawing renders.

The fixing policy is the one that reads the structured fields: `category` (the noun's own node,
for example Dresses, drops the row), `department` (a cross-department row sits in another root,
so the All Departments persona drops it), `color` (the brand rows in every color but blue).
Rows the English stemmer would match ("dressing" for dress, "coated" for coat) are not planted:
the prototype search folds a plural only, and no row that does not rank is counted. Blue Bull is a
class-7 color-word brand on footwear with its own house style.

Each new real type carries a floor of three ordinary products, listed in `FLOOR`.

**A feature's own section** (the care cream, Sports & Outdoors, cups, cycling accessories, gifts,
the gift card, seed phrases, electronics) is a page in
[retail-product-word-decoys/](retail-product-word-decoys/), one file per topic and issue, named
`<topic>-<issue>.md`. Every decoy PR appended its section here, so any two conflicted (gen#659);
`scripts/check_no_registry_append.py` refuses a bold section lead added to this page.

**The table of every decoy** (query, noun, product id, title, true type and fixing policy) is
built, not committed: `uv run python scripts/build_derived.py --out build/derived` writes
`docs/retail-product-word-decoys-table.md` from `decoy_product_words.TABLE`, and CI uploads it in
the `derived` artifact. Every decoy PR pasted the whole table here, so any two conflicted (gen#513);
`scripts/check_no_registry_append.py` refuses a table line added to this page.

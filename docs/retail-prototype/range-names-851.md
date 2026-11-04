# Range names with no number, and a color as a SKU (#851)

A derived style of a line-grammar family used to take a model of a lead word, a sub-model and a
generation number. On a cup set that read "Brackenmere Home Supper 6 Set of 4 Porcelain Espresso
Cups in Gift Box, Black", next to "Supper 9 …, Green" from the same brand. No retailer names a cup
set that way. Each of those was also a product of one SKU, split from the brand's grouped
product by a color and a numbered range alone.

**A derived range is a plain word.** Outside the cleaning and beauty families, a derived style's
model is one of its brand's lead words alone, "Larchwood Living Gather Set of 4 Porcelain
Espresso Cups in Gift Box" (`line_grammar.Deal.owned`). A lead word that any template's title,
description, brand or attribute value also uses is not dealt (`line_grammar.text_words`):
without a number, "Toast" would be the range of "for toast, cake or a starter", and "Bright" of
"Bright Orange Crew Neck Tee". So the families gained words no text uses (storage, kitchen,
lighting, sport and tools), and eight words a description used were replaced (Feather, Border,
Patio, Grow, Whisk, Roast, Starter, Smooth). An authored model, and a cleaning or beauty model, may
still carry a sub-model and a number. `line_grammar.is_model` reads a lead word alone as a model.

**A color is a SKU, not a product.** A derived style whose title-shown values its template, or
an earlier sibling, already shows used to carry its hero color alone, with the color named in
its title. It now carries every color of its template, hero first, and its title names none
(`scale._draw`). So it is its brand's one product of the kind. A second one from the same brand
would be a twin (`scale_text.twin_key`), so the build makes none, and different brands stay
separate products. A cleaning or beauty style (a lipstick shade, a scent) keeps the older rule
until those families drop their numbers.

**The report.** `scale --report` has `single_sku_kinds`: each product type where most products
have one SKU although one of its products has two colors or sizes, with its counts.

At the ceiling build the build has fewer products and more SKUs (`scale --report` measures them;
a total is never typed here, `tests/test_retail_figures_162.py`). The numbered ranges left are the
cleaning and beauty models and the authored bra, jeans, running shoe and walking boot lines. Cup
sets and travel cups are one product per brand, each with several colors as its SKUs.

The guards are in `tests/test_retail_scale_range_names_851.py`.

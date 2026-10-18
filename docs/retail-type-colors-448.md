# The colors and attributes a type really comes in (gen#448)

gen#275 gives every color-bearing type the six main colors, so "red shirt" finds a shirt. A type
that is not sold in some of them declares it, with the colors it does come in and why, in
`prototypes/retail_drawings/type_colors.py` (`RESTRICTED`, keyed by the category-path prefix; the
longest prefix wins):

| Path | Comes in | Why |
|---|---|---|
| Mens > Suits & Tailoring (blazers, jackets, trousers, waistcoats, dinner suits), Mens > Trousers > Formal Trousers | Black, Navy, Grey, Charcoal, White | tailoring comes in dark suiting colors and white |
| Kids > School Uniform > School Trousers | Black, Navy, Grey, Charcoal | the dress code of a school |
| Kids > School Uniform > School Shirts | White, Blue | white or pale blue by the dress code |
| Kids > School Uniform > School Skirts, School Pinafores | the trouser colors, Brown, Green, Burgundy | the dress code of a school |
| Womens > Hosiery > Tights | Nude, Natural, Black, White, Navy, Grey, Charcoal, Brown, Burgundy, Teal, Beige, Cream | skin tones and dark opaque colors |
| Home > Heating & Cooling > Fans > Ceiling Fans | White, Black, Silver, Brown, Gold, Copper, Bronze, Nickel | a ceiling fan's color is its metal or wood finish |

One table is read three times: `main_colors.complete` adds a missing main color only to a style
whose type comes in it, `main_colors.missing` asks a restricted type for only the main colors it
comes in (the gen#275 gate), and `mens_depth_rows` palettes and the decoy clone picker
(`decoy_apparel`) take only a permitted color. A near-neutral shade (Ivory, Cream, Taupe...) is a
real finish of cloth and is allowed on every restricted type. `main_colors.offered` counts
"Black Leather" as the color Black, so completion adds no second "Black" beside it.

## Material is a cloth

A pool entry that is not a cloth is carried by its own attribute (`type_colors.CARRIED_AS`):
"Crease Resistant", "Easy Iron" and "Non-Iron" are `Finish`; "Checked" is `Pattern` = Check (and
the color options are checks); "Arch Support" and "Moisture Wicking" are `Feature`. "Recycled" is
a sourcing claim, carried as `Material` = Recycled Polyester. The description names the cloth
once, with a plural-aware article ("Black suit trousers", never "A black suit trousers"), "wool-free:
made in cotton" keeps its hyphen, and a formal-trousers leaf says "formal trousers", not "chinos".

## One department per path

Shoe Polish, Shoe Laces and the Shoe Care Kits sit under Mens > Accessories > Shoe Care in the
Footwear department; a test asserts that one category path has one department.

## Guard

`tests/test_retail_real_attributes_448.py`, with ten mutation rows
(`scripts/mutation_rows_real_attributes_448.py`, `--only "real attributes 448:"`). The guard reads
the Material leaks in the `mens_depth_rows` pools; a Material leak elsewhere (a Belted, Hooded or
Packable value) is not covered.

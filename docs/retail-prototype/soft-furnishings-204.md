# Soft furnishings (gen#204)

Six types, each a leaf of its own and a spec of its own: Curtains, Blinds, Rugs and Throws under
Home > Soft Furnishings, and Bath Mats and Shower Curtains under Home > Bathroom. Before this, a
search for a curtain, a rug or a throw found nothing or a cushion, and width, drop, heading, pile
and room filters had nothing to narrow.

| Spec file | Product type | Styles | Key attributes (each a structured entry) |
| --- | --- | --- | --- |
| `type_specs/curtains.py` | Curtains | 4 | heading, lining, material, panels |
| `type_specs/blind.py` | Blind | 4 | blind type, material, fits, blackout, cordless |
| `type_specs/rug.py` | Rug | 4 | shape, pile, material, indoor or outdoor, washable |
| `type_specs/throw.py` | Throws | 3 | material, use, edge, reversible |
| `type_specs/bath_mat.py` | Bath Mat | 3 | material, texture, non-slip, quick dry |
| `type_specs/shower_curtain.py` | Shower Curtain | 3 | material, waterproof, weighted hem |

Each style comes from a different brand within its type and carries the six main colors (and more
for some). `softfurn_rows.py` holds the shared helpers (`SoftRow`, the paths, brands, colors and
the decoy clone helper); `kit_softfurn.py` draws the six shapes, and a param changes the drawing
(`heading`, `lined`, `kind`, `form`, `pile`, `edge`, `texture`, `hem`).

A size is measured, never a word in a title. A SKU carries the width and the drop (`width_cm`,
`drop_cm`) for curtains, blinds and shower curtains, the width and the length (`width_cm`,
`length_cm`) for rugs, throws and bath mats, and the diameter (`diameter_cm`) for a round rug.
`width_cm`, `length_cm` and `diameter_cm` are shared options in `export.SHARED_OPTIONS`; `drop_cm`
is declared by the three specs that use it as `Option("drop_cm", "drop_length", "Drop length",
"CMT")` (an identical redeclaration is allowed). `SoftRow.skus()` splits a size written
`"117x137"` into its two fields.

The throws leaf was already in the legacy list (`Home|Throws`, the product type the word decoys
use). That line is removed and `LEGACY_CEILING` is 294. The three ordinary throws that the word-decoy
floor carried (`FY040` to `FY042`, in `decoy_product_words.py`) are removed with it, as the throw
spec holds the type's ordinary products now. The four class-8 throws (`DY36`, `DY62`, `DY702`,
`DY720`) stay where they are and are listed in `tests/test_retail_type_specs_351.py` as decoys that
sit beside a spec type.

The model names of the five other types come from `line_grammar_families/softfurn.py` (the
throws are in the `soft` family already), so a scaled build leads no title with an invented range
word.

Decoys. Each spec carries three text-match decoys in its own department and type (`DSF01` to
`DSF18`, classes 1, 2, 3, 4 and 6): a trim or cord in a color the product lacks, a feature the
title suggests and the fields deny ("Cordless Look Roman Blind" on a cord), a category word
("Door Mat Style" on a rug) and an incidental word ("Garden Party" curtains). Their structured
fields tell the truth. `tests/test_retail_softfurn_204.py` pins the depth, the units, the
drawing, the six colors, the decoys and the figures.

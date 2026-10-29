# Product-line grammar of clothing and footwear (gen#663)

A range name that leads a title the way a brand does reads as a second brand. Public retail
listings name a model from plain words instead: a word, an optional sub-model, a number or a code,
then the kind ("Ghost 18 Road Running Trainers"). gen#662 did this for running shoes, bicycles,
dress shoes and appliances; gen#663 does it for the other clothing and footwear kinds. The grammar
is `src/synthetic_ecommerce_data/domains/retail/line_grammar.py`, which derives `FAMILIES` (a product type to its
family) from the modules of `src/synthetic_ecommerce_data/domains/retail/line_grammar_families/` (gen#513): a
vocabulary lives in a module per family (`bra.py`, `jeans.py`, `tee.py`, `trainers.py`,
`boots.py`, `casual.py` for the six below), each exposing `KINDS`, `LEADS`, `SUBS` and `NUMBERS`.
A lead two modules hold is refused at import, so the home families gave up the words an authored
bra or jeans row uses (furniture Comfort, Heritage and Core are Settle, Tradition and Heart; decor
Jolly and Delight are Mirth and Gladness; toys Hop is Leap).

A model reads `<lead> [<sub>] <number>`, and the title reads `<brand> <model> <descriptors> <kind>`.
The sub-model is one of Pro, Max, Elite, Edge, Lite, Plus. The number is a generation (2 to 9), or
for jeans a fit code (101, 205, 312, 418, 520, 625, 731, 840). Every lead is a plain English word
of public retail listings, never a coined brand-sounding word and never a place name or a first
name. A range belongs to one brand (gen#642): an authored lead is reserved for its brand, and the
rest of the pool is dealt over the brands in name order. A title never repeats its brand back to
back.

| Family | Kinds | Lead words (sample) | A real title from the 10K build |
|---|---|---|---|
| bra | Bra | Comfort, Support, Anytime, Balance, Contour | Bramblewood Comfort 2 Underwired Balcony Bra |
| jeans | Jeans | Original, Heritage, Core, Authentic, Rider | Ottery Denim Original 101 High Rise Skinny Jeans |
| tee | Tee, T-Shirt | Regular, Casual, Weekend, Laidback, Varsity | Little Fernby Varsity Max 2 Slim Fit Ribbed Tee, Green |
| trainers | Trainers, Platform Trainers, Plimsolls, Barefoot Shoes | Dash, Cruise, Baseline, Pitch, Orbit | Treadmoor Blaze 9 Leather Platform Trainers |
| boots | Walking, Chelsea, Ankle, Chukka, Knee High, Safety Boots, Wellies | Summit, Ascent, Alpine, Grit, Puddle | Cobbleway Alpine Pro 5 Suede Chelsea Boots |
| casual | Espadrilles, Slippers, Wedges, Mules, Sandals, Clogs, Jelly Shoes | Siesta, Fiesta, Sorbet, Languid, Tropic | Cobbleway Fiesta Pro 5 Block Heel Mules |

The guards in `tests/test_retail_scale_clothing_footwear_663.py` cover the families: every kind has a family, each
vocabulary has a lead for every brand and no lead is shared, a style of a new kind names a model of
its family after its brand, and no title repeats its brand back to back.

## What changed in the rows

- Authored bras and jeans state their model as the `Line` attribute (the bra and jeans styles in
  `variants.py`, `scale_rows.py`, `needs_rows.py`, `colorgroup_rows.py`), and their titles lead with
  the brand and that line. `line_grammar.deals` reads that stated line, so a lead an authored row
  uses is reserved for its brand.
- The place brand "Shirt Row" is "Shirt Mews": the class 8 fit-word decoy "T-Shirt Row Bra" named
  that brand inside its title.
- A bra style whose line already leads with its brand (the Nike sports bra, line "Nike Dri-FIT")
  says the brand once in its title and description (`BraStyle.name`), so it no longer reads "Nike
  Nike Dri-FIT".

## Class 6 and class 5 decoys

The place name of a class 6 decoy (Cardigan Bay, Jumper Lane) is the decoy's brand, and a place
sells its decoys alone; the title stays short and keeps the trap word. Decoy class 5 (`SHADES`, a
shade only in the description) is retired with its table, class entry and tests. Top, Dress, Jumper
and Shirt carry more decoys a class (`decoy_apparel._MORE`), so each keeps a tenth of its styles.

A class 6 decoy is never given the fit word a class 8 query asks for (Barrel jeans, a cami bra),
and a class 8 decoy leaves out any word the exemplar's own fields hold, so the short place-brand
title cannot outrank the fit-word decoys in the top 10 of "barrel jeans" or "cami bra".

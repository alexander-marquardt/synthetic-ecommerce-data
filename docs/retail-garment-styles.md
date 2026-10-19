# Garment style words and their attributes (gen#511)

A title that names a style promises a garment. "Red Coat Dress" carried a boat neck, a mini length
and crepe: a decoy cloned from a boat-neck mini under a new title. A coat dress is tailored, with a
collar, lapels or a V neck, at knee or midi length, in wool, ponte or crepe; a maxi dress is long.
A shopper who filters on Garment length Midi must find every "Midi Dress", and a "Coat Dress" must
look like one.

## The table

`prototypes/retail_drawings/style_table.py` declares, per style word, the necklines, lengths,
sleeves and materials the style allows (`STYLES`). A field left out allows any value.

| Style word | Necklines | Lengths | Materials |
|---|---|---|---|
| coat | collared, v-neck | Knee, Midi | wool, ponte, crepe, tweed, twill, gabardine, boucle |
| blazer | collared, v-neck | any | wool, ponte, crepe, suiting, tweed, twill |
| shirt | collared | any | cotton, poplin, linen, denim, chambray, oxford, twill |
| wrap | v-neck | any | any |
| tea | v-neck, square, round, crew, collared | Knee, Midi | any |
| slip | v-neck, round, square, cowl | Mini to Maxi | satin, silk, crepe, jersey, viscose, lace |
| shift | boat, round, square, crew, v-neck | Mini, Knee, Midi | any |
| bodycon | square, round, v-neck, high, crew, halter | Mini, Knee, Midi | jersey, crepe, scuba, knit, satin, rib, stretch |
| jumper | crew, high, v-neck, boat | any | knit, merino, wool, cashmere, cable, rib |
| t-shirt | crew | any | jersey, cotton, modal |
| hoodie | crew, high | any | jersey, cotton, fleece, loopback |
| tunic | any | Mini, Knee, Midi | any |
| maxi, midi, mini | any | the word itself | any |

Tops and knitwear: `polo` is collared, `roll neck` (also turtle, funnel) is high, and `camisole`
and `vest top` are sleeveless. A title's neckline or sleeve phrase ("V Neck", "Long Sleeve") must
match the `neckline` fact and the `sleeve_length` attribute.

A style word is read only where it sits straight before "dress" (or before its length, "Wrap Midi
Dress"), so "T-Shirt Dress" is the t-shirt style and not the shirt style.

## Where the generator draws inside it

- **Decoys** (`decoy_apparel`): a decoy is a clone of a real style under a new title. An option
  whose title names a style the exemplar contradicts is not drawn; the same word and color is drawn
  on the next exemplar that carries it (`_restyle`).
- **A dress that states no neckline** (`neckline_rows.complete`) was given one by its id alone. It
  now chooses among the necklines its title's style words allow, and a polo top is collared.
  "T-Shirt Dress" no longer reads as "Shirt Dress" (a collar).
- **A title length word** (`style_table.complete_lengths`, run in `scale.templates` before the
  decoys clone): "Midi Dress" without a `length` attribute gets `Midi`.

## The guard

`tests/test_garment_style_table_511.py` runs `style_table.violations` over every document of
`scale.templates()`, decoys included, and fails on any style word outside its table (coat with a
boat neck, maxi with a Mini length). The impossible pairs are written out in the test, not read
from the table. Adding a style word is a row in `STYLES` and, where the generator names it, a
compound in `decoy_apparel.COMPOUNDS`.

# Retail knitwear depth (gen#309)

`prototypes/retail_drawings/knitwear_rows.py` adds Women's and Men's jumpers, cardigans and
knitted tops as distinct products (a style is a product; its colors times its sizes are its
SKUs), so "ladies white jumper", "mens navy v neck jumper" or "cashmere cardigan" have products to
choose between. The floors and the style by material grid are pinned by
`tests/test_retail_knitwear_309.py` over `scale.templates()`. It builds on gen#18 (one spelling
per value), #58 (price), #233 (each department holds a floor of its own styles), #302 (near-white
shades), #181 (neckline) and #275 (main colors).

## What a knitwear product carries

- **Style** (`knit_style` attribute): Women have 12 (crew, V, roll, turtle, cable, half zip, boat
  neck jumpers; button front, longline, cropped cardigans; tank top and slipover), Men have 10
  (crew, V, roll, cable, half zip, quarter zip jumpers; button front, zip through, shawl collar
  cardigans; slipover).
- **Material**: cashmere, merino wool, lambswool, cotton, wool blend, recycled wool, acrylic
  blend, shown in the title ("Womens Pure Cashmere Relaxed Crew Neck Jumper"). Every style exists
  in every material.
- **Neckline**: the existing facet's words (`crew`, `high`, `boat`, `collared`, `round`) plus
  `v-neck`. Roll neck, turtle neck, half zip and quarter zip are `high`.
- **Colors**: two to four per product. Four products in five carry one of the white group:
  White, Cream, Ivory, Off White, Ecru, each its own color value. There is no color-group
  attribute; the group "white" is the consumer's vocabulary (gen#186). `main_colors.complete`
  adds the missing main colors.
- **Sizes**: XS to XXL (Women) and S to XXL (Men). The depth is in products, not sizes.

## Text-match decoys (gen#294)

Each type (jumper, cardigan, knitted top) and audience carries three decoys of each of seven
classes, 126 in all, listed in `knitwear_rows.TABLE` with the class, the misleading word, the
query it targets and the policy that repairs it. A decoy's structured fields are true, and
`main_colors.complete` skips decoys, so a "white" decoy is never given a color its text names.

| Class | Decoy | Example |
|---|---|---|
| 1 color | a trim names another color | "Womens Navy Jumper with Red Stripes" is navy |
| 2 category word | another category's noun as a modifier | "Womens Dress Length Cardigan" |
| 3 audience word | a sibling cut | "Mens Women's-Style Cut Jumper" |
| 4 feature absent | a feature named and missing | "Womens Alpaca-Feel Jumper" has no alpaca |
| 5 shade in the description | a fancy title, the shade in the text | "Womens Moonbeam Jumper" is Ivory |
| 6 incidental word | a range name in a short title | "Womens Red Tarn Jumper" is not red |
| 7 invented brand | a brand holding a color or category word | "White Heron", "Red Kite", "Cardigan Finch" |

The three class 7 brands each have a house style with its own mark and a full lockup whose text
is the brand name; the garment is drawn in its true color.

The decoys outside clothing that the knitwear queries meet are other rows: "jumper dress" under
Dresses (`decoy_apparel`, class 2), jump leads in Home > DIY & Car, and a knitwear care cream in
Home > Laundry > Fabric Care for "cream jumper" (both in `decoy_product_words.py`, class 8; see
`docs/retail-product-word-decoys.md`).

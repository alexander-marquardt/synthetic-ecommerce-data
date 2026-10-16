# Retail class-8 decoys: the shopper's product noun on a different product (gen#326)

A class-8 decoy has a title that holds the product word of a demo query ("dress", "sofa",
"jumper", "tie") while the product is something else: Dress for Success shoes, a sofa cover,
jumper cables, bow tie pasta. The structured fields tell the truth (category path, product type,
color, drawing). A title names at most the misleading color ("Sofa Cushion, Blue Trim" is a
cream cushion piped in blue; "Dress for Success, Red Laces" are black shoes with red laces) and
the drawing renders that detail. The rows are generated from
`prototypes/retail_drawings/decoy_product_words.py` and pinned by
`tests/test_retail_product_word_decoys_326.py`.

The fixing policy is the one that reads the structured fields: `category` (the noun's own node,
for example Dresses, drops the row), `department` (a cross-department row sits in another root,
so the All Departments persona drops it), `color` (the brand rows in every color but blue).
Rows the English stemmer would match ("dressing" for dress, "coated" for coat) are not planted:
the prototype search folds a plural only, and no row that does not rank is counted. Blue Bull is a
class-7 color-word brand on footwear with its own house style.

Each new real type carries a floor of three ordinary products, listed in `FLOOR`.

| Query | Noun | Product id | Title | True type | Fixing policy |
|---|---|---|---|---|---|
| red dress | dress | PLT-DY01 | Dress for Success, Red Laces | Brogues | category |
| black dress | dress | PLT-DY02 | Dress for Success Black Oxford | Brogues | category |
| red dress | dress | PLT-DY03 | Party Dress Doll | Doll | category |
| black dress | dress | PLT-DY04 | Little Black Dress Parfum | Eau de Parfum | category |
| black shoes | shoe | PLT-DY05 | Black Shoe Polish | Shoe Polish | category |
| red shoes | shoe | PLT-DY06 | Red Shoe Laces | Shoe Laces | category |
| black boots | boot | PLT-DY07 | Black Boot Polish | Shoe Polish | category |
| black boots | boot | PLT-DY08 | Black Boot Socks | Boot Socks | category |
| white trainers | trainer | PLT-DY09 | White Trainer Socks | Socks | category |
| blue trainers | trainer | PLT-DY10 | Trainer Cup, Blue | Baby Beakers | department |
| white trainers | trainer | PLT-DY11 | White Trainer Laces | Shoe Laces | category |
| black coat | coat | PLT-DY12 | Black Coat Hooks | Wall Hooks | category |
| black coat | coat | PLT-DY13 | Black Coat Stand | Hallway Stands | category |
| black coat | coat | PLT-DY14 | Black Coat Hangers, 6 Pack | Clothes Hangers | category |
| white coat | coat | PLT-DY15 | White Top Coat Paint | Paint | department |
| jacket | jacket | PLT-DY16 | Jacket Potatoes | Potatoes | department |
| red jacket | jacket | PLT-DY17 | Red Jacket Potato Crisps | Crisps | department |
| red jumper | jumper | PLT-DY18 | Red Jumper Cables | Jump Leads | department |
| white jumper | jumper | PLT-DY19 | White Jumper Drying Rack | Drying Racks | category |
| white skirt | skirt | PLT-DY20 | White Bed Skirt | Valances | category |
| white skirt | skirt | PLT-DY22 | White Skirt Hangers, 4 Pack | Clothes Hangers | category |
| navy suit | suit | PLT-DY23 | Navy Suit Carrier | Garment Bags | category |
| navy suit | suit | PLT-DY24 | Navy Suit Cover, Breathable | Garment Bags | category |
| white bra | bra | PLT-DY25 | White Bra Wash Bag | Wash Bags | category |
| white bra | bra | PLT-DY26 | White Bra Travel Case | Travel Cases | category |
| pink hat | hat | PLT-DY27 | Pink Hat Box | Storage Boxes | category |
| pink hat | hat | PLT-DY28 | Pink Hat Stand | Hallway Stands | category |
| brown leather belt | belt | PLT-DY29 | Brown Leather Belt Bag | Waist Bags | category |
| brown leather belt | belt | PLT-DY30 | Leather Belt Keyring, Brown | Key Clips | category |
| black ties | tie | PLT-DY31 | Black Cable Ties | Cable Ties | department |
| black ties | tie | PLT-DY32 | Black Bow Tie Pasta | Pasta | department |
| black ties | tie | PLT-DY33 | Black Tie Rack | Wall Hooks | category |
| blue sofa | sofa | PLT-DY34 | Blue Sofa Cover | Sofa Covers | category |
| blue sofa | sofa | PLT-DY35 | Sofa Cushion, Blue Trim | Cushion | category |
| blue sofa | sofa | PLT-DY36 | Blue Sofa Throw | Throws | category |
| black pumps | pump | PLT-DY37 | Black Bike Pump | Bike Pumps | department |
| black pumps | pump | PLT-DY38 | Black Foot Pump | Foot Pumps | department |
| black shoes | shoe | PLT-DY39 | Black Shoe String Pasta | Pasta | department |
| blue trainers | brand | PLT-DY40 | Blue Bull Trainers | Trainers | color |
| blue boots | brand | PLT-DY41 | Blue Bull Chelsea Boots | Chelsea Boots | color |
| blue shoes | brand | PLT-DY42 | Blue Bull Court Shoes | Court Shoes | color |

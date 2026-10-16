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

**Sports & Outdoors (gen#368).** Every Sports & Outdoors type carries at least two decoys: a product
of another department, an existing type of the catalog, whose title holds the shopper's word for the
sports product (a block-heel shoe for "yoga block", a lantern-sleeve blouse for "camping lantern", a
crystal tennis bracelet for "tennis racket"). A row names its sports type in `target`, holds no
color word in its title or description, and is fixed by the department policy (the `Sports & Outdoors`
department drops it). `tests/test_retail_sports_decoys_368.py` walks the live catalog's Sports &
Outdoors types, so a new type reds until it has two decoys or an entry in `SPORTS_EXEMPT` that names
its follow-up issue. The seven first-increment types (tents, sleeping bags, camping chairs, yoga mats,
dumbbells, kettlebells, foam rollers) are exempt until #375. The prototype's plural strip reads
"tennis" as "tenni", so the noun of those two rows is `tenni`.

**Gifts (gen#425).** The five Gifts types of the mug, greeting card, notebook, money box and pamper
hamper issue carry two decoys each: a wall mug rack and a microwave mug cake for "mug", a card holder
case and card-making paper for "card", a notebook computer sleeve and tote for "notebook", a lockable
storage box and chocolate coins in a box for "money box", a laundry hamper and a wicker storage hamper
for "hamper". A row names its Gifts type in `gift_type`, holds no color word in its title or
description, and is fixed by the department policy (the paper row sits in Gifts, so the category
policy fixes it). `tests/test_retail_gifts_425.py` holds the census. Memory cards and gift cards
(the issue's other "card" examples) need a type this build lacks and are not planted; gen#437 files them.

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
| black pumps | pump | PLT-DY37 | Black Bike Pump | Bike Pump | department |
| black pumps | pump | PLT-DY38 | Black Foot Pump | Foot Pumps | department |
| black shoes | shoe | PLT-DY39 | Black Shoe String Pasta | Pasta | department |
| blue trainers | brand | PLT-DY40 | Blue Bull Trainers | Trainers | color |
| blue boots | brand | PLT-DY41 | Blue Bull Chelsea Boots | Chelsea Boots | color |
| blue shoes | brand | PLT-DY42 | Blue Bull Court Shoes | Court Shoes | color |
| block | block | PLT-DY43 | Suede Block Heel Shoes | Block Heels | department |
| block | block | PLT-DY44 | Building Blocks Set | Building Set | department |
| strap | strap | PLT-DY45 | Shoulder Bag with Long Strap | Handbag | department |
| strap | strap | PLT-DY46 | Buckle Strap Sandals | Sandals | department |
| band | band | PLT-DY47 | Band Collar Cotton Shirt | Shirt | department |
| resistance | resistance | PLT-DY48 | Mesh Watch, 50m Water Resistance | Watch | department |
| lantern | lantern | PLT-DY49 | Lantern Sleeve Blouse | Blouse | department |
| lantern | lantern | PLT-DY50 | Lantern Glow Scented Candle | Scented Candle | department |
| roll | roll | PLT-DY51 | Roll Top Rucksack | Backpack | department |
| roll | roll | PLT-DY52 | Gift Wrapping Paper Roll | Wrapping Paper | department |
| pump | pump | PLT-DY53 | Pump Bottle Hand Wash | Hand Wash | department |
| pump | pump | PLT-DY54 | Cushioned Ballet Pumps | Ballet Pumps | department |
| bat | bat | PLT-DY55 | Bat Wing Sleeve Jumper | Jumper | department |
| baseball | baseball | PLT-DY56 | Baseball Bomber Jacket | Bomber Jacket | department |
| glove | glove | PLT-DY57 | Glove Box Organizer | Car Boot Organiser | department |
| glove | glove | PLT-DY58 | Glove Leather Loafers | Loafers | department |
| baseball | baseball | PLT-DY59 | Baseball Fan Cushion | Cushion | department |
| baseball | baseball | PLT-DY60 | Baseball Fan Duvet Set | Duvet Set | department |
| batting | batting | PLT-DY61 | Soft Batting Duvet | Duvet | department |
| batting | batting | PLT-DY62 | Quilted Batting Throw | Throws | department |
| swim | swim | PLT-DY63 | Quick-Dry Swim Towel | Towel | department |
| swim | swim | PLT-DY64 | Mesh Swim Tote Bag | Tote Bag | department |
| cap | cap | PLT-DY65 | Cap Sleeve Wrap Dress | Dress | department |
| cap | cap | PLT-DY66 | Cap Toe Leather Brogues | Brogues | department |
| kickboard | kickboard | PLT-DY67 | Kickboard Scooter, Two Wheels | Ride-On Toy | department |
| kickboard | kickboard | PLT-DY68 | Kickboard Scooter, Three Wheels | Ride-On Toy | department |
| armband | armband | PLT-DY69 | Running Armband Phone Pouch | Waist Bags | department |
| armband | armband | PLT-DY70 | Upper Armband Cuff Bracelet | Bracelet | department |
| football | football | PLT-DY71 | Football Fan T-Shirt | Tee | department |
| football | football | PLT-DY72 | Football Socks, 5 Pack | Socks | department |
| tennis | tenni | PLT-DY73 | Tennis Court Trainers | Trainers | department |
| tennis | tenni | PLT-DY74 | Crystal Tennis Bracelet | Bracelet | department |
| badminton | badminton | PLT-DY75 | Badminton Club T-Shirt | Tee | department |
| badminton | badminton | PLT-DY76 | Badminton Club Tote Bag | Tote Bag | department |
| mug | mug | PLT-DY77 | Wall Mug Rack, Five Hooks | Wall Hooks | department |
| mug | mug | PLT-DY78 | Microwave Mug Cake | Cake | department |
| card | card | PLT-DY79 | Travel Card Holder Case | Travel Cases | department |
| card | card | PLT-DY80 | Card Making Craft Paper | Wrapping Paper | category |
| notebook | notebook | PLT-DY81 | Notebook Computer Sleeve | Travel Cases | department |
| notebook | notebook | PLT-DY82 | Notebook Carry Tote Bag | Tote Bag | department |
| money box | box | PLT-DY83 | Lockable Storage Box | Storage Boxes | department |
| money box | box | PLT-DY84 | Chocolate Money Box | Biscuit | department |
| hamper | hamper | PLT-DY85 | Folding Laundry Hamper | Wash Bags | department |
| hamper | hamper | PLT-DY86 | Wicker Storage Hamper | Storage Boxes | department |

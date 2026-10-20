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

**A care cream for jumpers (gen#309).** "cream jumper" also meets a product that says both words
and is neither: `PLT-DY494`, Jumper and Knitwear Softening Cream, a white tub in Cleaning > Laundry >
Fabric Softener, an existing type with products of its own. Its color is White, so the color policy
drops it for the shade Cream, the category policy (Jumpers) drops it, and the department policy
(Cleaning & Janitorial) drops it. `tests/test_retail_knitwear_care_cream_309.py` pins the row, its
fields and its place in the baseline top 10.

**Sports & Outdoors (gen#368).** Every Sports & Outdoors type carries at least two decoys: a product
of another department, an existing type of the catalog, whose title holds the shopper's word for the
sports product (a block-heel shoe for "yoga block", a lantern-sleeve blouse for "camping lantern", a
crystal tennis bracelet for "tennis racket"). A row names its sports type in `target`, holds no
color word in its title or description, and is fixed by the department policy (the `Sports & Outdoors`
department drops it). `tests/test_retail_sports_decoys_368.py` walks the live catalog's Sports &
Outdoors types, so a new type reds until it has two decoys or an entry in `SPORTS_EXEMPT` that names
its follow-up issue. `SPORTS_EXEMPT` has been empty since gen#375 gave the seven first-increment types
(tents, sleeping bags, camping chairs, yoga mats, dumbbells, kettlebells, foam rollers) their two
decoys each, in `feature_decoys/sports_first_increment.py` (a tent dress and a tent stitch cushion,
a sleeping cat cushion and a sleeping beauty doll, camping club and camping trip rows, yoga leggings
and a yoga candle, dumbbell and kettlebell prints, a foam hand wash and foam sole sandals), and a test
pins it empty. The prototype's plural strip reads
"tennis" as "tenni", so the noun of those two rows is `tenni`. The picnic blanket of gen#217 (Camping)
carries two rows of its own (`picnic`), beside the two decoys of `decor_rows.py`.

**Gifts (gen#425).** The five Gifts types of the mug, greeting card, notebook, money box and pamper
hamper issue carry two decoys each: a wall mug rack and a microwave mug cake for "mug", a card holder
case and card-making paper for "card", a notebook computer sleeve and tote for "notebook", a lockable
storage box and chocolate coins in a box for "money box", a laundry hamper and a wicker storage hamper
for "hamper". A row names its Gifts type in `gift_type`, holds no color word in its title or
description, and is fixed by the department policy (the paper row sits in Gifts, so the category
policy fixes it). `tests/test_retail_gifts_425.py` holds the census.

**Gift card (gen#437).** The gift card has a home since gen#424 (Gifts > Cards > Gift Cards), so it
carries two decoys of its own: a gift card holder case (Travel Cases) and gift card wrapping sheets
(Wrapping Paper, in Gifts, so the category policy fixes it). Both name `Gift Card` in `gift_type`,
hold "gift card" in the title, and a "gift card" search and a "greeting card" search each rank the
intended Gifts type first once the policy applies. `tests/test_retail_gift_card_decoys_437.py` holds
the checks. The memory card, the other "card" example of gen#425, needs a storage or memory-card type
of the Electronics department (gen#332), which this build lacks; gen#437 stays open for it, with the
card reader and the card-slot phone case as its incidental-word decoys.

**Seed phrases (gen#460).** The homepage seed queries are two or three words ("leather boots", "skinny
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
| batting | batting | PLT-DY62 | Quilted Throw with Batting | Throws | department |
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
| picnic | picnic | PLT-DY87 | Picnic Check Cushion | Cushion | department |
| picnic | picnic | PLT-DY88 | Insulated Picnic Tote Bag | Tote Bag | department |
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
| gift card | card | PLT-DY104 | Gift Card Holder Case | Travel Cases | department |
| gift card | card | PLT-DY105 | Gift Card Wrapping Sheets | Wrapping Paper | category |
| cream jumper | jumper | PLT-DY494 | Jumper and Knitwear Softening Cream | Fabric Softener | category |
| high rise jeans | seed phrase | PLT-DY460 | High Rise Jeans Slim Belt | Belt | category |
| high rise jeans | seed phrase | PLT-DY461 | Skinny Jeans Jeggings | Leggings | category |
| high rise jeans | seed phrase | PLT-DY462 | Jeans Clip Hangers, 10 Pack | Hanger | department |
| skinny jeans | seed phrase | PLT-DY463 | Skinny Jeans Trouser Hanger | Clothes Hangers | department |
| barrel trousers | seed phrase | PLT-DY464 | Barrel Trousers Fashion Doll | Doll | department |
| barrel trousers | seed phrase | PLT-DY465 | Barrel Trousers Clip Hangers | Hanger | department |
| barrel trousers | seed phrase | PLT-DY466 | Barrel Trousers Garment Bag | Garment Bags | department |
| womens boat neck top | seed phrase | PLT-DY467 | Boat Neck Top Hanger | Clothes Hangers | department |
| womens boat neck top | seed phrase | PLT-DY468 | Boat Neck Top Fashion Doll | Doll | department |
| womens boat neck top | seed phrase | PLT-DY469 | Boat Neck Top Garment Bag | Garment Bags | department |
| tea dress | seed phrase | PLT-DY470 | Tea Dress Fashion Doll | Doll | department |
| tea dress | seed phrase | PLT-DY471 | Tea Dress Padded Hangers | Clothes Hangers | department |
| tea dress | seed phrase | PLT-DY472 | Tea Dress Garment Bag | Garment Bags | department |
| denim jacket | seed phrase | PLT-DY473 | Denim Jacket Wide Hanger | Clothes Hangers | department |
| denim jacket | seed phrase | PLT-DY474 | Denim Jacket Fashion Doll | Doll | department |
| denim jacket | seed phrase | PLT-DY475 | Denim Jacket Garment Bag | Garment Bags | department |
| pyjamas | seed phrase | PLT-DY476 | Pyjama Case, Embroidered | Travel Cases | category |
| pyjamas | seed phrase | PLT-DY477 | Pyjama Party Doll | Doll | department |
| pyjamas | seed phrase | PLT-DY478 | Pyjamas Overnight Tote Bag | Tote Bag | category |
| leather boots | seed phrase | PLT-DY479 | Leather Boots Care Kit | Shoe Care Kit | category |
| leather boots | seed phrase | PLT-DY480 | Leather Boot Cream | Shoe Polish | category |
| leather boots | seed phrase | PLT-DY481 | Leather Boots Waxed Laces | Shoe Laces | category |
| running shoes | seed phrase | PLT-DY482 | Running Shoes Flat Laces | Shoe Laces | category |
| running shoes | seed phrase | PLT-DY483 | Running Shoe Mesh Bag | Wash Bags | department |
| running shoes | seed phrase | PLT-DY484 | Running Shoes Cleaning Kit | Shoe Care Kit | category |
| brogues | seed phrase | PLT-DY485 | Brogue Detail Leather Belt | Belt | category |
| brogues | seed phrase | PLT-DY486 | Brogues Shoe Cream | Shoe Polish | category |
| brogues | seed phrase | PLT-DY487 | Brogues Waxed Laces | Shoe Laces | category |
| navy dresses | seed phrase | PLT-DY488 | Navy Garment Bag for Dresses | Garment Bags | department |
| navy dresses | seed phrase | PLT-DY489 | Navy Velvet Hangers for Dresses | Clothes Hangers | department |
| navy dresses | seed phrase | PLT-DY490 | Navy Dresses Fashion Doll Set | Doll | department |
| large dresses | seed phrase | PLT-DY491 | Large Garment Bag for Dresses | Garment Bags | department |
| large dresses | seed phrase | PLT-DY492 | Large Dresses Storage Box | Storage Boxes | department |
| large dresses | seed phrase | PLT-DY493 | Large Dresses Padded Hangers | Clothes Hangers | department |
| duvet cover | duvet cover | PLT-DY495 | Duvet Cover Storage Bag | Garment Bags | category |
| duvet cover | duvet cover | PLT-DY496 | Duvet Cover Mesh Wash Bag | Wash Bags | category |
| bed frame | bed frame | PLT-DY89 | Bed Frame Valance | Valances | category |
| bed frame | bed frame | PLT-DY90 | Bed Frame Headboard Cushion | Cushion | category |
| tea towels | tea towels | PLT-DY91 | Tea Towel Hook Rail | Wall Hooks | category |
| tea towels | tea towels | PLT-DY92 | Tea Towel Hanger, 4 Pack | Hanger | category |
| lipstick | lipstick | PLT-DY93 | Lipstick Case, Mini Zip | Make-Up Bag | category |
| lipstick | lipstick | PLT-DY94 | Lipstick Plant, Trailing | Plant | department |
| foundation | foundation | PLT-DY95 | Foundation Remover Face Cloth | Towel | category |
| foundation | foundation | PLT-DY96 | Foundation Brush Make-Up Bag | Make-Up Bag | category |
| lemon drizzle cake | lemon drizzle cake | PLT-DY97 | Lemon Drizzle Cake Candle | Scented Candle | department |
| lemon drizzle cake | lemon drizzle cake | PLT-DY98 | Lemon Drizzle Cake Flavour Tea | Tea | department |
| lemon drizzle cake | lemon drizzle cake | PLT-DY99 | Lemon Drizzle Cake Hand Wash | Hand Wash | department |
| gift hamper | gift hamper | PLT-DY100 | Empty Gift Hamper Basket, Wicker | Storage Basket | department |
| gift hamper | gift hamper | PLT-DY101 | Gift Hamper Cellophane Wrap | Wrapping Paper | department |
| olive tree | olive tree | PLT-DY102 | Olive Tree Scented Candle | Scented Candle | department |
| olive tree | olive tree | PLT-DY103 | Olive Tree Hand Wash | Hand Wash | department |
| bicycle | bicycle | PLT-DY3521 | Bicycle Print T-Shirt | T-Shirt | department |
| bicycle | bicycle | PLT-DY3522 | Bicycle Print Tote Bag | Tote Bag | department |
| bike helmet | helmet | PLT-DY3523 | Bike Helmet Print Pyjamas | Pyjamas | department |
| bike helmet | helmet | PLT-DY3524 | Bike Helmet Print Sweatshirt | Sweatshirt | department |
| kayak | kayak | PLT-DY3525 | Kayak Print Beach Towel | Towel | department |
| kayak | kayak | PLT-DY3526 | Kayak Print Cushion | Cushion | department |
| kick scooter | scooter | PLT-DY3527 | Kick Scooter Print T-Shirt | T-Shirt | department |
| kick scooter | scooter | PLT-DY3528 | Kick Scooter Print Sweatshirt | Sweatshirt | department |
| skateboard | skateboard | PLT-DY3529 | Skateboard Print T-Shirt | T-Shirt | department |
| skateboard | skateboard | PLT-DY3530 | Skateboard Print Tote Bag | Tote Bag | department |
| tent | tent | PLT-DY540 | Tent Dress, Swing Fit | Dress | department |
| tent | tent | PLT-DY541 | Tent Stitch Cushion | Cushion | department |
| sleeping | sleeping | PLT-DY542 | Sleeping Cat Cushion | Cushion | department |
| sleeping | sleeping | PLT-DY543 | Sleeping Beauty Doll | Doll | department |
| camping | camping | PLT-DY544 | Camping Club Kids T-Shirt | T-Shirt | department |
| camping | camping | PLT-DY545 | Camping Trip Scented Candle | Scented Candle | department |
| yoga | yoga | PLT-DY546 | Yoga Waist Leggings | Leggings | department |
| yoga | yoga | PLT-DY547 | Yoga Calm Scented Candle | Scented Candle | department |
| dumbbell | dumbbell | PLT-DY548 | Dumbbell Print Tee | Tee | department |
| dumbbell | dumbbell | PLT-DY549 | Dumbbell Charm Bracelet | Bracelet | department |
| kettlebell | kettlebell | PLT-DY550 | Kettlebell Class Tee | Tee | department |
| kettlebell | kettlebell | PLT-DY551 | Kettlebell Class Tote Bag | Tote Bag | department |
| foam | foam | PLT-DY552 | Foam Hand Wash | Hand Wash | department |
| foam | foam | PLT-DY553 | Foam Sole Sandals | Sandals | department |

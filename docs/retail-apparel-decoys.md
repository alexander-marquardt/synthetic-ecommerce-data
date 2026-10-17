# Text-match decoys on every clothing, footwear and lingerie type (gen#311)

`prototypes/retail_drawings/decoy_apparel.py` plants, on every product type of the Womens, Mens and
Kids clothing, footwear and lingerie, products whose words mislead a plain text search while their
structured fields tell the truth (gen#294's rule; `decoy_rows.py` holds the demo-query rows). A
decoy is a clone of one real style of its type in one main color. The color, category and audience
policies read the fields and drop it. The classes: 1 a color word names a trim or strap; 2 another
category's noun in a real compound; 3 an audience word of a sibling version; 4 a material or
feature named but absent; 5 the shade is in the description only; 6 a short range name, a place,
holds a category word; 7 an invented brand holds a color or category word.

Each type holds at least three decoys per class (nine and twelve for bras and jeans, so a type
holds a tenth of its size), and one class 7 decoy per brand (at most eight).
Classes 6 and 7 have titles of five words or fewer. A title names the misleading color only
(never the real one); the drawing shows the named part (class 1) in that color, and nothing else
of it (`details.py`). A class 7 brand holds its color word in the brand field only, and its
drawing colors no part: "Yellow Wagtail Co-ord Set" is a blue co-ord set with no yellow part.

A decoy must read as a real product and describe what it is (#444). A color word sits in the
title only as an invented brand that is the product's brand field and is shown as the brand
(class 7: "Red Plover Bra"), or as a part that really is that color and the drawing shows
(class 1: "Bra with Red Straps"). So class 6 has no color variant: a range name such as "Red
Harbour" read as a red dress by a strange brand, with only the straps drawn red, and a range that
is a visible line of the product's brand would only repeat class 7. Class 6 keeps its category
word variant, a range named for a place ("Jumper Lane Dress"). Class 2 uses the compounds of
`decoy_apparel.COMPOUNDS` (dress shirt, shirt dress, slipper socks), each a real retail name,
never an invented one ("Dress Pyjamas"); a compound drops a type's own modifier only where the
shorter name still describes the product (Sandal Boots for Ankle Boots).
`tests/test_retail_apparel_decoys_311.py` holds the reviewed list of real compounds apart from the
generator's table, and a type holds at least three, except the declared exceptions below. The
Policy column is
`generic` where the color, category or audience policy separates the decoy, and
`special: <name>` where it needs its own
(a material claim: no field says the product is not leather). The exempt types are in
`decoy_apparel.EXEMPT`. The table is generated
(`python3 prototypes/retail_drawings/decoy_apparel.py`) and
`tests/test_retail_apparel_decoys_311.py` holds it verbatim.

Types with fewer than three real class 2 compounds (a third is never invented; #444):

- Ballet Pumps: only ballet slippers and ballet sandals pair another noun with a ballet pump.
- Barefoot Shoes: only the sandal barefoot shoe is a name a shopper meets.
- Blouse: only the dress blouse and the tunic blouse are names a shopper meets.
- Chukka Boots: only sneaker boots and loafer boots are names; a shoe boot is not one.
- Clogs: only the mule clog is a name a shopper meets.
- Court Shoes: only dress shoes pairs another category's noun with a court shoe.
- Dressing Gown: only hoodie and kimono dressing gowns are names a shopper meets.
- Espadrilles: only the sneaker espadrille is a name; a wedge espadrille is an espadrille.
- Jeans: only cargo jeans and jogger jeans are names a shopper meets.
- Jelly Shoes: only the mary jane jelly shoe is a name a shopper meets.
- Jumper: only the tunic jumper and the polo jumper are names a shopper meets.
- Loafers: only mule loafers and brogue loafers are names a shopper meets.
- Platform Trainers: only the sock platform trainer is a name a shopper meets.
- Plimsolls: only the sneaker plimsoll is a name met; a pump or a trainer is a plimsoll.
- Pyjamas: only short pyjamas and cami pyjamas are names a shopper meets.
- School Pinafore: a school pinafore dress is the only compound name of it.
- School Shirt: only the school polo shirt and the oxford school shirt are names met.
- School Skirt: only the pinafore school skirt is a name a shopper meets.
- T-Shirt: only the polo and tunic t-shirt name another category; a henley is a t-shirt.
- Tee: only the polo tee and the tunic tee name another category; a henley is a tee.
- Tights: only running tights and cycling tights are names a shopper meets.
- Walking Boots: only the chukka walking boot is a name a shopper meets.
- Wedges: only sneaker wedges and sandal wedges are names; espadrille wedges are wedges.
- Wellies: only the chelsea welly is a name a shopper meets.

| Product id | Type | Class | Title | Word | Query | Policy |
|---|---|---|---|---|---|---|
| PLT-DA00100 | Blouse | 1 color names a part | Blouse with Blue Hem | blue | blue blouse | generic |
| PLT-DA00101 | Blouse | 1 color names a part | Blouse with White Hem | white | white blouse | generic |
| PLT-DA00102 | Blouse | 1 color names a part | Blouse with Red Hem | red | red blouse | generic |
| PLT-DA00200 | Blouse | 2 another category's noun as a modifier | Pink Tunic Blouse | tunic | tunic | generic |
| PLT-DA00201 | Blouse | 2 another category's noun as a modifier | Green Dress Blouse | dress | dress | generic |
| PLT-DA00202 | Blouse | 2 another category's noun as a modifier | Brown Tunic Blouse | tunic | tunic | generic |
| PLT-DA00300 | Blouse | 3 audience word of a sibling version | Green Mens-Style Blouse | mens | mens blouse | generic |
| PLT-DA00301 | Blouse | 3 audience word of a sibling version | Brown Boys Fit Blouse | boys | boys blouse | generic |
| PLT-DA00302 | Blouse | 3 audience word of a sibling version | Navy Mens Fit Blouse | mens | mens blouse | generic |
| PLT-DA00400 | Blouse | 4 material or feature named but absent | Black Leather-Look Blouse | leather | leather blouse | special: material claim |
| PLT-DA00401 | Blouse | 4 material or feature named but absent | Blue Suede-Look Blouse | suede | suede blouse | special: material claim |
| PLT-DA00402 | Blouse | 4 material or feature named but absent | Brown Cashmere-Feel Blouse | cashmere | cashmere blouse | special: material claim |
| PLT-DA00500 | Blouse | 5 shade spelled in the description only | Moonbeam Blouse | ivory | ivory blouse | generic |
| PLT-DA00501 | Blouse | 5 shade spelled in the description only | Driftwood Blouse | taupe | taupe blouse | generic |
| PLT-DA00502 | Blouse | 5 shade spelled in the description only | Dune Blouse | beige | beige blouse | generic |
| PLT-DA00600 | Blouse | 6 incidental word in a range name | Cardigan Bay Blouse | cardigan | cardigan | generic |
| PLT-DA00601 | Blouse | 6 incidental word in a range name | Pump Lane Blouse | pump | pump | generic |
| PLT-DA00602 | Blouse | 6 incidental word in a range name | Skirt Point Blouse | skirt | skirt | generic |
| PLT-DA00700 | Blouse | 7 invented brand holding a color or category word | Blue Otter Blouse | blue | blue blouse | generic |
| PLT-DA00701 | Blouse | 7 invented brand holding a color or category word | White Dormouse Blouse | white | white blouse | generic |
| PLT-DA00702 | Blouse | 7 invented brand holding a color or category word | Green Stoat Blouse | green | green blouse | generic |
| PLT-DA01100 | Bodysuit | 1 color names a part | Bodysuit with Green Hem | green | green bodysuit | generic |
| PLT-DA01101 | Bodysuit | 1 color names a part | Bodysuit with Black Hem | black | black bodysuit | generic |
| PLT-DA01102 | Bodysuit | 1 color names a part | Bodysuit with Yellow Hem | yellow | yellow bodysuit | generic |
| PLT-DA01200 | Bodysuit | 2 another category's noun as a modifier | Grey Corset Bodysuit | corset | corset | generic |
| PLT-DA01201 | Bodysuit | 2 another category's noun as a modifier | White Corset Bodysuit | corset | corset | generic |
| PLT-DA01202 | Bodysuit | 2 another category's noun as a modifier | Cream Cami Bodysuit | cami | cami | generic |
| PLT-DA01300 | Bodysuit | 3 audience word of a sibling version | Blue Mens Fit Bodysuit | mens | mens bodysuit | generic |
| PLT-DA01301 | Bodysuit | 3 audience word of a sibling version | Black Boys Fit Bodysuit | boys | boys bodysuit | generic |
| PLT-DA01302 | Bodysuit | 3 audience word of a sibling version | Brown Boys Fit Bodysuit | boys | boys bodysuit | generic |
| PLT-DA01400 | Bodysuit | 4 material or feature named but absent | Brown Leather-Look Bodysuit | leather | leather bodysuit | special: material claim |
| PLT-DA01401 | Bodysuit | 4 material or feature named but absent | Brown Suede-Look Bodysuit | suede | suede bodysuit | special: material claim |
| PLT-DA01402 | Bodysuit | 4 material or feature named but absent | Green Cashmere-Feel Bodysuit | cashmere | cashmere bodysuit | special: material claim |
| PLT-DA01500 | Bodysuit | 5 shade spelled in the description only | Moonbeam Bodysuit | ivory | ivory bodysuit | generic |
| PLT-DA01501 | Bodysuit | 5 shade spelled in the description only | Driftwood Bodysuit | taupe | taupe bodysuit | generic |
| PLT-DA01502 | Bodysuit | 5 shade spelled in the description only | Dune Bodysuit | beige | beige bodysuit | generic |
| PLT-DA01600 | Bodysuit | 6 incidental word in a range name | Shoe Lane Bodysuit | shoe | shoe | generic |
| PLT-DA01601 | Bodysuit | 6 incidental word in a range name | Sandal Wood Bodysuit | sandal | sandal | generic |
| PLT-DA01602 | Bodysuit | 6 incidental word in a range name | Pump Lane Bodysuit | pump | pump | generic |
| PLT-DA01700 | Bodysuit | 7 invented brand holding a color or category word | Coat Crake Bodysuit | coat | coat bodysuit | generic |
| PLT-DA01701 | Bodysuit | 7 invented brand holding a color or category word | Green Stoat Bodysuit | green | green bodysuit | generic |
| PLT-DA01702 | Bodysuit | 7 invented brand holding a color or category word | Black Lapwing Bodysuit | black | black bodysuit | generic |
| PLT-DA02100 | Bomber Jacket | 1 color names a part | Bomber Jacket with Blue Hem | blue | blue bomber jacket | generic |
| PLT-DA02101 | Bomber Jacket | 1 color names a part | Bomber Jacket with Yellow Hem | yellow | yellow bomber jacket | generic |
| PLT-DA02102 | Bomber Jacket | 1 color names a part | Bomber Jacket with Black Hem | black | black bomber jacket | generic |
| PLT-DA02200 | Bomber Jacket | 2 another category's noun as a modifier | Cream Blazer Jacket | blazer | blazer | generic |
| PLT-DA02201 | Bomber Jacket | 2 another category's noun as a modifier | Cream Shirt Jacket | shirt | shirt | generic |
| PLT-DA02202 | Bomber Jacket | 2 another category's noun as a modifier | Red Shirt Jacket | shirt | shirt | generic |
| PLT-DA02300 | Bomber Jacket | 3 audience word of a sibling version | Grey Mens-Style Bomber Jacket | mens | mens bomber jacket | generic |
| PLT-DA02301 | Bomber Jacket | 3 audience word of a sibling version | Grey Mini-Me Mens Bomber Jacket | mens | mens bomber jacket | generic |
| PLT-DA02302 | Bomber Jacket | 3 audience word of a sibling version | Brown Mini-Me Womens Bomber Jacket | womens | womens bomber jacket | generic |
| PLT-DA02400 | Bomber Jacket | 4 material or feature named but absent | Black Leather-Look Bomber Jacket | leather | leather bomber jacket | special: material claim |
| PLT-DA02401 | Bomber Jacket | 4 material or feature named but absent | White Suede-Look Bomber Jacket | suede | suede bomber jacket | special: material claim |
| PLT-DA02402 | Bomber Jacket | 4 material or feature named but absent | Grey Cashmere-Feel Bomber Jacket | cashmere | cashmere bomber jacket | special: material claim |
| PLT-DA02500 | Bomber Jacket | 5 shade spelled in the description only | Moonbeam Bomber Jacket | ivory | ivory bomber jacket | generic |
| PLT-DA02501 | Bomber Jacket | 5 shade spelled in the description only | Driftwood Bomber Jacket | taupe | taupe bomber jacket | generic |
| PLT-DA02502 | Bomber Jacket | 5 shade spelled in the description only | Dune Bomber Jacket | beige | beige bomber jacket | generic |
| PLT-DA02600 | Bomber Jacket | 6 incidental word in a range name | Jumper Lane Bomber Jacket | jumper | jumper | generic |
| PLT-DA02601 | Bomber Jacket | 6 incidental word in a range name | Blazer Court Bomber Jacket | blazer | blazer | generic |
| PLT-DA02602 | Bomber Jacket | 6 incidental word in a range name | Dress Circle Bomber Jacket | dress | dress | generic |
| PLT-DA02700 | Bomber Jacket | 7 invented brand holding a color or category word | White Dormouse Bomber Jacket | white | white bomber jacket | generic |
| PLT-DA02701 | Bomber Jacket | 7 invented brand holding a color or category word | Jumper Jay Bomber Jacket | jumper | jumper bomber jacket | generic |
| PLT-DA02702 | Bomber Jacket | 7 invented brand holding a color or category word | Blue Otter Bomber Jacket | blue | blue bomber jacket | generic |
| PLT-DA03100 | Cardigan | 1 color names a part | Cardigan with Red Hem | red | red cardigan | generic |
| PLT-DA03101 | Cardigan | 1 color names a part | Cardigan with White Collar | white | white cardigan | generic |
| PLT-DA03102 | Cardigan | 1 color names a part | Cardigan with Red Collar | red | red cardigan | generic |
| PLT-DA03200 | Cardigan | 2 another category's noun as a modifier | Brown Duster Cardigan | duster | duster | generic |
| PLT-DA03201 | Cardigan | 2 another category's noun as a modifier | Red Kimono Cardigan | kimono | kimono | generic |
| PLT-DA03202 | Cardigan | 2 another category's noun as a modifier | Black Kimono Cardigan | kimono | kimono | generic |
| PLT-DA03300 | Cardigan | 3 audience word of a sibling version | Red Girls Fit Cardigan | girls | girls cardigan | generic |
| PLT-DA03301 | Cardigan | 3 audience word of a sibling version | Brown Womens Fit Cardigan | womens | womens cardigan | generic |
| PLT-DA03302 | Cardigan | 3 audience word of a sibling version | White Girls Fit Cardigan | girls | girls cardigan | generic |
| PLT-DA03400 | Cardigan | 4 material or feature named but absent | Pink Leather-Look Cardigan | leather | leather cardigan | special: material claim |
| PLT-DA03401 | Cardigan | 4 material or feature named but absent | Blue Suede-Look Cardigan | suede | suede cardigan | special: material claim |
| PLT-DA03402 | Cardigan | 4 material or feature named but absent | Black Cashmere-Feel Cardigan | cashmere | cashmere cardigan | special: material claim |
| PLT-DA03500 | Cardigan | 5 shade spelled in the description only | Moonbeam Cardigan | ivory | ivory cardigan | generic |
| PLT-DA03501 | Cardigan | 5 shade spelled in the description only | Driftwood Cardigan | taupe | taupe cardigan | generic |
| PLT-DA03502 | Cardigan | 5 shade spelled in the description only | Dune Cardigan | beige | beige cardigan | generic |
| PLT-DA03600 | Cardigan | 6 incidental word in a range name | Shoe Lane Cardigan | shoe | shoe | generic |
| PLT-DA03601 | Cardigan | 6 incidental word in a range name | Coat Hook Cardigan | coat | coat | generic |
| PLT-DA03602 | Cardigan | 6 incidental word in a range name | Slipper Brook Cardigan | slipper | slipper | generic |
| PLT-DA03700 | Cardigan | 7 invented brand holding a color or category word | Red Plover Cardigan | red | red cardigan | generic |
| PLT-DA03701 | Cardigan | 7 invented brand holding a color or category word | Blue Otter Cardigan | blue | blue cardigan | generic |
| PLT-DA03702 | Cardigan | 7 invented brand holding a color or category word | Yellow Wagtail Cardigan | yellow | yellow cardigan | generic |
| PLT-DA04100 | Coat | 1 color names a part | Coat with Red Hem | red | red coat | generic |
| PLT-DA04101 | Coat | 1 color names a part | Coat with Blue Hem | blue | blue coat | generic |
| PLT-DA04102 | Coat | 1 color names a part | Coat with Yellow Hem | yellow | yellow coat | generic |
| PLT-DA04200 | Coat | 2 another category's noun as a modifier | White Puffer Coat | puffer | puffer | generic |
| PLT-DA04201 | Coat | 2 another category's noun as a modifier | Blue Duffle Coat | duffle | duffle | generic |
| PLT-DA04202 | Coat | 2 another category's noun as a modifier | Red Duffle Coat | duffle | duffle | generic |
| PLT-DA04300 | Coat | 3 audience word of a sibling version | Pink Womens-Style Coat | womens | womens coat | generic |
| PLT-DA04301 | Coat | 3 audience word of a sibling version | White Girls Fit Coat | girls | girls coat | generic |
| PLT-DA04302 | Coat | 3 audience word of a sibling version | Black Womens Fit Coat | womens | womens coat | generic |
| PLT-DA04400 | Coat | 4 material or feature named but absent | Pink Leather-Look Coat | leather | leather coat | special: material claim |
| PLT-DA04401 | Coat | 4 material or feature named but absent | Blue Suede-Look Coat | suede | suede coat | special: material claim |
| PLT-DA04402 | Coat | 4 material or feature named but absent | Green Cashmere-Feel Coat | cashmere | cashmere coat | special: material claim |
| PLT-DA04500 | Coat | 5 shade spelled in the description only | Moonbeam Coat | ivory | ivory coat | generic |
| PLT-DA04501 | Coat | 5 shade spelled in the description only | Driftwood Coat | taupe | taupe coat | generic |
| PLT-DA04502 | Coat | 5 shade spelled in the description only | Dune Coat | beige | beige coat | generic |
| PLT-DA04600 | Coat | 6 incidental word in a range name | Cardigan Bay Coat | cardigan | cardigan | generic |
| PLT-DA04601 | Coat | 6 incidental word in a range name | Shirt Row Coat | shirt | shirt | generic |
| PLT-DA04602 | Coat | 6 incidental word in a range name | Shoe Lane Coat | shoe | shoe | generic |
| PLT-DA04700 | Coat | 7 invented brand holding a color or category word | Green Stoat Coat | green | green coat | generic |
| PLT-DA04701 | Coat | 7 invented brand holding a color or category word | Yellow Wagtail Coat | yellow | yellow coat | generic |
| PLT-DA04702 | Coat | 7 invented brand holding a color or category word | Red Plover Coat | red | red coat | generic |
| PLT-DA05100 | Co-ord Set | 1 color names a part | Co-ord Set with Yellow Waistband | yellow | yellow co-ord set | generic |
| PLT-DA05101 | Co-ord Set | 1 color names a part | Co-ord Set with Green Waistband | green | green co-ord set | generic |
| PLT-DA05102 | Co-ord Set | 1 color names a part | Co-ord Set with Black Waistband | black | black co-ord set | generic |
| PLT-DA05200 | Co-ord Set | 2 another category's noun as a modifier | Red Short Co-ord Set | short | short | generic |
| PLT-DA05201 | Co-ord Set | 2 another category's noun as a modifier | White Skirt Co-ord Set | skirt | skirt | generic |
| PLT-DA05202 | Co-ord Set | 2 another category's noun as a modifier | Grey Short Co-ord Set | short | short | generic |
| PLT-DA05300 | Co-ord Set | 3 audience word of a sibling version | Navy Mens-Style Co-ord Set | mens | mens co-ord set | generic |
| PLT-DA05301 | Co-ord Set | 3 audience word of a sibling version | White Mens-Style Co-ord Set | mens | mens co-ord set | generic |
| PLT-DA05302 | Co-ord Set | 3 audience word of a sibling version | White Boys Fit Co-ord Set | boys | boys co-ord set | generic |
| PLT-DA05400 | Co-ord Set | 4 material or feature named but absent | Brown Leather-Look Co-ord Set | leather | leather co-ord set | special: material claim |
| PLT-DA05401 | Co-ord Set | 4 material or feature named but absent | White Suede-Look Co-ord Set | suede | suede co-ord set | special: material claim |
| PLT-DA05402 | Co-ord Set | 4 material or feature named but absent | Pink Cashmere-Feel Co-ord Set | cashmere | cashmere co-ord set | special: material claim |
| PLT-DA05500 | Co-ord Set | 5 shade spelled in the description only | Moonbeam Co-ord Set | ivory | ivory co-ord set | generic |
| PLT-DA05501 | Co-ord Set | 5 shade spelled in the description only | Driftwood Co-ord Set | taupe | taupe co-ord set | generic |
| PLT-DA05502 | Co-ord Set | 5 shade spelled in the description only | Dune Co-ord Set | beige | beige co-ord set | generic |
| PLT-DA05600 | Co-ord Set | 6 incidental word in a range name | Coat Hook Co-ord Set | coat | coat | generic |
| PLT-DA05601 | Co-ord Set | 6 incidental word in a range name | Jumper Lane Co-ord Set | jumper | jumper | generic |
| PLT-DA05602 | Co-ord Set | 6 incidental word in a range name | Skirt Point Co-ord Set | skirt | skirt | generic |
| PLT-DA05700 | Co-ord Set | 7 invented brand holding a color or category word | Blue Otter Co-ord Set | blue | blue co-ord set | generic |
| PLT-DA05701 | Co-ord Set | 7 invented brand holding a color or category word | Yellow Wagtail Co-ord Set | yellow | yellow co-ord set | generic |
| PLT-DA05702 | Co-ord Set | 7 invented brand holding a color or category word | White Dormouse Co-ord Set | white | white co-ord set | generic |
| PLT-DA06100 | Cycling Shorts | 1 color names a part | Compression Cycling Shorts with Green Waistband | green | green cycling shorts | generic |
| PLT-DA06101 | Cycling Shorts | 1 color names a part | Compression Cycling Shorts with White Waistband | white | white cycling shorts | generic |
| PLT-DA06102 | Cycling Shorts | 1 color names a part | Compression Cycling Shorts with White Cuffs | white | white cycling shorts | generic |
| PLT-DA06200 | Cycling Shorts | 2 another category's noun as a modifier | Blue Tailored Shorts | tailored | tailored | generic |
| PLT-DA06201 | Cycling Shorts | 2 another category's noun as a modifier | Grey Tailored Shorts | tailored | tailored | generic |
| PLT-DA06202 | Cycling Shorts | 2 another category's noun as a modifier | Brown Cargo Shorts | cargo | cargo | generic |
| PLT-DA06300 | Cycling Shorts | 3 audience word of a sibling version | Pink Girls Fit Compression Cycling Shorts | girls | girls cycling shorts | generic |
| PLT-DA06301 | Cycling Shorts | 3 audience word of a sibling version | Grey Girls Fit Compression Cycling Shorts | girls | girls cycling shorts | generic |
| PLT-DA06302 | Cycling Shorts | 3 audience word of a sibling version | Navy Girls Fit Compression Cycling Shorts | girls | girls cycling shorts | generic |
| PLT-DA06400 | Cycling Shorts | 4 material or feature named but absent | Navy Leather-Look Compression Cycling Shorts | leather | leather cycling shorts | special: material claim |
| PLT-DA06401 | Cycling Shorts | 4 material or feature named but absent | Blue Suede-Look Compression Cycling Shorts | suede | suede cycling shorts | special: material claim |
| PLT-DA06402 | Cycling Shorts | 4 material or feature named but absent | White Cashmere-Feel Compression Cycling Shorts | cashmere | cashmere cycling shorts | special: material claim |
| PLT-DA06500 | Cycling Shorts | 5 shade spelled in the description only | Moonbeam Compression Cycling Shorts | ivory | ivory cycling shorts | generic |
| PLT-DA06501 | Cycling Shorts | 5 shade spelled in the description only | Driftwood Compression Cycling Shorts | taupe | taupe cycling shorts | generic |
| PLT-DA06502 | Cycling Shorts | 5 shade spelled in the description only | Dune Compression Cycling Shorts | beige | beige cycling shorts | generic |
| PLT-DA06600 | Cycling Shorts | 6 incidental word in a range name | Skirt Point Compression Cycling Shorts | skirt | skirt | generic |
| PLT-DA06601 | Cycling Shorts | 6 incidental word in a range name | Shoe Lane Compression Cycling Shorts | shoe | shoe | generic |
| PLT-DA06602 | Cycling Shorts | 6 incidental word in a range name | Jacket Quay Compression Cycling Shorts | jacket | jacket | generic |
| PLT-DA06700 | Cycling Shorts | 7 invented brand holding a color or category word | Red Plover Compression Cycling Shorts | red | red cycling shorts | generic |
| PLT-DA06701 | Cycling Shorts | 7 invented brand holding a color or category word | Yellow Wagtail Compression Cycling Shorts | yellow | yellow cycling shorts | generic |
| PLT-DA06702 | Cycling Shorts | 7 invented brand holding a color or category word | Jumper Jay Compression Cycling Shorts | jumper | jumper cycling shorts | generic |
| PLT-DA07100 | Denim Jacket | 1 color names a part | Denim Jacket with White Hem | white | white denim jacket | generic |
| PLT-DA07101 | Denim Jacket | 1 color names a part | Denim Jacket with Red Hem | red | red denim jacket | generic |
| PLT-DA07102 | Denim Jacket | 1 color names a part | Denim Jacket with Green Hem | green | green denim jacket | generic |
| PLT-DA07200 | Denim Jacket | 2 another category's noun as a modifier | Green Denim Bomber Jacket | bomber | bomber | generic |
| PLT-DA07201 | Denim Jacket | 2 another category's noun as a modifier | Navy Denim Bomber Jacket | bomber | bomber | generic |
| PLT-DA07202 | Denim Jacket | 2 another category's noun as a modifier | Navy Denim Biker Jacket | biker | biker | generic |
| PLT-DA07300 | Denim Jacket | 3 audience word of a sibling version | Navy Mens-Style Denim Jacket | mens | mens denim jacket | generic |
| PLT-DA07301 | Denim Jacket | 3 audience word of a sibling version | Pink Mens Fit Denim Jacket | mens | mens denim jacket | generic |
| PLT-DA07302 | Denim Jacket | 3 audience word of a sibling version | Black Mens-Style Denim Jacket | mens | mens denim jacket | generic |
| PLT-DA07400 | Denim Jacket | 4 material or feature named but absent | Green Leather-Look Denim Jacket | leather | leather denim jacket | special: material claim |
| PLT-DA07401 | Denim Jacket | 4 material or feature named but absent | Brown Suede-Look Denim Jacket | suede | suede denim jacket | special: material claim |
| PLT-DA07402 | Denim Jacket | 4 material or feature named but absent | Grey Cashmere-Feel Denim Jacket | cashmere | cashmere denim jacket | special: material claim |
| PLT-DA07500 | Denim Jacket | 5 shade spelled in the description only | Moonbeam Denim Jacket | ivory | ivory denim jacket | generic |
| PLT-DA07501 | Denim Jacket | 5 shade spelled in the description only | Driftwood Denim Jacket | taupe | taupe denim jacket | generic |
| PLT-DA07502 | Denim Jacket | 5 shade spelled in the description only | Dune Denim Jacket | beige | beige denim jacket | generic |
| PLT-DA07600 | Denim Jacket | 6 incidental word in a range name | Sandal Wood Denim Jacket | sandal | sandal | generic |
| PLT-DA07601 | Denim Jacket | 6 incidental word in a range name | Blazer Court Denim Jacket | blazer | blazer | generic |
| PLT-DA07602 | Denim Jacket | 6 incidental word in a range name | Jumper Lane Denim Jacket | jumper | jumper | generic |
| PLT-DA07700 | Denim Jacket | 7 invented brand holding a color or category word | White Dormouse Denim Jacket | white | white denim jacket | generic |
| PLT-DA07701 | Denim Jacket | 7 invented brand holding a color or category word | Red Plover Denim Jacket | red | red denim jacket | generic |
| PLT-DA07702 | Denim Jacket | 7 invented brand holding a color or category word | Jumper Jay Denim Jacket | jumper | jumper denim jacket | generic |
| PLT-DA08100 | Dress | 1 color names a part | Dress with Red Straps | red | red dress | generic |
| PLT-DA08101 | Dress | 1 color names a part | Dress with Black Straps | black | black dress | generic |
| PLT-DA08102 | Dress | 1 color names a part | Dress with Green Straps | green | green dress | generic |
| PLT-DA08200 | Dress | 2 another category's noun as a modifier | Grey Jumper Dress | jumper | jumper | generic |
| PLT-DA08201 | Dress | 2 another category's noun as a modifier | Cream Coat Dress | coat | coat | generic |
| PLT-DA08202 | Dress | 2 another category's noun as a modifier | Blue Shirt Dress | shirt | shirt | generic |
| PLT-DA08300 | Dress | 3 audience word of a sibling version | White Boys Fit Dress | boys | boys dress | generic |
| PLT-DA08301 | Dress | 3 audience word of a sibling version | Grey Boys Fit Dress | boys | boys dress | generic |
| PLT-DA08302 | Dress | 3 audience word of a sibling version | Black Mens Fit Dress | mens | mens dress | generic |
| PLT-DA08400 | Dress | 4 material or feature named but absent | Black Leather-Look Dress | leather | leather dress | special: material claim |
| PLT-DA08401 | Dress | 4 material or feature named but absent | Grey Suede-Look Dress | suede | suede dress | special: material claim |
| PLT-DA08402 | Dress | 4 material or feature named but absent | Black Cashmere-Feel Dress | cashmere | cashmere dress | special: material claim |
| PLT-DA08500 | Dress | 5 shade spelled in the description only | Moonbeam Dress | ivory | ivory dress | generic |
| PLT-DA08501 | Dress | 5 shade spelled in the description only | Driftwood Dress | taupe | taupe dress | generic |
| PLT-DA08502 | Dress | 5 shade spelled in the description only | Dune Dress | beige | beige dress | generic |
| PLT-DA08600 | Dress | 6 incidental word in a range name | Jumper Lane Dress | jumper | jumper | generic |
| PLT-DA08601 | Dress | 6 incidental word in a range name | Boot Hill Dress | boot | boot | generic |
| PLT-DA08602 | Dress | 6 incidental word in a range name | Pump Lane Dress | pump | pump | generic |
| PLT-DA08700 | Dress | 7 invented brand holding a color or category word | Red Plover Dress | red | red dress | generic |
| PLT-DA08701 | Dress | 7 invented brand holding a color or category word | White Dormouse Dress | white | white dress | generic |
| PLT-DA08702 | Dress | 7 invented brand holding a color or category word | Blue Otter Dress | blue | blue dress | generic |
| PLT-DA09100 | Joggers | 1 color names a part | Regular Joggers with Red Cuffs | red | red joggers | generic |
| PLT-DA09101 | Joggers | 1 color names a part | Oversized Joggers with Blue Cuffs | blue | blue joggers | generic |
| PLT-DA09102 | Joggers | 1 color names a part | Regular Joggers with Yellow Cuffs | yellow | yellow joggers | generic |
| PLT-DA09200 | Joggers | 2 another category's noun as a modifier | Brown Relaxed Cargo Joggers | cargo | cargo | generic |
| PLT-DA09201 | Joggers | 2 another category's noun as a modifier | Blue Slim Chino Joggers | chino | chino | generic |
| PLT-DA09202 | Joggers | 2 another category's noun as a modifier | Grey Relaxed Denim Joggers | denim | denim | generic |
| PLT-DA09300 | Joggers | 3 audience word of a sibling version | Pink Girls Fit Regular Joggers | girls | girls joggers | generic |
| PLT-DA09301 | Joggers | 3 audience word of a sibling version | Green Mens-Style Oversized Joggers | mens | mens joggers | generic |
| PLT-DA09302 | Joggers | 3 audience word of a sibling version | Red Girls Fit Regular Joggers | girls | girls joggers | generic |
| PLT-DA09400 | Joggers | 4 material or feature named but absent | Red Leather-Look Relaxed Joggers | leather | leather joggers | special: material claim |
| PLT-DA09401 | Joggers | 4 material or feature named but absent | Blue Suede-Look Slim Joggers | suede | suede joggers | special: material claim |
| PLT-DA09402 | Joggers | 4 material or feature named but absent | Navy Cashmere-Feel Relaxed Joggers | cashmere | cashmere joggers | special: material claim |
| PLT-DA09500 | Joggers | 5 shade spelled in the description only | Moonbeam Regular Joggers | ivory | ivory joggers | generic |
| PLT-DA09501 | Joggers | 5 shade spelled in the description only | Driftwood Oversized Joggers | taupe | taupe joggers | generic |
| PLT-DA09502 | Joggers | 5 shade spelled in the description only | Dune Regular Joggers | beige | beige joggers | generic |
| PLT-DA09600 | Joggers | 6 incidental word in a range name | Shoe Lane Relaxed Joggers | shoe | shoe | generic |
| PLT-DA09601 | Joggers | 6 incidental word in a range name | Slip Road Slim Joggers | slip | slip | generic |
| PLT-DA09602 | Joggers | 6 incidental word in a range name | Skirt Point Relaxed Joggers | skirt | skirt | generic |
| PLT-DA09700 | Joggers | 7 invented brand holding a color or category word | Jumper Jay Regular Joggers | jumper | jumper joggers | generic |
| PLT-DA09701 | Joggers | 7 invented brand holding a color or category word | White Dormouse Oversized Joggers | white | white joggers | generic |
| PLT-DA09702 | Joggers | 7 invented brand holding a color or category word | Coat Crake Regular Joggers | coat | coat joggers | generic |
| PLT-DA10100 | Jumper | 1 color names a part | Jumper with Blue Hem | blue | blue jumper | generic |
| PLT-DA10101 | Jumper | 1 color names a part | Jumper with White Hem | white | white jumper | generic |
| PLT-DA10102 | Jumper | 1 color names a part | Jumper with Black Hem | black | black jumper | generic |
| PLT-DA10200 | Jumper | 2 another category's noun as a modifier | Brown Tunic Jumper | tunic | tunic | generic |
| PLT-DA10201 | Jumper | 2 another category's noun as a modifier | Brown Polo Jumper | polo | polo | generic |
| PLT-DA10202 | Jumper | 2 another category's noun as a modifier | Blue Polo Jumper | polo | polo | generic |
| PLT-DA10300 | Jumper | 3 audience word of a sibling version | Red Girls Fit Jumper | girls | girls jumper | generic |
| PLT-DA10301 | Jumper | 3 audience word of a sibling version | Cream Womens Fit Jumper | womens | womens jumper | generic |
| PLT-DA10302 | Jumper | 3 audience word of a sibling version | Pink Girls Fit Jumper | girls | girls jumper | generic |
| PLT-DA10400 | Jumper | 4 material or feature named but absent | Red Leather-Look Jumper | leather | leather jumper | special: material claim |
| PLT-DA10401 | Jumper | 4 material or feature named but absent | Green Suede-Look Jumper | suede | suede jumper | special: material claim |
| PLT-DA10402 | Jumper | 4 material or feature named but absent | White Cashmere-Feel Jumper | cashmere | cashmere jumper | special: material claim |
| PLT-DA10500 | Jumper | 5 shade spelled in the description only | Moonbeam Jumper | ivory | ivory jumper | generic |
| PLT-DA10501 | Jumper | 5 shade spelled in the description only | Driftwood Jumper | taupe | taupe jumper | generic |
| PLT-DA10502 | Jumper | 5 shade spelled in the description only | Dune Jumper | beige | beige jumper | generic |
| PLT-DA10600 | Jumper | 6 incidental word in a range name | Slip Road Jumper | slip | slip | generic |
| PLT-DA10601 | Jumper | 6 incidental word in a range name | Shoe Lane Jumper | shoe | shoe | generic |
| PLT-DA10602 | Jumper | 6 incidental word in a range name | Sock Hop Jumper | sock | sock | generic |
| PLT-DA10700 | Jumper | 7 invented brand holding a color or category word | Blue Otter Jumper | blue | blue jumper | generic |
| PLT-DA10701 | Jumper | 7 invented brand holding a color or category word | Black Lapwing Jumper | black | black jumper | generic |
| PLT-DA10702 | Jumper | 7 invented brand holding a color or category word | White Dormouse Jumper | white | white jumper | generic |
| PLT-DA11100 | Leggings | 1 color names a part | Compression Leggings with White Waistband | white | white leggings | generic |
| PLT-DA11101 | Leggings | 1 color names a part | Regular Leggings with Black Waistband | black | black leggings | generic |
| PLT-DA11102 | Leggings | 1 color names a part | Regular Leggings with White Cuffs | white | white leggings | generic |
| PLT-DA11200 | Leggings | 2 another category's noun as a modifier | Green Regular Cycling Leggings | cycling | cycling | generic |
| PLT-DA11201 | Leggings | 2 another category's noun as a modifier | Blue Regular Cycling Leggings | cycling | cycling | generic |
| PLT-DA11202 | Leggings | 2 another category's noun as a modifier | Navy Regular Cycling Leggings | cycling | cycling | generic |
| PLT-DA11300 | Leggings | 3 audience word of a sibling version | Red Boys Fit Compression Leggings | boys | boys leggings | generic |
| PLT-DA11301 | Leggings | 3 audience word of a sibling version | Cream Mens-Style Compression Leggings | mens | mens leggings | generic |
| PLT-DA11302 | Leggings | 3 audience word of a sibling version | Blue Boys Fit Regular Leggings | boys | boys leggings | generic |
| PLT-DA11400 | Leggings | 4 material or feature named but absent | Blue Leather-Look Regular Leggings | leather | leather leggings | special: material claim |
| PLT-DA11401 | Leggings | 4 material or feature named but absent | Pink Suede-Look Regular Leggings | suede | suede leggings | special: material claim |
| PLT-DA11402 | Leggings | 4 material or feature named but absent | Cream Cashmere-Feel Regular Leggings | cashmere | cashmere leggings | special: material claim |
| PLT-DA11500 | Leggings | 5 shade spelled in the description only | Moonbeam Regular Leggings | ivory | ivory leggings | generic |
| PLT-DA11501 | Leggings | 5 shade spelled in the description only | Driftwood Compression Leggings | taupe | taupe leggings | generic |
| PLT-DA11502 | Leggings | 5 shade spelled in the description only | Dune Compression Leggings | beige | beige leggings | generic |
| PLT-DA11600 | Leggings | 6 incidental word in a range name | Skirt Point Regular Leggings | skirt | skirt | generic |
| PLT-DA11601 | Leggings | 6 incidental word in a range name | Sandal Wood Regular Leggings | sandal | sandal | generic |
| PLT-DA11602 | Leggings | 6 incidental word in a range name | Shoe Lane Regular Leggings | shoe | shoe | generic |
| PLT-DA11700 | Leggings | 7 invented brand holding a color or category word | Red Plover Regular Leggings | red | red leggings | generic |
| PLT-DA11701 | Leggings | 7 invented brand holding a color or category word | Green Stoat Regular Leggings | green | green leggings | generic |
| PLT-DA11702 | Leggings | 7 invented brand holding a color or category word | Black Lapwing Compression Leggings | black | black leggings | generic |
| PLT-DA12100 | Outfit Set | 1 color names a part | Outfit Set with Green Waistband | green | green outfit set | generic |
| PLT-DA12101 | Outfit Set | 1 color names a part | Outfit Set with White Waistband | white | white outfit set | generic |
| PLT-DA12102 | Outfit Set | 1 color names a part | Outfit Set with Red Waistband | red | red outfit set | generic |
| PLT-DA12200 | Outfit Set | 2 another category's noun as a modifier | Black Blazer Set | blazer | blazer | generic |
| PLT-DA12201 | Outfit Set | 2 another category's noun as a modifier | Brown Trouser Set | trouser | trouser | generic |
| PLT-DA12202 | Outfit Set | 2 another category's noun as a modifier | Blue Short Set | short | short | generic |
| PLT-DA12300 | Outfit Set | 3 audience word of a sibling version | Blue Mini-Me Mens Outfit Set | mens | mens outfit set | generic |
| PLT-DA12301 | Outfit Set | 3 audience word of a sibling version | Green Mens-Style Outfit Set | mens | mens outfit set | generic |
| PLT-DA12302 | Outfit Set | 3 audience word of a sibling version | Brown Mens-Style Outfit Set | mens | mens outfit set | generic |
| PLT-DA12400 | Outfit Set | 4 material or feature named but absent | Cream Leather-Look Outfit Set | leather | leather outfit set | special: material claim |
| PLT-DA12401 | Outfit Set | 4 material or feature named but absent | Blue Suede-Look Outfit Set | suede | suede outfit set | special: material claim |
| PLT-DA12402 | Outfit Set | 4 material or feature named but absent | Green Cashmere-Feel Outfit Set | cashmere | cashmere outfit set | special: material claim |
| PLT-DA12500 | Outfit Set | 5 shade spelled in the description only | Moonbeam Outfit Set | ivory | ivory outfit set | generic |
| PLT-DA12501 | Outfit Set | 5 shade spelled in the description only | Driftwood Outfit Set | taupe | taupe outfit set | generic |
| PLT-DA12502 | Outfit Set | 5 shade spelled in the description only | Dune Outfit Set | beige | beige outfit set | generic |
| PLT-DA12600 | Outfit Set | 6 incidental word in a range name | Shirt Row Outfit Set | shirt | shirt | generic |
| PLT-DA12601 | Outfit Set | 6 incidental word in a range name | Boot Hill Outfit Set | boot | boot | generic |
| PLT-DA12602 | Outfit Set | 6 incidental word in a range name | Coat Hook Outfit Set | coat | coat | generic |
| PLT-DA12700 | Outfit Set | 7 invented brand holding a color or category word | Blue Otter Outfit Set | blue | blue outfit set | generic |
| PLT-DA12701 | Outfit Set | 7 invented brand holding a color or category word | Black Lapwing Outfit Set | black | black outfit set | generic |
| PLT-DA12702 | Outfit Set | 7 invented brand holding a color or category word | Yellow Wagtail Outfit Set | yellow | yellow outfit set | generic |
| PLT-DA13100 | Puffer Jacket | 1 color names a part | Puffer Jacket with Green Hem | green | green puffer jacket | generic |
| PLT-DA13101 | Puffer Jacket | 1 color names a part | Puffer Jacket with Blue Hem | blue | blue puffer jacket | generic |
| PLT-DA13102 | Puffer Jacket | 1 color names a part | Puffer Jacket with Green Hem | green | green puffer jacket | generic |
| PLT-DA13200 | Puffer Jacket | 2 another category's noun as a modifier | White Biker Jacket | biker | biker | generic |
| PLT-DA13201 | Puffer Jacket | 2 another category's noun as a modifier | Green Shirt Jacket | shirt | shirt | generic |
| PLT-DA13202 | Puffer Jacket | 2 another category's noun as a modifier | White Biker Jacket | biker | biker | generic |
| PLT-DA13300 | Puffer Jacket | 3 audience word of a sibling version | Pink Womens-Style Puffer Jacket | womens | womens puffer jacket | generic |
| PLT-DA13301 | Puffer Jacket | 3 audience word of a sibling version | Navy Womens Fit Puffer Jacket | womens | womens puffer jacket | generic |
| PLT-DA13302 | Puffer Jacket | 3 audience word of a sibling version | Brown Mini-Me Mens Puffer Jacket | mens | mens puffer jacket | generic |
| PLT-DA13400 | Puffer Jacket | 4 material or feature named but absent | Pink Leather-Look Puffer Jacket | leather | leather puffer jacket | special: material claim |
| PLT-DA13401 | Puffer Jacket | 4 material or feature named but absent | Brown Suede-Look Puffer Jacket | suede | suede puffer jacket | special: material claim |
| PLT-DA13402 | Puffer Jacket | 4 material or feature named but absent | Green Cashmere-Feel Puffer Jacket | cashmere | cashmere puffer jacket | special: material claim |
| PLT-DA13500 | Puffer Jacket | 5 shade spelled in the description only | Moonbeam Puffer Jacket | ivory | ivory puffer jacket | generic |
| PLT-DA13501 | Puffer Jacket | 5 shade spelled in the description only | Driftwood Puffer Jacket | taupe | taupe puffer jacket | generic |
| PLT-DA13502 | Puffer Jacket | 5 shade spelled in the description only | Dune Puffer Jacket | beige | beige puffer jacket | generic |
| PLT-DA13600 | Puffer Jacket | 6 incidental word in a range name | Shirt Row Puffer Jacket | shirt | shirt | generic |
| PLT-DA13601 | Puffer Jacket | 6 incidental word in a range name | Sock Hop Puffer Jacket | sock | sock | generic |
| PLT-DA13602 | Puffer Jacket | 6 incidental word in a range name | Shoe Lane Puffer Jacket | shoe | shoe | generic |
| PLT-DA13700 | Puffer Jacket | 7 invented brand holding a color or category word | Red Plover Puffer Jacket | red | red puffer jacket | generic |
| PLT-DA13701 | Puffer Jacket | 7 invented brand holding a color or category word | Jumper Jay Puffer Jacket | jumper | jumper puffer jacket | generic |
| PLT-DA13702 | Puffer Jacket | 7 invented brand holding a color or category word | Black Lapwing Puffer Jacket | black | black puffer jacket | generic |
| PLT-DA14100 | Shirt | 1 color names a part | Shirt with Green Hem | green | green shirt | generic |
| PLT-DA14101 | Shirt | 1 color names a part | Shirt with Red Hem | red | red shirt | generic |
| PLT-DA14102 | Shirt | 1 color names a part | Shirt with Black Hem | black | black shirt | generic |
| PLT-DA14200 | Shirt | 2 another category's noun as a modifier | Blue Dress Shirt | dress | dress | generic |
| PLT-DA14201 | Shirt | 2 another category's noun as a modifier | Red Polo Shirt | polo | polo | generic |
| PLT-DA14202 | Shirt | 2 another category's noun as a modifier | Black Polo Shirt | polo | polo | generic |
| PLT-DA14300 | Shirt | 3 audience word of a sibling version | Navy Womens Fit Shirt | womens | womens shirt | generic |
| PLT-DA14301 | Shirt | 3 audience word of a sibling version | Blue Womens Fit Shirt | womens | womens shirt | generic |
| PLT-DA14302 | Shirt | 3 audience word of a sibling version | Pink Womens-Style Shirt | womens | womens shirt | generic |
| PLT-DA14400 | Shirt | 4 material or feature named but absent | White Leather-Look Shirt | leather | leather shirt | special: material claim |
| PLT-DA14401 | Shirt | 4 material or feature named but absent | Black Suede-Look Shirt | suede | suede shirt | special: material claim |
| PLT-DA14402 | Shirt | 4 material or feature named but absent | Pink Cashmere-Feel Shirt | cashmere | cashmere shirt | special: material claim |
| PLT-DA14500 | Shirt | 5 shade spelled in the description only | Moonbeam Shirt | ivory | ivory shirt | generic |
| PLT-DA14501 | Shirt | 5 shade spelled in the description only | Driftwood Shirt | taupe | taupe shirt | generic |
| PLT-DA14502 | Shirt | 5 shade spelled in the description only | Dune Shirt | beige | beige shirt | generic |
| PLT-DA14600 | Shirt | 6 incidental word in a range name | Jacket Quay Shirt | jacket | jacket | generic |
| PLT-DA14601 | Shirt | 6 incidental word in a range name | Slipper Brook Shirt | slipper | slipper | generic |
| PLT-DA14602 | Shirt | 6 incidental word in a range name | Pump Lane Shirt | pump | pump | generic |
| PLT-DA14700 | Shirt | 7 invented brand holding a color or category word | Coat Crake Shirt | coat | coat shirt | generic |
| PLT-DA14701 | Shirt | 7 invented brand holding a color or category word | Green Stoat Shirt | green | green shirt | generic |
| PLT-DA14702 | Shirt | 7 invented brand holding a color or category word | Blue Otter Shirt | blue | blue shirt | generic |
| PLT-DA15100 | Shorts | 1 color names a part | Shorts with White Waistband | white | white shorts | generic |
| PLT-DA15101 | Shorts | 1 color names a part | Shorts with Blue Waistband | blue | blue shorts | generic |
| PLT-DA15102 | Shorts | 1 color names a part | Shorts with Red Waistband | red | red shorts | generic |
| PLT-DA15200 | Shorts | 2 another category's noun as a modifier | Pink Tailored Shorts | tailored | tailored | generic |
| PLT-DA15201 | Shorts | 2 another category's noun as a modifier | Grey Chino Shorts | chino | chino | generic |
| PLT-DA15202 | Shorts | 2 another category's noun as a modifier | Green Jean Shorts | jean | jean | generic |
| PLT-DA15300 | Shorts | 3 audience word of a sibling version | Brown Boys Fit Shorts | boys | boys shorts | generic |
| PLT-DA15301 | Shorts | 3 audience word of a sibling version | Pink Boys Fit Shorts | boys | boys shorts | generic |
| PLT-DA15302 | Shorts | 3 audience word of a sibling version | White Womens Fit Shorts | womens | womens shorts | generic |
| PLT-DA15400 | Shorts | 4 material or feature named but absent | Green Leather-Look Shorts | leather | leather shorts | special: material claim |
| PLT-DA15401 | Shorts | 4 material or feature named but absent | Navy Suede-Look Shorts | suede | suede shorts | special: material claim |
| PLT-DA15402 | Shorts | 4 material or feature named but absent | Brown Cashmere-Feel Shorts | cashmere | cashmere shorts | special: material claim |
| PLT-DA15500 | Shorts | 5 shade spelled in the description only | Moonbeam Shorts | ivory | ivory shorts | generic |
| PLT-DA15501 | Shorts | 5 shade spelled in the description only | Driftwood Shorts | taupe | taupe shorts | generic |
| PLT-DA15502 | Shorts | 5 shade spelled in the description only | Dune Shorts | beige | beige shorts | generic |
| PLT-DA15600 | Shorts | 6 incidental word in a range name | Jumper Lane Shorts | jumper | jumper | generic |
| PLT-DA15601 | Shorts | 6 incidental word in a range name | Pump Lane Shorts | pump | pump | generic |
| PLT-DA15602 | Shorts | 6 incidental word in a range name | Cardigan Bay Shorts | cardigan | cardigan | generic |
| PLT-DA15700 | Shorts | 7 invented brand holding a color or category word | Black Lapwing Shorts | black | black shorts | generic |
| PLT-DA15701 | Shorts | 7 invented brand holding a color or category word | Black Lapwing Shorts | black | black shorts | generic |
| PLT-DA15702 | Shorts | 7 invented brand holding a color or category word | Jumper Jay Shorts | jumper | jumper shorts | generic |
| PLT-DA16100 | Skirt | 1 color names a part | Skirt with Green Waistband | green | green skirt | generic |
| PLT-DA16101 | Skirt | 1 color names a part | Skirt with Yellow Waistband | yellow | yellow skirt | generic |
| PLT-DA16102 | Skirt | 1 color names a part | Skirt with White Waistband | white | white skirt | generic |
| PLT-DA16200 | Skirt | 2 another category's noun as a modifier | Cream Cargo Skirt | cargo | cargo | generic |
| PLT-DA16201 | Skirt | 2 another category's noun as a modifier | Cream Slip Skirt | slip | slip | generic |
| PLT-DA16202 | Skirt | 2 another category's noun as a modifier | Pink Cargo Skirt | cargo | cargo | generic |
| PLT-DA16300 | Skirt | 3 audience word of a sibling version | Black Mens Fit Skirt | mens | mens skirt | generic |
| PLT-DA16301 | Skirt | 3 audience word of a sibling version | White Mens Fit Skirt | mens | mens skirt | generic |
| PLT-DA16302 | Skirt | 3 audience word of a sibling version | Navy Mens-Style Skirt | mens | mens skirt | generic |
| PLT-DA16400 | Skirt | 4 material or feature named but absent | Blue Leather-Look Skirt | leather | leather skirt | special: material claim |
| PLT-DA16401 | Skirt | 4 material or feature named but absent | Pink Suede-Look Skirt | suede | suede skirt | special: material claim |
| PLT-DA16402 | Skirt | 4 material or feature named but absent | Black Cashmere-Feel Skirt | cashmere | cashmere skirt | special: material claim |
| PLT-DA16500 | Skirt | 5 shade spelled in the description only | Moonbeam Skirt | ivory | ivory skirt | generic |
| PLT-DA16501 | Skirt | 5 shade spelled in the description only | Driftwood Skirt | taupe | taupe skirt | generic |
| PLT-DA16502 | Skirt | 5 shade spelled in the description only | Dune Skirt | beige | beige skirt | generic |
| PLT-DA16600 | Skirt | 6 incidental word in a range name | Slipper Brook Skirt | slipper | slipper | generic |
| PLT-DA16601 | Skirt | 6 incidental word in a range name | Dress Circle Skirt | dress | dress | generic |
| PLT-DA16602 | Skirt | 6 incidental word in a range name | Slip Road Skirt | slip | slip | generic |
| PLT-DA16700 | Skirt | 7 invented brand holding a color or category word | Red Plover Skirt | red | red skirt | generic |
| PLT-DA16701 | Skirt | 7 invented brand holding a color or category word | Coat Crake Skirt | coat | coat skirt | generic |
| PLT-DA16702 | Skirt | 7 invented brand holding a color or category word | Jumper Jay Skirt | jumper | jumper skirt | generic |
| PLT-DA17100 | Suit Jacket | 1 color names a part | Suit Jacket with Yellow Hem | yellow | yellow suit jacket | generic |
| PLT-DA17101 | Suit Jacket | 1 color names a part | Suit Jacket with Black Hem | black | black suit jacket | generic |
| PLT-DA17102 | Suit Jacket | 1 color names a part | Suit Jacket with Red Hem | red | red suit jacket | generic |
| PLT-DA17200 | Suit Jacket | 2 another category's noun as a modifier | Blue Shirt Jacket | shirt | shirt | generic |
| PLT-DA17201 | Suit Jacket | 2 another category's noun as a modifier | Green Shirt Jacket | shirt | shirt | generic |
| PLT-DA17202 | Suit Jacket | 2 another category's noun as a modifier | Green Dress Jacket | dress | dress | generic |
| PLT-DA17300 | Suit Jacket | 3 audience word of a sibling version | Grey Womens-Style Suit Jacket | womens | womens suit jacket | generic |
| PLT-DA17301 | Suit Jacket | 3 audience word of a sibling version | Grey Girls Fit Suit Jacket | girls | girls suit jacket | generic |
| PLT-DA17302 | Suit Jacket | 3 audience word of a sibling version | Pink Girls Fit Suit Jacket | girls | girls suit jacket | generic |
| PLT-DA17400 | Suit Jacket | 4 material or feature named but absent | White Leather-Look Suit Jacket | leather | leather suit jacket | special: material claim |
| PLT-DA17401 | Suit Jacket | 4 material or feature named but absent | Blue Suede-Look Suit Jacket | suede | suede suit jacket | special: material claim |
| PLT-DA17402 | Suit Jacket | 4 material or feature named but absent | Pink Cashmere-Feel Suit Jacket | cashmere | cashmere suit jacket | special: material claim |
| PLT-DA17500 | Suit Jacket | 5 shade spelled in the description only | Moonbeam Suit Jacket | ivory | ivory suit jacket | generic |
| PLT-DA17501 | Suit Jacket | 5 shade spelled in the description only | Driftwood Suit Jacket | taupe | taupe suit jacket | generic |
| PLT-DA17502 | Suit Jacket | 5 shade spelled in the description only | Dune Suit Jacket | beige | beige suit jacket | generic |
| PLT-DA17600 | Suit Jacket | 6 incidental word in a range name | Dress Circle Suit Jacket | dress | dress | generic |
| PLT-DA17601 | Suit Jacket | 6 incidental word in a range name | Shirt Row Suit Jacket | shirt | shirt | generic |
| PLT-DA17602 | Suit Jacket | 6 incidental word in a range name | Sandal Wood Suit Jacket | sandal | sandal | generic |
| PLT-DA17700 | Suit Jacket | 7 invented brand holding a color or category word | Green Stoat Suit Jacket | green | green suit jacket | generic |
| PLT-DA17701 | Suit Jacket | 7 invented brand holding a color or category word | Black Lapwing Suit Jacket | black | black suit jacket | generic |
| PLT-DA17702 | Suit Jacket | 7 invented brand holding a color or category word | Red Plover Suit Jacket | red | red suit jacket | generic |
| PLT-DA18100 | Sweatshirt | 1 color names a part | Sweatshirt with Black Hem | black | black sweatshirt | generic |
| PLT-DA18101 | Sweatshirt | 1 color names a part | Sweatshirt with Black Collar | black | black sweatshirt | generic |
| PLT-DA18102 | Sweatshirt | 1 color names a part | Sweatshirt with Green Hem | green | green sweatshirt | generic |
| PLT-DA18200 | Sweatshirt | 2 another category's noun as a modifier | Red Hoodie Sweatshirt | hoodie | hoodie | generic |
| PLT-DA18201 | Sweatshirt | 2 another category's noun as a modifier | Pink Polo Sweatshirt | polo | polo | generic |
| PLT-DA18202 | Sweatshirt | 2 another category's noun as a modifier | White Hoodie Sweatshirt | hoodie | hoodie | generic |
| PLT-DA18300 | Sweatshirt | 3 audience word of a sibling version | Red Womens-Style Sweatshirt | womens | womens sweatshirt | generic |
| PLT-DA18301 | Sweatshirt | 3 audience word of a sibling version | Brown Womens Fit Sweatshirt | womens | womens sweatshirt | generic |
| PLT-DA18302 | Sweatshirt | 3 audience word of a sibling version | Blue Womens Fit Sweatshirt | womens | womens sweatshirt | generic |
| PLT-DA18400 | Sweatshirt | 4 material or feature named but absent | Blue Leather-Look Sweatshirt | leather | leather sweatshirt | special: material claim |
| PLT-DA18401 | Sweatshirt | 4 material or feature named but absent | Green Suede-Look Sweatshirt | suede | suede sweatshirt | special: material claim |
| PLT-DA18402 | Sweatshirt | 4 material or feature named but absent | Navy Cashmere-Feel Sweatshirt | cashmere | cashmere sweatshirt | special: material claim |
| PLT-DA18500 | Sweatshirt | 5 shade spelled in the description only | Moonbeam Sweatshirt | ivory | ivory sweatshirt | generic |
| PLT-DA18501 | Sweatshirt | 5 shade spelled in the description only | Driftwood Sweatshirt | taupe | taupe sweatshirt | generic |
| PLT-DA18502 | Sweatshirt | 5 shade spelled in the description only | Dune Sweatshirt | beige | beige sweatshirt | generic |
| PLT-DA18600 | Sweatshirt | 6 incidental word in a range name | Blazer Court Sweatshirt | blazer | blazer | generic |
| PLT-DA18601 | Sweatshirt | 6 incidental word in a range name | Sandal Wood Sweatshirt | sandal | sandal | generic |
| PLT-DA18602 | Sweatshirt | 6 incidental word in a range name | Coat Hook Sweatshirt | coat | coat | generic |
| PLT-DA18700 | Sweatshirt | 7 invented brand holding a color or category word | Red Plover Sweatshirt | red | red sweatshirt | generic |
| PLT-DA18701 | Sweatshirt | 7 invented brand holding a color or category word | Jumper Jay Sweatshirt | jumper | jumper sweatshirt | generic |
| PLT-DA18702 | Sweatshirt | 7 invented brand holding a color or category word | Jumper Jay Sweatshirt | jumper | jumper sweatshirt | generic |
| PLT-DA19100 | T-Shirt | 1 color names a part | T-Shirt with Blue Collar | blue | blue t-shirt | generic |
| PLT-DA19101 | T-Shirt | 1 color names a part | T-Shirt with Red Hem | red | red t-shirt | generic |
| PLT-DA19102 | T-Shirt | 1 color names a part | T-Shirt with White Hem | white | white t-shirt | generic |
| PLT-DA19200 | T-Shirt | 2 another category's noun as a modifier | Brown Tunic T-Shirt | tunic | tunic | generic |
| PLT-DA19201 | T-Shirt | 2 another category's noun as a modifier | Cream Polo T-Shirt | polo | polo | generic |
| PLT-DA19202 | T-Shirt | 2 another category's noun as a modifier | Cream Polo T-Shirt | polo | polo | generic |
| PLT-DA19300 | T-Shirt | 3 audience word of a sibling version | Grey Girls Fit T-Shirt | girls | girls t-shirt | generic |
| PLT-DA19301 | T-Shirt | 3 audience word of a sibling version | Brown Mens-Style T-Shirt | mens | mens t-shirt | generic |
| PLT-DA19302 | T-Shirt | 3 audience word of a sibling version | Pink Womens Fit T-Shirt | womens | womens t-shirt | generic |
| PLT-DA19400 | T-Shirt | 4 material or feature named but absent | Blue Leather-Look T-Shirt | leather | leather t-shirt | special: material claim |
| PLT-DA19401 | T-Shirt | 4 material or feature named but absent | Pink Suede-Look T-Shirt | suede | suede t-shirt | special: material claim |
| PLT-DA19402 | T-Shirt | 4 material or feature named but absent | White Cashmere-Feel T-Shirt | cashmere | cashmere t-shirt | special: material claim |
| PLT-DA19500 | T-Shirt | 5 shade spelled in the description only | Moonbeam T-Shirt | ivory | ivory t-shirt | generic |
| PLT-DA19501 | T-Shirt | 5 shade spelled in the description only | Driftwood T-Shirt | taupe | taupe t-shirt | generic |
| PLT-DA19502 | T-Shirt | 5 shade spelled in the description only | Dune T-Shirt | beige | beige t-shirt | generic |
| PLT-DA19600 | T-Shirt | 6 incidental word in a range name | Boot Hill T-Shirt | boot | boot | generic |
| PLT-DA19601 | T-Shirt | 6 incidental word in a range name | Boot Hill T-Shirt | boot | boot | generic |
| PLT-DA19602 | T-Shirt | 6 incidental word in a range name | Jacket Quay T-Shirt | jacket | jacket | generic |
| PLT-DA19700 | T-Shirt | 7 invented brand holding a color or category word | Red Plover T-Shirt | red | red t-shirt | generic |
| PLT-DA19701 | T-Shirt | 7 invented brand holding a color or category word | Blue Otter T-Shirt | blue | blue t-shirt | generic |
| PLT-DA19702 | T-Shirt | 7 invented brand holding a color or category word | Black Lapwing T-Shirt | black | black t-shirt | generic |
| PLT-DA20100 | Tea Dress | 1 color names a part | Tea Dress with Red Straps | red | red tea dress | generic |
| PLT-DA20101 | Tea Dress | 1 color names a part | Tea Dress with Black Straps | black | black tea dress | generic |
| PLT-DA20102 | Tea Dress | 1 color names a part | Tea Dress with Blue Straps | blue | blue tea dress | generic |
| PLT-DA20200 | Tea Dress | 2 another category's noun as a modifier | Cream Jumper Dress | jumper | jumper | generic |
| PLT-DA20201 | Tea Dress | 2 another category's noun as a modifier | Blue Tunic Dress | tunic | tunic | generic |
| PLT-DA20202 | Tea Dress | 2 another category's noun as a modifier | Pink Shirt Dress | shirt | shirt | generic |
| PLT-DA20300 | Tea Dress | 3 audience word of a sibling version | Black Mens Fit Tea Dress | mens | mens tea dress | generic |
| PLT-DA20301 | Tea Dress | 3 audience word of a sibling version | Brown Mens Fit Tea Dress | mens | mens tea dress | generic |
| PLT-DA20302 | Tea Dress | 3 audience word of a sibling version | Pink Mens-Style Tea Dress | mens | mens tea dress | generic |
| PLT-DA20400 | Tea Dress | 4 material or feature named but absent | Pink Leather-Look Tea Dress | leather | leather tea dress | special: material claim |
| PLT-DA20401 | Tea Dress | 4 material or feature named but absent | White Suede-Look Tea Dress | suede | suede tea dress | special: material claim |
| PLT-DA20402 | Tea Dress | 4 material or feature named but absent | Grey Cashmere-Feel Tea Dress | cashmere | cashmere tea dress | special: material claim |
| PLT-DA20500 | Tea Dress | 5 shade spelled in the description only | Moonbeam Tea Dress | ivory | ivory tea dress | generic |
| PLT-DA20501 | Tea Dress | 5 shade spelled in the description only | Driftwood Tea Dress | taupe | taupe tea dress | generic |
| PLT-DA20502 | Tea Dress | 5 shade spelled in the description only | Dune Tea Dress | beige | beige tea dress | generic |
| PLT-DA20600 | Tea Dress | 6 incidental word in a range name | Jumper Lane Tea Dress | jumper | jumper | generic |
| PLT-DA20601 | Tea Dress | 6 incidental word in a range name | Sock Hop Tea Dress | sock | sock | generic |
| PLT-DA20602 | Tea Dress | 6 incidental word in a range name | Boot Hill Tea Dress | boot | boot | generic |
| PLT-DA20700 | Tea Dress | 7 invented brand holding a color or category word | Red Plover Tea Dress | red | red tea dress | generic |
| PLT-DA20701 | Tea Dress | 7 invented brand holding a color or category word | Green Stoat Tea Dress | green | green tea dress | generic |
| PLT-DA20702 | Tea Dress | 7 invented brand holding a color or category word | Blue Otter Tea Dress | blue | blue tea dress | generic |
| PLT-DA21100 | Tee | 1 color names a part | Tee with Green Collar | green | green tee | generic |
| PLT-DA21101 | Tee | 1 color names a part | Tee with Black Collar | black | black tee | generic |
| PLT-DA21102 | Tee | 1 color names a part | Tee with Yellow Collar | yellow | yellow tee | generic |
| PLT-DA21200 | Tee | 2 another category's noun as a modifier | Pink Tunic Tee | tunic | tunic | generic |
| PLT-DA21201 | Tee | 2 another category's noun as a modifier | Blue Tunic Tee | tunic | tunic | generic |
| PLT-DA21202 | Tee | 2 another category's noun as a modifier | Red Tunic Tee | tunic | tunic | generic |
| PLT-DA21300 | Tee | 3 audience word of a sibling version | Green Womens Fit Tee | womens | womens tee | generic |
| PLT-DA21301 | Tee | 3 audience word of a sibling version | Grey Womens Fit Tee | womens | womens tee | generic |
| PLT-DA21302 | Tee | 3 audience word of a sibling version | Green Womens-Style Tee | womens | womens tee | generic |
| PLT-DA21400 | Tee | 4 material or feature named but absent | White Leather-Look Tee | leather | leather tee | special: material claim |
| PLT-DA21401 | Tee | 4 material or feature named but absent | Green Suede-Look Tee | suede | suede tee | special: material claim |
| PLT-DA21402 | Tee | 4 material or feature named but absent | Black Cashmere-Feel Tee | cashmere | cashmere tee | special: material claim |
| PLT-DA21500 | Tee | 5 shade spelled in the description only | Moonbeam Tee | ivory | ivory tee | generic |
| PLT-DA21501 | Tee | 5 shade spelled in the description only | Driftwood Tee | taupe | taupe tee | generic |
| PLT-DA21502 | Tee | 5 shade spelled in the description only | Dune Tee | beige | beige tee | generic |
| PLT-DA21600 | Tee | 6 incidental word in a range name | Sock Hop Tee | sock | sock | generic |
| PLT-DA21601 | Tee | 6 incidental word in a range name | Shoe Lane Tee | shoe | shoe | generic |
| PLT-DA21602 | Tee | 6 incidental word in a range name | Boot Hill Tee | boot | boot | generic |
| PLT-DA21700 | Tee | 7 invented brand holding a color or category word | Red Plover Tee | red | red tee | generic |
| PLT-DA21701 | Tee | 7 invented brand holding a color or category word | White Dormouse Tee | white | white tee | generic |
| PLT-DA21702 | Tee | 7 invented brand holding a color or category word | Black Lapwing Tee | black | black tee | generic |
| PLT-DA22100 | Top | 1 color names a part | Top with Blue Hem | blue | blue top | generic |
| PLT-DA22101 | Top | 1 color names a part | Top with Blue Collar | blue | blue top | generic |
| PLT-DA22102 | Top | 1 color names a part | Top with White Hem | white | white top | generic |
| PLT-DA22200 | Top | 2 another category's noun as a modifier | Pink Vest Top | vest | vest | generic |
| PLT-DA22201 | Top | 2 another category's noun as a modifier | Navy Cami Top | cami | cami | generic |
| PLT-DA22202 | Top | 2 another category's noun as a modifier | Red Vest Top | vest | vest | generic |
| PLT-DA22300 | Top | 3 audience word of a sibling version | Green Mens-Style Top | mens | mens top | generic |
| PLT-DA22301 | Top | 3 audience word of a sibling version | Pink Boys Fit Top | boys | boys top | generic |
| PLT-DA22302 | Top | 3 audience word of a sibling version | White Boys Fit Top | boys | boys top | generic |
| PLT-DA22400 | Top | 4 material or feature named but absent | Cream Leather-Look Top | leather | leather top | special: material claim |
| PLT-DA22401 | Top | 4 material or feature named but absent | Cream Suede-Look Top | suede | suede top | special: material claim |
| PLT-DA22402 | Top | 4 material or feature named but absent | Red Cashmere-Feel Top | cashmere | cashmere top | special: material claim |
| PLT-DA22500 | Top | 5 shade spelled in the description only | Moonbeam Top | ivory | ivory top | generic |
| PLT-DA22501 | Top | 5 shade spelled in the description only | Driftwood Top | taupe | taupe top | generic |
| PLT-DA22502 | Top | 5 shade spelled in the description only | Dune Top | beige | beige top | generic |
| PLT-DA22600 | Top | 6 incidental word in a range name | Dress Circle Top | dress | dress | generic |
| PLT-DA22601 | Top | 6 incidental word in a range name | Shirt Row Top | shirt | shirt | generic |
| PLT-DA22602 | Top | 6 incidental word in a range name | Slipper Brook Top | slipper | slipper | generic |
| PLT-DA22700 | Top | 7 invented brand holding a color or category word | Blue Otter Top | blue | blue top | generic |
| PLT-DA22701 | Top | 7 invented brand holding a color or category word | Green Stoat Top | green | green top | generic |
| PLT-DA22702 | Top | 7 invented brand holding a color or category word | Red Plover Top | red | red top | generic |
| PLT-DA23100 | Tracksuit | 1 color names a part | Regular Tracksuit with Red Cuffs | red | red tracksuit | generic |
| PLT-DA23101 | Tracksuit | 1 color names a part | Regular Tracksuit with White Cuffs | white | white tracksuit | generic |
| PLT-DA23102 | Tracksuit | 1 color names a part | Regular Tracksuit with White Cuffs | white | white tracksuit | generic |
| PLT-DA23200 | Tracksuit | 2 another category's noun as a modifier | Green Slim Jogger Tracksuit | jogger | jogger | generic |
| PLT-DA23201 | Tracksuit | 2 another category's noun as a modifier | Navy Relaxed Jogger Tracksuit | jogger | jogger | generic |
| PLT-DA23202 | Tracksuit | 2 another category's noun as a modifier | Red Regular Jogger Tracksuit | jogger | jogger | generic |
| PLT-DA23300 | Tracksuit | 3 audience word of a sibling version | White Mens Fit Relaxed Tracksuit | mens | mens tracksuit | generic |
| PLT-DA23301 | Tracksuit | 3 audience word of a sibling version | Red Mens-Style Slim Tracksuit | mens | mens tracksuit | generic |
| PLT-DA23302 | Tracksuit | 3 audience word of a sibling version | Red Mini-Me Womens Regular Tracksuit | womens | womens tracksuit | generic |
| PLT-DA23400 | Tracksuit | 4 material or feature named but absent | Pink Leather-Look Regular Tracksuit | leather | leather tracksuit | special: material claim |
| PLT-DA23401 | Tracksuit | 4 material or feature named but absent | Green Suede-Look Regular Tracksuit | suede | suede tracksuit | special: material claim |
| PLT-DA23402 | Tracksuit | 4 material or feature named but absent | Cream Cashmere-Feel Slim Tracksuit | cashmere | cashmere tracksuit | special: material claim |
| PLT-DA23500 | Tracksuit | 5 shade spelled in the description only | Moonbeam Relaxed Tracksuit | ivory | ivory tracksuit | generic |
| PLT-DA23501 | Tracksuit | 5 shade spelled in the description only | Driftwood Regular Tracksuit | taupe | taupe tracksuit | generic |
| PLT-DA23502 | Tracksuit | 5 shade spelled in the description only | Dune Relaxed Tracksuit | beige | beige tracksuit | generic |
| PLT-DA23600 | Tracksuit | 6 incidental word in a range name | Skirt Point Slim Tracksuit | skirt | skirt | generic |
| PLT-DA23601 | Tracksuit | 6 incidental word in a range name | Jumper Lane Regular Tracksuit | jumper | jumper | generic |
| PLT-DA23602 | Tracksuit | 6 incidental word in a range name | Slip Road Regular Tracksuit | slip | slip | generic |
| PLT-DA23700 | Tracksuit | 7 invented brand holding a color or category word | Yellow Wagtail Regular Tracksuit | yellow | yellow tracksuit | generic |
| PLT-DA23701 | Tracksuit | 7 invented brand holding a color or category word | Black Lapwing Slim Tracksuit | black | black tracksuit | generic |
| PLT-DA23702 | Tracksuit | 7 invented brand holding a color or category word | White Dormouse Relaxed Tracksuit | white | white tracksuit | generic |
| PLT-DA24100 | Trousers | 1 color names a part | Barrel Trousers with Green Cuffs | green | green trousers | generic |
| PLT-DA24101 | Trousers | 1 color names a part | Barrel Trousers with White Waistband | white | white trousers | generic |
| PLT-DA24102 | Trousers | 1 color names a part | Barrel Trousers with Red Waistband | red | red trousers | generic |
| PLT-DA24200 | Trousers | 2 another category's noun as a modifier | Blue Barrel Chino Trousers | chino | chino | generic |
| PLT-DA24201 | Trousers | 2 another category's noun as a modifier | Brown Wide Leg Cargo Trousers | cargo | cargo | generic |
| PLT-DA24202 | Trousers | 2 another category's noun as a modifier | Black Tapered Dress Trousers | dress | dress | generic |
| PLT-DA24300 | Trousers | 3 audience word of a sibling version | White Mens Fit Straight Trousers | mens | mens trousers | generic |
| PLT-DA24301 | Trousers | 3 audience word of a sibling version | Black Boys Fit Slim Trousers | boys | boys trousers | generic |
| PLT-DA24302 | Trousers | 3 audience word of a sibling version | Cream Mens Fit Wide Leg Trousers | mens | mens trousers | generic |
| PLT-DA24400 | Trousers | 4 material or feature named but absent | Grey Leather-Look Tapered Trousers | leather | leather trousers | special: material claim |
| PLT-DA24401 | Trousers | 4 material or feature named but absent | Green Suede-Look Straight Trousers | suede | suede trousers | special: material claim |
| PLT-DA24402 | Trousers | 4 material or feature named but absent | Grey Cashmere-Feel Slim Trousers | cashmere | cashmere trousers | special: material claim |
| PLT-DA24500 | Trousers | 5 shade spelled in the description only | Moonbeam Wide Leg Trousers | ivory | ivory trousers | generic |
| PLT-DA24501 | Trousers | 5 shade spelled in the description only | Driftwood Tapered Trousers | taupe | taupe trousers | generic |
| PLT-DA24502 | Trousers | 5 shade spelled in the description only | Dune Straight Trousers | beige | beige trousers | generic |
| PLT-DA24600 | Trousers | 6 incidental word in a range name | Shirt Row Slim Trousers | shirt | shirt | generic |
| PLT-DA24601 | Trousers | 6 incidental word in a range name | Skirt Point Wide Leg Trousers | skirt | skirt | generic |
| PLT-DA24602 | Trousers | 6 incidental word in a range name | Sandal Wood Tapered Trousers | sandal | sandal | generic |
| PLT-DA24700 | Trousers | 7 invented brand holding a color or category word | Yellow Wagtail Straight Trousers | yellow | yellow trousers | generic |
| PLT-DA24701 | Trousers | 7 invented brand holding a color or category word | Green Stoat Slim Trousers | green | green trousers | generic |
| PLT-DA24702 | Trousers | 7 invented brand holding a color or category word | White Dormouse Wide Leg Trousers | white | white trousers | generic |
| PLT-DA25100 | Jeans | 1 color names a part | Jegging Jeans with White Waistband | white | white jeans | generic |
| PLT-DA25101 | Jeans | 1 color names a part | Skinny Jeans with Red Cuffs | red | red jeans | generic |
| PLT-DA25102 | Jeans | 1 color names a part | Bootcut Jeans with Black Waistband | black | black jeans | generic |
| PLT-DA25103 | Jeans | 1 color names a part | Kick Flare Jeans with Red Waistband | red | red jeans | generic |
| PLT-DA25104 | Jeans | 1 color names a part | Tapered Jeans with Yellow Waistband | yellow | yellow jeans | generic |
| PLT-DA25105 | Jeans | 1 color names a part | Straight Jeans with Blue Waistband | blue | blue jeans | generic |
| PLT-DA25106 | Jeans | 1 color names a part | Cigarette Jeans with Yellow Cuffs | yellow | yellow jeans | generic |
| PLT-DA25107 | Jeans | 1 color names a part | Baggy Jeans with Red Waistband | red | red jeans | generic |
| PLT-DA25108 | Jeans | 1 color names a part | Super Skinny Jeans with White Cuffs | white | white jeans | generic |
| PLT-DA25109 | Jeans | 1 color names a part | Cropped Jeans with Green Waistband | green | green jeans | generic |
| PLT-DA25110 | Jeans | 1 color names a part | Wide Leg Jeans with Yellow Waistband | yellow | yellow jeans | generic |
| PLT-DA25111 | Jeans | 1 color names a part | Wide Leg Jeans with Red Cuffs | red | red jeans | generic |
| PLT-DA25200 | Jeans | 2 another category's noun as a modifier | Brown Tapered Jogger Jeans | jogger | jogger | generic |
| PLT-DA25201 | Jeans | 2 another category's noun as a modifier | White Athletic Cargo Jeans | cargo | cargo | generic |
| PLT-DA25202 | Jeans | 2 another category's noun as a modifier | Navy Culotte Cargo Jeans | cargo | cargo | generic |
| PLT-DA25203 | Jeans | 2 another category's noun as a modifier | White Wide Leg Cargo Jeans | cargo | cargo | generic |
| PLT-DA25204 | Jeans | 2 another category's noun as a modifier | Black Bootcut Jogger Jeans | jogger | jogger | generic |
| PLT-DA25205 | Jeans | 2 another category's noun as a modifier | Red Cropped Jogger Jeans | jogger | jogger | generic |
| PLT-DA25206 | Jeans | 2 another category's noun as a modifier | Blue Bootcut Cargo Jeans | cargo | cargo | generic |
| PLT-DA25207 | Jeans | 2 another category's noun as a modifier | Black Relaxed Cargo Jeans | cargo | cargo | generic |
| PLT-DA25208 | Jeans | 2 another category's noun as a modifier | Red Slim Cargo Jeans | cargo | cargo | generic |
| PLT-DA25209 | Jeans | 2 another category's noun as a modifier | Brown Skinny Cargo Jeans | cargo | cargo | generic |
| PLT-DA25210 | Jeans | 2 another category's noun as a modifier | White Mom Jogger Jeans | jogger | jogger | generic |
| PLT-DA25211 | Jeans | 2 another category's noun as a modifier | White Straight Jogger Jeans | jogger | jogger | generic |
| PLT-DA25300 | Jeans | 3 audience word of a sibling version | Cream Womens Fit Baggy Jeans | womens | womens jeans | generic |
| PLT-DA25301 | Jeans | 3 audience word of a sibling version | Navy Girls Fit Athletic Jeans | girls | girls jeans | generic |
| PLT-DA25302 | Jeans | 3 audience word of a sibling version | Pink Boys Fit Tapered Jeans | boys | boys jeans | generic |
| PLT-DA25303 | Jeans | 3 audience word of a sibling version | Black Womens Fit Carrot Jeans | womens | womens jeans | generic |
| PLT-DA25304 | Jeans | 3 audience word of a sibling version | White Mens Fit Carrot Jeans | mens | mens jeans | generic |
| PLT-DA25305 | Jeans | 3 audience word of a sibling version | Pink Womens Fit Relaxed Jeans | womens | womens jeans | generic |
| PLT-DA25306 | Jeans | 3 audience word of a sibling version | Navy Boys Fit Super Skinny Jeans | boys | boys jeans | generic |
| PLT-DA25307 | Jeans | 3 audience word of a sibling version | Cream Boys Fit Jegging Jeans | boys | boys jeans | generic |
| PLT-DA25308 | Jeans | 3 audience word of a sibling version | Pink Mens-Style Flared Jeans | mens | mens jeans | generic |
| PLT-DA25309 | Jeans | 3 audience word of a sibling version | Navy Mens-Style Kick Flare Jeans | mens | mens jeans | generic |
| PLT-DA25310 | Jeans | 3 audience word of a sibling version | Pink Mens Fit Bootcut Jeans | mens | mens jeans | generic |
| PLT-DA25311 | Jeans | 3 audience word of a sibling version | Brown Mens Fit Boyfriend Jeans | mens | mens jeans | generic |
| PLT-DA25400 | Jeans | 4 material or feature named but absent | Pink Leather-Look Barrel Jeans | leather | leather jeans | special: material claim |
| PLT-DA25401 | Jeans | 4 material or feature named but absent | Pink Suede-Look Athletic Jeans | suede | suede jeans | special: material claim |
| PLT-DA25402 | Jeans | 4 material or feature named but absent | White Cashmere-Feel Barrel Jeans | cashmere | cashmere jeans | special: material claim |
| PLT-DA25403 | Jeans | 4 material or feature named but absent | Cream Wool-Free Balloon Jeans | wool | wool jeans | special: material claim |
| PLT-DA25404 | Jeans | 4 material or feature named but absent | Pink Silk-Feel Slim Jeans | silk | silk jeans | special: material claim |
| PLT-DA25405 | Jeans | 4 material or feature named but absent | Blue Linen-Look Cigarette Jeans | linen | linen jeans | special: material claim |
| PLT-DA25406 | Jeans | 4 material or feature named but absent | Red Lace-Free Mom Jeans | lace | lace jeans | special: material claim |
| PLT-DA25407 | Jeans | 4 material or feature named but absent | Navy Velvet-Feel Balloon Jeans | velvet | velvet jeans | special: material claim |
| PLT-DA25408 | Jeans | 4 material or feature named but absent | Green Denim-Look Flared Jeans | denim | denim jeans | special: material claim |
| PLT-DA25409 | Jeans | 4 material or feature named but absent | Pink Satin-Look Cropped Jeans | satin | satin jeans | special: material claim |
| PLT-DA25410 | Jeans | 4 material or feature named but absent | Black Mohair-Free Slim Jeans | mohair | mohair jeans | special: material claim |
| PLT-DA25411 | Jeans | 4 material or feature named but absent | Cream Tweed-Look Baggy Jeans | tweed | tweed jeans | special: material claim |
| PLT-DA25500 | Jeans | 5 shade spelled in the description only | Moonbeam Flared Jeans | ivory | ivory jeans | generic |
| PLT-DA25501 | Jeans | 5 shade spelled in the description only | Driftwood Boyfriend Jeans | taupe | taupe jeans | generic |
| PLT-DA25502 | Jeans | 5 shade spelled in the description only | Dune Slim Jeans | beige | beige jeans | generic |
| PLT-DA25503 | Jeans | 5 shade spelled in the description only | Ember Straight Jeans | burgundy | burgundy jeans | generic |
| PLT-DA25504 | Jeans | 5 shade spelled in the description only | Lagoon Skinny Jeans | teal | teal jeans | generic |
| PLT-DA25505 | Jeans | 5 shade spelled in the description only | Willow Culotte Jeans | olive | olive jeans | generic |
| PLT-DA25506 | Jeans | 5 shade spelled in the description only | Pebble Balloon Jeans | ecru | ecru jeans | generic |
| PLT-DA25507 | Jeans | 5 shade spelled in the description only | Meadow Balloon Jeans | mint | mint jeans | generic |
| PLT-DA25508 | Jeans | 5 shade spelled in the description only | Harvest Balloon Jeans | rust | rust jeans | generic |
| PLT-DA25509 | Jeans | 5 shade spelled in the description only | Seashell Barrel Jeans | coral | coral jeans | generic |
| PLT-DA25510 | Jeans | 5 shade spelled in the description only | Biscuit Barrel Jeans | champagne | champagne jeans | generic |
| PLT-DA25511 | Jeans | 5 shade spelled in the description only | Hearth Barrel Jeans | khaki | khaki jeans | generic |
| PLT-DA25600 | Jeans | 6 incidental word in a range name | Sandal Wood Barrel Jeans | sandal | sandal | generic |
| PLT-DA25601 | Jeans | 6 incidental word in a range name | Jacket Quay Barrel Jeans | jacket | jacket | generic |
| PLT-DA25602 | Jeans | 6 incidental word in a range name | Dress Circle Barrel Jeans | dress | dress | generic |
| PLT-DA25603 | Jeans | 6 incidental word in a range name | Coat Hook Barrel Jeans | coat | coat | generic |
| PLT-DA25604 | Jeans | 6 incidental word in a range name | Sandal Wood Balloon Jeans | sandal | sandal | generic |
| PLT-DA25605 | Jeans | 6 incidental word in a range name | Boot Hill Balloon Jeans | boot | boot | generic |
| PLT-DA25606 | Jeans | 6 incidental word in a range name | Dress Circle Balloon Jeans | dress | dress | generic |
| PLT-DA25607 | Jeans | 6 incidental word in a range name | Skirt Point Barrel Jeans | skirt | skirt | generic |
| PLT-DA25608 | Jeans | 6 incidental word in a range name | Slip Road Barrel Jeans | slip | slip | generic |
| PLT-DA25609 | Jeans | 6 incidental word in a range name | Shirt Row Barrel Jeans | shirt | shirt | generic |
| PLT-DA25610 | Jeans | 6 incidental word in a range name | Sock Hop Barrel Jeans | sock | sock | generic |
| PLT-DA25611 | Jeans | 6 incidental word in a range name | Slipper Brook Barrel Jeans | slipper | slipper | generic |
| PLT-DA25700 | Jeans | 7 invented brand holding a color or category word | Yellow Wagtail Barrel Jeans | yellow | yellow jeans | generic |
| PLT-DA25701 | Jeans | 7 invented brand holding a color or category word | Red Plover Barrel Jeans | red | red jeans | generic |
| PLT-DA25702 | Jeans | 7 invented brand holding a color or category word | Black Lapwing Barrel Jeans | black | black jeans | generic |
| PLT-DA25703 | Jeans | 7 invented brand holding a color or category word | Coat Crake Barrel Jeans | coat | coat jeans | generic |
| PLT-DA25704 | Jeans | 7 invented brand holding a color or category word | Jumper Jay Barrel Jeans | jumper | jumper jeans | generic |
| PLT-DA25705 | Jeans | 7 invented brand holding a color or category word | White Dormouse Barrel Jeans | white | white jeans | generic |
| PLT-DA25706 | Jeans | 7 invented brand holding a color or category word | Blue Otter Barrel Jeans | blue | blue jeans | generic |
| PLT-DA25707 | Jeans | 7 invented brand holding a color or category word | Green Stoat Straight Jeans | green | green jeans | generic |
| PLT-DA26100 | Socks | 1 color names a part | Socks with Black Heel | black | black socks | generic |
| PLT-DA26101 | Socks | 1 color names a part | Socks with Green Toe | green | green socks | generic |
| PLT-DA26102 | Socks | 1 color names a part | Socks with Red Toe | red | red socks | generic |
| PLT-DA26200 | Socks | 2 another category's noun as a modifier | Green Trouser Socks | trouser | trouser | generic |
| PLT-DA26201 | Socks | 2 another category's noun as a modifier | Cream Slipper Socks | slipper | slipper | generic |
| PLT-DA26202 | Socks | 2 another category's noun as a modifier | Black Boot Socks | boot | boot | generic |
| PLT-DA26300 | Socks | 3 audience word of a sibling version | White Womens-Style Socks | womens | womens socks | generic |
| PLT-DA26301 | Socks | 3 audience word of a sibling version | Blue Womens Fit Socks | womens | womens socks | generic |
| PLT-DA26302 | Socks | 3 audience word of a sibling version | Grey Womens-Style Socks | womens | womens socks | generic |
| PLT-DA26400 | Socks | 4 material or feature named but absent | Green Leather-Look Socks | leather | leather socks | special: material claim |
| PLT-DA26401 | Socks | 4 material or feature named but absent | Cream Suede-Look Socks | suede | suede socks | special: material claim |
| PLT-DA26402 | Socks | 4 material or feature named but absent | Cream Cashmere-Feel Socks | cashmere | cashmere socks | special: material claim |
| PLT-DA26500 | Socks | 5 shade spelled in the description only | Moonbeam Socks | ivory | ivory socks | generic |
| PLT-DA26501 | Socks | 5 shade spelled in the description only | Driftwood Socks | taupe | taupe socks | generic |
| PLT-DA26502 | Socks | 5 shade spelled in the description only | Dune Socks | beige | beige socks | generic |
| PLT-DA26600 | Socks | 6 incidental word in a range name | Dress Circle Socks | dress | dress | generic |
| PLT-DA26601 | Socks | 6 incidental word in a range name | Slip Road Socks | slip | slip | generic |
| PLT-DA26602 | Socks | 6 incidental word in a range name | Boot Hill Socks | boot | boot | generic |
| PLT-DA26700 | Socks | 7 invented brand holding a color or category word | Green Stoat Socks | green | green socks | generic |
| PLT-DA26701 | Socks | 7 invented brand holding a color or category word | White Dormouse Socks | white | white socks | generic |
| PLT-DA26702 | Socks | 7 invented brand holding a color or category word | Blue Otter Socks | blue | blue socks | generic |
| PLT-DA27100 | Boot Socks | 1 color names a part | Boot Socks with Black Cuff | black | black boot socks | generic |
| PLT-DA27101 | Boot Socks | 1 color names a part | Boot Socks with Green Heel | green | green boot socks | generic |
| PLT-DA27102 | Boot Socks | 1 color names a part | Boot Socks with White Toe | white | white boot socks | generic |
| PLT-DA27200 | Boot Socks | 2 another category's noun as a modifier | Grey Welly Boot Socks | welly | welly | generic |
| PLT-DA27201 | Boot Socks | 2 another category's noun as a modifier | Pink Walking Boot Socks | walking | walking | generic |
| PLT-DA27202 | Boot Socks | 2 another category's noun as a modifier | White Welly Boot Socks | welly | welly | generic |
| PLT-DA27300 | Boot Socks | 3 audience word of a sibling version | Cream Boys Fit Boot Socks | boys | boys boot socks | generic |
| PLT-DA27301 | Boot Socks | 3 audience word of a sibling version | Red Boys Fit Boot Socks | boys | boys boot socks | generic |
| PLT-DA27302 | Boot Socks | 3 audience word of a sibling version | Cream Mens-Style Boot Socks | mens | mens boot socks | generic |
| PLT-DA27400 | Boot Socks | 4 material or feature named but absent | Green Leather-Look Boot Socks | leather | leather boot socks | special: material claim |
| PLT-DA27401 | Boot Socks | 4 material or feature named but absent | Pink Suede-Look Boot Socks | suede | suede boot socks | special: material claim |
| PLT-DA27402 | Boot Socks | 4 material or feature named but absent | Red Cashmere-Feel Boot Socks | cashmere | cashmere boot socks | special: material claim |
| PLT-DA27500 | Boot Socks | 5 shade spelled in the description only | Moonbeam Boot Socks | ivory | ivory boot socks | generic |
| PLT-DA27501 | Boot Socks | 5 shade spelled in the description only | Driftwood Boot Socks | taupe | taupe boot socks | generic |
| PLT-DA27502 | Boot Socks | 5 shade spelled in the description only | Dune Boot Socks | beige | beige boot socks | generic |
| PLT-DA27600 | Boot Socks | 6 incidental word in a range name | Sandal Wood Boot Socks | sandal | sandal | generic |
| PLT-DA27601 | Boot Socks | 6 incidental word in a range name | Slip Road Boot Socks | slip | slip | generic |
| PLT-DA27602 | Boot Socks | 6 incidental word in a range name | Shirt Row Boot Socks | shirt | shirt | generic |
| PLT-DA27700 | Boot Socks | 7 invented brand holding a color or category word | Blue Otter Boot Socks | blue | blue boot socks | generic |
| PLT-DA27701 | Boot Socks | 7 invented brand holding a color or category word | Red Plover Boot Socks | red | red boot socks | generic |
| PLT-DA27702 | Boot Socks | 7 invented brand holding a color or category word | White Dormouse Boot Socks | white | white boot socks | generic |
| PLT-DA28100 | Ankle Boots | 1 color names a part | Ankle Boots with Black Sole | black | black ankle boots | generic |
| PLT-DA28101 | Ankle Boots | 1 color names a part | Ankle Boots with White Sole | white | white ankle boots | generic |
| PLT-DA28102 | Ankle Boots | 1 color names a part | Ankle Boots with Blue Sole | blue | blue ankle boots | generic |
| PLT-DA28200 | Ankle Boots | 2 another category's noun as a modifier | Green Loafer Boots | loafer | loafer | generic |
| PLT-DA28201 | Ankle Boots | 2 another category's noun as a modifier | Pink Sandal Boots | sandal | sandal | generic |
| PLT-DA28202 | Ankle Boots | 2 another category's noun as a modifier | Brown Sandal Boots | sandal | sandal | generic |
| PLT-DA28300 | Ankle Boots | 3 audience word of a sibling version | Red Mens-Style Ankle Boots | mens | mens ankle boots | generic |
| PLT-DA28301 | Ankle Boots | 3 audience word of a sibling version | White Mens Fit Ankle Boots | mens | mens ankle boots | generic |
| PLT-DA28302 | Ankle Boots | 3 audience word of a sibling version | Grey Boys Fit Ankle Boots | boys | boys ankle boots | generic |
| PLT-DA28400 | Ankle Boots | 4 material or feature named but absent | Grey Leather-Look Ankle Boots | leather | leather ankle boots | special: material claim |
| PLT-DA28401 | Ankle Boots | 4 material or feature named but absent | White Cashmere-Feel Ankle Boots | cashmere | cashmere ankle boots | special: material claim |
| PLT-DA28402 | Ankle Boots | 4 material or feature named but absent | Cream Wool-Free Ankle Boots | wool | wool ankle boots | special: material claim |
| PLT-DA28500 | Ankle Boots | 5 shade spelled in the description only | Moonbeam Ankle Boots | ivory | ivory ankle boots | generic |
| PLT-DA28501 | Ankle Boots | 5 shade spelled in the description only | Driftwood Ankle Boots | taupe | taupe ankle boots | generic |
| PLT-DA28502 | Ankle Boots | 5 shade spelled in the description only | Dune Ankle Boots | beige | beige ankle boots | generic |
| PLT-DA28600 | Ankle Boots | 6 incidental word in a range name | Sandal Wood Ankle Boots | sandal | sandal | generic |
| PLT-DA28601 | Ankle Boots | 6 incidental word in a range name | Coat Hook Ankle Boots | coat | coat | generic |
| PLT-DA28602 | Ankle Boots | 6 incidental word in a range name | Cardigan Bay Ankle Boots | cardigan | cardigan | generic |
| PLT-DA28700 | Ankle Boots | 7 invented brand holding a color or category word | Blue Otter Ankle Boots | blue | blue ankle boots | generic |
| PLT-DA28701 | Ankle Boots | 7 invented brand holding a color or category word | Coat Crake Ankle Boots | coat | coat ankle boots | generic |
| PLT-DA28702 | Ankle Boots | 7 invented brand holding a color or category word | Yellow Wagtail Ankle Boots | yellow | yellow ankle boots | generic |
| PLT-DA29100 | Ballet Pumps | 1 color names a part | Ballet Pumps with Blue Sole | blue | blue ballet pumps | generic |
| PLT-DA29101 | Ballet Pumps | 1 color names a part | Ballet Pumps with Red Sole | red | red ballet pumps | generic |
| PLT-DA29102 | Ballet Pumps | 1 color names a part | Ballet Pumps with White Sole | white | white ballet pumps | generic |
| PLT-DA29200 | Ballet Pumps | 2 another category's noun as a modifier | Grey Ballet Slippers | slipper | slipper | generic |
| PLT-DA29201 | Ballet Pumps | 2 another category's noun as a modifier | Black Ballet Sandals | sandal | sandal | generic |
| PLT-DA29202 | Ballet Pumps | 2 another category's noun as a modifier | Navy Ballet Slippers | slipper | slipper | generic |
| PLT-DA29300 | Ballet Pumps | 3 audience word of a sibling version | Brown Mens-Style Ballet Pumps | mens | mens ballet pumps | generic |
| PLT-DA29301 | Ballet Pumps | 3 audience word of a sibling version | Green Mens-Style Ballet Pumps | mens | mens ballet pumps | generic |
| PLT-DA29302 | Ballet Pumps | 3 audience word of a sibling version | Red Mens Fit Ballet Pumps | mens | mens ballet pumps | generic |
| PLT-DA29400 | Ballet Pumps | 4 material or feature named but absent | Black Cashmere-Feel Ballet Pumps | cashmere | cashmere ballet pumps | special: material claim |
| PLT-DA29401 | Ballet Pumps | 4 material or feature named but absent | Blue Wool-Free Ballet Pumps | wool | wool ballet pumps | special: material claim |
| PLT-DA29402 | Ballet Pumps | 4 material or feature named but absent | Blue Leather-Look Ballet Pumps | leather | leather ballet pumps | special: material claim |
| PLT-DA29500 | Ballet Pumps | 5 shade spelled in the description only | Moonbeam Ballet Pumps | ivory | ivory ballet pumps | generic |
| PLT-DA29501 | Ballet Pumps | 5 shade spelled in the description only | Driftwood Ballet Pumps | taupe | taupe ballet pumps | generic |
| PLT-DA29502 | Ballet Pumps | 5 shade spelled in the description only | Dune Ballet Pumps | beige | beige ballet pumps | generic |
| PLT-DA29600 | Ballet Pumps | 6 incidental word in a range name | Sock Hop Ballet Pumps | sock | sock | generic |
| PLT-DA29601 | Ballet Pumps | 6 incidental word in a range name | Jacket Quay Ballet Pumps | jacket | jacket | generic |
| PLT-DA29602 | Ballet Pumps | 6 incidental word in a range name | Slipper Brook Ballet Pumps | slipper | slipper | generic |
| PLT-DA29700 | Ballet Pumps | 7 invented brand holding a color or category word | Black Lapwing Ballet Pumps | black | black ballet pumps | generic |
| PLT-DA29701 | Ballet Pumps | 7 invented brand holding a color or category word | White Dormouse Ballet Pumps | white | white ballet pumps | generic |
| PLT-DA29702 | Ballet Pumps | 7 invented brand holding a color or category word | Jumper Jay Ballet Pumps | jumper | jumper ballet pumps | generic |
| PLT-DA30100 | Block Heels | 1 color names a part | Block Heels with Blue Sole | blue | blue block heels | generic |
| PLT-DA30101 | Block Heels | 1 color names a part | Block Heels with Yellow Sole | yellow | yellow block heels | generic |
| PLT-DA30102 | Block Heels | 1 color names a part | Block Heels with Green Sole | green | green block heels | generic |
| PLT-DA30200 | Block Heels | 2 another category's noun as a modifier | Pink Loafer Heels | loafer | loafer | generic |
| PLT-DA30201 | Block Heels | 2 another category's noun as a modifier | Brown Loafer Heels | loafer | loafer | generic |
| PLT-DA30202 | Block Heels | 2 another category's noun as a modifier | Pink Mule Heels | mule | mule | generic |
| PLT-DA30300 | Block Heels | 3 audience word of a sibling version | Red Mens Fit Block Heels | mens | mens block heels | generic |
| PLT-DA30301 | Block Heels | 3 audience word of a sibling version | Brown Boys Fit Block Heels | boys | boys block heels | generic |
| PLT-DA30302 | Block Heels | 3 audience word of a sibling version | White Mens Fit Block Heels | mens | mens block heels | generic |
| PLT-DA30400 | Block Heels | 4 material or feature named but absent | Pink Cashmere-Feel Block Heels | cashmere | cashmere block heels | special: material claim |
| PLT-DA30401 | Block Heels | 4 material or feature named but absent | Red Wool-Free Block Heels | wool | wool block heels | special: material claim |
| PLT-DA30402 | Block Heels | 4 material or feature named but absent | Cream Leather-Look Block Heels | leather | leather block heels | special: material claim |
| PLT-DA30500 | Block Heels | 5 shade spelled in the description only | Moonbeam Block Heels | ivory | ivory block heels | generic |
| PLT-DA30501 | Block Heels | 5 shade spelled in the description only | Driftwood Block Heels | taupe | taupe block heels | generic |
| PLT-DA30502 | Block Heels | 5 shade spelled in the description only | Dune Block Heels | beige | beige block heels | generic |
| PLT-DA30600 | Block Heels | 6 incidental word in a range name | Slipper Brook Block Heels | slipper | slipper | generic |
| PLT-DA30601 | Block Heels | 6 incidental word in a range name | Blazer Court Block Heels | blazer | blazer | generic |
| PLT-DA30602 | Block Heels | 6 incidental word in a range name | Cardigan Bay Block Heels | cardigan | cardigan | generic |
| PLT-DA30700 | Block Heels | 7 invented brand holding a color or category word | Red Plover Block Heels | red | red block heels | generic |
| PLT-DA30701 | Block Heels | 7 invented brand holding a color or category word | Coat Crake Block Heels | coat | coat block heels | generic |
| PLT-DA30702 | Block Heels | 7 invented brand holding a color or category word | Green Stoat Block Heels | green | green block heels | generic |
| PLT-DA31100 | Brogues | 1 color names a part | Brogues with Green Sole | green | green brogues | generic |
| PLT-DA31101 | Brogues | 1 color names a part | Brogues with Yellow Sole | yellow | yellow brogues | generic |
| PLT-DA31102 | Brogues | 1 color names a part | Brogues with Blue Sole | blue | blue brogues | generic |
| PLT-DA31200 | Brogues | 2 another category's noun as a modifier | Cream Derby Brogues | derby | derby | generic |
| PLT-DA31201 | Brogues | 2 another category's noun as a modifier | Blue Dress Brogues | dress | dress | generic |
| PLT-DA31202 | Brogues | 2 another category's noun as a modifier | Brown Oxford Brogues | oxford | oxford | generic |
| PLT-DA31300 | Brogues | 3 audience word of a sibling version | Brown Mens Fit Brogues | mens | mens brogues | generic |
| PLT-DA31301 | Brogues | 3 audience word of a sibling version | Grey Womens-Style Brogues | womens | womens brogues | generic |
| PLT-DA31302 | Brogues | 3 audience word of a sibling version | Red Girls Fit Brogues | girls | girls brogues | generic |
| PLT-DA31400 | Brogues | 4 material or feature named but absent | White Leather-Look Brogues | leather | leather brogues | special: material claim |
| PLT-DA31401 | Brogues | 4 material or feature named but absent | Red Suede-Look Brogues | suede | suede brogues | special: material claim |
| PLT-DA31402 | Brogues | 4 material or feature named but absent | Green Cashmere-Feel Brogues | cashmere | cashmere brogues | special: material claim |
| PLT-DA31500 | Brogues | 5 shade spelled in the description only | Moonbeam Brogues | ivory | ivory brogues | generic |
| PLT-DA31501 | Brogues | 5 shade spelled in the description only | Driftwood Brogues | taupe | taupe brogues | generic |
| PLT-DA31502 | Brogues | 5 shade spelled in the description only | Dune Brogues | beige | beige brogues | generic |
| PLT-DA31600 | Brogues | 6 incidental word in a range name | Slipper Brook Brogues | slipper | slipper | generic |
| PLT-DA31601 | Brogues | 6 incidental word in a range name | Jumper Lane Brogues | jumper | jumper | generic |
| PLT-DA31602 | Brogues | 6 incidental word in a range name | Dress Circle Brogues | dress | dress | generic |
| PLT-DA31700 | Brogues | 7 invented brand holding a color or category word | Yellow Wagtail Brogues | yellow | yellow brogues | generic |
| PLT-DA31701 | Brogues | 7 invented brand holding a color or category word | Black Lapwing Brogues | black | black brogues | generic |
| PLT-DA31702 | Brogues | 7 invented brand holding a color or category word | Red Plover Brogues | red | red brogues | generic |
| PLT-DA32100 | Chelsea Boots | 1 color names a part | Chelsea Boots with Black Sole | black | black chelsea boots | generic |
| PLT-DA32101 | Chelsea Boots | 1 color names a part | Chelsea Boots with Yellow Sole | yellow | yellow chelsea boots | generic |
| PLT-DA32102 | Chelsea Boots | 1 color names a part | Chelsea Boots with Red Sole | red | red chelsea boots | generic |
| PLT-DA32200 | Chelsea Boots | 2 another category's noun as a modifier | Black Loafer Boots | loafer | loafer | generic |
| PLT-DA32201 | Chelsea Boots | 2 another category's noun as a modifier | Grey Sneaker Boots | sneaker | sneaker | generic |
| PLT-DA32202 | Chelsea Boots | 2 another category's noun as a modifier | Black Slipper Boots | slipper | slipper | generic |
| PLT-DA32300 | Chelsea Boots | 3 audience word of a sibling version | Black Womens-Style Chelsea Boots | womens | womens chelsea boots | generic |
| PLT-DA32301 | Chelsea Boots | 3 audience word of a sibling version | Brown Boys Fit Chelsea Boots | boys | boys chelsea boots | generic |
| PLT-DA32302 | Chelsea Boots | 3 audience word of a sibling version | Red Girls Fit Chelsea Boots | girls | girls chelsea boots | generic |
| PLT-DA32400 | Chelsea Boots | 4 material or feature named but absent | Cream Leather-Look Chelsea Boots | leather | leather chelsea boots | special: material claim |
| PLT-DA32401 | Chelsea Boots | 4 material or feature named but absent | Red Suede-Look Chelsea Boots | suede | suede chelsea boots | special: material claim |
| PLT-DA32402 | Chelsea Boots | 4 material or feature named but absent | Red Cashmere-Feel Chelsea Boots | cashmere | cashmere chelsea boots | special: material claim |
| PLT-DA32500 | Chelsea Boots | 5 shade spelled in the description only | Moonbeam Chelsea Boots | ivory | ivory chelsea boots | generic |
| PLT-DA32501 | Chelsea Boots | 5 shade spelled in the description only | Driftwood Chelsea Boots | taupe | taupe chelsea boots | generic |
| PLT-DA32502 | Chelsea Boots | 5 shade spelled in the description only | Dune Chelsea Boots | beige | beige chelsea boots | generic |
| PLT-DA32600 | Chelsea Boots | 6 incidental word in a range name | Cardigan Bay Chelsea Boots | cardigan | cardigan | generic |
| PLT-DA32601 | Chelsea Boots | 6 incidental word in a range name | Pump Lane Chelsea Boots | pump | pump | generic |
| PLT-DA32602 | Chelsea Boots | 6 incidental word in a range name | Shirt Row Chelsea Boots | shirt | shirt | generic |
| PLT-DA32700 | Chelsea Boots | 7 invented brand holding a color or category word | Black Lapwing Chelsea Boots | black | black chelsea boots | generic |
| PLT-DA32701 | Chelsea Boots | 7 invented brand holding a color or category word | Black Lapwing Chelsea Boots | black | black chelsea boots | generic |
| PLT-DA32702 | Chelsea Boots | 7 invented brand holding a color or category word | Yellow Wagtail Chelsea Boots | yellow | yellow chelsea boots | generic |
| PLT-DA33100 | Chukka Boots | 1 color names a part | Chukka Boots with White Sole | white | white chukka boots | generic |
| PLT-DA33101 | Chukka Boots | 1 color names a part | Chukka Boots with Yellow Sole | yellow | yellow chukka boots | generic |
| PLT-DA33102 | Chukka Boots | 1 color names a part | Chukka Boots with Red Sole | red | red chukka boots | generic |
| PLT-DA33200 | Chukka Boots | 2 another category's noun as a modifier | Brown Loafer Boots | loafer | loafer | generic |
| PLT-DA33201 | Chukka Boots | 2 another category's noun as a modifier | Cream Loafer Boots | loafer | loafer | generic |
| PLT-DA33202 | Chukka Boots | 2 another category's noun as a modifier | Blue Sneaker Boots | sneaker | sneaker | generic |
| PLT-DA33300 | Chukka Boots | 3 audience word of a sibling version | Black Girls Fit Chukka Boots | girls | girls chukka boots | generic |
| PLT-DA33301 | Chukka Boots | 3 audience word of a sibling version | White Girls Fit Chukka Boots | girls | girls chukka boots | generic |
| PLT-DA33302 | Chukka Boots | 3 audience word of a sibling version | Blue Girls Fit Chukka Boots | girls | girls chukka boots | generic |
| PLT-DA33400 | Chukka Boots | 4 material or feature named but absent | Black Leather-Look Chukka Boots | leather | leather chukka boots | special: material claim |
| PLT-DA33401 | Chukka Boots | 4 material or feature named but absent | Red Cashmere-Feel Chukka Boots | cashmere | cashmere chukka boots | special: material claim |
| PLT-DA33402 | Chukka Boots | 4 material or feature named but absent | Blue Wool-Free Chukka Boots | wool | wool chukka boots | special: material claim |
| PLT-DA33500 | Chukka Boots | 5 shade spelled in the description only | Moonbeam Chukka Boots | ivory | ivory chukka boots | generic |
| PLT-DA33501 | Chukka Boots | 5 shade spelled in the description only | Driftwood Chukka Boots | taupe | taupe chukka boots | generic |
| PLT-DA33502 | Chukka Boots | 5 shade spelled in the description only | Dune Chukka Boots | beige | beige chukka boots | generic |
| PLT-DA33600 | Chukka Boots | 6 incidental word in a range name | Jumper Lane Chukka Boots | jumper | jumper | generic |
| PLT-DA33601 | Chukka Boots | 6 incidental word in a range name | Skirt Point Chukka Boots | skirt | skirt | generic |
| PLT-DA33602 | Chukka Boots | 6 incidental word in a range name | Sandal Wood Chukka Boots | sandal | sandal | generic |
| PLT-DA33700 | Chukka Boots | 7 invented brand holding a color or category word | White Dormouse Chukka Boots | white | white chukka boots | generic |
| PLT-DA33701 | Chukka Boots | 7 invented brand holding a color or category word | Green Stoat Chukka Boots | green | green chukka boots | generic |
| PLT-DA33702 | Chukka Boots | 7 invented brand holding a color or category word | Jumper Jay Chukka Boots | jumper | jumper chukka boots | generic |
| PLT-DA34100 | Court Shoes | 1 color names a part | Court Shoes with Blue Sole | blue | blue court shoes | generic |
| PLT-DA34101 | Court Shoes | 1 color names a part | Court Shoes with Red Sole | red | red court shoes | generic |
| PLT-DA34102 | Court Shoes | 1 color names a part | Court Shoes with Green Sole | green | green court shoes | generic |
| PLT-DA34200 | Court Shoes | 2 another category's noun as a modifier | Navy Dress Shoes | dress | dress | generic |
| PLT-DA34201 | Court Shoes | 2 another category's noun as a modifier | Cream Dress Shoes | dress | dress | generic |
| PLT-DA34202 | Court Shoes | 2 another category's noun as a modifier | Black Dress Shoes | dress | dress | generic |
| PLT-DA34300 | Court Shoes | 3 audience word of a sibling version | Black Boys Fit Court Shoes | boys | boys court shoes | generic |
| PLT-DA34301 | Court Shoes | 3 audience word of a sibling version | Pink Mens Fit Court Shoes | mens | mens court shoes | generic |
| PLT-DA34302 | Court Shoes | 3 audience word of a sibling version | Brown Boys Fit Court Shoes | boys | boys court shoes | generic |
| PLT-DA34400 | Court Shoes | 4 material or feature named but absent | Blue Cashmere-Feel Court Shoes | cashmere | cashmere court shoes | special: material claim |
| PLT-DA34401 | Court Shoes | 4 material or feature named but absent | Brown Wool-Free Court Shoes | wool | wool court shoes | special: material claim |
| PLT-DA34402 | Court Shoes | 4 material or feature named but absent | Red Leather-Look Court Shoes | leather | leather court shoes | special: material claim |
| PLT-DA34500 | Court Shoes | 5 shade spelled in the description only | Moonbeam Court Shoes | ivory | ivory court shoes | generic |
| PLT-DA34501 | Court Shoes | 5 shade spelled in the description only | Driftwood Court Shoes | taupe | taupe court shoes | generic |
| PLT-DA34502 | Court Shoes | 5 shade spelled in the description only | Dune Court Shoes | beige | beige court shoes | generic |
| PLT-DA34600 | Court Shoes | 6 incidental word in a range name | Coat Hook Court Shoes | coat | coat | generic |
| PLT-DA34601 | Court Shoes | 6 incidental word in a range name | Sock Hop Court Shoes | sock | sock | generic |
| PLT-DA34602 | Court Shoes | 6 incidental word in a range name | Pump Lane Court Shoes | pump | pump | generic |
| PLT-DA34700 | Court Shoes | 7 invented brand holding a color or category word | Yellow Wagtail Court Shoes | yellow | yellow court shoes | generic |
| PLT-DA34701 | Court Shoes | 7 invented brand holding a color or category word | Blue Otter Court Shoes | blue | blue court shoes | generic |
| PLT-DA34702 | Court Shoes | 7 invented brand holding a color or category word | Jumper Jay Court Shoes | jumper | jumper court shoes | generic |
| PLT-DA35100 | Kitten Heels | 1 color names a part | Kitten Heels with Red Sole | red | red kitten heels | generic |
| PLT-DA35101 | Kitten Heels | 1 color names a part | Kitten Heels with Green Sole | green | green kitten heels | generic |
| PLT-DA35102 | Kitten Heels | 1 color names a part | Kitten Heels with White Sole | white | white kitten heels | generic |
| PLT-DA35200 | Kitten Heels | 2 another category's noun as a modifier | Green Sandal Heels | sandal | sandal | generic |
| PLT-DA35201 | Kitten Heels | 2 another category's noun as a modifier | Brown Sandal Heels | sandal | sandal | generic |
| PLT-DA35202 | Kitten Heels | 2 another category's noun as a modifier | Grey Loafer Heels | loafer | loafer | generic |
| PLT-DA35300 | Kitten Heels | 3 audience word of a sibling version | Brown Mens-Style Kitten Heels | mens | mens kitten heels | generic |
| PLT-DA35301 | Kitten Heels | 3 audience word of a sibling version | Navy Mens Fit Kitten Heels | mens | mens kitten heels | generic |
| PLT-DA35302 | Kitten Heels | 3 audience word of a sibling version | Cream Boys Fit Kitten Heels | boys | boys kitten heels | generic |
| PLT-DA35400 | Kitten Heels | 4 material or feature named but absent | Red Suede-Look Kitten Heels | suede | suede kitten heels | special: material claim |
| PLT-DA35401 | Kitten Heels | 4 material or feature named but absent | Green Cashmere-Feel Kitten Heels | cashmere | cashmere kitten heels | special: material claim |
| PLT-DA35402 | Kitten Heels | 4 material or feature named but absent | Grey Wool-Free Kitten Heels | wool | wool kitten heels | special: material claim |
| PLT-DA35500 | Kitten Heels | 5 shade spelled in the description only | Moonbeam Kitten Heels | ivory | ivory kitten heels | generic |
| PLT-DA35501 | Kitten Heels | 5 shade spelled in the description only | Driftwood Kitten Heels | taupe | taupe kitten heels | generic |
| PLT-DA35502 | Kitten Heels | 5 shade spelled in the description only | Dune Kitten Heels | beige | beige kitten heels | generic |
| PLT-DA35600 | Kitten Heels | 6 incidental word in a range name | Jumper Lane Kitten Heels | jumper | jumper | generic |
| PLT-DA35601 | Kitten Heels | 6 incidental word in a range name | Boot Hill Kitten Heels | boot | boot | generic |
| PLT-DA35602 | Kitten Heels | 6 incidental word in a range name | Pump Lane Kitten Heels | pump | pump | generic |
| PLT-DA35700 | Kitten Heels | 7 invented brand holding a color or category word | Jumper Jay Kitten Heels | jumper | jumper kitten heels | generic |
| PLT-DA35701 | Kitten Heels | 7 invented brand holding a color or category word | Yellow Wagtail Kitten Heels | yellow | yellow kitten heels | generic |
| PLT-DA35702 | Kitten Heels | 7 invented brand holding a color or category word | Red Plover Kitten Heels | red | red kitten heels | generic |
| PLT-DA36100 | Knee High Boots | 1 color names a part | Knee High Boots with Green Sole | green | green knee high boots | generic |
| PLT-DA36101 | Knee High Boots | 1 color names a part | Knee High Boots with Blue Sole | blue | blue knee high boots | generic |
| PLT-DA36102 | Knee High Boots | 1 color names a part | Knee High Boots with Black Sole | black | black knee high boots | generic |
| PLT-DA36200 | Knee High Boots | 2 another category's noun as a modifier | Red Sock Boots | sock | sock | generic |
| PLT-DA36201 | Knee High Boots | 2 another category's noun as a modifier | Black Sneaker Boots | sneaker | sneaker | generic |
| PLT-DA36202 | Knee High Boots | 2 another category's noun as a modifier | White Sneaker Boots | sneaker | sneaker | generic |
| PLT-DA36300 | Knee High Boots | 3 audience word of a sibling version | Blue Boys Fit Knee High Boots | boys | boys knee high boots | generic |
| PLT-DA36301 | Knee High Boots | 3 audience word of a sibling version | Blue Mens Fit Knee High Boots | mens | mens knee high boots | generic |
| PLT-DA36302 | Knee High Boots | 3 audience word of a sibling version | White Boys Fit Knee High Boots | boys | boys knee high boots | generic |
| PLT-DA36400 | Knee High Boots | 4 material or feature named but absent | Pink Suede-Look Knee High Boots | suede | suede knee high boots | special: material claim |
| PLT-DA36401 | Knee High Boots | 4 material or feature named but absent | Red Cashmere-Feel Knee High Boots | cashmere | cashmere knee high boots | special: material claim |
| PLT-DA36402 | Knee High Boots | 4 material or feature named but absent | White Wool-Free Knee High Boots | wool | wool knee high boots | special: material claim |
| PLT-DA36500 | Knee High Boots | 5 shade spelled in the description only | Moonbeam Knee High Boots | ivory | ivory knee high boots | generic |
| PLT-DA36501 | Knee High Boots | 5 shade spelled in the description only | Driftwood Knee High Boots | taupe | taupe knee high boots | generic |
| PLT-DA36502 | Knee High Boots | 5 shade spelled in the description only | Dune Knee High Boots | beige | beige knee high boots | generic |
| PLT-DA36600 | Knee High Boots | 6 incidental word in a range name | Skirt Point Knee High Boots | skirt | skirt | generic |
| PLT-DA36601 | Knee High Boots | 6 incidental word in a range name | Dress Circle Knee High Boots | dress | dress | generic |
| PLT-DA36602 | Knee High Boots | 6 incidental word in a range name | Slip Road Knee High Boots | slip | slip | generic |
| PLT-DA36700 | Knee High Boots | 7 invented brand holding a color or category word | White Dormouse Knee High Boots | white | white knee high boots | generic |
| PLT-DA36701 | Knee High Boots | 7 invented brand holding a color or category word | Coat Crake Knee High Boots | coat | coat knee high boots | generic |
| PLT-DA36702 | Knee High Boots | 7 invented brand holding a color or category word | Red Plover Knee High Boots | red | red knee high boots | generic |
| PLT-DA37100 | Loafers | 1 color names a part | Loafers with Green Sole | green | green loafers | generic |
| PLT-DA37101 | Loafers | 1 color names a part | Loafers with White Sole | white | white loafers | generic |
| PLT-DA37102 | Loafers | 1 color names a part | Loafers with Blue Sole | blue | blue loafers | generic |
| PLT-DA37200 | Loafers | 2 another category's noun as a modifier | Pink Brogue Loafers | brogue | brogue | generic |
| PLT-DA37201 | Loafers | 2 another category's noun as a modifier | Blue Brogue Loafers | brogue | brogue | generic |
| PLT-DA37202 | Loafers | 2 another category's noun as a modifier | Blue Brogue Loafers | brogue | brogue | generic |
| PLT-DA37300 | Loafers | 3 audience word of a sibling version | Navy Mens Fit Loafers | mens | mens loafers | generic |
| PLT-DA37301 | Loafers | 3 audience word of a sibling version | Black Mens-Style Loafers | mens | mens loafers | generic |
| PLT-DA37302 | Loafers | 3 audience word of a sibling version | Brown Girls Fit Loafers | girls | girls loafers | generic |
| PLT-DA37400 | Loafers | 4 material or feature named but absent | Brown Suede-Look Loafers | suede | suede loafers | special: material claim |
| PLT-DA37401 | Loafers | 4 material or feature named but absent | Brown Cashmere-Feel Loafers | cashmere | cashmere loafers | special: material claim |
| PLT-DA37402 | Loafers | 4 material or feature named but absent | Black Leather-Look Loafers | leather | leather loafers | special: material claim |
| PLT-DA37500 | Loafers | 5 shade spelled in the description only | Moonbeam Loafers | ivory | ivory loafers | generic |
| PLT-DA37501 | Loafers | 5 shade spelled in the description only | Driftwood Loafers | taupe | taupe loafers | generic |
| PLT-DA37502 | Loafers | 5 shade spelled in the description only | Dune Loafers | beige | beige loafers | generic |
| PLT-DA37600 | Loafers | 6 incidental word in a range name | Boot Hill Loafers | boot | boot | generic |
| PLT-DA37601 | Loafers | 6 incidental word in a range name | Boot Hill Loafers | boot | boot | generic |
| PLT-DA37602 | Loafers | 6 incidental word in a range name | Shirt Row Loafers | shirt | shirt | generic |
| PLT-DA37700 | Loafers | 7 invented brand holding a color or category word | Black Lapwing Loafers | black | black loafers | generic |
| PLT-DA37701 | Loafers | 7 invented brand holding a color or category word | Yellow Wagtail Loafers | yellow | yellow loafers | generic |
| PLT-DA37702 | Loafers | 7 invented brand holding a color or category word | Jumper Jay Loafers | jumper | jumper loafers | generic |
| PLT-DA38100 | Running Shoes | 1 color names a part | Running Shoes with White Sole | white | white running shoes | generic |
| PLT-DA38101 | Running Shoes | 1 color names a part | Running Shoes with Red Sole | red | red running shoes | generic |
| PLT-DA38102 | Running Shoes | 1 color names a part | Running Shoes with Green Sole | green | green running shoes | generic |
| PLT-DA38200 | Running Shoes | 2 another category's noun as a modifier | Pink Walking Shoes | walking | walking | generic |
| PLT-DA38201 | Running Shoes | 2 another category's noun as a modifier | Black Tennis Shoes | tennis | tennis | generic |
| PLT-DA38202 | Running Shoes | 2 another category's noun as a modifier | Navy Tennis Shoes | tennis | tennis | generic |
| PLT-DA38300 | Running Shoes | 3 audience word of a sibling version | Cream Mini-Me Mens Running Shoes | mens | mens running shoes | generic |
| PLT-DA38301 | Running Shoes | 3 audience word of a sibling version | Black Girls Fit Running Shoes | girls | girls running shoes | generic |
| PLT-DA38302 | Running Shoes | 3 audience word of a sibling version | Grey Mens Fit Running Shoes | mens | mens running shoes | generic |
| PLT-DA38400 | Running Shoes | 4 material or feature named but absent | Red Leather-Look Running Shoes | leather | leather running shoes | special: material claim |
| PLT-DA38401 | Running Shoes | 4 material or feature named but absent | Green Suede-Look Running Shoes | suede | suede running shoes | special: material claim |
| PLT-DA38402 | Running Shoes | 4 material or feature named but absent | White Cashmere-Feel Running Shoes | cashmere | cashmere running shoes | special: material claim |
| PLT-DA38500 | Running Shoes | 5 shade spelled in the description only | Moonbeam Running Shoes | ivory | ivory running shoes | generic |
| PLT-DA38501 | Running Shoes | 5 shade spelled in the description only | Driftwood Running Shoes | taupe | taupe running shoes | generic |
| PLT-DA38502 | Running Shoes | 5 shade spelled in the description only | Dune Running Shoes | beige | beige running shoes | generic |
| PLT-DA38600 | Running Shoes | 6 incidental word in a range name | Blazer Court Running Shoes | blazer | blazer | generic |
| PLT-DA38601 | Running Shoes | 6 incidental word in a range name | Cardigan Bay Running Shoes | cardigan | cardigan | generic |
| PLT-DA38602 | Running Shoes | 6 incidental word in a range name | Jumper Lane Running Shoes | jumper | jumper | generic |
| PLT-DA38700 | Running Shoes | 7 invented brand holding a color or category word | Red Plover Running Shoes | red | red running shoes | generic |
| PLT-DA38701 | Running Shoes | 7 invented brand holding a color or category word | Coat Crake Running Shoes | coat | coat running shoes | generic |
| PLT-DA38702 | Running Shoes | 7 invented brand holding a color or category word | Black Lapwing Running Shoes | black | black running shoes | generic |
| PLT-DA39100 | Safety Boots | 1 color names a part | Safety Boots with Black Sole | black | black safety boots | generic |
| PLT-DA39101 | Safety Boots | 1 color names a part | Safety Boots with Yellow Sole | yellow | yellow safety boots | generic |
| PLT-DA39102 | Safety Boots | 1 color names a part | Safety Boots with Blue Sole | blue | blue safety boots | generic |
| PLT-DA39200 | Safety Boots | 2 another category's noun as a modifier | Brown Wellington Safety Boots | wellington | wellington | generic |
| PLT-DA39201 | Safety Boots | 2 another category's noun as a modifier | Red Hiker Safety Boots | hiker | hiker | generic |
| PLT-DA39202 | Safety Boots | 2 another category's noun as a modifier | Green Wellington Safety Boots | wellington | wellington | generic |
| PLT-DA39300 | Safety Boots | 3 audience word of a sibling version | Cream Womens Fit Safety Boots | womens | womens safety boots | generic |
| PLT-DA39301 | Safety Boots | 3 audience word of a sibling version | White Womens-Style Safety Boots | womens | womens safety boots | generic |
| PLT-DA39302 | Safety Boots | 3 audience word of a sibling version | Blue Womens-Style Safety Boots | womens | womens safety boots | generic |
| PLT-DA39400 | Safety Boots | 4 material or feature named but absent | Grey Suede-Look Safety Boots | suede | suede safety boots | special: material claim |
| PLT-DA39401 | Safety Boots | 4 material or feature named but absent | Pink Cashmere-Feel Safety Boots | cashmere | cashmere safety boots | special: material claim |
| PLT-DA39402 | Safety Boots | 4 material or feature named but absent | Cream Wool-Free Safety Boots | wool | wool safety boots | special: material claim |
| PLT-DA39500 | Safety Boots | 5 shade spelled in the description only | Moonbeam Safety Boots | ivory | ivory safety boots | generic |
| PLT-DA39501 | Safety Boots | 5 shade spelled in the description only | Driftwood Safety Boots | taupe | taupe safety boots | generic |
| PLT-DA39502 | Safety Boots | 5 shade spelled in the description only | Dune Safety Boots | beige | beige safety boots | generic |
| PLT-DA39600 | Safety Boots | 6 incidental word in a range name | Dress Circle Safety Boots | dress | dress | generic |
| PLT-DA39601 | Safety Boots | 6 incidental word in a range name | Shirt Row Safety Boots | shirt | shirt | generic |
| PLT-DA39602 | Safety Boots | 6 incidental word in a range name | Cardigan Bay Safety Boots | cardigan | cardigan | generic |
| PLT-DA39700 | Safety Boots | 7 invented brand holding a color or category word | Coat Crake Safety Boots | coat | coat safety boots | generic |
| PLT-DA39701 | Safety Boots | 7 invented brand holding a color or category word | Blue Otter Safety Boots | blue | blue safety boots | generic |
| PLT-DA39702 | Safety Boots | 7 invented brand holding a color or category word | Yellow Wagtail Safety Boots | yellow | yellow safety boots | generic |
| PLT-DA40100 | Sandals | 1 color names a part | Sandals with Green Sole | green | green sandals | generic |
| PLT-DA40101 | Sandals | 1 color names a part | Sandals with Black Sole | black | black sandals | generic |
| PLT-DA40102 | Sandals | 1 color names a part | Sandals with Blue Sole | blue | blue sandals | generic |
| PLT-DA40200 | Sandals | 2 another category's noun as a modifier | Blue Mule Sandals | mule | mule | generic |
| PLT-DA40201 | Sandals | 2 another category's noun as a modifier | Pink Mule Sandals | mule | mule | generic |
| PLT-DA40202 | Sandals | 2 another category's noun as a modifier | Green Espadrille Sandals | espadrille | espadrille | generic |
| PLT-DA40300 | Sandals | 3 audience word of a sibling version | Green Mens-Style Sandals | mens | mens sandals | generic |
| PLT-DA40301 | Sandals | 3 audience word of a sibling version | Red Mens-Style Sandals | mens | mens sandals | generic |
| PLT-DA40302 | Sandals | 3 audience word of a sibling version | Cream Mini-Me Mens Sandals | mens | mens sandals | generic |
| PLT-DA40400 | Sandals | 4 material or feature named but absent | Red Leather-Look Sandals | leather | leather sandals | special: material claim |
| PLT-DA40401 | Sandals | 4 material or feature named but absent | Brown Suede-Look Sandals | suede | suede sandals | special: material claim |
| PLT-DA40402 | Sandals | 4 material or feature named but absent | Green Cashmere-Feel Sandals | cashmere | cashmere sandals | special: material claim |
| PLT-DA40500 | Sandals | 5 shade spelled in the description only | Moonbeam Sandals | ivory | ivory sandals | generic |
| PLT-DA40501 | Sandals | 5 shade spelled in the description only | Driftwood Sandals | taupe | taupe sandals | generic |
| PLT-DA40502 | Sandals | 5 shade spelled in the description only | Dune Sandals | beige | beige sandals | generic |
| PLT-DA40600 | Sandals | 6 incidental word in a range name | Skirt Point Sandals | skirt | skirt | generic |
| PLT-DA40601 | Sandals | 6 incidental word in a range name | Jumper Lane Sandals | jumper | jumper | generic |
| PLT-DA40602 | Sandals | 6 incidental word in a range name | Pump Lane Sandals | pump | pump | generic |
| PLT-DA40700 | Sandals | 7 invented brand holding a color or category word | Yellow Wagtail Sandals | yellow | yellow sandals | generic |
| PLT-DA40701 | Sandals | 7 invented brand holding a color or category word | White Dormouse Sandals | white | white sandals | generic |
| PLT-DA40702 | Sandals | 7 invented brand holding a color or category word | White Dormouse Sandals | white | white sandals | generic |
| PLT-DA41100 | School Shoes | 1 color names a part | School Shoes with Blue Sole | blue | blue school shoes | generic |
| PLT-DA41101 | School Shoes | 1 color names a part | School Shoes with Green Sole | green | green school shoes | generic |
| PLT-DA41102 | School Shoes | 1 color names a part | School Shoes with Yellow Sole | yellow | yellow school shoes | generic |
| PLT-DA41200 | School Shoes | 2 another category's noun as a modifier | Brown Brogue School Shoes | brogue | brogue | generic |
| PLT-DA41201 | School Shoes | 2 another category's noun as a modifier | Grey Brogue School Shoes | brogue | brogue | generic |
| PLT-DA41202 | School Shoes | 2 another category's noun as a modifier | Red Loafer School Shoes | loafer | loafer | generic |
| PLT-DA41300 | School Shoes | 3 audience word of a sibling version | Red Mens-Style School Shoes | mens | mens school shoes | generic |
| PLT-DA41301 | School Shoes | 3 audience word of a sibling version | Cream Mens-Style School Shoes | mens | mens school shoes | generic |
| PLT-DA41302 | School Shoes | 3 audience word of a sibling version | Pink Mini-Me Mens School Shoes | mens | mens school shoes | generic |
| PLT-DA41400 | School Shoes | 4 material or feature named but absent | Pink Suede-Look School Shoes | suede | suede school shoes | special: material claim |
| PLT-DA41401 | School Shoes | 4 material or feature named but absent | Black Cashmere-Feel School Shoes | cashmere | cashmere school shoes | special: material claim |
| PLT-DA41402 | School Shoes | 4 material or feature named but absent | Pink Wool-Free School Shoes | wool | wool school shoes | special: material claim |
| PLT-DA41500 | School Shoes | 5 shade spelled in the description only | Moonbeam School Shoes | ivory | ivory school shoes | generic |
| PLT-DA41501 | School Shoes | 5 shade spelled in the description only | Driftwood School Shoes | taupe | taupe school shoes | generic |
| PLT-DA41502 | School Shoes | 5 shade spelled in the description only | Dune School Shoes | beige | beige school shoes | generic |
| PLT-DA41600 | School Shoes | 6 incidental word in a range name | Pump Lane School Shoes | pump | pump | generic |
| PLT-DA41601 | School Shoes | 6 incidental word in a range name | Slip Road School Shoes | slip | slip | generic |
| PLT-DA41602 | School Shoes | 6 incidental word in a range name | Cardigan Bay School Shoes | cardigan | cardigan | generic |
| PLT-DA41700 | School Shoes | 7 invented brand holding a color or category word | Jumper Jay School Shoes | jumper | jumper school shoes | generic |
| PLT-DA41701 | School Shoes | 7 invented brand holding a color or category word | Red Plover School Shoes | red | red school shoes | generic |
| PLT-DA41702 | School Shoes | 7 invented brand holding a color or category word | White Dormouse School Shoes | white | white school shoes | generic |
| PLT-DA42100 | Slippers | 1 color names a part | Slippers with White Sole | white | white slippers | generic |
| PLT-DA42101 | Slippers | 1 color names a part | Slippers with Blue Sole | blue | blue slippers | generic |
| PLT-DA42102 | Slippers | 1 color names a part | Slippers with Green Sole | green | green slippers | generic |
| PLT-DA42200 | Slippers | 2 another category's noun as a modifier | Red Mule Slippers | mule | mule | generic |
| PLT-DA42201 | Slippers | 2 another category's noun as a modifier | Red Mule Slippers | mule | mule | generic |
| PLT-DA42202 | Slippers | 2 another category's noun as a modifier | Brown Sock Slippers | sock | sock | generic |
| PLT-DA42300 | Slippers | 3 audience word of a sibling version | Grey Womens Fit Slippers | womens | womens slippers | generic |
| PLT-DA42301 | Slippers | 3 audience word of a sibling version | Navy Mens Fit Slippers | mens | mens slippers | generic |
| PLT-DA42302 | Slippers | 3 audience word of a sibling version | Green Boys Fit Slippers | boys | boys slippers | generic |
| PLT-DA42400 | Slippers | 4 material or feature named but absent | Black Leather-Look Slippers | leather | leather slippers | special: material claim |
| PLT-DA42401 | Slippers | 4 material or feature named but absent | Pink Cashmere-Feel Slippers | cashmere | cashmere slippers | special: material claim |
| PLT-DA42402 | Slippers | 4 material or feature named but absent | Pink Wool-Free Slippers | wool | wool slippers | special: material claim |
| PLT-DA42500 | Slippers | 5 shade spelled in the description only | Moonbeam Slippers | ivory | ivory slippers | generic |
| PLT-DA42501 | Slippers | 5 shade spelled in the description only | Driftwood Slippers | taupe | taupe slippers | generic |
| PLT-DA42502 | Slippers | 5 shade spelled in the description only | Dune Slippers | beige | beige slippers | generic |
| PLT-DA42600 | Slippers | 6 incidental word in a range name | Dress Circle Slippers | dress | dress | generic |
| PLT-DA42601 | Slippers | 6 incidental word in a range name | Jumper Lane Slippers | jumper | jumper | generic |
| PLT-DA42602 | Slippers | 6 incidental word in a range name | Sandal Wood Slippers | sandal | sandal | generic |
| PLT-DA42700 | Slippers | 7 invented brand holding a color or category word | Blue Otter Slippers | blue | blue slippers | generic |
| PLT-DA42701 | Slippers | 7 invented brand holding a color or category word | White Dormouse Slippers | white | white slippers | generic |
| PLT-DA42702 | Slippers | 7 invented brand holding a color or category word | Yellow Wagtail Slippers | yellow | yellow slippers | generic |
| PLT-DA43100 | Trainers | 1 color names a part | Trainers with Yellow Sole | yellow | yellow trainers | generic |
| PLT-DA43101 | Trainers | 1 color names a part | Trainers with White Sole | white | white trainers | generic |
| PLT-DA43102 | Trainers | 1 color names a part | Trainers with Black Sole | black | black trainers | generic |
| PLT-DA43200 | Trainers | 2 another category's noun as a modifier | Black Running Trainers | running | running | generic |
| PLT-DA43201 | Trainers | 2 another category's noun as a modifier | Green Running Trainers | running | running | generic |
| PLT-DA43202 | Trainers | 2 another category's noun as a modifier | Brown Walking Trainers | walking | walking | generic |
| PLT-DA43300 | Trainers | 3 audience word of a sibling version | Green Womens Fit Trainers | womens | womens trainers | generic |
| PLT-DA43301 | Trainers | 3 audience word of a sibling version | Grey Girls Fit Trainers | girls | girls trainers | generic |
| PLT-DA43302 | Trainers | 3 audience word of a sibling version | Brown Womens Fit Trainers | womens | womens trainers | generic |
| PLT-DA43400 | Trainers | 4 material or feature named but absent | Cream Leather-Look Trainers | leather | leather trainers | special: material claim |
| PLT-DA43401 | Trainers | 4 material or feature named but absent | Pink Suede-Look Trainers | suede | suede trainers | special: material claim |
| PLT-DA43402 | Trainers | 4 material or feature named but absent | Grey Cashmere-Feel Trainers | cashmere | cashmere trainers | special: material claim |
| PLT-DA43500 | Trainers | 5 shade spelled in the description only | Moonbeam Trainers | ivory | ivory trainers | generic |
| PLT-DA43501 | Trainers | 5 shade spelled in the description only | Driftwood Trainers | taupe | taupe trainers | generic |
| PLT-DA43502 | Trainers | 5 shade spelled in the description only | Dune Trainers | beige | beige trainers | generic |
| PLT-DA43600 | Trainers | 6 incidental word in a range name | Slipper Brook Trainers | slipper | slipper | generic |
| PLT-DA43601 | Trainers | 6 incidental word in a range name | Jumper Lane Trainers | jumper | jumper | generic |
| PLT-DA43602 | Trainers | 6 incidental word in a range name | Pump Lane Trainers | pump | pump | generic |
| PLT-DA43700 | Trainers | 7 invented brand holding a color or category word | Yellow Wagtail Trainers | yellow | yellow trainers | generic |
| PLT-DA43701 | Trainers | 7 invented brand holding a color or category word | White Dormouse Trainers | white | white trainers | generic |
| PLT-DA43702 | Trainers | 7 invented brand holding a color or category word | Yellow Wagtail Trainers | yellow | yellow trainers | generic |
| PLT-DA44100 | Walking Boots | 1 color names a part | Walking Boots with Red Sole | red | red walking boots | generic |
| PLT-DA44101 | Walking Boots | 1 color names a part | Walking Boots with Black Sole | black | black walking boots | generic |
| PLT-DA44102 | Walking Boots | 1 color names a part | Walking Boots with Green Sole | green | green walking boots | generic |
| PLT-DA44200 | Walking Boots | 2 another category's noun as a modifier | Black Chukka Walking Boots | chukka | chukka | generic |
| PLT-DA44201 | Walking Boots | 2 another category's noun as a modifier | Navy Chukka Walking Boots | chukka | chukka | generic |
| PLT-DA44202 | Walking Boots | 2 another category's noun as a modifier | Black Chukka Walking Boots | chukka | chukka | generic |
| PLT-DA44300 | Walking Boots | 3 audience word of a sibling version | Pink Mens-Style Walking Boots | mens | mens walking boots | generic |
| PLT-DA44301 | Walking Boots | 3 audience word of a sibling version | Black Girls Fit Walking Boots | girls | girls walking boots | generic |
| PLT-DA44302 | Walking Boots | 3 audience word of a sibling version | Grey Mens-Style Walking Boots | mens | mens walking boots | generic |
| PLT-DA44400 | Walking Boots | 4 material or feature named but absent | Green Leather-Look Walking Boots | leather | leather walking boots | special: material claim |
| PLT-DA44401 | Walking Boots | 4 material or feature named but absent | White Suede-Look Walking Boots | suede | suede walking boots | special: material claim |
| PLT-DA44402 | Walking Boots | 4 material or feature named but absent | Cream Cashmere-Feel Walking Boots | cashmere | cashmere walking boots | special: material claim |
| PLT-DA44500 | Walking Boots | 5 shade spelled in the description only | Moonbeam Walking Boots | ivory | ivory walking boots | generic |
| PLT-DA44501 | Walking Boots | 5 shade spelled in the description only | Driftwood Walking Boots | taupe | taupe walking boots | generic |
| PLT-DA44502 | Walking Boots | 5 shade spelled in the description only | Dune Walking Boots | beige | beige walking boots | generic |
| PLT-DA44600 | Walking Boots | 6 incidental word in a range name | Cardigan Bay Walking Boots | cardigan | cardigan | generic |
| PLT-DA44601 | Walking Boots | 6 incidental word in a range name | Shirt Row Walking Boots | shirt | shirt | generic |
| PLT-DA44602 | Walking Boots | 6 incidental word in a range name | Slip Road Walking Boots | slip | slip | generic |
| PLT-DA44700 | Walking Boots | 7 invented brand holding a color or category word | Black Lapwing Walking Boots | black | black walking boots | generic |
| PLT-DA44701 | Walking Boots | 7 invented brand holding a color or category word | Jumper Jay Walking Boots | jumper | jumper walking boots | generic |
| PLT-DA44702 | Walking Boots | 7 invented brand holding a color or category word | Jumper Jay Walking Boots | jumper | jumper walking boots | generic |
| PLT-DA45100 | Wellies | 1 color names a part | Wellies with Red Sole | red | red wellies | generic |
| PLT-DA45101 | Wellies | 1 color names a part | Wellies with White Sole | white | white wellies | generic |
| PLT-DA45102 | Wellies | 1 color names a part | Wellies with Red Sole | red | red wellies | generic |
| PLT-DA45200 | Wellies | 2 another category's noun as a modifier | Pink Chelsea Wellies | chelsea | chelsea | generic |
| PLT-DA45201 | Wellies | 2 another category's noun as a modifier | Cream Chelsea Wellies | chelsea | chelsea | generic |
| PLT-DA45202 | Wellies | 2 another category's noun as a modifier | Blue Chelsea Wellies | chelsea | chelsea | generic |
| PLT-DA45300 | Wellies | 3 audience word of a sibling version | Red Mens Fit Wellies | mens | mens wellies | generic |
| PLT-DA45301 | Wellies | 3 audience word of a sibling version | Green Boys Fit Wellies | boys | boys wellies | generic |
| PLT-DA45302 | Wellies | 3 audience word of a sibling version | Black Mini-Me Womens Wellies | womens | womens wellies | generic |
| PLT-DA45400 | Wellies | 4 material or feature named but absent | Red Leather-Look Wellies | leather | leather wellies | special: material claim |
| PLT-DA45401 | Wellies | 4 material or feature named but absent | Green Suede-Look Wellies | suede | suede wellies | special: material claim |
| PLT-DA45402 | Wellies | 4 material or feature named but absent | Navy Cashmere-Feel Wellies | cashmere | cashmere wellies | special: material claim |
| PLT-DA45500 | Wellies | 5 shade spelled in the description only | Moonbeam Wellies | ivory | ivory wellies | generic |
| PLT-DA45501 | Wellies | 5 shade spelled in the description only | Driftwood Wellies | taupe | taupe wellies | generic |
| PLT-DA45502 | Wellies | 5 shade spelled in the description only | Dune Wellies | beige | beige wellies | generic |
| PLT-DA45600 | Wellies | 6 incidental word in a range name | Skirt Point Wellies | skirt | skirt | generic |
| PLT-DA45601 | Wellies | 6 incidental word in a range name | Coat Hook Wellies | coat | coat | generic |
| PLT-DA45602 | Wellies | 6 incidental word in a range name | Dress Circle Wellies | dress | dress | generic |
| PLT-DA45700 | Wellies | 7 invented brand holding a color or category word | Yellow Wagtail Wellies | yellow | yellow wellies | generic |
| PLT-DA45701 | Wellies | 7 invented brand holding a color or category word | White Dormouse Wellies | white | white wellies | generic |
| PLT-DA45702 | Wellies | 7 invented brand holding a color or category word | Jumper Jay Wellies | jumper | jumper wellies | generic |
| PLT-DA46100 | Bra | 1 color names a part | Bra with Blue Straps | blue | blue bra | generic |
| PLT-DA46101 | Bra | 1 color names a part | Bra with Black Bow | black | black bra | generic |
| PLT-DA46102 | Bra | 1 color names a part | Bra with Blue Bow | blue | blue bra | generic |
| PLT-DA46103 | Bra | 1 color names a part | Bra with Red Bow | red | red bra | generic |
| PLT-DA46104 | Bra | 1 color names a part | Bra with Yellow Bow | yellow | yellow bra | generic |
| PLT-DA46105 | Bra | 1 color names a part | Bra with Green Straps | green | green bra | generic |
| PLT-DA46106 | Bra | 1 color names a part | Bra with White Bow | white | white bra | generic |
| PLT-DA46107 | Bra | 1 color names a part | Bra with Black Straps | black | black bra | generic |
| PLT-DA46108 | Bra | 1 color names a part | Bra with Green Bow | green | green bra | generic |
| PLT-DA46200 | Bra | 2 another category's noun as a modifier | Black T-Shirt Bra | t-shirt | t-shirt | generic |
| PLT-DA46201 | Bra | 2 another category's noun as a modifier | Cream Cami Bra | cami | cami | generic |
| PLT-DA46202 | Bra | 2 another category's noun as a modifier | Grey Corset Bra | corset | corset | generic |
| PLT-DA46203 | Bra | 2 another category's noun as a modifier | White Corset Bra | corset | corset | generic |
| PLT-DA46204 | Bra | 2 another category's noun as a modifier | Black Cami Bra | cami | cami | generic |
| PLT-DA46205 | Bra | 2 another category's noun as a modifier | Blue Cami Bra | cami | cami | generic |
| PLT-DA46206 | Bra | 2 another category's noun as a modifier | Brown Cami Bra | cami | cami | generic |
| PLT-DA46207 | Bra | 2 another category's noun as a modifier | Green T-Shirt Bra | t-shirt | t-shirt | generic |
| PLT-DA46208 | Bra | 2 another category's noun as a modifier | Navy Corset Bra | corset | corset | generic |
| PLT-DA46300 | Bra | 3 audience word of a sibling version | Navy Boys Fit Bra | boys | boys bra | generic |
| PLT-DA46301 | Bra | 3 audience word of a sibling version | Pink Mens Fit Bra | mens | mens bra | generic |
| PLT-DA46302 | Bra | 3 audience word of a sibling version | Green Mens Fit Bra | mens | mens bra | generic |
| PLT-DA46303 | Bra | 3 audience word of a sibling version | Brown Mens-Style Bra | mens | mens bra | generic |
| PLT-DA46304 | Bra | 3 audience word of a sibling version | Brown Boys Fit Bra | boys | boys bra | generic |
| PLT-DA46305 | Bra | 3 audience word of a sibling version | Pink Boys Fit Bra | boys | boys bra | generic |
| PLT-DA46306 | Bra | 3 audience word of a sibling version | Cream Mens Fit Bra | mens | mens bra | generic |
| PLT-DA46307 | Bra | 3 audience word of a sibling version | Red Mens-Style Bra | mens | mens bra | generic |
| PLT-DA46308 | Bra | 3 audience word of a sibling version | Brown Mens Fit Bra | mens | mens bra | generic |
| PLT-DA46400 | Bra | 4 material or feature named but absent | Grey Leather-Look Bra | leather | leather bra | special: material claim |
| PLT-DA46401 | Bra | 4 material or feature named but absent | Red Suede-Look Bra | suede | suede bra | special: material claim |
| PLT-DA46402 | Bra | 4 material or feature named but absent | Blue Cashmere-Feel Bra | cashmere | cashmere bra | special: material claim |
| PLT-DA46403 | Bra | 4 material or feature named but absent | White Wool-Free Bra | wool | wool bra | special: material claim |
| PLT-DA46404 | Bra | 4 material or feature named but absent | Red Silk-Free Bra | silk | silk bra | special: material claim |
| PLT-DA46405 | Bra | 4 material or feature named but absent | Green Linen-Look Bra | linen | linen bra | special: material claim |
| PLT-DA46406 | Bra | 4 material or feature named but absent | Green Lace-Free Bra | lace | lace bra | special: material claim |
| PLT-DA46407 | Bra | 4 material or feature named but absent | Brown Velvet-Feel Bra | velvet | velvet bra | special: material claim |
| PLT-DA46408 | Bra | 4 material or feature named but absent | Grey Denim-Look Bra | denim | denim bra | special: material claim |
| PLT-DA46500 | Bra | 5 shade spelled in the description only | Moonbeam Bra | ivory | ivory bra | generic |
| PLT-DA46501 | Bra | 5 shade spelled in the description only | Driftwood Bra | taupe | taupe bra | generic |
| PLT-DA46502 | Bra | 5 shade spelled in the description only | Dune Bra | beige | beige bra | generic |
| PLT-DA46503 | Bra | 5 shade spelled in the description only | Ember Bra | burgundy | burgundy bra | generic |
| PLT-DA46504 | Bra | 5 shade spelled in the description only | Lagoon Bra | teal | teal bra | generic |
| PLT-DA46505 | Bra | 5 shade spelled in the description only | Willow Bra | olive | olive bra | generic |
| PLT-DA46506 | Bra | 5 shade spelled in the description only | Pebble Bra | ecru | ecru bra | generic |
| PLT-DA46507 | Bra | 5 shade spelled in the description only | Meadow Bra | mint | mint bra | generic |
| PLT-DA46508 | Bra | 5 shade spelled in the description only | Harvest Bra | rust | rust bra | generic |
| PLT-DA46600 | Bra | 6 incidental word in a range name | Pump Lane Bra | pump | pump | generic |
| PLT-DA46601 | Bra | 6 incidental word in a range name | Sock Hop Bra | sock | sock | generic |
| PLT-DA46602 | Bra | 6 incidental word in a range name | Coat Hook Bra | coat | coat | generic |
| PLT-DA46603 | Bra | 6 incidental word in a range name | Sandal Wood Bra | sandal | sandal | generic |
| PLT-DA46604 | Bra | 6 incidental word in a range name | Skirt Point Bra | skirt | skirt | generic |
| PLT-DA46605 | Bra | 6 incidental word in a range name | Dress Circle Bra | dress | dress | generic |
| PLT-DA46606 | Bra | 6 incidental word in a range name | Blazer Court Bra | blazer | blazer | generic |
| PLT-DA46607 | Bra | 6 incidental word in a range name | Boot Hill Bra | boot | boot | generic |
| PLT-DA46608 | Bra | 6 incidental word in a range name | Cardigan Bay Bra | cardigan | cardigan | generic |
| PLT-DA46700 | Bra | 7 invented brand holding a color or category word | Blue Otter Bra | blue | blue bra | generic |
| PLT-DA46701 | Bra | 7 invented brand holding a color or category word | White Dormouse Bra | white | white bra | generic |
| PLT-DA46702 | Bra | 7 invented brand holding a color or category word | Coat Crake Bra | coat | coat bra | generic |
| PLT-DA46703 | Bra | 7 invented brand holding a color or category word | Green Stoat Bra | green | green bra | generic |
| PLT-DA46704 | Bra | 7 invented brand holding a color or category word | Red Plover Bra | red | red bra | generic |
| PLT-DA46705 | Bra | 7 invented brand holding a color or category word | Yellow Wagtail Bra | yellow | yellow bra | generic |
| PLT-DA46706 | Bra | 7 invented brand holding a color or category word | Black Lapwing Bra | black | black bra | generic |
| PLT-DA46707 | Bra | 7 invented brand holding a color or category word | Jumper Jay Bra | jumper | jumper bra | generic |
| PLT-DA47100 | Boxers | 1 color names a part | Boxers with Green Waistband | green | green boxers | generic |
| PLT-DA47101 | Boxers | 1 color names a part | Boxers with White Waistband | white | white boxers | generic |
| PLT-DA47102 | Boxers | 1 color names a part | Boxers with Red Waistband | red | red boxers | generic |
| PLT-DA47200 | Boxers | 2 another category's noun as a modifier | Brown Boxer Briefs | brief | brief | generic |
| PLT-DA47201 | Boxers | 2 another category's noun as a modifier | Red Boxer Trunks | trunk | trunk | generic |
| PLT-DA47202 | Boxers | 2 another category's noun as a modifier | Cream Boxer Shorts | short | short | generic |
| PLT-DA47300 | Boxers | 3 audience word of a sibling version | Grey Womens Fit Boxers | womens | womens boxers | generic |
| PLT-DA47301 | Boxers | 3 audience word of a sibling version | Grey Womens-Style Boxers | womens | womens boxers | generic |
| PLT-DA47302 | Boxers | 3 audience word of a sibling version | Red Girls Fit Boxers | girls | girls boxers | generic |
| PLT-DA47400 | Boxers | 4 material or feature named but absent | Navy Leather-Look Boxers | leather | leather boxers | special: material claim |
| PLT-DA47401 | Boxers | 4 material or feature named but absent | Cream Suede-Look Boxers | suede | suede boxers | special: material claim |
| PLT-DA47402 | Boxers | 4 material or feature named but absent | Cream Cashmere-Feel Boxers | cashmere | cashmere boxers | special: material claim |
| PLT-DA47500 | Boxers | 5 shade spelled in the description only | Moonbeam Boxers | ivory | ivory boxers | generic |
| PLT-DA47501 | Boxers | 5 shade spelled in the description only | Driftwood Boxers | taupe | taupe boxers | generic |
| PLT-DA47502 | Boxers | 5 shade spelled in the description only | Dune Boxers | beige | beige boxers | generic |
| PLT-DA47600 | Boxers | 6 incidental word in a range name | Shirt Row Boxers | shirt | shirt | generic |
| PLT-DA47601 | Boxers | 6 incidental word in a range name | Slip Road Boxers | slip | slip | generic |
| PLT-DA47602 | Boxers | 6 incidental word in a range name | Dress Circle Boxers | dress | dress | generic |
| PLT-DA47700 | Boxers | 7 invented brand holding a color or category word | Coat Crake Boxers | coat | coat boxers | generic |
| PLT-DA47701 | Boxers | 7 invented brand holding a color or category word | Blue Otter Boxers | blue | blue boxers | generic |
| PLT-DA47702 | Boxers | 7 invented brand holding a color or category word | Black Lapwing Boxers | black | black boxers | generic |
| PLT-DA48100 | Dressing Gown | 1 color names a part | Dressing Gown with Red Hem | red | red dressing gown | generic |
| PLT-DA48101 | Dressing Gown | 1 color names a part | Dressing Gown with Yellow Hem | yellow | yellow dressing gown | generic |
| PLT-DA48102 | Dressing Gown | 1 color names a part | Dressing Gown with Black Hem | black | black dressing gown | generic |
| PLT-DA48200 | Dressing Gown | 2 another category's noun as a modifier | Cream Kimono Dressing Gown | kimono | kimono | generic |
| PLT-DA48201 | Dressing Gown | 2 another category's noun as a modifier | Navy Kimono Dressing Gown | kimono | kimono | generic |
| PLT-DA48202 | Dressing Gown | 2 another category's noun as a modifier | Navy Kimono Dressing Gown | kimono | kimono | generic |
| PLT-DA48300 | Dressing Gown | 3 audience word of a sibling version | Cream Boys Fit Dressing Gown | boys | boys dressing gown | generic |
| PLT-DA48301 | Dressing Gown | 3 audience word of a sibling version | Brown Mens Fit Dressing Gown | mens | mens dressing gown | generic |
| PLT-DA48302 | Dressing Gown | 3 audience word of a sibling version | Pink Mini-Me Womens Dressing Gown | womens | womens dressing gown | generic |
| PLT-DA48400 | Dressing Gown | 4 material or feature named but absent | Cream Leather-Look Dressing Gown | leather | leather dressing gown | special: material claim |
| PLT-DA48401 | Dressing Gown | 4 material or feature named but absent | Pink Suede-Look Dressing Gown | suede | suede dressing gown | special: material claim |
| PLT-DA48402 | Dressing Gown | 4 material or feature named but absent | Grey Cashmere-Feel Dressing Gown | cashmere | cashmere dressing gown | special: material claim |
| PLT-DA48500 | Dressing Gown | 5 shade spelled in the description only | Moonbeam Dressing Gown | ivory | ivory dressing gown | generic |
| PLT-DA48501 | Dressing Gown | 5 shade spelled in the description only | Driftwood Dressing Gown | taupe | taupe dressing gown | generic |
| PLT-DA48502 | Dressing Gown | 5 shade spelled in the description only | Dune Dressing Gown | beige | beige dressing gown | generic |
| PLT-DA48600 | Dressing Gown | 6 incidental word in a range name | Slip Road Dressing Gown | slip | slip | generic |
| PLT-DA48601 | Dressing Gown | 6 incidental word in a range name | Coat Hook Dressing Gown | coat | coat | generic |
| PLT-DA48602 | Dressing Gown | 6 incidental word in a range name | Jumper Lane Dressing Gown | jumper | jumper | generic |
| PLT-DA48700 | Dressing Gown | 7 invented brand holding a color or category word | Black Lapwing Dressing Gown | black | black dressing gown | generic |
| PLT-DA48701 | Dressing Gown | 7 invented brand holding a color or category word | Green Stoat Dressing Gown | green | green dressing gown | generic |
| PLT-DA48702 | Dressing Gown | 7 invented brand holding a color or category word | Coat Crake Dressing Gown | coat | coat dressing gown | generic |
| PLT-DA49100 | Knickers | 1 color names a part | Knickers with Yellow Waistband | yellow | yellow knickers | generic |
| PLT-DA49101 | Knickers | 1 color names a part | Knickers with Black Waistband | black | black knickers | generic |
| PLT-DA49102 | Knickers | 1 color names a part | Knickers with Green Waistband | green | green knickers | generic |
| PLT-DA49200 | Knickers | 2 another category's noun as a modifier | Cream Cami Knickers | cami | cami | generic |
| PLT-DA49201 | Knickers | 2 another category's noun as a modifier | Black Bikini Knickers | bikini | bikini | generic |
| PLT-DA49202 | Knickers | 2 another category's noun as a modifier | Red Cami Knickers | cami | cami | generic |
| PLT-DA49300 | Knickers | 3 audience word of a sibling version | White Mens-Style Knickers | mens | mens knickers | generic |
| PLT-DA49301 | Knickers | 3 audience word of a sibling version | Pink Boys Fit Knickers | boys | boys knickers | generic |
| PLT-DA49302 | Knickers | 3 audience word of a sibling version | Cream Mens Fit Knickers | mens | mens knickers | generic |
| PLT-DA49400 | Knickers | 4 material or feature named but absent | Green Leather-Look Knickers | leather | leather knickers | special: material claim |
| PLT-DA49401 | Knickers | 4 material or feature named but absent | Navy Suede-Look Knickers | suede | suede knickers | special: material claim |
| PLT-DA49402 | Knickers | 4 material or feature named but absent | White Cashmere-Feel Knickers | cashmere | cashmere knickers | special: material claim |
| PLT-DA49500 | Knickers | 5 shade spelled in the description only | Moonbeam Knickers | ivory | ivory knickers | generic |
| PLT-DA49501 | Knickers | 5 shade spelled in the description only | Driftwood Knickers | taupe | taupe knickers | generic |
| PLT-DA49502 | Knickers | 5 shade spelled in the description only | Dune Knickers | beige | beige knickers | generic |
| PLT-DA49600 | Knickers | 6 incidental word in a range name | Boot Hill Knickers | boot | boot | generic |
| PLT-DA49601 | Knickers | 6 incidental word in a range name | Slipper Brook Knickers | slipper | slipper | generic |
| PLT-DA49602 | Knickers | 6 incidental word in a range name | Sock Hop Knickers | sock | sock | generic |
| PLT-DA49700 | Knickers | 7 invented brand holding a color or category word | Yellow Wagtail Knickers | yellow | yellow knickers | generic |
| PLT-DA49701 | Knickers | 7 invented brand holding a color or category word | Red Plover Knickers | red | red knickers | generic |
| PLT-DA49702 | Knickers | 7 invented brand holding a color or category word | Blue Otter Knickers | blue | blue knickers | generic |
| PLT-DA50100 | Pyjama Shorts | 1 color names a part | Pyjama Shorts with Yellow Waistband | yellow | yellow pyjama shorts | generic |
| PLT-DA50101 | Pyjama Shorts | 1 color names a part | Pyjama Shorts with Red Waistband | red | red pyjama shorts | generic |
| PLT-DA50102 | Pyjama Shorts | 1 color names a part | Pyjama Shorts with Blue Waistband | blue | blue pyjama shorts | generic |
| PLT-DA50200 | Pyjama Shorts | 2 another category's noun as a modifier | Blue Bermuda Shorts | bermuda | bermuda | generic |
| PLT-DA50201 | Pyjama Shorts | 2 another category's noun as a modifier | Red Bermuda Shorts | bermuda | bermuda | generic |
| PLT-DA50202 | Pyjama Shorts | 2 another category's noun as a modifier | Red Boxer Shorts | boxer | boxer | generic |
| PLT-DA50300 | Pyjama Shorts | 3 audience word of a sibling version | Cream Mens-Style Pyjama Shorts | mens | mens pyjama shorts | generic |
| PLT-DA50301 | Pyjama Shorts | 3 audience word of a sibling version | Grey Boys Fit Pyjama Shorts | boys | boys pyjama shorts | generic |
| PLT-DA50302 | Pyjama Shorts | 3 audience word of a sibling version | Red Boys Fit Pyjama Shorts | boys | boys pyjama shorts | generic |
| PLT-DA50400 | Pyjama Shorts | 4 material or feature named but absent | Navy Leather-Look Pyjama Shorts | leather | leather pyjama shorts | special: material claim |
| PLT-DA50401 | Pyjama Shorts | 4 material or feature named but absent | Pink Suede-Look Pyjama Shorts | suede | suede pyjama shorts | special: material claim |
| PLT-DA50402 | Pyjama Shorts | 4 material or feature named but absent | Blue Cashmere-Feel Pyjama Shorts | cashmere | cashmere pyjama shorts | special: material claim |
| PLT-DA50500 | Pyjama Shorts | 5 shade spelled in the description only | Moonbeam Pyjama Shorts | ivory | ivory pyjama shorts | generic |
| PLT-DA50501 | Pyjama Shorts | 5 shade spelled in the description only | Driftwood Pyjama Shorts | taupe | taupe pyjama shorts | generic |
| PLT-DA50502 | Pyjama Shorts | 5 shade spelled in the description only | Dune Pyjama Shorts | beige | beige pyjama shorts | generic |
| PLT-DA50600 | Pyjama Shorts | 6 incidental word in a range name | Blazer Court Pyjama Shorts | blazer | blazer | generic |
| PLT-DA50601 | Pyjama Shorts | 6 incidental word in a range name | Sock Hop Pyjama Shorts | sock | sock | generic |
| PLT-DA50602 | Pyjama Shorts | 6 incidental word in a range name | Shirt Row Pyjama Shorts | shirt | shirt | generic |
| PLT-DA50700 | Pyjama Shorts | 7 invented brand holding a color or category word | Green Stoat Pyjama Shorts | green | green pyjama shorts | generic |
| PLT-DA50701 | Pyjama Shorts | 7 invented brand holding a color or category word | Jumper Jay Pyjama Shorts | jumper | jumper pyjama shorts | generic |
| PLT-DA50702 | Pyjama Shorts | 7 invented brand holding a color or category word | White Dormouse Pyjama Shorts | white | white pyjama shorts | generic |
| PLT-DA51100 | Pyjamas | 1 color names a part | Pyjamas with White Cuffs | white | white pyjamas | generic |
| PLT-DA51101 | Pyjamas | 1 color names a part | Pyjamas with Black Cuffs | black | black pyjamas | generic |
| PLT-DA51102 | Pyjamas | 1 color names a part | Pyjamas with Green Cuffs | green | green pyjamas | generic |
| PLT-DA51200 | Pyjamas | 2 another category's noun as a modifier | White Short Pyjamas | short | short | generic |
| PLT-DA51201 | Pyjamas | 2 another category's noun as a modifier | Red Short Pyjamas | short | short | generic |
| PLT-DA51202 | Pyjamas | 2 another category's noun as a modifier | Blue Short Pyjamas | short | short | generic |
| PLT-DA51300 | Pyjamas | 3 audience word of a sibling version | Green Mini-Me Mens Pyjamas | mens | mens pyjamas | generic |
| PLT-DA51301 | Pyjamas | 3 audience word of a sibling version | Red Mini-Me Mens Pyjamas | mens | mens pyjamas | generic |
| PLT-DA51302 | Pyjamas | 3 audience word of a sibling version | White Mini-Me Womens Pyjamas | womens | womens pyjamas | generic |
| PLT-DA51400 | Pyjamas | 4 material or feature named but absent | Black Leather-Look Pyjamas | leather | leather pyjamas | special: material claim |
| PLT-DA51401 | Pyjamas | 4 material or feature named but absent | Grey Suede-Look Pyjamas | suede | suede pyjamas | special: material claim |
| PLT-DA51402 | Pyjamas | 4 material or feature named but absent | Red Cashmere-Feel Pyjamas | cashmere | cashmere pyjamas | special: material claim |
| PLT-DA51500 | Pyjamas | 5 shade spelled in the description only | Moonbeam Pyjamas | ivory | ivory pyjamas | generic |
| PLT-DA51501 | Pyjamas | 5 shade spelled in the description only | Driftwood Pyjamas | taupe | taupe pyjamas | generic |
| PLT-DA51502 | Pyjamas | 5 shade spelled in the description only | Dune Pyjamas | beige | beige pyjamas | generic |
| PLT-DA51600 | Pyjamas | 6 incidental word in a range name | Sandal Wood Pyjamas | sandal | sandal | generic |
| PLT-DA51601 | Pyjamas | 6 incidental word in a range name | Slipper Brook Pyjamas | slipper | slipper | generic |
| PLT-DA51602 | Pyjamas | 6 incidental word in a range name | Shoe Lane Pyjamas | shoe | shoe | generic |
| PLT-DA51700 | Pyjamas | 7 invented brand holding a color or category word | Coat Crake Pyjamas | coat | coat pyjamas | generic |
| PLT-DA51701 | Pyjamas | 7 invented brand holding a color or category word | Red Plover Pyjamas | red | red pyjamas | generic |
| PLT-DA51702 | Pyjamas | 7 invented brand holding a color or category word | Green Stoat Pyjamas | green | green pyjamas | generic |
| PLT-DA52100 | Shapewear | 1 color names a part | Shapewear with Black Straps | black | black shapewear | generic |
| PLT-DA52101 | Shapewear | 1 color names a part | Shapewear with Yellow Straps | yellow | yellow shapewear | generic |
| PLT-DA52102 | Shapewear | 1 color names a part | Shapewear with Blue Straps | blue | blue shapewear | generic |
| PLT-DA52200 | Shapewear | 2 another category's noun as a modifier | Blue Bodysuit Shapewear | bodysuit | bodysuit | generic |
| PLT-DA52201 | Shapewear | 2 another category's noun as a modifier | White Slip Shapewear | slip | slip | generic |
| PLT-DA52202 | Shapewear | 2 another category's noun as a modifier | Grey Cami Shapewear | cami | cami | generic |
| PLT-DA52300 | Shapewear | 3 audience word of a sibling version | Brown Mens-Style Shapewear | mens | mens shapewear | generic |
| PLT-DA52301 | Shapewear | 3 audience word of a sibling version | Navy Mens Fit Shapewear | mens | mens shapewear | generic |
| PLT-DA52302 | Shapewear | 3 audience word of a sibling version | Pink Mens Fit Shapewear | mens | mens shapewear | generic |
| PLT-DA52400 | Shapewear | 4 material or feature named but absent | Green Leather-Look Shapewear | leather | leather shapewear | special: material claim |
| PLT-DA52401 | Shapewear | 4 material or feature named but absent | White Suede-Look Shapewear | suede | suede shapewear | special: material claim |
| PLT-DA52402 | Shapewear | 4 material or feature named but absent | Grey Cashmere-Feel Shapewear | cashmere | cashmere shapewear | special: material claim |
| PLT-DA52500 | Shapewear | 5 shade spelled in the description only | Moonbeam Shapewear | ivory | ivory shapewear | generic |
| PLT-DA52501 | Shapewear | 5 shade spelled in the description only | Driftwood Shapewear | taupe | taupe shapewear | generic |
| PLT-DA52502 | Shapewear | 5 shade spelled in the description only | Dune Shapewear | beige | beige shapewear | generic |
| PLT-DA52600 | Shapewear | 6 incidental word in a range name | Dress Circle Shapewear | dress | dress | generic |
| PLT-DA52601 | Shapewear | 6 incidental word in a range name | Sandal Wood Shapewear | sandal | sandal | generic |
| PLT-DA52602 | Shapewear | 6 incidental word in a range name | Blazer Court Shapewear | blazer | blazer | generic |
| PLT-DA52700 | Shapewear | 7 invented brand holding a color or category word | Red Plover Shapewear | red | red shapewear | generic |
| PLT-DA52701 | Shapewear | 7 invented brand holding a color or category word | Coat Crake Shapewear | coat | coat shapewear | generic |
| PLT-DA52702 | Shapewear | 7 invented brand holding a color or category word | Black Lapwing Shapewear | black | black shapewear | generic |
| PLT-DA53100 | Slip | 1 color names a part | Slip with Red Straps | red | red slip | generic |
| PLT-DA53101 | Slip | 1 color names a part | Slip with Yellow Straps | yellow | yellow slip | generic |
| PLT-DA53102 | Slip | 1 color names a part | Slip with White Straps | white | white slip | generic |
| PLT-DA53200 | Slip | 2 another category's noun as a modifier | Red Skirt Slip | skirt | skirt | generic |
| PLT-DA53201 | Slip | 2 another category's noun as a modifier | Blue Skirt Slip | skirt | skirt | generic |
| PLT-DA53202 | Slip | 2 another category's noun as a modifier | Grey Dress Slip | dress | dress | generic |
| PLT-DA53300 | Slip | 3 audience word of a sibling version | Brown Mens Fit Slip | mens | mens slip | generic |
| PLT-DA53301 | Slip | 3 audience word of a sibling version | White Boys Fit Slip | boys | boys slip | generic |
| PLT-DA53302 | Slip | 3 audience word of a sibling version | Blue Mens-Style Slip | mens | mens slip | generic |
| PLT-DA53400 | Slip | 4 material or feature named but absent | Grey Leather-Look Slip | leather | leather slip | special: material claim |
| PLT-DA53401 | Slip | 4 material or feature named but absent | Red Suede-Look Slip | suede | suede slip | special: material claim |
| PLT-DA53402 | Slip | 4 material or feature named but absent | Red Cashmere-Feel Slip | cashmere | cashmere slip | special: material claim |
| PLT-DA53500 | Slip | 5 shade spelled in the description only | Moonbeam Slip | ivory | ivory slip | generic |
| PLT-DA53501 | Slip | 5 shade spelled in the description only | Driftwood Slip | taupe | taupe slip | generic |
| PLT-DA53502 | Slip | 5 shade spelled in the description only | Dune Slip | beige | beige slip | generic |
| PLT-DA53600 | Slip | 6 incidental word in a range name | Dress Circle Slip | dress | dress | generic |
| PLT-DA53601 | Slip | 6 incidental word in a range name | Shirt Row Slip | shirt | shirt | generic |
| PLT-DA53602 | Slip | 6 incidental word in a range name | Pump Lane Slip | pump | pump | generic |
| PLT-DA53700 | Slip | 7 invented brand holding a color or category word | Jumper Jay Slip | jumper | jumper slip | generic |
| PLT-DA53701 | Slip | 7 invented brand holding a color or category word | Blue Otter Slip | blue | blue slip | generic |
| PLT-DA53702 | Slip | 7 invented brand holding a color or category word | Green Stoat Slip | green | green slip | generic |
| PLT-DA54100 | Tights | 1 color names a part | Tights with Black Waistband | black | black tights | generic |
| PLT-DA54101 | Tights | 1 color names a part | Tights with White Waistband | white | white tights | generic |
| PLT-DA54102 | Tights | 1 color names a part | Tights with Yellow Waistband | yellow | yellow tights | generic |
| PLT-DA54200 | Tights | 2 another category's noun as a modifier | Red Running Tights | running | running | generic |
| PLT-DA54201 | Tights | 2 another category's noun as a modifier | Green Running Tights | running | running | generic |
| PLT-DA54202 | Tights | 2 another category's noun as a modifier | Navy Running Tights | running | running | generic |
| PLT-DA54300 | Tights | 3 audience word of a sibling version | Pink Boys Fit Tights | boys | boys tights | generic |
| PLT-DA54301 | Tights | 3 audience word of a sibling version | Green Mens-Style Tights | mens | mens tights | generic |
| PLT-DA54302 | Tights | 3 audience word of a sibling version | Blue Mens Fit Tights | mens | mens tights | generic |
| PLT-DA54400 | Tights | 4 material or feature named but absent | Navy Leather-Look Tights | leather | leather tights | special: material claim |
| PLT-DA54401 | Tights | 4 material or feature named but absent | Blue Suede-Look Tights | suede | suede tights | special: material claim |
| PLT-DA54402 | Tights | 4 material or feature named but absent | Brown Cashmere-Feel Tights | cashmere | cashmere tights | special: material claim |
| PLT-DA54500 | Tights | 5 shade spelled in the description only | Moonbeam Tights | ivory | ivory tights | generic |
| PLT-DA54501 | Tights | 5 shade spelled in the description only | Driftwood Tights | taupe | taupe tights | generic |
| PLT-DA54502 | Tights | 5 shade spelled in the description only | Dune Tights | beige | beige tights | generic |
| PLT-DA54600 | Tights | 6 incidental word in a range name | Sandal Wood Tights | sandal | sandal | generic |
| PLT-DA54601 | Tights | 6 incidental word in a range name | Slipper Brook Tights | slipper | slipper | generic |
| PLT-DA54602 | Tights | 6 incidental word in a range name | Coat Hook Tights | coat | coat | generic |
| PLT-DA54700 | Tights | 7 invented brand holding a color or category word | Jumper Jay Tights | jumper | jumper tights | generic |
| PLT-DA54701 | Tights | 7 invented brand holding a color or category word | Red Plover Tights | red | red tights | generic |
| PLT-DA54702 | Tights | 7 invented brand holding a color or category word | Coat Crake Tights | coat | coat tights | generic |
| PLT-DA55100 | Vest | 1 color names a part | Vest with Red Straps | red | red vest | generic |
| PLT-DA55101 | Vest | 1 color names a part | Vest with White Straps | white | white vest | generic |
| PLT-DA55102 | Vest | 1 color names a part | Vest with Yellow Straps | yellow | yellow vest | generic |
| PLT-DA55200 | Vest | 2 another category's noun as a modifier | Blue Dress Vest | dress | dress | generic |
| PLT-DA55201 | Vest | 2 another category's noun as a modifier | Grey Dress Vest | dress | dress | generic |
| PLT-DA55202 | Vest | 2 another category's noun as a modifier | Brown Cami Vest | cami | cami | generic |
| PLT-DA55300 | Vest | 3 audience word of a sibling version | White Womens Fit Vest | womens | womens vest | generic |
| PLT-DA55301 | Vest | 3 audience word of a sibling version | Grey Mens Fit Vest | mens | mens vest | generic |
| PLT-DA55302 | Vest | 3 audience word of a sibling version | Brown Boys Fit Vest | boys | boys vest | generic |
| PLT-DA55400 | Vest | 4 material or feature named but absent | Red Leather-Look Vest | leather | leather vest | special: material claim |
| PLT-DA55401 | Vest | 4 material or feature named but absent | Brown Suede-Look Vest | suede | suede vest | special: material claim |
| PLT-DA55402 | Vest | 4 material or feature named but absent | Red Cashmere-Feel Vest | cashmere | cashmere vest | special: material claim |
| PLT-DA55500 | Vest | 5 shade spelled in the description only | Moonbeam Vest | ivory | ivory vest | generic |
| PLT-DA55501 | Vest | 5 shade spelled in the description only | Driftwood Vest | taupe | taupe vest | generic |
| PLT-DA55502 | Vest | 5 shade spelled in the description only | Dune Vest | beige | beige vest | generic |
| PLT-DA55600 | Vest | 6 incidental word in a range name | Coat Hook Vest | coat | coat | generic |
| PLT-DA55601 | Vest | 6 incidental word in a range name | Slip Road Vest | slip | slip | generic |
| PLT-DA55602 | Vest | 6 incidental word in a range name | Boot Hill Vest | boot | boot | generic |
| PLT-DA55700 | Vest | 7 invented brand holding a color or category word | Coat Crake Vest | coat | coat vest | generic |
| PLT-DA55701 | Vest | 7 invented brand holding a color or category word | Yellow Wagtail Vest | yellow | yellow vest | generic |
| PLT-DA55702 | Vest | 7 invented brand holding a color or category word | Red Plover Vest | red | red vest | generic |
| PLT-DA56100 | School Trousers | 1 color names a part | School Trousers with White Cuffs | white | white school trousers | generic |
| PLT-DA56101 | School Trousers | 1 color names a part | School Trousers with Black Waistband | black | black school trousers | generic |
| PLT-DA56102 | School Trousers | 1 color names a part | School Trousers with Red Waistband | red | red school trousers | generic |
| PLT-DA56200 | School Trousers | 2 another category's noun as a modifier | White Chino School Trousers | chino | chino | generic |
| PLT-DA56201 | School Trousers | 2 another category's noun as a modifier | Cream Cargo School Trousers | cargo | cargo | generic |
| PLT-DA56202 | School Trousers | 2 another category's noun as a modifier | Blue Jogger School Trousers | jogger | jogger | generic |
| PLT-DA56300 | School Trousers | 3 audience word of a sibling version | Cream Mens-Style School Trousers | mens | mens school trousers | generic |
| PLT-DA56301 | School Trousers | 3 audience word of a sibling version | Brown Mini-Me Womens School Trousers | womens | womens school trousers | generic |
| PLT-DA56302 | School Trousers | 3 audience word of a sibling version | Navy Mini-Me Mens School Trousers | mens | mens school trousers | generic |
| PLT-DA56400 | School Trousers | 4 material or feature named but absent | Blue Leather-Look School Trousers | leather | leather school trousers | special: material claim |
| PLT-DA56401 | School Trousers | 4 material or feature named but absent | Pink Suede-Look School Trousers | suede | suede school trousers | special: material claim |
| PLT-DA56402 | School Trousers | 4 material or feature named but absent | Pink Cashmere-Feel School Trousers | cashmere | cashmere school trousers | special: material claim |
| PLT-DA56500 | School Trousers | 5 shade spelled in the description only | Moonbeam School Trousers | ivory | ivory school trousers | generic |
| PLT-DA56501 | School Trousers | 5 shade spelled in the description only | Driftwood School Trousers | taupe | taupe school trousers | generic |
| PLT-DA56502 | School Trousers | 5 shade spelled in the description only | Dune School Trousers | beige | beige school trousers | generic |
| PLT-DA56600 | School Trousers | 6 incidental word in a range name | Shoe Lane School Trousers | shoe | shoe | generic |
| PLT-DA56601 | School Trousers | 6 incidental word in a range name | Pump Lane School Trousers | pump | pump | generic |
| PLT-DA56602 | School Trousers | 6 incidental word in a range name | Coat Hook School Trousers | coat | coat | generic |
| PLT-DA56700 | School Trousers | 7 invented brand holding a color or category word | Yellow Wagtail School Trousers | yellow | yellow school trousers | generic |
| PLT-DA56701 | School Trousers | 7 invented brand holding a color or category word | Black Lapwing School Trousers | black | black school trousers | generic |
| PLT-DA56702 | School Trousers | 7 invented brand holding a color or category word | Green Stoat School Trousers | green | green school trousers | generic |
| PLT-DA57100 | School Skirt | 1 color names a part | School Skirt with White Waistband | white | white school skirt | generic |
| PLT-DA57101 | School Skirt | 1 color names a part | School Skirt with Red Waistband | red | red school skirt | generic |
| PLT-DA57102 | School Skirt | 1 color names a part | School Skirt with Black Waistband | black | black school skirt | generic |
| PLT-DA57200 | School Skirt | 2 another category's noun as a modifier | Green Pinafore School Skirt | pinafore | pinafore | generic |
| PLT-DA57201 | School Skirt | 2 another category's noun as a modifier | White Pinafore School Skirt | pinafore | pinafore | generic |
| PLT-DA57202 | School Skirt | 2 another category's noun as a modifier | Navy Pinafore School Skirt | pinafore | pinafore | generic |
| PLT-DA57300 | School Skirt | 3 audience word of a sibling version | White Mini-Me Mens School Skirt | mens | mens school skirt | generic |
| PLT-DA57301 | School Skirt | 3 audience word of a sibling version | Red Mini-Me Womens School Skirt | womens | womens school skirt | generic |
| PLT-DA57302 | School Skirt | 3 audience word of a sibling version | Cream Mini-Me Womens School Skirt | womens | womens school skirt | generic |
| PLT-DA57400 | School Skirt | 4 material or feature named but absent | Grey Leather-Look School Skirt | leather | leather school skirt | special: material claim |
| PLT-DA57401 | School Skirt | 4 material or feature named but absent | Black Suede-Look School Skirt | suede | suede school skirt | special: material claim |
| PLT-DA57402 | School Skirt | 4 material or feature named but absent | Red Cashmere-Feel School Skirt | cashmere | cashmere school skirt | special: material claim |
| PLT-DA57500 | School Skirt | 5 shade spelled in the description only | Moonbeam School Skirt | ivory | ivory school skirt | generic |
| PLT-DA57501 | School Skirt | 5 shade spelled in the description only | Driftwood School Skirt | taupe | taupe school skirt | generic |
| PLT-DA57502 | School Skirt | 5 shade spelled in the description only | Dune School Skirt | beige | beige school skirt | generic |
| PLT-DA57600 | School Skirt | 6 incidental word in a range name | Slipper Brook School Skirt | slipper | slipper | generic |
| PLT-DA57601 | School Skirt | 6 incidental word in a range name | Slip Road School Skirt | slip | slip | generic |
| PLT-DA57602 | School Skirt | 6 incidental word in a range name | Sandal Wood School Skirt | sandal | sandal | generic |
| PLT-DA57700 | School Skirt | 7 invented brand holding a color or category word | White Dormouse School Skirt | white | white school skirt | generic |
| PLT-DA57701 | School Skirt | 7 invented brand holding a color or category word | Yellow Wagtail School Skirt | yellow | yellow school skirt | generic |
| PLT-DA57702 | School Skirt | 7 invented brand holding a color or category word | Black Lapwing School Skirt | black | black school skirt | generic |
| PLT-DA58100 | School Pinafore | 1 color names a part | School Pinafore with Yellow Straps | yellow | yellow school pinafore | generic |
| PLT-DA58101 | School Pinafore | 1 color names a part | School Pinafore with Blue Straps | blue | blue school pinafore | generic |
| PLT-DA58102 | School Pinafore | 1 color names a part | School Pinafore with Green Straps | green | green school pinafore | generic |
| PLT-DA58200 | School Pinafore | 2 another category's noun as a modifier | Pink School Pinafore Dress | dress | dress | generic |
| PLT-DA58201 | School Pinafore | 2 another category's noun as a modifier | White School Pinafore Dress | dress | dress | generic |
| PLT-DA58202 | School Pinafore | 2 another category's noun as a modifier | Brown School Pinafore Dress | dress | dress | generic |
| PLT-DA58300 | School Pinafore | 3 audience word of a sibling version | Navy Mini-Me Womens School Pinafore | womens | womens school pinafore | generic |
| PLT-DA58301 | School Pinafore | 3 audience word of a sibling version | Grey Mini-Me Mens School Pinafore | mens | mens school pinafore | generic |
| PLT-DA58302 | School Pinafore | 3 audience word of a sibling version | Blue Mens-Style School Pinafore | mens | mens school pinafore | generic |
| PLT-DA58400 | School Pinafore | 4 material or feature named but absent | Cream Leather-Look School Pinafore | leather | leather school pinafore | special: material claim |
| PLT-DA58401 | School Pinafore | 4 material or feature named but absent | Brown Suede-Look School Pinafore | suede | suede school pinafore | special: material claim |
| PLT-DA58402 | School Pinafore | 4 material or feature named but absent | White Cashmere-Feel School Pinafore | cashmere | cashmere school pinafore | special: material claim |
| PLT-DA58500 | School Pinafore | 5 shade spelled in the description only | Moonbeam School Pinafore | ivory | ivory school pinafore | generic |
| PLT-DA58501 | School Pinafore | 5 shade spelled in the description only | Driftwood School Pinafore | taupe | taupe school pinafore | generic |
| PLT-DA58502 | School Pinafore | 5 shade spelled in the description only | Dune School Pinafore | beige | beige school pinafore | generic |
| PLT-DA58600 | School Pinafore | 6 incidental word in a range name | Slip Road School Pinafore | slip | slip | generic |
| PLT-DA58601 | School Pinafore | 6 incidental word in a range name | Slipper Brook School Pinafore | slipper | slipper | generic |
| PLT-DA58602 | School Pinafore | 6 incidental word in a range name | Blazer Court School Pinafore | blazer | blazer | generic |
| PLT-DA58700 | School Pinafore | 7 invented brand holding a color or category word | Jumper Jay School Pinafore | jumper | jumper school pinafore | generic |
| PLT-DA58701 | School Pinafore | 7 invented brand holding a color or category word | White Dormouse School Pinafore | white | white school pinafore | generic |
| PLT-DA58702 | School Pinafore | 7 invented brand holding a color or category word | Coat Crake School Pinafore | coat | coat school pinafore | generic |
| PLT-DA59100 | School Shirt | 1 color names a part | School Shirt with Black Collar | black | black school shirt | generic |
| PLT-DA59101 | School Shirt | 1 color names a part | School Shirt with Black Hem | black | black school shirt | generic |
| PLT-DA59102 | School Shirt | 1 color names a part | School Shirt with Green Hem | green | green school shirt | generic |
| PLT-DA59200 | School Shirt | 2 another category's noun as a modifier | White School Polo Shirt | polo | polo | generic |
| PLT-DA59201 | School Shirt | 2 another category's noun as a modifier | Green Oxford School Shirt | oxford | oxford | generic |
| PLT-DA59202 | School Shirt | 2 another category's noun as a modifier | Brown School Polo Shirt | polo | polo | generic |
| PLT-DA59300 | School Shirt | 3 audience word of a sibling version | Blue Mens-Style School Shirt | mens | mens school shirt | generic |
| PLT-DA59301 | School Shirt | 3 audience word of a sibling version | Brown Mini-Me Womens School Shirt | womens | womens school shirt | generic |
| PLT-DA59302 | School Shirt | 3 audience word of a sibling version | Brown Mini-Me Mens School Shirt | mens | mens school shirt | generic |
| PLT-DA59400 | School Shirt | 4 material or feature named but absent | Cream Leather-Look School Shirt | leather | leather school shirt | special: material claim |
| PLT-DA59401 | School Shirt | 4 material or feature named but absent | Green Suede-Look School Shirt | suede | suede school shirt | special: material claim |
| PLT-DA59402 | School Shirt | 4 material or feature named but absent | Brown Cashmere-Feel School Shirt | cashmere | cashmere school shirt | special: material claim |
| PLT-DA59500 | School Shirt | 5 shade spelled in the description only | Moonbeam School Shirt | ivory | ivory school shirt | generic |
| PLT-DA59501 | School Shirt | 5 shade spelled in the description only | Driftwood School Shirt | taupe | taupe school shirt | generic |
| PLT-DA59502 | School Shirt | 5 shade spelled in the description only | Dune School Shirt | beige | beige school shirt | generic |
| PLT-DA59600 | School Shirt | 6 incidental word in a range name | Cardigan Bay School Shirt | cardigan | cardigan | generic |
| PLT-DA59601 | School Shirt | 6 incidental word in a range name | Boot Hill School Shirt | boot | boot | generic |
| PLT-DA59602 | School Shirt | 6 incidental word in a range name | Skirt Point School Shirt | skirt | skirt | generic |
| PLT-DA59700 | School Shirt | 7 invented brand holding a color or category word | Yellow Wagtail School Shirt | yellow | yellow school shirt | generic |
| PLT-DA59701 | School Shirt | 7 invented brand holding a color or category word | White Dormouse School Shirt | white | white school shirt | generic |
| PLT-DA59702 | School Shirt | 7 invented brand holding a color or category word | Green Stoat School Shirt | green | green school shirt | generic |
| PLT-DA60100 | Plimsolls | 1 color names a part | Plimsolls with Yellow Sole | yellow | yellow plimsolls | generic |
| PLT-DA60101 | Plimsolls | 1 color names a part | Plimsolls with Black Sole | black | black plimsolls | generic |
| PLT-DA60102 | Plimsolls | 1 color names a part | Plimsolls with Blue Sole | blue | blue plimsolls | generic |
| PLT-DA60200 | Plimsolls | 2 another category's noun as a modifier | Green Sneaker Plimsolls | sneaker | sneaker | generic |
| PLT-DA60201 | Plimsolls | 2 another category's noun as a modifier | Grey Sneaker Plimsolls | sneaker | sneaker | generic |
| PLT-DA60202 | Plimsolls | 2 another category's noun as a modifier | Black Sneaker Plimsolls | sneaker | sneaker | generic |
| PLT-DA60300 | Plimsolls | 3 audience word of a sibling version | Red Mens-Style Plimsolls | mens | mens plimsolls | generic |
| PLT-DA60301 | Plimsolls | 3 audience word of a sibling version | White Womens-Style Plimsolls | womens | womens plimsolls | generic |
| PLT-DA60302 | Plimsolls | 3 audience word of a sibling version | Brown Boys Fit Plimsolls | boys | boys plimsolls | generic |
| PLT-DA60400 | Plimsolls | 4 material or feature named but absent | Red Leather-Look Plimsolls | leather | leather plimsolls | special: material claim |
| PLT-DA60401 | Plimsolls | 4 material or feature named but absent | Brown Suede-Look Plimsolls | suede | suede plimsolls | special: material claim |
| PLT-DA60402 | Plimsolls | 4 material or feature named but absent | Blue Cashmere-Feel Plimsolls | cashmere | cashmere plimsolls | special: material claim |
| PLT-DA60500 | Plimsolls | 5 shade spelled in the description only | Moonbeam Plimsolls | ivory | ivory plimsolls | generic |
| PLT-DA60501 | Plimsolls | 5 shade spelled in the description only | Driftwood Plimsolls | taupe | taupe plimsolls | generic |
| PLT-DA60502 | Plimsolls | 5 shade spelled in the description only | Dune Plimsolls | beige | beige plimsolls | generic |
| PLT-DA60600 | Plimsolls | 6 incidental word in a range name | Slipper Brook Plimsolls | slipper | slipper | generic |
| PLT-DA60601 | Plimsolls | 6 incidental word in a range name | Blazer Court Plimsolls | blazer | blazer | generic |
| PLT-DA60602 | Plimsolls | 6 incidental word in a range name | Blazer Court Plimsolls | blazer | blazer | generic |
| PLT-DA60700 | Plimsolls | 7 invented brand holding a color or category word | Red Plover Plimsolls | red | red plimsolls | generic |
| PLT-DA60701 | Plimsolls | 7 invented brand holding a color or category word | Black Lapwing Plimsolls | black | black plimsolls | generic |
| PLT-DA60702 | Plimsolls | 7 invented brand holding a color or category word | Coat Crake Plimsolls | coat | coat plimsolls | generic |
| PLT-DA61100 | Clogs | 1 color names a part | Clogs with White Sole | white | white clogs | generic |
| PLT-DA61101 | Clogs | 1 color names a part | Clogs with Blue Sole | blue | blue clogs | generic |
| PLT-DA61102 | Clogs | 1 color names a part | Clogs with Green Sole | green | green clogs | generic |
| PLT-DA61200 | Clogs | 2 another category's noun as a modifier | Pink Mule Clogs | mule | mule | generic |
| PLT-DA61201 | Clogs | 2 another category's noun as a modifier | Pink Mule Clogs | mule | mule | generic |
| PLT-DA61202 | Clogs | 2 another category's noun as a modifier | Brown Mule Clogs | mule | mule | generic |
| PLT-DA61300 | Clogs | 3 audience word of a sibling version | Grey Womens-Style Clogs | womens | womens clogs | generic |
| PLT-DA61301 | Clogs | 3 audience word of a sibling version | Pink Mens Fit Clogs | mens | mens clogs | generic |
| PLT-DA61302 | Clogs | 3 audience word of a sibling version | Blue Mens Fit Clogs | mens | mens clogs | generic |
| PLT-DA61400 | Clogs | 4 material or feature named but absent | Green Suede-Look Clogs | suede | suede clogs | special: material claim |
| PLT-DA61401 | Clogs | 4 material or feature named but absent | Black Leather-Look Clogs | leather | leather clogs | special: material claim |
| PLT-DA61402 | Clogs | 4 material or feature named but absent | Pink Cashmere-Feel Clogs | cashmere | cashmere clogs | special: material claim |
| PLT-DA61500 | Clogs | 5 shade spelled in the description only | Moonbeam Clogs | ivory | ivory clogs | generic |
| PLT-DA61501 | Clogs | 5 shade spelled in the description only | Driftwood Clogs | taupe | taupe clogs | generic |
| PLT-DA61502 | Clogs | 5 shade spelled in the description only | Dune Clogs | beige | beige clogs | generic |
| PLT-DA61600 | Clogs | 6 incidental word in a range name | Dress Circle Clogs | dress | dress | generic |
| PLT-DA61601 | Clogs | 6 incidental word in a range name | Jacket Quay Clogs | jacket | jacket | generic |
| PLT-DA61602 | Clogs | 6 incidental word in a range name | Sandal Wood Clogs | sandal | sandal | generic |
| PLT-DA61700 | Clogs | 7 invented brand holding a color or category word | Jumper Jay Clogs | jumper | jumper clogs | generic |
| PLT-DA61701 | Clogs | 7 invented brand holding a color or category word | Red Plover Clogs | red | red clogs | generic |
| PLT-DA61702 | Clogs | 7 invented brand holding a color or category word | Jumper Jay Clogs | jumper | jumper clogs | generic |
| PLT-DA62100 | Wedges | 1 color names a part | Wedges with Green Sole | green | green wedges | generic |
| PLT-DA62101 | Wedges | 1 color names a part | Wedges with Blue Sole | blue | blue wedges | generic |
| PLT-DA62102 | Wedges | 1 color names a part | Wedges with White Sole | white | white wedges | generic |
| PLT-DA62200 | Wedges | 2 another category's noun as a modifier | Pink Sneaker Wedges | sneaker | sneaker | generic |
| PLT-DA62201 | Wedges | 2 another category's noun as a modifier | Navy Sandal Wedges | sandal | sandal | generic |
| PLT-DA62202 | Wedges | 2 another category's noun as a modifier | Cream Sandal Wedges | sandal | sandal | generic |
| PLT-DA62300 | Wedges | 3 audience word of a sibling version | Pink Boys Fit Wedges | boys | boys wedges | generic |
| PLT-DA62301 | Wedges | 3 audience word of a sibling version | Black Mens Fit Wedges | mens | mens wedges | generic |
| PLT-DA62302 | Wedges | 3 audience word of a sibling version | Navy Mens-Style Wedges | mens | mens wedges | generic |
| PLT-DA62400 | Wedges | 4 material or feature named but absent | Red Leather-Look Wedges | leather | leather wedges | special: material claim |
| PLT-DA62401 | Wedges | 4 material or feature named but absent | Grey Suede-Look Wedges | suede | suede wedges | special: material claim |
| PLT-DA62402 | Wedges | 4 material or feature named but absent | Black Cashmere-Feel Wedges | cashmere | cashmere wedges | special: material claim |
| PLT-DA62500 | Wedges | 5 shade spelled in the description only | Moonbeam Wedges | ivory | ivory wedges | generic |
| PLT-DA62501 | Wedges | 5 shade spelled in the description only | Driftwood Wedges | taupe | taupe wedges | generic |
| PLT-DA62502 | Wedges | 5 shade spelled in the description only | Dune Wedges | beige | beige wedges | generic |
| PLT-DA62600 | Wedges | 6 incidental word in a range name | Shirt Row Wedges | shirt | shirt | generic |
| PLT-DA62601 | Wedges | 6 incidental word in a range name | Jacket Quay Wedges | jacket | jacket | generic |
| PLT-DA62602 | Wedges | 6 incidental word in a range name | Slipper Brook Wedges | slipper | slipper | generic |
| PLT-DA62700 | Wedges | 7 invented brand holding a color or category word | White Dormouse Wedges | white | white wedges | generic |
| PLT-DA62701 | Wedges | 7 invented brand holding a color or category word | Blue Otter Wedges | blue | blue wedges | generic |
| PLT-DA62702 | Wedges | 7 invented brand holding a color or category word | Jumper Jay Wedges | jumper | jumper wedges | generic |
| PLT-DA63100 | Espadrilles | 1 color names a part | Espadrilles with Black Sole | black | black espadrilles | generic |
| PLT-DA63101 | Espadrilles | 1 color names a part | Espadrilles with Red Sole | red | red espadrilles | generic |
| PLT-DA63102 | Espadrilles | 1 color names a part | Espadrilles with Blue Sole | blue | blue espadrilles | generic |
| PLT-DA63200 | Espadrilles | 2 another category's noun as a modifier | Green Sneaker Espadrilles | sneaker | sneaker | generic |
| PLT-DA63201 | Espadrilles | 2 another category's noun as a modifier | Navy Sneaker Espadrilles | sneaker | sneaker | generic |
| PLT-DA63202 | Espadrilles | 2 another category's noun as a modifier | Grey Sneaker Espadrilles | sneaker | sneaker | generic |
| PLT-DA63300 | Espadrilles | 3 audience word of a sibling version | White Girls Fit Espadrilles | girls | girls espadrilles | generic |
| PLT-DA63301 | Espadrilles | 3 audience word of a sibling version | White Boys Fit Espadrilles | boys | boys espadrilles | generic |
| PLT-DA63302 | Espadrilles | 3 audience word of a sibling version | Green Mens-Style Espadrilles | mens | mens espadrilles | generic |
| PLT-DA63400 | Espadrilles | 4 material or feature named but absent | Red Leather-Look Espadrilles | leather | leather espadrilles | special: material claim |
| PLT-DA63401 | Espadrilles | 4 material or feature named but absent | Navy Suede-Look Espadrilles | suede | suede espadrilles | special: material claim |
| PLT-DA63402 | Espadrilles | 4 material or feature named but absent | Blue Cashmere-Feel Espadrilles | cashmere | cashmere espadrilles | special: material claim |
| PLT-DA63500 | Espadrilles | 5 shade spelled in the description only | Moonbeam Espadrilles | ivory | ivory espadrilles | generic |
| PLT-DA63501 | Espadrilles | 5 shade spelled in the description only | Driftwood Espadrilles | taupe | taupe espadrilles | generic |
| PLT-DA63502 | Espadrilles | 5 shade spelled in the description only | Dune Espadrilles | beige | beige espadrilles | generic |
| PLT-DA63600 | Espadrilles | 6 incidental word in a range name | Cardigan Bay Espadrilles | cardigan | cardigan | generic |
| PLT-DA63601 | Espadrilles | 6 incidental word in a range name | Slipper Brook Espadrilles | slipper | slipper | generic |
| PLT-DA63602 | Espadrilles | 6 incidental word in a range name | Blazer Court Espadrilles | blazer | blazer | generic |
| PLT-DA63700 | Espadrilles | 7 invented brand holding a color or category word | Jumper Jay Espadrilles | jumper | jumper espadrilles | generic |
| PLT-DA63701 | Espadrilles | 7 invented brand holding a color or category word | Blue Otter Espadrilles | blue | blue espadrilles | generic |
| PLT-DA63702 | Espadrilles | 7 invented brand holding a color or category word | Jumper Jay Espadrilles | jumper | jumper espadrilles | generic |
| PLT-DA64100 | Platform Trainers | 1 color names a part | Platform Trainers with White Sole | white | white platform trainers | generic |
| PLT-DA64101 | Platform Trainers | 1 color names a part | Platform Trainers with Green Sole | green | green platform trainers | generic |
| PLT-DA64102 | Platform Trainers | 1 color names a part | Platform Trainers with Red Sole | red | red platform trainers | generic |
| PLT-DA64200 | Platform Trainers | 2 another category's noun as a modifier | White Sock Platform Trainers | sock | sock | generic |
| PLT-DA64201 | Platform Trainers | 2 another category's noun as a modifier | Navy Sock Platform Trainers | sock | sock | generic |
| PLT-DA64202 | Platform Trainers | 2 another category's noun as a modifier | Black Sock Platform Trainers | sock | sock | generic |
| PLT-DA64300 | Platform Trainers | 3 audience word of a sibling version | Cream Mens-Style Platform Trainers | mens | mens platform trainers | generic |
| PLT-DA64301 | Platform Trainers | 3 audience word of a sibling version | Blue Mens-Style Platform Trainers | mens | mens platform trainers | generic |
| PLT-DA64302 | Platform Trainers | 3 audience word of a sibling version | Navy Boys Fit Platform Trainers | boys | boys platform trainers | generic |
| PLT-DA64400 | Platform Trainers | 4 material or feature named but absent | Pink Leather-Look Platform Trainers | leather | leather platform trainers | special: material claim |
| PLT-DA64401 | Platform Trainers | 4 material or feature named but absent | Grey Suede-Look Platform Trainers | suede | suede platform trainers | special: material claim |
| PLT-DA64402 | Platform Trainers | 4 material or feature named but absent | Green Cashmere-Feel Platform Trainers | cashmere | cashmere platform trainers | special: material claim |
| PLT-DA64500 | Platform Trainers | 5 shade spelled in the description only | Moonbeam Platform Trainers | ivory | ivory platform trainers | generic |
| PLT-DA64501 | Platform Trainers | 5 shade spelled in the description only | Driftwood Platform Trainers | taupe | taupe platform trainers | generic |
| PLT-DA64502 | Platform Trainers | 5 shade spelled in the description only | Dune Platform Trainers | beige | beige platform trainers | generic |
| PLT-DA64600 | Platform Trainers | 6 incidental word in a range name | Slip Road Platform Trainers | slip | slip | generic |
| PLT-DA64601 | Platform Trainers | 6 incidental word in a range name | Cardigan Bay Platform Trainers | cardigan | cardigan | generic |
| PLT-DA64602 | Platform Trainers | 6 incidental word in a range name | Boot Hill Platform Trainers | boot | boot | generic |
| PLT-DA64700 | Platform Trainers | 7 invented brand holding a color or category word | Yellow Wagtail Platform Trainers | yellow | yellow platform trainers | generic |
| PLT-DA64701 | Platform Trainers | 7 invented brand holding a color or category word | Blue Otter Platform Trainers | blue | blue platform trainers | generic |
| PLT-DA64702 | Platform Trainers | 7 invented brand holding a color or category word | Red Plover Platform Trainers | red | red platform trainers | generic |
| PLT-DA65100 | Mules | 1 color names a part | Mules with Yellow Sole | yellow | yellow mules | generic |
| PLT-DA65101 | Mules | 1 color names a part | Mules with Black Sole | black | black mules | generic |
| PLT-DA65102 | Mules | 1 color names a part | Mules with Green Sole | green | green mules | generic |
| PLT-DA65200 | Mules | 2 another category's noun as a modifier | Green Loafer Mules | loafer | loafer | generic |
| PLT-DA65201 | Mules | 2 another category's noun as a modifier | Pink Sandal Mules | sandal | sandal | generic |
| PLT-DA65202 | Mules | 2 another category's noun as a modifier | Black Loafer Mules | loafer | loafer | generic |
| PLT-DA65300 | Mules | 3 audience word of a sibling version | Black Mens-Style Mules | mens | mens mules | generic |
| PLT-DA65301 | Mules | 3 audience word of a sibling version | Pink Mens Fit Mules | mens | mens mules | generic |
| PLT-DA65302 | Mules | 3 audience word of a sibling version | Green Mens-Style Mules | mens | mens mules | generic |
| PLT-DA65400 | Mules | 4 material or feature named but absent | Brown Cashmere-Feel Mules | cashmere | cashmere mules | special: material claim |
| PLT-DA65401 | Mules | 4 material or feature named but absent | Red Suede-Look Mules | suede | suede mules | special: material claim |
| PLT-DA65402 | Mules | 4 material or feature named but absent | Pink Wool-Free Mules | wool | wool mules | special: material claim |
| PLT-DA65500 | Mules | 5 shade spelled in the description only | Moonbeam Mules | ivory | ivory mules | generic |
| PLT-DA65501 | Mules | 5 shade spelled in the description only | Driftwood Mules | taupe | taupe mules | generic |
| PLT-DA65502 | Mules | 5 shade spelled in the description only | Dune Mules | beige | beige mules | generic |
| PLT-DA65600 | Mules | 6 incidental word in a range name | Shirt Row Mules | shirt | shirt | generic |
| PLT-DA65601 | Mules | 6 incidental word in a range name | Coat Hook Mules | coat | coat | generic |
| PLT-DA65602 | Mules | 6 incidental word in a range name | Sandal Wood Mules | sandal | sandal | generic |
| PLT-DA65700 | Mules | 7 invented brand holding a color or category word | Black Lapwing Mules | black | black mules | generic |
| PLT-DA65701 | Mules | 7 invented brand holding a color or category word | Coat Crake Mules | coat | coat mules | generic |
| PLT-DA65702 | Mules | 7 invented brand holding a color or category word | Green Stoat Mules | green | green mules | generic |
| PLT-DA66100 | Jelly Shoes | 1 color names a part | Jelly Shoes with White Sole | white | white jelly shoes | generic |
| PLT-DA66101 | Jelly Shoes | 1 color names a part | Jelly Shoes with Green Sole | green | green jelly shoes | generic |
| PLT-DA66102 | Jelly Shoes | 1 color names a part | Jelly Shoes with Yellow Sole | yellow | yellow jelly shoes | generic |
| PLT-DA66200 | Jelly Shoes | 2 another category's noun as a modifier | Navy Mary Jane Jelly Shoes | mary jane | mary jane | generic |
| PLT-DA66201 | Jelly Shoes | 2 another category's noun as a modifier | Pink Mary Jane Jelly Shoes | mary jane | mary jane | generic |
| PLT-DA66202 | Jelly Shoes | 2 another category's noun as a modifier | Cream Mary Jane Jelly Shoes | mary jane | mary jane | generic |
| PLT-DA66300 | Jelly Shoes | 3 audience word of a sibling version | Cream Mini-Me Womens Jelly Shoes | womens | womens jelly shoes | generic |
| PLT-DA66301 | Jelly Shoes | 3 audience word of a sibling version | White Boys Fit Jelly Shoes | boys | boys jelly shoes | generic |
| PLT-DA66302 | Jelly Shoes | 3 audience word of a sibling version | Red Mens Fit Jelly Shoes | mens | mens jelly shoes | generic |
| PLT-DA66400 | Jelly Shoes | 4 material or feature named but absent | Blue Leather-Look Jelly Shoes | leather | leather jelly shoes | special: material claim |
| PLT-DA66401 | Jelly Shoes | 4 material or feature named but absent | Pink Suede-Look Jelly Shoes | suede | suede jelly shoes | special: material claim |
| PLT-DA66402 | Jelly Shoes | 4 material or feature named but absent | Black Cashmere-Feel Jelly Shoes | cashmere | cashmere jelly shoes | special: material claim |
| PLT-DA66500 | Jelly Shoes | 5 shade spelled in the description only | Moonbeam Jelly Shoes | ivory | ivory jelly shoes | generic |
| PLT-DA66501 | Jelly Shoes | 5 shade spelled in the description only | Driftwood Jelly Shoes | taupe | taupe jelly shoes | generic |
| PLT-DA66502 | Jelly Shoes | 5 shade spelled in the description only | Dune Jelly Shoes | beige | beige jelly shoes | generic |
| PLT-DA66600 | Jelly Shoes | 6 incidental word in a range name | Boot Hill Jelly Shoes | boot | boot | generic |
| PLT-DA66601 | Jelly Shoes | 6 incidental word in a range name | Sandal Wood Jelly Shoes | sandal | sandal | generic |
| PLT-DA66602 | Jelly Shoes | 6 incidental word in a range name | Jacket Quay Jelly Shoes | jacket | jacket | generic |
| PLT-DA66700 | Jelly Shoes | 7 invented brand holding a color or category word | Red Plover Jelly Shoes | red | red jelly shoes | generic |
| PLT-DA66701 | Jelly Shoes | 7 invented brand holding a color or category word | Coat Crake Jelly Shoes | coat | coat jelly shoes | generic |
| PLT-DA66702 | Jelly Shoes | 7 invented brand holding a color or category word | Black Lapwing Jelly Shoes | black | black jelly shoes | generic |
| PLT-DA67100 | Barefoot Shoes | 1 color names a part | Barefoot Shoes with Blue Sole | blue | blue barefoot shoes | generic |
| PLT-DA67101 | Barefoot Shoes | 1 color names a part | Barefoot Shoes with Blue Sole | blue | blue barefoot shoes | generic |
| PLT-DA67102 | Barefoot Shoes | 1 color names a part | Barefoot Shoes with Red Sole | red | red barefoot shoes | generic |
| PLT-DA67200 | Barefoot Shoes | 2 another category's noun as a modifier | Cream Sandal Barefoot Shoes | sandal | sandal | generic |
| PLT-DA67201 | Barefoot Shoes | 2 another category's noun as a modifier | Blue Sandal Barefoot Shoes | sandal | sandal | generic |
| PLT-DA67202 | Barefoot Shoes | 2 another category's noun as a modifier | Red Sandal Barefoot Shoes | sandal | sandal | generic |
| PLT-DA67300 | Barefoot Shoes | 3 audience word of a sibling version | White Mini-Me Mens Barefoot Shoes | mens | mens barefoot shoes | generic |
| PLT-DA67301 | Barefoot Shoes | 3 audience word of a sibling version | Grey Girls Fit Barefoot Shoes | girls | girls barefoot shoes | generic |
| PLT-DA67302 | Barefoot Shoes | 3 audience word of a sibling version | Grey Boys Fit Barefoot Shoes | boys | boys barefoot shoes | generic |
| PLT-DA67400 | Barefoot Shoes | 4 material or feature named but absent | Pink Leather-Look Barefoot Shoes | leather | leather barefoot shoes | special: material claim |
| PLT-DA67401 | Barefoot Shoes | 4 material or feature named but absent | Blue Suede-Look Barefoot Shoes | suede | suede barefoot shoes | special: material claim |
| PLT-DA67402 | Barefoot Shoes | 4 material or feature named but absent | Red Cashmere-Feel Barefoot Shoes | cashmere | cashmere barefoot shoes | special: material claim |
| PLT-DA67500 | Barefoot Shoes | 5 shade spelled in the description only | Moonbeam Barefoot Shoes | ivory | ivory barefoot shoes | generic |
| PLT-DA67501 | Barefoot Shoes | 5 shade spelled in the description only | Driftwood Barefoot Shoes | taupe | taupe barefoot shoes | generic |
| PLT-DA67502 | Barefoot Shoes | 5 shade spelled in the description only | Dune Barefoot Shoes | beige | beige barefoot shoes | generic |
| PLT-DA67600 | Barefoot Shoes | 6 incidental word in a range name | Shirt Row Barefoot Shoes | shirt | shirt | generic |
| PLT-DA67601 | Barefoot Shoes | 6 incidental word in a range name | Blazer Court Barefoot Shoes | blazer | blazer | generic |
| PLT-DA67602 | Barefoot Shoes | 6 incidental word in a range name | Cardigan Bay Barefoot Shoes | cardigan | cardigan | generic |
| PLT-DA67700 | Barefoot Shoes | 7 invented brand holding a color or category word | White Dormouse Barefoot Shoes | white | white barefoot shoes | generic |
| PLT-DA67701 | Barefoot Shoes | 7 invented brand holding a color or category word | White Dormouse Barefoot Shoes | white | white barefoot shoes | generic |
| PLT-DA67702 | Barefoot Shoes | 7 invented brand holding a color or category word | Yellow Wagtail Barefoot Shoes | yellow | yellow barefoot shoes | generic |
| PLT-DSKNITTED_TOP100 | Knitted Top | 1 color names a part | Knitted Top with White Hem | white | white knitted top | generic |
| PLT-DSKNITTED_TOP101 | Knitted Top | 1 color names a part | Knitted Top with Red Hem | red | red knitted top | generic |
| PLT-DSKNITTED_TOP102 | Knitted Top | 1 color names a part | Knitted Top with Yellow Hem | yellow | yellow knitted top | generic |
| PLT-DSKNITTED_TOP200 | Knitted Top | 2 another category's noun as a modifier | Brown Knitted Tunic Top | tunic | tunic | generic |
| PLT-DSKNITTED_TOP201 | Knitted Top | 2 another category's noun as a modifier | Brown Knitted Cami Top | cami | cami | generic |
| PLT-DSKNITTED_TOP202 | Knitted Top | 2 another category's noun as a modifier | Black Knitted Polo Top | polo | polo | generic |
| PLT-DSKNITTED_TOP300 | Knitted Top | 3 audience word of a sibling version | Brown Womens Fit Knitted Top | womens | womens knitted top | generic |
| PLT-DSKNITTED_TOP301 | Knitted Top | 3 audience word of a sibling version | Cream Girls Fit Knitted Top | girls | girls knitted top | generic |
| PLT-DSKNITTED_TOP302 | Knitted Top | 3 audience word of a sibling version | Pink Girls Fit Knitted Top | girls | girls knitted top | generic |
| PLT-DSKNITTED_TOP400 | Knitted Top | 4 material or feature named but absent | Cream Leather-Look Knitted Top | leather | leather knitted top | special: material claim |
| PLT-DSKNITTED_TOP401 | Knitted Top | 4 material or feature named but absent | Green Suede-Look Knitted Top | suede | suede knitted top | special: material claim |
| PLT-DSKNITTED_TOP402 | Knitted Top | 4 material or feature named but absent | White Cashmere-Feel Knitted Top | cashmere | cashmere knitted top | special: material claim |
| PLT-DSKNITTED_TOP500 | Knitted Top | 5 shade spelled in the description only | Moonbeam Knitted Top | ivory | ivory knitted top | generic |
| PLT-DSKNITTED_TOP501 | Knitted Top | 5 shade spelled in the description only | Driftwood Knitted Top | taupe | taupe knitted top | generic |
| PLT-DSKNITTED_TOP502 | Knitted Top | 5 shade spelled in the description only | Dune Knitted Top | beige | beige knitted top | generic |
| PLT-DSKNITTED_TOP600 | Knitted Top | 6 incidental word in a range name | Cardigan Bay Knitted Top | cardigan | cardigan | generic |
| PLT-DSKNITTED_TOP601 | Knitted Top | 6 incidental word in a range name | Jacket Quay Knitted Top | jacket | jacket | generic |
| PLT-DSKNITTED_TOP602 | Knitted Top | 6 incidental word in a range name | Slip Road Knitted Top | slip | slip | generic |
| PLT-DSKNITTED_TOP700 | Knitted Top | 7 invented brand holding a color or category word | Coat Crake Knitted Top | coat | coat knitted top | generic |
| PLT-DSKNITTED_TOP701 | Knitted Top | 7 invented brand holding a color or category word | Green Stoat Knitted Top | green | green knitted top | generic |
| PLT-DSKNITTED_TOP702 | Knitted Top | 7 invented brand holding a color or category word | Black Lapwing Knitted Top | black | black knitted top | generic |

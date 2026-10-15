# Text-match decoys on every clothing, footwear and lingerie type (gen#311)

`prototypes/retail_drawings/decoy_apparel.py` plants, on every product type of the Womens, Mens and
Kids clothing, footwear and lingerie, products whose words mislead a plain text search while their
structured fields tell the truth (gen#294's rule; `decoy_rows.py` holds the demo-query rows). A
decoy is a clone of one real style of its type in one main color. The color, category and audience
policies read the fields and drop it. The classes: 1 a color word names a trim or strap; 2 another
category's noun is a modifier; 3 an audience word of a sibling version; 4 a material or feature
named but absent; 5 the shade is in the description only; 6 a short range name holds a color word
(or a category word); 7 an invented brand holds a color or category word.

Each type holds at least three decoys per class (nine and twelve for bras and jeans, so a type
holds a tenth of its size), one more of class 6 on a category word, and one class 7 decoy per brand.
Classes 6 and 7 have titles of five words or fewer. The Policy column is `generic` where the
color, category or audience policy separates the decoy, and `special: <name>` where it needs its own
(a material claim: no field says the product is not leather). The exempt types are in
`decoy_apparel.EXEMPT`. The table is generated
(`python3 prototypes/retail_drawings/decoy_apparel.py`) and
`tests/test_retail_apparel_decoys_311.py` holds it verbatim.

| Product id | Type | Class | Title | Word | Query | Policy |
|---|---|---|---|---|---|---|
| PLT-DA00100 | Blouse | 1 color names a part | Grey Blouse, Red Collar | red | red blouse | generic |
| PLT-DA00101 | Blouse | 1 color names a part | Pink Blouse, Red Buttons | red | red blouse | generic |
| PLT-DA00102 | Blouse | 1 color names a part | Cream Blouse, Blue Buttons | blue | blue blouse | generic |
| PLT-DA00200 | Blouse | 2 another category's noun as a modifier | Brown Trouser Blouse | trouser | trouser | generic |
| PLT-DA00201 | Blouse | 2 another category's noun as a modifier | Brown Tunic Blouse | tunic | tunic | generic |
| PLT-DA00202 | Blouse | 2 another category's noun as a modifier | Navy Tunic Blouse | tunic | tunic | generic |
| PLT-DA00300 | Blouse | 3 audience word of a sibling version | Green Mens-Style Blouse | mens | mens blouse | generic |
| PLT-DA00301 | Blouse | 3 audience word of a sibling version | Brown Boys Fit Blouse | boys | boys blouse | generic |
| PLT-DA00302 | Blouse | 3 audience word of a sibling version | Navy Mens Fit Blouse | mens | mens blouse | generic |
| PLT-DA00400 | Blouse | 4 material or feature named but absent | Black Leather-Look Blouse | leather | leather blouse | special: material claim |
| PLT-DA00401 | Blouse | 4 material or feature named but absent | Blue Suede-Look Blouse | suede | suede blouse | special: material claim |
| PLT-DA00402 | Blouse | 4 material or feature named but absent | Brown Cashmere-Feel Blouse | cashmere | cashmere blouse | special: material claim |
| PLT-DA00500 | Blouse | 5 shade spelled in the description only | Moonbeam Blouse | ivory | ivory blouse | generic |
| PLT-DA00501 | Blouse | 5 shade spelled in the description only | Driftwood Blouse | taupe | taupe blouse | generic |
| PLT-DA00502 | Blouse | 5 shade spelled in the description only | Dune Blouse | beige | beige blouse | generic |
| PLT-DA00600 | Blouse | 6 incidental word in a range name | Green Park Blouse | green | green blouse | generic |
| PLT-DA00601 | Blouse | 6 incidental word in a range name | Black Tor Blouse | black | black blouse | generic |
| PLT-DA00602 | Blouse | 6 incidental word in a range name | Yellow Marsh Blouse | yellow | yellow blouse | generic |
| PLT-DA00603 | Blouse | 6 incidental word in a range name | Skirt Point Blouse | skirt | skirt | generic |
| PLT-DA00700 | Blouse | 7 invented brand holding a color or category word | Blue Otter Blouse | blue | blue blouse | generic |
| PLT-DA00701 | Blouse | 7 invented brand holding a color or category word | White Dormouse Blouse | white | white blouse | generic |
| PLT-DA00702 | Blouse | 7 invented brand holding a color or category word | Green Stoat Blouse | green | green blouse | generic |
| PLT-DA01100 | Bodysuit | 1 color names a part | Pink Bodysuit, Yellow Lining | yellow | yellow bodysuit | generic |
| PLT-DA01101 | Bodysuit | 1 color names a part | Cream Bodysuit, Red Stitching | red | red bodysuit | generic |
| PLT-DA01102 | Bodysuit | 1 color names a part | Red Bodysuit, Yellow Collar | yellow | yellow bodysuit | generic |
| PLT-DA01200 | Bodysuit | 2 another category's noun as a modifier | Pink Gilet Bodysuit | gilet | gilet | generic |
| PLT-DA01201 | Bodysuit | 2 another category's noun as a modifier | Black Vest Bodysuit | vest | vest | generic |
| PLT-DA01202 | Bodysuit | 2 another category's noun as a modifier | Black Skirt Bodysuit | skirt | skirt | generic |
| PLT-DA01300 | Bodysuit | 3 audience word of a sibling version | Blue Mens Fit Bodysuit | mens | mens bodysuit | generic |
| PLT-DA01301 | Bodysuit | 3 audience word of a sibling version | Black Boys Fit Bodysuit | boys | boys bodysuit | generic |
| PLT-DA01302 | Bodysuit | 3 audience word of a sibling version | Brown Boys Fit Bodysuit | boys | boys bodysuit | generic |
| PLT-DA01400 | Bodysuit | 4 material or feature named but absent | Brown Leather-Look Bodysuit | leather | leather bodysuit | special: material claim |
| PLT-DA01401 | Bodysuit | 4 material or feature named but absent | Brown Suede-Look Bodysuit | suede | suede bodysuit | special: material claim |
| PLT-DA01402 | Bodysuit | 4 material or feature named but absent | Green Cashmere-Feel Bodysuit | cashmere | cashmere bodysuit | special: material claim |
| PLT-DA01500 | Bodysuit | 5 shade spelled in the description only | Moonbeam Bodysuit | ivory | ivory bodysuit | generic |
| PLT-DA01501 | Bodysuit | 5 shade spelled in the description only | Driftwood Bodysuit | taupe | taupe bodysuit | generic |
| PLT-DA01502 | Bodysuit | 5 shade spelled in the description only | Dune Bodysuit | beige | beige bodysuit | generic |
| PLT-DA01600 | Bodysuit | 6 incidental word in a range name | Green Park Bodysuit | green | green bodysuit | generic |
| PLT-DA01601 | Bodysuit | 6 incidental word in a range name | Yellow Marsh Bodysuit | yellow | yellow bodysuit | generic |
| PLT-DA01602 | Bodysuit | 6 incidental word in a range name | Black Mill Bodysuit | black | black bodysuit | generic |
| PLT-DA01603 | Bodysuit | 6 incidental word in a range name | Shirt Row Bodysuit | shirt | shirt | generic |
| PLT-DA01700 | Bodysuit | 7 invented brand holding a color or category word | Coat Crake Bodysuit | coat | coat bodysuit | generic |
| PLT-DA01701 | Bodysuit | 7 invented brand holding a color or category word | Green Stoat Bodysuit | green | green bodysuit | generic |
| PLT-DA01702 | Bodysuit | 7 invented brand holding a color or category word | Black Lapwing Bodysuit | black | black bodysuit | generic |
| PLT-DA02100 | Bomber Jacket | 1 color names a part | Green Bomber Jacket, Red Collar | red | red bomber jacket | generic |
| PLT-DA02101 | Bomber Jacket | 1 color names a part | Red Bomber Jacket, Green Zip | green | green bomber jacket | generic |
| PLT-DA02102 | Bomber Jacket | 1 color names a part | Brown Bomber Jacket, Blue Trim | blue | blue bomber jacket | generic |
| PLT-DA02200 | Bomber Jacket | 2 another category's noun as a modifier | Cream Cardigan Bomber Jacket | cardigan | cardigan | generic |
| PLT-DA02201 | Bomber Jacket | 2 another category's noun as a modifier | Grey Jumper Bomber Jacket | jumper | jumper | generic |
| PLT-DA02202 | Bomber Jacket | 2 another category's noun as a modifier | Pink Dress Bomber Jacket | dress | dress | generic |
| PLT-DA02300 | Bomber Jacket | 3 audience word of a sibling version | Grey Mini-Me Mens Bomber Jacket | mens | mens bomber jacket | generic |
| PLT-DA02301 | Bomber Jacket | 3 audience word of a sibling version | Brown Mini-Me Mens Bomber Jacket | mens | mens bomber jacket | generic |
| PLT-DA02302 | Bomber Jacket | 3 audience word of a sibling version | Grey Mens Fit Bomber Jacket | mens | mens bomber jacket | generic |
| PLT-DA02400 | Bomber Jacket | 4 material or feature named but absent | Black Leather-Look Bomber Jacket | leather | leather bomber jacket | special: material claim |
| PLT-DA02401 | Bomber Jacket | 4 material or feature named but absent | White Suede-Look Bomber Jacket | suede | suede bomber jacket | special: material claim |
| PLT-DA02402 | Bomber Jacket | 4 material or feature named but absent | Grey Cashmere-Feel Bomber Jacket | cashmere | cashmere bomber jacket | special: material claim |
| PLT-DA02500 | Bomber Jacket | 5 shade spelled in the description only | Moonbeam Bomber Jacket | ivory | ivory bomber jacket | generic |
| PLT-DA02501 | Bomber Jacket | 5 shade spelled in the description only | Driftwood Bomber Jacket | taupe | taupe bomber jacket | generic |
| PLT-DA02502 | Bomber Jacket | 5 shade spelled in the description only | Dune Bomber Jacket | beige | beige bomber jacket | generic |
| PLT-DA02600 | Bomber Jacket | 6 incidental word in a range name | Red Harbour Bomber Jacket | red | red bomber jacket | generic |
| PLT-DA02601 | Bomber Jacket | 6 incidental word in a range name | Black Mill Bomber Jacket | black | black bomber jacket | generic |
| PLT-DA02602 | Bomber Jacket | 6 incidental word in a range name | Blue Meadow Bomber Jacket | blue | blue bomber jacket | generic |
| PLT-DA02603 | Bomber Jacket | 6 incidental word in a range name | Jumper Lane Bomber Jacket | jumper | jumper | generic |
| PLT-DA02700 | Bomber Jacket | 7 invented brand holding a color or category word | White Dormouse Bomber Jacket | white | white bomber jacket | generic |
| PLT-DA02701 | Bomber Jacket | 7 invented brand holding a color or category word | Yellow Wagtail Bomber Jacket | yellow | yellow bomber jacket | generic |
| PLT-DA02702 | Bomber Jacket | 7 invented brand holding a color or category word | Red Plover Bomber Jacket | red | red bomber jacket | generic |
| PLT-DA03100 | Cardigan | 1 color names a part | Grey Cardigan, Yellow Stripes | yellow | yellow cardigan | generic |
| PLT-DA03101 | Cardigan | 1 color names a part | Green Cardigan, White Trim | white | white cardigan | generic |
| PLT-DA03102 | Cardigan | 1 color names a part | Red Cardigan, Yellow Trim | yellow | yellow cardigan | generic |
| PLT-DA03200 | Cardigan | 2 another category's noun as a modifier | Navy Poncho Cardigan | poncho | poncho | generic |
| PLT-DA03201 | Cardigan | 2 another category's noun as a modifier | Blue Skirt Cardigan | skirt | skirt | generic |
| PLT-DA03202 | Cardigan | 2 another category's noun as a modifier | White Shirt Cardigan | shirt | shirt | generic |
| PLT-DA03300 | Cardigan | 3 audience word of a sibling version | Red Boys Fit Cardigan | boys | boys cardigan | generic |
| PLT-DA03301 | Cardigan | 3 audience word of a sibling version | Brown Mens Fit Cardigan | mens | mens cardigan | generic |
| PLT-DA03302 | Cardigan | 3 audience word of a sibling version | White Boys Fit Cardigan | boys | boys cardigan | generic |
| PLT-DA03400 | Cardigan | 4 material or feature named but absent | Pink Leather-Look Cardigan | leather | leather cardigan | special: material claim |
| PLT-DA03401 | Cardigan | 4 material or feature named but absent | Blue Suede-Look Cardigan | suede | suede cardigan | special: material claim |
| PLT-DA03402 | Cardigan | 4 material or feature named but absent | Black Cashmere-Feel Cardigan | cashmere | cashmere cardigan | special: material claim |
| PLT-DA03500 | Cardigan | 5 shade spelled in the description only | Moonbeam Cardigan | ivory | ivory cardigan | generic |
| PLT-DA03501 | Cardigan | 5 shade spelled in the description only | Driftwood Cardigan | taupe | taupe cardigan | generic |
| PLT-DA03502 | Cardigan | 5 shade spelled in the description only | Dune Cardigan | beige | beige cardigan | generic |
| PLT-DA03600 | Cardigan | 6 incidental word in a range name | Green Park Cardigan | green | green cardigan | generic |
| PLT-DA03601 | Cardigan | 6 incidental word in a range name | White Moor Cardigan | white | white cardigan | generic |
| PLT-DA03602 | Cardigan | 6 incidental word in a range name | Red Harbour Cardigan | red | red cardigan | generic |
| PLT-DA03603 | Cardigan | 6 incidental word in a range name | Skirt Point Cardigan | skirt | skirt | generic |
| PLT-DA03700 | Cardigan | 7 invented brand holding a color or category word | Red Plover Cardigan | red | red cardigan | generic |
| PLT-DA03701 | Cardigan | 7 invented brand holding a color or category word | Blue Otter Cardigan | blue | blue cardigan | generic |
| PLT-DA03702 | Cardigan | 7 invented brand holding a color or category word | Yellow Wagtail Cardigan | yellow | yellow cardigan | generic |
| PLT-DA04100 | Coat | 1 color names a part | Brown Coat, Blue Buttons | blue | blue coat | generic |
| PLT-DA04101 | Coat | 1 color names a part | Brown Coat, White Stripes | white | white coat | generic |
| PLT-DA04102 | Coat | 1 color names a part | Blue Coat, White Cuffs | white | white coat | generic |
| PLT-DA04200 | Coat | 2 another category's noun as a modifier | Grey Blazer Coat | blazer | blazer | generic |
| PLT-DA04201 | Coat | 2 another category's noun as a modifier | Green Tunic Coat | tunic | tunic | generic |
| PLT-DA04202 | Coat | 2 another category's noun as a modifier | Brown Tunic Coat | tunic | tunic | generic |
| PLT-DA04300 | Coat | 3 audience word of a sibling version | Pink Mens-Style Coat | mens | mens coat | generic |
| PLT-DA04301 | Coat | 3 audience word of a sibling version | White Boys Fit Coat | boys | boys coat | generic |
| PLT-DA04302 | Coat | 3 audience word of a sibling version | Black Mens Fit Coat | mens | mens coat | generic |
| PLT-DA04400 | Coat | 4 material or feature named but absent | Pink Leather-Look Coat | leather | leather coat | special: material claim |
| PLT-DA04401 | Coat | 4 material or feature named but absent | Blue Suede-Look Coat | suede | suede coat | special: material claim |
| PLT-DA04402 | Coat | 4 material or feature named but absent | Green Cashmere-Feel Coat | cashmere | cashmere coat | special: material claim |
| PLT-DA04500 | Coat | 5 shade spelled in the description only | Moonbeam Coat | ivory | ivory coat | generic |
| PLT-DA04501 | Coat | 5 shade spelled in the description only | Driftwood Coat | taupe | taupe coat | generic |
| PLT-DA04502 | Coat | 5 shade spelled in the description only | Dune Coat | beige | beige coat | generic |
| PLT-DA04600 | Coat | 6 incidental word in a range name | Green Park Coat | green | green coat | generic |
| PLT-DA04601 | Coat | 6 incidental word in a range name | Blue Meadow Coat | blue | blue coat | generic |
| PLT-DA04602 | Coat | 6 incidental word in a range name | Black Mill Coat | black | black coat | generic |
| PLT-DA04603 | Coat | 6 incidental word in a range name | Skirt Point Coat | skirt | skirt | generic |
| PLT-DA04700 | Coat | 7 invented brand holding a color or category word | Green Stoat Coat | green | green coat | generic |
| PLT-DA04701 | Coat | 7 invented brand holding a color or category word | Yellow Wagtail Coat | yellow | yellow coat | generic |
| PLT-DA04702 | Coat | 7 invented brand holding a color or category word | Red Plover Coat | red | red coat | generic |
| PLT-DA05100 | Co-ord Set | 1 color names a part | Navy Co-ord Set, Black Trim | black | black co-ord set | generic |
| PLT-DA05101 | Co-ord Set | 1 color names a part | Grey Co-ord Set, White Lining | white | white co-ord set | generic |
| PLT-DA05102 | Co-ord Set | 1 color names a part | Navy Co-ord Set, Green Stitching | green | green co-ord set | generic |
| PLT-DA05200 | Co-ord Set | 2 another category's noun as a modifier | Pink Shirt Co-ord Set | shirt | shirt | generic |
| PLT-DA05201 | Co-ord Set | 2 another category's noun as a modifier | Brown Poncho Co-ord Set | poncho | poncho | generic |
| PLT-DA05202 | Co-ord Set | 2 another category's noun as a modifier | Brown Tunic Co-ord Set | tunic | tunic | generic |
| PLT-DA05300 | Co-ord Set | 3 audience word of a sibling version | Navy Mens-Style Co-ord Set | mens | mens co-ord set | generic |
| PLT-DA05301 | Co-ord Set | 3 audience word of a sibling version | White Mens-Style Co-ord Set | mens | mens co-ord set | generic |
| PLT-DA05302 | Co-ord Set | 3 audience word of a sibling version | White Boys Fit Co-ord Set | boys | boys co-ord set | generic |
| PLT-DA05400 | Co-ord Set | 4 material or feature named but absent | Brown Leather-Look Co-ord Set | leather | leather co-ord set | special: material claim |
| PLT-DA05401 | Co-ord Set | 4 material or feature named but absent | White Suede-Look Co-ord Set | suede | suede co-ord set | special: material claim |
| PLT-DA05402 | Co-ord Set | 4 material or feature named but absent | Pink Cashmere-Feel Co-ord Set | cashmere | cashmere co-ord set | special: material claim |
| PLT-DA05500 | Co-ord Set | 5 shade spelled in the description only | Moonbeam Co-ord Set | ivory | ivory co-ord set | generic |
| PLT-DA05501 | Co-ord Set | 5 shade spelled in the description only | Driftwood Co-ord Set | taupe | taupe co-ord set | generic |
| PLT-DA05502 | Co-ord Set | 5 shade spelled in the description only | Dune Co-ord Set | beige | beige co-ord set | generic |
| PLT-DA05600 | Co-ord Set | 6 incidental word in a range name | Black Tor Co-ord Set | black | black co-ord set | generic |
| PLT-DA05601 | Co-ord Set | 6 incidental word in a range name | Red Fern Co-ord Set | red | red co-ord set | generic |
| PLT-DA05602 | Co-ord Set | 6 incidental word in a range name | White Moor Co-ord Set | white | white co-ord set | generic |
| PLT-DA05603 | Co-ord Set | 6 incidental word in a range name | Jumper Lane Co-ord Set | jumper | jumper | generic |
| PLT-DA05700 | Co-ord Set | 7 invented brand holding a color or category word | Blue Otter Co-ord Set | blue | blue co-ord set | generic |
| PLT-DA05701 | Co-ord Set | 7 invented brand holding a color or category word | Yellow Wagtail Co-ord Set | yellow | yellow co-ord set | generic |
| PLT-DA05702 | Co-ord Set | 7 invented brand holding a color or category word | White Dormouse Co-ord Set | white | white co-ord set | generic |
| PLT-DA06100 | Cycling Shorts | 1 color names a part | Green Cycling Shorts, Yellow Buttons | yellow | yellow cycling shorts | generic |
| PLT-DA06101 | Cycling Shorts | 1 color names a part | Brown Cycling Shorts, Black Lining | black | black cycling shorts | generic |
| PLT-DA06102 | Cycling Shorts | 1 color names a part | Pink Cycling Shorts, Black Buttons | black | black cycling shorts | generic |
| PLT-DA06200 | Cycling Shorts | 2 another category's noun as a modifier | White Tunic Cycling Shorts | tunic | tunic | generic |
| PLT-DA06201 | Cycling Shorts | 2 another category's noun as a modifier | Brown Blazer Cycling Shorts | blazer | blazer | generic |
| PLT-DA06202 | Cycling Shorts | 2 another category's noun as a modifier | Green Jumper Cycling Shorts | jumper | jumper | generic |
| PLT-DA06300 | Cycling Shorts | 3 audience word of a sibling version | Pink Girls Fit Cycling Shorts | girls | girls cycling shorts | generic |
| PLT-DA06301 | Cycling Shorts | 3 audience word of a sibling version | Grey Girls Fit Cycling Shorts | girls | girls cycling shorts | generic |
| PLT-DA06302 | Cycling Shorts | 3 audience word of a sibling version | Navy Girls Fit Cycling Shorts | girls | girls cycling shorts | generic |
| PLT-DA06400 | Cycling Shorts | 4 material or feature named but absent | Navy Leather-Look Cycling Shorts | leather | leather cycling shorts | special: material claim |
| PLT-DA06401 | Cycling Shorts | 4 material or feature named but absent | Blue Suede-Look Cycling Shorts | suede | suede cycling shorts | special: material claim |
| PLT-DA06402 | Cycling Shorts | 4 material or feature named but absent | White Cashmere-Feel Cycling Shorts | cashmere | cashmere cycling shorts | special: material claim |
| PLT-DA06500 | Cycling Shorts | 5 shade spelled in the description only | Moonbeam Cycling Shorts | ivory | ivory cycling shorts | generic |
| PLT-DA06501 | Cycling Shorts | 5 shade spelled in the description only | Driftwood Cycling Shorts | taupe | taupe cycling shorts | generic |
| PLT-DA06502 | Cycling Shorts | 5 shade spelled in the description only | Dune Cycling Shorts | beige | beige cycling shorts | generic |
| PLT-DA06600 | Cycling Shorts | 6 incidental word in a range name | Blue Cove Cycling Shorts | blue | blue cycling shorts | generic |
| PLT-DA06601 | Cycling Shorts | 6 incidental word in a range name | Green Park Cycling Shorts | green | green cycling shorts | generic |
| PLT-DA06602 | Cycling Shorts | 6 incidental word in a range name | Black Tor Cycling Shorts | black | black cycling shorts | generic |
| PLT-DA06603 | Cycling Shorts | 6 incidental word in a range name | Shirt Row Cycling Shorts | shirt | shirt | generic |
| PLT-DA06700 | Cycling Shorts | 7 invented brand holding a color or category word | Red Plover Cycling Shorts | red | red cycling shorts | generic |
| PLT-DA06701 | Cycling Shorts | 7 invented brand holding a color or category word | Yellow Wagtail Cycling Shorts | yellow | yellow cycling shorts | generic |
| PLT-DA06702 | Cycling Shorts | 7 invented brand holding a color or category word | Coat Crake Cycling Shorts | coat | coat cycling shorts | generic |
| PLT-DA07100 | Denim Jacket | 1 color names a part | Pink Denim Jacket, Red Piping | red | red denim jacket | generic |
| PLT-DA07101 | Denim Jacket | 1 color names a part | Brown Denim Jacket, White Collar | white | white denim jacket | generic |
| PLT-DA07102 | Denim Jacket | 1 color names a part | Pink Denim Jacket, Yellow Lining | yellow | yellow denim jacket | generic |
| PLT-DA07200 | Denim Jacket | 2 another category's noun as a modifier | Red Vest Denim Jacket | vest | vest | generic |
| PLT-DA07201 | Denim Jacket | 2 another category's noun as a modifier | Blue Blazer Denim Jacket | blazer | blazer | generic |
| PLT-DA07202 | Denim Jacket | 2 another category's noun as a modifier | Cream Hoodie Denim Jacket | hoodie | hoodie | generic |
| PLT-DA07300 | Denim Jacket | 3 audience word of a sibling version | Navy Mens-Style Denim Jacket | mens | mens denim jacket | generic |
| PLT-DA07301 | Denim Jacket | 3 audience word of a sibling version | Pink Mens Fit Denim Jacket | mens | mens denim jacket | generic |
| PLT-DA07302 | Denim Jacket | 3 audience word of a sibling version | Black Mens-Style Denim Jacket | mens | mens denim jacket | generic |
| PLT-DA07400 | Denim Jacket | 4 material or feature named but absent | Green Leather-Look Denim Jacket | leather | leather denim jacket | special: material claim |
| PLT-DA07401 | Denim Jacket | 4 material or feature named but absent | Brown Suede-Look Denim Jacket | suede | suede denim jacket | special: material claim |
| PLT-DA07402 | Denim Jacket | 4 material or feature named but absent | Grey Cashmere-Feel Denim Jacket | cashmere | cashmere denim jacket | special: material claim |
| PLT-DA07500 | Denim Jacket | 5 shade spelled in the description only | Moonbeam Denim Jacket | ivory | ivory denim jacket | generic |
| PLT-DA07501 | Denim Jacket | 5 shade spelled in the description only | Driftwood Denim Jacket | taupe | taupe denim jacket | generic |
| PLT-DA07502 | Denim Jacket | 5 shade spelled in the description only | Dune Denim Jacket | beige | beige denim jacket | generic |
| PLT-DA07600 | Denim Jacket | 6 incidental word in a range name | Green Hollow Denim Jacket | green | green denim jacket | generic |
| PLT-DA07601 | Denim Jacket | 6 incidental word in a range name | White Cliff Denim Jacket | white | white denim jacket | generic |
| PLT-DA07602 | Denim Jacket | 6 incidental word in a range name | Red Harbour Denim Jacket | red | red denim jacket | generic |
| PLT-DA07603 | Denim Jacket | 6 incidental word in a range name | Shirt Row Denim Jacket | shirt | shirt | generic |
| PLT-DA07700 | Denim Jacket | 7 invented brand holding a color or category word | White Dormouse Denim Jacket | white | white denim jacket | generic |
| PLT-DA07701 | Denim Jacket | 7 invented brand holding a color or category word | Red Plover Denim Jacket | red | red denim jacket | generic |
| PLT-DA07702 | Denim Jacket | 7 invented brand holding a color or category word | Jumper Jay Denim Jacket | jumper | jumper denim jacket | generic |
| PLT-DA08100 | Dress | 1 color names a part | Cream Dress, Red Buttons | red | red dress | generic |
| PLT-DA08101 | Dress | 1 color names a part | Brown Dress, White Trim | white | white dress | generic |
| PLT-DA08102 | Dress | 1 color names a part | Blue Dress, White Collar | white | white dress | generic |
| PLT-DA08200 | Dress | 2 another category's noun as a modifier | Pink Blazer Dress | blazer | blazer | generic |
| PLT-DA08201 | Dress | 2 another category's noun as a modifier | Cream Coat Dress | coat | coat | generic |
| PLT-DA08202 | Dress | 2 another category's noun as a modifier | Blue Vest Dress | vest | vest | generic |
| PLT-DA08300 | Dress | 3 audience word of a sibling version | White Boys Fit Dress | boys | boys dress | generic |
| PLT-DA08301 | Dress | 3 audience word of a sibling version | Grey Boys Fit Dress | boys | boys dress | generic |
| PLT-DA08302 | Dress | 3 audience word of a sibling version | Black Mens Fit Dress | mens | mens dress | generic |
| PLT-DA08400 | Dress | 4 material or feature named but absent | Black Leather-Look Dress | leather | leather dress | special: material claim |
| PLT-DA08401 | Dress | 4 material or feature named but absent | Grey Suede-Look Dress | suede | suede dress | special: material claim |
| PLT-DA08402 | Dress | 4 material or feature named but absent | Black Cashmere-Feel Dress | cashmere | cashmere dress | special: material claim |
| PLT-DA08500 | Dress | 5 shade spelled in the description only | Moonbeam Dress | ivory | ivory dress | generic |
| PLT-DA08501 | Dress | 5 shade spelled in the description only | Driftwood Dress | taupe | taupe dress | generic |
| PLT-DA08502 | Dress | 5 shade spelled in the description only | Dune Dress | beige | beige dress | generic |
| PLT-DA08600 | Dress | 6 incidental word in a range name | Red Harbour Dress | red | red dress | generic |
| PLT-DA08601 | Dress | 6 incidental word in a range name | White Cliff Dress | white | white dress | generic |
| PLT-DA08602 | Dress | 6 incidental word in a range name | Blue Meadow Dress | blue | blue dress | generic |
| PLT-DA08603 | Dress | 6 incidental word in a range name | Boot Hill Dress | boot | boot | generic |
| PLT-DA08700 | Dress | 7 invented brand holding a color or category word | Red Plover Dress | red | red dress | generic |
| PLT-DA08701 | Dress | 7 invented brand holding a color or category word | White Dormouse Dress | white | white dress | generic |
| PLT-DA08702 | Dress | 7 invented brand holding a color or category word | Blue Otter Dress | blue | blue dress | generic |
| PLT-DA09100 | Joggers | 1 color names a part | Green Joggers, White Trim | white | white joggers | generic |
| PLT-DA09101 | Joggers | 1 color names a part | Brown Joggers, White Pocket | white | white joggers | generic |
| PLT-DA09102 | Joggers | 1 color names a part | Red Joggers, Blue Cuffs | blue | blue joggers | generic |
| PLT-DA09200 | Joggers | 2 another category's noun as a modifier | Cream Tunic Joggers | tunic | tunic | generic |
| PLT-DA09201 | Joggers | 2 another category's noun as a modifier | Grey Blazer Joggers | blazer | blazer | generic |
| PLT-DA09202 | Joggers | 2 another category's noun as a modifier | Black Hoodie Joggers | hoodie | hoodie | generic |
| PLT-DA09300 | Joggers | 3 audience word of a sibling version | Pink Girls Fit Joggers | girls | girls joggers | generic |
| PLT-DA09301 | Joggers | 3 audience word of a sibling version | Green Mens-Style Joggers | mens | mens joggers | generic |
| PLT-DA09302 | Joggers | 3 audience word of a sibling version | Red Girls Fit Joggers | girls | girls joggers | generic |
| PLT-DA09400 | Joggers | 4 material or feature named but absent | Red Leather-Look Joggers | leather | leather joggers | special: material claim |
| PLT-DA09401 | Joggers | 4 material or feature named but absent | Blue Suede-Look Joggers | suede | suede joggers | special: material claim |
| PLT-DA09402 | Joggers | 4 material or feature named but absent | Navy Cashmere-Feel Joggers | cashmere | cashmere joggers | special: material claim |
| PLT-DA09500 | Joggers | 5 shade spelled in the description only | Moonbeam Joggers | ivory | ivory joggers | generic |
| PLT-DA09501 | Joggers | 5 shade spelled in the description only | Driftwood Joggers | taupe | taupe joggers | generic |
| PLT-DA09502 | Joggers | 5 shade spelled in the description only | Dune Joggers | beige | beige joggers | generic |
| PLT-DA09600 | Joggers | 6 incidental word in a range name | Green Park Joggers | green | green joggers | generic |
| PLT-DA09601 | Joggers | 6 incidental word in a range name | White Moor Joggers | white | white joggers | generic |
| PLT-DA09602 | Joggers | 6 incidental word in a range name | Black Tor Joggers | black | black joggers | generic |
| PLT-DA09603 | Joggers | 6 incidental word in a range name | Shirt Row Joggers | shirt | shirt | generic |
| PLT-DA09700 | Joggers | 7 invented brand holding a color or category word | Jumper Jay Joggers | jumper | jumper joggers | generic |
| PLT-DA09701 | Joggers | 7 invented brand holding a color or category word | White Dormouse Joggers | white | white joggers | generic |
| PLT-DA09702 | Joggers | 7 invented brand holding a color or category word | Coat Crake Joggers | coat | coat joggers | generic |
| PLT-DA10100 | Jumper | 1 color names a part | Black Jumper, White Piping | white | white jumper | generic |
| PLT-DA10101 | Jumper | 1 color names a part | Navy Jumper, Yellow Lining | yellow | yellow jumper | generic |
| PLT-DA10102 | Jumper | 1 color names a part | Navy Jumper, White Lining | white | white jumper | generic |
| PLT-DA10200 | Jumper | 2 another category's noun as a modifier | Navy Skirt Jumper | skirt | skirt | generic |
| PLT-DA10201 | Jumper | 2 another category's noun as a modifier | Pink Tunic Jumper | tunic | tunic | generic |
| PLT-DA10202 | Jumper | 2 another category's noun as a modifier | Cream Skirt Jumper | skirt | skirt | generic |
| PLT-DA10300 | Jumper | 3 audience word of a sibling version | Red Boys Fit Jumper | boys | boys jumper | generic |
| PLT-DA10301 | Jumper | 3 audience word of a sibling version | Cream Mens Fit Jumper | mens | mens jumper | generic |
| PLT-DA10302 | Jumper | 3 audience word of a sibling version | Pink Boys Fit Jumper | boys | boys jumper | generic |
| PLT-DA10400 | Jumper | 4 material or feature named but absent | Red Leather-Look Jumper | leather | leather jumper | special: material claim |
| PLT-DA10401 | Jumper | 4 material or feature named but absent | Green Suede-Look Jumper | suede | suede jumper | special: material claim |
| PLT-DA10402 | Jumper | 4 material or feature named but absent | White Cashmere-Feel Jumper | cashmere | cashmere jumper | special: material claim |
| PLT-DA10500 | Jumper | 5 shade spelled in the description only | Moonbeam Jumper | ivory | ivory jumper | generic |
| PLT-DA10501 | Jumper | 5 shade spelled in the description only | Driftwood Jumper | taupe | taupe jumper | generic |
| PLT-DA10502 | Jumper | 5 shade spelled in the description only | Dune Jumper | beige | beige jumper | generic |
| PLT-DA10600 | Jumper | 6 incidental word in a range name | Yellow Marsh Jumper | yellow | yellow jumper | generic |
| PLT-DA10601 | Jumper | 6 incidental word in a range name | White Moor Jumper | white | white jumper | generic |
| PLT-DA10602 | Jumper | 6 incidental word in a range name | Blue Cove Jumper | blue | blue jumper | generic |
| PLT-DA10603 | Jumper | 6 incidental word in a range name | Sock Hop Jumper | sock | sock | generic |
| PLT-DA10700 | Jumper | 7 invented brand holding a color or category word | Blue Otter Jumper | blue | blue jumper | generic |
| PLT-DA10701 | Jumper | 7 invented brand holding a color or category word | Black Lapwing Jumper | black | black jumper | generic |
| PLT-DA10702 | Jumper | 7 invented brand holding a color or category word | White Dormouse Jumper | white | white jumper | generic |
| PLT-DA11100 | Leggings | 1 color names a part | Blue Leggings, White Stitching | white | white leggings | generic |
| PLT-DA11101 | Leggings | 1 color names a part | Cream Leggings, Green Pocket | green | green leggings | generic |
| PLT-DA11102 | Leggings | 1 color names a part | Pink Leggings, Red Lining | red | red leggings | generic |
| PLT-DA11200 | Leggings | 2 another category's noun as a modifier | Green Gilet Leggings | gilet | gilet | generic |
| PLT-DA11201 | Leggings | 2 another category's noun as a modifier | Blue Hoodie Leggings | hoodie | hoodie | generic |
| PLT-DA11202 | Leggings | 2 another category's noun as a modifier | Cream Cardigan Leggings | cardigan | cardigan | generic |
| PLT-DA11300 | Leggings | 3 audience word of a sibling version | Red Boys Fit Leggings | boys | boys leggings | generic |
| PLT-DA11301 | Leggings | 3 audience word of a sibling version | Cream Mens-Style Leggings | mens | mens leggings | generic |
| PLT-DA11302 | Leggings | 3 audience word of a sibling version | Blue Boys Fit Leggings | boys | boys leggings | generic |
| PLT-DA11400 | Leggings | 4 material or feature named but absent | Blue Leather-Look Leggings | leather | leather leggings | special: material claim |
| PLT-DA11401 | Leggings | 4 material or feature named but absent | Pink Suede-Look Leggings | suede | suede leggings | special: material claim |
| PLT-DA11402 | Leggings | 4 material or feature named but absent | Cream Cashmere-Feel Leggings | cashmere | cashmere leggings | special: material claim |
| PLT-DA11500 | Leggings | 5 shade spelled in the description only | Moonbeam Leggings | ivory | ivory leggings | generic |
| PLT-DA11501 | Leggings | 5 shade spelled in the description only | Driftwood Leggings | taupe | taupe leggings | generic |
| PLT-DA11502 | Leggings | 5 shade spelled in the description only | Dune Leggings | beige | beige leggings | generic |
| PLT-DA11600 | Leggings | 6 incidental word in a range name | Blue Cove Leggings | blue | blue leggings | generic |
| PLT-DA11601 | Leggings | 6 incidental word in a range name | Black Tor Leggings | black | black leggings | generic |
| PLT-DA11602 | Leggings | 6 incidental word in a range name | Yellow Marsh Leggings | yellow | yellow leggings | generic |
| PLT-DA11603 | Leggings | 6 incidental word in a range name | Dress Circle Leggings | dress | dress | generic |
| PLT-DA11700 | Leggings | 7 invented brand holding a color or category word | Red Plover Leggings | red | red leggings | generic |
| PLT-DA11701 | Leggings | 7 invented brand holding a color or category word | Green Stoat Leggings | green | green leggings | generic |
| PLT-DA11702 | Leggings | 7 invented brand holding a color or category word | Black Lapwing Leggings | black | black leggings | generic |
| PLT-DA12100 | Outfit Set | 1 color names a part | Black Outfit Set, Green Stitching | green | green outfit set | generic |
| PLT-DA12101 | Outfit Set | 1 color names a part | Grey Outfit Set, Yellow Piping | yellow | yellow outfit set | generic |
| PLT-DA12102 | Outfit Set | 1 color names a part | Green Outfit Set, White Stripes | white | white outfit set | generic |
| PLT-DA12200 | Outfit Set | 2 another category's noun as a modifier | Navy Tunic Outfit Set | tunic | tunic | generic |
| PLT-DA12201 | Outfit Set | 2 another category's noun as a modifier | Navy Blazer Outfit Set | blazer | blazer | generic |
| PLT-DA12202 | Outfit Set | 2 another category's noun as a modifier | White Gilet Outfit Set | gilet | gilet | generic |
| PLT-DA12300 | Outfit Set | 3 audience word of a sibling version | Blue Mini-Me Mens Outfit Set | mens | mens outfit set | generic |
| PLT-DA12301 | Outfit Set | 3 audience word of a sibling version | Green Mens-Style Outfit Set | mens | mens outfit set | generic |
| PLT-DA12302 | Outfit Set | 3 audience word of a sibling version | Brown Mens-Style Outfit Set | mens | mens outfit set | generic |
| PLT-DA12400 | Outfit Set | 4 material or feature named but absent | Cream Leather-Look Outfit Set | leather | leather outfit set | special: material claim |
| PLT-DA12401 | Outfit Set | 4 material or feature named but absent | Blue Suede-Look Outfit Set | suede | suede outfit set | special: material claim |
| PLT-DA12402 | Outfit Set | 4 material or feature named but absent | Green Cashmere-Feel Outfit Set | cashmere | cashmere outfit set | special: material claim |
| PLT-DA12500 | Outfit Set | 5 shade spelled in the description only | Moonbeam Outfit Set | ivory | ivory outfit set | generic |
| PLT-DA12501 | Outfit Set | 5 shade spelled in the description only | Driftwood Outfit Set | taupe | taupe outfit set | generic |
| PLT-DA12502 | Outfit Set | 5 shade spelled in the description only | Dune Outfit Set | beige | beige outfit set | generic |
| PLT-DA12600 | Outfit Set | 6 incidental word in a range name | Red Fern Outfit Set | red | red outfit set | generic |
| PLT-DA12601 | Outfit Set | 6 incidental word in a range name | Blue Cove Outfit Set | blue | blue outfit set | generic |
| PLT-DA12602 | Outfit Set | 6 incidental word in a range name | Red Harbour Outfit Set | red | red outfit set | generic |
| PLT-DA12603 | Outfit Set | 6 incidental word in a range name | Jumper Lane Outfit Set | jumper | jumper | generic |
| PLT-DA12700 | Outfit Set | 7 invented brand holding a color or category word | Blue Otter Outfit Set | blue | blue outfit set | generic |
| PLT-DA12701 | Outfit Set | 7 invented brand holding a color or category word | Black Lapwing Outfit Set | black | black outfit set | generic |
| PLT-DA12702 | Outfit Set | 7 invented brand holding a color or category word | Yellow Wagtail Outfit Set | yellow | yellow outfit set | generic |
| PLT-DA13100 | Puffer Jacket | 1 color names a part | Black Puffer Jacket, Yellow Lining | yellow | yellow puffer jacket | generic |
| PLT-DA13101 | Puffer Jacket | 1 color names a part | Blue Puffer Jacket, Yellow Buttons | yellow | yellow puffer jacket | generic |
| PLT-DA13102 | Puffer Jacket | 1 color names a part | White Puffer Jacket, Blue Pocket | blue | blue puffer jacket | generic |
| PLT-DA13200 | Puffer Jacket | 2 another category's noun as a modifier | Pink Hoodie Puffer Jacket | hoodie | hoodie | generic |
| PLT-DA13201 | Puffer Jacket | 2 another category's noun as a modifier | Red Skirt Puffer Jacket | skirt | skirt | generic |
| PLT-DA13202 | Puffer Jacket | 2 another category's noun as a modifier | Navy Hoodie Puffer Jacket | hoodie | hoodie | generic |
| PLT-DA13300 | Puffer Jacket | 3 audience word of a sibling version | Pink Womens-Style Puffer Jacket | womens | womens puffer jacket | generic |
| PLT-DA13301 | Puffer Jacket | 3 audience word of a sibling version | Navy Womens Fit Puffer Jacket | womens | womens puffer jacket | generic |
| PLT-DA13302 | Puffer Jacket | 3 audience word of a sibling version | Brown Mini-Me Mens Puffer Jacket | mens | mens puffer jacket | generic |
| PLT-DA13400 | Puffer Jacket | 4 material or feature named but absent | Pink Leather-Look Puffer Jacket | leather | leather puffer jacket | special: material claim |
| PLT-DA13401 | Puffer Jacket | 4 material or feature named but absent | Brown Suede-Look Puffer Jacket | suede | suede puffer jacket | special: material claim |
| PLT-DA13402 | Puffer Jacket | 4 material or feature named but absent | Green Cashmere-Feel Puffer Jacket | cashmere | cashmere puffer jacket | special: material claim |
| PLT-DA13500 | Puffer Jacket | 5 shade spelled in the description only | Moonbeam Puffer Jacket | ivory | ivory puffer jacket | generic |
| PLT-DA13501 | Puffer Jacket | 5 shade spelled in the description only | Driftwood Puffer Jacket | taupe | taupe puffer jacket | generic |
| PLT-DA13502 | Puffer Jacket | 5 shade spelled in the description only | Dune Puffer Jacket | beige | beige puffer jacket | generic |
| PLT-DA13600 | Puffer Jacket | 6 incidental word in a range name | Red Harbour Puffer Jacket | red | red puffer jacket | generic |
| PLT-DA13601 | Puffer Jacket | 6 incidental word in a range name | Blue Cove Puffer Jacket | blue | blue puffer jacket | generic |
| PLT-DA13602 | Puffer Jacket | 6 incidental word in a range name | Yellow Marsh Puffer Jacket | yellow | yellow puffer jacket | generic |
| PLT-DA13603 | Puffer Jacket | 6 incidental word in a range name | Skirt Point Puffer Jacket | skirt | skirt | generic |
| PLT-DA13700 | Puffer Jacket | 7 invented brand holding a color or category word | Red Plover Puffer Jacket | red | red puffer jacket | generic |
| PLT-DA13701 | Puffer Jacket | 7 invented brand holding a color or category word | Black Lapwing Puffer Jacket | black | black puffer jacket | generic |
| PLT-DA13702 | Puffer Jacket | 7 invented brand holding a color or category word | Yellow Wagtail Puffer Jacket | yellow | yellow puffer jacket | generic |
| PLT-DA14100 | Shirt | 1 color names a part | Brown Shirt, Black Lining | black | black shirt | generic |
| PLT-DA14101 | Shirt | 1 color names a part | White Shirt, Green Stripes | green | green shirt | generic |
| PLT-DA14102 | Shirt | 1 color names a part | Cream Shirt, Red Pocket | red | red shirt | generic |
| PLT-DA14200 | Shirt | 2 another category's noun as a modifier | Pink Cardigan Shirt | cardigan | cardigan | generic |
| PLT-DA14201 | Shirt | 2 another category's noun as a modifier | Black Vest Shirt | vest | vest | generic |
| PLT-DA14202 | Shirt | 2 another category's noun as a modifier | Red Blazer Shirt | blazer | blazer | generic |
| PLT-DA14300 | Shirt | 3 audience word of a sibling version | Navy Womens Fit Shirt | womens | womens shirt | generic |
| PLT-DA14301 | Shirt | 3 audience word of a sibling version | Blue Womens Fit Shirt | womens | womens shirt | generic |
| PLT-DA14302 | Shirt | 3 audience word of a sibling version | Pink Womens-Style Shirt | womens | womens shirt | generic |
| PLT-DA14400 | Shirt | 4 material or feature named but absent | White Leather-Look Shirt | leather | leather shirt | special: material claim |
| PLT-DA14401 | Shirt | 4 material or feature named but absent | Black Suede-Look Shirt | suede | suede shirt | special: material claim |
| PLT-DA14402 | Shirt | 4 material or feature named but absent | Pink Cashmere-Feel Shirt | cashmere | cashmere shirt | special: material claim |
| PLT-DA14500 | Shirt | 5 shade spelled in the description only | Moonbeam Shirt | ivory | ivory shirt | generic |
| PLT-DA14501 | Shirt | 5 shade spelled in the description only | Driftwood Shirt | taupe | taupe shirt | generic |
| PLT-DA14502 | Shirt | 5 shade spelled in the description only | Dune Shirt | beige | beige shirt | generic |
| PLT-DA14600 | Shirt | 6 incidental word in a range name | Blue Meadow Shirt | blue | blue shirt | generic |
| PLT-DA14601 | Shirt | 6 incidental word in a range name | Yellow Brook Shirt | yellow | yellow shirt | generic |
| PLT-DA14602 | Shirt | 6 incidental word in a range name | Green Park Shirt | green | green shirt | generic |
| PLT-DA14603 | Shirt | 6 incidental word in a range name | Jacket Quay Shirt | jacket | jacket | generic |
| PLT-DA14700 | Shirt | 7 invented brand holding a color or category word | Coat Crake Shirt | coat | coat shirt | generic |
| PLT-DA14701 | Shirt | 7 invented brand holding a color or category word | Green Stoat Shirt | green | green shirt | generic |
| PLT-DA14702 | Shirt | 7 invented brand holding a color or category word | Blue Otter Shirt | blue | blue shirt | generic |
| PLT-DA15100 | Shorts | 1 color names a part | Pink Shorts, Yellow Cuffs | yellow | yellow shorts | generic |
| PLT-DA15101 | Shorts | 1 color names a part | Grey Shorts, Blue Stripes | blue | blue shorts | generic |
| PLT-DA15102 | Shorts | 1 color names a part | Green Shorts, White Trim | white | white shorts | generic |
| PLT-DA15200 | Shorts | 2 another category's noun as a modifier | Brown Blazer Shorts | blazer | blazer | generic |
| PLT-DA15201 | Shorts | 2 another category's noun as a modifier | Brown Poncho Shorts | poncho | poncho | generic |
| PLT-DA15202 | Shorts | 2 another category's noun as a modifier | Green Gilet Shorts | gilet | gilet | generic |
| PLT-DA15300 | Shorts | 3 audience word of a sibling version | Brown Boys Fit Shorts | boys | boys shorts | generic |
| PLT-DA15301 | Shorts | 3 audience word of a sibling version | Pink Boys Fit Shorts | boys | boys shorts | generic |
| PLT-DA15302 | Shorts | 3 audience word of a sibling version | White Womens Fit Shorts | womens | womens shorts | generic |
| PLT-DA15400 | Shorts | 4 material or feature named but absent | Green Leather-Look Shorts | leather | leather shorts | special: material claim |
| PLT-DA15401 | Shorts | 4 material or feature named but absent | Navy Suede-Look Shorts | suede | suede shorts | special: material claim |
| PLT-DA15402 | Shorts | 4 material or feature named but absent | Brown Cashmere-Feel Shorts | cashmere | cashmere shorts | special: material claim |
| PLT-DA15500 | Shorts | 5 shade spelled in the description only | Moonbeam Shorts | ivory | ivory shorts | generic |
| PLT-DA15501 | Shorts | 5 shade spelled in the description only | Driftwood Shorts | taupe | taupe shorts | generic |
| PLT-DA15502 | Shorts | 5 shade spelled in the description only | Dune Shorts | beige | beige shorts | generic |
| PLT-DA15600 | Shorts | 6 incidental word in a range name | Red Harbour Shorts | red | red shorts | generic |
| PLT-DA15601 | Shorts | 6 incidental word in a range name | Black Tor Shorts | black | black shorts | generic |
| PLT-DA15602 | Shorts | 6 incidental word in a range name | Yellow Marsh Shorts | yellow | yellow shorts | generic |
| PLT-DA15603 | Shorts | 6 incidental word in a range name | Sock Hop Shorts | sock | sock | generic |
| PLT-DA15700 | Shorts | 7 invented brand holding a color or category word | Black Lapwing Shorts | black | black shorts | generic |
| PLT-DA15701 | Shorts | 7 invented brand holding a color or category word | White Dormouse Shorts | white | white shorts | generic |
| PLT-DA15702 | Shorts | 7 invented brand holding a color or category word | White Dormouse Shorts | white | white shorts | generic |
| PLT-DA16100 | Skirt | 1 color names a part | Red Skirt, Blue Lining | blue | blue skirt | generic |
| PLT-DA16101 | Skirt | 1 color names a part | Blue Skirt, Yellow Pocket | yellow | yellow skirt | generic |
| PLT-DA16102 | Skirt | 1 color names a part | White Skirt, Blue Stitching | blue | blue skirt | generic |
| PLT-DA16200 | Skirt | 2 another category's noun as a modifier | Brown Gilet Skirt | gilet | gilet | generic |
| PLT-DA16201 | Skirt | 2 another category's noun as a modifier | Navy Jacket Skirt | jacket | jacket | generic |
| PLT-DA16202 | Skirt | 2 another category's noun as a modifier | Red Gilet Skirt | gilet | gilet | generic |
| PLT-DA16300 | Skirt | 3 audience word of a sibling version | Black Mens Fit Skirt | mens | mens skirt | generic |
| PLT-DA16301 | Skirt | 3 audience word of a sibling version | White Mens Fit Skirt | mens | mens skirt | generic |
| PLT-DA16302 | Skirt | 3 audience word of a sibling version | Navy Mens-Style Skirt | mens | mens skirt | generic |
| PLT-DA16400 | Skirt | 4 material or feature named but absent | Blue Leather-Look Skirt | leather | leather skirt | special: material claim |
| PLT-DA16401 | Skirt | 4 material or feature named but absent | Pink Suede-Look Skirt | suede | suede skirt | special: material claim |
| PLT-DA16402 | Skirt | 4 material or feature named but absent | Black Cashmere-Feel Skirt | cashmere | cashmere skirt | special: material claim |
| PLT-DA16500 | Skirt | 5 shade spelled in the description only | Moonbeam Skirt | ivory | ivory skirt | generic |
| PLT-DA16501 | Skirt | 5 shade spelled in the description only | Driftwood Skirt | taupe | taupe skirt | generic |
| PLT-DA16502 | Skirt | 5 shade spelled in the description only | Dune Skirt | beige | beige skirt | generic |
| PLT-DA16600 | Skirt | 6 incidental word in a range name | Green Hollow Skirt | green | green skirt | generic |
| PLT-DA16601 | Skirt | 6 incidental word in a range name | Red Fern Skirt | red | red skirt | generic |
| PLT-DA16602 | Skirt | 6 incidental word in a range name | Black Tor Skirt | black | black skirt | generic |
| PLT-DA16603 | Skirt | 6 incidental word in a range name | Coat Hook Skirt | coat | coat | generic |
| PLT-DA16700 | Skirt | 7 invented brand holding a color or category word | Red Plover Skirt | red | red skirt | generic |
| PLT-DA16701 | Skirt | 7 invented brand holding a color or category word | Coat Crake Skirt | coat | coat skirt | generic |
| PLT-DA16702 | Skirt | 7 invented brand holding a color or category word | Jumper Jay Skirt | jumper | jumper skirt | generic |
| PLT-DA17100 | Suit Jacket | 1 color names a part | Pink Suit Jacket, Blue Trim | blue | blue suit jacket | generic |
| PLT-DA17101 | Suit Jacket | 1 color names a part | Cream Suit Jacket, Yellow Zip | yellow | yellow suit jacket | generic |
| PLT-DA17102 | Suit Jacket | 1 color names a part | Navy Suit Jacket, Green Piping | green | green suit jacket | generic |
| PLT-DA17200 | Suit Jacket | 2 another category's noun as a modifier | Navy Hoodie Suit Jacket | hoodie | hoodie | generic |
| PLT-DA17201 | Suit Jacket | 2 another category's noun as a modifier | Red Hoodie Suit Jacket | hoodie | hoodie | generic |
| PLT-DA17202 | Suit Jacket | 2 another category's noun as a modifier | Pink Hoodie Suit Jacket | hoodie | hoodie | generic |
| PLT-DA17300 | Suit Jacket | 3 audience word of a sibling version | Grey Mens-Style Suit Jacket | mens | mens suit jacket | generic |
| PLT-DA17301 | Suit Jacket | 3 audience word of a sibling version | Grey Boys Fit Suit Jacket | boys | boys suit jacket | generic |
| PLT-DA17302 | Suit Jacket | 3 audience word of a sibling version | Pink Boys Fit Suit Jacket | boys | boys suit jacket | generic |
| PLT-DA17400 | Suit Jacket | 4 material or feature named but absent | White Leather-Look Suit Jacket | leather | leather suit jacket | special: material claim |
| PLT-DA17401 | Suit Jacket | 4 material or feature named but absent | Blue Suede-Look Suit Jacket | suede | suede suit jacket | special: material claim |
| PLT-DA17402 | Suit Jacket | 4 material or feature named but absent | Pink Cashmere-Feel Suit Jacket | cashmere | cashmere suit jacket | special: material claim |
| PLT-DA17500 | Suit Jacket | 5 shade spelled in the description only | Moonbeam Suit Jacket | ivory | ivory suit jacket | generic |
| PLT-DA17501 | Suit Jacket | 5 shade spelled in the description only | Driftwood Suit Jacket | taupe | taupe suit jacket | generic |
| PLT-DA17502 | Suit Jacket | 5 shade spelled in the description only | Dune Suit Jacket | beige | beige suit jacket | generic |
| PLT-DA17600 | Suit Jacket | 6 incidental word in a range name | Blue Meadow Suit Jacket | blue | blue suit jacket | generic |
| PLT-DA17601 | Suit Jacket | 6 incidental word in a range name | Blue Cove Suit Jacket | blue | blue suit jacket | generic |
| PLT-DA17602 | Suit Jacket | 6 incidental word in a range name | White Cliff Suit Jacket | white | white suit jacket | generic |
| PLT-DA17603 | Suit Jacket | 6 incidental word in a range name | Jumper Lane Suit Jacket | jumper | jumper | generic |
| PLT-DA17700 | Suit Jacket | 7 invented brand holding a color or category word | Green Stoat Suit Jacket | green | green suit jacket | generic |
| PLT-DA17701 | Suit Jacket | 7 invented brand holding a color or category word | Blue Otter Suit Jacket | blue | blue suit jacket | generic |
| PLT-DA17702 | Suit Jacket | 7 invented brand holding a color or category word | Red Plover Suit Jacket | red | red suit jacket | generic |
| PLT-DA18100 | Sweatshirt | 1 color names a part | Cream Sweatshirt, Yellow Lining | yellow | yellow sweatshirt | generic |
| PLT-DA18101 | Sweatshirt | 1 color names a part | Red Sweatshirt, White Buttons | white | white sweatshirt | generic |
| PLT-DA18102 | Sweatshirt | 1 color names a part | Green Sweatshirt, Black Cuffs | black | black sweatshirt | generic |
| PLT-DA18200 | Sweatshirt | 2 another category's noun as a modifier | Blue Poncho Sweatshirt | poncho | poncho | generic |
| PLT-DA18201 | Sweatshirt | 2 another category's noun as a modifier | White Skirt Sweatshirt | skirt | skirt | generic |
| PLT-DA18202 | Sweatshirt | 2 another category's noun as a modifier | Grey Trouser Sweatshirt | trouser | trouser | generic |
| PLT-DA18300 | Sweatshirt | 3 audience word of a sibling version | Red Womens-Style Sweatshirt | womens | womens sweatshirt | generic |
| PLT-DA18301 | Sweatshirt | 3 audience word of a sibling version | Brown Womens Fit Sweatshirt | womens | womens sweatshirt | generic |
| PLT-DA18302 | Sweatshirt | 3 audience word of a sibling version | Blue Womens Fit Sweatshirt | womens | womens sweatshirt | generic |
| PLT-DA18400 | Sweatshirt | 4 material or feature named but absent | Blue Leather-Look Sweatshirt | leather | leather sweatshirt | special: material claim |
| PLT-DA18401 | Sweatshirt | 4 material or feature named but absent | Green Suede-Look Sweatshirt | suede | suede sweatshirt | special: material claim |
| PLT-DA18402 | Sweatshirt | 4 material or feature named but absent | Navy Cashmere-Feel Sweatshirt | cashmere | cashmere sweatshirt | special: material claim |
| PLT-DA18500 | Sweatshirt | 5 shade spelled in the description only | Moonbeam Sweatshirt | ivory | ivory sweatshirt | generic |
| PLT-DA18501 | Sweatshirt | 5 shade spelled in the description only | Driftwood Sweatshirt | taupe | taupe sweatshirt | generic |
| PLT-DA18502 | Sweatshirt | 5 shade spelled in the description only | Dune Sweatshirt | beige | beige sweatshirt | generic |
| PLT-DA18600 | Sweatshirt | 6 incidental word in a range name | Yellow Brook Sweatshirt | yellow | yellow sweatshirt | generic |
| PLT-DA18601 | Sweatshirt | 6 incidental word in a range name | Yellow Brook Sweatshirt | yellow | yellow sweatshirt | generic |
| PLT-DA18602 | Sweatshirt | 6 incidental word in a range name | White Moor Sweatshirt | white | white sweatshirt | generic |
| PLT-DA18603 | Sweatshirt | 6 incidental word in a range name | Jumper Lane Sweatshirt | jumper | jumper | generic |
| PLT-DA18700 | Sweatshirt | 7 invented brand holding a color or category word | Red Plover Sweatshirt | red | red sweatshirt | generic |
| PLT-DA18701 | Sweatshirt | 7 invented brand holding a color or category word | White Dormouse Sweatshirt | white | white sweatshirt | generic |
| PLT-DA18702 | Sweatshirt | 7 invented brand holding a color or category word | Coat Crake Sweatshirt | coat | coat sweatshirt | generic |
| PLT-DA19100 | T-Shirt | 1 color names a part | White T-Shirt, Yellow Zip | yellow | yellow t-shirt | generic |
| PLT-DA19101 | T-Shirt | 1 color names a part | Blue T-Shirt, Yellow Stripes | yellow | yellow t-shirt | generic |
| PLT-DA19102 | T-Shirt | 1 color names a part | Green T-Shirt, White Stitching | white | white t-shirt | generic |
| PLT-DA19200 | T-Shirt | 2 another category's noun as a modifier | Red Poncho T-Shirt | poncho | poncho | generic |
| PLT-DA19201 | T-Shirt | 2 another category's noun as a modifier | Pink Coat T-Shirt | coat | coat | generic |
| PLT-DA19202 | T-Shirt | 2 another category's noun as a modifier | Blue Coat T-Shirt | coat | coat | generic |
| PLT-DA19300 | T-Shirt | 3 audience word of a sibling version | Grey Girls Fit T-Shirt | girls | girls t-shirt | generic |
| PLT-DA19301 | T-Shirt | 3 audience word of a sibling version | Brown Mens-Style T-Shirt | mens | mens t-shirt | generic |
| PLT-DA19302 | T-Shirt | 3 audience word of a sibling version | Pink Womens Fit T-Shirt | womens | womens t-shirt | generic |
| PLT-DA19400 | T-Shirt | 4 material or feature named but absent | Blue Leather-Look T-Shirt | leather | leather t-shirt | special: material claim |
| PLT-DA19401 | T-Shirt | 4 material or feature named but absent | Pink Suede-Look T-Shirt | suede | suede t-shirt | special: material claim |
| PLT-DA19402 | T-Shirt | 4 material or feature named but absent | White Cashmere-Feel T-Shirt | cashmere | cashmere t-shirt | special: material claim |
| PLT-DA19500 | T-Shirt | 5 shade spelled in the description only | Moonbeam T-Shirt | ivory | ivory t-shirt | generic |
| PLT-DA19501 | T-Shirt | 5 shade spelled in the description only | Driftwood T-Shirt | taupe | taupe t-shirt | generic |
| PLT-DA19502 | T-Shirt | 5 shade spelled in the description only | Dune T-Shirt | beige | beige t-shirt | generic |
| PLT-DA19600 | T-Shirt | 6 incidental word in a range name | Black Tor T-Shirt | black | black t-shirt | generic |
| PLT-DA19601 | T-Shirt | 6 incidental word in a range name | Blue Meadow T-Shirt | blue | blue t-shirt | generic |
| PLT-DA19602 | T-Shirt | 6 incidental word in a range name | Red Fern T-Shirt | red | red t-shirt | generic |
| PLT-DA19603 | T-Shirt | 6 incidental word in a range name | Dress Circle T-Shirt | dress | dress | generic |
| PLT-DA19700 | T-Shirt | 7 invented brand holding a color or category word | Red Plover T-Shirt | red | red t-shirt | generic |
| PLT-DA19701 | T-Shirt | 7 invented brand holding a color or category word | Blue Otter T-Shirt | blue | blue t-shirt | generic |
| PLT-DA19702 | T-Shirt | 7 invented brand holding a color or category word | Black Lapwing T-Shirt | black | black t-shirt | generic |
| PLT-DA20100 | Tea Dress | 1 color names a part | Blue Tea Dress, Red Piping | red | red tea dress | generic |
| PLT-DA20101 | Tea Dress | 1 color names a part | Navy Tea Dress, Black Piping | black | black tea dress | generic |
| PLT-DA20102 | Tea Dress | 1 color names a part | Brown Tea Dress, Yellow Trim | yellow | yellow tea dress | generic |
| PLT-DA20200 | Tea Dress | 2 another category's noun as a modifier | Blue Skirt Tea Dress | skirt | skirt | generic |
| PLT-DA20201 | Tea Dress | 2 another category's noun as a modifier | Red Jacket Tea Dress | jacket | jacket | generic |
| PLT-DA20202 | Tea Dress | 2 another category's noun as a modifier | Black Cardigan Tea Dress | cardigan | cardigan | generic |
| PLT-DA20300 | Tea Dress | 3 audience word of a sibling version | Black Mens Fit Tea Dress | mens | mens tea dress | generic |
| PLT-DA20301 | Tea Dress | 3 audience word of a sibling version | Brown Mens Fit Tea Dress | mens | mens tea dress | generic |
| PLT-DA20302 | Tea Dress | 3 audience word of a sibling version | Pink Mens-Style Tea Dress | mens | mens tea dress | generic |
| PLT-DA20400 | Tea Dress | 4 material or feature named but absent | Pink Leather-Look Tea Dress | leather | leather tea dress | special: material claim |
| PLT-DA20401 | Tea Dress | 4 material or feature named but absent | White Suede-Look Tea Dress | suede | suede tea dress | special: material claim |
| PLT-DA20402 | Tea Dress | 4 material or feature named but absent | Grey Cashmere-Feel Tea Dress | cashmere | cashmere tea dress | special: material claim |
| PLT-DA20500 | Tea Dress | 5 shade spelled in the description only | Moonbeam Tea Dress | ivory | ivory tea dress | generic |
| PLT-DA20501 | Tea Dress | 5 shade spelled in the description only | Driftwood Tea Dress | taupe | taupe tea dress | generic |
| PLT-DA20502 | Tea Dress | 5 shade spelled in the description only | Dune Tea Dress | beige | beige tea dress | generic |
| PLT-DA20600 | Tea Dress | 6 incidental word in a range name | Red Harbour Tea Dress | red | red tea dress | generic |
| PLT-DA20601 | Tea Dress | 6 incidental word in a range name | White Cliff Tea Dress | white | white tea dress | generic |
| PLT-DA20602 | Tea Dress | 6 incidental word in a range name | Green Park Tea Dress | green | green tea dress | generic |
| PLT-DA20603 | Tea Dress | 6 incidental word in a range name | Shirt Row Tea Dress | shirt | shirt | generic |
| PLT-DA20700 | Tea Dress | 7 invented brand holding a color or category word | Red Plover Tea Dress | red | red tea dress | generic |
| PLT-DA20701 | Tea Dress | 7 invented brand holding a color or category word | Green Stoat Tea Dress | green | green tea dress | generic |
| PLT-DA20702 | Tea Dress | 7 invented brand holding a color or category word | Blue Otter Tea Dress | blue | blue tea dress | generic |
| PLT-DA21100 | Tee | 1 color names a part | Green Tee, Black Zip | black | black tee | generic |
| PLT-DA21101 | Tee | 1 color names a part | Grey Tee, Red Collar | red | red tee | generic |
| PLT-DA21102 | Tee | 1 color names a part | Grey Tee, Black Zip | black | black tee | generic |
| PLT-DA21200 | Tee | 2 another category's noun as a modifier | Red Skirt Tee | skirt | skirt | generic |
| PLT-DA21201 | Tee | 2 another category's noun as a modifier | Navy Gilet Tee | gilet | gilet | generic |
| PLT-DA21202 | Tee | 2 another category's noun as a modifier | Cream Coat Tee | coat | coat | generic |
| PLT-DA21300 | Tee | 3 audience word of a sibling version | Green Womens Fit Tee | womens | womens tee | generic |
| PLT-DA21301 | Tee | 3 audience word of a sibling version | Grey Womens Fit Tee | womens | womens tee | generic |
| PLT-DA21302 | Tee | 3 audience word of a sibling version | Green Womens-Style Tee | womens | womens tee | generic |
| PLT-DA21400 | Tee | 4 material or feature named but absent | White Leather-Look Tee | leather | leather tee | special: material claim |
| PLT-DA21401 | Tee | 4 material or feature named but absent | Green Suede-Look Tee | suede | suede tee | special: material claim |
| PLT-DA21402 | Tee | 4 material or feature named but absent | Black Cashmere-Feel Tee | cashmere | cashmere tee | special: material claim |
| PLT-DA21500 | Tee | 5 shade spelled in the description only | Moonbeam Tee | ivory | ivory tee | generic |
| PLT-DA21501 | Tee | 5 shade spelled in the description only | Driftwood Tee | taupe | taupe tee | generic |
| PLT-DA21502 | Tee | 5 shade spelled in the description only | Dune Tee | beige | beige tee | generic |
| PLT-DA21600 | Tee | 6 incidental word in a range name | Blue Cove Tee | blue | blue tee | generic |
| PLT-DA21601 | Tee | 6 incidental word in a range name | Green Park Tee | green | green tee | generic |
| PLT-DA21602 | Tee | 6 incidental word in a range name | Green Hollow Tee | green | green tee | generic |
| PLT-DA21603 | Tee | 6 incidental word in a range name | Skirt Point Tee | skirt | skirt | generic |
| PLT-DA21700 | Tee | 7 invented brand holding a color or category word | Red Plover Tee | red | red tee | generic |
| PLT-DA21701 | Tee | 7 invented brand holding a color or category word | White Dormouse Tee | white | white tee | generic |
| PLT-DA21702 | Tee | 7 invented brand holding a color or category word | Black Lapwing Tee | black | black tee | generic |
| PLT-DA22100 | Top | 1 color names a part | Grey Top, Red Buttons | red | red top | generic |
| PLT-DA22101 | Top | 1 color names a part | Navy Top, Green Trim | green | green top | generic |
| PLT-DA22102 | Top | 1 color names a part | Pink Top, White Lining | white | white top | generic |
| PLT-DA22200 | Top | 2 another category's noun as a modifier | Grey Jacket Top | jacket | jacket | generic |
| PLT-DA22201 | Top | 2 another category's noun as a modifier | Red Skirt Top | skirt | skirt | generic |
| PLT-DA22202 | Top | 2 another category's noun as a modifier | Pink Jacket Top | jacket | jacket | generic |
| PLT-DA22300 | Top | 3 audience word of a sibling version | Green Mens-Style Top | mens | mens top | generic |
| PLT-DA22301 | Top | 3 audience word of a sibling version | Pink Boys Fit Top | boys | boys top | generic |
| PLT-DA22302 | Top | 3 audience word of a sibling version | White Boys Fit Top | boys | boys top | generic |
| PLT-DA22400 | Top | 4 material or feature named but absent | Cream Leather-Look Top | leather | leather top | special: material claim |
| PLT-DA22401 | Top | 4 material or feature named but absent | Cream Suede-Look Top | suede | suede top | special: material claim |
| PLT-DA22402 | Top | 4 material or feature named but absent | Red Cashmere-Feel Top | cashmere | cashmere top | special: material claim |
| PLT-DA22500 | Top | 5 shade spelled in the description only | Moonbeam Top | ivory | ivory top | generic |
| PLT-DA22501 | Top | 5 shade spelled in the description only | Driftwood Top | taupe | taupe top | generic |
| PLT-DA22502 | Top | 5 shade spelled in the description only | Dune Top | beige | beige top | generic |
| PLT-DA22600 | Top | 6 incidental word in a range name | Red Fern Top | red | red top | generic |
| PLT-DA22601 | Top | 6 incidental word in a range name | Black Tor Top | black | black top | generic |
| PLT-DA22602 | Top | 6 incidental word in a range name | White Cliff Top | white | white top | generic |
| PLT-DA22603 | Top | 6 incidental word in a range name | Coat Hook Top | coat | coat | generic |
| PLT-DA22700 | Top | 7 invented brand holding a color or category word | Blue Otter Top | blue | blue top | generic |
| PLT-DA22701 | Top | 7 invented brand holding a color or category word | Green Stoat Top | green | green top | generic |
| PLT-DA22702 | Top | 7 invented brand holding a color or category word | Red Plover Top | red | red top | generic |
| PLT-DA23100 | Tracksuit | 1 color names a part | Grey Tracksuit, Green Stripes | green | green tracksuit | generic |
| PLT-DA23101 | Tracksuit | 1 color names a part | Green Tracksuit, Red Zip | red | red tracksuit | generic |
| PLT-DA23102 | Tracksuit | 1 color names a part | Red Tracksuit, White Stitching | white | white tracksuit | generic |
| PLT-DA23200 | Tracksuit | 2 another category's noun as a modifier | Brown Poncho Tracksuit | poncho | poncho | generic |
| PLT-DA23201 | Tracksuit | 2 another category's noun as a modifier | Grey Jumper Tracksuit | jumper | jumper | generic |
| PLT-DA23202 | Tracksuit | 2 another category's noun as a modifier | Grey Poncho Tracksuit | poncho | poncho | generic |
| PLT-DA23300 | Tracksuit | 3 audience word of a sibling version | White Mens Fit Tracksuit | mens | mens tracksuit | generic |
| PLT-DA23301 | Tracksuit | 3 audience word of a sibling version | Red Mens-Style Tracksuit | mens | mens tracksuit | generic |
| PLT-DA23302 | Tracksuit | 3 audience word of a sibling version | Red Mini-Me Womens Tracksuit | womens | womens tracksuit | generic |
| PLT-DA23400 | Tracksuit | 4 material or feature named but absent | Pink Leather-Look Tracksuit | leather | leather tracksuit | special: material claim |
| PLT-DA23401 | Tracksuit | 4 material or feature named but absent | Green Suede-Look Tracksuit | suede | suede tracksuit | special: material claim |
| PLT-DA23402 | Tracksuit | 4 material or feature named but absent | Cream Cashmere-Feel Tracksuit | cashmere | cashmere tracksuit | special: material claim |
| PLT-DA23500 | Tracksuit | 5 shade spelled in the description only | Moonbeam Tracksuit | ivory | ivory tracksuit | generic |
| PLT-DA23501 | Tracksuit | 5 shade spelled in the description only | Driftwood Tracksuit | taupe | taupe tracksuit | generic |
| PLT-DA23502 | Tracksuit | 5 shade spelled in the description only | Dune Tracksuit | beige | beige tracksuit | generic |
| PLT-DA23600 | Tracksuit | 6 incidental word in a range name | White Cliff Tracksuit | white | white tracksuit | generic |
| PLT-DA23601 | Tracksuit | 6 incidental word in a range name | Blue Meadow Tracksuit | blue | blue tracksuit | generic |
| PLT-DA23602 | Tracksuit | 6 incidental word in a range name | Red Harbour Tracksuit | red | red tracksuit | generic |
| PLT-DA23603 | Tracksuit | 6 incidental word in a range name | Jacket Quay Tracksuit | jacket | jacket | generic |
| PLT-DA23700 | Tracksuit | 7 invented brand holding a color or category word | Yellow Wagtail Tracksuit | yellow | yellow tracksuit | generic |
| PLT-DA23701 | Tracksuit | 7 invented brand holding a color or category word | Black Lapwing Tracksuit | black | black tracksuit | generic |
| PLT-DA23702 | Tracksuit | 7 invented brand holding a color or category word | White Dormouse Tracksuit | white | white tracksuit | generic |
| PLT-DA24100 | Trousers | 1 color names a part | Pink Trousers, Green Stitching | green | green trousers | generic |
| PLT-DA24101 | Trousers | 1 color names a part | Cream Trousers, Black Stripes | black | black trousers | generic |
| PLT-DA24102 | Trousers | 1 color names a part | Navy Trousers, Red Zip | red | red trousers | generic |
| PLT-DA24200 | Trousers | 2 another category's noun as a modifier | Navy Cardigan Trousers | cardigan | cardigan | generic |
| PLT-DA24201 | Trousers | 2 another category's noun as a modifier | Black Jacket Trousers | jacket | jacket | generic |
| PLT-DA24202 | Trousers | 2 another category's noun as a modifier | Brown Tunic Trousers | tunic | tunic | generic |
| PLT-DA24300 | Trousers | 3 audience word of a sibling version | White Mens Fit Trousers | mens | mens trousers | generic |
| PLT-DA24301 | Trousers | 3 audience word of a sibling version | Black Boys Fit Trousers | boys | boys trousers | generic |
| PLT-DA24302 | Trousers | 3 audience word of a sibling version | Cream Mens Fit Trousers | mens | mens trousers | generic |
| PLT-DA24400 | Trousers | 4 material or feature named but absent | Grey Leather-Look Trousers | leather | leather trousers | special: material claim |
| PLT-DA24401 | Trousers | 4 material or feature named but absent | Green Suede-Look Trousers | suede | suede trousers | special: material claim |
| PLT-DA24402 | Trousers | 4 material or feature named but absent | Grey Cashmere-Feel Trousers | cashmere | cashmere trousers | special: material claim |
| PLT-DA24500 | Trousers | 5 shade spelled in the description only | Moonbeam Trousers | ivory | ivory trousers | generic |
| PLT-DA24501 | Trousers | 5 shade spelled in the description only | Driftwood Trousers | taupe | taupe trousers | generic |
| PLT-DA24502 | Trousers | 5 shade spelled in the description only | Dune Trousers | beige | beige trousers | generic |
| PLT-DA24600 | Trousers | 6 incidental word in a range name | White Moor Trousers | white | white trousers | generic |
| PLT-DA24601 | Trousers | 6 incidental word in a range name | Red Fern Trousers | red | red trousers | generic |
| PLT-DA24602 | Trousers | 6 incidental word in a range name | Blue Cove Trousers | blue | blue trousers | generic |
| PLT-DA24603 | Trousers | 6 incidental word in a range name | Skirt Point Trousers | skirt | skirt | generic |
| PLT-DA24700 | Trousers | 7 invented brand holding a color or category word | Yellow Wagtail Trousers | yellow | yellow trousers | generic |
| PLT-DA24701 | Trousers | 7 invented brand holding a color or category word | Green Stoat Trousers | green | green trousers | generic |
| PLT-DA24702 | Trousers | 7 invented brand holding a color or category word | White Dormouse Trousers | white | white trousers | generic |
| PLT-DA25100 | Jeans | 1 color names a part | Green Jeans, Black Stitching | black | black jeans | generic |
| PLT-DA25101 | Jeans | 1 color names a part | White Jeans, Green Trim | green | green jeans | generic |
| PLT-DA25102 | Jeans | 1 color names a part | Cream Jeans, Blue Pocket | blue | blue jeans | generic |
| PLT-DA25103 | Jeans | 1 color names a part | Cream Jeans, White Stripes | white | white jeans | generic |
| PLT-DA25104 | Jeans | 1 color names a part | Black Jeans, Red Lining | red | red jeans | generic |
| PLT-DA25105 | Jeans | 1 color names a part | Red Jeans, Black Stripes | black | black jeans | generic |
| PLT-DA25106 | Jeans | 1 color names a part | Green Jeans, Black Pocket | black | black jeans | generic |
| PLT-DA25107 | Jeans | 1 color names a part | Pink Jeans, White Stripes | white | white jeans | generic |
| PLT-DA25108 | Jeans | 1 color names a part | Red Jeans, Blue Trim | blue | blue jeans | generic |
| PLT-DA25109 | Jeans | 1 color names a part | Navy Jeans, Red Buttons | red | red jeans | generic |
| PLT-DA25110 | Jeans | 1 color names a part | Green Jeans, Red Buttons | red | red jeans | generic |
| PLT-DA25111 | Jeans | 1 color names a part | White Jeans, Green Piping | green | green jeans | generic |
| PLT-DA25200 | Jeans | 2 another category's noun as a modifier | Red Tunic Jeans | tunic | tunic | generic |
| PLT-DA25201 | Jeans | 2 another category's noun as a modifier | Cream Jumper Jeans | jumper | jumper | generic |
| PLT-DA25202 | Jeans | 2 another category's noun as a modifier | Navy Jacket Jeans | jacket | jacket | generic |
| PLT-DA25203 | Jeans | 2 another category's noun as a modifier | Navy Jumper Jeans | jumper | jumper | generic |
| PLT-DA25204 | Jeans | 2 another category's noun as a modifier | Blue Cardigan Jeans | cardigan | cardigan | generic |
| PLT-DA25205 | Jeans | 2 another category's noun as a modifier | Navy Tunic Jeans | tunic | tunic | generic |
| PLT-DA25206 | Jeans | 2 another category's noun as a modifier | White Skirt Jeans | skirt | skirt | generic |
| PLT-DA25207 | Jeans | 2 another category's noun as a modifier | Grey Shirt Jeans | shirt | shirt | generic |
| PLT-DA25208 | Jeans | 2 another category's noun as a modifier | Brown Skirt Jeans | skirt | skirt | generic |
| PLT-DA25209 | Jeans | 2 another category's noun as a modifier | Navy Dress Jeans | dress | dress | generic |
| PLT-DA25210 | Jeans | 2 another category's noun as a modifier | Blue Hoodie Jeans | hoodie | hoodie | generic |
| PLT-DA25211 | Jeans | 2 another category's noun as a modifier | Pink Blazer Jeans | blazer | blazer | generic |
| PLT-DA25300 | Jeans | 3 audience word of a sibling version | Cream Womens Fit Jeans | womens | womens jeans | generic |
| PLT-DA25301 | Jeans | 3 audience word of a sibling version | Navy Girls Fit Jeans | girls | girls jeans | generic |
| PLT-DA25302 | Jeans | 3 audience word of a sibling version | Pink Boys Fit Jeans | boys | boys jeans | generic |
| PLT-DA25303 | Jeans | 3 audience word of a sibling version | Black Womens Fit Jeans | womens | womens jeans | generic |
| PLT-DA25304 | Jeans | 3 audience word of a sibling version | White Mens Fit Jeans | mens | mens jeans | generic |
| PLT-DA25305 | Jeans | 3 audience word of a sibling version | Pink Womens Fit Jeans | womens | womens jeans | generic |
| PLT-DA25306 | Jeans | 3 audience word of a sibling version | Navy Boys Fit Jeans | boys | boys jeans | generic |
| PLT-DA25307 | Jeans | 3 audience word of a sibling version | Cream Boys Fit Jeans | boys | boys jeans | generic |
| PLT-DA25308 | Jeans | 3 audience word of a sibling version | Pink Mens-Style Jeans | mens | mens jeans | generic |
| PLT-DA25309 | Jeans | 3 audience word of a sibling version | Navy Mens-Style Jeans | mens | mens jeans | generic |
| PLT-DA25310 | Jeans | 3 audience word of a sibling version | Pink Mens Fit Jeans | mens | mens jeans | generic |
| PLT-DA25311 | Jeans | 3 audience word of a sibling version | Brown Mens Fit Jeans | mens | mens jeans | generic |
| PLT-DA25400 | Jeans | 4 material or feature named but absent | Pink Leather-Look Jeans | leather | leather jeans | special: material claim |
| PLT-DA25401 | Jeans | 4 material or feature named but absent | Pink Suede-Look Jeans | suede | suede jeans | special: material claim |
| PLT-DA25402 | Jeans | 4 material or feature named but absent | White Cashmere-Feel Jeans | cashmere | cashmere jeans | special: material claim |
| PLT-DA25403 | Jeans | 4 material or feature named but absent | Cream Wool-Free Jeans | wool | wool jeans | special: material claim |
| PLT-DA25404 | Jeans | 4 material or feature named but absent | Pink Silk-Feel Jeans | silk | silk jeans | special: material claim |
| PLT-DA25405 | Jeans | 4 material or feature named but absent | Blue Linen-Look Jeans | linen | linen jeans | special: material claim |
| PLT-DA25406 | Jeans | 4 material or feature named but absent | Red Lace-Free Jeans | lace | lace jeans | special: material claim |
| PLT-DA25407 | Jeans | 4 material or feature named but absent | Navy Velvet-Feel Jeans | velvet | velvet jeans | special: material claim |
| PLT-DA25408 | Jeans | 4 material or feature named but absent | Green Denim-Look Jeans | denim | denim jeans | special: material claim |
| PLT-DA25409 | Jeans | 4 material or feature named but absent | Pink Satin-Look Jeans | satin | satin jeans | special: material claim |
| PLT-DA25410 | Jeans | 4 material or feature named but absent | Black Mohair-Free Jeans | mohair | mohair jeans | special: material claim |
| PLT-DA25411 | Jeans | 4 material or feature named but absent | Cream Tweed-Look Jeans | tweed | tweed jeans | special: material claim |
| PLT-DA25500 | Jeans | 5 shade spelled in the description only | Moonbeam Jeans | ivory | ivory jeans | generic |
| PLT-DA25501 | Jeans | 5 shade spelled in the description only | Driftwood Jeans | taupe | taupe jeans | generic |
| PLT-DA25502 | Jeans | 5 shade spelled in the description only | Dune Jeans | beige | beige jeans | generic |
| PLT-DA25503 | Jeans | 5 shade spelled in the description only | Ember Jeans | burgundy | burgundy jeans | generic |
| PLT-DA25504 | Jeans | 5 shade spelled in the description only | Lagoon Jeans | teal | teal jeans | generic |
| PLT-DA25505 | Jeans | 5 shade spelled in the description only | Willow Jeans | olive | olive jeans | generic |
| PLT-DA25506 | Jeans | 5 shade spelled in the description only | Pebble Jeans | ecru | ecru jeans | generic |
| PLT-DA25507 | Jeans | 5 shade spelled in the description only | Meadow Jeans | mint | mint jeans | generic |
| PLT-DA25508 | Jeans | 5 shade spelled in the description only | Harvest Jeans | rust | rust jeans | generic |
| PLT-DA25509 | Jeans | 5 shade spelled in the description only | Seashell Jeans | coral | coral jeans | generic |
| PLT-DA25510 | Jeans | 5 shade spelled in the description only | Biscuit Jeans | champagne | champagne jeans | generic |
| PLT-DA25511 | Jeans | 5 shade spelled in the description only | Hearth Jeans | khaki | khaki jeans | generic |
| PLT-DA25600 | Jeans | 6 incidental word in a range name | Yellow Marsh Jeans | yellow | yellow jeans | generic |
| PLT-DA25601 | Jeans | 6 incidental word in a range name | Blue Cove Jeans | blue | blue jeans | generic |
| PLT-DA25602 | Jeans | 6 incidental word in a range name | Red Fern Jeans | red | red jeans | generic |
| PLT-DA25603 | Jeans | 6 incidental word in a range name | Blue Meadow Jeans | blue | blue jeans | generic |
| PLT-DA25604 | Jeans | 6 incidental word in a range name | White Cliff Jeans | white | white jeans | generic |
| PLT-DA25605 | Jeans | 6 incidental word in a range name | Yellow Brook Jeans | yellow | yellow jeans | generic |
| PLT-DA25606 | Jeans | 6 incidental word in a range name | Blue Meadow Jeans | blue | blue jeans | generic |
| PLT-DA25607 | Jeans | 6 incidental word in a range name | Red Fern Jeans | red | red jeans | generic |
| PLT-DA25608 | Jeans | 6 incidental word in a range name | Green Hollow Jeans | green | green jeans | generic |
| PLT-DA25609 | Jeans | 6 incidental word in a range name | Green Park Jeans | green | green jeans | generic |
| PLT-DA25610 | Jeans | 6 incidental word in a range name | Blue Cove Jeans | blue | blue jeans | generic |
| PLT-DA25611 | Jeans | 6 incidental word in a range name | Black Tor Jeans | black | black jeans | generic |
| PLT-DA25612 | Jeans | 6 incidental word in a range name | Jacket Quay Jeans | jacket | jacket | generic |
| PLT-DA25700 | Jeans | 7 invented brand holding a color or category word | Yellow Wagtail Jeans | yellow | yellow jeans | generic |
| PLT-DA25701 | Jeans | 7 invented brand holding a color or category word | Red Plover Jeans | red | red jeans | generic |
| PLT-DA25702 | Jeans | 7 invented brand holding a color or category word | Black Lapwing Jeans | black | black jeans | generic |
| PLT-DA25703 | Jeans | 7 invented brand holding a color or category word | Coat Crake Jeans | coat | coat jeans | generic |
| PLT-DA25704 | Jeans | 7 invented brand holding a color or category word | Jumper Jay Jeans | jumper | jumper jeans | generic |
| PLT-DA25705 | Jeans | 7 invented brand holding a color or category word | White Dormouse Jeans | white | white jeans | generic |
| PLT-DA25706 | Jeans | 7 invented brand holding a color or category word | Blue Otter Jeans | blue | blue jeans | generic |
| PLT-DA25707 | Jeans | 7 invented brand holding a color or category word | Green Stoat Jeans | green | green jeans | generic |
| PLT-DA26100 | Socks | 1 color names a part | Green Socks, Blue Cuff | blue | blue socks | generic |
| PLT-DA26101 | Socks | 1 color names a part | Blue Socks, White Trim | white | white socks | generic |
| PLT-DA26102 | Socks | 1 color names a part | Black Socks, Yellow Cuff | yellow | yellow socks | generic |
| PLT-DA26200 | Socks | 2 another category's noun as a modifier | Green Trainer Socks | trainer | trainer | generic |
| PLT-DA26201 | Socks | 2 another category's noun as a modifier | Brown Slipper Socks | slipper | slipper | generic |
| PLT-DA26202 | Socks | 2 another category's noun as a modifier | Black Boot Socks | boot | boot | generic |
| PLT-DA26300 | Socks | 3 audience word of a sibling version | White Mini-Me Mens Socks | mens | mens socks | generic |
| PLT-DA26301 | Socks | 3 audience word of a sibling version | Red Womens Fit Socks | womens | womens socks | generic |
| PLT-DA26302 | Socks | 3 audience word of a sibling version | Green Girls Fit Socks | girls | girls socks | generic |
| PLT-DA26400 | Socks | 4 material or feature named but absent | Green Leather-Look Socks | leather | leather socks | special: material claim |
| PLT-DA26401 | Socks | 4 material or feature named but absent | Cream Suede-Look Socks | suede | suede socks | special: material claim |
| PLT-DA26402 | Socks | 4 material or feature named but absent | Cream Cashmere-Feel Socks | cashmere | cashmere socks | special: material claim |
| PLT-DA26500 | Socks | 5 shade spelled in the description only | Moonbeam Socks | ivory | ivory socks | generic |
| PLT-DA26501 | Socks | 5 shade spelled in the description only | Driftwood Socks | taupe | taupe socks | generic |
| PLT-DA26502 | Socks | 5 shade spelled in the description only | Dune Socks | beige | beige socks | generic |
| PLT-DA26600 | Socks | 6 incidental word in a range name | Black Mill Socks | black | black socks | generic |
| PLT-DA26601 | Socks | 6 incidental word in a range name | Red Fern Socks | red | red socks | generic |
| PLT-DA26602 | Socks | 6 incidental word in a range name | Yellow Brook Socks | yellow | yellow socks | generic |
| PLT-DA26603 | Socks | 6 incidental word in a range name | Dress Circle Socks | dress | dress | generic |
| PLT-DA26700 | Socks | 7 invented brand holding a color or category word | Green Stoat Socks | green | green socks | generic |
| PLT-DA26701 | Socks | 7 invented brand holding a color or category word | White Dormouse Socks | white | white socks | generic |
| PLT-DA26702 | Socks | 7 invented brand holding a color or category word | Blue Otter Socks | blue | blue socks | generic |
| PLT-DA27100 | Boot Socks | 1 color names a part | Brown Boot Socks, Yellow Heel | yellow | yellow boot socks | generic |
| PLT-DA27101 | Boot Socks | 1 color names a part | Red Boot Socks, Yellow Trim | yellow | yellow boot socks | generic |
| PLT-DA27102 | Boot Socks | 1 color names a part | Grey Boot Socks, Yellow Cuff | yellow | yellow boot socks | generic |
| PLT-DA27200 | Boot Socks | 2 another category's noun as a modifier | Green Shoe Boot Socks | shoe | shoe | generic |
| PLT-DA27201 | Boot Socks | 2 another category's noun as a modifier | Grey Trouser Boot Socks | trouser | trouser | generic |
| PLT-DA27202 | Boot Socks | 2 another category's noun as a modifier | Grey Trainer Boot Socks | trainer | trainer | generic |
| PLT-DA27300 | Boot Socks | 3 audience word of a sibling version | Cream Boys Fit Boot Socks | boys | boys boot socks | generic |
| PLT-DA27301 | Boot Socks | 3 audience word of a sibling version | Red Boys Fit Boot Socks | boys | boys boot socks | generic |
| PLT-DA27302 | Boot Socks | 3 audience word of a sibling version | Cream Mens-Style Boot Socks | mens | mens boot socks | generic |
| PLT-DA27400 | Boot Socks | 4 material or feature named but absent | Green Leather-Look Boot Socks | leather | leather boot socks | special: material claim |
| PLT-DA27401 | Boot Socks | 4 material or feature named but absent | Pink Suede-Look Boot Socks | suede | suede boot socks | special: material claim |
| PLT-DA27402 | Boot Socks | 4 material or feature named but absent | Red Cashmere-Feel Boot Socks | cashmere | cashmere boot socks | special: material claim |
| PLT-DA27500 | Boot Socks | 5 shade spelled in the description only | Moonbeam Boot Socks | ivory | ivory boot socks | generic |
| PLT-DA27501 | Boot Socks | 5 shade spelled in the description only | Driftwood Boot Socks | taupe | taupe boot socks | generic |
| PLT-DA27502 | Boot Socks | 5 shade spelled in the description only | Dune Boot Socks | beige | beige boot socks | generic |
| PLT-DA27600 | Boot Socks | 6 incidental word in a range name | Green Hollow Boot Socks | green | green boot socks | generic |
| PLT-DA27601 | Boot Socks | 6 incidental word in a range name | Blue Cove Boot Socks | blue | blue boot socks | generic |
| PLT-DA27602 | Boot Socks | 6 incidental word in a range name | Green Park Boot Socks | green | green boot socks | generic |
| PLT-DA27603 | Boot Socks | 6 incidental word in a range name | Skirt Point Boot Socks | skirt | skirt | generic |
| PLT-DA27700 | Boot Socks | 7 invented brand holding a color or category word | Blue Otter Boot Socks | blue | blue boot socks | generic |
| PLT-DA27701 | Boot Socks | 7 invented brand holding a color or category word | Red Plover Boot Socks | red | red boot socks | generic |
| PLT-DA27702 | Boot Socks | 7 invented brand holding a color or category word | White Dormouse Boot Socks | white | white boot socks | generic |
| PLT-DA28100 | Ankle Boots | 1 color names a part | Brown Ankle Boots, Black Trim | black | black ankle boots | generic |
| PLT-DA28101 | Ankle Boots | 1 color names a part | Navy Ankle Boots, Green Heel | green | green ankle boots | generic |
| PLT-DA28102 | Ankle Boots | 1 color names a part | Green Ankle Boots, Yellow Heel | yellow | yellow ankle boots | generic |
| PLT-DA28200 | Ankle Boots | 2 another category's noun as a modifier | Grey Sandal Ankle Boots | sandal | sandal | generic |
| PLT-DA28201 | Ankle Boots | 2 another category's noun as a modifier | White Sandal Ankle Boots | sandal | sandal | generic |
| PLT-DA28202 | Ankle Boots | 2 another category's noun as a modifier | Navy Slipper Ankle Boots | slipper | slipper | generic |
| PLT-DA28300 | Ankle Boots | 3 audience word of a sibling version | Red Mens-Style Ankle Boots | mens | mens ankle boots | generic |
| PLT-DA28301 | Ankle Boots | 3 audience word of a sibling version | White Mens Fit Ankle Boots | mens | mens ankle boots | generic |
| PLT-DA28302 | Ankle Boots | 3 audience word of a sibling version | Grey Boys Fit Ankle Boots | boys | boys ankle boots | generic |
| PLT-DA28400 | Ankle Boots | 4 material or feature named but absent | Grey Leather-Look Ankle Boots | leather | leather ankle boots | special: material claim |
| PLT-DA28401 | Ankle Boots | 4 material or feature named but absent | White Cashmere-Feel Ankle Boots | cashmere | cashmere ankle boots | special: material claim |
| PLT-DA28402 | Ankle Boots | 4 material or feature named but absent | Cream Wool-Free Ankle Boots | wool | wool ankle boots | special: material claim |
| PLT-DA28500 | Ankle Boots | 5 shade spelled in the description only | Moonbeam Ankle Boots | ivory | ivory ankle boots | generic |
| PLT-DA28501 | Ankle Boots | 5 shade spelled in the description only | Driftwood Ankle Boots | taupe | taupe ankle boots | generic |
| PLT-DA28502 | Ankle Boots | 5 shade spelled in the description only | Dune Ankle Boots | beige | beige ankle boots | generic |
| PLT-DA28600 | Ankle Boots | 6 incidental word in a range name | Green Hollow Ankle Boots | green | green ankle boots | generic |
| PLT-DA28601 | Ankle Boots | 6 incidental word in a range name | Red Fern Ankle Boots | red | red ankle boots | generic |
| PLT-DA28602 | Ankle Boots | 6 incidental word in a range name | Black Tor Ankle Boots | black | black ankle boots | generic |
| PLT-DA28603 | Ankle Boots | 6 incidental word in a range name | Coat Hook Ankle Boots | coat | coat | generic |
| PLT-DA28700 | Ankle Boots | 7 invented brand holding a color or category word | Blue Otter Ankle Boots | blue | blue ankle boots | generic |
| PLT-DA28701 | Ankle Boots | 7 invented brand holding a color or category word | Coat Crake Ankle Boots | coat | coat ankle boots | generic |
| PLT-DA28702 | Ankle Boots | 7 invented brand holding a color or category word | Yellow Wagtail Ankle Boots | yellow | yellow ankle boots | generic |
| PLT-DA29100 | Ballet Pumps | 1 color names a part | Red Ballet Pumps, Blue Heel | blue | blue ballet pumps | generic |
| PLT-DA29101 | Ballet Pumps | 1 color names a part | Red Ballet Pumps, Blue Eyelets | blue | blue ballet pumps | generic |
| PLT-DA29102 | Ballet Pumps | 1 color names a part | Black Ballet Pumps, Blue Stitching | blue | blue ballet pumps | generic |
| PLT-DA29200 | Ballet Pumps | 2 another category's noun as a modifier | Red Sock Ballet Pumps | sock | sock | generic |
| PLT-DA29201 | Ballet Pumps | 2 another category's noun as a modifier | Red Sandal Ballet Pumps | sandal | sandal | generic |
| PLT-DA29202 | Ballet Pumps | 2 another category's noun as a modifier | Green Boot Ballet Pumps | boot | boot | generic |
| PLT-DA29300 | Ballet Pumps | 3 audience word of a sibling version | Brown Mens-Style Ballet Pumps | mens | mens ballet pumps | generic |
| PLT-DA29301 | Ballet Pumps | 3 audience word of a sibling version | Green Mens-Style Ballet Pumps | mens | mens ballet pumps | generic |
| PLT-DA29302 | Ballet Pumps | 3 audience word of a sibling version | Red Mens Fit Ballet Pumps | mens | mens ballet pumps | generic |
| PLT-DA29400 | Ballet Pumps | 4 material or feature named but absent | Black Cashmere-Feel Ballet Pumps | cashmere | cashmere ballet pumps | special: material claim |
| PLT-DA29401 | Ballet Pumps | 4 material or feature named but absent | Blue Wool-Free Ballet Pumps | wool | wool ballet pumps | special: material claim |
| PLT-DA29402 | Ballet Pumps | 4 material or feature named but absent | Pink Silk-Free Ballet Pumps | silk | silk ballet pumps | special: material claim |
| PLT-DA29500 | Ballet Pumps | 5 shade spelled in the description only | Moonbeam Ballet Pumps | ivory | ivory ballet pumps | generic |
| PLT-DA29501 | Ballet Pumps | 5 shade spelled in the description only | Driftwood Ballet Pumps | taupe | taupe ballet pumps | generic |
| PLT-DA29502 | Ballet Pumps | 5 shade spelled in the description only | Dune Ballet Pumps | beige | beige ballet pumps | generic |
| PLT-DA29600 | Ballet Pumps | 6 incidental word in a range name | White Moor Ballet Pumps | white | white ballet pumps | generic |
| PLT-DA29601 | Ballet Pumps | 6 incidental word in a range name | Green Park Ballet Pumps | green | green ballet pumps | generic |
| PLT-DA29602 | Ballet Pumps | 6 incidental word in a range name | Yellow Marsh Ballet Pumps | yellow | yellow ballet pumps | generic |
| PLT-DA29603 | Ballet Pumps | 6 incidental word in a range name | Shirt Row Ballet Pumps | shirt | shirt | generic |
| PLT-DA29700 | Ballet Pumps | 7 invented brand holding a color or category word | Black Lapwing Ballet Pumps | black | black ballet pumps | generic |
| PLT-DA29701 | Ballet Pumps | 7 invented brand holding a color or category word | White Dormouse Ballet Pumps | white | white ballet pumps | generic |
| PLT-DA29702 | Ballet Pumps | 7 invented brand holding a color or category word | Jumper Jay Ballet Pumps | jumper | jumper ballet pumps | generic |
| PLT-DA30100 | Block Heels | 1 color names a part | Brown Block Heels, Blue Heel | blue | blue block heels | generic |
| PLT-DA30101 | Block Heels | 1 color names a part | Pink Block Heels, Black Heel | black | black block heels | generic |
| PLT-DA30102 | Block Heels | 1 color names a part | Red Block Heels, Yellow Heel | yellow | yellow block heels | generic |
| PLT-DA30200 | Block Heels | 2 another category's noun as a modifier | Brown Sneaker Block Heels | sneaker | sneaker | generic |
| PLT-DA30201 | Block Heels | 2 another category's noun as a modifier | Cream Sneaker Block Heels | sneaker | sneaker | generic |
| PLT-DA30202 | Block Heels | 2 another category's noun as a modifier | Pink Slipper Block Heels | slipper | slipper | generic |
| PLT-DA30300 | Block Heels | 3 audience word of a sibling version | Red Mens Fit Block Heels | mens | mens block heels | generic |
| PLT-DA30301 | Block Heels | 3 audience word of a sibling version | Brown Boys Fit Block Heels | boys | boys block heels | generic |
| PLT-DA30302 | Block Heels | 3 audience word of a sibling version | White Mens Fit Block Heels | mens | mens block heels | generic |
| PLT-DA30400 | Block Heels | 4 material or feature named but absent | Pink Cashmere-Feel Block Heels | cashmere | cashmere block heels | special: material claim |
| PLT-DA30401 | Block Heels | 4 material or feature named but absent | Red Wool-Free Block Heels | wool | wool block heels | special: material claim |
| PLT-DA30402 | Block Heels | 4 material or feature named but absent | Red Silk-Feel Block Heels | silk | silk block heels | special: material claim |
| PLT-DA30500 | Block Heels | 5 shade spelled in the description only | Moonbeam Block Heels | ivory | ivory block heels | generic |
| PLT-DA30501 | Block Heels | 5 shade spelled in the description only | Driftwood Block Heels | taupe | taupe block heels | generic |
| PLT-DA30502 | Block Heels | 5 shade spelled in the description only | Dune Block Heels | beige | beige block heels | generic |
| PLT-DA30600 | Block Heels | 6 incidental word in a range name | Yellow Brook Block Heels | yellow | yellow block heels | generic |
| PLT-DA30601 | Block Heels | 6 incidental word in a range name | Green Hollow Block Heels | green | green block heels | generic |
| PLT-DA30602 | Block Heels | 6 incidental word in a range name | White Moor Block Heels | white | white block heels | generic |
| PLT-DA30603 | Block Heels | 6 incidental word in a range name | Dress Circle Block Heels | dress | dress | generic |
| PLT-DA30700 | Block Heels | 7 invented brand holding a color or category word | Red Plover Block Heels | red | red block heels | generic |
| PLT-DA30701 | Block Heels | 7 invented brand holding a color or category word | Coat Crake Block Heels | coat | coat block heels | generic |
| PLT-DA30702 | Block Heels | 7 invented brand holding a color or category word | Green Stoat Block Heels | green | green block heels | generic |
| PLT-DA31100 | Brogues | 1 color names a part | Black Brogues, White Lining | white | white brogues | generic |
| PLT-DA31101 | Brogues | 1 color names a part | Cream Brogues, Blue Trim | blue | blue brogues | generic |
| PLT-DA31102 | Brogues | 1 color names a part | Blue Brogues, White Eyelets | white | white brogues | generic |
| PLT-DA31200 | Brogues | 2 another category's noun as a modifier | Brown Loafer Brogues | loafer | loafer | generic |
| PLT-DA31201 | Brogues | 2 another category's noun as a modifier | Navy Sandal Brogues | sandal | sandal | generic |
| PLT-DA31202 | Brogues | 2 another category's noun as a modifier | Grey Mule Brogues | mule | mule | generic |
| PLT-DA31300 | Brogues | 3 audience word of a sibling version | Brown Womens Fit Brogues | womens | womens brogues | generic |
| PLT-DA31301 | Brogues | 3 audience word of a sibling version | Grey Mens-Style Brogues | mens | mens brogues | generic |
| PLT-DA31302 | Brogues | 3 audience word of a sibling version | Red Girls Fit Brogues | girls | girls brogues | generic |
| PLT-DA31400 | Brogues | 4 material or feature named but absent | White Suede-Look Brogues | suede | suede brogues | special: material claim |
| PLT-DA31401 | Brogues | 4 material or feature named but absent | Red Cashmere-Feel Brogues | cashmere | cashmere brogues | special: material claim |
| PLT-DA31402 | Brogues | 4 material or feature named but absent | Green Wool-Free Brogues | wool | wool brogues | special: material claim |
| PLT-DA31500 | Brogues | 5 shade spelled in the description only | Moonbeam Brogues | ivory | ivory brogues | generic |
| PLT-DA31501 | Brogues | 5 shade spelled in the description only | Driftwood Brogues | taupe | taupe brogues | generic |
| PLT-DA31502 | Brogues | 5 shade spelled in the description only | Dune Brogues | beige | beige brogues | generic |
| PLT-DA31600 | Brogues | 6 incidental word in a range name | Green Hollow Brogues | green | green brogues | generic |
| PLT-DA31601 | Brogues | 6 incidental word in a range name | Red Harbour Brogues | red | red brogues | generic |
| PLT-DA31602 | Brogues | 6 incidental word in a range name | Red Fern Brogues | red | red brogues | generic |
| PLT-DA31603 | Brogues | 6 incidental word in a range name | Shirt Row Brogues | shirt | shirt | generic |
| PLT-DA31700 | Brogues | 7 invented brand holding a color or category word | Yellow Wagtail Brogues | yellow | yellow brogues | generic |
| PLT-DA31701 | Brogues | 7 invented brand holding a color or category word | Yellow Wagtail Brogues | yellow | yellow brogues | generic |
| PLT-DA31702 | Brogues | 7 invented brand holding a color or category word | Red Plover Brogues | red | red brogues | generic |
| PLT-DA32100 | Chelsea Boots | 1 color names a part | Grey Chelsea Boots, White Stitching | white | white chelsea boots | generic |
| PLT-DA32101 | Chelsea Boots | 1 color names a part | Grey Chelsea Boots, Yellow Sole | yellow | yellow chelsea boots | generic |
| PLT-DA32102 | Chelsea Boots | 1 color names a part | Green Chelsea Boots, White Heel | white | white chelsea boots | generic |
| PLT-DA32200 | Chelsea Boots | 2 another category's noun as a modifier | Cream Loafer Chelsea Boots | loafer | loafer | generic |
| PLT-DA32201 | Chelsea Boots | 2 another category's noun as a modifier | Pink Slipper Chelsea Boots | slipper | slipper | generic |
| PLT-DA32202 | Chelsea Boots | 2 another category's noun as a modifier | Green Heel Chelsea Boots | heel | heel | generic |
| PLT-DA32300 | Chelsea Boots | 3 audience word of a sibling version | Black Womens-Style Chelsea Boots | womens | womens chelsea boots | generic |
| PLT-DA32301 | Chelsea Boots | 3 audience word of a sibling version | Brown Boys Fit Chelsea Boots | boys | boys chelsea boots | generic |
| PLT-DA32302 | Chelsea Boots | 3 audience word of a sibling version | Red Girls Fit Chelsea Boots | girls | girls chelsea boots | generic |
| PLT-DA32400 | Chelsea Boots | 4 material or feature named but absent | Cream Suede-Look Chelsea Boots | suede | suede chelsea boots | special: material claim |
| PLT-DA32401 | Chelsea Boots | 4 material or feature named but absent | Red Leather-Look Chelsea Boots | leather | leather chelsea boots | special: material claim |
| PLT-DA32402 | Chelsea Boots | 4 material or feature named but absent | Red Cashmere-Feel Chelsea Boots | cashmere | cashmere chelsea boots | special: material claim |
| PLT-DA32500 | Chelsea Boots | 5 shade spelled in the description only | Moonbeam Chelsea Boots | ivory | ivory chelsea boots | generic |
| PLT-DA32501 | Chelsea Boots | 5 shade spelled in the description only | Driftwood Chelsea Boots | taupe | taupe chelsea boots | generic |
| PLT-DA32502 | Chelsea Boots | 5 shade spelled in the description only | Dune Chelsea Boots | beige | beige chelsea boots | generic |
| PLT-DA32600 | Chelsea Boots | 6 incidental word in a range name | Black Mill Chelsea Boots | black | black chelsea boots | generic |
| PLT-DA32601 | Chelsea Boots | 6 incidental word in a range name | Blue Cove Chelsea Boots | blue | blue chelsea boots | generic |
| PLT-DA32602 | Chelsea Boots | 6 incidental word in a range name | Yellow Brook Chelsea Boots | yellow | yellow chelsea boots | generic |
| PLT-DA32603 | Chelsea Boots | 6 incidental word in a range name | Shirt Row Chelsea Boots | shirt | shirt | generic |
| PLT-DA32700 | Chelsea Boots | 7 invented brand holding a color or category word | Black Lapwing Chelsea Boots | black | black chelsea boots | generic |
| PLT-DA32701 | Chelsea Boots | 7 invented brand holding a color or category word | Black Lapwing Chelsea Boots | black | black chelsea boots | generic |
| PLT-DA32702 | Chelsea Boots | 7 invented brand holding a color or category word | Yellow Wagtail Chelsea Boots | yellow | yellow chelsea boots | generic |
| PLT-DA33100 | Chukka Boots | 1 color names a part | Navy Chukka Boots, Red Stitching | red | red chukka boots | generic |
| PLT-DA33101 | Chukka Boots | 1 color names a part | Green Chukka Boots, Yellow Sole | yellow | yellow chukka boots | generic |
| PLT-DA33102 | Chukka Boots | 1 color names a part | Grey Chukka Boots, Green Trim | green | green chukka boots | generic |
| PLT-DA33200 | Chukka Boots | 2 another category's noun as a modifier | White Pump Chukka Boots | pump | pump | generic |
| PLT-DA33201 | Chukka Boots | 2 another category's noun as a modifier | Navy Sneaker Chukka Boots | sneaker | sneaker | generic |
| PLT-DA33202 | Chukka Boots | 2 another category's noun as a modifier | Navy Trainer Chukka Boots | trainer | trainer | generic |
| PLT-DA33300 | Chukka Boots | 3 audience word of a sibling version | Black Girls Fit Chukka Boots | girls | girls chukka boots | generic |
| PLT-DA33301 | Chukka Boots | 3 audience word of a sibling version | White Girls Fit Chukka Boots | girls | girls chukka boots | generic |
| PLT-DA33302 | Chukka Boots | 3 audience word of a sibling version | Blue Girls Fit Chukka Boots | girls | girls chukka boots | generic |
| PLT-DA33400 | Chukka Boots | 4 material or feature named but absent | Black Leather-Look Chukka Boots | leather | leather chukka boots | special: material claim |
| PLT-DA33401 | Chukka Boots | 4 material or feature named but absent | Red Cashmere-Feel Chukka Boots | cashmere | cashmere chukka boots | special: material claim |
| PLT-DA33402 | Chukka Boots | 4 material or feature named but absent | Blue Wool-Free Chukka Boots | wool | wool chukka boots | special: material claim |
| PLT-DA33500 | Chukka Boots | 5 shade spelled in the description only | Moonbeam Chukka Boots | ivory | ivory chukka boots | generic |
| PLT-DA33501 | Chukka Boots | 5 shade spelled in the description only | Driftwood Chukka Boots | taupe | taupe chukka boots | generic |
| PLT-DA33502 | Chukka Boots | 5 shade spelled in the description only | Dune Chukka Boots | beige | beige chukka boots | generic |
| PLT-DA33600 | Chukka Boots | 6 incidental word in a range name | Red Harbour Chukka Boots | red | red chukka boots | generic |
| PLT-DA33601 | Chukka Boots | 6 incidental word in a range name | Green Hollow Chukka Boots | green | green chukka boots | generic |
| PLT-DA33602 | Chukka Boots | 6 incidental word in a range name | White Moor Chukka Boots | white | white chukka boots | generic |
| PLT-DA33603 | Chukka Boots | 6 incidental word in a range name | Jacket Quay Chukka Boots | jacket | jacket | generic |
| PLT-DA33700 | Chukka Boots | 7 invented brand holding a color or category word | White Dormouse Chukka Boots | white | white chukka boots | generic |
| PLT-DA33701 | Chukka Boots | 7 invented brand holding a color or category word | Green Stoat Chukka Boots | green | green chukka boots | generic |
| PLT-DA33702 | Chukka Boots | 7 invented brand holding a color or category word | Jumper Jay Chukka Boots | jumper | jumper chukka boots | generic |
| PLT-DA34100 | Court Shoes | 1 color names a part | White Court Shoes, Red Heel | red | red court shoes | generic |
| PLT-DA34101 | Court Shoes | 1 color names a part | Navy Court Shoes, Red Eyelets | red | red court shoes | generic |
| PLT-DA34102 | Court Shoes | 1 color names a part | Green Court Shoes, Yellow Sole | yellow | yellow court shoes | generic |
| PLT-DA34200 | Court Shoes | 2 another category's noun as a modifier | Green Sock Court Shoes | sock | sock | generic |
| PLT-DA34201 | Court Shoes | 2 another category's noun as a modifier | Black Slipper Court Shoes | slipper | slipper | generic |
| PLT-DA34202 | Court Shoes | 2 another category's noun as a modifier | Blue Sneaker Court Shoes | sneaker | sneaker | generic |
| PLT-DA34300 | Court Shoes | 3 audience word of a sibling version | Black Boys Fit Court Shoes | boys | boys court shoes | generic |
| PLT-DA34301 | Court Shoes | 3 audience word of a sibling version | Pink Mens Fit Court Shoes | mens | mens court shoes | generic |
| PLT-DA34302 | Court Shoes | 3 audience word of a sibling version | Brown Boys Fit Court Shoes | boys | boys court shoes | generic |
| PLT-DA34400 | Court Shoes | 4 material or feature named but absent | Blue Cashmere-Feel Court Shoes | cashmere | cashmere court shoes | special: material claim |
| PLT-DA34401 | Court Shoes | 4 material or feature named but absent | Brown Wool-Free Court Shoes | wool | wool court shoes | special: material claim |
| PLT-DA34402 | Court Shoes | 4 material or feature named but absent | Brown Silk-Free Court Shoes | silk | silk court shoes | special: material claim |
| PLT-DA34500 | Court Shoes | 5 shade spelled in the description only | Moonbeam Court Shoes | ivory | ivory court shoes | generic |
| PLT-DA34501 | Court Shoes | 5 shade spelled in the description only | Driftwood Court Shoes | taupe | taupe court shoes | generic |
| PLT-DA34502 | Court Shoes | 5 shade spelled in the description only | Dune Court Shoes | beige | beige court shoes | generic |
| PLT-DA34600 | Court Shoes | 6 incidental word in a range name | Red Fern Court Shoes | red | red court shoes | generic |
| PLT-DA34601 | Court Shoes | 6 incidental word in a range name | Black Mill Court Shoes | black | black court shoes | generic |
| PLT-DA34602 | Court Shoes | 6 incidental word in a range name | Green Park Court Shoes | green | green court shoes | generic |
| PLT-DA34603 | Court Shoes | 6 incidental word in a range name | Boot Hill Court Shoes | boot | boot | generic |
| PLT-DA34700 | Court Shoes | 7 invented brand holding a color or category word | Yellow Wagtail Court Shoes | yellow | yellow court shoes | generic |
| PLT-DA34701 | Court Shoes | 7 invented brand holding a color or category word | Blue Otter Court Shoes | blue | blue court shoes | generic |
| PLT-DA34702 | Court Shoes | 7 invented brand holding a color or category word | Jumper Jay Court Shoes | jumper | jumper court shoes | generic |
| PLT-DA35100 | Kitten Heels | 1 color names a part | White Kitten Heels, Blue Eyelets | blue | blue kitten heels | generic |
| PLT-DA35101 | Kitten Heels | 1 color names a part | Pink Kitten Heels, Green Heel | green | green kitten heels | generic |
| PLT-DA35102 | Kitten Heels | 1 color names a part | Grey Kitten Heels, Yellow Trim | yellow | yellow kitten heels | generic |
| PLT-DA35200 | Kitten Heels | 2 another category's noun as a modifier | Pink Pump Kitten Heels | pump | pump | generic |
| PLT-DA35201 | Kitten Heels | 2 another category's noun as a modifier | Black Sneaker Kitten Heels | sneaker | sneaker | generic |
| PLT-DA35202 | Kitten Heels | 2 another category's noun as a modifier | Grey Loafer Kitten Heels | loafer | loafer | generic |
| PLT-DA35300 | Kitten Heels | 3 audience word of a sibling version | Brown Mens-Style Kitten Heels | mens | mens kitten heels | generic |
| PLT-DA35301 | Kitten Heels | 3 audience word of a sibling version | Navy Mens Fit Kitten Heels | mens | mens kitten heels | generic |
| PLT-DA35302 | Kitten Heels | 3 audience word of a sibling version | Cream Boys Fit Kitten Heels | boys | boys kitten heels | generic |
| PLT-DA35400 | Kitten Heels | 4 material or feature named but absent | Red Suede-Look Kitten Heels | suede | suede kitten heels | special: material claim |
| PLT-DA35401 | Kitten Heels | 4 material or feature named but absent | Green Cashmere-Feel Kitten Heels | cashmere | cashmere kitten heels | special: material claim |
| PLT-DA35402 | Kitten Heels | 4 material or feature named but absent | Grey Wool-Free Kitten Heels | wool | wool kitten heels | special: material claim |
| PLT-DA35500 | Kitten Heels | 5 shade spelled in the description only | Moonbeam Kitten Heels | ivory | ivory kitten heels | generic |
| PLT-DA35501 | Kitten Heels | 5 shade spelled in the description only | Driftwood Kitten Heels | taupe | taupe kitten heels | generic |
| PLT-DA35502 | Kitten Heels | 5 shade spelled in the description only | Dune Kitten Heels | beige | beige kitten heels | generic |
| PLT-DA35600 | Kitten Heels | 6 incidental word in a range name | Red Harbour Kitten Heels | red | red kitten heels | generic |
| PLT-DA35601 | Kitten Heels | 6 incidental word in a range name | Blue Cove Kitten Heels | blue | blue kitten heels | generic |
| PLT-DA35602 | Kitten Heels | 6 incidental word in a range name | White Cliff Kitten Heels | white | white kitten heels | generic |
| PLT-DA35603 | Kitten Heels | 6 incidental word in a range name | Shirt Row Kitten Heels | shirt | shirt | generic |
| PLT-DA35700 | Kitten Heels | 7 invented brand holding a color or category word | Jumper Jay Kitten Heels | jumper | jumper kitten heels | generic |
| PLT-DA35701 | Kitten Heels | 7 invented brand holding a color or category word | Yellow Wagtail Kitten Heels | yellow | yellow kitten heels | generic |
| PLT-DA35702 | Kitten Heels | 7 invented brand holding a color or category word | Red Plover Kitten Heels | red | red kitten heels | generic |
| PLT-DA36100 | Knee High Boots | 1 color names a part | Pink Knee High Boots, Yellow Lining | yellow | yellow knee high boots | generic |
| PLT-DA36101 | Knee High Boots | 1 color names a part | Pink Knee High Boots, White Eyelets | white | white knee high boots | generic |
| PLT-DA36102 | Knee High Boots | 1 color names a part | Red Knee High Boots, Black Heel | black | black knee high boots | generic |
| PLT-DA36200 | Knee High Boots | 2 another category's noun as a modifier | Black Trainer Knee High Boots | trainer | trainer | generic |
| PLT-DA36201 | Knee High Boots | 2 another category's noun as a modifier | Red Trainer Knee High Boots | trainer | trainer | generic |
| PLT-DA36202 | Knee High Boots | 2 another category's noun as a modifier | White Loafer Knee High Boots | loafer | loafer | generic |
| PLT-DA36300 | Knee High Boots | 3 audience word of a sibling version | Blue Boys Fit Knee High Boots | boys | boys knee high boots | generic |
| PLT-DA36301 | Knee High Boots | 3 audience word of a sibling version | Blue Mens Fit Knee High Boots | mens | mens knee high boots | generic |
| PLT-DA36302 | Knee High Boots | 3 audience word of a sibling version | White Boys Fit Knee High Boots | boys | boys knee high boots | generic |
| PLT-DA36400 | Knee High Boots | 4 material or feature named but absent | Pink Suede-Look Knee High Boots | suede | suede knee high boots | special: material claim |
| PLT-DA36401 | Knee High Boots | 4 material or feature named but absent | Red Cashmere-Feel Knee High Boots | cashmere | cashmere knee high boots | special: material claim |
| PLT-DA36402 | Knee High Boots | 4 material or feature named but absent | White Wool-Free Knee High Boots | wool | wool knee high boots | special: material claim |
| PLT-DA36500 | Knee High Boots | 5 shade spelled in the description only | Moonbeam Knee High Boots | ivory | ivory knee high boots | generic |
| PLT-DA36501 | Knee High Boots | 5 shade spelled in the description only | Driftwood Knee High Boots | taupe | taupe knee high boots | generic |
| PLT-DA36502 | Knee High Boots | 5 shade spelled in the description only | Dune Knee High Boots | beige | beige knee high boots | generic |
| PLT-DA36600 | Knee High Boots | 6 incidental word in a range name | White Cliff Knee High Boots | white | white knee high boots | generic |
| PLT-DA36601 | Knee High Boots | 6 incidental word in a range name | Yellow Marsh Knee High Boots | yellow | yellow knee high boots | generic |
| PLT-DA36602 | Knee High Boots | 6 incidental word in a range name | Blue Meadow Knee High Boots | blue | blue knee high boots | generic |
| PLT-DA36603 | Knee High Boots | 6 incidental word in a range name | Dress Circle Knee High Boots | dress | dress | generic |
| PLT-DA36700 | Knee High Boots | 7 invented brand holding a color or category word | White Dormouse Knee High Boots | white | white knee high boots | generic |
| PLT-DA36701 | Knee High Boots | 7 invented brand holding a color or category word | Coat Crake Knee High Boots | coat | coat knee high boots | generic |
| PLT-DA36702 | Knee High Boots | 7 invented brand holding a color or category word | Red Plover Knee High Boots | red | red knee high boots | generic |
| PLT-DA37100 | Loafers | 1 color names a part | White Loafers, Yellow Lining | yellow | yellow loafers | generic |
| PLT-DA37101 | Loafers | 1 color names a part | Blue Loafers, Green Eyelets | green | green loafers | generic |
| PLT-DA37102 | Loafers | 1 color names a part | Navy Loafers, Black Trim | black | black loafers | generic |
| PLT-DA37200 | Loafers | 2 another category's noun as a modifier | Pink Pump Loafers | pump | pump | generic |
| PLT-DA37201 | Loafers | 2 another category's noun as a modifier | Navy Heel Loafers | heel | heel | generic |
| PLT-DA37202 | Loafers | 2 another category's noun as a modifier | Green Heel Loafers | heel | heel | generic |
| PLT-DA37300 | Loafers | 3 audience word of a sibling version | Navy Womens Fit Loafers | womens | womens loafers | generic |
| PLT-DA37301 | Loafers | 3 audience word of a sibling version | Black Mens-Style Loafers | mens | mens loafers | generic |
| PLT-DA37302 | Loafers | 3 audience word of a sibling version | Pink Boys Fit Loafers | boys | boys loafers | generic |
| PLT-DA37400 | Loafers | 4 material or feature named but absent | Brown Suede-Look Loafers | suede | suede loafers | special: material claim |
| PLT-DA37401 | Loafers | 4 material or feature named but absent | Brown Cashmere-Feel Loafers | cashmere | cashmere loafers | special: material claim |
| PLT-DA37402 | Loafers | 4 material or feature named but absent | Black Wool-Free Loafers | wool | wool loafers | special: material claim |
| PLT-DA37500 | Loafers | 5 shade spelled in the description only | Moonbeam Loafers | ivory | ivory loafers | generic |
| PLT-DA37501 | Loafers | 5 shade spelled in the description only | Driftwood Loafers | taupe | taupe loafers | generic |
| PLT-DA37502 | Loafers | 5 shade spelled in the description only | Dune Loafers | beige | beige loafers | generic |
| PLT-DA37600 | Loafers | 6 incidental word in a range name | Blue Meadow Loafers | blue | blue loafers | generic |
| PLT-DA37601 | Loafers | 6 incidental word in a range name | Blue Meadow Loafers | blue | blue loafers | generic |
| PLT-DA37602 | Loafers | 6 incidental word in a range name | White Moor Loafers | white | white loafers | generic |
| PLT-DA37603 | Loafers | 6 incidental word in a range name | Coat Hook Loafers | coat | coat | generic |
| PLT-DA37700 | Loafers | 7 invented brand holding a color or category word | Black Lapwing Loafers | black | black loafers | generic |
| PLT-DA37701 | Loafers | 7 invented brand holding a color or category word | Yellow Wagtail Loafers | yellow | yellow loafers | generic |
| PLT-DA37702 | Loafers | 7 invented brand holding a color or category word | Jumper Jay Loafers | jumper | jumper loafers | generic |
| PLT-DA38100 | Running Shoes | 1 color names a part | Brown Running Shoes, Red Sole | red | red running shoes | generic |
| PLT-DA38101 | Running Shoes | 1 color names a part | Blue Running Shoes, Yellow Heel | yellow | yellow running shoes | generic |
| PLT-DA38102 | Running Shoes | 1 color names a part | Red Running Shoes, Black Heel | black | black running shoes | generic |
| PLT-DA38200 | Running Shoes | 2 another category's noun as a modifier | Grey Slipper Running Shoes | slipper | slipper | generic |
| PLT-DA38201 | Running Shoes | 2 another category's noun as a modifier | Navy Trainer Running Shoes | trainer | trainer | generic |
| PLT-DA38202 | Running Shoes | 2 another category's noun as a modifier | White Loafer Running Shoes | loafer | loafer | generic |
| PLT-DA38300 | Running Shoes | 3 audience word of a sibling version | Cream Mini-Me Mens Running Shoes | mens | mens running shoes | generic |
| PLT-DA38301 | Running Shoes | 3 audience word of a sibling version | Black Girls Fit Running Shoes | girls | girls running shoes | generic |
| PLT-DA38302 | Running Shoes | 3 audience word of a sibling version | Grey Mens Fit Running Shoes | mens | mens running shoes | generic |
| PLT-DA38400 | Running Shoes | 4 material or feature named but absent | Red Leather-Look Running Shoes | leather | leather running shoes | special: material claim |
| PLT-DA38401 | Running Shoes | 4 material or feature named but absent | Green Suede-Look Running Shoes | suede | suede running shoes | special: material claim |
| PLT-DA38402 | Running Shoes | 4 material or feature named but absent | White Cashmere-Feel Running Shoes | cashmere | cashmere running shoes | special: material claim |
| PLT-DA38500 | Running Shoes | 5 shade spelled in the description only | Moonbeam Running Shoes | ivory | ivory running shoes | generic |
| PLT-DA38501 | Running Shoes | 5 shade spelled in the description only | Driftwood Running Shoes | taupe | taupe running shoes | generic |
| PLT-DA38502 | Running Shoes | 5 shade spelled in the description only | Dune Running Shoes | beige | beige running shoes | generic |
| PLT-DA38600 | Running Shoes | 6 incidental word in a range name | Green Hollow Running Shoes | green | green running shoes | generic |
| PLT-DA38601 | Running Shoes | 6 incidental word in a range name | Green Park Running Shoes | green | green running shoes | generic |
| PLT-DA38602 | Running Shoes | 6 incidental word in a range name | Black Mill Running Shoes | black | black running shoes | generic |
| PLT-DA38603 | Running Shoes | 6 incidental word in a range name | Jumper Lane Running Shoes | jumper | jumper | generic |
| PLT-DA38700 | Running Shoes | 7 invented brand holding a color or category word | Red Plover Running Shoes | red | red running shoes | generic |
| PLT-DA38701 | Running Shoes | 7 invented brand holding a color or category word | Coat Crake Running Shoes | coat | coat running shoes | generic |
| PLT-DA38702 | Running Shoes | 7 invented brand holding a color or category word | Black Lapwing Running Shoes | black | black running shoes | generic |
| PLT-DA39100 | Safety Boots | 1 color names a part | Red Safety Boots, White Lining | white | white safety boots | generic |
| PLT-DA39101 | Safety Boots | 1 color names a part | White Safety Boots, Red Heel | red | red safety boots | generic |
| PLT-DA39102 | Safety Boots | 1 color names a part | Red Safety Boots, Yellow Heel | yellow | yellow safety boots | generic |
| PLT-DA39200 | Safety Boots | 2 another category's noun as a modifier | Cream Sandal Safety Boots | sandal | sandal | generic |
| PLT-DA39201 | Safety Boots | 2 another category's noun as a modifier | Brown Trainer Safety Boots | trainer | trainer | generic |
| PLT-DA39202 | Safety Boots | 2 another category's noun as a modifier | White Sandal Safety Boots | sandal | sandal | generic |
| PLT-DA39300 | Safety Boots | 3 audience word of a sibling version | Cream Womens Fit Safety Boots | womens | womens safety boots | generic |
| PLT-DA39301 | Safety Boots | 3 audience word of a sibling version | White Womens-Style Safety Boots | womens | womens safety boots | generic |
| PLT-DA39302 | Safety Boots | 3 audience word of a sibling version | Blue Womens-Style Safety Boots | womens | womens safety boots | generic |
| PLT-DA39400 | Safety Boots | 4 material or feature named but absent | Grey Suede-Look Safety Boots | suede | suede safety boots | special: material claim |
| PLT-DA39401 | Safety Boots | 4 material or feature named but absent | Pink Cashmere-Feel Safety Boots | cashmere | cashmere safety boots | special: material claim |
| PLT-DA39402 | Safety Boots | 4 material or feature named but absent | Cream Wool-Free Safety Boots | wool | wool safety boots | special: material claim |
| PLT-DA39500 | Safety Boots | 5 shade spelled in the description only | Moonbeam Safety Boots | ivory | ivory safety boots | generic |
| PLT-DA39501 | Safety Boots | 5 shade spelled in the description only | Driftwood Safety Boots | taupe | taupe safety boots | generic |
| PLT-DA39502 | Safety Boots | 5 shade spelled in the description only | Dune Safety Boots | beige | beige safety boots | generic |
| PLT-DA39600 | Safety Boots | 6 incidental word in a range name | White Moor Safety Boots | white | white safety boots | generic |
| PLT-DA39601 | Safety Boots | 6 incidental word in a range name | Black Tor Safety Boots | black | black safety boots | generic |
| PLT-DA39602 | Safety Boots | 6 incidental word in a range name | Red Fern Safety Boots | red | red safety boots | generic |
| PLT-DA39603 | Safety Boots | 6 incidental word in a range name | Shirt Row Safety Boots | shirt | shirt | generic |
| PLT-DA39700 | Safety Boots | 7 invented brand holding a color or category word | Coat Crake Safety Boots | coat | coat safety boots | generic |
| PLT-DA39701 | Safety Boots | 7 invented brand holding a color or category word | Blue Otter Safety Boots | blue | blue safety boots | generic |
| PLT-DA39702 | Safety Boots | 7 invented brand holding a color or category word | Yellow Wagtail Safety Boots | yellow | yellow safety boots | generic |
| PLT-DA40100 | Sandals | 1 color names a part | Grey Sandals, White Heel | white | white sandals | generic |
| PLT-DA40101 | Sandals | 1 color names a part | Cream Sandals, Yellow Eyelets | yellow | yellow sandals | generic |
| PLT-DA40102 | Sandals | 1 color names a part | Red Sandals, Black Sole | black | black sandals | generic |
| PLT-DA40200 | Sandals | 2 another category's noun as a modifier | Navy Heel Sandals | heel | heel | generic |
| PLT-DA40201 | Sandals | 2 another category's noun as a modifier | Red Pump Sandals | pump | pump | generic |
| PLT-DA40202 | Sandals | 2 another category's noun as a modifier | Grey Slipper Sandals | slipper | slipper | generic |
| PLT-DA40300 | Sandals | 3 audience word of a sibling version | Green Mini-Me Mens Sandals | mens | mens sandals | generic |
| PLT-DA40301 | Sandals | 3 audience word of a sibling version | Red Mens-Style Sandals | mens | mens sandals | generic |
| PLT-DA40302 | Sandals | 3 audience word of a sibling version | Cream Mens-Style Sandals | mens | mens sandals | generic |
| PLT-DA40400 | Sandals | 4 material or feature named but absent | Red Leather-Look Sandals | leather | leather sandals | special: material claim |
| PLT-DA40401 | Sandals | 4 material or feature named but absent | Brown Suede-Look Sandals | suede | suede sandals | special: material claim |
| PLT-DA40402 | Sandals | 4 material or feature named but absent | Green Cashmere-Feel Sandals | cashmere | cashmere sandals | special: material claim |
| PLT-DA40500 | Sandals | 5 shade spelled in the description only | Moonbeam Sandals | ivory | ivory sandals | generic |
| PLT-DA40501 | Sandals | 5 shade spelled in the description only | Driftwood Sandals | taupe | taupe sandals | generic |
| PLT-DA40502 | Sandals | 5 shade spelled in the description only | Dune Sandals | beige | beige sandals | generic |
| PLT-DA40600 | Sandals | 6 incidental word in a range name | White Cliff Sandals | white | white sandals | generic |
| PLT-DA40601 | Sandals | 6 incidental word in a range name | Blue Cove Sandals | blue | blue sandals | generic |
| PLT-DA40602 | Sandals | 6 incidental word in a range name | White Moor Sandals | white | white sandals | generic |
| PLT-DA40603 | Sandals | 6 incidental word in a range name | Jumper Lane Sandals | jumper | jumper | generic |
| PLT-DA40700 | Sandals | 7 invented brand holding a color or category word | Yellow Wagtail Sandals | yellow | yellow sandals | generic |
| PLT-DA40701 | Sandals | 7 invented brand holding a color or category word | White Dormouse Sandals | white | white sandals | generic |
| PLT-DA40702 | Sandals | 7 invented brand holding a color or category word | White Dormouse Sandals | white | white sandals | generic |
| PLT-DA41100 | School Shoes | 1 color names a part | Blue School Shoes, Green Heel | green | green school shoes | generic |
| PLT-DA41101 | School Shoes | 1 color names a part | Grey School Shoes, Green Eyelets | green | green school shoes | generic |
| PLT-DA41102 | School Shoes | 1 color names a part | Black School Shoes, White Eyelets | white | white school shoes | generic |
| PLT-DA41200 | School Shoes | 2 another category's noun as a modifier | Pink Mule School Shoes | mule | mule | generic |
| PLT-DA41201 | School Shoes | 2 another category's noun as a modifier | White Pump School Shoes | pump | pump | generic |
| PLT-DA41202 | School Shoes | 2 another category's noun as a modifier | Navy Boot School Shoes | boot | boot | generic |
| PLT-DA41300 | School Shoes | 3 audience word of a sibling version | Red Mens-Style School Shoes | mens | mens school shoes | generic |
| PLT-DA41301 | School Shoes | 3 audience word of a sibling version | Cream Mens-Style School Shoes | mens | mens school shoes | generic |
| PLT-DA41302 | School Shoes | 3 audience word of a sibling version | Pink Mini-Me Mens School Shoes | mens | mens school shoes | generic |
| PLT-DA41400 | School Shoes | 4 material or feature named but absent | Pink Suede-Look School Shoes | suede | suede school shoes | special: material claim |
| PLT-DA41401 | School Shoes | 4 material or feature named but absent | Black Cashmere-Feel School Shoes | cashmere | cashmere school shoes | special: material claim |
| PLT-DA41402 | School Shoes | 4 material or feature named but absent | Pink Wool-Free School Shoes | wool | wool school shoes | special: material claim |
| PLT-DA41500 | School Shoes | 5 shade spelled in the description only | Moonbeam School Shoes | ivory | ivory school shoes | generic |
| PLT-DA41501 | School Shoes | 5 shade spelled in the description only | Driftwood School Shoes | taupe | taupe school shoes | generic |
| PLT-DA41502 | School Shoes | 5 shade spelled in the description only | Dune School Shoes | beige | beige school shoes | generic |
| PLT-DA41600 | School Shoes | 6 incidental word in a range name | White Cliff School Shoes | white | white school shoes | generic |
| PLT-DA41601 | School Shoes | 6 incidental word in a range name | Yellow Brook School Shoes | yellow | yellow school shoes | generic |
| PLT-DA41602 | School Shoes | 6 incidental word in a range name | Black Mill School Shoes | black | black school shoes | generic |
| PLT-DA41603 | School Shoes | 6 incidental word in a range name | Jacket Quay School Shoes | jacket | jacket | generic |
| PLT-DA41700 | School Shoes | 7 invented brand holding a color or category word | Jumper Jay School Shoes | jumper | jumper school shoes | generic |
| PLT-DA41701 | School Shoes | 7 invented brand holding a color or category word | Red Plover School Shoes | red | red school shoes | generic |
| PLT-DA41702 | School Shoes | 7 invented brand holding a color or category word | White Dormouse School Shoes | white | white school shoes | generic |
| PLT-DA42100 | Slippers | 1 color names a part | Navy Slippers, White Eyelets | white | white slippers | generic |
| PLT-DA42101 | Slippers | 1 color names a part | Black Slippers, White Eyelets | white | white slippers | generic |
| PLT-DA42102 | Slippers | 1 color names a part | Red Slippers, Green Stitching | green | green slippers | generic |
| PLT-DA42200 | Slippers | 2 another category's noun as a modifier | Brown Heel Slippers | heel | heel | generic |
| PLT-DA42201 | Slippers | 2 another category's noun as a modifier | Brown Heel Slippers | heel | heel | generic |
| PLT-DA42202 | Slippers | 2 another category's noun as a modifier | White Trainer Slippers | trainer | trainer | generic |
| PLT-DA42300 | Slippers | 3 audience word of a sibling version | Grey Womens Fit Slippers | womens | womens slippers | generic |
| PLT-DA42301 | Slippers | 3 audience word of a sibling version | Navy Mens Fit Slippers | mens | mens slippers | generic |
| PLT-DA42302 | Slippers | 3 audience word of a sibling version | Green Boys Fit Slippers | boys | boys slippers | generic |
| PLT-DA42400 | Slippers | 4 material or feature named but absent | Black Leather-Look Slippers | leather | leather slippers | special: material claim |
| PLT-DA42401 | Slippers | 4 material or feature named but absent | Pink Cashmere-Feel Slippers | cashmere | cashmere slippers | special: material claim |
| PLT-DA42402 | Slippers | 4 material or feature named but absent | Pink Wool-Free Slippers | wool | wool slippers | special: material claim |
| PLT-DA42500 | Slippers | 5 shade spelled in the description only | Moonbeam Slippers | ivory | ivory slippers | generic |
| PLT-DA42501 | Slippers | 5 shade spelled in the description only | Driftwood Slippers | taupe | taupe slippers | generic |
| PLT-DA42502 | Slippers | 5 shade spelled in the description only | Dune Slippers | beige | beige slippers | generic |
| PLT-DA42600 | Slippers | 6 incidental word in a range name | White Moor Slippers | white | white slippers | generic |
| PLT-DA42601 | Slippers | 6 incidental word in a range name | Black Tor Slippers | black | black slippers | generic |
| PLT-DA42602 | Slippers | 6 incidental word in a range name | White Moor Slippers | white | white slippers | generic |
| PLT-DA42603 | Slippers | 6 incidental word in a range name | Coat Hook Slippers | coat | coat | generic |
| PLT-DA42700 | Slippers | 7 invented brand holding a color or category word | Blue Otter Slippers | blue | blue slippers | generic |
| PLT-DA42701 | Slippers | 7 invented brand holding a color or category word | Jumper Jay Slippers | jumper | jumper slippers | generic |
| PLT-DA42702 | Slippers | 7 invented brand holding a color or category word | Yellow Wagtail Slippers | yellow | yellow slippers | generic |
| PLT-DA43100 | Trainers | 1 color names a part | Green Trainers, White Lining | white | white trainers | generic |
| PLT-DA43101 | Trainers | 1 color names a part | Navy Trainers, Black Heel | black | black trainers | generic |
| PLT-DA43102 | Trainers | 1 color names a part | Grey Trainers, Yellow Heel | yellow | yellow trainers | generic |
| PLT-DA43200 | Trainers | 2 another category's noun as a modifier | Navy Loafer Trainers | loafer | loafer | generic |
| PLT-DA43201 | Trainers | 2 another category's noun as a modifier | Red Heel Trainers | heel | heel | generic |
| PLT-DA43202 | Trainers | 2 another category's noun as a modifier | Pink Sneaker Trainers | sneaker | sneaker | generic |
| PLT-DA43300 | Trainers | 3 audience word of a sibling version | Green Womens Fit Trainers | womens | womens trainers | generic |
| PLT-DA43301 | Trainers | 3 audience word of a sibling version | Cream Mens-Style Trainers | mens | mens trainers | generic |
| PLT-DA43302 | Trainers | 3 audience word of a sibling version | Brown Womens Fit Trainers | womens | womens trainers | generic |
| PLT-DA43400 | Trainers | 4 material or feature named but absent | Cream Leather-Look Trainers | leather | leather trainers | special: material claim |
| PLT-DA43401 | Trainers | 4 material or feature named but absent | Pink Suede-Look Trainers | suede | suede trainers | special: material claim |
| PLT-DA43402 | Trainers | 4 material or feature named but absent | Grey Cashmere-Feel Trainers | cashmere | cashmere trainers | special: material claim |
| PLT-DA43500 | Trainers | 5 shade spelled in the description only | Moonbeam Trainers | ivory | ivory trainers | generic |
| PLT-DA43501 | Trainers | 5 shade spelled in the description only | Driftwood Trainers | taupe | taupe trainers | generic |
| PLT-DA43502 | Trainers | 5 shade spelled in the description only | Dune Trainers | beige | beige trainers | generic |
| PLT-DA43600 | Trainers | 6 incidental word in a range name | Yellow Brook Trainers | yellow | yellow trainers | generic |
| PLT-DA43601 | Trainers | 6 incidental word in a range name | Red Harbour Trainers | red | red trainers | generic |
| PLT-DA43602 | Trainers | 6 incidental word in a range name | Black Tor Trainers | black | black trainers | generic |
| PLT-DA43603 | Trainers | 6 incidental word in a range name | Boot Hill Trainers | boot | boot | generic |
| PLT-DA43700 | Trainers | 7 invented brand holding a color or category word | Yellow Wagtail Trainers | yellow | yellow trainers | generic |
| PLT-DA43701 | Trainers | 7 invented brand holding a color or category word | Jumper Jay Trainers | jumper | jumper trainers | generic |
| PLT-DA43702 | Trainers | 7 invented brand holding a color or category word | Yellow Wagtail Trainers | yellow | yellow trainers | generic |
| PLT-DA44100 | Walking Boots | 1 color names a part | White Walking Boots, Blue Eyelets | blue | blue walking boots | generic |
| PLT-DA44101 | Walking Boots | 1 color names a part | Navy Walking Boots, White Heel | white | white walking boots | generic |
| PLT-DA44102 | Walking Boots | 1 color names a part | Grey Walking Boots, Yellow Eyelets | yellow | yellow walking boots | generic |
| PLT-DA44200 | Walking Boots | 2 another category's noun as a modifier | Brown Sock Walking Boots | sock | sock | generic |
| PLT-DA44201 | Walking Boots | 2 another category's noun as a modifier | Pink Slipper Walking Boots | slipper | slipper | generic |
| PLT-DA44202 | Walking Boots | 2 another category's noun as a modifier | Black Sock Walking Boots | sock | sock | generic |
| PLT-DA44300 | Walking Boots | 3 audience word of a sibling version | Pink Mens-Style Walking Boots | mens | mens walking boots | generic |
| PLT-DA44301 | Walking Boots | 3 audience word of a sibling version | Black Girls Fit Walking Boots | girls | girls walking boots | generic |
| PLT-DA44302 | Walking Boots | 3 audience word of a sibling version | Grey Mens-Style Walking Boots | mens | mens walking boots | generic |
| PLT-DA44400 | Walking Boots | 4 material or feature named but absent | Green Leather-Look Walking Boots | leather | leather walking boots | special: material claim |
| PLT-DA44401 | Walking Boots | 4 material or feature named but absent | White Suede-Look Walking Boots | suede | suede walking boots | special: material claim |
| PLT-DA44402 | Walking Boots | 4 material or feature named but absent | Cream Cashmere-Feel Walking Boots | cashmere | cashmere walking boots | special: material claim |
| PLT-DA44500 | Walking Boots | 5 shade spelled in the description only | Moonbeam Walking Boots | ivory | ivory walking boots | generic |
| PLT-DA44501 | Walking Boots | 5 shade spelled in the description only | Driftwood Walking Boots | taupe | taupe walking boots | generic |
| PLT-DA44502 | Walking Boots | 5 shade spelled in the description only | Dune Walking Boots | beige | beige walking boots | generic |
| PLT-DA44600 | Walking Boots | 6 incidental word in a range name | Green Park Walking Boots | green | green walking boots | generic |
| PLT-DA44601 | Walking Boots | 6 incidental word in a range name | Red Fern Walking Boots | red | red walking boots | generic |
| PLT-DA44602 | Walking Boots | 6 incidental word in a range name | Yellow Brook Walking Boots | yellow | yellow walking boots | generic |
| PLT-DA44603 | Walking Boots | 6 incidental word in a range name | Sock Hop Walking Boots | sock | sock | generic |
| PLT-DA44700 | Walking Boots | 7 invented brand holding a color or category word | Black Lapwing Walking Boots | black | black walking boots | generic |
| PLT-DA44701 | Walking Boots | 7 invented brand holding a color or category word | Jumper Jay Walking Boots | jumper | jumper walking boots | generic |
| PLT-DA44702 | Walking Boots | 7 invented brand holding a color or category word | Jumper Jay Walking Boots | jumper | jumper walking boots | generic |
| PLT-DA45100 | Wellies | 1 color names a part | Pink Wellies, Green Sole | green | green wellies | generic |
| PLT-DA45101 | Wellies | 1 color names a part | Cream Wellies, Black Sole | black | black wellies | generic |
| PLT-DA45102 | Wellies | 1 color names a part | Cream Wellies, Yellow Heel | yellow | yellow wellies | generic |
| PLT-DA45200 | Wellies | 2 another category's noun as a modifier | Black Heel Wellies | heel | heel | generic |
| PLT-DA45201 | Wellies | 2 another category's noun as a modifier | Cream Loafer Wellies | loafer | loafer | generic |
| PLT-DA45202 | Wellies | 2 another category's noun as a modifier | White Sandal Wellies | sandal | sandal | generic |
| PLT-DA45300 | Wellies | 3 audience word of a sibling version | Red Mens Fit Wellies | mens | mens wellies | generic |
| PLT-DA45301 | Wellies | 3 audience word of a sibling version | Green Boys Fit Wellies | boys | boys wellies | generic |
| PLT-DA45302 | Wellies | 3 audience word of a sibling version | Black Mini-Me Womens Wellies | womens | womens wellies | generic |
| PLT-DA45400 | Wellies | 4 material or feature named but absent | Red Leather-Look Wellies | leather | leather wellies | special: material claim |
| PLT-DA45401 | Wellies | 4 material or feature named but absent | Green Suede-Look Wellies | suede | suede wellies | special: material claim |
| PLT-DA45402 | Wellies | 4 material or feature named but absent | Navy Cashmere-Feel Wellies | cashmere | cashmere wellies | special: material claim |
| PLT-DA45500 | Wellies | 5 shade spelled in the description only | Moonbeam Wellies | ivory | ivory wellies | generic |
| PLT-DA45501 | Wellies | 5 shade spelled in the description only | Driftwood Wellies | taupe | taupe wellies | generic |
| PLT-DA45502 | Wellies | 5 shade spelled in the description only | Dune Wellies | beige | beige wellies | generic |
| PLT-DA45600 | Wellies | 6 incidental word in a range name | Blue Cove Wellies | blue | blue wellies | generic |
| PLT-DA45601 | Wellies | 6 incidental word in a range name | White Moor Wellies | white | white wellies | generic |
| PLT-DA45602 | Wellies | 6 incidental word in a range name | Red Harbour Wellies | red | red wellies | generic |
| PLT-DA45603 | Wellies | 6 incidental word in a range name | Coat Hook Wellies | coat | coat | generic |
| PLT-DA45700 | Wellies | 7 invented brand holding a color or category word | Yellow Wagtail Wellies | yellow | yellow wellies | generic |
| PLT-DA45701 | Wellies | 7 invented brand holding a color or category word | Black Lapwing Wellies | black | black wellies | generic |
| PLT-DA45702 | Wellies | 7 invented brand holding a color or category word | Jumper Jay Wellies | jumper | jumper wellies | generic |
| PLT-DA46100 | Bra | 1 color names a part | Pink Bra, White Straps | white | white bra | generic |
| PLT-DA46101 | Bra | 1 color names a part | Brown Bra, Blue Hooks | blue | blue bra | generic |
| PLT-DA46102 | Bra | 1 color names a part | Black Bra, Yellow Trim | yellow | yellow bra | generic |
| PLT-DA46103 | Bra | 1 color names a part | Red Bra, Blue Hooks | blue | blue bra | generic |
| PLT-DA46104 | Bra | 1 color names a part | White Bra, Red Bow | red | red bra | generic |
| PLT-DA46105 | Bra | 1 color names a part | Grey Bra, Red Trim | red | red bra | generic |
| PLT-DA46106 | Bra | 1 color names a part | Navy Bra, Yellow Hooks | yellow | yellow bra | generic |
| PLT-DA46107 | Bra | 1 color names a part | Pink Bra, Black Trim | black | black bra | generic |
| PLT-DA46108 | Bra | 1 color names a part | Brown Bra, White Bow | white | white bra | generic |
| PLT-DA46200 | Bra | 2 another category's noun as a modifier | White Dress Bra | dress | dress | generic |
| PLT-DA46201 | Bra | 2 another category's noun as a modifier | Green Jumper Bra | jumper | jumper | generic |
| PLT-DA46202 | Bra | 2 another category's noun as a modifier | Brown Bodysuit Bra | bodysuit | bodysuit | generic |
| PLT-DA46203 | Bra | 2 another category's noun as a modifier | Black Skirt Bra | skirt | skirt | generic |
| PLT-DA46204 | Bra | 2 another category's noun as a modifier | Blue Top Bra | top | top | generic |
| PLT-DA46205 | Bra | 2 another category's noun as a modifier | Grey Bodysuit Bra | bodysuit | bodysuit | generic |
| PLT-DA46206 | Bra | 2 another category's noun as a modifier | Cream Slip Bra | slip | slip | generic |
| PLT-DA46207 | Bra | 2 another category's noun as a modifier | Pink Top Bra | top | top | generic |
| PLT-DA46208 | Bra | 2 another category's noun as a modifier | Green Bodysuit Bra | bodysuit | bodysuit | generic |
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
| PLT-DA46600 | Bra | 6 incidental word in a range name | Yellow Marsh Bra | yellow | yellow bra | generic |
| PLT-DA46601 | Bra | 6 incidental word in a range name | Green Park Bra | green | green bra | generic |
| PLT-DA46602 | Bra | 6 incidental word in a range name | White Cliff Bra | white | white bra | generic |
| PLT-DA46603 | Bra | 6 incidental word in a range name | Red Harbour Bra | red | red bra | generic |
| PLT-DA46604 | Bra | 6 incidental word in a range name | Yellow Brook Bra | yellow | yellow bra | generic |
| PLT-DA46605 | Bra | 6 incidental word in a range name | White Moor Bra | white | white bra | generic |
| PLT-DA46606 | Bra | 6 incidental word in a range name | Black Tor Bra | black | black bra | generic |
| PLT-DA46607 | Bra | 6 incidental word in a range name | Blue Meadow Bra | blue | blue bra | generic |
| PLT-DA46608 | Bra | 6 incidental word in a range name | Black Mill Bra | black | black bra | generic |
| PLT-DA46609 | Bra | 6 incidental word in a range name | Shirt Row Bra | shirt | shirt | generic |
| PLT-DA46700 | Bra | 7 invented brand holding a color or category word | Blue Otter Bra | blue | blue bra | generic |
| PLT-DA46701 | Bra | 7 invented brand holding a color or category word | White Dormouse Bra | white | white bra | generic |
| PLT-DA46702 | Bra | 7 invented brand holding a color or category word | Coat Crake Bra | coat | coat bra | generic |
| PLT-DA46703 | Bra | 7 invented brand holding a color or category word | Green Stoat Bra | green | green bra | generic |
| PLT-DA46704 | Bra | 7 invented brand holding a color or category word | Red Plover Bra | red | red bra | generic |
| PLT-DA46705 | Bra | 7 invented brand holding a color or category word | Yellow Wagtail Bra | yellow | yellow bra | generic |
| PLT-DA46706 | Bra | 7 invented brand holding a color or category word | Black Lapwing Bra | black | black bra | generic |
| PLT-DA46707 | Bra | 7 invented brand holding a color or category word | Jumper Jay Bra | jumper | jumper bra | generic |
| PLT-DA47100 | Boxers | 1 color names a part | Grey Boxers, White Trim | white | white boxers | generic |
| PLT-DA47101 | Boxers | 1 color names a part | Brown Boxers, Black Waistband | black | black boxers | generic |
| PLT-DA47102 | Boxers | 1 color names a part | Pink Boxers, White Waistband | white | white boxers | generic |
| PLT-DA47200 | Boxers | 2 another category's noun as a modifier | White Trouser Boxers | trouser | trouser | generic |
| PLT-DA47201 | Boxers | 2 another category's noun as a modifier | Grey Shirt Boxers | shirt | shirt | generic |
| PLT-DA47202 | Boxers | 2 another category's noun as a modifier | Green Short Boxers | short | short | generic |
| PLT-DA47300 | Boxers | 3 audience word of a sibling version | Grey Womens Fit Boxers | womens | womens boxers | generic |
| PLT-DA47301 | Boxers | 3 audience word of a sibling version | Grey Womens-Style Boxers | womens | womens boxers | generic |
| PLT-DA47302 | Boxers | 3 audience word of a sibling version | Red Girls Fit Boxers | girls | girls boxers | generic |
| PLT-DA47400 | Boxers | 4 material or feature named but absent | Navy Leather-Look Boxers | leather | leather boxers | special: material claim |
| PLT-DA47401 | Boxers | 4 material or feature named but absent | Cream Suede-Look Boxers | suede | suede boxers | special: material claim |
| PLT-DA47402 | Boxers | 4 material or feature named but absent | Cream Cashmere-Feel Boxers | cashmere | cashmere boxers | special: material claim |
| PLT-DA47500 | Boxers | 5 shade spelled in the description only | Moonbeam Boxers | ivory | ivory boxers | generic |
| PLT-DA47501 | Boxers | 5 shade spelled in the description only | Driftwood Boxers | taupe | taupe boxers | generic |
| PLT-DA47502 | Boxers | 5 shade spelled in the description only | Dune Boxers | beige | beige boxers | generic |
| PLT-DA47600 | Boxers | 6 incidental word in a range name | White Cliff Boxers | white | white boxers | generic |
| PLT-DA47601 | Boxers | 6 incidental word in a range name | Red Fern Boxers | red | red boxers | generic |
| PLT-DA47602 | Boxers | 6 incidental word in a range name | Black Mill Boxers | black | black boxers | generic |
| PLT-DA47603 | Boxers | 6 incidental word in a range name | Sock Hop Boxers | sock | sock | generic |
| PLT-DA47700 | Boxers | 7 invented brand holding a color or category word | Coat Crake Boxers | coat | coat boxers | generic |
| PLT-DA47701 | Boxers | 7 invented brand holding a color or category word | Blue Otter Boxers | blue | blue boxers | generic |
| PLT-DA47702 | Boxers | 7 invented brand holding a color or category word | Black Lapwing Boxers | black | black boxers | generic |
| PLT-DA48100 | Dressing Gown | 1 color names a part | Pink Dressing Gown, White Waistband | white | white dressing gown | generic |
| PLT-DA48101 | Dressing Gown | 1 color names a part | Red Dressing Gown, Blue Piping | blue | blue dressing gown | generic |
| PLT-DA48102 | Dressing Gown | 1 color names a part | Brown Dressing Gown, White Cuffs | white | white dressing gown | generic |
| PLT-DA48200 | Dressing Gown | 2 another category's noun as a modifier | Cream Top Dressing Gown | top | top | generic |
| PLT-DA48201 | Dressing Gown | 2 another category's noun as a modifier | White Top Dressing Gown | top | top | generic |
| PLT-DA48202 | Dressing Gown | 2 another category's noun as a modifier | Green Vest Dressing Gown | vest | vest | generic |
| PLT-DA48300 | Dressing Gown | 3 audience word of a sibling version | Cream Boys Fit Dressing Gown | boys | boys dressing gown | generic |
| PLT-DA48301 | Dressing Gown | 3 audience word of a sibling version | Brown Mens Fit Dressing Gown | mens | mens dressing gown | generic |
| PLT-DA48302 | Dressing Gown | 3 audience word of a sibling version | Pink Mini-Me Womens Dressing Gown | womens | womens dressing gown | generic |
| PLT-DA48400 | Dressing Gown | 4 material or feature named but absent | Cream Leather-Look Dressing Gown | leather | leather dressing gown | special: material claim |
| PLT-DA48401 | Dressing Gown | 4 material or feature named but absent | Pink Suede-Look Dressing Gown | suede | suede dressing gown | special: material claim |
| PLT-DA48402 | Dressing Gown | 4 material or feature named but absent | Grey Cashmere-Feel Dressing Gown | cashmere | cashmere dressing gown | special: material claim |
| PLT-DA48500 | Dressing Gown | 5 shade spelled in the description only | Moonbeam Dressing Gown | ivory | ivory dressing gown | generic |
| PLT-DA48501 | Dressing Gown | 5 shade spelled in the description only | Driftwood Dressing Gown | taupe | taupe dressing gown | generic |
| PLT-DA48502 | Dressing Gown | 5 shade spelled in the description only | Dune Dressing Gown | beige | beige dressing gown | generic |
| PLT-DA48600 | Dressing Gown | 6 incidental word in a range name | Yellow Marsh Dressing Gown | yellow | yellow dressing gown | generic |
| PLT-DA48601 | Dressing Gown | 6 incidental word in a range name | Red Harbour Dressing Gown | red | red dressing gown | generic |
| PLT-DA48602 | Dressing Gown | 6 incidental word in a range name | White Cliff Dressing Gown | white | white dressing gown | generic |
| PLT-DA48603 | Dressing Gown | 6 incidental word in a range name | Jumper Lane Dressing Gown | jumper | jumper | generic |
| PLT-DA48700 | Dressing Gown | 7 invented brand holding a color or category word | Black Lapwing Dressing Gown | black | black dressing gown | generic |
| PLT-DA48701 | Dressing Gown | 7 invented brand holding a color or category word | Green Stoat Dressing Gown | green | green dressing gown | generic |
| PLT-DA48702 | Dressing Gown | 7 invented brand holding a color or category word | Coat Crake Dressing Gown | coat | coat dressing gown | generic |
| PLT-DA49100 | Knickers | 1 color names a part | White Knickers, Yellow Piping | yellow | yellow knickers | generic |
| PLT-DA49101 | Knickers | 1 color names a part | Grey Knickers, Yellow Piping | yellow | yellow knickers | generic |
| PLT-DA49102 | Knickers | 1 color names a part | Grey Knickers, Red Trim | red | red knickers | generic |
| PLT-DA49200 | Knickers | 2 another category's noun as a modifier | Brown Top Knickers | top | top | generic |
| PLT-DA49201 | Knickers | 2 another category's noun as a modifier | Blue Bra Knickers | bra | bra | generic |
| PLT-DA49202 | Knickers | 2 another category's noun as a modifier | Blue Trouser Knickers | trouser | trouser | generic |
| PLT-DA49300 | Knickers | 3 audience word of a sibling version | White Mens-Style Knickers | mens | mens knickers | generic |
| PLT-DA49301 | Knickers | 3 audience word of a sibling version | Pink Boys Fit Knickers | boys | boys knickers | generic |
| PLT-DA49302 | Knickers | 3 audience word of a sibling version | Cream Mens Fit Knickers | mens | mens knickers | generic |
| PLT-DA49400 | Knickers | 4 material or feature named but absent | Green Leather-Look Knickers | leather | leather knickers | special: material claim |
| PLT-DA49401 | Knickers | 4 material or feature named but absent | Navy Suede-Look Knickers | suede | suede knickers | special: material claim |
| PLT-DA49402 | Knickers | 4 material or feature named but absent | White Cashmere-Feel Knickers | cashmere | cashmere knickers | special: material claim |
| PLT-DA49500 | Knickers | 5 shade spelled in the description only | Moonbeam Knickers | ivory | ivory knickers | generic |
| PLT-DA49501 | Knickers | 5 shade spelled in the description only | Driftwood Knickers | taupe | taupe knickers | generic |
| PLT-DA49502 | Knickers | 5 shade spelled in the description only | Dune Knickers | beige | beige knickers | generic |
| PLT-DA49600 | Knickers | 6 incidental word in a range name | Blue Meadow Knickers | blue | blue knickers | generic |
| PLT-DA49601 | Knickers | 6 incidental word in a range name | Yellow Brook Knickers | yellow | yellow knickers | generic |
| PLT-DA49602 | Knickers | 6 incidental word in a range name | Green Park Knickers | green | green knickers | generic |
| PLT-DA49603 | Knickers | 6 incidental word in a range name | Shirt Row Knickers | shirt | shirt | generic |
| PLT-DA49700 | Knickers | 7 invented brand holding a color or category word | Yellow Wagtail Knickers | yellow | yellow knickers | generic |
| PLT-DA49701 | Knickers | 7 invented brand holding a color or category word | Red Plover Knickers | red | red knickers | generic |
| PLT-DA49702 | Knickers | 7 invented brand holding a color or category word | Blue Otter Knickers | blue | blue knickers | generic |
| PLT-DA50100 | Pyjama Shorts | 1 color names a part | Pink Pyjama Shorts, White Piping | white | white pyjama shorts | generic |
| PLT-DA50101 | Pyjama Shorts | 1 color names a part | Brown Pyjama Shorts, Green Waistband | green | green pyjama shorts | generic |
| PLT-DA50102 | Pyjama Shorts | 1 color names a part | Navy Pyjama Shorts, White Cuffs | white | white pyjama shorts | generic |
| PLT-DA50200 | Pyjama Shorts | 2 another category's noun as a modifier | Black Vest Pyjama Shorts | vest | vest | generic |
| PLT-DA50201 | Pyjama Shorts | 2 another category's noun as a modifier | Pink Shirt Pyjama Shorts | shirt | shirt | generic |
| PLT-DA50202 | Pyjama Shorts | 2 another category's noun as a modifier | Black Top Pyjama Shorts | top | top | generic |
| PLT-DA50300 | Pyjama Shorts | 3 audience word of a sibling version | Cream Mens-Style Pyjama Shorts | mens | mens pyjama shorts | generic |
| PLT-DA50301 | Pyjama Shorts | 3 audience word of a sibling version | Grey Boys Fit Pyjama Shorts | boys | boys pyjama shorts | generic |
| PLT-DA50302 | Pyjama Shorts | 3 audience word of a sibling version | Red Boys Fit Pyjama Shorts | boys | boys pyjama shorts | generic |
| PLT-DA50400 | Pyjama Shorts | 4 material or feature named but absent | Navy Leather-Look Pyjama Shorts | leather | leather pyjama shorts | special: material claim |
| PLT-DA50401 | Pyjama Shorts | 4 material or feature named but absent | Pink Suede-Look Pyjama Shorts | suede | suede pyjama shorts | special: material claim |
| PLT-DA50402 | Pyjama Shorts | 4 material or feature named but absent | Blue Cashmere-Feel Pyjama Shorts | cashmere | cashmere pyjama shorts | special: material claim |
| PLT-DA50500 | Pyjama Shorts | 5 shade spelled in the description only | Moonbeam Pyjama Shorts | ivory | ivory pyjama shorts | generic |
| PLT-DA50501 | Pyjama Shorts | 5 shade spelled in the description only | Driftwood Pyjama Shorts | taupe | taupe pyjama shorts | generic |
| PLT-DA50502 | Pyjama Shorts | 5 shade spelled in the description only | Dune Pyjama Shorts | beige | beige pyjama shorts | generic |
| PLT-DA50600 | Pyjama Shorts | 6 incidental word in a range name | White Moor Pyjama Shorts | white | white pyjama shorts | generic |
| PLT-DA50601 | Pyjama Shorts | 6 incidental word in a range name | Black Mill Pyjama Shorts | black | black pyjama shorts | generic |
| PLT-DA50602 | Pyjama Shorts | 6 incidental word in a range name | Green Hollow Pyjama Shorts | green | green pyjama shorts | generic |
| PLT-DA50603 | Pyjama Shorts | 6 incidental word in a range name | Dress Circle Pyjama Shorts | dress | dress | generic |
| PLT-DA50700 | Pyjama Shorts | 7 invented brand holding a color or category word | Green Stoat Pyjama Shorts | green | green pyjama shorts | generic |
| PLT-DA50701 | Pyjama Shorts | 7 invented brand holding a color or category word | Jumper Jay Pyjama Shorts | jumper | jumper pyjama shorts | generic |
| PLT-DA50702 | Pyjama Shorts | 7 invented brand holding a color or category word | White Dormouse Pyjama Shorts | white | white pyjama shorts | generic |
| PLT-DA51100 | Pyjamas | 1 color names a part | Pink Pyjamas, White Cuffs | white | white pyjamas | generic |
| PLT-DA51101 | Pyjamas | 1 color names a part | White Pyjamas, Blue Trim | blue | blue pyjamas | generic |
| PLT-DA51102 | Pyjamas | 1 color names a part | Black Pyjamas, Red Piping | red | red pyjamas | generic |
| PLT-DA51200 | Pyjamas | 2 another category's noun as a modifier | Red Dress Pyjamas | dress | dress | generic |
| PLT-DA51201 | Pyjamas | 2 another category's noun as a modifier | Pink Skirt Pyjamas | skirt | skirt | generic |
| PLT-DA51202 | Pyjamas | 2 another category's noun as a modifier | Brown Skirt Pyjamas | skirt | skirt | generic |
| PLT-DA51300 | Pyjamas | 3 audience word of a sibling version | Green Mini-Me Mens Pyjamas | mens | mens pyjamas | generic |
| PLT-DA51301 | Pyjamas | 3 audience word of a sibling version | Red Mini-Me Mens Pyjamas | mens | mens pyjamas | generic |
| PLT-DA51302 | Pyjamas | 3 audience word of a sibling version | White Mini-Me Womens Pyjamas | womens | womens pyjamas | generic |
| PLT-DA51400 | Pyjamas | 4 material or feature named but absent | Black Leather-Look Pyjamas | leather | leather pyjamas | special: material claim |
| PLT-DA51401 | Pyjamas | 4 material or feature named but absent | Grey Suede-Look Pyjamas | suede | suede pyjamas | special: material claim |
| PLT-DA51402 | Pyjamas | 4 material or feature named but absent | Red Cashmere-Feel Pyjamas | cashmere | cashmere pyjamas | special: material claim |
| PLT-DA51500 | Pyjamas | 5 shade spelled in the description only | Moonbeam Pyjamas | ivory | ivory pyjamas | generic |
| PLT-DA51501 | Pyjamas | 5 shade spelled in the description only | Driftwood Pyjamas | taupe | taupe pyjamas | generic |
| PLT-DA51502 | Pyjamas | 5 shade spelled in the description only | Dune Pyjamas | beige | beige pyjamas | generic |
| PLT-DA51600 | Pyjamas | 6 incidental word in a range name | Yellow Brook Pyjamas | yellow | yellow pyjamas | generic |
| PLT-DA51601 | Pyjamas | 6 incidental word in a range name | Yellow Marsh Pyjamas | yellow | yellow pyjamas | generic |
| PLT-DA51602 | Pyjamas | 6 incidental word in a range name | Green Park Pyjamas | green | green pyjamas | generic |
| PLT-DA51603 | Pyjamas | 6 incidental word in a range name | Dress Circle Pyjamas | dress | dress | generic |
| PLT-DA51700 | Pyjamas | 7 invented brand holding a color or category word | Coat Crake Pyjamas | coat | coat pyjamas | generic |
| PLT-DA51701 | Pyjamas | 7 invented brand holding a color or category word | Red Plover Pyjamas | red | red pyjamas | generic |
| PLT-DA51702 | Pyjamas | 7 invented brand holding a color or category word | Green Stoat Pyjamas | green | green pyjamas | generic |
| PLT-DA52100 | Shapewear | 1 color names a part | Cream Shapewear, Green Cuffs | green | green shapewear | generic |
| PLT-DA52101 | Shapewear | 1 color names a part | Green Shapewear, Blue Piping | blue | blue shapewear | generic |
| PLT-DA52102 | Shapewear | 1 color names a part | Pink Shapewear, Green Bow | green | green shapewear | generic |
| PLT-DA52200 | Shapewear | 2 another category's noun as a modifier | Grey Short Shapewear | short | short | generic |
| PLT-DA52201 | Shapewear | 2 another category's noun as a modifier | Navy Cami Shapewear | cami | cami | generic |
| PLT-DA52202 | Shapewear | 2 another category's noun as a modifier | Brown Top Shapewear | top | top | generic |
| PLT-DA52300 | Shapewear | 3 audience word of a sibling version | Brown Mens-Style Shapewear | mens | mens shapewear | generic |
| PLT-DA52301 | Shapewear | 3 audience word of a sibling version | Navy Mens Fit Shapewear | mens | mens shapewear | generic |
| PLT-DA52302 | Shapewear | 3 audience word of a sibling version | Pink Mens Fit Shapewear | mens | mens shapewear | generic |
| PLT-DA52400 | Shapewear | 4 material or feature named but absent | Green Leather-Look Shapewear | leather | leather shapewear | special: material claim |
| PLT-DA52401 | Shapewear | 4 material or feature named but absent | White Suede-Look Shapewear | suede | suede shapewear | special: material claim |
| PLT-DA52402 | Shapewear | 4 material or feature named but absent | Grey Cashmere-Feel Shapewear | cashmere | cashmere shapewear | special: material claim |
| PLT-DA52500 | Shapewear | 5 shade spelled in the description only | Moonbeam Shapewear | ivory | ivory shapewear | generic |
| PLT-DA52501 | Shapewear | 5 shade spelled in the description only | Driftwood Shapewear | taupe | taupe shapewear | generic |
| PLT-DA52502 | Shapewear | 5 shade spelled in the description only | Dune Shapewear | beige | beige shapewear | generic |
| PLT-DA52600 | Shapewear | 6 incidental word in a range name | Black Tor Shapewear | black | black shapewear | generic |
| PLT-DA52601 | Shapewear | 6 incidental word in a range name | White Moor Shapewear | white | white shapewear | generic |
| PLT-DA52602 | Shapewear | 6 incidental word in a range name | Blue Meadow Shapewear | blue | blue shapewear | generic |
| PLT-DA52603 | Shapewear | 6 incidental word in a range name | Sock Hop Shapewear | sock | sock | generic |
| PLT-DA52700 | Shapewear | 7 invented brand holding a color or category word | Red Plover Shapewear | red | red shapewear | generic |
| PLT-DA52701 | Shapewear | 7 invented brand holding a color or category word | Coat Crake Shapewear | coat | coat shapewear | generic |
| PLT-DA52702 | Shapewear | 7 invented brand holding a color or category word | Black Lapwing Shapewear | black | black shapewear | generic |
| PLT-DA53100 | Slip | 1 color names a part | Grey Slip, Red Waistband | red | red slip | generic |
| PLT-DA53101 | Slip | 1 color names a part | Blue Slip, Yellow Trim | yellow | yellow slip | generic |
| PLT-DA53102 | Slip | 1 color names a part | White Slip, Black Piping | black | black slip | generic |
| PLT-DA53200 | Slip | 2 another category's noun as a modifier | Black Bra Slip | bra | bra | generic |
| PLT-DA53201 | Slip | 2 another category's noun as a modifier | Green Trouser Slip | trouser | trouser | generic |
| PLT-DA53202 | Slip | 2 another category's noun as a modifier | Blue Shirt Slip | shirt | shirt | generic |
| PLT-DA53300 | Slip | 3 audience word of a sibling version | Brown Mens Fit Slip | mens | mens slip | generic |
| PLT-DA53301 | Slip | 3 audience word of a sibling version | White Boys Fit Slip | boys | boys slip | generic |
| PLT-DA53302 | Slip | 3 audience word of a sibling version | Blue Mens-Style Slip | mens | mens slip | generic |
| PLT-DA53400 | Slip | 4 material or feature named but absent | Grey Leather-Look Slip | leather | leather slip | special: material claim |
| PLT-DA53401 | Slip | 4 material or feature named but absent | Red Suede-Look Slip | suede | suede slip | special: material claim |
| PLT-DA53402 | Slip | 4 material or feature named but absent | Red Cashmere-Feel Slip | cashmere | cashmere slip | special: material claim |
| PLT-DA53500 | Slip | 5 shade spelled in the description only | Moonbeam Slip | ivory | ivory slip | generic |
| PLT-DA53501 | Slip | 5 shade spelled in the description only | Driftwood Slip | taupe | taupe slip | generic |
| PLT-DA53502 | Slip | 5 shade spelled in the description only | Dune Slip | beige | beige slip | generic |
| PLT-DA53600 | Slip | 6 incidental word in a range name | White Moor Slip | white | white slip | generic |
| PLT-DA53601 | Slip | 6 incidental word in a range name | Red Fern Slip | red | red slip | generic |
| PLT-DA53602 | Slip | 6 incidental word in a range name | Black Mill Slip | black | black slip | generic |
| PLT-DA53603 | Slip | 6 incidental word in a range name | Coat Hook Slip | coat | coat | generic |
| PLT-DA53700 | Slip | 7 invented brand holding a color or category word | Jumper Jay Slip | jumper | jumper slip | generic |
| PLT-DA53701 | Slip | 7 invented brand holding a color or category word | Blue Otter Slip | blue | blue slip | generic |
| PLT-DA53702 | Slip | 7 invented brand holding a color or category word | Green Stoat Slip | green | green slip | generic |
| PLT-DA54100 | Tights | 1 color names a part | Cream Tights, Yellow Cuffs | yellow | yellow tights | generic |
| PLT-DA54101 | Tights | 1 color names a part | Blue Tights, Green Piping | green | green tights | generic |
| PLT-DA54102 | Tights | 1 color names a part | Navy Tights, Blue Stitching | blue | blue tights | generic |
| PLT-DA54200 | Tights | 2 another category's noun as a modifier | Green Skirt Tights | skirt | skirt | generic |
| PLT-DA54201 | Tights | 2 another category's noun as a modifier | Grey Short Tights | short | short | generic |
| PLT-DA54202 | Tights | 2 another category's noun as a modifier | Blue Dress Tights | dress | dress | generic |
| PLT-DA54300 | Tights | 3 audience word of a sibling version | Pink Boys Fit Tights | boys | boys tights | generic |
| PLT-DA54301 | Tights | 3 audience word of a sibling version | Green Mens-Style Tights | mens | mens tights | generic |
| PLT-DA54302 | Tights | 3 audience word of a sibling version | Blue Mens Fit Tights | mens | mens tights | generic |
| PLT-DA54400 | Tights | 4 material or feature named but absent | Navy Leather-Look Tights | leather | leather tights | special: material claim |
| PLT-DA54401 | Tights | 4 material or feature named but absent | Blue Suede-Look Tights | suede | suede tights | special: material claim |
| PLT-DA54402 | Tights | 4 material or feature named but absent | Brown Cashmere-Feel Tights | cashmere | cashmere tights | special: material claim |
| PLT-DA54500 | Tights | 5 shade spelled in the description only | Moonbeam Tights | ivory | ivory tights | generic |
| PLT-DA54501 | Tights | 5 shade spelled in the description only | Driftwood Tights | taupe | taupe tights | generic |
| PLT-DA54502 | Tights | 5 shade spelled in the description only | Dune Tights | beige | beige tights | generic |
| PLT-DA54600 | Tights | 6 incidental word in a range name | Yellow Marsh Tights | yellow | yellow tights | generic |
| PLT-DA54601 | Tights | 6 incidental word in a range name | White Moor Tights | white | white tights | generic |
| PLT-DA54602 | Tights | 6 incidental word in a range name | Yellow Brook Tights | yellow | yellow tights | generic |
| PLT-DA54603 | Tights | 6 incidental word in a range name | Jumper Lane Tights | jumper | jumper | generic |
| PLT-DA54700 | Tights | 7 invented brand holding a color or category word | Jumper Jay Tights | jumper | jumper tights | generic |
| PLT-DA54701 | Tights | 7 invented brand holding a color or category word | Red Plover Tights | red | red tights | generic |
| PLT-DA54702 | Tights | 7 invented brand holding a color or category word | Coat Crake Tights | coat | coat tights | generic |
| PLT-DA55100 | Vest | 1 color names a part | Brown Vest, Blue Waistband | blue | blue vest | generic |
| PLT-DA55101 | Vest | 1 color names a part | Pink Vest, Green Cuffs | green | green vest | generic |
| PLT-DA55102 | Vest | 1 color names a part | Brown Vest, Green Cuffs | green | green vest | generic |
| PLT-DA55200 | Vest | 2 another category's noun as a modifier | Grey Cami Vest | cami | cami | generic |
| PLT-DA55201 | Vest | 2 another category's noun as a modifier | Green Trouser Vest | trouser | trouser | generic |
| PLT-DA55202 | Vest | 2 another category's noun as a modifier | Black Skirt Vest | skirt | skirt | generic |
| PLT-DA55300 | Vest | 3 audience word of a sibling version | White Womens Fit Vest | womens | womens vest | generic |
| PLT-DA55301 | Vest | 3 audience word of a sibling version | Grey Mens Fit Vest | mens | mens vest | generic |
| PLT-DA55302 | Vest | 3 audience word of a sibling version | Brown Boys Fit Vest | boys | boys vest | generic |
| PLT-DA55400 | Vest | 4 material or feature named but absent | Red Leather-Look Vest | leather | leather vest | special: material claim |
| PLT-DA55401 | Vest | 4 material or feature named but absent | Brown Suede-Look Vest | suede | suede vest | special: material claim |
| PLT-DA55402 | Vest | 4 material or feature named but absent | Red Cashmere-Feel Vest | cashmere | cashmere vest | special: material claim |
| PLT-DA55500 | Vest | 5 shade spelled in the description only | Moonbeam Vest | ivory | ivory vest | generic |
| PLT-DA55501 | Vest | 5 shade spelled in the description only | Driftwood Vest | taupe | taupe vest | generic |
| PLT-DA55502 | Vest | 5 shade spelled in the description only | Dune Vest | beige | beige vest | generic |
| PLT-DA55600 | Vest | 6 incidental word in a range name | Black Tor Vest | black | black vest | generic |
| PLT-DA55601 | Vest | 6 incidental word in a range name | Red Harbour Vest | red | red vest | generic |
| PLT-DA55602 | Vest | 6 incidental word in a range name | Black Mill Vest | black | black vest | generic |
| PLT-DA55603 | Vest | 6 incidental word in a range name | Sock Hop Vest | sock | sock | generic |
| PLT-DA55700 | Vest | 7 invented brand holding a color or category word | Coat Crake Vest | coat | coat vest | generic |
| PLT-DA55701 | Vest | 7 invented brand holding a color or category word | Yellow Wagtail Vest | yellow | yellow vest | generic |
| PLT-DA55702 | Vest | 7 invented brand holding a color or category word | Red Plover Vest | red | red vest | generic |

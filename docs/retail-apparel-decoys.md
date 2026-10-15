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
| PLT-DA00300 | Blouse | 3 audience word of a sibling version | Green Womens Blouse, Mens-Style | mens | mens blouse | generic |
| PLT-DA00301 | Blouse | 3 audience word of a sibling version | Brown Womens Blouse, Boys Fit | boys | boys blouse | generic |
| PLT-DA00302 | Blouse | 3 audience word of a sibling version | Navy Womens Blouse, Mens Fit | mens | mens blouse | generic |
| PLT-DA00400 | Blouse | 4 material or feature named but absent | Black Leather-Look Blouse, Crepe | leather | leather blouse | special: material claim |
| PLT-DA00401 | Blouse | 4 material or feature named but absent | Blue Suede-Look Blouse, Satin | suede | suede blouse | special: material claim |
| PLT-DA00402 | Blouse | 4 material or feature named but absent | Brown Cashmere-Feel Blouse | cashmere | cashmere blouse | special: material claim |
| PLT-DA00500 | Blouse | 5 shade spelled in the description only | Moonbeam Blouse | ivory | ivory blouse | generic |
| PLT-DA00501 | Blouse | 5 shade spelled in the description only | Driftwood Blouse | taupe | taupe blouse | generic |
| PLT-DA00502 | Blouse | 5 shade spelled in the description only | Dune Blouse | beige | beige blouse | generic |
| PLT-DA00600 | Blouse | 6 incidental word in a range name | Green Park Blouse, Grey | green | green blouse | generic |
| PLT-DA00601 | Blouse | 6 incidental word in a range name | Black Tor Blouse, Red | black | black blouse | generic |
| PLT-DA00602 | Blouse | 6 incidental word in a range name | Yellow Marsh Blouse, White | yellow | yellow blouse | generic |
| PLT-DA00603 | Blouse | 6 incidental word in a range name | Skirt Point Blouse, White | skirt | skirt | generic |
| PLT-DA00700 | Blouse | 7 invented brand holding a color or category word | Blue Otter Blouse, Red | blue | blue blouse | generic |
| PLT-DA00701 | Blouse | 7 invented brand holding a color or category word | White Dormouse Blouse, Pink | white | white blouse | generic |
| PLT-DA00702 | Blouse | 7 invented brand holding a color or category word | Green Stoat Blouse, White | green | green blouse | generic |
| PLT-DA01100 | Bodysuit | 1 color names a part | Pink Bodysuit, Yellow Lining | yellow | yellow bodysuit | generic |
| PLT-DA01101 | Bodysuit | 1 color names a part | Cream Bodysuit, Red Stitching | red | red bodysuit | generic |
| PLT-DA01102 | Bodysuit | 1 color names a part | Red Bodysuit, Yellow Collar | yellow | yellow bodysuit | generic |
| PLT-DA01200 | Bodysuit | 2 another category's noun as a modifier | Pink Gilet Bodysuit | gilet | gilet | generic |
| PLT-DA01201 | Bodysuit | 2 another category's noun as a modifier | Black Vest Bodysuit | vest | vest | generic |
| PLT-DA01202 | Bodysuit | 2 another category's noun as a modifier | Black Skirt Bodysuit | skirt | skirt | generic |
| PLT-DA01300 | Bodysuit | 3 audience word of a sibling version | Blue Womens Bodysuit, Mens Fit | mens | mens bodysuit | generic |
| PLT-DA01301 | Bodysuit | 3 audience word of a sibling version | Black Womens Bodysuit, Boys Fit | boys | boys bodysuit | generic |
| PLT-DA01302 | Bodysuit | 3 audience word of a sibling version | Brown Womens Bodysuit, Boys Fit | boys | boys bodysuit | generic |
| PLT-DA01400 | Bodysuit | 4 material or feature named but absent | Brown Leather-Look Bodysuit | leather | leather bodysuit | special: material claim |
| PLT-DA01401 | Bodysuit | 4 material or feature named but absent | Brown Suede-Look Bodysuit | suede | suede bodysuit | special: material claim |
| PLT-DA01402 | Bodysuit | 4 material or feature named but absent | Green Cashmere-Feel Bodysuit | cashmere | cashmere bodysuit | special: material claim |
| PLT-DA01500 | Bodysuit | 5 shade spelled in the description only | Moonbeam Bodysuit | ivory | ivory bodysuit | generic |
| PLT-DA01501 | Bodysuit | 5 shade spelled in the description only | Driftwood Bodysuit | taupe | taupe bodysuit | generic |
| PLT-DA01502 | Bodysuit | 5 shade spelled in the description only | Dune Bodysuit | beige | beige bodysuit | generic |
| PLT-DA01600 | Bodysuit | 6 incidental word in a range name | Green Park Bodysuit, Brown | green | green bodysuit | generic |
| PLT-DA01601 | Bodysuit | 6 incidental word in a range name | Yellow Marsh Bodysuit, Black | yellow | yellow bodysuit | generic |
| PLT-DA01602 | Bodysuit | 6 incidental word in a range name | Black Mill Bodysuit, Navy | black | black bodysuit | generic |
| PLT-DA01603 | Bodysuit | 6 incidental word in a range name | Shirt Row Bodysuit, Green | shirt | shirt | generic |
| PLT-DA01700 | Bodysuit | 7 invented brand holding a color or category word | Coat Crake Bodysuit, Cream | coat | coat bodysuit | generic |
| PLT-DA01701 | Bodysuit | 7 invented brand holding a color or category word | Green Stoat Bodysuit, Blue | green | green bodysuit | generic |
| PLT-DA01702 | Bodysuit | 7 invented brand holding a color or category word | Black Lapwing Bodysuit, Grey | black | black bodysuit | generic |
| PLT-DA02100 | Bomber Jacket | 1 color names a part | Green Bomber Jacket, Red Collar | red | red bomber jacket | generic |
| PLT-DA02101 | Bomber Jacket | 1 color names a part | Red Bomber Jacket, Green Zip | green | green bomber jacket | generic |
| PLT-DA02102 | Bomber Jacket | 1 color names a part | Brown Bomber Jacket, Blue Trim | blue | blue bomber jacket | generic |
| PLT-DA02200 | Bomber Jacket | 2 another category's noun as a modifier | Cream Cardigan Bomber Jacket | cardigan | cardigan | generic |
| PLT-DA02201 | Bomber Jacket | 2 another category's noun as a modifier | Grey Jumper Bomber Jacket | jumper | jumper | generic |
| PLT-DA02202 | Bomber Jacket | 2 another category's noun as a modifier | Pink Dress Bomber Jacket | dress | dress | generic |
| PLT-DA02300 | Bomber Jacket | 3 audience word of a sibling version | Grey Boys Bomber Jacket, Mini-Me Mens | mens | mens bomber jacket | generic |
| PLT-DA02301 | Bomber Jacket | 3 audience word of a sibling version | Grey Baby Bomber Jacket, Mini-Me Mens | mens | mens bomber jacket | generic |
| PLT-DA02302 | Bomber Jacket | 3 audience word of a sibling version | Grey Womens Bomber Jacket, Mens Fit | mens | mens bomber jacket | generic |
| PLT-DA02400 | Bomber Jacket | 4 material or feature named but absent | Black Leather-Look Bomber Jacket | leather | leather bomber jacket | special: material claim |
| PLT-DA02401 | Bomber Jacket | 4 material or feature named but absent | White Suede-Look Bomber Jacket | suede | suede bomber jacket | special: material claim |
| PLT-DA02402 | Bomber Jacket | 4 material or feature named but absent | Grey Cashmere-Feel Bomber Jacket | cashmere | cashmere bomber jacket | special: material claim |
| PLT-DA02500 | Bomber Jacket | 5 shade spelled in the description only | Moonbeam Bomber Jacket | ivory | ivory bomber jacket | generic |
| PLT-DA02501 | Bomber Jacket | 5 shade spelled in the description only | Driftwood Bomber Jacket | taupe | taupe bomber jacket | generic |
| PLT-DA02502 | Bomber Jacket | 5 shade spelled in the description only | Dune Bomber Jacket | beige | beige bomber jacket | generic |
| PLT-DA02600 | Bomber Jacket | 6 incidental word in a range name | Red Harbour Bomber Jacket, Grey | red | red bomber jacket | generic |
| PLT-DA02601 | Bomber Jacket | 6 incidental word in a range name | Black Mill Bomber Jacket, Red | black | black bomber jacket | generic |
| PLT-DA02602 | Bomber Jacket | 6 incidental word in a range name | Blue Meadow Bomber Jacket, White | blue | blue bomber jacket | generic |
| PLT-DA02603 | Bomber Jacket | 6 incidental word in a range name | Jumper Lane Bomber Jacket, Cream | jumper | jumper | generic |
| PLT-DA02700 | Bomber Jacket | 7 invented brand holding a color or category word | White Dormouse Bomber Jacket, Navy | white | white bomber jacket | generic |
| PLT-DA02701 | Bomber Jacket | 7 invented brand holding a color or category word | Yellow Wagtail Bomber Jacket, Navy | yellow | yellow bomber jacket | generic |
| PLT-DA02702 | Bomber Jacket | 7 invented brand holding a color or category word | Red Plover Bomber Jacket, Blue | red | red bomber jacket | generic |
| PLT-DA03100 | Cardigan | 1 color names a part | Grey Cardigan, Yellow Stripes | yellow | yellow cardigan | generic |
| PLT-DA03101 | Cardigan | 1 color names a part | Green Cardigan, White Trim | white | white cardigan | generic |
| PLT-DA03102 | Cardigan | 1 color names a part | Red Cardigan, Yellow Trim | yellow | yellow cardigan | generic |
| PLT-DA03200 | Cardigan | 2 another category's noun as a modifier | Navy Poncho Cardigan | poncho | poncho | generic |
| PLT-DA03201 | Cardigan | 2 another category's noun as a modifier | Blue Skirt Cardigan | skirt | skirt | generic |
| PLT-DA03202 | Cardigan | 2 another category's noun as a modifier | White Shirt Cardigan | shirt | shirt | generic |
| PLT-DA03300 | Cardigan | 3 audience word of a sibling version | Red Womens Cardigan, Boys Fit | boys | boys cardigan | generic |
| PLT-DA03301 | Cardigan | 3 audience word of a sibling version | Brown Womens Cardigan, Mens Fit | mens | mens cardigan | generic |
| PLT-DA03302 | Cardigan | 3 audience word of a sibling version | White Womens Cardigan, Boys Fit | boys | boys cardigan | generic |
| PLT-DA03400 | Cardigan | 4 material or feature named but absent | Pink Leather-Look Cardigan | leather | leather cardigan | special: material claim |
| PLT-DA03401 | Cardigan | 4 material or feature named but absent | Blue Suede-Look Cardigan, Acrylic Blend | suede | suede cardigan | special: material claim |
| PLT-DA03402 | Cardigan | 4 material or feature named but absent | Black Cashmere-Feel Cardigan, Cotton Blend | cashmere | cashmere cardigan | special: material claim |
| PLT-DA03500 | Cardigan | 5 shade spelled in the description only | Moonbeam Cardigan | ivory | ivory cardigan | generic |
| PLT-DA03501 | Cardigan | 5 shade spelled in the description only | Driftwood Cardigan | taupe | taupe cardigan | generic |
| PLT-DA03502 | Cardigan | 5 shade spelled in the description only | Dune Cardigan | beige | beige cardigan | generic |
| PLT-DA03600 | Cardigan | 6 incidental word in a range name | Green Park Cardigan, Brown | green | green cardigan | generic |
| PLT-DA03601 | Cardigan | 6 incidental word in a range name | White Moor Cardigan, Green | white | white cardigan | generic |
| PLT-DA03602 | Cardigan | 6 incidental word in a range name | Red Harbour Cardigan, Pink | red | red cardigan | generic |
| PLT-DA03603 | Cardigan | 6 incidental word in a range name | Skirt Point Cardigan, Cream | skirt | skirt | generic |
| PLT-DA03700 | Cardigan | 7 invented brand holding a color or category word | Red Plover Cardigan, Black | red | red cardigan | generic |
| PLT-DA03701 | Cardigan | 7 invented brand holding a color or category word | Blue Otter Cardigan, Red | blue | blue cardigan | generic |
| PLT-DA03702 | Cardigan | 7 invented brand holding a color or category word | Yellow Wagtail Cardigan, White | yellow | yellow cardigan | generic |
| PLT-DA04100 | Coat | 1 color names a part | Brown Coat, Blue Buttons | blue | blue coat | generic |
| PLT-DA04101 | Coat | 1 color names a part | Brown Coat, White Stripes | white | white coat | generic |
| PLT-DA04102 | Coat | 1 color names a part | Blue Coat, White Cuffs | white | white coat | generic |
| PLT-DA04200 | Coat | 2 another category's noun as a modifier | Grey Blazer Coat | blazer | blazer | generic |
| PLT-DA04201 | Coat | 2 another category's noun as a modifier | Green Tunic Coat | tunic | tunic | generic |
| PLT-DA04202 | Coat | 2 another category's noun as a modifier | Brown Tunic Coat | tunic | tunic | generic |
| PLT-DA04300 | Coat | 3 audience word of a sibling version | Pink Womens Coat, Mens-Style | mens | mens coat | generic |
| PLT-DA04301 | Coat | 3 audience word of a sibling version | White Womens Coat, Boys Fit | boys | boys coat | generic |
| PLT-DA04302 | Coat | 3 audience word of a sibling version | Black Womens Coat, Mens Fit | mens | mens coat | generic |
| PLT-DA04400 | Coat | 4 material or feature named but absent | Pink Leather-Look Coat | leather | leather coat | special: material claim |
| PLT-DA04401 | Coat | 4 material or feature named but absent | Blue Suede-Look Coat | suede | suede coat | special: material claim |
| PLT-DA04402 | Coat | 4 material or feature named but absent | Green Cashmere-Feel Coat | cashmere | cashmere coat | special: material claim |
| PLT-DA04500 | Coat | 5 shade spelled in the description only | Moonbeam Coat | ivory | ivory coat | generic |
| PLT-DA04501 | Coat | 5 shade spelled in the description only | Driftwood Coat | taupe | taupe coat | generic |
| PLT-DA04502 | Coat | 5 shade spelled in the description only | Dune Coat | beige | beige coat | generic |
| PLT-DA04600 | Coat | 6 incidental word in a range name | Green Park Coat, Black | green | green coat | generic |
| PLT-DA04601 | Coat | 6 incidental word in a range name | Blue Meadow Coat, White | blue | blue coat | generic |
| PLT-DA04602 | Coat | 6 incidental word in a range name | Black Mill Coat, Cream | black | black coat | generic |
| PLT-DA04603 | Coat | 6 incidental word in a range name | Skirt Point Coat, Grey | skirt | skirt | generic |
| PLT-DA04700 | Coat | 7 invented brand holding a color or category word | Green Stoat Coat, Blue | green | green coat | generic |
| PLT-DA04701 | Coat | 7 invented brand holding a color or category word | Yellow Wagtail Coat, Cream | yellow | yellow coat | generic |
| PLT-DA04702 | Coat | 7 invented brand holding a color or category word | Red Plover Coat, Navy | red | red coat | generic |
| PLT-DA05100 | Co-ord Set | 1 color names a part | Navy Co-ord Set, Black Trim | black | black co-ord set | generic |
| PLT-DA05101 | Co-ord Set | 1 color names a part | Grey Co-ord Set, White Lining | white | white co-ord set | generic |
| PLT-DA05102 | Co-ord Set | 1 color names a part | Navy Co-ord Set, Green Stitching | green | green co-ord set | generic |
| PLT-DA05200 | Co-ord Set | 2 another category's noun as a modifier | Pink Shirt Co-ord Set | shirt | shirt | generic |
| PLT-DA05201 | Co-ord Set | 2 another category's noun as a modifier | Brown Poncho Co-ord Set | poncho | poncho | generic |
| PLT-DA05202 | Co-ord Set | 2 another category's noun as a modifier | Brown Tunic Co-ord Set | tunic | tunic | generic |
| PLT-DA05300 | Co-ord Set | 3 audience word of a sibling version | Navy Womens Co-ord Set, Mens-Style | mens | mens co-ord set | generic |
| PLT-DA05301 | Co-ord Set | 3 audience word of a sibling version | White Womens Co-ord Set, Mens-Style | mens | mens co-ord set | generic |
| PLT-DA05302 | Co-ord Set | 3 audience word of a sibling version | White Womens Co-ord Set, Boys Fit | boys | boys co-ord set | generic |
| PLT-DA05400 | Co-ord Set | 4 material or feature named but absent | Brown Leather-Look Co-ord Set | leather | leather co-ord set | special: material claim |
| PLT-DA05401 | Co-ord Set | 4 material or feature named but absent | White Suede-Look Co-ord Set | suede | suede co-ord set | special: material claim |
| PLT-DA05402 | Co-ord Set | 4 material or feature named but absent | Pink Cashmere-Feel Co-ord Set | cashmere | cashmere co-ord set | special: material claim |
| PLT-DA05500 | Co-ord Set | 5 shade spelled in the description only | Moonbeam Co-ord Set | ivory | ivory co-ord set | generic |
| PLT-DA05501 | Co-ord Set | 5 shade spelled in the description only | Driftwood Co-ord Set | taupe | taupe co-ord set | generic |
| PLT-DA05502 | Co-ord Set | 5 shade spelled in the description only | Dune Co-ord Set | beige | beige co-ord set | generic |
| PLT-DA05600 | Co-ord Set | 6 incidental word in a range name | Black Tor Co-ord Set, Navy | black | black co-ord set | generic |
| PLT-DA05601 | Co-ord Set | 6 incidental word in a range name | Red Fern Co-ord Set, Black | red | red co-ord set | generic |
| PLT-DA05602 | Co-ord Set | 6 incidental word in a range name | White Moor Co-ord Set, Red | white | white co-ord set | generic |
| PLT-DA05603 | Co-ord Set | 6 incidental word in a range name | Jumper Lane Co-ord Set, White | jumper | jumper | generic |
| PLT-DA05700 | Co-ord Set | 7 invented brand holding a color or category word | Blue Otter Co-ord Set, Navy | blue | blue co-ord set | generic |
| PLT-DA05701 | Co-ord Set | 7 invented brand holding a color or category word | Yellow Wagtail Co-ord Set, Blue | yellow | yellow co-ord set | generic |
| PLT-DA05702 | Co-ord Set | 7 invented brand holding a color or category word | White Dormouse Co-ord Set, Grey | white | white co-ord set | generic |
| PLT-DA06100 | Cycling Shorts | 1 color names a part | Green Compression Cycling Shorts, Yellow Buttons | yellow | yellow cycling shorts | generic |
| PLT-DA06101 | Cycling Shorts | 1 color names a part | Brown Compression Cycling Shorts, Black Lining | black | black cycling shorts | generic |
| PLT-DA06102 | Cycling Shorts | 1 color names a part | Pink Compression Cycling Shorts, Black Buttons | black | black cycling shorts | generic |
| PLT-DA06200 | Cycling Shorts | 2 another category's noun as a modifier | White Tunic Compression Cycling Shorts | tunic | tunic | generic |
| PLT-DA06201 | Cycling Shorts | 2 another category's noun as a modifier | Brown Blazer Compression Cycling Shorts | blazer | blazer | generic |
| PLT-DA06202 | Cycling Shorts | 2 another category's noun as a modifier | Green Jumper Compression Cycling Shorts | jumper | jumper | generic |
| PLT-DA06300 | Cycling Shorts | 3 audience word of a sibling version | Pink Mens Compression Cycling Shorts, Girls Fit | girls | girls cycling shorts | generic |
| PLT-DA06301 | Cycling Shorts | 3 audience word of a sibling version | Grey Mens Compression Cycling Shorts, Girls Fit | girls | girls cycling shorts | generic |
| PLT-DA06302 | Cycling Shorts | 3 audience word of a sibling version | Navy Mens Compression Cycling Shorts, Girls Fit | girls | girls cycling shorts | generic |
| PLT-DA06400 | Cycling Shorts | 4 material or feature named but absent | Navy Leather-Look Compression Cycling Shorts | leather | leather cycling shorts | special: material claim |
| PLT-DA06401 | Cycling Shorts | 4 material or feature named but absent | Blue Suede-Look Compression Cycling Shorts | suede | suede cycling shorts | special: material claim |
| PLT-DA06402 | Cycling Shorts | 4 material or feature named but absent | White Cashmere-Feel Compression Cycling Shorts | cashmere | cashmere cycling shorts | special: material claim |
| PLT-DA06500 | Cycling Shorts | 5 shade spelled in the description only | Moonbeam Compression Cycling Shorts | ivory | ivory cycling shorts | generic |
| PLT-DA06501 | Cycling Shorts | 5 shade spelled in the description only | Driftwood Compression Cycling Shorts | taupe | taupe cycling shorts | generic |
| PLT-DA06502 | Cycling Shorts | 5 shade spelled in the description only | Dune Compression Cycling Shorts | beige | beige cycling shorts | generic |
| PLT-DA06600 | Cycling Shorts | 6 incidental word in a range name | Blue Cove Compression Cycling Shorts, White | blue | blue cycling shorts | generic |
| PLT-DA06601 | Cycling Shorts | 6 incidental word in a range name | Green Park Compression Cycling Shorts, Blue | green | green cycling shorts | generic |
| PLT-DA06602 | Cycling Shorts | 6 incidental word in a range name | Black Tor Compression Cycling Shorts, Grey | black | black cycling shorts | generic |
| PLT-DA06603 | Cycling Shorts | 6 incidental word in a range name | Shirt Row Compression Cycling Shorts, Blue | shirt | shirt | generic |
| PLT-DA06700 | Cycling Shorts | 7 invented brand holding a color or category word | Red Plover Compression Cycling Shorts, Grey | red | red cycling shorts | generic |
| PLT-DA06701 | Cycling Shorts | 7 invented brand holding a color or category word | Yellow Wagtail Compression Cycling Shorts, Cream | yellow | yellow cycling shorts | generic |
| PLT-DA06702 | Cycling Shorts | 7 invented brand holding a color or category word | Coat Crake Compression Cycling Shorts, Cream | coat | coat cycling shorts | generic |
| PLT-DA07100 | Denim Jacket | 1 color names a part | Pink Denim Jacket, Red Piping | red | red denim jacket | generic |
| PLT-DA07101 | Denim Jacket | 1 color names a part | Brown Denim Jacket, White Collar | white | white denim jacket | generic |
| PLT-DA07102 | Denim Jacket | 1 color names a part | Pink Denim Jacket, Yellow Lining | yellow | yellow denim jacket | generic |
| PLT-DA07200 | Denim Jacket | 2 another category's noun as a modifier | Red Vest Denim Jacket | vest | vest | generic |
| PLT-DA07201 | Denim Jacket | 2 another category's noun as a modifier | Blue Blazer Denim Jacket | blazer | blazer | generic |
| PLT-DA07202 | Denim Jacket | 2 another category's noun as a modifier | Cream Hoodie Denim Jacket | hoodie | hoodie | generic |
| PLT-DA07300 | Denim Jacket | 3 audience word of a sibling version | Navy Womens Denim Jacket, Mens-Style | mens | mens denim jacket | generic |
| PLT-DA07301 | Denim Jacket | 3 audience word of a sibling version | Pink Womens Denim Jacket, Mens Fit | mens | mens denim jacket | generic |
| PLT-DA07302 | Denim Jacket | 3 audience word of a sibling version | Black Womens Denim Jacket, Mens-Style | mens | mens denim jacket | generic |
| PLT-DA07400 | Denim Jacket | 4 material or feature named but absent | Green Leather-Look Denim Jacket | leather | leather denim jacket | special: material claim |
| PLT-DA07401 | Denim Jacket | 4 material or feature named but absent | Brown Suede-Look Denim Jacket | suede | suede denim jacket | special: material claim |
| PLT-DA07402 | Denim Jacket | 4 material or feature named but absent | Grey Cashmere-Feel Denim Jacket | cashmere | cashmere denim jacket | special: material claim |
| PLT-DA07500 | Denim Jacket | 5 shade spelled in the description only | Moonbeam Denim Jacket | ivory | ivory denim jacket | generic |
| PLT-DA07501 | Denim Jacket | 5 shade spelled in the description only | Driftwood Denim Jacket | taupe | taupe denim jacket | generic |
| PLT-DA07502 | Denim Jacket | 5 shade spelled in the description only | Dune Denim Jacket | beige | beige denim jacket | generic |
| PLT-DA07600 | Denim Jacket | 6 incidental word in a range name | Green Hollow Denim Jacket, Red | green | green denim jacket | generic |
| PLT-DA07601 | Denim Jacket | 6 incidental word in a range name | White Cliff Denim Jacket, Red | white | white denim jacket | generic |
| PLT-DA07602 | Denim Jacket | 6 incidental word in a range name | Red Harbour Denim Jacket, White | red | red denim jacket | generic |
| PLT-DA07603 | Denim Jacket | 6 incidental word in a range name | Shirt Row Denim Jacket, Blue | shirt | shirt | generic |
| PLT-DA07700 | Denim Jacket | 7 invented brand holding a color or category word | White Dormouse Denim Jacket, Brown | white | white denim jacket | generic |
| PLT-DA07701 | Denim Jacket | 7 invented brand holding a color or category word | Red Plover Denim Jacket, Brown | red | red denim jacket | generic |
| PLT-DA07702 | Denim Jacket | 7 invented brand holding a color or category word | Jumper Jay Denim Jacket, Red | jumper | jumper denim jacket | generic |
| PLT-DA08100 | Dress | 1 color names a part | Cream Dress, Red Buttons | red | red dress | generic |
| PLT-DA08101 | Dress | 1 color names a part | Brown Dress, White Trim | white | white dress | generic |
| PLT-DA08102 | Dress | 1 color names a part | Blue Dress, White Collar | white | white dress | generic |
| PLT-DA08200 | Dress | 2 another category's noun as a modifier | Pink Blazer Dress | blazer | blazer | generic |
| PLT-DA08201 | Dress | 2 another category's noun as a modifier | Cream Coat Dress | coat | coat | generic |
| PLT-DA08202 | Dress | 2 another category's noun as a modifier | Blue Vest Dress | vest | vest | generic |
| PLT-DA08300 | Dress | 3 audience word of a sibling version | White Womens Dress, Boys Fit | boys | boys dress | generic |
| PLT-DA08301 | Dress | 3 audience word of a sibling version | Grey Womens Dress, Boys Fit | boys | boys dress | generic |
| PLT-DA08302 | Dress | 3 audience word of a sibling version | Black Womens Dress, Mens Fit | mens | mens dress | generic |
| PLT-DA08400 | Dress | 4 material or feature named but absent | Black Leather-Look Dress | leather | leather dress | special: material claim |
| PLT-DA08401 | Dress | 4 material or feature named but absent | Grey Suede-Look Dress | suede | suede dress | special: material claim |
| PLT-DA08402 | Dress | 4 material or feature named but absent | Black Cashmere-Feel Dress | cashmere | cashmere dress | special: material claim |
| PLT-DA08500 | Dress | 5 shade spelled in the description only | Moonbeam Dress | ivory | ivory dress | generic |
| PLT-DA08501 | Dress | 5 shade spelled in the description only | Driftwood Dress | taupe | taupe dress | generic |
| PLT-DA08502 | Dress | 5 shade spelled in the description only | Dune Dress | beige | beige dress | generic |
| PLT-DA08600 | Dress | 6 incidental word in a range name | Red Harbour Dress, Grey | red | red dress | generic |
| PLT-DA08601 | Dress | 6 incidental word in a range name | White Cliff Dress, Red | white | white dress | generic |
| PLT-DA08602 | Dress | 6 incidental word in a range name | Blue Meadow Dress, White | blue | blue dress | generic |
| PLT-DA08603 | Dress | 6 incidental word in a range name | Boot Hill Dress, Grey | boot | boot | generic |
| PLT-DA08700 | Dress | 7 invented brand holding a color or category word | Red Plover Dress, Blue | red | red dress | generic |
| PLT-DA08701 | Dress | 7 invented brand holding a color or category word | White Dormouse Dress, Blue | white | white dress | generic |
| PLT-DA08702 | Dress | 7 invented brand holding a color or category word | Blue Otter Dress, Red | blue | blue dress | generic |
| PLT-DA09100 | Joggers | 1 color names a part | Green Regular Joggers, White Trim | white | white joggers | generic |
| PLT-DA09101 | Joggers | 1 color names a part | Brown Oversized Joggers, White Pocket | white | white joggers | generic |
| PLT-DA09102 | Joggers | 1 color names a part | Red Regular Joggers, Blue Cuffs | blue | blue joggers | generic |
| PLT-DA09200 | Joggers | 2 another category's noun as a modifier | Cream Tunic Relaxed Joggers | tunic | tunic | generic |
| PLT-DA09201 | Joggers | 2 another category's noun as a modifier | Grey Blazer Slim Joggers | blazer | blazer | generic |
| PLT-DA09202 | Joggers | 2 another category's noun as a modifier | Black Hoodie Relaxed Joggers | hoodie | hoodie | generic |
| PLT-DA09300 | Joggers | 3 audience word of a sibling version | Pink Mens Regular Joggers, Girls Fit | girls | girls joggers | generic |
| PLT-DA09301 | Joggers | 3 audience word of a sibling version | Green Womens Oversized Joggers, Mens-Style | mens | mens joggers | generic |
| PLT-DA09302 | Joggers | 3 audience word of a sibling version | Red Mens Regular Joggers, Girls Fit | girls | girls joggers | generic |
| PLT-DA09400 | Joggers | 4 material or feature named but absent | Red Leather-Look Relaxed Joggers | leather | leather joggers | special: material claim |
| PLT-DA09401 | Joggers | 4 material or feature named but absent | Blue Suede-Look Slim Joggers | suede | suede joggers | special: material claim |
| PLT-DA09402 | Joggers | 4 material or feature named but absent | Navy Cashmere-Feel Relaxed Joggers | cashmere | cashmere joggers | special: material claim |
| PLT-DA09500 | Joggers | 5 shade spelled in the description only | Moonbeam Regular Joggers | ivory | ivory joggers | generic |
| PLT-DA09501 | Joggers | 5 shade spelled in the description only | Driftwood Oversized Joggers | taupe | taupe joggers | generic |
| PLT-DA09502 | Joggers | 5 shade spelled in the description only | Dune Regular Joggers | beige | beige joggers | generic |
| PLT-DA09600 | Joggers | 6 incidental word in a range name | Green Park Relaxed Joggers, Pink | green | green joggers | generic |
| PLT-DA09601 | Joggers | 6 incidental word in a range name | White Moor Slim Joggers, Navy | white | white joggers | generic |
| PLT-DA09602 | Joggers | 6 incidental word in a range name | Black Tor Relaxed Joggers, White | black | black joggers | generic |
| PLT-DA09603 | Joggers | 6 incidental word in a range name | Shirt Row Regular Joggers, Pink | shirt | shirt | generic |
| PLT-DA09700 | Joggers | 7 invented brand holding a color or category word | Jumper Jay Oversized Joggers, White | jumper | jumper joggers | generic |
| PLT-DA09701 | Joggers | 7 invented brand holding a color or category word | White Dormouse Regular Joggers, Cream | white | white joggers | generic |
| PLT-DA09702 | Joggers | 7 invented brand holding a color or category word | Coat Crake Relaxed Joggers, Red | coat | coat joggers | generic |
| PLT-DA10100 | Jumper | 1 color names a part | Black Jumper, White Piping | white | white jumper | generic |
| PLT-DA10101 | Jumper | 1 color names a part | Navy Jumper, Yellow Lining | yellow | yellow jumper | generic |
| PLT-DA10102 | Jumper | 1 color names a part | Navy Jumper, White Lining | white | white jumper | generic |
| PLT-DA10200 | Jumper | 2 another category's noun as a modifier | Navy Skirt Jumper | skirt | skirt | generic |
| PLT-DA10201 | Jumper | 2 another category's noun as a modifier | Pink Tunic Jumper | tunic | tunic | generic |
| PLT-DA10202 | Jumper | 2 another category's noun as a modifier | Cream Skirt Jumper | skirt | skirt | generic |
| PLT-DA10300 | Jumper | 3 audience word of a sibling version | Red Womens Jumper, Boys Fit | boys | boys jumper | generic |
| PLT-DA10301 | Jumper | 3 audience word of a sibling version | Cream Womens Jumper, Mens Fit | mens | mens jumper | generic |
| PLT-DA10302 | Jumper | 3 audience word of a sibling version | Pink Womens Jumper, Boys Fit | boys | boys jumper | generic |
| PLT-DA10400 | Jumper | 4 material or feature named but absent | Red Leather-Look Jumper, Wool Blend | leather | leather jumper | special: material claim |
| PLT-DA10401 | Jumper | 4 material or feature named but absent | Green Suede-Look Jumper | suede | suede jumper | special: material claim |
| PLT-DA10402 | Jumper | 4 material or feature named but absent | White Cashmere-Feel Jumper, Wool Blend | cashmere | cashmere jumper | special: material claim |
| PLT-DA10500 | Jumper | 5 shade spelled in the description only | Moonbeam Jumper | ivory | ivory jumper | generic |
| PLT-DA10501 | Jumper | 5 shade spelled in the description only | Driftwood Jumper | taupe | taupe jumper | generic |
| PLT-DA10502 | Jumper | 5 shade spelled in the description only | Dune Jumper | beige | beige jumper | generic |
| PLT-DA10600 | Jumper | 6 incidental word in a range name | Yellow Marsh Jumper, Navy | yellow | yellow jumper | generic |
| PLT-DA10601 | Jumper | 6 incidental word in a range name | White Moor Jumper, Black | white | white jumper | generic |
| PLT-DA10602 | Jumper | 6 incidental word in a range name | Blue Cove Jumper, Green | blue | blue jumper | generic |
| PLT-DA10603 | Jumper | 6 incidental word in a range name | Sock Hop Jumper, Pink | sock | sock | generic |
| PLT-DA10700 | Jumper | 7 invented brand holding a color or category word | Blue Otter Jumper, Grey | blue | blue jumper | generic |
| PLT-DA10701 | Jumper | 7 invented brand holding a color or category word | Black Lapwing Jumper, Grey | black | black jumper | generic |
| PLT-DA10702 | Jumper | 7 invented brand holding a color or category word | White Dormouse Jumper, Grey | white | white jumper | generic |
| PLT-DA11100 | Leggings | 1 color names a part | Blue Compression Leggings, White Stitching | white | white leggings | generic |
| PLT-DA11101 | Leggings | 1 color names a part | Cream Regular Leggings, Green Pocket | green | green leggings | generic |
| PLT-DA11102 | Leggings | 1 color names a part | Pink Regular Leggings, Red Lining | red | red leggings | generic |
| PLT-DA11200 | Leggings | 2 another category's noun as a modifier | Green Gilet Regular Leggings | gilet | gilet | generic |
| PLT-DA11201 | Leggings | 2 another category's noun as a modifier | Blue Hoodie Regular Leggings | hoodie | hoodie | generic |
| PLT-DA11202 | Leggings | 2 another category's noun as a modifier | Cream Cardigan Regular Leggings | cardigan | cardigan | generic |
| PLT-DA11300 | Leggings | 3 audience word of a sibling version | Red Womens Compression Leggings, Boys Fit | boys | boys leggings | generic |
| PLT-DA11301 | Leggings | 3 audience word of a sibling version | Cream Womens Compression Leggings, Mens-Style | mens | mens leggings | generic |
| PLT-DA11302 | Leggings | 3 audience word of a sibling version | Blue Womens Regular Leggings, Boys Fit | boys | boys leggings | generic |
| PLT-DA11400 | Leggings | 4 material or feature named but absent | Blue Leather-Look Regular Leggings | leather | leather leggings | special: material claim |
| PLT-DA11401 | Leggings | 4 material or feature named but absent | Pink Suede-Look Regular Leggings | suede | suede leggings | special: material claim |
| PLT-DA11402 | Leggings | 4 material or feature named but absent | Cream Cashmere-Feel Regular Leggings | cashmere | cashmere leggings | special: material claim |
| PLT-DA11500 | Leggings | 5 shade spelled in the description only | Moonbeam Regular Leggings | ivory | ivory leggings | generic |
| PLT-DA11501 | Leggings | 5 shade spelled in the description only | Driftwood Compression Leggings | taupe | taupe leggings | generic |
| PLT-DA11502 | Leggings | 5 shade spelled in the description only | Dune Compression Leggings | beige | beige leggings | generic |
| PLT-DA11600 | Leggings | 6 incidental word in a range name | Blue Cove Regular Leggings, Black | blue | blue leggings | generic |
| PLT-DA11601 | Leggings | 6 incidental word in a range name | Black Tor Regular Leggings, Brown | black | black leggings | generic |
| PLT-DA11602 | Leggings | 6 incidental word in a range name | Yellow Marsh Regular Leggings, Grey | yellow | yellow leggings | generic |
| PLT-DA11603 | Leggings | 6 incidental word in a range name | Dress Circle Regular Leggings, Pink | dress | dress | generic |
| PLT-DA11700 | Leggings | 7 invented brand holding a color or category word | Red Plover Regular Leggings, Green | red | red leggings | generic |
| PLT-DA11701 | Leggings | 7 invented brand holding a color or category word | Green Stoat Compression Leggings, Black | green | green leggings | generic |
| PLT-DA11702 | Leggings | 7 invented brand holding a color or category word | Black Lapwing Compression Leggings, Green | black | black leggings | generic |
| PLT-DA12100 | Outfit Set | 1 color names a part | Black Outfit Set, Green Stitching | green | green outfit set | generic |
| PLT-DA12101 | Outfit Set | 1 color names a part | Grey Outfit Set, Yellow Piping | yellow | yellow outfit set | generic |
| PLT-DA12102 | Outfit Set | 1 color names a part | Green Outfit Set, White Stripes | white | white outfit set | generic |
| PLT-DA12200 | Outfit Set | 2 another category's noun as a modifier | Navy Tunic Outfit Set | tunic | tunic | generic |
| PLT-DA12201 | Outfit Set | 2 another category's noun as a modifier | Navy Blazer Outfit Set | blazer | blazer | generic |
| PLT-DA12202 | Outfit Set | 2 another category's noun as a modifier | White Gilet Outfit Set | gilet | gilet | generic |
| PLT-DA12300 | Outfit Set | 3 audience word of a sibling version | Blue Boys Outfit Set, Mini-Me Mens | mens | mens outfit set | generic |
| PLT-DA12301 | Outfit Set | 3 audience word of a sibling version | Green Boys Outfit Set, Mens-Style | mens | mens outfit set | generic |
| PLT-DA12302 | Outfit Set | 3 audience word of a sibling version | Brown Boys Outfit Set, Mens-Style | mens | mens outfit set | generic |
| PLT-DA12400 | Outfit Set | 4 material or feature named but absent | Cream Leather-Look Outfit Set | leather | leather outfit set | special: material claim |
| PLT-DA12401 | Outfit Set | 4 material or feature named but absent | Blue Suede-Look Outfit Set | suede | suede outfit set | special: material claim |
| PLT-DA12402 | Outfit Set | 4 material or feature named but absent | Green Cashmere-Feel Outfit Set | cashmere | cashmere outfit set | special: material claim |
| PLT-DA12500 | Outfit Set | 5 shade spelled in the description only | Moonbeam Outfit Set | ivory | ivory outfit set | generic |
| PLT-DA12501 | Outfit Set | 5 shade spelled in the description only | Driftwood Outfit Set | taupe | taupe outfit set | generic |
| PLT-DA12502 | Outfit Set | 5 shade spelled in the description only | Dune Outfit Set | beige | beige outfit set | generic |
| PLT-DA12600 | Outfit Set | 6 incidental word in a range name | Red Fern Outfit Set, Cream | red | red outfit set | generic |
| PLT-DA12601 | Outfit Set | 6 incidental word in a range name | Blue Cove Outfit Set, White | blue | blue outfit set | generic |
| PLT-DA12602 | Outfit Set | 6 incidental word in a range name | Red Harbour Outfit Set, Brown | red | red outfit set | generic |
| PLT-DA12603 | Outfit Set | 6 incidental word in a range name | Jumper Lane Outfit Set, Black | jumper | jumper | generic |
| PLT-DA12700 | Outfit Set | 7 invented brand holding a color or category word | Blue Otter Outfit Set, Grey | blue | blue outfit set | generic |
| PLT-DA12701 | Outfit Set | 7 invented brand holding a color or category word | Black Lapwing Outfit Set, Navy | black | black outfit set | generic |
| PLT-DA12702 | Outfit Set | 7 invented brand holding a color or category word | Yellow Wagtail Outfit Set, Black | yellow | yellow outfit set | generic |
| PLT-DA13100 | Puffer Jacket | 1 color names a part | Black Puffer Jacket, Yellow Lining | yellow | yellow puffer jacket | generic |
| PLT-DA13101 | Puffer Jacket | 1 color names a part | Blue Puffer Jacket, Yellow Buttons | yellow | yellow puffer jacket | generic |
| PLT-DA13102 | Puffer Jacket | 1 color names a part | White Puffer Jacket, Blue Pocket | blue | blue puffer jacket | generic |
| PLT-DA13200 | Puffer Jacket | 2 another category's noun as a modifier | Pink Hoodie Puffer Jacket | hoodie | hoodie | generic |
| PLT-DA13201 | Puffer Jacket | 2 another category's noun as a modifier | Red Skirt Puffer Jacket | skirt | skirt | generic |
| PLT-DA13202 | Puffer Jacket | 2 another category's noun as a modifier | Navy Hoodie Puffer Jacket | hoodie | hoodie | generic |
| PLT-DA13300 | Puffer Jacket | 3 audience word of a sibling version | Pink Mens Puffer Jacket, Womens-Style | womens | womens puffer jacket | generic |
| PLT-DA13301 | Puffer Jacket | 3 audience word of a sibling version | Navy Mens Puffer Jacket, Womens Fit | womens | womens puffer jacket | generic |
| PLT-DA13302 | Puffer Jacket | 3 audience word of a sibling version | Brown Boys Puffer Jacket, Mini-Me Mens | mens | mens puffer jacket | generic |
| PLT-DA13400 | Puffer Jacket | 4 material or feature named but absent | Pink Leather-Look Puffer Jacket | leather | leather puffer jacket | special: material claim |
| PLT-DA13401 | Puffer Jacket | 4 material or feature named but absent | Brown Suede-Look Puffer Jacket | suede | suede puffer jacket | special: material claim |
| PLT-DA13402 | Puffer Jacket | 4 material or feature named but absent | Green Cashmere-Feel Puffer Jacket | cashmere | cashmere puffer jacket | special: material claim |
| PLT-DA13500 | Puffer Jacket | 5 shade spelled in the description only | Moonbeam Puffer Jacket | ivory | ivory puffer jacket | generic |
| PLT-DA13501 | Puffer Jacket | 5 shade spelled in the description only | Driftwood Puffer Jacket | taupe | taupe puffer jacket | generic |
| PLT-DA13502 | Puffer Jacket | 5 shade spelled in the description only | Dune Puffer Jacket | beige | beige puffer jacket | generic |
| PLT-DA13600 | Puffer Jacket | 6 incidental word in a range name | Red Harbour Puffer Jacket, Pink | red | red puffer jacket | generic |
| PLT-DA13601 | Puffer Jacket | 6 incidental word in a range name | Blue Cove Puffer Jacket, White | blue | blue puffer jacket | generic |
| PLT-DA13602 | Puffer Jacket | 6 incidental word in a range name | Yellow Marsh Puffer Jacket, Grey | yellow | yellow puffer jacket | generic |
| PLT-DA13603 | Puffer Jacket | 6 incidental word in a range name | Skirt Point Puffer Jacket, Pink | skirt | skirt | generic |
| PLT-DA13700 | Puffer Jacket | 7 invented brand holding a color or category word | Red Plover Puffer Jacket, Brown | red | red puffer jacket | generic |
| PLT-DA13701 | Puffer Jacket | 7 invented brand holding a color or category word | Black Lapwing Puffer Jacket, Blue | black | black puffer jacket | generic |
| PLT-DA13702 | Puffer Jacket | 7 invented brand holding a color or category word | Yellow Wagtail Puffer Jacket, Navy | yellow | yellow puffer jacket | generic |
| PLT-DA14100 | Shirt | 1 color names a part | Brown Shirt, Black Lining | black | black shirt | generic |
| PLT-DA14101 | Shirt | 1 color names a part | White Shirt, Green Stripes | green | green shirt | generic |
| PLT-DA14102 | Shirt | 1 color names a part | Cream Shirt, Red Pocket | red | red shirt | generic |
| PLT-DA14200 | Shirt | 2 another category's noun as a modifier | Pink Cardigan Shirt | cardigan | cardigan | generic |
| PLT-DA14201 | Shirt | 2 another category's noun as a modifier | Black Vest Shirt | vest | vest | generic |
| PLT-DA14202 | Shirt | 2 another category's noun as a modifier | Red Blazer Shirt | blazer | blazer | generic |
| PLT-DA14300 | Shirt | 3 audience word of a sibling version | Navy Mens Shirt, Womens Fit | womens | womens shirt | generic |
| PLT-DA14301 | Shirt | 3 audience word of a sibling version | Blue Mens Shirt, Womens Fit | womens | womens shirt | generic |
| PLT-DA14302 | Shirt | 3 audience word of a sibling version | Pink Mens Shirt, Womens-Style | womens | womens shirt | generic |
| PLT-DA14400 | Shirt | 4 material or feature named but absent | White Leather-Look Shirt | leather | leather shirt | special: material claim |
| PLT-DA14401 | Shirt | 4 material or feature named but absent | Black Suede-Look Shirt | suede | suede shirt | special: material claim |
| PLT-DA14402 | Shirt | 4 material or feature named but absent | Pink Cashmere-Feel Shirt | cashmere | cashmere shirt | special: material claim |
| PLT-DA14500 | Shirt | 5 shade spelled in the description only | Moonbeam Shirt | ivory | ivory shirt | generic |
| PLT-DA14501 | Shirt | 5 shade spelled in the description only | Driftwood Shirt | taupe | taupe shirt | generic |
| PLT-DA14502 | Shirt | 5 shade spelled in the description only | Dune Shirt | beige | beige shirt | generic |
| PLT-DA14600 | Shirt | 6 incidental word in a range name | Blue Meadow Shirt, Green | blue | blue shirt | generic |
| PLT-DA14601 | Shirt | 6 incidental word in a range name | Yellow Brook Shirt, Black | yellow | yellow shirt | generic |
| PLT-DA14602 | Shirt | 6 incidental word in a range name | Green Park Shirt, Brown | green | green shirt | generic |
| PLT-DA14603 | Shirt | 6 incidental word in a range name | Jacket Quay Shirt, Red | jacket | jacket | generic |
| PLT-DA14700 | Shirt | 7 invented brand holding a color or category word | Coat Crake Shirt, Blue | coat | coat shirt | generic |
| PLT-DA14701 | Shirt | 7 invented brand holding a color or category word | Green Stoat Shirt, Blue | green | green shirt | generic |
| PLT-DA14702 | Shirt | 7 invented brand holding a color or category word | Blue Otter Shirt, Grey | blue | blue shirt | generic |
| PLT-DA15100 | Shorts | 1 color names a part | Pink Shorts, Yellow Cuffs | yellow | yellow shorts | generic |
| PLT-DA15101 | Shorts | 1 color names a part | Grey Shorts, Blue Stripes | blue | blue shorts | generic |
| PLT-DA15102 | Shorts | 1 color names a part | Green Shorts, White Trim | white | white shorts | generic |
| PLT-DA15200 | Shorts | 2 another category's noun as a modifier | Brown Blazer Shorts | blazer | blazer | generic |
| PLT-DA15201 | Shorts | 2 another category's noun as a modifier | Brown Poncho Shorts | poncho | poncho | generic |
| PLT-DA15202 | Shorts | 2 another category's noun as a modifier | Green Gilet Shorts | gilet | gilet | generic |
| PLT-DA15300 | Shorts | 3 audience word of a sibling version | Brown Womens Shorts, Boys Fit | boys | boys shorts | generic |
| PLT-DA15301 | Shorts | 3 audience word of a sibling version | Pink Womens Shorts, Boys Fit | boys | boys shorts | generic |
| PLT-DA15302 | Shorts | 3 audience word of a sibling version | White Mens Shorts, Womens Fit | womens | womens shorts | generic |
| PLT-DA15400 | Shorts | 4 material or feature named but absent | Green Leather-Look Shorts | leather | leather shorts | special: material claim |
| PLT-DA15401 | Shorts | 4 material or feature named but absent | Navy Suede-Look Shorts | suede | suede shorts | special: material claim |
| PLT-DA15402 | Shorts | 4 material or feature named but absent | Brown Cashmere-Feel Shorts | cashmere | cashmere shorts | special: material claim |
| PLT-DA15500 | Shorts | 5 shade spelled in the description only | Moonbeam Shorts | ivory | ivory shorts | generic |
| PLT-DA15501 | Shorts | 5 shade spelled in the description only | Driftwood Shorts | taupe | taupe shorts | generic |
| PLT-DA15502 | Shorts | 5 shade spelled in the description only | Dune Shorts | beige | beige shorts | generic |
| PLT-DA15600 | Shorts | 6 incidental word in a range name | Red Harbour Shorts, Black | red | red shorts | generic |
| PLT-DA15601 | Shorts | 6 incidental word in a range name | Black Tor Shorts, Blue | black | black shorts | generic |
| PLT-DA15602 | Shorts | 6 incidental word in a range name | Yellow Marsh Shorts, Navy | yellow | yellow shorts | generic |
| PLT-DA15603 | Shorts | 6 incidental word in a range name | Sock Hop Shorts, Red | sock | sock | generic |
| PLT-DA15700 | Shorts | 7 invented brand holding a color or category word | Black Lapwing Shorts, Brown | black | black shorts | generic |
| PLT-DA15701 | Shorts | 7 invented brand holding a color or category word | White Dormouse Shorts, Navy | white | white shorts | generic |
| PLT-DA15702 | Shorts | 7 invented brand holding a color or category word | White Dormouse Shorts, Pink | white | white shorts | generic |
| PLT-DA16100 | Skirt | 1 color names a part | Red Skirt, Blue Lining | blue | blue skirt | generic |
| PLT-DA16101 | Skirt | 1 color names a part | Blue Skirt, Yellow Pocket | yellow | yellow skirt | generic |
| PLT-DA16102 | Skirt | 1 color names a part | White Skirt, Blue Stitching | blue | blue skirt | generic |
| PLT-DA16200 | Skirt | 2 another category's noun as a modifier | Brown Gilet Skirt | gilet | gilet | generic |
| PLT-DA16201 | Skirt | 2 another category's noun as a modifier | Navy Jacket Skirt | jacket | jacket | generic |
| PLT-DA16202 | Skirt | 2 another category's noun as a modifier | Red Gilet Skirt | gilet | gilet | generic |
| PLT-DA16300 | Skirt | 3 audience word of a sibling version | Black Womens Skirt, Mens Fit | mens | mens skirt | generic |
| PLT-DA16301 | Skirt | 3 audience word of a sibling version | White Womens Skirt, Mens Fit | mens | mens skirt | generic |
| PLT-DA16302 | Skirt | 3 audience word of a sibling version | Navy Womens Skirt, Mens-Style | mens | mens skirt | generic |
| PLT-DA16400 | Skirt | 4 material or feature named but absent | Blue Leather-Look Skirt | leather | leather skirt | special: material claim |
| PLT-DA16401 | Skirt | 4 material or feature named but absent | Pink Suede-Look Skirt | suede | suede skirt | special: material claim |
| PLT-DA16402 | Skirt | 4 material or feature named but absent | Black Cashmere-Feel Skirt | cashmere | cashmere skirt | special: material claim |
| PLT-DA16500 | Skirt | 5 shade spelled in the description only | Moonbeam Skirt | ivory | ivory skirt | generic |
| PLT-DA16501 | Skirt | 5 shade spelled in the description only | Driftwood Skirt | taupe | taupe skirt | generic |
| PLT-DA16502 | Skirt | 5 shade spelled in the description only | Dune Skirt | beige | beige skirt | generic |
| PLT-DA16600 | Skirt | 6 incidental word in a range name | Green Hollow Skirt, Brown | green | green skirt | generic |
| PLT-DA16601 | Skirt | 6 incidental word in a range name | Red Fern Skirt, Blue | red | red skirt | generic |
| PLT-DA16602 | Skirt | 6 incidental word in a range name | Black Tor Skirt, Cream | black | black skirt | generic |
| PLT-DA16603 | Skirt | 6 incidental word in a range name | Coat Hook Skirt, Cream | coat | coat | generic |
| PLT-DA16700 | Skirt | 7 invented brand holding a color or category word | Red Plover Skirt, Brown | red | red skirt | generic |
| PLT-DA16701 | Skirt | 7 invented brand holding a color or category word | Coat Crake Skirt, Brown | coat | coat skirt | generic |
| PLT-DA16702 | Skirt | 7 invented brand holding a color or category word | Jumper Jay Skirt, Green | jumper | jumper skirt | generic |
| PLT-DA17100 | Suit Jacket | 1 color names a part | Pink Suit Jacket, Blue Trim | blue | blue suit jacket | generic |
| PLT-DA17101 | Suit Jacket | 1 color names a part | Cream Suit Jacket, Yellow Zip | yellow | yellow suit jacket | generic |
| PLT-DA17102 | Suit Jacket | 1 color names a part | Navy Suit Jacket, Green Piping | green | green suit jacket | generic |
| PLT-DA17200 | Suit Jacket | 2 another category's noun as a modifier | Navy Hoodie Suit Jacket | hoodie | hoodie | generic |
| PLT-DA17201 | Suit Jacket | 2 another category's noun as a modifier | Red Hoodie Suit Jacket | hoodie | hoodie | generic |
| PLT-DA17202 | Suit Jacket | 2 another category's noun as a modifier | Pink Hoodie Suit Jacket | hoodie | hoodie | generic |
| PLT-DA17300 | Suit Jacket | 3 audience word of a sibling version | Grey Womens Suit Jacket, Mens-Style | mens | mens suit jacket | generic |
| PLT-DA17301 | Suit Jacket | 3 audience word of a sibling version | Grey Womens Suit Jacket, Boys Fit | boys | boys suit jacket | generic |
| PLT-DA17302 | Suit Jacket | 3 audience word of a sibling version | Pink Womens Suit Jacket, Boys Fit | boys | boys suit jacket | generic |
| PLT-DA17400 | Suit Jacket | 4 material or feature named but absent | White Leather-Look Suit Jacket | leather | leather suit jacket | special: material claim |
| PLT-DA17401 | Suit Jacket | 4 material or feature named but absent | Blue Suede-Look Suit Jacket | suede | suede suit jacket | special: material claim |
| PLT-DA17402 | Suit Jacket | 4 material or feature named but absent | Pink Cashmere-Feel Suit Jacket | cashmere | cashmere suit jacket | special: material claim |
| PLT-DA17500 | Suit Jacket | 5 shade spelled in the description only | Moonbeam Suit Jacket | ivory | ivory suit jacket | generic |
| PLT-DA17501 | Suit Jacket | 5 shade spelled in the description only | Driftwood Suit Jacket | taupe | taupe suit jacket | generic |
| PLT-DA17502 | Suit Jacket | 5 shade spelled in the description only | Dune Suit Jacket | beige | beige suit jacket | generic |
| PLT-DA17600 | Suit Jacket | 6 incidental word in a range name | Blue Meadow Suit Jacket, Black | blue | blue suit jacket | generic |
| PLT-DA17601 | Suit Jacket | 6 incidental word in a range name | Blue Cove Suit Jacket, Green | blue | blue suit jacket | generic |
| PLT-DA17602 | Suit Jacket | 6 incidental word in a range name | White Cliff Suit Jacket, Green | white | white suit jacket | generic |
| PLT-DA17603 | Suit Jacket | 6 incidental word in a range name | Jumper Lane Suit Jacket, Red | jumper | jumper | generic |
| PLT-DA17700 | Suit Jacket | 7 invented brand holding a color or category word | Green Stoat Suit Jacket, Pink | green | green suit jacket | generic |
| PLT-DA17701 | Suit Jacket | 7 invented brand holding a color or category word | Blue Otter Suit Jacket, Brown | blue | blue suit jacket | generic |
| PLT-DA17702 | Suit Jacket | 7 invented brand holding a color or category word | Red Plover Suit Jacket, Brown | red | red suit jacket | generic |
| PLT-DA18100 | Sweatshirt | 1 color names a part | Cream Sweatshirt, Yellow Lining | yellow | yellow sweatshirt | generic |
| PLT-DA18101 | Sweatshirt | 1 color names a part | Red Sweatshirt, White Buttons | white | white sweatshirt | generic |
| PLT-DA18102 | Sweatshirt | 1 color names a part | Green Sweatshirt, Black Cuffs | black | black sweatshirt | generic |
| PLT-DA18200 | Sweatshirt | 2 another category's noun as a modifier | Blue Poncho Sweatshirt | poncho | poncho | generic |
| PLT-DA18201 | Sweatshirt | 2 another category's noun as a modifier | White Skirt Sweatshirt | skirt | skirt | generic |
| PLT-DA18202 | Sweatshirt | 2 another category's noun as a modifier | Grey Trouser Sweatshirt | trouser | trouser | generic |
| PLT-DA18300 | Sweatshirt | 3 audience word of a sibling version | Red Mens Sweatshirt, Womens-Style | womens | womens sweatshirt | generic |
| PLT-DA18301 | Sweatshirt | 3 audience word of a sibling version | Brown Mens Sweatshirt, Womens Fit | womens | womens sweatshirt | generic |
| PLT-DA18302 | Sweatshirt | 3 audience word of a sibling version | Blue Mens Sweatshirt, Womens Fit | womens | womens sweatshirt | generic |
| PLT-DA18400 | Sweatshirt | 4 material or feature named but absent | Blue Leather-Look Sweatshirt | leather | leather sweatshirt | special: material claim |
| PLT-DA18401 | Sweatshirt | 4 material or feature named but absent | Green Suede-Look Sweatshirt | suede | suede sweatshirt | special: material claim |
| PLT-DA18402 | Sweatshirt | 4 material or feature named but absent | Navy Cashmere-Feel Sweatshirt | cashmere | cashmere sweatshirt | special: material claim |
| PLT-DA18500 | Sweatshirt | 5 shade spelled in the description only | Moonbeam Sweatshirt | ivory | ivory sweatshirt | generic |
| PLT-DA18501 | Sweatshirt | 5 shade spelled in the description only | Driftwood Sweatshirt | taupe | taupe sweatshirt | generic |
| PLT-DA18502 | Sweatshirt | 5 shade spelled in the description only | Dune Sweatshirt | beige | beige sweatshirt | generic |
| PLT-DA18600 | Sweatshirt | 6 incidental word in a range name | Yellow Brook Sweatshirt, Black | yellow | yellow sweatshirt | generic |
| PLT-DA18601 | Sweatshirt | 6 incidental word in a range name | Yellow Brook Sweatshirt, Blue | yellow | yellow sweatshirt | generic |
| PLT-DA18602 | Sweatshirt | 6 incidental word in a range name | White Moor Sweatshirt, Green | white | white sweatshirt | generic |
| PLT-DA18603 | Sweatshirt | 6 incidental word in a range name | Jumper Lane Sweatshirt, Green | jumper | jumper | generic |
| PLT-DA18700 | Sweatshirt | 7 invented brand holding a color or category word | Red Plover Sweatshirt, Navy | red | red sweatshirt | generic |
| PLT-DA18701 | Sweatshirt | 7 invented brand holding a color or category word | White Dormouse Sweatshirt, Pink | white | white sweatshirt | generic |
| PLT-DA18702 | Sweatshirt | 7 invented brand holding a color or category word | Coat Crake Sweatshirt, Blue | coat | coat sweatshirt | generic |
| PLT-DA19100 | T-Shirt | 1 color names a part | White T-Shirt, Yellow Zip | yellow | yellow t-shirt | generic |
| PLT-DA19101 | T-Shirt | 1 color names a part | Blue T-Shirt, Yellow Stripes | yellow | yellow t-shirt | generic |
| PLT-DA19102 | T-Shirt | 1 color names a part | Green T-Shirt, White Stitching | white | white t-shirt | generic |
| PLT-DA19200 | T-Shirt | 2 another category's noun as a modifier | Red Poncho T-Shirt | poncho | poncho | generic |
| PLT-DA19201 | T-Shirt | 2 another category's noun as a modifier | Pink Coat T-Shirt | coat | coat | generic |
| PLT-DA19202 | T-Shirt | 2 another category's noun as a modifier | Blue Coat T-Shirt | coat | coat | generic |
| PLT-DA19300 | T-Shirt | 3 audience word of a sibling version | Grey Mens T-Shirt, Girls Fit | girls | girls t-shirt | generic |
| PLT-DA19301 | T-Shirt | 3 audience word of a sibling version | Brown Womens T-Shirt, Mens-Style | mens | mens t-shirt | generic |
| PLT-DA19302 | T-Shirt | 3 audience word of a sibling version | Pink Mens T-Shirt, Womens Fit | womens | womens t-shirt | generic |
| PLT-DA19400 | T-Shirt | 4 material or feature named but absent | Blue Leather-Look T-Shirt | leather | leather t-shirt | special: material claim |
| PLT-DA19401 | T-Shirt | 4 material or feature named but absent | Pink Suede-Look T-Shirt | suede | suede t-shirt | special: material claim |
| PLT-DA19402 | T-Shirt | 4 material or feature named but absent | White Cashmere-Feel T-Shirt | cashmere | cashmere t-shirt | special: material claim |
| PLT-DA19500 | T-Shirt | 5 shade spelled in the description only | Moonbeam T-Shirt | ivory | ivory t-shirt | generic |
| PLT-DA19501 | T-Shirt | 5 shade spelled in the description only | Driftwood T-Shirt | taupe | taupe t-shirt | generic |
| PLT-DA19502 | T-Shirt | 5 shade spelled in the description only | Dune T-Shirt | beige | beige t-shirt | generic |
| PLT-DA19600 | T-Shirt | 6 incidental word in a range name | Black Tor T-Shirt, Blue | black | black t-shirt | generic |
| PLT-DA19601 | T-Shirt | 6 incidental word in a range name | Blue Meadow T-Shirt, White | blue | blue t-shirt | generic |
| PLT-DA19602 | T-Shirt | 6 incidental word in a range name | Red Fern T-Shirt, Pink | red | red t-shirt | generic |
| PLT-DA19603 | T-Shirt | 6 incidental word in a range name | Dress Circle T-Shirt, Grey | dress | dress | generic |
| PLT-DA19700 | T-Shirt | 7 invented brand holding a color or category word | Red Plover T-Shirt, Grey | red | red t-shirt | generic |
| PLT-DA19701 | T-Shirt | 7 invented brand holding a color or category word | Blue Otter T-Shirt, Black | blue | blue t-shirt | generic |
| PLT-DA19702 | T-Shirt | 7 invented brand holding a color or category word | Black Lapwing T-Shirt, Blue | black | black t-shirt | generic |
| PLT-DA20100 | Tea Dress | 1 color names a part | Blue Tea Dress, Red Piping | red | red tea dress | generic |
| PLT-DA20101 | Tea Dress | 1 color names a part | Navy Tea Dress, Black Piping | black | black tea dress | generic |
| PLT-DA20102 | Tea Dress | 1 color names a part | Brown Tea Dress, Yellow Trim | yellow | yellow tea dress | generic |
| PLT-DA20200 | Tea Dress | 2 another category's noun as a modifier | Blue Skirt Tea Dress | skirt | skirt | generic |
| PLT-DA20201 | Tea Dress | 2 another category's noun as a modifier | Red Jacket Tea Dress | jacket | jacket | generic |
| PLT-DA20202 | Tea Dress | 2 another category's noun as a modifier | Black Cardigan Tea Dress | cardigan | cardigan | generic |
| PLT-DA20300 | Tea Dress | 3 audience word of a sibling version | Black Womens Tea Dress, Mens Fit | mens | mens tea dress | generic |
| PLT-DA20301 | Tea Dress | 3 audience word of a sibling version | Brown Womens Tea Dress, Mens Fit | mens | mens tea dress | generic |
| PLT-DA20302 | Tea Dress | 3 audience word of a sibling version | Pink Womens Tea Dress, Mens-Style | mens | mens tea dress | generic |
| PLT-DA20400 | Tea Dress | 4 material or feature named but absent | Pink Leather-Look Tea Dress | leather | leather tea dress | special: material claim |
| PLT-DA20401 | Tea Dress | 4 material or feature named but absent | White Suede-Look Tea Dress | suede | suede tea dress | special: material claim |
| PLT-DA20402 | Tea Dress | 4 material or feature named but absent | Grey Cashmere-Feel Tea Dress | cashmere | cashmere tea dress | special: material claim |
| PLT-DA20500 | Tea Dress | 5 shade spelled in the description only | Moonbeam Tea Dress | ivory | ivory tea dress | generic |
| PLT-DA20501 | Tea Dress | 5 shade spelled in the description only | Driftwood Tea Dress | taupe | taupe tea dress | generic |
| PLT-DA20502 | Tea Dress | 5 shade spelled in the description only | Dune Tea Dress | beige | beige tea dress | generic |
| PLT-DA20600 | Tea Dress | 6 incidental word in a range name | Red Harbour Tea Dress, Grey | red | red tea dress | generic |
| PLT-DA20601 | Tea Dress | 6 incidental word in a range name | White Cliff Tea Dress, Brown | white | white tea dress | generic |
| PLT-DA20602 | Tea Dress | 6 incidental word in a range name | Green Park Tea Dress, White | green | green tea dress | generic |
| PLT-DA20603 | Tea Dress | 6 incidental word in a range name | Shirt Row Tea Dress, Navy | shirt | shirt | generic |
| PLT-DA20700 | Tea Dress | 7 invented brand holding a color or category word | Red Plover Tea Dress, Pink | red | red tea dress | generic |
| PLT-DA20701 | Tea Dress | 7 invented brand holding a color or category word | Green Stoat Tea Dress, Pink | green | green tea dress | generic |
| PLT-DA20702 | Tea Dress | 7 invented brand holding a color or category word | Blue Otter Tea Dress, Black | blue | blue tea dress | generic |
| PLT-DA21100 | Tee | 1 color names a part | Green Tee, Black Zip | black | black tee | generic |
| PLT-DA21101 | Tee | 1 color names a part | Grey Tee, Red Collar | red | red tee | generic |
| PLT-DA21102 | Tee | 1 color names a part | Grey Tee, Black Zip | black | black tee | generic |
| PLT-DA21200 | Tee | 2 another category's noun as a modifier | Red Skirt Tee | skirt | skirt | generic |
| PLT-DA21201 | Tee | 2 another category's noun as a modifier | Navy Gilet Tee | gilet | gilet | generic |
| PLT-DA21202 | Tee | 2 another category's noun as a modifier | Cream Coat Tee | coat | coat | generic |
| PLT-DA21300 | Tee | 3 audience word of a sibling version | Green Mens Tee, Womens Fit | womens | womens tee | generic |
| PLT-DA21301 | Tee | 3 audience word of a sibling version | Grey Mens Tee, Womens Fit | womens | womens tee | generic |
| PLT-DA21302 | Tee | 3 audience word of a sibling version | Green Mens Tee, Womens-Style | womens | womens tee | generic |
| PLT-DA21400 | Tee | 4 material or feature named but absent | White Leather-Look Tee | leather | leather tee | special: material claim |
| PLT-DA21401 | Tee | 4 material or feature named but absent | Green Suede-Look Tee | suede | suede tee | special: material claim |
| PLT-DA21402 | Tee | 4 material or feature named but absent | Black Cashmere-Feel Tee | cashmere | cashmere tee | special: material claim |
| PLT-DA21500 | Tee | 5 shade spelled in the description only | Moonbeam Tee | ivory | ivory tee | generic |
| PLT-DA21501 | Tee | 5 shade spelled in the description only | Driftwood Tee | taupe | taupe tee | generic |
| PLT-DA21502 | Tee | 5 shade spelled in the description only | Dune Tee | beige | beige tee | generic |
| PLT-DA21600 | Tee | 6 incidental word in a range name | Blue Cove Tee, Brown | blue | blue tee | generic |
| PLT-DA21601 | Tee | 6 incidental word in a range name | Green Park Tee, Cream | green | green tee | generic |
| PLT-DA21602 | Tee | 6 incidental word in a range name | Green Hollow Tee, Grey | green | green tee | generic |
| PLT-DA21603 | Tee | 6 incidental word in a range name | Skirt Point Tee, Brown | skirt | skirt | generic |
| PLT-DA21700 | Tee | 7 invented brand holding a color or category word | Red Plover Tee, Brown | red | red tee | generic |
| PLT-DA21701 | Tee | 7 invented brand holding a color or category word | White Dormouse Tee, Pink | white | white tee | generic |
| PLT-DA21702 | Tee | 7 invented brand holding a color or category word | Black Lapwing Tee, Navy | black | black tee | generic |
| PLT-DA22100 | Top | 1 color names a part | Grey Top, Red Buttons | red | red top | generic |
| PLT-DA22101 | Top | 1 color names a part | Navy Top, Green Trim | green | green top | generic |
| PLT-DA22102 | Top | 1 color names a part | Pink Top, White Lining | white | white top | generic |
| PLT-DA22200 | Top | 2 another category's noun as a modifier | Grey Jacket Top | jacket | jacket | generic |
| PLT-DA22201 | Top | 2 another category's noun as a modifier | Red Skirt Top | skirt | skirt | generic |
| PLT-DA22202 | Top | 2 another category's noun as a modifier | Pink Jacket Top | jacket | jacket | generic |
| PLT-DA22300 | Top | 3 audience word of a sibling version | Green Womens Top, Mens-Style | mens | mens top | generic |
| PLT-DA22301 | Top | 3 audience word of a sibling version | Pink Womens Top, Boys Fit | boys | boys top | generic |
| PLT-DA22302 | Top | 3 audience word of a sibling version | White Womens Top, Boys Fit | boys | boys top | generic |
| PLT-DA22400 | Top | 4 material or feature named but absent | Cream Leather-Look Top | leather | leather top | special: material claim |
| PLT-DA22401 | Top | 4 material or feature named but absent | Cream Suede-Look Top | suede | suede top | special: material claim |
| PLT-DA22402 | Top | 4 material or feature named but absent | Red Cashmere-Feel Top | cashmere | cashmere top | special: material claim |
| PLT-DA22500 | Top | 5 shade spelled in the description only | Moonbeam Top | ivory | ivory top | generic |
| PLT-DA22501 | Top | 5 shade spelled in the description only | Driftwood Top | taupe | taupe top | generic |
| PLT-DA22502 | Top | 5 shade spelled in the description only | Dune Top | beige | beige top | generic |
| PLT-DA22600 | Top | 6 incidental word in a range name | Red Fern Top, Blue | red | red top | generic |
| PLT-DA22601 | Top | 6 incidental word in a range name | Black Tor Top, Brown | black | black top | generic |
| PLT-DA22602 | Top | 6 incidental word in a range name | White Cliff Top, Pink | white | white top | generic |
| PLT-DA22603 | Top | 6 incidental word in a range name | Coat Hook Top, Black | coat | coat | generic |
| PLT-DA22700 | Top | 7 invented brand holding a color or category word | Blue Otter Top, White | blue | blue top | generic |
| PLT-DA22701 | Top | 7 invented brand holding a color or category word | Green Stoat Top, Navy | green | green top | generic |
| PLT-DA22702 | Top | 7 invented brand holding a color or category word | Red Plover Top, Blue | red | red top | generic |
| PLT-DA23100 | Tracksuit | 1 color names a part | Grey Regular Tracksuit, Green Stripes | green | green tracksuit | generic |
| PLT-DA23101 | Tracksuit | 1 color names a part | Green Regular Tracksuit, Red Zip | red | red tracksuit | generic |
| PLT-DA23102 | Tracksuit | 1 color names a part | Red Regular Tracksuit, White Stitching | white | white tracksuit | generic |
| PLT-DA23200 | Tracksuit | 2 another category's noun as a modifier | Brown Poncho Slim Tracksuit | poncho | poncho | generic |
| PLT-DA23201 | Tracksuit | 2 another category's noun as a modifier | Grey Jumper Relaxed Tracksuit | jumper | jumper | generic |
| PLT-DA23202 | Tracksuit | 2 another category's noun as a modifier | Grey Poncho Regular Tracksuit | poncho | poncho | generic |
| PLT-DA23300 | Tracksuit | 3 audience word of a sibling version | White Womens Relaxed Tracksuit, Mens Fit | mens | mens tracksuit | generic |
| PLT-DA23301 | Tracksuit | 3 audience word of a sibling version | Red Womens Slim Tracksuit, Mens-Style | mens | mens tracksuit | generic |
| PLT-DA23302 | Tracksuit | 3 audience word of a sibling version | Red Boys Regular Tracksuit, Mini-Me Womens | womens | womens tracksuit | generic |
| PLT-DA23400 | Tracksuit | 4 material or feature named but absent | Pink Leather-Look Regular Tracksuit | leather | leather tracksuit | special: material claim |
| PLT-DA23401 | Tracksuit | 4 material or feature named but absent | Green Suede-Look Regular Tracksuit | suede | suede tracksuit | special: material claim |
| PLT-DA23402 | Tracksuit | 4 material or feature named but absent | Cream Cashmere-Feel Slim Tracksuit | cashmere | cashmere tracksuit | special: material claim |
| PLT-DA23500 | Tracksuit | 5 shade spelled in the description only | Moonbeam Relaxed Tracksuit | ivory | ivory tracksuit | generic |
| PLT-DA23501 | Tracksuit | 5 shade spelled in the description only | Driftwood Regular Tracksuit | taupe | taupe tracksuit | generic |
| PLT-DA23502 | Tracksuit | 5 shade spelled in the description only | Dune Relaxed Tracksuit | beige | beige tracksuit | generic |
| PLT-DA23600 | Tracksuit | 6 incidental word in a range name | White Cliff Slim Tracksuit, Red | white | white tracksuit | generic |
| PLT-DA23601 | Tracksuit | 6 incidental word in a range name | Blue Meadow Regular Tracksuit, Green | blue | blue tracksuit | generic |
| PLT-DA23602 | Tracksuit | 6 incidental word in a range name | Red Harbour Regular Tracksuit, Navy | red | red tracksuit | generic |
| PLT-DA23603 | Tracksuit | 6 incidental word in a range name | Jacket Quay Regular Tracksuit, Red | jacket | jacket | generic |
| PLT-DA23700 | Tracksuit | 7 invented brand holding a color or category word | Yellow Wagtail Slim Tracksuit, Navy | yellow | yellow tracksuit | generic |
| PLT-DA23701 | Tracksuit | 7 invented brand holding a color or category word | Black Lapwing Relaxed Tracksuit, Navy | black | black tracksuit | generic |
| PLT-DA23702 | Tracksuit | 7 invented brand holding a color or category word | White Dormouse Regular Tracksuit, Green | white | white tracksuit | generic |
| PLT-DA24100 | Trousers | 1 color names a part | Pink Trousers, Green Stitching | green | green trousers | generic |
| PLT-DA24101 | Trousers | 1 color names a part | Cream Trousers, Black Stripes | black | black trousers | generic |
| PLT-DA24102 | Trousers | 1 color names a part | Navy Trousers, Red Zip | red | red trousers | generic |
| PLT-DA24200 | Trousers | 2 another category's noun as a modifier | Navy Cardigan Trousers | cardigan | cardigan | generic |
| PLT-DA24201 | Trousers | 2 another category's noun as a modifier | Black Jacket Trousers | jacket | jacket | generic |
| PLT-DA24202 | Trousers | 2 another category's noun as a modifier | Brown Tunic Trousers | tunic | tunic | generic |
| PLT-DA24300 | Trousers | 3 audience word of a sibling version | White Womens Trousers, Mens Fit | mens | mens trousers | generic |
| PLT-DA24301 | Trousers | 3 audience word of a sibling version | Black Womens Trousers, Boys Fit | boys | boys trousers | generic |
| PLT-DA24302 | Trousers | 3 audience word of a sibling version | Cream Womens Trousers, Mens Fit | mens | mens trousers | generic |
| PLT-DA24400 | Trousers | 4 material or feature named but absent | Grey Leather-Look Trousers | leather | leather trousers | special: material claim |
| PLT-DA24401 | Trousers | 4 material or feature named but absent | Green Suede-Look Trousers | suede | suede trousers | special: material claim |
| PLT-DA24402 | Trousers | 4 material or feature named but absent | Grey Cashmere-Feel Trousers | cashmere | cashmere trousers | special: material claim |
| PLT-DA24500 | Trousers | 5 shade spelled in the description only | Moonbeam Trousers | ivory | ivory trousers | generic |
| PLT-DA24501 | Trousers | 5 shade spelled in the description only | Driftwood Trousers | taupe | taupe trousers | generic |
| PLT-DA24502 | Trousers | 5 shade spelled in the description only | Dune Trousers | beige | beige trousers | generic |
| PLT-DA24600 | Trousers | 6 incidental word in a range name | White Moor Trousers, Red | white | white trousers | generic |
| PLT-DA24601 | Trousers | 6 incidental word in a range name | Red Fern Trousers, Cream | red | red trousers | generic |
| PLT-DA24602 | Trousers | 6 incidental word in a range name | Blue Cove Trousers, Cream | blue | blue trousers | generic |
| PLT-DA24603 | Trousers | 6 incidental word in a range name | Skirt Point Trousers, Navy | skirt | skirt | generic |
| PLT-DA24700 | Trousers | 7 invented brand holding a color or category word | Yellow Wagtail Trousers, Grey | yellow | yellow trousers | generic |
| PLT-DA24701 | Trousers | 7 invented brand holding a color or category word | Green Stoat Trousers, Cream | green | green trousers | generic |
| PLT-DA24702 | Trousers | 7 invented brand holding a color or category word | White Dormouse Trousers, Blue | white | white trousers | generic |
| PLT-DA25100 | Jeans | 1 color names a part | Green Jegging Jeans, Black Stitching | black | black jeans | generic |
| PLT-DA25101 | Jeans | 1 color names a part | White Skinny Jeans, Green Trim | green | green jeans | generic |
| PLT-DA25102 | Jeans | 1 color names a part | Cream Bootcut Jeans, Blue Pocket | blue | blue jeans | generic |
| PLT-DA25103 | Jeans | 1 color names a part | Cream Kick Flare Jeans, White Stripes | white | white jeans | generic |
| PLT-DA25104 | Jeans | 1 color names a part | Black Tapered Jeans, Red Lining | red | red jeans | generic |
| PLT-DA25105 | Jeans | 1 color names a part | Red Straight Jeans, Black Stripes | black | black jeans | generic |
| PLT-DA25106 | Jeans | 1 color names a part | Green Cigarette Jeans, Black Pocket | black | black jeans | generic |
| PLT-DA25107 | Jeans | 1 color names a part | Pink Baggy Jeans, White Stripes | white | white jeans | generic |
| PLT-DA25108 | Jeans | 1 color names a part | Red Super Skinny Jeans, Blue Trim | blue | blue jeans | generic |
| PLT-DA25109 | Jeans | 1 color names a part | Navy Cropped Jeans, Red Buttons | red | red jeans | generic |
| PLT-DA25110 | Jeans | 1 color names a part | Green Wide Leg Jeans, Red Buttons | red | red jeans | generic |
| PLT-DA25111 | Jeans | 1 color names a part | White Wide Leg Jeans, Green Piping | green | green jeans | generic |
| PLT-DA25200 | Jeans | 2 another category's noun as a modifier | Red Tunic Tapered Jeans | tunic | tunic | generic |
| PLT-DA25201 | Jeans | 2 another category's noun as a modifier | Cream Jumper Athletic Jeans | jumper | jumper | generic |
| PLT-DA25202 | Jeans | 2 another category's noun as a modifier | Navy Jacket Culotte Jeans | jacket | jacket | generic |
| PLT-DA25203 | Jeans | 2 another category's noun as a modifier | Navy Jumper Wide Leg Jeans | jumper | jumper | generic |
| PLT-DA25204 | Jeans | 2 another category's noun as a modifier | Blue Cardigan Bootcut Jeans | cardigan | cardigan | generic |
| PLT-DA25205 | Jeans | 2 another category's noun as a modifier | Navy Tunic Cropped Jeans | tunic | tunic | generic |
| PLT-DA25206 | Jeans | 2 another category's noun as a modifier | White Skirt Bootcut Jeans | skirt | skirt | generic |
| PLT-DA25207 | Jeans | 2 another category's noun as a modifier | Grey Shirt Relaxed Jeans | shirt | shirt | generic |
| PLT-DA25208 | Jeans | 2 another category's noun as a modifier | Brown Skirt Slim Jeans | skirt | skirt | generic |
| PLT-DA25209 | Jeans | 2 another category's noun as a modifier | Navy Dress Skinny Jeans | dress | dress | generic |
| PLT-DA25210 | Jeans | 2 another category's noun as a modifier | Blue Hoodie Mom Jeans | hoodie | hoodie | generic |
| PLT-DA25211 | Jeans | 2 another category's noun as a modifier | Pink Blazer Straight Jeans | blazer | blazer | generic |
| PLT-DA25300 | Jeans | 3 audience word of a sibling version | Cream Mens Baggy Jeans, Womens Fit | womens | womens jeans | generic |
| PLT-DA25301 | Jeans | 3 audience word of a sibling version | Navy Mens Athletic Jeans, Girls Fit | girls | girls jeans | generic |
| PLT-DA25302 | Jeans | 3 audience word of a sibling version | Pink Womens Tapered Jeans, Boys Fit | boys | boys jeans | generic |
| PLT-DA25303 | Jeans | 3 audience word of a sibling version | Black Mens Carrot Jeans, Womens Fit | womens | womens jeans | generic |
| PLT-DA25304 | Jeans | 3 audience word of a sibling version | White Womens Carrot Jeans, Mens Fit | mens | mens jeans | generic |
| PLT-DA25305 | Jeans | 3 audience word of a sibling version | Pink Mens Relaxed Jeans, Womens Fit | womens | womens jeans | generic |
| PLT-DA25306 | Jeans | 3 audience word of a sibling version | Navy Womens Super Skinny Jeans, Boys Fit | boys | boys jeans | generic |
| PLT-DA25307 | Jeans | 3 audience word of a sibling version | Cream Womens Jegging Jeans, Boys Fit | boys | boys jeans | generic |
| PLT-DA25308 | Jeans | 3 audience word of a sibling version | Pink Womens Flared Jeans, Mens-Style | mens | mens jeans | generic |
| PLT-DA25309 | Jeans | 3 audience word of a sibling version | Navy Womens Kick Flare Jeans, Mens-Style | mens | mens jeans | generic |
| PLT-DA25310 | Jeans | 3 audience word of a sibling version | Pink Womens Bootcut Jeans, Mens Fit | mens | mens jeans | generic |
| PLT-DA25311 | Jeans | 3 audience word of a sibling version | Brown Womens Boyfriend Jeans, Mens Fit | mens | mens jeans | generic |
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
| PLT-DA25506 | Jeans | 5 shade spelled in the description only | Pebble Jegging Jeans | ecru | ecru jeans | generic |
| PLT-DA25507 | Jeans | 5 shade spelled in the description only | Meadow Skinny Jeans | mint | mint jeans | generic |
| PLT-DA25508 | Jeans | 5 shade spelled in the description only | Harvest Bootcut Jeans | rust | rust jeans | generic |
| PLT-DA25509 | Jeans | 5 shade spelled in the description only | Seashell Kick Flare Jeans | coral | coral jeans | generic |
| PLT-DA25510 | Jeans | 5 shade spelled in the description only | Biscuit Tapered Jeans | champagne | champagne jeans | generic |
| PLT-DA25511 | Jeans | 5 shade spelled in the description only | Hearth Straight Jeans | khaki | khaki jeans | generic |
| PLT-DA25600 | Jeans | 6 incidental word in a range name | Yellow Marsh Cigarette Jeans, Black | yellow | yellow jeans | generic |
| PLT-DA25601 | Jeans | 6 incidental word in a range name | Blue Cove Baggy Jeans, Cream | blue | blue jeans | generic |
| PLT-DA25602 | Jeans | 6 incidental word in a range name | Red Fern Super Skinny Jeans, Green | red | red jeans | generic |
| PLT-DA25603 | Jeans | 6 incidental word in a range name | Blue Meadow Cropped Jeans, Green | blue | blue jeans | generic |
| PLT-DA25604 | Jeans | 6 incidental word in a range name | Black Tor Wide Leg Jeans, Pink | black | black jeans | generic |
| PLT-DA25605 | Jeans | 6 incidental word in a range name | Green Park Wide Leg Jeans, Grey | green | green jeans | generic |
| PLT-DA25606 | Jeans | 6 incidental word in a range name | Red Fern Tapered Jeans, Green | red | red jeans | generic |
| PLT-DA25607 | Jeans | 6 incidental word in a range name | Green Hollow Athletic Jeans, Pink | green | green jeans | generic |
| PLT-DA25608 | Jeans | 6 incidental word in a range name | Green Hollow Culotte Jeans, Grey | green | green jeans | generic |
| PLT-DA25609 | Jeans | 6 incidental word in a range name | Blue Cove Wide Leg Jeans, Pink | blue | blue jeans | generic |
| PLT-DA25610 | Jeans | 6 incidental word in a range name | White Cliff Bootcut Jeans, Black | white | white jeans | generic |
| PLT-DA25611 | Jeans | 6 incidental word in a range name | White Cliff Cropped Jeans, Brown | white | white jeans | generic |
| PLT-DA25612 | Jeans | 6 incidental word in a range name | Dress Circle Bootcut Jeans, Red | dress | dress | generic |
| PLT-DA25700 | Jeans | 7 invented brand holding a color or category word | Yellow Wagtail Relaxed Jeans, Red | yellow | yellow jeans | generic |
| PLT-DA25701 | Jeans | 7 invented brand holding a color or category word | Red Plover Slim Jeans, Brown | red | red jeans | generic |
| PLT-DA25702 | Jeans | 7 invented brand holding a color or category word | Jumper Jay Skinny Jeans, Blue | jumper | jumper jeans | generic |
| PLT-DA25703 | Jeans | 7 invented brand holding a color or category word | White Dormouse Mom Jeans, Pink | white | white jeans | generic |
| PLT-DA25704 | Jeans | 7 invented brand holding a color or category word | Green Stoat Straight Jeans, Brown | green | green jeans | generic |
| PLT-DA25705 | Jeans | 7 invented brand holding a color or category word | Yellow Wagtail Baggy Jeans, Blue | yellow | yellow jeans | generic |
| PLT-DA25706 | Jeans | 7 invented brand holding a color or category word | White Dormouse Athletic Jeans, Cream | white | white jeans | generic |
| PLT-DA25707 | Jeans | 7 invented brand holding a color or category word | Green Stoat Tapered Jeans, White | green | green jeans | generic |
| PLT-DA26100 | Socks | 1 color names a part | Green Socks, Blue Cuff | blue | blue socks | generic |
| PLT-DA26101 | Socks | 1 color names a part | Blue Socks, White Trim | white | white socks | generic |
| PLT-DA26102 | Socks | 1 color names a part | Black Socks, Yellow Cuff | yellow | yellow socks | generic |
| PLT-DA26200 | Socks | 2 another category's noun as a modifier | Green Trainer Socks | trainer | trainer | generic |
| PLT-DA26201 | Socks | 2 another category's noun as a modifier | Brown Slipper Socks | slipper | slipper | generic |
| PLT-DA26202 | Socks | 2 another category's noun as a modifier | Black Boot Socks | boot | boot | generic |
| PLT-DA26300 | Socks | 3 audience word of a sibling version | White Unisex Socks, Mini-Me Mens | mens | mens socks | generic |
| PLT-DA26301 | Socks | 3 audience word of a sibling version | Red Mens Socks, Womens Fit | womens | womens socks | generic |
| PLT-DA26302 | Socks | 3 audience word of a sibling version | Green Mens Socks, Girls Fit | girls | girls socks | generic |
| PLT-DA26400 | Socks | 4 material or feature named but absent | Green Leather-Look Socks | leather | leather socks | special: material claim |
| PLT-DA26401 | Socks | 4 material or feature named but absent | Cream Suede-Look Socks | suede | suede socks | special: material claim |
| PLT-DA26402 | Socks | 4 material or feature named but absent | Cream Cashmere-Feel Socks | cashmere | cashmere socks | special: material claim |
| PLT-DA26500 | Socks | 5 shade spelled in the description only | Moonbeam Socks | ivory | ivory socks | generic |
| PLT-DA26501 | Socks | 5 shade spelled in the description only | Driftwood Socks | taupe | taupe socks | generic |
| PLT-DA26502 | Socks | 5 shade spelled in the description only | Dune Socks | beige | beige socks | generic |
| PLT-DA26600 | Socks | 6 incidental word in a range name | Black Mill Socks, Pink | black | black socks | generic |
| PLT-DA26601 | Socks | 6 incidental word in a range name | Red Fern Socks, Blue | red | red socks | generic |
| PLT-DA26602 | Socks | 6 incidental word in a range name | Yellow Brook Socks, Pink | yellow | yellow socks | generic |
| PLT-DA26603 | Socks | 6 incidental word in a range name | Dress Circle Socks, Green | dress | dress | generic |
| PLT-DA26700 | Socks | 7 invented brand holding a color or category word | Green Stoat Socks, Brown | green | green socks | generic |
| PLT-DA26701 | Socks | 7 invented brand holding a color or category word | White Dormouse Socks, Grey | white | white socks | generic |
| PLT-DA26702 | Socks | 7 invented brand holding a color or category word | Blue Otter Socks, White | blue | blue socks | generic |
| PLT-DA27100 | Boot Socks | 1 color names a part | Brown Boot Socks, Yellow Heel | yellow | yellow boot socks | generic |
| PLT-DA27101 | Boot Socks | 1 color names a part | Red Boot Socks, Yellow Trim | yellow | yellow boot socks | generic |
| PLT-DA27102 | Boot Socks | 1 color names a part | Grey Boot Socks, Yellow Cuff | yellow | yellow boot socks | generic |
| PLT-DA27200 | Boot Socks | 2 another category's noun as a modifier | Green Shoe Boot Socks | shoe | shoe | generic |
| PLT-DA27201 | Boot Socks | 2 another category's noun as a modifier | Grey Trouser Boot Socks | trouser | trouser | generic |
| PLT-DA27202 | Boot Socks | 2 another category's noun as a modifier | Grey Trainer Boot Socks | trainer | trainer | generic |
| PLT-DA27300 | Boot Socks | 3 audience word of a sibling version | Cream Womens Boot Socks, Boys Fit | boys | boys boot socks | generic |
| PLT-DA27301 | Boot Socks | 3 audience word of a sibling version | Red Womens Boot Socks, Boys Fit | boys | boys boot socks | generic |
| PLT-DA27302 | Boot Socks | 3 audience word of a sibling version | Cream Womens Boot Socks, Mens-Style | mens | mens boot socks | generic |
| PLT-DA27400 | Boot Socks | 4 material or feature named but absent | Green Leather-Look Boot Socks | leather | leather boot socks | special: material claim |
| PLT-DA27401 | Boot Socks | 4 material or feature named but absent | Pink Suede-Look Boot Socks | suede | suede boot socks | special: material claim |
| PLT-DA27402 | Boot Socks | 4 material or feature named but absent | Red Cashmere-Feel Boot Socks | cashmere | cashmere boot socks | special: material claim |
| PLT-DA27500 | Boot Socks | 5 shade spelled in the description only | Moonbeam Boot Socks | ivory | ivory boot socks | generic |
| PLT-DA27501 | Boot Socks | 5 shade spelled in the description only | Driftwood Boot Socks | taupe | taupe boot socks | generic |
| PLT-DA27502 | Boot Socks | 5 shade spelled in the description only | Dune Boot Socks | beige | beige boot socks | generic |
| PLT-DA27600 | Boot Socks | 6 incidental word in a range name | Green Hollow Boot Socks, Blue | green | green boot socks | generic |
| PLT-DA27601 | Boot Socks | 6 incidental word in a range name | Blue Cove Boot Socks, Navy | blue | blue boot socks | generic |
| PLT-DA27602 | Boot Socks | 6 incidental word in a range name | Green Park Boot Socks, Blue | green | green boot socks | generic |
| PLT-DA27603 | Boot Socks | 6 incidental word in a range name | Skirt Point Boot Socks, Pink | skirt | skirt | generic |
| PLT-DA27700 | Boot Socks | 7 invented brand holding a color or category word | Blue Otter Boot Socks, Brown | blue | blue boot socks | generic |
| PLT-DA27701 | Boot Socks | 7 invented brand holding a color or category word | Red Plover Boot Socks, Grey | red | red boot socks | generic |
| PLT-DA27702 | Boot Socks | 7 invented brand holding a color or category word | White Dormouse Boot Socks, Grey | white | white boot socks | generic |
| PLT-DA28100 | Ankle Boots | 1 color names a part | Brown Ankle Boots, Black Trim | black | black ankle boots | generic |
| PLT-DA28101 | Ankle Boots | 1 color names a part | Navy Ankle Boots, Green Heel | green | green ankle boots | generic |
| PLT-DA28102 | Ankle Boots | 1 color names a part | Green Ankle Boots, Yellow Heel | yellow | yellow ankle boots | generic |
| PLT-DA28200 | Ankle Boots | 2 another category's noun as a modifier | Grey Sandal Ankle Boots | sandal | sandal | generic |
| PLT-DA28201 | Ankle Boots | 2 another category's noun as a modifier | White Sandal Ankle Boots | sandal | sandal | generic |
| PLT-DA28202 | Ankle Boots | 2 another category's noun as a modifier | Navy Slipper Ankle Boots | slipper | slipper | generic |
| PLT-DA28300 | Ankle Boots | 3 audience word of a sibling version | Red Womens Ankle Boots, Mens-Style | mens | mens ankle boots | generic |
| PLT-DA28301 | Ankle Boots | 3 audience word of a sibling version | White Womens Ankle Boots, Mens Fit | mens | mens ankle boots | generic |
| PLT-DA28302 | Ankle Boots | 3 audience word of a sibling version | Grey Womens Ankle Boots, Boys Fit | boys | boys ankle boots | generic |
| PLT-DA28400 | Ankle Boots | 4 material or feature named but absent | Grey Leather-Look Ankle Boots, Suede | leather | leather ankle boots | special: material claim |
| PLT-DA28401 | Ankle Boots | 4 material or feature named but absent | White Cashmere-Feel Ankle Boots, Suede | cashmere | cashmere ankle boots | special: material claim |
| PLT-DA28402 | Ankle Boots | 4 material or feature named but absent | Cream Wool-Free Ankle Boots, Suede | wool | wool ankle boots | special: material claim |
| PLT-DA28500 | Ankle Boots | 5 shade spelled in the description only | Moonbeam Ankle Boots | ivory | ivory ankle boots | generic |
| PLT-DA28501 | Ankle Boots | 5 shade spelled in the description only | Driftwood Ankle Boots | taupe | taupe ankle boots | generic |
| PLT-DA28502 | Ankle Boots | 5 shade spelled in the description only | Dune Ankle Boots | beige | beige ankle boots | generic |
| PLT-DA28600 | Ankle Boots | 6 incidental word in a range name | Green Hollow Ankle Boots, Red | green | green ankle boots | generic |
| PLT-DA28601 | Ankle Boots | 6 incidental word in a range name | Red Fern Ankle Boots, Navy | red | red ankle boots | generic |
| PLT-DA28602 | Ankle Boots | 6 incidental word in a range name | Black Tor Ankle Boots, Cream | black | black ankle boots | generic |
| PLT-DA28603 | Ankle Boots | 6 incidental word in a range name | Coat Hook Ankle Boots, Navy | coat | coat | generic |
| PLT-DA28700 | Ankle Boots | 7 invented brand holding a color or category word | Blue Otter Ankle Boots, Black | blue | blue ankle boots | generic |
| PLT-DA28701 | Ankle Boots | 7 invented brand holding a color or category word | Coat Crake Ankle Boots, Grey | coat | coat ankle boots | generic |
| PLT-DA28702 | Ankle Boots | 7 invented brand holding a color or category word | Yellow Wagtail Ankle Boots, Red | yellow | yellow ankle boots | generic |
| PLT-DA29100 | Ballet Pumps | 1 color names a part | Red Ballet Pumps, Blue Heel | blue | blue ballet pumps | generic |
| PLT-DA29101 | Ballet Pumps | 1 color names a part | Red Ballet Pumps, Blue Eyelets | blue | blue ballet pumps | generic |
| PLT-DA29102 | Ballet Pumps | 1 color names a part | Black Ballet Pumps, Blue Stitching | blue | blue ballet pumps | generic |
| PLT-DA29200 | Ballet Pumps | 2 another category's noun as a modifier | Red Sock Ballet Pumps | sock | sock | generic |
| PLT-DA29201 | Ballet Pumps | 2 another category's noun as a modifier | Red Sandal Ballet Pumps | sandal | sandal | generic |
| PLT-DA29202 | Ballet Pumps | 2 another category's noun as a modifier | Green Boot Ballet Pumps | boot | boot | generic |
| PLT-DA29300 | Ballet Pumps | 3 audience word of a sibling version | Brown Womens Ballet Pumps, Mens-Style | mens | mens ballet pumps | generic |
| PLT-DA29301 | Ballet Pumps | 3 audience word of a sibling version | Green Womens Ballet Pumps, Mens-Style | mens | mens ballet pumps | generic |
| PLT-DA29302 | Ballet Pumps | 3 audience word of a sibling version | Red Womens Ballet Pumps, Mens Fit | mens | mens ballet pumps | generic |
| PLT-DA29400 | Ballet Pumps | 4 material or feature named but absent | Black Cashmere-Feel Ballet Pumps, Leather, Suede, Patent | cashmere | cashmere ballet pumps | special: material claim |
| PLT-DA29401 | Ballet Pumps | 4 material or feature named but absent | Blue Wool-Free Ballet Pumps, Leather, Suede, Patent | wool | wool ballet pumps | special: material claim |
| PLT-DA29402 | Ballet Pumps | 4 material or feature named but absent | Pink Silk-Free Ballet Pumps, Leather, Suede, Patent | silk | silk ballet pumps | special: material claim |
| PLT-DA29500 | Ballet Pumps | 5 shade spelled in the description only | Moonbeam Ballet Pumps | ivory | ivory ballet pumps | generic |
| PLT-DA29501 | Ballet Pumps | 5 shade spelled in the description only | Driftwood Ballet Pumps | taupe | taupe ballet pumps | generic |
| PLT-DA29502 | Ballet Pumps | 5 shade spelled in the description only | Dune Ballet Pumps | beige | beige ballet pumps | generic |
| PLT-DA29600 | Ballet Pumps | 6 incidental word in a range name | White Moor Ballet Pumps, Grey | white | white ballet pumps | generic |
| PLT-DA29601 | Ballet Pumps | 6 incidental word in a range name | Green Park Ballet Pumps, White | green | green ballet pumps | generic |
| PLT-DA29602 | Ballet Pumps | 6 incidental word in a range name | Yellow Marsh Ballet Pumps, Pink | yellow | yellow ballet pumps | generic |
| PLT-DA29603 | Ballet Pumps | 6 incidental word in a range name | Shirt Row Ballet Pumps, Brown | shirt | shirt | generic |
| PLT-DA29700 | Ballet Pumps | 7 invented brand holding a color or category word | Black Lapwing Ballet Pumps, Pink | black | black ballet pumps | generic |
| PLT-DA29701 | Ballet Pumps | 7 invented brand holding a color or category word | White Dormouse Ballet Pumps, Cream | white | white ballet pumps | generic |
| PLT-DA29702 | Ballet Pumps | 7 invented brand holding a color or category word | Jumper Jay Ballet Pumps, Cream | jumper | jumper ballet pumps | generic |
| PLT-DA30100 | Block Heels | 1 color names a part | Brown Block Heels, Blue Heel | blue | blue block heels | generic |
| PLT-DA30101 | Block Heels | 1 color names a part | Pink Block Heels, Black Heel | black | black block heels | generic |
| PLT-DA30102 | Block Heels | 1 color names a part | Red Block Heels, Yellow Heel | yellow | yellow block heels | generic |
| PLT-DA30200 | Block Heels | 2 another category's noun as a modifier | Brown Sneaker Block Heels | sneaker | sneaker | generic |
| PLT-DA30201 | Block Heels | 2 another category's noun as a modifier | Cream Sneaker Block Heels | sneaker | sneaker | generic |
| PLT-DA30202 | Block Heels | 2 another category's noun as a modifier | Pink Slipper Block Heels | slipper | slipper | generic |
| PLT-DA30300 | Block Heels | 3 audience word of a sibling version | Red Womens Block Heels, Mens Fit | mens | mens block heels | generic |
| PLT-DA30301 | Block Heels | 3 audience word of a sibling version | Brown Womens Block Heels, Boys Fit | boys | boys block heels | generic |
| PLT-DA30302 | Block Heels | 3 audience word of a sibling version | White Womens Block Heels, Mens Fit | mens | mens block heels | generic |
| PLT-DA30400 | Block Heels | 4 material or feature named but absent | Pink Cashmere-Feel Block Heels, Suede, Leather | cashmere | cashmere block heels | special: material claim |
| PLT-DA30401 | Block Heels | 4 material or feature named but absent | Red Wool-Free Block Heels, Suede, Leather | wool | wool block heels | special: material claim |
| PLT-DA30402 | Block Heels | 4 material or feature named but absent | Red Silk-Feel Block Heels, Suede, Leather | silk | silk block heels | special: material claim |
| PLT-DA30500 | Block Heels | 5 shade spelled in the description only | Moonbeam Block Heels | ivory | ivory block heels | generic |
| PLT-DA30501 | Block Heels | 5 shade spelled in the description only | Driftwood Block Heels | taupe | taupe block heels | generic |
| PLT-DA30502 | Block Heels | 5 shade spelled in the description only | Dune Block Heels | beige | beige block heels | generic |
| PLT-DA30600 | Block Heels | 6 incidental word in a range name | Yellow Brook Block Heels, Black | yellow | yellow block heels | generic |
| PLT-DA30601 | Block Heels | 6 incidental word in a range name | Green Hollow Block Heels, Grey | green | green block heels | generic |
| PLT-DA30602 | Block Heels | 6 incidental word in a range name | White Moor Block Heels, Grey | white | white block heels | generic |
| PLT-DA30603 | Block Heels | 6 incidental word in a range name | Dress Circle Block Heels, Brown | dress | dress | generic |
| PLT-DA30700 | Block Heels | 7 invented brand holding a color or category word | Red Plover Block Heels, Green | red | red block heels | generic |
| PLT-DA30701 | Block Heels | 7 invented brand holding a color or category word | Coat Crake Block Heels, White | coat | coat block heels | generic |
| PLT-DA30702 | Block Heels | 7 invented brand holding a color or category word | Green Stoat Block Heels, Pink | green | green block heels | generic |
| PLT-DA31100 | Brogues | 1 color names a part | Black Brogues, White Lining | white | white brogues | generic |
| PLT-DA31101 | Brogues | 1 color names a part | Cream Brogues, Blue Trim | blue | blue brogues | generic |
| PLT-DA31102 | Brogues | 1 color names a part | Blue Brogues, White Eyelets | white | white brogues | generic |
| PLT-DA31200 | Brogues | 2 another category's noun as a modifier | Brown Loafer Brogues | loafer | loafer | generic |
| PLT-DA31201 | Brogues | 2 another category's noun as a modifier | Navy Sandal Brogues | sandal | sandal | generic |
| PLT-DA31202 | Brogues | 2 another category's noun as a modifier | Grey Mule Brogues | mule | mule | generic |
| PLT-DA31300 | Brogues | 3 audience word of a sibling version | Brown Mens Brogues, Womens Fit | womens | womens brogues | generic |
| PLT-DA31301 | Brogues | 3 audience word of a sibling version | Grey Womens Brogues, Mens-Style | mens | mens brogues | generic |
| PLT-DA31302 | Brogues | 3 audience word of a sibling version | Red Mens Brogues, Girls Fit | girls | girls brogues | generic |
| PLT-DA31400 | Brogues | 4 material or feature named but absent | White Suede-Look Brogues, Leather | suede | suede brogues | special: material claim |
| PLT-DA31401 | Brogues | 4 material or feature named but absent | Red Cashmere-Feel Brogues, Leather | cashmere | cashmere brogues | special: material claim |
| PLT-DA31402 | Brogues | 4 material or feature named but absent | Green Wool-Free Brogues, Leather | wool | wool brogues | special: material claim |
| PLT-DA31500 | Brogues | 5 shade spelled in the description only | Moonbeam Brogues | ivory | ivory brogues | generic |
| PLT-DA31501 | Brogues | 5 shade spelled in the description only | Driftwood Brogues | taupe | taupe brogues | generic |
| PLT-DA31502 | Brogues | 5 shade spelled in the description only | Dune Brogues | beige | beige brogues | generic |
| PLT-DA31600 | Brogues | 6 incidental word in a range name | Green Hollow Brogues, Red | green | green brogues | generic |
| PLT-DA31601 | Brogues | 6 incidental word in a range name | Red Harbour Brogues, Cream | red | red brogues | generic |
| PLT-DA31602 | Brogues | 6 incidental word in a range name | Red Fern Brogues, Blue | red | red brogues | generic |
| PLT-DA31603 | Brogues | 6 incidental word in a range name | Shirt Row Brogues, Blue | shirt | shirt | generic |
| PLT-DA31700 | Brogues | 7 invented brand holding a color or category word | Yellow Wagtail Brogues, Cream | yellow | yellow brogues | generic |
| PLT-DA31701 | Brogues | 7 invented brand holding a color or category word | Yellow Wagtail Brogues, Cream | yellow | yellow brogues | generic |
| PLT-DA31702 | Brogues | 7 invented brand holding a color or category word | Red Plover Brogues, Brown | red | red brogues | generic |
| PLT-DA32100 | Chelsea Boots | 1 color names a part | Grey Chelsea Boots, White Stitching | white | white chelsea boots | generic |
| PLT-DA32101 | Chelsea Boots | 1 color names a part | Grey Chelsea Boots, Yellow Sole | yellow | yellow chelsea boots | generic |
| PLT-DA32102 | Chelsea Boots | 1 color names a part | Green Chelsea Boots, White Heel | white | white chelsea boots | generic |
| PLT-DA32200 | Chelsea Boots | 2 another category's noun as a modifier | Cream Loafer Chelsea Boots | loafer | loafer | generic |
| PLT-DA32201 | Chelsea Boots | 2 another category's noun as a modifier | Pink Slipper Chelsea Boots | slipper | slipper | generic |
| PLT-DA32202 | Chelsea Boots | 2 another category's noun as a modifier | Green Heel Chelsea Boots | heel | heel | generic |
| PLT-DA32300 | Chelsea Boots | 3 audience word of a sibling version | Black Mens Chelsea Boots, Womens-Style | womens | womens chelsea boots | generic |
| PLT-DA32301 | Chelsea Boots | 3 audience word of a sibling version | Brown Womens Chelsea Boots, Boys Fit | boys | boys chelsea boots | generic |
| PLT-DA32302 | Chelsea Boots | 3 audience word of a sibling version | Red Mens Chelsea Boots, Girls Fit | girls | girls chelsea boots | generic |
| PLT-DA32400 | Chelsea Boots | 4 material or feature named but absent | Cream Suede-Look Chelsea Boots, Leather | suede | suede chelsea boots | special: material claim |
| PLT-DA32401 | Chelsea Boots | 4 material or feature named but absent | Red Leather-Look Chelsea Boots, Suede | leather | leather chelsea boots | special: material claim |
| PLT-DA32402 | Chelsea Boots | 4 material or feature named but absent | Red Cashmere-Feel Chelsea Boots, Leather | cashmere | cashmere chelsea boots | special: material claim |
| PLT-DA32500 | Chelsea Boots | 5 shade spelled in the description only | Moonbeam Chelsea Boots | ivory | ivory chelsea boots | generic |
| PLT-DA32501 | Chelsea Boots | 5 shade spelled in the description only | Driftwood Chelsea Boots | taupe | taupe chelsea boots | generic |
| PLT-DA32502 | Chelsea Boots | 5 shade spelled in the description only | Dune Chelsea Boots | beige | beige chelsea boots | generic |
| PLT-DA32600 | Chelsea Boots | 6 incidental word in a range name | Black Mill Chelsea Boots, White | black | black chelsea boots | generic |
| PLT-DA32601 | Chelsea Boots | 6 incidental word in a range name | Blue Cove Chelsea Boots, Green | blue | blue chelsea boots | generic |
| PLT-DA32602 | Chelsea Boots | 6 incidental word in a range name | Yellow Brook Chelsea Boots, Brown | yellow | yellow chelsea boots | generic |
| PLT-DA32603 | Chelsea Boots | 6 incidental word in a range name | Shirt Row Chelsea Boots, Pink | shirt | shirt | generic |
| PLT-DA32700 | Chelsea Boots | 7 invented brand holding a color or category word | Black Lapwing Chelsea Boots, Brown | black | black chelsea boots | generic |
| PLT-DA32701 | Chelsea Boots | 7 invented brand holding a color or category word | Black Lapwing Chelsea Boots, Blue | black | black chelsea boots | generic |
| PLT-DA32702 | Chelsea Boots | 7 invented brand holding a color or category word | Yellow Wagtail Chelsea Boots, Cream | yellow | yellow chelsea boots | generic |
| PLT-DA33100 | Chukka Boots | 1 color names a part | Navy Chukka Boots, Red Stitching | red | red chukka boots | generic |
| PLT-DA33101 | Chukka Boots | 1 color names a part | Green Chukka Boots, Yellow Sole | yellow | yellow chukka boots | generic |
| PLT-DA33102 | Chukka Boots | 1 color names a part | Grey Chukka Boots, Green Trim | green | green chukka boots | generic |
| PLT-DA33200 | Chukka Boots | 2 another category's noun as a modifier | White Pump Chukka Boots | pump | pump | generic |
| PLT-DA33201 | Chukka Boots | 2 another category's noun as a modifier | Navy Sneaker Chukka Boots | sneaker | sneaker | generic |
| PLT-DA33202 | Chukka Boots | 2 another category's noun as a modifier | Navy Trainer Chukka Boots | trainer | trainer | generic |
| PLT-DA33300 | Chukka Boots | 3 audience word of a sibling version | Black Mens Chukka Boots, Girls Fit | girls | girls chukka boots | generic |
| PLT-DA33301 | Chukka Boots | 3 audience word of a sibling version | White Mens Chukka Boots, Girls Fit | girls | girls chukka boots | generic |
| PLT-DA33302 | Chukka Boots | 3 audience word of a sibling version | Blue Mens Chukka Boots, Girls Fit | girls | girls chukka boots | generic |
| PLT-DA33400 | Chukka Boots | 4 material or feature named but absent | Black Leather-Look Chukka Boots, Suede | leather | leather chukka boots | special: material claim |
| PLT-DA33401 | Chukka Boots | 4 material or feature named but absent | Red Cashmere-Feel Chukka Boots, Suede | cashmere | cashmere chukka boots | special: material claim |
| PLT-DA33402 | Chukka Boots | 4 material or feature named but absent | Blue Wool-Free Chukka Boots, Suede | wool | wool chukka boots | special: material claim |
| PLT-DA33500 | Chukka Boots | 5 shade spelled in the description only | Moonbeam Chukka Boots | ivory | ivory chukka boots | generic |
| PLT-DA33501 | Chukka Boots | 5 shade spelled in the description only | Driftwood Chukka Boots | taupe | taupe chukka boots | generic |
| PLT-DA33502 | Chukka Boots | 5 shade spelled in the description only | Dune Chukka Boots | beige | beige chukka boots | generic |
| PLT-DA33600 | Chukka Boots | 6 incidental word in a range name | Red Harbour Chukka Boots, Navy | red | red chukka boots | generic |
| PLT-DA33601 | Chukka Boots | 6 incidental word in a range name | Green Hollow Chukka Boots, White | green | green chukka boots | generic |
| PLT-DA33602 | Chukka Boots | 6 incidental word in a range name | White Moor Chukka Boots, Black | white | white chukka boots | generic |
| PLT-DA33603 | Chukka Boots | 6 incidental word in a range name | Jacket Quay Chukka Boots, Pink | jacket | jacket | generic |
| PLT-DA33700 | Chukka Boots | 7 invented brand holding a color or category word | White Dormouse Chukka Boots, Grey | white | white chukka boots | generic |
| PLT-DA33701 | Chukka Boots | 7 invented brand holding a color or category word | Green Stoat Chukka Boots, Navy | green | green chukka boots | generic |
| PLT-DA33702 | Chukka Boots | 7 invented brand holding a color or category word | Jumper Jay Chukka Boots, Cream | jumper | jumper chukka boots | generic |
| PLT-DA34100 | Court Shoes | 1 color names a part | White Court Shoes, Red Heel | red | red court shoes | generic |
| PLT-DA34101 | Court Shoes | 1 color names a part | Navy Court Shoes, Red Eyelets | red | red court shoes | generic |
| PLT-DA34102 | Court Shoes | 1 color names a part | Green Court Shoes, Yellow Sole | yellow | yellow court shoes | generic |
| PLT-DA34200 | Court Shoes | 2 another category's noun as a modifier | Green Sock Court Shoes | sock | sock | generic |
| PLT-DA34201 | Court Shoes | 2 another category's noun as a modifier | Black Slipper Court Shoes | slipper | slipper | generic |
| PLT-DA34202 | Court Shoes | 2 another category's noun as a modifier | Blue Sneaker Court Shoes | sneaker | sneaker | generic |
| PLT-DA34300 | Court Shoes | 3 audience word of a sibling version | Black Womens Court Shoes, Boys Fit | boys | boys court shoes | generic |
| PLT-DA34301 | Court Shoes | 3 audience word of a sibling version | Pink Womens Court Shoes, Mens Fit | mens | mens court shoes | generic |
| PLT-DA34302 | Court Shoes | 3 audience word of a sibling version | Brown Womens Court Shoes, Boys Fit | boys | boys court shoes | generic |
| PLT-DA34400 | Court Shoes | 4 material or feature named but absent | Blue Cashmere-Feel Court Shoes, Patent, Suede | cashmere | cashmere court shoes | special: material claim |
| PLT-DA34401 | Court Shoes | 4 material or feature named but absent | Brown Wool-Free Court Shoes, Patent, Suede | wool | wool court shoes | special: material claim |
| PLT-DA34402 | Court Shoes | 4 material or feature named but absent | Brown Silk-Free Court Shoes, Patent, Suede | silk | silk court shoes | special: material claim |
| PLT-DA34500 | Court Shoes | 5 shade spelled in the description only | Moonbeam Court Shoes | ivory | ivory court shoes | generic |
| PLT-DA34501 | Court Shoes | 5 shade spelled in the description only | Driftwood Court Shoes | taupe | taupe court shoes | generic |
| PLT-DA34502 | Court Shoes | 5 shade spelled in the description only | Dune Court Shoes | beige | beige court shoes | generic |
| PLT-DA34600 | Court Shoes | 6 incidental word in a range name | Red Fern Court Shoes, Black | red | red court shoes | generic |
| PLT-DA34601 | Court Shoes | 6 incidental word in a range name | Black Mill Court Shoes, Green | black | black court shoes | generic |
| PLT-DA34602 | Court Shoes | 6 incidental word in a range name | Green Park Court Shoes, Pink | green | green court shoes | generic |
| PLT-DA34603 | Court Shoes | 6 incidental word in a range name | Boot Hill Court Shoes, Pink | boot | boot | generic |
| PLT-DA34700 | Court Shoes | 7 invented brand holding a color or category word | Yellow Wagtail Court Shoes, Brown | yellow | yellow court shoes | generic |
| PLT-DA34701 | Court Shoes | 7 invented brand holding a color or category word | Blue Otter Court Shoes, Brown | blue | blue court shoes | generic |
| PLT-DA34702 | Court Shoes | 7 invented brand holding a color or category word | Jumper Jay Court Shoes, Green | jumper | jumper court shoes | generic |
| PLT-DA35100 | Kitten Heels | 1 color names a part | White Kitten Heels, Blue Eyelets | blue | blue kitten heels | generic |
| PLT-DA35101 | Kitten Heels | 1 color names a part | Pink Kitten Heels, Green Heel | green | green kitten heels | generic |
| PLT-DA35102 | Kitten Heels | 1 color names a part | Grey Kitten Heels, Yellow Trim | yellow | yellow kitten heels | generic |
| PLT-DA35200 | Kitten Heels | 2 another category's noun as a modifier | Pink Pump Kitten Heels | pump | pump | generic |
| PLT-DA35201 | Kitten Heels | 2 another category's noun as a modifier | Black Sneaker Kitten Heels | sneaker | sneaker | generic |
| PLT-DA35202 | Kitten Heels | 2 another category's noun as a modifier | Grey Loafer Kitten Heels | loafer | loafer | generic |
| PLT-DA35300 | Kitten Heels | 3 audience word of a sibling version | Brown Womens Kitten Heels, Mens-Style | mens | mens kitten heels | generic |
| PLT-DA35301 | Kitten Heels | 3 audience word of a sibling version | Navy Womens Kitten Heels, Mens Fit | mens | mens kitten heels | generic |
| PLT-DA35302 | Kitten Heels | 3 audience word of a sibling version | Cream Womens Kitten Heels, Boys Fit | boys | boys kitten heels | generic |
| PLT-DA35400 | Kitten Heels | 4 material or feature named but absent | Red Suede-Look Kitten Heels, Leather | suede | suede kitten heels | special: material claim |
| PLT-DA35401 | Kitten Heels | 4 material or feature named but absent | Green Cashmere-Feel Kitten Heels, Leather | cashmere | cashmere kitten heels | special: material claim |
| PLT-DA35402 | Kitten Heels | 4 material or feature named but absent | Grey Wool-Free Kitten Heels, Leather | wool | wool kitten heels | special: material claim |
| PLT-DA35500 | Kitten Heels | 5 shade spelled in the description only | Moonbeam Kitten Heels | ivory | ivory kitten heels | generic |
| PLT-DA35501 | Kitten Heels | 5 shade spelled in the description only | Driftwood Kitten Heels | taupe | taupe kitten heels | generic |
| PLT-DA35502 | Kitten Heels | 5 shade spelled in the description only | Dune Kitten Heels | beige | beige kitten heels | generic |
| PLT-DA35600 | Kitten Heels | 6 incidental word in a range name | Red Harbour Kitten Heels, Black | red | red kitten heels | generic |
| PLT-DA35601 | Kitten Heels | 6 incidental word in a range name | Blue Cove Kitten Heels, Black | blue | blue kitten heels | generic |
| PLT-DA35602 | Kitten Heels | 6 incidental word in a range name | White Cliff Kitten Heels, Cream | white | white kitten heels | generic |
| PLT-DA35603 | Kitten Heels | 6 incidental word in a range name | Shirt Row Kitten Heels, Green | shirt | shirt | generic |
| PLT-DA35700 | Kitten Heels | 7 invented brand holding a color or category word | Jumper Jay Kitten Heels, Green | jumper | jumper kitten heels | generic |
| PLT-DA35701 | Kitten Heels | 7 invented brand holding a color or category word | Yellow Wagtail Kitten Heels, Red | yellow | yellow kitten heels | generic |
| PLT-DA35702 | Kitten Heels | 7 invented brand holding a color or category word | Red Plover Kitten Heels, Green | red | red kitten heels | generic |
| PLT-DA36100 | Knee High Boots | 1 color names a part | Pink Knee High Boots, Yellow Lining | yellow | yellow knee high boots | generic |
| PLT-DA36101 | Knee High Boots | 1 color names a part | Pink Knee High Boots, White Eyelets | white | white knee high boots | generic |
| PLT-DA36102 | Knee High Boots | 1 color names a part | Red Knee High Boots, Black Heel | black | black knee high boots | generic |
| PLT-DA36200 | Knee High Boots | 2 another category's noun as a modifier | Black Trainer Knee High Boots | trainer | trainer | generic |
| PLT-DA36201 | Knee High Boots | 2 another category's noun as a modifier | Red Trainer Knee High Boots | trainer | trainer | generic |
| PLT-DA36202 | Knee High Boots | 2 another category's noun as a modifier | White Loafer Knee High Boots | loafer | loafer | generic |
| PLT-DA36300 | Knee High Boots | 3 audience word of a sibling version | Blue Womens Knee High Boots, Boys Fit | boys | boys knee high boots | generic |
| PLT-DA36301 | Knee High Boots | 3 audience word of a sibling version | Blue Womens Knee High Boots, Mens Fit | mens | mens knee high boots | generic |
| PLT-DA36302 | Knee High Boots | 3 audience word of a sibling version | White Womens Knee High Boots, Boys Fit | boys | boys knee high boots | generic |
| PLT-DA36400 | Knee High Boots | 4 material or feature named but absent | Pink Suede-Look Knee High Boots, Leather | suede | suede knee high boots | special: material claim |
| PLT-DA36401 | Knee High Boots | 4 material or feature named but absent | Red Cashmere-Feel Knee High Boots, Leather | cashmere | cashmere knee high boots | special: material claim |
| PLT-DA36402 | Knee High Boots | 4 material or feature named but absent | White Wool-Free Knee High Boots, Leather | wool | wool knee high boots | special: material claim |
| PLT-DA36500 | Knee High Boots | 5 shade spelled in the description only | Moonbeam Knee High Boots | ivory | ivory knee high boots | generic |
| PLT-DA36501 | Knee High Boots | 5 shade spelled in the description only | Driftwood Knee High Boots | taupe | taupe knee high boots | generic |
| PLT-DA36502 | Knee High Boots | 5 shade spelled in the description only | Dune Knee High Boots | beige | beige knee high boots | generic |
| PLT-DA36600 | Knee High Boots | 6 incidental word in a range name | White Cliff Knee High Boots, Grey | white | white knee high boots | generic |
| PLT-DA36601 | Knee High Boots | 6 incidental word in a range name | Yellow Marsh Knee High Boots, Cream | yellow | yellow knee high boots | generic |
| PLT-DA36602 | Knee High Boots | 6 incidental word in a range name | Blue Meadow Knee High Boots, Grey | blue | blue knee high boots | generic |
| PLT-DA36603 | Knee High Boots | 6 incidental word in a range name | Dress Circle Knee High Boots, Black | dress | dress | generic |
| PLT-DA36700 | Knee High Boots | 7 invented brand holding a color or category word | White Dormouse Knee High Boots, Green | white | white knee high boots | generic |
| PLT-DA36701 | Knee High Boots | 7 invented brand holding a color or category word | Coat Crake Knee High Boots, Blue | coat | coat knee high boots | generic |
| PLT-DA36702 | Knee High Boots | 7 invented brand holding a color or category word | Red Plover Knee High Boots, Green | red | red knee high boots | generic |
| PLT-DA37100 | Loafers | 1 color names a part | White Loafers, Yellow Lining | yellow | yellow loafers | generic |
| PLT-DA37101 | Loafers | 1 color names a part | Blue Loafers, Green Eyelets | green | green loafers | generic |
| PLT-DA37102 | Loafers | 1 color names a part | Navy Loafers, Black Trim | black | black loafers | generic |
| PLT-DA37200 | Loafers | 2 another category's noun as a modifier | Pink Pump Loafers | pump | pump | generic |
| PLT-DA37201 | Loafers | 2 another category's noun as a modifier | Navy Heel Loafers | heel | heel | generic |
| PLT-DA37202 | Loafers | 2 another category's noun as a modifier | Green Heel Loafers | heel | heel | generic |
| PLT-DA37300 | Loafers | 3 audience word of a sibling version | Navy Mens Loafers, Womens Fit | womens | womens loafers | generic |
| PLT-DA37301 | Loafers | 3 audience word of a sibling version | Black Womens Loafers, Mens-Style | mens | mens loafers | generic |
| PLT-DA37302 | Loafers | 3 audience word of a sibling version | Pink Womens Loafers, Boys Fit | boys | boys loafers | generic |
| PLT-DA37400 | Loafers | 4 material or feature named but absent | Brown Suede-Look Loafers, Leather | suede | suede loafers | special: material claim |
| PLT-DA37401 | Loafers | 4 material or feature named but absent | Brown Cashmere-Feel Loafers, Leather | cashmere | cashmere loafers | special: material claim |
| PLT-DA37402 | Loafers | 4 material or feature named but absent | Black Wool-Free Loafers, Leather | wool | wool loafers | special: material claim |
| PLT-DA37500 | Loafers | 5 shade spelled in the description only | Moonbeam Loafers | ivory | ivory loafers | generic |
| PLT-DA37501 | Loafers | 5 shade spelled in the description only | Driftwood Loafers | taupe | taupe loafers | generic |
| PLT-DA37502 | Loafers | 5 shade spelled in the description only | Dune Loafers | beige | beige loafers | generic |
| PLT-DA37600 | Loafers | 6 incidental word in a range name | Blue Meadow Loafers, Pink | blue | blue loafers | generic |
| PLT-DA37601 | Loafers | 6 incidental word in a range name | Blue Meadow Loafers, Navy | blue | blue loafers | generic |
| PLT-DA37602 | Loafers | 6 incidental word in a range name | White Moor Loafers, Black | white | white loafers | generic |
| PLT-DA37603 | Loafers | 6 incidental word in a range name | Coat Hook Loafers, Navy | coat | coat | generic |
| PLT-DA37700 | Loafers | 7 invented brand holding a color or category word | Black Lapwing Loafers, Navy | black | black loafers | generic |
| PLT-DA37701 | Loafers | 7 invented brand holding a color or category word | Yellow Wagtail Loafers, Brown | yellow | yellow loafers | generic |
| PLT-DA37702 | Loafers | 7 invented brand holding a color or category word | Jumper Jay Loafers, Grey | jumper | jumper loafers | generic |
| PLT-DA38100 | Running Shoes | 1 color names a part | Brown Running Shoes, Red Sole | red | red running shoes | generic |
| PLT-DA38101 | Running Shoes | 1 color names a part | Blue Running Shoes, Yellow Heel | yellow | yellow running shoes | generic |
| PLT-DA38102 | Running Shoes | 1 color names a part | Red Running Shoes, Black Heel | black | black running shoes | generic |
| PLT-DA38200 | Running Shoes | 2 another category's noun as a modifier | Grey Slipper Running Shoes | slipper | slipper | generic |
| PLT-DA38201 | Running Shoes | 2 another category's noun as a modifier | Navy Trainer Running Shoes | trainer | trainer | generic |
| PLT-DA38202 | Running Shoes | 2 another category's noun as a modifier | White Loafer Running Shoes | loafer | loafer | generic |
| PLT-DA38300 | Running Shoes | 3 audience word of a sibling version | Cream Unisex Running Shoes, Mini-Me Mens | mens | mens running shoes | generic |
| PLT-DA38301 | Running Shoes | 3 audience word of a sibling version | Black Mens Running Shoes, Girls Fit | girls | girls running shoes | generic |
| PLT-DA38302 | Running Shoes | 3 audience word of a sibling version | Grey Womens Running Shoes, Mens Fit | mens | mens running shoes | generic |
| PLT-DA38400 | Running Shoes | 4 material or feature named but absent | Red Leather-Look Running Shoes, Mesh | leather | leather running shoes | special: material claim |
| PLT-DA38401 | Running Shoes | 4 material or feature named but absent | Green Suede-Look Running Shoes, Mesh | suede | suede running shoes | special: material claim |
| PLT-DA38402 | Running Shoes | 4 material or feature named but absent | White Cashmere-Feel Running Shoes, Mesh | cashmere | cashmere running shoes | special: material claim |
| PLT-DA38500 | Running Shoes | 5 shade spelled in the description only | Moonbeam Running Shoes | ivory | ivory running shoes | generic |
| PLT-DA38501 | Running Shoes | 5 shade spelled in the description only | Driftwood Running Shoes | taupe | taupe running shoes | generic |
| PLT-DA38502 | Running Shoes | 5 shade spelled in the description only | Dune Running Shoes | beige | beige running shoes | generic |
| PLT-DA38600 | Running Shoes | 6 incidental word in a range name | Green Hollow Running Shoes, Cream | green | green running shoes | generic |
| PLT-DA38601 | Running Shoes | 6 incidental word in a range name | Green Park Running Shoes, Red | green | green running shoes | generic |
| PLT-DA38602 | Running Shoes | 6 incidental word in a range name | Black Mill Running Shoes, Blue | black | black running shoes | generic |
| PLT-DA38603 | Running Shoes | 6 incidental word in a range name | Jumper Lane Running Shoes, Black | jumper | jumper | generic |
| PLT-DA38700 | Running Shoes | 7 invented brand holding a color or category word | Red Plover Running Shoes, Pink | red | red running shoes | generic |
| PLT-DA38701 | Running Shoes | 7 invented brand holding a color or category word | Coat Crake Running Shoes, Green | coat | coat running shoes | generic |
| PLT-DA38702 | Running Shoes | 7 invented brand holding a color or category word | Black Lapwing Running Shoes, Red | black | black running shoes | generic |
| PLT-DA39100 | Safety Boots | 1 color names a part | Red Safety Boots, White Lining | white | white safety boots | generic |
| PLT-DA39101 | Safety Boots | 1 color names a part | White Safety Boots, Red Heel | red | red safety boots | generic |
| PLT-DA39102 | Safety Boots | 1 color names a part | Red Safety Boots, Yellow Heel | yellow | yellow safety boots | generic |
| PLT-DA39200 | Safety Boots | 2 another category's noun as a modifier | Cream Sandal Safety Boots | sandal | sandal | generic |
| PLT-DA39201 | Safety Boots | 2 another category's noun as a modifier | Brown Trainer Safety Boots | trainer | trainer | generic |
| PLT-DA39202 | Safety Boots | 2 another category's noun as a modifier | White Sandal Safety Boots | sandal | sandal | generic |
| PLT-DA39300 | Safety Boots | 3 audience word of a sibling version | Cream Mens Safety Boots, Womens Fit | womens | womens safety boots | generic |
| PLT-DA39301 | Safety Boots | 3 audience word of a sibling version | White Mens Safety Boots, Womens-Style | womens | womens safety boots | generic |
| PLT-DA39302 | Safety Boots | 3 audience word of a sibling version | Blue Mens Safety Boots, Womens-Style | womens | womens safety boots | generic |
| PLT-DA39400 | Safety Boots | 4 material or feature named but absent | Grey Suede-Look Safety Boots, Leather, Nubuck | suede | suede safety boots | special: material claim |
| PLT-DA39401 | Safety Boots | 4 material or feature named but absent | Pink Cashmere-Feel Safety Boots, Leather, Nubuck | cashmere | cashmere safety boots | special: material claim |
| PLT-DA39402 | Safety Boots | 4 material or feature named but absent | Cream Wool-Free Safety Boots, Leather, Nubuck | wool | wool safety boots | special: material claim |
| PLT-DA39500 | Safety Boots | 5 shade spelled in the description only | Moonbeam Safety Boots | ivory | ivory safety boots | generic |
| PLT-DA39501 | Safety Boots | 5 shade spelled in the description only | Driftwood Safety Boots | taupe | taupe safety boots | generic |
| PLT-DA39502 | Safety Boots | 5 shade spelled in the description only | Dune Safety Boots | beige | beige safety boots | generic |
| PLT-DA39600 | Safety Boots | 6 incidental word in a range name | White Moor Safety Boots, Navy | white | white safety boots | generic |
| PLT-DA39601 | Safety Boots | 6 incidental word in a range name | Black Tor Safety Boots, Brown | black | black safety boots | generic |
| PLT-DA39602 | Safety Boots | 6 incidental word in a range name | Red Fern Safety Boots, Blue | red | red safety boots | generic |
| PLT-DA39603 | Safety Boots | 6 incidental word in a range name | Shirt Row Safety Boots, Blue | shirt | shirt | generic |
| PLT-DA39700 | Safety Boots | 7 invented brand holding a color or category word | Coat Crake Safety Boots, Navy | coat | coat safety boots | generic |
| PLT-DA39701 | Safety Boots | 7 invented brand holding a color or category word | Blue Otter Safety Boots, Grey | blue | blue safety boots | generic |
| PLT-DA39702 | Safety Boots | 7 invented brand holding a color or category word | Yellow Wagtail Safety Boots, Brown | yellow | yellow safety boots | generic |
| PLT-DA40100 | Sandals | 1 color names a part | Grey Sandals, White Heel | white | white sandals | generic |
| PLT-DA40101 | Sandals | 1 color names a part | Cream Sandals, Yellow Eyelets | yellow | yellow sandals | generic |
| PLT-DA40102 | Sandals | 1 color names a part | Red Sandals, Black Sole | black | black sandals | generic |
| PLT-DA40200 | Sandals | 2 another category's noun as a modifier | Navy Heel Sandals | heel | heel | generic |
| PLT-DA40201 | Sandals | 2 another category's noun as a modifier | Red Pump Sandals | pump | pump | generic |
| PLT-DA40202 | Sandals | 2 another category's noun as a modifier | Grey Slipper Sandals | slipper | slipper | generic |
| PLT-DA40300 | Sandals | 3 audience word of a sibling version | Green Unisex Sandals, Mini-Me Mens | mens | mens sandals | generic |
| PLT-DA40301 | Sandals | 3 audience word of a sibling version | Red Womens Sandals, Mens-Style | mens | mens sandals | generic |
| PLT-DA40302 | Sandals | 3 audience word of a sibling version | Cream Womens Sandals, Mens-Style | mens | mens sandals | generic |
| PLT-DA40400 | Sandals | 4 material or feature named but absent | Red Leather-Look Sandals, Synthetic | leather | leather sandals | special: material claim |
| PLT-DA40401 | Sandals | 4 material or feature named but absent | Brown Suede-Look Sandals, Synthetic | suede | suede sandals | special: material claim |
| PLT-DA40402 | Sandals | 4 material or feature named but absent | Green Cashmere-Feel Sandals, Leather | cashmere | cashmere sandals | special: material claim |
| PLT-DA40500 | Sandals | 5 shade spelled in the description only | Moonbeam Sandals | ivory | ivory sandals | generic |
| PLT-DA40501 | Sandals | 5 shade spelled in the description only | Driftwood Sandals | taupe | taupe sandals | generic |
| PLT-DA40502 | Sandals | 5 shade spelled in the description only | Dune Sandals | beige | beige sandals | generic |
| PLT-DA40600 | Sandals | 6 incidental word in a range name | White Cliff Sandals, Black | white | white sandals | generic |
| PLT-DA40601 | Sandals | 6 incidental word in a range name | Blue Cove Sandals, Navy | blue | blue sandals | generic |
| PLT-DA40602 | Sandals | 6 incidental word in a range name | White Moor Sandals, Black | white | white sandals | generic |
| PLT-DA40603 | Sandals | 6 incidental word in a range name | Jumper Lane Sandals, Cream | jumper | jumper | generic |
| PLT-DA40700 | Sandals | 7 invented brand holding a color or category word | Yellow Wagtail Sandals, Grey | yellow | yellow sandals | generic |
| PLT-DA40701 | Sandals | 7 invented brand holding a color or category word | White Dormouse Sandals, Navy | white | white sandals | generic |
| PLT-DA40702 | Sandals | 7 invented brand holding a color or category word | White Dormouse Sandals, Red | white | white sandals | generic |
| PLT-DA41100 | School Shoes | 1 color names a part | Blue School Shoes, Green Heel | green | green school shoes | generic |
| PLT-DA41101 | School Shoes | 1 color names a part | Grey School Shoes, Green Eyelets | green | green school shoes | generic |
| PLT-DA41102 | School Shoes | 1 color names a part | Black School Shoes, White Eyelets | white | white school shoes | generic |
| PLT-DA41200 | School Shoes | 2 another category's noun as a modifier | Pink Mule School Shoes | mule | mule | generic |
| PLT-DA41201 | School Shoes | 2 another category's noun as a modifier | White Pump School Shoes | pump | pump | generic |
| PLT-DA41202 | School Shoes | 2 another category's noun as a modifier | Navy Boot School Shoes | boot | boot | generic |
| PLT-DA41300 | School Shoes | 3 audience word of a sibling version | Red Unisex School Shoes, Mens-Style | mens | mens school shoes | generic |
| PLT-DA41301 | School Shoes | 3 audience word of a sibling version | Cream Unisex School Shoes, Mens-Style | mens | mens school shoes | generic |
| PLT-DA41302 | School Shoes | 3 audience word of a sibling version | Pink Unisex School Shoes, Mini-Me Mens | mens | mens school shoes | generic |
| PLT-DA41400 | School Shoes | 4 material or feature named but absent | Pink Suede-Look School Shoes, Leather, Patent | suede | suede school shoes | special: material claim |
| PLT-DA41401 | School Shoes | 4 material or feature named but absent | Black Cashmere-Feel School Shoes, Leather, Patent | cashmere | cashmere school shoes | special: material claim |
| PLT-DA41402 | School Shoes | 4 material or feature named but absent | Pink Wool-Free School Shoes, Leather, Patent | wool | wool school shoes | special: material claim |
| PLT-DA41500 | School Shoes | 5 shade spelled in the description only | Moonbeam School Shoes | ivory | ivory school shoes | generic |
| PLT-DA41501 | School Shoes | 5 shade spelled in the description only | Driftwood School Shoes | taupe | taupe school shoes | generic |
| PLT-DA41502 | School Shoes | 5 shade spelled in the description only | Dune School Shoes | beige | beige school shoes | generic |
| PLT-DA41600 | School Shoes | 6 incidental word in a range name | White Cliff School Shoes, Black | white | white school shoes | generic |
| PLT-DA41601 | School Shoes | 6 incidental word in a range name | Yellow Brook School Shoes, Red | yellow | yellow school shoes | generic |
| PLT-DA41602 | School Shoes | 6 incidental word in a range name | Black Mill School Shoes, Cream | black | black school shoes | generic |
| PLT-DA41603 | School Shoes | 6 incidental word in a range name | Jacket Quay School Shoes, Grey | jacket | jacket | generic |
| PLT-DA41700 | School Shoes | 7 invented brand holding a color or category word | Jumper Jay School Shoes, Grey | jumper | jumper school shoes | generic |
| PLT-DA41701 | School Shoes | 7 invented brand holding a color or category word | Red Plover School Shoes, Navy | red | red school shoes | generic |
| PLT-DA41702 | School Shoes | 7 invented brand holding a color or category word | White Dormouse School Shoes, Green | white | white school shoes | generic |
| PLT-DA42100 | Slippers | 1 color names a part | Navy Slippers, White Eyelets | white | white slippers | generic |
| PLT-DA42101 | Slippers | 1 color names a part | Black Slippers, White Eyelets | white | white slippers | generic |
| PLT-DA42102 | Slippers | 1 color names a part | Red Slippers, Green Stitching | green | green slippers | generic |
| PLT-DA42200 | Slippers | 2 another category's noun as a modifier | Brown Heel Slippers | heel | heel | generic |
| PLT-DA42201 | Slippers | 2 another category's noun as a modifier | Brown Heel Slippers | heel | heel | generic |
| PLT-DA42202 | Slippers | 2 another category's noun as a modifier | White Trainer Slippers | trainer | trainer | generic |
| PLT-DA42300 | Slippers | 3 audience word of a sibling version | Grey Mens Slippers, Womens Fit | womens | womens slippers | generic |
| PLT-DA42301 | Slippers | 3 audience word of a sibling version | Navy Womens Slippers, Mens Fit | mens | mens slippers | generic |
| PLT-DA42302 | Slippers | 3 audience word of a sibling version | Green Womens Slippers, Boys Fit | boys | boys slippers | generic |
| PLT-DA42400 | Slippers | 4 material or feature named but absent | Black Leather-Look Slippers, Suede | leather | leather slippers | special: material claim |
| PLT-DA42401 | Slippers | 4 material or feature named but absent | Pink Cashmere-Feel Slippers, Suede | cashmere | cashmere slippers | special: material claim |
| PLT-DA42402 | Slippers | 4 material or feature named but absent | Pink Wool-Free Slippers, Suede | wool | wool slippers | special: material claim |
| PLT-DA42500 | Slippers | 5 shade spelled in the description only | Moonbeam Slippers | ivory | ivory slippers | generic |
| PLT-DA42501 | Slippers | 5 shade spelled in the description only | Driftwood Slippers | taupe | taupe slippers | generic |
| PLT-DA42502 | Slippers | 5 shade spelled in the description only | Dune Slippers | beige | beige slippers | generic |
| PLT-DA42600 | Slippers | 6 incidental word in a range name | White Moor Slippers, Pink | white | white slippers | generic |
| PLT-DA42601 | Slippers | 6 incidental word in a range name | Black Tor Slippers, Green | black | black slippers | generic |
| PLT-DA42602 | Slippers | 6 incidental word in a range name | White Moor Slippers, Pink | white | white slippers | generic |
| PLT-DA42603 | Slippers | 6 incidental word in a range name | Coat Hook Slippers, Red | coat | coat | generic |
| PLT-DA42700 | Slippers | 7 invented brand holding a color or category word | Blue Otter Slippers, Cream | blue | blue slippers | generic |
| PLT-DA42701 | Slippers | 7 invented brand holding a color or category word | Jumper Jay Slippers, Cream | jumper | jumper slippers | generic |
| PLT-DA42702 | Slippers | 7 invented brand holding a color or category word | Yellow Wagtail Slippers, Pink | yellow | yellow slippers | generic |
| PLT-DA43100 | Trainers | 1 color names a part | Green Trainers, White Lining | white | white trainers | generic |
| PLT-DA43101 | Trainers | 1 color names a part | Navy Trainers, Black Heel | black | black trainers | generic |
| PLT-DA43102 | Trainers | 1 color names a part | Grey Trainers, Yellow Heel | yellow | yellow trainers | generic |
| PLT-DA43200 | Trainers | 2 another category's noun as a modifier | Navy Loafer Trainers | loafer | loafer | generic |
| PLT-DA43201 | Trainers | 2 another category's noun as a modifier | Red Heel Trainers | heel | heel | generic |
| PLT-DA43202 | Trainers | 2 another category's noun as a modifier | Pink Sneaker Trainers | sneaker | sneaker | generic |
| PLT-DA43300 | Trainers | 3 audience word of a sibling version | Green Mens Trainers, Womens Fit | womens | womens trainers | generic |
| PLT-DA43301 | Trainers | 3 audience word of a sibling version | Cream Unisex Trainers, Mens-Style | mens | mens trainers | generic |
| PLT-DA43302 | Trainers | 3 audience word of a sibling version | Brown Mens Trainers, Womens Fit | womens | womens trainers | generic |
| PLT-DA43400 | Trainers | 4 material or feature named but absent | Cream Leather-Look Trainers, Canvas | leather | leather trainers | special: material claim |
| PLT-DA43401 | Trainers | 4 material or feature named but absent | Pink Suede-Look Trainers, Leather | suede | suede trainers | special: material claim |
| PLT-DA43402 | Trainers | 4 material or feature named but absent | Grey Cashmere-Feel Trainers | cashmere | cashmere trainers | special: material claim |
| PLT-DA43500 | Trainers | 5 shade spelled in the description only | Moonbeam Trainers | ivory | ivory trainers | generic |
| PLT-DA43501 | Trainers | 5 shade spelled in the description only | Driftwood Trainers | taupe | taupe trainers | generic |
| PLT-DA43502 | Trainers | 5 shade spelled in the description only | Dune Trainers | beige | beige trainers | generic |
| PLT-DA43600 | Trainers | 6 incidental word in a range name | Yellow Brook Trainers, Black | yellow | yellow trainers | generic |
| PLT-DA43601 | Trainers | 6 incidental word in a range name | Red Harbour Trainers, Navy | red | red trainers | generic |
| PLT-DA43602 | Trainers | 6 incidental word in a range name | Black Tor Trainers, Blue | black | black trainers | generic |
| PLT-DA43603 | Trainers | 6 incidental word in a range name | Boot Hill Trainers, Navy | boot | boot | generic |
| PLT-DA43700 | Trainers | 7 invented brand holding a color or category word | Yellow Wagtail Trainers, Green | yellow | yellow trainers | generic |
| PLT-DA43701 | Trainers | 7 invented brand holding a color or category word | Jumper Jay Trainers, Pink | jumper | jumper trainers | generic |
| PLT-DA43702 | Trainers | 7 invented brand holding a color or category word | Yellow Wagtail Trainers, Green | yellow | yellow trainers | generic |
| PLT-DA44100 | Walking Boots | 1 color names a part | White Walking Boots, Blue Eyelets | blue | blue walking boots | generic |
| PLT-DA44101 | Walking Boots | 1 color names a part | Navy Walking Boots, White Heel | white | white walking boots | generic |
| PLT-DA44102 | Walking Boots | 1 color names a part | Grey Walking Boots, Yellow Eyelets | yellow | yellow walking boots | generic |
| PLT-DA44200 | Walking Boots | 2 another category's noun as a modifier | Brown Sock Walking Boots | sock | sock | generic |
| PLT-DA44201 | Walking Boots | 2 another category's noun as a modifier | Pink Slipper Walking Boots | slipper | slipper | generic |
| PLT-DA44202 | Walking Boots | 2 another category's noun as a modifier | Black Sock Walking Boots | sock | sock | generic |
| PLT-DA44300 | Walking Boots | 3 audience word of a sibling version | Pink Unisex Walking Boots, Mens-Style | mens | mens walking boots | generic |
| PLT-DA44301 | Walking Boots | 3 audience word of a sibling version | Black Mens Walking Boots, Girls Fit | girls | girls walking boots | generic |
| PLT-DA44302 | Walking Boots | 3 audience word of a sibling version | Grey Womens Walking Boots, Mens-Style | mens | mens walking boots | generic |
| PLT-DA44400 | Walking Boots | 4 material or feature named but absent | Green Leather-Look Walking Boots, Nubuck | leather | leather walking boots | special: material claim |
| PLT-DA44401 | Walking Boots | 4 material or feature named but absent | White Suede-Look Walking Boots, Nubuck | suede | suede walking boots | special: material claim |
| PLT-DA44402 | Walking Boots | 4 material or feature named but absent | Cream Cashmere-Feel Walking Boots, Nubuck | cashmere | cashmere walking boots | special: material claim |
| PLT-DA44500 | Walking Boots | 5 shade spelled in the description only | Moonbeam Walking Boots | ivory | ivory walking boots | generic |
| PLT-DA44501 | Walking Boots | 5 shade spelled in the description only | Driftwood Walking Boots | taupe | taupe walking boots | generic |
| PLT-DA44502 | Walking Boots | 5 shade spelled in the description only | Dune Walking Boots | beige | beige walking boots | generic |
| PLT-DA44600 | Walking Boots | 6 incidental word in a range name | Green Park Walking Boots, Navy | green | green walking boots | generic |
| PLT-DA44601 | Walking Boots | 6 incidental word in a range name | Red Fern Walking Boots, Navy | red | red walking boots | generic |
| PLT-DA44602 | Walking Boots | 6 incidental word in a range name | Yellow Brook Walking Boots, Green | yellow | yellow walking boots | generic |
| PLT-DA44603 | Walking Boots | 6 incidental word in a range name | Sock Hop Walking Boots, Brown | sock | sock | generic |
| PLT-DA44700 | Walking Boots | 7 invented brand holding a color or category word | Black Lapwing Walking Boots, White | black | black walking boots | generic |
| PLT-DA44701 | Walking Boots | 7 invented brand holding a color or category word | Jumper Jay Walking Boots, Black | jumper | jumper walking boots | generic |
| PLT-DA44702 | Walking Boots | 7 invented brand holding a color or category word | Jumper Jay Walking Boots, Brown | jumper | jumper walking boots | generic |
| PLT-DA45100 | Wellies | 1 color names a part | Pink Wellies, Green Sole | green | green wellies | generic |
| PLT-DA45101 | Wellies | 1 color names a part | Cream Wellies, Black Sole | black | black wellies | generic |
| PLT-DA45102 | Wellies | 1 color names a part | Cream Wellies, Yellow Heel | yellow | yellow wellies | generic |
| PLT-DA45200 | Wellies | 2 another category's noun as a modifier | Black Heel Wellies | heel | heel | generic |
| PLT-DA45201 | Wellies | 2 another category's noun as a modifier | Cream Loafer Wellies | loafer | loafer | generic |
| PLT-DA45202 | Wellies | 2 another category's noun as a modifier | White Sandal Wellies | sandal | sandal | generic |
| PLT-DA45300 | Wellies | 3 audience word of a sibling version | Red Womens Wellies, Mens Fit | mens | mens wellies | generic |
| PLT-DA45301 | Wellies | 3 audience word of a sibling version | Green Womens Wellies, Boys Fit | boys | boys wellies | generic |
| PLT-DA45302 | Wellies | 3 audience word of a sibling version | Black Unisex Wellies, Mini-Me Womens | womens | womens wellies | generic |
| PLT-DA45400 | Wellies | 4 material or feature named but absent | Red Leather-Look Wellies, Rubber | leather | leather wellies | special: material claim |
| PLT-DA45401 | Wellies | 4 material or feature named but absent | Green Suede-Look Wellies, Rubber | suede | suede wellies | special: material claim |
| PLT-DA45402 | Wellies | 4 material or feature named but absent | Navy Cashmere-Feel Wellies, Rubber | cashmere | cashmere wellies | special: material claim |
| PLT-DA45500 | Wellies | 5 shade spelled in the description only | Moonbeam Wellies | ivory | ivory wellies | generic |
| PLT-DA45501 | Wellies | 5 shade spelled in the description only | Driftwood Wellies | taupe | taupe wellies | generic |
| PLT-DA45502 | Wellies | 5 shade spelled in the description only | Dune Wellies | beige | beige wellies | generic |
| PLT-DA45600 | Wellies | 6 incidental word in a range name | Blue Cove Wellies, Black | blue | blue wellies | generic |
| PLT-DA45601 | Wellies | 6 incidental word in a range name | White Moor Wellies, Navy | white | white wellies | generic |
| PLT-DA45602 | Wellies | 6 incidental word in a range name | Red Harbour Wellies, Blue | red | red wellies | generic |
| PLT-DA45603 | Wellies | 6 incidental word in a range name | Coat Hook Wellies, Pink | coat | coat | generic |
| PLT-DA45700 | Wellies | 7 invented brand holding a color or category word | Yellow Wagtail Wellies, Navy | yellow | yellow wellies | generic |
| PLT-DA45701 | Wellies | 7 invented brand holding a color or category word | Black Lapwing Wellies, Cream | black | black wellies | generic |
| PLT-DA45702 | Wellies | 7 invented brand holding a color or category word | Jumper Jay Wellies, Navy | jumper | jumper wellies | generic |
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
| PLT-DA46300 | Bra | 3 audience word of a sibling version | Navy Womens Bra, Boys Fit | boys | boys bra | generic |
| PLT-DA46301 | Bra | 3 audience word of a sibling version | Pink Womens Bra, Mens Fit | mens | mens bra | generic |
| PLT-DA46302 | Bra | 3 audience word of a sibling version | Green Womens Bra, Mens Fit | mens | mens bra | generic |
| PLT-DA46303 | Bra | 3 audience word of a sibling version | Brown Womens Bra, Mens-Style | mens | mens bra | generic |
| PLT-DA46304 | Bra | 3 audience word of a sibling version | Brown Womens Bra, Boys Fit | boys | boys bra | generic |
| PLT-DA46305 | Bra | 3 audience word of a sibling version | Pink Womens Bra, Boys Fit | boys | boys bra | generic |
| PLT-DA46306 | Bra | 3 audience word of a sibling version | Cream Womens Bra, Mens Fit | mens | mens bra | generic |
| PLT-DA46307 | Bra | 3 audience word of a sibling version | Red Womens Bra, Mens-Style | mens | mens bra | generic |
| PLT-DA46308 | Bra | 3 audience word of a sibling version | Brown Womens Bra, Mens Fit | mens | mens bra | generic |
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
| PLT-DA46600 | Bra | 6 incidental word in a range name | Yellow Marsh Bra, Grey | yellow | yellow bra | generic |
| PLT-DA46601 | Bra | 6 incidental word in a range name | Green Park Bra, Navy | green | green bra | generic |
| PLT-DA46602 | Bra | 6 incidental word in a range name | White Cliff Bra, Cream | white | white bra | generic |
| PLT-DA46603 | Bra | 6 incidental word in a range name | Red Harbour Bra, Brown | red | red bra | generic |
| PLT-DA46604 | Bra | 6 incidental word in a range name | Yellow Brook Bra, Red | yellow | yellow bra | generic |
| PLT-DA46605 | Bra | 6 incidental word in a range name | White Moor Bra, Blue | white | white bra | generic |
| PLT-DA46606 | Bra | 6 incidental word in a range name | Black Tor Bra, Green | black | black bra | generic |
| PLT-DA46607 | Bra | 6 incidental word in a range name | Blue Meadow Bra, Grey | blue | blue bra | generic |
| PLT-DA46608 | Bra | 6 incidental word in a range name | Black Mill Bra, Red | black | black bra | generic |
| PLT-DA46609 | Bra | 6 incidental word in a range name | Shirt Row Bra, Grey | shirt | shirt | generic |
| PLT-DA46700 | Bra | 7 invented brand holding a color or category word | Blue Otter Bra, Brown | blue | blue bra | generic |
| PLT-DA46701 | Bra | 7 invented brand holding a color or category word | White Dormouse Bra, Black | white | white bra | generic |
| PLT-DA46702 | Bra | 7 invented brand holding a color or category word | Coat Crake Bra, Brown | coat | coat bra | generic |
| PLT-DA46703 | Bra | 7 invented brand holding a color or category word | Green Stoat Bra, Brown | green | green bra | generic |
| PLT-DA46704 | Bra | 7 invented brand holding a color or category word | Red Plover Bra, Pink | red | red bra | generic |
| PLT-DA46705 | Bra | 7 invented brand holding a color or category word | Yellow Wagtail Bra, Blue | yellow | yellow bra | generic |
| PLT-DA46706 | Bra | 7 invented brand holding a color or category word | Black Lapwing Bra, Green | black | black bra | generic |
| PLT-DA46707 | Bra | 7 invented brand holding a color or category word | Jumper Jay Bra, Cream | jumper | jumper bra | generic |
| PLT-DA47100 | Boxers | 1 color names a part | Grey Boxers, White Trim | white | white boxers | generic |
| PLT-DA47101 | Boxers | 1 color names a part | Brown Boxers, Black Waistband | black | black boxers | generic |
| PLT-DA47102 | Boxers | 1 color names a part | Pink Boxers, White Waistband | white | white boxers | generic |
| PLT-DA47200 | Boxers | 2 another category's noun as a modifier | White Trouser Boxers | trouser | trouser | generic |
| PLT-DA47201 | Boxers | 2 another category's noun as a modifier | Grey Shirt Boxers | shirt | shirt | generic |
| PLT-DA47202 | Boxers | 2 another category's noun as a modifier | Green Short Boxers | short | short | generic |
| PLT-DA47300 | Boxers | 3 audience word of a sibling version | Grey Mens Boxers, Womens Fit | womens | womens boxers | generic |
| PLT-DA47301 | Boxers | 3 audience word of a sibling version | Grey Mens Boxers, Womens-Style | womens | womens boxers | generic |
| PLT-DA47302 | Boxers | 3 audience word of a sibling version | Red Mens Boxers, Girls Fit | girls | girls boxers | generic |
| PLT-DA47400 | Boxers | 4 material or feature named but absent | Navy Leather-Look Boxers | leather | leather boxers | special: material claim |
| PLT-DA47401 | Boxers | 4 material or feature named but absent | Cream Suede-Look Boxers | suede | suede boxers | special: material claim |
| PLT-DA47402 | Boxers | 4 material or feature named but absent | Cream Cashmere-Feel Boxers | cashmere | cashmere boxers | special: material claim |
| PLT-DA47500 | Boxers | 5 shade spelled in the description only | Moonbeam Boxers | ivory | ivory boxers | generic |
| PLT-DA47501 | Boxers | 5 shade spelled in the description only | Driftwood Boxers | taupe | taupe boxers | generic |
| PLT-DA47502 | Boxers | 5 shade spelled in the description only | Dune Boxers | beige | beige boxers | generic |
| PLT-DA47600 | Boxers | 6 incidental word in a range name | White Cliff Boxers, Green | white | white boxers | generic |
| PLT-DA47601 | Boxers | 6 incidental word in a range name | Red Fern Boxers, Grey | red | red boxers | generic |
| PLT-DA47602 | Boxers | 6 incidental word in a range name | Black Mill Boxers, Brown | black | black boxers | generic |
| PLT-DA47603 | Boxers | 6 incidental word in a range name | Sock Hop Boxers, Pink | sock | sock | generic |
| PLT-DA47700 | Boxers | 7 invented brand holding a color or category word | Coat Crake Boxers, Navy | coat | coat boxers | generic |
| PLT-DA47701 | Boxers | 7 invented brand holding a color or category word | Blue Otter Boxers, Pink | blue | blue boxers | generic |
| PLT-DA47702 | Boxers | 7 invented brand holding a color or category word | Black Lapwing Boxers, Blue | black | black boxers | generic |
| PLT-DA48100 | Dressing Gown | 1 color names a part | Pink Dressing Gown, White Waistband | white | white dressing gown | generic |
| PLT-DA48101 | Dressing Gown | 1 color names a part | Red Dressing Gown, Blue Piping | blue | blue dressing gown | generic |
| PLT-DA48102 | Dressing Gown | 1 color names a part | Brown Dressing Gown, White Cuffs | white | white dressing gown | generic |
| PLT-DA48200 | Dressing Gown | 2 another category's noun as a modifier | Cream Top Dressing Gown | top | top | generic |
| PLT-DA48201 | Dressing Gown | 2 another category's noun as a modifier | White Top Dressing Gown | top | top | generic |
| PLT-DA48202 | Dressing Gown | 2 another category's noun as a modifier | Green Vest Dressing Gown | vest | vest | generic |
| PLT-DA48300 | Dressing Gown | 3 audience word of a sibling version | Cream Womens Dressing Gown, Boys Fit | boys | boys dressing gown | generic |
| PLT-DA48301 | Dressing Gown | 3 audience word of a sibling version | Brown Womens Dressing Gown, Mens Fit | mens | mens dressing gown | generic |
| PLT-DA48302 | Dressing Gown | 3 audience word of a sibling version | Pink Unisex Dressing Gown, Mini-Me Womens | womens | womens dressing gown | generic |
| PLT-DA48400 | Dressing Gown | 4 material or feature named but absent | Cream Leather-Look Dressing Gown | leather | leather dressing gown | special: material claim |
| PLT-DA48401 | Dressing Gown | 4 material or feature named but absent | Pink Suede-Look Dressing Gown | suede | suede dressing gown | special: material claim |
| PLT-DA48402 | Dressing Gown | 4 material or feature named but absent | Grey Cashmere-Feel Dressing Gown | cashmere | cashmere dressing gown | special: material claim |
| PLT-DA48500 | Dressing Gown | 5 shade spelled in the description only | Moonbeam Dressing Gown | ivory | ivory dressing gown | generic |
| PLT-DA48501 | Dressing Gown | 5 shade spelled in the description only | Driftwood Dressing Gown | taupe | taupe dressing gown | generic |
| PLT-DA48502 | Dressing Gown | 5 shade spelled in the description only | Dune Dressing Gown | beige | beige dressing gown | generic |
| PLT-DA48600 | Dressing Gown | 6 incidental word in a range name | Yellow Marsh Dressing Gown, Green | yellow | yellow dressing gown | generic |
| PLT-DA48601 | Dressing Gown | 6 incidental word in a range name | Red Harbour Dressing Gown, Pink | red | red dressing gown | generic |
| PLT-DA48602 | Dressing Gown | 6 incidental word in a range name | White Cliff Dressing Gown, Grey | white | white dressing gown | generic |
| PLT-DA48603 | Dressing Gown | 6 incidental word in a range name | Jumper Lane Dressing Gown, Black | jumper | jumper | generic |
| PLT-DA48700 | Dressing Gown | 7 invented brand holding a color or category word | Black Lapwing Dressing Gown, Pink | black | black dressing gown | generic |
| PLT-DA48701 | Dressing Gown | 7 invented brand holding a color or category word | Green Stoat Dressing Gown, White | green | green dressing gown | generic |
| PLT-DA48702 | Dressing Gown | 7 invented brand holding a color or category word | Coat Crake Dressing Gown, Green | coat | coat dressing gown | generic |
| PLT-DA49100 | Knickers | 1 color names a part | White Knickers, Yellow Piping | yellow | yellow knickers | generic |
| PLT-DA49101 | Knickers | 1 color names a part | Grey Knickers, Yellow Piping | yellow | yellow knickers | generic |
| PLT-DA49102 | Knickers | 1 color names a part | Grey Knickers, Red Trim | red | red knickers | generic |
| PLT-DA49200 | Knickers | 2 another category's noun as a modifier | Brown Top Knickers | top | top | generic |
| PLT-DA49201 | Knickers | 2 another category's noun as a modifier | Blue Bra Knickers | bra | bra | generic |
| PLT-DA49202 | Knickers | 2 another category's noun as a modifier | Blue Trouser Knickers | trouser | trouser | generic |
| PLT-DA49300 | Knickers | 3 audience word of a sibling version | White Womens Knickers, Mens-Style | mens | mens knickers | generic |
| PLT-DA49301 | Knickers | 3 audience word of a sibling version | Pink Womens Knickers, Boys Fit | boys | boys knickers | generic |
| PLT-DA49302 | Knickers | 3 audience word of a sibling version | Cream Womens Knickers, Mens Fit | mens | mens knickers | generic |
| PLT-DA49400 | Knickers | 4 material or feature named but absent | Green Leather-Look Knickers | leather | leather knickers | special: material claim |
| PLT-DA49401 | Knickers | 4 material or feature named but absent | Navy Suede-Look Knickers | suede | suede knickers | special: material claim |
| PLT-DA49402 | Knickers | 4 material or feature named but absent | White Cashmere-Feel Knickers | cashmere | cashmere knickers | special: material claim |
| PLT-DA49500 | Knickers | 5 shade spelled in the description only | Moonbeam Knickers | ivory | ivory knickers | generic |
| PLT-DA49501 | Knickers | 5 shade spelled in the description only | Driftwood Knickers | taupe | taupe knickers | generic |
| PLT-DA49502 | Knickers | 5 shade spelled in the description only | Dune Knickers | beige | beige knickers | generic |
| PLT-DA49600 | Knickers | 6 incidental word in a range name | Blue Meadow Knickers, Cream | blue | blue knickers | generic |
| PLT-DA49601 | Knickers | 6 incidental word in a range name | Yellow Brook Knickers, Red | yellow | yellow knickers | generic |
| PLT-DA49602 | Knickers | 6 incidental word in a range name | Green Park Knickers, Cream | green | green knickers | generic |
| PLT-DA49603 | Knickers | 6 incidental word in a range name | Shirt Row Knickers, Grey | shirt | shirt | generic |
| PLT-DA49700 | Knickers | 7 invented brand holding a color or category word | Yellow Wagtail Knickers, White | yellow | yellow knickers | generic |
| PLT-DA49701 | Knickers | 7 invented brand holding a color or category word | Red Plover Knickers, Green | red | red knickers | generic |
| PLT-DA49702 | Knickers | 7 invented brand holding a color or category word | Blue Otter Knickers, White | blue | blue knickers | generic |
| PLT-DA50100 | Pyjama Shorts | 1 color names a part | Pink Pyjama Shorts, White Piping | white | white pyjama shorts | generic |
| PLT-DA50101 | Pyjama Shorts | 1 color names a part | Brown Pyjama Shorts, Green Waistband | green | green pyjama shorts | generic |
| PLT-DA50102 | Pyjama Shorts | 1 color names a part | Navy Pyjama Shorts, White Cuffs | white | white pyjama shorts | generic |
| PLT-DA50200 | Pyjama Shorts | 2 another category's noun as a modifier | Black Vest Pyjama Shorts | vest | vest | generic |
| PLT-DA50201 | Pyjama Shorts | 2 another category's noun as a modifier | Pink Shirt Pyjama Shorts | shirt | shirt | generic |
| PLT-DA50202 | Pyjama Shorts | 2 another category's noun as a modifier | Black Top Pyjama Shorts | top | top | generic |
| PLT-DA50300 | Pyjama Shorts | 3 audience word of a sibling version | Cream Womens Pyjama Shorts, Mens-Style | mens | mens pyjama shorts | generic |
| PLT-DA50301 | Pyjama Shorts | 3 audience word of a sibling version | Grey Womens Pyjama Shorts, Boys Fit | boys | boys pyjama shorts | generic |
| PLT-DA50302 | Pyjama Shorts | 3 audience word of a sibling version | Red Womens Pyjama Shorts, Boys Fit | boys | boys pyjama shorts | generic |
| PLT-DA50400 | Pyjama Shorts | 4 material or feature named but absent | Navy Leather-Look Pyjama Shorts | leather | leather pyjama shorts | special: material claim |
| PLT-DA50401 | Pyjama Shorts | 4 material or feature named but absent | Pink Suede-Look Pyjama Shorts | suede | suede pyjama shorts | special: material claim |
| PLT-DA50402 | Pyjama Shorts | 4 material or feature named but absent | Blue Cashmere-Feel Pyjama Shorts | cashmere | cashmere pyjama shorts | special: material claim |
| PLT-DA50500 | Pyjama Shorts | 5 shade spelled in the description only | Moonbeam Pyjama Shorts | ivory | ivory pyjama shorts | generic |
| PLT-DA50501 | Pyjama Shorts | 5 shade spelled in the description only | Driftwood Pyjama Shorts | taupe | taupe pyjama shorts | generic |
| PLT-DA50502 | Pyjama Shorts | 5 shade spelled in the description only | Dune Pyjama Shorts | beige | beige pyjama shorts | generic |
| PLT-DA50600 | Pyjama Shorts | 6 incidental word in a range name | White Moor Pyjama Shorts, Brown | white | white pyjama shorts | generic |
| PLT-DA50601 | Pyjama Shorts | 6 incidental word in a range name | Black Mill Pyjama Shorts, Navy | black | black pyjama shorts | generic |
| PLT-DA50602 | Pyjama Shorts | 6 incidental word in a range name | Green Hollow Pyjama Shorts, Red | green | green pyjama shorts | generic |
| PLT-DA50603 | Pyjama Shorts | 6 incidental word in a range name | Dress Circle Pyjama Shorts, Blue | dress | dress | generic |
| PLT-DA50700 | Pyjama Shorts | 7 invented brand holding a color or category word | Green Stoat Pyjama Shorts, Black | green | green pyjama shorts | generic |
| PLT-DA50701 | Pyjama Shorts | 7 invented brand holding a color or category word | Jumper Jay Pyjama Shorts, Red | jumper | jumper pyjama shorts | generic |
| PLT-DA50702 | Pyjama Shorts | 7 invented brand holding a color or category word | White Dormouse Pyjama Shorts, Green | white | white pyjama shorts | generic |
| PLT-DA51100 | Pyjamas | 1 color names a part | Pink Pyjamas, White Cuffs | white | white pyjamas | generic |
| PLT-DA51101 | Pyjamas | 1 color names a part | White Pyjamas, Blue Trim | blue | blue pyjamas | generic |
| PLT-DA51102 | Pyjamas | 1 color names a part | Black Pyjamas, Red Piping | red | red pyjamas | generic |
| PLT-DA51200 | Pyjamas | 2 another category's noun as a modifier | Red Dress Pyjamas | dress | dress | generic |
| PLT-DA51201 | Pyjamas | 2 another category's noun as a modifier | Pink Skirt Pyjamas | skirt | skirt | generic |
| PLT-DA51202 | Pyjamas | 2 another category's noun as a modifier | Brown Skirt Pyjamas | skirt | skirt | generic |
| PLT-DA51300 | Pyjamas | 3 audience word of a sibling version | Green Unisex Pyjamas, Mini-Me Mens | mens | mens pyjamas | generic |
| PLT-DA51301 | Pyjamas | 3 audience word of a sibling version | Red Unisex Pyjamas, Mini-Me Mens | mens | mens pyjamas | generic |
| PLT-DA51302 | Pyjamas | 3 audience word of a sibling version | White Unisex Pyjamas, Mini-Me Womens | womens | womens pyjamas | generic |
| PLT-DA51400 | Pyjamas | 4 material or feature named but absent | Black Leather-Look Pyjamas, Cotton | leather | leather pyjamas | special: material claim |
| PLT-DA51401 | Pyjamas | 4 material or feature named but absent | Grey Suede-Look Pyjamas, Cotton | suede | suede pyjamas | special: material claim |
| PLT-DA51402 | Pyjamas | 4 material or feature named but absent | Red Cashmere-Feel Pyjamas, Cotton | cashmere | cashmere pyjamas | special: material claim |
| PLT-DA51500 | Pyjamas | 5 shade spelled in the description only | Moonbeam Pyjamas | ivory | ivory pyjamas | generic |
| PLT-DA51501 | Pyjamas | 5 shade spelled in the description only | Driftwood Pyjamas | taupe | taupe pyjamas | generic |
| PLT-DA51502 | Pyjamas | 5 shade spelled in the description only | Dune Pyjamas | beige | beige pyjamas | generic |
| PLT-DA51600 | Pyjamas | 6 incidental word in a range name | Yellow Brook Pyjamas, Red | yellow | yellow pyjamas | generic |
| PLT-DA51601 | Pyjamas | 6 incidental word in a range name | Yellow Marsh Pyjamas, White | yellow | yellow pyjamas | generic |
| PLT-DA51602 | Pyjamas | 6 incidental word in a range name | Green Park Pyjamas, Red | green | green pyjamas | generic |
| PLT-DA51603 | Pyjamas | 6 incidental word in a range name | Dress Circle Pyjamas, Brown | dress | dress | generic |
| PLT-DA51700 | Pyjamas | 7 invented brand holding a color or category word | Coat Crake Pyjamas, Grey | coat | coat pyjamas | generic |
| PLT-DA51701 | Pyjamas | 7 invented brand holding a color or category word | Red Plover Pyjamas, Black | red | red pyjamas | generic |
| PLT-DA51702 | Pyjamas | 7 invented brand holding a color or category word | Green Stoat Pyjamas, Blue | green | green pyjamas | generic |
| PLT-DA52100 | Shapewear | 1 color names a part | Cream Shapewear, Green Cuffs | green | green shapewear | generic |
| PLT-DA52101 | Shapewear | 1 color names a part | Green Shapewear, Blue Piping | blue | blue shapewear | generic |
| PLT-DA52102 | Shapewear | 1 color names a part | Pink Shapewear, Green Bow | green | green shapewear | generic |
| PLT-DA52200 | Shapewear | 2 another category's noun as a modifier | Grey Short Shapewear | short | short | generic |
| PLT-DA52201 | Shapewear | 2 another category's noun as a modifier | Navy Cami Shapewear | cami | cami | generic |
| PLT-DA52202 | Shapewear | 2 another category's noun as a modifier | Brown Top Shapewear | top | top | generic |
| PLT-DA52300 | Shapewear | 3 audience word of a sibling version | Brown Womens Shapewear, Mens-Style | mens | mens shapewear | generic |
| PLT-DA52301 | Shapewear | 3 audience word of a sibling version | Navy Womens Shapewear, Mens Fit | mens | mens shapewear | generic |
| PLT-DA52302 | Shapewear | 3 audience word of a sibling version | Pink Womens Shapewear, Mens Fit | mens | mens shapewear | generic |
| PLT-DA52400 | Shapewear | 4 material or feature named but absent | Green Leather-Look Shapewear | leather | leather shapewear | special: material claim |
| PLT-DA52401 | Shapewear | 4 material or feature named but absent | White Suede-Look Shapewear | suede | suede shapewear | special: material claim |
| PLT-DA52402 | Shapewear | 4 material or feature named but absent | Grey Cashmere-Feel Shapewear | cashmere | cashmere shapewear | special: material claim |
| PLT-DA52500 | Shapewear | 5 shade spelled in the description only | Moonbeam Shapewear | ivory | ivory shapewear | generic |
| PLT-DA52501 | Shapewear | 5 shade spelled in the description only | Driftwood Shapewear | taupe | taupe shapewear | generic |
| PLT-DA52502 | Shapewear | 5 shade spelled in the description only | Dune Shapewear | beige | beige shapewear | generic |
| PLT-DA52600 | Shapewear | 6 incidental word in a range name | Black Tor Shapewear, Green | black | black shapewear | generic |
| PLT-DA52601 | Shapewear | 6 incidental word in a range name | White Moor Shapewear, Black | white | white shapewear | generic |
| PLT-DA52602 | Shapewear | 6 incidental word in a range name | Blue Meadow Shapewear, White | blue | blue shapewear | generic |
| PLT-DA52603 | Shapewear | 6 incidental word in a range name | Sock Hop Shapewear, Blue | sock | sock | generic |
| PLT-DA52700 | Shapewear | 7 invented brand holding a color or category word | Red Plover Shapewear, Green | red | red shapewear | generic |
| PLT-DA52701 | Shapewear | 7 invented brand holding a color or category word | Coat Crake Shapewear, Red | coat | coat shapewear | generic |
| PLT-DA52702 | Shapewear | 7 invented brand holding a color or category word | Black Lapwing Shapewear, Blue | black | black shapewear | generic |
| PLT-DA53100 | Slip | 1 color names a part | Grey Slip, Red Waistband | red | red slip | generic |
| PLT-DA53101 | Slip | 1 color names a part | Blue Slip, Yellow Trim | yellow | yellow slip | generic |
| PLT-DA53102 | Slip | 1 color names a part | White Slip, Black Piping | black | black slip | generic |
| PLT-DA53200 | Slip | 2 another category's noun as a modifier | Black Bra Slip | bra | bra | generic |
| PLT-DA53201 | Slip | 2 another category's noun as a modifier | Green Trouser Slip | trouser | trouser | generic |
| PLT-DA53202 | Slip | 2 another category's noun as a modifier | Blue Shirt Slip | shirt | shirt | generic |
| PLT-DA53300 | Slip | 3 audience word of a sibling version | Brown Womens Slip, Mens Fit | mens | mens slip | generic |
| PLT-DA53301 | Slip | 3 audience word of a sibling version | White Womens Slip, Boys Fit | boys | boys slip | generic |
| PLT-DA53302 | Slip | 3 audience word of a sibling version | Blue Womens Slip, Mens-Style | mens | mens slip | generic |
| PLT-DA53400 | Slip | 4 material or feature named but absent | Grey Leather-Look Slip | leather | leather slip | special: material claim |
| PLT-DA53401 | Slip | 4 material or feature named but absent | Red Suede-Look Slip | suede | suede slip | special: material claim |
| PLT-DA53402 | Slip | 4 material or feature named but absent | Red Cashmere-Feel Slip | cashmere | cashmere slip | special: material claim |
| PLT-DA53500 | Slip | 5 shade spelled in the description only | Moonbeam Slip | ivory | ivory slip | generic |
| PLT-DA53501 | Slip | 5 shade spelled in the description only | Driftwood Slip | taupe | taupe slip | generic |
| PLT-DA53502 | Slip | 5 shade spelled in the description only | Dune Slip | beige | beige slip | generic |
| PLT-DA53600 | Slip | 6 incidental word in a range name | White Moor Slip, Brown | white | white slip | generic |
| PLT-DA53601 | Slip | 6 incidental word in a range name | Red Fern Slip, Green | red | red slip | generic |
| PLT-DA53602 | Slip | 6 incidental word in a range name | Black Mill Slip, Blue | black | black slip | generic |
| PLT-DA53603 | Slip | 6 incidental word in a range name | Coat Hook Slip, Navy | coat | coat | generic |
| PLT-DA53700 | Slip | 7 invented brand holding a color or category word | Jumper Jay Slip, Grey | jumper | jumper slip | generic |
| PLT-DA53701 | Slip | 7 invented brand holding a color or category word | Blue Otter Slip, Cream | blue | blue slip | generic |
| PLT-DA53702 | Slip | 7 invented brand holding a color or category word | Green Stoat Slip, Grey | green | green slip | generic |
| PLT-DA54100 | Tights | 1 color names a part | Cream Tights, Yellow Cuffs | yellow | yellow tights | generic |
| PLT-DA54101 | Tights | 1 color names a part | Blue Tights, Green Piping | green | green tights | generic |
| PLT-DA54102 | Tights | 1 color names a part | Navy Tights, Blue Stitching | blue | blue tights | generic |
| PLT-DA54200 | Tights | 2 another category's noun as a modifier | Green Skirt Tights | skirt | skirt | generic |
| PLT-DA54201 | Tights | 2 another category's noun as a modifier | Grey Short Tights | short | short | generic |
| PLT-DA54202 | Tights | 2 another category's noun as a modifier | Blue Dress Tights | dress | dress | generic |
| PLT-DA54300 | Tights | 3 audience word of a sibling version | Pink Womens Tights, Boys Fit | boys | boys tights | generic |
| PLT-DA54301 | Tights | 3 audience word of a sibling version | Green Womens Tights, Mens-Style | mens | mens tights | generic |
| PLT-DA54302 | Tights | 3 audience word of a sibling version | Blue Womens Tights, Mens Fit | mens | mens tights | generic |
| PLT-DA54400 | Tights | 4 material or feature named but absent | Navy Leather-Look Tights | leather | leather tights | special: material claim |
| PLT-DA54401 | Tights | 4 material or feature named but absent | Blue Suede-Look Tights | suede | suede tights | special: material claim |
| PLT-DA54402 | Tights | 4 material or feature named but absent | Brown Cashmere-Feel Tights | cashmere | cashmere tights | special: material claim |
| PLT-DA54500 | Tights | 5 shade spelled in the description only | Moonbeam Tights | ivory | ivory tights | generic |
| PLT-DA54501 | Tights | 5 shade spelled in the description only | Driftwood Tights | taupe | taupe tights | generic |
| PLT-DA54502 | Tights | 5 shade spelled in the description only | Dune Tights | beige | beige tights | generic |
| PLT-DA54600 | Tights | 6 incidental word in a range name | Yellow Marsh Tights, Black | yellow | yellow tights | generic |
| PLT-DA54601 | Tights | 6 incidental word in a range name | White Moor Tights, Black | white | white tights | generic |
| PLT-DA54602 | Tights | 6 incidental word in a range name | Yellow Brook Tights, Cream | yellow | yellow tights | generic |
| PLT-DA54603 | Tights | 6 incidental word in a range name | Jumper Lane Tights, Green | jumper | jumper | generic |
| PLT-DA54700 | Tights | 7 invented brand holding a color or category word | Jumper Jay Tights, Pink | jumper | jumper tights | generic |
| PLT-DA54701 | Tights | 7 invented brand holding a color or category word | Red Plover Tights, White | red | red tights | generic |
| PLT-DA54702 | Tights | 7 invented brand holding a color or category word | Coat Crake Tights, Grey | coat | coat tights | generic |
| PLT-DA55100 | Vest | 1 color names a part | Brown Vest, Blue Waistband | blue | blue vest | generic |
| PLT-DA55101 | Vest | 1 color names a part | Pink Vest, Green Cuffs | green | green vest | generic |
| PLT-DA55102 | Vest | 1 color names a part | Brown Vest, Green Cuffs | green | green vest | generic |
| PLT-DA55200 | Vest | 2 another category's noun as a modifier | Grey Cami Vest | cami | cami | generic |
| PLT-DA55201 | Vest | 2 another category's noun as a modifier | Green Trouser Vest | trouser | trouser | generic |
| PLT-DA55202 | Vest | 2 another category's noun as a modifier | Black Skirt Vest | skirt | skirt | generic |
| PLT-DA55300 | Vest | 3 audience word of a sibling version | White Mens Vest, Womens Fit | womens | womens vest | generic |
| PLT-DA55301 | Vest | 3 audience word of a sibling version | Grey Womens Vest, Mens Fit | mens | mens vest | generic |
| PLT-DA55302 | Vest | 3 audience word of a sibling version | Brown Womens Vest, Boys Fit | boys | boys vest | generic |
| PLT-DA55400 | Vest | 4 material or feature named but absent | Red Leather-Look Vest | leather | leather vest | special: material claim |
| PLT-DA55401 | Vest | 4 material or feature named but absent | Brown Suede-Look Vest | suede | suede vest | special: material claim |
| PLT-DA55402 | Vest | 4 material or feature named but absent | Red Cashmere-Feel Vest | cashmere | cashmere vest | special: material claim |
| PLT-DA55500 | Vest | 5 shade spelled in the description only | Moonbeam Vest | ivory | ivory vest | generic |
| PLT-DA55501 | Vest | 5 shade spelled in the description only | Driftwood Vest | taupe | taupe vest | generic |
| PLT-DA55502 | Vest | 5 shade spelled in the description only | Dune Vest | beige | beige vest | generic |
| PLT-DA55600 | Vest | 6 incidental word in a range name | Black Tor Vest, Brown | black | black vest | generic |
| PLT-DA55601 | Vest | 6 incidental word in a range name | Red Harbour Vest, Green | red | red vest | generic |
| PLT-DA55602 | Vest | 6 incidental word in a range name | Black Mill Vest, Grey | black | black vest | generic |
| PLT-DA55603 | Vest | 6 incidental word in a range name | Sock Hop Vest, Green | sock | sock | generic |
| PLT-DA55700 | Vest | 7 invented brand holding a color or category word | Coat Crake Vest, Grey | coat | coat vest | generic |
| PLT-DA55701 | Vest | 7 invented brand holding a color or category word | Yellow Wagtail Vest, Cream | yellow | yellow vest | generic |
| PLT-DA55702 | Vest | 7 invented brand holding a color or category word | Red Plover Vest, Brown | red | red vest | generic |

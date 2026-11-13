# The catalogue's 500K mix, by department (gen#837)

The maintainer set the target on 2026-11-11: about 500K SKUs across the combined catalogue, grown
mostly in the everyday departments that general retailers carry. He wanted no more industrial
products except home hardware and DIY ("most people relate to retail more than industrial").
This page is the survey that gen#837 asks for first (its Done-when 1). It holds today's count
per department, the categories the retailers carry that the catalogue lacks or has only thinly,
and a target per department. Each family issue (gen#837 Done-when 2) grows one row, and the
row's `Family issue` column names it. The sized release build (Done-when 3 to 5, which waits on
gen#949 and gen#952) is measured against the `Target` column. `tests/test_catalogue_mix_837.py` checks the table: it sums to about 500K and
every department it names is on `core/departments.py`'s list or marked `new`, and every row that
grows names its own family issue.

## Today

Measured on 2026-11-12 with a `terms` aggregation on `department` over the served index
`catalog_combined_2026-11-11-2028`: 394,766 SKUs. Retail holds 262,770 and industrial 131,996.
Apparel makes up 211,902 of them (Womens 163,904 and Mens 47,998), and lingerie and bras alone
make up 152,848. Six everyday departments hold under 3K each.

## What the retailers carry

These are the top-level departments on the public sites, read on 2026-11-12. Target's came from
its "shop all categories" page. Walmart's, Amazon's and El Corte Inglés's came from their menus,
because their sites refuse an automated fetch.

- **Target:** Clothing, Shoes & Accessories; Home, Garden & Tools; Baby & Kids; Electronics &
  Video Games; School, Office & Art Supplies; Toys & Gifts; Sports & Outdoors; Books, Music &
  Movies; Beauty & Personal Care; Health, Wellness & Pharmacy; Household Essentials; Pets;
  Grocery; Celebrations & Holidays.
- **Walmart:** Grocery; Electronics; Beauty; Pets; Sports & Outdoors; Household Essentials; Patio
  & Garden; Home Improvement; Auto & Tires; Baby; Home; Fashion; Toys; Health & Wellness.
- **Amazon (US):** among them Appliances; Arts, Crafts & Sewing; Automotive Parts & Accessories;
  Baby; Beauty & Personal Care; Cell Phones & Accessories; Clothing, Shoes & Jewelry; Computers;
  Electronics; Garden & Outdoor; Grocery & Gourmet Food; Health, Household & Baby Care; Home &
  Kitchen; Luggage & Travel Gear; Office Products; Pet Supplies; Smart Home; Sports & Outdoors;
  Tools & Home Improvement; Toys & Games; Video Games.
- **El Corte Inglés:** among them Moda (women, men, kids); Electrodomésticos (appliances);
  Electrónica; Perfumería y parafarmacia (beauty and over-the-counter health); Libros y papelería
  (books and stationery); Bricolaje y jardín (DIY and garden); Mascotas (pets); Juguetes (toys);
  Deportes (sports); Supermercado (grocery); Bebé (baby).

All four carry pets, baby gear, household essentials, health, and office and school supplies.
The catalogue has no department for pets, health, office and school, or automotive. It carries
baby only as clothing (Kids > Baby, 1,226), and household essentials only as cleaning sprays
and detergents.

## The mix

`Domain` is the generator domain that builds the department. `Status` is `existing` for a
department on `core/departments.py`'s list, and `new` for one that the department's family issue
adds to that list. `Today` is the 2026-11-12 count. `Family issue` is the issue that grows the
row; each one carries `Depends-On: alexander-marquardt/synthetic-ecommerce-data#949`, so none
starts before the build stops crashing at larger sizes. A row that does not grow names `none`.

| Department | Domain | Status | Today | Target | Growth | Family issue | Add first: what the retailers carry and the catalogue lacks or has thinly |
|---|---|---|---:|---:|---:|---|---|
| Electronics | retail | existing | 1,166 | 14,000 | 12,834 | gen#956 | headphones and speakers (23 earbuds today), TVs by size and soundbars, smart home (plugs, bulbs, doorbell cameras), video-game controllers and headsets, printers and ink, wearables, power banks, webcams |
| Beauty | retail | existing | 2,589 | 14,000 | 11,411 | gen#957 | hair care (24 shampoos today), hair dryers and straighteners, oral care, shaving and grooming, deodorant, skincare beyond creams (cleansers, serums), eye make-up (26 today), fragrance (82 today), nails |
| Sports & outdoors | retail | existing | 1,093 | 11,000 | 9,907 | gen#959 | fishing, golf, cardio machines and weights, team-sport balls and gear, racket sports, hiking packs, coolers and bottles, bike lights and locks, winter sports |
| Toys | retail | existing | 1,464 | 11,000 | 9,536 | gen#960 | board games and puzzles (10 board games today), action figures, dolls in depth, building sets (89 today), arts and crafts (38 today), remote-control vehicles, learning toys, trampolines and swings |
| Garden | retail | existing | 827 | 9,000 | 8,173 | gen#961 | patio furniture in depth, planters and pots, hand tools, seeds and bulbs, outdoor lighting, soil and compost, weed and pest control, bird care, grill accessories |
| Cleaning | retail | existing | 835 | 9,000 | 8,165 | gen#962 | paper towels, toilet paper and tissues, trash bags, food storage (foil, wrap, zip bags), sponges and cloths, dishwasher tablets, laundry pods and stain removers, light bulbs and batteries |
| Home | retail | existing | 14,059 | 25,000 | 10,941 | gen#963 | small kitchen appliances (coffee makers, kettles, toasters, air fryers, blenders), cookware and bakeware, storage and organization (344 today), sheets and pillows, rugs, curtains and blinds, mirrors and wall art, desks, bookcases, beds and mattresses, vacuums, fans and heaters |
| Food & drink | retail | existing | 12,265 | 17,000 | 4,735 | gen#964 | coffee, cereal, rice and grains, herbs and spices, canned and international foods, frozen meals, baking |
| Kids | retail | existing | 15,567 | 19,000 | 3,433 | gen#965 | baby gear under Kids > Baby: diapers and wipes, bottles and feeding, high chairs, strollers, car seats, nursery furniture, baby monitors |
| Gifts | retail | existing | 1,003 | 3,000 | 1,997 | gen#966 | party supplies (balloons, party tableware), seasonal decorations (Christmas, Halloween), gift wrap and cards in depth |
| Pets | retail | new | 0 | 7,000 | 7,000 | gen#967 | dog and cat food, treats, cat litter, toys, beds and crates, leashes and collars, grooming, aquarium and small-animal supplies |
| Health | retail | new | 0 | 5,000 | 5,000 | gen#968 | vitamins and supplements, first aid, thermometers and blood-pressure monitors, eye care, incontinence, mobility aids; over-the-counter only, invented brands, no medical claims |
| Office & school | retail | new | 0 | 4,500 | 4,500 | gen#969 | pens and pencils, paper and notebooks, binders and folders, backpacks, desk accessories, calculators, art supplies |
| Automotive | retail | existing | 0 | 2,000 | 2,000 | gen#970 | car wash and wax, wiper blades, motor oil and fluids, phone mounts, seat covers and floor mats, jump starters, tire inflators |
| Hardware | industrial | existing | 73,436 | 75,000 | 1,564 | gen#958 | home hardware only: picture hanging, hooks, wall anchors, door and cabinet knobs and hinges, shelf brackets, household fastener assortments |
| Tools | industrial | existing | 58,147 | 59,500 | 1,353 | gen#971 | homeowner tools only: tape measures, levels, utility knives, stud finders, household tool sets |
| Workshop & safety | industrial | existing | 413 | 413 | 0 | none | none |
| Womens | retail | existing | 163,904 | 163,904 | 0 | none | none |
| Mens | retail | existing | 47,998 | 47,998 | 0 | none | none |
| **Total** | | | **394,766** | **497,315** | **102,549** | | |

The new targets put 362,402 SKUs in retail and 134,913 in industrial. The growth is 102,549:
99,632 of it in retail and 2,917 in industrial home hardware and DIY. The thin departments come
first in the table, as the issue orders, and then the departments the catalogue lacks.

## Left out

- **Books, music, movies and video games.** All four retailers sell them, but each product is a
  named work. An invented title has no attributes to filter on, and a real one fails the
  non-copying audit.
- **Prescription pharmacy and fresh perishables.** These go beyond what the demo searches today.
  Health stays over the counter.
- **More apparel.** Womens and Mens hold 54% of the SKUs today and 43% at the target. That share
  is already above what a general retailer carries, so they do not grow.

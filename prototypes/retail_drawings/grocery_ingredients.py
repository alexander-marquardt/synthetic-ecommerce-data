"""Invented ingredient lists for the grocery build (gen#154): data and a small expander.

A food SKU's list is its flavor's ``HEAD`` (the main ingredients, heaviest first) and
its family's ``TAIL`` (the small print), 5 to 20 strings in descending-weight order as
on a label. Everything is invented: Open Food Facts inspired only the label shape
(a bracketed percentage on a named ingredient, an additive written ``class (name)``).

Two marks in a string are drawn once per product, so every variant of a product reads
the same: ``a|b`` picks one alternative, and ``{lo-hi}`` an integer in the range.

A flavor's head must name a source of exactly the allergens its codes list
(``grocery_rows.F.codes``): ``tests/test_grocery_ingredients_154.py`` holds every list
to its SKU's ``contains``. Fresh whole fruit and vegetables carry no list, as on a
shop shelf. Plain staples (tea, coffee, milk, pasta, honey) are written as a blend of
origins or as their fortification so that a list reaches five.
"""

# ruff: noqa: E501 -- one flavor per line reads better than wrapped (data only).

from __future__ import annotations

import re
import zlib

#: Families whose products are sold loose or whole and carry no ingredients list.
NO_LIST = frozenset({"ORA", "LEM", "APP", "VEG"})

_MARK = re.compile(r"\{(\d+)-(\d+)\}")
_VAT = "vitamin d3, vitamin a, calcium, riboflavin"

#: Family code -> the small print every flavor of the family ends with.
TAIL: dict[str, str] = {
    "CHB": "emulsifier (soya lecithin), natural flavoring",
    "CHX": "emulsifier (soya lecithin), natural flavoring",
    "SWT": "natural flavoring, color (anthocyanins)",
    "BIS": "salt, raising agent (sodium bicarbonate), natural flavoring",
    "ORB": "salt, raising agent (sodium bicarbonate), natural flavoring",
    "CHO": "emulsifier (soya lecithin), natural flavoring",
    "PAN": "salt, preservative (potassium sorbate), natural flavoring",
    "CRS": "antioxidant (rosemary extract)",
    "CBR": "emulsifier (sunflower lecithin), natural flavoring",
    "CER": "salt, vitamins (niacin, b6, folic acid)",
    "BRD": "yeast, salt, preservative (calcium propionate)",
    "CAK": "raising agents (diphosphates, sodium carbonates), salt",
    "MLK": _VAT,
    "PLM": "calcium carbonate, sea salt, vitamins (b12, d2), stabiliser (gellan gum)",
    "YOG": "live yoghurt cultures",
    "FRV": "sunflower oil, sea salt, black pepper",
    "PAS": "niacin, iron, thiamin, riboflavin",
}

#: (family code, flavor name) -> the flavor's main ingredients, heaviest first.
HEAD: dict[tuple[str, str], str] = {
    ("CHB", "Milk"): "sugar, cocoa butter, whole milk powder, cocoa mass, whey powder|lactose",
    ("CHB", "Dark 70%"): "cocoa mass (70% cocoa solids), sugar, cocoa butter",
    ("CHB", "Hazelnut Milk"): "sugar, cocoa butter, whole milk powder, cocoa mass, hazelnut paste ({8-15}%)",
    ("CHB", "Peanut Caramel"): "sugar, cocoa butter, whole milk powder, roasted peanuts ({10-18}%), cocoa mass, caramel pieces",
    ("CHB", "Mint Dark"): "cocoa mass ({55-70}%), sugar, cocoa butter, peppermint oil",
    ("CHB", "Orange Dark"): "cocoa mass ({55-70}%), sugar, cocoa butter, orange oil",
    ("CHB", "Coconut Dark"): "cocoa mass ({55-70}%), sugar, cocoa butter, desiccated coconut ({5-10}%)",
    ("CHB", "Salted Caramel Milk"): "sugar, cocoa butter, whole milk powder, cocoa mass, salted caramel pieces, sea salt",
    ("CHB", "White"): "sugar, cocoa butter, whole milk powder, skimmed milk powder, vanilla extract",
    ("CHB", "Almond Dark"): "cocoa mass ({55-70}%), sugar, cocoa butter, toasted almonds ({8-14}%)",
    ("CHB", "Lemon White"): "sugar, cocoa butter, whole milk powder, freeze-dried lemon, lemon oil",
    ("CHB", "Raspberry Dark"): "cocoa mass ({55-70}%), sugar, cocoa butter, freeze-dried raspberry ({3-6}%)",
    ("CHX", "Classic Milk"): "sugar, cocoa butter, whole milk powder, cocoa mass, glucose syrup",
    ("CHX", "Praline"): "sugar, cocoa butter, whole milk powder, hazelnut praline ({10-20}%), cocoa mass",
    ("CHX", "Dark Truffle"): "sugar, cocoa mass, cocoa butter, double cream, butter, glucose syrup",
    ("CHX", "Mint Crisp"): "sugar, cocoa butter, whole milk powder, cocoa mass, peppermint oil, sugar crystals",
    ("CHX", "Orange Cream"): "sugar, cocoa butter, whole milk powder, cocoa mass, orange oil, cream powder",
    ("CHX", "Vegan Dark"): "cocoa mass, sugar, cocoa butter, coconut oil, vanilla extract",
    ("SWT", "Fruit Gums"): "glucose syrup, sugar, modified maize starch, fruit juice from concentrate ({1-3}%), glazing agent (beeswax)",
    ("SWT", "Lemon Sherbets"): "sugar, glucose syrup, dextrose, lemon oil, sodium bicarbonate",
    ("SWT", "Mint Imperials"): "sugar, glucose syrup, peppermint oil, maize starch, citric acid",
    ("SWT", "Fizzy Cola"): "glucose syrup, sugar, modified maize starch, cola flavoring, glazing agent (beeswax)",
    ("SWT", "Toffee"): "sugar, glucose syrup, condensed skimmed milk, butter ({4-8}%), salt",
    ("SWT", "Vegan Jellies"): "glucose syrup, sugar, modified maize starch, fruit juice from concentrate, citric acid",
    ("BIS", "Chocolate Chip"): "wheat flour, sugar, butter, milk chocolate chips ({10-16}%), emulsifier (soya lecithin)",
    ("BIS", "Ginger Snap"): "wheat flour, sugar, sunflower oil, ground ginger ({1-3}%), golden syrup",
    ("BIS", "Shortbread"): "wheat flour, butter ({20-30}%), sugar, rice flour",
    ("BIS", "Oat & Coconut"): "rolled oats ({20-30}%), wheat flour, sugar, sunflower oil, desiccated coconut ({4-8}%)",
    ("BIS", "Lemon Puff"): "wheat flour, sugar, butter, lemon curd filling ({6-10}%), pasteurised egg, lemon oil",
    ("BIS", "Milk Chocolate Digestive"): "wheat flour, milk chocolate ({20-30}%), sugar, wholemeal wheat flour, vegetable oil, emulsifier (soya lecithin)",
    ("CRS", "Sea Salt"): "potatoes ({70-80}%), sunflower oil|rapeseed oil|palm oil, sea salt, potato starch, sugar",
    ("CRS", "Cheese & Onion"): "potatoes, sunflower oil|rapeseed oil|palm oil, cheese powder ({3-6}%), onion powder, whey powder, sea salt",
    ("CRS", "Salt & Vinegar"): "potatoes, sunflower oil|rapeseed oil|palm oil, salt, white wine vinegar powder, acidity regulator (sodium diacetate)",
    ("CRS", "Sweet Chilli"): "potatoes, sunflower oil|rapeseed oil|palm oil, sugar, chilli powder, paprika extract, sea salt",
    ("CRS", "Smoky Bacon"): "potatoes, sunflower oil|rapeseed oil|palm oil, smoked paprika, yeast extract, sea salt, smoke flavoring",
    ("CRS", "Sour Cream & Chive"): "potatoes, sunflower oil|rapeseed oil|palm oil, sour cream powder ({2-4}%), chives, sea salt, whey powder",
    ("NUT", "Salted Peanuts"): "peanuts ({88-94}%), sunflower oil, sea salt, rice flour, natural flavoring",
    ("NUT", "Honey Roast Cashews"): "cashew nuts ({55-65}%), honey ({8-14}%), sugar, sunflower oil, sea salt",
    ("NUT", "Mixed Nuts"): "peanuts, almonds, cashew nuts, hazelnuts, brazil nuts, sunflower oil, sea salt",
    ("NUT", "Sweet & Salty Popcorn"): "popcorn kernels ({50-60}%), sugar, sunflower oil, sea salt, natural flavoring",
    ("NUT", "Coconut Chips"): "coconut chips ({85-92}%), sugar, sea salt, sunflower oil, natural flavoring",
    ("NUT", "Toffee Popcorn"): "popcorn kernels, sugar, butter, glucose syrup, sunflower oil, skimmed milk powder, salt",
    ("CBR", "Oat & Honey"): "rolled oats ({30-40}%), glucose syrup, honey ({5-10}%), sunflower oil, sugar",
    ("CBR", "Chocolate Chip"): "rolled oats, glucose syrup, milk chocolate chips ({8-14}%), sugar, soya flour",
    ("CBR", "Peanut Butter"): "rolled oats, glucose syrup, peanut paste ({12-20}%), roasted peanuts, sugar",
    ("CBR", "Apple & Cinnamon"): "rolled oats, glucose syrup, dried apple ({10-15}%), sugar, cinnamon",
    ("CBR", "Coconut & Cashew"): "puffed rice, glucose syrup, coconut chips, cashew nuts, sugar",
    ("CBR", "Lemon & Poppy"): "rolled oats, glucose syrup, sugar, poppy seeds, lemon peel, lemon oil",
    ("CER", "Honey Oat Crunch"): "wholegrain oats ({40-50}%), sugar, honey ({3-6}%), sunflower oil, wheat flour",
    ("CER", "Chocolate Hoops"): "wholegrain wheat, sugar, cocoa powder ({4-8}%), skimmed milk powder, sunflower oil",
    ("CER", "Bran Flakes"): "wholegrain wheat ({60-70}%), wheat bran ({10-20}%), sugar, barley malt extract",
    ("CER", "Fruit & Nut Muesli"): "rolled oats, raisins ({10-15}%), hazelnuts ({4-8}%), dried apple, sunflower seeds",
    ("CER", "Corn Flakes"): "maize grits, sugar, glucose syrup, caramelised sugar",
    ("CER", "Coconut Granola"): "rolled oats, coconut chips ({8-14}%), sugar, sunflower oil, glucose syrup",
    ("OAT", "Original"): "rolled oats, oat bran, oat flour, sugar, salt",
    ("OAT", "Golden Syrup"): "rolled oats, golden syrup ({6-10}%), sugar, oat bran, salt",
    ("OAT", "Apple & Blueberry"): "rolled oats, dried apple ({4-8}%), blueberry pieces ({2-4}%), sugar, cinnamon",
    ("OAT", "Gluten Free Oat"): "gluten free rolled oats, gluten free oat bran, sugar, salt, natural flavoring",
    ("BRD", "White"): "wheat flour, water, rapeseed oil, sugar, ascorbic acid",
    ("BRD", "Wholemeal"): "wholemeal wheat flour, water, wheat bran, rapeseed oil, sugar",
    ("BRD", "Seeded"): "wheat flour, water, sunflower seeds, linseed, pumpkin seeds, rapeseed oil",
    ("BRD", "Sourdough"): "wheat flour, water, rye flour, sourdough culture, rapeseed oil",
    ("BRD", "Gluten Free Brown"): "water, brown rice flour, tapioca starch, maize starch, egg white, psyllium husk, rapeseed oil",
    ("CAK", "Lemon Drizzle"): "sugar, wheat flour, butter, pasteurised egg, lemon juice, lemon zest",
    ("CAK", "Chocolate Fudge"): "sugar, wheat flour, butter, egg, cocoa powder, fudge pieces, soya flour",
    ("CAK", "Coffee & Walnut"): "sugar, wheat flour, butter, egg, walnuts ({6-10}%), coffee extract",
    ("CAK", "Carrot"): "sugar, wheat flour, carrots ({15-22}%), pasteurised egg, butter, cinnamon",
    ("CAK", "Victoria Sponge"): "sugar, wheat flour, butter, egg, strawberry jam ({8-12}%), icing sugar",
    ("MLK", "Whole"): "pasteurised whole cows' milk",
    ("MLK", "Semi Skimmed"): "pasteurised semi-skimmed cows' milk",
    ("MLK", "Skimmed"): "pasteurised skimmed cows' milk",
    ("MLK", "Lactose Free"): "pasteurised semi-skimmed cows' milk, lactase enzyme",
    ("PLM", "Oat"): "water, oats ({10-12}%), rapeseed oil",
    ("PLM", "Almond"): "water, almonds ({2-3}%)",
    ("PLM", "Soya"): "water, hulled soya beans ({8-10}%)",
    ("PLM", "Coconut"): "water, coconut milk ({5-8}%), rice ({3-4}%)",
    ("PLM", "Barista Oat"): "water, oats ({10-12}%), rapeseed oil, acidity regulator (dipotassium phosphate)",
    ("YOG", "Natural"): "whole milk, cream, skimmed milk powder, milk protein concentrate",
    ("YOG", "Strawberry"): "whole milk, strawberries ({6-9}%), sugar, skimmed milk powder, maize starch",
    ("YOG", "Lemon Curd"): "whole milk, sugar, lemon curd ({6-9}%), egg yolk, skimmed milk powder",
    ("YOG", "Coconut"): "whole milk, coconut ({4-7}%), sugar, skimmed milk powder, maize starch",
    ("YOG", "Honey"): "whole milk, honey ({5-8}%), skimmed milk powder, cream, maize starch",
    ("YOG", "Vanilla"): "whole milk, sugar, skimmed milk powder, vanilla extract, maize starch",
    ("BUT", "Salted Butter"): "pasteurised cream, water, salt, lactic culture, color (carotenes)",
    ("BUT", "Unsalted Butter"): "pasteurised cream, water, lactic culture, color (carotenes), vitamin a",
    ("BUT", "Spreadable Butter"): "butter ({75-80}%), rapeseed oil, water, salt, natural flavoring",
    ("BUT", "Plant Spread"): "sunflower oil, water, rapeseed oil, palm oil, salt, emulsifier (sunflower lecithin), vitamin d",
    ("CHE", "Mature Cheddar"): "pasteurised cows' milk, salt, starter culture, vegetable rennet, color (annatto)",
    ("CHE", "Red Leicester"): "pasteurised cows' milk, salt, starter culture, vegetable rennet, color (annatto)",
    ("CHE", "Wensleydale & Cranberry"): "pasteurised cows' milk, cranberries ({8-12}%), sugar, salt, starter culture",
    ("CHE", "Blue Stilton"): "pasteurised cows' milk, salt, starter culture, vegetable rennet, penicillium roqueforti",
    ("CHE", "Smoked Applewood"): "pasteurised cows' milk, salt, starter culture, vegetable rennet, smoked paprika",
    ("CHE", "Vegan Cheddar Style"): "coconut oil ({20-24}%), potato starch, water, sea salt, olive extract, natural flavoring",
    ("RDY", "Chicken Tikka Masala"): "cooked chicken breast ({22-28}%), water, tomato, cream ({6-9}%), onion, yoghurt, rapeseed oil, ginger, garlic, ground coriander, cumin, sugar, salt, turmeric, chilli powder",
    ("RDY", "Beef Lasagne"): "beef ({18-24}%), water, tomato, cooked lasagne pasta (water, durum wheat semolina), milk, onion, carrot, cheddar cheese, butter, wheat flour, salt, garlic, oregano",
    ("RDY", "Vegetable Chilli"): "kidney beans, tomato, water, onion, red pepper, sweetcorn, rapeseed oil, garlic, cumin, chilli powder, salt",
    ("RDY", "Macaroni Cheese"): "cooked macaroni (water, durum wheat semolina), milk, cheddar cheese ({16-22}%), wheat flour, butter, mustard powder, salt, nutmeg",
    ("RDY", "Thai Green Curry"): "cooked chicken, coconut milk ({14-20}%), water, green beans, bamboo shoots, green curry paste, sugar, lime leaf, salt, rapeseed oil",
    ("RDY", "Lemon Chicken"): "cooked chicken breast ({30-38}%), water, lemon juice, sugar, maize starch, rapeseed oil, garlic, salt, lemon zest, ginger",
    ("PIZ", "Margherita"): "wheat flour, tomato, mozzarella cheese ({18-24}%), water, rapeseed oil, yeast, salt, basil, sugar",
    ("PIZ", "Pepperoni"): "wheat flour, mozzarella cheese, tomato, pepperoni ({10-15}%), water, rapeseed oil, yeast, salt, sugar, oregano",
    ("PIZ", "Vegan Garden"): "wheat flour, tomato, water, red pepper, courgette, aubergine, rapeseed oil, yeast, dairy free topping (coconut oil, potato starch), salt, basil",
    ("PIZ", "Four Cheese"): "wheat flour, tomato, mozzarella cheese ({12-16}%), cheddar cheese, edam cheese, emmental cheese, water, rapeseed oil, yeast, salt",
    ("PIZ", "Ham & Pineapple"): "wheat flour, mozzarella cheese, tomato, cooked ham ({8-12}%), pineapple ({8-12}%), water, rapeseed oil, yeast, salt",
    ("ICE", "Vanilla"): "whole milk, cream, sugar, skimmed milk powder, egg yolk, vanilla extract, stabiliser (locust bean gum)",
    ("ICE", "Mint Choc Chip"): "milk, sugar, cream, chocolate chips ({6-9}%), skimmed milk powder, peppermint oil, emulsifier (soya lecithin), stabiliser (guar gum)",
    ("ICE", "Honeycomb"): "milk, cream, sugar, honeycomb pieces ({8-12}%), skimmed milk powder, honey, stabiliser (guar gum)",
    ("ICE", "Lemon Sorbet"): "water, sugar, lemon juice from concentrate ({18-24}%), glucose syrup, lemon zest, stabiliser (pectin)",
    ("ICE", "Coconut Dairy Free"): "water, coconut milk ({12-18}%), sugar, coconut oil, glucose syrup, stabiliser (locust bean gum)",
    ("ICE", "Salted Caramel"): "milk, cream, sugar, caramel sauce ({8-12}%), skimmed milk powder, sea salt, stabiliser (guar gum)",
    ("FRV", "Garden Peas"): "garden peas ({88-94}%), water",
    ("FRV", "Sweetcorn"): "sweetcorn kernels ({88-94}%), water",
    ("FRV", "Mixed Vegetables"): "carrots, sweetcorn, garden peas, green beans",
    ("FRV", "Broccoli Florets"): "broccoli florets ({88-94}%), water",
    ("FRV", "Edamame Beans"): "edamame soya beans ({88-94}%), water",
    ("TIN", "Chopped Tomatoes"): "tomatoes ({90-95}%), tomato juice, firming agent (calcium chloride), acidity regulator (citric acid), basil",
    ("TIN", "Baked Beans"): "haricot beans ({50-55}%), tomatoes, water, sugar, maize starch, salt, spirit vinegar, onion powder",
    ("TIN", "Coconut Milk"): "coconut extract ({55-60}%), water, guar gum, citric acid, sea salt",
    ("TIN", "Chickpeas"): "chickpeas ({55-60}%), water, salt, firming agent (calcium chloride), antioxidant (ascorbic acid)",
    ("TIN", "Tuna in Spring Water"): "yellowfin tuna ({70-75}%), spring water, salt, citric acid, ascorbic acid",
    ("TIN", "Peach Slices"): "peaches ({50-55}%), water, apple juice from concentrate, acidity regulator (citric acid), antioxidant (ascorbic acid)",
    ("PAS", "Penne"): "durum wheat semolina",
    ("PAS", "Fusilli"): "durum wheat semolina",
    ("PAS", "Spaghetti"): "durum wheat semolina",
    ("PAS", "Egg Tagliatelle"): "durum wheat semolina, pasteurised egg ({20-25}%)",
    ("PAS", "Gluten Free Penne"): "maize flour, rice flour, maize starch, emulsifier (mono- and diglycerides of fatty acids)",
    ("PAS", "Lemon & Pepper Linguine"): "durum wheat semolina, lemon powder, black pepper, parsley",
    ("RIC", "Basmati Rice"): "cooked basmati rice ({80-90}%), water, sunflower oil, salt, natural flavoring",
    ("RIC", "Long Grain Rice"): "cooked long grain rice ({80-90}%), water, sunflower oil, salt, natural flavoring",
    ("RIC", "Brown Rice"): "cooked brown rice ({80-90}%), water, sunflower oil, salt, natural flavoring",
    ("RIC", "Coconut Jasmine Rice"): "cooked jasmine rice ({70-80}%), water, coconut extract, sunflower oil, salt",
    ("RIC", "Quinoa"): "cooked quinoa ({80-90}%), water, sunflower oil, salt, lemon juice",
    ("RIC", "Couscous"): "durum wheat semolina, water, sunflower oil, sea salt, natural flavoring",
    ("SAU", "Tomato Ketchup"): "tomatoes, spirit vinegar, sugar, salt, spice extracts",
    ("SAU", "Mayonnaise"): "rapeseed oil ({60-70}%), water, pasteurised egg yolk ({5-8}%), spirit vinegar, salt, mustard, sugar",
    ("SAU", "Brown Sauce"): "tomatoes, barley malt vinegar, sugar, dates, molasses, salt, spices",
    ("SAU", "Sweet Chilli Sauce"): "sugar, water, red chilli ({8-12}%), garlic, white wine vinegar, salt, maize starch",
    ("SAU", "Mint Sauce"): "spirit vinegar, mint ({20-30}%), sugar, water, salt",
    ("SAU", "Honey & Mustard Dressing"): "rapeseed oil, honey ({6-9}%), water, mustard, spirit vinegar, sugar, salt",
    ("JAM", "Clear Honey"): "clover honey, wildflower honey, orange blossom honey, heather honey, acacia honey",
    ("JAM", "Set Honey"): "clover honey, wildflower honey, orange blossom honey, heather honey, acacia honey",
    ("JAM", "Strawberry Jam"): "strawberries, sugar, glucose syrup, gelling agent (pectin), acidity regulator (citric acid)",
    ("JAM", "Lemon Curd"): "sugar, butter, lemon juice, pasteurised egg ({8-12}%), lemon zest, maize starch",
    ("JAM", "Seville Orange Marmalade"): "sugar, seville oranges ({33-40}%), water, gelling agent (pectin), acidity regulator (sodium citrate), orange peel",
    ("JAM", "Raspberry Jam"): "raspberries, sugar, glucose syrup, gelling agent (pectin), acidity regulator (citric acid)",
    ("SPR", "Smooth Peanut Butter"): "roasted peanuts ({92-98}%), palm oil, sugar, sea salt, rapeseed oil",
    ("SPR", "Crunchy Peanut Butter"): "roasted peanuts ({85-92}%), peanut pieces, palm oil, sugar, sea salt",
    ("SPR", "Almond Butter"): "roasted almonds ({92-98}%), sunflower oil, sea salt, sugar, palm oil",
    ("SPR", "Chocolate Hazelnut Spread"): "sugar, palm oil, hazelnuts ({13-20}%), skimmed milk powder, cocoa powder, emulsifier (soya lecithin), vanillin",
    ("SPR", "Cashew Butter"): "roasted cashew nuts ({92-98}%), sunflower oil, sea salt, sugar, palm oil",
    ("SPR", "Smooth Chocolate Spread"): "sugar, sunflower oil, skimmed milk powder, cocoa powder ({6-10}%), whey powder, vanilla extract",
    ("WLD", "Korma Paste"): "water, sunflower oil, cashew nuts ({8-12}%), cream ({3-5}%), onion, sugar, ginger, garlic, ground coriander, salt, turmeric, cumin",
    ("WLD", "Red Thai Curry Paste"): "red chilli, lemongrass, garlic, galangal, shallot, salt, kaffir lime peel, sunflower oil",
    ("WLD", "Mango Chutney"): "mango ({35-45}%), sugar, spirit vinegar, water, salt, ginger, chilli, spices",
    ("WLD", "Harissa"): "red peppers, tomato puree, rapeseed oil, chilli, garlic, salt, caraway, cumin, coriander",
    ("WLD", "Coconut & Lemongrass Paste"): "water, coconut extract ({20-26}%), lemongrass ({6-9}%), galangal, sunflower oil, garlic, sugar, salt, lime juice",
    ("WLD", "Miso Paste"): "soya beans ({40-50}%), water, rice, salt, koji",
    ("TEA", "English Breakfast"): "black tea (assam), black tea (kenya), black tea (ceylon), black tea (rwanda), black tea (malawi)",
    ("TEA", "Earl Grey"): "black tea (ceylon), black tea (assam), bergamot flavoring ({1-2}%), cornflower petals, orange peel",
    ("TEA", "Peppermint"): "peppermint leaves, spearmint leaves, natural mint flavoring, liquorice root, lemon balm",
    ("TEA", "Lemon & Ginger"): "ginger root, lemon peel, lemongrass, natural lemon flavoring, liquorice root",
    ("TEA", "Green"): "green tea (sencha), green tea (gunpowder), jasmine petals, lemon verbena, natural flavoring",
    ("TEA", "Honey & Vanilla Rooibos"): "rooibos, honey granules ({3-5}%), vanilla pieces, natural flavoring, cinnamon",
    ("COF", "Medium Roast Instant"): "freeze-dried arabica coffee, freeze-dried robusta coffee, roasted coffee granules, natural coffee aroma, coffee oil",
    ("COF", "Dark Roast Ground"): "dark roasted arabica coffee (brazil), dark roasted arabica coffee (colombia), dark roasted robusta coffee (vietnam), roasted coffee (honduras), roasted coffee (peru)",
    ("COF", "Decaf Instant"): "decaffeinated arabica coffee, decaffeinated robusta coffee, roasted coffee granules, natural coffee aroma, coffee oil",
    ("COF", "Hazelnut Flavored Ground"): "roasted arabica coffee (brazil), roasted arabica coffee (colombia), roasted robusta coffee (vietnam), natural flavorings, coffee oil",
    ("COF", "Colombian Ground"): "roasted arabica coffee (huila), roasted arabica coffee (narino), roasted arabica coffee (cauca), roasted arabica coffee (tolima), roasted arabica coffee (santander)",
    ("SFT", "Cloudy Lemonade"): "carbonated water, sugar, lemon juice from concentrate ({4-8}%), citric acid, natural flavoring",
    ("SFT", "Orange Crush"): "carbonated water, orange juice from concentrate ({5-10}%), sugar, citric acid, natural flavoring, color (carotenes)",
    ("SFT", "Cola"): "carbonated water, sugar, color (caramel e150d), phosphoric acid, natural flavoring, caffeine",
    ("SFT", "Ginger Beer"): "carbonated water, sugar, ginger extract ({1-2}%), citric acid, natural flavoring",
    ("SFT", "Elderflower Presse"): "carbonated water, apple juice from concentrate, sugar, elderflower extract, citric acid, natural flavoring",
    ("SFT", "Sparkling Mint Water"): "carbonated water, mint extract, lime juice, citric acid, natural flavoring",
    ("JUI", "Smooth Orange"): "orange juice, orange puree, orange oil, orange flavoring, vitamin c",
    ("JUI", "Orange with Bits"): "orange juice from concentrate, orange pulp, orange juice cells, orange oil, vitamin c",
    ("JUI", "Apple"): "apple juice from concentrate, apple puree, malic acid, vitamin c, antioxidant (ascorbic acid)",
    ("JUI", "Pineapple"): "pineapple juice from concentrate, pineapple puree, citric acid, vitamin c, natural flavoring",
    ("JUI", "Coconut Water"): "coconut water ({95-99}%), coconut water concentrate, vitamin c, citric acid, natural flavoring",
    ("BAB", "Apple & Pear"): "apple puree ({50-60}%), pear puree ({25-35}%), water, rice flour, vitamin c",
    ("BAB", "Sweet Potato & Carrot"): "sweet potato ({40-50}%), carrot ({30-40}%), water, sunflower oil, vitamin c",
    ("BAB", "Banana & Mango"): "banana puree, mango puree, water, apple juice, vitamin c",
    ("BAB", "Creamy Porridge"): "oat flour, skimmed milk powder, water, sunflower oil, iron, vitamin d",
    ("FRE", "Chocolate Brownies"): "sugar, rice flour, rapeseed oil, cocoa powder ({8-12}%), water, potato starch, tapioca starch, raising agents (sodium carbonates)",
    ("FRE", "Lemon Slices"): "sugar, rice flour, rapeseed oil, lemon juice ({4-8}%), maize starch, water, xanthan gum, lemon oil",
    ("FRE", "Oat Cookies"): "gluten free oats ({30-40}%), sugar, rapeseed oil, rice flour, golden syrup, raising agent (sodium bicarbonate)",
    ("FRE", "Orange Shortbread"): "rice flour, maize starch, sunflower oil, sugar, orange peel, orange oil",
    ("MEA", "Chicken Breast Fillets"): "chicken breast ({92-97}%), water, salt, stabiliser (sodium triphosphate), rapeseed oil",
    ("MEA", "Beef Mince"): "beef ({90-95}%), beef fat, water, salt, black pepper",
    ("MEA", "Pork Sausages"): "pork ({70-80}%), water, wheat rusk, salt, spices, dextrose, antioxidant (ascorbic acid)",
    ("MEA", "Smoked Bacon"): "pork belly, salt, sugar, preservative (sodium nitrite), antioxidant (sodium ascorbate)",
    ("MEA", "Lemon & Herb Chicken Thighs"): "chicken thighs ({80-88}%), lemon juice, rapeseed oil, herbs (parsley, thyme), salt, garlic",
    ("FSH", "Salmon Fillets"): "salmon ({93-97}%), sea salt, sunflower oil, black pepper, lemon juice",
    ("FSH", "Cod Loins"): "cod ({85-92}%), water, salt, stabiliser (sodium triphosphate), antioxidant (ascorbic acid)",
    ("FSH", "Smoked Mackerel"): "mackerel, salt, oak smoke, sugar, sunflower oil",
    ("FSH", "Lemon & Pepper Haddock"): "haddock, lemon juice, black pepper, rapeseed oil, salt, lemon zest",
    ("BRD", "Malted Beer"): "wheat flour, water, beer (water, barley malt), malted barley flour, treacle, rapeseed oil",
    # Beer: every list names barley malt, the source of its gluten.
    ("BLG", "Premium Lager"): "water, barley malt, maize, hops, hop extract, yeast",
    ("BLG", "Helles Lager"): "water, pilsner malt, caramalt, hop pellets, hop extract, yeast",
    ("BLG", "Pilsner"): "water, pilsner malt (barley), saaz hops, malted barley, hop extract, yeast",
    ("BLG", "Golden Table Beer"): "water, barley malt, caramalt, english hops, hop extract, yeast",
    ("BLG", "Export Lager"): "water, barley malt, rice, hops, hop extract, yeast",
    ("BPA", "Session Pale Ale"): "water, pale malt (barley), crystal malt, citra hops, hop extract, yeast",
    ("BPA", "American Pale Ale"): "water, pale malt (barley), crystal malt, cascade hops, centennial hops, yeast",
    ("BPA", "Hazy Pale Ale"): "water, pale malt (barley), oats, wheat malt, mosaic hops, yeast",
    ("BPA", "Hazy Wheat Beer"): "water, wheat malt, barley malt, coriander seed, orange peel, hops, yeast",
    ("BSO", "Tropical Pineapple Sour Beer"): "water, barley malt, wheat malt, pineapple juice ({3-6}%), passion fruit juice, lactic acid, hops, yeast",
    ("BSO", "Raspberry Sour Beer"): "water, barley malt, wheat malt, raspberry puree ({4-8}%), lactic acid, hops, yeast",
    ("BSO", "Passion Fruit Sour Beer"): "water, barley malt, wheat malt, passion fruit juice ({4-8}%), lactic acid, hops, yeast",
    ("BSO", "Salted Gose Sour Beer"): "water, wheat malt, barley malt, sea salt, coriander seed, lactic acid, hops, yeast",
    ("BFR", "Raspberry Fruit Beer"): "water, barley malt, raspberry juice ({8-12}%), sugar, hops, yeast",
    ("BFR", "Cherry Fruit Beer"): "water, barley malt, cherry juice ({8-12}%), sugar, hops, yeast",
    ("BFR", "Blood Orange Fruit Beer"): "water, barley malt, blood orange juice ({8-12}%), sugar, hops, yeast",
    ("BFR", "Peach Fruit Beer"): "water, barley malt, peach puree ({8-12}%), sugar, hops, yeast",
    ("BAF", "Alcohol Free Lager"): "water, barley malt, maize, hops, hop extract, yeast",
    ("BAF", "Alcohol Free Pale Ale"): "water, pale malt (barley), crystal malt, citra hops, hop extract, yeast",
    ("BAF", "Low Alcohol Pilsner"): "water, pilsner malt (barley), saaz hops, malted barley, hop extract, yeast",
    ("BAF", "Alcohol Free Wheat Beer"): "water, wheat malt, barley malt, coriander seed, hops, yeast",
    # The word beer, not the drink.
    ("GNB", "Ginger Beer"): "carbonated water, sugar, ginger extract ({1-2}%), lemon juice from concentrate, citric acid, natural flavoring",
    ("GNB", "Fiery Ginger Beer"): "carbonated water, sugar, ginger extract ({3-5}%), chilli extract, lemon juice from concentrate, citric acid",
    ("GNB", "Root Beer"): "carbonated water, sugar, caramel color, sarsaparilla extract, vanilla extract, natural flavoring",
    ("BBF", "Beer Battered Scottish Haddock"): "haddock ({45-55}%), wheat flour, water, beer (water, barley malt), rapeseed oil, maize starch, salt, raising agents (diphosphates, sodium carbonates)",
    ("BBF", "Beer Battered Cod Fillets"): "cod ({45-55}%), wheat flour, water, beer (water, barley malt), rapeseed oil, maize starch, salt, raising agents (diphosphates, sodium carbonates)",
    ("BBF", "Crispy Battered Haddock"): "haddock ({45-55}%), wheat flour, water, rapeseed oil, maize starch, salt, raising agents (diphosphates, sodium carbonates)",
    ("VIN", "Cider Vinegar"): "cider vinegar, apple juice concentrate, water, acidity regulator (acetic acid), natural cloudiness",
    ("VIN", "Raw Cider Vinegar"): "unfiltered cider vinegar, apple juice concentrate, water, the mother, acidity regulator (acetic acid)",
    ("VIN", "Balsamic Vinegar"): "wine vinegar, grape must ({20-30}%), concentrated grape juice, water, color (caramel)",
    ("VIN", "White Wine Vinegar"): "white wine vinegar, water, grape must, acidity regulator (acetic acid), natural flavoring",
    ("WGM", "Wine Gums"): "glucose syrup, sugar, gelatine, wine flavoring, acid (citric acid), color (anthocyanins)",
    ("WGM", "Sour Wine Gums"): "glucose syrup, sugar, gelatine, citric acid, wine flavoring, color (anthocyanins)",
    ("WGM", "Vegan Wine Gums"): "glucose syrup, sugar, modified maize starch, wine flavoring, citric acid, color (anthocyanins)",
    # The word orange, not the fruit.
    ("CHO", "Milk Chocolate Orange"): "sugar, cocoa butter, whole milk powder, cocoa mass, orange oil, orange flakes ({2-4}%)",
    ("CHO", "Dark Chocolate Orange"): "cocoa mass ({50-60}%), sugar, cocoa butter, orange oil, orange flakes ({2-4}%)",
    ("PAN", "Cranberry & Orange Panettone"): "wheat flour, sugar, butter, egg yolk, candied orange peel ({5-9}%), dried cranberries ({4-8}%), yeast",
    ("PAN", "Lemon & Orange Panettone"): "wheat flour, sugar, butter, egg yolk, candied orange peel ({4-7}%), candied lemon peel ({3-5}%), yeast",
    ("PAN", "Cherry & Orange Christmas Pudding"): "vine fruit ({30-40}%), sugar, vegetable suet, wheat flour, glace cherries ({4-8}%), orange peel, egg",
    ("PAN", "Chocolate Panettone"): "wheat flour, sugar, butter, egg yolk, chocolate chips ({10-15}%), yeast",
    ("ORB", "Orange Shortbread"): "wheat flour, butter, sugar, orange peel ({1-3}%), orange oil",
    ("ORB", "Chocolate & Orange Cookies"): "wheat flour, sugar, butter, dark chocolate chips ({12-18}%), egg, orange oil",
    ("ORB", "Orange Cream Sandwich Biscuits"): "wheat flour, sugar, palm oil, butter, orange flavoring, emulsifier (soya lecithin)",
    ("HOT", "Orange Drinking Chocolate"): "sugar, cocoa powder ({18-25}%), skimmed milk powder, orange oil, natural flavoring, salt",
    ("HOT", "Classic Drinking Chocolate"): "sugar, cocoa powder ({18-25}%), skimmed milk powder, natural flavoring, salt",
    ("HOT", "Salted Caramel Hot Chocolate"): "sugar, cocoa powder ({15-20}%), skimmed milk powder, caramel pieces, sea salt, natural flavoring",
}  # fmt: skip


def _split(text: str) -> list[str]:
    """Split on the commas outside brackets."""
    out, depth, cur = [], 0, ""
    for ch in text:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return [*out, cur.strip()] if cur.strip() else out


def _draw(text: str, pid: str) -> str:
    """One ingredient with its marks resolved, from ``pid`` and the text alone."""
    key = zlib.crc32(f"{pid}:{text}".encode())
    if "|" in text:
        options = text.split("|")
        text = options[key % len(options)]
    return _MARK.sub(lambda m: str(int(m[1]) + key % (int(m[2]) - int(m[1]) + 1)), text)


def ingredients(family: str, flavor: str, pid: str) -> list[str] | None:
    """A flavor's list for product ``pid``: its head then its family's tail, or ``None``
    when the family carries no list."""
    if family in NO_LIST:
        return None
    items = [*_split(HEAD[family, flavor]), *_split(TAIL.get(family, ""))]
    return list(dict.fromkeys(_draw(i, pid) for i in items))


def shared(lists: list[list[str]]) -> list[str]:
    """A product's list: the items every variant lists (the base recipe), in the first
    variant's order. Never longer than a variant's list, so never over 20."""
    return [i for i in lists[0] if all(i in lst for lst in lists[1:])]


_PERCENT = re.compile(r"\s*\(\d+(?:\.\d+)?%\)")


def facet_value(item: str) -> str:
    """The filterable form of one label ingredient: lower-case, the percentage dropped
    ("Roasted Peanuts (94%)" -> "roasted peanuts"), the last word singularised when it
    is a regular plural ("red peppers" -> "red pepper", "cherries" -> "cherry"). A word
    ending in ss, us, is or ses is left alone ("molasses", "hummus")."""
    text = _PERCENT.sub("", item).strip().lower()
    head, sep, last = text.rpartition(" ")
    if last.endswith("ies") and len(last) > 4:
        last = last[:-3] + "y"
    elif last.endswith("s") and not last.endswith(("ss", "us", "is", "ses")) and len(last) > 3:
        last = last[:-1]
    return head + sep + last

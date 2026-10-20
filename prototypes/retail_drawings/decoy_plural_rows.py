"""Class 9 decoys: a product of another category whose title names a fresh plural (gen#445).

On the combined demo with interpretation off, "oranges" must not return fresh oranges alone. Each
row is a believable retail product (gen#444) whose title carries the exact plural of a fresh fruit
or vegetable as its ingredient or source: a juice pressed from oranges, sun-dried tomatoes in oil,
a strawberries and cream biscuit. The category, the ingredients and the drawing (a carton, a bar,
a tin) say what it is; no title or description claims it is the fresh fruit. The fixing policy is
the category-node reading of the fresh word (the Oranges node keeps the fresh leaf and drops the
rest). Titles are five or six tokens, so the title field's length does not put every fresh product
above them. Data only: :mod:`decoy_rows` turns each tuple into a :class:`decoy_rows.Decoy`.

A row is (code, kind, title, description, color, plural, sold, ingredients).
"""

# ruff: noqa: E501 -- one decoy's row reads better whole than wrapped (data only).

ROWS: tuple[tuple[str, str, str, str, str, str, int, tuple[str, ...]], ...] = (
    # -- oranges
    ("XQ01", "juice", "Juice from Oranges, 1L", "Not-from-concentrate juice pressed from oranges, in a 1 litre carton. Keep chilled.", "Orange", "oranges", 950, ("pressed oranges (100%)",)),
    ("XQ02", "chocolate", "Chocolate with Candied Oranges", "A 70% dark chocolate bar studded with pieces of candied oranges.", "Brown", "oranges", 930, ("cocoa mass", "sugar", "candied oranges (12%)", "cocoa butter")),
    ("XQ03", "tinned", "Mandarin Oranges in Juice", "Segments of mandarin oranges in a light juice, in a 298g tin.", "Orange", "oranges", 910, ("mandarin oranges (60%)", "mandarin juice")),
    ("XQ04", "jam", "Seville Oranges Marmalade", "A thick cut marmalade made with bitter Seville oranges, in a 340g jar.", "Orange", "oranges", 890, ("seville oranges (45%)", "sugar", "lemon juice")),
    # -- lemons
    ("XQ05", "water", "Sicilian Lemons Sparkling Water", "Sparkling spring water flavored with the juice of Sicilian lemons. No sugar.", "Yellow", "lemons", 950, ("carbonated spring water", "lemon juice (1%)", "natural flavoring")),
    ("XQ06", "pickle", "Preserved Lemons in Brine", "Whole lemons preserved in salt and brine, for tagines and dressings. A 350g jar.", "Yellow", "lemons", 920, ("lemons", "salt", "water")),
    ("XQ07", "sweets", "Sherbet Lemons Boiled Sweets", "Boiled sweets with a fizzing sherbet center, in a 200g bag.", "Yellow", "lemons", 900, ("sugar", "glucose syrup", "dried lemon juice", "citric acid")),
    ("XQ08", "biscuit", "Lemons and Ginger Shortbread", "All butter shortbread baked with lemon zest and stem ginger.", "Cream", "lemons", 870, ("wheat flour", "butter", "lemon zest", "stem ginger")),
    # -- limes
    ("XQ09", "water", "Sparkling Mineral Water with Limes", "Sparkling mineral water with a squeeze of limes. No sugar, no sweeteners.", "Green", "limes", 940, ("carbonated mineral water", "lime juice (1%)", "natural flavoring")),
    ("XQ10", "sweets", "Lemons and Limes Boiled Sweets", "Boiled sweets in lemon and lime flavors, in a 200g bag.", "Green", "limes", 910, ("sugar", "glucose syrup", "dried lime juice", "dried lemon juice")),
    ("XQ11", "marinade", "Marinade with Limes and Coriander", "A bottled marinade of limes, coriander and chilli for chicken and fish.", "Green", "limes", 880, ("lime juice (20%)", "coriander", "rapeseed oil", "chilli")),
    # -- apples
    ("XQ12", "juice", "Cloudy Juice from Apples", "A cloudy juice pressed from British apples, in a 1 litre carton.", "Green", "apples", 950, ("pressed apples (100%)",)),
    ("XQ13", "tinned", "Stewed Apples in Syrup", "Stewed apples in a light syrup, in a 385g tin. Warm for crumble or porridge.", "Green", "apples", 920, ("apples (62%)", "water", "sugar")),
    ("XQ14", "cereal_bar", "Apples Cinnamon Oat Bars", "Chewy oat bars with dried apples and cinnamon, in a box of 5.", "Brown", "apples", 890, ("oats", "dried apples (14%)", "honey", "cinnamon")),
    ("XQ15", "cake", "Spiced Apples Crumble Cake", "A crumble-topped sponge baked with spiced apples. Serves 8.", "Brown", "apples", 860, ("wheat flour", "apples (20%)", "butter", "sugar")),
    # -- strawberries
    ("XQ16", "biscuit", "Strawberries and Cream Biscuits", "Sandwich biscuits with a strawberries and cream filling.", "Pink", "strawberries", 950, ("wheat flour", "dried strawberries (3%)", "cream powder", "sugar")),
    ("XQ17", "ice_cream", "Strawberries & Cream Ice Cream", "Creamy vanilla ice cream rippled with strawberry sauce, in a 500ml tub.", "Pink", "strawberries", 930, ("milk", "cream", "strawberries (9%)", "sugar")),
    ("XQ18", "yoghurt", "Strawberries and Cream Yogurt, 4 Pack", "Four pots of creamy yogurt with strawberry puree.", "Pink", "strawberries", 910, ("yogurt", "strawberry puree (8%)", "cream")),
    ("XQ19", "sweets", "Milk Chocolate Covered Strawberries", "Freeze-dried strawberries coated in milk chocolate, in a 120g bag.", "Pink", "strawberries", 880, ("milk chocolate", "freeze-dried strawberries (30%)")),
    # -- raspberries
    ("XQ20", "chocolate", "White Chocolate Raspberries Bar", "A white chocolate bar with pieces of freeze-dried raspberries.", "White", "raspberries", 940, ("sugar", "cocoa butter", "milk powder", "freeze-dried raspberries (6%)")),
    ("XQ21", "biscuit", "Raspberries and Cream Shortbread", "Shortbread biscuits filled with raspberries and cream.", "Pink", "raspberries", 910, ("wheat flour", "butter", "raspberry jam", "cream")),
    ("XQ22", "cereal", "Raspberries and Almond Granola", "Crunchy oat granola with almonds and dried raspberries, in a 500g box.", "Pink", "raspberries", 890, ("oats", "almonds", "dried raspberries (5%)", "honey")),
    ("XQ23", "jam", "Seedless Raspberries Jam, 340g", "A seedless jam made from raspberries, in a 340g jar.", "Red", "raspberries", 860, ("raspberries (50%)", "sugar", "lemon juice")),
    # -- tomatoes
    ("XQ24", "tinned", "Tomatoes in Tomato Juice", "Chopped tomatoes in a thick tomato juice, in a 400g tin.", "Red", "tomatoes", 950, ("tomatoes (70%)", "tomato juice", "acidity regulator")),
    ("XQ25", "pickle", "Sun-Dried Tomatoes in Oil, 270g", "Sun-dried tomatoes in sunflower oil with oregano. A 270g jar.", "Red", "tomatoes", 930, ("sun-dried tomatoes (55%)", "sunflower oil", "oregano")),
    ("XQ26", "pasta_sauce", "Roasted Tomatoes Pasta Sauce", "A pasta sauce of roasted tomatoes, garlic and basil, in a 350g jar.", "Red", "tomatoes", 910, ("tomatoes (80%)", "roasted tomatoes", "garlic", "basil")),
    ("XQ27", "tinned", "Roasted Tomatoes Soup, 400g", "A ready-to-heat soup of roasted tomatoes and basil, in a 400g tin.", "Red", "tomatoes", 880, ("tomatoes (65%)", "roasted tomatoes", "basil", "cream")),
    # -- onions
    ("XQ28", "spice", "Crispy Fried Onions, 100g", "Crispy fried onions for burgers, salads and casseroles. A 100g tub.", "Gold", "onions", 940, ("onions (80%)", "sunflower oil", "wheat flour")),
    ("XQ29", "pickle", "Pickled Onions in Malt Vinegar", "Small onions pickled in malt vinegar, in a 440g jar.", "Cream", "onions", 910, ("pickled onions", "malt vinegar", "salt")),
    ("XQ30", "pickle", "Caramelised Onions Chutney, 290g", "A sweet chutney of slow cooked onions, for cheese and cold meat. A 290g jar.", "Brown", "onions", 880, ("caramelised onions (60%)", "sugar", "vinegar")),
    # -- potatoes
    ("XQ31", "tinned", "New Potatoes in Water, 540g", "Small new potatoes in water, ready to heat. A 540g tin.", "Cream", "potatoes", 940, ("new potatoes (65%)", "water", "salt")),
    ("XQ32", "frozen_veg", "Roast Potatoes in Goose Fat", "Frozen potatoes ready to roast, cooked in goose fat. A 600g bag.", "Gold", "potatoes", 910, ("potatoes (90%)", "goose fat", "salt")),
    ("XQ33", "tinned", "Leeks and Potatoes Soup, 400g", "A smooth soup of leeks and potatoes, in a 400g tin.", "Cream", "potatoes", 880, ("potatoes (30%)", "leeks", "cream", "vegetable stock")),
    # -- carrots
    ("XQ34", "tinned", "Sliced Carrots in Water, 300g", "Sliced carrots in water, in a 300g tin.", "Orange", "carrots", 940, ("carrots (62%)", "water", "salt")),
    ("XQ35", "tinned", "Carrots and Coriander Soup", "A smooth soup of carrots and coriander, in a 400g tin.", "Orange", "carrots", 910, ("carrots (45%)", "coriander", "cream", "vegetable stock")),
    ("XQ36", "spread", "Houmous with Roasted Carrots", "A chilled houmous swirled with roasted carrots and cumin. A 200g pot.", "Orange", "carrots", 880, ("chickpeas", "roasted carrots (14%)", "tahini", "cumin")),
    # -- bananas
    ("XQ37", "juice", "Strawberries and Bananas Smoothie", "A fruit smoothie of strawberries and bananas, in a 750ml carton.", "Pink", "bananas", 940, ("apple juice", "banana puree (20%)", "strawberry puree (18%)")),
    ("XQ38", "cereal_bar", "Bananas and Honey Oat Bars", "Chewy oat bars with dried bananas and honey, in a box of 5.", "Cream", "bananas", 910, ("oats", "dried bananas (12%)", "honey")),
    ("XQ39", "sweets", "Milk Chocolate Covered Bananas", "Dried banana slices coated in milk chocolate, in a 130g bag.", "Brown", "bananas", 880, ("milk chocolate", "dried bananas (35%)")),
    # -- cherries
    ("XQ40", "pickle", "Morello Cherries in Syrup, 425g", "Morello cherries in a light syrup, for baking and desserts. A 425g jar.", "Red", "cherries", 940, ("morello cherries (55%)", "water", "sugar")),
    ("XQ41", "jam", "Black Cherries Conserve, 340g", "A conserve of black cherries, in a 340g jar.", "Red", "cherries", 910, ("black cherries (50%)", "sugar", "lemon juice")),
    ("XQ42", "chocolate_box", "Dark Chocolate Covered Cherries", "Whole cherries in kirsch syrup, covered in dark chocolate. A 150g box.", "Brown", "cherries", 880, ("dark chocolate", "cherries (30%)", "sugar syrup")),
)

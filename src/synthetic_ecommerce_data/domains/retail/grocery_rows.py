"""Grocery families for the retail catalog (gen#154): data only, read by :mod:`grocery`.

A :class:`Family` is one kind of product on one leaf (milk chocolate bars, crisps,
honey). :func:`grocery.build` makes styles from it. A style is a range name and a
brand, plus a subset of the family's flavors (or scents or varieties) and pack sizes.
Its SKUs are flavor x pack.

The shape follows Open Food Facts (ODbL), used only as inspiration: its category
tree, its allergen, trace and label model, and rough distributions. In a bounded
UK sample of chocolate, about half contain milk, about 40% may contain nuts and
most grade E. No name, brand or ingredient list comes from it. Every brand is a
:mod:`house_styles` row.

One category path per product. A family's ``path`` is the retailer's breadcrumb
(``Food & Drink > Fruit & Vegetables > Fresh Fruit > Citrus Fruit > Oranges``) and every
product of the family sits under that one path, never under several, and no other family or row
reaches the same leaf label by another path (gen#330, ``tests/test_one_path_per_leaf_330.py``). Open Food Facts
tags a product with many categories at once: that is a classification, not a store
tree, so only its node NAMES and depth guide the tree here and no multi-valued tag is
copied. The leaf of a bare-noun family (Oranges, Lemons, Apples, Beer's Lager) is what a
"query names a category" policy boosts; the failure classes it must beat are the families
that share only the WORD (a chocolate orange, a beer battered haddock, a ginger beer).

A flavor's ``codes`` are the allergens it contains: P peanuts, T tree nuts,
M milk, G gluten, S soy, E egg, F fish. Two lower-case flags mark animal ingredients:
``h`` is not vegan but is vegetarian (honey, gelatine), and ``x`` is not
vegetarian (meat, fish). A family's ``may`` is a weighted choice of a style's
may-contain codes: the factory's traces.
"""

# ruff: noqa: E501 -- one family's flavors read better on few lines than wrapped (data only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.grocery_families import (
    FAMILIES,
    TIER_BRANDS,  # noqa: F401 -- read through this module
)
from synthetic_ecommerce_data.domains.retail.grocery_model import (
    ALLERGENS,  # noqa: F401 -- read through this module
    DIETARY,  # noqa: F401 -- read through this module
    F,  # noqa: F401 -- read through this module
    Family,  # noqa: F401 -- read through this module
)

OWNERS = {
    "Pantry Mill": "own", "Hearth & Table": "own", "Barrowby Kitchen": "own",
    "Crunchworth": "third_party", "Wheatsheaf Lane": "third_party",
    "Crofter's Bakehouse": "third_party", "Goldfield Farms": "third_party",
    "Meadowgate Dairy": "third_party", "Mossgill Dairy": "third_party",
    "Olivar Grove": "third_party", "Copper Hill Preserves": "third_party",
    "Kettleby Tea Co.": "third_party", "Brewhollow Roasters": "third_party",
    "Vine & Valley": "third_party", "Freshfold": "third_party",
    "Clearbrook Household": "third_party", "Soapwell": "third_party",
    "Brightwater Botanics": "third_party", "Velling Apothecary": "third_party",
    "Orrin Skin": "third_party",
    "Hollowbrook Cellars": "third_party", "Stonepine Estate": "third_party",
    "Orchardgate Cider Co.": "third_party",
    # The 50K tier's new brands (gen#376).
    "Marlpit Growers": "third_party",
    "Heronsgate Fresh": "third_party",
    "Tamsworth Cellars": "third_party",
    "Ovenden Vineyards": "third_party",
    "Plumtree Larder": "third_party",
    "Saltmarsh Preserves": "third_party",
    "Hobsworth Kitchen": "third_party",
    "Brindlemere Drinks": "third_party",
    "Thistlemoor Snacks": "third_party",
    "Pellam Crisps": "third_party",
    "Dellwick Chocolatiers": "third_party",
    "Honeysett Sweets": "third_party",
    "Wetherly Creamery": "third_party",
    "Larchfield Home Care": "third_party",
    "Dunnock Bakehouse": "third_party",
    "Cobbleby Kitchen": "third_party",
    "Wyncote Skin": "third_party",
    "Ledwick Botanics": "third_party",
    "Oakenshaw Mills": "third_party",
    "Pippinfold Cider Co.": "third_party",
    "Marrowdale Tea Co.": "third_party",
    "Fellbeck Roasters": "third_party",
}  # fmt: skip

#: Range names: invented place words, the head of a style's title.
LINES = (
    "Ashcombe", "Brackley", "Corrow", "Dunmere", "Elstow", "Fallowfield", "Garrick",
    "Harlow Bay", "Ingleby", "Juniper Row", "Kelmscott", "Linthorpe", "Marbury",
    "Netherby", "Oakhurst", "Pennine", "Quarry Hill", "Rydal", "Stanwick", "Tarnside",
    "Upwood", "Varley", "Wexcombe", "Yarrow", "Amberley", "Bellingham", "Coldstream",
    "Deepdale", "Eskdale", "Fernhill", "Greyfriars", "Hartside", "Ivybridge",
    "Kingsmead", "Larkrise", "Millbrook", "Northcote", "Orchard Lane", "Priory",
    "Redbrook", "Silverdale", "Thornbury", "Underhill", "Wansford", "Whitmore",
    "Alderley", "Birchfield", "Cranmore", "Dovedale", "Edgecote",
)  # fmt: skip

#: The 50K tier's extra range names (gen#376): invented place words, drawn after :data:`LINES`.
TIER_LINES: tuple[str, ...] = (
    "Abbeyford", "Ainthorpe", "Aldwick", "Applegarth", "Arkholme", "Ashdown", "Aspley", "Astwood",
    "Attleby", "Aysgarth", "Badsworth", "Balderton", "Bamford", "Barnoldby", "Barrowdale",
    "Bathgate", "Beckwith", "Bellerby", "Bentham", "Bescar", "Bickerdale", "Birkdale",
    "Blackmoor", "Bleasby", "Bowerchalke", "Bradbourne", "Braithby", "Bramhope", "Brandesby",
    "Brayton", "Bridgemere", "Brindley", "Broadmead", "Brockhall", "Brockley", "Broxholme",
    "Buckden", "Burnsall", "Butterwick", "Caldbeck", "Calderbrook", "Calverley", "Carlton",
    "Castlerigg", "Catterick", "Chalford", "Charnwood", "Chelmsley", "Cheswold", "Chilcombe",
    "Clanfield", "Claybrooke", "Cleeve", "Clifton", "Coldharbour", "Colwall", "Copthorne",
    "Cornforth", "Cowdale", "Crakehall", "Cressbrook", "Crowle", "Croxdale", "Cuddesdon", "Dalby",
    "Danesmoor", "Darrowby", "Daventry", "Denholme", "Dentdale", "Dewsbury", "Dinnington",
    "Dowsby", "Drayton", "Duddon", "Dunsmore", "Dunstall", "Durrington", "Eastry", "Ebbesbourne",
    "Eccleshall", "Edenbridge", "Elmstead", "Elvaston", "Embleton", "Eppleby", "Esholt",
    "Etherow", "Evenwood", "Exford", "Fairfield", "Falstone", "Farndale", "Fenwick", "Fernilee",
    "Finchale", "Flaxton", "Foxholes", "Framlingham", "Frensham", "Fulbeck", "Fylingdale",
    "Gadbrook", "Gamblesby", "Garsdale", "Gaydon", "Gisburn", "Glaston", "Goathland",
    "Goldsborough", "Grafton", "Grassington", "Greenhow", "Grinton", "Gunnerside", "Hackness",
    "Haddenham", "Halsham", "Hambleton", "Hampsthwaite", "Hanbury", "Hardwick", "Harewood",
    "Hartington", "Haxby", "Hazelwood", "Heathfield", "Helmsley", "Hepworth", "Hesketh",
    "Highfold", "Hinderwell", "Holbeck", "Holmfirth", "Hornby", "Hovingham", "Hubberholme",
    "Hunmanby", "Ingbirchworth", "Ingleton", "Ireby", "Jervaulx", "Kearby", "Kelbrook",
    "Kettlewell", "Kexby", "Kilburn", "Knaresdale", "Lambley", "Langdale", "Lastingham",
    "Lealholm", "Ledsham", "Levisham", "Lindley", "Litton", "Longtown", "Lothersdale", "Lowick",
    "Lydgate", "Malham", "Mallerstang", "Marske", "Mickleby", "Middleham", "Milnthorpe",
    "Monkton", "Moorsholm", "Morland", "Mossdale", "Muker", "Nettlebed", "Newbiggin",
    "Nidderdale", "Norbury", "Nunnington", "Oakworth", "Offerton", "Oldstead", "Orgreave",
    "Osmotherley", "Oswaldkirk", "Otterburn", "Oulton", "Pateley", "Peasholm", "Pilsley",
    "Pinchbeck", "Pocklington", "Prestbury", "Quernmore", "Raskelf", "Ravenstonedale",
    "Rawcliffe", "Reeth", "Ribblehead", "Rosedale", "Rothbury", "Rudston", "Rushton", "Ryedale",
    "Saltaire", "Sawley", "Scarcroft", "Sedbergh", "Shap", "Sherburn", "Shipton", "Skelwith",
    "Skidby", "Slaidburn", "Snaizeholme", "Sowerby", "Spofforth", "Staveley", "Stokesley",
    "Swaledale", "Tanfield", "Thoralby", "Threshfield", "Thurlby", "Thwaite", "Tickhill",
    "Tideswell", "Towton", "Ulverston", "Upsall", "Walkington", "Wasdale", "Wath", "Weardale",
    "Wharram", "Wigglesworth", "Winster", "Wolsingham", "Woolley", "Wragby", "Wykeham", "Yealand",
    "Yockenthwaite", "Youlgrave", "Zouch",
)  # fmt: skip

#: A beef cut's own description sentence, by (family code, flavor name): what the cut is and how
#: it cooks, so the six cuts do not share one template (gen#269). Words the SKUs do not carry
#: (a weight, a price) stay out.
CUT_NOTES = {
    ("SKS", "Sirloin Steak"): "A lean cut from the back with a thin edge of fat, best seared hot and left to rest.",
    ("SKR", "Ribeye Steak"): "A well marbled cut from the rib that stays juicy, cooked quickly in a hot pan or on the grill.",
    ("SKF", "Fillet Steak"): "The most tender cut, from the tenderloin, with a mild flavour; cook it briefly and rare to medium.",
    ("SKU", "Rump Steak"): "A full flavoured cut from the hindquarter with a firm bite, good marinated and sliced across the grain.",
    ("SKC", "Chuck Steak"): "A richly flavoured cut from the shoulder with connective tissue, best braised slowly or cooked low and long.",
    ("SKT", "T-Bone Steak"): "A cut across the loin with the bone between a strip and a small fillet, grilled hot for a crust.",
    ("SKL", "Flank Steak"): "A lean, long-grained cut from the belly muscle, marinated, seared quickly and sliced thinly across the grain.",
    ("SKW", "Skirt Steak"): "A thin, beefy cut from the diaphragm with a loose grain, cooked fast over a high heat for fajitas.",
}

#: One authored sentence per food product type, "{name}" the style's one flavor or variety: what the
#: product is and what it is for, in place of the old "Name, in 400g, 800g." field dump (gen#449).
#: A beef cut adds its own :data:`CUT_NOTES` line after it.
INTRO = {
    "Chocolate Bar": "{name}, a chocolate treat to snap or share.",
    "Chocolate Box": "{name}, a box of chocolates to share or give as a gift.",
    "Sweets": "{name}, a bag of sweets to share.",
    "Biscuits": "{name}, a biscuit to dunk in a cup of tea.",
    "Crisps": "{name} crisps, thin and crunchy for sharing or snacking.",
    "Nuts & Popcorn": "{name}, a snack to share or keep for later.",
    "Cereal Bar": "{name}, a cereal bar for breakfast on the go.",
    "Cereal": "{name}, a breakfast cereal to pour into a bowl with milk.",
    "Porridge": "{name}, porridge oats cooked on the hob or in the microwave.",
    "Bread": "{name}, a loaf baked for toast and sandwiches.",
    "Cake": "{name} cake, baked to share with a cup of tea.",
    "Milk": "{name} milk, for tea, coffee, cereal and cooking.",
    "Plant Milk": "{name} drink, a dairy free alternative to milk.",
    "Yogurt": "{name} yogurt, a pot for breakfast or dessert.",
    "Butter & Spreads": "{name}, for toast, baking and cooking.",
    "Cheese": "{name}, a cheese to slice, grate or serve on a board.",
    "Ready Meal": "{name}, a ready meal to heat through and serve.",
    "Pizza": "{name} pizza, ready to bake for lunch or supper.",
    "Ice Cream": "{name}, a frozen dessert to scoop from the tub.",
    "Frozen Vegetables": "{name}, frozen vegetables to cook straight from the bag.",
    "Tinned Food": "{name}, a tinned staple for the store cupboard.",
    "Pasta": "{name}, dried pasta that cooks in minutes.",
    "Rice & Grains": "{name}, a grain for side dishes and one-pot meals.",
    "Sauce": "{name}, a sauce to cook with or serve at the table.",
    "Jam": "{name}, a spread for toast, scones and baking.",
    "Honey": "{name}, honey for toast, tea and baking.",
    "Spread": "{name}, a spread for toast, sandwiches and baking.",
    "World Food": "{name}, an ingredient for cooking dishes from around the world.",
    "Tea": "{name} tea bags for brewing a hot cup.",
    "Coffee": "{name} coffee, to make a hot cup at home.",
    "Soft Drink": "{name}, a soft drink best served chilled.",
    "Juice": "{name}, a refreshing drink to serve chilled.",
    "Baby Food": "{name}, food made for babies and young children.",
    "Free From Snack": "{name}, a free from snack for the lunchbox.",
    "Fresh Fruit": "Fresh {name}, ready to eat or to cook with.",
    "Fresh Vegetables": "Fresh {name}, packed for the kitchen.",
    "Meat": "{name}, trimmed and packed fresh in a sealed tray.",
    "Fish": "{name}, fish packed ready to cook or serve.",
    "Beer": "{name}, a beer best served cold.",
    "Battered Fish": "{name}, fish in a crisp batter to bake from frozen.",
    "Vinegar": "{name}, for dressings, pickling and cooking.",
    "Festive Bake": "{name}, a festive bake for the Christmas table.",
    "Hot Chocolate": "{name}, a powder to stir into hot milk.",
    "Wine": "A bottle of {name}, for pouring with a meal.",
    "Champagne": "A bottle of {name}, for a celebration.",
    "Cider": "{name}, a cider best served cold over ice.",
    "Whisky": "A bottle of {name}, to sip neat or over ice.",
    "Gin": "A bottle of {name}, for a gin and tonic or a cocktail.",
    "Vodka": "A bottle of {name}, to mix or serve chilled.",
    "Rum": "A bottle of {name}, to sip or to mix in a cocktail.",
    "Tequila": "A bottle of {name}, to sip or to mix in a margarita.",
    "Fortified Wine": "A bottle of {name}, a fortified wine to sip or to cook with.",
    "Perry": "{name}, a perry made from pears and best served cold.",
    "Mead": "{name}, a honey wine to sip or to warm.",
    "Seasoning": "{name}, a seasoning to rub or sprinkle on meat before cooking.",
}
#: The opening sentence of a style that carries several flavors (``per_style`` above one, or an
#: anchor that lists several): it
#: names no flavor, an "Includes A and B." sentence lists them.
INTRO_MULTI = {
    "Chocolate Bar": "Chocolate bars to snap and share.",
    "Milk": "Milk for tea, coffee, cereal and cooking.",
    "Sweets": "Sweets to share from the bag.",
    "Biscuits": "Biscuits to dunk in a cup of tea.",
    "Crisps": "Thin, crunchy crisps for sharing or snacking.",
    "Cereal Bar": "Cereal bars for breakfast on the go.",
    "Yogurt": "Yogurt pots for breakfast or dessert.",
    "Pizza": "Pizzas ready to bake for lunch or supper.",
    "Ice Cream": "Ice cream to scoop from the tub.",
    "Tea": "Tea bags for brewing a hot cup.",
    "Soft Drink": "Soft drinks best served chilled.",
}


#: A family that stocks more sizes across its range than any one style sells (gen#347): the
#: packs a style carries. Each style takes this many of the family's packs, the window moving
#: one pack per style, so a shop's range spans every size and each style stays what it was
#: (its SKU count, so the family's styles, flavors and draws). Sparkling wine sells one size
#: per style: a piccolo, a bottle or a magnum.
PACKS_PER_STYLE: dict[str, int] = {
    **dict.fromkeys(("PLM", "ICE", "SAU", "JUI", "DSH", "GLS", "LDY", "HWS", "SSA", "GJU", "BFR", "VIN", "CLN", "BOD", "FLR", "BTH", "SGL", "WRD", "WWH", "WRS", "WCH", "HCR", "ECR", "SWH", "SGN", "SVD", "SRM", "STQ", "FPT", "FSY", "FVM", "MED", "FTC", "BCR"), 2),
    "WSP": 1,
}

#: The styles every build plants first, so each demo case exists at any size:
#: (family, the flavors it carries, its may-contain codes).
ANCHORS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("CHB", ("Peanut Caramel", "Milk"), ""),  # contains peanuts
    ("CHB", ("Milk", "Dark 70%"), "PT"),  # may contain peanuts
    ("CHB", ("Dark 70%", "Mint Dark", "Orange Dark", "Coconut Dark"), ""),  # vegan, nut free
    ("CHB", ("Milk", "Salted Caramel Milk", "White"), ""),  # milk chocolate, nut free
    ("LEM", ("Unwaxed Lemons",), ""),
    ("ORA", ("Oranges",), ""),
    ("ORA", ("Blood Oranges",), ""),
    ("ORA", ("Orange Segments",), ""),
    ("ORA", ("Easy Peelers",), ""),
    ("APP", ("Gala Apples",), ""),
    ("BLG", ("Premium Lager",), ""),
    ("BSO", ("Tropical Pineapple Sour Beer",), ""),
    ("BAF", ("Alcohol Free Lager",), ""),
    ("GNB", ("Ginger Beer",), ""),
    ("BBF", ("Beer Battered Scottish Haddock",), ""),
    ("BBF", ("Beer Battered Cod Fillets",), ""),
    ("VIN", ("Cider Vinegar",), ""),
    ("WGM", ("Wine Gums",), ""),
    ("CHO", ("Milk Chocolate Orange",), ""),
    ("PAN", ("Cranberry & Orange Panettone",), ""),
    ("ORB", ("Orange Shortbread",), ""),
    ("ORB", ("Chocolate & Orange Cookies",), ""),
    ("HOT", ("Orange Drinking Chocolate",), ""),
    ("HON", ("Clear Honey",), ""),
    ("JAM", ("Lemon Curd",), ""),
    ("JUI", ("Smooth Orange",), ""),
    ("TIN", ("Coconut Milk",), ""),
    ("MLK", ("Whole", "Semi Skimmed"), ""),
    ("CLN", ("Lemon",), ""),
    ("CLN", ("Orange",), ""),
    ("CLN", ("Mint",), ""),
    ("BOD", ("Honey",), ""),
    ("BOD", ("Coconut",), ""),
)


#: The text-match decoys of the grocery build (gen#294), planted after :data:`ANCHORS` from the
#: depth stream (so no core family's draw moves): (family, its flavors, may-contain codes, the
#: range-name offset). Two ranges per peanut-in-title flavor, so a title and a brand repeat nowhere.
DECOY_ANCHORS: tuple[tuple[str, tuple[str, ...], str, int], ...] = (
    *(("PNT", (f.name,), "", 60 + 7 * k + j) for j in range(2) for k, f in enumerate(
        next(f for f in FAMILIES if f.code == "PNT").flavors)),
    *(("PNH", (f.name,), "", 90 + 5 * k + j) for j in range(2) for k, f in enumerate(
        next(f for f in FAMILIES if f.code == "PNH").flavors)),
    *(("PNF", (f.name,), "", 120 + 5 * k) for k, f in enumerate(
        next(f for f in FAMILIES if f.code == "PNF").flavors)),
)

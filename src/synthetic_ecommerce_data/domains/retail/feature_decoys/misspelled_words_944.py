"""Products whose brand or product name is a common misspelling (gen#944, gen#1130).

The retail-and-industrial demo shows the spelling suggestion: a search that finds the literal
word serves its hits, and offers "You may also consider searching for <common spelling>" only
when it has 3 or fewer Best results (the Engine's ``did_you_mean_head_hit_threshold``) and the
common spelling is at least 5 times more common. For the demo to show both sides, three words
here are on 3 products (the hits and the suggestion show) and two on 7 to 10 (hits only):

==========  ========  ===============  ===================================
Word        Products  Common spelling  The demo shows
==========  ========  ===============  ===================================
choocolate  3         chocolate        the hits and the suggestion
bannana     3         banana           the hits and the suggestion
pliars      3         pliers           the hits and the suggestion
leggins     8         leggings         hits only
cardigen    8         cardigan         hits only
==========  ========  ===============  ===================================

gen#1130: a misspelling is a deliberate brand or product name, a pun a real company might choose,
never a misspelled generic word in an ordinary product's title ("Big Bannana Bunch" read as a
data error). The shopper who types it knows the brand: ``Choo-Choocolate Express`` (chocolate
train gift boxes and a wooden train set), ``Bannana Bros`` gummy sweets and the Bannana Brothers
Crazy Apes board game, Pliars, a bluffing party card game (pliers and liars) that replaced
#944's three industrial "Conduit Pliars", the ``Leggins & Co`` fashion label's eight leggings, and
``Cardigen``, a deck-building trading card game (cards and generations) of eight products in Card
Games, far from knitwear. No category node, product type or attribute holds a misspelling, so no
vocabulary or category name learns one; each product is drawn by its own kit (a gift box, a
wooden train, a sweets bag, a board-game box, a card-game tuck box, leggings, and Cardigen's
``trading_cards`` packs, display box, decks, sleeves and deck box).
``tests/test_retail_misspelled_words_944.py`` counts each word's products and checks the rules.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    misspelled_brands,  # noqa: F401 -- owners and house styles
)
from synthetic_ecommerce_data.domains.retail.decoy_kind import Kind

_UK = ("6", "8", "10", "12", "14", "16")

#: misspelling -> (the common spelling, how many products carry it).
WORDS = {
    "choocolate": ("chocolate", 3),
    "bannana": ("banana", 3),
    "leggins": ("leggings", 8),
    "cardigen": ("cardigan", 8),
}

#: The true types, each a real type in its own category.
KINDS = {
    "ms944_choc_box": Kind("Food & Drink", ("Food & Drink", "Chocolate & Sweets", "Chocolate", "Chocolate Boxes"), "Chocolate Box",
                           "box", "Hearth & Table", 9.5, colorless=True),
    "ms944_train": Kind("Toys", ("Toys", "Baby & Toddler", "Wooden Toys"), "Wooden Toy", "wooden_toy", "Little Fernby", 22.0, "kids",
                        params=(("kind", "train"), ("counts", "1,2,6")),
                        extra=(("toy_type", "Toy type", "Train Set"), ("age_range", "Age range", "3+ years"),
                               ("material", "Material", "Wooden"), ("fsc_certified", "FSC certified", "Yes"))),
    "ms944_sweets": Kind("Food & Drink", ("Food & Drink", "Chocolate & Sweets", "Sweets"), "Sweets", "bag", "Pantry Mill", 1.8,
                         colorless=True),
    "ms944_board_game": Kind("Toys", ("Toys", "Games", "Board Games"), "Board Game", "board_game", "Little Fernby", 20.0, "kids",
                             params=(("kind", "family"), ("theme", "Crazy Apes")),
                             extra=(("toy_type", "Toy type", "Family Board Game"), ("age_range", "Age range", "6+ years")),
                             colorless=True),
    "ms944_card_game": Kind("Toys", ("Toys", "Games", "Card Games"), "Card Game", "card_game", "Little Fernby", 12.0, "kids",
                            params=(("kind", "party"),),
                            extra=(("toy_type", "Toy type", "Party Card Game"), ("age_range", "Age range", "10+ years")),
                            colorless=True),
    **{
        f"ms944_leggings{key}": Kind("Clothing", ("Womens", "Leggings"), "Leggings", "leggings", "Larkmoor", 18.0, sizes=_UK,
                                     size_range="regular", params=params)
        for key, params in (
            ("", (("length", "full"), ("rise", "high"))),
            ("_pocket", (("length", "full"), ("rise", "high"), ("pocket", "yes"))),
            ("_78", (("length", "7_8"), ("rise", "high"))),
            ("_cropped", (("length", "cropped"), ("rise", "mid"))),
        )
    },
    **{
        f"ms944_tcg_{form if not theme else theme.split()[-1].lower()}": Kind(
            "Toys", ("Toys", "Games", "Card Games"), "Card Game", "trading_cards", "Little Fernby", price, "kids",
            params=(("form", form), *((("theme", theme),) if theme else ())),
            extra=(("toy_type", "Toy type", toy_type), ("age_range", "Age range", "8+ years"),
                   *((("theme", "Theme", theme),) if theme else ())),
            colorless=True)
        for form, theme, toy_type, price in (
            ("starter_deck", "", "Trading Card Game", 12.0),
            ("booster_pack", "", "Trading Card Game", 4.0),
            ("booster_box", "", "Trading Card Game", 90.0),
            ("expansion", "Dragons", "Trading Card Game", 14.0),
            ("expansion", "Deep Space", "Trading Card Game", 14.0),
            ("battle_set", "", "Trading Card Game", 25.0),
            ("sleeves", "", "Card Sleeves", 7.0),
            ("deck_box", "", "Deck Box", 9.0),
        )
    },
}  # fmt: skip

_CE, _BB, _LC, _CG = misspelled_brands.BRANDS

#: Rows of (number, kind, title, description, color, the misspelling, brand or None for the kind's).
_ROWS = (
    # choocolate: 3 products of the Choo-Choocolate Express brand, two gift boxes and a toy train
    (9441, "ms944_choc_box", "Choo-Choocolate Express Milk Chocolate Train Gift Box", "A milk chocolate engine and three carriages on a track of chocolate, in a gift box.", "Brown", "choocolate", _CE),
    (9442, "ms944_choc_box", "Choo-Choocolate Express Dark Chocolate Train Gift Box", "A dark chocolate engine, a coal truck of chocolate buttons and two carriages, in a gift box.", "Brown", "choocolate", _CE),
    (9443, "ms944_train", "Choo-Choocolate Express Wooden Train Set", "A wooden engine, two carriages and six pieces of track, painted chocolate brown and cream. For ages 3 and up.", "Brown", "choocolate", _CE),
    # bannana: 3 products, the Bannana Bros sweets and the Bannana Brothers board game
    (9444, "ms944_sweets", "Bannana Bros Gummy Sweets", "Banana flavor gummy sweets shaped like little bananas, in a 150g bag.", "Yellow", "bannana", _BB),
    (9445, "ms944_sweets", "Bannana Bros Sour Gummy Sweets", "Sour banana and lime gummy sweets, dusted in sugar, in a 150g bag.", "Green", "bannana", _BB),
    (9446, "ms944_board_game", "Bannana Brothers Crazy Apes Board Game", "Race your ape up the jungle tree, swing past the snakes and grab the bunch at the top. A family game for 2 to 4 players that takes about 20 minutes. For ages 6 and up.", "Yellow", "bannana", None),
    # pliars: 3 products of Pliars, the bluffing party card game (pliers and liars)
    (9463, "ms944_card_game", "Pliars Bluffing Party Card Game", "Play a card face down and say what it is: the table calls your bluff or lets it go. A party game for 3 to 8 players that takes about 20 minutes. For ages 10 and up.", "Red", "pliars", None),
    (9464, "ms944_card_game", "Pliars Big Fibs Expansion Pack", "Sixty new cards for Pliars, with wild cards and double bluffs. Needs the Pliars base game.", "Blue", "pliars", None),
    (9465, "ms944_card_game", "Pliars Travel Edition", "Pliars in a pocket-sized tin: the bluffing party game for trains, planes and holidays.", "Green", "pliars", None),
    # leggins: 8 leggings of the Leggins & Co fashion label, the word only in the brand
    (9447, "ms944_leggings", "Leggins & Co High-Rise Leggings", "Full length leggings with a high, wide waistband.", "Black", "leggins", _LC),
    (9448, "ms944_leggings", "Leggins & Co Yoga Leggings", "Soft stretch leggings for yoga and the studio.", "Navy", "leggins", _LC),
    (9449, "ms944_leggings", "Leggins & Co Ribbed Leggings", "Ribbed jersey leggings with a high waist.", "Grey", "leggins", _LC),
    (9450, "ms944_leggings_pocket", "Leggins & Co Gym Leggings with Pockets", "Squat-proof full length leggings with a high waistband and a side pocket on each leg.", "Black", "leggins", _LC),
    (9451, "ms944_leggings_78", "Leggins & Co Seamless 7/8 Leggings", "Seamless knit leggings that stop just above the ankle.", "Blue", "leggins", _LC),
    (9452, "ms944_leggings", "Leggins & Co Everyday Stretch Leggings", "Cotton stretch leggings for every day.", "Grey", "leggins", _LC),
    (9453, "ms944_leggings_cropped", "Leggins & Co Cropped Lounge Leggings", "Brushed jersey leggings that stop at mid calf, for the sofa.", "Pink", "leggins", _LC),
    (9454, "ms944_leggings", "Leggins & Co Thermal Running Leggings", "Brushed-back running leggings with a high waistband, for cold mornings.", "Black", "leggins", _LC),
    # cardigen: 8 products of Cardigen, the deck-building trading card game (cards and generations)
    (9455, "ms944_tcg_starter_deck", "Cardigen Starter Deck", "A ready-to-play deck of 60 cards, a rules guide and a fold-out play mat: the way into the Cardigen deck-building trading card game. For 2 players, ages 8 and up.", "Purple", "cardigen", _CG),
    (9456, "ms944_tcg_booster_pack", "Cardigen Booster Pack", "Ten random Cardigen cards in a sealed foil pack, one of them rare or better, to grow your deck.", "Purple", "cardigen", _CG),
    (9457, "ms944_tcg_booster_box", "Cardigen Booster Box", "A display box of 36 sealed Cardigen booster packs, for a league night or a big trade.", "Purple", "cardigen", _CG),
    (9458, "ms944_tcg_dragons", "Cardigen Expansion: Dragons", "Sixty new cards of fire-breathing dragons and the hoards they guard. Needs a Cardigen starter deck to play.", "Red", "cardigen", _CG),
    (9459, "ms944_tcg_space", "Cardigen Expansion: Deep Space", "Sixty new cards of starships, comets and far-off moons. Needs a Cardigen starter deck to play.", "Blue", "cardigen", _CG),
    (9460, "ms944_tcg_battle_set", "Cardigen Two-Player Battle Set", "Two ready-to-play decks, two play mats and a rules guide: all two players need to start a Cardigen duel.", "Purple", "cardigen", _CG),
    (9461, "ms944_tcg_sleeves", "Cardigen Card Sleeves (100 pack)", "One hundred clear card sleeves that keep your Cardigen cards safe in play and in trade.", "Clear", "cardigen", _CG),
    (9462, "ms944_tcg_deck_box", "Cardigen Deck Box", "A hard deck box with a magnetic flip lid that holds a sleeved deck of up to 80 cards.", "Black", "cardigen", _CG),
)  # fmt: skip


def word_rows(d):
    """The rows, made with the class-8 table's row maker. No row is a decoy, so none names a
    query, a noun or a fixing policy, and the decoy contract (:mod:`decoy_contract`) skips them."""
    rows = []
    for n, kind, title, desc, color, _word, brand in _ROWS:
        own = {"brand": brand} if brand else {}
        rows.append(d(n, kind, title, desc, color, "", "", "", decoy=False, **own))
    return tuple(rows)


def product_ids() -> frozenset[str]:
    """The product ids of the rows (``PLT-DY<number>``)."""
    return frozenset(f"PLT-DY{n:02d}" for n, *_ in _ROWS)

"""Text-match decoys of "blood red dress" (gen#540, the rule of #294 on the set shape of #538).

"Blood red" is a real shade name, and "blood orange" is a fruit, a scent and a jam. A shopper who
types ``blood red dress`` should get the five red dresses called "Blood Red ..." first (they are
true hits, and rank first on the words alone) and then a field of products whose TITLE holds the
words and whose fields say they are not a red dress. Each keeps its structured fields true
(category, product type, drawing, color), so only the text misleads and only an interpreting
search can tell them from the dresses.

(a) A dress that is not red: black, with blood red roses on it (class 1, a print names the color).
(b) Not a dress, with "dress" in the name: a dress shirt, dress socks, dress hangers (class 2).
(c) Not a dress, with the shade or the fruit as the name: a lipstick, a candle, a shower gel, a
    marmalade, a juice (classes 2 and 4). "Blood orange" shares the rare word "blood".

The five dresses sit in five leaves of Womens > Dresses; every decoy sits in a department the
catalog already has. ``tests/test_retail_text_match_decoys_294.py`` pins the ranking and the
counts, and ``tests/test_feature_decoys_513.py`` holds the contract for the file.
"""

from __future__ import annotations

from decoy_kind import Kind

_UK = ("6", "8", "10", "12", "14", "16")
_WD = ("Womens", "Dresses")

#: The true type of each row: five dresses (the true hits and a black one), then the others.
KINDS = {
    "br_midi": Kind("Clothing", (*_WD, "Midi Dresses"), "Dress", "dress", "Larkmoor", 45.0,
                    sizes=_UK, size_range="regular",
                    params=(("neckline", "boat"),)),
    "br_slip": Kind("Clothing", (*_WD, "Slip Dresses"), "Dress", "dress", "Larkmoor", 39.0,
                    sizes=_UK, size_range="regular", params=(("neckline", "cowl"),)),
    "br_wrap": Kind("Clothing", (*_WD, "Wrap Dresses"), "Dress", "dress", "Harbour & Pine", 34.0,
                    sizes=_UK, size_range="regular", params=(("neckline", "v_neck"),)),
    "br_maxi": Kind("Clothing", (*_WD, "Maxi Dresses"), "Dress", "dress", "Harbour & Pine", 48.0,
                    sizes=_UK, size_range="regular", params=(("neckline", "halter"),)),
    "br_lipstick": Kind("Beauty", ("Beauty", "Make-Up", "Lips", "Lipstick"), "Lipstick",
                        "lipstick", "Kestlewood Cosmetics", 14.0),
    "br_mens_shirt": Kind("Clothing", ("Mens", "Tops", "Shirts", "Formal Shirts"), "Shirt",
                          "blouse", "Wrenfield", 24.0, sizes=("S", "M", "L", "XL", "XXL"),
                          size_range="regular"),
}  # fmt: skip

#: Rows of (code, kind, title, description, color, class, sold). The first five are the true
#: hits (class 0); the kind of a decoy may be one of another module or of ``decoy_rows``.
_HITS = (
    ("BLR01", "br_midi", "Blood Red Boat Neck Midi Dress",
     "A midi dress in a deep blood red crepe, with a boat neck and a fitted waist.",
     "Red", 960),
    ("BLR02", "br_slip", "Blood Red Satin Slip Dress",
     "A bias cut satin slip dress in blood red, with a cowl neck and thin straps.", "Red", 940),
    ("BLR03", "br_wrap", "Blood Red Jersey Wrap Dress",
     "A soft jersey wrap dress in blood red, tied at the waist, to the knee.", "Red", 920),
    ("BLR04", "br_maxi", "Blood Red Halter Neck Maxi Dress",
     "A floor length maxi dress in blood red, with a halter neck and an open back.", "Red", 900),
    ("BLR05", "shirt_dress", "Blood Red Belted Shirt Dress",
     "A cotton shirt dress in blood red, with a collar, a button front and a self belt.",
     "Red", 880),
)  # fmt: skip

_DECOYS = (
    # (a) a dress that is not red: the blood red is a print on it.
    ("BLR06", "br_midi", "Black Midi Dress with Blood Red Roses",
     "A black crepe midi dress printed with blood red roses; the dress is black.", "Black", 1, 700),
    # (b) not a dress: "dress" is the name of the thing, or what it is worn with.
    ("BLR07", "br_mens_shirt", "Blood Red Dress Shirt, Slim Fit",
     "A mens poplin dress shirt in blood red, with a cutaway collar and a slim fit.",
     "Red", 2, 560),
    ("BLR08", "socks_m", "Blood Red Dress Socks, 5 Pack",
     "Five pairs of fine knit mens dress socks in blood red, for a suit.", "Red", 2, 520),
    ("BLR09", "hanger", "Blood Red Dress Hangers, Pack of 10",
     "Ten blood red velvet hangers with a notch, made to hold a dress by the shoulder.",
     "Red", 2, 600),
    # (c) the shade or the fruit as the name of something else.
    ("BLR10", "br_lipstick", "Blood Red Satin Lipstick",
     "A creamy satin lipstick in the shade Blood Red, in a slim bullet.", "Red", 2, 780),
    ("BLR11", "fruit_candle", "Blood Orange Scented Candle",
     "A soy wax candle scented with blood orange, in a glass jar. Burns for about 30 hours.",
     "Orange", 4, 740),
    ("BLR12", "shower_gel", "Blood Orange Shower Gel, 250ml",
     "A shower gel scented with blood orange, in a 250ml bottle.", "Orange", 4, 700),
    ("BLR13", "jam", "Blood Orange Marmalade, 340g",
     "A thin cut marmalade made with blood oranges, in a 340g jar.", "Orange", 2, 660),
    ("BLR14", "juice", "Blood Orange Juice, 1L",
     "A juice pressed from blood oranges, in a 1 litre carton. Keep chilled.", "Orange", 2, 640),
)  # fmt: skip


def decoy_rows(d):
    hits = tuple(
        d(code, kind, title, desc, color, 0, "blood red dress", sold, true_hit=True)
        for code, kind, title, desc, color, sold in _HITS
    )
    scent = {"BLR11": "Blood Orange", "BLR12": "Blood Orange"}
    decoys = tuple(
        d(code, kind, title, desc, color, cls, "blood red dress", sold, scent=scent.get(code))
        for code, kind, title, desc, color, cls, sold in _DECOYS
    )
    return hits + decoys

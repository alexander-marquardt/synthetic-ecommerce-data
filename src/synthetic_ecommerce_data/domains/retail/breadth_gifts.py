"""The breadth rows of the Gifts department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

# --------------------------------------------------------------------------
# Gifts: the frame, the paper, the charm or the decoration is drawn.
# --------------------------------------------------------------------------

_FRAMES = ("Gifts", "Keepsakes", "Photo Frames")
_WRAP = ("Gifts", "Gift Wrap", "Wrapping Paper")
_CHARM = ("Gifts", "Keepsakes", "Charm Keyrings")
_DECOR = ("Gifts", "Christmas Gifts", "Tree Decorations")
_CANDLE = ("Gifts", "Home Fragrance", "Scented Candles")


def _occ(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("occasion", "Occasion", v),)


def _charm(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("charm", "Charm", v),)


def _scent(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("scent", "Scent", v),)


_SILVER, _OAK = cw("Silver", "#c0c0c0"), cw("Oak", "#b08a5a")

GIFTS = (
    Row("FRMSLV", "Silver-Plated Wedding Photo Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 22.0, "photo_frame",
        "An engraved frame for a 5 x 7 in photo, with a velvet back and a fold-out stand.",
        (_SILVER,), _occ("Wedding"), (("5 x 7 in", 22.0), ("8 x 10 in", 32.0))),
    Row("FRMOAK", "Solid Oak New Baby Photo Frame", "Lanternby", "Gifts", _FRAMES,
        "Photo Frame", 18.0, "photo_frame",
        "A deep oak frame with a cream mount and a printed message, gift boxed.",
        (_OAK, cw("White", "#ffffff")), _occ("New Baby")),
    Row("FRMGLS", "Glass Anniversary Photo Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 15.0, "photo_frame",
        "Two glass panes that hold a 6 x 4 in photo between them, with a chrome stand.",
        (cw("Clear", "#e8f0f2"),), _occ("Anniversary")),
    Row("FRMMLT", "Graduation Multi-Photo Frame", "Lanternby", "Gifts", _FRAMES, "Photo Frame",
        28.0, "photo_frame",
        "A wall frame with five apertures, for a run of photos from one big day.",
        (cw("Black", "#2a2a2e"), _OAK), _occ("Graduation")),
    Row("WRPRLL", "Birthday Wrapping Paper Roll, 4 m", "Lanternby", "Gifts", _WRAP,
        "Wrapping Paper", 4.0, "wrapping_paper",
        "A roll of thick printed paper with a grid on the back for straight cuts.",
        (cw("Confetti", "#ffffff", "polka", "#d6267a"),
         cw("Pastel Spot", "#8fb8de", "polka", "#f2d14b")),
        _occ("Birthday")),
    Row("WRPSHT", "Christmas Wrapping Paper, 3 Sheets", "Calderby & Lune", "Gifts", _WRAP,
        "Wrapping Paper", 5.0, "wrapping_paper",
        "Three folded sheets with matching tags, printed on recycled paper.",
        (cw("Red Stripe", "#ffffff", "stripe", "#c8312e"),
         cw("Gold Star", "#1f2e4a", "polka", "#d4af37")),
        _occ("Christmas")),
    Row("WRPKRF", "Baby Shower Kraft Wrap and Ribbon Set", "Lanternby", "Gifts", _WRAP,
        "Wrapping Paper", 7.0, "wrapping_paper",
        "Two sheets of kraft paper, a printed sheet and 3 m of cotton ribbon.",
        (cw("Kraft", "#c9a77a", "stripe", "#ffffff"),), _occ("Baby Shower")),
    Row("CHMENM", "Enamel Fox Charm Keyring", "Lanternby", "Gifts", _CHARM, "Keyring", 8.0,
        "keyring", "A hard enamel charm on a split ring with a short chain, on a gift card.",
        (cw("Rust", "#a8502e"),), _charm("Fox")),
    Row("CHMPWT", "Pewter Hare Charm Keyring", "Calderby & Lune", "Gifts", _CHARM, "Keyring",
        12.0, "keyring", "A cast pewter charm on a leather tab, boxed with a care card.",
        (cw("Pewter", "#8a8d8f"),), _charm("Hare")),
    Row("CHMWOD", "Wooden Owl Charm Keyring", "Lanternby", "Gifts", _CHARM, "Keyring", 6.0,
        "keyring", "A laser-cut wooden charm, oiled and threaded on a cotton cord.",
        (cw("Natural", "#d8c9a8"),), _charm("Owl")),
    Row("CHMSLV", "Sterling Silver Bee Charm Keyring", "Calderby & Lune", "Gifts", _CHARM,
        "Keyring", 35.0, "keyring",
        "A hallmarked silver charm on a polished ring, in a lined gift box.",
        (_SILVER,), _charm("Bee")),
    Row("DECSTR", "Glitter Glass Star Decoration", "Lanternby", "Gifts", _DECOR,
        "Christmas Decoration", 6.0, "star",
        "A mouth-blown glass star with a ribbon loop, about 10 cm across.",
        (cw("Gold", "#d4af37"), cw("Silver", "#c0c0c0")), (("finish", "Finish", "Glitter"),)),
    Row("DECWST", "Painted Wooden Star Decoration Set", "Calderby & Lune", "Gifts", _DECOR,
        "Christmas Decoration", 9.0, "star",
        "Six flat wooden stars on jute loops, for a tree, a garland or a gift.",
        (cw("Red", "#c8312e"), cw("White", "#ffffff")), (("finish", "Finish", "Painted"),)),
    Row("DECSNO", "Glitter Glass Snowflake Decoration", "Lanternby", "Gifts", _DECOR,
        "Christmas Decoration", 7.0, "snowflake",
        "A flat glass snowflake that catches the tree lights, on a fine hanging thread.",
        (cw("Ice", "#dbe9f2"),), (("finish", "Finish", "Glitter"),)),
    Row("DECFLT", "Gilded Felt Snowflake Decoration", "Calderby & Lune", "Gifts", _DECOR,
        "Christmas Decoration", 5.0, "snowflake",
        "A hand-cut felt snowflake with stitched edges, light enough for any branch.",
        (cw("Cream", "#efe8d8"), cw("Red", "#c8312e")), (("finish", "Finish", "Gilded"),)),
    Row("CNDJAR", "Fig and Cedar Scented Candle", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 18.0, "jar",
        "A soy wax candle in a reusable glass jar, about 40 hours of burn time.",
        (cw("Smoke", "#6f6a66"),), _scent("Fig and Cedar"), (("Medium", 18.0), ("Large", 28.0)),
        "Candle"),
    Row("CNDTIN", "Sea Salt Travel Tin Candle", "Calderby & Lune", "Gifts", _CANDLE,
        "Scented Candle", 8.0, "tin",
        "A small candle in a lidded tin, about 15 hours of burn time, for a bag or a desk.",
        (cw("Sand", "#d9c7a3"),), _scent("Sea Salt"), label="Candle"),
    Row("CNDTRW", "Amber Woods Three-Wick Candle", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 32.0, "jar",
        "A wide candle with three cotton wicks that fills a room, about 50 hours of burn time.",
        (cw("Amber", "#c98a2e"),), _scent("Amber Woods"), label="Candle"),
    Row("CNDLIN", "Fresh Linen Candle Gift Set", "Calderby & Lune", "Gifts", _CANDLE,
        "Scented Candle", 24.0, "jar",
        "Three votive candles in frosted glass, boxed with a ribbon for giving.",
        (cw("White", "#ffffff"),), _scent("Fresh Linen"), label="Candle"),
    # Round 2 (gen#125): at 20K, gifts held 28 styles against a half share of 30.
    # As in toys: one new value per leaf at most, extra colors for the rest.
    Row("FRMCHR", "Pewter Christening Photo Frame", "Lanternby", "Gifts", _FRAMES,
        "Photo Frame", 26.0, "photo_frame",
        "A heavy frame for a 6 x 4 in photo with an easel back, boxed in tissue.",
        (cw("Pewter", "#8a8d8f"), cw("Brushed Gold", "#c9a85a")), _occ("Christening")),
    Row("FRMRET", "Graduation Signature Photo Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 30.0, "photo_frame",
        "A wide frame with a mount for a message from every friend around the photo.",
        (cw("Walnut", "#6b4a30"), _OAK, cw("Black", "#2a2a2e")), _occ("Graduation")),
    Row("WRPWED", "Wedding Gift Wrap Roll, 2 m", "Calderby & Lune", "Gifts", _WRAP,
        "Wrapping Paper", 6.0, "wrapping_paper",
        "A heavyweight paper with a soft sheen, wide enough for a boxed present.",
        (cw("Ivory Lace", "#f6f1e4", "polka", "#d4af37"),
         cw("Sage Leaf", "#c9d6c0", "stripe", "#ffffff")), _occ("Wedding")),
    Row("WRPANV", "Birthday Foil Wrapping Paper Pack", "Lanternby", "Gifts", _WRAP,
        "Wrapping Paper", 5.5, "wrapping_paper",
        "Two foil-printed sheets and two tags, folded flat in a card sleeve.",
        (cw("Ruby Spot", "#8e1b2c", "polka", "#d4af37"),
         cw("Navy Stripe", "#26365c", "stripe", "#c0c0c0")),
        _occ("Birthday")),
    Row("CHMBRS", "Brass Hedgehog Charm Keyring", "Lanternby", "Gifts", _CHARM, "Keyring",
        10.0, "keyring", "A solid brass charm that darkens with use, on a small gift card.",
        (cw("Brass", "#b5a642"), cw("Copper", "#b87333")), _charm("Hedgehog")),
    Row("CHMCER", "Ceramic Owl Charm Keyring", "Calderby & Lune", "Gifts", _CHARM, "Keyring",
        9.0, "keyring", "A glazed charm hand-painted in the studio, on a waxed cotton cord.",
        (cw("Glaze", "#e8e2d6"), cw("Celadon", "#a7c4a0")), _charm("Owl")),
    Row("CNDPOT", "Orange Blossom Ceramic Pot Candle", "Calderby & Lune", "Gifts", _CANDLE,
        "Scented Candle", 22.0, "jar",
        "A candle poured into a stoneware pot that makes a plant pot once it burns down.",
        (cw("Stone", "#c9c1b3"), cw("Terracotta", "#b5603a")), _scent("Orange Blossom"),
        label="Candle"),
    Row("CNDREF", "Sea Salt Candle Refill", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 12.0, "tin",
        "A wax refill that drops into an empty candle jar, about 35 hours of burn time.",
        (cw("Leaf", "#6f8f4a"),), _scent("Sea Salt"), label="Candle"),
    Row("DECFRS", "Frosted Glass Bauble Star", "Lanternby", "Gifts", _DECOR,
        "Christmas Decoration", 8.0, "star",
        "A hollow star with a crown cap and a loop, boxed singly in tissue.",
        (cw("Pale Blue", "#c9dcea"), cw("Blush", "#ecc6c6")), (("finish", "Finish", "Frosted"),)),
    Row("DECPRL", "Gilded Snowflake Ornament Trio", "Calderby & Lune", "Gifts", _DECOR,
        "Christmas Decoration", 10.0, "snowflake",
        "Three shatterproof snowflakes in graded sizes, on a card for giving.",
        (cw("Pearl", "#efe9e1"),), (("finish", "Finish", "Gilded"),)),
    Row("FRMLTH", "Leather Wedding Photo Album Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 34.0, "photo_frame",
        "A stitched frame that folds like a book, holding two 6 x 4 in photos side by side.",
        (cw("Tan", "#a8743f"), cw("Black", "#2a2a2e")), _occ("Wedding")),
    Row("CNDBEE", "Amber Woods Beeswax Pillar Candle", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 16.0, "jar",
        "A hand-poured pillar on a glass dish, about 30 hours of burn time.",
        (cw("Honey", "#e0a030"),), _scent("Amber Woods"), label="Candle"),
    # gen#509: the scents of the plants a shopper names by a scent word (lavender, sage,
    # eucalyptus), so the word keeps its scent sense beside the plant node.
    Row("CNDLAV", "Lavender Soy Wax Candle in Glass Jar", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 17.0, "jar",
        "A soy wax candle in a reusable glass jar, about 40 hours of burn time, for a bedroom.",
        (cw("Lilac", "#c8b6d8"),), _scent("Lavender"), (("Medium", 17.0), ("Large", 27.0)),
        "Candle"),
    Row("CNDSAG", "Sage Travel Tin Candle", "Calderby & Lune", "Gifts", _CANDLE,
        "Scented Candle", 8.0, "tin",
        "A small candle in a lidded tin, about 15 hours of burn time, with a fresh herbal scent.",
        (cw("Sage", "#9bb08f"),), _scent("Sage"), label="Candle"),
    Row("CNDEUC", "Eucalyptus Three-Wick Candle", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 30.0, "jar",
        "A wide candle with three cotton wicks and a clean, minty scent, about 50 hours of "
        "burn time.", (cw("Teal", "#2a7f80"),), _scent("Eucalyptus"), label="Candle"),
)  # fmt: skip

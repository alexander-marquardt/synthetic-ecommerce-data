"""Video games (gen#1120): Electronics > Gaming > Video Games.

The build had game controllers and gaming headsets (gen#956) and no game to play on them. A
style is one invented title in one edition, and its SKUs are the three platforms it is sold on:
PC or one of the invented console families whose consoles ``type_specs/game_console.py`` sells.
Each title cycles which of the four platforms it skips. Every style states its genre, age
rating (3+ to 18+), number of players, edition (Standard, or Deluxe on its own style) and format
(Disc, or Download Code), and :func:`kit_gaming.video_game` draws the format and the edition.

Most titles are a world of our own and a genre word ("Quarrow Rally"). :data:`COLLISIONS` lists
the titles whose words name another department's product type ("Garden Party" against Garden
Chair and the party goods), which ``docs/retail-prototype/video-games-1120.md`` turns into a
demo query list. ``tests/test_retail_video_games_1120.py`` measures each collision word on the
build's own vocabulary and holds every other title to none. The rows are templates only
(``derivable`` False): a derived style would invent titles from the values a title shows, and a
game's name shows none. Every title, publisher and platform is invented.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import zlib
from typing import NamedTuple

from synthetic_ecommerce_data.domains.retail.gaming_rows import ROOT
from synthetic_ecommerce_data.domains.retail.type_registry import Option, Row, TypeSpec, a, cw

DEPARTMENT = "Electronics"
PATH = (ROOT, "Gaming", "Video Games")
PC = "PC"
#: The invented console families, one console maker each (``type_specs/game_console.py``).
CONSOLE_FAMILIES = ("Kestara", "Lumivo", "Drovik")
PLATFORMS = (PC, *CONSOLE_FAMILIES)
#: The invented publishers: a game's brand is its publisher.
PUBLISHERS = (
    "Thornvale Studios", "Brassik Softworks", "Quillmere Interactive", "Calvenby Studios",
    "Larkspire Softworks", "Dunmarrow Interactive", "Fennick Studios", "Wendlecott Interactive",
)  # fmt: skip
#: What a download code costs less than the disc, and what a deluxe edition costs more.
CODE_OFF, DELUXE_ON = 3.0, 20.0
#: Every tenth title also comes in a deluxe edition, on a style of its own.
DELUXE_EVERY = 10


class Genre(NamedTuple):
    age: str
    players: str
    price: float
    cover: str
    words: tuple[str, str]
    description: str


#: genre -> its age rating, players, disc price, cover color, the two title words a world takes
#: in it, and its description ({world} is the title's world).
GENRES: dict[str, Genre] = {
    "Racing": Genre("3+", "1-4", 34.0, "#c8312e", ("Rally", "Speedway"), "Race the mountain passes and harbor circuits of {world} against friends on a split screen or against the clock."),
    "Adventure": Genre("7+", "1", 39.0, "#4f8a3a", ("Expedition", "Voyage"), "Cross the islands of {world}, map its ruins and solve the riddle at the heart of each one."),
    "Role-Playing": Genre("12+", "1", 49.0, "#7b5aa6", ("Chronicles", "Saga"), "Build a party of six heroes, choose who they become and decide the fate of {world} over sixty hours."),
    "Strategy": Genre("12+", "1-2", 44.0, "#2f8f8a", ("Tactics", "Dominion"), "Command squads on a hex map of {world}, turn by turn, and outthink a rival general."),
    "Puzzle": Genre("3+", "1-2", 24.0, "#f2c230", ("Riddles", "Enigma"), "Two hundred hand-made puzzles set in {world}, with hints when a level holds you up."),
    "Platformer": Genre("7+", "1-2", 34.0, "#e07a1f", ("Dash", "Hop"), "Run, jump and wall-climb through forty levels of {world}, alone or with a friend."),
    "Sports": Genre("3+", "1-4", 44.0, "#3f6fb5", ("League", "Champions"), "Pick a club from {world}, run its season and play every match with up to four players."),
    "Simulation": Genre("3+", "1", 34.0, "#8a6d3b", ("Tycoon", "Colony"), "Found a settlement in {world}, plan its roads and keep its people fed through the seasons."),
    "Shooter": Genre("16+", "1-8", 49.0, "#4a4f57", ("Siege", "Vanguard"), "Hold the walls of {world} in a story campaign, then take eight-player matches online."),
    "Horror": Genre("18+", "1", 39.0, "#2d2d33", ("Dread", "Haunting"), "Survive the long night in the abandoned halls of {world} with a torch and what you can find."),
    "Fighting": Genre("16+", "1-2", 39.0, "#a8323e", ("Duel", "Brawlers"), "Twenty fighters from {world}, each with a move list to master, in story, arcade and versus modes."),
    "Party": Genre("3+", "1-4", 29.0, "#e59ab0", ("Jamboree", "Fiesta"), "Fifty quick mini-games set across {world} for up to four players on one screen."),
}  # fmt: skip
#: The invented worlds the titles are named for; each takes nine genres.
WORLDS = (
    "Quarrow", "Velden", "Ostrik", "Brannoch", "Tavrel", "Mirrin", "Caldrith", "Korvath",
    "Lunmere", "Pashtir", "Sarnoth", "Ulvane", "Ashkar", "Bryndle", "Corvel", "Eskeli",
    "Yorrow", "Zenthe",
)  # fmt: skip
GENRES_PER_WORLD = 9


class Collision(NamedTuple):
    """A title whose ``words`` name another department's product ``types``."""

    title: str
    words: tuple[str, ...]
    types: tuple[str, ...]
    genre: str
    age: str
    players: str
    description: str


#: The collision titles (gen#1120 point 2): each word is a word of another department's product
#: type or category, measured on the build's vocabulary by the test.
COLLISIONS = (
    Collision("Garden Party", ("garden", "party"), ("Garden Chair", "Party Cup", "Party Plate"), "Party", "3+", "1-4", "Host the summer party of the year: thirty lawn games, a bake-off and a fireworks finale for up to four players."),
    Collision("Kitchen Rush", ("kitchen",), ("Kitchen Utensil", "Kitchen Knife"), "Simulation", "3+", "1-4", "Chop, fry and plate up against the clock in a busy restaurant, alone or with three friends."),
    Collision("Pet Rescue", ("pet",), ("Pet Bed", "Pet Toy"), "Simulation", "3+", "1", "Run an animal shelter, nurse strays back to health and find each one a home."),
    Collision("Tool Time", ("tool",), ("Hand Tool", "Tool Kit"), "Puzzle", "7+", "1-2", "Fix a hundred broken gadgets by choosing the right part and the right order to fit it."),
    Collision("Dinosaur Dig", ("dinosaur",), ("Toy Figure",), "Adventure", "7+", "1-2", "Lead a fossil hunt across three deserts, dig out bones and build each skeleton in your museum."),
    Collision("Pillow Fight", ("pillow",), ("Pillow",), "Party", "7+", "1-4", "A late-night brawl in twelve bedrooms, where the last player standing keeps the duvet."),
    Collision("Cake Quest", ("cake",), ("Cake",), "Platformer", "3+", "1-2", "Hop through a kingdom of sponge and icing to bring back the stolen birthday candles."),
    Collision("Sofa Surfers", ("sofa",), ("Sofa", "Corner Sofa"), "Party", "7+", "1-4", "Jump from couch to couch across a flooded living room and never touch the floor."),
    Collision("Tent Troopers", ("tent",), ("Tent",), "Strategy", "12+", "1-2", "Pitch a base camp in the wilds, survey the ridge and outlast a rival camp through a storm."),
    Collision("Golf Club Legends", ("golf", "club"), ("Golf Club", "Golf Ball"), "Sports", "3+", "1-4", "Eighteen fantasy courses, a career mode and a club house to fill with trophies."),
    Collision("Robot Mower Mayhem", ("robot", "mower"), ("Robot Mower", "Lawn Mower"), "Racing", "7+", "1-4", "Race runaway lawn robots round the suburbs, cutting shortcuts through every hedge."),
    Collision("Jigsaw Isle", ("jigsaw",), ("Jigsaw Puzzle",), "Puzzle", "3+", "1", "Piece together the map of a lost island, one picture at a time, to open the shore beyond."),
    Collision("Toaster Tactics", ("toaster",), ("Toaster",), "Strategy", "7+", "1-2", "Command an army of kitchen gadgets in turn-based battles across the breakfast table."),
    Collision("Kettle Kingdom", ("kettle",), ("Kettle",), "Adventure", "7+", "1", "Clockwork knights defend a tiny realm built on a stove top from the cold of the fridge."),
    Collision("Blender Brawl", ("blender",), ("Blender",), "Fighting", "12+", "1-2", "Fruit fighters spin, slice and smoothie each other in a whirling arena."),
    Collision("Shampoo Showdown", ("shampoo",), ("Shampoo",), "Party", "3+", "1-4", "Salon mini-games: style, foam and rinse faster than the other three stylists."),
    Collision("Dog Park Dash", ("dog",), ("Dog Food", "Dog Treats"), "Racing", "3+", "1-4", "Race puppies round the park, fetching balls and leaping benches for the top prize."),
    Collision("Cat Burglar", ("cat",), ("Cat Food", "Cat Litter"), "Adventure", "12+", "1", "A nimble thief with nine lives sneaks over rooftops to return stolen jewels to their owners."),
    Collision("Umbrella Storm", ("umbrella",), ("Umbrella",), "Platformer", "7+", "1-2", "Ride the wind under a magic brolly across forty levels of thunderclouds."),
    Collision("Saucepan Samurai", ("saucepan",), ("Saucepan",), "Fighting", "12+", "1-2", "A chef with a hidden past fights through a city of rival kitchens, pan in hand."),
    Collision("Lantern Light", ("lantern", "light"), ("Camping Lantern", "Night Light"), "Horror", "16+", "1", "Lost in a forest at night with one lamp and its last oil, find the way out before it goes dark."),
    Collision("Picnic Blanket Panic", ("picnic", "blanket"), ("Picnic Blanket",), "Puzzle", "3+", "1-2", "Fit every basket, plate and sandwich onto the rug before the ants arrive."),
    Collision("Coffee Table Tycoon", ("coffee", "table"), ("Coffee Table", "Coffee"), "Simulation", "3+", "1", "Open a cafe, roast your own beans and grow it into a chain across the city."),
    Collision("Candle Vigil", ("candle",), ("Scented Candle",), "Horror", "16+", "1", "Keep the flames of an old lighthouse alight through a haunted winter."),
    Collision("Light Bulb Labs", ("light", "bulb"), ("Light Bulb",), "Puzzle", "7+", "1-2", "Wire up a mad inventor's lab, circuit by circuit, until every lamp in the tower glows."),
    Collision("Ladder Climb", ("ladder",), ("Step Ladder",), "Platformer", "7+", "1-2", "Climb a tower of rungs, ropes and moving platforms to the window at the very top."),
)  # fmt: skip


def _crc(text: str) -> int:
    return zlib.crc32(text.encode())


def _titles() -> list[tuple[str, str, str, str, str]]:
    """Each title once: (title, genre, age, players, description), the worlds' then the
    collisions'. A world takes the nine genres its name hashes first, and one of each genre's
    two words."""
    out = []
    for world in WORLDS:
        for genre in sorted(GENRES, key=lambda g, w=world: _crc(f"{w}:{g}"))[:GENRES_PER_WORLD]:
            g = GENRES[genre]
            word = g.words[_crc(f"{world}:{genre}:word") % 2]
            out.append((f"{world} {word}", genre, g.age, g.players, g.description.format(world=world)))
    out += [(c.title, c.genre, c.age, c.players, c.description) for c in COLLISIONS]
    return out


def _row(code: str, title: str, genre: str, age: str, players: str, description: str,
         n: int, edition: str) -> Row:  # fmt: skip
    """One title in one edition; its SKUs are the three platforms it is sold on."""
    fmt = "Download Code" if n % 4 == 3 else "Disc"
    price = GENRES[genre].price - (CODE_OFF if fmt == "Download Code" else 0.0) + (DELUXE_ON if edition == "Deluxe" else 0.0)
    platforms = tuple(p for p in PLATFORMS if p != PLATFORMS[n % len(PLATFORMS)])
    attrs = (a("genre", "Genre", genre), a("age_rating", "Age rating", age),
             a("number_of_players", "Number of players", players), a("edition", "Edition", edition),
             a("format", "Format", fmt))  # fmt: skip
    return Row(code, title, PUBLISHERS[_crc(title) % len(PUBLISHERS)], DEPARTMENT, PATH, "Video Game", price,
               "video_game", description, (cw("Cover", GENRES[genre].cover),), attrs,
               tuple((p, price) for p in platforms), colorless=True, size_key="platform",
               params=(("format", fmt.lower()), ("edition", edition.lower())))  # fmt: skip


def _rows() -> tuple[Row, ...]:
    out = []
    for n, (title, genre, age, players, description) in enumerate(_titles()):
        out.append(_row(f"VG{n:04d}", title, genre, age, players, description, n, "Standard"))
        if n % DELUXE_EVERY == DELUXE_EVERY - 1:
            out.append(_row(f"VD{n:04d}", f"{title} Deluxe Edition", genre, age, players,
                            f"{description} The deluxe edition adds the season pass and a digital art book.",
                            n, "Deluxe"))  # fmt: skip
    return tuple(out)


ROWS = _rows()

SPEC = TypeSpec(
    key="video_game",
    department=DEPARTMENT,
    product_type="Video Game",
    derivable=False,
    owners=tuple((p, "third_party") for p in PUBLISHERS),
    rows=ROWS,
    options=(Option("platform", "platform", "Platform"),),
)

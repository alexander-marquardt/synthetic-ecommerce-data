"""Video games and consoles (gen#1120): Electronics > Gaming > Video Games and Consoles.

On main the retail build held game controllers and gaming headsets (gen#956, slice 2b) but no
game and no console. These checks hold the Done-when of gen#1120, from its gate comment:

- About 600 video game SKUs: about 200 invented titles, each a style whose SKUs are the three
  platforms it is sold on (PC or an invented console family), with genre, age rating, number of
  players, edition and format.
- About 30 console SKUs, one family per console platform the games name.
- At least 20 titles whose words name another department's product type, each word measured on
  the build's own vocabulary; every other title names none.
- No real console, platform or publisher name in any title, brand, platform or description.
- The demo query list (``docs/retail-prototype/video-games-1120.md``) names every collision title
  and the four queries the issue asks for.
"""

from __future__ import annotations

import collections
import importlib
import importlib.util
import pathlib
import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry

ROOT = "Electronics"
GAME, CONSOLE = "Video Game", "Game Console"
GAME_SPEC = "synthetic_ecommerce_data.domains.retail.type_specs.video_game"
#: The issue's band around "about 600" game SKUs, and around "about 30" console SKUs.
GAME_SKUS = (550, 650)
TITLES = (180, 220)
CONSOLE_SKUS = (25, 40)
MIN_COLLISIONS = 20
AGES = {"3+", "7+", "12+", "16+", "18+"}
EDITIONS = {"Standard", "Deluxe"}
FORMATS = {"Disc", "Download Code"}
#: Real consoles, platforms, stores and publishers: none may appear (the issue's point 3).
REAL = (
    "playstation", "xbox", "nintendo", "switch", "wii", "gamecube", "game boy", "sega",
    "dreamcast", "mega drive", "genesis", "atari", "steam", "stadia", "sony", "microsoft",
    "valve", "ubisoft", "activision", "blizzard", "electronic arts", "bandai", "namco",
    "capcom", "konami", "square enix", "bethesda", "rockstar", "epic games", "take-two",
    "tencent", "odyssey", "neo geo", "ps5", "ps4", "psp", "vita", "3ds", "snes", "n64",
)
DOC = pathlib.Path(__file__).resolve().parent.parent / "docs/retail-prototype/video-games-1120.md"
DEMO_QUERIES = ("garden party", "kitchen rush", "garden party game", "garden party chairs")


def _game_module():
    """The video game spec module; a plain assert, so the test is red on main, not an error."""
    assert importlib.util.find_spec(GAME_SPEC) is not None, "no video_game spec"
    return importlib.import_module(GAME_SPEC)


@pytest.fixture(scope="module")
def electronics() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == ROOT]


@pytest.fixture(scope="module")
def vocabulary() -> dict[str, set[str]]:
    """Each word of a product type or category label outside Electronics, to the product types
    whose type or path holds it: the words a game title collides with."""
    out: dict[str, set[str]] = collections.defaultdict(set)
    for r in scale.templates():
        if r["category_path"][0] == ROOT:
            continue
        for label in (r["product_type"], *r["category_path"]):
            for w in re.findall(r"[a-z]+", label.lower()):
                out[w].add(r["product_type"])
    return out


def _mine(electronics: list[dict], ptype: str) -> list[dict]:
    return [r for r in electronics if r["product_type"] == ptype]


def _attr(record: dict, key: str) -> str | None:
    return next((x["value"] for x in record["attributes"] if x["key"] == key), None)


def _words(title: str) -> set[str]:
    return set(re.findall(r"[a-z]+", title.lower()))


def test_the_video_games_hold_about_600_skus(electronics) -> None:
    n = sum(r["sku_count"] for r in _mine(electronics, GAME))
    assert GAME_SKUS[0] <= n <= GAME_SKUS[1], n


def test_the_video_games_hold_about_200_titles(electronics) -> None:
    titles = {r["title"].removesuffix(" Deluxe Edition") for r in _mine(electronics, GAME)}
    assert TITLES[0] <= len(titles) <= TITLES[1], len(titles)


def test_every_game_states_its_attributes_and_each_sku_its_platform(electronics) -> None:
    games = _mine(electronics, GAME)
    assert games
    for r in games:
        assert _attr(r, "genre"), r["product_id"]
        assert _attr(r, "age_rating") in AGES, r["product_id"]
        assert _attr(r, "number_of_players"), r["product_id"]
        assert _attr(r, "edition") in EDITIONS, r["product_id"]
        assert _attr(r, "format") in FORMATS, r["product_id"]
        platforms = [s.get("platform") for s in r["skus"]]
        assert len(platforms) == 3 and len(set(platforms)) == 3 and all(platforms), r["product_id"]
    for key, want in (("age_rating", AGES), ("edition", EDITIONS), ("format", FORMATS)):
        assert {_attr(r, key) for r in games} == want, key


def test_the_consoles_hold_about_30_skus_and_every_game_platform_has_one(electronics) -> None:
    consoles = _mine(electronics, CONSOLE)
    n = sum(r["sku_count"] for r in consoles)
    assert CONSOLE_SKUS[0] <= n <= CONSOLE_SKUS[1], n
    families = {_attr(r, "platform") for r in consoles}
    named = {s["platform"] for r in _mine(electronics, GAME) for s in r["skus"]} - {"PC"}
    assert named and named == families


@pytest.mark.parametrize("ptype", [GAME, CONSOLE], ids=["video_game", "game_console"])
def test_each_type_sits_under_gaming_and_is_never_derived(electronics, ptype) -> None:
    mine = _mine(electronics, ptype)
    assert mine
    assert {tuple(r["category_path"][:2]) for r in mine} == {(ROOT, "Gaming")}
    derived = set(ceiling_build().template_of)
    assert not [r["product_id"] for r in mine if r["product_id"] in derived]


def test_at_least_20_titles_collide_with_another_departments_type(electronics, vocabulary) -> None:
    mod = _game_module()
    titles = {r["title"] for r in _mine(electronics, GAME)}
    assert len(mod.COLLISIONS) >= MIN_COLLISIONS
    for c in mod.COLLISIONS:
        assert c.title in titles, c.title
        assert _words(c.title) & set(vocabulary) == set(c.words), c.title
        hit = set().union(*(vocabulary[w] for w in c.words))
        assert set(c.types) <= hit, (c.title, set(c.types) - hit)


def test_no_other_title_names_another_departments_type(electronics, vocabulary) -> None:
    mod = _game_module()
    declared = {c.title for c in mod.COLLISIONS}
    stray = {r["title"]: sorted(_words(r["title"]) & set(vocabulary))
             for r in _mine(electronics, GAME)
             if r["title"].removesuffix(" Deluxe Edition") not in declared}  # fmt: skip
    assert not {t: w for t, w in stray.items() if w}


@pytest.mark.parametrize("ptype", [GAME, CONSOLE], ids=["video_game", "game_console"])
def test_no_real_console_platform_or_publisher_name(electronics, ptype) -> None:
    found = []
    for r in _mine(electronics, ptype):
        text = " ".join([r["title"], r["brand"], r["description"],
                         *(str(s.get("platform", "")) for s in r["skus"]),
                         *(str(x["value"]) for x in r["attributes"])]).lower()  # fmt: skip
        found += [(r["product_id"], n) for n in REAL if re.search(rf"\b{re.escape(n)}\b", text)]
    assert not found


def test_the_demo_page_lists_every_collision_and_the_demo_queries() -> None:
    mod = _game_module()
    assert DOC.exists(), DOC
    text = DOC.read_text()
    missing = [c.title for c in mod.COLLISIONS if f"`{c.title.lower()}`" not in text]
    missing += [q for q in DEMO_QUERIES if f"`{q}`" not in text]
    assert not missing


def test_the_rows_and_drawings_are_deterministic() -> None:
    _game_module()
    for key in ("video_game", "game_console"):
        spec = type_registry.specs()[key]
        assert spec.docs() == spec.docs()


@pytest.mark.parametrize(
    ("shape", "params", "other"),
    [
        ("video_game", {"format": "disc"}, {"format": "download code"}),
        ("video_game", {"edition": "standard"}, {"edition": "deluxe"}),
        ("game_console", {"console_form": "home"}, {"console_form": "slim"}),
        ("game_console", {"console_form": "home"}, {"console_form": "handheld"}),
    ],
)
def test_a_param_changes_the_drawing(shape, params, other) -> None:
    _game_module()
    assert shape in kit.shapes(), shape
    fill = kit.Fill("solid", "#123456", "#654321")
    assert kit.render(shape, fill, params=params) != kit.render(shape, fill, params=other)


def test_the_games_take_no_word_another_department_draws_names_from() -> None:
    """A word of a game's text that is a line grammar lead word or a scale range name re-deals
    that whole family's names: the first draft's "Bounce" and "Leap" renamed every derived toy.
    The games add no such word to the build's text."""
    import pkgutil  # noqa: PLC0415

    from synthetic_ecommerce_data.domains.retail import (  # noqa: PLC0415
        line_grammar,
        line_grammar_families,
        range_ownership,
    )

    tpls = scale.templates(baseline=False)
    games = [r for r in tpls if r["product_type"] in (GAME, CONSOLE)]
    assert games
    rest = [r for r in tpls if r["product_type"] not in (GAME, CONSOLE)]
    added = line_grammar.text_words(games) - line_grammar.text_words(rest)
    pools = {"range.scale": set(range_ownership.whole_halves()["scale"])}
    for m in pkgutil.iter_modules(line_grammar_families.__path__):
        mod = importlib.import_module(f"{line_grammar_families.__name__}.{m.name}")
        pools[m.name] = set(getattr(mod, "LEADS", ()))
    assert len([p for p in pools.values() if p]) > 5  # non-vacuous: the families' lead lists load
    hits = {name: sorted(w for w in words if w.lower() in added) for name, words in pools.items()}
    assert {k: v for k, v in hits.items() if v} == {}

"""The figures and SKUs the tests pin on ``golden-catalog/``, measured by rule (#50).

A regeneration of the golden catalog moves every SKU code and many counts. Before this, each test
that pinned one restated it by hand, one measurement script at a time. Now
``scripts/measure_pins.py`` re-measures all of them with this module and writes
``tests/data/golden_pins.json``; the tests read the fixture, so the next regeneration is::

    uv run ecom-generate build --out golden-catalog && uv run python scripts/measure_pins.py

and the diff of the fixture is the review artifact: a figure that moved for no stated reason is
questioned there.

Three kinds of pin live in the fixture:

``lens``
    The SKUs the handle-less magnifier lens tests name, each picked by a stated rule in
    :data:`SKU_RULES`, and the smallest enlargement any committed lens gives. A rule that no SKU
    satisfies raises :class:`PinRuleError` naming the rule. It never falls back to a weaker SKU.
``titles``
    What the cap cut this replaced would have done to the default catalog: the document count, the
    titles over the cap and the titles it would cut mid-word.
``anchor``
    The product line the mutation bed plants its golden-catalog defects in: the first line, in
    catalog order, with more than one variant. :func:`anchor_needles` lists the texts a planted
    row quotes, and :func:`measure_anchor` refuses an anchor any of them does not occur in exactly
    once.
``figures``
    What a test measured on one build and compared exactly: a type's SKU count at
    ``--lines 39000``, the sizes a defect rewrote, a fit's spread. Each module ``tests/pinned.py``
    names measures its own with ``measure_pins(config)``, the test's own code on the build that
    config makes, and reads the figures back from the fixture. A census band is never a figure.

The same command rewrites every slice of ``tests/data/golden_slices/`` (:func:`write_slices`), a
type's default build that its ``tests/test_type_<key>.py`` holds byte for byte; slice 2 of #50
found the slices stale on a moved seed, each rewritten only by its test's own ``__main__``.
"""

from __future__ import annotations

import functools
import importlib
import json
import string
import sys
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "golden-catalog"
PINS_PATH = ROOT / "tests" / "data" / "golden_pins.json"
SLICES = ROOT / "tests" / "data" / "golden_slices"

#: The command a contributor runs after a regeneration; every failure here names it.
REGENERATE = (
    "uv run ecom-generate build --out golden-catalog && uv run python scripts/measure_pins.py"
)


class PinRuleError(Exception):
    """A pin rule that no SKU of the catalog satisfies, or an anchor that is not unique."""


@dataclass(frozen=True)
class SkuRule:
    """One pinned SKU: the first in catalog order of a product type that fits a statement."""

    key: str
    statement: str
    product_type: str
    #: ``(attribute key, value)`` the SKU must publish, or ``None``.
    attribute: tuple[str, str] | None
    #: Whether the handle-less lens must serve the SKU (``True``) or the rule ignores the lens.
    handle_less: bool


SKU_RULES: tuple[SkuRule, ...] = (
    SkuRule(
        "screw",
        "the first socket head cap screw SKU in catalog order drawn under the handle-less lens",
        "screw_socket_head",
        None,
        True,
    ),
    SkuRule(
        "drill",
        'the first 5/64" jobber drill SKU in catalog order drawn under the handle-less lens',
        "drill_jobber",
        ("size", "5/64"),
        True,
    ),
    SkuRule(
        "hairline_drill",
        'the first 1/16" jobber drill SKU in catalog order',
        "drill_jobber",
        ("size", "1/16"),
        False,
    ),
)


# --- reading the committed catalog -------------------------------------------------------------


@functools.cache
def facets(golden: Path = GOLDEN):
    """``{sku: facets}``: a nested entry carries no spelling, so a drawing reads it here (#42)."""
    from synthetic_ecommerce_data.core import bundle

    return bundle.flat_facets(golden)


def type_scale(type_key: str) -> float:
    from synthetic_ecommerce_data.core.drawing.sheet import type_scale as scale
    from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES

    return scale(FIGURES[type_key][1])


def drawn_size(type_key: str, record) -> tuple[float, float]:
    from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES

    x0, y0, x1, y1 = FIGURES[type_key][0](dict(record)).figure.bounds()
    scale = type_scale(type_key)
    return (x1 - x0) * scale, (y1 - y0) * scale


def golden_skus(golden: Path = GOLDEN) -> Iterator[tuple[dict, dict, Any]]:
    """``(parent, variant, record)`` for every committed SKU, in catalog order."""
    from synthetic_ecommerce_data.core import bundle

    for line in (golden / "nested.jsonl").read_text("utf-8").splitlines():
        parent = json.loads(line)
        for variant in parent["variants"]:
            yield (
                parent,
                variant,
                bundle._record(
                    parent,
                    variant,
                    facets(golden)[variant["sku"]],
                    facets(golden).authored.get(parent["product_type"]),
                ),
            )


# --- the lens pins -----------------------------------------------------------------------------


def pick_sku(rule: SkuRule, candidates: Iterable[tuple[dict, dict, bool]]) -> str:
    """The first candidate SKU that the rule's statement holds for.

    ``candidates`` is ``(parent, variant, handle_less)`` in catalog order. When none fits, the
    rule is named in the error: a weaker SKU would pin something other than what the test says.
    """
    for parent, variant, handle_less in candidates:
        if parent["product_type"] != rule.product_type:
            continue
        if rule.attribute is not None:
            key, value = rule.attribute
            if not any(a["key"] == key and a["value"] == value for a in variant["attributes"]):
                continue
        if rule.handle_less and not handle_less:
            continue
        return variant["sku"]
    raise PinRuleError(f"no SKU satisfies the pin rule {rule.key!r}: {rule.statement}")


def measure_lens(golden: Path = GOLDEN) -> dict:
    """The rule-picked SKUs and the lowest enlargement (rounded down to 0.01) of the catalog."""
    from synthetic_ecommerce_data.core.drawing.sheet import magnifier

    candidates: list[tuple[dict, dict, bool]] = []
    lowest = 99.0
    for parent, variant, record in golden_skus(golden):
        width, height = drawn_size(parent["product_type"], record)
        lens = magnifier(width, height)
        if lens is not None:
            lowest = min(lowest, lens.k)
        candidates.append((parent, variant, lens is not None and not lens.handle))
    skus = {rule.key: pick_sku(rule, candidates) for rule in SKU_RULES}
    return {"skus": skus, "min_enlargement": int(lowest * 100) / 100}


# --- the title cap -----------------------------------------------------------------------------


@functools.cache
def measure_title_cut(seed: int | None = None) -> dict:
    """The titles the pre-#9284 cap cut would have landed inside a word, on a fresh build.

    The build is the default one, or the default one with ``seed``: the seed the catalog the
    other pins are measured on was built with. Spies on ``build_title`` rather than
    reimplementing the grammar: the segments and delimiters are the production ones and only
    the trimming rule is the old one.
    """
    from synthetic_ecommerce_data.core.config import GeneratorConfig
    from synthetic_ecommerce_data.core.naming import DELIMITER
    from synthetic_ecommerce_data.domains.industrial import finishing as finishing_module
    from synthetic_ecommerce_data.domains.industrial import generate as generate_module
    from synthetic_ecommerce_data.domains.industrial import titles as titles_module

    real = titles_module.build_title
    assembled: dict[str, tuple[str, int]] = {}

    def spy(item, segments, *, cap=100):
        pieces = [item]
        for segment in segments:
            pieces.append(DELIMITER + segment.text())
        title = real(item, segments, cap=cap)
        assembled.setdefault(title.text, ("".join(pieces), cap))
        return title

    # Both modules build titles: the thinning pass rebuilds a title the titles module made.
    titles_module.build_title = finishing_module.build_title = spy
    try:
        catalog = generate_module.generate(None if seed is None else GeneratorConfig(seed=seed))
    finally:
        titles_module.build_title = finishing_module.build_title = real

    # The breadth categories build their titles with ``naming.build_title`` directly and a simpler
    # grammar with no segment list to cut, so they are not part of what this measures.
    documents = [
        child
        for line in catalog.lines
        for child in line.children
        if line.spec_quality != "fast_and_cheap"
    ]
    if len(assembled) <= 100:
        raise PinRuleError("the spy recorded nothing; the title reconstruction is broken")
    word = set(string.ascii_letters + string.digits + './"-')
    over_cap = mid_word = 0
    for document in documents:
        if document.detail_image_id:
            continue  # a pack's title is its single's with a count in front (gen#14)
        full, cap = assembled[document.title]
        if len(full) <= cap:
            continue
        over_cap += 1
        if full[cap - 1] in word and full[cap] in word:
            mid_word += 1
    return {"documents": len(documents), "over_cap": over_cap, "mid_word": mid_word}


# --- the mutation bed's anchor -----------------------------------------------------------------


def find_anchor(nested_lines: Iterable[str]) -> dict:
    """The first product line, in catalog order, with more than one variant."""
    for line in nested_lines:
        parent = json.loads(line)
        if len(parent["variants"]) > 1:
            return {
                "rule": "the first product line in catalog order with more than one variant",
                "product_id": parent["product_id"],
                "product_type": parent["product_type"],
                "variant_count": parent["variant_count"],
                "first_sku": parent["variants"][0]["sku"],
                "second_sku": parent["variants"][1]["sku"],
                "order_multiple": parent["variants"][0]["order_multiple"],
            }
    raise PinRuleError("no product line has more than one variant: the mutation anchor rule")


def anchor_needles(anchor: dict) -> list[tuple[str, str]]:
    """``(file, text)`` for each text a planted golden-catalog row quotes.

    Each must occur in its file exactly once, or a row would plant its defect in the wrong
    place (or nowhere), and still read as a mutant that was caught.
    """
    sku, product_id = anchor["first_sku"], anchor["product_id"]
    image_id = f"{anchor['product_type']}/{product_id}/{sku}"
    url = f"/images/industrial/{image_id}.svg"
    return [
        ("flat.jsonl", f'"image_id": "{image_id}", "image_url": "{url}"'),
        # The line carries the same three keys for its own image; ``order_multiple`` is the
        # variant's key just before them, so the text is the variant's alone.
        (
            "nested.jsonl",
            f'"order_multiple": {anchor["order_multiple"]}, "image_id": "{image_id}", '
            f'"image_url": "{url}", "image_detail_url": "{url}"',
        ),
        ("flat.jsonl", f'{{"sku": "{sku}", "product_id": "{product_id}"'),
        (
            "nested.jsonl",
            f'"variant_count": {anchor["variant_count"]}, "variants": [{{"sku": "{sku}"',
        ),
    ]


def check_anchor(anchor: dict, texts: dict[str, str]) -> None:
    for name, needle in anchor_needles(anchor):
        found = texts[name].count(needle)
        if found != 1:
            raise PinRuleError(
                f"the mutation anchor {needle!r} occurs {found} times in {name}, not once "
                f"(rule: {anchor['rule']})"
            )


def measure_anchor(golden: Path = GOLDEN) -> dict:
    texts = {name: (golden / name).read_text("utf-8") for name in ("flat.jsonl", "nested.jsonl")}
    anchor = find_anchor(texts["nested.jsonl"].splitlines())
    check_anchor(anchor, texts)
    return anchor


# --- prose -------------------------------------------------------------------------------------


def prose_patterns(pins: dict) -> dict[str, str]:
    """A pattern per pinned figure that prose might restate, by the figure it quotes.

    Prose names the fixture instead of quoting a number, so a figure that moves cannot leave a
    stale one behind. Only the figures that appear in a stated shape are looked for; a bare count
    would match unrelated numbers.
    """
    patterns: dict[str, str] = {}
    lens = pins.get("lens", {})
    if "min_enlargement" in lens:
        patterns["lens.min_enlargement"] = rf"\bx{lens['min_enlargement']:.2f}\b"
    titles = pins.get("titles", {})
    if titles:
        patterns["titles.mid_word"] = (
            rf"\b{titles['mid_word']}\s+of\s+(?:the\s+default\s+catalog's\s+)?{titles['documents']:,}\b"
        )
        patterns["titles.over_cap"] = rf"\b{titles['over_cap']}\s+over\s+the\s+cap\b"
    return patterns


# --- the figures of one build and the golden slices --------------------------------------------


def _config(seed: int | None):
    from synthetic_ecommerce_data.core.config import GeneratorConfig

    return GeneratorConfig() if seed is None else GeneratorConfig(seed=seed)


def _tests_importable() -> None:
    tests = str(ROOT / "tests")
    if tests not in sys.path:
        sys.path.insert(0, tests)


def measure_figures(seed: int | None = None) -> dict:
    """``{module: figures}`` for each module ``tests/pinned.py`` names, on ``seed``'s build."""
    _tests_importable()
    import pinned

    config = _config(seed)
    return {name: importlib.import_module(name).measure_pins(config) for name in pinned.MODULES}


def write_slices(slices: Path, seed: int | None = None) -> list[str]:
    """Rewrite each ``<key>.jsonl`` in ``slices`` as type ``key``'s build; the names rewritten."""
    _tests_importable()
    import type_gates
    from synthetic_ecommerce_data.domains.industrial.generate import generate_type

    moved = []
    for path in sorted(slices.glob("*.jsonl")):
        records = type_gates.records(generate_type(_config(seed), path.stem))
        text = "".join(line + "\n" for line in records)
        if path.read_text("utf-8") != text:
            path.write_text(text, "utf-8")
            moved.append(path.name)
    return moved


# --- the fixture -------------------------------------------------------------------------------

#: Each measure reads the catalog directory and the seed it was built with (``None``: the default).
MEASURES: dict[str, Callable[[Path, int | None], dict]] = {
    "lens": lambda golden, seed: measure_lens(golden),
    "titles": lambda golden, seed: measure_title_cut(seed),
    "anchor": lambda golden, seed: measure_anchor(golden),
    "figures": lambda golden, seed: measure_figures(seed),
}


def measure_all(golden: Path = GOLDEN, seed: int | None = None) -> dict:
    return {name: measure(golden, seed) for name, measure in MEASURES.items()}


def load() -> dict:
    """The committed fixture."""
    return json.loads(PINS_PATH.read_text("utf-8"))


def dump(pins: dict) -> str:
    return json.dumps(pins, indent=2, sort_keys=True) + "\n"

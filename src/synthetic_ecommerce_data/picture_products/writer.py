"""Step 2: a product of our own around each picture of a manifest (gen#1022).

:func:`write` takes the checked rows of a picture manifest (:mod:`..picture_manifest`) and makes one
new generator product per picture of a type the book describes (``book.TYPES``). A row of another
type, or a fallback row, shows nothing to describe and makes no product. The product gets:

* a generator id (``BRD-PC`` and eight hex digits, from a hash), never the image id;
* a brand with a house style and one of that brand's ranges (:mod:`.book`);
* a title and a description, worded from the book;
* a price, and one SKU through the catalog's own row (``breadth_row.Row``);
* attributes that state what the picture shows: each part, and the measured width, height and
  depth in centimeters. Those sizes are the generator's own, chosen in the type's realistic
  range to fit the drawn proportions.

The product's picture is drawn again through ``drawings.render`` in the ``brand`` finish, under
the product's own id. Its angle and its brand mark both come from that id, so the file differs
from the picture the manifest was made from, and its name is the product id.
"""

from __future__ import annotations

import inspect
from collections.abc import Iterable
from dataclasses import dataclass

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data.domains.retail import kit, stable_ids
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import cw
from synthetic_ecommerce_data.picture_manifest import COLORS, TYPES, Fallback, Picture, is_count
from synthetic_ecommerce_data.picture_products import book

INCH = 2.54
DEPARTMENT = "Home"
PRICE_FACTOR = (0.6, 1.8)
PER_COUNT = 15.0


@dataclass(frozen=True)
class Product:
    """One product of our own: its catalog document and its picture."""

    doc: dict
    image_name: str
    svg: str


def defaults(type_: str) -> dict[str, str]:
    """The value each part of ``type_`` is drawn with when a picture leaves it out."""
    sig = inspect.signature(kit._draw(type_)).parameters
    return {part: sig[part].default for part in TYPES[type_]}


def _fraction(*parts: object) -> float:
    return int(stable_ids.digest(*parts)[:8], 16) / 0xFFFFFFFF


def _clamp(v: float, lo: float, hi: float) -> float:
    return min(max(v, lo), hi)


def measure(picture: Picture, product_id: str) -> tuple[int, int, int]:
    """Width, height and depth in centimeters: in the type's realistic ranges, at the picture's
    proportions. Depth is not drawn from the front, so it gives way first; a proportion no
    size of the type has takes the nearest one."""
    tb = book.TYPES[picture.type]
    rh, rd = picture.proportions
    (w0, w1), (h0, h1), (d0, d1) = tb.width, tb.height, tb.depth
    lo, hi = max(w0, h0 / rh, d0 / rd), min(w1, h1 / rh, d1 / rd)
    if lo > hi:
        lo, hi = max(w0, h0 / rh), min(w1, h1 / rh)
    if lo > hi:
        lo = hi = _clamp((h0 + h1) / 2 / rh, w0, w1)
    w = round(lo + _fraction("picture-size", product_id) * (hi - lo))
    w = int(_clamp(w, w0, w1))
    return w, int(_clamp(round(w * rh), h0, h1)), int(_clamp(round(w * rd), d0, d1))


def _parts(picture: Picture) -> list[tuple[str, str]]:
    """Every part the picture draws, in the shape's own order, a left-out one at its default."""
    given = dict(picture.parts)
    return [(p, given.get(p, v)) for p, v in defaults(picture.type).items()]


def _noun(picture: Picture, parts: dict[str, str]) -> str:
    noun = book.TYPES[picture.type].noun
    if isinstance(noun, str):
        return noun
    part, by_value = noun
    return by_value[parts[part]]


def _count_words(type_: str, part: str) -> tuple[str, str]:
    return book.COUNTS_OF.get((type_, part), book.COUNTS[part])


def _name(part: str) -> str:
    return book.NAMES.get(part, part.replace("_", " ").capitalize())


def title(picture: Picture, range_: str) -> str:
    parts = dict(_parts(picture))
    words = [range_]
    for part, value in parts.items():
        if is_count(picture.type, part):
            if value != "0" and (picture.type, part) not in book.UNTITLED_COUNTS:
                words.append(f"{value} {_count_words(picture.type, part)[0]}")
        elif word := book.TITLE_WORDS.get((picture.type, part), {}).get(value):
            words.append(word)
    return " ".join([*words, _noun(picture, parts)])


def description(picture: Picture, brand: str, range_: str, size: tuple[int, int, int]) -> str:
    parts = _parts(picture)
    w, h, d = size
    features = []
    for part, value in parts:
        if is_count(picture.type, part):
            one, many = _count_words(picture.type, part)
            n = int(value)
            word = many if n != 1 else one.lower()
            features.append(f"no {many}" if n == 0 else f"{n} {word}")
        else:
            features.append(f"{_name(part).lower()}: {value.replace('_', ' ')}")
    noun = _noun(picture, dict(parts))
    return (
        f"The {range_} {noun} from {brand}, {w} cm wide, {h} cm high and {d} cm deep, "
        f"in {picture.color.lower()}. Features: {'; '.join(features)}."
    )


def attributes(picture: Picture, size: tuple[int, int, int]) -> tuple[tuple, ...]:
    """What the picture shows: each part, and the measured size (canonical millimeters)."""
    out: list[tuple] = []
    for part, value in _parts(picture):
        if is_count(picture.type, part):
            one = book.COUNTS[part][0]
            out.append((f"{one.lower()}_count", f"{one} count", value, "C62", float(value)))
        else:
            out.append((part, _name(part), value.replace("_", " ").title()))
    for key, v in zip(("item_width", "item_height", "item_depth"), size, strict=True):
        out.append((key, f"Item {key.removeprefix('item_')}", str(v), "CMT", float(v * 10)))
    return tuple(out)


def price(picture: Picture, size: tuple[int, int, int]) -> float:
    """The type's price for a mid-sized piece, by its front's area, plus each door or drawer."""
    tb = book.TYPES[picture.type]
    w, h, _ = size
    mid = (sum(tb.width) / 2) * (sum(tb.height) / 2)
    counts = sum(int(v) for p, v in _parts(picture) if is_count(picture.type, p))
    raw = tb.price * _clamp(w * h / mid, *PRICE_FACTOR) + PER_COUNT * counts
    return float(max(9, round(raw / 10) * 10 - 1))


def product(picture: Picture) -> Product:
    """The product of our own around ``picture``, and its picture in the ``brand`` finish."""
    code = "PC" + stable_ids.digest("picture-product", picture.image_id)[:8].upper()
    product_id = f"BRD-{code}"
    brand = stable_ids.pick(sorted(book.RANGES), "picture-brand", product_id)
    range_ = stable_ids.pick(list(book.RANGES[brand]), "picture-range", product_id)
    size = measure(picture, product_id)
    tb = book.TYPES[picture.type]
    doc = Row(
        code, title(picture, range_), brand, DEPARTMENT, tb.path, tb.product_type,
        price(picture, size), picture.type, description(picture, brand, range_, size),
        (cw(picture.color, COLORS[picture.color]),), attributes(picture, size),
        params=tuple(_parts(picture)), product_line=range_,
    ).doc()  # fmt: skip
    w, h, d = size
    svg = drawings.render(
        picture.type,
        {"color": COLORS[picture.color], "width": w / INCH, "height": h / INCH,
         "depth": d / INCH, **dict(picture.parts)},
        "brand", product_id=product_id, brand=brand,
    )  # fmt: skip
    return Product(doc=doc, image_name=f"{product_id}.svg", svg=svg)


def write(pictures: Iterable[Picture | Fallback]) -> list[Product]:
    """One product per picture of a type the book describes; two pictures that would share a
    product id are refused."""
    out = [product(p) for p in pictures if isinstance(p, Picture) and p.type in book.TYPES]
    ids = [p.doc["product_id"] for p in out]
    if len(set(ids)) != len(ids):
        raise ValueError("two pictures hash to one product id")
    return out

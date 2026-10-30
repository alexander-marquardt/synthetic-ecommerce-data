"""The real brands the retail catalogue may name, and the guard that refuses all others (gen#341).

README "Every name is invented" holds for every brand but these. The maintainer's ruling: Nike
(2026-10-15, gen#341) is real, so a shopper who types ``nike air max`` finds products. A real brand
is TEXT ONLY: its name is in the title, the ``brand`` field and the description, and no drawing
carries its logo, mark, swoosh, wordmark or trade dress (:func:`house_styles.logo` draws nothing
for a style whose mark is ``none``). Apple, iPhone and iPad were ruled out on 2026-10-30 (gen#720):
the devices are Grape Computer's GrapePhone and GrapePad.

:data:`ALLOWED` is the one list of the exceptions. :data:`KNOWN_REAL` is the real brand names the
guard refuses: a name a contributor might reach for (sportswear, electronics, retail).
:data:`BRAND_ONLY` is the real brands that are also plain words, refused in the ``brand`` field
alone. Adding an exception is a maintainer ruling: move the name from :data:`KNOWN_REAL` to
:data:`ALLOWED` in the same change as the README and the issue that records the ruling.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

#: Real brands the maintainer has ruled in, text only: Nike (gen#341).
ALLOWED: tuple[str, ...] = ("Nike",)

#: Real brand names the catalogue refuses in any field (unambiguous ones: no "gap" or "orange").
KNOWN_REAL: tuple[str, ...] = (
    "Adidas", "Puma", "Reebok", "Asics", "New Balance", "Under Armour", "Converse", "Vans",
    "Skechers", "Fila", "Umbro", "Hoka", "Brooks", "Mizuno", "Saucony", "Lululemon", "Gymshark",
    "Levi's", "Wrangler", "Lee Cooper", "Zara", "H&M", "Uniqlo", "Primark", "Next",
    "Dr Martens", "Clarks", "Timberland", "North Face", "Patagonia", "Columbia", "Barbour",
    "iPhone", "iPad", "Samsung", "Sony", "Huawei", "Nokia", "Google Pixel", "Dell", "Lenovo",
    "Microsoft", "Bosch",
    "Xiaomi", "Motorola", "OnePlus", "Oppo", "Vivo", "Realme", "Asus", "Acer", "Logitech", "Anker",
    "Belkin", "JBL", "Bose", "Garmin", "Fitbit", "Kindle", "Amazon Fire", "Razer", "Corsair",
    "Dyson", "Hoover", "Siemens", "Whirlpool", "Miele", "Ikea", "Nestle", "Cadbury", "Heinz",
    "Coca-Cola", "Pepsi", "Tesco", "Asda", "Sainsbury's", "Waitrose",
)  # fmt: skip

#: Real brands that are also a plain word: "Apple" is the fruit in a title, so only the ``brand``
#: field refuses it (gen#720).
BRAND_ONLY: tuple[str, ...] = ("Apple",)


def _pattern(names: Iterable[str]) -> re.Pattern[str]:
    alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(rf"(?<![A-Za-z0-9])(?:{alt})(?![A-Za-z0-9])", re.IGNORECASE)


_REFUSED = _pattern(KNOWN_REAL)
_REFUSED_BRAND = _pattern((*KNOWN_REAL, *BRAND_ONLY))


def check(docs: Iterable[dict]) -> list[str]:
    """One line per document whose brand, title or description names a real brand that is not in
    :data:`ALLOWED`. An empty list is a catalogue that names only invented brands and the
    ruled-in exceptions."""
    found = []
    for d in docs:
        for field in ("brand", "title", "description"):
            refused = _REFUSED_BRAND if field == "brand" else _REFUSED
            m = refused.search(str(d.get(field) or ""))
            if m:
                found.append(f"{d.get('product_id')}: {field} names the real brand {m.group(0)!r}")
    return found

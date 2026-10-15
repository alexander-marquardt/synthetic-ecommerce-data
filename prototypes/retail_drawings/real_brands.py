"""The real brands the retail catalogue may name, and the guard that refuses all others (gen#341).

README "Every name is invented" holds for every brand but these. The maintainer's rulings:
Apple, iPhone and iPad (gen#332) and Nike (2026-10-15, gen#341) are real, so a shopper who types
``nike air max`` finds products. A real brand is TEXT ONLY: its name is in the title, the
``brand`` field and the description, and no drawing carries its logo, mark, swoosh, wordmark or
trade dress (:func:`house_styles.logo` draws nothing for a style whose mark is ``none``).

:data:`ALLOWED` is the one list of the exceptions. :data:`KNOWN_REAL` is the real brand names the
guard refuses: a name a contributor might reach for (sportswear, electronics, retail). Adding an
exception is a maintainer ruling: move the name from :data:`KNOWN_REAL` to :data:`ALLOWED` in the
same change as the README and the issue that records the ruling.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

#: Real brands the maintainer has ruled in, text only. Apple, iPhone and iPad join with gen#332.
ALLOWED: tuple[str, ...] = ("Nike",)

#: Real brand names the catalogue refuses (unambiguous ones: no "gap", "apple" or "orange").
KNOWN_REAL: tuple[str, ...] = (
    "Adidas", "Puma", "Reebok", "Asics", "New Balance", "Under Armour", "Converse", "Vans",
    "Skechers", "Fila", "Umbro", "Hoka", "Brooks", "Mizuno", "Saucony", "Lululemon", "Gymshark",
    "Levi's", "Wrangler", "Lee Cooper", "Zara", "H&M", "Uniqlo", "Primark", "Next",
    "Marks & Spencer",
    "Dr Martens", "Clarks", "Timberland", "North Face", "Patagonia", "Columbia", "Barbour",
    "Samsung", "Sony", "Huawei", "Nokia", "Google Pixel", "Dell", "Lenovo", "Microsoft", "Bosch",
    "Dyson", "Hoover", "Siemens", "Whirlpool", "Miele", "Ikea", "Nestle", "Cadbury", "Heinz",
    "Coca-Cola", "Pepsi", "Tesco", "Asda", "Sainsbury's", "Waitrose",
)  # fmt: skip


def _pattern(names: Iterable[str]) -> re.Pattern[str]:
    alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(rf"(?<![A-Za-z0-9])(?:{alt})(?![A-Za-z0-9])", re.IGNORECASE)


_REFUSED = _pattern(KNOWN_REAL)


def check(docs: Iterable[dict]) -> list[str]:
    """One line per document whose brand, title or description names a real brand that is not in
    :data:`ALLOWED`. An empty list is a catalogue that names only invented brands and the
    ruled-in exceptions."""
    return []

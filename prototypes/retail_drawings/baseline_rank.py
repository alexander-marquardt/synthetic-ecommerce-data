"""The no-policy baseline of the retail demo, ranked in plain Python (gen#125).

What the retailer's live search does without PRISM's interpretation: BM25 over the
title (x2) and the description, the best field plus 0.3 of the other (the
``multi_match`` of :func:`real_classes.text_query`), times the popularity boost of
:data:`real_classes.POPULARITY` (``log1p`` of ``sold_last_5_days``, x1.5 in the
bestseller top 15). A query word with a search-time synonym reads as all of them
(:data:`real_classes.SYNONYMS`: ``balloon`` is also ``barrel``). Every document
with at least one query word is scored, so a distractor that shares one word
competes, as it does on the live site.

This ranks a whole built catalog (:func:`rank`), so a test can hold that a demo
query fails without a policy on the 76K-SKU build, not only on the 300-style proof
corpus that :mod:`es_proof` runs on Elasticsearch. Tokens follow
:func:`distractors.tokens`, a plural strip, not Elasticsearch's English stemmer:
the order is a faithful proxy, not byte for byte. Standard library only.
"""

from __future__ import annotations

import math
from collections import Counter

from distractors import tokens

K1, B, TIE = 1.2, 0.75, 0.3
TITLE_BOOST = 2.0
#: ``balloon => balloon, barrel``: a query word and the words that also match it.
SYNONYMS = {"balloon": ("balloon", "barrel")}
BESTSELLER_TOP = 15


class Index:
    """Per-field BM25 statistics over a catalog, with an inverted index for recall."""

    def __init__(self, catalog: list[dict]) -> None:
        self.catalog = catalog
        self.n = len(catalog)
        self.fields: dict[str, list[Counter[str]]] = {
            "title": [Counter(tokens(d["title"])) for d in catalog],
            "description": [Counter(tokens(d.get("description", ""))) for d in catalog],
        }
        self.avgdl = {f: sum(sum(c.values()) for c in cs) / self.n for f, cs in self.fields.items()}
        self.df: dict[str, Counter[str]] = {
            f: Counter(t for c in cs for t in c) for f, cs in self.fields.items()
        }
        self.postings: dict[str, set[int]] = {}
        for cs in self.fields.values():
            for i, c in enumerate(cs):
                for t in c:
                    self.postings.setdefault(t, set()).add(i)

    def _idf(self, field: str, term: str) -> float:
        n = self.df[field][term]
        return math.log(1 + (self.n - n + 0.5) / (n + 0.5))

    def _bm25(self, field: str, i: int, term: str) -> float:
        counts = self.fields[field][i]
        tf = counts[term]
        if not tf:
            return 0.0
        dl = sum(counts.values())
        norm = tf + K1 * (1 - B + B * dl / self.avgdl[field])
        return self._idf(field, term) * tf * (K1 + 1) / norm

    def _field_score(self, field: str, i: int, query: list[str]) -> float:
        """Sum over the query words of the best score among a word and its synonyms."""
        total = 0.0
        for word in query:
            alts = SYNONYMS.get(word, (word,))
            total += max(self._bm25(field, i, a) for a in alts)
        return total

    def text_score(self, i: int, query: list[str]) -> float:
        t = TITLE_BOOST * self._field_score("title", i, query)
        d = self._field_score("description", i, query)
        return max(t, d) + TIE * min(t, d)

    def candidates(self, query: list[str]) -> set[int]:
        out: set[int] = set()
        for word in query:
            for alt in SYNONYMS.get(word, (word,)):
                out |= self.postings.get(alt, set())
        return out


def popularity(doc: dict) -> float:
    boost = math.log1p(doc.get("sold_last_5_days", 1))
    rank = doc.get("bestseller_rank")
    return boost * (1.5 if rank is not None and rank <= BESTSELLER_TOP else 1.0)


def rank(
    index: Index, query: str, size: int = 10, *, popular: bool = True
) -> list[dict]:
    """The top ``size`` documents for ``query``: text score times popularity, ties by id.

    ``popular=False`` ranks by text score alone. A test of which TYPE a query's words find uses it:
    ``sold_last_5_days`` is drawn from one seeded stream, so adding a type elsewhere moves the
    draws of every later product and a decoy can outsell the type (#432).
    """
    words = tokens(query)
    scored = [
        (
            index.text_score(i, words) * (popularity(index.catalog[i]) if popular else 1.0),
            index.catalog[i],
        )
        for i in index.candidates(words)
    ]
    scored.sort(key=lambda s: (-s[0], s[1]["product_id"]))
    return [d for _, d in scored[:size]]

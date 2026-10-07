"""Review plant (#82 round 1): a bearing ratings table read on one basis.

Within one ISO 15 diameter series a larger bore never carries a lower load
rating or a higher limiting speed. A table whose rows come from two makers
on different rating bases breaks that at the seam, and the shopper sees it
on the published Max. RPM: a 609 (9x24 mm) rated slower than a 6000
(10x26 mm). The PR's own rule drops a number that breaks the series' order;
this holds the rows it keeps to the same rule.
"""

from __future__ import annotations

import itertools

from synthetic_industrial_products.catalog import newtypes


def _series(number: str) -> str:
    """The ISO 15 diameter series: the second digit of 60/62/63 and of the
    single-digit 60x/62x numbers."""
    return number[1]


def test_each_metric_series_is_in_rating_order_by_bore():
    by_series: dict[str, list[tuple[int, str]]] = {}
    for number, bore, _od, _width in newtypes._BEARINGS_METRIC:
        by_series.setdefault(_series(number), []).append((bore, number))
    breaks = []
    for series, rows in sorted(by_series.items()):
        rows.sort()
        for (_, small), (_, large) in itertools.pairwise(rows):
            c1, c01, rpm1 = newtypes.BEARING_RATINGS[small]
            c2, c02, rpm2 = newtypes.BEARING_RATINGS[large]
            if c2 < c1 or c02 < c01 or rpm2 > rpm1:
                breaks.append((series, small, large))
    assert breaks == []

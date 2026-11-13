"""The build's two whole-catalogue passes hold nothing that grows with the rows (gen#952).

Measured on main at ``--lines 39000`` (176,348 SKUs), the catalogue itself was 499 MiB,
but the build peaked at 3,866 MiB, from two passes that each held the catalogue again:

* ``price_report.collect`` stored every within-cell SKU pair: 2.2 GiB, growing with the
  square of a cell's members, so about 17.7 GiB at 500K SKUs;
* ``_measured_figures`` read ``flat.jsonl`` back as one list of dicts: 3.3 GiB.

Both now walk what they read: a cell's pairs are generated when a row counts them, and
the written files are read one line at a time.
"""

from __future__ import annotations

import json
import sys
import tracemalloc
from pathlib import Path

from synthetic_ecommerce_data import generate_cli as cli
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import price_report
from synthetic_ecommerce_data.domains.industrial.generate import generate

#: Bytes a stored pair costs at least: its two-tuple and its list slot. The census's own
#: state (cells, specs, each SKU's type) grows with the SKUs, the pairs with the square
#: of a cell: at the golden size, storing them alone costs twice what the rest does.
STORED_PAIR = sys.getsizeof(("", "")) + 8


def _peak(run) -> int:
    tracemalloc.start()
    try:
        run()
        return tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()


def _write_build(out: Path, rows: int) -> None:
    """``rows`` flat documents and drawings, alike so nothing the figures keep grows."""
    out.mkdir(parents=True)
    flat = {
        "product_type": "widget",
        "product_id": "P-1",
        "brand": "Acme",
        "facets": {},
        "facets_num": {},
        "attributes": [],
        "title": "w" * 4000,
    }
    image = {
        "image_id": "widget/P-1/S-1",
        "product_type": "widget",
        "bytes": 10,
        "geometry": "drawn",
    }
    line = json.dumps(flat) + "\n"
    (out / "flat.jsonl").write_text(line * rows, encoding="utf-8")
    (out / "images.jsonl").write_text((json.dumps(image) + "\n") * rows, encoding="utf-8")


def test_the_figures_pass_holds_no_list_of_rows(tmp_path):
    """Twice the rows, the same peak: ``_measured_figures`` keeps no parsed row."""
    _write_build(tmp_path / "small", 1000)
    _write_build(tmp_path / "large", 2000)
    small = cli._measured_figures(tmp_path / "small")
    large = cli._measured_figures(tmp_path / "large")
    assert small["drawings"]["count"] == 1000
    assert large["drawings"]["count"] == 2000

    peak_small = _peak(lambda: cli._measured_figures(tmp_path / "small"))
    peak_large = _peak(lambda: cli._measured_figures(tmp_path / "large"))

    # A held list doubles (4 MB more here); a walk adds nothing but noise.
    assert peak_large < peak_small * 1.25 + 256 * 1024, (peak_small, peak_large)


def test_the_price_census_stores_no_within_cell_pair():
    """``collect`` costs less than its pairs alone would: they are generated, never stored."""
    catalog = generate(GeneratorConfig())
    collected = None

    def run() -> None:
        nonlocal collected
        collected = price_report.collect(catalog)

    peak = _peak(run)
    assert collected is not None
    pairs = sum(
        1
        for by_type in (collected.pairs, collected.length_pairs)
        for type_pairs in by_type.values()
        for _ in type_pairs
    )
    assert pairs > 100_000, pairs  # the golden build pairs ~190K: enough to see them stored
    assert peak < STORED_PAIR * pairs, (peak, STORED_PAIR * pairs)

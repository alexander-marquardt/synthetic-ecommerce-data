"""The price rows out of band on any of several seeds of the default build (#891).

    uv run python scripts/price_seed_survey.py 20260917 20260918 ... 20260928
    uv run python scripts/price_seed_survey.py --level 20260917 ...   # p50 and p90/p10 only

Builds the default catalog at each seed (six at a time, about 15 s each), scores its price
rows, and prints each row that lands out of band on one seed or more: how many seeds, its
band at the first seed, and its figure on each seed in order, ``*`` before a figure out of
band. The last line counts the rows. ``price.FITTED`` is fitted at the default seed, so a row
out here is one whose band a build on another seed does not meet.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.measure import measure

LEVEL_PREFIXES = ("price p50 (USD): ", "price p90/p10: ")


def price_rows(seed: int) -> dict[str, tuple[float, tuple[float, float], bool]]:
    """Each price row of the default build at ``seed``: (figure, band, within)."""
    config = GeneratorConfig(seed=seed)
    stats = measure(generate(config), config)
    return {
        row.name: (row.achieved, row.band, row.within)
        for row in stats["comparisons"]
        if row.band is not None and row.name.startswith("price ")
    }


def survey(by_seed: list[dict], level_only: bool) -> list[str]:
    """The report's lines for the rows of ``by_seed`` (one dict per seed, in order)."""
    names = sorted({name for rows in by_seed for name in rows})
    if level_only:
        names = [name for name in names if name.startswith(LEVEL_PREFIXES)]
    lines = []
    for name in names:
        figures = [rows.get(name) for rows in by_seed]
        out = sum(1 for figure in figures if figure and not figure[2])
        if not out:
            continue
        band = next(figure[1] for figure in figures if figure)
        shown = " ".join(
            ("" if figure[2] else "*") + f"{figure[0]:.3g}" if figure else "-" for figure in figures
        )
        lines.append(f"{out:2d}/{len(by_seed)} {name} band=[{band[0]:.4g}, {band[1]:.4g}]: {shown}")
    lines.append(f"rows out of band on at least one seed: {len(lines)}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("seeds", nargs="+", type=int)
    parser.add_argument("--level", action="store_true", help="the p50 and p90/p10 rows only")
    args = parser.parse_args(argv)
    with ProcessPoolExecutor(max_workers=min(len(args.seeds), 6)) as pool:
        by_seed = list(pool.map(price_rows, args.seeds))
    print("\n".join(survey(by_seed, args.level)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

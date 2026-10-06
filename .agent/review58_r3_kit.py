"""Kit p50 / p90/p10 and the exception bound at both builds, for a kit price
scaled by each factor (review round 3 of #58)."""

from dataclasses import replace

from synthetic_industrial_products.catalog import price, price_report
from synthetic_industrial_products.catalog.config import HUNDRED_K_LINES, GeneratorConfig
from synthetic_industrial_products.catalog.generate import generate

NAMES = ("price p50 (USD): kit_assortment", "price p90/p10: kit_assortment")
base = price.MODELS["kit_assortment"]
for factor in (2.0, 1.25, 1.2, 0.85, 0.8, 0.5):
    price.MODELS["kit_assortment"] = replace(base, anchor=base.anchor * factor)
    cells = []
    for build, config in enumerate((GeneratorConfig(), GeneratorConfig(lines=HUNDRED_K_LINES))):
        for row in price_report.price_comparisons(generate(config)):
            if row.name == NAMES[0]:
                limit = price.EXCEPTION_DRIFT * price_report.band_miss(
                    price.EXCEPTED_FIGURES[row.name][build], row.band
                )
                miss = price_report.band_miss(row.achieved, row.band)
                held = price_report.exception_holds(row, build)
                cells.append(
                    f"b{build} p50 {row.achieved:.2f} miss {miss:.3f}/{limit:.3f} holds={held} within={row.within}"
                )
    print(factor, " | ".join(cells), flush=True)
price.MODELS["kit_assortment"] = base

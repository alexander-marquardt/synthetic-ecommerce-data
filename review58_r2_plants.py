"""Round-2 review plants for #58: revert each round-1 fix, and mutate the fit
and band code; report which tests in tests/test_price.py go red.

    uv run python review58_r2_plants.py [plant-id ...]

Each plant is a single exact-text substitution, applied, scored, restored.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
PKG = "src/synthetic_industrial_products/catalog/"

PLANTS: dict[str, tuple[str, str, str, str]] = {
    # --- reverts of round-1 fixes ---
    "R1-length-term-off": (
        PKG + "price.py",
        "        length_slope=(length.slope if length else 0.0) if length_slope is None else length_slope,",
        "        length_slope=0.0,",
        "s1: price has no length term",
    ),
    "R1b-bearing-brand-ladder": (
        PKG + "price.py",
        '_model("bearing_radial_ball", 25.55, 0.5, 0.080, 0.086)',
        '_model("bearing_radial_ball", 25.55, 0.5, 1.163, 0.084)',
        "s1b: bearing back on the bc0b907 group/sku sigmas",
    ),
    "R2a-tap-no-ladder": (
        PKG + "price.py",
        "            price_step=0.19,\n",
        "",
        "s2: tap list-price ladder removed (no ties)",
    ),
    "R2b-tap-slope-hand-cut": (
        PKG + "price.py",
        '"tap_spiral_point",\n            16.55,\n            0.25,',
        '"tap_spiral_point",\n            16.55,\n            0.25,\n            slope=0.40,',
        "s2: tap slope cut by hand, no SLOPE_CUTS reason",
    ),
    "R3a-drill-99-off-census": (
        PKG + "price.py",
        '        ".99": 0.0068,\n        ".97": 0.0056,',
        '        ".99": 0.30,\n        ".97": 0.0056,',
        "s3: drill .99 share 30%",
    ),
    "R3b-endings-band-wide": (
        PKG + "price_report.py",
        "    width = CENSUS_SES * math.sqrt(_ending_variance(cls, type_counts))",
        "    width = 30 * math.sqrt(_ending_variance(cls, type_counts))",
        "s3: ending bands 10x wider (the old +/-97% .99 band)",
    ),
    "R5-tier-swap": (
        PKG + "brands.py",
        None,
        None,
        "s5 3a: cutting-tool economy/premium labels trade tiers (filled at runtime)",
    ),
    # --- mutants on the fit and band code ---
    "M1-twice-threshold-3x": (
        PKG + "price_report.py",
        "    twice = sum(prices[small] >= 2 * prices[big] for big, small, _ in pairs)",
        "    twice = sum(prices[small] >= 3 * prices[big] for big, small, _ in pairs)",
        "2x row counts 3x inversions",
    ),
    "M2-equal-band-10x": (
        PKG + "price_report.py",
        "    width = CENSUS_SES * math.sqrt(share * (1 - share) / census.n_pairs)",
        "    width = 10 * CENSUS_SES * math.sqrt(share * (1 - share) / census.n_pairs)",
        "equal-price band 10x wider",
    ),
    "M3-brand-band-high-x5": (
        PKG + "price_report.py",
        "        figure.spread_p50 * max(BRAND_SPREAD_BAND[1], high),",
        "        figure.spread_p50 * max(BRAND_SPREAD_BAND[1], high) * 5,",
        "brand-spread band top 5x higher",
    ),
    "M4-share-band-wide": (
        PKG + "price_report.py",
        "    width = max(MONOTONE_BAND, CENSUS_SES * math.sqrt(target * (1 - target) / n_pairs))",
        "    width = max(0.4, CENSUS_SES * math.sqrt(target * (1 - target) / n_pairs))",
        "order/length share bands +/-0.40",
    ),
    "M5-bearing-pin-worse": (
        PKG + "price.py",
        '_model("bearing_radial_ball", 25.55, 0.5, 0.080, 0.086)',
        '_model("bearing_radial_ball", 25.55, 0.5, 0.000, 0.000)',
        "bearing shortfall worsens (all noise off)",
    ),
    "M6-wheel-pin-worse": (
        PKG + "price.py",
        '_model("wheel_depressed_center", 7.322, 4.5, 0.694, 0.314)',
        '_model("wheel_depressed_center", 7.322, 4.5, 1.800, 0.314)',
        "wheel brand-spread shortfall worsens (group sigma 1.8)",
    ),
    "M7-twice-target-zero": (
        PKG + "price_report.py",
        "    if not log_ratios or not 0.0 < less < 0.5:\n        return 0.0",
        "    if True:\n        return 0.0",
        "implied 2x target always 0",
    ),
}


def tier_swap(text: str) -> str:
    # Wendlow Tool (ECONOMY) <-> Varrick Precision (PREMIUM).
    econ = '"Stone Wicket", "Wendlow Tool"}'
    prem = '        "Varrick Precision",\n'
    assert text.count(econ) == 1 and text.count(prem) == 1
    text = text.replace(econ, '"Stone Wicket", "Varrick Precision"}')
    return text.replace(prem, '        "Wendlow Tool",\n')


def run(pid: str) -> str:
    rel, old, new, what = PLANTS[pid]
    path = REPO / rel
    original = path.read_text()
    if old is None:
        mutated = tier_swap(original)
    else:
        assert original.count(old) == 1, f"{pid}: anchor matches {original.count(old)}"
        mutated = original.replace(old, new)
    path.write_text(mutated)
    try:
        out = subprocess.run(
            ["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_price.py"],
            cwd=REPO, capture_output=True, text=True,
        ).stdout
    finally:
        path.write_text(original)
    failed = sorted({m.split("::")[1].split("[")[0] for m in re.findall(r"FAILED (\S+)", out)})
    verdict = "RED " + ", ".join(failed) if failed else "GREEN"
    return f"{pid} ({what}): {verdict}"


if __name__ == "__main__":
    for pid in sys.argv[1:] or PLANTS:
        print(run(pid), flush=True)

"""Re-measure every figure and SKU the tests pin on ``golden-catalog/`` (#50).

After a regeneration::

    uv run ecom-generate build --out golden-catalog && uv run python scripts/measure_pins.py

writes ``tests/data/golden_pins.json``. The rules are in ``scripts/golden_pins.py``. A rule that no
SKU of the catalog satisfies stops the script and names the rule: it writes nothing and never
falls back to a weaker SKU.

``--check`` writes nothing and exits 1, printing the fixture's diff, when the committed fixture is
not what the committed catalog measures. The diff of the fixture is the review artifact of a
regeneration: a figure that moved for no stated reason is questioned there.
"""

from __future__ import annotations

import argparse
import difflib
import sys

import golden_pins


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--check", action="store_true", help="compare the committed fixture, write nothing"
    )
    args = parser.parse_args(argv)
    try:
        measured = golden_pins.dump(golden_pins.measure_all())
    except golden_pins.PinRuleError as error:
        print(f"measure_pins: {error}", file=sys.stderr)
        return 1
    path = golden_pins.PINS_PATH
    committed = path.read_text("utf-8") if path.exists() else ""
    diff = "".join(
        difflib.unified_diff(
            committed.splitlines(keepends=True),
            measured.splitlines(keepends=True),
            "committed",
            "measured",
        )
    )
    if args.check:
        if diff:
            print(diff, file=sys.stderr)
            print(f"the fixture is stale; run {golden_pins.REGENERATE}", file=sys.stderr)
            return 1
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(measured, "utf-8")
    print(diff or f"{path.name}: no figure moved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

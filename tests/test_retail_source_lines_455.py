"""No retail source file holds more than 1,000 lines (gen#455).

Changing one product used to mean reading files of 1,000 to 1,600 lines: the cost gen#351
measured at about 55K tokens per type. The repository's file-size gate caps a file at 1,750
lines, so it does not hold this tighter limit. A file that reaches the cap moves a family or a
table into a sibling module, as ``breadth_rows.py`` and ``decoy_product_words.py`` did.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "src" / "synthetic_ecommerce_data" / "domains" / "retail"
CAP = 1000


def over_cap(root: Path) -> dict[str, int]:
    """Each Python file under ``root`` longer than :data:`CAP`, with its line count."""
    sizes = {p: len(p.read_text(encoding="utf-8").splitlines()) for p in root.rglob("*.py")}
    return {str(p.relative_to(root)): n for p, n in sizes.items() if n > CAP}


def test_no_retail_source_file_is_over_the_cap() -> None:
    assert len(list(RETAIL.rglob("*.py"))) > 600, "the walk no longer reaches the retail modules"
    assert over_cap(RETAIL) == {}


def test_the_cap_names_the_first_line_past_it(tmp_path: Path) -> None:
    (tmp_path / "at_cap.py").write_text("x = 1\n" * CAP, encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "past_cap.py").write_text("x = 1\n" * (CAP + 1), encoding="utf-8")
    assert over_cap(tmp_path) == {"nested/past_cap.py": CAP + 1}

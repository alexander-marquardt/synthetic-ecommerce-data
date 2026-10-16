"""A build whose audit refuses must leave nothing behind (gen#253).

``ecom-generate build --out X`` runs three audits: the image audit, the product
audit and the non-copying audit. They used to sit after the first writes, so a
refusal exited 1 with ``flat.jsonl``, ``nested.jsonl`` and ``images.jsonl``
already on disk -- and ``--out golden-catalog`` overwrote the tracked golden
files with the catalog the audit had just refused.

Each audit is forced to fail here, rather than by a mutated generator, so the
test pins the ORDER (audit, then write) and not any one audit's rule.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from synthetic_ecommerce_data import generate_cli as cli
from synthetic_ecommerce_data.core import noncopy

#: A small catalog: the audits are forced, so the build only has to get far enough.
SMALL = ["build", "--lines", "200"]


def _refuse_images(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_check_images", lambda catalog, referenced: ["forced image problem"])


def _refuse_product(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "distribution_problems", lambda stats, config: ["forced product"])


def _refuse_noncopy(monkeypatch: pytest.MonkeyPatch) -> None:
    real = noncopy.audit

    def audit(catalog):
        return {**real(catalog), "sku_collisions": ["forced"]}

    monkeypatch.setattr(cli.noncopy, "audit", audit)


REFUSALS = {
    "image-audit": (_refuse_images, "image audit FAILED"),
    "product-audit": (_refuse_product, "product audit FAILED"),
    "noncopy-audit": (_refuse_noncopy, "non-copying audit FAILED"),
}


def _digest(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.mark.parametrize("refusal", sorted(REFUSALS))
def test_a_refused_build_leaves_no_output_behind(refusal, tmp_path, monkeypatch, capsys):
    arrange, message = REFUSALS[refusal]
    arrange(monkeypatch)
    out = tmp_path / "fresh"

    assert cli.main([*SMALL, "--out", str(out)]) == 1

    assert message in capsys.readouterr().err
    left = _digest(out) if out.exists() else {}
    assert left == {}, f"a refused build wrote {sorted(left)}"


@pytest.mark.parametrize("refusal", sorted(REFUSALS))
def test_a_refused_build_does_not_overwrite_the_existing_catalog(
    refusal, tmp_path, monkeypatch, capsys
):
    """The ``--out golden-catalog`` case: the tracked files must survive a refusal."""
    out = tmp_path / "golden"
    out.mkdir()
    for name in ("flat.jsonl", "nested.jsonl", "images.jsonl", "render.jsonl", "stats.json"):
        (out / name).write_text(f"previous {name}\n", encoding="utf-8")
    before = _digest(out)
    arrange, _ = REFUSALS[refusal]
    arrange(monkeypatch)

    assert cli.main([*SMALL, "--out", str(out)]) == 1

    capsys.readouterr()
    assert _digest(out) == before

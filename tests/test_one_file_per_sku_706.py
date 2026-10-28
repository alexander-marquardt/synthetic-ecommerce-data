"""One image release for the combined catalog, and one image file per SKU (gen#706).

The retail image id was a digest of the drawing spec, so the SKUs of one colorway, pack factor and
size rung shared a file: the 173,222-SKU release shipped 94,230 files and 105,752 SKUs shared one.
Each SKU now has its own file, a copy when two SKUs draw the same picture, so one SKU's color,
size or shape can change later without touching another's. The industrial and retail drawings ship
as one archive under one pin, and the release refuses a set where two SKUs share a file, a SKU has
no file, or a file names no SKU.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core import bundle

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
for _path in (RETAIL, ROOT / "scripts"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import export  # noqa: E402 -- the prototype's own directory is its import root
import image_release  # noqa: E402
import open_pin_bump_pr as pins  # noqa: E402

GOLDEN = ROOT / "golden-catalog"


@pytest.fixture(scope="module")
def documents() -> list[dict[str, Any]]:
    return export.documents()


def test_every_retail_sku_has_its_own_image_file(documents) -> None:
    urls = [v["image_url"] for d in documents for v in d["variants"]]
    assert len(set(urls)) == len(urls)


def test_two_skus_of_one_drawing_still_have_two_files(documents) -> None:
    """The sizes of one rung draw one picture, and each has its own copy of it."""
    rec = next(r for r in image_release.records() if r["product_id"] == "JEA-HARROW")
    by_drawing: dict[str, list[str]] = {}
    for sku in rec["skus"]:
        by_drawing.setdefault(export.drawing_id(rec, sku), []).append(export.image_id(rec, sku))
    shared = next(ids for ids in by_drawing.values() if len(ids) > 1)
    assert len(set(shared)) == len(shared)
    files = dict(image_release.image_files([rec]))
    first, second = (files[image_release.member_path(i)] for i in shared[:2])
    assert first == second, "one drawing, two identical copies"


def test_two_skus_sharing_a_file_is_refused() -> None:
    skus = [("A-1", "/images/retail/x.svg"), ("A-2", "/images/retail/x.svg")]
    problems = bundle.sku_file_problems(skus, ["retail/x.svg"])
    assert problems == ["2 SKUs share 1 file(s): retail/x.svg (A-1, A-2)"]


def test_a_sku_with_no_file_is_refused() -> None:
    skus = [("A-1", "/images/retail/a.svg"), ("A-2", "/images/retail/b.svg")]
    problems = bundle.sku_file_problems(skus, ["retail/a.svg"])
    assert problems == ["1 SKU(s) have no file: A-2 (retail/b.svg)"]


def test_a_file_no_sku_names_is_refused() -> None:
    problems = bundle.sku_file_problems([("A-1", "/images/retail/a.svg")], ["retail/a.svg", "z"])
    assert problems == ["1 file(s) name no SKU: z"]


def test_a_clean_set_has_no_problem() -> None:
    skus = [("A-1", "/images/retail/a.svg"), ("A-2", "/images/industrial/b.svg")]
    assert bundle.sku_file_problems(skus, ["retail/a.svg", "industrial/b.svg"]) == []


def test_the_command_refuses_a_set_with_a_sku_missing_its_file(tmp_path, monkeypatch, capsys):
    real = image_release.image_files
    monkeypatch.setattr(image_release, "image_files", lambda recs=None: real(recs)[1:])
    code = image_release.main(["--out", str(tmp_path / "out")])
    assert code == 1
    assert "REFUSED" in capsys.readouterr().err
    assert not (tmp_path / "out").exists(), "a refused set writes nothing"


def test_one_archive_carries_both_halves_under_one_digest(tmp_path) -> None:
    out, archive = tmp_path / "out", tmp_path / "images.tar.gz"
    run = subprocess.run(
        [sys.executable, str(RETAIL / "image_release.py"), "--industrial-catalog", str(GOLDEN),
         "--out", str(out), "--archive", str(archive)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 0, run.stderr[-800:]
    industrial = sum(1 for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines() if line)
    retail = sum(len(d["variants"]) for d in export.documents())
    with tarfile.open(archive, mode="r:gz") as tar:
        members = [(m.name, tar.extractfile(m).read()) for m in tar.getmembers()]  # type: ignore[union-attr]
    roots = {name.split("/", 1)[0] for name, _ in members}
    assert roots == {"industrial", "retail"}
    assert len(members) == industrial + retail
    sidecar = archive.with_name(archive.name + ".content-sha256").read_text("utf-8")
    assert sidecar == f"{bundle.files_digest(members)}  {industrial + retail}\n"
    assert f"{industrial + retail} files for {industrial + retail} SKUs" in run.stdout


def test_the_pin_bump_writes_one_image_pin(tmp_path, capsys) -> None:
    assert pins.IMAGES_PIN == "src/prism_retail_and_industrial/data/images_release.json"
    assert pins.IMAGES_ASSET == "images.tar.gz"
    catalog = tmp_path / "catalog.ndjson"
    catalog.write_bytes(b"{}\n")
    sidecar = tmp_path / "images.tar.gz.content-sha256"
    sidecar.write_text("ab" * 32 + "  12\n", encoding="utf-8")
    argv = ["--tag", "v1", "--catalog", str(catalog), "--images-sidecar", str(sidecar)]
    assert pins.main([*argv, "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "images_release_retail" not in out
    pinned = json.loads(out.split(f"--- {pins.IMAGES_PIN}\n", 1)[1])
    assert pinned["asset"] == "images.tar.gz" and pinned["file_count"] == 12

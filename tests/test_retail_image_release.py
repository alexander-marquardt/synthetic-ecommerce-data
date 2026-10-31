"""The retail image release: one drawing per style, colorway and size rung (gen#125, gen#339),
written to every SKU's own file (gen#706).

``src/synthetic_ecommerce_data/domains/retail/image_release.py`` renders every image the retail
export (``export.py``) references and packages it as the industrial bundle is
(:mod:`synthetic_ecommerce_data.core.bundle`): members under one top-level
folder, a deterministic ``.tar.gz``, and the content digest a customization pins.
"""

from __future__ import annotations

import hashlib
import io
import subprocess
import sys
import tarfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    pack_scale,
    scale,
    size_ladder,
)
from synthetic_ecommerce_data.domains.retail.build_preview import drawing_svg
from synthetic_ecommerce_data.domains.retail.build_preview4 import samples
from synthetic_ecommerce_data.domains.retail.retail_figures import figures
from synthetic_ecommerce_data.domains.retail.variants import FAMILIES

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "src" / "synthetic_ecommerce_data" / "domains" / "retail"


#: The authored-styles build, as ``retail_figures.figures()`` measures it (gen#162, gen#536).
RETAIL_SKUS = figures()["templates"]["authored"]["skus"]
#: One drawing per style, colorway and size rung, plus one for each style sold in no color.
RETAIL_DRAWINGS = figures()["templates"]["authored_drawings"]
#: The scaled build ``image_release.py --skus`` releases (``tests/test_retail_scale.py``'s target).
SCALED_SKUS = 19_000
#: The demo serves the images folder at this prefix; a URL less it is the member.
URL_PREFIX = "/images/"


RECORDS = image_release.records()


@pytest.fixture(scope="module")
def documents() -> list[dict[str, Any]]:
    return export.documents()


@pytest.fixture(scope="module")
def files() -> list[tuple[str, bytes]]:
    return image_release.image_files()


def _color(variant: dict[str, Any]) -> str | None:
    """The colorway: the color with its pattern, as a wash is a pattern of Blue (#188); a
    complexion product's colorway is its shade (#345)."""
    pair = [a["value"] for a in variant["attributes"] if a["key"] in ("color", "shade", "pattern")]
    return "/".join(pair) or None


def _drawn(doc: dict[str, Any], variant: dict[str, Any]) -> tuple[str, float | None, float | None]:
    """What a variant's file draws: its ``drawing_id``, and the rung and pack factor it stands on
    (its drawing's ``size_scale`` and ``pack_scale``; ``None``: neither applies)."""
    rec = next(r for r in RECORDS if r["product_id"] == doc["product_id"])
    sku = next(s for s in rec["skus"] if s["sku"] == variant["sku"])
    drawing = image_release.colorway_drawing(rec, sku)
    assert drawing.get("pack_scale") == pack_scale.factor(rec, sku)
    return export.drawing_id(rec, sku), drawing.get("size_scale"), drawing.get("pack_scale")


def test_one_drawing_per_style_colorway_pack_scale_and_size_rung_and_one_file_per_sku(
    documents, files
):
    """A colorway has one drawing, or one per pack factor (gen#543) and per rung of its size
    ladder (gen#339); the sizes of a rung (a footwear row's UK, EU and US) draw it, and each
    has its own file of it (gen#706)."""
    by_key: dict[tuple, set[str]] = defaultdict(set)
    by_drawing: dict[str, set[tuple]] = defaultdict(set)
    for doc in documents:
        for variant in doc["variants"]:
            drawn, *rung = _drawn(doc, variant)
            key = (doc["product_id"], _color(variant), *rung)
            by_key[key].add(drawn)
            by_drawing[drawn].add(key)
            assert variant["image_id"].endswith("/" + variant["sku"])
    assert sum(len(d["variants"]) for d in documents) == RETAIL_SKUS
    assert [k for k, ids in by_key.items() if len(ids) != 1] == []
    assert [i for i, keys in by_drawing.items() if len(keys) != 1] == []
    assert len(by_drawing) == RETAIL_DRAWINGS < RETAIL_SKUS
    assert len(files) == RETAIL_SKUS
    assert len({data for _, data in files}) <= RETAIL_DRAWINGS, "a drawing is rendered once"


def test_every_image_reference_resolves_to_a_packaged_file(documents, files):
    members = {path for path, _ in files}
    urls = {
        row[field]
        for doc in documents
        for row in (doc, *doc["variants"])
        for field in ("image_url", "image_detail_url")
    }
    unbacked = sorted(u for u in urls if not u.startswith(URL_PREFIX)
                      or u.removeprefix(URL_PREFIX) not in members)  # fmt: skip
    assert unbacked == []
    assert {u.removeprefix(URL_PREFIX) for u in urls} == members, "a packaged file no doc names"
    assert [path for path, data in files if not data.startswith(b"<svg")] == []
    assert all(path.startswith(f"{export.IMAGE_ROOT}/") for path in members)


def test_a_colorway_image_draws_that_colorway():
    rec = next(r for rs in samples().values() for r in rs if r["product_id"] == "BED-COVPRT")
    colors = {c[0]: c for c in next(s for s in FAMILIES["Bedding"] if s.code == "COVPRT").colors}
    first_color = [s for s in rec["skus"] if s["color"] == rec["skus"][0]["color"]]
    largest = max(first_color, key=lambda s: size_ladder.size_scale(rec, s))
    assert image_release.render(rec, largest) == drawing_svg(rec).encode()
    drawn: dict[str, bytes] = {}
    for sku in rec["skus"]:
        name, pattern, base, accent = colors[sku["color"]]
        drawing = image_release.colorway_drawing(rec, sku)
        assert (drawing["pattern"], drawing["base"], drawing["accent"]) == (pattern, base, accent)
        drawn[sku["color"]] = image_release.render(rec, sku)
    assert len(set(drawn.values())) == len(colors) == 3


def test_a_drawing_id_naming_two_drawings_is_refused(monkeypatch):
    rec = next(r for rs in samples().values() for r in rs if r["product_id"] == "BED-COVPRT")
    monkeypatch.setattr(export, "drawing_id", lambda rec, sku: f"bedding/{rec['product_id']}/one")
    with pytest.raises(ValueError, match="names 2 different drawings"):
        image_release.image_files([rec])


def test_the_scaled_release_ships_an_image_for_every_image_id_its_export_names():
    """``records(N)`` is ``scale.build(N)``: the 19K export names an ``image_id`` per SKU of the
    derived styles too, and every one of them is a packaged file."""
    named = {v["image_id"] for d in scale.documents(scale.build(SCALED_SKUS))
             for v in d["variants"]}  # fmt: skip
    recs = image_release.records(SCALED_SKUS)
    members = {path for path, _ in image_release.image_files(recs)}
    missing = sorted(i for i in named if image_release.member_path(i) not in members)
    assert missing == []
    assert len(members) == len(named) == sum(len(r["skus"]) for r in recs) >= SCALED_SKUS


def test_the_command_takes_a_sku_target(tmp_path):
    target = RETAIL_SKUS + 1_000  # above the authored range, so it grows with it
    recs = image_release.records(target)
    skus = sum(len(r["skus"]) for r in recs)
    files = len(image_release.image_files(recs))
    run = subprocess.run(
        [sys.executable, str(RETAIL / "image_release.py"), "--skus", str(target),
         "--out", str(tmp_path / "out")],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 0, run.stderr
    assert f"{files} files for {skus} SKUs" in run.stdout
    assert files == skus
    assert skus >= target > RETAIL_SKUS


def test_the_command_writes_the_industrial_package_shape(tmp_path, files):
    out, archive = tmp_path / "out", tmp_path / "images.tar.gz"
    stale = out / export.IMAGE_ROOT / "stale.svg"
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"<svg/>")
    run = subprocess.run(
        [sys.executable, str(RETAIL / "image_release.py"), "--out", str(out),
         "--archive", str(archive)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 0, run.stderr
    assert f"{RETAIL_SKUS} files for {RETAIL_SKUS} SKUs" in run.stdout
    assert not stale.exists(), "a previous set's file lingers beside the new one"
    on_disk = sorted(p.relative_to(out).as_posix() for p in out.rglob("*.svg"))
    assert on_disk == [path for path, _ in files]
    content = bundle.files_digest(files)
    sidecar = archive.with_name(archive.name + ".content-sha256").read_text("utf-8")
    assert sidecar == f"{content}  {RETAIL_SKUS}\n"
    packed = archive.read_bytes()
    assert archive.with_name(archive.name + ".sha256").read_text("utf-8") == (
        f"{hashlib.sha256(packed).hexdigest()}  {archive.name}\n"
    )
    with tarfile.open(fileobj=io.BytesIO(packed), mode="r:gz") as tar:
        members = tar.getmembers()
        unpacked = [(m.name, tar.extractfile(m).read()) for m in members]  # type: ignore[union-attr]
    assert [m.name for m in members if not m.isfile() or m.mtime != 0] == []
    assert unpacked == files
    again = bundle.write_archive(files, tmp_path / "again.tar.gz")
    assert again == hashlib.sha256(packed).hexdigest(), "the archive is not deterministic"


def test_a_style_with_one_print_colorway_and_solid_ones_renders_every_sku():
    """The floral dress draws its first colorway as a print; its solid colorways keep the style's
    motif keys on the drawing, and a solid fill carries none (gen#408)."""
    from synthetic_ecommerce_data.domains.retail import scale  # noqa: PLC0415

    rec = next(r for r in scale.templates() if r["product_id"] == "BRD-CLRWRP")
    patterns = {}
    for sku in rec["skus"]:
        drawing = image_release.colorway_drawing(rec, sku)
        patterns[sku["color"]] = drawing["pattern"]
        if drawing["pattern"] != "print":
            keys = {"motif", "placement", "scale", "spacing", "count"}
            assert keys & drawing.keys() == set(), f"{sku['color']} keeps the print's keys"
        assert image_release.render(rec, sku).startswith(b"<svg")
    assert set(patterns.values()) == {"print", "solid"}

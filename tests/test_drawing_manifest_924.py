"""Each image names what it was drawn from, beside the image release (gen#924).

A title/image mismatch (gen#922: the Petite Pinstripe Wrap Midi Dress drawn as a plain strap
dress) was traced by re-deriving the drawing from the generator's templates. The release now
writes ``drawings.jsonl.gz``: one row per image file, keyed by its ``image_url``, naming the
drawing that rendered it (retail: shape, fill, params; industrial: the type's figure, the fill its
finish or material picks, and the published values it reads). A lookup reads that file alone.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.core.drawing import draw_product
from synthetic_ecommerce_data.domains.retail import image_release, scale
from synthetic_ecommerce_data.domains.retail.build_preview import drawing_svg

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "golden-catalog"
#: The row gen#922 reported, and the words its drawing must carry.
REPORTED = ("PLT-DPT105", ("pinstripe", "wrap"))
#: A few products of several kinds: a print, colorways, a size ladder, the reported dress.
SAMPLE = ("PLT-DPT105", "BRD-CLRWRP", "PLT-SDMAXI", "BRD-NKXDBOAD")
#: The industrial products read from the golden catalog: enough to cross several types.
INDUSTRIAL_LINES = 12


@pytest.fixture(scope="module")
def sample() -> list[dict]:
    recs = {d["product_id"]: d for d in scale.templates(baseline=False)}
    return [recs[code] for code in SAMPLE]


def _read(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_every_retail_image_has_one_row_and_its_drawing_renders_that_image(sample) -> None:
    rows = image_release.drawing_rows(sample)
    assert sorted(row["image_url"] for row in rows) == sorted(
        url for _, url in image_release.sku_urls(sample)
    )
    by_url = {row["image_url"]: row for row in rows}
    for rec in sample:
        urls = dict(image_release.sku_urls([rec]))
        for sku in rec["skus"]:
            url = urls[sku["sku"]]
            row = json.loads(json.dumps(by_url[url]))  # as the file holds it
            assert (row["product_id"], row["sku"]) == (rec["product_id"], sku["sku"])
            drawn = drawing_svg(rec | {"drawing": row["drawing"]}, True).encode()
            assert drawn == image_release.render(rec, sku), url


def test_the_file_is_deterministic_and_sorted_by_image_url(sample, tmp_path) -> None:
    rows = image_release.drawing_rows(sample)
    one, two = tmp_path / "one.jsonl.gz", tmp_path / "two.jsonl.gz"
    image_release.write_drawings(rows, one)
    image_release.write_drawings(list(reversed(rows)), two)
    assert one.read_bytes() == two.read_bytes()
    read = _read(one)
    assert [row["image_url"] for row in read] == sorted(row["image_url"] for row in rows)


def test_the_reported_dress_is_found_by_its_image_url_and_its_product_id(sample, tmp_path) -> None:
    code, words = REPORTED
    path = tmp_path / image_release.DRAWINGS_FILE
    image_release.write_drawings(image_release.drawing_rows(sample), path)
    rec = next(r for r in sample if r["product_id"] == code)
    url = dict(image_release.sku_urls([rec]))[rec["skus"][0]["sku"]]
    for key in (url, f"https://demo.example{url}"):
        found = image_release.drawing_for(path, key)
        assert len(found) == 1, (key, found)
        row = found[0]
        assert row["drawing"]["shape"] == "dress"
        assert set(words) <= set(row["drawing"]["params"]["features"].split()), row
    by_product = image_release.drawing_for(path, code)
    assert len(by_product) == len(rec["skus"])
    assert image_release.drawing_for(path, "/images/retail/no/such/image.svg") == []


def test_an_industrial_image_names_the_shape_fill_and_params_that_drew_it(tmp_path) -> None:
    nested = (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()[:INDUSTRIAL_LINES]
    skus = {v["sku"] for v in (json.loads(line) for line in nested) for v in v["variants"]}
    flat = [line for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()
            if line and json.loads(line)["sku"] in skus]  # fmt: skip
    (tmp_path / "nested.jsonl").write_text("\n".join(nested) + "\n", encoding="utf-8")
    (tmp_path / "flat.jsonl").write_text("\n".join(flat) + "\n", encoding="utf-8")
    shutil.copy(GOLDEN / "authored_names.json", tmp_path / "authored_names.json")
    recorded = {
        row["image_id"]: row
        for row in map(json.loads, (GOLDEN / "images.jsonl").read_text("utf-8").splitlines())
    }
    rows = bundle.drawing_rows(tmp_path)
    assert sorted(row["image_url"] for row in rows) == sorted(
        json.loads(line)["image_url"] for line in flat
    )
    by_product: dict[str, list[dict]] = {}
    for row in rows:
        assert set(row["drawing"]) == {"shape", "fill", "params"}, row
        assert row["drawing"]["fill"].startswith("#"), row
        by_product.setdefault(row["product_id"], []).append(row)
    for parent in map(json.loads, nested):
        own = by_product[parent["product_id"]]
        assert [r["sku"] for r in own] == [v["sku"] for v in parent["variants"]]
        drawn = draw_product(
            own[0]["drawing"]["shape"],
            parent["brand"],
            [r["drawing"]["params"] for r in own],
            parent["product_id"],
        )
        for row, (data, _) in zip(own, drawn, strict=True):
            assert hashlib.sha256(data).hexdigest() == recorded[row["image_id"]]["sha256"], row


def test_the_command_writes_the_file_beside_the_archive_and_looks_an_image_up(
    sample, tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(image_release, "records", lambda skus=None: sample)
    out, archive = tmp_path / "out", tmp_path / "images.tar.gz"
    assert image_release.main(["--out", str(out), "--archive", str(archive)]) == 0
    beside = archive.with_name(image_release.DRAWINGS_FILE)
    assert beside.exists() and (out / image_release.DRAWINGS_FILE).exists()
    assert beside.read_bytes() == (out / image_release.DRAWINGS_FILE).read_bytes()
    assert len(_read(beside)) == sum(len(rec["skus"]) for rec in sample)
    capsys.readouterr()
    code, words = REPORTED
    url = next(u for s, u in image_release.sku_urls(sample) if f"/{code}/" in u)
    assert image_release.main(["--lookup", url, "--drawings", str(beside)]) == 0
    (printed,) = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line]
    assert printed["image_url"] == url
    assert set(words) <= set(printed["drawing"]["params"]["features"].split())
    assert image_release.main(["--lookup", "NO-SUCH-ID", "--drawings", str(beside)]) == 1

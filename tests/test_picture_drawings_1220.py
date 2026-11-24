"""gen#1220: every row of a picture manifest gets a drawing of its own.

The manifest is the generator's own vocabulary under made-up hex image ids: one row per drawn type
and one per fallback department. No benchmark data is in it. Pinned here: a run draws every row, one
file each, and counts the fallbacks, with the same bytes on a second run (Done-when 1), and a run
stopped part way is gone on from by the next (Done-when 2).
"""

from __future__ import annotations

import ast
import inspect
import itertools
import json
import subprocess
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data import drawings, picture_drawings, picture_manifest
from synthetic_ecommerce_data.domains.retail import kit
from synthetic_ecommerce_data.picture_products import book, load, write

TYPE_ROWS = [
    {"image_id": f"a{i:015x}", "type": t, "color": "Natural"}
    for i, t in enumerate(picture_manifest.TYPES)
]
FALLBACK_ROWS = [
    {"image_id": f"b{i:015x}", "department": d} for i, d in enumerate(picture_manifest.DEPARTMENTS)
]
ROWS = [*TYPE_ROWS, *FALLBACK_ROWS]


@pytest.fixture
def manifest(tmp_path: Path) -> Path:
    path = tmp_path / "manifest.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in ROWS), encoding="utf-8")
    return path


def _files(out: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in (out / "images").iterdir()}


def _refused(row: dict) -> str | None:
    try:
        load([row])
    except ValueError as e:
        return str(e)
    return None


def test_a_run_draws_every_row_and_counts_the_fallbacks(manifest, tmp_path):
    report = picture_drawings.draw(manifest, tmp_path / "out")
    files = _files(tmp_path / "out")
    assert set(files) == {f"{r['image_id']}.svg" for r in ROWS}
    assert all(b.startswith(b"<svg") for b in files.values())
    assert report.rows == report.files == report.drawn == len(ROWS)
    assert dict(report.own_type) == dict.fromkeys(drawings.PROPORTIONS, 1)
    assert dict(report.fallbacks) == dict.fromkeys(picture_manifest.DEPARTMENTS, 1)


def test_a_second_run_gives_the_same_bytes(manifest, tmp_path):
    picture_drawings.draw(manifest, tmp_path / "one")
    picture_drawings.draw(manifest, tmp_path / "two")
    assert len(_files(tmp_path / "one")) == len(ROWS)
    assert _files(tmp_path / "one") == _files(tmp_path / "two")


def test_a_stopped_run_goes_on_from_the_rows_not_yet_drawn(manifest, tmp_path, monkeypatch):
    out, real, seen = tmp_path / "out", drawings.render, []

    def stops(type_, attributes, finish, *, product_id):
        if product_id in {r["image_id"] for r in ROWS} and len(seen) == 7:
            raise KeyboardInterrupt
        if product_id in {r["image_id"] for r in ROWS}:
            seen.append(product_id)
        return real(type_, attributes, finish, product_id=product_id)

    monkeypatch.setattr(drawings, "render", stops)
    stopped = False
    try:
        picture_drawings.draw(manifest, out)
    except KeyboardInterrupt:
        stopped = True
    assert stopped
    before = _files(out)
    assert len(before) == 7 and all(n.endswith(".svg") for n in before)
    monkeypatch.setattr(drawings, "render", real)
    report = picture_drawings.draw(manifest, out)
    assert (report.drawn, report.files) == (len(ROWS) - 7, len(ROWS))
    after = _files(out)
    assert {n: after[n] for n in before} == before
    assert after == _files_of_a_fresh_run(manifest, tmp_path)


def _files_of_a_fresh_run(manifest: Path, tmp_path: Path) -> dict[str, bytes]:
    picture_drawings.draw(manifest, tmp_path / "fresh")
    return _files(tmp_path / "fresh")


def test_a_half_written_picture_is_drawn_again(manifest, tmp_path):
    out = tmp_path / "out"
    picture_drawings.draw(manifest, out)
    whole = (out / "images" / f"{ROWS[0]['image_id']}.svg").read_bytes()
    (out / "images" / f"{ROWS[0]['image_id']}.svg").rename(
        out / "images" / f"{ROWS[0]['image_id']}.part"
    )
    report = picture_drawings.draw(manifest, out)
    assert report.drawn == 1
    assert (out / "images" / f"{ROWS[0]['image_id']}.svg").read_bytes() == whole
    assert not list((out / "images").glob("*.part"))


def test_a_directory_drawn_from_another_manifest_is_refused(manifest, tmp_path):
    picture_drawings.draw(manifest, tmp_path / "out")
    manifest.write_text(json.dumps(ROWS[:3]), encoding="utf-8")
    with pytest.raises(ValueError, match="another manifest"):
        picture_drawings.draw(manifest, tmp_path / "out")


def test_a_directory_drawn_by_another_renderer_is_refused(manifest, tmp_path, monkeypatch):
    picture_drawings.draw(manifest, tmp_path / "out")
    monkeypatch.setattr(drawings, "UNBRANDED_FRAMES", ("double",) * 5)
    with pytest.raises(ValueError, match="another renderer"):
        picture_drawings.draw(manifest, tmp_path / "out")


def test_pictures_of_no_run_are_refused(manifest, tmp_path):
    (tmp_path / "out" / "images").mkdir(parents=True)
    (tmp_path / "out" / "images" / "c.svg").write_text("<svg/>", encoding="utf-8")
    with pytest.raises(ValueError, match="no run"):
        picture_drawings.draw(manifest, tmp_path / "out")


def test_the_command_prints_the_counts_and_fails_when_files_are_not_rows(
    manifest, tmp_path, capsys
):
    out = str(tmp_path / "out")
    assert picture_drawings.main([str(manifest), out]) == 0
    printed = capsys.readouterr().out
    n, types = len(ROWS), len(TYPE_ROWS)
    assert f"rows: {n}\nfiles: {n}\nown-type drawings: {types}\nfallbacks: {n - types}" in printed
    (tmp_path / "out" / "images" / "stray.svg").write_text("<svg/>", encoding="utf-8")
    assert picture_drawings.main([str(manifest), out]) == 1


def test_the_manifest_takes_every_type_render_draws_and_every_part_value_draws():
    assert tuple(picture_manifest.TYPES) == tuple(drawings.PROPORTIONS)
    for type_, parts in picture_manifest.TYPES.items():
        assert set(parts) <= set(list(inspect.signature(kit._draw(type_)).parameters)), type_
        for values in itertools.product(*parts.values()):
            drawn = drawings.figure(
                type_, {"color": "#9a9ca0", **dict(zip(parts, values, strict=True))}
            )
            assert drawn.startswith("<g"), (type_, values)


def test_a_fallback_row_is_closed_and_carries_no_text():
    row = {"image_id": "7c1e0a9d4b2f8e63", "department": "lighting"}
    assert load([row]) == [picture_manifest.Fallback("7c1e0a9d4b2f8e63", "lighting")]
    for extra in ({"title": "x"}, {"type": "sofa"}, {"color": "Grey"}, {"category": "x"}):
        refused = _refused(row | extra)
        assert refused is not None and next(iter(extra)) in refused, extra
    assert "department" in (_refused(row | {"department": "any words"}) or "")
    assert "image_id" in (_refused({"department": "lighting"}) or "")
    assert "image_id" in (_refused(row | {"image_id": "a title"}) or "")


def test_no_picture_holds_text():
    for row in load(ROWS):
        assert "<text" not in picture_drawings.picture(row), row


def test_the_products_are_written_around_the_types_the_book_describes():
    products = write(load(ROWS))
    assert {p.doc["drawing"]["shape"] for p in products} == set(book.TYPES)
    assert len(products) == len(book.TYPES)


def test_the_drawing_run_imports_no_product_writer_and_reads_no_benchmark():
    code = (
        "import sys; import synthetic_ecommerce_data.picture_drawings; "
        "print(sorted(m for m in sys.modules if 'picture_products' in m or 'wands' in m))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]", out.stdout
    tree = ast.parse(Path(picture_drawings.__file__).read_text(encoding="utf-8"))
    names = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)]
    assert names and not [n for n in names if isinstance(n, str) and "wands" in n.lower()]

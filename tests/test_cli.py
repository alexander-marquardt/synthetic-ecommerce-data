from __future__ import annotations

import json

import pytest

from synthetic_industrial_products.cli import main, png_dimensions
from synthetic_industrial_products.records import FIXTURES
from synthetic_industrial_products.render import UnknownProductError


def test_fixtures_renders_every_bundled_record(tmp_path, png_size):
    assert main(["fixtures", "--out", str(tmp_path)]) == 0
    written = sorted(p.name for p in tmp_path.glob("*.png"))
    assert len(written) == len(FIXTURES) * 2
    for path in tmp_path.glob("*_card.png"):
        assert png_size(path) == (600, 880)
    for path in tmp_path.glob("*_detail.png"):
        assert png_size(path) == (1400, 1400)


@pytest.mark.parametrize(
    "argv",
    [
        ["--profile", "card", "--out", "{out}", "sku", "4LU10"],
        ["sku", "4LU10", "--profile", "card", "--out", "{out}"],
    ],
    ids=["options-before-subcommand", "options-after-subcommand"],
)
def test_the_options_work_on_either_side_of_the_subcommand(argv, tmp_path, png_size):
    # argparse re-applies a subparser's defaults, so an option given before the
    # subcommand name is silently discarded unless it is suppressed there.
    assert main([a.format(out=tmp_path) for a in argv]) == 0
    written = sorted(p.name for p in tmp_path.glob("*.png"))
    assert written == ["4LU10_card.png"]
    assert png_size(tmp_path / "4LU10_card.png") == (600, 880)


def test_batch_reads_one_record_per_line(tmp_path, png_size):
    jsonl = tmp_path / "records.jsonl"
    jsonl.write_text(
        "\n".join(json.dumps(FIXTURES[sku]) for sku in ("4LU10", "26LD37")) + "\n",
        encoding="utf-8",
    )
    assert main(["batch", str(jsonl), "--out", str(tmp_path), "--profile", "card"]) == 0
    assert sorted(p.name for p in tmp_path.glob("*.png")) == [
        "26LD37_card.png",
        "4LU10_card.png",
    ]


def test_a_malformed_batch_line_is_reported_with_its_line_number(tmp_path):
    jsonl = tmp_path / "bad.jsonl"
    jsonl.write_text(json.dumps(FIXTURES["4LU10"]) + "\nnot json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bad.jsonl:2"):
        main(["batch", str(jsonl), "--out", str(tmp_path)])
    # and nothing was written: the file is read through before anything is drawn
    assert not list(tmp_path.glob("*.png"))


def test_a_record_nothing_can_draw_is_refused(tmp_path):
    jsonl = tmp_path / "mystery.jsonl"
    jsonl.write_text(json.dumps({"sku": "A", "Colour": "red"}) + "\n", encoding="utf-8")
    with pytest.raises(UnknownProductError):
        main(["batch", str(jsonl), "--out", str(tmp_path)])


def test_an_unknown_sku_is_an_error_not_an_empty_run(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["sku", "NOPE", "--out", str(tmp_path)])
    assert exc.value.code != 0
    assert not list(tmp_path.glob("*.png"))


def test_png_dimensions_reads_the_header_width_first(tmp_path, png_size):
    # Measured on the card, which is not square: on the square detail image a
    # helper that returned height first would agree with one that did not.
    main(["sku", "4LU10", "--profile", "card", "--out", str(tmp_path)])
    path = tmp_path / "4LU10_card.png"
    assert png_dimensions(path) == png_size(path) == (600, 880)


def test_png_dimensions_rejects_a_file_that_is_not_a_png(tmp_path):
    path = tmp_path / "not.png"
    path.write_bytes(b"GIF89a")
    with pytest.raises(ValueError):
        png_dimensions(path)

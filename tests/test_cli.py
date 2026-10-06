from __future__ import annotations

import json

import pytest

from synthetic_industrial_products.cli import main, png_dimensions, render_all
from synthetic_industrial_products.records import BUNDLED, DRAWABLE, FIXTURES, NO_IMAGE
from synthetic_industrial_products.render import CARD, UnknownProductError


def test_fixtures_renders_every_bundled_record_that_has_a_drawing(tmp_path, png_size):
    """All but the four end mills that do not say which end they have.

    Those are refused and named in the report, and the run still succeeds: a
    refusal is the renderer working, not the tool breaking. See records.py.
    """
    assert main(["fixtures", "--out", str(tmp_path)]) == 0
    written = sorted(p.name for p in tmp_path.glob("*.png"))
    assert len(written) == len(DRAWABLE) * 2
    assert len(BUNDLED) > len(FIXTURES), "the generated samples are bundled too"
    assert not [name for name in written if name.split("_")[0] in NO_IMAGE]
    for path in tmp_path.glob("*_card.png"):
        assert png_size(path) == (600, 880)
    for path in tmp_path.glob("*_detail.png"):
        assert png_size(path) == (1400, 1400)


@pytest.mark.parametrize(
    "argv",
    [
        ["--profile", "card", "--out", "{out}", "sku", "26VW40"],
        ["sku", "26VW40", "--profile", "card", "--out", "{out}"],
    ],
    ids=["options-before-subcommand", "options-after-subcommand"],
)
def test_the_options_work_on_either_side_of_the_subcommand(argv, tmp_path, png_size):
    # argparse re-applies a subparser's defaults, so an option given before the
    # subcommand name is silently discarded unless it is suppressed there.
    assert main([a.format(out=tmp_path) for a in argv]) == 0
    written = sorted(p.name for p in tmp_path.glob("*.png"))
    assert written == ["26VW40_card.png"]
    assert png_size(tmp_path / "26VW40_card.png") == (600, 880)


def test_batch_reads_one_record_per_line(tmp_path, png_size):
    jsonl = tmp_path / "records.jsonl"
    jsonl.write_text(
        "\n".join(json.dumps(BUNDLED[sku]) for sku in ("26VW40", "26LD37")) + "\n",
        encoding="utf-8",
    )
    assert main(["batch", str(jsonl), "--out", str(tmp_path), "--profile", "card"]) == 0
    assert sorted(p.name for p in tmp_path.glob("*.png")) == [
        "26LD37_card.png",
        "26VW40_card.png",
    ]


def test_a_malformed_batch_line_is_reported_with_its_line_number(tmp_path):
    jsonl = tmp_path / "bad.jsonl"
    jsonl.write_text(json.dumps(BUNDLED["26VW40"]) + "\nnot json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bad.jsonl:2"):
        main(["batch", str(jsonl), "--out", str(tmp_path)])
    # and nothing was written: the file is read through before anything is drawn
    assert not list(tmp_path.glob("*.png"))


def test_a_record_nothing_can_draw_is_skipped_and_counted(tmp_path, capsys):
    """Issue #2: a batch must not die on one record it cannot place.

    There is no type drawing for a record with no identifiable type -- the type
    drawing is a statement about a product type -- so this one gets no image.
    It is counted, named, and the run carries on; the exit status says it
    happened so a regeneration script cannot read a clean exit over it.
    """
    jsonl = tmp_path / "mystery.jsonl"
    jsonl.write_text(json.dumps({"sku": "A", "Colour": "red"}) + "\n", encoding="utf-8")
    assert main(["batch", str(jsonl), "--out", str(tmp_path), "--profile", "card"]) == 0
    assert not list(tmp_path.glob("*.png"))
    assert "UnknownProductError" in capsys.readouterr().out


def test_a_batch_carries_on_past_the_record_it_cannot_draw(tmp_path):
    """The behaviour issue #2 asks for: one bad record costs one image.

    The undrawable record is put FIRST on purpose. The driver used to abort on
    the first refusal, so a version with that defect passes a test where the
    bad line is last.
    """
    jsonl = tmp_path / "mixed.jsonl"
    jsonl.write_text(
        "\n".join(
            [
                json.dumps({"sku": "MYSTERY", "Colour": "red"}),
                *(json.dumps(BUNDLED[sku]) for sku in ("26VW40", "2DY27", "57KY59")),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    assert main(["batch", str(jsonl), "--out", str(tmp_path), "--profile", "card"]) == 0
    assert sorted(p.name for p in tmp_path.glob("*.png")) == [
        "26VW40_card.png",
        "2DY27_card.png",
        "57KY59_card.png",
    ]


def test_the_batch_report_separates_the_two_kinds_of_drawing(tmp_path):
    """ "Three images" and "three dimensioned drawings" are different claims."""
    report = render_all([BUNDLED["26VW40"], BUNDLED["57KY59"], BUNDLED["2DY27"]], tmp_path, [CARD])
    assert report.drawn == 3
    assert sum(report.to_scale.values()) == 2
    assert sum(report.as_type.values()) == 1
    assert report.refusals["UnsupportedFeatureError"] == 1
    assert report.refused == report.failed == {}


def test_without_keep_going_the_first_refusal_stops_the_run(tmp_path):
    """The behaviour issue #2 reported, kept available and kept out of the CLI."""
    with pytest.raises(UnknownProductError):
        render_all([{"sku": "A", "Colour": "red"}], tmp_path, [CARD])


def test_a_refusal_and_a_failure_are_counted_apart(tmp_path):
    """Only a failure fails the run; a refusal is a property of the record.

    A catalog contains records that identify nothing, and the right answer for
    those is no image rather than a guessed one -- so a run that meets some
    must still be able to succeed, or the exit status stops meaning anything.
    """
    report = render_all([{"sku": "A", "Colour": "red"}], tmp_path, [CARD], keep_going=True)
    assert report.refused == {"UnknownProductError": 1}
    assert report.failed == {}


def test_the_generics_subcommand_writes_the_ten(tmp_path, png_size):
    from synthetic_industrial_products.render import generic

    assert main(["generics", "--out", str(tmp_path), "--profile", "card"]) == 0
    written = sorted(p.stem.removesuffix("_card") for p in tmp_path.glob("*.png"))
    assert written == sorted(generic.IMAGE_IDS)
    for path in tmp_path.glob("*.png"):
        assert png_size(path) == (600, 880)


def test_an_unknown_sku_is_an_error_not_an_empty_run(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["sku", "NOPE", "--out", str(tmp_path)])
    assert exc.value.code != 0
    assert not list(tmp_path.glob("*.png"))


def test_png_dimensions_reads_the_header_width_first(tmp_path, png_size):
    # Measured on the card, which is not square: on the square detail image a
    # helper that returned height first would agree with one that did not.
    main(["sku", "26VW40", "--profile", "card", "--out", str(tmp_path)])
    path = tmp_path / "26VW40_card.png"
    assert png_dimensions(path) == png_size(path) == (600, 880)


def test_png_dimensions_rejects_a_file_that_is_not_a_png(tmp_path):
    path = tmp_path / "not.png"
    path.write_bytes(b"GIF89a")
    with pytest.raises(ValueError):
        png_dimensions(path)

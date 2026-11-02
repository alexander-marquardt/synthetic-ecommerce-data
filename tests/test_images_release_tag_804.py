"""The one image archive ships as its own release, ``images-<count>-<YYYYMMDD>`` (gen#804).

The combined catalog's drawings, industrial and retail, are one archive (gen#706), but the release
put it on the ``v*`` generator release and its pin named ``v1.0.0``: nothing published an images
release under the name the catalogue repository pins, ``images-<count>-<YYYYMMDD>``. The release
now creates that release for ``images.tar.gz`` and its sidecars, keeps the catalog on the ``v*``
release, and the pin-bump writes the one image pin with the images tag.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import open_pin_bump_pr as pins  # noqa: E402

RELEASE = yaml.safe_load((ROOT / ".github" / "workflows" / "release.yaml").read_text("utf-8"))


def _inputs(tmp_path: Path) -> list[str]:
    catalog = tmp_path / "catalog.ndjson"
    catalog.write_bytes(b'{"a": 1}\n{"a": 2}\n')
    sidecar = tmp_path / "images.tar.gz.content-sha256"
    sidecar.write_text("ab" * 32 + "  12\n", encoding="utf-8")
    return ["--repository", "o/r", "--catalog", str(catalog), "--images-sidecar", str(sidecar)]


def _pins(out: str) -> dict[str, dict]:
    found = {}
    for path in (pins.CATALOG_PIN, pins.IMAGES_PIN):
        text = out.split(f"--- {path}\n", 1)[1]
        found[path] = json.loads(text[: text.index("}") + 1])
    return found


def test_the_image_pin_names_the_images_release_and_the_catalog_keeps_the_v_tag(
    tmp_path, capsys
) -> None:
    argv = ["--tag", "v1.0.0", "--images-tag", "images-12-20261102", *_inputs(tmp_path)]
    assert pins.main([*argv, "--dry-run"]) == 0
    out = capsys.readouterr().out
    found = _pins(out)
    assert found[pins.CATALOG_PIN]["tag"] == "v1.0.0"
    assert found[pins.IMAGES_PIN]["tag"] == "images-12-20261102"
    assert found[pins.IMAGES_PIN]["asset"] == "images.tar.gz"
    assert "https://github.com/o/r/releases/tag/images-12-20261102" in out
    assert "https://github.com/o/r/releases/tag/v1.0.0" in out


def test_with_no_images_tag_it_is_the_archives_count_and_todays_utc_date(
    tmp_path, capsys, monkeypatch
) -> None:
    monkeypatch.setattr(pins, "utc_day", lambda: "20261231")
    assert pins.main(["--tag", "v1", *_inputs(tmp_path), "--dry-run"]) == 0
    assert _pins(capsys.readouterr().out)[pins.IMAGES_PIN]["tag"] == "images-12-20261231"


@pytest.mark.parametrize(
    "tag",
    [
        "images-13-20261102",  # a count the archive does not hold
        "v1.0.0",  # the generator tag
        "images-12-2026110",  # not a YYYYMMDD date
        "images-12-20261302",  # no thirteenth month
        "retail-images-12-20261102",  # a per-department set
    ],
)
def test_an_images_tag_that_is_not_the_archives_is_refused(tmp_path, tag) -> None:
    with pytest.raises(SystemExit):
        pins.main(["--tag", "v1", "--images-tag", tag, *_inputs(tmp_path), "--dry-run"])


def _commands(run: str) -> list[str]:
    return [line.strip() for line in run.replace("\\\n", " ").splitlines() if line.strip()]


def test_the_workflow_puts_the_archive_on_the_images_release_alone() -> None:
    steps = RELEASE["jobs"]["release"]["steps"]
    step = next(s for s in steps if s.get("name", "").startswith("The pin-bump"))
    creates = [c for c in _commands(step["run"]) if c.startswith("gh release create")]
    by_tag = {c.split()[3]: c for c in creates}
    assert set(by_tag) == {'"$TAG"', '"$IMAGES_TAG"'}
    assert "images.tar.gz" not in by_tag['"$TAG"']
    assert "catalog.ndjson.gz" in by_tag['"$TAG"']
    for asset in ("images.tar.gz ", "images.tar.gz.content-sha256", "images.tar.gz.sha256"):
        assert asset in by_tag['"$IMAGES_TAG"'] + " ", asset
    assert "catalog" not in by_tag['"$IMAGES_TAG"']
    assert '--images-tag "$IMAGES_TAG"' in step["run"]

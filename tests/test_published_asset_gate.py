"""The asset-publication gate has to bite, and bite where a sample would not.

The defect it exists for: a regeneration mints new image ids, the catalog is
committed and served, and the drawings those ids name were never published.
That shipped -- 499 of 500 ids dead, 4,680 of 4,689 products showing a broken
image -- with every other gate on both sides of the seam green.

Two of these tests are about the gate REFUSING rather than passing. An empty
manifest and an empty hosted set both satisfy a set comparison for free, and a
vacuous OK from a check written to prevent a catastrophe is worse than no
check: it is a green that gets believed.

``test_a_per_type_sample_would_have_passed_the_shipped_defect`` is the reason
the comparison is over the whole manifest. It reconstructs the shipped state --
one surviving ``end_mill_square`` id, every other id dead -- and shows the
cheap version passing it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import verify_published_assets as gate  # noqa: E402

TYPES = ("end_mill_square", "screw_socket_head", "drill_jobber", "washer_flat")


def _manifest(tmp_path: Path, ids: list[str]) -> Path:
    path = tmp_path / "images.jsonl"
    path.write_text(
        "".join(
            json.dumps(
                {
                    "image_id": image_id,
                    "path": f"{image_id}/card.png",
                    "detail_path": f"{image_id}/detail.png",
                }
            )
            + "\n"
            for image_id in ids
        ),
        encoding="utf-8",
    )
    return path


def _checkout(tmp_path: Path, paths: list[str]) -> Path:
    root = tmp_path / "host"
    for relative in paths:
        target = root / gate.HOST_PREFIX / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\x89PNG\r\n\x1a\n")
    return root


def _run(manifest: Path, host: Path) -> int:
    return gate.main(["--manifest", str(manifest), "--host-tree", str(host)])


IDS = [f"{kind}/ID-{index:04d}" for index, kind in enumerate(TYPES * 5)]
ALL_PATHS = [f"{i}/{profile}.png" for i in IDS for profile in ("card", "detail")]


def test_every_referenced_file_hosted_passes(tmp_path):
    assert _run(_manifest(tmp_path, IDS), _checkout(tmp_path, ALL_PATHS)) == 0


def test_one_missing_file_fails(tmp_path):
    """One dead detail sheet out of forty. A card that resolves is not enough:
    the record carries a URL per profile and the product page uses the other."""
    hosted = [p for p in ALL_PATHS if p != f"{IDS[3]}/detail.png"]
    assert _run(_manifest(tmp_path, IDS), _checkout(tmp_path, hosted)) == 1


def test_a_whole_regeneration_of_dead_ids_fails(tmp_path):
    """The shipped shape: the host holds the PREVIOUS generation's files, all
    of them, and not one id the new catalog names."""
    stale = [p.replace("ID-", "OLD-") for p in ALL_PATHS]
    assert _run(_manifest(tmp_path, IDS), _checkout(tmp_path, stale)) == 1


def test_a_per_type_sample_would_have_passed_the_shipped_defect(tmp_path):
    """Why the check is over the whole set and not one image per type.

    Reconstructed from the real incident: exactly one id survived the
    regeneration and it was an ``end_mill_square``, the type a sampler reaches
    first. Sampling one id per type is satisfied by 1 of 40 files existing when
    that one is the sampled type's; the set comparison fails on the other 39.
    """
    survivor = next(i for i in IDS if i.startswith("end_mill_square/"))
    hosted = [f"{survivor}/card.png", f"{survivor}/detail.png"]
    manifest = _manifest(tmp_path, IDS)
    host = _checkout(tmp_path, hosted)

    wanted = gate.published_paths(manifest)
    on_host = gate.hosted_from_checkout(host, gate.HOST_PREFIX)

    # The cheap check: one id per product type, and it is satisfied.
    sampled = {}
    for path, image_id in wanted.items():
        sampled.setdefault(image_id.split("/", 1)[0], path)
    assert sampled["end_mill_square"] in on_host

    # The real one is not.
    assert len(set(wanted) - on_host) == len(ALL_PATHS) - 2
    assert _run(manifest, host) == 1


def test_an_empty_manifest_is_refused_not_passed(tmp_path):
    empty = tmp_path / "images.jsonl"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit):
        _run(empty, _checkout(tmp_path, ALL_PATHS))


def test_an_empty_hosted_set_is_refused_not_reported_as_all_dead(tmp_path):
    """A collection failure reads identically to a total outage. It must not be
    reported as one, or the next real outage is the one nobody believes."""
    host = tmp_path / "bare"
    (host / gate.HOST_PREFIX).mkdir(parents=True)
    with pytest.raises(SystemExit):
        _run(_manifest(tmp_path, IDS), host)


def test_a_truncated_trees_response_is_refused(monkeypatch):
    """The API answers a big tree with a short list and a flag. Reading the
    short list would understate the hosted set and accuse live files."""

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps({"truncated": True, "tree": []}).encode()

    monkeypatch.setattr(gate.urllib.request, "urlopen", lambda *a, **k: _Response())
    with pytest.raises(SystemExit):
        gate.hosted_paths("owner/repo", "main", gate.HOST_PREFIX, None)


def test_the_committed_manifest_names_every_committed_product_line(tmp_path):
    """The gate is only as good as the manifest it reads. If a regeneration
    wrote a catalog whose lines are not all in ``images.jsonl``, the missing
    ones would never be checked -- a hole shaped exactly like the defect."""
    root = Path(__file__).resolve().parent.parent
    lines = {
        json.loads(line)["image_id"]
        for line in (root / "golden-catalog" / "nested.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    }
    manifest = gate.published_paths(root / "golden-catalog" / "images.jsonl")
    assert set(manifest.values()) == lines
    assert len(manifest) == 2 * len(lines)

"""A new product type is one declarative data file, read by a generic builder (#72).

Three claims, each its own test:

* the pilot, ``set_screws_hex_socket``, is a data file and no code module;
* a sibling type added as a data file ONLY -- a copy of the package with one
  new file in it, nothing else edited -- is found, builds its SKUs, and passes
  every per-type gate in :mod:`type_gates`;
* a type file that is wrong is refused at discovery, naming the file.

The sibling is built in a copy of ``src`` run in a fresh process, so the proof
is that no other file had to change, not that the repository was edited for it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import type_gates
from synthetic_ecommerce_data.core import typespec

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
TYPES = SRC / "synthetic_ecommerce_data" / "domains" / "industrial" / "product_types"
PILOT_KEY = "set_screws_hex_socket"
PILOT_FILE = TYPES / "fasteners" / f"{PILOT_KEY}.yaml"
SIBLING_KEY = "set_screws_hex_socket_stainless"

#: What the sibling's records are held to, as the pilot's gate file holds the pilot's.
DIMENSIONAL = ["ISO 4026", "ISO 4027", "ISO 4028", "ISO 4029", "ASME B18.3"]
DIMENSIONS = ["Length", "Drive Size", "Point Dia."]


def test_the_pilot_type_is_a_data_file_and_no_code_module() -> None:
    assert PILOT_FILE.is_file(), f"{PILOT_FILE.name} is not beside the family's modules"
    assert not PILOT_FILE.with_suffix(".py").exists(), "the pilot is still a code module"
    spec = typespec.discover()[PILOT_KEY]
    assert spec.module == f"{typespec.TYPES_PACKAGE}.fasteners.{PILOT_KEY}"
    assert spec.make is not None and spec.figure is not None


def _sibling_text() -> str:
    """The pilot's data file with a new key, label, category leaf and materials."""
    assert PILOT_FILE.is_file(), "there is no pilot data file to derive a sibling from"
    data = yaml.safe_load(PILOT_FILE.read_text(encoding="utf-8"))
    data["key"] = SIBLING_KEY
    data["label"] = "Stainless Hex Socket Set Screws"
    data["category"] = [*data["category"][:-1], "Stainless Hex Socket Set Screws"]
    data["share"] = 0.01
    data["materials"] = {k: v for k, v in data["materials"].items() if "Stainless" in k}
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


#: Runs in the copy: every per-type gate of ``type_gates`` for the sibling, as JSON.
_GATES = """
import json, sys
sys.path.insert(0, sys.argv[1])
import synthetic_ecommerce_data as pkg
import type_gates
from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.domains.industrial.generate import generate

key = sys.argv[2]
records = type_gates.default_records(key)
first, second = type_gates.builds_under_two_hash_seeds(key)
docs = [json.loads(line) for line in records]
problems, checked = type_gates.provenance_problems(
    docs, json.loads(sys.argv[3]), json.loads(sys.argv[4])
)
whole = type_gates.records(generate().lines)
print(json.dumps({
    "package": pkg.__file__,
    "module": typespec.discover()[key].module,
    "records": len(records),
    "skus": len({d["sku"] for d in docs}),
    "in_whole_build": sum(1 for r in whole if json.loads(r)["product_type"] == key),
    "hash_seeds": type_gates.difference(first, second),
    "others_moved": type_gates.others_moved_from_the_golden(key),
    "provenance_problems": problems[:5],
    "provenance_checked": checked,
}))
"""


def test_a_sibling_type_added_as_one_data_file_builds_with_every_type_gate_green(
    tmp_path: Path,
) -> None:
    text = _sibling_text()
    copy = tmp_path / "src"
    # Copied whole, so what runs is the repository's code with ONE file added.
    subprocess.run(["cp", "-r", str(SRC), str(copy)], check=True)
    (copy / TYPES.relative_to(SRC) / "fasteners" / f"{SIBLING_KEY}.yaml").write_text(
        text, encoding="utf-8"
    )
    run = subprocess.run(
        [
            sys.executable, "-c", _GATES, str(Path(type_gates.__file__).parent), SIBLING_KEY,
            json.dumps(DIMENSIONAL), json.dumps(DIMENSIONS),
        ],  # fmt: skip
        env={**os.environ, "PYTHONPATH": str(copy), "PYTHONHASHSEED": "0"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=900,
    )
    assert run.returncode == 0, run.stderr[-3000:]
    got = json.loads(run.stdout.splitlines()[-1])
    assert got["package"].startswith(str(copy)), f"the copy was not what ran: {got['package']}"
    assert got["module"].endswith(f".fasteners.{SIBLING_KEY}")
    assert got["records"] >= 100, f"the sibling built {got['records']} records"
    assert got["skus"] == got["records"], "a SKU is carried twice"
    assert got["in_whole_build"] == got["records"], "the whole build does not carry its SKUs"
    assert got["hash_seeds"] is None, got["hash_seeds"]
    assert got["others_moved"] is None, got["others_moved"]
    assert got["provenance_problems"] == [], got["provenance_problems"]
    assert got["provenance_checked"] > 20


def _plant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, text: str) -> None:
    """A throwaway type package ``planted_types`` with one family and one type file."""
    family = tmp_path / "planted_types" / "widgets"
    family.mkdir(parents=True)
    (tmp_path / "planted_types" / "__init__.py").write_text("")
    (family / "__init__.py").write_text("")
    (family / name).write_text(text, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    for loaded in [m for m in sys.modules if m.split(".")[0] == "planted_types"]:
        monkeypatch.delitem(sys.modules, loaded)


@pytest.mark.parametrize(
    ("text", "refusal"),
    [
        pytest.param(
            "key: blue_widget\nbogus_field: 1\n",
            r"blue_widget\.yaml.*unknown field 'bogus_field'",
            id="unknown-field",
        ),
        pytest.param(
            "key: red_widget\n", r"blue_widget\.yaml declares 'red_widget'", id="key-not-file-name"
        ),
        pytest.param("- not\n- a mapping\n", r"blue_widget\.yaml.*mapping", id="not-a-mapping"),
        pytest.param("key: [unclosed\n", r"blue_widget\.yaml.*(parse|YAML)", id="unparseable"),
    ],
)
def test_a_wrong_type_file_is_refused_by_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str, refusal: str
) -> None:
    _plant(tmp_path, monkeypatch, "blue_widget.yaml", text)
    with pytest.raises(typespec.TypeModuleError, match=refusal):
        typespec.discover("planted_types")

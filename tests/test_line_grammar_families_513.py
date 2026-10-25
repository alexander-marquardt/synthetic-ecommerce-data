"""A numbered family of the line grammar is a module, found by walking its package (gen#513).

``line_grammar.py`` was a registry: a feature that gave a new family of kinds its model names
added a ``FAMILIES`` row, a vocabulary constant and a ``fam == ...`` branch there, so the four open
PRs of 2026-10-25 (synth#671 to #674) conflicted in all 6 pairs. A family whose model is a lead
word, an optional sub-model and a number is now ``line_grammar_families/<family>.py`` with
``KINDS``, ``LEADS``, ``SUBS`` and ``NUMBERS``, and ``line_grammar`` reads it with no edit to a
shared file. The tests plant a probe module in a throwaway directory that is put on the package
path, in a subprocess so the import-time tables are built fresh, then hold the contract.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"

PROBE = """
KINDS = ("Probe Mop", "Probe Broom")
LEADS = ("Zzgentle", "Zztotal")
SUBS = ("Pro", "Max")
NUMBERS = (3, 4, 5)
"""

REPORT = """
import json, sys
sys.path.insert(0, {retail!r})
import line_grammar_families
line_grammar_families.__path__.append({extra!r})
import line_grammar as lg
mop = {{"product_type": "Probe Mop", "brand": "Acme", "product_line": "Zzgentle Pro 4",
        "title": "Old Zzgentle Pro 4 Floor Mop"}}
deal = lg.deals([], {{("Home", "Probe Mop"): ["Acme", "Bolt"]}})["zz_probe"]
print(json.dumps({{
    "family": lg.family(mop),
    "other_kind": lg.family({{"product_type": "Probe Broom"}}),
    "numbered": "zz_probe" in lg.NUMBERED,
    "model": lg.is_model("zz_probe", "Acme", "Zzgentle Pro 4"),
    "bare_lead": lg.is_model("zz_probe", "Acme", "Zzgentle"),
    "foreign_lead": lg.is_model("zz_probe", "Acme", "Speed 4"),
    "acme": list(deal.of("Acme")),
    "bolt": list(deal.of("Bolt")),
    "owned": [deal.owned("Acme", i) for i in range(4)],
    "sport_kept": lg.family({{"product_type": "Bicycle"}}),
    "retitled": (lg.retitle(mop, {{"brand": "Old"}}, 0), mop["title"])[1],
    "suffix": lg.color_suffix(mop, "Red"),
}}))
"""

ERROR = """
import sys
sys.path.insert(0, {retail!r})
import line_grammar_families
line_grammar_families.__path__.append({extra!r})
import line_grammar
"""


def _run(tmp_path: Path, template: str, modules: dict[str, str]) -> subprocess.CompletedProcess:
    extra = tmp_path / "extra"
    extra.mkdir()
    for name, text in modules.items():
        (extra / f"{name}.py").write_text(text, encoding="utf-8")
    code = template.format(retail=str(RETAIL), extra=str(extra))
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


def test_a_probe_family_module_is_read_with_no_shared_file_edited(tmp_path):
    done = _run(tmp_path, REPORT, {"zz_probe": PROBE})
    assert done.returncode == 0, done.stderr
    got = json.loads(done.stdout)
    assert got["family"] == "zz_probe" and got["other_kind"] == "zz_probe"
    assert got["numbered"] is True
    assert got["model"] is True
    assert got["bare_lead"] is False, "a lead word alone is a range name, not a model"
    assert got["foreign_lead"] is False, "another family's lead is not this family's"
    assert got["acme"] and got["bolt"] and not set(got["acme"]) & set(got["bolt"])
    assert set(got["acme"]) | set(got["bolt"]) == {"Zzgentle", "Zztotal"}
    assert all(m.split()[0] in got["acme"] for m in got["owned"])
    assert got["owned"][0].split()[-1] in {"3", "4", "5"}
    assert got["retitled"] == "Acme Zzgentle Pro 4 Floor Mop"
    assert got["suffix"] == ", Red"
    assert got["sport_kept"] == "sport", "the shipped sport family is still read"


def test_the_shipped_sport_family_is_a_module_of_the_package():
    sys.path.insert(0, str(RETAIL))
    try:
        import line_grammar_families as pkg

        found = pkg.families()
    finally:
        sys.path.remove(str(RETAIL))
    assert "sport" in found
    assert set(found["sport"].kinds) == {"Running Shoes", "Bicycle"}
    assert found["sport"].leads[0] == "Speed" and found["sport"].numbers == tuple(range(2, 10))


def test_a_module_that_names_no_kind_or_lead_is_refused(tmp_path):
    done = _run(tmp_path, ERROR, {"zz_empty": "X = 1\n"})
    assert done.returncode != 0
    assert "zz_empty" in done.stderr and "KINDS" in done.stderr


def test_a_kind_two_modules_claim_is_refused(tmp_path):
    other = PROBE.replace("Zzgentle", "Yygentle").replace("Zztotal", "Yytotal")
    done = _run(tmp_path, ERROR, {"zz_probe": PROBE, "zz_twin": other})
    assert done.returncode != 0
    assert "Probe Mop" in done.stderr and "zz_probe" in done.stderr and "zz_twin" in done.stderr


def test_a_kind_the_core_families_hold_is_refused(tmp_path):
    clash = PROBE.replace('"Probe Broom"', '"Dishwasher"')
    done = _run(tmp_path, ERROR, {"zz_probe": clash})
    assert done.returncode != 0
    assert "Dishwasher" in done.stderr


def test_a_lead_word_two_modules_share_is_refused(tmp_path):
    other = PROBE.replace('"Probe Mop", "Probe Broom"', '"Probe Pail"')
    done = _run(tmp_path, ERROR, {"zz_probe": PROBE, "zz_twin": other})
    assert done.returncode != 0
    assert "Zzgentle" in done.stderr and "zz_twin" in done.stderr


def test_a_name_like_lead_word_is_refused(tmp_path):
    named = PROBE.replace("Zzgentle", "Merlin")
    done = _run(tmp_path, ERROR, {"zz_probe": named})
    assert done.returncode != 0
    assert "Merlin" in done.stderr

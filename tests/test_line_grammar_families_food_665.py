"""Food and drink are numbered-family modules, with three optional module attributes (gen#665).

``GROCERY_LEADS`` is the second lead half the grocery build deals, ``BARE`` lets the lead word
alone be a model and ``MIXED_BRAND`` leads the title with its brand in two of three draws. The
twelve modules that predate them read no such attribute and keep their defaults, so the food
grammar adds no constant, row or branch to ``line_grammar.py``. The tests plant a probe module in
a throwaway directory on the package path, in a subprocess so the import tables are built fresh.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"

PROBE = """
KINDS = ("Probe Jam",)
LEADS = ("Zzscale", "Zzother")
GROCERY_LEADS = ("Zzshop", "Zzbasket")
SUBS = ("Pro",)
NUMBERS = (3, 4)
BARE = True
MIXED_BRAND = True
"""

REPORT = """
import json, sys
sys.path.insert(0, {retail!r})
import line_grammar_families
line_grammar_families.__path__.append({extra!r})
import line_grammar as lg
fam = line_grammar_families.families()["zz_probe"]
shop = lg.Deal("zz_probe", ["Acme", "Bolt"], {{}}, "grocery")
scale = lg.Deal("zz_probe", ["Acme", "Bolt"], {{}})
led = [lg.brand_led(d) for d in range(30)]
titles = []
for draw in range(30):
    rec = {{"product_type": "Probe Jam", "brand": "Acme", "product_line": "Zzscale",
            "title": "Old Zzscale Probe Jam"}}
    lg.retitle(rec, {{"brand": "Old"}}, draw)
    titles.append(rec["title"])
print(json.dumps({{
    "fields": [list(fam.grocery_leads), fam.bare, fam.mixed_brand],
    "bare_model": lg.is_model("zz_probe", "Acme", "Zzscale"),
    "grocery_word": lg.is_model("zz_probe", "Acme", "Zzshop Pro 3"),
    "shop": sorted(w for b in ("Acme", "Bolt") for w in shop.of(b)),
    "scale": sorted(w for b in ("Acme", "Bolt") for w in scale.of(b)),
    "owned": [shop.owned("Acme", i) for i in range(5)],
    "led": led,
    "titles": titles,
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


def test_a_probe_module_with_the_three_attributes_yields_a_family_with_those_fields(tmp_path):
    done = _run(tmp_path, REPORT, {"zz_probe": PROBE})
    assert done.returncode == 0, done.stderr
    got = json.loads(done.stdout)
    assert got["fields"] == [["Zzshop", "Zzbasket"], True, True]
    assert got["bare_model"] is True, "BARE: the lead word alone is a model"
    assert got["grocery_word"] is True, "is_model accepts both lead halves"
    assert got["shop"] == ["Zzbasket", "Zzshop"] and got["scale"] == ["Zzother", "Zzscale"]
    assert got["owned"][0] in ("Zzshop", "Zzbasket") and got["owned"][1].split()[-1] == "Pro"
    assert 0 < sum(got["led"]) < 30
    for led, title in zip(got["led"], got["titles"], strict=True):
        assert title == ("Acme Zzscale Probe Jam" if led else "Zzscale Probe Jam"), title


def test_a_grocery_lead_another_module_holds_is_refused(tmp_path):
    clash = PROBE.replace("Zzshop", "Speed")
    done = _run(tmp_path, ERROR, {"zz_probe": clash})
    assert done.returncode != 0
    assert "Speed" in done.stderr and "zz_probe" in done.stderr


def test_a_grocery_lead_that_repeats_its_own_lead_is_refused(tmp_path):
    clash = PROBE.replace("Zzshop", "Zzscale")
    done = _run(tmp_path, ERROR, {"zz_probe": clash})
    assert done.returncode != 0 and "Zzscale" in done.stderr


def test_a_shipped_module_without_the_attributes_keeps_the_defaults():
    sys.path.insert(0, str(RETAIL))
    try:
        import line_grammar_families as pkg

        found = pkg.families()
    finally:
        sys.path.remove(str(RETAIL))
    sport = found["sport"]
    assert (sport.grocery_leads, sport.bare, sport.mixed_brand) == ((), False, False)
    for name in ("pantry", "drink", "alcohol"):
        assert name in found
        fam = found[name]
        assert fam.bare and fam.mixed_brand and fam.grocery_leads and fam.leads

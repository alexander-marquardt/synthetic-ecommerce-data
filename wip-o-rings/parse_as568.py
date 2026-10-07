"""Parse the AS568 chart text (pdftotext -layout) into module rows."""

import re
import sys
from fractions import Fraction

FRAC = r"(?:\d+ \d+/\d+|\d+/\d+|\d+)"
ROW = re.compile(
    rf"-(\d{{3}})(?: 1/2)?\s+(\d*\.\d+) ± (\.\d+)\s+(\.\d+) ± (\.\d+)\s+({FRAC})\s+({FRAC})\s+({FRAC})"
)


def frac(text: str) -> Fraction:
    total = Fraction(0)
    for part in text.split():
        total += Fraction(part)
    return total


rows = {}
for line in open(sys.argv[1], encoding="utf-8"):
    for m in ROW.finditer(line):
        whole = m.group(0)
        if whole.startswith("-001 1/2"):
            continue
        dash = m.group(1)
        rows[dash] = (
            dash,
            m.group(2),
            m.group(3),
            m.group(4),
            m.group(5),
            m.group(6),
            m.group(7),
            m.group(8),
        )

dashes = sorted(rows)
print("rows", len(rows), file=sys.stderr)
series = {}
for d in dashes:
    series.setdefault(d[0], []).append(rows[d])
for s, rs in series.items():
    noms = [frac(r[5]) for r in rs]
    css = {r[3] for r in rs}
    dup = len(noms) != len(set(noms))
    print(s, len(rs), rs[0][0], rs[-1][0], "cs", css, "dup-nominal", dup, file=sys.stderr)
    if dup:
        seen = {}
        for r in rs:
            seen.setdefault(frac(r[5]), []).append(r[0])
        print({str(k): v for k, v in seen.items() if len(v) > 1}, file=sys.stderr)
    # ID strictly increasing
    ids = [float(r[1]) for r in rs]
    assert ids == sorted(ids), s
for s, rs in series.items():
    print(f"# {s}xx")
    for r in rs:
        dash, i, it, c, ct, nid, nod, nw = r
        print(f'    ("{dash}", {float(i)!r}, {float(it)!r}, {float(c)!r}, {float(ct)!r}, "{nid}"),')

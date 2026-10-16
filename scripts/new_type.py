#!/usr/bin/env python3
"""Write the spec file of a new retail product type (gen#351).

    uv run python scripts/new_type.py <key> --kind clothing|beauty --product-type "Tracksuit"

writes ``prototypes/retail_drawings/type_specs/<key>.py``: one ``SPEC = TypeSpec(...)`` with a
working example row. Edit that file and nothing else: the registry finds it, the scaled build
and the figures read the registry, and ``tests/test_retail_type_specs_351.py`` holds every spec
to the same checks. Then regenerate the figures (``docs/new-type-quick-path.md``). The command
refuses a key whose file exists, and a key that is not lower-case words joined by underscores.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SPECS = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings" / "type_specs"
KEY = re.compile(r"[a-z][a-z0-9_]*")
CODE = re.compile(r"[A-Z][A-Z0-9]{2,5}")

#: What a kind fills in: the department, the example row's leaf and drawing shape, its sizes and
#: the attributes a shopper filters the type on. The example uses a shape the kit already draws.
KINDS = {
    "clothing": {
        "department": "Clothing",
        "path": '("Womens", "Tops", "Jersey Tops")',
        "shape": "top",
        "brand": "Larkmoor",
        "row": "LRow",
        "extra": '            facts=(("size_range", ["regular"]), ("pattern", "plain")),\n',
        "sizes": 'sizes(20.0, ("XS", "S", "M", "L", "XL"))',
        "colors": '(cw("Navy", "#26365c"), cw("Black", "#2f2f35"))',
        "attrs": '(a("fabric", "Fabric", "Cotton"), a("fit", "Fit", "Regular"))',
        "colorless": "",
        "apparel": "    apparel=ApparelPlan(),\n",
        "imports": "ApparelPlan, LRow, TypeSpec, a, cw, sizes",
    },
    "beauty": {
        "department": "Beauty",
        "path": '("Beauty", "Hair Care", "{leaf}")',
        "shape": "bottle",
        "brand": "Mirefield Naturals",
        "row": "Row",
        "extra": "",
        "sizes": '(("250ml", 6.0), ("500ml", 10.0))',
        "colors": '(cw("Amber", "#c98a2e", "solid", "#ffffff"),)',
        "attrs": '(a("ingredient", "Ingredient", "Argan Oil"),)',
        "colorless": "            colorless=True,\n",
        "apparel": "",
        "imports": "Row, TypeSpec, a, cw",
    },
}

TEMPLATE = '''"""{title} (gen#351 scaffold): edit this file only.

Replace the example row with the type's real rows (a style is its colors times its sizes), then
set ``derivable`` True only if the scaled build should draw more styles from them. The leaf
(``path``), the drawing ``shape`` and the attribute keys must be ones the catalog already uses;
a shape the kit lacks is defined in this module and added with ``kit.register``.
"""

from __future__ import annotations

from type_registry import {imports}

SPEC = TypeSpec(
    key="{key}",
    department="{department}",
    product_type="{ptype}",
    derivable={derivable},
{apparel}    rows=(
        {row}(
            code="{code}",
            title="{title}",
            brand="{brand}",
            department="{department}",
            path={path},
            product_type="{ptype}",
            price=20.0,
            shape="{shape}",
            description="A {lower} for the example row: replace this text.",
            colors={colors},
            attrs={attrs},
            sizes={sizes},
{colorless}{extra}        ),
    ),
)
'''


def pick_code(key: str, taken: set[str]) -> str:
    """The row code of the example row: the key cut to six letters, or that with a digit at the
    end when a registered spec already builds ``BRD-<code>``. Two keys that share their first
    six letters (``specimen_kaftan``, ``specimen_serum``) would otherwise build one id."""
    base = key.replace("_", "").upper()[:6] or "EXMPLE"
    code, n = base, 1
    while f"BRD-{code}" in taken and n < 100:
        n += 1
        code = base[: 6 - len(str(n))] + str(n)
    return code


def _taken() -> set[str]:
    """Every product id the registered specs build (the rows still outside the registry are
    checked by the build, which names the clash)."""
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "prototypes" / "retail_drawings"), str(root / "src")]
    import type_registry

    return {i for s in type_registry.specs().values() for i in type_registry.ids_of(s)}


def render(key: str, kind: str, ptype: str, code: str | None = None) -> str:
    spec = KINDS[kind]
    leaf = ptype + ("es" if ptype.endswith("s") else "s")
    return TEMPLATE.format(
        title=f"Example {ptype}", key=key, ptype=ptype, lower=ptype.lower(), row=spec["row"],
        department=spec["department"], path=spec["path"].format(leaf=leaf),
        code=code or pick_code(key, set()), brand=spec["brand"],
        shape=spec["shape"], colors=spec["colors"], attrs=spec["attrs"], sizes=spec["sizes"],
        imports=spec["imports"], apparel=spec["apparel"],
        colorless=spec["colorless"], extra=spec["extra"],
        derivable="True" if kind == "beauty" else "False",
    )  # fmt: skip


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("key", help="lower-case words joined by underscores; the file is <key>.py")
    ap.add_argument("--kind", choices=sorted(KINDS), required=True)
    ap.add_argument("--product-type", required=True, help='the shopper-facing type, "Tracksuit"')
    ap.add_argument("--out", type=Path, default=SPECS, help="the directory to write into")
    ap.add_argument("--code", help="the example row's code (3-6 capitals); default: from the key")
    args = ap.parse_args(argv)
    if not KEY.fullmatch(args.key):
        print(f"new_type: {args.key!r} is not lower-case words joined by underscores")
        return 2
    path = args.out / f"{args.key}.py"
    if path.exists():
        print(f"new_type: {path} exists; edit it, the scaffold never overwrites a spec")
        return 2
    taken = _taken()
    if args.code and not CODE.fullmatch(args.code):
        print(f"new_type: --code {args.code!r} is not 3 to 6 capitals and digits, capital first")
        return 2
    if args.code and f"BRD-{args.code}" in taken:
        print(f"new_type: BRD-{args.code} is built by a registered spec; pick another code")
        return 2
    code = args.code or pick_code(args.key, taken)
    path.write_text(render(args.key, args.kind, args.product_type, code), encoding="utf-8")
    print(f"wrote {path}\nnext: edit it, then see docs/new-type-quick-path.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

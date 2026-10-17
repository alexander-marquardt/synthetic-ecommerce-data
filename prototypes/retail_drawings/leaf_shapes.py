"""The shape a garment leaf is drawn with, one place for all its rows (gen#447).

A believability audit found garments drawn as another garment than their title and category name:
a bomber and a puffer as a double-breasted trench (``coat``), a shirt dress as a strappy sundress,
a long sleeve top and a polo as a short-sleeved tee, cargo trousers as plain chinos, pyjama shorts
as chinos with belt loops. The rows that say so sit in a dozen row modules, and every text-match
decoy of them (:mod:`decoy_apparel`) clones its exemplar's drawing, so a wrong shape was copied
into dozens of decoys.

:data:`RULES` is the allow-list: a leaf (or a product type) -> the shape and the parameters that
draw it as itself. :func:`apply` sets them on the authored templates, before the decoys clone
them (:func:`scale.templates`); :func:`violations` is the check ``test_shape_honesty.py`` runs, so
a new row of a listed leaf drawn another way is named, not silently shipped.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Rule:
    """``shape`` and ``params`` for the templates of ``leaves`` (the last category-path name) and
    of ``types`` (the ``product_type``). ``params`` replace the same keys of the row's own; a row's
    other parameters (a top's neckline, a trouser's fit) stay."""

    name: str
    shape: str
    leaves: tuple[str, ...] = ()
    types: tuple[str, ...] = ()
    params: dict[str, str] = field(default_factory=dict)

    def matches(self, tpl: dict) -> bool:
        return tpl["category_path"][-1] in self.leaves or tpl["product_type"] in self.types


RULES: tuple[Rule, ...] = (
    Rule("bomber", "bomber_jacket", ("Bomber Jackets",), ("Bomber Jacket",)),
    Rule("puffer", "puffer_jacket", ("Puffer Jackets",), ("Puffer Jacket",)),
    Rule("polo", "top", ("Polos",), ("Polo Shirt",),
         {"kind": "polo", "neckline": "polo", "sleeve": "short"}),
    Rule("long sleeve", "top", ("Long Sleeve Tops",), (), {"sleeve": "long"}),
    Rule("shirt dress", "shirt_dress", ("Shirt Dresses",)),
    Rule("cargo trousers", "trousers", ("Cargo Trousers",), (),
         {"cargo": "yes", "style": "chino"}),
    # Pyjama shorts are plain: an elastic waist and no pockets or belt loops.
    Rule("pyjama shorts", "shorts", (), ("Pyjama Shorts",), {"length": "mini", "style": "sweat", "pocket": "no"}),
    Rule("knee boots", "shoe", ("Knee High Boots",), (), {"kind": "knee_boot"}),
)  # fmt: skip


def rule_for(tpl: dict) -> Rule | None:
    return next((r for r in RULES if r.matches(tpl)), None)


def apply(tpls: list[dict]) -> list[dict]:
    """``tpls`` with the drawing of every listed leaf set to its rule's shape and parameters."""
    for tpl in tpls:
        rule = rule_for(tpl)
        if rule is None:
            continue
        drawing = tpl["drawing"]
        drawing["shape"] = rule.shape
        if rule.params:
            drawing["params"] = {**(drawing.get("params") or {}), **rule.params}
    return tpls


def violations(tpls: list[dict]) -> list[str]:
    """One line per template whose drawing is not its rule's: the shape or a parameter differs."""
    out = []
    for tpl in tpls:
        rule = rule_for(tpl)
        if rule is None:
            continue
        drawing = tpl["drawing"]
        params = drawing.get("params") or {}
        wrong = [] if drawing["shape"] == rule.shape else [f"shape {drawing['shape']}"]
        wrong += [f"{k}={params.get(k)}" for k, v in rule.params.items() if params.get(k) != v]
        if wrong:
            out.append(f"{tpl['product_id']} {tpl['title']!r} ({rule.name}): {', '.join(wrong)}")
    return out

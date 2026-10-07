"""Catalog-copy noise: the true-but-distracting sentences a distributor's text carries.

A real catalog's copy mentions sizes and materials a product is NOT, the
siblings it is also sold in, the units a shopper might have typed, what it
pairs with and what it cuts. Every one of those words is searchable, so a
query matches more than the products it names, and the policies and facets
are what narrow the page back down. A catalog without that noise let the
words alone do the narrowing, and nothing showed a filter or a facet at work.

Every sentence here is TRUE of its record, read from the record's own
published values, its siblings, or a table in this module, and checked by
``tests/test_noise_text.py`` sentence type by sentence type. Attributes are
never touched: the noise lives in the description and the searchable text
only, so the facets can always separate it out, and a build with the knob
off (``GeneratorConfig.noise = 0``) has identical attributes.

THE KNOB. ``GeneratorConfig.noise`` scales every rate below; 1.0 is the
realistic default, 0 is a clean catalog. Each record's draws come from its
OWN stream, seeded by the catalog seed and the SKU, so the noise never moves
a draw of the main generation -- which is what makes the clean and the noisy
builds comparable record for record.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Mapping, Sequence
from fractions import Fraction

from ..dimensions import DimensionParseError, parse_length
from . import compat, conformance, standards
from .standards import MM_PER_INCH

#: Per-sentence-type rate at ``noise = 1.0``, each an independent draw.
#: UNIT_EQUIVALENT is the one with a stated bound: 15-20% of eligible records
#: (maintainer ruling, 2026-09-29) -- the facets expand units themselves, so a
#: result must show the facet working, not text luck.
RATES: dict[str, float] = {
    "negative": 0.25,
    "also_available": 0.30,
    "unit_equivalent": 0.175,
    "fit_or_pairing": 0.30,
    "material_contrast": 0.30,
    "work_material": 0.35,
    "standards": 0.35,
    "application": 0.40,
}
UNIT_EQUIVALENT_SHARE = (0.15, 0.20)

# --- tables --------------------------------------------------------------------

#: The diameter series a "not for" names its neighbours from.
METRIC_DIAMETERS = ("M3", "M4", "M5", "M6", "M8", "M10", "M12", "M16", "M20", "M24")
INCH_DIAMETERS = ("#6", "#8", "#10", "1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "1")

#: What a cutting tool of each material cuts, from common machining practice:
#: high speed steel the soft and mild metals, cobalt adds stainless, carbide
#: adds cast iron and hardened steel.
WORK_MATERIALS: dict[str, tuple[str, ...]] = {
    "High Speed Steel": ("aluminum", "brass", "mild steel"),
    "Powdered Metal": ("aluminum", "mild steel", "stainless steel"),
    "Cobalt": ("aluminum", "brass", "mild steel", "stainless steel"),
    "Solid Carbide": (
        "aluminum",
        "brass",
        "mild steel",
        "stainless steel",
        "cast iron",
        "hardened steel",
    ),
}

#: Standards with the SAME dimensions under another designation -- the one
#: table the Standards attribute reads too, so both spell a designation alike.
EQUIVALENT_STANDARDS: dict[str, str] = conformance.EQUIVALENTS

#: Property classes and grades, each with one it is stronger than (minimum
#: tensile strength, ISO 898-1 and SAE J429).
STRONGER_THAN: dict[str, str] = {
    "Class 10.9": "Class 8.8",
    "Grade 8": "Grade 5",
    "Class 10": "Class 8",
}

#: ISO 492 Normal tolerance class, bore deviation (upper 0, lower -value mm),
#: by bore size range (over, up to) in mm.
BORE_TOLERANCE_MM: tuple[tuple[float, float, float], ...] = (
    (2.5, 10.0, 0.008),
    (10.0, 18.0, 0.008),
    (18.0, 30.0, 0.010),
    (30.0, 50.0, 0.012),
)

THREADED = {
    "screw_socket_head": "Dia./Thread Size",
    "screw_flat_head": "Dia./Thread Size",
    "screw_button_head": "Dia./Thread Size",
    "screw_low_head": "Dia./Thread Size",
    "bolt_hex": "Dia./Thread Size",
    "nut_hex": "Thread Size",
    "lock_nuts_nylon_insert": "Thread Size",
    "tap_spiral_point": "Thread Size",
}
CUTTING = ("end_mill_square", "end_mill_ball", "drill_jobber", "tap_spiral_point")
FASTENERS = (
    *compat.SOCKET_SCREWS,
    "bolt_hex",
    "nut_hex",
    "lock_nuts_nylon_insert",
    "washer_flat",
)

#: The attribute a type's unit equivalent is written for.
UNIT_PRIMARY = {
    "end_mill_square": "Milling Dia.",
    "end_mill_ball": "Milling Dia.",
    "drill_jobber": "Size",
    "hex_key": "Size",
    "bearing_radial_ball": "Bore",
    "wheel_depressed_center": "Diameter",
    "abrasive_flap_disc": "Diameter",
    "dowel_pins": "Diameter",
}


def record_rng(seed: int, sku: str) -> random.Random:
    digest = hashlib.sha256(f"{seed}:noise:{sku}".encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def _join(items: Sequence[str]) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def _inches(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return parse_length(value).inches
    except DimensionParseError:
        return None


# --- the sentences ---------------------------------------------------------------


def negative(type_key: str, values: Mapping[str, str]) -> str | None:
    """``Not for M10 or M16 threads.`` -- the neighbouring diameters, which cannot fit."""
    if type_key in THREADED:
        designation = values.get(THREADED[type_key])
        if not designation:
            return None
        diameter = compat.diameter_of(designation)
        series = METRIC_DIAMETERS if diameter.startswith("M") else INCH_DIAMETERS
        if diameter not in series:
            return None
        i = series.index(diameter)
        near = [series[j] for j in (i - 1, i + 1) if 0 <= j < len(series)]
        spelled = [d if d.startswith(("M", "#")) else f'{d}"' for d in near]
        return f"Not for {' or '.join(spelled)} threads."
    if type_key == "hex_key":
        size = values.get("Size")
        size_in = _inches(size)
        if size_in is None or size is None:
            return None
        metric = size.strip().endswith("mm")
        series = (
            [k / MM_PER_INCH for k in compat.KEY_SERIES_MM]
            if metric
            else list(compat.KEY_SERIES_IN)
        )
        smaller = [k for k in series if k < size_in - 1e-6]
        if not smaller:
            return None
        return f"Will not fit {_key(smaller[-1], metric)} sockets."
    return None


def _key(size_in: float, metric: bool) -> str:
    if metric:
        return f"{size_in * MM_PER_INCH:g}mm"
    frac = Fraction(round(size_in * 64), 64)
    return f'{frac}"' if abs(float(frac) - size_in) < 1e-9 else f'{size_in:.3f}"'


def also_available(primary: str | None, siblings: Sequence[str]) -> str | None:
    """``Also available in M8 / M10 / M16 sizes.`` -- only sizes the product's other SKUs are.

    Only when the variant axis IS a size (a length or a thread): a bearing's
    closure or a wheel's grit is not a size, and "Also available in Double
    Shield / Open sizes" says something false about the word.
    """
    if primary is None or not _is_size(primary):
        return None
    others = [s for s in dict.fromkeys(siblings) if s and s != primary]
    if not others:
        return None
    # " / " between sizes and a closing word, because a size may itself end in
    # a period (``5/32 in.``) and the sentence has to end unambiguously.
    return f"Also available in {' / '.join(others[:3])} sizes."


def _is_size(value: str) -> bool:
    """A length (parses with a unit) or a thread designation."""
    if _inches(value) is not None and not value.strip().replace(".", "").isdigit():
        return True
    return (
        bool(value)
        and (value.startswith(("M", "#")) or "-" in value)
        and any(c.isdigit() for c in value)
    )


def unit_equivalent(type_key: str, values: Mapping[str, str]) -> str | None:
    """``12mm (approx. 15/32")`` / ``1/2" (approx. 12.7mm)`` -- the other system, rounded."""
    name = UNIT_PRIMARY.get(type_key)
    value = values.get(name) if name else None
    size_in = _inches(value)
    if value is None or size_in is None or size_in <= 0:
        return None
    if value.strip().endswith("mm"):
        # To the nearest 64th, the finest step imperial tooling is sized in.
        frac = Fraction(round(size_in * 64), 64)
        if frac == 0:
            return None
        other = f'{frac}"' if frac.denominator > 1 else f'{frac.numerator}"'
    else:
        other = f"{size_in * MM_PER_INCH:.1f}mm"
    return f"{value.strip()} (approx. {other})."


def fit_or_pairing(type_key: str, values: Mapping[str, str]) -> str | None:
    """Bore tolerance for a metric bearing; what a screw or bolt pairs with."""
    if type_key == "bearing_radial_ball":
        bore = values.get("Bore")
        bore_in = _inches(bore)
        if bore is None or bore_in is None or not bore.strip().endswith("mm"):
            return None
        mm = round(bore_in * MM_PER_INCH, 3)
        for low, high, tol in BORE_TOLERANCE_MM:
            if low < mm <= high:
                return f"Bore {mm - tol:.3f}-{mm:.3f}mm (ISO 492 Normal class)."
        return None
    designation = values.get("Dia./Thread Size")
    if not designation:
        return None
    if type_key in compat.SOCKET_SCREWS:
        key = compat.drive_sentence(values.get("Drive Size"))
        if key is None:
            return None
        key_text = key.removeprefix("Takes a ").removesuffix(" hex key.")
        return f"Pair with {designation} hex nuts and a {key_text} hex key."
    if type_key == "bolt_hex":
        diameter = compat.diameter_of(designation)
        if diameter in standards.available_sizes("ISO 7089"):
            return f"Pair with {designation} hex nuts and {diameter} flat washers."
        return f"Pair with {designation} hex nuts."
    return None


def material_contrast(type_key: str, values: Mapping[str, str]) -> str | None:
    """``Zinc-plated steel (not stainless).`` -- what the part is NOT, stated beside what it is."""
    if type_key not in FASTENERS:
        return None
    material = values.get("Material", "")
    finish = values.get("Finish", "")
    if "Stainless" in material:
        # "not plated", never "not zinc plated": the finish's own NAME in a
        # negation would put "zinc plated" on stainless records, and a policy
        # that trusts the whole finish name only where every record carrying
        # it has that finish would then stop trusting it.
        return f"{material} (not plated)." if finish in ("", "Plain") else None
    if material == "Brass":
        return "Brass (not steel)."
    if material in ("Steel", "Alloy Steel") and finish == "Zinc Plated":
        return f"Zinc-plated {material.lower()} (not stainless)."
    if material == "Steel":
        return "Note: not alloy steel."
    return None


def work_material(type_key: str, values: Mapping[str, str]) -> str | None:
    """``Suitable for aluminum, brass and mild steel.`` -- by the tool's own material."""
    if type_key not in CUTTING:
        return None
    cuts = WORK_MATERIALS.get(values.get("Material", ""))
    return f"Suitable for {_join(cuts)}." if cuts else None


def standards_reference(type_key: str, values: Mapping[str, str], provenance: str) -> str | None:
    """``Equivalent to DIN 912 / ISO 4762.``; ``Higher strength than Class 8.8.``"""
    grade = values.get("Grade", "")
    if type_key == "bolt_hex" and grade in STRONGER_THAN:
        return f"Higher strength than {STRONGER_THAN[grade]}."
    if type_key == "nut_hex" and grade in STRONGER_THAN:
        return f"Higher strength than {STRONGER_THAN[grade]}."
    equivalent = EQUIVALENT_STANDARDS.get(provenance)
    if equivalent is None:
        return None
    return f"Equivalent to {equivalent} / {provenance}."


def application(type_key: str) -> str | None:
    """``For use with socket cap screws.`` -- what a hex key is for."""
    return "For use with socket cap screws." if type_key == "hex_key" else None


def sentences(
    type_key: str,
    values: Mapping[str, str],
    *,
    sku: str,
    seed: int,
    noise: float,
    provenance: str,
    primary: str | None,
    siblings: Sequence[str],
) -> list[str]:
    """This record's noise sentences, in a fixed order, from its own stream."""
    if noise <= 0:
        return []
    rng = record_rng(seed, sku)
    candidates = (
        ("negative", lambda: negative(type_key, values)),
        ("also_available", lambda: also_available(primary, siblings)),
        ("unit_equivalent", lambda: unit_equivalent(type_key, values)),
        ("fit_or_pairing", lambda: fit_or_pairing(type_key, values)),
        ("material_contrast", lambda: material_contrast(type_key, values)),
        ("work_material", lambda: work_material(type_key, values)),
        ("standards", lambda: standards_reference(type_key, values, provenance)),
        ("application", lambda: application(type_key)),
    )
    out: list[str] = []
    for kind, make in candidates:
        # Drawn for every kind whether or not it applies, so one kind's
        # eligibility never shifts another's draw.
        draw = rng.random()
        if draw < min(1.0, RATES[kind] * noise):
            sentence = make()
            if sentence:
                out.append(sentence)
    return out

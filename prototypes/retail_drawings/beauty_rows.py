"""Retail beauty depth (gen#214): data only.

The beauty range held lipstick, foundation, eyeliner, highlighter, a skin tint, a face powder, a
perfume and a few creams, so a search for a mascara, a setting spray, a serum or an aftershave
found an unrelated make-up item and finish, skin-concern and size had nothing to filter. This
module adds ten types, each a leaf with its own drawing (:mod:`kit_beauty`), three or more styles
from three or more invented brands, its key attributes as structured entries and the SKU axis the
issue names:

==============  ============================================  =============================
type            key attributes                                SKUs
==============  ============================================  =============================
Mascara         effect, waterproof                            shade
Face Primer     finish, skin type                             size (ml)
Setting Spray   finish, skin type                             size (ml)
Serum           active, skin concern                          size (ml)
Face Mask       mask type, skin concern                       pack count
Eye Patches     patch type, skin concern                      pack count (pairs)
Body Mist       fragrance family                              fragrance x size (ml)
Aftershave      fragrance family, concentration               size (ml)
Talc            fragrance                                     size (g)
Sun Cream       area (face or body)                           SPF x size (ml)
==============  ============================================  =============================

A mascara's shades are a declared exception to the six main colors (``main_colors.EXCEPTIONS``);
every other type is sold in its one pack and carries no color. The styles are templates only:
:func:`scale.derivable` leaves them out, so the range grows by authored rows.

**Text-match decoys (gen#294).** Every type carries :data:`DECOYS`, one of each class, a clone of
the type's first style whose words mislead a plain text search while its fields tell the truth:

1. **part**: the word names a cap, a lid or a pack ("Pink Cap Volume Mascara" is black).
2. **range**: the word sits in a short range name ("Green Valley Length Mascara").
3. **brand**: an invented brand holds the word ("Red Kestrel Curl Mascara").

A decoy's id is in ``scale.BEAUTY_DECOY_IDS``, exempt by id from the text-agrees check. Every name
is invented.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import dataclass, fields

import kit_beauty  # noqa: F401 -- registers the beauty shapes
from breadth_rows import OWNERS, Row
from variants import cw

D = "Beauty"
_EYES = (D, "Make-Up", "Eyes", "Mascara")
_FACE = (D, "Make-Up", "Face")
_SKIN = (D, "Skincare")
_FRAG = (D, "Fragrance")

#: The invented brands these rows sell, all third party.
_REAL = ("Veilmoor", "Pearlbrook", "Aldermist", "Fenmere", "Thornlea Skin", "Sorrel & Salt")
_DECOY_BRANDS = ("Pink Kestrel", "Dewy Finch", "Vitamin C Orchard", "Clay Wren", "Cloth Wren",
                 "Vanilla Wren", "Citrus Heron", "Rose Kestrel", "Body Kestrel", "Matte Heron")  # fmt: skip
BRANDS = _REAL
OWNERS.update(dict.fromkeys((*_REAL, *_DECOY_BRANDS), "third_party"))

BLACK, BROWN = cw("Black", "#2a2a2e"), cw("Brown", "#5a3a28")
BLUE, GREEN, PURPLE = cw("Blue", "#2f4f9a"), cw("Green", "#2f6b4a"), cw("Purple", "#5a3a7a")
PACK = cw("Pack", "#f3eee4")
PACK_ROSE, PACK_SAGE, PACK_SKY = cw("Pack", "#f1d9d6"), cw("Pack", "#d7e4d3"), cw("Pack", "#d6e3ee")
PACK_SAND, PACK_INK = cw("Pack", "#e7dcc6"), cw("Pack", "#2f3a4a")


@dataclass(frozen=True)
class BeautyRow(Row):
    """A :class:`Row` that may also sell over a second axis: ``option`` is ``(sku key, values)``,
    each value crossed with every size (a fragrance times a size, an SPF times a size)."""

    option: tuple = ()

    def skus(self) -> list[dict]:
        sizes = [{self.size_key: s, "price": p} for s, p in self.sizes] or [{"price": self.price}]
        colors = self.colors[:1] if self.colorless else self.colors
        opts = [{self.option[0]: v} for v in self.option[1]] if self.option else [{}]
        return [
            {**({} if self.colorless else {"color": c[0]}), **o, **s, "in_stock": True}
            for c in colors
            for o in opts
            for s in sizes
        ]


@dataclass(frozen=True)
class Decoy(BeautyRow):
    """A text-match decoy: ``cls`` (1 part, 2 range, 3 brand) and the misleading ``word``."""

    cls: int = 0
    word: str = ""


def _a(key: str, name: str, value: str) -> tuple[str, str, str]:
    return (key, name, value)


def _s(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    return tuple((str(v), p) for v, p in pairs)


def _row(code, title, brand, path, ptype, price, shape, desc, attrs, sizes, size_key, params,
         colors=(PACK,), option=(), colorless=True) -> BeautyRow:  # fmt: skip
    return BeautyRow(code, title, brand, D, path, ptype, price, shape, desc, colors, attrs, sizes,
                     size_key=size_key, params=params, colorless=colorless, option=option)  # fmt: skip


def _mascara(code, title, brand, price, effect, wp, desc, colors, wand):
    return _row(code, title, brand, _EYES, "Mascara", price, "mascara", desc,
                (_a("effect", "Effect", effect), _a("waterproof", "Waterproof", wp)), (), "size",
                (("effect", wand),), colors=colors, colorless=False)  # fmt: skip


MASCARAS = (
    _mascara(
        "MSCVOL",
        "Volume Boost Mascara",
        "Veilmoor",
        11.0,
        "Volume",
        "No",
        "A thick, buildable formula and a full brush for big lashes.",
        (BLACK, BROWN, BLUE),
        "volume",
    ),
    _mascara(
        "MSCLNG",
        "Lash Lengthening Mascara",
        "Pearlbrook",
        10.0,
        "Length",
        "No",
        "A long, slim brush that separates and stretches each lash.",
        (BLACK, BROWN, GREEN),
        "length",
    ),
    _mascara(
        "MSCCRL",
        "Curl Lift Waterproof Mascara",
        "Aldermist",
        12.0,
        "Curl",
        "Yes",
        "A curved brush that lifts lashes into a curl that lasts all day and survives rain.",
        (BLACK, PURPLE, BLUE),
        "curl",
    ),
    _mascara(
        "MSCWPV",
        "Waterproof Volume Mascara",
        "Veilmoor",
        13.0,
        "Volume",
        "Yes",
        "A smudge-proof, swim-proof formula with a full brush for dramatic lashes.",
        (BLACK, BROWN),
        "volume",
    ),
    _mascara(
        "MSCWPL",
        "Waterproof Length Mascara",
        "Pearlbrook",
        12.5,
        "Length",
        "Yes",
        "A long-wearing, waterproof formula on a slim brush.",
        (BLACK, BLUE, GREEN),
        "length",
    ),
)

PRIMERS = (
    _row(
        "PRMMAT",
        "Matte Pore Blur Face Primer",
        "Pearlbrook",
        (*_FACE, "Primers"),
        "Face Primer",
        14.0,
        "primer",
        "A silky primer that blurs pores and keeps an oily T-zone shine free all day.",
        (_a("finish", "Finish", "Matte"), _a("skin_type", "Skin type", "Oily")),
        _s((15, 14.0), (30, 22.0)),
        "net_volume_ml",
        (("form", "tube"),),
        colors=(PACK_SAND,),
    ),
    _row(
        "PRMDEW",
        "Dewy Glow Face Primer",
        "Fenmere",
        (*_FACE, "Primers"),
        "Face Primer",
        16.0,
        "primer",
        "A plumping primer for a fresh, lit-from-within base on thirsty skin.",
        (_a("finish", "Finish", "Dewy"), _a("skin_type", "Skin type", "Dry")),
        _s((30, 16.0), (50, 24.0)),
        "net_volume_ml",
        (("form", "pump"),),
        colors=(PACK_ROSE,),
    ),
    _row(
        "PRMRAD",
        "Radiant Skin Primer",
        "Aldermist",
        (*_FACE, "Primers"),
        "Face Primer",
        15.0,
        "primer",
        "A light primer with a soft glow that suits every day and every skin.",
        (_a("finish", "Finish", "Radiant"), _a("skin_type", "Skin type", "Normal")),
        _s((15, 15.0), (30, 23.0)),
        "net_volume_ml",
        (("form", "pump"),),
        colors=(PACK_SKY,),
    ),
    _row(
        "PRMGRP",
        "Grip and Hold Face Primer",
        "Veilmoor",
        (*_FACE, "Primers"),
        "Face Primer",
        13.0,
        "primer",
        "A gripping base that holds make-up in place from desk to dinner.",
        (_a("finish", "Finish", "Satin"), _a("skin_type", "Skin type", "Combination")),
        _s((15, 13.0), (30, 20.0)),
        "net_volume_ml",
        (("form", "tube"),),
        colors=(PACK_SAGE,),
    ),
)

SETTING_SPRAYS = (
    _row(
        "SSPMAT",
        "Matte Finish Setting Spray",
        "Veilmoor",
        (*_FACE, "Setting Sprays"),
        "Setting Spray",
        12.0,
        "setting_spray",
        "A fine mist that locks make-up in place with a shine-free finish for oily skin.",
        (_a("finish", "Finish", "Matte"), _a("skin_type", "Skin type", "Oily")),
        _s((50, 12.0), (100, 18.0)),
        "net_volume_ml",
        (("nozzle", "mist"),),
        colors=(PACK_SAND,),
    ),
    _row(
        "SSPDEW",
        "Dewy Setting Spray",
        "Fenmere",
        (*_FACE, "Setting Sprays"),
        "Setting Spray",
        13.0,
        "setting_spray",
        "A hydrating mist that sets make-up and leaves a fresh, glowing look on dry skin.",
        (_a("finish", "Finish", "Dewy"), _a("skin_type", "Skin type", "Dry")),
        _s((50, 13.0), (100, 19.0)),
        "net_volume_ml",
        (("nozzle", "pump"),),
        colors=(PACK_ROSE,),
    ),
    _row(
        "SSPLNG",
        "Long Wear Setting Spray",
        "Sorrel & Salt",
        (*_FACE, "Setting Sprays"),
        "Setting Spray",
        11.0,
        "setting_spray",
        "A weightless spray that keeps a natural look in place for sixteen hours.",
        (_a("finish", "Finish", "Natural"), _a("skin_type", "Skin type", "Combination")),
        _s((50, 11.0), (100, 17.0), (150, 23.0)),
        "net_volume_ml",
        (("nozzle", "mist"),),
        colors=(PACK_SKY,),
    ),
)

SERUMS = (
    _row(
        "SRMRET",
        "Retinol Night Serum",
        "Thornlea Skin",
        (*_SKIN, "Serums"),
        "Serum",
        24.0,
        "serum",
        "A night serum with encapsulated retinol that smooths the look of lines.",
        (_a("active", "Active", "Retinol"), _a("skin_concern", "Skin concern", "Fine Lines")),
        _s((15, 24.0), (30, 38.0)),
        "net_volume_ml",
        (("form", "dropper"),),
        colors=(PACK_INK,),
    ),
    _row(
        "SRMVTC",
        "Vitamin C Brightening Serum",
        "Fenmere",
        (*_SKIN, "Serums"),
        "Serum",
        20.0,
        "serum",
        "A fresh daily serum with stabilised vitamin C to wake up skin that looks tired.",
        (_a("active", "Active", "Vitamin C"), _a("skin_concern", "Skin concern", "Dullness")),
        _s((15, 20.0), (30, 32.0), (50, 44.0)),
        "net_volume_ml",
        (("form", "dropper"),),
        colors=(PACK_SAND,),
    ),
    _row(
        "SRMHYA",
        "Hyaluronic Acid Hydrating Serum",
        "Pearlbrook",
        (*_SKIN, "Serums"),
        "Serum",
        18.0,
        "serum",
        "A water-light serum with three weights of hyaluronic acid that plumps and comforts.",
        (_a("active", "Active", "Hyaluronic Acid"), _a("skin_concern", "Skin concern", "Dryness")),
        _s((30, 18.0), (50, 26.0)),
        "net_volume_ml",
        (("form", "pump"),),
        colors=(PACK_SKY,),
    ),
    _row(
        "SRMNIA",
        "Niacinamide Pore Serum",
        "Thornlea Skin",
        (*_SKIN, "Serums"),
        "Serum",
        15.0,
        "serum",
        "A lightweight serum with ten percent niacinamide that tightens the look of enlarged pores.",
        (_a("active", "Active", "Niacinamide"), _a("skin_concern", "Skin concern", "Blemishes")),
        _s((30, 15.0), (50, 22.0)),
        "net_volume_ml",
        (("form", "pump"),),
        colors=(PACK_SAGE,),
    ),
)

FACE_MASKS = (
    _row(
        "FMSSHT",
        "Hydrating Sheet Face Mask",
        "Pearlbrook",
        (*_SKIN, "Face Masks"),
        "Face Mask",
        2.5,
        "face_mask",
        "A soaked cotton sheet mask that leaves skin soft and bouncy in fifteen minutes.",
        (_a("mask_type", "Mask type", "Sheet"), _a("skin_concern", "Skin concern", "Dryness")),
        _s((1, 2.5), (5, 11.0), (10, 20.0)),
        "units_per_pack",
        (("mask", "sheet"),),
        colors=(PACK_SKY,),
    ),
    _row(
        "FMSCLY",
        "Purifying Clay Face Mask",
        "Thornlea Skin",
        (*_SKIN, "Face Masks"),
        "Face Mask",
        9.0,
        "face_mask",
        "A rinse-off kaolin mask that draws out oil and clears the look of pores.",
        (_a("mask_type", "Mask type", "Clay"), _a("skin_concern", "Skin concern", "Blemishes")),
        _s((1, 9.0), (2, 16.0), (3, 22.0)),
        "units_per_pack",
        (("mask", "clay"),),
        colors=(PACK_SAGE,),
    ),
    _row(
        "FMSNGT",
        "Overnight Repair Face Mask",
        "Aldermist",
        (*_SKIN, "Face Masks"),
        "Face Mask",
        14.0,
        "face_mask",
        "A rich leave-on mask that works while you sleep to smooth the look of lines.",
        (
            _a("mask_type", "Mask type", "Overnight"),
            _a("skin_concern", "Skin concern", "Fine Lines"),
        ),
        _s((1, 14.0), (2, 26.0)),
        "units_per_pack",
        (("mask", "overnight"),),
        colors=(PACK_ROSE,),
    ),
)

EYE_PATCHES = (
    _row(
        "EYPHYD",
        "Hydrogel Eye Patches",
        "Aldermist",
        (*_SKIN, "Eye Patches"),
        "Eye Patches",
        8.0,
        "eye_patches",
        "Cooling hydrogel patches that ease a puffy morning look in ten minutes.",
        (
            _a("patch_type", "Patch type", "Hydrogel"),
            _a("skin_concern", "Skin concern", "Puffiness"),
        ),
        _s((6, 8.0), (30, 24.0)),
        "units_per_pack",
        (("patch", "hydrogel"),),
        colors=(PACK_SKY,),
    ),
    _row(
        "EYPCOL",
        "Collagen Under Eye Patches",
        "Sorrel & Salt",
        (*_SKIN, "Eye Patches"),
        "Eye Patches",
        10.0,
        "eye_patches",
        "Soft cloth patches with marine collagen to smooth the fine skin under the eye.",
        (_a("patch_type", "Patch type", "Cloth"), _a("skin_concern", "Skin concern", "Fine Lines")),
        _s((8, 10.0), (24, 26.0)),
        "units_per_pack",
        (("patch", "cloth"),),
        colors=(PACK_ROSE,),
    ),
    _row(
        "EYPGLD",
        "Brightening Gel Eye Patches",
        "Veilmoor",
        (*_SKIN, "Eye Patches"),
        "Eye Patches",
        12.0,
        "eye_patches",
        "Gel patches with caffeine that brighten the look of tired eyes.",
        (_a("patch_type", "Patch type", "Gel"), _a("skin_concern", "Skin concern", "Dark Circles")),
        _s((6, 12.0), (30, 34.0)),
        "units_per_pack",
        (("patch", "hydrogel"),),
        colors=(PACK_SAND,),
    ),
)

BODY_MISTS = (
    _row(
        "BMSFLR",
        "Peony Blossom Body Mist",
        "Fenmere",
        (*_FRAG, "Body Mists"),
        "Body Mist",
        7.0,
        "body_mist",
        "A light, floral veil of petals to spritz over skin and clothes.",
        (_a("fragrance_family", "Fragrance family", "Floral"),),
        _s((100, 7.0), (250, 12.0)),
        "net_volume_ml",
        (("cap", "dome"),),
        colors=(PACK_ROSE,),
        option=("fragrance", ("Peony", "Rose", "Jasmine")),
    ),
    _row(
        "BMSFRT",
        "Berry Burst Body Mist",
        "Sorrel & Salt",
        (*_FRAG, "Body Mists"),
        "Body Mist",
        6.0,
        "body_mist",
        "A juicy, sparkling mist of summer berries.",
        (_a("fragrance_family", "Fragrance family", "Fruity"),),
        _s((100, 6.0), (250, 11.0)),
        "net_volume_ml",
        (("cap", "ring"),),
        colors=(PACK_SKY,),
        option=("fragrance", ("Strawberry", "Peach", "Cherry")),
    ),
    _row(
        "BMSGRM",
        "Vanilla Sugar Body Mist",
        "Veilmoor",
        (*_FRAG, "Body Mists"),
        "Body Mist",
        7.5,
        "body_mist",
        "A warm, sweet mist that smells like fresh baking.",
        (_a("fragrance_family", "Fragrance family", "Gourmand"),),
        _s((100, 7.5), (250, 13.0)),
        "net_volume_ml",
        (("cap", "dome"),),
        colors=(PACK_SAND,),
        option=("fragrance", ("Vanilla", "Caramel", "Coconut")),
    ),
)

AFTERSHAVES = (
    _row(
        "ASHWDY",
        "Cedar Woods Aftershave",
        "Thornlea Skin",
        (*_FRAG, "Aftershave"),
        "Aftershave",
        14.0,
        "aftershave",
        "A calming splash of cedar and oak moss for freshly shaved skin.",
        (
            _a("fragrance_family", "Fragrance family", "Woody"),
            _a("concentration", "Concentration", "Aftershave Splash"),
        ),
        _s((50, 14.0), (100, 22.0)),
        "net_volume_ml",
        (("cap", "stopper"),),
        colors=(PACK_INK,),
    ),
    _row(
        "ASHFRS",
        "Ocean Fresh Eau de Toilette for Men",
        "Aldermist",
        (*_FRAG, "Aftershave"),
        "Aftershave",
        24.0,
        "aftershave",
        "A clean, salty eau de toilette with sea notes and a crisp finish.",
        (
            _a("fragrance_family", "Fragrance family", "Aquatic"),
            _a("concentration", "Concentration", "Eau de Toilette"),
        ),
        _s((50, 24.0), (100, 36.0)),
        "net_volume_ml",
        (("cap", "spray"),),
        colors=(PACK_SKY,),
    ),
    _row(
        "ASHSPC",
        "Black Pepper Eau de Cologne",
        "Pearlbrook",
        (*_FRAG, "Aftershave"),
        "Aftershave",
        18.0,
        "aftershave",
        "A warm, spicy cologne with pepper and amber for evenings out.",
        (
            _a("fragrance_family", "Fragrance family", "Spicy"),
            _a("concentration", "Concentration", "Eau de Cologne"),
        ),
        _s((50, 18.0), (100, 28.0)),
        "net_volume_ml",
        (("cap", "stopper"),),
        colors=(PACK_SAND,),
    ),
)

TALCS = (
    _row(
        "TLCLAV",
        "Lavender Body Talc",
        "Sorrel & Salt",
        (D, "Bath & Body", "Talc"),
        "Talc",
        4.0,
        "talc",
        "A silky talc that leaves skin soft and dry, with a calming lavender scent.",
        (_a("fragrance", "Fragrance", "Lavender"),),
        _s((100, 4.0), (200, 6.5)),
        "net_weight_g",
        (("lid", "shaker"),),
        colors=(PACK_SKY,),
    ),
    _row(
        "TLCPWD",
        "Rose Dusting Powder with Puff",
        "Fenmere",
        (D, "Bath & Body", "Talc"),
        "Talc",
        9.0,
        "talc",
        "A luxurious dusting powder in a tin with a soft puff, scented with garden rose.",
        (_a("fragrance", "Fragrance", "Rose"),),
        _s((100, 9.0), (150, 12.0)),
        "net_weight_g",
        (("lid", "puff"),),
        colors=(PACK_ROSE,),
    ),
    _row(
        "TLCUNS",
        "Fragrance Free Body Talc",
        "Aldermist",
        (D, "Bath & Body", "Talc"),
        "Talc",
        4.5,
        "talc",
        "A gentle, plain talc for sensitive skin.",
        (_a("fragrance", "Fragrance", "Unscented"),),
        _s((100, 4.5), (200, 7.0)),
        "net_weight_g",
        (("lid", "shaker"),),
        colors=(PACK,),
    ),
)

_FSC, _BSC = (D, "Suncare", "Face Sun Cream"), (D, "Suncare", "Body Sun Cream")
SUN_CREAMS = (
    _row(
        "SPFLGT",
        "Light Daily Face Sun Cream",
        "Aldermist",
        _FSC,
        "Sun Cream",
        12.0,
        "sun_cream",
        "A fluid daily sun cream for the face that sits well under make-up.",
        (_a("area", "Area", "Face"),),
        _s((50, 12.0), (100, 19.0)),
        "net_volume_ml",
        (("form", "tube"),),
        colors=(PACK_SAND,),
        option=("spf", ("30", "50")),
    ),
    _row(
        "SPFBDY",
        "Family Body Sun Cream",
        "Fenmere",
        _BSC,
        "Sun Cream",
        9.0,
        "sun_cream",
        "A water-resistant sun cream for the body in a family size.",
        (_a("area", "Area", "Body"),),
        _s((200, 9.0), (400, 15.0)),
        "net_volume_ml",
        (("form", "tube"),),
        colors=(PACK_SKY,),
        option=("spf", ("30", "50")),
    ),
    _row(
        "SPFSPR",
        "Quick Dry Body Sun Spray Cream",
        "Sorrel & Salt",
        _BSC,
        "Sun Cream",
        11.0,
        "sun_cream",
        "A spray-on sun cream that dries fast and goes on without rubbing in.",
        (_a("area", "Area", "Body"),),
        _s((150, 11.0), (300, 18.0)),
        "net_volume_ml",
        (("form", "spray"),),
        colors=(PACK_ROSE,),
        option=("spf", ("20", "30", "50")),
    ),
    _row(
        "SPFSNS",
        "Sensitive Mineral Face Sun Cream",
        "Thornlea Skin",
        _FSC,
        "Sun Cream",
        14.0,
        "sun_cream",
        "A mineral sun cream for the face, gentle on skin that burns easily.",
        (_a("area", "Area", "Face"),),
        _s((50, 14.0), (100, 22.0)),
        "net_volume_ml",
        (("form", "spray"),),
        colors=(PACK_SAGE,),
        option=("spf", ("30", "50")),
    ),
)

ROWS = (*MASCARAS, *PRIMERS, *SETTING_SPRAYS, *SERUMS, *FACE_MASKS, *EYE_PATCHES, *BODY_MISTS,
        *AFTERSHAVES, *TALCS, *SUN_CREAMS)  # fmt: skip


def _exemplar(ptype: str) -> BeautyRow:
    return next(r for r in ROWS if r.product_type == ptype)


def _decoys(
    ptype: str, code: str, word: str, rows: tuple[tuple[int, str, str, str], ...]
) -> list[Decoy]:
    """Three decoys of ``ptype`` (one per class): (class, title, brand or "", description)."""
    ex = _exemplar(ptype)
    base = {f.name: getattr(ex, f.name) for f in fields(BeautyRow)}
    if ptype == "Mascara":
        base["colors"] = (BLACK,)
    out = []
    for cls, title, brand, desc in rows:
        out.append(Decoy(**{**base, "code": f"{code}{cls}", "title": title,
                            "brand": brand or ex.brand, "description": desc}, cls=cls, word=word))  # fmt: skip
    return out


def _all_decoys() -> tuple[Decoy, ...]:
    spec = [
        (
            "Mascara",
            "MSD",
            "pink",
            (
                (1, "Pink Cap Volume Mascara", "", "A black mascara in a tube with a pink cap."),
                (
                    2,
                    "Pink Valley Volume Mascara",
                    "",
                    "From the Pink Valley range: a black volume mascara.",
                ),
                (3, "Volume Mascara", "Pink Kestrel", "A black volume mascara."),
            ),
        ),
        (
            "Face Primer",
            "PRD",
            "dewy",
            (
                (1, "Dewy Gold Cap Face Primer", "", "A matte primer with a gold cap."),
                (2, "Dewy Meadow Pore Primer", "", "From the Dewy Meadow range: a matte primer."),
                (3, "Pore Blur Face Primer", "Dewy Finch", "A matte primer for oily skin."),
            ),
        ),
        (
            "Setting Spray",
            "SSD",
            "dewy",
            (
                (1, "Dewy Pink Cap Setting Spray", "", "A matte setting spray with a pink cap."),
                (
                    2,
                    "Dewy Orchard Setting Spray",
                    "",
                    "From the Dewy Orchard range: a matte setting spray.",
                ),
                (3, "Matte Setting Spray", "Dewy Finch", "A matte setting spray for oily skin."),
            ),
        ),
        (
            "Serum",
            "SRD",
            "vitamin c",
            (
                (1, "Vitamin C Orange Cap Serum", "", "A retinol serum with an orange cap."),
                (
                    2,
                    "Vitamin C Grove Night Serum",
                    "",
                    "From the Vitamin C Grove range: a retinol night serum.",
                ),
                (3, "Night Serum", "Vitamin C Orchard", "A retinol night serum."),
            ),
        ),
        (
            "Face Mask",
            "FMD",
            "clay",
            (
                (
                    1,
                    "Clay Pot Sheet Face Mask",
                    "",
                    "A sheet mask that comes with a clay pot-style sachet.",
                ),
                (2, "Clay Hill Sheet Face Mask", "", "From the Clay Hill range: a sheet mask."),
                (3, "Sheet Face Mask", "Clay Wren", "A hydrating sheet mask."),
            ),
        ),
        (
            "Eye Patches",
            "EPD",
            "cloth",
            (
                (1, "Cloth Pouch Eye Patches", "", "Hydrogel patches in a cloth pouch."),
                (2, "Cloth Hill Eye Patches", "", "From the Cloth Hill range: hydrogel patches."),
                (3, "Hydrogel Eye Patches", "Cloth Wren", "Cooling hydrogel patches."),
            ),
        ),
        (
            "Body Mist",
            "BMD",
            "vanilla",
            (
                (
                    1,
                    "Vanilla Cap Floral Body Mist",
                    "",
                    "A floral mist in a bottle with a vanilla-coloured cap.",
                ),
                (
                    2,
                    "Vanilla Bay Floral Body Mist",
                    "",
                    "From the Vanilla Bay range: a floral mist.",
                ),
                (3, "Floral Body Mist", "Vanilla Wren", "A light floral mist."),
            ),
        ),
        (
            "Aftershave",
            "ASD",
            "citrus",
            (
                (
                    1,
                    "Citrus Stopper Woody Aftershave",
                    "",
                    "A woody aftershave with a citrus-green stopper.",
                ),
                (
                    2,
                    "Citrus Bay Woody Aftershave",
                    "",
                    "From the Citrus Bay range: a woody aftershave.",
                ),
                (3, "Woody Aftershave", "Citrus Heron", "A woody aftershave splash."),
            ),
        ),
        (
            "Talc",
            "TLD",
            "rose",
            (
                (1, "Rose Puff Lavender Talc", "", "A lavender talc with a rose-pink puff."),
                (2, "Rose Bay Lavender Talc", "", "From the Rose Bay range: a lavender talc."),
                (3, "Lavender Body Talc", "Rose Kestrel", "A lavender body talc."),
            ),
        ),
        (
            "Sun Cream",
            "SPD",
            "body",
            (
                (
                    1,
                    "Body Lotion Cap Face Sun Cream",
                    "",
                    "A face sun cream with a body lotion-style cap.",
                ),
                (2, "Body Glow Face Sun Cream", "", "From the Body Glow range: a face sun cream."),
                (3, "Face Sun Cream", "Body Kestrel", "A daily face sun cream."),
            ),
        ),
    ]
    return tuple(d for ptype, code, word, rows in spec for d in _decoys(ptype, code, word, rows))


DECOYS = _all_decoys()


def docs() -> list[dict]:
    """Every row's catalog document, the decoys included."""
    return [r.doc() for r in (*ROWS, *DECOYS)]

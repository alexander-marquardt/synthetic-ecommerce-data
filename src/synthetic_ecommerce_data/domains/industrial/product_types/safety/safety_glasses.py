"""Safety glasses: spectacles marked to ANSI/ISEA Z87.1, deepened from breadth
(#834, the safety family of #53).

A pair is built from its model line, not from a size table: ANSI/ISEA Z87.1
rates a spectacle's impact protection and marks its lens, and says nothing of
its frame's size, so a type of these is the set of model lines makers stock.

**Model lines.** :data:`MODEL_LINES` are the spectacles of the maker's own
product feed at https://www.pyramex.com/products.json, read 2026-11-04: the
products filed under ``Eyewear > Frameless``, ``Eyewear > Half Frame`` and
``Eyewear > Full Frame``, each variant a body (frame) color, a lens color and
a lens treatment. A row here is one frame style, lens coating and frame color
with the lens colors a model is sold in at that coating; the models and item
numbers behind it are beside it, and two models that are sold in the same
combination share a row. The feed's anti-fog treatments (``H2X``, ``H2MAX``,
``Standard``) are published by their generic name, ``Anti-Fog``, and its
``No Anti-fog`` as ``No Anti-Fog``. A frameless pair publishes no ``Frame
Color``: it has no frame, and the body color the feed gives some frameless
models is their temples'.

**Dropped.** The feed's sealed, reader, over-the-glasses and goggle products
(other kinds of eyewear), its EU, retail-packed and assorted-temple duplicates,
its polarized variants (a polarizing filter, not a coating), its interchangeable
lens kit, its wire-mesh spectacles (no lens), the products whose variants name
no lens treatment (the anti-fog of their lens is unstated), and every lens color
but the six :data:`LENS_COLORS`, the tints sold across most models; the others
are trade-named tints of one or two models each.

**Standard.** Every line claims ANSI/ISEA Z87.1: a spectacle sold as eye
protection to a US workplace meets it (OSHA 29 CFR 1910.133(b)), and the feed's
descriptions state Z87.1 where they state a standard.

**Names.** ``Style`` is the frame style and ``Coating`` the lens coating, both
census names. The census has no name for a lens's tint or a frame's color (its
``Color`` is one color per part), and a pair has both, so the breadth row's
``Color`` is split into ``Lens Color`` and ``Frame Color``, the feed's
``Lens Color`` and ``Body Color``: ``names.NAME_EXCEPTIONS`` entries.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, NamedTuple

from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.model import keyword_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft

KEY = "safety_glasses"
ITEM = "Safety Glasses"
STANDARD = "ANSI/ISEA Z87.1"
FEED = "https://www.pyramex.com/products.json"

CLEAR = "Clear"
GRAY = "Gray"
AMBER = "Amber"
IO = "Indoor/Outdoor Mirror"
SILVER = "Silver Mirror"
BLUE = "Blue Mirror"
#: The lens colors published, in the order a line's run of them is taken.
LENS_COLORS = (CLEAR, GRAY, AMBER, IO, SILVER, BLUE)


class ModelLine(NamedTuple):
    """One spectacle model at one coating and frame color: what every lens of it shares."""

    style: str
    coating: str
    #: ``None`` for a frameless pair, which has no frame.
    frame_color: str | None
    #: The lens colors it is sold in, in :data:`LENS_COLORS` order.
    tints: tuple[str, ...]


#: The feed's spectacles, one row per distinct combination, by model name.
MODEL_LINES: tuple[ModelLine, ...] = (
    # Alair S3210S S3220S S3280S S3270S S3275S
    ModelLine("Frameless", "No Anti-Fog", None, (CLEAR, GRAY, IO, SILVER, BLUE)),
    # Alair S3210ST; Cortez SB3610ST; Mini Ztek S2510SNT
    ModelLine("Frameless", "Anti-Fog", None, (CLEAR,)),
    # Atoka S9110S S9120S S9180S; Cortez SB3610S SB3620S SB3680S; Endeavor Plus SBG9610S SBG9620S
    # SBG9680S; Neshoba S9710S S9720S S9780S
    ModelLine("Frameless", "No Anti-Fog", None, (CLEAR, GRAY, IO)),
    # Atoka S9110ST S9120ST S9180ST; Intruder S4110ST S4120ST S4180ST; Intruder Foam Padded
    # S4110STFP S4120STFP S4180STFP; Provoq S7210ST S7220ST S7280ST; TruLock SB9510ST SB9520ST
    # SB9580ST
    ModelLine("Frameless", "Anti-Fog", None, (CLEAR, GRAY, IO)),
    # Drone 2.0 VGSB1720T
    ModelLine("Half-Frame", "Anti-Fog", "Black", (GRAY,)),
    # Drone 2.0 VGSG1720T
    ModelLine("Half-Frame", "Anti-Fog", "OD Green", (GRAY,)),
    # Endeavor Plus SBG9610ST SBG9620ST; Endeavor Plus Foam Padded SBG9610STMFP SBG9620STMFP; Itek
    # S5810ST S5820ST; Legacy S10910STM S10920STM; Neshoba S9710ST S9720ST; PMXSLIM SB7110ST
    # SB7120ST; Ztek S2510ST S2520ST
    ModelLine("Frameless", "Anti-Fog", None, (CLEAR, GRAY)),
    # Ever-Lite SB8610D SB8620D SB8630D SB8680D; Rendezvous SB2810S SB2820S SB2830S SB2880S
    ModelLine("Half-Frame", "No Anti-Fog", "Black", (CLEAR, GRAY, AMBER, IO)),
    # Ever-Lite SB8610DT SB8620DT SB8680DT; Venture II SB1810ST SB1820ST SB1880ST
    ModelLine("Half-Frame", "Anti-Fog", "Black", (CLEAR, GRAY, IO)),
    # Ever-Lite SBL8610DTM SBL8620DTM
    ModelLine("Half-Frame", "Anti-Fog", "Black/Lime", (CLEAR, GRAY)),
    # Exeter SB5110DT SB5120DT SB5175DT
    ModelLine("Full-Frame", "Anti-Fog", "Black", (CLEAR, GRAY, BLUE)),
    # Goliath SB5610D SB5620D SB5680D SB5670D
    ModelLine("Full-Frame", "No Anti-Fog", "Black", (CLEAR, GRAY, IO, SILVER)),
    # Goliath SB5610DT SB5620DT
    ModelLine("Full-Frame", "Anti-Fog", "Black", (CLEAR, GRAY)),
    # Howitzer VGSB1310T
    ModelLine("Full-Frame", "Anti-Fog", "Black", (CLEAR,)),
    # Howitzer VGST1310T
    ModelLine("Full-Frame", "Anti-Fog", "Tan", (CLEAR,)),
    # Integra SB410S SB420S
    ModelLine("Half-Frame", "No Anti-Fog", "Black", (CLEAR, GRAY)),
    # Integra SN410S
    ModelLine("Half-Frame", "No Anti-Fog", "Blue", (CLEAR,)),
    # Integra SR410S
    ModelLine("Half-Frame", "No Anti-Fog", "Red", (CLEAR,)),
    # Integra SNWR410S
    ModelLine("Half-Frame", "No Anti-Fog", "Red/White/Blue", (CLEAR,)),
    # Integra SB410ST
    ModelLine("Half-Frame", "Anti-Fog", "Black", (CLEAR,)),
    # Intruder S4110S S4120S S4130S S4180S S4170S S4175S; Itek S5810S S5820S S5830S S5880S S5870S
    # S5875S; Provoq S7210S S7220S S7230S S7280S S7270S S7275S; Ztek S2510S S2520S S2530S S2580S
    # S2570S S2575S
    ModelLine("Frameless", "No Anti-Fog", None, (CLEAR, GRAY, AMBER, IO, SILVER, BLUE)),
    # Legacy S10910S S10920S; Mini Intruder S4110SN S4120SN
    ModelLine("Frameless", "No Anti-Fog", None, (CLEAR, GRAY)),
    # Mini Ztek S2510SN S2520SN S2530SN S2580SN S2575SN
    ModelLine("Frameless", "No Anti-Fog", None, (CLEAR, GRAY, AMBER, IO, BLUE)),
    # Monteagle VGSGMV1620T
    ModelLine("Half-Frame", "Anti-Fog", "Gun Metal/Hi-Vis Yellow", (GRAY,)),
    # Onix SGR4910ST
    ModelLine("Half-Frame", "Anti-Fog", "Black/Hi-Vis Green", (CLEAR,)),
    # PMXSLIM SB7110S; TruLock SB9510S
    ModelLine("Frameless", "No Anti-Fog", None, (CLEAR,)),
    # PMXSPEC SB11210STM SB11220STM
    ModelLine("Half-Frame", "Anti-Fog", "Matte Black", (CLEAR, GRAY)),
    # PMXSPEC SB11265ST
    ModelLine("Half-Frame", "Anti-Fog", "Matte Black/Blue", (BLUE,)),
    # PMXTREME SB6310SP SB6320SP SB6330SP SB6380SP SB6370SP SB6375SP; Venture II SB1810S SB1820S
    # SB1830S SB1880S SB1870S SB1875S
    ModelLine("Half-Frame", "No Anti-Fog", "Black", (CLEAR, GRAY, AMBER, IO, SILVER, BLUE)),
    # PMXTREME SR6320SP
    ModelLine("Half-Frame", "No Anti-Fog", "Red", (GRAY,)),
    # PMXTREME SS6310SP
    ModelLine("Half-Frame", "No Anti-Fog", "Silver", (CLEAR,)),
    # PMXTREME SB6310STP SB6320STP; Rendezvous SB2810ST SB2820ST; Sustainable Ever-Lite
    # ESB8610DTMBCB ESB8620DTMBCB; Venture 3 SB5710DT SB5720DT
    ModelLine("Half-Frame", "Anti-Fog", "Black", (CLEAR, GRAY)),
    # PMXTREME SCM6320STP
    ModelLine("Half-Frame", "Anti-Fog", "Camo", (GRAY,)),
    # Rendezvous SCG2810ST
    ModelLine("Half-Frame", "Anti-Fog", "Crystal Gray", (CLEAR,)),
    # Sitecore SBG10110D SBG10120D SBG10130D SBG10180D
    ModelLine("Half-Frame", "No Anti-Fog", "Black/Gray", (CLEAR, GRAY, AMBER, IO)),
    # Sitecore SGL10110D SGL10120D SGL10180D
    ModelLine("Half-Frame", "No Anti-Fog", "Gray/Lime", (CLEAR, GRAY, IO)),
    # Sitecore SBG10110DTM SBG10120DTM
    ModelLine("Half-Frame", "Anti-Fog", "Black/Gray", (CLEAR, GRAY)),
    # Sitecore SGL10110DTM SGL10120DTM
    ModelLine("Half-Frame", "Anti-Fog", "Gray/Lime", (CLEAR, GRAY)),
    # Tensaw VGSB310T
    ModelLine("Half-Frame", "Anti-Fog", "Black/Gray", (CLEAR,)),
    # TruFlex SBG11310DT SBG11320DT SBG11380DT
    ModelLine("Half-Frame", "Anti-Fog", "Black/Gray", (CLEAR, GRAY, IO)),
    # TruFlex SGL11310DT SGL11320DT SGL11380DT
    ModelLine("Half-Frame", "Anti-Fog", "Gray/Lime", (CLEAR, GRAY, IO)),
    # Venture 3 SB5710D SB5720D SB5730D SB5780D SB5770D
    ModelLine("Half-Frame", "No Anti-Fog", "Black", (CLEAR, GRAY, AMBER, IO, SILVER)),
    # Venture II SMB1810S SMB1820S SMB1880S
    ModelLine("Half-Frame", "No Anti-Fog", "Metallic Blue", (CLEAR, GRAY, IO)),
    # Venture II SSG1810S
    ModelLine("Half-Frame", "No Anti-Fog", "Slate Gray", (CLEAR,)),
)

PROVENANCE = f"model lines read from {FEED} (2026-11-04)"

VOCAB = (
    AttrSpec("Style", "line"),
    AttrSpec("Coating", "line"),
    AttrSpec("Frame Color", "line"),
    AttrSpec("Lens Color", "sku"),
)


def build(gen: Any, type_key: str, category: tuple[str, ...]) -> LineDraft:
    """One line: a brand's pair of one model line, in a run of that line's lens colors."""
    # Imported here: generate imports the type tables, which discover this module.
    from synthetic_ecommerce_data.core.brands import pick_brand
    from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

    rng = gen.rng
    brand = pick_brand(rng, type_key, gen._exhausted)
    model = MODEL_LINES[gen._rotate("model", len(MODEL_LINES))]
    draft = LineDraft(
        item=ITEM,
        brand=brand,
        series=f"SG{rng.randint(100, 999)}",
        category=category,
        provenance=PROVENANCE,
    )
    draft.line_attrs = [
        keyword_attribute("Style", model.style),
        keyword_attribute("Coating", model.coating),
    ]
    if model.frame_color:
        draft.line_attrs.append(keyword_attribute("Frame Color", model.frame_color))
    draft.descriptors = [("Style", model.style)]
    count = max(1, min(gen._variant_count(), len(model.tints)))
    start = gen._rotate(f"tint:{len(model.tints)}:{count}", len(model.tints) - count + 1)
    for tint in model.tints[start : start + count]:
        child = ChildDraft()
        child.primary = keyword_attribute("Lens Color", tint)
        child.attrs = [child.primary]
        draft.children.append(child)
    return draft


#: Nominal proportions of the drawn pair, in inches, for what no source gives:
#: a frame's front 5.9" across, a lens 1.9" high, the bridge between the lenses
#: 0.7" wide, a rim or brow bar 0.12" thick.
FRONT = 5.9
LENS = 1.9
BRIDGE = 0.7
RIM = 0.12
#: How far the lens's lower edge sweeps up toward the nose, of the lens's height.
SWEEP = 0.3
STYLES = ("Frameless", "Half-Frame", "Full-Frame")
#: Each lens color's fill: the lens is drawn in its tint, so two lenses of one
#: model draw apart. Nominal sRGB colors, no source.
LENS_FILL = {
    CLEAR: "#e4eef1",
    GRAY: "#6d7175",
    AMBER: "#e0a33a",
    IO: "#b7c0c5",
    SILVER: "#d2d5d7",
    BLUE: "#4e7db5",
}


def _lens(x_out: float, x_in: float, top: float, bottom: float) -> list[tuple[float, float]]:
    """One lens seen from the front: square at the temple, its lower edge swept up to the nose."""
    lift = SWEEP * (bottom - top)
    return [(x_out, top), (x_in, top), (x_in, bottom - lift), (x_out, bottom)]


def figure(record: dict[str, str]) -> Drawn:
    """The pair seen from the front: a one-piece shield (frameless), two lenses
    under a brow bar (half-frame) or two lenses in rims (full-frame), the
    lenses in their tint."""
    style = record.get("Style", "")
    tint = LENS_FILL.get(record.get("Lens Color", ""))
    source = "record" if tint else "partial"
    if style not in STYLES:
        source = "nominal"
    half, gap = FRONT / 2, BRIDGE / 2
    # The page's y runs down: the brow is y = 0 and the lenses hang below it.
    fig = Figure(size_in=FRONT)
    if style == "Frameless":
        lift = SWEEP * LENS
        fig.poly(
            [
                (-half, 0.0),
                (half, 0.0),
                (half, LENS),
                (gap, LENS - lift),
                (0.0, LENS - 1.6 * lift),
                (-gap, LENS - lift),
                (-half, LENS),
            ],
            "lens",
            tint,
        )
        return Drawn(fig, source)
    for sign in (-1.0, 1.0):
        if style == "Full-Frame":
            fig.poly(_lens(sign * half, sign * gap, 0.0, LENS))
            inner = _lens(sign * (half - RIM), sign * (gap + RIM), RIM, LENS - RIM)
        else:
            inner = _lens(sign * (half - RIM), sign * (gap + RIM), RIM, LENS)
        fig.poly(inner, "lens", tint)
    if style != "Full-Frame":
        fig.rect(-half, 0.0, half, RIM)
    fig.rect(-gap, RIM, gap, 2 * RIM)
    return Drawn(fig, source)


def claims(
    facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
) -> tuple[str, ...]:
    """Every line states its ANSI/ISEA Z87.1 marking."""
    return (STANDARD,)


#: The census ending mix of the 74 pairs (``breadth_categories.safety_glasses``),
#: restated as the gloves restate their own: the type was a breadth row, so
#: :data:`...core.price.ENDINGS` does not carry it.
ENDINGS = {
    "other": 0.3784,
    ".00": 0.3378,
    "other .x9": 0.1351,
    "other .x5": 0.1081,
    ".49": 0.027,
    ".98": 0.0135,
}

#: Hand-set to the census's 74 pairs (p10 5.0, p50 8.605, p90 24.26; the census
#: keys no dimension, so a slope of 0.0 on the lens color). The anchor is a
#: standard-tier pair without anti-fog. The anti-fog premium is NOT MEASURED:
#: the census does not record a lens's coating, so it is a declared estimate
#: that keeps an anti-fog lens dearer.
PRICE = PriceModel(
    # @fit-begin
    8.0, 1.0, 0.0, 0.6, 0.0,
    # @fit-end
    endings=ENDINGS,
    option_attribute="Coating",
    option_factors={"No Anti-Fog": 1.0, "Anti-Fog": 1.3},
)  # fmt: skip

SPEC = TypeSpec(
    KEY,
    category=("Safety", "Eye Protection", "Protective Glasses"),
    standards_family="hand_tool",
    vocab=VOCAB,
    figure=figure,
    extent=(6.0, 2.0),
    make=build,
    share=0.015,
    price=PRICE,
    claims=claims,
    may_claim=frozenset({STANDARD}),
    key_attributes=("Lens Color",),
    compat=False,
    use_lines=(
        "For grinding, cutting and shop work where flying particles are a hazard.",
        "Sold as a pair.",
    ),
)

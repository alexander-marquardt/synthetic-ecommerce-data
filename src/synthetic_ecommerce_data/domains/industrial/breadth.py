"""Catalog BREADTH: ~50 new categories, 1-2 SKUs each, from ONE data table.

alexander-marquardt/synthetic-ecommerce-data#34. The maintainer's own
comparison: a real industrial storefront returns 51 items across 9 categories
for ``1/2 ball`` (tooling balls, rubber balls, ball stock, gage balls, ...);
this catalog's twelve original types return 488 across 3 (ball end mills,
ball-end hex keys, radial bearings). Description noise adds hits WITHIN a
type; it cannot add a category. This module does, cheaply:

* **ONE YAML table** (``data/breadth_categories/``, :func:`load_rows`),
  ~50 rows, one file per row so two PRs that add or remove rows never edit
  the same file (#48): a category path, a shape, an item noun, 3-5 line-scoped
  attributes with short value lists, one variant (size) attribute, and a
  one-line reason naming the customer query it joins.
* **ONE generic loop** (:func:`build_line`) turns a row into a
  :class:`~.model.ProductLine` of 1-2 SKUs, reusing the catalog's brand
  machinery (:func:`.brands.pick_brand`), its description grammar
  (:meth:`.generate.Generator._build_description`) and its noise generator
  (:mod:`.noise`) exactly as the twelve original types do. Titles are built
  directly with :func:`.naming.build_title` rather than through the full
  title algorithm (:meth:`.generate.Generator._build_line_title`): a breadth
  title is deliberately the SHORT ``<descriptor> <item>, <size>`` shape
  (maintainer, 2026-09-30: "Stainless Steel Ball, 1/2 in"), not the
  multi-segment census grammar the deep types reproduce.
* No sparsity, no injected defects, no ``Standards`` claim: every declared
  attribute is always published. Cheap means simple, not merely small.

Every row publishes a top-level ``spec_quality: "fast_and_cheap"``
(:attr:`.model.ProductLine.spec_quality`) -- never a nested attribute, so it
is neither searchable text nor a facet on the industrial deployment. Removing
a row from the table, or the whole table, removes every SKU it made and
nothing else: :func:`build_line` reads only the row it is given, and no
other code path constructs a ``fast_and_cheap`` line.

Registration. A breadth row is a full product TYPE to the rest of the
generator -- it needs a category leaf (:data:`.taxonomy.LEAVES`), a drawing
(:data:`.taxonomy.DRAWING`), a brand family (:data:`.vocab.STANDARDS_FAMILY`)
and a vocabulary entry (:data:`.vocab.VOCAB`, so
``tests/test_catalog_vocab.py``'s ``set(VOCAB) == set(taxonomy.LEAVES) ==
set(STANDARDS_FAMILY)`` invariant holds) -- and a fixed-shape SVG figure
(:data:`..drawing.figures.FIGURES`). :func:`register` adds all five, from the
table alone: no per-category code, one generic registration for all ~50 rows.
It runs once, at import.
"""

from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING, Any

from synthetic_ecommerce_data.core import typespec
from synthetic_ecommerce_data.core.breadth import BreadthRow, read_rows, row_from_dict
from synthetic_ecommerce_data.core.model import (
    Attribute,
    ProductLine,
    Sku,
    keyword_attribute,
    length_attribute,
)
from synthetic_ecommerce_data.core.naming import Segment, build_title
from synthetic_ecommerce_data.core.voice import product_name
from synthetic_ecommerce_data.domains.industrial import taxonomy
from synthetic_ecommerce_data.domains.industrial.drawing.breadth_shapes import BREADTH_SHAPES
from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES
from synthetic_ecommerce_data.domains.industrial.vocab import STANDARDS_FAMILY, VOCAB, AttrSpec

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.industrial.generate import Generator

#: Every breadth row publishes this, verbatim, on ``dimension_provenance``:
#: honest about where its numbers came from, and distinct from every deep
#: type's provenance string so a reader is never told a breadth SKU's sizes
#: are read from a standard or generated to fill a conventional series.
PROVENANCE = "breadth filler: a short, plausible size list, not modelled on any standard"

#: "spec_quality" (:attr:`.model.ProductLine.spec_quality`) for every row this
#: module builds.
SPEC_QUALITY = "fast_and_cheap"


#: The directory whose files are the table's rows, one ``<key>.yaml`` each; a
#: row's ``part_number_block:`` lives in its own file.
TABLE = "synthetic_ecommerce_data/domains/industrial/data/breadth_categories"


def row_file(key: str) -> str:
    """The file that holds ``key``'s row."""
    return f"{TABLE}/{key}.yaml"


def fix_site(key: str) -> str:
    """Where a breadth type declares its own block: a key in its row's file."""
    return f"part_number_block: <block> in {row_file(key)}"


def _row_from_dict(raw: dict[str, Any]) -> BreadthRow:
    return row_from_dict(raw, TABLE)


def load_rows() -> tuple[BreadthRow, ...]:
    """Every row file, in file-name order; a file named for another key is refused.

    The name check keeps :func:`row_file` (the path every refusal names) true.
    """
    data = resources.files("synthetic_ecommerce_data.domains.industrial.data")
    return read_rows(data.joinpath("breadth_categories"), TABLE)


#: Loaded once, at import, from the YAML table; a type module's row joins it
#: through :func:`add_row`. Private, and read only through :func:`rows`: a
#: type module's row is added when the type modules register, so a direct
#: read before that would miss it. Once it is emptied (the "easy removal"
#: property ``tests/test_breadth.py`` checks), :func:`register` registers
#: nothing and :func:`.generate.all_type_keys` lists no breadth type: no other
#: code path constructs a breadth line.
_ROWS: tuple[BreadthRow, ...] = load_rows()


def rows() -> tuple[BreadthRow, ...]:
    """Every breadth row, the YAML table's and the type modules', registering first.

    The type modules register here rather than when this module is imported:
    a breadth type module imports this module for :class:`BreadthRow`, so
    registering at import would re-import that type module while it is still
    half-initialised (#54).
    """
    typespec.ensure_registered()
    return _ROWS


def row_for(key: str) -> BreadthRow:
    """The row whose type is ``key``."""
    return next(row for row in rows() if row.key == key)


def register(new_rows: tuple[BreadthRow, ...] | None = None) -> None:
    """Wire ``new_rows`` (the YAML table's, by default) into the shared,
    type-keyed registries every row needs.

    Idempotent (every assignment is keyed by the row's own ``key``, so a
    second call overwrites each entry with itself) and safe to call with an
    empty ``new_rows``, which registers nothing.
    """
    for row in _ROWS if new_rows is None else new_rows:
        taxonomy.LEAVES[row.key] = (row.category,)
        taxonomy.DRAWING[row.key] = row.shape
        STANDARDS_FAMILY[row.key] = row.family
        shape_fn, extent = BREADTH_SHAPES[row.shape]
        FIGURES[row.key] = (shape_fn, extent)
        specs = [AttrSpec(name="Item", scope="line")]
        specs.extend(AttrSpec(name=name, scope="line") for name in row.attributes)
        specs.append(AttrSpec(name=row.size_attr, scope="sku", kind="length"))
        VOCAB[row.key] = tuple(specs)
        if row.part_number_block is not None:
            typespec.DECLARED_BLOCKS[row.key] = row.part_number_block


register()


def add_row(row: BreadthRow) -> None:
    """A row a type module declares (:func:`.typespec.register`), joined to :data:`_ROWS`.

    Once joined it is a breadth row like any other: built by
    :func:`build_line`, listed by :func:`.generate.all_type_keys`, and gone
    with the rest when :data:`_ROWS` is emptied.
    """
    global _ROWS
    if any(existing.key == row.key for existing in _ROWS):
        raise typespec.TypeCollisionError(
            f"breadth type {row.key!r} is declared both in {row_file(row.key)} and in a type module"
        )
    _ROWS = (*_ROWS, row)
    register((row,))


def _build_sku(
    gen: Generator,
    row: BreadthRow,
    item_text: str,
    size_value: str,
    sku: str,
    price: float,
    stock: int,
    draft,
    product_id: str,
) -> Sku:
    """One SKU: its title (built directly, not through the census grammar),
    its description (:meth:`.generate.Generator._build_description`, reused
    exactly as every other type calls it) and its noise (:mod:`.noise`)."""
    from synthetic_ecommerce_data.core import noise
    from synthetic_ecommerce_data.domains.industrial import (
        compat,  # noqa: PLC0415 -- see newtypes.py for why: avoids the cycle
    )

    size_attribute = length_attribute(row.size_attr, size_value)
    title = build_title(item_text, (Segment(value=size_value, attribute=row.size_attr),))
    merged = {a.name: a.value for a in draft.line_attrs}
    merged[row.size_attr] = size_value
    compatibility = compat.sentence_for(row.key, merged) or ""
    noise_text = " ".join(
        noise.sentences(
            row.key,
            merged,
            sku=sku,
            seed=gen.config.seed,
            noise=gen.config.noise,
            provenance=PROVENANCE,
            primary=None,
            siblings=(),
        )
    )
    extra = " ".join(part for part in (compatibility, noise_text) if part)
    description = gen._build_description(draft, title, [size_attribute], extra)  # noqa: SLF001
    return Sku(
        sku=sku,
        title=title.text,
        description=description,
        attributes=(size_attribute,),
        price_usd=price,
        stock=stock,
        image_id=taxonomy.image_id_for(row.key, product_id, sku),
        compatibility=compatibility,
        noise=noise_text,
    )


#: Finishes that are PLATING or COATING processes applied to a base metal --
#: the deep generator's own rule (:data:`.generate.WASHER_FINISHES`,
#: :func:`.newtypes` kit-finish selection) refuses every one of these on a
#: stainless material, because stainless does not need, and is not sold
#: with, a corrosion-preventing plating: the alloy IS the corrosion
#: resistance. A finish absent from this set (``Plain``, ``Bright``,
#: ``Passivated``) is never touched.
_PLATING_FINISHES = frozenset({"Zinc Plated", "Zinc Yellow", "Hot Dip Galvanized"})

#: The finish a plating draw is replaced with on a stainless material, when
#: the row offers it -- the deep generator's own fallback
#: (:mod:`.newtypes`: ``"Plain" if "Stainless" in material else ...``).
_STAINLESS_FALLBACK_FINISH = "Plain"


def _apply_finish_follows_material(chosen: dict[str, str], row: BreadthRow, rng: Any) -> None:
    """Redraw ``chosen["Finish"]`` if it is a plating and the row's material
    is stainless (alexander-marquardt/synthetic-ecommerce-data#37).

    IN PLACE, on the row's own already-drawn ``Material`` -- never a second,
    independent draw, so this cannot disagree with the material the SKU
    actually publishes. A row with no ``Finish`` attribute, or whose
    ``Material`` is not stainless, or whose drawn finish already isn't a
    plating, is untouched. ``featured_attrs`` may still fix a plating finish
    deliberately (checked first: a row's own authored pairing is a choice,
    not a draw this function corrects).
    """
    material = chosen.get("Material", "")
    finish = chosen.get("Finish")
    if finish is None or "Stainless" not in material:
        return
    if finish not in _PLATING_FINISHES:
        return
    if row.featured_attrs.get("Finish") == finish:
        return
    options = row.attributes.get("Finish", ())
    non_plating = [v for v in options if v not in _PLATING_FINISHES]
    if _STAINLESS_FALLBACK_FINISH in non_plating:
        chosen["Finish"] = _STAINLESS_FALLBACK_FINISH
    elif non_plating:
        chosen["Finish"] = rng.choice(non_plating)
    # else: every option is a plating (a row misconfigured for a stainless
    # material) -- left as drawn rather than silently invented; the
    # catalog-vocab test below catches a row that reaches this branch.


def sku_count(row: BreadthRow) -> int:
    """How many SKUs ``row`` builds: its ``skus``, capped by the sizes it offers."""
    return max(1, min(row.skus, len(row.size_values)))


def build_line(gen: Generator, row: BreadthRow, index: int) -> ProductLine:
    """One breadth product line: 1-2 SKUs, from ``row`` alone.

    ``gen`` is the row's OWN type generator (:class:`.generate.Generator`),
    seeded from the seed and ``row.key`` -- adding, removing or reordering a
    row moves no other row's draws, the guarantee every type has
    (:mod:`.typespec`).
    """
    from synthetic_ecommerce_data.core import brands  # noqa: PLC0415
    from synthetic_ecommerce_data.core import price as prices  # noqa: PLC0415
    from synthetic_ecommerce_data.domains.industrial.generate import LineDraft  # noqa: PLC0415

    rng = gen.rng
    brand = brands.pick_brand(rng, row.key)

    chosen: dict[str, str] = {}
    for name, values in row.attributes.items():
        chosen[name] = row.featured_attrs.get(name) or rng.choice(values)
    _apply_finish_follows_material(chosen, row, rng)

    line_attrs: list[Attribute] = [keyword_attribute("Item", row.item)]
    descriptor_value: str | None = None
    for name, value in chosen.items():
        line_attrs.append(keyword_attribute(name, value))
        if name == row.descriptor_attr:
            descriptor_value = value
    item_text = f"{descriptor_value} {row.item}" if descriptor_value else row.item

    count = sku_count(row)
    # Featured sizes fill the row's SKU slots first, so a size ``reason``
    # cites is never left out to a rotation that starts at index 0 every
    # time (#35 review -- every row is built exactly once, so the rotation
    # never gets a second pass to reach a later value). Any slots left over
    # still rotate over the remaining, non-featured values, unchanged for a
    # row with no featured sizes.
    featured_sizes = [value for value in row.featured_sizes if value in row.size_values][:count]
    remaining_pool = [value for value in row.size_values if value not in featured_sizes]
    extra_needed = count - len(featured_sizes)
    extra: list[str] = []
    if extra_needed > 0 and remaining_pool:
        window = len(remaining_pool) - min(extra_needed, len(remaining_pool)) + 1
        start = gen._rotate(f"breadth:{row.key}:size", window)  # noqa: SLF001
        extra = remaining_pool[start : start + extra_needed]
    sizes = featured_sizes + extra

    series = f"BR{rng.randint(100, 999)}"
    draft = LineDraft(
        item=item_text,
        brand=brand,
        series=series,
        category=row.category,
        line_attrs=line_attrs,
        provenance=PROVENANCE,
        descriptors=[(name, value) for name, value in chosen.items()],
    )
    draft.type_key = row.key
    gen._line_facts = {a.name: a.value for a in line_attrs}  # noqa: SLF001
    product_id = gen._product_id(brand, series, index)  # noqa: SLF001

    children: list[Sku] = []
    for size_value in sizes:
        sku = gen._new_sku()  # noqa: SLF001
        # One draw, where the uniform this replaced drew one (see :mod:`.price`).
        price = prices.breadth_price(
            row,
            size_value,
            brands.BY_NAME[brand].tier,
            rng.random(),
            prices.ending_draw(gen.config.seed, sku),
        )
        stock_pool = (0, rng.randint(1, 40), rng.randint(40, 900))
        stock = rng.choices(stock_pool, weights=(0.08, 0.42, 0.5))[0]
        children.append(
            _build_sku(gen, row, item_text, size_value, sku, price, stock, draft, product_id)
        )
        gen._bump("skus")  # noqa: SLF001
        gen._bump("breadth_skus")  # noqa: SLF001

    parent_title = product_name(brand, series, item_text, row.family)
    gen._bump("lines")  # noqa: SLF001
    gen._bump("breadth_lines")  # noqa: SLF001
    return ProductLine(
        product_id=product_id,
        type_key=row.key,
        title=parent_title,
        brand=brand,
        series=series,
        category=row.category,
        attributes=tuple(line_attrs),
        children=tuple(children),
        dimension_provenance=PROVENANCE,
        spec_quality=SPEC_QUALITY,
        image_id=children[0].image_id,
        drawing=taxonomy.drawing_for(row.key),
    )

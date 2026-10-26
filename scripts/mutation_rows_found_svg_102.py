"""Mutation rows for the found-SVG normaliser, loader and the C-clamp row (#102).

Each row plants one plausible defect and names the test that must go red.
``mutation_check.py --only "found svg:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "found svg"
T = "tests/test_found_svg_102.py -k"
SCRIPT = "normalise_found_svg.py"
SHAPES = "domains/industrial/drawing/found_shapes.py"
YAML = "domains/industrial/data/breadth_categories/c_clamps.yaml"


def _script(name: str, old: str, new: str, selector: str, prop: str) -> Row:
    return Row(f"{PREFIX}: {name}", SCRIPT, old, new, f'{T} "{selector}"', prop, root="scripts")


def _shapes(name: str, old: str, new: str, selector: str, prop: str, file: str = SHAPES) -> Row:
    return Row(f"{PREFIX}: {name}", file, old, new, f'{T} "{selector}"', prop)


def rows() -> list[Row]:
    return [
        _script(
            "an arc is read as a straight command",
            'if low == "a":',
            'if low == "~":',
            "arc_command_is_refused",
            "a found file with an arc is refused, not flattened wrongly",
        ),
        _script(
            "an ancestor transform is not applied",
            '        matrix = _multiply(matrix, _transform(node.get("transform")))\n',
            "",
            "every_transform_level",
            "every transform on the way to the selection reaches the points",
        ),
        _script(
            "a transform on the path itself is not applied",
            '        inner = _multiply(matrix, _transform(child.get("transform")))',
            "        inner = matrix",
            "every_transform_level",
            "a path's own transform reaches its points",
        ),
        _script(
            "transforms compose in the wrong order",
            "        matrix = _multiply(matrix, step)",
            "        matrix = _multiply(step, matrix)",
            "every_transform_level",
            "'rotate scale' applies the scale first",
        ),
        _script(
            "a curve is one segment",
            "CURVE_STEPS = 8",
            "CURVE_STEPS = 1",
            "flattens_a_curve",
            "a curve is flattened to several segments",
        ),
        _script(
            "a relative move after close starts from the last point",
            "current, pos = [start], start",
            "current, pos = [start], pos",
            "relative_move_after_close",
            "a relative m after z starts from the subpath's start",
        ),
        _script(
            "a horizontal line is relative whatever its case",
            "pos = (ox + a[0] if rel else a[0], pos[1])",
            "pos = (pos[0] + a[0], pos[1])",
            "absolute_h_and_v_start",
            "H is absolute and h relative",
        ),
        _script(
            "a vertical line is relative whatever its case",
            "pos = (pos[0], oy + a[0] if rel else a[0])",
            "pos = (pos[0], pos[1] + a[0])",
            "absolute_h_and_v_start",
            "V is absolute and v relative",
        ),
        _script(
            "a repeated closing point stays",
            "points[:-1] if points[0] == points[-1] else points",
            "points",
            "repeated_closing_point",
            "a path that returns to its start does not repeat the point",
        ),
        _script(
            "a two-point subpath is kept",
            "if len(set(points)) >= 3",
            "if len(set(points)) >= 1",
            "degenerate_subpath",
            "a subpath with fewer than three points is no polygon",
        ),
        _script(
            "an unmapped fill is painted anyway",
            "if fill not in roles:",
            "if False:",
            "unmapped_fill_is_refused",
            "a fill with no role is refused, never defaulted",
        ),
        _script(
            "an unknown element is skipped",
            '            raise ValueError(f"unsupported element <{tag}> in the selection")',
            "            continue",
            "not_a_group_or_path",
            "an element the normaliser does not read is refused",
        ),
        _script(
            "a DOCTYPE is parsed",
            'if "<!DOCTYPE" in svg_text or "<!ENTITY" in svg_text:',
            "if False:",
            "doctype_is_refused",
            "a downloaded file with a DOCTYPE is refused",
        ),
        _script(
            "the outermost fill wins",
            "for element in (path, *reversed(ancestors)):",
            "for element in (path, *ancestors):",
            "fill_is_inherited",
            "a path takes the fill of its nearest group",
        ),
        _script(
            "the longer side is not scaled to one thousand",
            "k = SIZE / max(width, height)",
            "k = SIZE / min(width, height)",
            "scales_to_one_thousand",
            "the longer side is SIZE units",
        ),
        _script(
            "numbers keep two decimals",
            "DECIMALS = 1",
            "DECIMALS = 2",
            "one_decimal_at_most",
            "the written numbers have one decimal",
        ),
        _shapes(
            "a path with an unknown role is loaded",
            "if role not in ROLES:",
            "if False:",
            "role_outside_the_vocabulary",
            "a found file may only hold the role vocabulary",
        ),
        _shapes(
            "the shape is scaled by its shorter side",
            "    k = longest_in / max(width, height)\n    fig = Figure",
            "    k = longest_in / min(width, height)\n    fig = Figure",
            "many_parts_scaled_to_its_extent",
            "the found shape's longer side is the extent",
        ),
        _shapes(
            "the extent is scaled by its shorter side",
            "    k = longest_in / max(width, height)\n    return width * k",
            "    k = longest_in / min(width, height)\n    return width * k",
            "loader_scales_the_longer_side",
            "extent() agrees with load()",
        ),
        _shapes(
            "the c_clamps row draws the bracket again",
            "shape: c_clamp",
            "shape: bracket",
            "row_draws_the_found_clamp",
            "the C-clamps category draws the found clamp",
            file=YAML,
        ),
    ]

#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
UPM = 1000
CAP_HEIGHT = 700
ASCENDER = 895
DESCENDER = -20
LINE_GAP = 0
SIDE_BEARING = 45
SPACE_WIDTH = 300
MARK_HEIGHT = 150
ALLOWED_PATH_COMMANDS = set("MmLlCcZz")
CAPITALS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PREVIEW_LINES = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz",
    "ABIADE",
    "Abiade",
    "ABÍÁDÉ",
    "Á É Í AÁ EÉ IÍ",
    "ABI ADE ABIADE",
    "AV AW AY AT VA WA YA TA",
    "FA PA RA LT LY LV",
    "AIA IAI BIB DED",
    "D O P Q R A B",
]
REQUIRED_TABLES = {"cmap", "glyf", "hmtx", "head", "hhea", "maxp", "name", "OS/2", "post", "GPOS"}
REQUIRED_BRAND_PAIRS = {"AB", "BI", "IA", "AD", "DE"}


@dataclass(frozen=True)
class SvgShape:
    source: str
    view_box: tuple[float, float, float, float]
    path_data: str
    fill_rule: str


class ContourPen:
    def __init__(self, transform):
        self.transform = transform
        self.contours: list[RecordingPen] = []
        self.current: RecordingPen | None = None

    def moveTo(self, point):
        if self.current is not None:
            self.endPath()
        self.current = RecordingPen()
        self.current.moveTo(self.transform(point))

    def lineTo(self, point):
        self._current().lineTo(self.transform(point))

    def curveTo(self, *points):
        self._current().curveTo(*(self.transform(point) for point in points))

    def qCurveTo(self, *points):
        self._current().qCurveTo(*(self.transform(point) for point in points))

    def closePath(self):
        current = self._current()
        current.closePath()
        self.contours.append(current)
        self.current = None

    def endPath(self):
        current = self._current()
        current.endPath()
        self.contours.append(current)
        self.current = None

    def _current(self) -> RecordingPen:
        if self.current is None:
            raise ValueError("SVG path emitted drawing commands before moveTo")
        return self.current


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def read_shape(relative_path: str) -> SvgShape:
    source_path = ROOT / relative_path
    if not source_path.exists():
        raise FileNotFoundError(f"Missing SVG source: {relative_path}")

    root = ET.parse(source_path).getroot()
    tag = root.tag.rsplit("}", 1)[-1]
    if tag != "svg":
        raise ValueError(f"{relative_path} is not an SVG root")

    view_box_text = root.attrib.get("viewBox")
    if not view_box_text:
        raise ValueError(f"{relative_path} has no viewBox")
    view_box_values = tuple(float(part) for part in view_box_text.replace(",", " ").split())
    if len(view_box_values) != 4:
        raise ValueError(f"{relative_path} has invalid viewBox: {view_box_text}")

    unsupported_root_attrs = {"transform", "mask", "clip-path", "style"} & set(root.attrib)
    if unsupported_root_attrs:
        raise ValueError(f"{relative_path} uses unsupported root attributes: {sorted(unsupported_root_attrs)}")

    children = [child for child in root if child.tag.rsplit("}", 1)[-1] != "defs"]
    paths = [child for child in children if child.tag.rsplit("}", 1)[-1] == "path"]
    if len(paths) != 1 or len(children) != 1:
        child_tags = [child.tag.rsplit("}", 1)[-1] for child in children]
        raise ValueError(f"{relative_path} must contain exactly one path; found {child_tags}")

    path = paths[0]
    unsupported_path_attrs = {"transform", "mask", "clip-path", "style"} & set(path.attrib)
    if unsupported_path_attrs:
        raise ValueError(f"{relative_path} uses unsupported path attributes: {sorted(unsupported_path_attrs)}")

    path_data = path.attrib.get("d")
    if not path_data:
        raise ValueError(f"{relative_path} path has no d attribute")

    commands = set(re.findall(r"[A-Za-z]", path_data))
    unsupported_commands = commands - ALLOWED_PATH_COMMANDS
    if unsupported_commands:
        raise ValueError(f"{relative_path} uses unsupported path commands: {sorted(unsupported_commands)}")

    if path.attrib.get("fill") in {None, "none"}:
        raise ValueError(f"{relative_path} path must carry a visible fill")

    return SvgShape(
        source=relative_path,
        view_box=view_box_values,  # type: ignore[arg-type]
        path_data=path_data,
        fill_rule=path.attrib.get("fill-rule", "nonzero"),
    )


def glyph_transform(shape: SvgShape, scale: float, left_bearing: int):
    view_x, view_y, _, view_height = shape.view_box

    def transform(point):
        x, y = point
        return (
            round((x - view_x) * scale + left_bearing),
            round(CAP_HEIGHT - (y - view_y) * scale),
        )

    return transform


def mark_transform(shape: SvgShape, anchor: dict[str, int]):
    view_x, view_y, view_width, view_height = shape.view_box
    scale = MARK_HEIGHT / view_height
    center_x = view_x + view_width / 2
    bottom_y = view_y + view_height

    def transform(point):
        x, y = point
        return (
            round(anchor["x"] + (x - center_x) * scale),
            round(anchor["y"] + (bottom_y - y) * scale),
        )

    return transform


def parse_contours(shape: SvgShape, transform) -> list[RecordingPen]:
    pen = ContourPen(transform)
    parse_path(shape.path_data, pen)
    if pen.current is not None:
        pen.endPath()
    if not pen.contours:
        raise ValueError(f"{shape.source} produced no contours")
    return pen.contours


def cubic_at(p0, p1, p2, p3, t: float):
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
    )


def quadratic_at(p0, p1, p2, t: float):
    u = 1 - t
    return (
        u**2 * p0[0] + 2 * u * t * p1[0] + t**2 * p2[0],
        u**2 * p0[1] + 2 * u * t * p1[1] + t**2 * p2[1],
    )


def contour_polyline(contour: RecordingPen) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    current: tuple[float, float] | None = None
    start: tuple[float, float] | None = None

    for operator, operands in contour.value:
        if operator == "moveTo":
            current = operands[0]
            start = current
            points.append(current)
        elif operator == "lineTo":
            current = operands[0]
            points.append(current)
        elif operator == "curveTo":
            if current is None:
                raise ValueError("curveTo before moveTo")
            p1, p2, p3 = operands
            for step in range(1, 13):
                points.append(cubic_at(current, p1, p2, p3, step / 12))
            current = p3
        elif operator == "qCurveTo":
            if current is None:
                raise ValueError("qCurveTo before moveTo")
            if len(operands) != 2:
                raise ValueError("Only simple quadratic SVG curves are supported")
            p1, p2 = operands
            for step in range(1, 13):
                points.append(quadratic_at(current, p1, p2, step / 12))
            current = p2
        elif operator in {"closePath", "endPath"}:
            if start is not None:
                points.append(start)
    return points


def signed_area(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0
    return sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])
    ) / 2


def point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    previous_x, previous_y = polygon[-1]
    for current_x, current_y in polygon:
        crosses = (current_y > y) != (previous_y > y)
        if crosses:
            slope_x = (previous_x - current_x) * (y - current_y) / (previous_y - current_y) + current_x
            if x < slope_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def orient_contours(contours: list[RecordingPen]) -> list[tuple[RecordingPen, bool]]:
    polygons = [contour_polyline(contour) for contour in contours]
    areas = [signed_area(polygon) for polygon in polygons]
    outer_sign = next((1 if area > 0 else -1 for area in areas if area), 1)
    oriented: list[tuple[RecordingPen, bool]] = []

    for index, contour in enumerate(contours):
        polygon = polygons[index]
        if not polygon:
            oriented.append((contour, False))
            continue
        probe = (
            sum(point[0] for point in polygon) / len(polygon),
            sum(point[1] for point in polygon) / len(polygon),
        )
        depth = sum(
            1
            for other_index, other_polygon in enumerate(polygons)
            if other_index != index
            and abs(areas[other_index]) > abs(areas[index])
            and point_in_polygon(probe, other_polygon)
        )
        desired_sign = outer_sign if depth % 2 == 0 else -outer_sign
        current_sign = 1 if areas[index] > 0 else -1
        oriented.append((contour, current_sign != desired_sign))

    return oriented


def make_glyph(contours: list[RecordingPen]):
    pen = TTGlyphPen(None)
    quadratic_pen = Cu2QuPen(pen, max_err=1.0)
    for contour, reverse in orient_contours(contours):
        target = ReverseContourPen(quadratic_pen) if reverse else quadratic_pen
        contour.replay(target)
    return pen.glyph()


def empty_glyph():
    return TTGlyphPen(None).glyph()


def bounds_for(contours: list[RecordingPen]) -> tuple[int, int, int, int] | None:
    if not contours:
        return None
    pen = BoundsPen(None)
    for contour in contours:
        contour.replay(pen)
    if pen.bounds is None:
        return None
    return tuple(round(value) for value in pen.bounds)


def translate_contours(contours: list[RecordingPen], dx: int) -> list[RecordingPen]:
    translated: list[RecordingPen] = []
    for contour in contours:
        pen = RecordingPen()
        for operator, operands in contour.value:
            shifted = []
            for operand in operands:
                if isinstance(operand, tuple) and len(operand) == 2:
                    shifted.append((operand[0] + dx, operand[1]))
                else:
                    shifted.append(operand)
            getattr(pen, operator)(*shifted)
        translated.append(pen)
    return translated


def apply_metric_override(
    contours: list[RecordingPen],
    override: dict[str, int] | None,
    default_advance_width: int,
) -> tuple[list[RecordingPen], int, tuple[int, int, int, int]]:
    bounds = bounds_for(contours)
    if bounds is None:
        raise ValueError("Glyph produced no drawable bounds")
    if override is None:
        return contours, default_advance_width, bounds

    left_side_bearing = int(override["leftSideBearing"])
    right_side_bearing = int(override["rightSideBearing"])
    shifted_contours = translate_contours(contours, left_side_bearing - bounds[0])
    shifted_bounds = bounds_for(shifted_contours)
    if shifted_bounds is None:
        raise ValueError("Glyph metric override removed drawable bounds")
    advance_width = shifted_bounds[2] + right_side_bearing
    return shifted_contours, advance_width, shifted_bounds


def validate_glyph_manifest(manifest: dict[str, Any]) -> None:
    glyphs = manifest.get("glyphs", {})
    aliases = manifest.get("aliases", {})
    metric_overrides = manifest.get("metrics", {})
    missing = [letter for letter in CAPITALS if letter not in glyphs]
    extra = [key for key in glyphs if key not in CAPITALS]
    if missing or extra:
        raise ValueError(f"Glyph manifest must map exactly A-Z; missing={missing}, extra={extra}")
    expected_aliases = {letter.lower(): letter for letter in CAPITALS}
    if aliases != expected_aliases:
        raise ValueError("Glyph aliases must map lowercase a-z to uppercase A-Z")
    unknown_metric_keys = sorted(set(metric_overrides) - set(CAPITALS))
    if unknown_metric_keys:
        raise ValueError(f"Glyph metric overrides reference unknown glyphs: {unknown_metric_keys}")
    for letter, override in metric_overrides.items():
        required_keys = {"leftSideBearing", "rightSideBearing"}
        if set(override) != required_keys:
            raise ValueError(f"Metric override for {letter} must define {sorted(required_keys)}")


def glyph_name_for_char(char: str, aliases: dict[str, str], composites: dict[str, Any]) -> str:
    if char == " ":
        return "space"
    if char in aliases:
        return aliases[char]
    if char in CAPITALS:
        return char
    if char in composites:
        return composites[char]["glyphName"]
    raise ValueError(f"No glyph is available for kerning character {char!r}")


def build_feature_text(kerning: dict[str, int], aliases: dict[str, str], composites: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    lines = ["feature kern {"]
    manifest_pairs: dict[str, Any] = {}
    for pair, value in kerning.items():
        characters = list(pair)
        if len(characters) != 2:
            raise ValueError(f"Kerning pair keys must contain exactly two characters: {pair!r}")
        left = glyph_name_for_char(characters[0], aliases, composites)
        right = glyph_name_for_char(characters[1], aliases, composites)
        lines.append(f"  pos {left} {right} {int(value)};")
        manifest_pairs[pair] = {"left": left, "right": right, "value": int(value)}
    lines.append("} kern;")
    return "\n".join(lines), manifest_pairs


def write_preview_html() -> None:
    lines_html = "\n".join(f"    <div>{escape(line)}</div>" for line in PREVIEW_LINES)
    (DIST / "preview.html").write_text(
        f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Abiade Font Preview</title>
  <style>
    @font-face {{
      font-family: \"Abiade\";
      src: url(\"./Abiade-Regular.woff2\") format(\"woff2\"), url(\"./Abiade-Regular.ttf\") format(\"truetype\");
      font-weight: 400;
      font-style: normal;
      font-display: block;
    }}
    body {{
      margin: 0;
      padding: 40px;
      background: #111;
      color: #f7f1e3;
      font-family: system-ui, sans-serif;
    }}
    h1 {{
      margin: 0 0 24px;
      font-family: system-ui, sans-serif;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .specimen {{
      font-family: \"Abiade\", system-ui, sans-serif;
      font-size: clamp(34px, 7vw, 92px);
      line-height: 1.35;
      letter-spacing: 0;
      font-kerning: normal;
    }}
  </style>
</head>
<body>
  <h1>Abiade Regular Preview</h1>
  <main class=\"specimen\">
{lines_html}
  </main>
</body>
</html>
"""
    )


def kerning_pixels(kerning: dict[str, int], left: str, right: str, font: ImageFont.FreeTypeFont) -> float:
    return kerning.get(left + right, 0) * font.size / UPM


def text_width_with_kerning(text: str, font: ImageFont.FreeTypeFont, kerning: dict[str, int]) -> float:
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    width = sum(draw.textlength(character, font=font) for character in text)
    width += sum(kerning_pixels(kerning, left, right, font) for left, right in zip(text, text[1:]))
    return width


def draw_text_with_kerning(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    kerning: dict[str, int],
) -> None:
    x, y = position
    for index, character in enumerate(text):
        draw.text((x, y), character, fill=fill, font=font)
        x += draw.textlength(character, font=font)
        if index + 1 < len(text):
            x += kerning_pixels(kerning, character, text[index + 1], font)


def write_specimen_png(ttf_path: Path, kerning: dict[str, int]) -> None:
    font = ImageFont.truetype(str(ttf_path), 82)
    small_font = ImageFont.truetype(str(ttf_path), 48)
    padding = 56
    line_gap = 28
    draw_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    widths = []
    heights = []
    for index, line in enumerate(PREVIEW_LINES):
        selected_font = font if index < 6 else small_font
        bbox = draw_probe.textbbox((0, 0), line, font=selected_font)
        widths.append(math.ceil(text_width_with_kerning(line, selected_font, kerning)))
        heights.append(bbox[3] - bbox[1])
    width = max(widths) + padding * 2
    height = sum(heights) + line_gap * (len(PREVIEW_LINES) - 1) + padding * 2
    image = Image.new("RGB", (width, height), "#111111")
    draw = ImageDraw.Draw(image)
    y = padding
    for index, line in enumerate(PREVIEW_LINES):
        selected_font = font if index < 6 else small_font
        draw_text_with_kerning(draw, (padding, y), line, selected_font, "#f7f1e3", kerning)
        y += heights[index] + line_gap
    image.save(DIST / "specimen.png")


def verify_outputs(paths: dict[str, Path], kerning_pairs: dict[str, Any]) -> dict[str, Any]:
    verification: dict[str, Any] = {}
    for label, path in paths.items():
        if not path.exists() or path.stat().st_size == 0:
            raise ValueError(f"Generated output is missing or empty: {path}")
        font = TTFont(path)
        tables = set(font.keys())
        missing_tables = sorted(REQUIRED_TABLES - tables)
        if missing_tables:
            raise ValueError(f"{path.name} is missing required tables: {missing_tables}")
        cmap = font.getBestCmap()
        expected_chars = set(CAPITALS + CAPITALS.lower()) | {"Á", "É", "Í", " "}
        missing_chars = sorted(char for char in expected_chars if ord(char) not in cmap)
        if missing_chars:
            raise ValueError(f"{path.name} cmap is missing: {missing_chars}")
        if ".notdef" not in font.getGlyphOrder():
            raise ValueError(f"{path.name} has no .notdef glyph")
        verification[label] = {
            "size": path.stat().st_size,
            "tables": sorted(tables),
            "glyphCount": len(font.getGlyphOrder()),
        }

    missing_brand_pairs = sorted(REQUIRED_BRAND_PAIRS - set(kerning_pairs))
    if missing_brand_pairs:
        raise ValueError(f"Kerning data is missing required brand pairs: {missing_brand_pairs}")
    return verification


def main() -> None:
    DIST.mkdir(exist_ok=True)
    glyph_manifest = load_json(ROOT / "glyphs.json")
    accents = load_json(ROOT / "accents.json")
    kerning = load_json(ROOT / "kerning.json")
    validate_glyph_manifest(glyph_manifest)

    glyphs: dict[str, Any] = {".notdef": empty_glyph(), "space": empty_glyph()}
    metrics: dict[str, tuple[int, int]] = {".notdef": (SPACE_WIDTH, 0), "space": (SPACE_WIDTH, 0)}
    source_contours: dict[str, list[RecordingPen]] = {}
    output_manifest: dict[str, Any] = {
        "font": {
            "familyName": "Abiade",
            "styleName": "Regular",
            "unitsPerEm": UPM,
            "capHeight": CAP_HEIGHT,
            "ascender": ASCENDER,
            "descender": DESCENDER,
            "lineGap": LINE_GAP,
            "sideBearing": SIDE_BEARING,
            "spaceWidth": SPACE_WIDTH,
        },
        "glyphs": {},
        "aliases": glyph_manifest["aliases"],
        "marks": {},
        "composites": {},
        "kerning": {},
        "verification": {},
    }

    for letter in CAPITALS:
        relative_path = glyph_manifest["glyphs"][letter]
        shape = read_shape(relative_path)
        _, _, view_width, view_height = shape.view_box
        scale = CAP_HEIGHT / view_height
        default_advance_width = round(view_width * scale + SIDE_BEARING * 2)
        contours = parse_contours(shape, glyph_transform(shape, scale, SIDE_BEARING))
        contours, advance_width, bounds = apply_metric_override(
            contours,
            glyph_manifest.get("metrics", {}).get(letter),
            default_advance_width,
        )
        glyphs[letter] = make_glyph(contours)
        lsb = bounds[0]
        rsb = advance_width - bounds[2]
        metrics[letter] = (advance_width, lsb)
        source_contours[letter] = contours
        output_manifest["glyphs"][letter] = {
            "source": relative_path,
            "viewBox": list(shape.view_box),
            "fillRule": shape.fill_rule,
            "scale": scale,
            "bounds": list(bounds),
            "advanceWidth": advance_width,
            "defaultAdvanceWidth": default_advance_width,
            "leftSideBearing": lsb,
            "rightSideBearing": rsb,
            "metricOverride": glyph_manifest.get("metrics", {}).get(letter),
        }

    mark_shapes = {name: read_shape(path) for name, path in accents["marks"].items()}
    for name, shape in mark_shapes.items():
        output_manifest["marks"][name] = {
            "source": shape.source,
            "viewBox": list(shape.view_box),
            "height": MARK_HEIGHT,
        }

    for character, composite in accents["composites"].items():
        base = composite["base"]
        mark = composite["mark"]
        glyph_name = composite["glyphName"]
        anchor = accents["anchors"][base][mark]
        mark_contours = parse_contours(mark_shapes[mark], mark_transform(mark_shapes[mark], anchor))
        contours = source_contours[base] + mark_contours
        glyphs[glyph_name] = make_glyph(contours)
        bounds = bounds_for(contours)
        if bounds is None:
            raise ValueError(f"{character} produced no drawable bounds")
        base_advance, _ = metrics[base]
        metrics[glyph_name] = (base_advance, bounds[0])
        output_manifest["composites"][character] = {
            "glyphName": glyph_name,
            "base": base,
            "mark": mark,
            "anchor": anchor,
            "bounds": list(bounds),
            "advanceWidth": base_advance,
            "leftSideBearing": bounds[0],
            "rightSideBearing": base_advance - bounds[2],
        }

    aliases = glyph_manifest["aliases"]
    composites = accents["composites"]
    feature_text, kerning_pairs = build_feature_text(kerning, aliases, composites)
    output_manifest["kerning"] = kerning_pairs

    glyph_order = [".notdef", "space", *CAPITALS, *(composites[char]["glyphName"] for char in composites)]
    cmap = {ord(" "): "space"}
    cmap.update({ord(letter): letter for letter in CAPITALS})
    cmap.update({ord(alias): target for alias, target in aliases.items()})
    cmap.update({ord(char): data["glyphName"] for char, data in composites.items()})

    builder = FontBuilder(UPM, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER, lineGap=LINE_GAP)
    builder.setupNameTable(
        {
            "familyName": "Abiade",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Abiade Regular 1.000",
            "fullName": "Abiade Regular",
            "psName": "Abiade-Regular",
            "version": "Version 1.000",
        }
    )
    builder.setupOS2(
        sTypoAscender=ASCENDER,
        sTypoDescender=DESCENDER,
        sTypoLineGap=LINE_GAP,
        usWinAscent=ASCENDER,
        usWinDescent=abs(DESCENDER),
        sCapHeight=CAP_HEIGHT,
        sxHeight=CAP_HEIGHT,
        fsSelection=0x40,
    )
    builder.setupPost()
    builder.setupMaxp()

    font = builder.font
    addOpenTypeFeaturesFromString(font, feature_text)

    ttf_path = DIST / "Abiade-Regular.ttf"
    woff2_path = DIST / "Abiade-Regular.woff2"
    font.save(ttf_path)

    web_font = TTFont(ttf_path)
    web_font.flavor = "woff2"
    web_font.save(woff2_path)

    write_preview_html()
    write_specimen_png(ttf_path, kerning)
    output_manifest["verification"] = verify_outputs(
        {"ttf": ttf_path, "woff2": woff2_path},
        kerning_pairs,
    )
    (DIST / "build-manifest.json").write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {ttf_path.relative_to(ROOT)}")
    print(f"Wrote {woff2_path.relative_to(ROOT)}")
    print(f"Wrote {Path('dist/build-manifest.json')}")
    print(f"Wrote {Path('dist/preview.html')}")
    print(f"Wrote {Path('dist/specimen.png')}")


if __name__ == "__main__":
    main()

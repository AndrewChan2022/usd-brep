"""Check local handbook structure and assets without loading SMLib."""

import ast
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


DOCS = Path(__file__).resolve().parents[1]
BASELINE = "3fd5b9548d19aa8c12c29bc9637a96d42a06f8a5"
GUIDES = """
topology geometry tolerances evaluation spatial-indexing solvers
intersections queries projection-trimming sections booleans
blend tessellation silhouettes-visibility
primitives-sweeps lofts-patches offsets-shells healing-stitching editing
deformation runtime validation-diagnostics polygon-brep assemblies-attributes
native-io usd-interchange local-operations
""".split()


def main():
    errors = []
    links = 0
    diagrams = 0
    index = (DOCS / "README.md").read_text(encoding="utf-8")
    for name in GUIDES:
        path = DOCS / f"{name}.md"
        if not path.is_file():
            errors.append(f"Missing planned guide: {path.name}")
            continue
        content = path.read_text(encoding="utf-8")
        if f"Source baseline: upstream `{BASELINE}`." not in content:
            errors.append(f"{path.name}: missing expected source baseline")
        if f"]({path.name})" not in index:
            errors.append(f"{path.name}: absent from handbook index")
        if "```mermaid" not in content:
            errors.append(f"{path.name}: no architecture/workflow diagram")

    for path in sorted(DOCS.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        fence = None
        display_math = False
        for number, line in enumerate(content.splitlines(), 1):
            if line.rstrip() != line or "\t" in line:
                errors.append(f"{path.name}:{number}: whitespace")
            if line.startswith("```"):
                if fence is None:
                    fence = number
                    diagrams += line.strip() == "```mermaid"
                else:
                    fence = None
                continue
            if fence is not None:
                continue
            if line.strip() == "$$":
                display_math = not display_math
            for match in re.finditer(r"!?\[[^\]\n]*\]\(([^\s)]+)\)", line):
                target = match.group(1).strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                local = unquote(parsed.path)
                if local and not (path.parent / local).exists():
                    errors.append(f"{path.name}:{number}: missing {local}")
                links += 1
        if fence is not None:
            errors.append(f"{path.name}:{fence}: unclosed code fence")
        if display_math:
            errors.append(f"{path.name}: unclosed display math")

    figures = DOCS / "assets" / "handbook"
    svg_files = sorted(figures.glob("*.svg"))
    if len(svg_files) != 7:
        errors.append(f"Expected seven handbook SVGs; found {len(svg_files)}")
    fillet_figures = DOCS / "assets" / "fillets"
    fillet_svg_files = sorted(fillet_figures.glob("*.svg"))
    if len(fillet_svg_files) != 2:
        errors.append(f"Expected two 3D fillet SVGs; found {len(fillet_svg_files)}")
    svg_files.extend(fillet_svg_files)
    local_figures = DOCS / "assets" / "local-operations"
    local_svg_files = sorted(local_figures.glob("*.svg"))
    if len(local_svg_files) != 1:
        errors.append(f"Expected one local-operation SVG; found {len(local_svg_files)}")
    svg_files.extend(local_svg_files)
    for path in svg_files:
        try:
            root = ET.parse(path).getroot()
            if path.parent in [fillet_figures, local_figures]:
                svg_ns = "{http://www.w3.org/2000/svg}"
                if not root.findall(f".//{svg_ns}image"):
                    errors.append(f"{path.name}: missing rasterized surface layer")
                if not root.findall(f".//{svg_ns}text"):
                    errors.append(f"{path.name}: missing vector labels")
                for group in root.findall(f".//{svg_ns}g"):
                    if (group.get("id", "").startswith("Poly3DCollection")
                            and group.findall(f".//{svg_ns}path")):
                        errors.append(f"{path.name}: individual 3D face paths can produce viewer seams")
        except ET.ParseError as error:
            errors.append(f"{path.name}: {error}")
        png = path.with_suffix(".png")
        if not png.is_file() or not png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append(f"{path.name}: missing/invalid PNG alternative")
    for path in [figures / "generate_figures.py", fillet_figures / "generate_figures.py",
                 local_figures / "generate_figures.py",
                 Path(__file__).resolve()]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Checked {len(GUIDES)} planned guides, {links} local links, "
          f"{diagrams} Mermaid fences, {len(svg_files)} SVG/PNG pairs and Python syntax.")
    print("Link checks verify target paths, not fragment anchors. "
          "Diagram/math rendering and C++ execution are separate checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

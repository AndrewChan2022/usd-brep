"""Planar Euler-edit schematics; these do not execute SMLib.

uv run --no-project --with matplotlib python mydocs/assets/euler/generate_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


OUTPUT = Path(__file__).resolve().parent
INK = "#29485e"
BLUE = "#d8eaf4"
ORANGE = "#cf6a15"
matplotlib.rcParams.update({"svg.hashsalt": "smlib-euler", "svg.fonttype": "none", "font.size": 11})


def vertex(axis, x, y, label, offset=(0, 11), new=False):
    axis.plot(x, y, "o", color=ORANGE if new else INK, ms=6, zorder=5)
    axis.annotate(label, (x, y), xytext=offset, textcoords="offset points",
                  ha="center", va="center", color=INK, fontsize=12)


def setup_panel(axis, title, counts):
    axis.set(xlim=(-0.5, 4.5), ylim=(-0.6, 3.6), aspect="equal")
    axis.axis("off")
    axis.set_title(title, loc="left", fontsize=13, color=INK, pad=15)
    axis.text(0.5, -0.06, counts, transform=axis.transAxes, ha="center", color=INK)


def edge_split(axis, after):
    axis.plot([0, 4], [1.5, 1.5], color=INK, lw=2)
    vertex(axis, 0, 1.5, "A")
    vertex(axis, 4, 1.5, "B")
    if after:
        vertex(axis, 2, 1.5, "M", new=True)
        axis.text(1, 1.13, "e1", ha="center", color=INK)
        axis.text(3, 1.13, "e2", ha="center", color=INK)
        axis.text(2, 0.35, "One shared vertex; two child edges", ha="center", color=ORANGE)
    else:
        axis.text(2, 1.13, "e", ha="center", color=INK)
        axis.text(2, 0.35, "An open edge graph", ha="center", color=INK)


def face_split(axis, after):
    corners = [(0, 0), (4, 0), (4, 3), (0, 3)]
    axis.add_patch(Polygon(corners, facecolor=BLUE, edgecolor=INK, lw=1.5))
    for (x, y), label in zip(corners, "ABCD"):
        vertex(axis, x, y, label, (0, -14 if y == 0 else 12))
    if after:
        axis.plot([0, 4], [0, 3], color=ORANGE, lw=2.5)
        axis.text(2.8, 0.8, "F1", ha="center", color=INK)
        axis.text(1.2, 2.2, "F2", ha="center", color=INK)
    else:
        axis.text(2, 1.5, "F", ha="center", color=INK)


def ring_bridge(axis, after):
    outer = [(0, 0), (4, 0), (4, 3), (0, 3)]
    inner = [(1, 0.8), (3, 0.8), (3, 2.2), (1, 2.2)]
    axis.add_patch(Polygon(outer, facecolor=BLUE, edgecolor=INK, lw=1.5))
    axis.add_patch(Polygon(inner, facecolor="white", edgecolor=INK, lw=1.5))
    for x, y in outer + inner:
        axis.plot(x, y, "o", color=INK, ms=4, zorder=5)
    axis.text(2, 1.5, "Open\nhole", ha="center", va="center", color=INK, fontsize=10)
    if after:
        axis.plot([0, 1], [0, 0.8], color=ORANGE, lw=2.5)
        axis.annotate("Bridge: two opposite uses", xy=(0.5, 0.4), xytext=(1.7, -0.48),
                      arrowprops={"arrowstyle": "->", "color": ORANGE},
                      color=ORANGE, ha="center", fontsize=10)
    else:
        axis.text(2, -0.43, "Two separate boundary walks", ha="center", color=INK, fontsize=10)


def verify_counts():
    # Tuples are (vertices, edges, faces, inner rings).
    examples = [((2, 1, 0, 0), (3, 2, 0, 0), 1),
                ((4, 4, 1, 0), (4, 5, 2, 0), 1),
                ((8, 8, 1, 1), (8, 9, 1, 0), 0)]
    for before, after, expected in examples:
        for vertices, edges, faces, rings in [before, after]:
            assert vertices - edges + faces - rings == expected
    box_stages = [(8, 12, 6), (9, 13, 6), (10, 14, 6), (10, 15, 7)]
    for vertices, edges, faces in box_stages:
        assert vertices - edges + faces == 2


def render():
    figure, axes = plt.subplots(3, 2, figsize=(10, 11.5))
    figure.subplots_adjust(left=0.06, right=0.97, top=0.88, bottom=0.08, hspace=0.6, wspace=0.32)
    rows = [
        (edge_split, "1. Subdivide an edge", "V=2, E=1, F=0;  chi=1", "V=3, E=2, F=0;  chi=1"),
        (face_split, "2. Split a disk face", "V=4, E=4, F=1;  chi=1", "V=4, E=5, F=2;  chi=1"),
        (ring_bridge, "3. Join boundary loops", "V=8, E=8, F=1, R=1;  chi=0", "V=8, E=9, F=1, R=0;  chi=0"),
    ]
    for row, (draw, title, before_counts, after_counts) in enumerate(rows):
        for column, after in enumerate([False, True]):
            axis = axes[row, column]
            setup_panel(axis, title if not after else "After", after_counts if after else before_counts)
            draw(axis, after)
    figure.suptitle("Euler edits: connectivity changes, consistent counts", fontsize=17, y=0.97, color=INK)
    figure.text(0.5, 0.925, "Before (left) and after (right)  |  Orange marks new topology",
                ha="center", color=INK, fontsize=12)
    figure.text(0.5, 0.025, "chi = V - E + F - R; R counts inner rings. Schematics, not SMLib execution results.",
                ha="center", color=INK, fontsize=10)
    path = OUTPUT / "topology_edits.svg"
    figure.savefig(path, bbox_inches="tight", metadata={"Date": None})
    figure.savefig(path.with_suffix(".png"), dpi=200, bbox_inches="tight")
    content = path.read_text(encoding="utf-8")
    path.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n",
                    encoding="utf-8", newline="\n")
    plt.close(figure)


if __name__ == "__main__":
    verify_counts()
    render()
    print("Verified three Euler-edit count pairs and the four-stage box imprint accounting.")

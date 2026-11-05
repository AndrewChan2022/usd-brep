"""Analytic face-edit constructions, not captured SMLib output.

uv run --no-project --with numpy --with matplotlib python mydocs/assets/local-operations/generate_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


OUTPUT = Path(__file__).resolve().parent
FACE_INDICES = [
    [0, 3, 2, 1],
    [4, 5, 6, 7],
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [2, 3, 7, 6],
    [3, 0, 4, 7],
]
FACE_COLORS = ["#6999b8", "#edab50", "#9cc8df", "#72a8c7", "#a9d0e3", "#82b5cf"]
matplotlib.rcParams.update({
    "svg.hashsalt": "smlib-local-operations",
    "svg.fonttype": "none",
    "font.size": 10,
})


def construct_block(height, slope):
    footprint = np.array([[0, 0], [20, 0], [20, 12], [0, 12]], dtype=float)
    bottom = np.column_stack((footprint, np.zeros(4)))
    top = np.column_stack((footprint, height + slope * footprint[:, 0]))
    return np.vstack((bottom, top))


def verify_geometry(vertices, height, slope, expected_volume):
    assert np.allclose(vertices[4:, 2], height + slope * vertices[4:, 0])
    assert np.allclose(vertices[:4, 2], 0)
    assert np.allclose(vertices[:4, :2], vertices[4:, :2])
    volume = 0.0
    for indices in FACE_INDICES:
        face = vertices[indices]
        normal = np.cross(face[1] - face[0], face[2] - face[0])
        assert np.isclose(np.dot(normal, face[3] - face[0]), 0)
        for index in range(1, len(face) - 1):
            volume += np.dot(face[0], np.cross(face[index], face[index + 1])) / 6
    assert np.isclose(volume, expected_volume)
    assert np.isclose(volume, 20 * 12 * (height + slope * 20 / 2))
    return volume


def render_panel(figure, index, vertices, title, subtitle, volume):
    axis = figure.add_subplot(1, 3, index, projection="3d")
    faces = [vertices[indices] for indices in FACE_INDICES]
    collection = Poly3DCollection(
        faces,
        facecolors=FACE_COLORS,
        edgecolors="#365468",
        linewidths=0.8,
        antialiased=False,
        rasterized=True,
    )
    axis.add_collection3d(collection)
    axis.set(
        xlim=(0, 20), ylim=(0, 12), zlim=(0, 12),
        xlabel="x", ylabel="y", zlabel="z",
        xticks=[0, 10, 20], yticks=[0, 6, 12], zticks=[0, 4, 8, 12],
    )
    axis.set_box_aspect((20, 12, 12))
    axis.set_proj_type("ortho")
    axis.view_init(elev=24, azim=-58)
    axis.grid(False)
    for dimension in [axis.xaxis, axis.yaxis, axis.zaxis]:
        dimension.pane.fill = False
        dimension.pane.set_edgecolor("#edf1f4")
    axis.set_title(f"{title}\n{subtitle}", fontsize=12, linespacing=1.6, pad=14)
    axis.text2D(0.5, -0.04, f"Volume = {volume:,.0f} cubic units",
                transform=axis.transAxes, ha="center", color="#29485e", fontsize=11)


def save_figure(figure):
    svg = OUTPUT / "face_edits_3d.svg"
    figure.savefig(svg, dpi=300, bbox_inches="tight", metadata={"Date": None})
    figure.savefig(svg.with_suffix(".png"), dpi=300, bbox_inches="tight")
    content = svg.read_text(encoding="utf-8")
    svg.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n",
                   encoding="utf-8", newline="\n")
    plt.close(figure)


def main():
    examples = [
        (8.0, 0.0, 1920, "Original block", "Top: z = 8"),
        (11.0, 0.0, 2640, "A. Raise top by 3", "Replacement: z = 11"),
        (8.0, 0.2, 2400, "B. Tilt top by 11.31 degrees", "Replacement: z = 8 + 0.2x"),
    ]
    figure = plt.figure(figsize=(15, 5.8))
    figure.subplots_adjust(left=0.02, right=0.97, bottom=0.15, top=0.76, wspace=0.17)
    for index, (height, slope, expected_volume, title, subtitle) in enumerate(examples, 1):
        vertices = construct_block(height, slope)
        volume = verify_geometry(vertices, height, slope, expected_volume)
        render_panel(figure, index, vertices, title, subtitle, volume)
    figure.suptitle("Local face edits: change the top, reconnect the side faces", y=0.97, fontsize=17)
    figure.text(0.5, 0.89, "20 × 12 footprint  |  Fixed side-wall supports and bottom  |  Same scale in all panels",
                ha="center", fontsize=12, color="#365468")
    figure.text(0.5, 0.025, "Analytic reference geometry — illustration only; no SMLib operation was executed",
                ha="center", fontsize=10, color="#586874")
    save_figure(figure)
    print("Verified planar faces, shared corner coordinates, and volumes: 1920, 2640, 2400.")


if __name__ == "__main__":
    main()

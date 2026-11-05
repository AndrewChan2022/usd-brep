"""Analytic 3D fillet illustrations, not captured SMLib output.

uv run --no-project --with numpy --with matplotlib python mydocs/assets/fillets/generate_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


OUTPUT = Path(__file__).resolve().parent
BLUE = "#85b7d5"
ORANGE = "#e69032"
GREEN = "#4caa8a"
matplotlib.rcParams.update({"svg.hashsalt": "smlib-fillet-3d", "svg.fonttype": "none"})


def save(figure, name):
    path = OUTPUT / f"{name}.svg"
    figure.savefig(path, bbox_inches="tight", metadata={"Date": None})
    figure.savefig(path.with_suffix(".png"), dpi=150, bbox_inches="tight")
    text = path.read_text(encoding="utf-8")
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n",
                    encoding="utf-8", newline="\n")
    plt.close(figure)


def polygon(axis, vertices, color=BLUE):
    axis.add_collection3d(Poly3DCollection(
        [vertices], facecolors=color, edgecolors="#37556a", linewidths=.8, alpha=1.0))


def box_with_one_fillet():
    length, width, height, radius = 20.0, 12.0, 8.0, 2.0
    figure = plt.figure(figsize=(13, 5.5), layout="constrained")
    angle = np.linspace(0, np.pi / 2, 65)
    arc_y = radius - radius * np.cos(angle)
    arc_z = height - radius + radius * np.sin(angle)
    assert np.allclose((arc_y - radius) ** 2 + (arc_z - height + radius) ** 2, radius ** 2)
    assert np.allclose([arc_y[0], arc_z[0], arc_y[-1], arc_z[-1]], [0, 6, 2, 8])
    for index, rounded in [(1, False), (2, True)]:
        axis = figure.add_subplot(1, 2, index, projection="3d")
        lower_top = height - radius if rounded else height
        top_start = radius if rounded else 0.0
        polygon(axis, [(0, 0, 0), (length, 0, 0), (length, 0, lower_top), (0, 0, lower_top)])
        polygon(axis, [(0, top_start, height), (length, top_start, height),
                       (length, width, height), (0, width, height)])
        polygon(axis, [(0, width, 0), (length, width, 0), (length, width, height), (0, width, height)])
        polygon(axis, [(0, 0, 0), (length, 0, 0), (length, width, 0), (0, width, 0)])
        cap = [(0, 0), (width, 0), (width, height), (top_start, height)]
        if rounded:
            cap.extend(zip(arc_y[::-1], arc_z[::-1]))
        else:
            cap.append((0, height))
        for x in [0, length]:
            polygon(axis, [(x, y, z) for y, z in cap])
        if rounded:
            xx, tt = np.meshgrid(np.linspace(0, length, 25), angle)
            axis.plot_surface(xx, radius - radius * np.cos(tt),
                              height - radius + radius * np.sin(tt), color=ORANGE,
                              linewidth=0, antialiased=False, rcount=65, ccount=25)
            for y, z in [(0, 6), (2, 8)]:
                axis.plot([0, length], [y, y], [z, z], color="#a54c12", lw=1.6, zorder=100)
            title = "After: one cylindrical fillet surface, R = 2"
        else:
            axis.plot([0, length], [0, 0], [height, height], color=ORANGE, lw=4, zorder=100)
            title = "Before: select the edge y = 0, z = 8"
        axis.set(title=title, xlabel="x", ylabel="y", zlabel="z",
                 xlim=(0, length), ylim=(0, width), zlim=(0, height))
        axis.set_box_aspect((length, width, height))
        axis.view_init(elev=24, azim=-58)
        axis.set_proj_type("ortho")
    figure.suptitle("20 × 12 × 8 block — one edge rounded along its full 20-unit length", fontsize=15)
    save(figure, "single_edge_3d")
    expected_volume = length * width * height - length * radius ** 2 * (1 - np.pi / 4)
    print(f"Ideal single-edge result volume: {expected_volume:.9f}")


def three_edge_corner():
    figure = plt.figure(figsize=(8, 6.5), layout="constrained")
    axis = figure.add_subplot(projection="3d")
    theta, run = np.meshgrid(np.linspace(0, np.pi / 2, 49), np.linspace(-2, 0, 20))
    c, s = np.cos(theta), np.sin(theta)
    for x, y, z in [(run, c, s), (c, run, s), (c, s, run)]:
        axis.plot_surface(x, y, z, color=ORANGE, linewidth=0, antialiased=False)
    u, v = np.meshgrid(np.linspace(0, np.pi / 2, 49), np.linspace(0, np.pi / 2, 49))
    x, y, z = np.cos(v) * np.cos(u), np.cos(v) * np.sin(u), np.sin(v)
    assert np.allclose(x ** 2 + y ** 2 + z ** 2, 1.0)
    axis.plot_surface(x, y, z, color=GREEN, linewidth=0, antialiased=False, rcount=49, ccount=49)
    t = np.linspace(0, np.pi / 2, 90)
    # On these interfaces, sphere and cylinder share radial unit normals.
    for x, y, z in [(0 * t, np.cos(t), np.sin(t)),
                    (np.cos(t), 0 * t, np.sin(t)),
                    (np.cos(t), np.sin(t), 0 * t)]:
        assert np.allclose(x * x + y * y + z * z, 1.0)
        axis.plot(x, y, z, color="#21674e", lw=2)
    axis.set(title="Three perpendicular, equal-radius fillets meet at a corner",
             xlabel="local x / r", ylabel="local y / r", zlabel="local z / r",
             xlim=(-2, 1), ylim=(-2, 1), zlim=(-2, 1))
    axis.set_box_aspect((1, 1, 1))
    axis.view_init(elev=25, azim=36)
    axis.set_proj_type("ortho")
    axis.legend(handles=[Patch(color=ORANGE, label="Three quarter-cylinder edge fillets"),
                         Patch(color=GREEN, label="Spherical corner patch (ideal symmetric case)")],
                loc="upper left", bbox_to_anchor=(0, .04), frameon=False)
    save(figure, "three_edge_corner_3d")


if __name__ == "__main__":
    box_with_one_fillet()
    three_edge_corner()
    print("3D figure geometry checks passed. SMLib was not executed.")

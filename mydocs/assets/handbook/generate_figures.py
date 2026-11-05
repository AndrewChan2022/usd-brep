"""Reproducible mathematical illustrations; this script does not execute SMLib.

Run from the repository root:
    uv run --no-project --with numpy --with matplotlib python \
        mydocs/assets/handbook/generate_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import numpy as np


matplotlib.rcParams["svg.hashsalt"] = "smlib-handbook"
OUTPUT = Path(__file__).resolve().parent
BLUE = "#2463a6"
ORANGE = "#c65e20"
GREEN = "#25816b"


def save(figure, name):
    svg = OUTPUT / f"{name}.svg"
    figure.savefig(svg, bbox_inches="tight", metadata={"Date": None})
    figure.savefig(OUTPUT / f"{name}.png", dpi=140, bbox_inches="tight")
    source = svg.read_text(encoding="utf-8")
    svg.write_text("\n".join(line.rstrip() for line in source.splitlines()) + "\n",
                   encoding="utf-8", newline="\n")
    plt.close(figure)


def plane_axes(axis, title):
    axis.set_aspect("equal")
    axis.set(title=title, xlabel="x", ylabel="y")


def containment():
    figure, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for axis, inner_x, title in [
        (axes[0], 1, "Containment: boundary gap = 1"),
        (axes[1], 5, "Separate: boundary gap = 1"),
    ]:
        axis.add_patch(Rectangle((0, 0), 4, 4, facecolor=BLUE, alpha=.18, edgecolor=BLUE, lw=2))
        axis.add_patch(Rectangle((inner_x, 1), 1, 1, facecolor=ORANGE, alpha=.8))
        axis.set(xlim=(-.5, 6.5), ylim=(-.5, 4.5))
        plane_axes(axis, title)
        start, stop = (0, 1) if inner_x == 1 else (4, 5)
        axis.annotate("", (stop, 1.5), (start, 1.5),
                      arrowprops={"arrowstyle": "<->", "lw": 2})
    save(figure, "boundary_distance")


def transitions():
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    radius = 1.0
    angle = np.linspace(np.pi, 1.5 * np.pi, 150)
    arc = np.column_stack((radius + radius * np.cos(angle), radius + radius * np.sin(angle)))
    assert np.max(np.abs(np.linalg.norm(arc - [radius, radius], axis=1) - radius)) < 1e-12
    for axis in axes:
        axis.plot([0, 0, 2], [2, 0, 0], "--", color="#88939f")
        axis.set(xlim=(-.15, 2.1), ylim=(-.15, 2.1))
    axes[0].plot(*arc.T, color=BLUE, lw=3)
    axes[0].plot([0, 1, 1], [1, 1, 0], ":", color=BLUE)
    axes[0].scatter([1], [1], color=BLUE)
    axes[0].text(.33, 1.08, "r = 1")
    plane_axes(axes[0], "Circular transition: radius r")
    width = 1.0
    setback = width / np.sqrt(2)
    assert abs(np.linalg.norm([setback, -setback]) - width) < 1e-12
    axes[1].plot([0, setback], [setback, 0], color=ORANGE, lw=3)
    axes[1].text(.5, .6, "width w = 1")
    axes[1].text(.35, -.11, "setback = w / √2", fontsize=10)
    plane_axes(axes[1], "Symmetric 90° chamfer: width w")
    save(figure, "transitions")


def sections():
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    axes[0].add_patch(Circle((0, 0), 2, facecolor=BLUE, alpha=.5))
    axes[0].add_patch(Circle((0, 0), 1, facecolor="white", edgecolor=BLUE, lw=2))
    axes[0].set(xlim=(-2.3, 2.3), ylim=(-2.3, 2.3))
    axes[0].text(-.55, 0, "void", fontsize=12)
    axes[0].text(-1.3, 1.4, "material")
    plane_axes(axes[0], "Hollow-body section: outer loop and hole")
    x = np.linspace(-2, 2, 200)
    axes[1].fill_between(x, 0, 2, color=GREEN, alpha=.25)
    axes[1].plot(x, np.zeros_like(x), color=GREEN, lw=2)
    axes[1].annotate("normal n", (0, 1.5), (0, .15),
                     arrowprops={"arrowstyle": "->", "color": GREEN}, ha="center")
    axes[1].text(.6, 1.2, "positive half-space")
    axes[1].text(-1.6, -.9, "negative half-space")
    axes[1].set(xlim=(-2.3, 2.3), ylim=(-2.3, 2.3))
    plane_axes(axes[1], "Cut: retain the selected half-space")
    assert abs(np.pi * (2 ** 2 - 1 ** 2) - 3 * np.pi) < 1e-12
    save(figure, "sections")


def chord_error():
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    theta = np.pi / 3
    angles = np.linspace(-theta / 2, theta / 2, 200)
    chord_x = np.cos(theta / 2)
    axes[0].plot(np.cos(angles), np.sin(angles), color=BLUE, lw=3, label="Unit circular arc")
    axes[0].plot([chord_x, chord_x], [-.5, .5], color=ORANGE, lw=2, label="Chord")
    axes[0].annotate("", (1, 0), (chord_x, 0), arrowprops={"arrowstyle": "<->"})
    axes[0].text(.88, .08, "sagitta e")
    axes[0].set(xlim=(.75, 1.1), ylim=(-.6, .6), title="Chord error at the arc midpoint")
    axes[0].set_aspect("equal")
    axes[0].legend(loc="lower right", fontsize=8)
    n = np.arange(3, 101)
    exact = 1 - np.cos(np.pi / n)
    approximation = np.pi ** 2 / (2 * n ** 2)
    assert np.all(np.diff(exact) < 0)
    assert np.all(exact <= approximation + 1e-14)
    axes[1].loglog(n, exact, color=BLUE, label="Exact: 1 − cos(π/n)")
    axes[1].loglog(n, approximation, "--", color=ORANGE, label="Small-angle approximation")
    axes[1].set(title="Unit circle split into n equal arcs", xlabel="Number of segments n", ylabel="Maximum arc/chord error")
    axes[1].legend(fontsize=9)
    save(figure, "chord_error")


def correspondence():
    figure, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for axis, reverse, title in [
        (axes[0], False, "Aligned section directions"),
        (axes[1], True, "Reversed correspondence crosses rulings"),
    ]:
        axis.plot([0, 1], [0, 0], color=BLUE, lw=4)
        axis.plot([0, 1], [1, 1], color=ORANGE, lw=4)
        for parameter in np.linspace(0, 1, 9):
            end = 1 - parameter if reverse else parameter
            axis.plot([parameter, end], [0, 1], color=GREEN, alpha=.65)
        axis.set(xlim=(-.1, 1.1), ylim=(-.15, 1.15))
        plane_axes(axis, title)
    save(figure, "loft_correspondence")


def boolean_sets():
    axis_values = np.linspace(-2.2, 2.2, 400)
    x, y = np.meshgrid(axis_values, axis_values)
    a = (x + .55) ** 2 + y ** 2 <= 1.4 ** 2
    b = (x - .55) ** 2 + y ** 2 <= 1.4 ** 2
    figure, axes = plt.subplots(1, 3, figsize=(12, 4), layout="constrained")
    for axis, mask, title in [
        (axes[0], a | b, "Union A ∪ B"),
        (axes[1], a & b, "Intersection A ∩ B"),
        (axes[2], a & ~b, "Difference A − B"),
    ]:
        axis.contourf(x, y, mask.astype(int), levels=[.5, 1.5], colors=[BLUE], alpha=.6)
        axis.add_patch(Circle((-.55, 0), 1.4, fill=False, edgecolor="#555555", ls="--"))
        axis.add_patch(Circle((.55, 0), 1.4, fill=False, edgecolor=ORANGE, ls="--"))
        plane_axes(axis, title)
    assert np.array_equal((a & ~b) | (a & b), a)
    save(figure, "boolean_sets")


def twist():
    figure = plt.figure(figsize=(10, 5), layout="constrained")
    for index, amount, title in [(1, 0, "Input lattice"), (2, np.pi / 2, "Twist angle increases with z")]:
        axis = figure.add_subplot(1, 2, index, projection="3d")
        z = np.linspace(0, 2, 80)
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                angle = amount * z / 2
                xx = x * np.cos(angle) - y * np.sin(angle)
                yy = x * np.sin(angle) + y * np.cos(angle)
                assert np.max(np.abs(xx ** 2 + yy ** 2 - (x ** 2 + y ** 2))) < 1e-12
                axis.plot(xx, yy, z, color=BLUE if index == 1 else GREEN)
        axis.set(title=title, xlabel="x", ylabel="y", zlabel="z")
        axis.set_box_aspect((1, 1, 1))
    save(figure, "twist")


def main():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": .15,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })
    for generator in [containment, transitions, sections, chord_error, correspondence, boolean_sets, twist]:
        generator()
    print("Generated seven educational figures; analytic invariants passed. SMLib was not executed.")


if __name__ == "__main__":
    main()

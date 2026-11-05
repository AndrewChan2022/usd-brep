"""Generate mathematical illustrations, independently of SMLib.

Run from the repository root:
    uv run --no-project --with numpy --with scipy --with matplotlib python \
        mydocs/assets/nurbs/generate_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import BSpline


OUTPUT = Path(__file__).resolve().parent
BLUE = "#2463a6"
ORANGE = "#c65e20"
GREEN = "#25816b"
KNOTS = np.array([0, 0, 0, 0, .2, .4, .6, .8, 1, 1, 1, 1])
CONTROLS = np.array([
    [0, 0], [1, 1.8], [2, -.2], [3, 1.3],
    [4, 1.1], [5, -.3], [6, 1.5], [7, 0],
])


def save(figure, name):
    figure.savefig(OUTPUT / f"{name}.svg", bbox_inches="tight")
    figure.savefig(OUTPUT / f"{name}.png", dpi=170, bbox_inches="tight")
    plt.close(figure)


def local_control():
    parameters = np.linspace(0, 1, 801)
    basis = BSpline(KNOTS, np.eye(len(CONTROLS)), 3)(parameters)
    changed = CONTROLS.copy()
    changed[3] += [0, 1.2]
    original = basis @ CONTROLS
    edited = basis @ changed
    assert np.max(np.abs(basis.sum(axis=1) - 1)) < 1e-12
    assert np.min(basis) >= -1e-12
    outside = parameters >= .8
    assert np.max(np.abs(original[outside] - edited[outside])) < 1e-12

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    for index in range(len(CONTROLS)):
        axes[0].plot(parameters, basis[:, index], color=ORANGE if index == 3 else "#a7b8ca",
                     linewidth=3 if index == 3 else 1)
    axes[0].axvspan(0, .8, alpha=.07, color=ORANGE)
    axes[0].set(title="Cubic basis: highlighted N₃,₃", xlabel="Parameter u", ylabel="Basis value")
    axes[0].text(.36, .82, "Support: [u₃, u₇] = [0, 0.8]", ha="center")
    axes[1].plot(*CONTROLS.T, "o--", color="#a7b8ca", linewidth=1, label="Original control polygon")
    axes[1].plot(*original.T, color=BLUE, linewidth=2.5, label="Original curve")
    axes[1].plot(*edited.T, color=ORANGE, linewidth=2, label="After moving P₃")
    axes[1].scatter(*changed[3], color=ORANGE, zorder=4)
    axes[1].annotate("", xy=changed[3], xytext=CONTROLS[3],
                     arrowprops={"arrowstyle": "->", "color": ORANGE, "lw": 2})
    axes[1].set(title="One control edit has local influence", xlabel="x", ylabel="y")
    axes[1].set_aspect("equal", adjustable="datalim")
    axes[1].legend(loc="upper left", fontsize=9)
    save(figure, "local_control")


def rational_weights():
    parameters = np.linspace(0, 1, 501)
    basis = np.column_stack(((1 - parameters) ** 2, 2 * parameters * (1 - parameters), parameters ** 2))
    controls = np.array([[1, 0], [1, 1], [0, 1]])
    figure, axis = plt.subplots(figsize=(7, 6), layout="constrained")
    axis.plot(*controls.T, "o--", color="#8d98a2", label="Control polygon")
    for weight, color, label in [
        (.3, "#9475aa", "w₁ = 0.3"),
        (np.sqrt(.5), GREEN, "w₁ = √2/2: exact circle"),
        (1, BLUE, "w₁ = 1: polynomial quadratic"),
        (2, ORANGE, "w₁ = 2"),
    ]:
        weighted_basis = basis * np.array([1, weight, 1])
        points = (weighted_basis @ controls) / weighted_basis.sum(axis=1)[:, None]
        axis.plot(*points.T, color=color, linewidth=2.5, label=label)
        if weight == np.sqrt(.5):
            assert np.max(np.abs(np.linalg.norm(points, axis=1) - 1)) < 1e-12
    axis.scatter([np.sqrt(.5)], [np.sqrt(.5)], color=GREEN, zorder=5)
    axis.annotate("u = 0.5", (np.sqrt(.5), np.sqrt(.5)), xytext=(.3, .5),
                  arrowprops={"arrowstyle": "->", "color": GREEN})
    axis.set(title="Same quadratic basis and controls; different weights",
             xlabel="x", ylabel="y", xlim=(-.06, 1.08), ylim=(-.06, 1.12))
    axis.set_aspect("equal")
    axis.legend(loc="lower left", fontsize=9)
    save(figure, "rational_weights")


def knot_insertion():
    original = BSpline(KNOTS, CONTROLS, 3)
    refined = original.insert_knot(.5)
    parameters = np.linspace(0, 1, 801)
    deviation = np.max(np.linalg.norm(original(parameters) - refined(parameters), axis=1))
    assert deviation < 1e-12
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained", sharex=True, sharey=True)
    for axis, spline, title, color in [
        (axes[0], original, "Before: 8 controls, degree 3", BLUE),
        (axes[1], refined, "After inserting u = 0.5: 9 controls, degree 3", ORANGE),
    ]:
        axis.plot(*spline.c.T, "o--", color=color, alpha=.65, label="Control polygon")
        axis.plot(*spline(parameters).T, color=GREEN, linewidth=2.5, label="Same curve")
        axis.scatter(*spline(.5), color="black", s=24, zorder=4)
        axis.set(title=title, xlabel="x", ylabel="y")
        axis.set_aspect("equal", adjustable="box")
        axis.legend(fontsize=9)
    save(figure, "knot_insertion")
    print(f"Knot insertion maximum sampled deviation: {deviation:.3g}")


def main():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": .18,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })
    local_control()
    rational_weights()
    knot_insertion()
    print("Verified basis properties, local support, exact circle, and refinement invariance.")


if __name__ == "__main__":
    main()

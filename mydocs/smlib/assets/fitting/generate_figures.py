"""Generate educational B-spline figures; this does not execute SMLib.

Run from the repository root:
    uv run --no-project --with numpy --with scipy --with matplotlib python \
        mydocs/smlib/assets/fitting/generate_figures.py
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


def interpolation_knots(parameters, degree):
    """Clamped knot averaging for one control point per sample."""
    interior = [
        np.mean(parameters[index:index + degree])
        for index in range(1, len(parameters) - degree)
    ]
    return np.r_[np.zeros(degree + 1), interior, np.ones(degree + 1)]


def uniform_knots(control_count, degree):
    interior = np.linspace(0.0, 1.0, control_count - degree + 1)[1:-1]
    return np.r_[np.zeros(degree + 1), interior, np.ones(degree + 1)]


def basis_matrix(parameters, knots, degree):
    return BSpline.design_matrix(parameters, knots, degree).toarray()


def save_figure(figure, name):
    figure.savefig(OUTPUT / f"{name}.svg", bbox_inches="tight")
    figure.savefig(OUTPUT / f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def configure_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.18,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })


def comparison_figure():
    parameters = np.linspace(0.0, 1.0, 17)
    noise = np.array([0, .07, -.08, .12, -.09, .06, -.12, .09, -.07, .1, -.1, .07, -.06, .1, -.08, .04, 0])
    samples = np.column_stack((parameters, np.sin(2 * np.pi * parameters) + noise))
    degree = 3
    dense = np.linspace(0.0, 1.0, 500)

    knots = interpolation_knots(parameters, degree)
    matrix = basis_matrix(parameters, knots, degree)
    controls = np.linalg.solve(matrix, samples)
    interpolant = BSpline(knots, controls, degree)
    assert np.max(np.abs(interpolant(parameters) - samples)) < 1e-10

    fit_knots = uniform_knots(7, degree)
    fit_matrix = basis_matrix(parameters, fit_knots, degree)
    fit_controls = np.empty((7, 2))
    fit_controls[0] = samples[0]
    fit_controls[-1] = samples[-1]
    rhs = samples - fit_matrix[:, :1] * samples[0] - fit_matrix[:, -1:] * samples[-1]
    fit_controls[1:-1] = np.linalg.lstsq(fit_matrix[:, 1:-1], rhs, rcond=None)[0]
    fit = BSpline(fit_knots, fit_controls, degree)
    fitted_samples = fit(parameters)
    residuals = np.linalg.norm(fitted_samples - samples, axis=1)

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True, sharey=True, layout="constrained")
    for axis, curve, color in zip(axes, (interpolant, fit), (BLUE, ORANGE)):
        values = curve(dense)
        axis.plot(values[:, 0], values[:, 1], color=color, linewidth=2.5, label="Cubic B-spline")
        axis.scatter(samples[:, 0], samples[:, 1], s=32, color="#263747", zorder=4, label="Input samples")
        axis.set_xlabel("x")
        axis.legend(loc="lower left", fontsize=9)
    for point, fitted in zip(samples, fitted_samples):
        axes[1].plot([point[0], fitted[0]], [point[1], fitted[1]], color=ORANGE, linewidth=2)
    axes[0].set_ylabel("y")
    axes[0].set_title("Interpolation: 17 samples, 17 control points")
    axes[1].set_title("Least squares: 17 samples, 7 control points")
    figure.suptitle("Same degree, different constraints and model size", fontsize=15)
    save_figure(figure, "interpolation_vs_approximation")
    print(f"Illustrative fit: sample RMS={np.sqrt(np.mean(residuals ** 2)):.6f}, max={residuals.max():.6f}")


def parameterization_figure():
    points = np.array([[0, 0], [.2, .45], [.45, .7], [1.5, 1], [3.5, .4], [3.8, -.4], [4, 0]])
    distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
    modes = [("Uniform", 0.0, BLUE), ("Chord length", 1.0, ORANGE), ("Centripetal", .5, GREEN)]
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.7), layout="constrained")
    for row, (name, exponent, color) in enumerate(modes):
        increments = distances ** exponent
        parameters = np.r_[0.0, np.cumsum(increments) / np.sum(increments)]
        knots = interpolation_knots(parameters, 3)
        controls = np.linalg.solve(basis_matrix(parameters, knots, 3), points)
        values = BSpline(knots, controls, 3)(np.linspace(0.0, 1.0, 500))
        axes[0].plot(values[:, 0], values[:, 1], color=color, linewidth=2, label=name)
        axes[1].hlines(row, 0, 1, color="#c4cbd1")
        axes[1].scatter(parameters, np.full_like(parameters, row), color=color, s=40)
        for index, parameter in enumerate(parameters):
            axes[1].annotate(str(index), (parameter, row), xytext=(0, 9), textcoords="offset points", ha="center")
    axes[0].scatter(points[:, 0], points[:, 1], color="#263747", s=30, zorder=5)
    axes[0].set(xlabel="x", ylabel="y", title="All three curves pass through the same samples")
    axes[0].legend(fontsize=9)
    axes[1].set_yticks(range(3), [entry[0] for entry in modes])
    axes[1].set(xlabel="Assigned sample parameter", ylim=(-.5, 2.6), title="Parameter spacing is a modeling choice")
    figure.suptitle("Parameterization changes the curve between samples", fontsize=15)
    save_figure(figure, "parameterization")


def tensor_product_figure():
    u = np.linspace(0.0, 1.0, 9)
    v = np.linspace(0.0, 1.0, 7)
    uu, vv = np.meshgrid(u, v, indexing="ij")
    heights = .35 * np.sin(np.pi * uu) * np.cos(np.pi * vv)
    heights += .018 * np.sin(19 * uu + 3 * vv) * np.sin(np.pi * uu) * np.sin(np.pi * vv)
    ku = uniform_knots(5, 3)
    kv = uniform_knots(4, 3)
    au = basis_matrix(u, ku, 3)
    av = basis_matrix(v, kv, 3)
    temporary = np.linalg.lstsq(au, heights, rcond=None)[0]
    controls = np.linalg.lstsq(av, temporary.T, rcond=None)[0].T
    dense = np.linspace(0.0, 1.0, 45)
    du, dv = np.meshgrid(dense, dense, indexing="ij")
    fitted = basis_matrix(dense, ku, 3) @ controls @ basis_matrix(dense, kv, 3).T
    assert controls.shape == (5, 4)

    figure = plt.figure(figsize=(12, 5), layout="constrained")
    left = figure.add_subplot(1, 2, 1)
    for row in range(len(u)):
        left.plot(uu[row], vv[row], color="#c4cbd1", linewidth=1)
    for column in range(len(v)):
        left.plot(uu[:, column], vv[:, column], color="#c4cbd1", linewidth=1)
    left.scatter(uu, vv, color=BLUE, s=24)
    left.set(xlabel="u", ylabel="v", title="Structured data: 9 x 7 samples", aspect="equal")
    right = figure.add_subplot(1, 2, 2, projection="3d")
    right.plot_surface(du, dv, fitted, color="#77b7d8", alpha=.75, edgecolor="none")
    right.scatter(uu, vv, heights, color="#263747", s=10, depthshade=False)
    right.set(xlabel="x = u", ylabel="y = v", zlabel="z", title="Bicubic fit: 5 x 4 control points")
    right.view_init(elev=25, azim=-55)
    figure.suptitle("Tensor product: solve along U, then along V", fontsize=15)
    save_figure(figure, "tensor_product")


def main():
    configure_style()
    comparison_figure()
    parameterization_figure()
    tensor_product_figure()


if __name__ == "__main__":
    main()

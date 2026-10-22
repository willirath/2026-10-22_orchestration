"""Tests for montepi.plot, written against the interface contract in PLAN.md.

Synthetic inputs only; montepi.core is not used.
"""

import math

import numpy as np
import pytest

matplotlib = pytest.importorskip("matplotlib")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.collections import LineCollection, PathCollection, PolyCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from montepi.plot import plot_convergence, plot_samples  # noqa: E402


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


@pytest.fixture
def points():
    """Hand-picked points: 3 inside the quarter circle, 2 outside."""
    x = np.array([0.1, 0.5, 0.0, 0.9, 0.8])
    y = np.array([0.1, 0.5, 1.0, 0.9, 0.8])
    return x, y


@pytest.fixture
def running():
    """Synthetic running estimate converging to pi."""
    n = np.arange(1, 1001)
    return math.pi + 1.0 / np.sqrt(n) * np.cos(n)


def _scatter_offsets(ax):
    offs = [
        np.asarray(c.get_offsets()).reshape(-1, 2)
        for c in ax.collections
        if isinstance(c, PathCollection)
    ]
    return np.concatenate(offs) if offs else np.empty((0, 2))


# --- plot_samples ---------------------------------------------------------


def test_plot_samples_returns_axes(points):
    ax = plot_samples(*points)
    assert isinstance(ax, Axes)


def test_plot_samples_uses_given_ax(points):
    _, ax = plt.subplots()
    assert plot_samples(*points, ax=ax) is ax


def test_plot_samples_equal_aspect_and_unit_limits(points):
    ax = plot_samples(*points)
    assert ax.get_aspect() in (1.0, "equal")
    assert ax.get_xlim() == pytest.approx((0.0, 1.0))
    assert ax.get_ylim() == pytest.approx((0.0, 1.0))


def test_plot_samples_draws_all_points(points):
    x, y = points
    ax = plot_samples(x, y)
    offs = _scatter_offsets(ax)
    assert len(offs) == len(x)
    r2 = offs[:, 0] ** 2 + offs[:, 1] ** 2
    assert np.any(r2 <= 1.0), "no inside points drawn"
    assert np.any(r2 > 1.0), "no outside points drawn"


def test_plot_samples_larger_random_input():
    rng = np.random.default_rng(1)
    x, y = rng.random(500), rng.random(500)
    ax = plot_samples(x, y)
    offs = _scatter_offsets(ax)
    assert len(offs) == 500
    drawn = set(map(tuple, np.round(offs, 12)))
    given = set(zip(np.round(x, 12), np.round(y, 12)))
    assert drawn == given


# --- plot_convergence -----------------------------------------------------


def test_plot_convergence_returns_axes(running):
    ax = plot_convergence(running)
    assert isinstance(ax, Axes)


def test_plot_convergence_uses_given_ax(running):
    _, ax = plt.subplots()
    assert plot_convergence(running, ax=ax) is ax


def test_plot_convergence_log_x(running):
    ax = plot_convergence(running)
    assert ax.get_xscale() == "log"


def _has_horizontal_line_at(ax, value):
    for line in ax.get_lines():
        if isinstance(line, Line2D):
            yd = np.asarray(line.get_ydata(), dtype=float)
            if yd.size >= 2 and np.allclose(yd, value):
                return True
    for coll in ax.collections:
        if isinstance(coll, LineCollection):
            for seg in coll.get_segments():
                seg = np.asarray(seg, dtype=float)
                if seg.shape[0] >= 2 and np.allclose(seg[:, 1], value):
                    return True
    return False


def test_plot_convergence_line_at_pi(running):
    ax = plot_convergence(running)
    assert _has_horizontal_line_at(ax, math.pi)


def test_plot_convergence_plots_running_data(running):
    ax = plot_convergence(running)
    lengths = [len(np.atleast_1d(line.get_ydata())) for line in ax.get_lines()]
    assert len(running) in lengths


# --- artists required by the contract -------------------------------------


def test_plot_samples_colours_inside_and_outside_differently(points):
    ax = plot_samples(*points)
    colours = {}
    for coll in ax.collections:
        if not isinstance(coll, PathCollection):
            continue
        offs = np.asarray(coll.get_offsets()).reshape(-1, 2)
        if len(offs) == 0:
            continue
        inside = offs[:, 0] ** 2 + offs[:, 1] ** 2 <= 1.0
        assert inside.all() or not inside.any(), "collection mixes inside and outside"
        colours[bool(inside[0])] = tuple(np.round(coll.get_facecolor()[0], 6))
    assert set(colours) == {True, False}
    assert colours[True] != colours[False]


def test_plot_samples_draws_quarter_circle_arc(points):
    ax = plot_samples(*points)
    arcs = [
        line
        for line in ax.get_lines()
        if len(line.get_xdata()) > 2
        and np.allclose(np.hypot(line.get_xdata(), line.get_ydata()), 1.0)
    ]
    assert len(arcs) == 1
    xd, yd = arcs[0].get_xdata(), arcs[0].get_ydata()
    assert xd.min() == pytest.approx(0.0, abs=1e-12)
    assert yd.min() == pytest.approx(0.0, abs=1e-12)


def test_plot_convergence_band_is_two_sigma(running):
    ax = plot_convergence(running)
    bands = [c for c in ax.collections if isinstance(c, PolyCollection)]
    assert len(bands) == 1
    xy = np.concatenate([p.vertices for p in bands[0].get_paths()])
    n = np.arange(1, len(running) + 1)
    on_grid = np.isin(xy[:, 0], n)
    xs, ys = xy[on_grid, 0], xy[on_grid, 1]
    two_sigma = 8.0 * np.sqrt(math.pi / 4 * (1 - math.pi / 4) / xs)
    assert np.allclose(np.abs(ys - math.pi), two_sigma)
    assert np.any(ys > math.pi) and np.any(ys < math.pi)

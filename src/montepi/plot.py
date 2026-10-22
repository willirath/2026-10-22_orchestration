"""Plotting helpers (requires the ``plot`` extra: matplotlib)."""

import matplotlib.pyplot as plt
import numpy as np


def plot_samples(x, y, ax=None):
    """Scatter, inside/outside coloured, quarter-circle arc, equal aspect."""
    if ax is None:
        _, ax = plt.subplots()
    x = np.asarray(x)
    y = np.asarray(y)
    inside = x**2 + y**2 <= 1.0
    ax.scatter(x[inside], y[inside], s=4, color="tab:blue", label="inside")
    ax.scatter(x[~inside], y[~inside], s=4, color="tab:orange", label="outside")
    theta = np.linspace(0.0, np.pi / 2, 200)
    ax.plot(np.cos(theta), np.sin(theta), color="black", lw=1.5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="upper right")
    return ax


def plot_convergence(running, ax=None):
    """pi_hat vs n on log-x, line at pi, band of +-2 sigma around pi."""
    if ax is None:
        _, ax = plt.subplots()
    running = np.asarray(running)
    n = np.arange(1, len(running) + 1)
    sigma = 4.0 * np.sqrt(np.pi / 4 * (1 - np.pi / 4) / n)
    ax.plot(n, running, color="tab:blue", lw=1, label=r"$\hat\pi$")
    ax.axhline(np.pi, color="black", lw=1, label=r"$\pi$")
    ax.fill_between(
        n, np.pi - 2 * sigma, np.pi + 2 * sigma, color="tab:gray", alpha=0.3,
        label=r"$\pi \pm 2\sigma$",
    )
    ax.set_xscale("log")
    ax.set_xlabel(r"number of samples $n$")
    ax.set_ylabel(r"$\hat\pi$")
    ax.legend(loc="upper right")
    return ax

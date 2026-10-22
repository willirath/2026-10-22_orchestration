"""Plotting helpers (requires the ``plot`` extra: matplotlib)."""

import matplotlib.pyplot as plt  # noqa: F401


def plot_samples(x, y, ax=None):
    """Scatter, inside/outside coloured, quarter-circle arc, equal aspect."""
    raise NotImplementedError


def plot_convergence(running, ax=None):
    """pi_hat vs n on log-x, line at pi, band of +-2 sigma around pi."""
    raise NotImplementedError

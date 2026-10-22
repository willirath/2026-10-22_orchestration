"""Core Monte Carlo estimation of pi.

Points $(x_i, y_i)$ are drawn uniformly in the unit square $[0, 1)^2$. The
fraction $p$ inside the quarter circle estimates $\\pi / 4$.
"""

import numpy as np


def sample_points(n, seed=None):
    """Return (x, y), two float arrays of length n, uniform in [0, 1).

    seed: int, np.random.Generator or None. ValueError if n < 1.
    """
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    rng = np.random.default_rng(seed)
    x = rng.random(int(n))
    y = rng.random(int(n))
    return x, y


def estimate_pi(x, y):
    r"""Return (pi_hat, std_error) from the sample coordinates x, y.

    With the inside fraction

    $$
    p = \frac{1}{n} \sum_{i=1}^{n} \mathbf{1}\left[x_i^2 + y_i^2 \le 1\right]
    $$

    the estimate is $\hat\pi = 4p$ and its standard error is

    $$
    \sigma_{\hat\pi} = 4\sqrt{\frac{p(1-p)}{n}}.
    $$

    Points on the circle ($x^2 + y^2 = 1$) count as inside.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    p = np.mean(x * x + y * y <= 1.0)
    pi_hat = 4.0 * p
    std_error = 4.0 * np.sqrt(p * (1.0 - p) / x.size)
    return float(pi_hat), float(std_error)


def running_estimate(x, y):
    r"""Return an array of length n: pi_hat after the first k samples, k = 1..n.

    $$
    \hat\pi_k = \frac{4}{k} \sum_{i=1}^{k} \mathbf{1}\left[x_i^2 + y_i^2 \le 1\right],
    \qquad k = 1, \dots, n.
    $$
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    inside = np.cumsum(x * x + y * y <= 1.0)
    return 4.0 * inside / np.arange(1, x.size + 1)

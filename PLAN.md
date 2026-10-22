# Plan: `montepi` — estimate pi by Monte Carlo

Sample $n$ points $(x_i, y_i)$ uniformly in the unit square $[0,1)^2$. The fraction
$p$ that falls inside the quarter circle estimates $\pi/4$:

$$
p = \frac{1}{n} \sum_{i=1}^{n} \mathbf{1}\left[x_i^2 + y_i^2 \le 1\right],
\qquad
\hat\pi = 4p,
\qquad
\sigma_{\hat\pi} = 4\sqrt{\frac{p(1-p)}{n}}.
$$

## Layout and tooling

- `uv`, Python ≥ 3.11, src layout, deps: `numpy`; extra `plot`: `matplotlib`; dev: `pytest`.
- Importable module only; no command-line interface.

```
pyproject.toml
README.md                   # WP-D
src/montepi/__init__.py     # re-exports the public API
src/montepi/core.py         # WP-A
src/montepi/plot.py         # WP-C
tests/test_core.py          # WP-B
tests/test_plot.py          # WP-C
```

## Interface contract (frozen before parallel work starts)

All work packages code against these signatures only. Plain functions, no classes.

```python
# montepi/core.py
def sample_points(n, seed=None):
    """Return (x, y), two float arrays of length n, uniform in [0, 1).

    seed: int, np.random.Generator or None. ValueError if n < 1.
    """

def estimate_pi(x, y):
    """Return (pi_hat, std_error) from the sample coordinates x, y."""

def running_estimate(x, y):
    """Return an array of length n: pi_hat after the first k samples, k = 1..n."""

# montepi/plot.py  (each returns the Axes; creates a figure if ax is None)
def plot_samples(x, y, ax=None):
    """Scatter, inside/outside coloured, quarter-circle arc, equal aspect."""

def plot_convergence(running, ax=None):
    """pi_hat vs n on log-x, line at pi, band of +-2 sigma around pi."""
```

`estimate_pi` and `running_estimate` each contain the whole path from the
coordinates to $\hat\pi$; no helper functions in between.

## Work packages

| WP | Owner files | Depends on | Content |
|----|-------------|------------|---------|
| 0 Scaffold | `pyproject.toml`, `__init__.py`, stub `core.py`/`plot.py` raising `NotImplementedError` | — | Run first, sequentially. `uv sync` and `pytest` collect cleanly. |
| A Core | `core.py` | 0 | Vectorised NumPy implementation of the contract. No plotting imports. |
| B Core tests | `tests/test_core.py` | 0 | Written against the contract, not against A. |
| C Plotting | `plot.py`, `tests/test_plot.py` | 0 | Use synthetic inputs in tests, not `core`. Agg backend; tests check returned Axes, artist count, axis limits. |
| D Docs | `README.md` | 0 | Method with LaTeX equations, install, a short usage example. |

A, B, C and D touch disjoint files and can run in parallel.

### Tests for WP-B

- `sample_points`: two arrays of length $n$, values in $[0, 1)$, same seed gives same arrays, $n < 1$ raises.
- `estimate_pi` on hand-picked points: $(0, 0)$ and $(1, 0)$ count as inside (boundary included), $(1, 1)$ and $(0.8, 0.8)$ as outside.
- `estimate_pi` statistics: for $n = 10^6$ and a fixed seed, $|\hat\pi - \pi| < 5\sigma_{\hat\pi}$; $\sigma_{\hat\pi}$ shrinks by about $\sqrt{10}$ when $n$ grows tenfold.
- Symmetry: `estimate_pi(x, y) == estimate_pi(y, x)` and `running_estimate(x, y) == running_estimate(y, x)`.
- `running_estimate`: length $n$; last value equals `estimate_pi(x, y)[0]`; all values in $[0, 4]$.

## Integration (after A–D)

1. `uv run pytest` passes.
2. A short script calling `sample_points(10**6, seed=0)`, `estimate_pi` and both plot functions gives $|\hat\pi - \pi| < 0.01$ and a two-panel figure (samples, convergence).
3. Review `__init__.py` exports against the contract.

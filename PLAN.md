# Plan: `montepi` — estimate π by Monte Carlo

Sample `n` points uniformly in the unit square [0,1)². The fraction `p` that falls
inside the quarter circle x² + y² ≤ 1 estimates π/4, so π̂ = 4p with standard
error 4·√(p(1−p)/n).

## Layout and tooling

- `uv`, Python ≥ 3.11, src layout, deps: `numpy`; extra `plot`: `matplotlib`; dev: `pytest`.

```
pyproject.toml
README.md
src/montepi/__init__.py     # re-exports the public API
src/montepi/core.py         # WP-A
src/montepi/plot.py         # WP-C
src/montepi/__main__.py     # WP-D (CLI)
tests/test_core.py          # WP-B
tests/test_plot.py          # WP-C
```

## Interface contract (frozen before parallel work starts)

All work packages code against these signatures only.

```python
# montepi/core.py
@dataclass(frozen=True)
class PiEstimate:
    pi: float          # 4 * n_inside / n
    n: int
    n_inside: int
    std_error: float   # 4 * sqrt(p * (1 - p) / n)

def sample_points(n: int, seed: int | np.random.Generator | None = None) -> np.ndarray:
    """(n, 2) float array, uniform in [0, 1). ValueError if n < 1."""

def inside_circle(points: np.ndarray) -> np.ndarray:
    """(n,) bool array, True where x**2 + y**2 <= 1."""

def estimate_pi(n: int, seed: int | np.random.Generator | None = None) -> PiEstimate: ...

def running_estimate(inside: np.ndarray) -> np.ndarray:
    """(n,) float array, π̂ after the first k samples, k = 1..n."""

# montepi/plot.py  (each returns the Axes; creates a figure if ax is None)
def plot_samples(points: np.ndarray, inside: np.ndarray, ax=None) -> Axes:
    """Scatter, inside/outside coloured, quarter-circle arc, equal aspect."""

def plot_convergence(running: np.ndarray, ax=None) -> Axes:
    """π̂ vs n on log-x, line at π, ±2σ band from 4·sqrt(π/4·(1−π/4)/n)."""
```

## Work packages

| WP | Owner files | Depends on | Content |
|----|-------------|------------|---------|
| 0 Scaffold | `pyproject.toml`, `__init__.py`, stub `core.py`/`plot.py` raising `NotImplementedError` | — | Run first, sequentially. `uv sync` and `pytest` collect cleanly. |
| A Core | `core.py` | 0 | Vectorised NumPy implementation of the contract. No plotting imports. |
| B Core tests | `tests/test_core.py` | 0 | Written against the contract, not against A. |
| C Plotting | `plot.py`, `tests/test_plot.py` | 0 | Use synthetic inputs in tests, not `core`. Agg backend; tests check returned Axes, artist count, axis limits. |
| D CLI + docs | `__main__.py`, `README.md` | 0 | `python -m montepi -n 100000 --seed 0 [--plot out.png]` prints π̂ ± σ. README: method, install, usage. |

A, B, C and D touch disjoint files and can run in parallel.

### Tests for WP-B

- `sample_points`: shape (n, 2), values in [0, 1), same seed gives same array, `n < 1` raises.
- `inside_circle`: (0, 0) → True, (1, 0) → True (boundary), (1, 1) → False, (0.8, 0.8) → False.
- `estimate_pi`: `n_inside ≤ n`; `pi == 4 * n_inside / n`; for n = 10⁶ and a fixed seed, |π̂ − π| < 5·σ; σ shrinks about √10 when n grows 10×.
- `running_estimate`: length n; last value equals `estimate_pi(...).pi` on the same samples; all values in [0, 4].

## Integration (after A–D)

1. `uv run pytest` passes.
2. `uv run python -m montepi -n 1000000 --seed 0 --plot pi.png` gives π̂ within 0.01 of π and a two-panel figure (samples, convergence).
3. Review `__init__.py` exports against the contract.

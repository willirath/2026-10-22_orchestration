# montepi

montepi estimates pi by Monte Carlo sampling. It draws random points in the unit square and counts the fraction that falls inside the quarter circle. The package returns the estimate with its standard error, the running estimate as the sample grows, and two plots. It is an importable Python module with no command-line interface.

## Method

Sample $n$ points $(x_i, y_i)$ uniformly in the unit square $[0, 1)^2$. The fraction $p$ of points inside the quarter circle estimates $\pi/4$:

$$
p = \frac{1}{n} \sum_{i=1}^{n} \mathbf{1}\left[x_i^2 + y_i^2 \le 1\right],
\qquad
\hat\pi = 4p.
$$

The number of points inside is binomially distributed. The standard error of the estimate follows from the binomial variance:

$$
\sigma_{\hat\pi} = 4\sqrt{\frac{p(1-p)}{n}}.
$$

The error shrinks as $1/\sqrt{n}$. A tenfold larger sample cuts it by about $\sqrt{10}$.

## Install

montepi requires Python 3.11 or later. From the project root, install with [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

The plotting functions need matplotlib, which ships as the `plot` extra:

```sh
uv sync --extra plot
```

## Usage

```python
import matplotlib.pyplot as plt

from montepi import sample_points, estimate_pi, running_estimate
from montepi import plot

x, y = sample_points(10**6, seed=0)
pi_hat, std_error = estimate_pi(x, y)
print(f"{pi_hat:.4f} +/- {std_error:.4f}")

running = running_estimate(x, y)

fig, (ax_samples, ax_conv) = plt.subplots(1, 2, figsize=(10, 4))
plot.plot_samples(x[:2000], y[:2000], ax=ax_samples)
plot.plot_convergence(running, ax=ax_conv)
plt.show()
```

`sample_points` accepts an integer seed, a `numpy.random.Generator`, or `None`. `plot_samples` marks points inside and outside the quarter circle. `plot_convergence` draws $\hat\pi$ against $n$ with a band of $\pm 2\sigma$ around $\pi$.

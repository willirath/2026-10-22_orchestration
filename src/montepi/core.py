"""Core Monte Carlo estimation of pi."""


def sample_points(n, seed=None):
    """Return (x, y), two float arrays of length n, uniform in [0, 1).

    seed: int, np.random.Generator or None. ValueError if n < 1.
    """
    raise NotImplementedError


def estimate_pi(x, y):
    """Return (pi_hat, std_error) from the sample coordinates x, y."""
    raise NotImplementedError


def running_estimate(x, y):
    """Return an array of length n: pi_hat after the first k samples, k = 1..n."""
    raise NotImplementedError

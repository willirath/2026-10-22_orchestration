"""Tests for montepi.core, written against the interface contract in PLAN.md."""

import math

import numpy as np
import pytest

from montepi.core import estimate_pi, running_estimate, sample_points


# --- sample_points ---------------------------------------------------------


def test_sample_points_returns_two_arrays_of_length_n():
    x, y = sample_points(1000, seed=1)
    assert isinstance(x, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert x.shape == (1000,)
    assert y.shape == (1000,)
    assert np.issubdtype(x.dtype, np.floating)
    assert np.issubdtype(y.dtype, np.floating)


def test_sample_points_n_equals_one():
    x, y = sample_points(1, seed=1)
    assert len(x) == 1
    assert len(y) == 1


def test_sample_points_values_in_half_open_unit_interval():
    x, y = sample_points(100_000, seed=2)
    for a in (x, y):
        assert np.all(a >= 0.0)
        assert np.all(a < 1.0)


def test_sample_points_same_seed_gives_same_arrays():
    x1, y1 = sample_points(500, seed=42)
    x2, y2 = sample_points(500, seed=42)
    np.testing.assert_array_equal(x1, x2)
    np.testing.assert_array_equal(y1, y2)


def test_sample_points_different_seed_gives_different_arrays():
    x1, _ = sample_points(500, seed=1)
    x2, _ = sample_points(500, seed=2)
    assert not np.array_equal(x1, x2)


def test_sample_points_accepts_generator():
    x1, y1 = sample_points(500, seed=np.random.default_rng(7))
    x2, y2 = sample_points(500, seed=np.random.default_rng(7))
    np.testing.assert_array_equal(x1, x2)
    np.testing.assert_array_equal(y1, y2)


def test_sample_points_accepts_none_seed():
    x, y = sample_points(10, seed=None)
    assert len(x) == 10
    assert len(y) == 10


@pytest.mark.parametrize("n", [0, -1, -100])
def test_sample_points_n_below_one_raises(n):
    with pytest.raises(ValueError):
        sample_points(n)


# --- estimate_pi: hand-picked points ---------------------------------------


@pytest.mark.parametrize("point", [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
def test_estimate_pi_point_inside_including_boundary(point):
    x, y = (np.array([c]) for c in point)
    pi_hat, std_error = estimate_pi(x, y)
    assert pi_hat == pytest.approx(4.0)
    assert std_error == pytest.approx(0.0)


@pytest.mark.parametrize("point", [(1.0, 1.0), (0.8, 0.8)])
def test_estimate_pi_point_outside(point):
    x, y = (np.array([c]) for c in point)
    pi_hat, std_error = estimate_pi(x, y)
    assert pi_hat == pytest.approx(0.0)
    assert std_error == pytest.approx(0.0)


def test_estimate_pi_mixed_hand_picked_points():
    # Inside: (0, 0), (1, 0). Outside: (1, 1), (0.8, 0.8). So p = 1/2.
    x = np.array([0.0, 1.0, 1.0, 0.8])
    y = np.array([0.0, 0.0, 1.0, 0.8])
    pi_hat, std_error = estimate_pi(x, y)
    assert pi_hat == pytest.approx(2.0)
    assert std_error == pytest.approx(4.0 * math.sqrt(0.5 * 0.5 / 4))


# --- estimate_pi: statistics ------------------------------------------------


def test_estimate_pi_within_five_sigma_for_large_n():
    x, y = sample_points(10**6, seed=12345)
    pi_hat, std_error = estimate_pi(x, y)
    assert std_error > 0
    assert abs(pi_hat - math.pi) < 5 * std_error


def test_estimate_pi_std_error_matches_formula():
    x, y = sample_points(10**4, seed=3)
    pi_hat, std_error = estimate_pi(x, y)
    p = pi_hat / 4
    assert std_error == pytest.approx(4 * math.sqrt(p * (1 - p) / 10**4))


def test_estimate_pi_std_error_shrinks_by_sqrt_ten():
    x_small, y_small = sample_points(10**5, seed=11)
    x_large, y_large = sample_points(10**6, seed=12)
    _, sigma_small = estimate_pi(x_small, y_small)
    _, sigma_large = estimate_pi(x_large, y_large)
    assert sigma_small / sigma_large == pytest.approx(math.sqrt(10), rel=0.05)


# --- symmetry ---------------------------------------------------------------


def test_estimate_pi_symmetric_in_x_and_y():
    x, y = sample_points(10_000, seed=5)
    assert estimate_pi(x, y) == estimate_pi(y, x)


def test_running_estimate_symmetric_in_x_and_y():
    x, y = sample_points(10_000, seed=5)
    np.testing.assert_array_equal(running_estimate(x, y), running_estimate(y, x))


# --- running_estimate -------------------------------------------------------


def test_running_estimate_has_length_n():
    x, y = sample_points(2_000, seed=8)
    running = running_estimate(x, y)
    assert len(running) == 2_000


def test_running_estimate_last_value_equals_estimate_pi():
    x, y = sample_points(2_000, seed=8)
    running = running_estimate(x, y)
    assert running[-1] == pytest.approx(estimate_pi(x, y)[0])


def test_running_estimate_values_in_zero_to_four():
    x, y = sample_points(2_000, seed=8)
    running = running_estimate(x, y)
    assert np.all(running >= 0.0)
    assert np.all(running <= 4.0)


def test_running_estimate_on_hand_picked_points():
    # in, in, out, out -> 4 * [1/1, 2/2, 2/3, 2/4]
    x = np.array([0.0, 1.0, 1.0, 0.8])
    y = np.array([0.0, 0.0, 1.0, 0.8])
    np.testing.assert_allclose(
        running_estimate(x, y), [4.0, 4.0, 8.0 / 3.0, 2.0]
    )

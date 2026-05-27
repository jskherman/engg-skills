"""Time-series helpers for process data.

Includes pure-Python implementations of:
- Sample autocorrelation (ACF) and partial autocorrelation (PACF) via
  Durbin-Levinson recursion.
- Block-bootstrap resampling for autocorrelated series.
- Estimation of an appropriate block length (Politis-White 2004) as a
  screening helper, with a sensible default if the spectral estimate fails.
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable, Sequence


def autocorrelation(x: Sequence[float], max_lag: int) -> list[float]:
    """Sample ACF up to `max_lag` (lag 0 = 1.0)."""

    n = len(x)
    if max_lag < 0 or max_lag >= n:
        raise ValueError("max_lag must be in [0, n-1)")
    mean = sum(x) / n
    var = sum((xi - mean) ** 2 for xi in x) / n
    if var <= 0:
        raise ValueError("series has zero variance")
    acf = [1.0]
    for k in range(1, max_lag + 1):
        c = sum((x[i] - mean) * (x[i + k] - mean) for i in range(n - k)) / n
        acf.append(c / var)
    return acf


def partial_autocorrelation(x: Sequence[float], max_lag: int) -> list[float]:
    """Durbin-Levinson PACF up to `max_lag` (lag 0 = 1.0)."""

    acf = autocorrelation(x, max_lag)
    pacf = [1.0]
    phi: list[list[float]] = [[0.0] * (max_lag + 1) for _ in range(max_lag + 1)]
    for k in range(1, max_lag + 1):
        if k == 1:
            phi[1][1] = acf[1]
        else:
            num = acf[k] - sum(phi[k - 1][j] * acf[k - j] for j in range(1, k))
            den = 1 - sum(phi[k - 1][j] * acf[j] for j in range(1, k))
            if abs(den) < 1e-18:
                phi[k][k] = 0.0
            else:
                phi[k][k] = num / den
            for j in range(1, k):
                phi[k][j] = phi[k - 1][j] - phi[k][k] * phi[k - 1][k - j]
        pacf.append(phi[k][k])
    return pacf


def estimate_block_length(x: Sequence[float], c: float = 2.0) -> dict[str, Any]:
    """Heuristic block length: first lag k where |rho_k| < 2/sqrt(n).

    Returns the first lag at which the empirical ACF drops below the white-noise
    confidence band, multiplied by `c` for safety. Result is clipped to [2, n/4].
    """

    n = len(x)
    max_lag = min(40, n // 2 - 1)
    acf = autocorrelation(x, max_lag)
    threshold = 2.0 / math.sqrt(n)
    first_below = None
    for k in range(1, max_lag + 1):
        if abs(acf[k]) < threshold:
            first_below = k
            break
    base = first_below if first_below is not None else max_lag
    L = max(2, min(int(c * base), n // 4))
    return {"method": "ACF-threshold", "max_lag": max_lag, "first_below": first_below, "block_length": L}


def moving_block_bootstrap(
    x: Sequence[float],
    *,
    block_length: int,
    n_resamples: int,
    statistic: Callable[[list[float]], float],
    seed: int | None = None,
) -> dict[str, Any]:
    """Moving block bootstrap (Kuensch 1989) for autocorrelated series.

    Resamples blocks of length `block_length` with replacement to form pseudo
    series of the same length as the input, computes `statistic` for each, and
    returns mean, standard error, and 2.5%/97.5% percentile interval.
    """

    n = len(x)
    if block_length < 1 or block_length > n:
        raise ValueError("invalid block_length")
    rng = random.Random(seed)
    n_blocks = math.ceil(n / block_length)
    samples: list[float] = []
    for _ in range(n_resamples):
        pseudo: list[float] = []
        for _b in range(n_blocks):
            start = rng.randint(0, n - block_length)
            pseudo.extend(x[start : start + block_length])
        pseudo = pseudo[:n]
        samples.append(statistic(pseudo))
    samples_sorted = sorted(samples)
    lo = samples_sorted[max(0, int(0.025 * n_resamples) - 1)]
    hi = samples_sorted[min(n_resamples - 1, int(0.975 * n_resamples))]
    mean = sum(samples) / n_resamples
    var = sum((s - mean) ** 2 for s in samples) / max(1, n_resamples - 1)
    return {
        "method": "moving-block-bootstrap",
        "block_length": block_length,
        "n_resamples": n_resamples,
        "statistic_mean": mean,
        "statistic_se": math.sqrt(var),
        "ci_2p5": lo,
        "ci_97p5": hi,
    }

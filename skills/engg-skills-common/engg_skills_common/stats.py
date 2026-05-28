"""Engineering statistics helpers using the Python standard library."""

from __future__ import annotations

import math
import statistics
from statistics import NormalDist
from typing import Any


T_CRITICAL_975 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.160,
    14: 2.145,
    15: 2.131,
    16: 2.120,
    17: 2.110,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    21: 2.080,
    22: 2.074,
    23: 2.069,
    24: 2.064,
    25: 2.060,
    26: 2.056,
    27: 2.052,
    28: 2.048,
    29: 2.045,
    30: 2.042,
}


def describe(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("values cannot be empty")
    result: dict[str, float | int] = {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
    }
    if len(values) >= 2:
        result["sample_variance"] = statistics.variance(values)
        result["sample_stdev"] = statistics.stdev(values)
        result["population_stdev"] = statistics.pstdev(values)
    else:
        result["sample_variance"] = math.nan
        result["sample_stdev"] = math.nan
        result["population_stdev"] = 0.0
    return result


def mean_confidence_interval(values: list[float], confidence: float = 0.95) -> dict[str, Any]:
    if len(values) < 2:
        raise ValueError("at least two values are required")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    n = len(values)
    mean = statistics.fmean(values)
    stdev = statistics.stdev(values)
    standard_error = stdev / math.sqrt(n)
    warnings: list[str] = []
    if math.isclose(confidence, 0.95) and (n - 1) in T_CRITICAL_975:
        critical = T_CRITICAL_975[n - 1]
        method = "t-table-95-two-sided"
    else:
        alpha = 1.0 - confidence
        critical = NormalDist().inv_cdf(1.0 - alpha / 2.0)
        method = "normal-approximation"
        if n < 30:
            warnings.append("Normal approximation used for small sample confidence interval.")
    margin = critical * standard_error
    return {
        "count": n,
        "mean": mean,
        "sample_stdev": stdev,
        "standard_error": standard_error,
        "confidence": confidence,
        "critical_value": critical,
        "critical_method": method,
        "lower": mean - margin,
        "upper": mean + margin,
        "warnings": warnings,
    }


def linear_regression(x_values: list[float], y_values: list[float]) -> dict[str, float | int]:
    if len(x_values) != len(y_values):
        raise ValueError("x and y must have the same length")
    if len(x_values) < 2:
        raise ValueError("at least two paired values are required")
    x_mean = statistics.fmean(x_values)
    y_mean = statistics.fmean(y_values)
    sxx = sum((x - x_mean) ** 2 for x in x_values)
    if sxx == 0:
        raise ValueError("x values must not all be equal")
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    fitted = [intercept + slope * x for x in x_values]
    residuals = [y - y_hat for y, y_hat in zip(y_values, fitted)]
    sst = sum((y - y_mean) ** 2 for y in y_values)
    sse = sum(residual**2 for residual in residuals)
    r_squared = 1.0 - sse / sst if sst else 1.0
    return {
        "count": len(x_values),
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "sse": sse,
    }

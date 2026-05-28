"""Statistical process control helpers."""

from __future__ import annotations

import math
import statistics
from typing import Any


XBAR_R_CONSTANTS = {
    2: {"A2": 1.880, "D3": 0.000, "D4": 3.267},
    3: {"A2": 1.023, "D3": 0.000, "D4": 2.574},
    4: {"A2": 0.729, "D3": 0.000, "D4": 2.282},
    5: {"A2": 0.577, "D3": 0.000, "D4": 2.114},
    6: {"A2": 0.483, "D3": 0.000, "D4": 2.004},
    7: {"A2": 0.419, "D3": 0.076, "D4": 1.924},
    8: {"A2": 0.373, "D3": 0.136, "D4": 1.864},
    9: {"A2": 0.337, "D3": 0.184, "D4": 1.816},
    10: {"A2": 0.308, "D3": 0.223, "D4": 1.777},
}


def individuals_chart(values: list[float]) -> dict[str, Any]:
    if len(values) < 2:
        raise ValueError("at least two values are required")
    mean = statistics.fmean(values)
    moving_ranges = [abs(b - a) for a, b in zip(values, values[1:])]
    mrbar = statistics.fmean(moving_ranges)
    return {
        "count": len(values),
        "center_line": mean,
        "moving_range_average": mrbar,
        "individuals_lcl": mean - 2.66 * mrbar,
        "individuals_ucl": mean + 2.66 * mrbar,
        "moving_range_lcl": 0.0,
        "moving_range_ucl": 3.267 * mrbar,
        "moving_ranges": moving_ranges,
    }


def xbar_r_chart(subgroups: list[list[float]]) -> dict[str, Any]:
    if len(subgroups) < 2:
        raise ValueError("at least two subgroups are required")
    sizes = {len(group) for group in subgroups}
    if len(sizes) != 1:
        raise ValueError("all subgroups must have the same size")
    subgroup_size = sizes.pop()
    if subgroup_size not in XBAR_R_CONSTANTS:
        raise ValueError("xbar-r constants are included only for subgroup sizes 2 through 10")
    constants = XBAR_R_CONSTANTS[subgroup_size]
    xbars = [statistics.fmean(group) for group in subgroups]
    ranges = [max(group) - min(group) for group in subgroups]
    xbarbar = statistics.fmean(xbars)
    rbar = statistics.fmean(ranges)
    return {
        "subgroup_count": len(subgroups),
        "subgroup_size": subgroup_size,
        "xbarbar": xbarbar,
        "rbar": rbar,
        "xbar_lcl": xbarbar - constants["A2"] * rbar,
        "xbar_ucl": xbarbar + constants["A2"] * rbar,
        "r_lcl": constants["D3"] * rbar,
        "r_ucl": constants["D4"] * rbar,
        "constants": constants,
        "subgroup_means": xbars,
        "subgroup_ranges": ranges,
    }


def capability(values: list[float], *, lsl: float, usl: float) -> dict[str, float | int]:
    if len(values) < 2:
        raise ValueError("at least two values are required")
    if lsl >= usl:
        raise ValueError("lsl must be less than usl")
    mean = statistics.fmean(values)
    sigma = statistics.stdev(values)
    if sigma <= 0:
        raise ValueError("sample standard deviation must be positive")
    cp = (usl - lsl) / (6.0 * sigma)
    cpk = min((usl - mean) / (3.0 * sigma), (mean - lsl) / (3.0 * sigma))
    return {
        "count": len(values),
        "mean": mean,
        "sample_stdev": sigma,
        "lsl": lsl,
        "usl": usl,
        "cp": cp,
        "cpk": cpk,
        "estimated_nonconforming_fraction_normal": _normal_tail_fraction(mean, sigma, lsl, usl),
    }


def _normal_tail_fraction(mean: float, sigma: float, lsl: float, usl: float) -> float:
    def normal_cdf(x: float) -> float:
        return 0.5 * (1.0 + math.erf((x - mean) / (sigma * math.sqrt(2.0))))

    return normal_cdf(lsl) + (1.0 - normal_cdf(usl))

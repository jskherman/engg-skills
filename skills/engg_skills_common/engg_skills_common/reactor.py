"""Reactor sizing and kinetics helpers.

Covers:
- Arrhenius rate fitting (linear regression on ln k vs 1/T).
- Isothermal design equations for CSTR, PFR, and batch reactors.
- nth-order, reversible-first-order, and arbitrary user-supplied rate forms.

All flows are in mol/s and volumes in m^3 unless noted. Concentrations are
in mol/m^3. The math is dimensionally consistent with rate constants in
units that make `k * C^n` resolve to mol/(m^3 s).
"""

from __future__ import annotations

import math
from typing import Any, Callable

R_GAS = 8.314462618  # J/(mol K)


def arrhenius_fit(temperatures_K: list[float], rate_constants: list[float]) -> dict[str, Any]:
    """Linear regression of ln(k) vs 1/T to get pre-exponential A and Ea.

    Returns A (same units as k), Ea (J/mol), and R^2 of the fit. Requires at
    least three temperatures for a useful estimate.
    """

    if len(temperatures_K) != len(rate_constants):
        raise ValueError("temperature and rate vectors must align")
    if len(temperatures_K) < 2:
        raise ValueError("need at least two data points")
    xs = [1.0 / T for T in temperatures_K]
    ys = [math.log(k) for k in rate_constants]
    n = len(xs)
    xbar = sum(xs) / n
    ybar = sum(ys) / n
    sxx = sum((x - xbar) ** 2 for x in xs)
    sxy = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    syy = sum((y - ybar) ** 2 for y in ys)
    slope = sxy / sxx
    intercept = ybar - slope * xbar
    r2 = (sxy ** 2) / (sxx * syy) if sxx > 0 and syy > 0 else 1.0
    Ea = -slope * R_GAS
    A = math.exp(intercept)
    return {
        "method": "Arrhenius-linear-regression",
        "A_pre_exponential": A,
        "Ea_J_mol": Ea,
        "ln_A": intercept,
        "slope_-Ea_over_R": slope,
        "n_points": n,
        "r_squared": r2,
    }


def k_arrhenius(T_K: float, A: float, Ea_J_mol: float) -> float:
    return A * math.exp(-Ea_J_mol / (R_GAS * T_K))


def cstr_volume_nth_order(
    *,
    C0: float,
    conversion: float,
    flow_m3_s: float,
    k: float,
    order: float = 1.0,
) -> dict[str, Any]:
    """Isothermal liquid-phase CSTR volume for a single nth-order reaction.

    Design equation: V = F0 X / (-r_A) with F0 = C0 Q, -r_A = k C^n at outlet.
    `order` may be any non-negative real.
    """

    if not (0 < conversion < 1):
        raise ValueError("conversion must be in (0, 1)")
    if C0 <= 0 or flow_m3_s <= 0 or k <= 0:
        raise ValueError("C0, flow, k must be positive")
    C = C0 * (1 - conversion)
    r = k * C ** order
    if r <= 0:
        raise RuntimeError("computed rate <= 0; check inputs")
    tau = conversion * C0 / r
    return {
        "method": "CSTR-nth-order",
        "order": order,
        "C0_mol_m3": C0,
        "C_out_mol_m3": C,
        "conversion": conversion,
        "k": k,
        "tau_residence_s": tau,
        "volume_m3": tau * flow_m3_s,
        "flow_m3_s": flow_m3_s,
    }


def pfr_volume_nth_order(
    *,
    C0: float,
    conversion: float,
    flow_m3_s: float,
    k: float,
    order: float = 1.0,
) -> dict[str, Any]:
    """Isothermal liquid-phase PFR volume for a single nth-order reaction."""

    if not (0 < conversion < 1):
        raise ValueError("conversion must be in (0, 1)")
    if C0 <= 0 or flow_m3_s <= 0 or k <= 0:
        raise ValueError("C0, flow, k must be positive")
    if abs(order - 1.0) < 1e-9:
        tau = -math.log(1 - conversion) / k
    elif abs(order - 0.0) < 1e-9:
        tau = conversion * C0 / k
    else:
        tau = (C0 ** (1 - order)) * (1 - (1 - conversion) ** (1 - order)) / (k * (1 - order))
    return {
        "method": "PFR-nth-order-analytical",
        "order": order,
        "C0_mol_m3": C0,
        "C_out_mol_m3": C0 * (1 - conversion),
        "conversion": conversion,
        "k": k,
        "tau_residence_s": tau,
        "volume_m3": tau * flow_m3_s,
        "flow_m3_s": flow_m3_s,
    }


def batch_time_nth_order(
    *,
    C0: float,
    conversion: float,
    k: float,
    order: float = 1.0,
) -> dict[str, Any]:
    """Isothermal constant-volume batch time for an nth-order reaction.

    For order=1: t = -ln(1-X)/k. For order=0: t = X C0 / k.
    For other order n != 1: t = (C0^(1-n) - C^(1-n)) / (k(n-1)).
    """

    if not (0 < conversion < 1):
        raise ValueError("conversion must be in (0, 1)")
    if C0 <= 0 or k <= 0:
        raise ValueError("C0 and k must be positive")
    if abs(order - 1.0) < 1e-9:
        t = -math.log(1 - conversion) / k
    elif abs(order - 0.0) < 1e-9:
        t = conversion * C0 / k
    else:
        C = C0 * (1 - conversion)
        t = (C ** (1 - order) - C0 ** (1 - order)) / (k * (order - 1))
    return {
        "method": "Batch-nth-order-analytical",
        "order": order,
        "C0_mol_m3": C0,
        "conversion": conversion,
        "k": k,
        "time_s": t,
    }


def cstr_in_series(
    *,
    C0: float,
    overall_conversion: float,
    flow_m3_s: float,
    k: float,
    N: int,
) -> dict[str, Any]:
    """N equal-sized CSTRs in series for first-order isothermal reaction.

    Returns per-vessel residence time and total volume.
    """

    if N < 1 or not (0 < overall_conversion < 1) or k <= 0:
        raise ValueError("require N >= 1, 0 < X < 1, k > 0")
    # For 1st order, C_N/C0 = (1+k tau)^-N -> per-vessel tau
    ratio = (1 - overall_conversion)
    tau_each = ((ratio ** (-1.0 / N)) - 1) / k
    return {
        "method": "CSTR-in-series-first-order",
        "N": N,
        "tau_each_s": tau_each,
        "total_tau_s": N * tau_each,
        "volume_each_m3": tau_each * flow_m3_s,
        "total_volume_m3": N * tau_each * flow_m3_s,
    }


def pfr_numeric(
    *,
    C0: float,
    target_conversion: float,
    rate_per_unit_volume: Callable[[float], float],
    flow_m3_s: float,
    max_tau_s: float = 1e6,
    steps: int = 10_000,
) -> dict[str, Any]:
    """Trapezoidal integration of dV = -F0 dX / r(C).

    `rate_per_unit_volume(C)` returns mol/(m^3 s) given concentration C (mol/m^3).
    Use for any non-standard rate law (Langmuir-Hinshelwood, Michaelis-Menten,
    reversible reactions, etc.).
    """

    if not (0 < target_conversion < 1):
        raise ValueError("conversion must be in (0, 1)")
    F0 = C0 * flow_m3_s
    dX = target_conversion / steps
    X = 0.0
    V = 0.0
    for _ in range(steps):
        C_mid = C0 * (1 - X - 0.5 * dX)
        r = rate_per_unit_volume(C_mid)
        if r <= 0:
            raise RuntimeError("non-positive rate encountered during integration")
        V += F0 * dX / r
        X += dX
        if V > flow_m3_s * max_tau_s:
            raise RuntimeError("integration exceeded max_tau_s")
    return {
        "method": "PFR-trapezoidal-numeric",
        "volume_m3": V,
        "tau_residence_s": V / flow_m3_s,
        "conversion": X,
        "C_out_mol_m3": C0 * (1 - X),
    }

"""Distillation, absorption, and stripping shortcut helpers.

Pure-Python implementations of textbook shortcut methods:

- Fenske: minimum number of equilibrium stages for binary or pseudo-binary cuts.
- Underwood: minimum reflux ratio for multicomponent systems.
- Gilliland: actual stages from N/Nmin vs R/Rmin correlation (Molokanov form).
- Kremser: absorption/stripping factor method for dilute systems.
- McCabe-Thiele: stage stepping for binary VLE on a constant relative volatility curve.

These are screening methods. They do NOT replace rigorous tray-by-tray
simulation (Lewis, Naphtali-Sandholm, or inside-out) for final design.
"""

from __future__ import annotations

import math
from typing import Any


def fenske_min_stages(*, alpha: float, xD: float, xB: float, light_key_recovery: float | None = None) -> dict[str, Any]:
    """Fenske minimum equilibrium stages for a binary or pseudo-binary cut.

    `alpha` is relative volatility (light/heavy), constant across the column.
    `xD` and `xB` are mole fractions of the light key in distillate and bottoms.
    For multicomponent cuts, supply pseudo-binary mole fractions or use the
    component-recovery form via `light_key_recovery` (fraction of LK in distillate).
    """

    if alpha <= 1:
        raise ValueError("relative volatility must be > 1 for separation")
    if not (0 < xB < xD < 1):
        raise ValueError("require 0 < xB < xD < 1")
    Nmin = math.log((xD / (1 - xD)) * ((1 - xB) / xB)) / math.log(alpha)
    out: dict[str, Any] = {
        "method": "Fenske",
        "alpha_avg": alpha,
        "xD": xD,
        "xB": xB,
        "N_min_stages_including_reboiler": Nmin,
    }
    if light_key_recovery is not None:
        if not (0 < light_key_recovery < 1):
            raise ValueError("recovery must be between 0 and 1")
        out["lk_recovery"] = light_key_recovery
    return out


def underwood_min_reflux(
    *,
    alphas: list[float],
    feed_zs: list[float],
    distillate_xs: list[float],
    q: float = 1.0,
) -> dict[str, Any]:
    """Underwood minimum reflux for a multicomponent column.

    `alphas` are component relative volatilities relative to the heaviest key.
    `q` is the thermal condition of the feed (q=1 saturated liquid, q=0 sat vapor).
    The Underwood theta is bracketed between consecutive alphas; the function
    bisects on the first interval containing a root and computes Rmin from the
    accepted theta.
    """

    if not (len(alphas) == len(feed_zs) == len(distillate_xs)):
        raise ValueError("alphas, feed_zs, distillate_xs must align")
    if abs(sum(feed_zs) - 1) > 1e-6 or abs(sum(distillate_xs) - 1) > 1e-6:
        raise ValueError("compositions must sum to 1")

    def g(theta: float) -> float:
        return sum(a * z / (a - theta) for a, z in zip(alphas, feed_zs)) - (1 - q)

    pairs = sorted(set(alphas))
    theta = None
    for i in range(len(pairs) - 1):
        lo = pairs[i] + 1e-6
        hi = pairs[i + 1] - 1e-6
        if lo >= hi:
            continue
        try:
            f_lo, f_hi = g(lo), g(hi)
        except ZeroDivisionError:
            continue
        if f_lo * f_hi > 0:
            continue
        a, b = lo, hi
        for _ in range(200):
            m = 0.5 * (a + b)
            fm = g(m)
            if abs(fm) < 1e-9 or (b - a) < 1e-12:
                break
            if f_lo * fm < 0:
                b = m
            else:
                a, f_lo = m, fm
        theta = 0.5 * (a + b)
        break
    if theta is None:
        raise RuntimeError("Underwood theta not bracketed; check alpha ordering / feed quality.")
    Rmin_plus_1 = sum(a * xD / (a - theta) for a, xD in zip(alphas, distillate_xs))
    Rmin = Rmin_plus_1 - 1
    return {
        "method": "Underwood",
        "theta": theta,
        "Rmin": Rmin,
        "q": q,
        "alphas": list(alphas),
    }


def gilliland_stages(*, Nmin: float, Rmin: float, R: float) -> dict[str, Any]:
    """Gilliland correlation (Molokanov form) for actual stages."""

    if R <= Rmin:
        raise ValueError("operating reflux must exceed Rmin")
    X = (R - Rmin) / (R + 1)
    Y = 1 - math.exp((1 + 54.4 * X) / (11 + 117.2 * X) * (X - 1) / math.sqrt(X))
    N = (Nmin + Y) / (1 - Y)
    return {
        "method": "Gilliland-Molokanov",
        "Nmin": Nmin,
        "Rmin": Rmin,
        "R": R,
        "X": X,
        "Y": Y,
        "N_stages_including_reboiler": N,
    }


def kremser(*, N: float, A: float, x_in: float, y_in: float, K: float) -> dict[str, Any]:
    """Kremser equation for absorption/stripping factor method.

    `A` is the absorption factor L/(K*V). For A != 1 the closed form applies;
    for A ~ 1 a limiting form is used.
    `x_in` is solvent inlet liquid composition (lean solvent), `y_in` is gas
    feed composition entering. Returns predicted lean-gas exit composition `y_out`.
    """

    if N <= 0 or K <= 0:
        raise ValueError("N and K must be positive")
    if abs(A - 1) < 1e-6:
        eta = N / (N + 1)
    else:
        eta = (A ** (N + 1) - A) / (A ** (N + 1) - 1)
    x_eq = y_in / K
    y_out = y_in - eta * (y_in - K * x_in)
    return {
        "method": "Kremser",
        "N_stages": N,
        "absorption_factor_A": A,
        "fractional_absorption_eta": eta,
        "x_in_solvent": x_in,
        "y_in_gas": y_in,
        "K_distribution_coefficient": K,
        "y_out_gas": y_out,
        "x_eq_with_inlet_gas": x_eq,
    }


def mccabe_thiele_stages(
    *,
    alpha: float,
    xD: float,
    xB: float,
    xF: float,
    q: float,
    R: float,
) -> dict[str, Any]:
    """Step off McCabe-Thiele stages for a binary column with constant alpha.

    Returns the integer number of equilibrium stages required to span (xD, xB)
    and the feed-stage index (counted from the top, including the partial
    reboiler as the last stage). Operating lines and the q-line are linear in
    (x, y); the stair-stepping uses the constant-alpha equilibrium relation.
    """

    if alpha <= 1:
        raise ValueError("alpha must be > 1")
    if not (0 < xB < xF < xD < 1):
        raise ValueError("require 0 < xB < xF < xD < 1")
    if R <= 0:
        raise ValueError("reflux ratio must be positive")
    # Rectifying line y = R/(R+1) x + xD/(R+1)
    m_r = R / (R + 1)
    b_r = xD / (R + 1)
    # q-line intersection with rectifying line gives feed-stage transition
    if abs(q - 1) < 1e-6:
        x_int = xF
        y_int = m_r * x_int + b_r
    else:
        # q-line: y = q/(q-1) x - xF/(q-1)
        m_q = q / (q - 1)
        b_q = -xF / (q - 1)
        # intersect with rectifying line
        x_int = (b_r - b_q) / (m_q - m_r)
        y_int = m_r * x_int + b_r
    # Stripping line passes through (xB, xB) and (x_int, y_int)
    if abs(x_int - xB) < 1e-9:
        raise RuntimeError("Operating lines degenerate; adjust R or q.")
    m_s = (y_int - xB) / (x_int - xB)
    b_s = xB - m_s * xB

    def y_eq_from_x(x: float) -> float:
        return alpha * x / (1 + (alpha - 1) * x)

    def x_eq_from_y(y: float) -> float:
        return y / (alpha - (alpha - 1) * y)

    stages = 0
    feed_stage = None
    x = xD
    y = xD
    on_rectifying = True
    while x > xB and stages < 200:
        stages += 1
        x = x_eq_from_y(y)
        if x <= xB:
            break
        if on_rectifying and x <= x_int:
            on_rectifying = False
            feed_stage = stages
        y = (m_r * x + b_r) if on_rectifying else (m_s * x + b_s)
    return {
        "method": "McCabe-Thiele",
        "alpha": alpha,
        "xD": xD,
        "xB": xB,
        "xF": xF,
        "q": q,
        "R": R,
        "operating_intersection": {"x": x_int, "y": y_int},
        "stages_including_reboiler": stages,
        "feed_stage_from_top": feed_stage,
    }

"""Compositional Data Analysis (CoDA) helpers.

Implements the log-ratio transforms (alr, clr, ilr) and sequential binary
partition (SBP)-based ilr balances directly. No third-party dependency on
`scikit-bio` or `python-coda` to keep the shared library lightweight; the
math is short and well-defined in Pawlowsky-Glahn et al. (Lecture Notes on
Compositional Data Analysis, 2007) and Egozcue & Pawlowsky-Glahn (Math
Geosci, 2005).

Conventions:
- Compositions are mole or mass fractions, strictly positive.
- Zeros must be replaced (multiplicative replacement or
  geometric-mean imputation) before any log-ratio transform.
"""

from __future__ import annotations

import math
from typing import Any, Sequence


def _validate_composition(x: Sequence[float]) -> list[float]:
    if not x:
        raise ValueError("composition cannot be empty")
    if any(xi <= 0 for xi in x):
        raise ValueError("composition components must be strictly positive (replace zeros first)")
    s = sum(x)
    if s <= 0:
        raise ValueError("composition must sum to > 0")
    return [xi / s for xi in x]


def geometric_mean(x: Sequence[float]) -> float:
    if not x:
        raise ValueError("empty sequence")
    if any(xi <= 0 for xi in x):
        raise ValueError("geometric mean requires positive values")
    return math.exp(sum(math.log(xi) for xi in x) / len(x))


def clr(x: Sequence[float]) -> list[float]:
    """Centered log-ratio transform."""

    x = _validate_composition(x)
    g = geometric_mean(x)
    return [math.log(xi / g) for xi in x]


def alr(x: Sequence[float], denominator_index: int = -1) -> list[float]:
    """Additive log-ratio transform, removing one component as denominator."""

    x = _validate_composition(x)
    denom_i = denominator_index % len(x)
    denom = x[denom_i]
    return [math.log(xi / denom) for i, xi in enumerate(x) if i != denom_i]


def multiplicative_replacement(x: Sequence[float], delta: float = 1e-6) -> list[float]:
    """Replace zeros with `delta` and rescale so the composition sums to 1.

    `delta` is the replacement fraction assigned to each zero component in the
    closed composition. Non-zero parts are scaled by `(1 - m*delta)` after the
    original composition is closed over its positive parts.
    """

    if not x:
        raise ValueError("composition cannot be empty")
    if delta <= 0:
        raise ValueError("delta must be positive")
    if any(v < 0 for v in x):
        raise ValueError("composition values cannot be negative")
    zeros = [i for i, v in enumerate(x) if v == 0]
    if not zeros:
        return list(_validate_composition(x))
    nz = len(zeros)
    if nz == len(x):
        raise ValueError("cannot replace an all-zero composition")
    if nz * delta >= 1:
        raise ValueError("delta is too large for the number of zero components")
    s_obs = sum(x)
    if s_obs <= 0:
        raise ValueError("positive composition sum required")
    factor = (1 - nz * delta) / s_obs
    return [delta if i in zeros else v * factor for i, v in enumerate(x)]


def sbp_to_psi(sbp: list[list[int]]) -> list[list[float]]:
    """Convert a sequential binary partition matrix into an ilr contrast matrix Psi.

    Each row of `sbp` is a partition: +1 for components in the numerator group,
    -1 for components in the denominator group, 0 for unused components.
    The function normalizes each row to satisfy the ilr orthonormality.

    Returns Psi of shape (D-1) x D.
    """

    if not sbp:
        raise ValueError("SBP must have at least one row")
    D = len(sbp[0])
    if D < 2:
        raise ValueError("need at least 2 components")
    psi: list[list[float]] = []
    for row in sbp:
        if len(row) != D:
            raise ValueError("all SBP rows must have the same length D")
        r = sum(1 for v in row if v > 0)
        s = sum(1 for v in row if v < 0)
        if r == 0 or s == 0:
            raise ValueError("each balance must have both a numerator and denominator group")
        a = math.sqrt(s / (r * (r + s)))
        b = math.sqrt(r / (s * (r + s)))
        psi.append([a if v > 0 else (-b if v < 0 else 0.0) for v in row])
    return psi


def ilr(x: Sequence[float], sbp: list[list[int]] | None = None) -> list[float]:
    """Isometric log-ratio with optional SBP. If sbp is None, uses default Helmert basis."""

    x = _validate_composition(x)
    D = len(x)
    if sbp is None:
        # Helmert-style default basis (Egozcue & Pawlowsky-Glahn 2003).
        sbp = []
        for i in range(D - 1):
            row = [0] * D
            for j in range(i + 1):
                row[j] = 1
            row[i + 1] = -1
            sbp.append(row)
    psi = sbp_to_psi(sbp)
    if any(len(row) != D for row in sbp):
        raise ValueError("SBP column count must match composition length")
    log_x = [math.log(xi) for xi in x]
    # Each balance: y_k = sum_j psi_kj * log(x_j)
    return [sum(psi_row[j] * log_x[j] for j in range(D)) for psi_row in psi]


def heavy_end_balance(
    composition: dict[str, float],
    heavy_components: list[str],
    body_components: list[str],
) -> dict[str, Any]:
    """Construct a 'heavy-end vs body' ilr balance for a single sample.

    Mirrors the LPG sulfur analysis example: H = {C5*, C6+}, B = {C3, C4}.
    Components present in `composition` but not in either group are ignored
    for this balance. Components specified but absent in the composition
    are treated as zeros and replaced via multiplicative_replacement.
    """

    if not heavy_components or not body_components:
        raise ValueError("heavy_components and body_components must both be non-empty")
    all_named = heavy_components + body_components
    raw = [composition.get(name, 0.0) for name in all_named]
    cleaned = multiplicative_replacement(raw)
    heavy_vals = cleaned[: len(heavy_components)]
    body_vals = cleaned[len(heavy_components) :]
    g_heavy = geometric_mean(heavy_vals)
    g_body = geometric_mean(body_vals)
    r = len(heavy_components)
    s = len(body_components)
    coef = math.sqrt((r * s) / (r + s))
    z_H = coef * math.log(g_heavy / g_body)
    return {
        "method": "ilr-balance-heavy-vs-body",
        "heavy_components": heavy_components,
        "body_components": body_components,
        "g_heavy": g_heavy,
        "g_body": g_body,
        "z_H": z_H,
        "interpretation": (
            "z_H > 0 indicates the sample is enriched in the heavy group relative "
            "to the body group, on a log-ratio scale."
        ),
    }

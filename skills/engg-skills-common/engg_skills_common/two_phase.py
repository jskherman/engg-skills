"""Two-phase (gas-liquid) pressure drop helpers.

Wrappers around `fluids.two_phase` with consistent SI inputs and graceful
error reporting when the library is missing. Includes the three correlations
the user is most likely to want: Lockhart-Martinelli, Beggs-Brill, and
Muller-Steinhagen-Heck.
"""

from __future__ import annotations

from typing import Any

from .property_backends import _require_library


def _validate_common_two_phase_inputs(
    *,
    m_total_kg_s: float,
    quality: float,
    rho_l: float,
    rho_g: float,
    mu_l: float,
    mu_g: float,
    D_m: float,
    L_m: float,
) -> None:
    if m_total_kg_s <= 0:
        raise ValueError("m_total_kg_s must be positive")
    if not (0 <= quality <= 1):
        raise ValueError("quality must be between 0 and 1")
    if rho_l <= 0 or rho_g <= 0 or mu_l <= 0 or mu_g <= 0:
        raise ValueError("densities and viscosities must be positive")
    if D_m <= 0 or L_m <= 0:
        raise ValueError("D_m and L_m must be positive")


def lockhart_martinelli(
    *,
    m_total_kg_s: float,
    quality: float,
    rho_l: float,
    rho_g: float,
    mu_l: float,
    mu_g: float,
    D_m: float,
    L_m: float = 1.0,
) -> dict[str, Any]:
    """Lockhart-Martinelli horizontal two-phase pressure drop."""

    _validate_common_two_phase_inputs(
        m_total_kg_s=m_total_kg_s,
        quality=quality,
        rho_l=rho_l,
        rho_g=rho_g,
        mu_l=mu_l,
        mu_g=mu_g,
        D_m=D_m,
        L_m=L_m,
    )
    tp = _require_library("fluids.two_phase", "fluids")
    dP = tp.Lockhart_Martinelli(
        m=m_total_kg_s, x=quality, rhol=rho_l, rhog=rho_g, mul=mu_l, mug=mu_g, D=D_m, L=L_m
    )
    return {
        "method": "fluids.two_phase.Lockhart_Martinelli",
        "delta_P_Pa": dP,
        "delta_P_per_m_Pa_m": dP / L_m,
        "quality": quality,
        "m_total_kg_s": m_total_kg_s,
        "D_m": D_m,
        "L_m": L_m,
    }


def beggs_brill(
    *,
    m_total_kg_s: float,
    quality: float,
    rho_l: float,
    rho_g: float,
    mu_l: float,
    mu_g: float,
    sigma_N_m: float,
    P_Pa: float,
    D_m: float,
    angle_deg: float = 0.0,
    roughness_m: float = 0.0,
    L_m: float = 1.0,
    include_acceleration: bool = True,
) -> dict[str, Any]:
    """Beggs-Brill two-phase pressure drop (handles inclination)."""

    _validate_common_two_phase_inputs(
        m_total_kg_s=m_total_kg_s,
        quality=quality,
        rho_l=rho_l,
        rho_g=rho_g,
        mu_l=mu_l,
        mu_g=mu_g,
        D_m=D_m,
        L_m=L_m,
    )
    if sigma_N_m <= 0 or P_Pa <= 0:
        raise ValueError("sigma_N_m and P_Pa must be positive")
    if roughness_m < 0:
        raise ValueError("roughness_m cannot be negative")
    tp = _require_library("fluids.two_phase", "fluids")
    dP = tp.Beggs_Brill(
        m=m_total_kg_s,
        x=quality,
        rhol=rho_l,
        rhog=rho_g,
        mul=mu_l,
        mug=mu_g,
        sigma=sigma_N_m,
        P=P_Pa,
        D=D_m,
        angle=angle_deg,
        roughness=roughness_m,
        L=L_m,
        acceleration=include_acceleration,
    )
    return {
        "method": "fluids.two_phase.Beggs_Brill",
        "delta_P_Pa": dP,
        "delta_P_per_m_Pa_m": dP / L_m,
        "quality": quality,
        "angle_deg": angle_deg,
        "L_m": L_m,
    }


def mueller_steinhagen_heck(
    *,
    m_total_kg_s: float,
    quality: float,
    rho_l: float,
    rho_g: float,
    mu_l: float,
    mu_g: float,
    D_m: float,
    roughness_m: float = 0.0,
    L_m: float = 1.0,
) -> dict[str, Any]:
    """Muller-Steinhagen-Heck two-phase pressure drop (smooth quality interpolation)."""

    _validate_common_two_phase_inputs(
        m_total_kg_s=m_total_kg_s,
        quality=quality,
        rho_l=rho_l,
        rho_g=rho_g,
        mu_l=mu_l,
        mu_g=mu_g,
        D_m=D_m,
        L_m=L_m,
    )
    if roughness_m < 0:
        raise ValueError("roughness_m cannot be negative")
    tp = _require_library("fluids.two_phase", "fluids")
    dP = tp.Muller_Steinhagen_Heck(
        m=m_total_kg_s, x=quality, rhol=rho_l, rhog=rho_g, mul=mu_l, mug=mu_g, D=D_m, roughness=roughness_m, L=L_m
    )
    return {
        "method": "fluids.two_phase.Muller_Steinhagen_Heck",
        "delta_P_Pa": dP,
        "delta_P_per_m_Pa_m": dP / L_m,
        "quality": quality,
        "L_m": L_m,
    }

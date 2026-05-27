"""Two-phase (gas-liquid) pressure drop helpers.

Wrappers around `fluids.two_phase` with consistent SI inputs and graceful
error reporting when the library is missing. Includes the three correlations
the user is most likely to want: Lockhart-Martinelli, Beggs-Brill, and
Mueller-Steinhagen-Heck.
"""

from __future__ import annotations

from typing import Any

from .property_backends import _require_library


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
    """Mueller-Steinhagen-Heck two-phase pressure drop (smooth quality interpolation)."""

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

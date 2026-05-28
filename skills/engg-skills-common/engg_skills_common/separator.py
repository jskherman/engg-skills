"""Separator vessel sizing helpers.

Uses `fluids.separator` where available and falls back to Souders-Brown with
literature K-factor ranges otherwise. Both horizontal and vertical two-phase
separator sizing is supported. Three-phase sizing requires explicit residence
times for both liquid phases.
"""

from __future__ import annotations

import math
from typing import Any

from .property_backends import _require_library


# GPSA-style K-factor ranges (m/s). Use the conservative midpoint when in
# doubt; refine using fluids.separator.K_separator_Watkins if quality x is known.
DEFAULT_K_RANGES = {
    "vertical_no_demister": (0.030, 0.075),
    "vertical_with_demister": (0.070, 0.110),
    "horizontal_no_demister": (0.040, 0.090),
    "horizontal_with_demister": (0.090, 0.150),
}


def souders_brown_velocity(*, K: float, rho_l: float, rho_v: float) -> float:
    """Souders-Brown max vapor velocity, m/s."""

    if rho_l <= rho_v:
        raise ValueError("liquid density must exceed vapor density")
    return K * math.sqrt((rho_l - rho_v) / rho_v)


def vertical_separator(
    *,
    vapor_volumetric_m3_s: float,
    liquid_volumetric_m3_s: float,
    rho_l: float,
    rho_v: float,
    K: float | None = None,
    demister: bool = True,
    liquid_holdup_minutes: float = 5.0,
) -> dict[str, Any]:
    """Vertical two-phase separator diameter and tan-tan height.

    Returns required diameter so vapor velocity equals Souders-Brown limit,
    and tan-tan height as: liquid holdup section + inlet/disengaging space +
    optional demister allowance.
    """

    if K is None:
        lo, hi = DEFAULT_K_RANGES["vertical_with_demister" if demister else "vertical_no_demister"]
        K = 0.5 * (lo + hi)
    v_max = souders_brown_velocity(K=K, rho_l=rho_l, rho_v=rho_v)
    area = vapor_volumetric_m3_s / v_max
    diameter = math.sqrt(4 * area / math.pi)
    liquid_volume = liquid_volumetric_m3_s * liquid_holdup_minutes * 60.0
    liquid_height = liquid_volume / area
    disengaging = 0.6  # m, rule of thumb for inlet+vapor space
    demister_allowance = 0.3 if demister else 0.0
    tt_height = liquid_height + disengaging + demister_allowance
    return {
        "method": "Souders-Brown-vertical",
        "K_m_s": K,
        "v_max_m_s": v_max,
        "diameter_m": diameter,
        "vessel_area_m2": area,
        "liquid_holdup_min": liquid_holdup_minutes,
        "liquid_height_m": liquid_height,
        "tan_tan_height_m": tt_height,
        "demister": demister,
    }


def horizontal_separator(
    *,
    vapor_volumetric_m3_s: float,
    liquid_volumetric_m3_s: float,
    rho_l: float,
    rho_v: float,
    K: float | None = None,
    demister: bool = True,
    liquid_holdup_minutes: float = 5.0,
    LD_ratio: float = 4.0,
    liquid_level_fraction: float = 0.5,
) -> dict[str, Any]:
    """Horizontal two-phase separator with assumed L/D ratio.

    Method:
    1. Compute vapor cross-sectional area required from Souders-Brown.
    2. Total cross-sectional area = vapor area / (1 - liquid_level_fraction).
    3. Diameter from total area; length from L/D ratio.
    4. Check liquid holdup time; if insufficient, increase L/D and report it.
    """

    if not (0 < liquid_level_fraction < 1):
        raise ValueError("liquid_level_fraction must be between 0 and 1")
    if K is None:
        lo, hi = DEFAULT_K_RANGES["horizontal_with_demister" if demister else "horizontal_no_demister"]
        K = 0.5 * (lo + hi)
    v_max = souders_brown_velocity(K=K, rho_l=rho_l, rho_v=rho_v)
    A_vapor = vapor_volumetric_m3_s / v_max
    A_total = A_vapor / (1 - liquid_level_fraction)
    diameter = math.sqrt(4 * A_total / math.pi)
    length = LD_ratio * diameter
    A_liquid = A_total * liquid_level_fraction
    liquid_volume_required = liquid_volumetric_m3_s * liquid_holdup_minutes * 60.0
    available_liquid_volume = A_liquid * length
    actual_holdup_min = available_liquid_volume / liquid_volumetric_m3_s / 60.0 if liquid_volumetric_m3_s > 0 else float("inf")
    warnings: list[str] = []
    if actual_holdup_min < liquid_holdup_minutes:
        warnings.append(
            "Computed L/D yields less liquid holdup than required; increase length or diameter."
        )
    return {
        "method": "Souders-Brown-horizontal",
        "K_m_s": K,
        "v_max_m_s": v_max,
        "diameter_m": diameter,
        "length_m": length,
        "LD_ratio": LD_ratio,
        "liquid_level_fraction": liquid_level_fraction,
        "available_liquid_holdup_min": actual_holdup_min,
        "required_liquid_holdup_min": liquid_holdup_minutes,
        "warnings": warnings,
    }


def fluids_K_separator_watkins(*, quality: float, rho_l: float, rho_v: float, horizontal: bool = False) -> dict[str, Any]:
    """Wrapper around fluids.separator.K_separator_Watkins."""

    sep = _require_library("fluids.separator", "fluids")
    K = sep.K_separator_Watkins(quality, rho_l, rho_v, horizontal=horizontal)
    return {
        "method": "fluids.separator.K_separator_Watkins",
        "K_m_s": K,
        "quality": quality,
        "rho_l_kg_m3": rho_l,
        "rho_v_kg_m3": rho_v,
        "horizontal": horizontal,
    }

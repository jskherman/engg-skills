"""Control and relief valve sizing helpers.

Control valve sizing uses `fluids.control_valve` (ISA 75.01.01 / IEC 60534
equations). Relief sizing implements API 520 8th-edition style equations for
gas/vapor and liquid service as preliminary screening; final relief sizing
must follow the published standard text and qualified relief engineering.
"""

from __future__ import annotations

import math
from typing import Any

from .property_backends import _require_library


def liquid_control_valve(
    *,
    rho_l_kg_m3: float,
    P1_Pa: float,
    P2_Pa: float,
    Q_m3_s: float,
    mu_Pa_s: float = 1e-3,
    Psat_Pa: float = 0.0,
    Pc_Pa: float = 2.2e7,
) -> dict[str, Any]:
    """Liquid control valve Kv via fluids.control_valve.size_control_valve_l."""

    cv = _require_library("fluids.control_valve", "fluids")
    Kv = cv.size_control_valve_l(rho=rho_l_kg_m3, Psat=Psat_Pa, Pc=Pc_Pa, mu=mu_Pa_s, P1=P1_Pa, P2=P2_Pa, Q=Q_m3_s)
    return {
        "method": "ISA-75.01.01-liquid",
        "Kv_m3_per_hr": Kv,
        "Cv_us_gpm": Kv * 1.156,
        "rho_l_kg_m3": rho_l_kg_m3,
        "P1_Pa": P1_Pa,
        "P2_Pa": P2_Pa,
        "Q_m3_s": Q_m3_s,
    }


def gas_control_valve(
    *,
    T_K: float,
    MW: float,
    mu_Pa_s: float,
    gamma: float,
    Z: float,
    P1_Pa: float,
    P2_Pa: float,
    Q_m3_s: float,
) -> dict[str, Any]:
    """Gas control valve Kv via fluids.control_valve.size_control_valve_g.

    `Q_m3_s` is volumetric flow at inlet conditions (P1, T).
    """

    cv = _require_library("fluids.control_valve", "fluids")
    Kv = cv.size_control_valve_g(T=T_K, MW=MW, mu=mu_Pa_s, gamma=gamma, Z=Z, P1=P1_Pa, P2=P2_Pa, Q=Q_m3_s)
    return {
        "method": "ISA-75.01.01-gas",
        "Kv_m3_per_hr": Kv,
        "Cv_us_gpm": Kv * 1.156,
        "T_K": T_K,
        "MW_g_mol": MW,
        "gamma": gamma,
        "P1_Pa": P1_Pa,
        "P2_Pa": P2_Pa,
        "Q_m3_s": Q_m3_s,
    }


def api520_gas_relief_area(
    *,
    mass_flow_kg_s: float,
    T_K: float,
    MW: float,
    Z: float = 1.0,
    gamma: float = 1.4,
    P1_relieving_Pa: float,
    Pb_Pa: float = 101325.0,
    Kd: float = 0.975,
    Kb: float = 1.0,
    Kc: float = 1.0,
) -> dict[str, Any]:
    """API 520 Part I preliminary gas/vapor relief orifice area (sub-critical or critical).

    Uses the critical-flow form for choked flow and the sub-critical form
    otherwise. Discharge coefficient Kd defaults to 0.975 (typical for gas
    PRV with rupture disk not in series).
    """

    R = 8314.462618  # J/(kmol K)
    # critical pressure ratio
    crit_ratio = (2 / (gamma + 1)) ** (gamma / (gamma - 1))
    Pb_ratio = Pb_Pa / P1_relieving_Pa
    if Pb_ratio <= crit_ratio:
        regime = "critical"
        C = math.sqrt(gamma * (2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1)))
        # API 520 Eq (in SI): A = W / (C * Kd * P1 * Kb * Kc) * sqrt(T Z / MW)
        # Here W in kg/s, P1 in Pa, A in m^2; constant absorbed in C-derivation.
        A = mass_flow_kg_s * math.sqrt(T_K * Z / MW) / (C * Kd * P1_relieving_Pa * Kb * Kc) * math.sqrt(R / 1000)
    else:
        regime = "subcritical"
        F2 = math.sqrt(
            (gamma / (gamma - 1))
            * (Pb_ratio ** (2 / gamma))
            * (1 - Pb_ratio ** ((gamma - 1) / gamma))
        )
        A = mass_flow_kg_s * math.sqrt(T_K * Z / MW) / (Kd * F2 * P1_relieving_Pa * Kc * math.sqrt(2)) * math.sqrt(R / 1000)
    return {
        "method": "API-520-Part-I-gas",
        "regime": regime,
        "required_orifice_area_m2": A,
        "required_orifice_area_mm2": A * 1e6,
        "critical_pressure_ratio": crit_ratio,
        "Pb_over_P1": Pb_ratio,
        "Kd": Kd,
        "Kb": Kb,
        "Kc": Kc,
        "mass_flow_kg_s": mass_flow_kg_s,
        "T_K": T_K,
        "MW_g_mol": MW,
        "P1_relieving_Pa": P1_relieving_Pa,
    }


def api520_liquid_relief_area(
    *,
    Q_m3_s: float,
    rho_kg_m3: float,
    P1_relieving_Pa: float,
    Pb_Pa: float = 101325.0,
    Kd: float = 0.65,
    Kw: float = 1.0,
    Kc: float = 1.0,
    Kv: float = 1.0,
) -> dict[str, Any]:
    """API 520 Part I preliminary liquid relief orifice area.

    Discharge coefficient Kd defaults to 0.65 (typical for liquid PRV without
    capacity certification). Override with vendor-certified value.
    """

    dP = P1_relieving_Pa - Pb_Pa
    if dP <= 0:
        raise ValueError("inlet relieving pressure must exceed back-pressure")
    # A = Q / (Kd * Kw * Kc * Kv) * sqrt(rho / (2 * dP))
    A = Q_m3_s / (Kd * Kw * Kc * Kv) * math.sqrt(rho_kg_m3 / (2 * dP))
    return {
        "method": "API-520-Part-I-liquid",
        "required_orifice_area_m2": A,
        "required_orifice_area_mm2": A * 1e6,
        "Q_m3_s": Q_m3_s,
        "rho_kg_m3": rho_kg_m3,
        "P1_relieving_Pa": P1_relieving_Pa,
        "Pb_Pa": Pb_Pa,
        "Kd": Kd,
        "Kw": Kw,
        "Kc": Kc,
        "Kv": Kv,
    }

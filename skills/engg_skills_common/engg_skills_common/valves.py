"""Control and relief valve sizing helpers.

Control valve sizing uses `fluids.control_valve` (ISA 75.01.01 / IEC 60534
equations). Relief sizing implements API 520 Part I 8th-edition gas/vapor and
liquid screening equations with SI inputs and explicit API-unit conversions.
Final relief sizing must follow the published standard text and qualified
pressure-relief engineering.
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


# Relief gas/vapor equation notes, API 520 Part I, 8th ed. SI basis:
# W kg/h, P kPa(a), T K, M kg/kmol, A mm^2, k = Cp/Cv.
# Critical ratio: Pcf/P1 = (2/(k + 1))^(k/(k - 1)).
# Critical area: A = W*sqrt(T*Z/M)/(C*Kd*P1*Kb*Kc).
# Gas C: C = 0.03948*sqrt(k*(2/(k + 1))^((k + 1)/(k - 1))).
# Subcritical area: A = 17.9*W*sqrt(T*Z/(M*P1*(P1 - P2)))/(F2*Kd*Kc).
# Subcritical F2, r = P2/P1: sqrt(k/(k - 1)*r^(2/k)*(1 - r^((k - 1)/k))/(1 - r)).


def api520_gas_critical_pressure_ratio(gamma: float) -> float:
    """Critical downstream/upstream absolute pressure ratio for ideal-gas PRV flow."""

    if gamma <= 1.0:
        raise ValueError("gamma must be > 1 for API 520 ideal-gas equations")
    return (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))


def api520_gas_coefficient_C(gamma: float) -> float:
    """API 520 gas/vapor coefficient C in SI units for critical-flow equations."""

    if gamma <= 1.0:
        raise ValueError("gamma must be > 1 for API 520 ideal-gas equations")
    return 0.03948 * math.sqrt(gamma * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (gamma - 1.0)))


def api520_subcritical_F2(gamma: float, pressure_ratio: float) -> float:
    """API 520 subcritical-flow coefficient F2 for gas/vapor service."""

    if gamma <= 1.0:
        raise ValueError("gamma must be > 1 for API 520 ideal-gas equations")
    if not (0.0 < pressure_ratio < 1.0):
        raise ValueError("pressure_ratio must be between 0 and 1")
    numerator = 1.0 - pressure_ratio ** ((gamma - 1.0) / gamma)
    return math.sqrt((gamma / (gamma - 1.0)) * pressure_ratio ** (2.0 / gamma) * numerator / (1.0 - pressure_ratio))


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
    """API 520 Part I preliminary gas/vapor relief orifice area.

    Inputs are SI: kg/s, K, g/mol, and absolute Pa. Internally the function
    converts to kg/h, kPa, K, kg/kmol, and mm^2. Critical flow uses the
    critical-flow area equation. Subcritical flow uses the subcritical equation
    for conventional and pilot-operated PRVs; for balanced-bellows subcritical
    service, obtain correction factors from the manufacturer or standard.
    """

    if mass_flow_kg_s <= 0 or T_K <= 0 or MW <= 0 or Z <= 0:
        raise ValueError("mass flow, temperature, MW, and Z must be positive")
    if P1_relieving_Pa <= Pb_Pa:
        raise ValueError("upstream relieving pressure must exceed backpressure")
    for name, value in {"Kd": Kd, "Kb": Kb, "Kc": Kc}.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive")

    W_kg_h = mass_flow_kg_s * 3600.0
    P1_kPa = P1_relieving_Pa / 1000.0
    P2_kPa = Pb_Pa / 1000.0
    pressure_ratio = P2_kPa / P1_kPa
    critical_ratio = api520_gas_critical_pressure_ratio(gamma)
    warnings: list[str] = []

    if pressure_ratio <= critical_ratio:
        regime = "critical"
        C = api520_gas_coefficient_C(gamma)
        A_mm2 = W_kg_h / (C * Kd * P1_kPa * Kb * Kc) * math.sqrt(T_K * Z / MW)
        equation = "API 520 Part I 8th ed. gas/vapor critical-flow equation; C equation"
        F2 = None
    else:
        regime = "subcritical"
        F2 = api520_subcritical_F2(gamma, pressure_ratio)
        A_mm2 = (
            17.9
            * W_kg_h
            / (F2 * Kd * Kc)
            * math.sqrt(T_K * Z / (MW * P1_kPa * (P1_kPa - P2_kPa)))
        )
        equation = "API 520 Part I 8th ed. gas/vapor subcritical-flow equation; F2 equation"
        C = None
        if abs(Kb - 1.0) > 1e-12:
            warnings.append("Kb is not used in the API 520 subcritical gas/vapor equation used here.")

    return {
        "method": "API-520-Part-I-8th-ed-gas-vapor",
        "api_equation_basis": equation,
        "regime": regime,
        "required_orifice_area_m2": A_mm2 / 1e6,
        "required_orifice_area_mm2": A_mm2,
        "critical_pressure_ratio_Pcf_over_P1": critical_ratio,
        "backpressure_ratio_P2_over_P1": pressure_ratio,
        "C_SI": C,
        "F2": F2,
        "Kd": Kd,
        "Kb": Kb,
        "Kc": Kc,
        "mass_flow_kg_s": mass_flow_kg_s,
        "mass_flow_kg_h": W_kg_h,
        "T_K": T_K,
        "MW_g_mol": MW,
        "Z": Z,
        "gamma": gamma,
        "P1_relieving_Pa_abs": P1_relieving_Pa,
        "Pb_Pa_abs": Pb_Pa,
        "warnings": warnings,
    }


# Relief liquid equation notes, API 520 Part I, 8th ed. SI basis:
# Q L/min, P kPa(a), G1 liquid SG vs water at flowing temperature, A mm^2, mu cP.
# Liquid area: A = 11.78*Q*sqrt(G1/(P1 - P2))/(Kd*Kw*Kc*Kv).
# Viscosity correction: Kv = (0.9935 + 2.878/sqrt(Re) + 342.75/Re^1.5)^-1.
# Re estimate for Kv correction: Re = 18800*Q*G1/(mu*sqrt(A)).
# Use Kv = 1 first, select the next larger standard orifice, then recheck Kv.


def api520_liquid_viscosity_correction(Re: float) -> float:
    """API 520 liquid-service viscosity correction factor Kv."""

    if Re <= 0:
        raise ValueError("Re must be positive")
    return (0.9935 + 2.878 / math.sqrt(Re) + 342.75 / (Re ** 1.5)) ** -1.0


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
    mu_Pa_s: float | None = None,
    selected_orifice_area_m2: float | None = None,
) -> dict[str, Any]:
    """API 520 Part I preliminary liquid relief orifice area.

    Inputs are SI: m^3/s, kg/m^3, and Pa. The calculation converts to L/min,
    kPa, and mm^2 internally. If `mu_Pa_s` is supplied, `Kv` is calculated
    from the Reynolds-number correction; otherwise the explicit `Kv` input is used.
    """

    if Q_m3_s <= 0 or rho_kg_m3 <= 0:
        raise ValueError("Q and rho must be positive")
    if P1_relieving_Pa <= Pb_Pa:
        raise ValueError("inlet relieving pressure must exceed back-pressure")
    for name, value in {"Kd": Kd, "Kw": Kw, "Kc": Kc, "Kv": Kv}.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    if mu_Pa_s is not None and mu_Pa_s <= 0:
        raise ValueError("mu_Pa_s must be positive when provided")
    if selected_orifice_area_m2 is not None and selected_orifice_area_m2 <= 0:
        raise ValueError("selected_orifice_area_m2 must be positive when provided")

    Q_L_min = Q_m3_s * 60_000.0
    dP_kPa = (P1_relieving_Pa - Pb_Pa) / 1000.0
    G1 = rho_kg_m3 / 999.016  # water density near standard conditions, kg/m^3
    A_no_visc_mm2 = 11.78 * Q_L_min / (Kd * Kw * Kc) * math.sqrt(G1 / dP_kPa)
    Re = None
    Kv_used = Kv
    warnings: list[str] = []
    if mu_Pa_s is not None:
        mu_cP = mu_Pa_s * 1000.0
        A_for_Re_mm2 = selected_orifice_area_m2 * 1e6 if selected_orifice_area_m2 is not None else A_no_visc_mm2
        Re = 18_800.0 * Q_L_min * G1 / (mu_cP * math.sqrt(A_for_Re_mm2))
        Kv_used = api520_liquid_viscosity_correction(Re)
        if abs(Kv - 1.0) > 1e-12:
            warnings.append("Explicit Kv input ignored because mu_Pa_s was provided and Kv was calculated.")
        if selected_orifice_area_m2 is None:
            warnings.append("Kv was estimated using the preliminary calculated area; select a standard orifice before final Re/Kv evaluation.")

    A_mm2 = A_no_visc_mm2 / Kv_used
    return {
        "method": "API-520-Part-I-8th-ed-liquid",
        "api_equation_basis": "API 520 Part I 8th ed. liquid equation; viscosity correction if calculated",
        "required_orifice_area_m2": A_mm2 / 1e6,
        "required_orifice_area_mm2": A_mm2,
        "area_without_viscosity_correction_mm2": A_no_visc_mm2,
        "Q_m3_s": Q_m3_s,
        "Q_L_min": Q_L_min,
        "rho_kg_m3": rho_kg_m3,
        "specific_gravity_G1": G1,
        "P1_relieving_Pa": P1_relieving_Pa,
        "Pb_Pa": Pb_Pa,
        "dP_kPa": dP_kPa,
        "Kd": Kd,
        "Kw": Kw,
        "Kc": Kc,
        "Kv": Kv_used,
        "Re": Re,
        "warnings": warnings,
    }

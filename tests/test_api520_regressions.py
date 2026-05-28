"""Regression tests for API 520 relief sizing helpers."""

from __future__ import annotations

import math

from engg_skills_common.valves import (
    api520_gas_coefficient_C,
    api520_gas_critical_pressure_ratio,
    api520_gas_relief_area,
    api520_liquid_relief_area,
    api520_liquid_viscosity_correction,
    api520_subcritical_F2,
)


def test_api520_gas_coefficient_and_critical_ratio_for_k_1p11():
    assert math.isclose(api520_gas_coefficient_C(1.11), 0.024890086557206686, rel_tol=1e-12)
    assert math.isclose(api520_gas_critical_pressure_ratio(1.11), 0.5825880118049674, rel_tol=1e-12)


def test_api520_gas_critical_example_si_equation_basis():
    res = api520_gas_relief_area(
        mass_flow_kg_s=24270 / 3600,
        T_K=313.2,
        MW=51.0,
        Z=1.0,
        gamma=1.11,
        P1_relieving_Pa=670e3,
        Pb_Pa=101.325e3,
        Kd=0.975,
        Kb=1.0,
        Kc=1.0,
    )
    assert res["regime"] == "critical"
    assert math.isclose(res["required_orifice_area_mm2"], 3699.0460646834417, rel_tol=1e-12)


def test_api520_gas_subcritical_example_si_equation_basis():
    res = api520_gas_relief_area(
        mass_flow_kg_s=24270 / 3600,
        T_K=313.2,
        MW=51.0,
        Z=1.0,
        gamma=1.11,
        P1_relieving_Pa=670e3,
        Pb_Pa=532e3,
        Kd=0.975,
        Kb=1.0,
        Kc=1.0,
    )
    assert res["regime"] == "subcritical"
    assert math.isclose(res["F2"], 0.8547632657974537, rel_tol=1e-12)
    assert math.isclose(res["required_orifice_area_mm2"], 4248.358775943481, rel_tol=1e-12)


def test_api520_liquid_equation_uses_api_si_units():
    res = api520_liquid_relief_area(
        Q_m3_s=2270 / 60_000,
        rho_kg_m3=0.9 * 999.016,
        P1_relieving_Pa=670e3,
        Pb_Pa=101.325e3,
        Kd=0.65,
        Kw=1.0,
        Kc=1.0,
        Kv=1.0,
    )
    assert math.isclose(res["specific_gravity_G1"], 0.9, rel_tol=1e-12)
    assert math.isclose(res["required_orifice_area_mm2"], 1636.6166969241663, rel_tol=1e-12)


def test_api520_liquid_viscosity_correction_decreases_area_correction_factor():
    Kv = api520_liquid_viscosity_correction(1000.0)
    assert 0.0 < Kv < 1.0

"""Smoke and correctness tests for new engg_skills_common modules."""

from __future__ import annotations

import math

import pytest

from engg_skills_common.amine import amine_circulation_rate
from engg_skills_common.causal import DAG
from engg_skills_common.coda import (
    alr,
    clr,
    heavy_end_balance,
    ilr,
    multiplicative_replacement,
    sbp_to_psi,
)
from engg_skills_common.convection import dittus_boelter, gnielinski
from engg_skills_common.merox import (
    disulfide_carryback_risk,
    extractor_kremser,
    mercaptide_loading,
)
from engg_skills_common.reactor import (
    arrhenius_fit,
    batch_time_nth_order,
    cstr_volume_nth_order,
    pfr_volume_nth_order,
)
from engg_skills_common.separations import (
    fenske_min_stages,
    gilliland_stages,
    kremser,
    underwood_min_reflux,
)
from engg_skills_common.separator import horizontal_separator, vertical_separator
from engg_skills_common.timeseries import (
    autocorrelation,
    estimate_block_length,
    moving_block_bootstrap,
    partial_autocorrelation,
)
from engg_skills_common.valves import api520_gas_relief_area, api520_liquid_relief_area
from engg_skills_common.vle import rachford_rice


# --- Compositional Data Analysis ---------------------------------------------


def test_clr_sums_to_zero():
    x = [0.4, 0.5, 0.05, 0.05]
    assert math.isclose(sum(clr(x)), 0.0, abs_tol=1e-12)


def test_ilr_default_has_D_minus_1_components():
    x = [0.4, 0.5, 0.05, 0.05]
    assert len(ilr(x)) == 3


def test_alr_drops_one_component():
    x = [0.4, 0.5, 0.1]
    assert len(alr(x)) == 2


def test_zero_replacement_preserves_sum():
    x = [0.0, 0.5, 0.3, 0.2]
    replaced = multiplicative_replacement(x, delta=1e-4)
    assert math.isclose(sum(replaced), 1.0, abs_tol=1e-6)
    assert all(v > 0 for v in replaced)


def test_heavy_end_balance_signs():
    heavy_rich = {"c3": 0.30, "c4": 0.30, "c5": 0.25, "c6plus": 0.15}
    res = heavy_end_balance(heavy_rich, ["c5", "c6plus"], ["c3", "c4"])
    assert res["z_H"] < 0  # heavy mole fractions still smaller than body geometric mean
    heavy_dom = {"c3": 0.10, "c4": 0.10, "c5": 0.40, "c6plus": 0.40}
    res = heavy_end_balance(heavy_dom, ["c5", "c6plus"], ["c3", "c4"])
    assert res["z_H"] > 0


def test_sbp_orthonormality():
    sbp = [[1, -1, 0, 0], [0, 0, 1, -1], [1, 1, -1, -1]]
    psi = sbp_to_psi(sbp)
    for row in psi:
        assert math.isclose(sum(v * v for v in row), 1.0, abs_tol=1e-9)


# --- Causal DAG --------------------------------------------------------------


def test_dag_cycle_rejected():
    with pytest.raises(ValueError):
        DAG.from_edges([("A", "B"), ("B", "A")])


def test_dag_backdoor_simple_confounder():
    g = DAG.from_edges([("Z", "T"), ("Z", "Y"), ("T", "Y")])
    res = g.backdoor_adjustment("T", "Y")
    assert "Z" in res["adjustment_set"]
    assert res["satisfies_backdoor"]


def test_dag_dsep_collider():
    g = DAG.from_edges([("A", "C"), ("B", "C")])
    # A and B marginally independent
    assert g.d_separated({"A"}, {"B"}, set())
    # Conditioning on collider opens the path
    assert not g.d_separated({"A"}, {"B"}, {"C"})


def test_dag_dsep_chain_blocking():
    g = DAG.from_edges([("A", "B"), ("B", "C")])
    assert g.d_separated({"A"}, {"C"}, {"B"})
    assert not g.d_separated({"A"}, {"C"}, set())


# --- Time series -------------------------------------------------------------


def test_acf_lag_zero_is_one():
    x = list(range(100))
    acf = autocorrelation(x, 5)
    assert math.isclose(acf[0], 1.0, abs_tol=1e-12)


def test_pacf_lag_zero_is_one():
    x = [math.sin(i * 0.3) for i in range(200)]
    pacf = partial_autocorrelation(x, 10)
    assert math.isclose(pacf[0], 1.0, abs_tol=1e-12)


def test_block_length_within_bounds():
    x = list(range(100))
    res = estimate_block_length(x)
    assert 2 <= res["block_length"] <= 100 // 4


def test_block_bootstrap_mean_is_close():
    x = [1.0 + 0.5 * math.sin(i * 0.1) for i in range(200)]
    res = moving_block_bootstrap(x, block_length=5, n_resamples=200, statistic=lambda s: sum(s) / len(s), seed=42)
    mean_x = sum(x) / len(x)
    assert abs(res["statistic_mean"] - mean_x) < 0.2


# --- Separations -------------------------------------------------------------


def test_fenske_basic():
    res = fenske_min_stages(alpha=2.5, xD=0.95, xB=0.05)
    assert 5 < res["N_min_stages_including_reboiler"] < 8


def test_underwood_basic():
    res = underwood_min_reflux(alphas=[4.0, 2.0, 1.0], feed_zs=[0.4, 0.4, 0.2], distillate_xs=[0.9, 0.09, 0.01], q=1.0)
    assert res["Rmin"] > 0


def test_gilliland_monotone_in_R():
    g_low = gilliland_stages(Nmin=10, Rmin=1.5, R=1.6)
    g_hi = gilliland_stages(Nmin=10, Rmin=1.5, R=3.0)
    assert g_hi["N_stages_including_reboiler"] < g_low["N_stages_including_reboiler"]


def test_kremser_basic():
    res = kremser(N=8, A=1.4, x_in=0.0, y_in=0.02, K=0.5)
    assert 0 < res["fractional_absorption_eta"] < 1
    assert res["y_out_gas"] < res["y_in_gas"]


# --- Reactor -----------------------------------------------------------------


def test_arrhenius_recovers_ea():
    R = 8.314462618
    Ea_true = 50000.0
    A_true = 1e7
    Ts = [298.0, 308.0, 318.0, 328.0, 338.0]
    ks = [A_true * math.exp(-Ea_true / (R * T)) for T in Ts]
    res = arrhenius_fit(Ts, ks)
    assert abs(res["Ea_J_mol"] - Ea_true) / Ea_true < 0.05
    assert abs(res["A_pre_exponential"] / A_true - 1) < 0.5  # exponential fit; allow some slack


def test_cstr_pfr_volume_ordering_first_order():
    cstr = cstr_volume_nth_order(C0=1000, conversion=0.9, flow_m3_s=0.001, k=5e-4)
    pfr = pfr_volume_nth_order(C0=1000, conversion=0.9, flow_m3_s=0.001, k=5e-4)
    assert cstr["volume_m3"] > pfr["volume_m3"]


def test_batch_time_first_order_matches_pfr_tau():
    pfr = pfr_volume_nth_order(C0=1000, conversion=0.9, flow_m3_s=0.001, k=5e-4)
    batch = batch_time_nth_order(C0=1000, conversion=0.9, k=5e-4)
    assert math.isclose(pfr["tau_residence_s"], batch["time_s"], rel_tol=1e-9)


# --- Amine / Merox -----------------------------------------------------------


def test_amine_circulation_basic():
    res = amine_circulation_rate(acid_gas_mol_s=0.5, rich_loading_mol_per_mol=0.4, lean_loading_mol_per_mol=0.05, amine="DEA", amine_wt_fraction=0.3)
    assert res["solution_mass_flow_kg_s"] > 0
    assert res["amine_mass_flow_kg_s"] < res["solution_mass_flow_kg_s"]


def test_merox_loading_basic():
    res = mercaptide_loading(rsh_inlet_lpg_ppmw=500, lpg_mass_flow_kg_s=10, caustic_circulation_kg_s=0.5, naoh_wt_fraction=0.12)
    assert res["rsh_per_naoh_mol_per_mol"] > 0


def test_merox_kremser_efficiency_in_range():
    res = extractor_kremser(distribution_K_lpg_to_caustic=0.02, lpg_volumetric_m3_s=0.014, caustic_volumetric_m3_s=0.0006, n_theoretical_stages=3, rsh_in_lpg=500)
    assert 0 < res["stage_efficiency_eta"] < 1


def test_disulfide_carryback_score_bounds():
    res = disulfide_carryback_risk(caustic_disulfide_ppmw=300, caustic_age_days=60, separator_dp_kpa=8)
    assert 0 <= res["score_0_to_1"] <= 1


# --- Convection --------------------------------------------------------------


def test_dittus_boelter_basic():
    res = dittus_boelter(Re=50000, Pr=4.5, k=0.6, Dh=0.025)
    assert res["Nu"] > 200
    assert res["h_W_m2_K"] > 0


def test_gnielinski_basic():
    res = gnielinski(Re=50000, Pr=4.5, k=0.6, Dh=0.025)
    assert res["Nu"] > 200


# --- Separator ---------------------------------------------------------------


def test_vertical_separator_diameter_positive():
    res = vertical_separator(vapor_volumetric_m3_s=0.4, liquid_volumetric_m3_s=0.005, rho_l=600, rho_v=30, demister=True)
    assert res["diameter_m"] > 0
    assert res["tan_tan_height_m"] > 0


def test_horizontal_separator_length_from_LD():
    res = horizontal_separator(vapor_volumetric_m3_s=0.4, liquid_volumetric_m3_s=0.005, rho_l=600, rho_v=30, demister=True, LD_ratio=4.0)
    assert math.isclose(res["length_m"] / res["diameter_m"], 4.0, rel_tol=1e-6)


# --- Valves ------------------------------------------------------------------


def test_api520_gas_area_positive():
    res = api520_gas_relief_area(
        mass_flow_kg_s=2.5, T_K=320, MW=44.1, Z=0.95, gamma=1.13, P1_relieving_Pa=1.5e6, Pb_Pa=2e5
    )
    assert res["required_orifice_area_m2"] > 0


def test_api520_liquid_area_positive():
    res = api520_liquid_relief_area(Q_m3_s=0.005, rho_kg_m3=800, P1_relieving_Pa=2.5e6, Pb_Pa=2e5)
    assert res["required_orifice_area_m2"] > 0


# --- VLE Rachford-Rice -------------------------------------------------------


def test_rachford_rice_two_phase():
    res = rachford_rice([4.2, 0.6], [0.4, 0.6])
    assert 0 < res["vapor_fraction"] < 1
    xs = res["xs"]
    ys = res["ys"]
    assert math.isclose(sum(xs), 1.0, abs_tol=1e-6)
    assert math.isclose(sum(ys), 1.0, abs_tol=1e-6)


def test_rachford_rice_single_phase():
    res = rachford_rice([0.5, 0.4], [0.5, 0.5])
    assert res["vapor_fraction"] == 0.0
    assert res["regime"] == "subcooled-liquid"

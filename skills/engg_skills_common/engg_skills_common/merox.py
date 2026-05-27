"""Merox caustic mercaptan extraction screening helpers.

Captures simple mass-balance and partition calculations for an aqueous-caustic
mercaptan extractor used in LPG sweetening (Merox-style):

- Mercaptide loading in caustic from a stoichiometric uptake assumption.
- A simple Kremser-style stage estimate with a user-supplied distribution
  coefficient between LPG and caustic (lab-measured or correlation-derived).
- Disulfide-carryback flag: if lean caustic contains residual disulfide,
  product disulfide concentration is correlated; the helper reports a
  carryback risk score (relative, not absolute).

These are screening calculations for plant troubleshooting and operator
discussion; not a substitute for the licensor's process model.
"""

from __future__ import annotations

from typing import Any


def mercaptide_loading(
    *,
    rsh_inlet_lpg_ppmw: float,
    lpg_mass_flow_kg_s: float,
    caustic_circulation_kg_s: float,
    naoh_wt_fraction: float,
    avg_rsh_mw_g_mol: float = 76.0,
) -> dict[str, Any]:
    """Steady-state RS-Na loading in caustic, mol RS- per mol NaOH.

    Assumes 100% extraction of mercaptan as RS-Na (worst-case loading). Use as
    an upper bound; actual loading is lower if regeneration is keeping pace.
    """

    NAOH_MW = 39.997  # g/mol
    rsh_mass_rate = rsh_inlet_lpg_ppmw * 1e-6 * lpg_mass_flow_kg_s  # kg/s
    rsh_mol_rate = rsh_mass_rate / (avg_rsh_mw_g_mol / 1000.0)
    naoh_mass_rate = caustic_circulation_kg_s * naoh_wt_fraction
    naoh_mol_rate = naoh_mass_rate / (NAOH_MW / 1000.0)
    loading = rsh_mol_rate / naoh_mol_rate if naoh_mol_rate > 0 else float("inf")
    return {
        "method": "merox-mercaptide-mass-balance",
        "rsh_inlet_lpg_ppmw": rsh_inlet_lpg_ppmw,
        "lpg_mass_flow_kg_s": lpg_mass_flow_kg_s,
        "caustic_circulation_kg_s": caustic_circulation_kg_s,
        "naoh_wt_fraction": naoh_wt_fraction,
        "rsh_mol_s": rsh_mol_rate,
        "naoh_mol_s": naoh_mol_rate,
        "rsh_per_naoh_mol_per_mol": loading,
    }


def extractor_kremser(
    *,
    distribution_K_lpg_to_caustic: float,
    lpg_volumetric_m3_s: float,
    caustic_volumetric_m3_s: float,
    n_theoretical_stages: float,
    rsh_in_lpg: float,
) -> dict[str, Any]:
    """Kremser-style extraction performance estimate for an idealized contactor.

    `distribution_K_lpg_to_caustic` is the equilibrium ratio C_LPG / C_caustic
    (so smaller K means stronger extraction into the caustic).
    """

    if distribution_K_lpg_to_caustic <= 0:
        raise ValueError("distribution coefficient must be positive")
    A = caustic_volumetric_m3_s / (distribution_K_lpg_to_caustic * lpg_volumetric_m3_s)
    if abs(A - 1) < 1e-6:
        eta = n_theoretical_stages / (n_theoretical_stages + 1)
    else:
        eta = (A ** (n_theoretical_stages + 1) - A) / (A ** (n_theoretical_stages + 1) - 1)
    rsh_out = rsh_in_lpg * (1 - eta)
    return {
        "method": "merox-extractor-kremser",
        "A_extraction_factor": A,
        "stage_efficiency_eta": eta,
        "n_theoretical_stages": n_theoretical_stages,
        "rsh_in_lpg": rsh_in_lpg,
        "rsh_out_lpg": rsh_out,
    }


def disulfide_carryback_risk(
    *,
    caustic_disulfide_ppmw: float,
    caustic_age_days: float,
    separator_dp_kpa: float,
) -> dict[str, Any]:
    """Heuristic risk score for disulfide carryback to product LPG.

    Returns a 0-1 score combining: caustic disulfide loading, time since last
    caustic changeout, and disulfide-separator differential pressure (poor
    separation flagged by elevated dP). This is NOT calibrated to any specific
    plant; treat as a screening sort and overlay plant data.
    """

    s1 = min(1.0, caustic_disulfide_ppmw / 500.0)
    s2 = min(1.0, caustic_age_days / 90.0)
    s3 = min(1.0, max(0.0, separator_dp_kpa - 5.0) / 20.0)
    score = (s1 + s2 + s3) / 3.0
    flag = "low"
    if score > 0.66:
        flag = "high"
    elif score > 0.33:
        flag = "moderate"
    return {
        "method": "merox-carryback-heuristic",
        "score_0_to_1": score,
        "flag": flag,
        "subscores": {
            "caustic_disulfide_ppmw": s1,
            "caustic_age_days": s2,
            "separator_dp_kpa": s3,
        },
    }

"""Aqueous amine treating helpers (DEA / MDEA / MEA).

Lightweight calculations for screening:
- Lean/rich loading in mol acid gas per mol amine.
- Mass-balance check around the absorber.
- Amine circulation rate from acid-gas load and chosen rich loading.

These are NOT a substitute for rate-based simulation (e.g., Aspen ProMax,
ProTreat) or the manufacturer's recommended operating envelope. Use them to
size circulation and sanity-check field data only.
"""

from __future__ import annotations

from typing import Any

AMINE_MW = {
    "DEA": 105.14,
    "MDEA": 119.16,
    "MEA": 61.08,
    "DGA": 105.14,
    "DIPA": 133.19,
    "PIPERAZINE": 86.14,
}


def loading_from_mass_balance(*, acid_gas_mol_s: float, amine_mol_s: float) -> float:
    """mol acid gas per mol amine (instantaneous loading)."""

    if amine_mol_s <= 0:
        raise ValueError("amine flow must be positive")
    return acid_gas_mol_s / amine_mol_s


def amine_circulation_rate(
    *,
    acid_gas_mol_s: float,
    rich_loading_mol_per_mol: float,
    lean_loading_mol_per_mol: float,
    amine: str = "DEA",
    amine_wt_fraction: float = 0.30,
) -> dict[str, Any]:
    """Compute required lean amine mass flow for a target rich loading.

    Pickup is `delta_loading = rich - lean`. Required amine molar flow is
    `acid_gas / delta_loading`. Convert to mass via amine wt% in solution.
    """

    if rich_loading_mol_per_mol <= lean_loading_mol_per_mol:
        raise ValueError("rich loading must exceed lean loading")
    if amine.upper() not in AMINE_MW:
        raise ValueError(f"unknown amine: {amine}; supported: {sorted(AMINE_MW)}")
    delta = rich_loading_mol_per_mol - lean_loading_mol_per_mol
    amine_mol_s = acid_gas_mol_s / delta
    MW = AMINE_MW[amine.upper()] / 1000.0  # kg/mol
    amine_kg_s = amine_mol_s * MW
    solution_kg_s = amine_kg_s / amine_wt_fraction
    return {
        "method": "amine-circulation-mass-balance",
        "amine": amine.upper(),
        "amine_wt_fraction": amine_wt_fraction,
        "acid_gas_mol_s": acid_gas_mol_s,
        "delta_loading": delta,
        "amine_molar_flow_mol_s": amine_mol_s,
        "amine_mass_flow_kg_s": amine_kg_s,
        "solution_mass_flow_kg_s": solution_kg_s,
        "rich_loading": rich_loading_mol_per_mol,
        "lean_loading": lean_loading_mol_per_mol,
    }


def loading_envelope_warnings(*, amine: str, rich_loading_mol_per_mol: float) -> list[str]:
    """Return warnings if rich loading exceeds common operating envelopes.

    These envelopes are drawn from widely cited general guidance (GPSA
    Engineering Data Book, vendor handbooks); cross-check with your licensed
    technology provider before operating.
    """

    a = amine.upper()
    warnings: list[str] = []
    envelope = {
        "DEA": 0.45,
        "MDEA": 0.55,
        "MEA": 0.40,
        "DGA": 0.50,
    }
    cap = envelope.get(a)
    if cap is not None and rich_loading_mol_per_mol > cap:
        warnings.append(
            f"Rich loading {rich_loading_mol_per_mol:.2f} exceeds the commonly cited "
            f"envelope of ~{cap:.2f} mol/mol for {a}; review corrosion risk and "
            f"vendor guidance."
        )
    return warnings

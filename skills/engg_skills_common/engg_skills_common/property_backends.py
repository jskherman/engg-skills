"""Property backends using Caleb Bell's thermo, chemicals, fluids, and ht libraries.

These wrappers keep engg-skills scripts stable while delegating rigorous property
and transport calculations to the same Python libraries commonly used when a GUI
process simulator is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


LPG_DEFAULTS = {
    "propane": {"Tc": 369.89, "Pc": 4.2512e6, "omega": 0.1521, "Vc": 0.0002, "MW": 44.09562e-3},
    "n-butane": {"Tc": 425.12, "Pc": 3.796e6, "omega": 0.2002, "Vc": 0.000255, "MW": 58.1222e-3},
    "isobutane": {"Tc": 407.81, "Pc": 3.629e6, "omega": 0.184, "Vc": 0.000263, "MW": 58.1222e-3},
    "n-pentane": {"Tc": 469.7, "Pc": 3.37e6, "omega": 0.251, "Vc": 0.000304, "MW": 72.14878e-3},
    "isopentane": {"Tc": 460.35, "Pc": 3.378e6, "omega": 0.2274, "Vc": 0.000306, "MW": 72.14878e-3},
}


def normalize_zs(zs: list[float]) -> list[float]:
    if not zs:
        raise ValueError("composition cannot be empty")
    if any(z < 0 for z in zs):
        raise ValueError("composition values cannot be negative")
    total = sum(zs)
    if total <= 0:
        raise ValueError("composition sum must be positive")
    return [z / total for z in zs]


def _require_library(import_name: str, package_hint: str):
    try:
        return __import__(import_name, fromlist=["*"])
    except Exception as exc:  # pragma: no cover - exercised by CLI failure path
        raise RuntimeError(
            f"Optional dependency {package_hint!r} is required for this calculation. "
            f"Install project dependencies with `uv sync` or add {package_hint}."
        ) from exc


def get_lpg_constants(components: list[str]) -> dict[str, list[float]]:
    """Return built-in light-hydrocarbon constants for examples and fallback use."""

    data = []
    missing = []
    for component in components:
        key = component.strip().lower()
        if key not in LPG_DEFAULTS:
            missing.append(component)
        else:
            data.append(LPG_DEFAULTS[key])
    if missing:
        raise ValueError(f"No built-in LPG constants for: {', '.join(missing)}. Provide explicit constants instead.")
    return {
        "Tcs": [d["Tc"] for d in data],
        "Pcs": [d["Pc"] for d in data],
        "omegas": [d["omega"] for d in data],
        "Vcs": [d["Vc"] for d in data],
        "MWs": [d["MW"] for d in data],
    }


def costald_liquid_density(
    *,
    T: float,
    P: float | None,
    zs: list[float],
    Tcs: list[float],
    Vcs: list[float],
    omegas: list[float],
    MWs: list[float],
) -> dict[str, Any]:
    """Return COSTALD mixture liquid density using chemicals.volume.

    `MWs` are kg/mol. Molar volumes are m^3/mol. Density is kg/m^3.
    """

    if not (len(zs) == len(Tcs) == len(Vcs) == len(omegas) == len(MWs)):
        raise ValueError("zs, Tcs, Vcs, omegas, and MWs must have the same length")
    zs = normalize_zs(zs)
    volume = _require_library("chemicals.volume", "chemicals.volume")
    Vm_sat = volume.COSTALD_mixture(zs, T, Tcs, Vcs, omegas)
    method = "COSTALD_mixture"
    Vm = Vm_sat
    warnings: list[str] = []
    if P is not None:
        try:
            Vm = volume.COSTALD_mixture_compressed(zs, T, Tcs, Vcs, omegas, P)
            method = "COSTALD_mixture_compressed"
        except Exception as exc:
            warnings.append(f"Compressed COSTALD failed; returned saturated COSTALD volume instead: {exc}")
    MW_mix = sum(z * MW for z, MW in zip(zs, MWs, strict=True))
    return {
        "method": method,
        "temperature_k": T,
        "pressure_pa": P,
        "mole_fractions": zs,
        "molar_volume_m3_mol": Vm,
        "saturated_molar_volume_m3_mol": Vm_sat,
        "mixture_mw_kg_mol": MW_mix,
        "density_kg_m3": MW_mix / Vm,
        "warnings": warnings + [
            "COSTALD is empirical; validate against measured/simulator data for final design.",
            "Most suitable for nonpolar or mildly polar liquids such as light hydrocarbons; use caution near the critical region.",
        ],
    }


def iapws95_state(*, T: float, P: float) -> dict[str, Any]:
    """Return water/steam properties from chemicals.iapws IAPWS-95."""

    iapws = _require_library("chemicals.iapws", "chemicals")
    rho, U, S, H, Cv, Cp, w, JT, delta_T, beta_s, drho_dP = iapws.iapws95_properties(T, P)
    return {
        "method": "chemicals.iapws.iapws95_properties",
        "temperature_k": T,
        "pressure_pa": P,
        "density_kg_m3": rho,
        "internal_energy_j_kg": U,
        "entropy_j_kg_k": S,
        "enthalpy_j_kg": H,
        "cv_j_kg_k": Cv,
        "cp_j_kg_k": Cp,
        "speed_of_sound_m_s": w,
        "joule_thomson_k_pa": JT,
        "isothermal_throttling_coefficient_k": delta_T,
        "isentropic_temperature_pressure_coefficient_k_pa": beta_s,
        "drho_dp_kg_m3_pa": drho_dP,
        "warnings": ["Use IAPWS water/steam methods rather than cubic EOS for water/steam utility calculations."],
    }


def iapws_saturation(*, T: float | None = None, P: float | None = None) -> dict[str, Any]:
    """Return saturation pressure or temperature using chemicals.iapws."""

    iapws = _require_library("chemicals.iapws", "chemicals")
    if (T is None) == (P is None):
        raise ValueError("provide exactly one of T or P")
    if T is not None:
        return {"method": "Psat_IAPWS", "temperature_k": T, "saturation_pressure_pa": iapws.Psat_IAPWS(T)}
    return {"method": "Tsat_IAPWS", "pressure_pa": P, "saturation_temperature_k": iapws.Tsat_IAPWS(P)}


def pr_translated_lpg_eos(
    *,
    T: float,
    P: float,
    zs: list[float],
    Tcs: list[float],
    Pcs: list[float],
    omegas: list[float],
    kijs: list[list[float]] | None = None,
    cs: list[float] | None = None,
) -> dict[str, Any]:
    """Instantiate thermo.eos_mix.PRMIXTranslatedPPJP and report key EOS values.

    This low-level function is for explicit EOS work such as LPG-mixture checks.
    For production flash workflows, prefer a higher-level thermo FlashVL wrapper.
    """

    eos_mod = _require_library("thermo.eos_mix", "thermo")
    # thermo 0.6.0 references a module-level `ndarray` symbol in this class;
    # define a harmless non-list sentinel when NumPy is unavailable in a slim
    # runtime so ordinary list inputs still follow the scalar code path.
    if not hasattr(eos_mod, "ndarray"):
        eos_mod.ndarray = tuple
    zs = normalize_zs(zs)
    if kijs is None:
        kijs = [[0.0 for _ in zs] for _ in zs]
    if cs is None:
        cs = [0.0 for _ in zs]
    eos = eos_mod.PRMIXTranslatedPPJP(Tcs=Tcs, Pcs=Pcs, omegas=omegas, zs=zs, kijs=kijs, cs=cs, T=T, P=P)
    result: dict[str, Any] = {
        "method": "thermo.eos_mix.PRMIXTranslatedPPJP",
        "temperature_k": T,
        "pressure_pa": P,
        "mole_fractions": zs,
        "phase": getattr(eos, "phase", None),
        "warnings": [
            "Binary interaction parameters and volume-translation constants strongly affect cubic-EOS mixture results.",
            "Validate against lab data, trusted simulator output, or plant data before design use.",
        ],
    }
    for attr in ("V_l", "V_g", "Z_l", "Z_g", "H_dep_l", "H_dep_g", "S_dep_l", "S_dep_g"):
        if hasattr(eos, attr):
            try:
                result[attr] = getattr(eos, attr)
            except Exception:
                pass
    return result


def recommend_property_method(*, components: list[str], application: str = "general", pressure_pa: float | None = None) -> dict[str, Any]:
    """Transparent simulator-inspired property-method recommendation heuristic."""

    comps = [c.lower() for c in components]
    app = application.lower()
    hydrocarbon_markers = {"methane", "ethane", "propane", "butane", "n-butane", "isobutane", "pentane", "n-pentane", "isopentane", "lpg", "natural gas"}
    water_only = set(comps) <= {"water", "steam", "h2o"}
    has_water = any(c in {"water", "steam", "h2o"} for c in comps)
    is_hydrocarbon = any(c in hydrocarbon_markers for c in comps) or "lpg" in app or "hydrocarbon" in app
    if water_only or "steam" in app:
        rec = "IAPWS95/IAPWS97 water-steam properties"
        backend = "chemicals.iapws or thermo.IAPWS95/IAPWS97"
        reason = "Dedicated steam tables are preferred for water/steam utility systems."
    elif is_hydrocarbon and (pressure_pa is None or pressure_pa > 1e6 or "lpg" in app):
        rec = "Peng-Robinson/SRK cubic EOS with binary interaction checks; COSTALD for LPG liquid density"
        backend = "thermo FlashVL/PRMIX or PRMIXTranslatedPPJP; chemicals.volume.COSTALD_mixture_compressed"
        reason = "Nonpolar hydrocarbon mixtures at elevated pressure are typical cubic-EOS applications; COSTALD is often accurate for light-hydrocarbon liquids."
    elif has_water:
        rec = "activity-coefficient or specialized electrolyte/association model; do not default to cubic EOS"
        backend = "thermo activity-coefficient models where data exists; specialized package may be required"
        reason = "Water-containing polar/nonideal mixtures often need activity-coefficient or specialized models."
    else:
        rec = "Start with component-class decision: ideal/Raoult for simple low-pressure systems, EOS for nonpolar high-pressure systems, activity coefficients for polar liquid systems"
        backend = "thermo/chemicals selected per available parameters"
        reason = "Insufficient classification data; use simulator-style method screening and validate with data."
    return {
        "recommended_method": rec,
        "python_backend": backend,
        "reason": reason,
        "checks": [
            "Confirm components, phases, T/P range, and basis.",
            "Check binary interaction parameters and model validity range.",
            "Compare important properties against experimental data, trusted simulator output, or plant data.",
            "Use dedicated packages for electrolytes, amines, glycols, sour water, hydrate inhibition, and reactive systems when required.",
        ],
        "documentation_basis": [
            "DWSIM property package selection guidance",
            "Aspen Plus/HYSYS public property-method training material",
            "AVEVA PRO/II public thermodynamics capability summaries",
        ],
    }

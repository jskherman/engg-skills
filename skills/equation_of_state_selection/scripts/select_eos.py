#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["chemicals>=1.5"]
# ///
"""Equation-of-state recommender — transparent, source-cited decision tree."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "equation_of_state_selection"
SKILL_DIR = Path(__file__).resolve().parents[1]


HYDROCARBON = {
    "methane", "ethane", "propane", "butane", "n-butane", "isobutane",
    "pentane", "n-pentane", "isopentane", "neopentane", "hexane", "n-hexane",
    "isohexane", "heptane", "octane", "ethylene", "propylene", "1-butene",
    "isobutylene", "1,3-butadiene",
}
ACID_GAS = {"h2s", "hydrogen sulfide", "co2", "carbon dioxide"}
INERT_GAS = {"n2", "nitrogen", "h2", "hydrogen", "co", "carbon monoxide", "argon", "ar", "helium", "he"}
AMINES = {"mea", "dea", "mdea", "dga", "dipa", "piperazine", "diethanolamine", "monoethanolamine", "methyldiethanolamine"}
GLYCOLS = {"meg", "deg", "teg", "ethylene glycol", "diethylene glycol", "triethylene glycol"}
ALCOHOLS = {"methanol", "ethanol", "isopropanol", "n-propanol", "n-butanol"}
WATER = {"water", "h2o", "steam"}
ORGANIC_ACIDS = {"acetic acid", "formic acid", "propionic acid"}
ELECTROLYTES = {"nacl", "naoh", "koh", "hcl", "hno3", "h2so4"}
MERCAPTAN_DISULFIDE = {"methyl mercaptan", "ethyl mercaptan", "dms", "dimethyl sulfide", "dmds", "diethyl disulfide", "deds", "dimethyl disulfide"}


def _classify(comps_lower: set[str]) -> dict[str, bool]:
    return {
        "has_water": bool(comps_lower & WATER),
        "has_hydrocarbon": bool(comps_lower & HYDROCARBON),
        "has_acid_gas": bool(comps_lower & ACID_GAS),
        "has_inert": bool(comps_lower & INERT_GAS),
        "has_amine": bool(comps_lower & AMINES),
        "has_glycol": bool(comps_lower & GLYCOLS),
        "has_alcohol": bool(comps_lower & ALCOHOLS),
        "has_acid": bool(comps_lower & ORGANIC_ACIDS),
        "has_electrolyte": bool(comps_lower & ELECTROLYTES),
        "has_sulfur_species": bool(comps_lower & MERCAPTAN_DISULFIDE),
        "water_only": comps_lower.issubset(WATER),
    }


def recommend(*, components: list[str], application: str, pressure_pa: float | None) -> dict:
    comps_lower = {c.strip().lower() for c in components}
    flags = _classify(comps_lower)
    app = application.lower()
    P = pressure_pa or 0.0
    sources = [
        "DWSIM Property Package Selection wiki",
        "Carlson, CEP 1996, 'Don't gamble with physical properties for simulations'",
    ]
    recs: list[dict] = []

    if flags["water_only"] or "steam" in app:
        recs.append({
            "method": "IAPWS-IF97 / IAPWS-95 (water/steam tables)",
            "python_backend": "chemicals.iapws (Psat_IAPWS, Tsat_IAPWS, iapws95_properties)",
            "rationale": "Pure water / steam utility system: dedicated IAPWS formulation is the industry reference.",
        })
    elif flags["has_amine"] and (flags["has_acid_gas"] or "amine" in app or "sweet" in app):
        recs.append({
            "method": "Rate-based reactive electrolyte model (ELECNRTL / e-NRTL or vendor amine package)",
            "python_backend": "Not available in thermo at production grade; use ProMax, ProTreat, or Aspen amine package. For screening only, see sour-gas-amine-treating skill.",
            "rationale": "Amine + acid gas systems involve chemical equilibrium and rate-based mass transfer; cubic EOS alone is inadequate.",
        })
        recs.append({
            "method": "PRSV with high kij for screening",
            "python_backend": "thermo.eos_mix.PRSVMIX via vle-flash-calculations",
            "rationale": "Screening only; gives an order-of-magnitude solubility but misses the loading curve.",
        })
    elif flags["has_glycol"] and flags["has_water"]:
        recs.append({
            "method": "Activity coefficient (e.g., NRTL) + Henry's law for light gases",
            "python_backend": "Use activity-coefficient package; thermo supports NRTL via mixture handlers when parameters exist.",
            "rationale": "Glycol-water dehydration loops are polar/associating; cubic EOS misses the hydrate / dehydration trade-off.",
        })
    elif (flags["has_alcohol"] or flags["has_acid"]) and flags["has_hydrocarbon"]:
        recs.append({
            "method": "Cubic-Plus-Association (CPA) or activity-coefficient + Henry",
            "python_backend": "CPA not in stock thermo; consider PC-SAFT (thermo PCSAFTMIX) or activity-coefficient model.",
            "rationale": "Associating species (alcohols, organic acids) break the assumptions of plain cubic EOS.",
        })
    elif flags["has_electrolyte"]:
        recs.append({
            "method": "Electrolyte NRTL or Pitzer-type model",
            "python_backend": "Not implemented in thermo; use Aspen ELECNRTL or specialised package.",
            "rationale": "Electrolyte effects (activity, dissociation) are outside any cubic EOS family.",
        })
    elif flags["has_hydrocarbon"] and (flags["has_acid_gas"] or flags["has_sulfur_species"]):
        recs.append({
            "method": "PRSV (sour-tuned binary interaction parameters)",
            "python_backend": "thermo.eos_mix.PRSVMIX with regressed kij; fall back to PRMIX if PRSV unavailable",
            "rationale": "Sour hydrocarbon systems benefit from PRSV's improved alpha function and the sour-gas BIP literature.",
        })
        recs.append({
            "method": "PR (translated) for liquid density quality",
            "python_backend": "thermo.eos_mix.PRMIXTranslatedPPJP or PRMIXTranslatedConsistent",
            "rationale": "Volume-translated PR gives liquid density within ~1-3% over a broad range when proper translation constants are supplied.",
        })
    elif flags["has_hydrocarbon"]:
        recs.append({
            "method": "Peng-Robinson (PR) cubic EOS",
            "python_backend": "thermo.eos_mix.PRMIX",
            "rationale": "Hydrocarbon systems are the canonical application of PR; large BIP database; well-validated across LPG, refinery gas, NGL.",
        })
        recs.append({
            "method": "SRK as a second opinion",
            "python_backend": "thermo.eos_mix.SRKMIX",
            "rationale": "Comparable accuracy to PR for many hydrocarbon mixes; useful sanity check.",
        })
        if P > 1e6 or "lpg" in app:
            recs.append({
                "method": "COSTALD for screening liquid density",
                "python_backend": "chemicals.volume.COSTALD_mixture_compressed",
                "rationale": "COSTALD is often the most accurate fast estimate for light-hydrocarbon liquid density.",
            })
    elif "low pressure" in app or "polar" in app:
        recs.append({
            "method": "Activity coefficient (NRTL / UNIQUAC) with Antoine vapor pressure",
            "python_backend": "thermo activity-coefficient modules where parameters exist; chemicals.vapor_pressure for Antoine",
            "rationale": "Polar liquid mixtures at low pressure are the domain of gE models.",
        })
    else:
        recs.append({
            "method": "Default to PR with comparison to SRK; document component classification",
            "python_backend": "thermo.eos_mix.PRMIX / SRKMIX",
            "rationale": "Insufficient classification; run two methods and compare against any data available.",
        })

    checks = [
        "Cross-check density against lab data or a trusted simulator.",
        "Cross-check K-values against any available VLE measurement.",
        "Confirm the recommended method's validity range covers the operating envelope.",
        "Document the binary interaction parameters (and their source) used in the run.",
    ]
    return {
        "primary": recs[0],
        "alternatives": recs[1:],
        "component_flags": flags,
        "application": application,
        "pressure_pa": pressure_pa,
        "checks": checks,
        "documentation_basis": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="EOS / property-method recommender")
    parser.add_argument("--components", required=True)
    parser.add_argument("--application", default="general")
    parser.add_argument("--pressure-pa", type=float, default=None, dest="pressure")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=[
            "https://dwsim.org/wiki/index.php?title=Property_Package_Selection",
            "https://thermo.readthedocs.io/",
            "https://chemicals.readthedocs.io/",
        ],
        library_attributions=[
            "thermo (Caleb Bell) — MIT",
            "chemicals (Caleb Bell) — MIT",
        ],
        extra_notes=(
            "Public-source decision logic based on Carlson (CEP 1996) and "
            "DWSIM documentation. Proprietary defaults and tables from "
            "commercial simulators are not reproduced."
        ),
    )
    try:
        comps = [c.strip() for c in args.components.split(",") if c.strip()]
        res = recommend(components=comps, application=args.application, pressure_pa=args.pressure)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=res["documentation_basis"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        write_json(
            result_envelope(skill=SKILL, inputs=vars(args), results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

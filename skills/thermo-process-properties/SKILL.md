---
name: thermo-process-properties
description: >-
  Run Caleb Bell library-backed process property calculations: PR /
  Translated-PR cubic EOS for LPG and light hydrocarbon mixtures, COSTALD
  mixture liquid density (saturated and compressed), IAPWS water/steam
  state, and a transparent property-method recommendation heuristic
  modeled on DWSIM / Aspen / HYSYS / PRO/II guidance. Use when you need a
  defensible property method or density for a process calculation. Don't
  use for full multi-component flash (use vle-flash-calculations), for
  the EOS decision tree by itself (use equation-of-state-selection), or
  for steam-only systems (use steam-tables-iapws).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, thermodynamics, thermo, process, properties]
    category: thermodynamics
---

# Thermodynamic Property Calculations

## Overview

Caleb Bell library wrapper utilities. Implements:

- `recommend`: property-method recommendation given components and
  application context.
- `costald-density`: COSTALD (saturated) or COSTALD_compressed mixture
  liquid density for light hydrocarbons.
- `pr-translated-eos`: instantiate `thermo.eos_mix.PRMIXTranslatedPPJP`
  with reported molar volumes, Z-factors, and departure functions.
- `iapws-state` / `iapws-saturation`: pure water / steam properties.

Heuristics for method selection are transparent and built from public
sources (DWSIM, Carlson, AVEVA / Aspen training material). No
proprietary defaults are reproduced.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt` listing
   the upstream library terms.

## When to Use

- Picking a property method for a flowsheet zone.
- Estimating LPG liquid density at storage / vessel conditions (COSTALD).
- Getting a Translated-PR liquid molar volume for an LPG mixture.
- Pure-water / steam state at known T, P.

## Don't use for

- Multi-component flash (`vle-flash-calculations`).
- EOS decision tree by itself (`equation-of-state-selection`).
- Steam-table-only calculations (`steam-tables-iapws`).
- Non-LPG hydrocarbon systems where COSTALD is outside its accuracy
  envelope.

## Utility Scripts

- `uv run scripts/property_methods.py recommend --components propane,n-butane,isobutane --application LPG --pressure-pa 1200000 --output /tmp/method.json`
- `uv run scripts/property_methods.py costald-density --components propane,n-butane --zs 0.5,0.5 --temperature-k 300 --pressure-pa 1000000 --output /tmp/lpg_density.json`
- `uv run scripts/property_methods.py iapws-state --temperature-k 373.15 --pressure-pa 101325 --output /tmp/steam.json`
- `uv run scripts/property_methods.py pr-translated-eos --components propane,n-butane --zs 0.5,0.5 --temperature-k 300 --pressure-pa 1000000 --output /tmp/pr.json`

## Procedure

1. Identify components and the operating envelope (T, P, composition).
2. Run `recommend` for a property-method check.
3. For LPG liquid density at vessel conditions, prefer COSTALD compressed.
4. For pure water/steam, prefer IAPWS.
5. For full flash, hand off to `vle-flash-calculations` with the selected
   EOS.

## Pitfalls

- Using PR (default) for LPG liquid density at moderate pressure; PR
  underpredicts liquid density by 5-15%. Use Translated-PR or COSTALD.
- Using COSTALD for a non-light-hydrocarbon (water, alcohol, amine);
  COSTALD is accurate only for nonpolar light hydrocarbons.
- Using IAPWS for water-in-hydrocarbon systems; IAPWS is pure water only.
- Passing the kij matrix as zeros for a sour LPG mixture; H2S / mercaptan
  / amine interactions need real kij.
- Confusing mass density (kg/m³) with molar volume (m³/mol).
- Treating the PRMIXTranslatedPPJP molar volume as exact without
  providing the per-component translation constants `cs`.
- Using `recommend` output as a final decision without doing the
  second-opinion flash recommended by the decision-tree.
- Treating water-content trace as negligible without checking with a
  hydrate / glycol skill.

## Fallback Strategies

- If `thermo` / `chemicals` import fails for an exotic component, fall
  back to built-in LPG defaults via `engg_skills_common.property_backends`.
- For density that is wildly off, switch from COSTALD to
  PRMIXTranslatedPPJP (or vice versa) and report both.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/property_method_selection.md` — full method matrix.
- `references/caleb_bell_libraries.md` — library overview and links.
- `thermo` docs: https://thermo.readthedocs.io/
- `chemicals` docs: https://chemicals.readthedocs.io/
- DWSIM property package selection wiki.

## Anti-Patterns

- Reporting properties without naming the EOS or correlation.
- Using cubic EOS for steam.
- Reporting LPG liquid density without naming whether COSTALD or PR was
  used.

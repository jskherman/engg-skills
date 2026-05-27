---
name: thermo-process-properties
description: >-
  Use Caleb Bell's thermo, chemicals, fluids, and ht ecosystem for process-property calculations when a full GUI simulator is unavailable. Includes LPG cubic-EOS/COSTALD workflows, IAPWS water/steam properties, and simulator-inspired property-method selection heuristics.
---

# Thermodynamic and Transport Property Calculations

## Overview

Use this skill for Python-based process simulation support with Caleb Bell's libraries:

- `thermo` for chemical constants, cubic EOS objects, flash calculations, and IAPWS phase classes.
- `chemicals` for correlations including COSTALD and IAPWS-95 utilities.
- `fluids` for hydraulics and pressure-drop correlations.
- `ht` for heat-transfer correlations, LMTD, correction factors, and NTU/effectiveness workflows.

## Core Rules

- Use dedicated IAPWS water/steam methods for water and steam; do not default to cubic EOS.
- For LPG/light-hydrocarbon processing, use cubic EOS workflows for VLE and COSTALD for liquid density when appropriate.
- For `thermo.eos_mix.PRMIXTranslatedPPJP`, explicitly track critical properties, acentric factors, binary interaction parameters, and volume-translation constants.
- Always state units, basis, property method, data source, and warnings.
- Treat outputs as preliminary; validate against lab data, plant data, or trusted simulator results before design use.

## Utility Scripts

- `uv run scripts/property_methods.py recommend --components propane,n-butane,isobutane --application LPG --pressure-pa 1200000 --output /tmp/method.json`
- `uv run scripts/property_methods.py costald-density --components propane,n-butane --zs 0.5,0.5 --temperature-k 300 --pressure-pa 1000000 --output /tmp/lpg_density.json`
- `uv run scripts/property_methods.py iapws-state --temperature-k 373.15 --pressure-pa 101325 --output /tmp/steam.json`
- `uv run scripts/property_methods.py pr-translated-eos --components propane,n-butane --zs 0.5,0.5 --temperature-k 300 --pressure-pa 1000000 --output /tmp/pr.json`

## Simulator-Inspired Heuristics

- Water/steam utility systems: IAPWS/steam tables.
- Nonpolar hydrocarbons at elevated pressure: Peng-Robinson/SRK-style cubic EOS, with BIP checks.
- LPG liquid density: COSTALD mixture/compressed density is often a good screening method for light hydrocarbons.
- Polar liquid systems: activity-coefficient models such as NRTL/UNIQUAC/UNIFAC when parameters are available.
- Electrolytes, amines, glycols, sour water, hydrates, and reactive systems: specialized models/packages; do not oversimplify.

## Anti-Patterns

- Assuming Aspen/HYSYS/PRO/II/DWSIM defaults without stating the selected property package.
- Using cubic EOS for steam-table utility calculations.
- Reporting LPG density without specifying whether it is saturated/compressed, liquid/vapor, and mass/molar basis.
- Ignoring binary interaction parameters and volume translation for cubic EOS.

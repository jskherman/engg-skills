---
name: process-units-conversion
description: >-
  Convert chemical/process engineering quantities between SI, US Customary,
  CGS, and mixed-unit forms with explicit dimensional checks. Use when an
  input is given in non-SI units or when an output needs to be reported in
  a different unit system. Don't use as a substitute for a property
  calculation (use thermo-process-properties or vle-flash-calculations);
  unit conversion only converts magnitudes, not properties that depend on
  T, P, or composition.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, thermodynamics, process, units, conversion]
    category: thermodynamics
---

# Process Units Conversion

## Overview

Deterministic unit conversions for the common process-engineering
quantities (flow, pressure, viscosity, thermal conductivity, energy,
temperature, length, area, volume, density, mass). All calculations are
SI under the hood; converting to or from a non-SI unit goes through the
SI value.

## Prerequisites

1. `uv` available.

## When to Use

- An input is given in psia, bar, lbm/hr, gpm, cP, ft, in, etc., and you
  need SI before calling another skill.
- The user requests output in non-SI units (e.g. shop-floor reporting).
- You need to sanity-check a vendor data sheet expressed in mixed units.

## Don't use for

- Computing properties that depend on state (density, viscosity, heat
  capacity) — those need a property package (`thermo-process-properties`).
- Currency, financial, or non-physical conversions.
- Unit groups that are NOT pure conversions (e.g. API gravity to density
  depends on water reference; check the underlying definition).

## Utility Scripts

- `uv run scripts/convert_units.py convert --value 100 --from-unit psi --to-unit Pa --output /tmp/p.json`
- `uv run scripts/convert_units.py convert --value 2.5 --from-unit gpm --to-unit m3_s --output /tmp/q.json`
- `uv run scripts/convert_units.py list-units --output /tmp/units.json`

## Procedure

1. Identify the source unit and the target unit.
2. Confirm the conversion is purely dimensional (no T/P/composition
   dependence).
3. Run the script; inspect the JSON for the SI value as well.
4. If the result is suspicious (off by a factor of 10), check whether you
   confused similar units (e.g. psia vs psig, bar vs barg, mol/h vs kmol/h).

## Pitfalls

- Treating gauge pressure (psig, barg) as absolute (psia, bara). The skill
  is unit-of-quantity, not gauge-vs-absolute; you must subtract / add
  atmospheric pressure yourself.
- Mixing mass and molar flow ("kg/s vs kmol/s"); they are different
  dimensions and the skill will refuse them.
- Treating "Bbl" or "STB" without specifying the reference (oil vs water).
- Treating Celsius and Kelvin as interchangeable for delta-T calculations
  (they are; for absolute, they are not). Convert intentionally.
- Treating cP and cSt as the same; cP is dynamic viscosity, cSt is
  kinematic viscosity (= dynamic / density).
- Converting GPM to m³/s and forgetting US-vs-Imperial gallons.
- Inputting flow in "mol%" when the schema expects mole fraction.
- Reporting a converted value with more digits than the source warrants.

## Fallback Strategies

- If the requested unit is not in the registry, surface to the user; do
  NOT guess the conversion factor.
- For non-trivial conversions (e.g. API gravity, gas SCF at standard
  conditions), use a dedicated property routine instead.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/unit_conventions.md` — supported quantities and units.

## Anti-Patterns

- Embedding a "convenient" conversion factor in another script instead of
  routing through this skill.
- Reporting bar and psi values together without naming gauge vs absolute.

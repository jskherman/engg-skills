---
name: heat-exchanger-sizing
description: >-
  LMTD-based duty and area estimate for counter- or co-current heat
  exchangers, with optional multi-pass F-factor correction (via `ht`).
  Use when sizing a new exchanger or sanity-checking an existing one with
  known U. Don't use for rigorous Bell-Delaware shell-side analysis,
  rate-based two-phase boiling/condensation design, or for an unknown U
  (compute h on each side first via convective-heat-transfer-correlations).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, fluid-flow, heat-transfer, heat, exchanger, sizing]
    category: fluid-flow-heat-transfer
---

# Heat Exchanger Sizing (LMTD)

## Overview

LMTD-based duty and area calculation for a known overall heat transfer
coefficient U. Counter-current or co-current; multi-pass F-factor via the
`ht` library. Duty can be computed from terminal temperatures or supplied
explicitly.

## Prerequisites

1. `uv` available.

## When to Use

- Sizing a new exchanger when you have a defensible U value (vendor data,
  prior project) and terminal temperatures.
- Sanity-checking an existing exchanger for new conditions.

## Don't use for

- Bell-Delaware shell-side design with detailed baffle / bundle
  configuration.
- Rate-based two-phase boiling or condensation (use a vendor or
  specialized tool).
- Calculating U from first principles when h on either side is unknown
  (use `convective-heat-transfer-correlations` first).

## Utility Scripts

- `uv run scripts/size_heat_exchanger.py --hot-in-c 150 --hot-out-c 90 --cold-in-c 25 --cold-out-c 90 --arrangement counterflow --u-w-m2-k 500 --duty-w 1e6 --output /tmp/hx.json`

## Procedure

1. Define hot/cold inlet and outlet temperatures (°C for the bundled script).
2. Decide arrangement: counterflow (preferred), co-current, or
   multi-pass with F-factor.
3. Estimate U from either side's h (or vendor data); typical ranges:
   liquid-liquid 300-1000 W/m²K, liquid-gas 30-100, condensing steam
   2000-5000, boiling 1000-4000.
4. Provide duty from one stream's sensible heat (m × cp × ΔT) or pass
   the value if known.
5. Run the script. Inspect area; round up to the nearest commercial
   bundle size.
6. Cross-check by computing the other stream's duty and verifying the
   energy balance closes.

## Pitfalls

- Using bare LMTD without the F-factor for multi-pass exchangers.
- Picking U from a textbook table without flagging the fouling
  factor (overstates U).
- Forgetting that LMTD blows up to ±infinity when terminal differences
  approach zero (temperature pinch).
- Using sensible-heat duty for a two-phase service (latent heat
  dominates).
- Reporting required area without acknowledging the fouling allowance.
- Choosing LMTD when one stream is isothermal (condensing / boiling) and
  using F = 1 by default. Even for single-phase the F-factor is < 1 for
  multi-pass.
- Picking shell-and-tube as default; for liquid-liquid services with low
  fouling, a plate-and-frame is often smaller and cheaper.
- Treating the calculated area as final without vendor-validated TEMA
  layout and pressure-drop check.

## Fallback Strategies

- If `ht.LMTD` is unavailable, the script falls back to the direct LMTD
  formula and flags the substitution.
- If only one stream's enthalpy data is supplied, the script computes the
  matching cold/hot side from the energy balance, but only when
  arrangement allows it.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/methods.md` — assumptions, formulas, and U ranges.
- TEMA standards (procure separately).
- Sinnott / Coulson & Richardson Vol 6 for U guidance.

## Anti-Patterns

- Reporting required area without specifying U and fouling factors.
- Using LMTD with widely different specific heats across the exchanger
  (Cp varies strongly with T).
- Sizing without checking the temperature pinch.

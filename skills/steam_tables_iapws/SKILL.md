---
name: steam-tables-iapws
description: >-
  Compute water and steam thermodynamic and transport properties using
  the IAPWS-95 / IAPWS-IF97 formulation (via `chemicals.iapws`). Use when
  any calculation involves pure water or steam (turbine, boiler,
  condensate, reboiler, BFW system). Don't use for hydrocarbon systems
  (use vle-flash-calculations or thermo-process-properties), water +
  hydrocarbon two-phase systems (different physics), or supercritical CO2
  power cycles (use a CO2-specific equation of state).
---

# IAPWS Steam Tables

## Overview

Water / steam properties via the IAPWS-95 scientific formulation
(industrial work usually uses IAPWS-IF97). Implemented through
`chemicals.iapws`:

- Single-phase state (T, P): density, enthalpy, entropy, internal
  energy, Cp, Cv, speed of sound, Joule-Thomson coefficient.
- Saturation: `Psat(T)` and `Tsat(P)`.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt` listing
   the IAPWS terms.

## Use when

- Sizing a steam turbine, condenser, or reboiler.
- BFW or condensate stream property work.
- Computing steam quality / vapor fraction for a flash drum on pure water.

## Don't use for

- Hydrocarbon systems — use `vle-flash-calculations`.
- Water + hydrocarbon two-phase systems — neither IAPWS nor plain cubic
  EOS handles them well in isolation.
- Supercritical CO2 — use a CO2 EOS (Span-Wagner).

## Utility Scripts

The IAPWS subcommands live in the `thermo-process-properties` skill:

- `uv run scripts/property_methods.py iapws-state --temperature-k 773 --pressure-pa 1e7 --output /tmp/steam.json`
- `uv run scripts/property_methods.py iapws-saturation --temperature-k 423 --output /tmp/sat.json`

## Workflow

1. Identify the state (T, P, or T + quality).
2. Call the appropriate subcommand.
3. Inspect the returned properties; if any value seems unphysical,
   recheck T and P bounds against the IAPWS validity range.

## Common Mistakes

- Confusing IAPWS-95 (scientific, full phase diagram, accurate near
  critical point) with IAPWS-IF97 (industrial, faster, small region
  discontinuities). For simulation use IF97; for high accuracy near
  critical, use IAPWS-95.
- Treating the IAPWS Psat at the saturation curve as exact; the
  formulation is accurate, but the calling code must be careful with
  rounding near saturation.
- Using IAPWS for sea water or brackish water — salt is not in the
  formulation.
- Using cubic EOS for water/steam utility work — IAPWS is the industry
  reference.
- Mixing kJ/kg (common in steam tables) with J/kg (the IAPWS native);
  the script reports both bases.
- Reporting steam quality in a flash with a non-water hydrocarbon trace
  contamination; IAPWS is pure-water only.

## Fallback Strategies

- If `chemicals.iapws` is unavailable, surface to the user that no
  fallback is available; do not attempt to substitute a cubic EOS.

## References

- `references/iapws_notes.md` — region boundaries and validity ranges.
- IAPWS releases: https://iapws.org/
- `chemicals.iapws` docs: https://chemicals.readthedocs.io/chemicals.iapws.html

## Anti-Patterns

- Using IAPWS for any non-water system.
- Quoting steam properties to four decimal places without naming the
  underlying formulation.
- Mixing IF97 and IAPWS-95 within the same calculation without naming the
  switch.

---
name: relief-valve-sizing-api520
description: >-
  Preliminary pressure-relief device orifice area for gas/vapor or liquid
  service using API 520 Part I sizing equations. Use only for early screening
  of relief loads, comparing scenarios, and sanity-checking vendor sizing.
  Don't use for final design (which requires the authoritative API 520/521/526
  text and qualified relief engineering), for two-phase / flashing relief
  (DIERS methodology), or for fire-case relief load development (use API 521 to
  establish the load first).
---

# API 520 Pressure-Relief Sizing (Preliminary)

## Overview

Implements the gas/vapor (critical and sub-critical) and liquid forms of the
API 520 Part I sizing equations as preliminary screening. The standard's
correction factors are user-supplied:

- `Kd` — effective coefficient of discharge.
- `Kb` — gas/vapor balanced-bellows backpressure correction.
- `Kw` — liquid balanced-bellows backpressure correction.
- `Kc` — rupture-disk combination correction when applicable.
- `Kv` — liquid viscosity correction.

The script does not embed the standard's correction charts or vendor-specific
limits.

## Safety Scope

This skill produces a **preliminary, screening-grade** required orifice area.
Final relief device selection, certification (NB-7), inlet/outlet piping
pressure-drop checks, blowdown system back-pressure analysis, and compliance
with ASME BPVC Section VIII / Section XIII and jurisdictional codes require the
authoritative API 520/521/526 text, vendor data, and qualified pressure-relief
engineering review.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt` listing the
   referenced standards (titles only).

## Use when

- Screening the order-of-magnitude orifice area for a relief case.
- Comparing several scenarios (blocked discharge, fire, thermal, tube rupture).
- Cross-checking vendor or simulator output before issuing a PR specification.

## Don't use for

- Final design / certification.
- Two-phase or flashing relief: use DIERS-style methodology. The script will
  not warn you if your scenario is actually two-phase.
- Fire case relief load calculation: use API 521 to establish the fire heat
  input and relief load before using this sizing helper.

## Utility Scripts

- `uv run scripts/api520.py gas --m 2.5 --T-K 320 --MW 44.1 --gamma 1.13 --Z 0.95 --P1 1500000 --Pb 200000 --Kd 0.975 --output /tmp/gas.json`
- `uv run scripts/api520.py liquid --Q 0.005 --rho 800 --P1 2500000 --Pb 200000 --Kd 0.65 --output /tmp/liq.json`

## Workflow

1. Identify the relief scenario (blocked discharge, fire, thermal expansion,
   tube rupture, etc.) and the controlling case.
2. Compute the relief load `W` (gas/vapor mass flow) or `Q` (liquid volumetric
   flow) using a separate scenario analysis (not in this skill).
3. Identify upstream relieving conditions: pressure, temperature, gas properties
   (MW, Z, gamma), or liquid properties (density, viscosity if needed).
4. Identify back-pressure conditions: built-up and superimposed back-pressure
   into the flare/atmosphere.
5. Choose `Kd` from the vendor certification or conservative screening defaults
   (typical screening: gas/vapor 0.975, liquid 0.65). Apply `Kb` only for
   gas/vapor balanced-bellows backpressure correction, `Kw` only for liquid
   balanced-bellows backpressure correction, `Kv` for liquid viscosity, and `Kc`
   for rupture-disk combination service.
6. Run the script; round the orifice area UP to the nearest API 526 orifice
   designation (D, E, F, G, H, J, K, L, M, N, P, Q, R, T).
7. Verify the inlet line pressure drop against API 520 and company criteria.
8. Verify the total back-pressure and corrected capacity remain within the valve
   type and vendor envelope.

## Common Mistakes

- Using molecular weight in kg/mol instead of g/mol / kg/kmol.
- Treating the relief load (W or Q) as exact; it is the dominant uncertainty in
  many relief-sizing checks.
- Applying gas/vapor `Kb` to all conventional spring PRVs. Use `Kb = 1` unless a
  balanced-bellows correction is being applied from the standard or vendor data.
- Applying liquid `Kw` to gas/vapor service or gas/vapor `Kb` to liquid service.
- Using `Kd = 1.0` because the manufacturer has not been chosen; use certified
  vendor data for final design and conservative screening defaults before then.
- Sizing for set pressure instead of relieving pressure.
- Treating gas relief as critical when `Pb / P1` exceeds the critical ratio for a
  conventional or pilot-operated valve.
- Sizing for the wrong fluid state (vapor instead of two-phase for boiling,
  flashing, or entraining service).
- Ignoring rupture-disk combination correction `Kc` when applicable.

## Fallback Strategies

- Two-phase / flashing relief is OUTSIDE this skill's scope. State that
  DIERS-style methodology is needed.
- If the scenario load is unknown, stop; do not guess.

## References

- `references/api520_equations.md` — equation forms used.
- `references/typical_kd_values.md` — typical Kd ranges (Vendor data needed for
  final design).
- API 520 Part I — Sizing, Selection, and Installation of Pressure-Relieving
  Devices.
- API 521 — Pressure-Relieving and Depressuring Systems (for the load side).
- API 526 — Flanged Steel Pressure-Relief Valves (orifice designations).

## Anti-Patterns

- Reporting an orifice in mm² without naming the API 526 designation.
- Sizing PRV without documenting the controlling scenario and the relief load
  source.
- Using this skill output to specify the valve directly to the vendor.
- Skipping inlet-line pressure-drop, outlet back-pressure, and reaction-force
  checks.

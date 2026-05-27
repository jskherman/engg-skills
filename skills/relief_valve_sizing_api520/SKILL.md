---
name: relief-valve-sizing-api520
description: >-
  Preliminary pressure-relief device orifice area for gas/vapor or liquid
  service using the API 520 Part I form of the sizing equation. Use only for
  early screening of relief loads, comparing scenarios, and sanity-checking
  vendor sizing. Don't use for final design (which requires the authoritative
  API 520/521/526 text and qualified relief engineering), for two-phase /
  flashing relief (DIERS methodology), or for fire-case relief loads (use
  API 521 procedure to size the load first).
---

# API 520 Pressure-Relief Sizing (Preliminary)

## Overview

Implements the gas/vapor (critical and sub-critical) and liquid forms of the
API 520 Part I sizing equation as preliminary screening. The standard's
constants (discharge coefficient `Kd`, back-pressure correction `Kb` /
viscosity correction `Kv`, capacity correction `Kc`) are user-supplied; the
script does not embed the published charts.

## Safety Scope

This skill produces a **preliminary, screening-grade** required orifice
area. Final relief device selection, certification (NB-7), inlet/outlet
piping pressure-drop checks, blowdown system back-pressure analysis, and
compliance with ASME BPVC Section VIII / Section XIII and jurisdictional
codes require the authoritative API 520/521/526 text, vendor data, and
qualified pressure-relief engineering review.

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
- Two-phase or flashing relief: use the DIERS methodology with the
  Omega-method or HEM. The script will not warn you if your scenario is
  actually two-phase.
- Fire case relief load calculation (`Q` for the equation): use API 521 with
  the vessel surface area in the fire zone and the chosen correlation
  (API 521 §4 / §5).

## Utility Scripts

- `uv run scripts/api520.py gas --m 2.5 --T-K 320 --MW 44.1 --gamma 1.13 --Z 0.95 --P1 1500000 --Pb 200000 --Kd 0.975 --output /tmp/gas.json`
- `uv run scripts/api520.py liquid --Q 0.005 --rho 800 --P1 2500000 --Pb 200000 --Kd 0.65 --output /tmp/liq.json`

## Workflow

1. Identify the relief scenario (blocked discharge, fire, thermal expansion,
   tube rupture, etc.) and the controlling case.
2. Compute the relief load `W` (gas/vapor mass flow) or `Q` (liquid
   volumetric flow) using a separate scenario analysis (not in this skill).
3. Identify upstream relieving conditions: pressure (per ASME), temperature,
   gas properties (MW, Z, gamma).
4. Identify back-pressure conditions: built-up and superimposed back-pressure
   into the flare/atmosphere.
5. Choose discharge coefficient `Kd` from the vendor certification
   (typical: gas 0.975, liquid 0.65) and corrections `Kb`, `Kv`, `Kc`.
6. Run the script; round the orifice area UP to the nearest API 526 orifice
   designation (D, E, F, G, H, J, K, L, M, N, P, Q, R, T).
7. Verify the inlet line pressure drop ≤ 3% of set pressure (API 520 limit).
8. Verify the back-pressure on a balanced bellows or pilot-operated valve
   is within vendor envelope.

## Common Mistakes

- Using molecular weight in g/mol vs kg/mol inconsistently.
- Treating the relief load (W or Q) as exact; it is the dominant uncertainty
  in any relief sizing.
- Forgetting the back-pressure correction `Kb` for conventional spring
  relief valves (must be < 1 when built-up back-pressure exceeds 10% of set).
- Using `Kd = 1.0` because the manufacturer hasn't been chosen; ASME requires
  `Kd ≤ 0.975` (gas) or `Kd ≤ 0.65` (liquid) for design until certified.
- Sizing for ASME P_set instead of P_relieving (typically 110% of P_set for
  non-fire, 121% for fire / multiple).
- Treating gas relief as critical when Pb / P1 exceeds the critical ratio
  (script flags subcritical).
- Sizing for the wrong fluid (vapor instead of two-phase for boiling reflux
  flash).
- Ignoring rupture-disk in series, which reduces effective Kd by 0.9.
- Ignoring `Kc = 0.9` when the PRV is downstream of a non-reclosing
  pressure-relief device combination.

## Fallback Strategies

- Two-phase / flashing relief is OUTSIDE this skill's scope. Surface to the
  user that DIERS-style methodology is needed.
- If you do not know the scenario load, surface to the user; do NOT guess.

## References

- `references/api520_equations.md` — equation forms used.
- `references/typical_kd_values.md` — typical Kd ranges (Vendor data needed
  for final design).
- API 520 Part I — Sizing, Selection, and Installation of Pressure-Relieving
  Devices.
- API 521 — Pressure-Relieving and Depressuring Systems (for the load side).
- API 526 — Flanged Steel Pressure-Relief Valves (orifice designations).

## Anti-Patterns

- Reporting an orifice in mm² without naming the API 526 designation.
- Sizing PRV without documenting the controlling scenario and the relief
  load source.
- Using this skill output to specify the valve directly to the vendor.
- Skipping the inlet-line pressure-drop check.

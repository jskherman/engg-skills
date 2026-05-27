---
name: pipe-flow-pressure-drop
description: >-
  Estimate single-phase incompressible pipe pressure drop, Reynolds number,
  Darcy friction factor, and head loss for steady flow in straight runs.
  Use when sizing a pump line, checking line size, or screening pressure
  drop in straight pipes. Don't use for two-phase flow (use
  two-phase-flow), compressible / choked flow, or fittings/valves pressure
  drop (use a K-factor or Crane TP-410 method).
---

# Single-Phase Pipe Pressure Drop

## Overview

Computes Darcy-Weisbach pressure drop with the Clamond friction factor
(via `fluids`) as primary, and the Haaland explicit form as fallback when
`fluids` is unavailable or fails. Outputs include Re, friction factor f,
velocity, head loss, and pressure drop.

## Prerequisites

1. `uv` available.

## Use when

- Sizing a pump suction or discharge line.
- Checking line size given a design flow.
- Screening pressure drop across a long straight run before adding
  fittings.

## Don't use for

- Two-phase flow (`two-phase-flow`).
- Compressible / choked gas flow.
- Pressure drop across fittings, valves, expansions, contractions (those
  need K factors).
- Non-Newtonian fluids.

## Utility Scripts

- `uv run scripts/pipe_pressure_drop.py --length-m 100 --diameter-m 0.05 --flow-m3-s 0.002 --density-kg-m3 998 --viscosity-pa-s 0.001 --roughness-m 1.5e-6 --output /tmp/pdrop.json`

## Workflow

1. Get fluid density and viscosity at the operating temperature.
2. Pick the pipe inside diameter (after accounting for wall thickness and
   schedule).
3. Pick the pipe absolute roughness (commercial steel ~ 45 μm, drawn
   tubing ~ 1.5 μm, PE ~ 0.0015 mm).
4. Run the script. The output reports Re; check that the flow is in the
   regime you expect.
5. Add fitting / valve K-factor losses separately if needed.
6. If the pressure drop is large, iterate to a larger diameter and rerun.

## Common Mistakes

- Using nominal pipe diameter instead of the inside diameter for a given
  schedule.
- Using roughness too low (e.g. ε = 0 for smooth pipe) for commercial
  steel.
- Forgetting elevation change; this skill returns frictional dP only.
- Treating the result as the total dP across a system (it omits fittings,
  valves, and entrance/exit losses).
- Using water properties for a hydrocarbon line.
- Mixing kinematic and dynamic viscosity.
- Reporting head loss in meters of water when the fluid is something else.
- Using the formula in the transitional regime (2300 < Re < 4000) without
  acknowledging the uncertainty band.

## Fallback Strategies

- If `fluids` is missing, the script falls back to Haaland explicitly and
  flags the substitution in the JSON output.
- If the calculated Re is borderline transitional, the script attaches a
  warning so downstream design margins can be increased.

## References

- `references/limitations.md` — full assumption list.
- Crane TP-410 (procure separately) for fittings / valve K-factors.

## Anti-Patterns

- Designing a pipe with an estimated dP and zero margin.
- Reporting Δp in psi without naming whether it is gauge or absolute (it
  is a Δ, but the reader still needs to know the basis).
- Using this skill for the long-run flare line where two-phase or
  compressible effects matter.

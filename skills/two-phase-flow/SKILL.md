---
name: two-phase-flow
description: >-
  Estimate frictional pressure drop for gas-liquid two-phase pipe flow using
  Lockhart-Martinelli (horizontal), Beggs-Brill (inclined, all angles), or
  Mueller-Steinhagen-Heck (smooth quality interpolation). Use when sizing
  flare lines, two-phase risers, knock-out drum inlets, or boiler-tube
  pressure drop. Don't use for single-phase pipe flow (use
  pipe-flow-pressure-drop), or for choked / sonic flow (different physics).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, fluid-flow, heat-transfer, two, phase, flow]
    category: fluid-flow-heat-transfer
---

# Two-Phase Pressure Drop

## Overview

Three established gas-liquid two-phase pressure-drop correlations from the
`fluids.two_phase` module. Each correlation has its strengths:

- **Lockhart-Martinelli**: classical horizontal, widely cited, ±30% typical.
- **Beggs-Brill**: handles inclination (essential for risers, hilly
  pipelines).
- **Mueller-Steinhagen-Heck**: smooth interpolation between all-liquid and
  all-vapor frictional gradients; recommended starting point for
  refrigerant evaporator design.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt` listing the
   `fluids` library terms.

## When to Use

- Two-phase frictional pressure drop is needed in a pipe (flare, reboiler
  return, riser, knock-out drum inlet, slug catcher manifold).
- Comparing two correlations to bracket the design pressure drop.

## Don't use for

- Single-phase pipe flow — use `pipe-flow-pressure-drop`.
- Choked / sonic flow at a relief valve outlet — use `relief-valve-sizing-api520`.
- Two-phase across a control valve — use `control-valve-sizing-isa75` with
  flashing/cavitation indices.

## Utility Scripts

- `uv run scripts/two_phase.py lm --m 5.0 --quality 0.3 --rho-l 600 --rho-g 30 --mu-l 0.0002 --mu-g 1.0e-5 --D 0.1 --L 50 --output /tmp/lm.json`
- `uv run scripts/two_phase.py beggs-brill --m 5.0 --quality 0.3 --rho-l 600 --rho-g 30 --mu-l 0.0002 --mu-g 1.0e-5 --sigma 0.02 --P 1000000 --D 0.1 --L 50 --angle 30 --output /tmp/bb.json`
- `uv run scripts/two_phase.py msh --m 5.0 --quality 0.3 --rho-l 600 --rho-g 30 --mu-l 0.0002 --mu-g 1.0e-5 --D 0.1 --L 50 --output /tmp/msh.json`

## Procedure

1. Establish phase mass flow rates and quality `x = m_g / (m_g + m_l)`.
2. Get phase densities and viscosities at operating conditions (use
   `vle-flash-calculations` if needed).
3. Pick a correlation:
   - Horizontal, dilute liquid: Lockhart-Martinelli.
   - Inclined, any angle, oil/gas pipeline: Beggs-Brill.
   - Refrigerant / process evaporator, smooth quality range: Mueller-
     Steinhagen-Heck.
4. Run two correlations and compare; use the higher dP for the design
   margin unless one is clearly outside its validity range.

## Pitfalls

- Using a single-phase friction factor on a two-phase stream.
- Treating the slip ratio as 1 (homogeneous) for high-quality steam — fine
  for refrigerant boiling, not for low-pressure flashing systems.
- Ignoring vapor density variation along the pipe; for long lines the
  acceleration term can dominate at the outlet.
- Picking Lockhart-Martinelli for a vertical riser; it does not include
  gravity head.
- Picking Beggs-Brill horizontal mode at 0° without verifying the
  correlation switches to the appropriate flow regime.
- Forgetting that quality changes when heat is added or pressure drops
  (flashing or condensing). The correlations assume a constant quality over
  the pipe length L; for large dP / large dT, segment the pipe.
- Reporting only one correlation's number; a 2x spread between correlations
  is normal for two-phase flow.
- Using these correlations for entrained-droplet flow at high vapor velocity
  with a demister downstream; entrainment loading matters and is not in the
  correlation.

## Fallback Strategies

- If `fluids` is not installed, escalate to the user; there is no clean
  pure-Python fallback for Beggs-Brill that captures all flow regimes.
- For very high quality (x → 1), the Lockhart-Martinelli parameter X
  approaches 0 and the correlation degrades; switch to a homogeneous-flow
  approximation or to Mueller-Steinhagen-Heck.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/correlation_choice.md` — when each correlation is most suitable.
- Beggs & Brill, *Two-Phase Flow in Pipes* (Univ Tulsa Press, 1991).
- Lockhart & Martinelli, *Chem Eng Prog* 45, 1949.
- Mueller-Steinhagen & Heck, *Chem Eng Proc* 20, 1986.
- `fluids` documentation: https://fluids.readthedocs.io/fluids.two_phase.html

## Anti-Patterns

- Picking one correlation and not documenting why.
- Designing a flare line without checking back-pressure on multiple PRV
  cases.
- Treating two-phase dP as if it were 1.2x single-phase dP — that
  shortcut fails dramatically in slug flow.

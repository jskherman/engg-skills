---
name: material-energy-balances
description: >-
  Compute steady-state component and total mass balance residuals,
  conversion / selectivity / yield, and degree-of-freedom counts for a
  process node. Use when checking that a stream table closes or sanity-
  checking a simulation export. Don't use for dynamic / transient
  balances (different math; use a state-space solver) or as a substitute
  for a flowsheet simulator's rigorous closure.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, material, energy, balances]
    category: process-engineering
---

# Material and Energy Balances

## Overview

Steady-state balance helpers:

- Component mass balance residual for one node (inlets - outlets, summed
  per component).
- Total mass balance residual.
- Conversion, selectivity, yield computed from inlet/outlet component
  flows.
- Degree-of-freedom (DoF) counter for a node, given the number of streams,
  components, and specifications.

## Prerequisites

1. `uv` available.

## When to Use

- Checking that a hand-built stream table closes.
- Sanity-checking a flowsheet export (mole or mass basis).
- Counting unknowns vs equations before deciding whether the problem is
  solvable.

## Don't use for

- Transient (dynamic) balances; the math involves dC/dt and requires a
  state-space approach.
- Rigorous flowsheet convergence; use a simulator.
- Detailed equilibrium / reactor design; this skill is balance-only.

## Utility Scripts

- `uv run scripts/balance_solver.py --inlets "feed:A=10,B=5" --outlets "vap:A=2,B=1;liq:A=8,B=4" --output /tmp/bal.json`

## Procedure

1. Identify the node and its streams.
2. List inlets and outlets with per-component flow rates (mol/s or kg/s,
   consistent basis).
3. Run the script. Inspect the per-component residual.
4. If residual is non-zero, look for: missing recycle, missing stream,
   wrong basis (mol vs mass), or an actual instrument bias.
5. For conversion/selectivity/yield, supply reactant and key product
   flows.

## Pitfalls

- Mixing mass and molar basis silently.
- Forgetting recycle streams.
- Reporting "conversion 97%" without naming the key reactant and the
  basis (per pass vs overall).
- Using yield where you mean selectivity (yield is mol product / mol
  reactant fed; selectivity is mol product / mol reactant reacted).
- Computing residuals only in absolute terms; relative residuals
  (residual / inlet) are usually more useful.
- Using mass balance closure to justify a doubtful instrument when
  energy balance also fails to close.
- Counting equations without subtracting redundant ones (a
  total-balance plus all-component balances over-counts).
- Not propagating measurement uncertainty when judging closure ("looks
  closed at 0.5%" might be within instrument noise).

## Fallback Strategies

- If the residual is large but the data is suspect, suggest data
  reconciliation (Crowe's method or similar).
- For dynamic balances, surface that this skill does not cover them.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/workflow.md` — detailed checklist for a node closure.

## Anti-Patterns

- Reporting a balance that does not close as if it does.
- Hiding the basis in the report.
- Using component balances to detect bias without ruling out leakage,
  recycle, or unmeasured purge.

---
name: material-energy-balances
description: >-
  Compute simple component totals and reaction conversion / yield metrics for
  steady-state process calculations. Use when summing stream component
  amounts or sanity-checking reaction metrics. Don't use for full inlet/outlet
  balance residuals, degree-of-freedom analysis, dynamic / transient balances,
  or as a substitute for a flowsheet simulator's rigorous closure.
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

Steady-state helper calculations:

- Component totals from one or more `NAME=amount` entries.
- Conversion and yield from supplied limiting-reactant and product amounts.
- JSON envelopes that make the basis and assumptions explicit.

## Prerequisites

1. `uv` available.

## When to Use

- Summing component amounts from a hand-built stream table.
- Sanity-checking a single stream or component set on a consistent basis.
- Computing rough conversion and yield metrics from known feed/reacted/product
  amounts.

## Don't use for

- Transient (dynamic) balances; the math involves dC/dt and requires a
  state-space approach.
- Rigorous flowsheet convergence; use a simulator.
- Detailed equilibrium / reactor design; this skill is balance-only.
- Full node closure with separate inlet and outlet stream tables.
- Degree-of-freedom counting.
- Selectivity calculations; only conversion and yield are exposed by the CLI.

## Utility Scripts

- `uv run scripts/balance_solver.py component-total --stream A=10 --stream B=5 --output /tmp/total.json`
- `uv run scripts/balance_solver.py reaction-metrics --feed-limiting 10 --reacted-limiting 8 --desired-product 7.2 --theoretical-product 8 --output /tmp/reaction.json`

## Procedure

1. Identify the stream, component set, or reaction metric you need.
2. Keep all values on a consistent molar or mass basis.
3. For totals, pass each component amount as a repeated `--stream NAME=amount`.
4. For conversion/yield, supply limiting-reactant feed, reacted amount,
   desired product amount, and theoretical product amount.
5. Inspect the JSON assumptions before using the result in a larger balance.

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

---
name: absorption-stripping-design
description: >-
  Apply the Kremser absorption/stripping factor method for dilute systems and
  packed/tray column HETP / efficiency screening. Use when sizing an
  absorber or stripper, estimating per-stage performance for a dilute solute,
  or sanity-checking a vendor sizing. Don't use for reactive absorption with
  chemical equilibrium (use sour-gas-amine-treating), highly concentrated
  systems (Kremser assumes dilute), or rate-based packed-column design with
  detailed mass-transfer correlations.
---

# Absorption and Stripping Shortcut Design

## Overview

Implements the Kremser equation and helpers for stage counting in dilute
absorber/stripper systems. The Kremser formulation is exact for systems with
constant absorption factor `A = L / (K V)` and a linear equilibrium
relationship `y* = K x`.

For concentrated systems, reactive absorbers, or rate-based design, use a
rigorous simulator or rate-based correlation; this skill is screening only.

## Prerequisites

1. `uv` available.
2. On first use the script writes `LICENSE_NOTIFICATION.txt`.

## Use when

- Sizing a dilute absorber (lean oil, glycol dehydrator screening, dilute
  acid-gas scrubber).
- Estimating the stripping factor and stage count for a desorber.
- Cross-checking vendor sizing for a tray or packed column.

## Don't use for

- Reactive absorption with chemical equilibrium (DEA/MDEA + acid gas):
  use `sour-gas-amine-treating` for screening or a rate-based simulator.
- Concentrated solute (mole fraction > 5-10%): Kremser breaks down.
- Detailed packing-specific design: use vendor correlations or a
  rate-based simulator.

## Utility Scripts

- `uv run scripts/kremser.py --N 8 --A 1.4 --K 0.5 --y-in 0.02 --x-in 0.0 --output /tmp/kremser.json`
- `uv run scripts/kremser.py --N 8 --A 0.8 --K 0.5 --y-in 0.02 --x-in 0.0 --output /tmp/stripper.json`

## Workflow

1. Decide on solute, lean-solvent K-value at column conditions (often
   evaluated at a representative `T`).
2. Pick a target removal fraction (e.g. 95% of solute absorbed).
3. Compute the required absorption factor `A = L / (K V)`; aim for
   `A = 1.2 - 1.5` (industry rule of thumb for non-reactive dilute systems).
4. Solve Kremser for `N` stages.
5. Convert equilibrium stages to actual stages with a Murphree efficiency
   (~0.5 - 0.8 for trays; for packed beds, divide column height by HETP).
6. Sanity-check operating line vs equilibrium line: lines must not cross.

## Common Mistakes

- Using Kremser for a reactive absorber. The acid-gas + amine system needs
  a different framework.
- Picking `A = 1.0` (or just slightly above) and reporting it as feasible;
  it implies infinite stages at the limit.
- Using a single `K` for the whole column when K varies strongly with T or
  composition. Average it with care.
- Confusing absorption factor `A = L/(KV)` with stripping factor `S = K V/L`.
- Reporting equilibrium stages as actual trays without applying efficiency.
- Forgetting to verify that the operating line and equilibrium line do not
  cross within the column (a sign that the requested removal is infeasible at
  the chosen `A`).
- Picking `L/G` from the gas mass balance only — heat balance and rich solvent
  loading change the effective `L`.
- Using Kremser for solute mole fractions > 5-10%; non-linear equilibrium
  invalidates the constant-`A` assumption.

## Fallback Strategies

- For reactive absorption, switch to `sour-gas-amine-treating` (screening) or
  a rate-based simulator (ProMax, ProTreat, Aspen rate-based).
- For high-concentration systems, do a manual stage-by-stage operating /
  equilibrium analysis on a y-x diagram with varying K.

## References

- `references/kremser_derivation.md` — derivation and assumptions.
- Treybal, *Mass-Transfer Operations*.
- Sinnott, *Coulson & Richardson*, Volume 6.

## Anti-Patterns

- Reporting "5 actual trays" without specifying Murphree efficiency.
- Picking `A` from the recommended range without justifying it from
  capex/opex trade-off.
- Mixing up "absorption factor" with "absorption efficiency".

---
name: distillation-shortcut-design
description: >-
  Estimate distillation column theoretical stages, minimum reflux, feed-stage
  location, and McCabe-Thiele stair-stepping for binary or pseudo-binary cuts
  using Fenske, Underwood, Gilliland (Molokanov form), and McCabe-Thiele
  methods. Use when sizing a new column, screening separation feasibility,
  or sanity-checking a rigorous simulation. Don't use for rigorous tray-by-
  tray design (use a rate-based or equilibrium-stage simulator), azeotropic
  / extractive distillation, or batch distillation.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, separations, distillation, shortcut, design]
    category: separations
---

# Distillation Shortcut Design

## Overview

Implements the classical shortcut suite:

- **Fenske**: minimum number of equilibrium stages from `xD`, `xB`, and an
  averaged relative volatility `alpha`.
- **Underwood**: minimum reflux ratio for a multicomponent feed at a given
  thermal condition `q`.
- **Gilliland (Molokanov)**: actual stages from `N/Nmin` vs `R/Rmin`.
- **McCabe-Thiele**: stage stepping on a constant-`alpha` binary equilibrium
  curve, with operating-line intersection from the feed q-line.

The methods are textbook (Seader/Henley, Sinnott, McCabe/Smith/Harriott) and
implemented from first principles in `engg_skills_common.separations`.

## Prerequisites

1. `uv` available.
2. On first use the script writes `LICENSE_NOTIFICATION.txt` listing the
   library terms.

## When to Use

- Sizing a new column (number of stages, reflux ratio, feed stage).
- Screening separation feasibility before committing to a rigorous simulation.
- Sanity-checking a rigorous result with an independent calculation path.

## Don't use for

- Rigorous tray-by-tray rating or design — use an equilibrium-stage or
  rate-based simulator.
- Azeotropic or extractive distillation — the `alpha` assumption breaks down.
- Reactive distillation, batch distillation, or columns with side draws and
  multiple feeds.
- Sub-ambient cryogenic columns where K-values change strongly with stage T.

## Utility Scripts

- `uv run scripts/shortcut.py fenske --alpha 2.5 --xD 0.95 --xB 0.05 --output /tmp/fenske.json`
- `uv run scripts/shortcut.py underwood --alphas 4.0,2.0,1.0 --zs 0.4,0.4,0.2 --xds 0.95,0.04,0.01 --q 1.0 --output /tmp/underwood.json`
- `uv run scripts/shortcut.py gilliland --Nmin 12 --Rmin 1.3 --R 1.8 --output /tmp/gilliland.json`
- `uv run scripts/shortcut.py mccabe-thiele --alpha 2.5 --xD 0.95 --xB 0.05 --xF 0.40 --q 1.0 --R 2.0 --output /tmp/mt.json`

## Procedure

1. Decide on light key (LK) and heavy key (HK). Compute or look up the
   average relative volatility `alpha = K_LK / K_HK` over the column.
2. Pick distillate (`xD`) and bottoms (`xB`) compositions for the LK from
   product specs or recovery targets.
3. Compute `Nmin` with Fenske.
4. For multicomponent feed, compute `Rmin` with Underwood at the feed
   thermal condition `q` (1.0 saturated liquid, 0.0 saturated vapor).
5. Pick operating reflux `R = 1.2-1.5 × Rmin` (industry rule of thumb;
   higher gives fewer stages but more reboiler/condenser duty).
6. Use Gilliland to estimate `N` and the feed-stage ratio.
7. For binary screening with constant `alpha`, run `mccabe-thiele` to
   sanity-check the integer stage count.

## Pitfalls

- Using a feed-zone `alpha` instead of an averaged `alpha` across the column.
  Fenske and Underwood need a representative value; averaging top and bottom
  K-values is the usual workaround.
- Underwood's theta is bracketed between successive component alphas;
  picking the wrong root gives a useless `Rmin`. The script bisects only the
  first valid interval — if your system has multiple distributed components,
  inspect the theta value carefully.
- Treating `R/Rmin` of 1.05 or less as feasible; the Gilliland correlation
  is increasingly inaccurate in that range and the resulting column would
  have many stages and small driving forces.
- Forgetting that Fenske returns total stages *including* the reboiler.
- Using McCabe-Thiele for a non-binary cut.
- Picking `R = 1.5 × Rmin` and reporting it as optimal without an
  energy-vs-capex trade-off check.
- Assuming `q = 1` for a partially vaporized feed; even ~10% vapor changes
  `Rmin` noticeably.
- Reporting "10 actual trays" when Gilliland returns "10 equilibrium
  stages" — actual tray count needs Murphree (or O'Connell-style) efficiency.
- Using the shortcut output for a tower-control or relief calculation.
  Shortcut methods do not give per-stage T/P profiles.

## Fallback Strategies

- If the system is too non-ideal for constant-`alpha` (e.g. methanol-water,
  ethanol-water), Fenske/Gilliland gives misleading numbers; switch to a
  pseudo-binary basis (LK vs HK at top and bottom alphas averaged) and flag
  the deviation in your report.
- If Underwood's theta is not bracketed, the alphas are likely too closely
  spaced (or the feed is too dilute in the keys). Pivot to a McCabe-Thiele
  treatment of LK/HK at constant average `alpha` and document the simplification.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/methods_summary.md` — equations and assumptions for each
  shortcut method.
- Seader, Henley, Roper, *Separation Process Principles* (any recent edition).
- McCabe, Smith, Harriott, *Unit Operations of Chemical Engineering*.

## Anti-Patterns

- Reporting Gilliland stages as the actual tray count without efficiency
  derating.
- Using shortcut methods to specify column internals (tray spacing, downcomer,
  weir height); those require flooding/loading correlations not in this skill.
- Hiding the `R/Rmin` ratio in the final report — the optimization context
  matters for the reader.

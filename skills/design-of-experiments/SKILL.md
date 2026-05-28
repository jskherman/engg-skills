---
name: design-of-experiments
description: >-
  Generate full-factorial and two-level factorial DOE plans with
  randomization support and compute main-effect estimates.
  Use when planning a small experimental campaign with 2-5 factors and
  a clear single response. Don't use for response-surface methodology
  (RSM is outside the scope), Plackett-Burman screening (different
  algorithm), or process-data observational study design (use
  process-causal-inference-dags).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [statistics, process-data, data-analysis, design, of, experiments]
    category: statistics-data-analysis
---

# Design of Experiments

## Overview

Factorial DOE helpers:

- Full factorial design enumeration for an arbitrary number of factors at
  arbitrary level counts.
- Two-level factorial design (2^k) with optional randomization.
- Main-effect estimates from a fitted run (simple averaging contrast).

Suitable for hands-on screening campaigns with a small number of factors;
not a replacement for full RSM (central composite, Box-Behnken) or
optimal-design software.

## Prerequisites

1. `uv` available.

## When to Use

- Planning a 2-5 factor screening campaign with clear inputs and a single
  response.
- Generating a randomised run sheet for a small experiment.
- Computing the rough magnitude of main effects after a small run.

## Don't use for

- Response-surface methodology (RSM, central composite, Box-Behnken).
- Plackett-Burman or fractional-factorial confounding analysis.
- Observational data — DOE assumes you control the factor levels.
- Mixture experiments (constrained simplex designs).

## Utility Scripts

- `uv run scripts/doe.py full-factorial --factor "T=300,320" --factor "P=1e5,2e5" --output /tmp/fact.json`
- `uv run scripts/doe.py two-level --factors "A,B,C" --randomize --seed 42 --output /tmp/2k.json`

## Procedure

1. List factors and their levels (2 for screening, more for full
   factorial).
2. Choose the design (full factorial for small k; two-level if you only
   want main effects and 2-factor interactions).
3. Randomise the run order to mitigate time-order effects.
4. Add replication externally if you need pure-error estimates or curvature checks.
5. After the run, compute main effects.
6. If main effects are statistically significant, iterate to RSM with a
   different tool.

## Pitfalls

- Choosing two levels that are too close; main effects fall in the noise.
- Forgetting to randomise; time-order confounds the factor effects.
- Reporting effects without replicate variability.
- Confusing main effect (averaged over the other factors) with
  conditional slope (computed at fixed values of the other factors).
- Treating a two-level design as a curvature test; this script does not add
  centre points or run an RSM analysis.
- Using a 2^k design when you have only one shot per condition (no
  replicates) and treating ±SE as meaningful.
- Picking response that is correlated with multiple physical phenomena
  without thinking about what the design is testing.
- Forgetting blocking when the experiment spans multiple days /
  raw-material lots.

## Fallback Strategies

- If the number of factors exceeds 5, switch to fractional-factorial or
  Plackett-Burman screening (use `pyDOE2` outside this skill).
- For curvature exploration, switch to a central composite design with a
  dedicated package.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/factorial_designs.md` — design conventions and analysis
  outline.
- Montgomery, *Design and Analysis of Experiments* (any edition).

## Anti-Patterns

- Reporting "the effect of T is X" without naming the level range and
  the other factors held fixed.
- Designing an experiment without randomization and reporting the
  estimates as if independent.
- Using 2-level factorial for a known curved response.

---
name: process-causal-inference-dags
description: >-
  Build a DAG for a process-data problem, test d-separation, enumerate
  back-door adjustment sets, and export to Graphviz DOT for review. Use
  when designing an observational study or distinguishing confounding from
  mediation. Don't use to estimate causal effects (that is a separate
  modelling task); the skill produces the adjustment set, not the estimate.
---

# Process Causal Inference (DAG-Based Adjustment)

## Overview

For observational process data, the right adjustment set determines
whether a regression coefficient is a confounded estimate, a partial
mediated estimate, or the total effect. This skill provides DAG tooling:

- Build a DAG from an edge list (YAML or CLI).
- Test d-separation between sets given conditioning.
- Enumerate parents of the treatment as a candidate back-door adjustment
  set; verify the criterion.
- Export DOT source for the user to render with Graphviz.

The implementation is pure-Python (no NetworkX dependency). For larger
problems, swap in `networkx`/`pgmpy`.

Scope is deliberately narrow per design review:
- It DOES NOT estimate causal effects. Pair it with `engineering-statistics`,
  `censored-regression`, `distributed-lag-models`, or
  `bayesian-hierarchical-process-models` for that.
- It DOES NOT do front-door or instrument-variable analysis. Extend as
  needed.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## Use when

- Designing an observational study and you need a defensible adjustment
  set.
- Resolving confounding-vs-mediation disagreements in plant data.
- Drawing a DAG for an internal report or for HAZOP-style review of an
  empirical claim.

## Don't use for

- Estimating effect sizes (see other skills).
- Bayesian network learning from data (use `pgmpy`).
- Counterfactual analysis (no potential-outcomes implementation here).

## Utility Scripts

- `uv run scripts/dag.py check --edges "A,B;A,C;B,D;C,D" --treatment B --outcome D --output /tmp/check.json`
- `uv run scripts/dag.py dsep --edges "A,B;A,C;B,D;C,D" --x B --y C --z A --output /tmp/dsep.json`
- `uv run scripts/dag.py dot --edges "A,B;A,C;B,D;C,D" --output /tmp/g.dot`

## Workflow

1. List variables (predictors, candidate confounders, mediators, colliders,
   regime indicators, lab outcomes).
2. Classify each variable (confounder vs mediator vs collider vs regime).
3. Draw the DAG (one edge per causal direction; no cycles).
4. Identify the treatment and the outcome.
5. Get the parent set of the treatment; verify it satisfies the back-door
   criterion via `check`.
6. Use d-separation tests for alternative paths.
7. Export DOT and render externally for review.

## Common Mistakes

- Adjusting for mediators when estimating a total effect; this introduces
  bias.
- Adjusting for colliders (variables caused by both treatment and outcome);
  this opens a spurious path.
- Drawing an unsigned graph and assuming the direction is obvious;
  always be explicit.
- Equating "correlation with the outcome" with "is a confounder"; a
  mediator is correlated too but should not be adjusted for total effect.
- Forgetting the regime / selection indicator; if operators routinely
  intervene in response to the outcome, that intervention may be a
  collider conditional on the response.
- Reporting "no confounding" because a regression coefficient barely moves
  with adjustment. The right test is graphical, not numerical.
- Treating descendants of the treatment as legitimate adjustment variables.

## Fallback Strategies

- If the DAG has many nodes (> ~30), switch to `networkx` + `pgmpy` for
  efficient enumeration of separation sets.

## References

- `references/dag_glossary.md` — confounders, mediators, colliders,
  back-door criterion.
- Pearl, *Causality* (2nd ed).
- Hernán & Robins, *Causal Inference: What If*.

## Anti-Patterns

- Drawing a DAG only after seeing the regression results.
- Adjusting "for everything"; that controls for mediators and colliders.
- Claiming causal effect from a coefficient without naming the DAG used.

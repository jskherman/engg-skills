---
name: bayesian-hierarchical-process-models
description: >-
  Fit Bayesian hierarchical (multi-level) regression models on process data
  using PyMC: campaign / regime random intercepts, censored likelihoods,
  AR(1) residuals, weakly informative priors. Use when you need calibrated
  uncertainty across regimes (campaigns, units, operators) or for partially
  pooled estimates with few observations per group. Don't use for plain
  OLS (use engineering-statistics), or as a substitute for first-principles
  modelling.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+, uv,
  and native scientific Python runtime support for PyMC/ArviZ/Pandas are
  required for bundled scripts.
metadata:
  hermes:
    tags: [statistics, process-data, data-analysis, bayesian, hierarchical, process, models]
    category: statistics-data-analysis
---

# Bayesian Hierarchical Process Models

## Overview

Fits hierarchical (multi-level) Bayesian regressions of the form

    y_t | x_t, group ~ Normal(alpha_{group[t]} + x_t' beta, sigma)

with optional censoring on `y_t` and an AR(1) residual structure. Group
intercepts are drawn from a hyperprior, enabling partial pooling across
regimes.

The implementation uses PyMC (NUTS sampler) via a thin wrapper. The
script accepts a YAML model specification so analysts can iterate on
priors and likelihoods without editing code.

## Prerequisites

1. `uv` available.
2. The script declares `pymc`, `arviz`, `pandas`, `pyyaml` in PEP-723;
   first run installs them (sizeable: ~500 MB combined).
3. On first use, writes `LICENSE_NOTIFICATION.txt`.

## When to Use

- Data has natural groupings (campaigns, operators, instruments) and you
  want partial pooling.
- You need calibrated credible intervals that propagate censoring,
  autocorrelation, and shrinkage.
- The model needs informative priors (e.g. from engineering judgement).

## Don't use for

- Plain OLS or single-level GLMs (`engineering-statistics`).
- Time-series forecasting (use a dedicated state-space tool).
- Extremely large datasets (>1M rows) without thinning — NUTS is not
  designed for that scale.

## Utility Scripts

- `uv run scripts/bhm.py fit --data data.csv --spec spec.yaml --output /tmp/fit.json`

Example spec.yaml:
```yaml
response: log_S_total
predictors: [z_heavy, source_split, lean_loading]
group: campaign
censoring:
  lower_col: LOQ_log
ar1: true
priors:
  beta: {dist: normal, mu: 0, sigma: 5}
  sigma: {dist: half_normal, sigma: 1}
  tau_group: {dist: half_normal, sigma: 0.5}
sampler:
  draws: 2000
  tune: 1000
  chains: 4
  target_accept: 0.95
```

## Procedure

1. Build a tidy CSV: one row per observation; columns for response,
   predictors, group, and censoring bounds.
2. Write the spec YAML. Start with weakly informative priors.
3. Run `fit`. Inspect:
   - R-hat (should be < 1.01 for all parameters).
   - Effective sample size (ESS bulk and tail > 400).
   - Divergences (should be 0).
   - Posterior predictive checks.
4. If diagnostics fail, increase `target_accept`, tighten priors, or
   reparameterise.
5. Report posterior means with 94% HDI; never report point estimates
   alone.

## Pitfalls

- Using flat priors and being surprised by funnel shapes. Weakly
  informative priors (e.g. `Normal(0, 5)` on standardised predictors) work
  better.
- Failing to standardise predictors; PyMC + NUTS works much better with
  scaled inputs.
- Treating the posterior mean as the only output; report the HDI.
- Running with `chains=1`; convergence diagnostics need at least 2 chains.
- Ignoring divergences; they indicate biased posterior geometry.
- Using non-centred parameterisation for groups with many observations
  but the centred version for groups with few; pick consistently and
  re-fit if diagnostics fail.
- Forgetting to write the InferenceData artefact (NetCDF) to disk —
  re-fitting is expensive.

## Fallback Strategies

- If PyMC is unavailable, surface to the user; there is no clean
  pure-Python fallback for hierarchical Bayesian with censoring.
- For sensitivity, fit the same model with at least two prior choices and
  compare.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/spec_format.md` — full spec.yaml grammar.
- Gelman, Carlin, Stern, Dunson, Vehtari, Rubin, *Bayesian Data Analysis*
  (3rd ed).
- PyMC docs: https://www.pymc.io/

## Anti-Patterns

- Reporting Bayesian posterior intervals as if they were classical CIs
  without naming the model.
- Skipping convergence diagnostics.
- Treating sampling failure as a tuning issue without reviewing the model
  geometry.

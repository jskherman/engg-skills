---
name: engineering-statistics
description: >-
  Descriptive statistics, t-table confidence intervals for the mean, and
  simple linear regression on engineering data. Use when summarising lab
  or process data, computing a mean CI for sample data, or fitting a
  one-predictor linear regression. Don't use for autocorrelated process
  time-series (use time-series-process-data-analysis), censored lab data
  (use censored-regression), compositional data (use
  compositional-data-analysis), or hierarchical / multi-level models
  (use bayesian-hierarchical-process-models).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [statistics, process-data, data-analysis, engineering]
    category: statistics-data-analysis
---

# Engineering Statistics

## Overview

Pure-Python statistics for engineering data summaries:

- Mean, median, standard deviation, IQR, min/max.
- Mean confidence interval (t-table if degrees of freedom in the
  built-in table, normal approximation otherwise).
- Simple linear regression (one predictor): slope, intercept, R², and SE
  of slope and intercept.

The implementation deliberately stays in the Python standard library so
the skill is fast and dependency-light.

## Prerequisites

1. `uv` available.

## When to Use

- Summarising a small batch of lab measurements.
- Computing a CI for the mean of a sample.
- Fitting a single-predictor linear regression for a sanity check.

## Don't use for

- Autocorrelated process time-series (`time-series-process-data-analysis`).
- Censored lab data with below-LOQ values (`censored-regression`).
- Compositional data (`compositional-data-analysis`).
- Hierarchical / multi-level models (`bayesian-hierarchical-process-models`).
- Multi-predictor regression (use `statsmodels` or `scikit-learn`).

## Utility Scripts

- `uv run scripts/engg_stats.py descriptive --values "12.3,12.5,12.1,12.4" --output /tmp/desc.json`
- `uv run scripts/engg_stats.py ci-mean --values "12.3,12.5,12.1,12.4" --confidence 0.95 --output /tmp/ci.json`
- `uv run scripts/engg_stats.py regression --x "1,2,3,4,5" --y "2.1,3.9,6.1,8.0,10.1" --output /tmp/reg.json`

## Procedure

1. Confirm the data is i.i.d.-like (no obvious autocorrelation, no
   censoring, not a composition).
2. Run the desired summary.
3. If the CI is for a process value and you suspect autocorrelation, use
   `time-series-process-data-analysis` instead.

## Pitfalls

- Treating SPC data as i.i.d.; lag-1 autocorrelation > 0.3 invalidates
  the t-CI for the mean.
- Using R² as a goodness-of-fit metric without checking residuals.
- Ignoring outliers; one or two leverage points can drive the regression.
- Computing a CI on fewer than 5 data points and reporting it as
  precise.
- Using mean ± 2 SD as a "95% interval" when the data is not normal.
- Reporting the slope of a linear fit with insignificant slope (CI crosses
  zero) as if it had physical meaning.
- Standardising the predictor before fitting and forgetting to back-
  transform the slope to original units.
- Using sample standard deviation `s` where population standard deviation
  `sigma` is needed (e.g. capability indices).

## Fallback Strategies

- For larger or more complex problems, switch to `statsmodels` or
  `scikit-learn` (not in this skill).
- If the t-table degrees of freedom are missing for an unusual df, the
  script falls back to a normal-approximation CI with a warning.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/reporting.md` — guidance for reporting CIs and regressions.

## Anti-Patterns

- Reporting "p = 0.04 so the effect is real" without checking residuals.
- Computing a CI without naming the assumed sampling distribution.
- Using linear regression on a clearly non-linear trend.

---
name: censored-regression
description: >-
  Fit censored-normal or censored-lognormal regression models for lab data
  reported as below-LOD, below-LOQ, above-range, or interval-censored. Use
  when fitting regressions on sulfur species, trace contaminants, or any
  analyte that is frequently censored. Don't use for ordinary uncensored
  regression (use engineering-statistics), time-to-event survival analysis,
  or compositional response data (use compositional-data-analysis).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [statistics, process-data, data-analysis, censored, regression]
    category: statistics-data-analysis
---

# Censored Regression (Censored Normal / Censored Lognormal)

## Overview

Many process lab measurements (H2S, COS, mercaptans, DMS, disulfides,
unknown sulfur, trace metals) are reported as below-LOD, below-LOQ, above an
instrument range, or within an interval. Ordinary least squares on
`log(S + epsilon)` is biased and understates uncertainty; the correct treatment
is a likelihood-based censored regression.

This skill provides:

- A censored-normal regression on the log scale by default (censored lognormal
  on the original response scale).
- A censored-normal regression on the raw scale with `--no-log`.
- Left, right, and interval censoring.
- Maximum-likelihood fitting through SciPy.

The implementation uses a hand-rolled SciPy likelihood. It does not calculate
standard errors, robust covariance estimates, or the naive substitution fit.
Use bootstrap/profile-likelihood checks externally when inference quality matters.

## Prerequisites

1. `uv` available.
2. The script declares `numpy`, `scipy`, and `pandas` in its PEP-723 header.
3. On first use, writes `LICENSE_NOTIFICATION.txt`.

## When to Use

- Lab data has below-LOQ rows that you cannot drop without introducing
  selection bias.
- Reported values include intervals, for example between LOD and LOQ.
- Fitting a regression of `log(species)` on operating variables, where the
  species is sometimes censored.

## Don't use for

- Fully uncensored regression: use `engineering-statistics`.
- Time-to-event survival analysis: use a survival-analysis package.
- Compositional response data (sulfur speciation fractions): combine with
  `compositional-data-analysis`.

## Utility Scripts

- `uv run scripts/censored.py fit --data data.csv --response S_total --predictors temperature,c5_c6plus_balance --lower-col LOQ --output /tmp/fit.json`
- `uv run scripts/censored.py interval --data data.csv --response S_total --predictors temperature --lower-col LOD --upper-col LOQ --output /tmp/int.json`

Input CSV layout:

- One row per observation.
- `response` column with the measured value when fully observed; NaN or blank
  when censored.
- `lower-col` and/or `upper-col` columns with the censoring bound for censored
  rows.
- Predictor columns referenced by name in `--predictors`.

Censoring-column semantics used by the script:

- finite `response`: exact observation; bounds ignored.
- missing `response` + only `lower-col` finite: left-censored, meaning
  `y <= lower_col` (typical below-LOQ row).
- missing `response` + only `upper-col` finite: right-censored, meaning
  `y >= upper_col` (above-range row).
- missing `response` + both bounds finite: interval-censored, meaning
  `lower_col < y < upper_col`.

## Procedure

1. Build a tidy CSV with response and predictor columns and the censoring bound
   columns.
2. Decide the censoring direction:
   - left-censored at LOQ for trace sulfur below quantitation;
   - right-censored for above-range measurements;
   - interval-censored when LOD and LOQ are both reported.
3. Run the fit. Inspect coefficients, convergence status, optimizer message,
   and fraction censored.
4. For downstream decisions, use a bootstrap/profile-likelihood workflow rather
   than treating the point estimate as final when the censoring fraction is high.

## Pitfalls

- Using `log(S + 0.5 * LOQ)` and reporting normal CIs; this substitution is
  biased and the CIs are wrong.
- Using a censored fit and then reporting the response as if it were not
  censored; predictions are for the latent uncensored response.
- Treating "non-detect" as zero. Zero is usually a measurement convention, not
  the physical concentration.
- Treating LOD and LOQ as the same. Use interval censoring if both are reported
  and meaningful.
- Reporting one fit with a single censoring bound when the LOQ changed during
  the data window.
- Fitting on the raw scale when the data are heavy-tailed.

## Fallback Strategies

- For extreme censoring fractions (> 80%), report only the censoring fraction
  and rank/order conclusions; full regression coefficients are unstable.
- If the row order is a time series, use block bootstrap or a dynamic model for
  uncertainty rather than i.i.d. inference.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/censored_likelihood.md` — likelihood derivation.
- Greene, *Econometric Analysis*, chapter on truncated/censored models.
- Helsel, *Statistics for Censored Environmental Data Using MINITAB and R*.

## Anti-Patterns

- Hiding the censoring fraction in the report.
- Reporting a censored-lognormal coefficient as if it were on the original
  response scale; by default, the response model is on log scale.
- Using ordinary bootstrap on autocorrelated censored data without preserving
  time dependence.

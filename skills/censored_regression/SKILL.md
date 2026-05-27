---
name: censored-regression
description: >-
  Fit censored regression models (Tobit / censored lognormal) for lab data
  reported as below-LOD, below-LOQ, or interval-censored. Use when fitting
  regressions on sulfur species, trace contaminants, or any analyte that
  is frequently censored. Don't use for ordinary (uncensored) regression
  (use engineering-statistics), survival-analysis with right-censoring (use
  a survival package), or compositional response data (use
  compositional-data-analysis).
---

# Censored Regression (Tobit / Censored Lognormal)

## Overview

Many process lab measurements (H2S, COS, mercaptans, DMS, disulfides,
unknown sulfur, trace metals) are reported as below-LOD, below-LOQ, or
within an interval. Ordinary least squares on `log(S + epsilon)` is biased
and understates uncertainty; the correct treatment is a likelihood-based
censored regression.

This skill provides:

- A Tobit-style censored-normal regression on the log scale (i.e.
  censored lognormal on the original scale).
- Left, right, and interval censoring.
- Robust standard errors via the OPG estimator (statsmodels default).
- A diagnostic comparing the censored fit to a naive `log(S + epsilon)`
  fit for sensitivity reporting.

The implementation uses `statsmodels` (Tobit via `Censored` in newer
statsmodels, or a hand-rolled likelihood as fallback).

## Prerequisites

1. `uv` available.
2. The script declares `statsmodels` and `pandas` in its PEP-723 header;
   first run will install them (~50 MB combined).
3. On first use, writes `LICENSE_NOTIFICATION.txt`.

## Use when

- Lab data has below-LOQ rows that you cannot drop without introducing
  selection bias.
- Reported values include intervals (e.g. "below 0.5 ppmw" or "between LOD
  and LOQ").
- Fitting a regression of `log(species)` on operating variables, where
  the species is sometimes censored.

## Don't use for

- Fully uncensored regression: use `engineering-statistics`.
- Right-censored survival data: use a survival-analysis package.
- Compositional response data (sulfur speciation fractions): combine with
  `compositional-data-analysis`.

## Utility Scripts

- `uv run scripts/censored.py fit --data data.csv --response S_total --predictors temperature,c5_c6plus_balance --lower-col LOQ --output /tmp/fit.json`
- `uv run scripts/censored.py interval --data data.csv --response S_total --predictors temperature --lower-col LOD --upper-col LOQ --output /tmp/int.json`

Input CSV layout:
- One row per observation.
- `response` column with the measured value when above LOQ; NaN (or
  blank) when censored.
- `lower-col` and/or `upper-col` columns with the censoring bound for
  censored rows.
- Predictor columns referenced by name in `--predictors`.

## Workflow

1. Build a tidy CSV with response and predictor columns and the censoring
   bound columns.
2. Decide the censoring direction:
   - Left censored at LOQ: typical for trace sulfur below quantitation.
   - Interval censored: when LOD and LOQ are both reported and behave
     differently.
3. Run the fit. Inspect:
   - Coefficients and their standard errors.
   - Fraction censored (a high fraction (> 30%) makes inference fragile).
   - Comparison with the naive `log(S + epsilon)` fit; coefficients should
     change in a defensible direction.
4. Use posterior or bootstrap CIs for downstream decisions, not the
   naive `±1.96 SE` if censoring fraction is large.

## Common Mistakes

- Using `log(S + 0.5 * LOQ)` and reporting normal CIs; this substitution
  is biased and the CIs are wrong.
- Using a Tobit fit and then reporting the response as if it were not
  censored; the predictions must be interpreted on the latent (uncensored)
  scale.
- Treating "non-detect" as zero. Zero is impossible for most chemical
  species; the measurement is censored, not zero.
- Treating LOD and LOQ as the same. They differ by ~3x; use interval
  censoring if both are reported.
- Reporting one fit with a single censoring bound when the LOQ has changed
  during the data window (new instrument, new method).
- Fitting on raw scale rather than log scale when the data is heavy-tailed.

## Fallback Strategies

- If `statsmodels` Tobit is unavailable, use the hand-rolled likelihood
  fallback (script).
- For extreme censoring fractions (> 80%), report only the censoring
  fraction and rank statistics; full regression coefficients are unstable.

## References

- `references/censored_likelihood.md` — likelihood derivation.
- Greene, *Econometric Analysis*, chapter on truncated/censored models.
- Helsel, *Statistics for Censored Environmental Data Using MINITAB and R*.

## Anti-Patterns

- Hiding the censoring fraction in the report.
- Reporting a Tobit coefficient as if it had the same units as an OLS
  coefficient — same units for the predictor side, but the response is on
  the latent log scale.
- Using ordinary bootstrap on censored data without modifying the
  resampling.

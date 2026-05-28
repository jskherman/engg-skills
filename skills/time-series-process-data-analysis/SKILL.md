---
name: time-series-process-data-analysis
description: >-
  Estimate the sample autocorrelation (ACF), partial autocorrelation (PACF),
  and run a moving-block bootstrap for autocorrelation-aware confidence
  intervals on statistics of process time series. Use when computing CIs on
  any statistic from autocorrelated process data (means, regression
  coefficients, control-chart limits). Don't use for stationary white-noise
  data (use engineering-statistics) or for forecasting (use a dedicated
  time-series model).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [statistics, process-data, data-analysis, time, series, process, data]
    category: statistics-data-analysis
---

# Time-Series Diagnostics and Block Bootstrap for Process Data

## Overview

Process data are almost always autocorrelated, which means ordinary i.i.d.
inference (Wald CIs, t-tests, normal CIs) understates uncertainty. This
skill provides:

- Sample ACF and PACF.
- A simple block-length heuristic (`2 × first lag where |rho| < 2/sqrt(n)`).
- Moving-block bootstrap (Kuensch 1989) for any user-supplied statistic.

The ACF/PACF are useful for picking residual-autocorrelation orders for
regressions and for selecting a sensible block length.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## When to Use

- Computing a CI for the mean of a daily lab series.
- Computing a CI for a regression coefficient where residuals are
  autocorrelated.
- Diagnosing the order of a residual AR(p) for ARIMA / DLM modelling.
- Picking a block length for downstream block-bootstrap procedures.

## Don't use for

- Stationary white-noise data — use `engineering-statistics`.
- Forecasting future values — use a state-space model.
- Strongly non-stationary data — pre-process (detrend, deseasonalise) first.

## Utility Scripts

- `uv run scripts/ts.py acf --data series.csv --column y --max-lag 30 --output /tmp/acf.json`
- `uv run scripts/ts.py pacf --data series.csv --column y --max-lag 30 --output /tmp/pacf.json`
- `uv run scripts/ts.py block-len --data series.csv --column y --output /tmp/L.json`
- `uv run scripts/ts.py bootstrap --data series.csv --column y --block-length 8 --n-resamples 2000 --statistic mean --output /tmp/bs.json`

## Procedure

1. Compute ACF and PACF; eyeball the lag structure.
2. Pick a block length:
   - Use the `block-len` helper as a starting point.
   - For short series (< 200), constrain block length to ≤ n/4.
   - For long series, consider Politis-White optimal block length
     (not implemented; use `statsmodels` if needed).
3. Choose your statistic (mean, regression coefficient, quantile, etc.).
4. Run the bootstrap. Compare the bootstrap SE / CI against the i.i.d.
   counterpart; the bootstrap should be wider for positively autocorrelated
   data.
5. Report both intervals for transparency.

## Pitfalls

- Using ordinary bootstrap (i.i.d. resampling) on autocorrelated data; the
  CI is too narrow.
- Using a tiny block length (e.g. 2-3) for very autocorrelated data; the
  CI is still too narrow.
- Using a huge block length (≥ n/4); the bootstrap has very few effective
  resamples and the CI is unreliable.
- Reporting block-bootstrap CIs without specifying the block length.
- Treating the PACF as if it were independent of ACF; they are connected
  by the Durbin-Levinson recursion.
- Treating spikes outside `±2/sqrt(n)` as automatically meaningful; the
  multiple-testing rate is not controlled.
- Failing to detrend / deseasonalise before computing ACF; non-stationary
  trends inflate the ACF.

## Fallback Strategies

- If the series is too short for block bootstrap (<50), report the i.i.d.
  CI with a warning that it likely understates uncertainty.
- If `statsmodels` is available, use it for ARIMA-style residual diagnostics
  (not implemented here).

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/methods_notes.md` — block-bootstrap derivation, references.
- Kuensch, H. R. "The Jackknife and the Bootstrap for General Stationary
  Observations," Annals of Statistics, 1989.
- Politis & Romano, *Subsampling*.

## Anti-Patterns

- Quoting "p < 0.05" on a process-data regression without addressing
  autocorrelation.
- Designing SPC limits assuming independence on data that is clearly
  serially correlated.
- Using the bootstrap to "rescue" a model that is misspecified.

---
name: distributed-lag-models
description: >-
  Fit finite-impulse-response (distributed-lag) models that relate a sampled
  process response (daily lab) to high-frequency inputs (DCS minute data)
  with smoothness-regularised lag coefficients. Use when the effect of an
  upstream change propagates with mixed-residence-time dynamics to a
  downstream measurement. Don't use for simple single-lag regressions (use
  engineering-statistics with a lag offset), for non-linear dynamic models
  (use a state-space / Kalman tool), or for forecasting where the goal is
  prediction rather than effect attribution.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+, uv,
  and native scientific Python runtime support for NumPy/SciPy/Pandas are
  required for bundled scripts.
metadata:
  hermes:
    tags: [statistics, process-data, data-analysis, distributed, lag, models]
    category: statistics-data-analysis
---

# Distributed-Lag (FIR) Models for Process Data

## Overview

Many process datasets have a low-frequency response (daily lab) tied to
high-frequency inputs (DCS data at per-minute resolution). The effect is
typically distributed across several lags reflecting holdup, residence
time, and recycle. The naive single-lag regression understates the
dynamics; a distributed-lag (FIR) model estimates one coefficient for
each lag and reports both the cumulative effect magnitude and the lag
shape when the coefficients can be normalised into a kernel.

This skill provides:

- Penalised FIR regression with second-difference smoothness penalty
  (`ridge` on Δ² coefficients).
- Unrestricted lag coefficients by default, preserving effect magnitude
  and allowing sign changes.
- Optional non-negative coefficients via `--nonnegative` when process
  physics requires a same-sign response.
- Normalised lag weights only when the fitted coefficients are same-sign
  and have non-zero cumulative effect.
- Lag-placebo diagnostic: regression with future inputs should be weaker
  than past inputs.

The implementation uses NumPy/SciPy and pandas.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## When to Use

- A daily lab response should be related to minute-level or hourly DCS
  time series.
- The physical path between a controlled input and the lab measurement
  has multiple tanks, exchangers, contactors, rundown lines, or recycle
  paths with different residence times.
- The LPG sulfur problem-style task: lagged heavy-end balance vs product
  sulfur, with a horizon of 0-72 h.

## Don't use for

- Forecasting (use ARIMA / state-space / RNN).
- Non-linear systems where the response saturates.
- Cases where the lab samples are too few for the lag horizon (a rough
  rule: at least 5 lab observations per lag bin).
- Treating the fitted lag coefficients as a physical residence-time
  distribution unless their signs and shape support that interpretation.

## Utility Scripts

- `uv run scripts/dlag.py fit --data data.csv --response S_total --predictor z_heavy --max-lag 72 --penalty 1.0 --output /tmp/dlag.json`
- `uv run scripts/dlag.py fit --data data.csv --response S_total --predictor z_heavy --max-lag 72 --penalty 1.0 --nonnegative --output /tmp/dlag_nonnegative.json`
- `uv run scripts/dlag.py placebo --data data.csv --response S_total --predictor z_heavy --max-lag 72 --output /tmp/placebo.json`

Input CSV layout: hourly or other regular time grid; response is NaN on
non-sample rows. Predictor column carries the high-frequency series.
The first `max_lag` rows cannot be fitted because the full lag history is
not yet available.

## Procedure

1. Decide the maximum lag horizon from process physics
   (sum of segment residence times).
2. Resample the high-frequency series to the lag resolution (e.g. hourly).
3. Align lab samples to the time grid; carry timestamp uncertainty by
   fitting shifted grids or by widening the lag kernel.
4. Fit the unrestricted FIR model first. Inspect cumulative effect and
   coefficient signs.
5. If the mechanism requires a same-sign response, refit with
   `--nonnegative` and compare RSS / plausibility.
6. Inspect lag-shape summaries: peak effect lag, centroid lag, and time
   to 50% response if normalised weights are available.
7. Run the placebo test: replace past inputs with future inputs and refit.
   The future-input fit should be substantially weaker. If not, a common
   trend or measurement artefact may be driving the apparent effect.
8. Block-bootstrap the coefficients (use `time-series-process-data-analysis`)
   for CIs that account for residual autocorrelation.

## Pitfalls

- Picking a max-lag that is too short; the late lags carry meaningful
  effect and truncating them inflates the early ones.
- Picking a max-lag that is too long; the model becomes ill-posed and
  coefficients are noisy.
- Failing to penalise smoothness; without it, the FIR coefficients
  oscillate from lag to lag.
- Treating the FIR coefficients as independent significance tests; they
  are highly correlated.
- Forgetting that the sample timestamp has uncertainty; a ±1 h window
  shifts the apparent peak.
- Using a single FIR coefficient set across regimes where the residence
  times change (e.g. unit turndown).
- Reporting normalised weights without reporting the cumulative effect
  magnitude; the former is lag shape, the latter is the process effect.
- Forcing `--nonnegative` when the response can legitimately reverse sign
  after control action or composition compensation.

## Fallback Strategies

- If the lab data is too sparse, drop to a single representative lag at
  the engineering residence time and report it as a screening estimate.
- If coefficients have mixed signs, report the lag coefficients and
  cumulative effect directly rather than a residence-time-style kernel.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/fir_setup.md` — exact penalised regression form.
- Almon, S., "The distributed lag between capital appropriations and
  expenditures," Econometrica, 1965.
- Politis, *Subsampling*.

## Anti-Patterns

- Reporting the peak lag as the system time constant without checking the
  centroid.
- Skipping the placebo test.
- Treating FIR weights as physical residence-time distributions when the
  process model says otherwise.

---
name: distributed-lag-models
description: >-
  Fit finite-impulse-response (distributed-lag) models that relate a sampled
  process response (daily lab) to high-frequency inputs (DCS minute data)
  with non-negative, smoothness-constrained lag weights. Use when the
  effect of an upstream change propagates with mixed-residence-time dynamics
  to a downstream measurement. Don't use for simple single-lag regressions
  (use engineering-statistics with a lag offset), for non-linear dynamic
  models (use a state-space / Kalman tool), or for forecasting where the
  goal is prediction rather than effect attribution.
---

# Distributed-Lag (FIR) Models for Process Data

## Overview

Many process datasets have a low-frequency response (daily lab) tied to
high-frequency inputs (DCS data at per-minute resolution). The effect is
typically distributed across several lags reflecting holdup, residence
time, and recycle. The naive single-lag regression understates the
dynamics; a distributed-lag (FIR) model assigns non-negative weights to
each lag and reports the effective impulse response.

This skill provides:

- A non-negative-weights, sum-to-one FIR fit by penalised least squares.
- Smoothness constraint via second-difference penalty (ridge on Δ²w).
- Optional Almon polynomial form for very long lag horizons.
- Lag-placebo diagnostic: regression with future inputs should be weaker
  than past inputs.

The implementation uses NumPy/SciPy; `statsmodels` is optional for
additional tests.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## Use when

- A daily lab response should be predicted from minute-level DCS time series.
- The physical path between a controlled input and the lab measurement has
  multiple tanks / exchangers with different residence times.
- The LPG sulfur problem-style task: lagged heavy-end balance vs product
  sulfur, with a horizon of 0-72 h.

## Don't use for

- Forecasting (use ARIMA / state-space / RNN).
- Non-linear systems where the response saturates.
- Cases where the lab samples are too few for the lag horizon (a rough
  rule: at least 5 lab observations per lag bin).

## Utility Scripts

- `uv run scripts/dlag.py fit --data data.csv --response S_total --predictor z_heavy --max-lag 72 --penalty 1.0 --output /tmp/dlag.json`
- `uv run scripts/dlag.py placebo --data data.csv --response S_total --predictor z_heavy --max-lag 72 --output /tmp/placebo.json`

Input CSV layout: hourly (or other regular) time grid; response is NaN on
non-sample rows. Predictor column carries the high-frequency series.

## Workflow

1. Decide the maximum lag horizon from process physics
   (sum of segment residence times).
2. Resample the high-frequency series to the lag resolution (e.g. hourly).
3. Align lab samples to the time grid (carry the timestamp uncertainty by
   averaging the response over a ±1 h window if needed).
4. Fit the FIR model. Inspect the impulse response: does the peak occur at
   a physically plausible lag?
5. Run the placebo test: replace past inputs with future inputs and refit.
   The future-input fit should be substantially weaker. If not, a common
   trend or measurement artefact may be driving the apparent effect.
6. Block-bootstrap the coefficients (use `time-series-process-data-analysis`)
   for CIs that account for residual autocorrelation.

## Common Mistakes

- Picking a max-lag that is too short; the late lags carry meaningful
  weight and truncating them inflates the early ones.
- Picking a max-lag that is too long; the model becomes ill-posed and
  weights are noisy.
- Failing to penalise smoothness; without it, the FIR coefficients
  oscillate from lag to lag.
- Treating the FIR coefficients as independent significance tests; they
  are highly correlated.
- Forgetting that the sample timestamp has uncertainty; a ±1 h window
  shifts the apparent peak.
- Using a single FIR weight set across regimes where the residence times
  change (e.g. unit turndown).
- Reporting the effective lag as the peak lag of the FIR; the centroid
  and the "time to 50% response" are more interpretable.

## Fallback Strategies

- If `statsmodels` is missing, the fit still runs via SciPy.
- If the lab data is too sparse, drop to a single representative lag at
  the engineering residence time and report it as a screening estimate.

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

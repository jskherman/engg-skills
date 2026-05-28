# FIR Setup (Penalised Regression)

## Model

The lagged predictor matrix `X` has columns `x_{t-k}` for `k = 0..L`. The
response is `y_t`. The default fit solves:

```text
min_{a,b} || y - a - X b ||^2 + lambda || D^2 b ||^2
```

where:

- `a` is an unpenalised intercept;
- `b_k` is the effect coefficient at lag `k`;
- `D^2` is the second-difference operator applied only to the lag
  coefficients.

This preserves effect magnitude. The cumulative process effect for a
one-unit sustained predictor change is:

```text
sum_k b_k
```

## Optional non-negative fit

If the physics requires a same-sign response, pass `--nonnegative`. The
fit then solves the same penalised objective subject to:

```text
b_k >= 0
```

Do not force non-negativity when control action, compensation, or source
mixing can create sign reversals across lags.

## Normalised lag kernel

A residence-time-style lag kernel is reported only when the fitted
coefficients are same-sign and have non-zero cumulative effect:

```text
w_k = b_k / sum_j b_j
```

In that case:

- `w_k` gives the lag shape.
- `sum_k b_k` gives the effect magnitude.

If coefficients have mixed signs, report `b_k` directly; normalising
mixed-sign coefficients into weights is misleading.

## Diagnostics

- Peak effect lag: `argmax |b_k|`.
- Peak positive lag: `argmax b_k`.
- Cumulative effect: `sum_k b_k`.
- Centroid lag: `sum k w_k`, only when normalised weights exist.
- Time to 50% response: smallest `k` with cumulative `w_k >= 0.5`, only
  when normalised weights exist.
- Placebo lag reversal: refit with future inputs. The placebo fit should
  be markedly weaker if the original effect is causal in direction. If
  they are similar, suspect common trend or selection.

## When does the model fail?

- Lab observations too sparse for the lag horizon.
- Strong non-stationarity, such as unit turndown changing residence time.
- Heavy non-linearity or saturating chemistry.
- Confounding by an unmeasured upstream driver that varies on the same
  time scale.
- Treating lag-shape weights as effect magnitude.

# FIR Setup (Penalised Regression)

## Model

The lagged predictor matrix `X` has columns `x_{t-k}` for `k = 0..L`. The
response is `y_t`. The fit solves:

    min_{w} || y - X w ||^2 + lambda || D^2 w ||^2

with `D^2` the second-difference operator. Non-negativity (`w_k >= 0`) and
sum-to-one (`sum w_k = 1`) constraints can be added via projection or
Lagrangian penalty.

## Almon polynomial form

For long horizons, a low-order polynomial on `w_k = sum_j alpha_j k^j`
reduces the number of free parameters and yields smoother weights without
the explicit penalty. The script's default penalised form is usually
sufficient up to ~100 lags.

## Diagnostics

- **Peak lag**: `argmax w_k`. Physical residence-time anchor.
- **Centroid lag**: `sum k w_k / sum w_k`. Less sensitive to noise than peak.
- **Time to 50% response**: smallest `k` with cumulative weight ≥ 0.5.
  Best operating-interpretation summary.
- **Placebo (lag-reversal)**: refit with future inputs (reverse the predictor
  in time). The placebo fit should be markedly weaker if the original
  effect is causal in direction. If they are similar, suspect common trend
  or selection.

## When does the model fail?

- Lab observations too sparse for the lag horizon.
- Strong non-stationarity (e.g. unit turndown changes residence time).
- Heavy non-linearity (saturating chemistry).
- Confounding by an unmeasured upstream driver that varies on the same
  time scale.

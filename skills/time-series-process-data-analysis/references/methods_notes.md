# Methods Notes

## ACF (Sample autocorrelation)

    rho_k = sum_{i=1}^{n-k} (x_i - xbar)(x_{i+k} - xbar)
            / sum_{i=1}^{n} (x_i - xbar)^2

Under the null of white noise, `rho_k ~ N(0, 1/n)` approximately, so
`±2/sqrt(n)` is the usual eyeball band.

## PACF (Partial autocorrelation)

Computed via Durbin-Levinson recursion from the ACF. `pacf_k` measures the
correlation between `x_t` and `x_{t-k}` after removing the linear effect
of `x_{t-1}, ..., x_{t-k+1}`.

## Block-length heuristic

The script uses a simple rule: pick `L = c × (first lag at which |rho_k| <
2/sqrt(n))`. The default `c = 2` and a floor of 2 and ceiling of `n/4`.
For more elaborate selection, see Politis & White (2004) optimal block
length; that is in `statsmodels`.

## Moving block bootstrap (Kuensch 1989)

For a series of length `n` and block length `L`, choose
`B = ceil(n / L)` starting positions uniformly at random in
`{0, 1, ..., n-L}`, concatenate the `L`-length blocks, truncate to `n`,
and compute the statistic. Repeat for `n_resamples`.

Returns:
- Bootstrap mean of the statistic.
- Bootstrap SE.
- 2.5% and 97.5% percentile interval.

For statistics that are smooth functions of the underlying distribution
(mean, regression coefficient), the moving block bootstrap is consistent.

## Caveats

- For non-stationary series (trend, seasonality), detrend / deseasonalise
  before bootstrapping.
- For very strong autocorrelation (`rho_1 > 0.9`), small block lengths
  underestimate variability; large block lengths reduce the number of
  effective resamples.
- For heavy-tailed series, consider stationary bootstrap (Politis-Romano)
  instead.

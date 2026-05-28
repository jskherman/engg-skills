# Spec YAML Format

```yaml
response: <column name>
predictors: [<col1>, <col2>, ...]
group: <column name (optional)>
censoring:
  lower_col: <column name (optional; left-censor limit or interval lower bound)>
  upper_col: <column name (optional; right-censor limit or interval upper bound)>
ar1: true | false
priors:
  beta:
    dist: normal
    mu: 0.0
    sigma: 5.0
  sigma:
    dist: half_normal
    sigma: 1.0
  tau_group:
    dist: half_normal
    sigma: 0.5
sampler:
  draws: 2000
  tune: 1000
  chains: 4
  target_accept: 0.95
```

## Notes

- Predictors are standardised before sampling (mean 0, sd 1) so prior
  scales of order 1-5 are sensible.
- The `group` column produces a multi-level intercept with shared
  `mu_alpha` and `tau_group`.
- Rows with finite `response` are treated as fully observed.
- Rows with missing `response` and only `censoring.lower_col` present are
  treated as left-censored: the latent response is at or below that limit.
- Rows with missing `response` and only `censoring.upper_col` present are
  treated as right-censored: the latent response is at or above that limit.
- Rows with missing `response` and both bounds present are treated as
  interval-censored; `lower_col < upper_col` is required.
- Rows with missing `response` and no censoring bound are rejected.
- AR(1) residuals are modelled via PyMC's `AR` distribution; combine
  cautiously with censoring because the joint model can be slow for long
  series.
- The script writes JSON summary; pass `--idata-out path.nc` for the
  full InferenceData NetCDF.

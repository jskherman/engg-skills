# Spec YAML Format

```yaml
response: <column name>
predictors: [<col1>, <col2>, ...]
group: <column name (optional)>
censoring:
  lower_col: <column name (optional, for left/interval censoring)>
  upper_col: <column name (optional, for right/interval censoring)>
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
- `censoring.lower_col` activates left-censored likelihood for rows whose
  response is NaN and whose `lower_col` is present.
- AR(1) residuals are modelled via PyMC's `AR` distribution; combine
  cautiously with censoring (PyMC supports the joint formulation but it
  can be slow for long series).
- The script writes JSON summary; pass `--idata-out path.nc` for the
  full InferenceData NetCDF.

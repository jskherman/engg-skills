# Censored-Normal Likelihood (Brief)

Assume a latent log-response `y* = X beta + epsilon`, `epsilon ~ N(0, sigma^2)`.
Observed data partition into:

- **Fully observed**: contribute `phi((y - mu) / sigma) / sigma` to the
  likelihood, log: `-0.5 log(2 pi sigma^2) - 0.5 (y - mu)^2 / sigma^2`.
- **Left censored** at `L`: contribute `Phi((L - mu) / sigma)`,
  log: `Phi((L - mu) / sigma)`.
- **Right censored** at `U`: contribute `1 - Phi((U - mu) / sigma)`,
  log: `Phi(-(U - mu) / sigma)` (via the survival function for numerical
  stability).
- **Interval censored** between `L` and `U`: contribute
  `Phi((U - mu) / sigma) - Phi((L - mu) / sigma)`.

Sum the log-likelihoods, maximise with respect to `beta` and `log sigma`.

## Standard errors

The inverse of the observed information matrix gives asymptotic standard
errors. For small samples or large censoring fractions, prefer bootstrap or
profile-likelihood intervals. Block bootstrap is needed if the rows are
autocorrelated in time.

## When does this break?

- Mis-specified censoring direction.
- Reported "non-detect" without a numeric LOD/LOQ; the likelihood needs a
  bound.
- The latent error is not actually Gaussian on the log scale (e.g. heavy
  tails); consider a Student-t or scale-mixture extension.

## Compared with `log(S + epsilon)`

The substitution `S + 0.5*LOQ` followed by OLS:

- Biases coefficients toward zero when the censoring fraction is large.
- Underestimates the residual variance because the censored points are
  forced to a single value.
- Does not propagate the censoring uncertainty into prediction intervals.

The script reports both fits when requested; the comparison is the key
diagnostic for the sensitivity of the report's conclusions.

# Censored-Normal Likelihood (Brief)

The script fits either:

- a censored-lognormal model, by applying the likelihood below to `log(y)`
  (default); or
- a censored-normal model on the raw response scale with `--no-log`.

Let the model-scale latent response be:

```text
y* = X beta + epsilon,    epsilon ~ N(0, sigma^2)
```

Observed rows contribute as follows.

- Fully observed:

```text
log f(y) = -0.5*log(2*pi*sigma^2) - 0.5*(y - mu)^2/sigma^2
```

- Left-censored at `L`, meaning `y <= L`:

```text
log P(y <= L) = log Phi((L - mu)/sigma)
```

- Right-censored at `U`, meaning `y >= U`:

```text
log P(y >= U) = log[1 - Phi((U - mu)/sigma)]
```

The implementation uses the survival function for numerical stability.

- Interval-censored between `L` and `U`:

```text
log P(L < y < U) = log[Phi((U - mu)/sigma) - Phi((L - mu)/sigma)]
```

Sum the log-likelihoods and maximize with respect to `beta` and `log(sigma)`.

## Standard errors

The script reports point estimates and optimizer convergence diagnostics only. It
does not compute the observed information matrix or robust covariance. For small
samples or large censoring fractions, prefer bootstrap or profile-likelihood
intervals. Block bootstrap is needed if the rows are autocorrelated in time.

## When does this break?

- Mis-specified censoring direction.
- Reported "non-detect" without a numeric LOD/LOQ; the likelihood needs a
  bound.
- Non-positive values or censoring bounds with the default log-response model.
- The latent error is not actually Gaussian on the model scale, for example
  heavy tails; consider a Student-t or scale-mixture extension.

## Compared with `log(S + epsilon)`

The substitution `S + 0.5*LOQ` followed by OLS:

- biases coefficients toward zero when the censoring fraction is large;
- underestimates residual variance because censored points are forced to a
  single value;
- does not propagate censoring uncertainty into prediction intervals.

Use a substitution fit only as a sensitivity check, not as the primary result.

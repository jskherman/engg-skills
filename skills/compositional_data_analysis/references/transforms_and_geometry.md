# Log-Ratio Transforms (Formulas)

For a composition `x = (x_1, ..., x_D)` with each `x_i > 0`:

## clr (Centered log-ratio)

    clr_i = ln(x_i / g(x))

with `g(x) = (prod x_i)^(1/D)`.

The clr is symmetric across components but the resulting coordinates sum
to zero, so regression on all `D` coordinates is rank-deficient.

## alr (Additive log-ratio)

    alr_i = ln(x_i / x_D)

picking one reference component (commonly the last). The alr has `D-1`
coordinates and is asymmetric (the reference matters).

## ilr (Isometric log-ratio)

Pick an orthonormal basis (typically from a sequential binary partition).
For a balance `B` defined as group `H` against group `B'`:

    z_B = sqrt(r*s/(r+s)) * ln( g(x_H) / g(x_B') )

with `r = |H|`, `s = |B'|`, and `g` the geometric mean of the components
in the group. This is the coordinate of the composition along that
balance direction.

The ilr coordinates are orthonormal: their covariance matrix matches the
Euclidean covariance of the underlying Aitchison geometry, so regression,
PCA, and clustering on ilr coordinates are valid in the usual sense.

## SBP → contrast matrix Psi

Given an SBP (each row +1 for numerator, -1 for denominator, 0 for unused),
the orthonormal contrast matrix Psi has entries:

    psi_kj = +sqrt(s/(r(r+s)))  if row k has +1 in column j
    psi_kj = -sqrt(r/(s(r+s)))  if row k has -1 in column j
    psi_kj = 0                  otherwise

so that `ilr(x) = Psi * log(x)`.

## Heavy-end vs body example

For LPG with `H = {C5, C6+}` (r=2) and `B = {C3, C4}` (s=2):

    coef = sqrt(2*2/(2+2)) = 1
    z_H  = ln( sqrt(C5 * C6+) / sqrt(C3 * C4) )

Positive `z_H` means the sample is enriched in the heavy group relative
to the body group on a log-ratio scale.

## Zero replacement (multiplicative)

For zeros, replace by `delta` and rescale the non-zero components by
`(1 - n_zeros * delta) / sum(observed)` so the composition still sums to 1.
Choose `delta` smaller than the LOD; typical 1e-6 to 1e-4 in mol/mass
fraction.

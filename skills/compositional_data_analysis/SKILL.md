---
name: compositional-data-analysis
description: >-
  Transform compositional data (mole/mass fractions, GC compositions, sulfur
  speciation) using log-ratio transforms (clr, alr, ilr) and sequential
  binary partition (SBP)-based balances so regressions, PCA, and
  correlations are valid on the simplex. Use when analysing GC composition
  trends, sulfur-species splits, or any data that lives on the simplex.
  Don't use for ordinary numeric data, for compositional data where one
  component dominates and the rest are noise, or as a substitute for
  domain-specific physical models.
---

# Compositional Data Analysis (CoDA)

## Overview

Compositional data — mole/mass fractions, GC compositions, sulfur
speciation, particle size distributions — live on the simplex. Raw
regression and correlation on a simplex are mathematically invalid:
spurious correlations arise from the unit-sum constraint, and standard
statistical methods do not have well-defined geometry there.

This skill provides:

- **Centered log-ratio (clr)**: `clr_i = ln(x_i / g(x))` with `g(x)` the
  geometric mean.
- **Additive log-ratio (alr)**: removes one component as denominator.
- **Isometric log-ratio (ilr)**: orthonormal coordinates from a sequential
  binary partition (SBP), giving balances with physical interpretation.
- **Heavy-end vs body balance helper** (the canonical example from the LPG
  sulfur problem: `H = {C5, C6+}`, `B = {C3, C4}`).

It also implements multiplicative zero-replacement for components that
are reported as zero (real zeros are incompatible with log-ratio
transforms; rounded zeros below LOD must be imputed first).

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## Use when

- Building a regression where the predictor (or response) is a composition.
- Computing PCA / clustering on multivariate compositions.
- Constructing an interpretable "balance" for plant data
  (heavy-end-vs-body, paraffin-vs-olefin, acid-vs-organic-sulfur).
- Working with the LPG sulfur problem's `z_H` heavy-end balance.

## Don't use for

- Data that just happens to include some fractions; only use CoDA when the
  vector lies on the simplex (sums to a constant).
- Univariate analyses of a single component fraction — those are special
  cases that often still need closure-aware interpretation but rarely full
  CoDA machinery.
- A substitute for physical modelling: ilr coordinates are abstract; map
  back to balances with interpretable names.

## Utility Scripts

- `uv run scripts/coda.py clr --x 0.4,0.5,0.05,0.05 --output /tmp/clr.json`
- `uv run scripts/coda.py alr --x 0.4,0.5,0.05,0.05 --denominator-index 0 --output /tmp/alr.json`
- `uv run scripts/coda.py ilr-default --x 0.4,0.5,0.05,0.05 --output /tmp/ilr.json`
- `uv run scripts/coda.py ilr-sbp --x 0.4,0.5,0.05,0.05 --sbp "1,-1,0,0;0,0,1,-1;1,1,-1,-1" --output /tmp/ilr_sbp.json`
- `uv run scripts/coda.py heavy-end --composition c3=0.45,c4=0.45,c5=0.07,c6plus=0.03 --heavy c5,c6plus --body c3,c4 --output /tmp/heavy.json`
- `uv run scripts/coda.py zero-replace --x 0.0,0.30,0.65,0.05 --delta 1e-6 --output /tmp/repl.json`

## Workflow

1. Confirm the vector is compositional (sums to a constant; non-negative).
2. Replace zeros (multiplicative replacement; `delta` typically 1e-6 to
   1e-4 in mol/mass fraction).
3. Choose the transform:
   - clr if you want a symmetric, single-coordinate-per-component view.
   - alr if you need to write a regression with one explicit reference.
   - ilr (with a fixed SBP) if you want orthonormal, interpretable balances.
4. Run downstream regression / PCA / correlation on the transformed
   coordinates.
5. Back-transform reported coefficients to balance interpretations
   (heavy-vs-body, etc.).

## Common Mistakes

- Running OLS on raw mole fractions; the unit-sum constraint induces
  spurious correlations.
- Treating measured zeros as exact (they are usually below-LOD); failing
  to impute zeros and then taking logs.
- Building an SBP after seeing the results ("garden of forking paths");
  always lock the SBP before fitting.
- Interpreting ilr coefficients directly. They are dimensionless balances;
  the physical interpretation requires going back through the SBP.
- Using clr in regression: clr coordinates sum to zero, so regressing
  all of them yields a rank-deficient system. Use ilr or alr for
  regression.
- Confusing the heavy-end balance with a simple ratio. The balance
  `coef * ln(g_H / g_B)` with `coef = sqrt(r s / (r + s))` carries
  important geometric meaning.
- Forgetting to scale the alr/ilr basis when comparing across studies; the
  same SBP is essential for cross-study comparisons.

## Fallback Strategies

- If you cannot decide on an SBP, use the default Helmert basis. It is
  orthonormal but the balances are not physically named — you must label
  them after the fact.
- If a component is structurally zero (never measurable), drop it from the
  composition before transforming. Document this.

## References

- `references/transforms_and_geometry.md` — short, formulas-only summary.
- Pawlowsky-Glahn, Egozcue, Tolosana-Delgado, *Modeling and Analysis of
  Compositional Data*, Wiley, 2015.
- Egozcue & Pawlowsky-Glahn, "Groups of Parts and Their Balances in
  Compositional Data Analysis," Mathematical Geology, 2005.

## Anti-Patterns

- Calling something a "balance" without specifying the SBP.
- Reporting compositional coefficients in linear-scale units.
- Running PCA on raw mol% data.

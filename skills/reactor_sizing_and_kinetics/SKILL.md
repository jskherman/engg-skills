---
name: reactor-sizing-and-kinetics
description: >-
  Fit Arrhenius parameters from k(T) data and size isothermal CSTR, PFR, or
  batch reactors for nth-order or arbitrary user-supplied rate laws. Includes
  N-CSTRs-in-series and a numeric PFR integrator. Use when designing or
  rating a reactor or fitting laboratory rate data. Don't use for
  non-isothermal reactors (energy balance not included), heterogeneous
  catalysis with pore diffusion (Thiele modulus not covered), or
  polymerization with moments-based balances.
---

# Reactor Sizing and Kinetics

## Overview

Isothermal liquid-phase reactor design equations from first principles:

- Arrhenius fit (`A`, `Ea`) from temperature / rate-constant data.
- CSTR / PFR / batch volume or time for nth-order kinetics (analytical).
- N equal-sized CSTRs in series for 1st-order kinetics.
- Numerical PFR for any user-defined rate law (Langmuir-Hinshelwood,
  Michaelis-Menten, reversible reactions).

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## Use when

- Sizing a CSTR, PFR, or batch reactor for a known rate law.
- Fitting `A` and `Ea` from experimental data at multiple temperatures.
- Comparing CSTR-in-series vs single PFR for a target conversion.

## Don't use for

- Non-isothermal design (no energy balance — would need a coupled `T(z)` or
  `T(t)` solver).
- Heterogeneous catalysis with pore diffusion (Thiele modulus, effectiveness
  factor not covered).
- Multiple parallel reactions where selectivity matters (extension needed).
- Polymerization moments / chain-length distribution work.
- Bioreactors with cell death / inhibition (use a specialised model).

## Utility Scripts

- `uv run scripts/reactor.py arrhenius --temperatures 298,308,318,328 --k-values 1.2e-3,2.4e-3,4.8e-3,9.5e-3 --output /tmp/arr.json`
- `uv run scripts/reactor.py cstr --C0 1000 --conversion 0.9 --flow 0.001 --k 5e-4 --order 1 --output /tmp/cstr.json`
- `uv run scripts/reactor.py pfr --C0 1000 --conversion 0.9 --flow 0.001 --k 5e-4 --order 2 --output /tmp/pfr.json`
- `uv run scripts/reactor.py batch --C0 1000 --conversion 0.9 --k 5e-4 --order 1 --output /tmp/batch.json`
- `uv run scripts/reactor.py series --C0 1000 --conversion 0.95 --flow 0.001 --k 5e-4 --N 3 --output /tmp/series.json`

## Workflow

1. Fit the rate constant if you have temperature data: `arrhenius`.
2. Pick reactor type from process needs:
   - CSTR: tight T control, easy fouling cleanout, lower conversion per
     volume for positive-order kinetics.
   - PFR: higher conversion per volume for positive-order; flow regime
     matters (turbulent assumed in the simple formulas).
   - Batch: small / specialty / multi-product.
3. Compute volume or time at the design conversion.
4. Sensitivity: re-run with `+10%`/`-10%` in `k` to bracket uncertainty in
   the rate constant.
5. Compare against any pilot data; the analytical formulas assume perfect
   mixing (CSTR) or plug flow (PFR), neither of which is exact in industry.

## Common Mistakes

- Using a single-temperature `k` for a reactor that operates over a 20 K
  range. Fit `A`, `Ea` and evaluate `k(T)` at the design temperature.
- Confusing reaction order with stoichiometry. The order in the rate law
  is empirical; do not assume it equals the stoichiometric coefficient.
- Reporting reactor volume without stating whether it is liquid volume,
  total vessel volume, or void volume in a packed bed.
- Using `pfr_volume_nth_order` for a system where back-mixing matters
  (low Re, large vessel). Real reactors are between CSTR and PFR.
- Using `cstr_volume_nth_order` for very high conversions with positive
  order kinetics — the volume blows up as conversion → 1.
- Forgetting that batch time excludes load / unload / cleaning time.
- Treating `R^2` from the Arrhenius fit as a substitute for prediction
  intervals; with three points an excellent `R^2` is not the same as a
  defensible `A`.
- Forgetting that real CSTRs in series do not behave like a single PFR
  even at large `N` because of finite mixing in each vessel.

## Fallback Strategies

- For arbitrary rate laws (Langmuir-Hinshelwood, Michaelis-Menten,
  reversible reactions), use the `pfr --rate-fn` subcommand which accepts a
  Python expression in `C` (e.g. `0.5*C/(1+0.1*C)`).
- For non-isothermal design, surface to the user that this skill does not
  cover it; they should set up a coupled ODE solver.

## References

- `references/design_equations.md` — derivations.
- Fogler, *Elements of Chemical Reaction Engineering*.
- Levenspiel, *Chemical Reaction Engineering*.

## Anti-Patterns

- Picking PFR over CSTR purely because PFR "is more efficient"; ignoring
  fouling, cleaning, and control implications.
- Citing reactor volume without the rate constant used.
- Using textbook `k` without checking units consistency in the rate law.

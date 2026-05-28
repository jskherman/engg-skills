# Kremser Derivation and Assumptions

## Setup

Counter-current absorber with `N` equilibrium stages, dilute solute,
constant `L`, `V`, `K`. Numbering from the top:
- Gas enters at the bottom with `y_in = y_{N+1}`, leaves at the top with
  `y_out = y_1`.
- Solvent enters at the top with `x_in = x_0`, leaves at the bottom with
  `x_out = x_N`.

## Absorption factor

    A = L / (K V)

Constant `A` requires constant `L`, `V`, and `K`. For dilute solutes the
liquid and gas molar flows are essentially constant across the column and
this assumption is excellent.

## Fractional absorption

    eta = (y_in - y_out) / (y_in - K x_in)

The Kremser closed form gives:

    eta = (A^{N+1} - A) / (A^{N+1} - 1)      for A != 1
    eta = N / (N + 1)                          for A = 1

## Stripping factor variant

For a stripper, use `S = K V / L = 1 / A`. The same algebra applies with `S`
substituted for `A`. The script reports both via the `A` input.

## When does Kremser break down?

- Solute mole fraction above ~5-10%; `L` and `V` are no longer constant.
- Strong equilibrium curvature; `K` is not constant.
- Reactive absorption (chemical reaction in the liquid phase).
- Heat effects (temperature rises along the column).

In any of those cases, switch to a stage-by-stage solver with varying `K`
and rate-based corrections, or to a rigorous simulator.

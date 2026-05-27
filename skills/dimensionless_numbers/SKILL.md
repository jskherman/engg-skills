---
name: dimensionless-numbers
description: >-
  Compute classical engineering dimensionless numbers (Reynolds, Prandtl,
  Schmidt, Peclet, Froude, Weber, Biot, Fourier, Grashof, Rayleigh, Nusselt
  via Dittus-Boelter) from SI inputs, with validity-range warnings. Use
  when you need a dimensionless group for a correlation, regime check, or
  scale-up analysis. Don't use for problem-specific correlations (use
  convective-heat-transfer-correlations or pipe-flow-pressure-drop);
  this skill computes the groups, not the downstream correlation.
---

# Dimensionless Numbers

## Overview

Calculates the standard engineering dimensionless numbers from SI inputs:

- Flow: Re, Fr, We, Eu.
- Heat transfer: Pr, Nu (Dittus-Boelter screening), Gr, Ra, Bi, Fo, Pe.
- Mass transfer: Sc, Sh (via analogy if requested).

Validity-range warnings (e.g. Dittus-Boelter for Re >= 10000) are appended
when the inputs fall outside common citations.

## Prerequisites

1. `uv` available.

## Use when

- A correlation needs a Reynolds, Prandtl, or Grashof number.
- A regime check (laminar vs turbulent, natural vs forced convection) is
  needed before picking a correlation.
- Scale-up analysis where matching a dimensionless group is the design
  criterion.

## Don't use for

- Picking the convective heat transfer coefficient (use
  `convective-heat-transfer-correlations`).
- Multi-phase regime classification (use `two-phase-flow`).
- The Reynolds analogy for combined heat / momentum transfer — that is a
  specific correlation, not a single number.

## Utility Scripts

- `uv run scripts/calculate_dimensionless.py reynolds --density 1000 --velocity 1.5 --length 0.05 --viscosity 0.001 --output /tmp/re.json`
- `uv run scripts/calculate_dimensionless.py prandtl --cp 4180 --viscosity 0.001 --conductivity 0.6 --output /tmp/pr.json`
- `uv run scripts/calculate_dimensionless.py nusselt-dittus-boelter --reynolds 50000 --prandtl 4 --output /tmp/nu.json`

## Workflow

1. Get fluid properties at the relevant film / bulk temperature.
2. Identify the geometric length scale (pipe diameter, plate length,
   particle diameter) — the right one depends on the correlation.
3. Run the script. Note any validity-range warnings.
4. Pass the dimensionless number into the matching skill (correlation,
   pressure drop, etc.).

## Common Mistakes

- Using the wrong length scale (pipe diameter vs hydraulic diameter for
  non-circular ducts; characteristic length for natural convection).
- Computing Pr at room temperature and using it for a hot fluid stream.
- Computing Re with mass velocity (G = rho v) where the correlation
  expects bulk velocity, or vice versa.
- Treating Dittus-Boelter Nu as the actual convective coefficient when
  the validity is borderline (Re ~ 5000 or Pr > 100).
- Using the kinematic viscosity in a Re formula that expects dynamic
  viscosity (or vice versa).
- Using Bi to decide a lumped-capacitance analysis without checking
  whether the surface heat transfer coefficient is itself in a turbulent
  regime.
- Computing Sc from a guessed diffusivity; quote the source of D_AB.

## Fallback Strategies

- If a needed property (k, mu, cp) is unknown, surface the missing input
  with a clear error rather than guessing.
- For very high or very low Pr (e.g. liquid metals), use a different
  correlation than Dittus-Boelter; this skill reports the number but the
  correlation choice is downstream.

## References

- `references/equations.md` — formula list and standard length-scale
  conventions.

## Anti-Patterns

- Reporting Re without stating the length scale used.
- Treating Nu = 0.023 Re^0.8 Pr^0.4 as a universal answer.
- Mixing units silently inside the script call.

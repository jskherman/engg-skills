# Binary Interaction Parameter Starting Points

Use these as *starting values only*. Regress against experimental phase
equilibrium or density data before using for design.

## Hydrocarbons in hydrocarbons

For paraffinic hydrocarbons of the same family, kij = 0 is a reasonable
default (e.g. propane / butane / pentane).

For aromatic-paraffin or naphthene-paraffin pairs in light cuts, use 0.005
to 0.02 unless you have regressed values.

## Acid gases

- H2S + CH4: 0.08
- H2S + C2H6: 0.07
- H2S + C3H8: 0.06
- H2S + nC4: 0.05
- H2S + iC4: 0.05
- H2S + nC5: 0.05
- H2S + CO2: 0.10
- CO2 + CH4: 0.10
- CO2 + C2H6: 0.13
- CO2 + C3H8: 0.13
- CO2 + nC4: 0.14
- N2 + CH4: 0.03
- N2 + C2H6: 0.05
- N2 + C3H8: 0.07
- N2 + nC4: 0.08

## Amines

Amines in hydrocarbons cannot be modelled well by a plain cubic EOS even with
kij regression; the cubic-plus-association model or rate-based packages are
required for accurate VLE. For *screening* (e.g. confirming a lean amine has
negligible solubility in LPG), kij ~ 0.15-0.25 between DEA/MDEA and light
hydrocarbon is the order of magnitude reported in the open literature.

## Mercaptans and disulfides

For ethyl/methyl mercaptan in propane/butane, kij ~ 0.0-0.02 is typical.
DMS / DEDS / DMDS in light hydrocarbon are usually approximated with kij ~ 0
for screening; the resulting K-values are useful for relative-volatility work
but not for solving distillation specifications.

## References

- Knapp et al., "Vapor-Liquid Equilibria for Mixtures of Low Boiling
  Substances" (DECHEMA Chemistry Data Series).
- Reid, Prausnitz, Poling, *The Properties of Gases and Liquids*.
- API Technical Data Book.

Always cite the source of any kij you use in a design submission.

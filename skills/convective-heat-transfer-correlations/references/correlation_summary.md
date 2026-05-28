# Correlation Summary

## Dittus-Boelter

`Nu = 0.023 * Re^0.8 * Pr^n`, n=0.4 (heating), n=0.3 (cooling).

Validity: Re ≥ 10000, 0.6 ≤ Pr ≤ 160, L/D ≥ 10, smooth pipe, fully developed
turbulent flow, modest property variation.

## Gnielinski

`Nu = (f/8)(Re - 1000) Pr / (1 + 12.7 sqrt(f/8) (Pr^(2/3) - 1))`

with `f = (0.79 ln Re - 1.64)^-2` for smooth tubes.

Validity: 3000 ≤ Re ≤ 5e6, 0.5 ≤ Pr ≤ 2000. More accurate than Dittus-
Boelter at moderate Pr.

## Sieder-Tate

`Nu = 0.027 * Re^0.8 * Pr^(1/3) * (mu_bulk / mu_wall)^0.14`

Validity: Re ≥ 10000. Use when there is a strong viscosity gradient at the
wall (typical for oils heated or cooled).

## Laminar pipe

- Constant wall temperature: `Nu = 3.66`.
- Constant wall heat flux: `Nu = 4.36`.

Validity: Re < 2300, fully developed thermal entrance.

## Churchill-Chu (vertical plate, natural convection)

`Nu = (0.825 + 0.387 Ra^(1/6) / [1 + (0.492/Pr)^(9/16)]^(8/27))^2`

Validity: covers laminar (Ra < 1e9) and turbulent (Ra > 1e9) regimes; works
for vertical plates and good approximation for tall, slender cylinders.

## Rohsenow pool boiling

`q'' = mu_l * dHvap * [g(rho_l - rho_g)/sigma]^0.5 * (cp_l dT_e / (Csf dHvap Pr_l^n))^3`

`Csf` and `n` are surface/fluid coefficients (e.g. water on copper:
Csf=0.013, n=1.0). The `ht` wrapper handles those internally; for
non-water fluids, supply Csf and n explicitly to the underlying `ht`
function.

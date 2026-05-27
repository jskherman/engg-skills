# Equation Forms Used (Public)

The script implements the SI form of the API 520 Part I gas and liquid
sizing equations. The equations are widely published in textbooks and
free-access engineering articles; consult the authoritative API 520 text
for the definitive form, units, and the values of the constants (Kd,
Kb, Kv, Kw, Kc) for your specific service.

## Gas / vapor — critical flow

When `Pb / P1 ≤ critical pressure ratio`:

    A = W / (C * Kd * P1 * Kb * Kc) * sqrt(T * Z / MW)

with

    C = sqrt( gamma * (2/(gamma+1))^((gamma+1)/(gamma-1)) )

The critical pressure ratio is

    P_crit / P1 = (2 / (gamma + 1))^(gamma / (gamma - 1))

## Gas / vapor — sub-critical flow

When `Pb / P1 > critical pressure ratio`:

    F2 = sqrt[ (gamma / (gamma - 1)) * (Pb/P1)^(2/gamma) * (1 - (Pb/P1)^((gamma-1)/gamma)) ]

    A = W / (Kd * F2 * P1 * Kc * sqrt(2)) * sqrt(T * Z / MW)

## Liquid

    A = Q / (Kd * Kw * Kc * Kv) * sqrt(rho / (2 * (P1 - Pb)))

## Variables

- `A` — required effective orifice area (m²).
- `W` — gas/vapor mass flow (kg/s).
- `Q` — liquid volumetric flow at relieving conditions (m³/s).
- `T` — relieving temperature (K).
- `MW` — molecular weight (g/mol).
- `Z` — compressibility factor at relieving conditions.
- `gamma` — Cp/Cv at relieving conditions.
- `P1` — upstream relieving pressure (Pa, absolute).
- `Pb` — built-up + superimposed back-pressure (Pa, absolute).
- `Kd, Kb, Kc, Kv, Kw` — capacity corrections per API 520 (charts in the
  standard, not reproduced here).
- `rho` — liquid density at relieving conditions (kg/m³).

## Standard-orifice rounding

After computing `A`, round UP to the nearest API 526 designation (D, E, F,
G, H, J, K, L, M, N, P, Q, R, T) — the chart is in the standard.

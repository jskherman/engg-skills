# Equation Forms Used

This note records the equation forms implemented by `scripts/api520.py` and
`engg_skills_common.valves`. It is a screening reference, not a substitute for
the standard. Source: API 520 Part I, 8th Edition, December 2008. The attached
standard is a page-image PDF, so the source should be verified visually against
the gas/vapor and liquid sizing sections before using the tool for controlled
work.

## Internal SI basis

The script accepts SI inputs:

- gas/vapor mass flow `mass_flow_kg_s` in kg/s;
- liquid volumetric flow `Q_m3_s` in m^3/s;
- pressure in Pa(a);
- temperature in K;
- density in kg/m^3;
- viscosity in Pa*s.

The API-form calculations then convert internally to:

- `W` in kg/h;
- `Q` in L/min;
- `P1` and `P2` in kPa(a);
- `A` in mm^2;
- `M` in kg/kmol, numerically equal to g/mol;
- `mu` in cP.

## Gas / vapor — critical-flow branch

Use this branch when the actual backpressure ratio is at or below the critical
pressure ratio.

```text
r_crit = (2/(k + 1))^(k/(k - 1))
```

```text
C = 0.03948 * sqrt(k * (2/(k + 1))^((k + 1)/(k - 1)))
```

```text
A = W * sqrt(T*Z/M) / (C*Kd*P1*Kb*Kc)
```

where `k = Cp/Cv`, `W` is kg/h, `P1` is kPa(a), `T` is K, `M` is kg/kmol,
and `A` is mm^2.

## Gas / vapor — subcritical-flow branch

Use this branch when `P2/P1 > r_crit`. Define:

```text
r = P2/P1
```

```text
F2 = sqrt((k/(k - 1)) * r^(2/k) * (1 - r^((k - 1)/k))/(1 - r))
```

```text
A = 17.9 * W * sqrt(T*Z/(M*P1*(P1 - P2))) / (F2*Kd*Kc)
```

For the subcritical equation implemented here, `Kb` is not applied. For balanced
bellows or pilot-operated valves, check the standard, manufacturer data, and
backpressure limits before relying on the result.

## Liquid branch

```text
G1 = rho / rho_water
```

The implementation uses `rho_water = 999.016 kg/m^3` as the SG reference density.

```text
A = 11.78 * Q * sqrt(G1/(P1 - P2)) / (Kd*Kw*Kc*Kv)
```

where `Q` is L/min, `P1 - P2` is kPa, and `A` is mm^2.

## Liquid viscosity correction

If viscosity is provided, the script estimates `Kv` from the Reynolds-number
correction:

```text
Kv = (0.9935 + 2.878/sqrt(Re) + 342.75/Re^1.5)^-1
```

```text
Re = 18800 * Q * G1 / (mu * sqrt(A))
```

where `mu` is cP and `A` is the selected effective discharge area in mm^2. The
preferred workflow is to calculate once with `Kv = 1`, select the next larger
standard orifice, then recheck Reynolds number and `Kv` using the selected area.
If `--selected-area` is omitted, the script uses the preliminary calculated area
and emits a warning.

## Corrections and factors

- `Kd` is the effective coefficient of discharge. Use certified vendor data for
  final work.
- `Kb` is a gas/vapor backpressure correction for the critical-flow branch.
- `Kw` is the liquid backpressure correction.
- `Kc` accounts for a rupture disk installed upstream of the PRV when applicable.
- `Kv` is the liquid viscosity correction.

## Out of scope

The script does not size two-phase/flashing relief, reactive relief, fire-case
loads, inlet pressure drop, outlet built-up backpressure, tailpipe acoustics, or
standard-orifice selection. Those steps remain part of the relief-system design
basis and vendor review.

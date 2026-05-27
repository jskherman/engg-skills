# Reactor Design Equations

## Arrhenius

`k(T) = A * exp(-Ea / (R T))`

Linear regression of `ln k` vs `1/T` gives slope `-Ea/R` and intercept `ln A`.
`R = 8.314462618 J/(mol K)`.

## CSTR (isothermal liquid-phase, single nth-order)

Design equation: `V = F0 X / (-r_A)` with `-r_A = k * C^n` at the outlet
concentration `C = C0 (1 - X)`.

Therefore:
```
tau = X C0 / (k * (C0 (1 - X))^n)
V   = tau * Q
```

For 1st order:
```
tau = X / (k (1 - X))
```

## PFR (isothermal liquid-phase, single nth-order)

`V = Q * integral_0^X (dX / -r_A)`. Analytical forms:

- Order 1: `tau = -ln(1 - X) / k`.
- Order 0: `tau = X C0 / k`.
- Other n: `tau = (C0^(1-n) - C^(1-n)) / (k (1 - n))`.

## Batch (isothermal constant-volume, single nth-order)

Same algebra as PFR with concentration as the integration variable; time
replaces residence time. `t = -ln(1-X)/k` for 1st order.

## N equal CSTRs in series, 1st order

`C_N / C0 = (1 + k tau_each)^-N`. Solve for `tau_each` given target
conversion and `N`.

## Numerical PFR

Trapezoidal integration of `dV = F0 * dX / r(C)`. The script provides
`pfr_numeric` for arbitrary `r(C)`; the user passes a Python expression
that evaluates `r` given `C`.

## Assumptions

- Isothermal (no energy balance).
- Single reaction, single phase (liquid).
- No volume change with reaction.
- Constant density.
- Perfect mixing (CSTR) or plug flow (PFR).

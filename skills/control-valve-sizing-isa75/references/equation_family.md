# ISA 75.01.01 / IEC 60534 Equation Family (Pointers)

The `fluids.control_valve` module implements the ISA 75.01.01 / IEC 60534
sizing equations. The standards are copyrighted; this file points to the
relevant equation references only.

## Liquid sizing

`size_control_valve_l(rho, Psat, Pc, mu, P1, P2, Q)` solves for Kv (m³/hr)
that satisfies the standard's liquid flow equation, with the recovery
factor `FL`, the critical pressure ratio factor `FF`, and the viscosity
correction `FR` evaluated per the standard.

## Gas sizing

`size_control_valve_g(T, MW, mu, gamma, Z, P1, P2, Q)` solves for Kv that
satisfies the gas flow equation, with the expansion factor `Y` and the
specific heat ratio factor `Fk` per the standard. The function uses iso-
thermal expansion approximations consistent with IEC 60534-2-1.

## Kv vs Cv

- Kv: cubic metres per hour of water at 1 bar dP and 15 °C (metric).
- Cv: US gallons per minute of water at 1 psi dP and 60 °F (US).
- Conversion: `Cv ≈ 1.156 × Kv` (for the standard reference fluid).

## Cavitation and flashing (liquid)

Compute the cavitation index `sigma = (P1 - Psat) / (P1 - P2)` and compare
with the trim's `sigma_inc` and `sigma_dam` if available. If P2 < Psat,
the flow is flashing and the choked Cv must be used.

## Choked flow (gas)

The pressure-ratio limit is approximately `(P1 - P2) / P1 = Fk * xT` where
`xT` is the trim-specific pressure-drop ratio factor (from vendor data).
The script reports Kv from the un-choked form; a flag in your design review
should explicitly cover the choked condition.

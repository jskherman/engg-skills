---
name: control-valve-sizing-isa75
description: >-
  Size liquid or gas control valves using `fluids.control_valve` (ISA 75.01.01
  / IEC 60534 sizing equations). Returns Kv (m³/hr) and US Cv. Use when
  selecting a control valve, checking a vendor sizing, or screening for
  cavitation/flashing risk. Don't use for relief devices (use
  relief-valve-sizing-api520), choked-flow check valves, or specialized
  cryogenic / slurry / abrasive service that requires vendor-specific
  derating.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, fluid-flow, heat-transfer, control, valve, sizing, isa75]
    category: fluid-flow-heat-transfer
---

# Control Valve Sizing (ISA 75.01.01)

## Overview

Wrapper around `fluids.control_valve.size_control_valve_l` (liquid) and
`size_control_valve_g` (gas) per the ISA 75.01.01 / IEC 60534 family of
sizing equations.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## When to Use

- Selecting a control valve size for liquid or gas service.
- Checking a vendor-supplied Cv.
- Comparing Cv against the operating envelope (min/normal/max flow).

## Don't use for

- Pressure relief / safety valves — use `relief-valve-sizing-api520`.
- On-off valves, ball-valve trim selection.
- Cryogenic, slurry, abrasive, or high-temperature service with
  vendor-specific corrections beyond the ISA standard.

## Utility Scripts

- `uv run scripts/cv.py liquid --rho 800 --P1 2000000 --P2 1700000 --Q 0.005 --mu 5e-4 --Psat 100000 --Pc 4.2e6 --output /tmp/liq.json`
- `uv run scripts/cv.py gas --T 300 --MW 30 --mu 1.2e-5 --gamma 1.3 --Z 0.92 --P1 800000 --P2 400000 --Q 0.6 --output /tmp/gas.json`

## Procedure

1. Determine min / normal / max flow rates for the service.
2. Get fluid properties at upstream conditions (rho, mu, Psat, gamma, Z).
3. Run sizing at each flow rate; the operating Cv should fall in the
   20-80% open range at the normal flow.
4. Check for cavitation (liquid: Psat too close to P2) and choked flow
   (gas: pressure ratio at or below critical).
5. Select the valve from vendor data such that the required Cv is met at
   max flow with margin.

## Pitfalls

- Sizing only for max flow; the valve may be unstable or hunt at min flow
  if it ends up too far closed.
- Using upstream density for downstream conditions when there is a large
  pressure drop and significant flashing.
- Treating cavitation onset as the same as choked flow. They are different:
  cavitation depends on pressure recovery (`FL`) and `Psat`; choked flow
  depends on pressure ratio and `gamma`.
- Confusing Kv (m³/hr) with Cv (US gpm); the ratio is ~1.156.
- Using a globe-valve `FL` for a butterfly-valve service. `FL` is
  trim-specific.
- Sizing with viscosity-corrected `FR` outside the correlation envelope.

## Fallback Strategies

- If `fluids.control_valve` is unavailable, surface to the user; the
  rigorous ISA equation is not reproduced here.
- For two-phase service, the standard ISA 75.01.01 does not apply
  directly; consult the vendor or use a specialised correlation.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/equation_family.md` — pointers to ISA 75.01.01 / IEC 60534.
- `fluids.control_valve` docs: https://fluids.readthedocs.io/fluids.control_valve.html
- ISA 75.01.01-2012 — Industrial-process control valves — Flow capacity.
- IEC 60534-2-1 — Industrial-process control valves — Part 2-1: Flow capacity.

## Anti-Patterns

- Specifying a control valve by line size rather than by Cv requirement.
- Skipping the min-flow check.
- Ignoring cavitation/flashing on liquid service near `Psat`.

---
name: separator-vessel-sizing
description: >-
  Size two-phase (gas-liquid) separator vessels (vertical or horizontal) using
  the Souders-Brown vapor-velocity criterion, K-factor heuristics, and
  liquid holdup time. Use when sizing flash drums, knock-out drums, suction
  scrubbers, or compressor inlet drums for screening. Don't use for
  three-phase separators with explicit water-hydrocarbon holdup (requires
  separate residence times), cyclonic separators, or high-pressure
  liquid-liquid coalescers.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, fluid-flow, heat-transfer, separator, vessel, sizing]
    category: fluid-flow-heat-transfer
---

# Two-Phase Separator Vessel Sizing

## Overview

Implements the Souders-Brown velocity criterion with GPSA-style K-factor
ranges (no proprietary table reproduced) for vertical and horizontal
two-phase vessels. Liquid holdup time defaults to 5 minutes (typical
operator-response horizon); override for your service.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## When to Use

- Sizing a knock-out drum, flash drum, suction scrubber, or compressor
  inlet drum.
- Screening vendor sizing or rating an existing vessel for new conditions.

## Don't use for

- Three-phase separators with explicit oil-water-gas residence time.
- Cyclonic / vane / coalescer-only separators.
- Tower-bottom sumps where downcomer hydraulics dominate.

## Utility Scripts

- `uv run scripts/sizing.py vertical --vapor-volumetric 0.4 --liquid-volumetric 0.005 --rho-l 600 --rho-g 30 --demister --output /tmp/v.json`
- `uv run scripts/sizing.py horizontal --vapor-volumetric 0.4 --liquid-volumetric 0.005 --rho-l 600 --rho-g 30 --demister --LD 4 --output /tmp/h.json`
- `uv run scripts/sizing.py watkins-k --quality 0.6 --rho-l 600 --rho-g 30 --output /tmp/k.json`

## Procedure

1. Get the vapor volumetric flow at operating P,T (from a flash, or from
   measured density and mass flow).
2. Get the liquid volumetric flow.
3. Decide demister or no demister (demister = ~50% smaller diameter for the
   same separation).
4. Pick liquid holdup time: 5 min for operator response, 2 min for high
   reliability shutdown systems, 10 min for upstream / unattended skids.
5. Pick `L/D` for horizontal: 3 (compact), 4 (default), 5 (long, high gas
   load).
6. Run `vertical` or `horizontal`; check that the available liquid holdup
   meets requirement.

## Pitfalls

- Picking the K-factor at the top of the range without justifying it.
- Sizing for max vapor flow but ignoring the relief contingency flow (which
  may govern the design).
- Forgetting to add a demister allowance to tan-tan height (~0.3 m typical).
- Using a vertical vessel for a high-liquid-loading service; horizontal is
  often better when liquid-to-vapor flow ratio is large.
- Treating the diameter as exact; round up to standard pipe / fab sizes.
- Reporting K without specifying horizontal vs vertical and with/without
  demister.
- Forgetting that high-pressure systems need different K factors than
  atmospheric service (the GPSA chart trends with P).
- Sizing on lab/measured density and forgetting that density at operating
  conditions can differ by 5-15%.

## Fallback Strategies

- If quality `x` is known, use `watkins-k` to derive a more realistic K
  from `fluids.separator.K_separator_Watkins` instead of the rule-of-thumb
  ranges.
- If the holdup time check fails, increase L/D for horizontal or vessel
  diameter for vertical and rerun.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/k_factor_ranges.md` — K-factor ranges and citations.
- GPSA Engineering Data Book (procure separately).
- API 12J — Specification for Oil and Gas Separators.

## Anti-Patterns

- Treating the vessel as final design without HAZOP, relief, or vendor
  review.
- Specifying tan-tan height without showing the holdup calculation.
- Picking K to fit a pre-existing nozzle size rather than to meet the
  separation duty.

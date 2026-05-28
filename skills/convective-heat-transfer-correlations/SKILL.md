---
name: convective-heat-transfer-correlations
description: >-
  Single-phase convective heat transfer coefficient correlations
  (Dittus-Boelter, Gnielinski, Sieder-Tate, Churchill-Chu
  natural convection, pool boiling via Rohsenow). Use when computing h for
  tube-side or shell-side flow, natural convection from a surface, or
  screening pool-boiling heat transfer. Don't use for shell-and-tube
  full sizing (use heat-exchanger-sizing), or for low-quality two-phase
  pressure drop (use two-phase-flow).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [chemical-engineering, process-engineering, fluid-flow, heat-transfer, convective, heat, transfer, correlations]
    category: fluid-flow-heat-transfer
---

# Convective Heat Transfer Correlations

## Overview

Pure-Python implementations of the classical pipe/duct flow correlations
plus a thin wrapper around `ht.boiling_nucleic.Rohsenow`:

- **Dittus-Boelter**: simplest turbulent pipe correlation, broad use.
- **Gnielinski**: turbulent / transitional pipe, wider Pr range, more
  accurate than Dittus-Boelter for moderate-Pr fluids.
- **Sieder-Tate**: turbulent pipe with viscosity correction (good for oils,
  high-viscosity service).
- **Laminar pipe** (constant Tw or constant q).
- **Churchill-Chu**: natural convection from a vertical plate (laminar +
  turbulent unified).
- **Rohsenow pool boiling**: screening estimate via `ht`.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## When to Use

- Estimating `h` for one side of a heat exchanger before passing to
  `heat-exchanger-sizing`.
- Sizing a steam tracing or insulation problem with natural convection.
- Screening pool boiling heat transfer for a kettle reboiler.

## Don't use for

- Full shell-and-tube exchanger design — use `heat-exchanger-sizing`.
- Plate exchangers — vendor-specific correlations apply.
- Falling-film, agitated vessel, or specialty geometries — those have their
  own correlations and are not in this skill.

## Utility Scripts

- `uv run scripts/h.py dittus-boelter --Re 50000 --Pr 4.5 --k 0.6 --Dh 0.025 --output /tmp/db.json`
- `uv run scripts/h.py gnielinski --Re 50000 --Pr 4.5 --k 0.6 --Dh 0.025 --output /tmp/gn.json`
- `uv run scripts/h.py sieder-tate --Re 50000 --Pr 4.5 --k 0.6 --Dh 0.025 --mu-bulk 0.001 --mu-wall 0.0007 --output /tmp/st.json`
- `uv run scripts/h.py laminar --regime constant-T --k 0.6 --Dh 0.025 --output /tmp/lam.json`
- `uv run scripts/h.py natural --Ra 1e9 --Pr 0.7 --k 0.026 --L 1.0 --output /tmp/nc.json`
- `uv run scripts/h.py boiling --T-sat 373.15 --T-wall 383.15 --P 101325 --k-l 0.68 --rho-l 958 --rho-g 0.6 --sigma 0.059 --cpl 4217 --dHvap 2257000 --mu-l 0.00028 --output /tmp/boil.json`

## Procedure

1. Decide the flow regime: Re, Pr, geometry, heated/cooled.
2. Pick the matching correlation:
   - Pipe, turbulent (Re > 10000), simple fluid: Dittus-Boelter.
   - Pipe, transitional or wide Pr (oils, gases): Gnielinski.
   - Pipe, large viscosity gradient at the wall: Sieder-Tate.
   - Pipe, laminar (Re < 2300): laminar formulas with the proper BC.
   - Surface, natural convection: Churchill-Chu (geometry-dependent).
   - Pool boiling: Rohsenow as screening; site-specific surface factors
     dominate.
3. Compute `h = Nu * k / Dh`.
4. Cross-check with a second correlation; flag the spread.

## Pitfalls

- Using Dittus-Boelter for Re = 5000. Outside its validity range.
- Using Dittus-Boelter for Pr = 200. Outside its validity range.
- Forgetting that Pr changes with temperature; use a properly averaged
  film temperature.
- Treating the "heating" exponent (0.4) as universal; use 0.3 for cooling.
- Using a single `h` for the entire tube length when entrance effects are
  significant (short tubes, low Re); Nu varies along the entrance length.
- Ignoring the viscosity correction `(mu_bulk / mu_wall)^0.14` for oils.
- Using Rohsenow with the wrong `Csf` surface factor (it varies by 2x for
  real surfaces); the `ht` wrapper uses the canonical Csf for water/copper.

## Fallback Strategies

- If `ht` is not installed, the single-phase correlations are pure Python
  and work without it.
- For specialty boiling (forced convective, flow film boiling), this skill
  has only the screening Rohsenow form; surface a request to the user for
  a different correlation.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/correlation_summary.md` — equation forms and ranges.
- Incropera & DeWitt, *Fundamentals of Heat and Mass Transfer*.
- Kakac, Liu, *Heat Exchangers Selection, Rating, and Thermal Design*.
- `ht` documentation: https://ht.readthedocs.io/

## Anti-Patterns

- Picking a correlation by name rather than by validity range.
- Reporting `h` without stating the correlation used.
- Computing tube-side `h` only and ignoring the shell-side (it usually
  dominates).

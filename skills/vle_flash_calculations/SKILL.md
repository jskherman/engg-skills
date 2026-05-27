---
name: vle-flash-calculations
description: >-
  Run vapor-liquid (and vapor-liquid-liquid) flash calculations, dew/bubble
  point solves, and Rachford-Rice K-value flashes for hydrocarbon, sour-gas,
  and light-process mixtures using Caleb Bell's `thermo` package. Use when
  the user needs phase split, K-values, dew/bubble pressure or temperature,
  or liquid/vapor properties at specified T,P. Don't use for water/steam
  utilities (use steam-tables-iapws), property-method selection by itself
  (use equation-of-state-selection), or amine reaction-equilibrium loading
  (use sour-gas-amine-treating).
---

# Vapor-Liquid Equilibrium Flash Calculations

## Overview

Solves VLE flashes for multicomponent mixtures using `thermo.FlashVL` backed
by a chosen cubic equation of state (PR, SRK, PRSV, PR-Translated variants).
Also provides a pure-Python Rachford-Rice solver for screening when only
K-values are available.

## Prerequisites

1. `uv` available on PATH (see the `uv` skill).
2. On first use, the script writes `LICENSE_NOTIFICATION.txt` into this
   skill directory listing the upstream terms for the `thermo` and `chemicals`
   libraries; review them before any regulated or commercial use.

## Use when

- A flash split, K-values, or dew/bubble curve is needed for a defined hydrocarbon
  or sour mixture.
- The user wants to evaluate phase behaviour at multiple T,P points.
- A quick Rachford-Rice solve with pre-computed K-values is needed for screening.

## Don't use for

- Pure water / steam utility states — use `steam-tables-iapws`.
- Picking the right property method in the first place — use
  `equation-of-state-selection`.
- Reactive systems (amine-CO2-H2S kinetics, ester hydrolysis, etc.) where the
  rate-based reaction matters more than phase equilibrium alone.
- Polymer or electrolyte systems — cubic EOS are unsuitable.

## Core Rules

- Always specify component identifiers in a form `chemicals.search_chemical`
  can resolve (IUPAC name, common name, or CAS number).
- Always declare which EOS is used; the default is PR but the right choice
  depends on the system (see `equation-of-state-selection`).
- Binary interaction parameters (kij) default to zero. For sour-gas, polar,
  or amine systems, pass realistic kijs (sources: Sandler, Whitson, vendor
  databases) — using zeros silently is a common error.
- Report the JSON result envelope; never paraphrase numerical values without
  reference to the JSON file written by the script.

## Utility Scripts

- `uv run scripts/flash.py tp --components propane,n-butane --zs 0.4,0.6 --T-K 300 --P-Pa 800000 --eos PR --output /tmp/flash.json`
- `uv run scripts/flash.py bubble --components propane,n-butane --zs 0.4,0.6 --T-K 300 --eos PR --output /tmp/bubble.json`
- `uv run scripts/flash.py dew --components propane,n-butane --zs 0.4,0.6 --T-K 320 --eos PR --output /tmp/dew.json`
- `uv run scripts/flash.py rr --Ks 4.2,0.6 --zs 0.4,0.6 --output /tmp/rr.json`
- `uv run scripts/flash.py envelope --components propane,n-butane --zs 0.5,0.5 --T-K-list 280,290,300,310,320 --eos PR --output /tmp/envelope.json`

## Workflow

1. Identify components and resolve their CAS numbers via
   `chemicals.search_chemical` (do this once, paste resolved names into
   the call).
2. Choose the EOS family (PR for most hydrocarbon work; PRSV / translated
   variants for sour or polar systems; SRK as a sanity check).
3. Decide on kij values: zero for chemically similar hydrocarbons; ~0.05-0.08
   for H2S in light hydrocarbon; ~0.10-0.25 for H2S/amine. Document the
   source.
4. Run `flash tp` for a specified (T,P,zs); inspect `vapor_fraction` and
   the phase classification.
5. For phase envelope work, repeat at a list of T or P values.
6. Validate the result: density vs lab data, dew/bubble vs operating data, or
   trusted simulator. Adjust kij if needed.

## Common Mistakes

- Using PR (default) for systems containing H2S, CO2, or amines without
  supplying non-zero kij values. Mixture properties (especially density and
  loading) will be wrong.
- Confusing PR with `PRMIXTranslatedPPJP` — both are PR family, but the
  translated/consistent versions give markedly different liquid densities
  (5-15% closer to experimental).
- Reporting K-values from an in-phase region (single-phase) as meaningful;
  K-values are only physically defined when both phases exist.
- Passing zs that sum to something other than 1 without normalizing. The
  script normalizes for you but logs a warning — don't ignore it.
- Using `flash tp` with a T that is above the mixture critical temperature
  and expecting two phases; thermo may converge to a "vapor" with a phase
  classification that needs interpretation.
- Treating volumetric flow as molar flow when computing absolute mass rates
  downstream; the JSON gives mole-basis K-values and compositions.
- Picking SRK because it is faster; the binary-parameter database for PR is
  larger, so PR usually gives better results for hydrocarbon work.
- Forgetting that `PRMIXTranslatedPPJP` needs volume-translation constants
  `cs`. The script defaults them to zero (a documented assumption); supply
  real values for production work.
- Calling Rachford-Rice with one phase or with all K > 1 or all K < 1; the
  script returns the trivial single-phase answer with a regime flag rather
  than failing.
- Treating the dew/bubble pressure as exact at the second decimal place; the
  underlying solver converges to a tolerance of about 1e-6 in mole fractions,
  which corresponds to wider uncertainty in pressure for near-azeotropic mixes.

## Fallback Strategies

- If `thermo.FlashVL` fails to converge (rare for hydrocarbon systems), drop
  to Rachford-Rice with K-values from Antoine vapor pressures and a
  modified-Raoult assumption (`flash rr`). Document the assumption.
- If `chemicals.search_chemical` cannot resolve a component (e.g. exotic
  amine or carbazole), supply explicit `--Tcs`, `--Pcs`, `--omegas` arrays
  using literature values.
- If the system contains water + hydrocarbon and the result is
  obviously wrong (e.g. water dissolves completely into the hydrocarbon
  phase at low T), switch to an activity-coefficient model — but those are
  outside this skill; surface that to the user.

## References

- `references/eos_choice.md` — quick decision matrix for PR/SRK/PRSV/translated.
- `references/kij_starting_points.md` — sourced kij starting values for
  H2S/CO2/N2 with light hydrocarbons.
- Caleb Bell, `thermo` documentation: https://thermo.readthedocs.io/
- Caleb Bell, `chemicals` documentation: https://chemicals.readthedocs.io/

## Anti-Patterns

- Reporting flash results as exact without stating the EOS, kijs, and zs basis.
- Using flash output as a final design basis for a relief case or for safety
  classification without independent validation.
- Hiding the difference between `PR` and `PRMIXTranslatedPPJP` when reporting
  liquid density.

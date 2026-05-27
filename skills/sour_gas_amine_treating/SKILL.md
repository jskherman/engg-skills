---
name: sour-gas-amine-treating
description: >-
  Screening-level mass-balance helpers for aqueous amine sweetening units
  (DEA, MDEA, MEA, DGA): rich/lean loading, required amine circulation,
  and loading envelope warnings. Use when sanity-checking circulation rate,
  pickup, or rich loading on a sweetening unit. Don't use for rate-based
  reactive simulation (use ProMax, ProTreat, Aspen Amines), foaming /
  corrosion prediction, or rigorous absorber tray-by-tray design.
---

# Sour Gas Amine Treating (Screening)

## Overview

Lightweight mass-balance helpers for aqueous amine sweetening:

- Lean/rich loading in mol acid gas per mol amine from measured flows.
- Required lean amine mass flow for a target rich loading.
- Warning if rich loading exceeds widely cited envelopes (corrosion risk).

This skill is for screening, troubleshooting, and operator-discussion
support. It does NOT model the absorber rate-based kinetics, the
regenerator stripping behaviour, or the corrosion-loading interaction.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## Use when

- Estimating required amine circulation for a known acid gas load.
- Checking whether observed rich loading is in the safe envelope.
- Cross-checking a vendor sizing for a sweetening unit.

## Don't use for

- Rate-based simulation of the absorber or regenerator (use ProMax,
  ProTreat, Aspen Amines).
- Predicting foaming, corrosion, or heat-stable salt formation.
- Selecting the amine itself (DEA vs MDEA vs blends): consult vendor
  recommendations and operating history.

## Utility Scripts

- `uv run scripts/amine.py loading --acid-gas-mol-s 0.5 --amine-mol-s 5 --output /tmp/loading.json`
- `uv run scripts/amine.py circulation --acid-gas-mol-s 0.5 --rich 0.40 --lean 0.05 --amine DEA --wt-fraction 0.30 --output /tmp/circ.json`

## Workflow

1. From the inlet sour-gas composition and flow, compute the acid-gas
   molar load (H2S + CO2). Use `vle-flash-calculations` if needed.
2. Decide a target rich loading (typical envelopes: DEA 0.35-0.45 mol/mol,
   MDEA 0.40-0.55 mol/mol). Cross-check against vendor envelope.
3. Decide a lean loading (regenerator performance dependent; typical
   0.01-0.10 mol/mol).
4. Run `circulation`; the script returns required amine molar and mass
   flow, and the solution mass flow at the chosen wt%.
5. Verify the result against the existing pump capacity and lean amine
   exchanger duty.

## Common Mistakes

- Treating "loading" as wt%; loading is mol acid gas per mol amine. They
  are very different quantities.
- Using a single rich loading for H2S+CO2 mixed streams without thinking
  about the relative absorption rates (DEA absorbs both; MDEA preferentially
  absorbs H2S over CO2).
- Forgetting that the rich loading envelope depends on amine concentration:
  higher wt% generally lower allowable loading due to corrosion.
- Sizing circulation only for the average case and ignoring upsets (e.g.
  feed sulfur swings).
- Assuming the lean amine is at the stripper outlet condition; lean amine
  cooler and pump can change concentration (e.g. cold lean amine may
  contain dissolved gases that re-vapourise in the absorber).
- Using mass balance loading without checking the regenerator's actual
  performance (it may not strip to the assumed lean loading).
- Ignoring heat-stable salt accumulation in long-run operation.

## Fallback Strategies

- For rigorous design, surface to the user that a rate-based simulator is
  required.
- If acid gas load is unknown, use `vle-flash-calculations` to estimate
  H2S/CO2 partial pressures and flow.

## References

- `references/loading_envelopes.md` — published rich loading envelopes and
  caveats.
- GPSA Engineering Data Book (Section 21 — Hydrocarbon Treating).
- Kohl & Nielsen, *Gas Purification* (5th ed).

## Anti-Patterns

- Reporting "amine circulation 100 GPM" without stating lean and rich
  loadings.
- Picking the rich loading from the top of the envelope without an
  operating margin.
- Using this skill output to specify a tower without rigorous review.

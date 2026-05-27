---
name: equation-of-state-selection
description: >-
  Recommend an appropriate equation of state (or activity-coefficient model)
  for a stated fluid system, using the same kind of decision logic that DWSIM,
  Aspen HYSYS, Aspen Plus, and AVEVA PRO/II publish in their property-method
  selection guides. Use when starting a new flow-sheet or property calculation
  and you need a justified pick (PR vs SRK vs PRSV vs translated PR vs IAPWS
  vs activity coefficient vs CPA/SAFT). Don't use to actually run the flash
  (use vle-flash-calculations) or to do steam-table calculations
  (use steam-tables-iapws).
---

# Equation of State Selection

## Overview

A structured decision tool that takes a component list and an application
context (gas processing, refinery LPG, sour gas, amine sweetening, glycol
dehydration, hydrocarbon polymerisation, steam utility, etc.) and returns:

- A primary EOS / property method recommendation.
- The Python backend (thermo class, chemicals correlation, or external).
- Rationale and the public-source basis for the recommendation.
- Specific caveats (binary interaction parameters, volume translation,
  validity range).

The logic is original and based on publicly available documentation from
DWSIM, Carlson's *Don't gamble with physical properties for simulations*
(CEP, 1996), and the Aspen / HYSYS / PRO/II training materials. No
proprietary text, table, or default is reproduced.

## Prerequisites

1. `uv` available on PATH.
2. On first use the script writes `LICENSE_NOTIFICATION.txt` listing the
   underlying library citations.

## Use when

- Starting a flow-sheet and the property method has not been chosen.
- The current method gives results that disagree with lab or plant data.
- A reviewer asks "why did you pick PR?" and you need a defensible answer.

## Don't use for

- Running the actual flash — that is `vle-flash-calculations`.
- Steam tables — that is `steam-tables-iapws`.
- Tuning kij values (this skill recommends a family, not parameter values).

## Utility Scripts

- `uv run scripts/select_eos.py --components propane,n-butane,h2s --application sour_lpg --pressure-pa 1200000 --output /tmp/select.json`
- `uv run scripts/select_eos.py --components methanol,water --application polar_low_pressure --pressure-pa 200000 --output /tmp/select_mw.json`
- `uv run scripts/select_eos.py --components dea,water,h2s,methane --application amine_sweetening --pressure-pa 5000000 --output /tmp/select_amine.json`

## Workflow

1. Enumerate components with their real names. Note any polar, associating,
   electrolyte, or reactive species.
2. State the application context: LPG storage, refinery off-gas, sour gas,
   amine, glycol, electrolyte, polymer, hydrate, supercritical extraction.
3. Note the pressure and temperature range you care about (skip extremes
   only if you are sure the system stays away from them).
4. Run the recommender; it returns a primary pick and an alternative. The
   alternative is the screening "second opinion" — run a flash with both
   and compare densities and K-values.
5. Validate: against lab data, regressed VLE, or a trusted simulator. If the
   primary EOS misses, switch to the alternative and document the swap.
6. Re-run the recommender whenever components, pressure regime, or
   application change materially.

## Common Mistakes

- Using PR for amine sweetening because it is the "default". Amine systems
  need rate-based reactive packages; cubic EOS is screening only.
- Using IAPWS for a water-containing hydrocarbon flash. IAPWS handles only
  pure water/steam; for water + hydrocarbon you need a method that handles
  immiscibility.
- Reaching for SRK as the "industry default". PR has the larger binary
  parameter database in `thermo` / `chemicals` and is usually a better
  starting point for hydrocarbons.
- Picking a cubic EOS for a system containing alcohols, organic acids, or
  water. These associate; CPA (cubic-plus-association) or activity-coefficient
  + Henry's law are usually better.
- Treating the result as final without doing the second-opinion flash.
- Picking a method without naming it in the final report; the property method
  is part of the calculation, not an implementation detail.
- Using one EOS for the whole flowsheet without re-validating at zones where
  the regime changes (e.g. compressor inlet vs cryogenic exchanger outlet).
- Ignoring the model validity envelope when integrating very far in T or P.
- Forgetting to revisit the choice when a new component is added that breaks
  the original system class (e.g. adding water to a hydrocarbon stream).

## Fallback Strategies

- If you cannot identify a clean class for the system, run two flashes with
  PR and SRK and compare against any available data. If they disagree by
  more than 5% in liquid density or 10% in K-value, escalate to an
  experimental data check or a more advanced method.
- If components include known associating species (water, alcohols, organic
  acids), and a CPA or SAFT implementation is not available, fall back to
  Raoult + Antoine for low-pressure screening with a warning.

## References

- `references/decision_matrix.md` — full decision matrix.
- `references/method_validity_ranges.md` — published validity envelopes for
  PR / SRK / PRSV / PR-Translated.
- DWSIM Property Package Selection: https://dwsim.org/wiki/index.php?title=Property_Package_Selection
- Carlson, E.C., "Don't gamble with physical properties for simulations,"
  Chemical Engineering Progress, October 1996.

## Anti-Patterns

- "Aspen uses PR-Peneloux by default, so it must be right."
- "We always use SRK at this site."
- "The simulator converged, so the method is fine."

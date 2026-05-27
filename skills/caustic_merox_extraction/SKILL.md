---
name: caustic-merox-extraction
description: >-
  Screening-level helpers for caustic mercaptan (Merox-style) extraction
  units: RS-Na loading in caustic, Kremser-style stage performance, and a
  disulfide carryback risk score. Use for plant troubleshooting, operator
  discussion, and order-of-magnitude estimation. Don't use for licensor
  design (use the licensor's package), for amine treating (use
  sour-gas-amine-treating), or to predict product disulfide concentration
  exactly — only the carryback risk direction is reliable.
---

# Caustic / Merox Mercaptan Extraction Screening

## Overview

Thin mass-balance helpers built around the chemistry of mercaptan
extraction with aqueous NaOH:

    RSH + NaOH → RS-Na + H2O

and the subsequent regeneration (oxidation):

    2 RS-Na + 0.5 O2 + H2O → RSSR + 2 NaOH

Provides:

- Stoichiometric RS-Na loading at steady extraction.
- Kremser-style stage performance with a user-supplied distribution
  coefficient `K = C_LPG / C_caustic`.
- Risk-score heuristic for disulfide carryback to product LPG (caustic
  disulfide loading + caustic age + separator dP).

These are screening and troubleshooting tools, not licensor design
calculations.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt`.

## Use when

- Troubleshooting a Merox unit (rising RSH slip, caustic age question,
  carryback suspicion).
- Sanity-checking caustic circulation rate vs RS-Na uptake.
- Order-of-magnitude operator discussion.

## Don't use for

- Licensor design (UOP Merox package and successors are proprietary; use
  the licensor's calculations).
- Amine treating: use `sour-gas-amine-treating`.
- Exact prediction of product disulfide concentration — the carryback
  score is directional, not quantitative.

## Utility Scripts

- `uv run scripts/merox.py loading --rsh-ppmw 500 --lpg-kg-s 10 --caustic-kg-s 0.5 --naoh-wt 0.12 --output /tmp/load.json`
- `uv run scripts/merox.py kremser --K 0.02 --lpg-vol 0.014 --caustic-vol 0.0006 --stages 3 --rsh-in 500 --output /tmp/k.json`
- `uv run scripts/merox.py carryback --caustic-disulfide-ppmw 300 --caustic-age-days 60 --separator-dp-kpa 8 --output /tmp/risk.json`

## Workflow

1. Compute RS-Na loading from inlet RSH and current caustic circulation.
2. Compare with the bound-alkalinity available in lean caustic (total
   alkalinity − free alkalinity).
3. If loading is approaching available bound alkalinity, regeneration is
   not keeping pace — investigate the oxidizer / separator side.
4. Use the Kremser estimate to bracket required stages for a given RSH
   removal.
5. Use the carryback risk score to triage process data when product
   disulfide is rising.

## Common Mistakes

- Treating `K` as a constant when it depends on caustic concentration, T,
  and RSH chain length.
- Confusing "free alkalinity" with "total alkalinity" — RS-Na consumption
  reduces free alkalinity.
- Ignoring water carryover between the LPG and caustic phases (and the
  reverse): the coalescer / sand filter is part of the design envelope.
- Treating the carryback heuristic score as quantitative.
- Treating disulfide rise in product solely as a Merox issue when it could
  be feed (DMS / DEDS / DMDS passthrough).
- Forgetting that caustic age increases mercaptide loading even at constant
  RSH inlet; bound alkalinity climbs over time.
- Sizing without considering the disulfide-separator (Stelter/Hsu-style)
  performance.

## Fallback Strategies

- If the Kremser estimate predicts unachievable removal at any reasonable
  stage count, the dominant problem is likely K (poor distribution) rather
  than stages; revisit caustic strength and contactor design.
- If disulfide carryback score is "high" but product disulfide is low,
  there may be a strong DMS feed passthrough; surface to
  `vle-flash-calculations` or product-sulfur speciation skill.

## References

- `references/merox_chemistry.md` — chemistry, regeneration, and the
  practical role of free alkalinity.
- Kohl & Nielsen, *Gas Purification*.
- UOP Merox descriptive literature (public).

## Anti-Patterns

- Reporting "Merox is the cause" without considering feed sulfur
  speciation.
- Treating the carryback score as a value to optimise on rather than a
  triage indicator.
- Using these helpers for licensor design or rerate.

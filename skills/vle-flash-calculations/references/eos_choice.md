# EOS Choice Quick Matrix

This is a short decision matrix to choose an equation of state for `thermo`
flash calculations. For deeper guidance use the `equation-of-state-selection`
skill.

| System | First choice | Comment |
| --- | --- | --- |
| Light hydrocarbon LPG (C2-C5, no acid gas) | `PR` | Largest BIP database; defaults reasonable. |
| LPG / NGL with H2S, mercaptans | `PRSV` or `PRSV2` | Better polar handling; supply real kij. |
| LPG, liquid density critical | `PRMIXTranslatedPPJP` or `PRMIXTranslatedConsistent` | Volume-translated; closer to lab density. |
| Refinery off-gas / fuel gas (CH4, C2, C3, N2, CO2, H2) | `PR` or `SRK` | PR usually wins; SRK as sanity check. |
| Sour natural gas (high H2S/CO2) | `PRSV` with sourced kij | Many references quote sour-PR-style tuning. |
| Polymer, very high MW | NOT cubic EOS | Use SAFT or activity-coefficient method outside this skill. |
| Water + hydrocarbon | NOT plain cubic EOS | Switch to CPA, activity coefficient with Henry, or specialised package. |
| Glycol / amine + light gas | NOT plain cubic EOS for tray-by-tray work | Cubic EOS gives screening only; use rate-based ProMax/ProTreat for design. |

## Key kij ranges (literature)

These are not vendor-quality; verify against your regressed parameters.

- H2S + C1 ~ 0.08; H2S + C2 ~ 0.07; H2S + C3 ~ 0.06.
- CO2 + C1 ~ 0.10; CO2 + C2 ~ 0.13; CO2 + C3 ~ 0.13.
- N2 + C1 ~ 0.03; N2 + C2 ~ 0.05; N2 + C3 ~ 0.07.
- Water + hydrocarbon: do NOT use cubic EOS without explicit aqueous-phase model.

## Volume translation

`PRMIXTranslated` and `PRMIXTranslatedPPJP` need per-component translation
constants `cs`. With `cs = 0` you get plain PR liquid density (too low by
5-15% for typical hydrocarbons). With component-specific cs you get
density within ~1-3% over a wide T range. Document which constants you use.

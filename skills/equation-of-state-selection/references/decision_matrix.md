# Property-Method Decision Matrix

A condensed selection matrix for choosing an equation of state or activity-
coefficient model. Sources are public engineering literature; commercial
simulator default tables are not reproduced.

## Step 1: Classify the system

| Class | Examples |
| --- | --- |
| Pure water / steam | Steam turbines, condensers, utility loops. |
| Light hydrocarbons | LPG, NGL, refinery off-gas, fuel gas. |
| Sour hydrocarbons | Above + H2S, mercaptans, COS. |
| Heavy hydrocarbons | Lubricants, vacuum cuts. |
| Polar liquids | Methanol-water, ethanol-water, acetone-water. |
| Associating species | Alcohols, organic acids, water with hydrocarbons. |
| Electrolytes | Brines, caustic, acid solutions. |
| Polymers | Polyethylene, polypropylene melt phases. |

## Step 2: Pick a property method

| Class | Primary | Secondary | Rationale |
| --- | --- | --- | --- |
| Pure water / steam | IAPWS-IF97 / IAPWS-95 | none | Industry reference. |
| Light hydrocarbons | PR | SRK | PR has the larger BIP database. |
| Sour hydrocarbons | PRSV (with sourced kij) | PR + COSTALD | Sour binary regression matters. |
| Heavy hydrocarbons | PR + volume translation | SRK | Density quality is critical. |
| Polar low-pressure | Activity coefficient (NRTL/UNIQUAC) | Wilson, UNIFAC | gE models in their natural domain. |
| Associating | CPA or PC-SAFT | Activity coefficient + Henry | Associating species violate cubic-EOS assumptions. |
| Electrolytes | e-NRTL / Pitzer | Specialised package | Outside cubic EOS family. |
| Polymers | PC-SAFT (polymer) | SAFT-VR | Cubic EOS fails at large MW. |

## Step 3: Validate before committing

- Run the primary and secondary in parallel for one representative operating
  point and compare density, K-values, and saturation curves against any lab
  data.
- If you have no data, use the most authoritative public reference (NIST
  Webbook, regressed kij sources, peer-reviewed paper) and document it.

## Step 4: Record the choice

The flow-sheet header should state:
- The property method (with version, e.g. PR-1976 vs PR78 vs PR-Translated-PPJP).
- The kij set used (its source).
- The validity envelope for which the choice is justified.
- The intended use (screening, design, operations).

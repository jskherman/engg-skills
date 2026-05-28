# Skill Licenses and Source Notices

You are responsible for ensuring that your use of each skill complies with applicable source terms, API terms, optional dependency licenses, and the license for any data you retrieve. Source URLs and terms may change over time.

Each script in this repository also writes a `LICENSE_NOTIFICATION.txt` file into its own skill directory on first invocation, recording the timestamp at which the user was notified of the upstream terms.

## Infrastructure / Meta

| Skill | Source or terms notes |
| --- | --- |
| `uv` | Uses the `uv` Python package manager. See https://docs.astral.sh/uv/ and https://github.com/astral-sh/uv. |
| `engg-skills-common` | Original shared code in this repository (Apache-2.0). |
| `engineering-skill-creator` | Original repository-specific skill-authoring guidance. |

## Process / Fluids / Heat-Transfer Skills

| Skill | Source or terms notes |
| --- | --- |
| `process-units-conversion` | Original conversion code using common SI relationships. Verify against authoritative unit definitions for regulated work. |
| `dimensionless-numbers` | Original implementation of common published engineering correlations and definitions. |
| `pipe-flow-pressure-drop` | Original Darcy-Weisbach implementation; uses `fluids` (Caleb Bell — MIT). Verify against governing design standards. |
| `two-phase-flow` | Uses `fluids.two_phase` (Caleb Bell — MIT). Correlation references: Lockhart-Martinelli 1949; Beggs-Brill 1973/1991 (procure separately); Mueller-Steinhagen & Heck 1986. |
| `separator-vessel-sizing` | Uses `fluids.separator` (Caleb Bell — MIT). References GPSA Engineering Data Book and API 12J (procure separately; no proprietary text reproduced). |
| `relief-valve-sizing-api520` | Original implementation of API 520 Part I gas/liquid sizing equation forms widely published in the open literature. Standard text NOT reproduced; final design requires the authoritative API 520/521/526 and qualified relief engineering review. |
| `control-valve-sizing-isa75` | Uses `fluids.control_valve` (Caleb Bell — MIT). References ISA 75.01.01 / IEC 60534-2-1 (procure separately). |
| `heat-exchanger-sizing` | Original LMTD helper; uses `ht` (Caleb Bell — MIT). Does not include proprietary TEMA, ASME, API, or vendor design rules. |
| `convective-heat-transfer-correlations` | Pure-Python implementations of classical Dittus-Boelter, Gnielinski, Sieder-Tate, laminar pipe, Churchill-Chu, plus a thin `ht.boiling_nucleic.Rohsenow` wrapper. |
| `material-energy-balances` | Original steady-balance residual helper. |
| `vle-flash-calculations` | Uses `thermo` and `chemicals` (Caleb Bell — MIT). |
| `equation-of-state-selection` | Original heuristic logic based on Carlson (CEP 1996) and DWSIM open documentation. No proprietary simulator defaults reproduced. |
| `distillation-shortcut-design` | Original implementation of Fenske / Underwood / Gilliland (Molokanov form) / McCabe-Thiele. Public textbook methods. |
| `absorption-stripping-design` | Original Kremser-equation implementation. Public textbook method. |
| `reactor-sizing-and-kinetics` | Original isothermal reactor design equations and Arrhenius fit. Public textbook methods. |
| `sour-gas-amine-treating` | Screening mass-balance helpers; references GPSA Engineering Data Book Section 21 and Kohl & Nielsen (procure separately). No proprietary licensor data reproduced. |
| `caustic-merox-extraction` | Screening helpers; references public Merox descriptive literature. No licensor data reproduced. |

## Thermodynamics / Property Skills

| Skill | Source or terms notes |
| --- | --- |
| `steam-tables-iapws` | Uses `chemicals.iapws` IAPWS utilities. Check the `chemicals` package license and IAPWS source terms before production use. See https://chemicals.readthedocs.io/chemicals.iapws.html and https://www.iapws.org/. |
| `thermo-process-properties` | Uses `thermo`, `chemicals`, `fluids`, and `ht` documentation and package behavior. See https://thermo.readthedocs.io/, https://chemicals.readthedocs.io/, https://fluids.readthedocs.io/, and https://ht.readthedocs.io/. Simulator-inspired property-method heuristics are based only on public documentation/training material such as DWSIM property package selection guidance and public Aspen/HYSYS/AVEVA summaries; proprietary algorithms, tables, and internal defaults are not reproduced. |

## Statistics / Data Analysis Skills

| Skill | Source or terms notes |
| --- | --- |
| `engineering-statistics` | Original statistical utilities using Python standard library calculations. |
| `design-of-experiments` | Original factorial-design generator. |
| `statistical-process-control` | Original SPC helper using common control-chart constants. Confirm constants and methods against your quality system. |
| `compositional-data-analysis` | Original implementation of clr/alr/ilr transforms per public CoDA theory (Pawlowsky-Glahn et al.; Egozcue & Pawlowsky-Glahn). |
| `censored-regression` | Original implementation of censored-normal maximum likelihood via SciPy. References Greene's *Econometric Analysis* and Helsel for environmental censored-data practice. |
| `distributed-lag-models` | Original penalised FIR regression implementation; references Almon (Econometrica 1965). Uses NumPy/SciPy. |
| `process-causal-inference-dags` | Original pure-Python DAG / d-separation / back-door adjustment implementation, based on Pearl (*Causality*) and Hernán & Robins. |
| `bayesian-hierarchical-process-models` | Uses PyMC (Apache-2.0) and ArviZ (Apache-2.0). References Gelman et al. *Bayesian Data Analysis*. |
| `time-series-process-data-analysis` | Original implementation of ACF/PACF and Kuensch (1989) moving-block bootstrap. |

## Research Tools

| Skill | Source or terms notes |
| --- | --- |
| `literature-search-engineering` | Builds URLs/reminders for public search services. Check each service's API terms before making requests: OpenAlex (https://docs.openalex.org/), Crossref (https://api.crossref.org/), and others. |

## Standards Referenced (Not Reproduced)

The following engineering standards are referenced by number/title in the
skills above. Skills do NOT reproduce the standard text or tables. You are
responsible for procuring the authoritative standard from the SDO before
relying on the output for design or operations:

- API 520 Part I — Sizing, Selection, and Installation of Pressure-Relieving Devices
- API 521 — Pressure-Relieving and Depressuring Systems
- API 526 — Flanged Steel Pressure-Relief Valves
- API 12J — Specification for Oil and Gas Separators
- ASME BPVC Section VIII Division 1; Section XIII
- ISA 75.01.01 — Industrial-process control valves — Flow capacity
- IEC 60534-2-1 — Industrial-process control valves
- TEMA — Tubular Exchanger Manufacturers Association standards
- GPSA Engineering Data Book — Section 21 (Hydrocarbon Treating), Section 7 (Separators)
- ASTM, AIChE, and other published engineering practice references as cited.

## Library Attributions

- `thermo`, `chemicals`, `fluids`, `ht` (Caleb Bell) — MIT
- `pymc`, `arviz` — Apache-2.0
- `numpy`, `scipy`, `pandas`, `statsmodels` — BSD
- `pytest` — MIT

## Caleb Bell Library-Backed Skills

The following skills delegate calculation to Caleb Bell's `thermo`,
`chemicals`, `fluids`, and `ht` libraries:

- `thermo-process-properties`
- `vle-flash-calculations`
- `two-phase-flow`
- `separator-vessel-sizing`
- `control-valve-sizing-isa75`
- `convective-heat-transfer-correlations`
- `heat-exchanger-sizing`
- `pipe-flow-pressure-drop`
- `steam-tables-iapws`

Simulator-inspired property-method heuristics are based only on public
documentation/training material such as DWSIM property package selection
guidance and public Aspen/HYSYS/AVEVA summaries; proprietary algorithms,
tables, and internal defaults are not reproduced.

# Engineering Skills

Engineering Skills is a curated set of agent skills for chemical engineering, process engineering, applied sciences, and engineering statistics. It follows the same broad packaging conventions used by the Google DeepMind [Science Skills](https://github.com/google-deepmind/science-skills) repository while keeping the content, examples, equations, and code original to this project.

Each skill gives an AI coding agent focused instructions, reusable Python CLI scripts, and compact reference material. The scripts are deterministic where practical, use SI units by default, write JSON outputs through `--output`, and include warnings for preliminary engineering use.

## Included Skills

### Infrastructure

| Skill | Purpose |
| --- | --- |
| `uv` | Confirms the `uv` Python runner is installed and on PATH. |
| `engg-skills-common` | Shared Python package used by all skill scripts. |
| `engineering-skill-creator` | Canonical template for authoring new skills. |

### Thermodynamics and Property Calculations

| Skill | Purpose |
| --- | --- |
| `vle-flash-calculations` | Flash, dew/bubble points, K-values via `thermo` (PR / SRK / PRSV / Translated PR). |
| `equation-of-state-selection` | Decision tree for PR / SRK / PRSV / Translated / IAPWS / activity-coefficient / CPA / SAFT method choice. |
| `thermo-process-properties` | LPG cubic-EOS, COSTALD mixture density, IAPWS, simulator-inspired method recommendation. |
| `steam-tables-iapws` | IAPWS-95 / IF97 water and steam properties through `chemicals.iapws`. |
| `process-units-conversion` | Deterministic unit conversions for common process-engineering quantities. |
| `dimensionless-numbers` | Reynolds, Prandtl, Schmidt, Peclet, Froude, Weber, Biot, Fourier, etc. |

### Unit Operations and Separations

| Skill | Purpose |
| --- | --- |
| `distillation-shortcut-design` | Fenske / Underwood / Gilliland (Molokanov) / McCabe-Thiele. |
| `absorption-stripping-design` | Kremser absorption-factor method for dilute systems. |
| `reactor-sizing-and-kinetics` | Arrhenius fit, CSTR / PFR / batch / N-CSTRs design, numerical PFR. |
| `sour-gas-amine-treating` | DEA/MDEA mass-balance loading and circulation screening. |
| `caustic-merox-extraction` | Mercaptide loading, Kremser extractor, disulfide carryback risk. |

### Fluid Flow and Heat Transfer

| Skill | Purpose |
| --- | --- |
| `pipe-flow-pressure-drop` | Darcy-Weisbach single-phase pressure drop. |
| `two-phase-flow` | Lockhart-Martinelli, Beggs-Brill, Mueller-Steinhagen-Heck. |
| `separator-vessel-sizing` | Souders-Brown vertical / horizontal separator sizing with demister K-factors. |
| `relief-valve-sizing-api520` | API 520 Part I preliminary relief orifice area (gas / liquid). |
| `control-valve-sizing-isa75` | ISA 75.01.01 / IEC 60534 control valve sizing via `fluids`. |
| `heat-exchanger-sizing` | LMTD-based duty and area estimate with F-factor correction. |
| `convective-heat-transfer-correlations` | Dittus-Boelter, Gnielinski, Sieder-Tate, Churchill-Chu, Rohsenow. |
| `material-energy-balances` | Steady-state balance residuals, conversion / selectivity / yield, degree-of-freedom counter. |

### Statistics and Data Analysis

| Skill | Purpose |
| --- | --- |
| `engineering-statistics` | Descriptive statistics, mean CI, simple linear regression. |
| `design-of-experiments` | Full factorial and two-level factorial DOE plans. |
| `statistical-process-control` | Individuals (I-MR), X-bar / R, Cp / Cpk. |
| `compositional-data-analysis` | clr / alr / ilr log-ratio transforms, sequential binary partitions, heavy-end balances. |
| `censored-regression` | Censored-lognormal maximum likelihood for below-LOQ lab data. |
| `distributed-lag-models` | Penalised finite-impulse-response distributed-lag regression with placebo test. |
| `process-causal-inference-dags` | DAG construction, d-separation, back-door adjustment set enumeration, DOT export. |
| `bayesian-hierarchical-process-models` | PyMC hierarchical regression with censoring and AR(1) residuals. |
| `time-series-process-data-analysis` | ACF, PACF, block-length heuristic, Kuensch moving-block bootstrap. |

### Research Tools

| Skill | Purpose |
| --- | --- |
| `literature-search-engineering` | Query-building helpers for OpenAlex / Crossref engineering literature search. |

## Skill Structure

Source skills live under `skills/<skill-name>/`, where `<skill-name>` is the
same lowercase hyphenated slug used in the skill's frontmatter `name` field:

```text
skills/<skill-name>/
  SKILL.md
  scripts/       # optional Python CLIs, run with uv
  references/    # optional equations, assumptions, examples, and source notes
```

Every source `SKILL.md` has YAML frontmatter with Agent Skills-compatible
`name` and `description`, plus `license`, `compatibility`, `version`, and
`metadata.hermes` for Hermes. Body sections use the Hermes-oriented
`When to Use`, `Procedure`, `Pitfalls`, and `Verification` structure.

Validate the source tree directly:

```bash
python3 tools/validate_hermes_skills.py skills --strict-directory-match
```

For packaging or local installation checks, copy the source skills to the
ignored export directory:

```bash
python3 tools/export_agent_skills.py
python3 tools/validate_hermes_skills.py dist/agent-skills --strict-directory-match
```

Utility scripts use `argparse`, require `--output` for JSON results, write the result envelope from `engg_skills_common.io.result_envelope`, and keep stdout to a short success message. Scripts that reference third-party libraries or engineering standards call `engg_skills_common.notices.write_license_notification` on first invocation to drop a one-time `LICENSE_NOTIFICATION.txt` in the skill directory (gitignored runtime artifact).

## Quick Start

Install `uv` if needed, then run tests:

```bash
uv run pytest
```

Run a script directly:

```bash
uv run skills/pipe-flow-pressure-drop/scripts/pipe_pressure_drop.py \
  --length-m 100 \
  --diameter-m 0.05 \
  --flow-m3-s 0.002 \
  --density-kg-m3 998 \
  --viscosity-pa-s 0.001 \
  --roughness-m 0.0000015 \
  --output /tmp/pipe_drop.json
```

Heavy-dependency skills (e.g. `bayesian-hierarchical-process-models` uses `pymc`) declare their dependencies inline in the script's PEP-723 header; the first `uv run` will install them and may take a few minutes for the Bayesian skill.

## Safety Scope

These skills and scripts support preliminary calculations, checking, teaching, and agent workflow grounding. They are not a substitute for qualified engineering judgment, site-specific design review, code compliance, hazard analysis, vendor data, or authoritative standards. Treat outputs as estimates unless independently verified. Skills that touch safety-critical work (`relief-valve-sizing-api520`, `separator-vessel-sizing`, `sour-gas-amine-treating`, `caustic-merox-extraction`) have an explicit Safety and Scope section in their SKILL.md.

## Caleb Bell Python Process-Calculation Stack

This repository treats Caleb Bell's [`thermo`](https://thermo.readthedocs.io/), [`chemicals`](https://chemicals.readthedocs.io/), [`fluids`](https://fluids.readthedocs.io/), and [`ht`](https://ht.readthedocs.io/) libraries as preferred calculation backends when a full GUI process simulator is unavailable. The `engg-skills-common` skill's `engg_skills_common` package wraps these libraries with soft imports and SI defaults.

Simulator-style heuristics are documented as transparent selection rules, not proprietary simulator implementations: IAPWS for water/steam, cubic EOS for nonpolar hydrocarbons at pressure, COSTALD for LPG liquid density screening, and activity-coefficient/specialized models for polar, electrolyte, amine, glycol, sour-water, or reactive systems. The `equation-of-state-selection` skill encodes the decision logic explicitly.

## Attribution

This repository is architecturally inspired by the public `google-deepmind/science-skills` project: https://github.com/google-deepmind/science-skills. No content is copied from that repository. The engineering content here is original and focused on process engineering, thermodynamics, fluid flow, heat transfer, separations, reaction engineering, and applied statistics for process data.

## Licensing

Software in this repository is licensed under Apache License 2.0. Skill documentation and reference notes are provided under the same repository license unless otherwise stated. See `LICENSE`, `NOTICE.md`, and `SKILL_LICENSES.md`. Each skill that uses a third-party library or references an engineering standard also writes a runtime `LICENSE_NOTIFICATION.txt` into the skill directory on first use.

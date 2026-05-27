# Engineering Skills

Engineering Skills is a curated set of agent skills for chemical engineering, process engineering, applied sciences, and engineering statistics. It follows the same broad packaging conventions used by the Google DeepMind Science Skills repository while keeping the content, examples, equations, and code original to this project.

Each skill gives an AI coding agent focused instructions, reusable Python CLI scripts, and compact reference material. The scripts are deterministic where practical, use SI units by default, write JSON outputs through `--output`, and include warnings for preliminary engineering use.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `uv` | Checks and documents the expected `uv` runner workflow. |
| `engg_skills_common` | Shared Python package used by the engineering skill scripts. |
| `process_units_conversion` | Deterministic unit conversions for common process engineering quantities. |
| `dimensionless_numbers` | Reynolds, Prandtl, Nusselt, Froude, Weber, Biot, and related calculations. |
| `pipe_flow_pressure_drop` | Darcy-Weisbach pressure-drop estimates for steady incompressible pipe flow. |
| `heat_exchanger_sizing` | LMTD-based exchanger duty and area estimates. |
| `material_energy_balances` | Component and energy residual checks for simple steady balances. |
| `engineering_statistics` | Descriptive statistics, confidence intervals, and linear regression. |
| `design_of_experiments` | Full-factorial and two-level factorial design helpers. |
| `statistical_process_control` | Individuals, Xbar-R, and basic process capability calculations. |
| `steam_tables_iapws` | IAPWS water/steam properties through `chemicals.iapws`. |
| `thermo_process_properties` | Caleb Bell library-backed process properties: PR EOS, COSTALD LPG density, IAPWS, and property-method heuristics. |
| `literature_search_engineering` | Query-building helpers and API terms reminders for engineering literature search. |
| `engineering_skill_creator` | Guidance for adding new engineering skills in this repository style. |

## Skill Structure

Skills live under `skills/<skill_folder>/` and use this convention:

```text
skills/<skill_folder>/
  SKILL.md
  scripts/       # optional Python CLIs, run with uv
  references/    # optional equations, assumptions, examples, and source notes
```

Every `SKILL.md` starts with YAML frontmatter containing `name` and `description`. Utility scripts use `argparse`, require `--output` for JSON results, and keep stdout to a short success message.

## Quick Start

Install `uv` if needed, then run tests:

```bash
uv run pytest
```

If `uv` is not available, the pure-Python tests can usually be run with:

```bash
python -m pytest
```

Run a script directly:

```bash
uv run skills/pipe_flow_pressure_drop/scripts/pipe_pressure_drop.py \
  --length-m 100 \
  --diameter-m 0.05 \
  --flow-m3-s 0.002 \
  --density-kg-m3 998 \
  --viscosity-pa-s 0.001 \
  --roughness-m 0.0000015 \
  --output /tmp/pipe_drop.json
```

## Safety Scope

These skills and scripts support preliminary calculations, checking, teaching, and agent workflow grounding. They are not a substitute for qualified engineering judgment, site-specific design review, code compliance, hazard analysis, vendor data, or authoritative standards. Treat outputs as estimates unless independently verified.

## Attribution

This repository is architecturally inspired by the public `google-deepmind/science-skills` project: https://github.com/google-deepmind/science-skills. No content is copied from that repository. The engineering content here is original and focused on process engineering and applied statistics.

## Licensing

Software in this repository is licensed under Apache License 2.0. Skill documentation and reference notes are provided under the same repository license unless otherwise stated. See `LICENSE`, `NOTICE.md`, and `SKILL_LICENSES.md`.


## Caleb Bell Python Process-Calculation Stack

This repository now treats Caleb Bell's `thermo`, `chemicals`, `fluids`, and `ht` libraries as preferred calculation backends when a full GUI process simulator is unavailable. The `thermo_process_properties` skill includes LPG/light-hydrocarbon examples using translated Peng-Robinson EOS (`thermo.eos_mix.PRMIXTranslatedPPJP`), COSTALD liquid density via `chemicals.volume`, and IAPWS water/steam calculations via `chemicals.iapws`.

Simulator-style heuristics are documented as transparent selection rules, not proprietary simulator implementations: IAPWS for water/steam, cubic EOS for nonpolar hydrocarbons at pressure, COSTALD for LPG liquid density screening, and activity-coefficient/specialized models for polar, electrolyte, amine, glycol, sour-water, or reactive systems.

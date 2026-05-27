# Skill Licenses and Source Notices

You are responsible for ensuring that your use of each skill complies with applicable source terms, API terms, optional dependency licenses, and the license for any data you retrieve. Source URLs and terms may change over time.

| Skill | Source or terms notes |
| --- | --- |
| `uv` | Uses the `uv` Python package manager. See https://docs.astral.sh/uv/ and https://github.com/astral-sh/uv. |
| `engg_skills_common` | Original shared code in this repository. |
| `process_units_conversion` | Original conversion code using common SI relationships. Verify against authoritative unit definitions for regulated work. |
| `dimensionless_numbers` | Original implementation of common published engineering correlations and definitions. |
| `pipe_flow_pressure_drop` | Original Darcy-Weisbach implementation using standard friction-factor correlations. Verify against governing design standards. |
| `heat_exchanger_sizing` | Original LMTD helper. Does not include proprietary TEMA, ASME, API, or vendor design rules. |
| `material_energy_balances` | Original steady-balance residual helper. |
| `engineering_statistics` | Original statistical utilities using Python standard library calculations. |
| `design_of_experiments` | Original factorial-design generator. |
| `statistical_process_control` | Original SPC helper using common control-chart constants. Confirm constants and methods against your quality system. |
| `steam_tables_iapws` | Optional helper can use the third-party `iapws` Python package if installed. Check that package license and IAPWS source terms before production use. See https://pypi.org/project/iapws/ and https://www.iapws.org/. |
| `literature_search_engineering` | Builds URLs/reminders for public search services. Check each service's API terms before making requests: arXiv, Crossref, OpenAlex, Semantic Scholar, PubMed, and other selected sources. |
| `engineering_skill_creator` | Original repository-specific skill-authoring guidance. |

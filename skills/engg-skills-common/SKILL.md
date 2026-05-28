---
name: engg-skills-common
description: >-
  Shared Python package used by all engineering skill scripts in this
  repository (JSON envelope, license-notification helper, dimensionless
  numbers, fluids/heat-transfer wrappers, VLE/separations/reactor
  helpers, compositional data, causal DAG, time-series, separator/valve
  helpers). Use when authoring a new skill or refactoring an existing one
  that needs shared utilities. Don't use as a user-facing skill — it has
  no CLI and no engineering output of its own.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [skills, tooling, engg, common]
    category: infrastructure
---

# engg-skills-common (Shared Library)

## Overview

This is a developer-facing skill describing the shared Python package
`engg_skills_common`. All engineering-skill scripts import from it. It
contains:

- `io.py` — JSON envelope, `write_json`, number parsing helpers.
- `notices.py` — warning strings, source notices, and the
  `write_license_notification` helper for the first-use
  `LICENSE_NOTIFICATION.txt` artifact.
- `dimensionless.py`, `units.py`, `stats.py`, `doe.py`, `spc.py`,
  `balances.py`, `fluids.py`, `heat_transfer.py` — original pure-Python
  helpers.
- `property_backends.py` — thin wrappers around `thermo`, `chemicals`,
  `fluids`, `ht` with soft imports and engineering defaults for LPG.
- `vle.py`, `separations.py`, `reactor.py`, `separator.py`, `valves.py`,
  `two_phase.py`, `convection.py`, `coda.py`, `causal.py`,
  `timeseries.py`, `amine.py`, `merox.py` — newer domain modules.

The package is intentionally light: heavy dependencies (`pymc`, `arviz`,
`statsmodels`) are NEVER imported at module load time. They are loaded
lazily inside the scripts that need them.

## When to Use

- Authoring a new skill that needs a shared helper.
- Adding a new shared module for a class of calculations.
- Reviewing the standard JSON envelope or notification pattern.

## Don't use for

- Running engineering calculations directly — go through a skill script.
- Adding a heavy ML dependency at module load; use the script PEP-723
  header instead.

## Conventions

- All functions take keyword arguments for clarity in scripts.
- All functions return plain dicts so `json.dumps` works.
- Validation errors raise `ValueError`; missing optional libraries raise
  a clear `RuntimeError` via `_require_library`.
- Names are descriptive with unit suffixes (e.g. `rho_kg_m3` not `rho`).

## Procedure

1. Read this SKILL.md and any referenced files needed for the task.
2. Use scripts from `scripts/` when a deterministic calculation or check is available.
3. Preserve stated assumptions, warnings, and scope limits in the final answer.

## Pitfalls

- Adding a heavy dependency import at the top of a module instead of
  using `_require_library` inside the function.
- Returning numpy arrays or pandas Index objects in a result dict — they
  do not JSON-serialise. Convert to lists / floats first.
- Mutating a caller's input list/dict in place.
- Writing a function that does I/O. The shared library does math and
  light orchestration; I/O belongs in the script.

## Tests

Tests live in `tests/`. Each module should have a dedicated
`test_<module>.py` with at least three tests covering: a typical case,
an edge case (zero / empty), and an error case.

## Verification

- Run `.venv/bin/python -m pytest -q` or `pytest -q` from the repository root after changing shared modules.
- Confirm scripts that import `engg_skills_common` resolve it from `skills/engg-skills-common`.

## References

- See each skill's SKILL.md for the user-facing usage.
- `skills/engineering-skill-creator/references/script_template.md` for
  the canonical CLI shape that consumes this library.

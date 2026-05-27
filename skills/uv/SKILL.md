---
name: uv
description: >-
  Confirm the `uv` Python package manager is installed and available on
  PATH and document the standard `uv run script.py --output ...` invocation
  used by every other skill in this repository. Use as a prerequisite check
  before invoking any other engineering skill. Don't use as a substitute
  for actually running a skill — it does no engineering work itself.
---

# uv (Python runner)

## Overview

Every other skill in this repository runs its scripts via `uv run`
(PEP-723 inline dependency declaration). This skill is a one-page check:
"is `uv` on PATH, and if not, how do you install it?"

## Use when

- Setting up the environment for the first time.
- A skill invocation has failed with `uv: command not found`.

## Don't use for

- Any engineering calculation.
- Authoring a new skill (use `engineering-skill-creator` instead).

## Setup

If `uv` is missing, install it from https://docs.astral.sh/uv/ . The
common path on Linux/macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then verify:

```bash
uv --version
```

## Conventions

- Every script in this repository is invoked as
  `uv run <path>/scripts/<name>.py <subcommand> --<flag> <value> --output /tmp/<name>.json`.
- The script header declares dependencies inline (PEP-723); `uv run` will
  install them the first time and cache for subsequent runs.
- Stdout is reserved for a single success message; results live in the
  JSON file at `--output`.

## Common Mistakes

- Trying to `python` a script directly rather than `uv run`; the script
  header won't be respected.
- Running scripts from a different working directory than the skill folder
  — works, but path-based imports of `engg_skills_common` use the script's
  own directory, which is robust.

## References

- https://docs.astral.sh/uv/
- https://github.com/astral-sh/uv

## Anti-Patterns

- Installing `uv` globally with `sudo`; let the install script handle it.
- Pinning `uv` versions in skill scripts; the PEP-723 dependencies pin the
  Python deps, and `uv` itself should be free to update.

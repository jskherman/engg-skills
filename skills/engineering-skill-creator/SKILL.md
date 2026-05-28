---
name: engineering-skill-creator
description: >-
  Author a new skill for this repository in the established format: YAML
  frontmatter with `Use when... Don't use for...` description, Pitfalls
  catalogue, Procedure checklist, fallback strategies, JSON output
  envelope, and (where third-party libraries or standards are referenced)
  a first-use `LICENSE_NOTIFICATION.txt` artifact. Use when you are adding
  a new skill or refactoring an existing one. Don't use to add features to
  an existing skill without rewriting its SKILL.md.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [skills, tooling, engineering, skill, creator]
    category: infrastructure
---

# Engineering Skill Creator

## Overview

This meta-skill is the canonical template for any new engineering skill in
this repository. The convention mirrors Google DeepMind's `science-skills`
format (YAML frontmatter, scripts that always write to `--output`, JSON
envelope, first-use license notification) and adds engineering-specific
elements: explicit safety scope where relevant, sources listed in
`SKILL_LICENSES.md`, fallback strategies for missing optional dependencies,
and an anti-patterns section.

Use this skill as the reference whenever you create a new skill or rewrite
an existing one. The template files in `references/` are the source of
truth for the format.

## When to Use

- You are adding a brand-new skill folder.
- You are refactoring an existing skill to the current format.
- You are documenting an internal review of the format itself.

## Don't use for

- Adding a new script to an existing skill without rewriting the SKILL.md.
- Editing the shared `engg-skills-common` library (that is developer code,
  not a user-facing skill).
- Authoring the `uv` infrastructure skill (it has its own minimal shape).

## Core Rules

- The YAML `description` MUST follow the pattern: `<one-sentence what the
  skill does>. Use when <scenarios>. Don't use for <complementary scope>`.
- Every script writes JSON via `result_envelope()` (or DOT/text for the
  rare diagrammatic case) and requires `--output` as the only output channel.
- Stdout is reserved for a single success message; warnings/diagnostics go
  inside the JSON envelope.
- If the script references any third-party library, standard, or external
  API, it MUST call `write_license_notification()` on first invocation.
- The skill MUST list at least 8 specific common mistakes for the domain.
- Procedure sections MUST be numbered checklists, not prose paragraphs.
- Fallback strategies MUST cover at least one realistic failure mode
  (missing dep, edge case input, etc.).

## Utility Scripts

This meta-skill does not have scripts; the templates in `references/` are
copy-paste starting points.

## Procedure

1. Pick a lowercase hyphenated folder name (e.g. `vle-flash-calculations`) and use the same value in frontmatter `name`.
2. Create `skills/<name>/SKILL.md` from `references/skill_template.md`.
3. Create `skills/<name>/scripts/<short_name>.py` using the PEP-723
   header pattern and the `result_envelope` + `write_license_notification`
   helpers.
4. Create `skills/<name>/references/<topic>.md` documents for any
   methodology or background the user (or a code reviewer) will need.
5. If the script needs a new pure-Python or thin-wrapper helper, add it to
   `skills/engg-skills-common/engg_skills_common/<module>.py` and import
   from the script via the established `sys.path.insert` pattern.
6. Add tests in `tests/test_<module>.py` covering at least one happy path,
   one edge case, and one error case for any new shared-library function.
7. Append a row to `SKILL_LICENSES.md` summarising the upstream sources
   and the engineering standards referenced (numbers only, not text).
8. Add a row to the README skill table.
9. Run `uv run pytest -q` and at least one end-to-end script invocation
   before committing.

## Pitfalls

- Writing a generic description like "Use when a user asks for engineering
  work matching this scope" — that defeats skill routing.
- Reproducing standard text (API, ASME, ISA, GPSA, TEMA): cite the number
  only and require the user to procure the standard.
- Embedding kij values, NIST table data, or vendor correlations without
  attribution; cite the source for every number.
- Forgetting the `LICENSE_NOTIFICATION.txt` first-use call when the script
  imports a third-party library.
- Putting heavy dependencies (`pymc`, `arviz`) in the project-level
  `pyproject.toml`; declare them in the script's PEP-723 header instead so
  users pay the cost only for the skills that need them.
- Returning Python objects from `result_envelope` `results` field that
  cannot be JSON-serialised (numpy types, pandas Index). Convert to native
  Python first.
- Forgetting to round / sanity-check final numbers in the script before
  emitting them. The JSON should look correct without further processing.
- Skipping the "fallback strategies" section because the happy path works.
- Writing scripts that print results to stdout; the contract is JSON-only.
- Putting safety-critical wording in a single paragraph without a
  dedicated "Safety and Scope" section.

## Fallback Strategies

- If the skill borders on a regulated calculation (relief, pressure
  vessel, electrical area classification), make the "Safety and Scope"
  section explicit and decline to produce final-design numbers.
- If a third-party library is not installable in some environments, the
  script should give a clear error message naming the missing library and
  the install command.

## Verification

- Run `python3 tools/validate_hermes_skills.py skills --strict-directory-match` after adding or rewriting a skill.
- Confirm the skill folder name matches `name`, the description includes routing guidance, and referenced scripts or files exist.

## References

- `references/skill_template.md` — copy-paste SKILL.md template.
- `references/calculation_result_schema.md` — JSON envelope schema.
- `references/script_template.md` — copy-paste Python CLI template.

## Anti-Patterns

- Authoring a skill whose description is duplicated verbatim from another
  skill.
- Producing skill content that quotes standards extensively rather than
  citing them.
- Authoring a script that does work outside its declared scope.

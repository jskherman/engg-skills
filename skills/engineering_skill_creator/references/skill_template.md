# SKILL.md Template

Copy this and replace the bracketed placeholders. This follows the AgentSkills
`SKILL.md` shape and adds Hermes-compatible metadata. Keep `name` and
`description` concise because agents use them for skill discovery before loading
the full skill body.

```markdown
---
name: <kebab-case-skill-name>
description: >-
  <Brief description of what this skill does. Use when ... Don't use for ...>
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
version: 1.0.0
metadata:
  hermes:
    tags: [<domain>, <method>, <tooling>]
    category: <category-slug>
---

# <Title Case Skill Name>

## When to Use

- <Trigger condition 1>
- <Trigger condition 2>
- <Trigger condition 3>

## Procedure

1. <Identify inputs / classify the problem.>
2. <Choose method / settings.>
3. <Run the script or follow the manual procedure.>
4. <Validate the result against an independent source.>
5. <Cross-check with a sensitivity analysis or known limit.>

## Pitfalls

- <Specific domain mistake 1 and the mitigation.>
- <Specific domain mistake 2 and the mitigation.>
- <Specific domain mistake 3 and the mitigation.>

## Verification

- <Check expected files or JSON outputs exist.>
- <Check result magnitudes, units, and warning fields.>
- <State what independent source or engineering sanity check should agree.>

## References

- `references/<file>.md` — <one-line description>
- <Public textbook, standard, paper, or package documentation reference>

## Safety and Scope  *(only if the skill touches regulated or safety-critical work)*

<Explicit statement that the output is preliminary screening, that final design
needs the authoritative standard and qualified engineering review.>
```

## Notes

- In the exported AgentSkills tree, the parent folder name must match the
  frontmatter `name`. Use `tools/export_agent_skills.py` to generate that tree
  from this repository's source `skills/` directory.
- Additional sections such as `## Utility Scripts`, `## Examples`, or
  `## Anti-Patterns` are allowed, but keep the four Hermes core sections:
  `When to Use`, `Procedure`, `Pitfalls`, and `Verification`.
- Put detailed derivations and long tables in `references/` and link them from
  the skill body to preserve progressive disclosure.
- Put executable helpers in `scripts/`; require `--output` for machine-readable
  results where practical.
- For platform-specific skills, add `platforms: [linux]`, `platforms: [macos]`,
  or `platforms: [windows]` in the frontmatter.
- For conditional Hermes activation, use `metadata.hermes.requires_toolsets`,
  `metadata.hermes.fallback_for_toolsets`, `metadata.hermes.requires_tools`, or
  `metadata.hermes.fallback_for_tools` as documented by Hermes.

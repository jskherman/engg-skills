# Contributing

Thanks for improving Engineering Skills. Contributions should keep the repository useful for practical engineering workflows while being explicit about assumptions, limitations, sources, and safety.

## Development Setup

Use `uv` for the normal workflow:

```bash
uv run pytest
```

The shared package is located at `skills/engg_skills_common/engg_skills_common`. Skill scripts import it directly from the repository layout so they can run without publishing a package.

## Skill Requirements

Each skill must include:

- `skills/<skill_folder>/SKILL.md`
- YAML frontmatter with `name` and `description`
- A clear overview, dependencies, quick start, workflow, common mistakes, and safety/source notices
- `scripts/` when deterministic computation, API interaction, file parsing, or repeatable data transformation is useful
- `references/` when equations, examples, assumptions, or source terms need more space

Scripts must:

- Use `argparse`
- Require `--output`
- Write JSON with `indent=2`
- Print only a short success/status message to stdout
- Include warnings that outputs are for preliminary engineering use
- Avoid proprietary standard text, copyrighted tables, or copied examples
- Handle invalid inputs with clear errors

## Tests

Add focused tests for shared utilities and deterministic calculations. Prefer small numerical examples with transparent expected values over broad snapshot tests.

Run:

```bash
uv run pytest
```

## Sources and Standards

Do not copy proprietary codes, standards, textbook tables, vendor tables, or subscription content. You may cite public documentation, open-source libraries, and well-known equations. When a skill relies on a third-party service or optional dependency, update `SKILL_LICENSES.md` with terms/source links.

## Safety Language

Engineering calculations can affect safety, environmental performance, cost, and compliance. Keep warnings visible in both `SKILL.md` and script JSON outputs. When a method has known limits, state them near the command that uses the method.

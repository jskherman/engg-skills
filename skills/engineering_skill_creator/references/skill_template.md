# SKILL.md Template

Copy this and replace the bracketed placeholders. Keep the section order so
all skills in the repository are scannable in the same way.

```markdown
---
name: <kebab-case-skill-name>
description: >-
  <One sentence stating what the skill does>. Use when <enumerate the
  scenarios>. Don't use for <complementary scope: at least 2 things and 1
  related skill to redirect to>.
---

# <Title Case Skill Name>

## Overview

<2-4 sentences. State the methods used and the underlying Python library
or theoretical basis. Keep claims modest.>

## Prerequisites

1. `uv` available on PATH.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt` listing
   upstream library and standards terms.

## Use when

- <Scenario 1>
- <Scenario 2>
- <Scenario 3>

## Don't use for

- <Scope 1>
- <Scope 2>
- <Cross-reference a related skill>

## Safety and Scope  *(only if the skill touches regulated or safety-critical work)*

<Explicit statement that the output is preliminary screening, that final
design needs the authoritative standard and qualified engineering review.>

## Utility Scripts

- `uv run scripts/<name>.py <subcommand> --<flag> <value> --output /tmp/<name>.json`
- (1-5 representative commands)

## Workflow

1. <Identify inputs / classify the problem>
2. <Choose method / settings>
3. <Run the script>
4. <Validate the result against an independent source>
5. <Cross-check with a sensitivity analysis>

## Common Mistakes

- <Specific domain mistake 1>
- <Specific domain mistake 2>
- (8-12 items)

## Fallback Strategies

- <Specific fallback for a missing dependency or edge-case input>
- <Specific fallback for invalid result conditions>

## References

- `references/<file>.md` — <one-line description>
- <Public textbook or paper reference>

## Anti-Patterns

- <Bad practice 1>
- <Bad practice 2>
- (3-5 items)
```

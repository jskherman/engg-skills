---
name: literature-search-engineering
description: >-
  Search engineering literature metadata through OpenAlex and Crossref while tracking source terms. Use when a user asks for chemical engineering, process engineering, applied science, or statistics work matching this scope.
---

# Literature Search Engineering

## Overview

Search engineering literature metadata through OpenAlex and Crossref while tracking source terms.

## Core Rules

- Prefer the provided script for repeatable calculations or data access.
- Require explicit units and assumptions; never invent missing physical property data.
- Write machine-readable outputs to JSON when a script is used.
- Report assumptions, warnings, methods, and sources.
- Keep proprietary standards, handbook tables, and copyrighted examples out of outputs unless the user supplies authorized excerpts.

## Source Terms

Before using external APIs, check `SKILL_LICENSES.md` and the current OpenAlex/Crossref documentation. Cite DOI/URL/source metadata in final answers.

## Workflow

1. Identify the engineering question and required inputs.
2. Check scope limits and safety/compliance implications.
3. Run the relevant script or follow the documented method.
4. Inspect warnings and validate units/magnitude.
5. Summarize results with assumptions, limitations, and next verification steps.

## Anti-Patterns

- Treating preliminary calculations as final design.
- Hiding unit conversions or basis assumptions.
- Reproducing proprietary standards or vendor tables.
- Presenting estimates without uncertainty/validity notes.

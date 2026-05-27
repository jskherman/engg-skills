---
name: engineering-statistics
description: >-
  Analyze engineering/lab/process data with descriptive statistics, confidence intervals, and simple regression. Use when a user asks for chemical engineering, process engineering, applied science, or statistics work matching this scope.
---

# Engineering Statistics

## Overview

Analyze engineering/lab/process data with descriptive statistics, confidence intervals, and simple regression.

## Core Rules

- Prefer the provided script for repeatable calculations or data access.
- Require explicit units and assumptions; never invent missing physical property data.
- Write machine-readable outputs to JSON when a script is used.
- Report assumptions, warnings, methods, and sources.
- Keep proprietary standards, handbook tables, and copyrighted examples out of outputs unless the user supplies authorized excerpts.

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

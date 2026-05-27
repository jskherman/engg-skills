---
name: material-energy-balances
description: >-
  Support material and energy balance workflows, component totals, conversion, selectivity, yield, and degree-of-freedom thinking. Use when a user asks for chemical engineering, process engineering, applied science, or statistics work matching this scope.
---

# Material Energy Balances

## Overview

Support material and energy balance workflows, component totals, conversion, selectivity, yield, and degree-of-freedom thinking.

## Core Rules

- Prefer the provided script for repeatable calculations or data access.
- Require explicit units and assumptions; never invent missing physical property data.
- Write machine-readable outputs to JSON when a script is used.
- Report assumptions, warnings, methods, and sources.
- Keep proprietary standards, handbook tables, and copyrighted examples out of outputs unless the user supplies authorized excerpts.

## Safety and Scope

Outputs are preliminary engineering calculations only. Do not use them as final design, operations, code-compliance, pressure-containing equipment, relief-device, or safety decisions without qualified engineering review and validated plant data.

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

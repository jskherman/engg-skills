---
name: statistical-process-control
description: >-
  Build individuals (I-MR) and X-bar / R control charts and compute basic
  process capability indices (Cp, Cpk) from quality-control data. Use
  when monitoring product quality on a stable process. Don't use on data
  that is strongly autocorrelated (use time-series-process-data-analysis
  to diagnose first), on highly skewed / censored measurements (use
  censored-regression for left-censored data), or as a substitute for a
  six-sigma improvement framework.
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [statistics, process-data, data-analysis, statistical, process, control]
    category: statistics-data-analysis
---

# Statistical Process Control

## Overview

Pure-Python SPC helpers:

- Individuals chart (I-MR) with control limits from the moving range.
- X-bar / R chart with constants from the standard SPC tables.
- Cp and Cpk capability indices.

The chart constants (A2, D3, D4, d2, etc.) are public-domain values widely
republished in textbooks; verify against your quality system's standard
before regulated reporting.

## Prerequisites

1. `uv` available.

## When to Use

- Computing control limits for a new chart.
- Estimating Cp / Cpk for a stable process with bilateral spec limits.
- Sanity-checking a vendor SPC report.

## Don't use for

- Autocorrelated process data (`time-series-process-data-analysis` first).
- Left-censored or interval-censored measurements
  (`censored-regression`).
- Attribute (count / defective) charts (p, np, c, u charts not
  implemented).
- Multivariate SPC (Hotelling T², MEWMA — not implemented).

## Utility Scripts

- `uv run scripts/spc.py individuals --values "12.3,12.5,12.1,12.4,12.6,12.2" --output /tmp/i.json`
- `uv run scripts/spc.py xbar-r --subgroups "12.3,12.5,12.1|12.4,12.6,12.2|12.2,12.4,12.3" --output /tmp/xr.json`
- `uv run scripts/spc.py capability --values "12.3,..." --usl 13 --lsl 11 --output /tmp/cap.json`

## Procedure

1. Confirm the process is stable (no obvious shifts, trends, autocorr).
2. Pick chart type:
   - Individuals (I-MR) for one measurement per sample.
   - X-bar / R for rational subgroups of 2-10.
3. Compute control limits from a stable baseline window (Phase I); apply
   in real time (Phase II).
4. For capability, ensure the process is centred between spec limits;
   compute Cp and Cpk.
5. Flag out-of-control signals: points beyond 3-sigma, runs of 7+ on the
   same side of the centre line, etc. (Western Electric rules).

## Pitfalls

- Computing Cp / Cpk on a process that is not in statistical control
  (Phase I diagnostics first).
- Using a one-sigma limit ("99.7% will be in tolerance") when the
  underlying distribution is not normal.
- Mixing Phase I (limit estimation) and Phase II (limit application) data.
- Treating Cpk as Cp when only one spec limit applies.
- Ignoring the moving-range constant d2 = 1.128 for n = 2.
- Computing X-bar / R with unequal subgroup sizes (the chart constants
  assume equal n).
- Applying control limits to data with strong autocorrelation; the limits
  become too tight or too wide.
- Reporting Cp / Cpk with too few data points (< ~30 ideally).

## Fallback Strategies

- If autocorrelation is suspected, use `time-series-process-data-analysis`
  to compute ACF; if significant, apply a pre-whitening filter (e.g. ARIMA
  residuals) before SPC.
- If censoring is suspected, see `censored-regression`.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/control_charts.md` — chart constants and formulas.
- Montgomery, *Introduction to Statistical Quality Control*.

## Anti-Patterns

- Reporting "process out of control" from a single point beyond 3-sigma
  without checking measurement quality.
- Computing Cpk on visibly bimodal data.
- Using SPC limits to decide on a process change instead of as a
  monitoring tool.

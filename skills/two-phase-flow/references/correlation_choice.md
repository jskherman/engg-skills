# Two-Phase Correlation Choice

| Flow situation | Recommended starting correlation | Notes |
| --- | --- | --- |
| Horizontal, dilute liquid (e.g. small condensate in gas) | Lockhart-Martinelli | ±30% typical accuracy. |
| Inclined or vertical (pipelines, risers) | Beggs-Brill | Handles gravity head; pick the right flow regime. |
| Refrigerant evaporator or smooth quality range | Mueller-Steinhagen-Heck | Smooth interpolation; good default for shell-and-tube. |
| Pure liquid, no vapor | Single-phase (Darcy-Weisbach) | Don't use these correlations for x = 0. |
| Slug-flow piping | Beggs-Brill with caution; consider OLGA-style transient | Spec real-time models for design; the steady correlation underpredicts surge. |

## Always run two correlations

For any design decision, run at least two of the above and document both. A
2x spread between correlations is normal and informs the design margin.

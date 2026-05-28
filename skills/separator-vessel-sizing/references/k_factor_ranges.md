# K-Factor Ranges (Souders-Brown, m/s)

These ranges are widely cited in the public engineering literature (Coker,
Gas Processors Suppliers Association engineering practice, vendor handbooks).
The GPSA Engineering Data Book contains the authoritative full chart; this
file is a transparent screening summary.

| Orientation | Demister | K range (m/s) |
| --- | --- | --- |
| Vertical | none | 0.030 - 0.075 |
| Vertical | demister pad | 0.070 - 0.110 |
| Horizontal | none | 0.040 - 0.090 |
| Horizontal | demister pad | 0.090 - 0.150 |

## Interpretation

- Use the midpoint of the range as a starting point.
- Drop toward the bottom of the range when liquid loading is high, the
  feed is foamy, or particulate fouling is a concern.
- Push toward the top of the range only when vendor or test data justify it.

## Watkins refinement

`fluids.separator.K_separator_Watkins(x, rhol, rhog, horizontal)` returns a
K that adjusts for the entrainment behaviour at the specified quality `x`.
Use it when quality is known and you want a less conservative size.

## Pressure dependence

GPSA shows K vs operating pressure for typical demister vessels: K decreases
mildly with rising pressure (e.g. K ~ 0.10 at 7 bar dropping to ~ 0.07 at
70 bar for horizontal with demister). Use the Watkins helper or vendor data
for high-pressure service.

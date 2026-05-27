# Typical Kd Values (Preliminary Use Only)

Per ASME Section VIII Div 1, the discharge coefficient used for sizing
without certification must not exceed the published "preliminary" caps:

- Gas / vapor PRV: `Kd ≤ 0.975`
- Liquid PRV: `Kd ≤ 0.65`

Once a manufacturer is selected, the vendor's certified (or "rated") Kd
applies, which is usually higher than these caps. Update the calculation
with the certified Kd before issuing the valve specification.

## Correction factors

| Symbol | Description | Typical |
| --- | --- | --- |
| `Kb` | Back-pressure correction for conventional spring valves | 1.0 if built-up back-pressure < 10% of set; otherwise from API 520 chart. |
| `Kc` | Combination factor for PRV downstream of a non-reclosing device | 0.9 if rupture disk in series. |
| `Kw` | Liquid back-pressure correction for balanced bellows | 1.0 if back-pressure < 18% of set; otherwise from chart. |
| `Kv` | Viscosity correction for liquid PRV | 1.0 if Re > ~100,000; otherwise from API 520 Figure 38. |

Always confirm the controlling case (blocked discharge, fire, thermal
expansion, tube rupture, etc.) and use the consistent relieving conditions
(per ASME Section VIII).

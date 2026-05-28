# Method Validity Ranges (Public Literature)

Order-of-magnitude validity envelopes drawn from textbook references and the
authors' published validation studies. Verify against your operating
envelope before relying on these as design constraints.

| Method | T range | P range | System class | Density accuracy | K-value accuracy |
| --- | --- | --- | --- | --- | --- |
| PR (1976) | -200 to 1000 C | 0 to ~300 bar | Light to mid hydrocarbon | Liquid ~5-15% low; vapor < 1% | Within 5-10% with sourced kij |
| PR-Translated (PPJP / Consistent) | Same as PR | Same as PR | Same as PR | Liquid ~1-3% | Same as PR |
| SRK | Similar to PR | Similar to PR | Hydrocarbon | Liquid ~5-15% low | Within 5-10% with kij |
| PRSV | Same as PR | Same as PR | Mildly polar (H2S, CO2) | Same as PR | Better than PR for polar |
| IAPWS-IF97 | 273-1073 K (industrial) | 0-100 MPa | Water/steam only | ~0.5-1% | n/a (pure substance) |
| IAPWS-95 | Full phase diagram | Up to saturation curve | Water/steam only | ~0.01-0.1% | n/a |
| Activity coefficient (NRTL/UNIQUAC) | Below boiling point typically | Low (< 5 bar) | Polar liquid mixtures | n/a (different basis) | Depends on regressed parameters |
| CPA | Wide | Wide | Associating fluids | 2-5% with regressed params | Within 5% with kij |
| PC-SAFT | Wide | Wide | Associating, polymers, asymmetric | 1-5% | 5-10% |

## Notes

- "Liquid density 5-15% low" for plain PR/SRK is the well-known weakness;
  use volume-translated variants if density matters.
- For PRSV the alpha function uses an extra parameter (`kappa1`); supply it
  per component if you have it.
- The validity ranges above are general; check the original reference for
  the specific binary or ternary you care about.

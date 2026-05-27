# Property Method Selection Notes

Open simulator documentation commonly groups property methods into:

- Ideal/Raoult methods for simple low-pressure systems.
- Cubic EOS methods such as Peng-Robinson and SRK for nonpolar gases and hydrocarbons, especially at elevated pressure.
- Activity-coefficient models such as NRTL, UNIQUAC, Wilson, Van Laar, and UNIFAC for polar/nonideal liquid systems.
- Special systems: steam tables/IAPWS for water, amine/glycol/electrolyte/sour-water/hydrate packages for specialized service.

Practical checks:

1. Define components, phases, composition basis, and T/P range.
2. Identify polar/nonpolar/electrolyte/associating behavior.
3. Check whether binary interaction parameters are available.
4. Select the simplest model with credible validity for the application.
5. Validate important outputs against experiment, plant data, or a trusted simulator.

Public sources used for heuristics include DWSIM property package selection guidance, Aspen Plus/HYSYS public property-method training material, and AVEVA PRO/II public thermodynamics capability summaries. Do not copy proprietary simulator tables or internal algorithms.

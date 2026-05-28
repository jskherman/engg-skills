# Caleb Bell Library Mapping

- `thermo.eos_mix.PRMIXTranslatedPPJP`: low-level translated Peng-Robinson mixture EOS object useful for explicit LPG EOS checks.
- `thermo.ChemicalConstantsPackage.from_IDs`, `CEOSGas`, `CEOSLiquid`, `FlashVL`, `FlashVLN`: higher-level flash workflow building blocks.
- `chemicals.volume.COSTALD_mixture` and `COSTALD_mixture_compressed`: light-hydrocarbon liquid density screening.
- `chemicals.iapws.iapws95_properties`, `Psat_IAPWS`, `Tsat_IAPWS`: water/steam properties.
- `fluids.friction_factor`, `fluids.Reynolds`, `fluids.two_phase_dP`, `fluids.nearest_pipe`: hydraulics.
- `ht.LMTD`, `ht.F_LMTD_Fakheri`, `ht.effectiveness_NTU_method`, `ht.Nu_conv_internal`: heat transfer.

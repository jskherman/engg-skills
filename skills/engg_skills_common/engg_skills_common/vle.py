"""Vapor-liquid equilibrium and flash helpers using Caleb Bell's thermo.

These wrappers assemble a `ChemicalConstantsPackage`, a
`PropertyCorrelationsPackage`, and a chosen cubic EOS, then run a flash. The
return is a plain dict so JSON serialization in `result_envelope` is trivial.

Design rules:

- Soft import of `thermo`/`chemicals` so the common library still imports on
  slim runtimes.
- EOS choice is exposed; the recommendation matrix lives in
  `engg_skills_common.property_backends` and the
  `equation_of_state_selection` skill.
- Binary interaction parameters default to zeros; the caller MUST supply
  real kij values for sour-gas, amine, or polar systems.
"""

from __future__ import annotations

from typing import Any

from .property_backends import normalize_zs, _require_library


SUPPORTED_EOS = {
    "PR": "thermo.eos_mix.PRMIX",
    "SRK": "thermo.eos_mix.SRKMIX",
    "PR78": "thermo.eos_mix.PR78MIX",
    "PRSV": "thermo.eos_mix.PRSVMIX",
    "PRSV2": "thermo.eos_mix.PRSV2MIX",
    "PRTranslated": "thermo.eos_mix.PRMIXTranslated",
    "PRTranslatedPPJP": "thermo.eos_mix.PRMIXTranslatedPPJP",
    "PRTranslatedConsistent": "thermo.eos_mix.PRMIXTranslatedConsistent",
    "VDW": "thermo.eos_mix.VDWMIX",
}


def _get_eos_class(eos_name: str):
    eos_mod = _require_library("thermo.eos_mix", "thermo")
    if not hasattr(eos_mod, "ndarray"):
        eos_mod.ndarray = tuple
    if eos_name not in SUPPORTED_EOS:
        raise ValueError(
            f"Unsupported EOS {eos_name!r}; choose from {sorted(SUPPORTED_EOS)}"
        )
    class_name = SUPPORTED_EOS[eos_name].split(".")[-1]
    if not hasattr(eos_mod, class_name):
        raise RuntimeError(
            f"thermo build does not expose {class_name}; upgrade `thermo` or pick a different EOS."
        )
    return getattr(eos_mod, class_name)


def build_constants_and_correlations(identifiers: list[str]) -> tuple[Any, Any]:
    """Build thermo `ChemicalConstantsPackage` and `PropertyCorrelationsPackage`."""

    thermo_mod = _require_library("thermo", "thermo")
    constants_cls = getattr(thermo_mod, "ChemicalConstantsPackage")
    corrs_cls = getattr(thermo_mod, "PropertyCorrelationsPackage")
    if hasattr(constants_cls, "from_IDs"):
        constants = constants_cls.from_IDs(identifiers)
    else:
        constants = constants_cls.constants_from_IDs(identifiers)
    if hasattr(corrs_cls, "from_IDs"):
        correlations = corrs_cls.from_IDs(identifiers)
    else:
        correlations = corrs_cls(constants=constants)
    return constants, correlations


def _kijs_matrix(n: int, kijs: list[list[float]] | None) -> list[list[float]]:
    if kijs is None:
        return [[0.0] * n for _ in range(n)]
    if len(kijs) != n or any(len(row) != n for row in kijs):
        raise ValueError(f"kijs must be {n}x{n}")
    for i in range(n):
        for j in range(n):
            if abs(kijs[i][j] - kijs[j][i]) > 1e-9:
                raise ValueError("kijs must be symmetric")
        if abs(kijs[i][i]) > 1e-9:
            raise ValueError("diagonal of kijs must be zero")
    return kijs


def flash_TP(
    *,
    identifiers: list[str],
    T: float,
    P: float,
    zs: list[float],
    eos_name: str = "PR",
    kijs: list[list[float]] | None = None,
) -> dict[str, Any]:
    """Perform a T,P flash and return summary fields.

    Parameters mirror thermo's FlashVL: temperature in K, pressure in Pa,
    composition as overall mole fractions. The function constructs the
    constants + correlations packages on the fly so it is suitable for ad-hoc
    calls; cache the packages externally for repeated calls.
    """

    if len(identifiers) != len(zs):
        raise ValueError("identifiers and zs must have the same length")
    zs = normalize_zs(zs)
    thermo_mod = _require_library("thermo", "thermo")
    constants, correlations = build_constants_and_correlations(identifiers)
    EOSClass = _get_eos_class(eos_name)
    n = len(zs)
    kij = _kijs_matrix(n, kijs)
    eos_kwargs = dict(Tcs=constants.Tcs, Pcs=constants.Pcs, omegas=constants.omegas, kijs=kij)
    GasCls = getattr(thermo_mod, "CEOSGas")
    LiqCls = getattr(thermo_mod, "CEOSLiquid")
    gas = GasCls(EOSClass, eos_kwargs=eos_kwargs, HeatCapacityGases=correlations.HeatCapacityGases, T=T, P=P, zs=zs)
    liquid = LiqCls(EOSClass, eos_kwargs=eos_kwargs, HeatCapacityGases=correlations.HeatCapacityGases, T=T, P=P, zs=zs)
    FlashCls = getattr(thermo_mod, "FlashVL")
    flasher = FlashCls(constants, correlations, gas=gas, liquid=liquid)
    state = flasher.flash(T=T, P=P, zs=zs)
    V = float(getattr(state, "VF", 0.0) or 0.0)
    phase = "two-phase"
    if V <= 1e-9:
        phase = "liquid"
    elif V >= 1 - 1e-9:
        phase = "vapor"
    summary: dict[str, Any] = {
        "method": f"thermo.FlashVL+{SUPPORTED_EOS[eos_name]}",
        "identifiers": list(identifiers),
        "T_K": T,
        "P_Pa": P,
        "zs": zs,
        "vapor_fraction": V,
        "phase_classification": phase,
    }
    if 0 < V < 1:
        try:
            summary["xs"] = list(state.liquid0.zs)
            summary["ys"] = list(state.gas.zs)
            summary["Ks"] = [yi / xi if xi > 0 else None for xi, yi in zip(summary["xs"], summary["ys"])]
        except Exception:
            pass
    for label, attr in (
        ("rho_liquid_kg_m3", "rho_l"),
        ("rho_vapor_kg_m3", "rho_g"),
        ("H_J_mol", "H"),
        ("S_J_mol_K", "S"),
    ):
        try:
            value = getattr(state, attr)
            if callable(value):
                value = value()
            summary[label] = float(value)
        except Exception:
            pass
    return summary


def bubble_point_P(
    *,
    identifiers: list[str],
    T: float,
    zs: list[float],
    eos_name: str = "PR",
    kijs: list[list[float]] | None = None,
) -> dict[str, Any]:
    """Solve for bubble point pressure at given T using thermo."""

    zs = normalize_zs(zs)
    thermo_mod = _require_library("thermo", "thermo")
    constants, correlations = build_constants_and_correlations(identifiers)
    EOSClass = _get_eos_class(eos_name)
    n = len(zs)
    eos_kwargs = dict(Tcs=constants.Tcs, Pcs=constants.Pcs, omegas=constants.omegas, kijs=_kijs_matrix(n, kijs))
    GasCls = getattr(thermo_mod, "CEOSGas")
    LiqCls = getattr(thermo_mod, "CEOSLiquid")
    P_guess = max(constants.Pcs) * 0.1
    gas = GasCls(EOSClass, eos_kwargs=eos_kwargs, HeatCapacityGases=correlations.HeatCapacityGases, T=T, P=P_guess, zs=zs)
    liquid = LiqCls(EOSClass, eos_kwargs=eos_kwargs, HeatCapacityGases=correlations.HeatCapacityGases, T=T, P=P_guess, zs=zs)
    flasher = getattr(thermo_mod, "FlashVL")(constants, correlations, gas=gas, liquid=liquid)
    state = flasher.flash(T=T, VF=0.0, zs=zs)
    return {
        "method": f"thermo.FlashVL(bubble)+{SUPPORTED_EOS[eos_name]}",
        "T_K": T,
        "bubble_pressure_Pa": float(state.P),
        "ys_at_bubble": list(state.gas.zs),
        "zs": zs,
    }


def dew_point_P(
    *,
    identifiers: list[str],
    T: float,
    zs: list[float],
    eos_name: str = "PR",
    kijs: list[list[float]] | None = None,
) -> dict[str, Any]:
    """Solve for dew point pressure at given T using thermo."""

    zs = normalize_zs(zs)
    thermo_mod = _require_library("thermo", "thermo")
    constants, correlations = build_constants_and_correlations(identifiers)
    EOSClass = _get_eos_class(eos_name)
    n = len(zs)
    eos_kwargs = dict(Tcs=constants.Tcs, Pcs=constants.Pcs, omegas=constants.omegas, kijs=_kijs_matrix(n, kijs))
    GasCls = getattr(thermo_mod, "CEOSGas")
    LiqCls = getattr(thermo_mod, "CEOSLiquid")
    P_guess = max(constants.Pcs) * 0.05
    gas = GasCls(EOSClass, eos_kwargs=eos_kwargs, HeatCapacityGases=correlations.HeatCapacityGases, T=T, P=P_guess, zs=zs)
    liquid = LiqCls(EOSClass, eos_kwargs=eos_kwargs, HeatCapacityGases=correlations.HeatCapacityGases, T=T, P=P_guess, zs=zs)
    flasher = getattr(thermo_mod, "FlashVL")(constants, correlations, gas=gas, liquid=liquid)
    state = flasher.flash(T=T, VF=1.0, zs=zs)
    return {
        "method": f"thermo.FlashVL(dew)+{SUPPORTED_EOS[eos_name]}",
        "T_K": T,
        "dew_pressure_Pa": float(state.P),
        "xs_at_dew": list(state.liquid0.zs),
        "zs": zs,
    }


def rachford_rice(Ks: list[float], zs: list[float]) -> dict[str, Any]:
    """Solve the Rachford-Rice equation for vapor fraction V.

    Pure-Python bisection; sufficient for screening calculations and works
    without thermo. For production flash, call `flash_TP`.
    """

    if len(Ks) != len(zs):
        raise ValueError("Ks and zs must have the same length")
    zs = normalize_zs(zs)
    if any(K <= 0 for K in Ks):
        raise ValueError("all K-values must be positive")

    def f(V: float) -> float:
        return sum(z * (K - 1) / (1 + V * (K - 1)) for z, K in zip(zs, Ks))

    f0 = f(0.0)
    f1 = f(1.0)
    if f0 <= 0:
        return {"vapor_fraction": 0.0, "regime": "subcooled-liquid", "Ks": Ks, "zs": zs}
    if f1 >= 0:
        return {"vapor_fraction": 1.0, "regime": "superheated-vapor", "Ks": Ks, "zs": zs}

    a, b = 0.0, 1.0
    fa = f0
    for _ in range(200):
        m = 0.5 * (a + b)
        fm = f(m)
        if abs(fm) < 1e-12 or (b - a) < 1e-12:
            break
        if fa * fm > 0:
            a, fa = m, fm
        else:
            b = m
    V = 0.5 * (a + b)
    xs = [z / (1 + V * (K - 1)) for z, K in zip(zs, Ks)]
    ys = [K * x for K, x in zip(Ks, xs)]
    xsum = sum(xs)
    ysum = sum(ys)
    if xsum <= 0 or ysum <= 0:
        raise RuntimeError("Rachford-Rice generated invalid phase composition")
    xs = [x / xsum for x in xs]
    ys = [y / ysum for y in ys]
    return {
        "method": "rachford_rice-bisection",
        "regime": "two-phase",
        "vapor_fraction": V,
        "xs": xs,
        "ys": ys,
        "Ks": Ks,
        "zs": zs,
    }

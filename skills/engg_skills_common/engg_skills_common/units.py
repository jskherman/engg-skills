"""Small unit-conversion registry for common process calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class UnitDefinition:
    dimension: str
    to_si: Callable[[float], float]
    from_si: Callable[[float], float]
    si_unit: str


def _linear(dimension: str, factor_to_si: float, si_unit: str) -> UnitDefinition:
    return UnitDefinition(
        dimension=dimension,
        to_si=lambda value: value * factor_to_si,
        from_si=lambda value: value / factor_to_si,
        si_unit=si_unit,
    )


UNITS: dict[str, UnitDefinition] = {
    # Length
    "m": _linear("length", 1.0, "m"),
    "meter": _linear("length", 1.0, "m"),
    "cm": _linear("length", 0.01, "m"),
    "mm": _linear("length", 0.001, "m"),
    "km": _linear("length", 1000.0, "m"),
    "in": _linear("length", 0.0254, "m"),
    "ft": _linear("length", 0.3048, "m"),
    # Area and volume
    "m2": _linear("area", 1.0, "m2"),
    "cm2": _linear("area", 1.0e-4, "m2"),
    "ft2": _linear("area", 0.09290304, "m2"),
    "m3": _linear("volume", 1.0, "m3"),
    "l": _linear("volume", 0.001, "m3"),
    "L": _linear("volume", 0.001, "m3"),
    "ml": _linear("volume", 1.0e-6, "m3"),
    "gal_us": _linear("volume", 0.003785411784, "m3"),
    "ft3": _linear("volume", 0.028316846592, "m3"),
    # Mass and time
    "kg": _linear("mass", 1.0, "kg"),
    "g": _linear("mass", 0.001, "kg"),
    "lbm": _linear("mass", 0.45359237, "kg"),
    "s": _linear("time", 1.0, "s"),
    "min": _linear("time", 60.0, "s"),
    "h": _linear("time", 3600.0, "s"),
    "day": _linear("time", 86400.0, "s"),
    # Pressure
    "pa": _linear("pressure", 1.0, "Pa"),
    "Pa": _linear("pressure", 1.0, "Pa"),
    "kpa": _linear("pressure", 1000.0, "Pa"),
    "KPa": _linear("pressure", 1000.0, "Pa"),
    "bar": _linear("pressure", 100000.0, "Pa"),
    "atm": _linear("pressure", 101325.0, "Pa"),
    "psi": _linear("pressure", 6894.757293168, "Pa"),
    # Energy and power
    "j": _linear("energy", 1.0, "J"),
    "J": _linear("energy", 1.0, "J"),
    "kj": _linear("energy", 1000.0, "J"),
    "KJ": _linear("energy", 1000.0, "J"),
    "btu": _linear("energy", 1055.05585262, "J"),
    "w": _linear("power", 1.0, "W"),
    "W": _linear("power", 1.0, "W"),
    "kw": _linear("power", 1000.0, "W"),
    "KW": _linear("power", 1000.0, "W"),
    "hp": _linear("power", 745.6998715822702, "W"),
    # Flow and properties
    "m3/s": _linear("volumetric_flow", 1.0, "m3/s"),
    "m3/h": _linear("volumetric_flow", 1.0 / 3600.0, "m3/s"),
    "l/min": _linear("volumetric_flow", 0.001 / 60.0, "m3/s"),
    "gpm_us": _linear("volumetric_flow", 0.003785411784 / 60.0, "m3/s"),
    "kg/s": _linear("mass_flow", 1.0, "kg/s"),
    "kg/h": _linear("mass_flow", 1.0 / 3600.0, "kg/s"),
    "lbm/h": _linear("mass_flow", 0.45359237 / 3600.0, "kg/s"),
    "kg/m3": _linear("density", 1.0, "kg/m3"),
    "g/cm3": _linear("density", 1000.0, "kg/m3"),
    "pa*s": _linear("dynamic_viscosity", 1.0, "Pa*s"),
    "Pa*s": _linear("dynamic_viscosity", 1.0, "Pa*s"),
    "cp": _linear("dynamic_viscosity", 0.001, "Pa*s"),
    "cP": _linear("dynamic_viscosity", 0.001, "Pa*s"),
    "j/kg/k": _linear("specific_heat", 1.0, "J/kg/K"),
    "kj/kg/k": _linear("specific_heat", 1000.0, "J/kg/K"),
    "w/m/k": _linear("thermal_conductivity", 1.0, "W/m/K"),
    # Absolute temperature
    "K": UnitDefinition("temperature", lambda v: v, lambda v: v, "K"),
    "C": UnitDefinition("temperature", lambda v: v + 273.15, lambda v: v - 273.15, "K"),
    "degC": UnitDefinition("temperature", lambda v: v + 273.15, lambda v: v - 273.15, "K"),
    "F": UnitDefinition(
        "temperature",
        lambda v: (v - 32.0) * 5.0 / 9.0 + 273.15,
        lambda v: (v - 273.15) * 9.0 / 5.0 + 32.0,
        "K",
    ),
    "R": UnitDefinition("temperature", lambda v: v * 5.0 / 9.0, lambda v: v * 9.0 / 5.0, "K"),
}


def convert(value: float, from_unit: str, to_unit: str) -> dict[str, float | str]:
    """Convert between registered units."""

    if from_unit not in UNITS:
        raise ValueError(f"unsupported from_unit {from_unit!r}")
    if to_unit not in UNITS:
        raise ValueError(f"unsupported to_unit {to_unit!r}")
    source = UNITS[from_unit]
    target = UNITS[to_unit]
    if source.dimension != target.dimension:
        raise ValueError(
            f"incompatible dimensions: {from_unit!r} is {source.dimension}, "
            f"{to_unit!r} is {target.dimension}"
        )
    si_value = source.to_si(value)
    converted = target.from_si(si_value)
    return {
        "input_value": value,
        "from_unit": from_unit,
        "si_value": si_value,
        "si_unit": source.si_unit,
        "converted_value": converted,
        "to_unit": to_unit,
        "dimension": source.dimension,
    }


def available_units() -> dict[str, list[str]]:
    """Return units grouped by dimension."""

    grouped: dict[str, list[str]] = {}
    for unit, definition in sorted(UNITS.items()):
        grouped.setdefault(definition.dimension, []).append(unit)
    return grouped

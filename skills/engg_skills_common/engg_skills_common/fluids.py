"""Fluid-flow helpers for process calculations."""

from __future__ import annotations

import math
from typing import Any

from .dimensionless import reynolds_number


def pipe_area(diameter: float) -> float:
    if diameter <= 0:
        raise ValueError("diameter must be positive")
    return math.pi * diameter**2 / 4.0


def darcy_friction_factor(reynolds: float, relative_roughness: float = 0.0) -> tuple[float, str, list[str]]:
    """Estimate Darcy friction factor with laminar and Haaland turbulent logic."""

    if reynolds <= 0:
        raise ValueError("reynolds must be positive")
    if relative_roughness < 0:
        raise ValueError("relative_roughness cannot be negative")
    warnings: list[str] = []
    if reynolds < 2300:
        return 64.0 / reynolds, "laminar-64/Re", warnings

    turbulent = (-1.8 * math.log10((relative_roughness / 3.7) ** 1.11 + 6.9 / reynolds)) ** -2
    if reynolds < 4000:
        laminar_at_2300 = 64.0 / 2300.0
        turbulent_at_4000 = (-1.8 * math.log10((relative_roughness / 3.7) ** 1.11 + 6.9 / 4000.0)) ** -2
        fraction = (reynolds - 2300.0) / 1700.0
        blended = laminar_at_2300 + fraction * (turbulent_at_4000 - laminar_at_2300)
        warnings.append("Reynolds number is transitional; pressure drop is uncertain.")
        return blended, "transition-blend", warnings
    return turbulent, "haaland", warnings


def pipe_pressure_drop(
    *,
    length: float,
    diameter: float,
    density: float,
    viscosity: float,
    flow_m3_s: float | None = None,
    velocity: float | None = None,
    roughness: float = 0.0,
    minor_k: float = 0.0,
    elevation_m: float = 0.0,
    gravity: float = 9.80665,
) -> dict[str, Any]:
    """Return Darcy-Weisbach pressure-drop terms for steady incompressible flow."""

    if length < 0:
        raise ValueError("length cannot be negative")
    if density <= 0 or viscosity <= 0:
        raise ValueError("density and viscosity must be positive")
    if roughness < 0 or minor_k < 0:
        raise ValueError("roughness and minor_k cannot be negative")
    if velocity is None:
        if flow_m3_s is None:
            raise ValueError("provide either flow_m3_s or velocity")
        if flow_m3_s <= 0:
            raise ValueError("flow_m3_s must be positive")
        area = pipe_area(diameter)
        velocity = flow_m3_s / area
    else:
        if velocity <= 0:
            raise ValueError("velocity must be positive")
        area = pipe_area(diameter)
        if flow_m3_s is None:
            flow_m3_s = velocity * area

    re = reynolds_number(density=density, velocity=velocity, length=diameter, viscosity=viscosity)
    rel_roughness = roughness / diameter
    f, method, warnings = darcy_friction_factor(re, rel_roughness)
    dynamic_pressure = 0.5 * density * velocity**2
    dp_major = f * length / diameter * dynamic_pressure
    dp_minor = minor_k * dynamic_pressure
    dp_static = density * gravity * elevation_m
    return {
        "area_m2": area,
        "velocity_m_s": velocity,
        "flow_m3_s": flow_m3_s,
        "reynolds": re,
        "relative_roughness": rel_roughness,
        "darcy_friction_factor": f,
        "friction_factor_method": method,
        "dynamic_pressure_pa": dynamic_pressure,
        "major_pressure_drop_pa": dp_major,
        "minor_pressure_drop_pa": dp_minor,
        "static_pressure_change_pa": dp_static,
        "total_pressure_drop_pa": dp_major + dp_minor + dp_static,
        "warnings": warnings,
    }

"""Dimensionless-number definitions and simple correlations."""

from __future__ import annotations

import math


def _positive(name: str, value: float) -> float:
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def reynolds_number(*, density: float, velocity: float, length: float, viscosity: float) -> float:
    """Return Reynolds number rho v L / mu."""

    return _positive("density", density) * _positive("velocity", velocity) * _positive("length", length) / _positive("viscosity", viscosity)


def prandtl_number(*, cp: float, viscosity: float, thermal_conductivity: float) -> float:
    """Return Prandtl number cp mu / k."""

    return _positive("cp", cp) * _positive("viscosity", viscosity) / _positive("thermal_conductivity", thermal_conductivity)


def schmidt_number(*, viscosity: float, density: float, diffusivity: float) -> float:
    """Return Schmidt number mu / (rho D)."""

    return _positive("viscosity", viscosity) / (_positive("density", density) * _positive("diffusivity", diffusivity))


def peclet_number(*, reynolds: float, prandtl: float) -> float:
    """Return thermal Peclet number Re Pr."""

    return _positive("reynolds", reynolds) * _positive("prandtl", prandtl)


def froude_number(*, velocity: float, length: float, gravity: float = 9.80665) -> float:
    """Return Froude number v / sqrt(g L)."""

    return _positive("velocity", velocity) / math.sqrt(_positive("gravity", gravity) * _positive("length", length))


def weber_number(*, density: float, velocity: float, length: float, surface_tension: float) -> float:
    """Return Weber number rho v^2 L / sigma."""

    return (
        _positive("density", density)
        * _positive("velocity", velocity) ** 2
        * _positive("length", length)
        / _positive("surface_tension", surface_tension)
    )


def biot_number(*, heat_transfer_coefficient: float, characteristic_length: float, solid_conductivity: float) -> float:
    """Return Biot number h Lc / ks."""

    return _positive("heat_transfer_coefficient", heat_transfer_coefficient) * _positive("characteristic_length", characteristic_length) / _positive("solid_conductivity", solid_conductivity)


def fourier_number(*, thermal_diffusivity: float, time: float, characteristic_length: float) -> float:
    """Return Fourier number alpha t / L^2."""

    return _positive("thermal_diffusivity", thermal_diffusivity) * _positive("time", time) / _positive("characteristic_length", characteristic_length) ** 2


def nusselt_dittus_boelter(*, reynolds: float, prandtl: float, heating: bool = True) -> tuple[float, list[str]]:
    """Return Dittus-Boelter turbulent internal-flow Nusselt estimate."""

    re = _positive("reynolds", reynolds)
    pr = _positive("prandtl", prandtl)
    exponent = 0.4 if heating else 0.3
    warnings: list[str] = []
    if re < 10000:
        warnings.append("Dittus-Boelter is normally used for turbulent Re >= 10000.")
    if pr < 0.6 or pr > 160:
        warnings.append("Dittus-Boelter is commonly cited for roughly 0.6 <= Pr <= 160.")
    return 0.023 * re**0.8 * pr**exponent, warnings

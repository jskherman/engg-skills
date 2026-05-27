"""Convective heat transfer coefficient correlations.

Pure-Python implementations of classic single-phase correlations plus thin
wrappers around `ht` for boiling/condensation. All return dimensionless
Nusselt and convective heat transfer coefficient h = Nu * k / Dh.

Conventions:
- Re, Pr, Nu are dimensionless.
- k is fluid thermal conductivity (W/m/K).
- Dh is hydraulic diameter (m).
"""

from __future__ import annotations

import math
from typing import Any

from .property_backends import _require_library


def _h_from_nu(Nu: float, k: float, Dh: float) -> float:
    return Nu * k / Dh


def dittus_boelter(*, Re: float, Pr: float, k: float, Dh: float, heating: bool = True) -> dict[str, Any]:
    """Dittus-Boelter for turbulent fully-developed pipe flow."""

    n = 0.4 if heating else 0.3
    Nu = 0.023 * Re ** 0.8 * Pr ** n
    warnings: list[str] = []
    if Re < 10_000:
        warnings.append("Dittus-Boelter is usually applied for Re >= 10000.")
    if Pr < 0.6 or Pr > 160:
        warnings.append("Dittus-Boelter usually cited for 0.6 <= Pr <= 160.")
    return {
        "method": "Dittus-Boelter",
        "Re": Re,
        "Pr": Pr,
        "Nu": Nu,
        "h_W_m2_K": _h_from_nu(Nu, k, Dh),
        "heating": heating,
        "warnings": warnings,
    }


def gnielinski(*, Re: float, Pr: float, k: float, Dh: float, f: float | None = None) -> dict[str, Any]:
    """Gnielinski correlation (transitional/turbulent, 3000 < Re < 5e6)."""

    warnings: list[str] = []
    if f is None:
        f = (0.790 * math.log(Re) - 1.64) ** -2  # Petukhov-Konakov smooth tube
    if Re < 3000 or Re > 5e6:
        warnings.append("Gnielinski is valid for 3000 <= Re <= 5e6.")
    if Pr < 0.5 or Pr > 2000:
        warnings.append("Gnielinski applies for 0.5 <= Pr <= 2000.")
    num = (f / 8) * (Re - 1000) * Pr
    den = 1 + 12.7 * math.sqrt(f / 8) * (Pr ** (2 / 3) - 1)
    Nu = num / den
    return {
        "method": "Gnielinski",
        "Re": Re,
        "Pr": Pr,
        "f_Darcy": f,
        "Nu": Nu,
        "h_W_m2_K": _h_from_nu(Nu, k, Dh),
        "warnings": warnings,
    }


def sieder_tate(
    *,
    Re: float,
    Pr: float,
    k: float,
    Dh: float,
    mu_bulk: float,
    mu_wall: float,
    heating: bool = True,
) -> dict[str, Any]:
    """Sieder-Tate for turbulent pipe flow with strong viscosity variation."""

    Nu = 0.027 * Re ** 0.8 * Pr ** (1 / 3) * (mu_bulk / mu_wall) ** 0.14
    warnings: list[str] = []
    if Re < 10_000:
        warnings.append("Sieder-Tate intended for Re >= 10000.")
    return {
        "method": "Sieder-Tate",
        "Re": Re,
        "Pr": Pr,
        "mu_bulk_over_wall": mu_bulk / mu_wall,
        "Nu": Nu,
        "h_W_m2_K": _h_from_nu(Nu, k, Dh),
        "heating": heating,
        "warnings": warnings,
    }


def laminar_pipe_constant_T(*, k: float, Dh: float) -> dict[str, Any]:
    """Laminar pipe flow, constant wall temperature: Nu = 3.66."""

    return {
        "method": "laminar-constant-Tw",
        "Nu": 3.66,
        "h_W_m2_K": _h_from_nu(3.66, k, Dh),
    }


def laminar_pipe_constant_q(*, k: float, Dh: float) -> dict[str, Any]:
    """Laminar pipe flow, constant wall heat flux: Nu = 4.36."""

    return {
        "method": "laminar-constant-q",
        "Nu": 4.36,
        "h_W_m2_K": _h_from_nu(4.36, k, Dh),
    }


def churchill_chu_natural_convection(*, Ra: float, Pr: float, k: float, L: float) -> dict[str, Any]:
    """Churchill-Chu correlation for a vertical plate (laminar+turbulent unified)."""

    term = (1 + (0.492 / Pr) ** (9 / 16)) ** (8 / 27)
    Nu = (0.825 + 0.387 * Ra ** (1 / 6) / term) ** 2
    return {
        "method": "Churchill-Chu-vertical-plate",
        "Ra": Ra,
        "Pr": Pr,
        "Nu": Nu,
        "h_W_m2_K": _h_from_nu(Nu, k, L),
    }


def ht_boiling(*, T_sat_K: float, T_wall_K: float, P_Pa: float, k_l: float, rho_l: float, rho_g: float, sigma: float, cpl: float, dHvap: float, mu_l: float) -> dict[str, Any]:
    """Pool boiling via ht.boiling_nucleic.Rohsenow as a screening estimate."""

    boiling = _require_library("ht.boiling_nucleic", "ht")
    h = boiling.Rohsenow(rhol=rho_l, rhog=rho_g, mul=mu_l, kl=k_l, Cpl=cpl, Hvap=dHvap, sigma=sigma, Te=T_wall_K - T_sat_K)
    return {
        "method": "ht.boiling_nucleic.Rohsenow",
        "h_W_m2_K": h,
        "T_sat_K": T_sat_K,
        "T_wall_K": T_wall_K,
        "delta_T_K": T_wall_K - T_sat_K,
    }

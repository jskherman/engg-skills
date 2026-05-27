#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Dimensionless-number calculation CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.dimensionless import (
    biot_number,
    fourier_number,
    froude_number,
    nusselt_dittus_boelter,
    peclet_number,
    prandtl_number,
    reynolds_number,
    schmidt_number,
    weber_number,
)
from engg_skills_common.io import result_envelope, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate common engineering dimensionless numbers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    re_parser = subparsers.add_parser("reynolds")
    re_parser.add_argument("--density", type=float, required=True, help="Density, kg/m3.")
    re_parser.add_argument("--velocity", type=float, required=True, help="Velocity, m/s.")
    re_parser.add_argument("--length", type=float, required=True, help="Characteristic length, m.")
    re_parser.add_argument("--viscosity", type=float, required=True, help="Dynamic viscosity, Pa*s.")
    re_parser.add_argument("--output", required=True)

    pr_parser = subparsers.add_parser("prandtl")
    pr_parser.add_argument("--cp", type=float, required=True, help="Heat capacity, J/kg/K.")
    pr_parser.add_argument("--viscosity", type=float, required=True, help="Dynamic viscosity, Pa*s.")
    pr_parser.add_argument("--thermal-conductivity", type=float, required=True, help="Thermal conductivity, W/m/K.")
    pr_parser.add_argument("--output", required=True)

    sc_parser = subparsers.add_parser("schmidt")
    sc_parser.add_argument("--viscosity", type=float, required=True)
    sc_parser.add_argument("--density", type=float, required=True)
    sc_parser.add_argument("--diffusivity", type=float, required=True, help="Mass diffusivity, m2/s.")
    sc_parser.add_argument("--output", required=True)

    nu_parser = subparsers.add_parser("nusselt-dittus-boelter")
    nu_parser.add_argument("--reynolds", type=float, required=True)
    nu_parser.add_argument("--prandtl", type=float, required=True)
    nu_parser.add_argument("--mode", choices=["heating", "cooling"], default="heating")
    nu_parser.add_argument("--output", required=True)

    fr_parser = subparsers.add_parser("froude")
    fr_parser.add_argument("--velocity", type=float, required=True)
    fr_parser.add_argument("--length", type=float, required=True)
    fr_parser.add_argument("--gravity", type=float, default=9.80665)
    fr_parser.add_argument("--output", required=True)

    we_parser = subparsers.add_parser("weber")
    we_parser.add_argument("--density", type=float, required=True)
    we_parser.add_argument("--velocity", type=float, required=True)
    we_parser.add_argument("--length", type=float, required=True)
    we_parser.add_argument("--surface-tension", type=float, required=True, help="Surface tension, N/m.")
    we_parser.add_argument("--output", required=True)

    bi_parser = subparsers.add_parser("biot")
    bi_parser.add_argument("--h", type=float, required=True, help="Heat-transfer coefficient, W/m2/K.")
    bi_parser.add_argument("--length", type=float, required=True, help="Characteristic length, m.")
    bi_parser.add_argument("--solid-conductivity", type=float, required=True, help="Solid conductivity, W/m/K.")
    bi_parser.add_argument("--output", required=True)

    fo_parser = subparsers.add_parser("fourier")
    fo_parser.add_argument("--thermal-diffusivity", type=float, required=True, help="m2/s.")
    fo_parser.add_argument("--time", type=float, required=True, help="s.")
    fo_parser.add_argument("--length", type=float, required=True, help="m.")
    fo_parser.add_argument("--output", required=True)

    pe_parser = subparsers.add_parser("peclet")
    pe_parser.add_argument("--reynolds", type=float, required=True)
    pe_parser.add_argument("--prandtl", type=float, required=True)
    pe_parser.add_argument("--output", required=True)

    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    warnings: list[str] = []
    if args.command == "reynolds":
        results = {"reynolds": reynolds_number(density=args.density, velocity=args.velocity, length=args.length, viscosity=args.viscosity)}
    elif args.command == "prandtl":
        results = {"prandtl": prandtl_number(cp=args.cp, viscosity=args.viscosity, thermal_conductivity=args.thermal_conductivity)}
    elif args.command == "schmidt":
        results = {"schmidt": schmidt_number(viscosity=args.viscosity, density=args.density, diffusivity=args.diffusivity)}
    elif args.command == "nusselt-dittus-boelter":
        value, warnings = nusselt_dittus_boelter(reynolds=args.reynolds, prandtl=args.prandtl, heating=args.mode == "heating")
        results = {"nusselt": value, "correlation": "Dittus-Boelter"}
    elif args.command == "froude":
        results = {"froude": froude_number(velocity=args.velocity, length=args.length, gravity=args.gravity)}
    elif args.command == "weber":
        results = {"weber": weber_number(density=args.density, velocity=args.velocity, length=args.length, surface_tension=args.surface_tension)}
    elif args.command == "biot":
        results = {"biot": biot_number(heat_transfer_coefficient=args.h, characteristic_length=args.length, solid_conductivity=args.solid_conductivity)}
    elif args.command == "fourier":
        results = {"fourier": fourier_number(thermal_diffusivity=args.thermal_diffusivity, time=args.time, characteristic_length=args.length)}
    elif args.command == "peclet":
        results = {"peclet": peclet_number(reynolds=args.reynolds, prandtl=args.prandtl)}
    else:
        raise ValueError(f"unknown command {args.command!r}")
    return result_envelope(
        skill="dimensionless_numbers",
        inputs=vars(args),
        results=results,
        assumptions=["Inputs are SI quantities unless a command explicitly states otherwise."],
        warnings=warnings,
    )


def main() -> int:
    args = build_parser().parse_args()
    try:
        path = write_json(run(args), args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        write_json(
            result_envelope(skill="dimensionless_numbers", inputs=vars(args), results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

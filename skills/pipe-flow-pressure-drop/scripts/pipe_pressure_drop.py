#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["fluids>=1.3"]
# ///
"""Darcy-Weisbach pipe pressure-drop CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.fluids import pipe_pressure_drop
from engg_skills_common.io import result_envelope, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Estimate steady incompressible pipe pressure drop.")
    parser.add_argument("--length-m", type=float, required=True)
    parser.add_argument("--diameter-m", type=float, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--flow-m3-s", type=float)
    group.add_argument("--velocity-m-s", type=float)
    parser.add_argument("--density-kg-m3", type=float, required=True)
    parser.add_argument("--viscosity-pa-s", type=float, required=True)
    parser.add_argument("--roughness-m", type=float, default=0.0)
    parser.add_argument("--minor-k", type=float, default=0.0, help="Sum of minor-loss K values.")
    parser.add_argument("--elevation-m", type=float, default=0.0, help="Outlet elevation minus inlet elevation.")
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        raw_results = pipe_pressure_drop(
            length=args.length_m,
            diameter=args.diameter_m,
            flow_m3_s=args.flow_m3_s,
            velocity=args.velocity_m_s,
            density=args.density_kg_m3,
            viscosity=args.viscosity_pa_s,
            roughness=args.roughness_m,
            minor_k=args.minor_k,
            elevation_m=args.elevation_m,
        )
        warnings = raw_results.pop("warnings")
        data = result_envelope(
            skill="pipe-flow-pressure-drop",
            inputs=vars(args),
            results=raw_results,
            assumptions=[
                "Single-phase Newtonian fluid.",
                "Steady incompressible flow in a round pipe.",
                "Darcy friction factor is reported, not Fanning friction factor.",
                "Elevation term is positive for flow to a higher outlet elevation.",
            ],
            warnings=warnings,
        )
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        write_json(result_envelope(skill="pipe-flow-pressure-drop", inputs=vars(args), results={"error": str(exc)}, ok=False), args.output)
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

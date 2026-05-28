#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["ht>=1.2"]
# ///
"""LMTD heat-exchanger sizing CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.heat_transfer import lmtd_sizing
from engg_skills_common.io import result_envelope, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Estimate exchanger LMTD, duty, and area.")
    parser.add_argument("--hot-in-c", type=float, required=True)
    parser.add_argument("--hot-out-c", type=float, required=True)
    parser.add_argument("--cold-in-c", type=float, required=True)
    parser.add_argument("--cold-out-c", type=float, required=True)
    parser.add_argument("--arrangement", choices=["counterflow", "parallel"], default="counterflow")
    parser.add_argument("--u-w-m2-k", type=float, required=True, help="Overall heat-transfer coefficient.")
    parser.add_argument("--f-correction", type=float, default=1.0, help="LMTD correction factor.")
    parser.add_argument("--duty-w", type=float)
    parser.add_argument("--hot-mdot-kg-s", type=float)
    parser.add_argument("--hot-cp-j-kg-k", type=float)
    parser.add_argument("--cold-mdot-kg-s", type=float)
    parser.add_argument("--cold-cp-j-kg-k", type=float)
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        raw_results = lmtd_sizing(
            hot_in=args.hot_in_c,
            hot_out=args.hot_out_c,
            cold_in=args.cold_in_c,
            cold_out=args.cold_out_c,
            arrangement=args.arrangement,
            overall_u_w_m2_k=args.u_w_m2_k,
            correction_factor=args.f_correction,
            duty_w=args.duty_w,
            hot_mass_flow_kg_s=args.hot_mdot_kg_s,
            hot_cp_j_kg_k=args.hot_cp_j_kg_k,
            cold_mass_flow_kg_s=args.cold_mdot_kg_s,
            cold_cp_j_kg_k=args.cold_cp_j_kg_k,
        )
        warnings = raw_results.pop("warnings")
        data = result_envelope(
            skill="heat-exchanger-sizing",
            inputs=vars(args),
            results=raw_results,
            assumptions=[
                "No phase change unless represented by an externally supplied duty.",
                "No heat losses to surroundings.",
                "U and correction factor are user-supplied estimates.",
            ],
            warnings=warnings,
        )
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        write_json(result_envelope(skill="heat-exchanger-sizing", inputs=vars(args), results={"error": str(exc)}, ok=False), args.output)
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Isothermal reactor sizing and Arrhenius helpers."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import parse_number_list, result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.reactor import (
    arrhenius_fit,
    batch_time_nth_order,
    cstr_in_series,
    cstr_volume_nth_order,
    pfr_numeric,
    pfr_volume_nth_order,
)

SKILL = "reactor_sizing_and_kinetics"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Reactor sizing and kinetics")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("arrhenius")
    a.add_argument("--temperatures", required=True)
    a.add_argument("--k-values", required=True, dest="k_values")
    a.add_argument("--output", required=True)

    for name in ("cstr", "pfr", "batch"):
        s = sub.add_parser(name)
        s.add_argument("--C0", type=float, required=True)
        s.add_argument("--conversion", type=float, required=True)
        s.add_argument("--k", type=float, required=True)
        s.add_argument("--order", type=float, default=1.0)
        if name in ("cstr", "pfr"):
            s.add_argument("--flow", type=float, required=True, dest="flow_m3_s")
        s.add_argument("--output", required=True)

    se = sub.add_parser("series")
    se.add_argument("--C0", type=float, required=True)
    se.add_argument("--conversion", type=float, required=True)
    se.add_argument("--flow", type=float, required=True, dest="flow_m3_s")
    se.add_argument("--k", type=float, required=True)
    se.add_argument("--N", type=int, required=True)
    se.add_argument("--output", required=True)

    pf = sub.add_parser("pfr-numeric")
    pf.add_argument("--C0", type=float, required=True)
    pf.add_argument("--conversion", type=float, required=True)
    pf.add_argument("--flow", type=float, required=True, dest="flow_m3_s")
    pf.add_argument("--rate-fn", required=True, dest="rate_fn",
                    help="Python expression in C (concentration mol/m^3) returning rate mol/(m^3 s).")
    pf.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["Original implementation; classical reactor design equations, public domain."],
    )
    try:
        if args.command == "arrhenius":
            res = arrhenius_fit(parse_number_list(args.temperatures), parse_number_list(args.k_values))
        elif args.command == "cstr":
            res = cstr_volume_nth_order(C0=args.C0, conversion=args.conversion, flow_m3_s=args.flow_m3_s, k=args.k, order=args.order)
        elif args.command == "pfr":
            res = pfr_volume_nth_order(C0=args.C0, conversion=args.conversion, flow_m3_s=args.flow_m3_s, k=args.k, order=args.order)
        elif args.command == "batch":
            res = batch_time_nth_order(C0=args.C0, conversion=args.conversion, k=args.k, order=args.order)
        elif args.command == "series":
            res = cstr_in_series(C0=args.C0, overall_conversion=args.conversion, flow_m3_s=args.flow_m3_s, k=args.k, N=args.N)
        else:  # pfr-numeric
            rate_fn = lambda C, _expr=args.rate_fn: float(eval(_expr, {"__builtins__": {}, "math": math}, {"C": C}))  # noqa: S307
            res = pfr_numeric(C0=args.C0, target_conversion=args.conversion, rate_per_unit_volume=rate_fn, flow_m3_s=args.flow_m3_s)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["Fogler", "Levenspiel"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        write_json(
            result_envelope(skill=SKILL, inputs=vars(args), results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

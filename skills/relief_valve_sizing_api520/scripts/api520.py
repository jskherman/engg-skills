#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""API 520 Part I preliminary relief orifice area (gas / liquid)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import SAFETY_RELIEF_NOTICE, license_notice_for, write_license_notification
from engg_skills_common.valves import api520_gas_relief_area, api520_liquid_relief_area

SKILL = "relief_valve_sizing_api520"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="API 520 Part I preliminary relief sizing")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("gas")
    g.add_argument("--m", type=float, required=True, dest="mass_flow_kg_s")
    g.add_argument("--T-K", type=float, required=True, dest="T_K")
    g.add_argument("--MW", type=float, required=True, help="MW in g/mol")
    g.add_argument("--Z", type=float, default=1.0)
    g.add_argument("--gamma", type=float, default=1.4)
    g.add_argument("--P1", type=float, required=True, dest="P1_relieving_Pa")
    g.add_argument("--Pb", type=float, default=101325.0, dest="Pb_Pa")
    g.add_argument("--Kd", type=float, default=0.975)
    g.add_argument("--Kb", type=float, default=1.0)
    g.add_argument("--Kc", type=float, default=1.0)
    g.add_argument("--output", required=True)

    l = sub.add_parser("liquid")
    l.add_argument("--Q", type=float, required=True, dest="Q_m3_s")
    l.add_argument("--rho", type=float, required=True, dest="rho_kg_m3")
    l.add_argument("--P1", type=float, required=True, dest="P1_relieving_Pa")
    l.add_argument("--Pb", type=float, default=101325.0, dest="Pb_Pa")
    l.add_argument("--Kd", type=float, default=0.65)
    l.add_argument("--Kw", type=float, default=1.0)
    l.add_argument("--Kc", type=float, default=1.0)
    l.add_argument("--Kv", type=float, default=1.0)
    l.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["API 520/521/526 (procure from the standards body)"],
        standards_referenced=[
            "API 520 Part I — Sizing, Selection, and Installation of Pressure-Relieving Devices",
            "API 521 — Pressure-Relieving and Depressuring Systems",
            "API 526 — Flanged Steel Pressure-Relief Valves",
            "ASME BPVC Section VIII Division 1, Section XIII",
        ],
        extra_notes=SAFETY_RELIEF_NOTICE,
    )
    try:
        kwargs = {k: v for k, v in vars(args).items() if k not in ("command", "output")}
        if args.command == "gas":
            res = api520_gas_relief_area(**kwargs)
        else:
            res = api520_liquid_relief_area(**kwargs)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            assumptions=[
                "Preliminary screening only.",
                "Standards: API 520 Part I sizing equations (referenced; text not reproduced).",
                "Two-phase / flashing relief is NOT covered.",
            ],
            warnings=[SAFETY_RELIEF_NOTICE],
            sources=[
                "API 520 Part I (referenced)",
                "API 521 (load side, referenced)",
                "API 526 (orifice designations, referenced)",
            ],
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

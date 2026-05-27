#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["fluids>=1.3"]
# ///
"""ISA 75.01.01 / IEC 60534 control valve sizing via fluids.control_valve."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.valves import gas_control_valve, liquid_control_valve

SKILL = "control_valve_sizing_isa75"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ISA 75.01.01 control valve sizing")
    sub = p.add_subparsers(dest="command", required=True)

    l = sub.add_parser("liquid")
    l.add_argument("--rho", type=float, required=True, dest="rho_l_kg_m3")
    l.add_argument("--P1", type=float, required=True, dest="P1_Pa")
    l.add_argument("--P2", type=float, required=True, dest="P2_Pa")
    l.add_argument("--Q", type=float, required=True, dest="Q_m3_s")
    l.add_argument("--mu", type=float, default=1e-3, dest="mu_Pa_s")
    l.add_argument("--Psat", type=float, default=0.0, dest="Psat_Pa")
    l.add_argument("--Pc", type=float, default=2.2e7, dest="Pc_Pa")
    l.add_argument("--output", required=True)

    g = sub.add_parser("gas")
    g.add_argument("--T", type=float, required=True, dest="T_K")
    g.add_argument("--MW", type=float, required=True)
    g.add_argument("--mu", type=float, required=True, dest="mu_Pa_s")
    g.add_argument("--gamma", type=float, required=True)
    g.add_argument("--Z", type=float, required=True)
    g.add_argument("--P1", type=float, required=True, dest="P1_Pa")
    g.add_argument("--P2", type=float, required=True, dest="P2_Pa")
    g.add_argument("--Q", type=float, required=True, dest="Q_m3_s")
    g.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://fluids.readthedocs.io/"],
        library_attributions=["fluids (Caleb Bell) — MIT"],
        standards_referenced=[
            "ISA 75.01.01-2012 Industrial-process control valves — Flow capacity",
            "IEC 60534-2-1 Industrial-process control valves",
        ],
    )
    try:
        kwargs = {k: v for k, v in vars(args).items() if k not in ("command", "output")}
        if args.command == "liquid":
            res = liquid_control_valve(**kwargs)
        else:
            res = gas_control_valve(**kwargs)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["fluids.control_valve", "ISA 75.01.01 (referenced)"],
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

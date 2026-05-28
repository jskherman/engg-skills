#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Kremser absorption/stripping factor method (dilute systems)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.separations import kremser

SKILL = "absorption-stripping-design"
SKILL_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Kremser absorption / stripping calculator")
    parser.add_argument("--N", type=float, required=True)
    parser.add_argument("--A", type=float, required=True, help="Absorption factor L/(K*V)")
    parser.add_argument("--K", type=float, required=True)
    parser.add_argument("--x-in", type=float, required=True, dest="x_in")
    parser.add_argument("--y-in", type=float, required=True, dest="y_in")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["Original implementation; classical Kremser equation, public domain."],
    )
    try:
        res = kremser(N=args.N, A=args.A, x_in=args.x_in, y_in=args.y_in, K=args.K)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["Treybal Mass-Transfer Operations", "Sinnott (Coulson & Richardson Vol 6)"],
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

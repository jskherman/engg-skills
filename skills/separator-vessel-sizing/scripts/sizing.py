#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["fluids>=1.3"]
# ///
"""Souders-Brown two-phase separator sizing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.separator import (
    fluids_K_separator_watkins,
    horizontal_separator,
    vertical_separator,
)

SKILL = "separator-vessel-sizing"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Separator vessel sizing")
    sub = p.add_subparsers(dest="command", required=True)

    def common(s):
        s.add_argument("--vapor-volumetric", type=float, required=True, dest="vapor_volumetric_m3_s")
        s.add_argument("--liquid-volumetric", type=float, required=True, dest="liquid_volumetric_m3_s")
        s.add_argument("--rho-l", type=float, required=True, dest="rho_l")
        s.add_argument("--rho-g", type=float, required=True, dest="rho_v")
        s.add_argument("--K", type=float, default=None)
        s.add_argument("--demister", action="store_true")
        s.add_argument("--holdup-min", type=float, default=5.0, dest="liquid_holdup_minutes")
        s.add_argument("--output", required=True)

    v = sub.add_parser("vertical"); common(v)
    h = sub.add_parser("horizontal"); common(h)
    h.add_argument("--LD", type=float, default=4.0, dest="LD_ratio")
    h.add_argument("--liquid-level", type=float, default=0.5, dest="liquid_level_fraction")

    w = sub.add_parser("watkins-k")
    w.add_argument("--quality", type=float, required=True)
    w.add_argument("--rho-l", type=float, required=True, dest="rho_l")
    w.add_argument("--rho-g", type=float, required=True, dest="rho_v")
    w.add_argument("--horizontal", action="store_true")
    w.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://fluids.readthedocs.io/", "GPSA Engineering Data Book (procure separately)", "API 12J"],
        library_attributions=["fluids (Caleb Bell) — MIT"],
        standards_referenced=["GPSA Engineering Data Book (referenced, not reproduced)", "API 12J Oil & Gas Separators"],
    )
    try:
        kwargs = {k: v for k, v in vars(args).items() if k not in ("command", "output")}
        if args.command == "vertical":
            res = vertical_separator(**kwargs)
        elif args.command == "horizontal":
            res = horizontal_separator(**kwargs)
        else:
            res = fluids_K_separator_watkins(quality=args.quality, rho_l=args.rho_l, rho_v=args.rho_v, horizontal=args.horizontal)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["fluids.separator", "GPSA Engineering Data Book (referenced)"],
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

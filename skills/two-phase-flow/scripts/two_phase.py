#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["fluids>=1.3"]
# ///
"""Two-phase pressure-drop CLI (Lockhart-Martinelli, Beggs-Brill, MSH)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.two_phase import (
    beggs_brill,
    lockhart_martinelli,
    mueller_steinhagen_heck,
)

SKILL = "two-phase-flow"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Two-phase pressure drop")
    sub = p.add_subparsers(dest="command", required=True)

    def common(s):
        s.add_argument("--m", type=float, required=True, dest="m_total_kg_s")
        s.add_argument("--quality", type=float, required=True)
        s.add_argument("--rho-l", type=float, required=True, dest="rho_l")
        s.add_argument("--rho-g", type=float, required=True, dest="rho_g")
        s.add_argument("--mu-l", type=float, required=True, dest="mu_l")
        s.add_argument("--mu-g", type=float, required=True, dest="mu_g")
        s.add_argument("--D", type=float, required=True, dest="D_m")
        s.add_argument("--L", type=float, default=1.0, dest="L_m")
        s.add_argument("--output", required=True)

    lm = sub.add_parser("lm"); common(lm)
    bb = sub.add_parser("beggs-brill"); common(bb)
    bb.add_argument("--sigma", type=float, required=True, dest="sigma_N_m")
    bb.add_argument("--P", type=float, required=True, dest="P_Pa")
    bb.add_argument("--angle", type=float, default=0.0, dest="angle_deg")
    bb.add_argument("--roughness", type=float, default=0.0, dest="roughness_m")
    bb.add_argument("--no-acceleration", action="store_false", dest="include_acceleration")
    msh = sub.add_parser("msh"); common(msh)
    msh.add_argument("--roughness", type=float, default=0.0, dest="roughness_m")
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://fluids.readthedocs.io/"],
        library_attributions=["fluids (Caleb Bell) — MIT"],
    )
    try:
        kwargs = {k: v for k, v in vars(args).items() if k not in ("command", "output")}
        if args.command == "lm":
            kwargs.pop("sigma_N_m", None); kwargs.pop("P_Pa", None); kwargs.pop("angle_deg", None); kwargs.pop("roughness_m", None); kwargs.pop("include_acceleration", None)
            res = lockhart_martinelli(**kwargs)
        elif args.command == "beggs-brill":
            res = beggs_brill(**kwargs)
        else:
            kwargs.pop("sigma_N_m", None); kwargs.pop("P_Pa", None); kwargs.pop("angle_deg", None); kwargs.pop("include_acceleration", None)
            res = mueller_steinhagen_heck(**kwargs)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["fluids.two_phase"],
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

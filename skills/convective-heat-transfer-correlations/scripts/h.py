#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["ht>=1.2"]
# ///
"""Convective heat transfer coefficient calculator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.convection import (
    churchill_chu_natural_convection,
    dittus_boelter,
    gnielinski,
    ht_boiling,
    laminar_pipe_constant_T,
    laminar_pipe_constant_q,
    sieder_tate,
)
from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "convective-heat-transfer-correlations"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Convective heat transfer correlations")
    sub = p.add_subparsers(dest="command", required=True)

    def re_pr(s):
        s.add_argument("--Re", type=float, required=True)
        s.add_argument("--Pr", type=float, required=True)
        s.add_argument("--k", type=float, required=True)
        s.add_argument("--Dh", type=float, required=True)

    db = sub.add_parser("dittus-boelter"); re_pr(db)
    db.add_argument("--heating", action="store_true")
    db.add_argument("--output", required=True)

    gn = sub.add_parser("gnielinski"); re_pr(gn)
    gn.add_argument("--f", type=float, default=None)
    gn.add_argument("--output", required=True)

    st = sub.add_parser("sieder-tate"); re_pr(st)
    st.add_argument("--mu-bulk", type=float, required=True, dest="mu_bulk")
    st.add_argument("--mu-wall", type=float, required=True, dest="mu_wall")
    st.add_argument("--heating", action="store_true")
    st.add_argument("--output", required=True)

    la = sub.add_parser("laminar")
    la.add_argument("--regime", choices=["constant-T", "constant-q"], required=True)
    la.add_argument("--k", type=float, required=True)
    la.add_argument("--Dh", type=float, required=True)
    la.add_argument("--output", required=True)

    nc = sub.add_parser("natural")
    nc.add_argument("--Ra", type=float, required=True)
    nc.add_argument("--Pr", type=float, required=True)
    nc.add_argument("--k", type=float, required=True)
    nc.add_argument("--L", type=float, required=True)
    nc.add_argument("--output", required=True)

    bo = sub.add_parser("boiling")
    bo.add_argument("--T-sat", type=float, required=True, dest="T_sat_K")
    bo.add_argument("--T-wall", type=float, required=True, dest="T_wall_K")
    bo.add_argument("--P", type=float, required=True, dest="P_Pa")
    bo.add_argument("--k-l", type=float, required=True, dest="k_l")
    bo.add_argument("--rho-l", type=float, required=True, dest="rho_l")
    bo.add_argument("--rho-g", type=float, required=True, dest="rho_g")
    bo.add_argument("--sigma", type=float, required=True)
    bo.add_argument("--cpl", type=float, required=True)
    bo.add_argument("--dHvap", type=float, required=True)
    bo.add_argument("--mu-l", type=float, required=True, dest="mu_l")
    bo.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://ht.readthedocs.io/"],
        library_attributions=["ht (Caleb Bell) — MIT"],
    )
    try:
        kw = {k: v for k, v in vars(args).items() if k not in ("command", "output", "regime")}
        if args.command == "dittus-boelter":
            res = dittus_boelter(**kw)
        elif args.command == "gnielinski":
            res = gnielinski(**kw)
        elif args.command == "sieder-tate":
            res = sieder_tate(**kw)
        elif args.command == "laminar":
            res = (laminar_pipe_constant_T if args.regime == "constant-T" else laminar_pipe_constant_q)(k=args.k, Dh=args.Dh)
        elif args.command == "natural":
            res = churchill_chu_natural_convection(**kw)
        else:
            res = ht_boiling(**kw)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["Incropera & DeWitt", "Kakac", "ht (Caleb Bell)"],
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

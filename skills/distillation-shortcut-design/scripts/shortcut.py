#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Distillation shortcut: Fenske, Underwood, Gilliland, McCabe-Thiele."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import parse_number_list, result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.separations import (
    fenske_min_stages,
    underwood_min_reflux,
    gilliland_stages,
    mccabe_thiele_stages,
)

SKILL = "distillation-shortcut-design"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Distillation shortcut methods")
    sub = p.add_subparsers(dest="command", required=True)

    f = sub.add_parser("fenske")
    f.add_argument("--alpha", type=float, required=True)
    f.add_argument("--xD", type=float, required=True)
    f.add_argument("--xB", type=float, required=True)
    f.add_argument("--output", required=True)

    u = sub.add_parser("underwood")
    u.add_argument("--alphas", required=True)
    u.add_argument("--zs", required=True)
    u.add_argument("--xds", required=True)
    u.add_argument("--q", type=float, default=1.0)
    u.add_argument("--output", required=True)

    g = sub.add_parser("gilliland")
    g.add_argument("--Nmin", type=float, required=True)
    g.add_argument("--Rmin", type=float, required=True)
    g.add_argument("--R", type=float, required=True)
    g.add_argument("--output", required=True)

    m = sub.add_parser("mccabe-thiele")
    m.add_argument("--alpha", type=float, required=True)
    m.add_argument("--xD", type=float, required=True)
    m.add_argument("--xB", type=float, required=True)
    m.add_argument("--xF", type=float, required=True)
    m.add_argument("--q", type=float, required=True)
    m.add_argument("--R", type=float, required=True)
    m.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["Original implementation; no proprietary text reproduced."],
        library_attributions=["engg_skills_common (this repo) — Apache-2.0"],
        extra_notes="Shortcut methods only; not a substitute for tray-by-tray simulation.",
    )
    try:
        if args.command == "fenske":
            res = fenske_min_stages(alpha=args.alpha, xD=args.xD, xB=args.xB)
        elif args.command == "underwood":
            res = underwood_min_reflux(
                alphas=parse_number_list(args.alphas),
                feed_zs=parse_number_list(args.zs),
                distillate_xs=parse_number_list(args.xds),
                q=args.q,
            )
        elif args.command == "gilliland":
            res = gilliland_stages(Nmin=args.Nmin, Rmin=args.Rmin, R=args.R)
        else:
            res = mccabe_thiele_stages(
                alpha=args.alpha, xD=args.xD, xB=args.xB, xF=args.xF, q=args.q, R=args.R
            )
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["Seader/Henley", "McCabe/Smith/Harriott", "Sinnott"],
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

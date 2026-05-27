#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compositional Data Analysis CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.coda import (
    alr,
    clr,
    heavy_end_balance,
    ilr,
    multiplicative_replacement,
    sbp_to_psi,
)
from engg_skills_common.io import parse_number_list, result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "compositional_data_analysis"
SKILL_DIR = Path(__file__).resolve().parents[1]


def _parse_composition(text: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in text.split(","):
        if "=" not in item:
            raise ValueError(f"expected NAME=VALUE, got {item!r}")
        name, value = item.split("=", 1)
        out[name.strip().lower()] = float(value)
    return out


def _parse_sbp(text: str) -> list[list[int]]:
    return [[int(v.strip()) for v in row.split(",")] for row in text.split(";") if row.strip()]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Compositional Data Analysis")
    sub = p.add_subparsers(dest="command", required=True)

    for name in ("clr", "alr", "ilr-default"):
        s = sub.add_parser(name)
        s.add_argument("--x", required=True)
        if name == "alr":
            s.add_argument("--denominator-index", type=int, default=-1, dest="denom")
        s.add_argument("--output", required=True)

    si = sub.add_parser("ilr-sbp")
    si.add_argument("--x", required=True)
    si.add_argument("--sbp", required=True)
    si.add_argument("--output", required=True)

    he = sub.add_parser("heavy-end")
    he.add_argument("--composition", required=True)
    he.add_argument("--heavy", required=True)
    he.add_argument("--body", required=True)
    he.add_argument("--output", required=True)

    zr = sub.add_parser("zero-replace")
    zr.add_argument("--x", required=True)
    zr.add_argument("--delta", type=float, default=1e-6)
    zr.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["Original implementation of public CoDA formulas."],
        extra_notes="Implements log-ratio transforms; cite Pawlowsky-Glahn et al. for theory.",
    )
    try:
        if args.command == "clr":
            x = parse_number_list(args.x)
            res = {"x": list(x), "clr": clr(x)}
        elif args.command == "alr":
            x = parse_number_list(args.x)
            res = {"x": list(x), "alr": alr(x, denominator_index=args.denom), "denominator_index": args.denom}
        elif args.command == "ilr-default":
            x = parse_number_list(args.x)
            res = {"x": list(x), "ilr": ilr(x), "basis": "Helmert-default"}
        elif args.command == "ilr-sbp":
            x = parse_number_list(args.x)
            sbp = _parse_sbp(args.sbp)
            res = {"x": list(x), "sbp": sbp, "psi": sbp_to_psi(sbp), "ilr": ilr(x, sbp)}
        elif args.command == "heavy-end":
            comp = _parse_composition(args.composition)
            heavy = [c.strip().lower() for c in args.heavy.split(",")]
            body = [c.strip().lower() for c in args.body.split(",")]
            res = heavy_end_balance(composition=comp, heavy_components=heavy, body_components=body)
        else:
            x = parse_number_list(args.x)
            res = {"x": list(x), "replaced": multiplicative_replacement(x, delta=args.delta), "delta": args.delta}
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["Pawlowsky-Glahn et al. (2015)", "Egozcue & Pawlowsky-Glahn (2005)"],
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

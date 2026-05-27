#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Screening amine treating mass-balance helpers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.amine import (
    amine_circulation_rate,
    loading_envelope_warnings,
    loading_from_mass_balance,
)
from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "sour_gas_amine_treating"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Amine treating screening helpers")
    sub = p.add_subparsers(dest="command", required=True)

    l = sub.add_parser("loading")
    l.add_argument("--acid-gas-mol-s", type=float, required=True, dest="acid_gas_mol_s")
    l.add_argument("--amine-mol-s", type=float, required=True, dest="amine_mol_s")
    l.add_argument("--output", required=True)

    c = sub.add_parser("circulation")
    c.add_argument("--acid-gas-mol-s", type=float, required=True, dest="acid_gas_mol_s")
    c.add_argument("--rich", type=float, required=True, dest="rich_loading_mol_per_mol")
    c.add_argument("--lean", type=float, required=True, dest="lean_loading_mol_per_mol")
    c.add_argument("--amine", default="DEA")
    c.add_argument("--wt-fraction", type=float, default=0.30, dest="amine_wt_fraction")
    c.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["GPSA Engineering Data Book Section 21 (procure separately)"],
        standards_referenced=["GPSA Engineering Data Book, Section 21 — Hydrocarbon Treating"],
        extra_notes="Screening only; not a substitute for rate-based amine simulation.",
    )
    try:
        if args.command == "loading":
            value = loading_from_mass_balance(acid_gas_mol_s=args.acid_gas_mol_s, amine_mol_s=args.amine_mol_s)
            res = {"loading_mol_acid_per_mol_amine": value, "acid_gas_mol_s": args.acid_gas_mol_s, "amine_mol_s": args.amine_mol_s}
            warnings: list[str] = []
        else:
            res = amine_circulation_rate(
                acid_gas_mol_s=args.acid_gas_mol_s,
                rich_loading_mol_per_mol=args.rich_loading_mol_per_mol,
                lean_loading_mol_per_mol=args.lean_loading_mol_per_mol,
                amine=args.amine,
                amine_wt_fraction=args.amine_wt_fraction,
            )
            warnings = loading_envelope_warnings(amine=args.amine, rich_loading_mol_per_mol=args.rich_loading_mol_per_mol)
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            warnings=warnings,
            sources=["GPSA Engineering Data Book Section 21 (referenced)", "Kohl & Nielsen Gas Purification"],
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

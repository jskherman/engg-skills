#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Caustic / Merox screening helpers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.merox import (
    disulfide_carryback_risk,
    extractor_kremser,
    mercaptide_loading,
)
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "caustic-merox-extraction"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Caustic Merox screening")
    sub = p.add_subparsers(dest="command", required=True)

    l = sub.add_parser("loading")
    l.add_argument("--rsh-ppmw", type=float, required=True, dest="rsh_inlet_lpg_ppmw")
    l.add_argument("--lpg-kg-s", type=float, required=True, dest="lpg_mass_flow_kg_s")
    l.add_argument("--caustic-kg-s", type=float, required=True, dest="caustic_circulation_kg_s")
    l.add_argument("--naoh-wt", type=float, required=True, dest="naoh_wt_fraction")
    l.add_argument("--rsh-mw", type=float, default=76.0, dest="avg_rsh_mw_g_mol")
    l.add_argument("--output", required=True)

    k = sub.add_parser("kremser")
    k.add_argument("--K", type=float, required=True, dest="distribution_K_lpg_to_caustic")
    k.add_argument("--lpg-vol", type=float, required=True, dest="lpg_volumetric_m3_s")
    k.add_argument("--caustic-vol", type=float, required=True, dest="caustic_volumetric_m3_s")
    k.add_argument("--stages", type=float, required=True, dest="n_theoretical_stages")
    k.add_argument("--rsh-in", type=float, required=True, dest="rsh_in_lpg")
    k.add_argument("--output", required=True)

    c = sub.add_parser("carryback")
    c.add_argument("--caustic-disulfide-ppmw", type=float, required=True)
    c.add_argument("--caustic-age-days", type=float, required=True)
    c.add_argument("--separator-dp-kpa", type=float, required=True)
    c.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["UOP Merox descriptive literature (public)"],
        extra_notes="Screening only; not a substitute for the licensor's process model.",
    )
    try:
        if args.command == "loading":
            res = mercaptide_loading(
                rsh_inlet_lpg_ppmw=args.rsh_inlet_lpg_ppmw,
                lpg_mass_flow_kg_s=args.lpg_mass_flow_kg_s,
                caustic_circulation_kg_s=args.caustic_circulation_kg_s,
                naoh_wt_fraction=args.naoh_wt_fraction,
                avg_rsh_mw_g_mol=args.avg_rsh_mw_g_mol,
            )
        elif args.command == "kremser":
            res = extractor_kremser(
                distribution_K_lpg_to_caustic=args.distribution_K_lpg_to_caustic,
                lpg_volumetric_m3_s=args.lpg_volumetric_m3_s,
                caustic_volumetric_m3_s=args.caustic_volumetric_m3_s,
                n_theoretical_stages=args.n_theoretical_stages,
                rsh_in_lpg=args.rsh_in_lpg,
            )
        else:
            res = disulfide_carryback_risk(
                caustic_disulfide_ppmw=args.caustic_disulfide_ppmw,
                caustic_age_days=args.caustic_age_days,
                separator_dp_kpa=args.separator_dp_kpa,
            )
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["Kohl & Nielsen Gas Purification", "UOP Merox descriptive literature"],
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

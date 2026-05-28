#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["thermo>=0.6", "chemicals>=1.5", "fluids>=1.3"]
# ///
"""CLI for VLE flash calculations using thermo / chemicals."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import parse_number_list, result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.vle import (
    SUPPORTED_EOS,
    bubble_point_P,
    dew_point_P,
    flash_TP,
    rachford_rice,
)

SKILL = "vle-flash-calculations"
SKILL_DIR = Path(__file__).resolve().parents[1]


def _emit_license() -> None:
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=[
            "https://thermo.readthedocs.io/",
            "https://chemicals.readthedocs.io/",
        ],
        library_attributions=[
            "thermo (Caleb Bell) — MIT",
            "chemicals (Caleb Bell) — MIT",
        ],
        extra_notes=(
            "Equation-of-state results are sensitive to binary interaction "
            "parameters; verify against lab data, plant data, or a trusted "
            "simulator before any design or operations decision."
        ),
    )


def _comps(text: str) -> list[str]:
    return [c.strip() for c in text.split(",") if c.strip()]


def _parse_kijs(text: str | None, n: int) -> list[list[float]] | None:
    if not text:
        return None
    rows = [r.strip() for r in text.split(";") if r.strip()]
    if len(rows) != n:
        raise ValueError(f"kijs must have {n} rows separated by ';'")
    return [parse_number_list(r) for r in rows]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="VLE flash calculator (thermo + chemicals)")
    sub = p.add_subparsers(dest="command", required=True)

    tp = sub.add_parser("tp", help="T,P,zs flash")
    tp.add_argument("--components", required=True)
    tp.add_argument("--zs", required=True)
    tp.add_argument("--T-K", type=float, required=True, dest="T")
    tp.add_argument("--P-Pa", type=float, required=True, dest="P")
    tp.add_argument("--eos", default="PR", choices=sorted(SUPPORTED_EOS))
    tp.add_argument("--kijs", default=None, help="kij matrix as rows of comma-separated floats joined by ';'")
    tp.add_argument("--output", required=True)

    for name, helptxt in (("bubble", "bubble-point pressure at T"), ("dew", "dew-point pressure at T")):
        b = sub.add_parser(name, help=helptxt)
        b.add_argument("--components", required=True)
        b.add_argument("--zs", required=True)
        b.add_argument("--T-K", type=float, required=True, dest="T")
        b.add_argument("--eos", default="PR", choices=sorted(SUPPORTED_EOS))
        b.add_argument("--kijs", default=None)
        b.add_argument("--output", required=True)

    rr = sub.add_parser("rr", help="Rachford-Rice flash from K-values")
    rr.add_argument("--Ks", required=True)
    rr.add_argument("--zs", required=True)
    rr.add_argument("--output", required=True)

    env = sub.add_parser("envelope", help="T,P,zs flash at a list of temperatures")
    env.add_argument("--components", required=True)
    env.add_argument("--zs", required=True)
    env.add_argument("--T-K-list", required=True, dest="Tlist")
    env.add_argument("--P-Pa", type=float, required=True, dest="P")
    env.add_argument("--eos", default="PR", choices=sorted(SUPPORTED_EOS))
    env.add_argument("--kijs", default=None)
    env.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    _emit_license()
    try:
        if args.command == "tp":
            comps = _comps(args.components)
            zs = parse_number_list(args.zs)
            res = flash_TP(
                identifiers=comps,
                T=args.T,
                P=args.P,
                zs=zs,
                eos_name=args.eos,
                kijs=_parse_kijs(args.kijs, len(comps)),
            )
        elif args.command == "bubble":
            comps = _comps(args.components)
            zs = parse_number_list(args.zs)
            res = bubble_point_P(
                identifiers=comps,
                T=args.T,
                zs=zs,
                eos_name=args.eos,
                kijs=_parse_kijs(args.kijs, len(comps)),
            )
        elif args.command == "dew":
            comps = _comps(args.components)
            zs = parse_number_list(args.zs)
            res = dew_point_P(
                identifiers=comps,
                T=args.T,
                zs=zs,
                eos_name=args.eos,
                kijs=_parse_kijs(args.kijs, len(comps)),
            )
        elif args.command == "rr":
            Ks = parse_number_list(args.Ks)
            zs = parse_number_list(args.zs)
            res = rachford_rice(Ks, zs)
        else:  # envelope
            comps = _comps(args.components)
            zs = parse_number_list(args.zs)
            Ts = parse_number_list(args.Tlist)
            envelope = []
            for T in Ts:
                envelope.append(
                    flash_TP(
                        identifiers=comps,
                        T=T,
                        P=args.P,
                        zs=zs,
                        eos_name=args.eos,
                        kijs=_parse_kijs(args.kijs, len(comps)),
                    )
                )
            res = {"method": "envelope-isobaric", "P_Pa": args.P, "points": envelope}
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            sources=["thermo.FlashVL", "thermo.eos_mix.*", "chemicals.search_chemical"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        write_json(
            result_envelope(
                skill=SKILL,
                inputs=vars(args),
                results={"error": str(exc)},
                ok=False,
            ),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

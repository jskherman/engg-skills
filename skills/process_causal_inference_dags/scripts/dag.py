#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""DAG-based adjustment-set helper for process-data observational studies."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.causal import DAG
from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "process_causal_inference_dags"
SKILL_DIR = Path(__file__).resolve().parents[1]


def _parse_edges(text: str) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for row in text.split(";"):
        row = row.strip()
        if not row:
            continue
        if "," not in row:
            raise ValueError(f"edge must be 'u,v', got {row!r}")
        u, v = row.split(",", 1)
        edges.append((u.strip(), v.strip()))
    return edges


def _set_or_empty(text: str | None) -> set[str]:
    if not text:
        return set()
    return {s.strip() for s in text.split(",") if s.strip()}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="DAG adjustment-set tooling")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("check")
    c.add_argument("--edges", required=True)
    c.add_argument("--treatment", required=True)
    c.add_argument("--outcome", required=True)
    c.add_argument("--output", required=True)

    d = sub.add_parser("dsep")
    d.add_argument("--edges", required=True)
    d.add_argument("--x", required=True)
    d.add_argument("--y", required=True)
    d.add_argument("--z", default="")
    d.add_argument("--output", required=True)

    g = sub.add_parser("dot")
    g.add_argument("--edges", required=True)
    g.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["Original implementation of public causal-DAG algorithms."],
        extra_notes="Implements Pearl-style d-separation and parents-of-treatment back-door adjustment.",
    )
    try:
        if args.command == "check":
            g = DAG.from_edges(_parse_edges(args.edges))
            res = g.backdoor_adjustment(args.treatment, args.outcome)
            res["treatment"] = args.treatment
            res["outcome"] = args.outcome
            data = result_envelope(skill=SKILL, inputs=vars(args), results=res)
        elif args.command == "dsep":
            g = DAG.from_edges(_parse_edges(args.edges))
            x = _set_or_empty(args.x)
            y = _set_or_empty(args.y)
            z = _set_or_empty(args.z)
            res = {"x": sorted(x), "y": sorted(y), "z": sorted(z), "d_separated": g.d_separated(x, y, z)}
            data = result_envelope(skill=SKILL, inputs=vars(args), results=res)
        else:
            g = DAG.from_edges(_parse_edges(args.edges))
            dot = g.to_dot("ProcessDAG")
            # write directly to the output as plain text (not JSON)
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(dot + "\n", encoding="utf-8")
            print(f"Success. DOT written to: {out}")
            return 0
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

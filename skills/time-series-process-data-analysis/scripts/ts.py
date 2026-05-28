#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas>=2.1"]
# ///
"""ACF, PACF, block-length heuristic, and moving block bootstrap CLI."""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

import pandas as pd

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import (
    STATISTICAL_INFERENCE_NOTICE,
    license_notice_for,
    write_license_notification,
)
from engg_skills_common.timeseries import (
    autocorrelation,
    estimate_block_length,
    moving_block_bootstrap,
    partial_autocorrelation,
)

SKILL = "time-series-process-data-analysis"
SKILL_DIR = Path(__file__).resolve().parents[1]

STATS = {
    "mean": statistics.fmean,
    "median": statistics.median,
    "std": statistics.stdev,
    "min": min,
    "max": max,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ACF / PACF / block bootstrap")
    sub = p.add_subparsers(dest="command", required=True)

    for name in ("acf", "pacf"):
        s = sub.add_parser(name)
        s.add_argument("--data", required=True)
        s.add_argument("--column", required=True)
        s.add_argument("--max-lag", type=int, required=True, dest="max_lag")
        s.add_argument("--output", required=True)

    bl = sub.add_parser("block-len")
    bl.add_argument("--data", required=True)
    bl.add_argument("--column", required=True)
    bl.add_argument("--c", type=float, default=2.0)
    bl.add_argument("--output", required=True)

    bs = sub.add_parser("bootstrap")
    bs.add_argument("--data", required=True)
    bs.add_argument("--column", required=True)
    bs.add_argument("--block-length", type=int, required=True, dest="block_length")
    bs.add_argument("--n-resamples", type=int, required=True, dest="n_resamples")
    bs.add_argument("--statistic", default="mean", choices=sorted(STATS))
    bs.add_argument("--seed", type=int, default=None)
    bs.add_argument("--output", required=True)
    return p


def _load_series(args) -> list[float]:
    df = pd.read_csv(args.data)
    return df[args.column].astype(float).dropna().tolist()


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["Original implementation of ACF/PACF and Kuensch block bootstrap."],
        extra_notes=STATISTICAL_INFERENCE_NOTICE,
    )
    try:
        x = _load_series(args)
        if args.command == "acf":
            res = {"max_lag": args.max_lag, "acf": autocorrelation(x, args.max_lag)}
        elif args.command == "pacf":
            res = {"max_lag": args.max_lag, "pacf": partial_autocorrelation(x, args.max_lag)}
        elif args.command == "block-len":
            res = estimate_block_length(x, c=args.c)
        else:
            stat = STATS[args.statistic]
            res = moving_block_bootstrap(
                x,
                block_length=args.block_length,
                n_resamples=args.n_resamples,
                statistic=stat,
                seed=args.seed,
            )
            res["statistic"] = args.statistic
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            warnings=[STATISTICAL_INFERENCE_NOTICE],
            sources=["Kuensch 1989", "Politis & Romano Subsampling"],
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

#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "scipy>=1.11", "pandas>=2.1"]
# ///
"""Penalised FIR distributed-lag regression."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import (
    STATISTICAL_INFERENCE_NOTICE,
    license_notice_for,
    write_license_notification,
)

SKILL = "distributed_lag_models"
SKILL_DIR = Path(__file__).resolve().parents[1]


def _build_lag_matrix(x: np.ndarray, max_lag: int) -> np.ndarray:
    n = len(x)
    L = max_lag + 1
    X = np.zeros((n, L))
    for k in range(L):
        X[k:, k] = x[: n - k]
    return X


def _second_difference_penalty(L: int) -> np.ndarray:
    D = np.zeros((L - 2, L))
    for i in range(L - 2):
        D[i, i] = 1.0
        D[i, i + 1] = -2.0
        D[i, i + 2] = 1.0
    return D.T @ D


def fit_fir(
    df: pd.DataFrame,
    response: str,
    predictor: str,
    max_lag: int,
    *,
    penalty: float = 1.0,
    reverse_for_placebo: bool = False,
) -> dict:
    x = df[predictor].astype(float).values
    y = df[response].astype(float).values
    if reverse_for_placebo:
        x = x[::-1]
    obs_mask = ~np.isnan(y)
    X_full = _build_lag_matrix(x, max_lag)
    X = X_full[obs_mask]
    y_obs = y[obs_mask]
    # Centre y to drop intercept; user can add fixed effects via predictor.
    y_mean = y_obs.mean()
    y_c = y_obs - y_mean
    L = max_lag + 1
    R = _second_difference_penalty(L) * penalty
    # Constrain weights to sum to 1 with a quadratic penalty (soft).
    sum1_pen = 1e3 * np.outer(np.ones(L), np.ones(L))
    A = X.T @ X + R + sum1_pen
    b = X.T @ y_c + 1e3 * np.ones(L)
    w = np.linalg.solve(A, b)
    # Non-negativity by projection (simple PGD step)
    for _ in range(50):
        w = np.maximum(w, 0.0)
        grad = A @ w - b
        w = w - 0.01 * grad
        w = np.maximum(w, 0.0)
        w = w / max(w.sum(), 1e-9)
    fitted = X @ w + y_mean
    rss = float(np.sum((y_obs - fitted) ** 2))
    centroid_lag = float(np.sum(np.arange(L) * w))
    cumulative = np.cumsum(w)
    t50 = int(np.argmax(cumulative >= 0.5)) if (cumulative >= 0.5).any() else max_lag
    return {
        "method": "FIR-penalised-NN-projection",
        "max_lag": max_lag,
        "weights": w.tolist(),
        "sum_weights": float(w.sum()),
        "peak_lag": int(np.argmax(w)),
        "centroid_lag": centroid_lag,
        "time_to_50pct_response": t50,
        "rss": rss,
        "n_observations": int(obs_mask.sum()),
        "penalty": penalty,
        "is_placebo": reverse_for_placebo,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Penalised distributed-lag FIR fit")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("fit", "placebo"):
        s = sub.add_parser(name)
        s.add_argument("--data", required=True)
        s.add_argument("--response", required=True)
        s.add_argument("--predictor", required=True)
        s.add_argument("--max-lag", type=int, required=True, dest="max_lag")
        s.add_argument("--penalty", type=float, default=1.0)
        s.add_argument("--output", required=True)
    args = parser.parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["scipy/numpy/pandas BSD-licensed"],
        extra_notes=STATISTICAL_INFERENCE_NOTICE,
    )
    try:
        df = pd.read_csv(args.data)
        res = fit_fir(
            df=df,
            response=args.response,
            predictor=args.predictor,
            max_lag=args.max_lag,
            penalty=args.penalty,
            reverse_for_placebo=(args.command == "placebo"),
        )
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            warnings=[STATISTICAL_INFERENCE_NOTICE],
            sources=["Almon 1965", "numpy/scipy"],
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

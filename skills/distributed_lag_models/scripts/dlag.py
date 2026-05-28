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
from scipy.optimize import minimize

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
    if max_lag < 0:
        raise ValueError("max_lag must be non-negative")
    n = len(x)
    L = max_lag + 1
    if L > n:
        raise ValueError("max_lag must be less than the number of rows")
    X = np.full((n, L), np.nan)
    for k in range(L):
        X[k:, k] = x[: n - k]
    return X


def _second_difference_penalty(L: int) -> np.ndarray:
    if L < 3:
        return np.zeros((L, L))
    D = np.zeros((L - 2, L))
    for i in range(L - 2):
        D[i, i] = 1.0
        D[i, i + 1] = -2.0
        D[i, i + 2] = 1.0
    return D.T @ D


def _fit_unrestricted(X: np.ndarray, y: np.ndarray, penalty: float) -> tuple[float, np.ndarray]:
    L = X.shape[1]
    Xd = np.column_stack([np.ones(len(X)), X])
    P = np.zeros((L + 1, L + 1))
    P[1:, 1:] = _second_difference_penalty(L) * penalty
    A = Xd.T @ Xd + P
    b = Xd.T @ y
    try:
        params = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        params = np.linalg.lstsq(A, b, rcond=None)[0]
    return float(params[0]), params[1:]


def _fit_nonnegative(X: np.ndarray, y: np.ndarray, penalty: float) -> tuple[float, np.ndarray]:
    intercept0, coeff0 = _fit_unrestricted(X, y, penalty)
    L = X.shape[1]
    P = _second_difference_penalty(L) * penalty
    start = np.r_[intercept0, np.maximum(coeff0, 0.0)]

    def objective(params: np.ndarray) -> float:
        intercept = params[0]
        coeff = params[1:]
        resid = y - (intercept + X @ coeff)
        return float(resid @ resid + coeff @ P @ coeff)

    res = minimize(
        objective,
        start,
        method="L-BFGS-B",
        bounds=[(None, None)] + [(0.0, None)] * L,
    )
    if not res.success:
        raise RuntimeError(f"nonnegative FIR optimization failed: {res.message}")
    return float(res.x[0]), res.x[1:]


def _kernel_summary(coeff: np.ndarray) -> tuple[list[float] | None, float | None, int | None, list[str]]:
    warnings: list[str] = []
    total = float(coeff.sum())
    if abs(total) < 1e-12:
        return None, None, None, ["Cumulative lag effect is approximately zero; normalized lag weights are undefined."]
    if np.any(coeff > 0) and np.any(coeff < 0):
        warnings.append("Lag coefficients have mixed signs; normalized residence-time-style weights are not reported.")
        return None, None, None, warnings
    weights = coeff / total
    cumulative = np.cumsum(weights)
    t50 = int(np.argmax(cumulative >= 0.5)) if np.any(cumulative >= 0.5) else None
    centroid = float(np.sum(np.arange(len(coeff)) * weights))
    return weights.tolist(), centroid, t50, warnings


def fit_fir(
    df: pd.DataFrame,
    response: str,
    predictor: str,
    max_lag: int,
    *,
    penalty: float = 1.0,
    nonnegative: bool = False,
    reverse_for_placebo: bool = False,
) -> dict:
    if penalty < 0:
        raise ValueError("penalty must be non-negative")
    x = df[predictor].astype(float).values
    y = df[response].astype(float).values
    if reverse_for_placebo:
        x = x[::-1]
    X_full = _build_lag_matrix(x, max_lag)
    obs_mask = (~np.isnan(y)) & np.all(np.isfinite(X_full), axis=1)
    X = X_full[obs_mask]
    y_obs = y[obs_mask]
    L = max_lag + 1
    if len(y_obs) <= L + 1:
        raise ValueError("not enough observed response rows for the requested lag horizon")

    if nonnegative:
        intercept, coeff = _fit_nonnegative(X, y_obs, penalty)
        method = "FIR-penalised-nonnegative"
    else:
        intercept, coeff = _fit_unrestricted(X, y_obs, penalty)
        method = "FIR-penalised-unrestricted"

    fitted = intercept + X @ coeff
    resid = y_obs - fitted
    rss = float(np.sum(resid ** 2))
    tss = float(np.sum((y_obs - y_obs.mean()) ** 2))
    r2 = 1.0 - rss / tss if tss > 0 else None
    normalized_weights, centroid_lag, t50, warnings = _kernel_summary(coeff)
    if len(y_obs) < 5 * L:
        warnings.append("Observed response count is less than five times the number of lag coefficients; use stronger prior/penalty or a shorter lag horizon.")

    return {
        "method": method,
        "max_lag": max_lag,
        "intercept": intercept,
        "lag_coefficients": coeff.tolist(),
        "cumulative_effect_per_predictor_unit": float(coeff.sum()),
        "normalized_lag_weights": normalized_weights,
        "weights": normalized_weights,
        "peak_effect_lag": int(np.argmax(np.abs(coeff))),
        "peak_positive_lag": int(np.argmax(coeff)),
        "centroid_lag": centroid_lag,
        "time_to_50pct_response": t50,
        "rss": rss,
        "r_squared": r2,
        "n_observations": int(obs_mask.sum()),
        "penalty": penalty,
        "nonnegative": nonnegative,
        "is_placebo": reverse_for_placebo,
        "warnings": warnings,
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
        s.add_argument("--nonnegative", action="store_true", help="Constrain lag coefficients to be non-negative")
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
            nonnegative=args.nonnegative,
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

#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "scipy>=1.11", "pandas>=2.1"]
# ///
"""Censored-normal / censored-lognormal regression.

Implements a censored-normal likelihood using SciPy's `minimize`. With the
log-response option enabled, the same likelihood is applied to log(y), giving a
censored-lognormal model on the original response scale.

Censoring-column semantics:
- observed response value present: exact observation; censoring bounds ignored.
- response missing + only `lower_col` finite: left-censored, y <= lower_col.
- response missing + only `upper_col` finite: right-censored, y >= upper_col.
- response missing + both bounds finite: interval-censored, lower_col < y < upper_col.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import (
    STATISTICAL_INFERENCE_NOTICE,
    license_notice_for,
    write_license_notification,
)

SKILL = "censored_regression"
SKILL_DIR = Path(__file__).resolve().parents[1]


def _build_X(df: pd.DataFrame, predictors: list[str]) -> np.ndarray:
    missing = [col for col in predictors if col not in df.columns]
    if missing:
        raise ValueError(f"predictor columns not found: {missing}")
    return np.column_stack([np.ones(len(df))] + [df[col].astype(float).values for col in predictors])


def _finite_or_nan(df: pd.DataFrame, column: str | None) -> np.ndarray:
    return df[column].astype(float).values if column else np.full(len(df), np.nan)


def _prepare_response_and_bounds(
    df: pd.DataFrame,
    *,
    response: str,
    lower_col: str | None,
    upper_col: str | None,
    log_response: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str], dict[str, Any]]:
    if response not in df.columns:
        raise ValueError(f"response column not found: {response}")
    for col in (lower_col, upper_col):
        if col and col not in df.columns:
            raise ValueError(f"censoring column not found: {col}")

    y_raw = df[response].astype(float).values
    lower = _finite_or_nan(df, lower_col)
    upper = _finite_or_nan(df, upper_col)
    observed = np.isfinite(y_raw)
    has_lower = np.isfinite(lower)
    has_upper = np.isfinite(upper)

    kinds: list[str] = []
    for i in range(len(df)):
        if observed[i]:
            kinds.append("obs")
        elif has_lower[i] and has_upper[i]:
            if lower[i] >= upper[i]:
                raise ValueError("interval-censored rows require lower_col < upper_col")
            kinds.append("interval")
        elif has_lower[i]:
            kinds.append("left")
        elif has_upper[i]:
            kinds.append("right")
        else:
            raise ValueError("missing response rows must have a censoring bound")

    if log_response:
        positive_observed = y_raw[observed]
        positive_bounds = np.r_[lower[has_lower], upper[has_upper]]
        if positive_observed.size and np.any(positive_observed <= 0):
            raise ValueError("log-response model requires positive observed responses")
        if positive_bounds.size and np.any(positive_bounds <= 0):
            raise ValueError("log-response model requires positive censoring bounds")
        y = np.where(observed, np.log(y_raw), np.nan)
        lower_model = np.where(has_lower, np.log(lower), np.nan)
        upper_model = np.where(has_upper, np.log(upper), np.nan)
    else:
        y = y_raw
        lower_model = lower
        upper_model = upper

    counts = {
        "n_observed": int(sum(k == "obs" for k in kinds)),
        "n_left_censored": int(sum(k == "left" for k in kinds)),
        "n_right_censored": int(sum(k == "right" for k in kinds)),
        "n_interval_censored": int(sum(k == "interval" for k in kinds)),
    }
    return y, lower_model, upper_model, kinds, counts


def _neg_log_lik(params, y, X, lower, upper, censoring_kind):
    n_beta = X.shape[1]
    beta = params[:n_beta]
    log_sigma = params[n_beta]
    sigma = math.exp(log_sigma)
    mu = X @ beta
    ll = 0.0
    for i in range(len(y)):
        if censoring_kind[i] == "obs":
            ll += norm.logpdf(y[i], loc=mu[i], scale=sigma)
        elif censoring_kind[i] == "left":
            ll += norm.logcdf(lower[i], loc=mu[i], scale=sigma)
        elif censoring_kind[i] == "right":
            ll += norm.logsf(upper[i], loc=mu[i], scale=sigma)
        else:  # interval
            p_up = norm.cdf(upper[i], loc=mu[i], scale=sigma)
            p_lo = norm.cdf(lower[i], loc=mu[i], scale=sigma)
            ll += math.log(max(p_up - p_lo, 1e-300))
    return -ll


def fit(
    df: pd.DataFrame,
    response: str,
    predictors: list[str],
    *,
    lower_col: str | None,
    upper_col: str | None,
    log_response: bool = True,
) -> dict:
    y, lower, upper, kinds, counts = _prepare_response_and_bounds(
        df,
        response=response,
        lower_col=lower_col,
        upper_col=upper_col,
        log_response=log_response,
    )
    X = _build_X(df, predictors)
    if np.any(~np.isfinite(X)):
        raise ValueError("predictor matrix contains NaN or infinite values")

    observed_mask = np.array([k == "obs" for k in kinds], dtype=bool)
    finite_initial_values = y[observed_mask]
    if finite_initial_values.size == 0:
        finite_initial_values = np.r_[lower[np.isfinite(lower)], upper[np.isfinite(upper)]]
    init = np.zeros(X.shape[1] + 1)
    init[0] = float(np.nanmean(finite_initial_values)) if finite_initial_values.size else 0.0
    init[-1] = math.log(max(float(np.nanstd(finite_initial_values)) if finite_initial_values.size else 1.0, 1e-3))

    res = minimize(
        _neg_log_lik,
        init,
        args=(y, X, lower, upper, kinds),
        method="L-BFGS-B",
    )
    n_beta = X.shape[1]
    beta = res.x[:n_beta].tolist()
    sigma = math.exp(res.x[-1])
    fraction_censored = float(np.mean([k != "obs" for k in kinds]))
    method = "censored-lognormal-ML" if log_response else "censored-normal-ML"
    return {
        "method": method,
        "coefficients": dict(zip(["intercept"] + predictors, beta)),
        "sigma_model_scale": sigma,
        "log_response": log_response,
        "neg_log_lik": float(res.fun),
        "converged": bool(res.success),
        "optimizer_message": str(res.message),
        "fraction_censored": fraction_censored,
        "n_observations": int(len(df)),
        **counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Censored normal/lognormal regression")
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--data", required=True)
    f.add_argument("--response", required=True)
    f.add_argument("--predictors", required=True)
    f.add_argument("--lower-col", default=None, dest="lower_col")
    f.add_argument("--upper-col", default=None, dest="upper_col")
    f.add_argument("--no-log", action="store_false", dest="log_response")
    f.add_argument("--output", required=True)

    i = sub.add_parser("interval")
    i.add_argument("--data", required=True)
    i.add_argument("--response", required=True)
    i.add_argument("--predictors", required=True)
    i.add_argument("--lower-col", required=True, dest="lower_col")
    i.add_argument("--upper-col", required=True, dest="upper_col")
    i.add_argument("--no-log", action="store_false", dest="log_response")
    i.add_argument("--output", required=True)

    args = parser.parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://www.scipy.org/"],
        library_attributions=["scipy — BSD", "pandas — BSD", "numpy — BSD"],
        extra_notes=STATISTICAL_INFERENCE_NOTICE,
    )
    try:
        df = pd.read_csv(args.data)
        predictors = [c.strip() for c in args.predictors.split(",") if c.strip()]
        res = fit(
            df=df,
            response=args.response,
            predictors=predictors,
            lower_col=args.lower_col,
            upper_col=args.upper_col,
            log_response=args.log_response,
        )
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            warnings=[STATISTICAL_INFERENCE_NOTICE],
            sources=["scipy.optimize", "Helsel, Statistics for Censored Environmental Data"],
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

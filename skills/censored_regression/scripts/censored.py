#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "scipy>=1.11", "pandas>=2.1"]
# ///
"""Censored (Tobit / censored lognormal) regression.

Implements the censored-normal likelihood by hand using SciPy's `minimize`
so the script does not require statsmodels' Tobit class (which moves
across versions). The likelihood handles left, right, and interval
censoring.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

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
    X = np.column_stack([np.ones(len(df))] + [df[col].astype(float).values for col in predictors])
    return X


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
    if log_response:
        y_raw = df[response].astype(float).values
        # observed: y_raw not NaN
        observed_mask = ~np.isnan(y_raw)
        # left-censored: response NaN, lower_col present
        lower = df[lower_col].astype(float).values if lower_col else np.full(len(df), np.nan)
        upper = df[upper_col].astype(float).values if upper_col else np.full(len(df), np.nan)
        y = np.where(observed_mask, np.log(np.maximum(y_raw, 1e-300)), np.nan)
        lower_log = np.where(~np.isnan(lower), np.log(np.maximum(lower, 1e-300)), np.nan)
        upper_log = np.where(~np.isnan(upper), np.log(np.maximum(upper, 1e-300)), np.nan)
    else:
        y = df[response].astype(float).values
        observed_mask = ~np.isnan(y)
        lower_log = df[lower_col].astype(float).values if lower_col else np.full(len(df), np.nan)
        upper_log = df[upper_col].astype(float).values if upper_col else np.full(len(df), np.nan)
    kinds: list[str] = []
    for i in range(len(df)):
        if observed_mask[i]:
            kinds.append("obs")
        elif lower_col and upper_col and not np.isnan(lower_log[i]) and not np.isnan(upper_log[i]):
            kinds.append("interval")
        elif lower_col and not np.isnan(lower_log[i]) and (upper_col is None or np.isnan(upper_log[i])):
            kinds.append("left")
        elif upper_col and not np.isnan(upper_log[i]):
            kinds.append("right")
        else:
            kinds.append("obs")  # treat as observed; user error otherwise
    X = _build_X(df, predictors)
    init = np.zeros(X.shape[1] + 1)
    init[0] = np.nanmean(y[observed_mask]) if observed_mask.any() else 0.0
    init[-1] = math.log(max(np.nanstd(y[observed_mask]) or 1.0, 1e-3))
    res = minimize(
        _neg_log_lik,
        init,
        args=(y, X, lower_log, upper_log, kinds),
        method="L-BFGS-B",
    )
    n_beta = X.shape[1]
    beta = res.x[:n_beta].tolist()
    sigma = math.exp(res.x[-1])
    fraction_censored = float(np.mean([k != "obs" for k in kinds]))
    return {
        "method": "censored-lognormal-ML",
        "coefficients": dict(zip(["intercept"] + predictors, beta)),
        "sigma_log_response": sigma,
        "neg_log_lik": float(res.fun),
        "converged": bool(res.success),
        "fraction_censored": fraction_censored,
        "n_observations": int(len(df)),
        "n_left_censored": int(sum(1 for k in kinds if k == "left")),
        "n_right_censored": int(sum(1 for k in kinds if k == "right")),
        "n_interval_censored": int(sum(1 for k in kinds if k == "interval")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Censored (Tobit) regression on log scale")
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

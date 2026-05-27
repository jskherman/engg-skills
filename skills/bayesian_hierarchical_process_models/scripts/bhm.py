#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymc>=5.10", "arviz>=0.17", "pandas>=2.1", "numpy>=1.26", "pyyaml>=6.0"]
# ///
"""Hierarchical Bayesian regression with optional censoring (PyMC)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import (
    STATISTICAL_INFERENCE_NOTICE,
    license_notice_for,
    write_license_notification,
)

SKILL = "bayesian_hierarchical_process_models"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_model(df: pd.DataFrame, spec: dict):
    import pymc as pm

    response = spec["response"]
    predictors = spec["predictors"]
    group = spec.get("group")
    censoring = spec.get("censoring") or {}
    ar1 = spec.get("ar1", False)
    priors = spec.get("priors", {})

    y_raw = df[response].astype(float).values
    X = np.column_stack([df[col].astype(float).values for col in predictors])
    X = (X - X.mean(axis=0)) / np.maximum(X.std(axis=0), 1e-9)

    group_idx = None
    n_groups = 0
    if group:
        codes, uniques = pd.factorize(df[group].astype("category"))
        group_idx = codes
        n_groups = len(uniques)

    lower = df[censoring["lower_col"]].astype(float).values if censoring.get("lower_col") else None
    upper = df[censoring["upper_col"]].astype(float).values if censoring.get("upper_col") else None
    observed_mask = ~np.isnan(y_raw)

    coords = {"obs": np.arange(len(df)), "pred": predictors}
    if group:
        coords["group"] = list(uniques)
    with pm.Model(coords=coords) as model:
        beta_prior = priors.get("beta", {"dist": "normal", "mu": 0.0, "sigma": 5.0})
        sigma_prior = priors.get("sigma", {"dist": "half_normal", "sigma": 1.0})
        beta = pm.Normal("beta", mu=beta_prior.get("mu", 0.0), sigma=beta_prior.get("sigma", 5.0), dims="pred")
        if group:
            tau_prior = priors.get("tau_group", {"dist": "half_normal", "sigma": 0.5})
            mu_alpha = pm.Normal("mu_alpha", mu=0.0, sigma=5.0)
            tau_group = pm.HalfNormal("tau_group", sigma=tau_prior.get("sigma", 0.5))
            alpha = pm.Normal("alpha", mu=mu_alpha, sigma=tau_group, dims="group")
            mu = alpha[group_idx] + pm.math.dot(X, beta)
        else:
            mu = pm.Normal("alpha", mu=0.0, sigma=5.0) + pm.math.dot(X, beta)
        sigma = pm.HalfNormal("sigma", sigma=sigma_prior.get("sigma", 1.0))
        if ar1:
            phi = pm.Uniform("phi", lower=-0.99, upper=0.99)
            eps = pm.AR("eps", rho=phi, sigma=sigma, init_dist=pm.Normal.dist(0.0, sigma), dims="obs")
            y_lat = pm.Deterministic("y_lat", mu + eps, dims="obs")
        else:
            y_lat = pm.Deterministic("y_lat", mu, dims="obs")
        # Observed (uncensored) data
        if observed_mask.any():
            pm.Normal("y_obs", mu=y_lat[observed_mask], sigma=sigma, observed=y_raw[observed_mask])
        # Censored data
        if lower is not None:
            left_mask = (~observed_mask) & (~np.isnan(lower))
            if left_mask.any():
                pm.Censored(
                    "y_left",
                    pm.Normal.dist(mu=y_lat[left_mask], sigma=sigma),
                    lower=-np.inf,
                    upper=lower[left_mask],
                    observed=lower[left_mask],
                )
    return model


def main() -> int:
    parser = argparse.ArgumentParser(description="Bayesian hierarchical fit (PyMC)")
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--data", required=True)
    f.add_argument("--spec", required=True)
    f.add_argument("--output", required=True)
    f.add_argument("--idata-out", default=None, dest="idata_out", help="Optional NetCDF path for InferenceData")
    args = parser.parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://www.pymc.io/", "https://www.arviz.org/"],
        library_attributions=["PyMC — Apache-2.0", "ArviZ — Apache-2.0"],
        extra_notes=STATISTICAL_INFERENCE_NOTICE,
    )
    try:
        import arviz as az
        import pymc as pm  # noqa: F401 imported via build_model

        df = pd.read_csv(args.data)
        with open(args.spec) as f:
            spec = yaml.safe_load(f)
        model = build_model(df, spec)
        sampler = spec.get("sampler", {})
        with model:
            idata = pm.sample(
                draws=int(sampler.get("draws", 1000)),
                tune=int(sampler.get("tune", 1000)),
                chains=int(sampler.get("chains", 4)),
                target_accept=float(sampler.get("target_accept", 0.9)),
                progressbar=False,
            )
        summary = az.summary(idata, hdi_prob=0.94)
        summary_dict = json.loads(summary.to_json(orient="index"))
        diagnostics = {
            "max_rhat": float(summary["r_hat"].max()),
            "min_ess_bulk": float(summary["ess_bulk"].min()),
            "min_ess_tail": float(summary["ess_tail"].min()),
            "divergences": int(idata.sample_stats["diverging"].sum().values),
        }
        if args.idata_out:
            az.to_netcdf(idata, args.idata_out)
            diagnostics["idata_path"] = args.idata_out
        res = {
            "method": "PyMC NUTS hierarchical regression",
            "summary": summary_dict,
            "diagnostics": diagnostics,
            "spec": spec,
        }
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            warnings=[STATISTICAL_INFERENCE_NOTICE],
            sources=["PyMC", "ArviZ", "Gelman et al. Bayesian Data Analysis"],
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

#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations
import argparse, sys
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.io import parse_number_list, result_envelope, write_json
from engg_skills_common.stats import describe, mean_confidence_interval, linear_regression

def main():
    p=argparse.ArgumentParser(description='Engineering statistics CLI')
    sub=p.add_subparsers(dest='command', required=True)
    d=sub.add_parser('describe'); d.add_argument('--values', required=True); d.add_argument('--output', required=True)
    ci=sub.add_parser('mean-ci'); ci.add_argument('--values', required=True); ci.add_argument('--confidence', type=float, default=0.95); ci.add_argument('--output', required=True)
    lr=sub.add_parser('linear-regression'); lr.add_argument('--x', required=True); lr.add_argument('--y', required=True); lr.add_argument('--output', required=True)
    a=p.parse_args()
    try:
        warnings=[]
        if a.command=='describe': res=describe(parse_number_list(a.values))
        elif a.command=='mean-ci': res=mean_confidence_interval(parse_number_list(a.values), a.confidence); warnings=res.pop('warnings', [])
        else: res=linear_regression(parse_number_list(a.x), parse_number_list(a.y))
        path=write_json(result_envelope(skill='engineering-statistics', inputs=vars(a), results=res, warnings=warnings), a.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='engineering-statistics', inputs=vars(a), results={'error':str(e)}, ok=False), a.output); print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())

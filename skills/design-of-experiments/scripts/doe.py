#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.doe import full_factorial, two_level_factorial
from engg_skills_common.io import result_envelope, write_json

def parse_factor(text):
    name, vals = text.split('=',1); return name.strip(), [v.strip() for v in vals.split(',') if v.strip()]
def main():
    p=argparse.ArgumentParser(description='Design of experiments helpers')
    sub=p.add_subparsers(dest='command', required=True)
    f=sub.add_parser('full-factorial'); f.add_argument('--factor', action='append', required=True, help='name=level1,level2,...'); f.add_argument('--replicates', type=int, default=1); f.add_argument('--randomize', action='store_true'); f.add_argument('--seed', type=int); f.add_argument('--output', required=True)
    t=sub.add_parser('two-level'); t.add_argument('--factors', required=True, help='comma-separated factor names'); t.add_argument('--randomize', action='store_true'); t.add_argument('--seed', type=int); t.add_argument('--output', required=True)
    a=p.parse_args()
    try:
        if a.command=='full-factorial': runs=full_factorial(dict(parse_factor(x) for x in a.factor), replicates=a.replicates, randomize=a.randomize, seed=a.seed)
        else: runs=two_level_factorial([x.strip() for x in a.factors.split(',') if x.strip()], randomize=a.randomize, seed=a.seed)
        path=write_json(result_envelope(skill='design-of-experiments', inputs=vars(a), results={'run_count':len(runs), 'runs':runs}, assumptions=['Generated plan only; confirm feasibility, blocking, randomization, and safety before execution.']), a.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='design-of-experiments', inputs=vars(a), results={'error':str(e)}, ok=False), a.output); print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())

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
from engg_skills_common.spc import individuals_chart, xbar_r_chart, capability

def parse_groups(s): return [parse_number_list(g) for g in s.split('|')]
def main():
    p=argparse.ArgumentParser(description='SPC helpers')
    sub=p.add_subparsers(dest='command', required=True)
    i=sub.add_parser('individuals'); i.add_argument('--values', required=True); i.add_argument('--output', required=True)
    x=sub.add_parser('xbar-r'); x.add_argument('--subgroups', required=True, help='groups separated by |, values by comma'); x.add_argument('--output', required=True)
    c=sub.add_parser('capability'); c.add_argument('--values', required=True); c.add_argument('--lsl', type=float, required=True); c.add_argument('--usl', type=float, required=True); c.add_argument('--output', required=True)
    a=p.parse_args()
    try:
        if a.command=='individuals': res=individuals_chart(parse_number_list(a.values))
        elif a.command=='xbar-r': res=xbar_r_chart(parse_groups(a.subgroups))
        else: res=capability(parse_number_list(a.values), lsl=a.lsl, usl=a.usl)
        path=write_json(result_envelope(skill='statistical-process-control', inputs=vars(a), results=res, assumptions=['Preliminary SPC calculation; verify rational subgrouping and measurement system.']), a.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='statistical-process-control', inputs=vars(a), results={'error':str(e)}, ok=False), a.output); print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())

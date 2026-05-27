#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations
import argparse, sys
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.io import parse_key_value_numbers, result_envelope, write_json

def main() -> int:
    p=argparse.ArgumentParser(description="Simple material-balance helpers")
    sub=p.add_subparsers(dest='command', required=True)
    c=sub.add_parser('component-total'); c.add_argument('--stream', action='append', required=True, help='NAME=amount, repeated'); c.add_argument('--output', required=True)
    y=sub.add_parser('reaction-metrics'); y.add_argument('--feed-limiting', type=float, required=True); y.add_argument('--reacted-limiting', type=float, required=True); y.add_argument('--desired-product', type=float, required=True); y.add_argument('--theoretical-product', type=float, required=True); y.add_argument('--output', required=True)
    args=p.parse_args()
    try:
        if args.command=='component-total':
            comps=parse_key_value_numbers(args.stream); res={'components': comps, 'total': sum(comps.values())}
            assumptions=['All stream entries are on the same basis and units.']
        else:
            conv=args.reacted_limiting/args.feed_limiting; yld=args.desired_product/args.theoretical_product
            res={'conversion_fraction': conv, 'yield_fraction': yld}; assumptions=['Stoichiometric theoretical product amount was supplied by user.']
        path=write_json(result_envelope(skill='material_energy_balances', inputs=vars(args), results=res, assumptions=assumptions), args.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='material_energy_balances', inputs=vars(args), results={'error':str(e)}, ok=False), args.output); print(f'Error. JSON written to: {args.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())

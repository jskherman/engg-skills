#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations
import argparse, sys
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.io import result_envelope, write_json

def main():
    p=argparse.ArgumentParser(description='Water/steam property helper using optional iapws package')
    p.add_argument('--temperature-c', type=float); p.add_argument('--pressure-mpa', type=float); p.add_argument('--quality', type=float); p.add_argument('--output', required=True)
    a=p.parse_args()
    try:
        try:
            from iapws import IAPWS97
        except Exception as e:
            raise RuntimeError('Optional package iapws is not installed. Run with a script dependency or install iapws before requesting steam properties.') from e
        kwargs={}
        if a.temperature_c is not None: kwargs['T']=a.temperature_c+273.15
        if a.pressure_mpa is not None: kwargs['P']=a.pressure_mpa
        if a.quality is not None: kwargs['x']=a.quality
        state=IAPWS97(**kwargs)
        res={'temperature_k':state.T,'pressure_mpa':state.P,'specific_volume_m3_kg':state.v,'enthalpy_kj_kg':state.h,'entropy_kj_kg_k':state.s,'phase':getattr(state,'phase',None)}
        path=write_json(result_envelope(skill='steam_tables_iapws', inputs=vars(a), results=res, sources=['IAPWS-IF97 via optional Python iapws package']), a.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='steam_tables_iapws', inputs=vars(a), results={'error':str(e)}, ok=False, warnings=['Do not invent steam properties; install/enable a validated property package or provide trusted data.']), a.output); print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())

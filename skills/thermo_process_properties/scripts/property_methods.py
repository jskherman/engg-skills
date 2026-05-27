#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["thermo>=0.6", "chemicals>=1.5", "fluids>=1.3", "ht>=1.2"]
# ///
from __future__ import annotations
import argparse, sys
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.io import parse_number_list, result_envelope, write_json
from engg_skills_common.property_backends import (costald_liquid_density, get_lpg_constants, iapws95_state, iapws_saturation, pr_translated_lpg_eos, recommend_property_method)

def comps(text): return [c.strip() for c in text.split(',') if c.strip()]
def constants_from_components(names): return get_lpg_constants(comps(names))

def main():
    p=argparse.ArgumentParser(description="Thermo/chemicals process-property helper")
    sub=p.add_subparsers(dest='command', required=True)
    r=sub.add_parser('recommend'); r.add_argument('--components', required=True); r.add_argument('--application', default='general'); r.add_argument('--pressure-pa', type=float); r.add_argument('--output', required=True)
    c=sub.add_parser('costald-density'); c.add_argument('--components', required=True); c.add_argument('--zs', required=True); c.add_argument('--temperature-k', type=float, required=True); c.add_argument('--pressure-pa', type=float); c.add_argument('--output', required=True)
    s=sub.add_parser('iapws-state'); s.add_argument('--temperature-k', type=float, required=True); s.add_argument('--pressure-pa', type=float, required=True); s.add_argument('--output', required=True)
    sat=sub.add_parser('iapws-saturation'); sat.add_argument('--temperature-k', type=float); sat.add_argument('--pressure-pa', type=float); sat.add_argument('--output', required=True)
    e=sub.add_parser('pr-translated-eos'); e.add_argument('--components', required=True); e.add_argument('--zs', required=True); e.add_argument('--temperature-k', type=float, required=True); e.add_argument('--pressure-pa', type=float, required=True); e.add_argument('--output', required=True)
    a=p.parse_args()
    try:
        warnings=[]; sources=[]
        if a.command=='recommend':
            res=recommend_property_method(components=comps(a.components), application=a.application, pressure_pa=a.pressure_pa)
        elif a.command=='costald-density':
            const=constants_from_components(a.components); res=costald_liquid_density(T=a.temperature_k, P=a.pressure_pa, zs=parse_number_list(a.zs), Tcs=const['Tcs'], Vcs=const['Vcs'], omegas=const['omegas'], MWs=const['MWs']); warnings=res.pop('warnings', []); sources=['chemicals.volume.COSTALD_mixture', 'chemicals.volume.COSTALD_mixture_compressed']
        elif a.command=='iapws-state':
            res=iapws95_state(T=a.temperature_k, P=a.pressure_pa); warnings=res.pop('warnings', []); sources=['chemicals.iapws.iapws95_properties']
        elif a.command=='iapws-saturation':
            res=iapws_saturation(T=a.temperature_k, P=a.pressure_pa); sources=['chemicals.iapws.Psat_IAPWS', 'chemicals.iapws.Tsat_IAPWS']
        else:
            const=constants_from_components(a.components); res=pr_translated_lpg_eos(T=a.temperature_k, P=a.pressure_pa, zs=parse_number_list(a.zs), Tcs=const['Tcs'], Pcs=const['Pcs'], omegas=const['omegas']); warnings=res.pop('warnings', []); sources=['thermo.eos_mix.PRMIXTranslatedPPJP']
        data=result_envelope(skill='thermo_process_properties', inputs=vars(a), results=res, warnings=warnings, sources=sources)
        path=write_json(data, a.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as exc:
        write_json(result_envelope(skill='thermo_process_properties', inputs=vars(a), results={'error':str(exc)}, ok=False), a.output); print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())

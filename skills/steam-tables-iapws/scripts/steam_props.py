#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["chemicals>=1.5"]
# ///
"""Water/steam properties using chemicals.iapws IAPWS-95 utilities."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification
from engg_skills_common.property_backends import iapws95_state, iapws_saturation

SKILL = "steam-tables-iapws"
SKILL_DIR = Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description='Water/steam property helper using chemicals.iapws')
    p.add_argument('--temperature-c', type=float, help='Temperature in degC for state calculation')
    p.add_argument('--temperature-k', type=float, help='Temperature in K for state or saturation calculation')
    p.add_argument('--pressure-mpa', type=float, help='Pressure in MPa for state calculation')
    p.add_argument('--pressure-pa', type=float, help='Pressure in Pa for state or saturation calculation')
    p.add_argument('--saturation', action='store_true', help='Calculate Psat from T or Tsat from P')
    p.add_argument('--output', required=True)
    a=p.parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://iapws.org/", "https://chemicals.readthedocs.io/chemicals.iapws.html"],
        library_attributions=["chemicals (Caleb Bell) — MIT"],
        extra_notes="Pure-water/steam properties only; do not apply to mixed water-hydrocarbon or saline systems.",
    )
    try:
        T = a.temperature_k if a.temperature_k is not None else (a.temperature_c + 273.15 if a.temperature_c is not None else None)
        P = a.pressure_pa if a.pressure_pa is not None else (a.pressure_mpa*1e6 if a.pressure_mpa is not None else None)
        if a.saturation:
            res=iapws_saturation(T=T, P=P)
            sources=['chemicals.iapws.Psat_IAPWS', 'chemicals.iapws.Tsat_IAPWS']
        else:
            if T is None or P is None:
                raise ValueError('state calculation requires temperature and pressure')
            res=iapws95_state(T=T, P=P)
            res['pressure_mpa']=P/1e6
            res['enthalpy_kj_kg']=res['enthalpy_j_kg']/1000.0
            res['entropy_kj_kg_k']=res['entropy_j_kg_k']/1000.0
            sources=['chemicals.iapws.iapws95_properties']
        warnings=res.pop('warnings', []) if isinstance(res, dict) else []
        data=result_envelope(skill=SKILL, inputs=vars(a), results=res, warnings=warnings, sources=sources)
        data["source_notice"] = license_notice_for(SKILL)
        path=write_json(data, a.output)
        print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='steam-tables-iapws', inputs=vars(a), results={'error':str(e)}, ok=False, warnings=['Do not invent steam properties; use validated IAPWS methods or provide trusted data.']), a.output)
        print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())

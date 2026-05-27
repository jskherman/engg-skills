"""Heat-transfer helpers, using Caleb Bell's ht library when available."""
from __future__ import annotations
import math
from typing import Any

def lmtd(delta_t1: float, delta_t2: float) -> float:
    if delta_t1 <= 0 or delta_t2 <= 0: raise ValueError("terminal temperature differences must be positive")
    if math.isclose(delta_t1, delta_t2): return delta_t1
    return (delta_t1-delta_t2)/math.log(delta_t1/delta_t2)

def terminal_differences(*, hot_in: float, hot_out: float, cold_in: float, cold_out: float, arrangement: str) -> tuple[float,float]:
    if arrangement == "counterflow": return hot_in-cold_out, hot_out-cold_in
    if arrangement == "parallel": return hot_in-cold_in, hot_out-cold_out
    raise ValueError("arrangement must be 'counterflow' or 'parallel'")

def exchanger_area(*, duty_w: float, overall_u_w_m2_k: float, lmtd_k: float, correction_factor: float=1.0) -> float:
    if overall_u_w_m2_k <= 0 or lmtd_k <= 0 or correction_factor <= 0: raise ValueError("U, LMTD, and correction factor must be positive")
    return abs(duty_w)/(overall_u_w_m2_k*correction_factor*lmtd_k)

def sensible_heat_duty(*, mass_flow_kg_s: float, cp_j_kg_k: float, inlet: float, outlet: float) -> float:
    if mass_flow_kg_s <= 0 or cp_j_kg_k <= 0: raise ValueError("mass_flow_kg_s and cp_j_kg_k must be positive")
    return mass_flow_kg_s*cp_j_kg_k*(outlet-inlet)

def lmtd_sizing(*, hot_in: float, hot_out: float, cold_in: float, cold_out: float, arrangement: str, overall_u_w_m2_k: float, correction_factor: float=1.0, duty_w: float|None=None, hot_mass_flow_kg_s: float|None=None, hot_cp_j_kg_k: float|None=None, cold_mass_flow_kg_s: float|None=None, cold_cp_j_kg_k: float|None=None) -> dict[str, Any]:
    dt1, dt2 = terminal_differences(hot_in=hot_in, hot_out=hot_out, cold_in=cold_in, cold_out=cold_out, arrangement=arrangement)
    warnings=[]
    try:
        from ht import LMTD
        value_lmtd=LMTD(Thi=hot_in, Tho=hot_out, Tci=cold_in, Tco=cold_out, counterflow=(arrangement=='counterflow'))
        lmtd_method='ht.LMTD'
    except Exception:
        value_lmtd=lmtd(dt1,dt2); lmtd_method='local LMTD fallback'
    calculated_duties={}
    if hot_mass_flow_kg_s is not None and hot_cp_j_kg_k is not None:
        calculated_duties['hot_side_w']=-sensible_heat_duty(mass_flow_kg_s=hot_mass_flow_kg_s, cp_j_kg_k=hot_cp_j_kg_k, inlet=hot_in, outlet=hot_out)
    if cold_mass_flow_kg_s is not None and cold_cp_j_kg_k is not None:
        calculated_duties['cold_side_w']=sensible_heat_duty(mass_flow_kg_s=cold_mass_flow_kg_s, cp_j_kg_k=cold_cp_j_kg_k, inlet=cold_in, outlet=cold_out)
    if duty_w is None:
        if calculated_duties:
            duty_w=sum(calculated_duties.values())/len(calculated_duties)
            if len(calculated_duties)==2 and abs(calculated_duties['hot_side_w']-calculated_duties['cold_side_w'])/max(abs(calculated_duties['hot_side_w']),abs(calculated_duties['cold_side_w']),1.0)>0.05: warnings.append('Hot- and cold-side calculated duties differ by more than 5%.')
        else: raise ValueError('provide duty_w or enough stream data to compute duty')
    return {"delta_t1_k":dt1,"delta_t2_k":dt2,"lmtd_k":value_lmtd,"lmtd_method":lmtd_method,"duty_w":duty_w,"calculated_duties_w":calculated_duties,"area_m2":exchanger_area(duty_w=duty_w, overall_u_w_m2_k=overall_u_w_m2_k, lmtd_k=value_lmtd, correction_factor=correction_factor),"warnings":warnings}

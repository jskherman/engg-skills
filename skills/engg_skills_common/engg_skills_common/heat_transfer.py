"""Heat-transfer helpers."""

from __future__ import annotations

import math
from typing import Any


def lmtd(delta_t1: float, delta_t2: float) -> float:
    """Return log-mean temperature difference."""

    if delta_t1 <= 0 or delta_t2 <= 0:
        raise ValueError("terminal temperature differences must be positive")
    if math.isclose(delta_t1, delta_t2, rel_tol=1.0e-12, abs_tol=1.0e-12):
        return (delta_t1 + delta_t2) / 2.0
    return (delta_t1 - delta_t2) / math.log(delta_t1 / delta_t2)


def terminal_differences(
    *,
    hot_in: float,
    hot_out: float,
    cold_in: float,
    cold_out: float,
    arrangement: str,
) -> tuple[float, float]:
    """Return exchanger terminal temperature differences in C or K deltas."""

    if arrangement == "counterflow":
        return hot_in - cold_out, hot_out - cold_in
    if arrangement == "parallel":
        return hot_in - cold_in, hot_out - cold_out
    raise ValueError("arrangement must be counterflow or parallel")


def exchanger_area(
    *,
    duty_w: float,
    overall_u_w_m2_k: float,
    lmtd_k: float,
    correction_factor: float = 1.0,
) -> float:
    """Return area from Q = U A F LMTD."""

    if overall_u_w_m2_k <= 0:
        raise ValueError("overall_u_w_m2_k must be positive")
    if lmtd_k <= 0:
        raise ValueError("lmtd_k must be positive")
    if correction_factor <= 0 or correction_factor > 1.0:
        raise ValueError("correction_factor must be in (0, 1]")
    return abs(duty_w) / (overall_u_w_m2_k * correction_factor * lmtd_k)


def sensible_heat_duty(*, mass_flow_kg_s: float, cp_j_kg_k: float, inlet: float, outlet: float) -> float:
    """Return signed sensible duty m cp (outlet - inlet)."""

    if mass_flow_kg_s <= 0 or cp_j_kg_k <= 0:
        raise ValueError("mass_flow_kg_s and cp_j_kg_k must be positive")
    return mass_flow_kg_s * cp_j_kg_k * (outlet - inlet)


def lmtd_sizing(
    *,
    hot_in: float,
    hot_out: float,
    cold_in: float,
    cold_out: float,
    arrangement: str,
    overall_u_w_m2_k: float,
    correction_factor: float = 1.0,
    duty_w: float | None = None,
    hot_mass_flow_kg_s: float | None = None,
    hot_cp_j_kg_k: float | None = None,
    cold_mass_flow_kg_s: float | None = None,
    cold_cp_j_kg_k: float | None = None,
) -> dict[str, Any]:
    """Return LMTD and area estimate from supplied stream temperatures."""

    dt1, dt2 = terminal_differences(
        hot_in=hot_in,
        hot_out=hot_out,
        cold_in=cold_in,
        cold_out=cold_out,
        arrangement=arrangement,
    )
    value_lmtd = lmtd(dt1, dt2)
    warnings: list[str] = []
    calculated_duties: dict[str, float] = {}
    if hot_mass_flow_kg_s is not None and hot_cp_j_kg_k is not None:
        calculated_duties["hot_side_w"] = -sensible_heat_duty(
            mass_flow_kg_s=hot_mass_flow_kg_s,
            cp_j_kg_k=hot_cp_j_kg_k,
            inlet=hot_in,
            outlet=hot_out,
        )
    if cold_mass_flow_kg_s is not None and cold_cp_j_kg_k is not None:
        calculated_duties["cold_side_w"] = sensible_heat_duty(
            mass_flow_kg_s=cold_mass_flow_kg_s,
            cp_j_kg_k=cold_cp_j_kg_k,
            inlet=cold_in,
            outlet=cold_out,
        )
    if duty_w is None:
        if calculated_duties:
            duty_w = sum(calculated_duties.values()) / len(calculated_duties)
            if len(calculated_duties) == 2:
                hot_q = calculated_duties["hot_side_w"]
                cold_q = calculated_duties["cold_side_w"]
                if abs(hot_q - cold_q) / max(abs(hot_q), abs(cold_q), 1.0) > 0.05:
                    warnings.append("Hot- and cold-side calculated duties differ by more than 5%.")
        else:
            raise ValueError("provide duty_w or enough stream data to compute duty")
    area = exchanger_area(
        duty_w=duty_w,
        overall_u_w_m2_k=overall_u_w_m2_k,
        lmtd_k=value_lmtd,
        correction_factor=correction_factor,
    )
    return {
        "delta_t1_k": dt1,
        "delta_t2_k": dt2,
        "lmtd_k": value_lmtd,
        "duty_w": duty_w,
        "calculated_duties_w": calculated_duties,
        "area_m2": area,
        "warnings": warnings,
    }

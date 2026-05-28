"""Simple material and energy balance residual helpers."""

from __future__ import annotations

from typing import Any


def balance_residuals(
    *,
    inlet_components: list[dict[str, float]],
    outlet_components: list[dict[str, float]],
    energy_in: list[float] | None = None,
    energy_out: list[float] | None = None,
) -> dict[str, Any]:
    """Return component and energy residuals using in minus out convention."""

    components = sorted(
        {
            component
            for stream in [*inlet_components, *outlet_components]
            for component in stream
        }
    )
    component_residuals: dict[str, float] = {}
    for component in components:
        inlet = sum(stream.get(component, 0.0) for stream in inlet_components)
        outlet = sum(stream.get(component, 0.0) for stream in outlet_components)
        component_residuals[component] = inlet - outlet
    total_in = sum(sum(stream.values()) for stream in inlet_components)
    total_out = sum(sum(stream.values()) for stream in outlet_components)
    result: dict[str, Any] = {
        "component_residuals_in_minus_out": component_residuals,
        "total_material_in": total_in,
        "total_material_out": total_out,
        "total_material_residual_in_minus_out": total_in - total_out,
    }
    if energy_in is not None or energy_out is not None:
        result["energy_in"] = sum(energy_in or [])
        result["energy_out"] = sum(energy_out or [])
        result["energy_residual_in_minus_out"] = result["energy_in"] - result["energy_out"]
    return result

"""I/O helpers for Engineering Skills scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .notices import PRELIMINARY_ENGINEERING_WARNING, SOURCE_NOTICE


def result_envelope(
    *,
    skill: str,
    inputs: dict[str, Any],
    results: dict[str, Any],
    assumptions: list[str] | None = None,
    warnings: list[str] | None = None,
    sources: list[str] | None = None,
    ok: bool = True,
) -> dict[str, Any]:
    """Return the standard JSON structure used by deterministic scripts."""

    merged_warnings = [PRELIMINARY_ENGINEERING_WARNING]
    if warnings:
        merged_warnings.extend(warnings)
    return {
        "ok": ok,
        "skill": skill,
        "inputs": inputs,
        "results": results,
        "assumptions": assumptions or [],
        "warnings": merged_warnings,
        "source_notice": SOURCE_NOTICE,
        "sources": sources or [],
    }


def write_json(data: dict[str, Any], output: str | Path) -> Path:
    """Write JSON to output and return the path."""

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def parse_number_list(text: str) -> list[float]:
    """Parse comma-, semicolon-, or whitespace-separated numbers."""

    values = [float(chunk) for chunk in re.split(r"[\s,;]+", text.strip()) if chunk]
    if not values:
        raise ValueError("expected at least one numeric value")
    return values


def parse_key_value_numbers(items: list[str]) -> dict[str, float]:
    """Parse repeated KEY=VALUE strings into a numeric dictionary."""

    parsed: dict[str, float] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"expected KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"empty key in {item!r}")
        parsed[key] = parsed.get(key, 0.0) + float(value)
    return parsed

"""Design-of-experiments helpers."""

from __future__ import annotations

import itertools
import random
from typing import Any


def full_factorial(
    factors: dict[str, list[str]],
    *,
    replicates: int = 1,
    randomize: bool = False,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    if not factors:
        raise ValueError("at least one factor is required")
    if replicates < 1:
        raise ValueError("replicates must be at least 1")
    names = list(factors)
    for name, levels in factors.items():
        if not name.strip():
            raise ValueError("factor names cannot be empty")
        if len(levels) < 2:
            raise ValueError(f"factor {name!r} needs at least two levels")
    base_rows = [dict(zip(names, combo, strict=True)) for combo in itertools.product(*(factors[name] for name in names))]
    rows: list[dict[str, Any]] = []
    run_number = 1
    for rep in range(1, replicates + 1):
        for row in base_rows:
            rows.append({"run": run_number, "replicate": rep, **row})
            run_number += 1
    if randomize:
        rng = random.Random(seed)
        rng.shuffle(rows)
        for index, row in enumerate(rows, start=1):
            row["run_order"] = index
    else:
        for row in rows:
            row["run_order"] = row["run"]
    return rows


def two_level_factorial(
    factor_names: list[str],
    *,
    low_label: str = "-1",
    high_label: str = "+1",
    randomize: bool = False,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    if not factor_names:
        raise ValueError("at least one factor is required")
    factors = {name: [low_label, high_label] for name in factor_names}
    return full_factorial(factors, randomize=randomize, seed=seed)

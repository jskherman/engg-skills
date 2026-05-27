#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Process engineering unit conversion CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.units import available_units, convert


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert process engineering units and write JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert a value between compatible units.")
    convert_parser.add_argument("--value", type=float, required=True)
    convert_parser.add_argument("--from-unit", required=True)
    convert_parser.add_argument("--to-unit", required=True)
    convert_parser.add_argument("--output", required=True)

    list_parser = subparsers.add_parser("list-units", help="List supported units grouped by dimension.")
    list_parser.add_argument("--output", required=True)
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "convert":
        results = convert(args.value, args.from_unit, args.to_unit)
        return result_envelope(
            skill="process_units_conversion",
            inputs={"value": args.value, "from_unit": args.from_unit, "to_unit": args.to_unit},
            results=results,
            assumptions=["Temperature units represent absolute temperatures, not temperature intervals."],
        )
    if args.command == "list-units":
        return result_envelope(
            skill="process_units_conversion",
            inputs={},
            results={"available_units": available_units()},
            assumptions=["Only units registered in the local conversion registry are listed."],
        )
    raise ValueError(f"unknown command {args.command!r}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        data = run(args)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        data = result_envelope(
            skill="process_units_conversion",
            inputs=vars(args),
            results={"error": str(exc)},
            warnings=["Conversion failed; check unit spelling and dimensional compatibility."],
            ok=False,
        )
        write_json(data, args.output)
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

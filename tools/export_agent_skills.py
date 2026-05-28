#!/usr/bin/env python3
"""Export source skills to an Agent Skills-compatible directory tree.

The source tree is already compatible with Hermes Agent and the Agent Skills
specification: each top-level skill directory is a lowercase hyphen slug and
matches the `name` field in `SKILL.md`. This helper copies that tree to
`dist/agent-skills` for packaging or local installation checks.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "skills"
DEFAULT_OUTPUT = ROOT / "dist" / "agent-skills"
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def _frontmatter_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{skill_md}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{skill_md}: unterminated YAML frontmatter")
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
            if not SLUG_RE.match(name) or "--" in name:
                raise ValueError(f"{skill_md}: invalid Agent Skills name {name!r}")
            return name
    raise ValueError(f"{skill_md}: missing required name field")


def _copy_skill(source_dir: Path, output_root: Path) -> str:
    skill_md = source_dir / "SKILL.md"
    if not skill_md.exists():
        raise ValueError(f"{source_dir}: missing SKILL.md")

    name = _frontmatter_name(skill_md)
    if source_dir.name != name:
        raise ValueError(f"{skill_md}: parent directory {source_dir.name!r} must match name {name!r}")

    dest = output_root / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        source_dir,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "*.egg-info", "LICENSE_NOTIFICATION.txt"),
    )
    return name


def export_skills(source_root: Path, output_root: Path) -> list[str]:
    if not source_root.exists():
        raise FileNotFoundError(source_root)
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    exported: list[str] = []
    for source_dir in sorted(p for p in source_root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        exported.append(_copy_skill(source_dir, output_root))
    return exported


def main() -> int:
    parser = argparse.ArgumentParser(description="Export source skills to an Agent Skills-compatible tree")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source skills directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Generated Agent Skills output directory")
    args = parser.parse_args()

    exported = export_skills(args.source, args.output)
    label = args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output
    print(f"Exported {len(exported)} skills to {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

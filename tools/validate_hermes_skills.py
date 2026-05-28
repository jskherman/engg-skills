#!/usr/bin/env python3
"""Validate Hermes SKILL.md frontmatter and required sections.

Based on the Hermes Skills System docs:
https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

Checks intentionally stay local and lightweight so the repo can verify skills
without importing the skill scripts or installing heavy process-engineering deps.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - local tooling guard
    raise SystemExit("PyYAML is required: uv add --dev pyyaml or pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
REQUIRED_SECTIONS = ("## When to Use", "## Procedure", "## Pitfalls", "## Verification")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


def _frontmatter(text: str, path: Path) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter block")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML frontmatter block")
    raw = text[4:end]
    body = text[end + 5 :]
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a YAML mapping")
    return data, body


def _validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        fm, body = _frontmatter(text, path)
    except ValueError as exc:
        return [str(exc)]

    name = fm.get("name")
    if not isinstance(name, str) or not SLUG_RE.match(name):
        errors.append(f"{path}: frontmatter.name must be a lowercase hyphen slug")
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{path}: frontmatter.description is required")
    if len(desc.strip()) > 600:
        errors.append(f"{path}: description is too long for Level-0 skill discovery")
    version = fm.get("version")
    if not isinstance(version, str) or not re.match(r"^\d+\.\d+\.\d+$", version):
        errors.append(f"{path}: frontmatter.version must be semver-like, e.g. 1.0.0")

    metadata = fm.get("metadata")
    hermes = metadata.get("hermes") if isinstance(metadata, dict) else None
    if not isinstance(hermes, dict):
        errors.append(f"{path}: metadata.hermes mapping is required")
    else:
        tags = hermes.get("tags")
        if not isinstance(tags, list) or not tags or not all(isinstance(t, str) and t for t in tags):
            errors.append(f"{path}: metadata.hermes.tags must be a non-empty string list")
        category = hermes.get("category")
        if not isinstance(category, str) or not category:
            errors.append(f"{path}: metadata.hermes.category is required")

    if not re.search(r"^#\s+\S", body, flags=re.MULTILINE):
        errors.append(f"{path}: body must start with a top-level # title")
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"{path}: missing required section {section!r}")
    return errors


def main() -> int:
    paths = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    errors: list[str] = []
    for path in paths:
        errors.extend(_validate_skill(path.relative_to(ROOT)))
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        print(f"{len(errors)} Hermes skill-format errors across {len(paths)} skills", file=sys.stderr)
        return 1
    print(f"Validated {len(paths)} Hermes skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

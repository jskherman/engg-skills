#!/usr/bin/env python3
"""Validate Hermes and AgentSkills-compatible SKILL.md files.

Sources:
- Hermes Skills System docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Agent Skills specification: https://agentskills.io/specification

Default behavior validates the generated compatibility tree at
`dist/agent-skills` when it exists; otherwise it validates the source `skills`
tree. Use `--strict-directory-match` when validating the exported tree because
AgentSkills requires the parent directory to match the frontmatter `name`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - local tooling guard
    raise SystemExit("PyYAML is required: uv add --dev pyyaml or pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILLS_DIR = ROOT / "skills"
EXPORTED_SKILLS_DIR = ROOT / "dist" / "agent-skills"
REQUIRED_HERMES_SECTIONS = ("## When to Use", "## Procedure", "## Pitfalls", "## Verification")
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "version",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
    "allowed_tools",
    "platforms",
}


def _frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
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


def _validate_agent_skills_frontmatter(
    path: Path,
    fm: dict[str, Any],
    *,
    strict_directory_match: bool,
    allow_extra_frontmatter: bool,
) -> list[str]:
    errors: list[str] = []
    name = fm.get("name")
    if not isinstance(name, str) or not SLUG_RE.match(name) or "--" in name:
        errors.append(f"{path}: frontmatter.name must be a lowercase hyphen slug of <=64 chars")
    elif strict_directory_match and path.parent.name != name:
        errors.append(f"{path}: AgentSkills requires parent directory {path.parent.name!r} to match name {name!r}")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{path}: frontmatter.description is required")
    elif len(desc.strip()) > 1000:
        errors.append(f"{path}: description is too long for reliable skill discovery")

    version = fm.get("version")
    if version is not None and (not isinstance(version, str) or not re.match(r"^\d+\.\d+\.\d+$", version)):
        errors.append(f"{path}: frontmatter.version should be semver-like, e.g. 1.0.0")

    allowed_tools = fm.get("allowed-tools", fm.get("allowed_tools"))
    if allowed_tools is not None and not (isinstance(allowed_tools, list) and all(isinstance(t, str) for t in allowed_tools)):
        errors.append(f"{path}: allowed-tools must be a string list when present")

    platforms = fm.get("platforms")
    if platforms is not None and not (isinstance(platforms, list) and all(isinstance(p, str) for p in platforms)):
        errors.append(f"{path}: platforms must be a string list when present")

    if not allow_extra_frontmatter:
        extra = set(fm) - ALLOWED_FRONTMATTER_KEYS
        if extra:
            errors.append(f"{path}: non-standard frontmatter keys present: {sorted(extra)}")
    return errors


def _validate_hermes_metadata(path: Path, fm: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = fm.get("metadata")
    hermes = metadata.get("hermes") if isinstance(metadata, dict) else None
    if not isinstance(hermes, dict):
        errors.append(f"{path}: metadata.hermes mapping is required for Hermes compatibility")
        return errors

    tags = hermes.get("tags")
    if not isinstance(tags, list) or not tags or not all(isinstance(t, str) and t for t in tags):
        errors.append(f"{path}: metadata.hermes.tags must be a non-empty string list")
    category = hermes.get("category")
    if not isinstance(category, str) or not category:
        errors.append(f"{path}: metadata.hermes.category is required")
    return errors


def _validate_body(path: Path, body: str, *, hermes_sections: bool) -> list[str]:
    errors: list[str] = []
    if not re.search(r"^#\s+\S", body, flags=re.MULTILINE):
        errors.append(f"{path}: body must contain a top-level # title")
    if hermes_sections:
        for section in REQUIRED_HERMES_SECTIONS:
            if section not in body:
                errors.append(f"{path}: missing Hermes section {section!r}")
    return errors


def _validate_skill(path: Path, *, strict_directory_match: bool, hermes_sections: bool, allow_extra_frontmatter: bool) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        fm, body = _frontmatter(text, path)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    errors.extend(
        _validate_agent_skills_frontmatter(
            path,
            fm,
            strict_directory_match=strict_directory_match,
            allow_extra_frontmatter=allow_extra_frontmatter,
        )
    )
    errors.extend(_validate_hermes_metadata(path, fm))
    errors.extend(_validate_body(path, body, hermes_sections=hermes_sections))
    return errors


def _default_skills_dir() -> Path:
    return EXPORTED_SKILLS_DIR if EXPORTED_SKILLS_DIR.exists() else SOURCE_SKILLS_DIR


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Hermes / AgentSkills SKILL.md files")
    parser.add_argument("skills_dir", nargs="?", type=Path, default=_default_skills_dir())
    parser.add_argument("--strict-directory-match", action="store_true", help="Require parent folder name to match frontmatter.name")
    parser.add_argument("--no-hermes-sections", action="store_true", help="Do not require Hermes body sections")
    parser.add_argument("--no-extra-frontmatter", action="store_true", help="Reject frontmatter keys outside the AgentSkills-compatible set")
    args = parser.parse_args()

    skills_dir = args.skills_dir
    paths = sorted(skills_dir.glob("*/SKILL.md"))
    if not paths:
        print(f"No SKILL.md files found under {skills_dir}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in paths:
        errors.extend(
            _validate_skill(
                path,
                strict_directory_match=args.strict_directory_match,
                hermes_sections=not args.no_hermes_sections,
                allow_extra_frontmatter=not args.no_extra_frontmatter,
            )
        )
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        print(f"{len(errors)} skill-format errors across {len(paths)} skills", file=sys.stderr)
        return 1
    label = skills_dir.relative_to(ROOT) if skills_dir.is_relative_to(ROOT) else skills_dir
    print(f"Validated {len(paths)} skills under {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

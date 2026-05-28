#!/usr/bin/env python3
"""Validate Hermes and Agent Skills-compatible SKILL.md files.

Sources:
- Hermes Skills System docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Agent Skills specification: https://agentskills.io/specification
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

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
    "platforms",
    "required_environment_variables",
}


def _frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter block")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML frontmatter block")
    raw = text[4:end]
    body = text[end + 5 :]
    return _parse_frontmatter(raw, path), body


def _parse_frontmatter(raw: str, path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith(" "):
            raise ValueError(f"{path}: unexpected indented top-level frontmatter line {line!r}")
        if ":" not in line:
            raise ValueError(f"{path}: invalid frontmatter line {line!r}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == ">-":
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                block.append(lines[i])
                i += 1
            data[key] = _fold_block(block)
            continue
        if value == "":
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                block.append(lines[i])
                i += 1
            data[key] = _parse_nested_mapping(block, path)
            continue
        data[key] = _parse_value(value)
        i += 1
    return data


def _fold_block(lines: list[str]) -> str:
    chunks = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            chunks.append(stripped)
    return " ".join(chunks)


def _parse_nested_mapping(lines: list[str], path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line in lines:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            raise ValueError(f"{path}: invalid nested frontmatter line {line!r}")
        key, raw_value = stripped.split(":", 1)
        value = raw_value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"{path}: invalid frontmatter indentation near {line!r}")
        parent = stack[-1][1]
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_value(value)
    return root


def _parse_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_unquote(part.strip()) for part in inner.split(",")]
    return _unquote(value)


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


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
        errors.append(f"{path}: Agent Skills requires parent directory {path.parent.name!r} to match name {name!r}")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{path}: frontmatter.description is required")
    elif len(desc.strip()) > 1024:
        errors.append(f"{path}: description must be <=1024 characters")

    version = fm.get("version")
    if version is not None and (not isinstance(version, str) or not re.match(r"^\d+\.\d+\.\d+$", version)):
        errors.append(f"{path}: frontmatter.version should be semver-like, e.g. 1.0.0")

    license_name = fm.get("license")
    if license_name is not None and not isinstance(license_name, str):
        errors.append(f"{path}: frontmatter.license must be a string when present")

    compatibility = fm.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str) or not compatibility.strip():
            errors.append(f"{path}: frontmatter.compatibility must be a non-empty string when present")
        elif len(compatibility.strip()) > 500:
            errors.append(f"{path}: frontmatter.compatibility must be <=500 characters")

    allowed_tools = fm.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        errors.append(f"{path}: allowed-tools must be a space-separated string when present")

    platforms = fm.get("platforms")
    if platforms is not None and not (isinstance(platforms, list) and all(isinstance(p, str) for p in platforms)):
        errors.append(f"{path}: platforms must be a string list when present")

    metadata = fm.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        errors.append(f"{path}: metadata must be a mapping when present")

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
    parser = argparse.ArgumentParser(description="Validate Hermes / Agent Skills SKILL.md files")
    parser.add_argument("skills_dir", nargs="?", type=Path, default=_default_skills_dir())
    parser.add_argument("--strict-directory-match", action="store_true", help="Require parent folder name to match frontmatter.name")
    parser.add_argument("--no-hermes-sections", action="store_true", help="Do not require Hermes body sections")
    parser.add_argument("--no-extra-frontmatter", action="store_true", help="Reject frontmatter keys outside the Agent Skills-compatible set")
    args = parser.parse_args()

    paths = sorted(args.skills_dir.glob("*/SKILL.md"))
    if not paths:
        print(f"No SKILL.md files found under {args.skills_dir}", file=sys.stderr)
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
    label = args.skills_dir.relative_to(ROOT) if args.skills_dir.is_relative_to(ROOT) else args.skills_dir
    print(f"Validated {len(paths)} skills under {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

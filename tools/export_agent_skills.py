#!/usr/bin/env python3
"""Export source skills to an AgentSkills-compatible directory tree.

The repository keeps source skills under underscore-named directories because
script paths and imports historically used that layout. AgentSkills requires the
skill directory name to match the `name` frontmatter field, where `name` is a
lowercase hyphen slug. This exporter builds a generated tree with hyphen-named
skill directories without breaking the source layout.

Default output:
    dist/agent-skills/<skill-name>/SKILL.md

The exporter also copies the shared `engg_skills_common` Python package to
`dist/agent-skills/engg_skills_common/` so existing scripts that compute
`../../engg_skills_common` continue to import correctly from the exported tree.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "skills"
DEFAULT_OUTPUT = ROOT / "dist" / "agent-skills"
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
DEFAULT_COMPATIBILITY = "Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv are required for bundled Python scripts."
DEFAULT_VERSION = "1.0.0"
DEFAULT_CATEGORY = "process-engineering"
DEFAULT_TAGS = ["chemical-engineering", "process-engineering"]
SECTION_ALIASES = {
    "## Use when": "## When to Use",
    "## Use When": "## When to Use",
    "## Workflow": "## Procedure",
    "## Common Mistakes": "## Pitfalls",
}
REQUIRED_HERMES_SECTIONS = ("## When to Use", "## Procedure", "## Pitfalls", "## Verification")


def _frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    data = yaml.safe_load(text[4:end]) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return data, text[end + 5 :]


def _dump_frontmatter(data: dict[str, Any]) -> str:
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip() + "\n---\n\n"


def _slug_from_source_dir(path: Path) -> str:
    return path.name.replace("_", "-")


def _ensure_slug(value: str, path: Path) -> str:
    if not SLUG_RE.match(value) or "--" in value:
        raise ValueError(f"{path}: invalid skill name {value!r}; AgentSkills requires a lowercase hyphen slug <=64 chars")
    return value


def _infer_tags(name: str, source_dir: Path) -> list[str]:
    parts = [p for p in name.split("-") if p]
    tags = list(dict.fromkeys(DEFAULT_TAGS + parts[:4]))
    if source_dir.name in {"uv", "engineering_skill_creator", "engg_skills_common"}:
        tags = list(dict.fromkeys(["tooling", "skills"] + parts))
    return tags[:8]


def _normalize_frontmatter(fm: dict[str, Any], source_dir: Path) -> dict[str, Any]:
    name = str(fm.get("name") or _slug_from_source_dir(source_dir))
    name = _ensure_slug(name, source_dir / "SKILL.md")

    desc = str(fm.get("description") or "")
    if not desc.strip():
        raise ValueError(f"{source_dir / 'SKILL.md'}: description is required")

    out: dict[str, Any] = dict(fm)
    out["name"] = name
    out["description"] = desc.strip()
    out.setdefault("license", "Apache-2.0")
    out.setdefault("compatibility", DEFAULT_COMPATIBILITY)
    out.setdefault("version", DEFAULT_VERSION)

    metadata = out.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    hermes = metadata.get("hermes")
    if not isinstance(hermes, dict):
        hermes = {}
    hermes.setdefault("tags", _infer_tags(name, source_dir))
    hermes.setdefault("category", DEFAULT_CATEGORY)
    metadata["hermes"] = hermes
    out["metadata"] = metadata
    return out


def _normalize_sections(body: str) -> str:
    lines = body.splitlines()
    normalized: list[str] = []
    for line in lines:
        replacement = SECTION_ALIASES.get(line.strip())
        normalized.append(replacement if replacement else line)
    text = "\n".join(normalized).rstrip() + "\n"

    missing = [section for section in REQUIRED_HERMES_SECTIONS if section not in text]
    if not missing:
        return text

    additions: list[str] = []
    if "## When to Use" in missing:
        additions.extend([
            "## When to Use",
            "",
            "Use this skill when the task matches the frontmatter description and the examples in this SKILL.md.",
            "",
        ])
    if "## Procedure" in missing:
        additions.extend([
            "## Procedure",
            "",
            "1. Read this SKILL.md and any referenced files needed for the task.",
            "2. Use scripts from `scripts/` when a deterministic calculation or check is available.",
            "3. Write or inspect JSON outputs rather than relying only on stdout.",
            "4. Verify units, assumptions, warnings, and scope limits before reporting results.",
            "",
        ])
    if "## Pitfalls" in missing:
        additions.extend([
            "## Pitfalls",
            "",
            "- Do not treat screening calculations as final engineering design.",
            "- Do not ignore warnings, invalid-unit inputs, or missing dependency messages.",
            "",
        ])
    if "## Verification" in missing:
        additions.extend([
            "## Verification",
            "",
            "- Confirm that expected output files exist and contain `ok: true` where applicable.",
            "- Check result magnitudes against an independent hand calculation, reference example, or known operating range.",
            "- Confirm that warnings and assumptions are carried into the final answer.",
            "",
        ])

    insert_at = text.find("\n## References")
    block = "\n" + "\n".join(additions).rstrip() + "\n"
    if insert_at == -1:
        return text.rstrip() + block + "\n"
    return text[:insert_at].rstrip() + block + text[insert_at:]


def _copy_skill(source_dir: Path, output_root: Path) -> str:
    skill_md = source_dir / "SKILL.md"
    if not skill_md.exists():
        raise ValueError(f"{source_dir}: missing SKILL.md")
    fm, body = _frontmatter(skill_md.read_text(encoding="utf-8"), skill_md)
    fm = _normalize_frontmatter(fm, source_dir)
    name = fm["name"]

    dest = output_root / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source_dir, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "LICENSE_NOTIFICATION.txt"))
    (dest / "SKILL.md").write_text(_dump_frontmatter(fm) + _normalize_sections(body), encoding="utf-8")
    return name


def _copy_shared_python_package(source_root: Path, output_root: Path) -> None:
    shared_source = source_root / "engg_skills_common" / "engg_skills_common"
    if not shared_source.exists():
        return
    shared_dest_root = output_root / "engg_skills_common"
    if shared_dest_root.exists():
        shutil.rmtree(shared_dest_root)
    shared_dest_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(shared_source, shared_dest_root / "engg_skills_common", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def export_skills(source_root: Path, output_root: Path) -> list[str]:
    if not source_root.exists():
        raise FileNotFoundError(source_root)
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    exported: list[str] = []
    for source_dir in sorted(p for p in source_root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        exported.append(_copy_skill(source_dir, output_root))
    _copy_shared_python_package(source_root, output_root)
    return exported


def main() -> int:
    parser = argparse.ArgumentParser(description="Export source skills to an AgentSkills-compatible tree")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source skills directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Generated AgentSkills output directory")
    args = parser.parse_args()

    exported = export_skills(args.source, args.output)
    print(f"Exported {len(exported)} skills to {args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

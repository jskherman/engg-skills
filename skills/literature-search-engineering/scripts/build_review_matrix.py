#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a literature-review screening matrix from search-result JSON files.

Formula/reference note:
  Deduplication is deterministic: canonical DOI match first; otherwise a
  normalized-title/year key. This is an audit convenience only, not a proof
  that two records are identical. Manual conflict review remains required.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "literature-search-engineering"
SKILL_DIR = Path(__file__).resolve().parents[1]


def _normalise_doi(value: Any) -> str | None:
    if not value:
        return None
    text = str(value).strip().lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:", "", text)
    return text or None


def _normalise_title(value: Any) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _year(item: dict[str, Any]) -> Any:
    for key in ("year", "publication_year"):
        if item.get(key):
            return item.get(key)
    published = item.get("published") or item.get("date")
    if isinstance(published, str):
        match = re.search(r"\b(19|20)\d{2}\b", published)
        if match:
            return int(match.group(0))
    return None


def _authors(item: dict[str, Any]) -> str:
    authors = item.get("authors")
    if isinstance(authors, list):
        return "; ".join(str(author) for author in authors if author)
    if authors:
        return str(authors)
    return ""


def _stable_url(item: dict[str, Any]) -> str | None:
    return item.get("url") or item.get("landing_page_url") or item.get("openalex_id") or item.get("arxiv_id")


def _access_status(item: dict[str, Any]) -> str:
    if item.get("access_status"):
        return str(item["access_status"])
    if item.get("pdf_url"):
        return "open_access_pdf_candidate"
    if item.get("is_open_access") or item.get("is_oa"):
        return "open_access_metadata"
    return "metadata_only"


def _record_key(item: dict[str, Any]) -> tuple[str, str]:
    doi = _normalise_doi(item.get("doi"))
    if doi:
        return ("doi", doi)
    return ("title_year", f"{_normalise_title(item.get('title'))}|{_year(item) or ''}")


def _source_name(path: Path, envelope: dict[str, Any]) -> str:
    results = envelope.get("results") or {}
    query_url = results.get("query_url") or ""
    if "openalex" in query_url:
        return "OpenAlex"
    if "crossref" in query_url:
        return "Crossref"
    if "semanticscholar" in query_url:
        return "Semantic Scholar"
    if "arxiv" in query_url:
        return "arXiv"
    return path.stem


def _query(envelope: dict[str, Any]) -> str | None:
    inputs = envelope.get("inputs") or {}
    return inputs.get("query")


def _rows_from_file(path: Path) -> list[dict[str, Any]]:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    source = _source_name(path, envelope)
    query = _query(envelope)
    items = (envelope.get("results") or {}).get("items") or []
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "source_database": source,
                "query": query,
                "title": item.get("title"),
                "authors": _authors(item),
                "year": _year(item),
                "doi": _normalise_doi(item.get("doi")),
                "stable_url": _stable_url(item),
                "pdf_url": item.get("pdf_url"),
                "access_status": _access_status(item),
                "citation_count": item.get("citation_count") or item.get("cited_by_count"),
                "document_type": "; ".join(item.get("publication_types") or []) if isinstance(item.get("publication_types"), list) else item.get("type"),
                "screening_decision": "unscreened",
                "screening_reason": "",
                "evidence_class": "",
                "system_or_material": "",
                "method_or_correlation": "",
                "operating_range": "",
                "key_result": "",
                "limitations": "",
                "relevance_to_decision": "",
                "verification_notes": "",
                "source_files": [str(path)],
            }
        )
    return rows


def _merge_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = _record_key(row)
        if key not in merged:
            merged[key] = row
            continue
        target = merged[key]
        target["source_database"] = "; ".join(sorted(set(filter(None, target["source_database"].split("; ") + [row["source_database"]]))))
        target["source_files"] = sorted(set(target["source_files"] + row["source_files"]))
        for field in ("doi", "stable_url", "pdf_url", "access_status", "citation_count", "document_type", "authors", "year"):
            if not target.get(field) and row.get(field):
                target[field] = row[field]
        if row.get("query") and row["query"] not in str(target.get("query")):
            target["query"] = "; ".join(filter(None, [target.get("query"), row.get("query")]))
    return list(merged.values())


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    columns = [
        "record_id",
        "screening_decision",
        "title",
        "year",
        "doi",
        "source_database",
        "access_status",
        "evidence_class",
        "relevance_to_decision",
    ]
    lines = ["# Literature Review Matrix", "", "| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        values = []
        for column in columns:
            text = "" if row.get(column) is None else str(row.get(column))
            values.append(text.replace("|", "\\|").replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deduplicated literature-review matrix from search JSON files")
    parser.add_argument("--inputs", nargs="+", required=True, help="Search-result JSON files")
    parser.add_argument("--output", required=True, help="Output JSON review matrix")
    parser.add_argument("--markdown-output", help="Optional Markdown table output")
    args = parser.parse_args()

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://docs.openalex.org/", "https://api.crossref.org/", "https://api.semanticscholar.org/api-docs/graph"],
        extra_notes="Review upstream terms for metadata reuse and preserve source provenance in literature reviews.",
    )

    try:
        raw_rows = []
        for input_path in args.inputs:
            raw_rows.extend(_rows_from_file(Path(input_path)))
        rows = _merge_rows(raw_rows)
        for idx, row in enumerate(rows, start=1):
            row["record_id"] = f"LIT-{idx:04d}"

        results = {
            "raw_records": len(raw_rows),
            "deduplicated_records": len(rows),
            "deduplication_rule": "DOI first, otherwise normalized title plus year.",
            "rows": rows,
        }
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=results,
            warnings=["Deduplication is a deterministic screening aid; manually review title/author/year conflicts before final citation use."],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        if args.markdown_output:
            markdown_path = Path(args.markdown_output)
            markdown_path.parent.mkdir(parents=True, exist_ok=True)
            markdown_path.write_text(_markdown_table(rows), encoding="utf-8")
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        write_json(result_envelope(skill=SKILL, inputs=vars(args), results={"error": str(exc)}, ok=False), args.output)
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

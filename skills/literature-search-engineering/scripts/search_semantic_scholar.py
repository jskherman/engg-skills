#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search Semantic Scholar Academic Graph metadata.

Formula/reference note:
  The Semantic Scholar Graph API paper search endpoint returns metadata fields
  selected through a comma-separated fields parameter. This script requests DOI,
  title, authors, venue, year, citation counts, abstract, and openAccessPdf so
  the downstream review matrix can track access status without scraping pages.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "literature-search-engineering"
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_FIELDS = (
    "paperId,title,year,authors,venue,publicationVenue,externalIds,url,abstract,"
    "citationCount,influentialCitationCount,isOpenAccess,openAccessPdf,publicationTypes"
)


def _authors(raw: list[dict]) -> list[str]:
    return [item.get("name") for item in raw if item.get("name")]


def _doi(external_ids: dict | None) -> str | None:
    if not external_ids:
        return None
    return external_ids.get("DOI") or external_ids.get("doi")


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Semantic Scholar Academic Graph paper metadata")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10, help="Maximum records to return, capped at 100")
    parser.add_argument("--api-key", help="Semantic Scholar API key; optional but recommended for heavier use")
    parser.add_argument("--fields", default=DEFAULT_FIELDS)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://api.semanticscholar.org/api-docs/graph"],
        extra_notes="Review Semantic Scholar API terms, authentication, and rate limits before reuse.",
    )

    try:
        limit = min(max(args.limit, 1), 100)
        params = {"query": args.query, "limit": str(limit), "fields": args.fields}
        url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
        headers = {"User-Agent": "engg-skills/0.1"}
        if args.api_key:
            headers["x-api-key"] = args.api_key
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = json.load(response)

        items = []
        for paper in raw.get("data", []):
            pdf = paper.get("openAccessPdf") or {}
            pdf_url = pdf.get("url")
            items.append(
                {
                    "title": paper.get("title"),
                    "authors": _authors(paper.get("authors") or []),
                    "year": paper.get("year"),
                    "doi": _doi(paper.get("externalIds")),
                    "semantic_scholar_id": paper.get("paperId"),
                    "venue": paper.get("venue"),
                    "url": paper.get("url"),
                    "abstract": paper.get("abstract"),
                    "citation_count": paper.get("citationCount"),
                    "influential_citation_count": paper.get("influentialCitationCount"),
                    "is_open_access": paper.get("isOpenAccess"),
                    "pdf_url": pdf_url,
                    "pdf_status": pdf.get("status"),
                    "access_status": "open_access_pdf" if pdf_url else ("open_access_metadata" if paper.get("isOpenAccess") else "metadata_only"),
                    "publication_types": paper.get("publicationTypes") or [],
                }
            )

        data = result_envelope(
            skill=SKILL,
            inputs={k: ("<provided>" if k == "api_key" and v else v) for k, v in vars(args).items()},
            results={"query_url": url, "items": items},
            sources=["https://api.semanticscholar.org/api-docs/graph"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        safe_inputs = {k: ("<provided>" if k == "api_key" and v else v) for k, v in vars(args).items()}
        write_json(result_envelope(skill=SKILL, inputs=safe_inputs, results={"error": str(exc)}, ok=False), args.output)
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

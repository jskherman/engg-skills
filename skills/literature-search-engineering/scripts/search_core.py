#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search CORE (core.ac.uk) — the world's largest open-access research aggregator.

CORE aggregates open-access full text from thousands of institutional and
subject repositories worldwide. The v3 API supports keyword search with
optional full-text availability filtering. An API key is required for
authenticated access.

API docs: https://api.core.ac.uk/docs/v3
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


def _authors(raw: list[dict] | None) -> list[str]:
    if not raw:
        return []
    return [
        author.get("name", "")
        for author in raw
        if author.get("name")
    ]


def _doi(identifiers: list[str] | None) -> str | None:
    if not identifiers:
        return None
    for identifier in identifiers:
        if identifier.lower().startswith("doi:"):
            return identifier[4:]
    return None


def _oa_link(links: list[dict] | None) -> str | None:
    if not links:
        return None
    for link in links:
        if link.get("type") in ("download", "direct"):
            return link.get("url")
    for link in links:
        if link.get("type") == "display":
            return link.get("url")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search CORE (core.ac.uk) open-access research aggregator"
    )
    parser.add_argument("--query", required=True,
                        help="Search query string")
    parser.add_argument("--limit", type=int, default=10,
                        help="Maximum records to return, capped at 100")
    parser.add_argument("--api-key", required=True,
                        help="CORE API key (required)")
    parser.add_argument("--fulltext-only", action="store_true",
                        help="Only return results with full-text availability")
    parser.add_argument("--output", required=True,
                        help="Output JSON file")
    args = parser.parse_args()

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://api.core.ac.uk/docs/v3"],
        extra_notes=(
            "CORE API requires registration for an API key. Review CORE terms "
            "of service and rate limits before reuse."
        ),
    )

    try:
        limit = min(max(args.limit, 1), 100)
        params: dict[str, str] = {
            "q": args.query,
            "limit": str(limit),
        }
        if args.fulltext_only:
            params["fulltext"] = "true"

        url = "https://api.core.ac.uk/v3/search/works?" + urllib.parse.urlencode(params)
        headers = {
            "User-Agent": "engg-skills/0.1",
            "Authorization": f"Bearer {args.api_key}",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = json.load(response)

        items = []
        for work in raw.get("results", []):
            links = work.get("links") or []
            pdf_url = _oa_link(links)
            download_url = None
            for link in links:
                if link.get("type") == "download":
                    download_url = link.get("url")

            items.append({
                "title": work.get("title"),
                "authors": _authors(work.get("authors")),
                "year": work.get("yearPublished"),
                "doi": _doi(work.get("identifiers")),
                "core_id": work.get("id"),
                "abstract": work.get("abstract"),
                "full_text_identifier": work.get("fullTextIdentifier"),
                "link": pdf_url,
                "download_url": download_url,
                "publisher": work.get("publisher"),
                "language": work.get("language", {}).get("name") if isinstance(work.get("language"), dict) else None,
                "access_status": "open_access_pdf" if download_url else ("open_access_metadata" if pdf_url else "metadata_only"),
                "source": "CORE",
                "repository_name": (work.get("source", {}) or {}).get("name"),
            })

        data = result_envelope(
            skill=SKILL,
            inputs={**vars(args), "api_key": "<provided>"},
            results={
                "query_url": url,
                "total_hits": raw.get("totalHits"),
                "items": items,
            },
            sources=["https://api.core.ac.uk/docs/v3"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        safe_inputs = {
            **{k: ("<provided>" if k == "api_key" and v else v) for k, v in vars(args).items()},
        }
        write_json(
            result_envelope(skill=SKILL, inputs=safe_inputs, results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
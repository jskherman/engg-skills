#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search arXiv metadata through the public Atom API.

Formula/reference note:
  arXiv query syntax uses field prefixes such as all:, ti:, au:, abs:, cat:,
  and submittedDate:. This script defaults to all:<query> unless the query
  already contains a field prefix or Boolean operator syntax provided by the
  user. See the arXiv API user manual.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "literature-search-engineering"
SKILL_DIR = Path(__file__).resolve().parents[1]
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _search_query(query: str) -> str:
    prefixes = ("all:", "ti:", "au:", "abs:", "co:", "jr:", "cat:", "id:")
    stripped = query.strip()
    if any(token in stripped for token in prefixes) or " AND " in stripped or " OR " in stripped:
        return stripped
    return f"all:{stripped}"


def _text(entry: ET.Element, path: str) -> str | None:
    value = entry.findtext(path, namespaces=ARXIV_NS)
    return " ".join(value.split()) if value else None


def _authors(entry: ET.Element) -> list[str]:
    return [
        " ".join((author.findtext("atom:name", namespaces=ARXIV_NS) or "").split())
        for author in entry.findall("atom:author", namespaces=ARXIV_NS)
    ]


def _links(entry: ET.Element) -> dict[str, str | None]:
    abs_url = None
    pdf_url = None
    for link in entry.findall("atom:link", namespaces=ARXIV_NS):
        href = link.attrib.get("href")
        if not href:
            continue
        if link.attrib.get("rel") == "alternate":
            abs_url = href
        if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
            pdf_url = href
    return {"url": abs_url, "pdf_url": pdf_url}


def main() -> int:
    parser = argparse.ArgumentParser(description="Search arXiv records through the public Atom API")
    parser.add_argument("--query", required=True, help="arXiv query or plain-text query")
    parser.add_argument("--limit", type=int, default=10, help="Maximum records to return, capped at 100")
    parser.add_argument("--sort-by", default="relevance", choices=["relevance", "lastUpdatedDate", "submittedDate"])
    parser.add_argument("--sort-order", default="descending", choices=["ascending", "descending"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://info.arxiv.org/help/api/user-manual.html"],
        extra_notes="Review arXiv API terms and use reasonable request rates before reuse.",
    )

    try:
        max_results = min(max(args.limit, 1), 100)
        params = {
            "search_query": _search_query(args.query),
            "start": "0",
            "max_results": str(max_results),
            "sortBy": args.sort_by,
            "sortOrder": args.sort_order,
        }
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers={"User-Agent": "engg-skills/0.1"})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()

        root = ET.fromstring(raw)
        items = []
        for entry in root.findall("atom:entry", namespaces=ARXIV_NS):
            links = _links(entry)
            arxiv_id = _text(entry, "atom:id")
            primary_category = entry.find("arxiv:primary_category", namespaces=ARXIV_NS)
            items.append(
                {
                    "title": _text(entry, "atom:title"),
                    "authors": _authors(entry),
                    "published": _text(entry, "atom:published"),
                    "updated": _text(entry, "atom:updated"),
                    "summary": _text(entry, "atom:summary"),
                    "arxiv_id": arxiv_id,
                    "doi": _text(entry, "arxiv:doi"),
                    "journal_ref": _text(entry, "arxiv:journal_ref"),
                    "primary_category": primary_category.attrib.get("term") if primary_category is not None else None,
                    "url": links["url"],
                    "pdf_url": links["pdf_url"],
                    "access_status": "open_access_arxiv" if links["pdf_url"] else "metadata_only",
                }
            )

        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results={"query_url": url, "items": items},
            sources=["https://info.arxiv.org/help/api/user-manual.html"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        write_json(
            result_envelope(skill=SKILL, inputs=vars(args), results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

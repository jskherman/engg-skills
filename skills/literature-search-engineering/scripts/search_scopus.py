#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Search Scopus (Elsevier) for academic papers by keywords, DOI, title, or raw query.

Scopus is one of the largest abstract and citation databases of peer-reviewed
literature. The Scopus Search API provides structured metadata including DOIs,
citation counts, author affiliations, and journal information.

API docs: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl

Query modes:
  --keywords "amine treating mercaptan" → TITLE-ABS-KEY("amine treating mercaptan")
  --doi 10.1016/j.ces.2020.115678        → DOI(10.1016/j.ces.2020.115678)
  --title "Heat Transfer in Packed Beds"  → TITLE("Heat Transfer in Packed Beds")
  --query "TITLE-ABS-KEY(amine) AND DOI(10.1000/xyz)" → raw Scopus query

Requires an Elsevier API key (--api-key or ELSEVIER_API_KEY environment variable).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "literature-search-engineering"
SKILL_DIR = Path(__file__).resolve().parents[1]

SCOPUS_SEARCH_URL = "https://api.elsevier.com/content/search/scopus"

# ── query construction ────────────────────────────────────────────────────────

SCOPUS_FIELD_CODES = (
    "TITLE", "ABS", "KEY", "AUTH", "DOI", "ALL",
    "SRCTITLE", "AFFIL", "PUBYEAR", "REF",
)

SCOPUS_BOOLEAN = re.compile(r"\b(AND|OR|AND NOT)\b", re.IGNORECASE)


def _is_raw_scopus_query(query: str) -> bool:
    """Detect whether the query string already contains Scopus field codes or Booleans."""
    upper = query.upper()
    for code in SCOPUS_FIELD_CODES:
        if f"{code}(" in upper:
            return True
    if SCOPUS_BOOLEAN.search(query):
        return True
    return False


def _escape_scopus(text: str) -> str:
    """Escape backslashes and double-quotes for Scopus query grammar."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _scopus_phrase(text: str) -> str:
    """Wrap text in double-quotes if it contains whitespace or special chars."""
    if any(ch.isspace() for ch in text) or any(ch in text for ch in '(){}[]'):
        return f'"{_escape_scopus(text)}"'
    return _escape_scopus(text)


def _build_query(args: argparse.Namespace) -> str:
    """Build a Scopus query string from the user's input mode."""
    if args.query:
        return args.query
    if args.doi:
        return f"DOI({args.doi.strip()})"
    if args.title:
        return f'TITLE("{_escape_scopus(args.title.strip())}")'
    # keywords mode (default)
    if _is_raw_scopus_query(args.keywords):
        return args.keywords
    return f'TITLE-ABS-KEY("{_escape_scopus(args.keywords.strip())}")'


# ── API call ───────────────────────────────────────────────────────────────────

def _scopus_request(
    api_key: str,
    inst_token: str | None,
    query: str,
    count: int,
    start: int,
    sort: str,
) -> dict[str, Any]:
    params = urllib.parse.urlencode({
        "query": query,
        "count": str(count),
        "start": str(start),
        "sort": sort,
    })
    url = f"{SCOPUS_SEARCH_URL}?{params}"
    headers: dict[str, str] = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json",
        "User-Agent": "engg-skills/0.1",
    }
    if inst_token:
        headers["X-ELS-Insttoken"] = inst_token

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Scopus API HTTP {exc.code}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Scopus API network error: {exc}") from exc


# ── result extraction ─────────────────────────────────────────────────────────

def _int_or(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_entries(raw: dict[str, Any]) -> dict[str, Any]:
    results = raw.get("search-results", {})
    total = _int_or(results.get("opensearch:totalResults", 0))
    items_per_page = _int_or(results.get("opensearch:itemsPerPage", 0))
    start_index = _int_or(results.get("opensearch:startIndex", 0))
    entries_raw = results.get("entry") or []
    if isinstance(entries_raw, dict):
        entries_raw = [entries_raw]

    entries: list[dict[str, Any]] = []
    for item in entries_raw:
        authors = item.get("dc:creator") or ""
        if authors:
            authors = [a.strip() for a in authors.split(",") if a.strip()]
        # Extract links: scopus record, full-text
        links_raw = item.get("link") or []
        if isinstance(links_raw, dict):
            links_raw = [links_raw]
        scopus_url = None
        fulltext_url = None
        for link in links_raw:
            ref_attr = link.get("@ref") or link.get("@href") or ""
            href = link.get("@href") or ""
            if "scopus" in ref_attr.lower() and not scopus_url:
                scopus_url = href
            if "full-text" in ref_attr.lower() and not fulltext_url:
                fulltext_url = href

        entries.append({
            "title": item.get("dc:title") or "",
            "doi": item.get("prism:doi"),
            "year": _int_or((item.get("prism:coverDate") or "")[:4]),
            "publication_name": item.get("prism:publicationName") or "",
            "volume": item.get("prism:volume"),
            "issue": item.get("prism:issueIdentifier"),
            "pages": item.get("prism:pageRange"),
            "cited_by": _int_or(item.get("citedby-count")),
            "authors": authors,
            "abstract": item.get("dc:description") or "",
            "document_type": item.get("subtypeDescription") or "",
            "eid": item.get("eid"),
            "scopus_url": scopus_url,
            "fulltext_url": fulltext_url,
            "open_access": item.get("openaccess") or "",
            "source": "Scopus",
        })

    return {
        "total": total,
        "items_per_page": items_per_page,
        "start_index": start_index,
        "returned": len(entries),
        "items": entries,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search Scopus for academic papers by keywords, DOI, title, or raw query"
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keywords", help="Topic keywords — builds a TITLE-ABS-KEY query")
    mode.add_argument("--doi", help="Exact DOI lookup")
    mode.add_argument("--title", help="Exact title lookup")
    mode.add_argument("--query", help="Raw Scopus query string (field codes, booleans)")

    parser.add_argument("--api-key", default=os.environ.get("ELSEVIER_API_KEY"),
                        help="Elsevier API key. Defaults to ELSEVIER_API_KEY env var")
    parser.add_argument("--inst-token", default=os.environ.get("ELSEVIER_INSTTOKEN"),
                        help="Elsevier institutional token (optional)")
    parser.add_argument("--count", type=int, default=20,
                        help="Max entries to return, capped at 200 (default: 20)")
    parser.add_argument("--start", type=int, default=0,
                        help="Result offset for pagination (default: 0)")
    parser.add_argument("--sort", default="-citedby-count",
                        help="Sort expression (default: -citedby-count)")
    parser.add_argument("--output", required=True,
                        help="Output JSON file")
    args = parser.parse_args()

    api_key = args.api_key
    if not api_key:
        print("Error: Elsevier API key required. Set ELSEVIER_API_KEY or use --api-key.",
              file=sys.stderr)
        return 2

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=[
            "https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl",
            "https://dev.elsevier.com/",
        ],
        extra_notes=(
            "Scopus API requires an Elsevier API key. Review Elsevier API terms "
            "of use and rate limits before reuse. Scopus metadata is copyrighted "
            "by Elsevier B.V."
        ),
    )

    safe_inputs = {
        **{k: ("<provided>" if k in ("api_key", "inst_token") and v else v)
           for k, v in vars(args).items()},
    }

    try:
        query = _build_query(args)
        limit = min(max(args.count, 1), 200)
        raw = _scopus_request(
            api_key=api_key,
            inst_token=args.inst_token,
            query=query,
            count=limit,
            start=args.start,
            sort=args.sort,
        )
        parsed = _extract_entries(raw)

        results: dict[str, Any] = {
            "query": query,
            "query_url": f"{SCOPUS_SEARCH_URL}?query={urllib.parse.quote(query)}&count={limit}&start={args.start}&sort={args.sort}",
            **parsed,
        }

        data = result_envelope(
            skill=SKILL,
            inputs=safe_inputs,
            results=results,
            sources=["https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success — {parsed['returned']} of {parsed['total']} results. JSON: {path}")
        return 0
    except RuntimeError as exc:
        write_json(
            result_envelope(skill=SKILL, inputs=safe_inputs, results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - CLI guardrail
        write_json(
            result_envelope(skill=SKILL, inputs=safe_inputs, results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve and optionally download lawful open-access PDFs for a DOI.

Formula/reference note:
  DOI lookup is performed against metadata and OA-location APIs, not pirate or
  access-control-bypass services. Candidate PDFs are accepted only from HTTPS
  URLs that are not known bypass domains and that return bytes beginning with
  the PDF magic header %PDF before being written to disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "literature-search-engineering"
SKILL_DIR = Path(__file__).resolve().parents[1]
BLOCKED_HOST_PATTERNS = (
    "sci-hub",
    "libgen",
    "librarygenesis",
    "z-lib",
    "zlibrary",
)


def _normalise_doi(doi: str) -> str:
    value = doi.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:", "", value, flags=re.IGNORECASE)
    return value.strip()


def _safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https" or not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    return not any(pattern in host for pattern in BLOCKED_HOST_PATTERNS)


def _request_json(url: str, *, email: str | None = None) -> dict:
    headers = {"User-Agent": f"engg-skills/0.1 ({email or 'mailto optional'})"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _candidate_from_location(location: dict | None, source: str) -> dict | None:
    if not location:
        return None
    pdf_url = location.get("pdf_url") or location.get("url_for_pdf")
    landing_url = location.get("landing_page_url") or location.get("url") or location.get("url_for_landing_page")
    if not pdf_url:
        return None
    return {
        "source": source,
        "pdf_url": pdf_url,
        "landing_page_url": landing_url,
        "license": location.get("license"),
        "version": location.get("version"),
        "is_oa": location.get("is_oa"),
        "host_type": ((location.get("source") or {}).get("type") if isinstance(location.get("source"), dict) else None),
    }


def _openalex_candidates(doi: str, email: str | None) -> tuple[dict | None, list[dict]]:
    work_url = "https://api.openalex.org/works/" + quote(f"doi:{doi}", safe=":")
    if email:
        work_url += "?" + urllib.parse.urlencode({"mailto": email})
    try:
        work = _request_json(work_url, email=email)
    except urllib.error.HTTPError:
        return None, []

    candidates = []
    for name in ("best_oa_location", "primary_location"):
        candidate = _candidate_from_location(work.get(name), f"openalex.{name}")
        if candidate:
            candidates.append(candidate)
    for idx, location in enumerate(work.get("locations") or []):
        candidate = _candidate_from_location(location, f"openalex.locations[{idx}]")
        if candidate:
            candidates.append(candidate)
    return work, candidates


def _unpaywall_candidates(doi: str, email: str | None) -> tuple[dict | None, list[dict]]:
    if not email:
        return None, []
    url = "https://api.unpaywall.org/v2/" + quote(doi, safe="") + "?" + urllib.parse.urlencode({"email": email})
    try:
        record = _request_json(url, email=email)
    except urllib.error.HTTPError:
        return None, []

    candidates = []
    best = _candidate_from_location(record.get("best_oa_location"), "unpaywall.best_oa_location")
    if best:
        candidates.append(best)
    for idx, location in enumerate(record.get("oa_locations") or []):
        candidate = _candidate_from_location(location, f"unpaywall.oa_locations[{idx}]")
        if candidate:
            candidates.append(candidate)
    return record, candidates


def _dedupe_candidates(candidates: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for candidate in candidates:
        pdf_url = candidate.get("pdf_url")
        if not pdf_url or pdf_url in seen:
            continue
        seen.add(pdf_url)
        candidate = dict(candidate)
        candidate["safe_url"] = _safe_url(pdf_url)
        output.append(candidate)
    return output


def _filename_from_doi(doi: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", doi).strip("_")
    return f"{safe or 'paper'}.pdf"


def _download_pdf(url: str, output_path: Path, email: str | None) -> dict:
    if not _safe_url(url):
        raise ValueError("refusing non-HTTPS, empty-host, or blocked-domain PDF URL")
    headers = {"User-Agent": f"engg-skills/0.1 ({email or 'mailto optional'})"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type")
    if not data.startswith(b"%PDF"):
        raise ValueError("downloaded bytes do not start with the PDF magic header %PDF")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return {
        "path": str(output_path),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "content_type": content_type,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve lawful open-access PDF URLs for a DOI")
    parser.add_argument("--doi", required=True)
    parser.add_argument("--email", help="Contact email for polite API access and Unpaywall lookup")
    parser.add_argument("--download-dir", default="pdf")
    parser.add_argument("--no-download", action="store_true", help="Resolve candidates without downloading")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://docs.openalex.org/", "https://unpaywall.org/products/api"],
        extra_notes="Download only lawful open-access PDFs or user-authorized full text. Do not use Sci-Hub or bypass services.",
    )

    doi = _normalise_doi(args.doi)
    safe_inputs = {**vars(args), "doi": doi, "email": "<provided>" if args.email else None}
    try:
        openalex_record, openalex = _openalex_candidates(doi, args.email)
        unpaywall_record, unpaywall = _unpaywall_candidates(doi, args.email)
        candidates = _dedupe_candidates(openalex + unpaywall)
        safe_candidates = [candidate for candidate in candidates if candidate.get("safe_url")]

        download = None
        if safe_candidates and not args.no_download:
            output_path = Path(args.download_dir) / _filename_from_doi(doi)
            download = _download_pdf(safe_candidates[0]["pdf_url"], output_path, args.email)

        results = {
            "doi": doi,
            "openalex_id": (openalex_record or {}).get("id"),
            "title": (openalex_record or {}).get("title") or (unpaywall_record or {}).get("title"),
            "is_oa": (openalex_record or {}).get("open_access", {}).get("is_oa") if openalex_record else (unpaywall_record or {}).get("is_oa"),
            "candidates": candidates,
            "selected_pdf_url": safe_candidates[0]["pdf_url"] if safe_candidates else None,
            "download": download,
            "blocked_policy": "Sci-Hub, LibGen, mirror portals, and access-control bypass domains are refused.",
        }
        warnings = []
        if not candidates:
            warnings.append("No open-access PDF candidate was found in queried metadata sources.")
        if candidates and not safe_candidates:
            warnings.append("PDF candidates were present but all failed safety/domain checks.")
        if args.no_download:
            warnings.append("PDF download skipped because --no-download was set.")

        data = result_envelope(
            skill=SKILL,
            inputs=safe_inputs,
            results=results,
            warnings=warnings,
            sources=["https://docs.openalex.org/", "https://unpaywall.org/products/api"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:  # pragma: no cover - CLI guardrail
        write_json(result_envelope(skill=SKILL, inputs=safe_inputs, results={"error": str(exc)}, ok=False), args.output)
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

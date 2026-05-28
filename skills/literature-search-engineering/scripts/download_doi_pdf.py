#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Download a paper PDF by DOI using Sci-Hub / LibGen mirrors with OA fallback.

Mirror strategy:
  1. Sci-Hub mirrors: https://sci-hub.{ee,st,su,vg}/{doi}
     Parse the response HTML for the embedded PDF iframe/embed src.
  2. LibGen Sci-Mag mirrors: https://libgen.{vg,gl,la,bz}/scimag/?s={doi}
     Parse the results table for the download link.
  3. OpenAlex / Unpaywall OA resolution as a lawful fallback.

The first successful PDF download (verified by %PDF magic) is written to disk.
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
from urllib.parse import quote

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "literature-search-engineering"
SKILL_DIR = Path(__file__).resolve().parents[1]

# ── mirrors ──────────────────────────────────────────────────────────────────

SCI_HUB_MIRRORS = ("ee", "st", "su", "vg")
LIBGEN_MIRRORS = ("vg", "gl", "la", "bz")

# ── helpers ───────────────────────────────────────────────────────────────────

def _normalise_doi(doi: str) -> str:
    value = doi.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:", "", value, flags=re.IGNORECASE)
    return value.strip()


def _filename_from_doi(doi: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", doi).strip("_")
    return f"{safe or 'paper'}.pdf"


def _request_html(url: str, *, email: str | None = None, timeout: int = 30) -> str:
    headers = {"User-Agent": f"engg-skills/0.1 ({email or 'mailto optional'})"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _request_bytes(url: str, *, email: str | None = None, timeout: int = 60) -> tuple[bytes, str | None]:
    headers = {"User-Agent": f"engg-skills/0.1 ({email or 'mailto optional'})"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        ct = resp.headers.get("Content-Type")
    return data, ct


def _is_pdf(data: bytes) -> bool:
    return data.startswith(b"%PDF")


def _ping_url(url: str, timeout: float = 5) -> bool:
    """Quickly check if a URL is reachable. Returns True if any response is received."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except Exception:
        return False


def _download_pdf(url: str, output_path: Path, email: str | None) -> dict:
    data, ct = _request_bytes(url, email=email, timeout=60)
    if not _is_pdf(data):
        raise ValueError("downloaded bytes do not start with the PDF magic header %PDF")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return {
        "path": str(output_path),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "content_type": ct,
    }


# ── Sci-Hub ───────────────────────────────────────────────────────────────────

def _scihub_candidate(mirror: str, doi: str, email: str | None) -> dict | None:
    """Try one Sci-Hub mirror and return the PDF URL if found."""
    url = f"https://sci-hub.{mirror}/{quote(doi)}"
    # Pre-ping the mirror to skip dead ones quickly
    if not _ping_url(f"https://sci-hub.{mirror}/", timeout=4):
        return None
    try:
        html = _request_html(url, email=email, timeout=20)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None

    pdf_url = None

    # Strategy 1: <iframe src="..." id="pdf">
    m = re.search(r'<iframe[^>]*\s+src\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        pdf_url = m.group(1)
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url

    # Strategy 2: <embed src="..." type="application/pdf">
    if not pdf_url:
        m = re.search(r'<embed[^>]*\s+src\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        if m:
            pdf_url = m.group(1)
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url

    # Strategy 3: <button onclick="location.href='...'">
    if not pdf_url:
        m = re.search(r"location\s*\.\s*href\s*=\s*['\"]([^'\"]+)", html, re.IGNORECASE)
        if m:
            pdf_url = m.group(1)
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url

    if not pdf_url:
        # Strategy 4: look for any URL ending in .pdf in the page
        m = re.search(r'["\'](https?://[^"\']+\.pdf)["\']', html, re.IGNORECASE)
        if m:
            pdf_url = m.group(1)

    if pdf_url and not pdf_url.startswith("http"):
        pdf_url = None

    if pdf_url:
        return {"source": f"sci-hub.{mirror}", "page_url": url, "pdf_url": pdf_url}
    return None


def _scihub_download(doi: str, output_path: Path, email: str | None) -> dict | None:
    for mirror in SCI_HUB_MIRRORS:
        candidate = _scihub_candidate(mirror, doi, email)
        if not candidate:
            continue
        try:
            return {
                **candidate,
                "download": _download_pdf(candidate["pdf_url"], output_path, email),
            }
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
            continue
    return None


# ── LibGen Sci-Mag ────────────────────────────────────────────────────────────

def _libgen_candidate(mirror: str, doi: str, email: str | None) -> dict | None:
    """Search LibGen Sci-Mag by DOI and find the download link."""
    # Pre-ping the mirror to skip dead ones quickly
    if not _ping_url(f"https://libgen.{mirror}/", timeout=4):
        return None
    search_url = (
        f"https://libgen.{mirror}/scimag/?"
        + urllib.parse.urlencode({"s": doi})
    )
    try:
        html = _request_html(search_url, email=email, timeout=20)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None

    download_url = None

    # Strategy 1: Look for links containing "get.php" or "ads.php" with the DOI
    m = re.search(
        r'<a\s+[^>]*href\s*=\s*["\']([^"\']*(?:get\.php|ads\.php)[^"\']*)["\'][^>]*>',
        html, re.IGNORECASE,
    )
    if m:
        href = m.group(1)
        if href.startswith("/"):
            download_url = f"https://libgen.{mirror}{href}"
        elif href.startswith("http"):
            download_url = href

    # Strategy 2: Look for a direct DOI-based download link
    if not download_url:
        candidate_url = f"https://libgen.{mirror}/scimag/get.php?doi={quote(doi, safe='')}"
        try:
            _request_html(candidate_url, email=email, timeout=15)
            download_url = candidate_url
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
            pass

    # Strategy 3: Look for library.lol direct links
    if not download_url:
        m = re.search(
            r'["\'](https?://(?:download\.)?library\.lol/[^"\']+)["\']',
            html, re.IGNORECASE,
        )
        if m:
            download_url = m.group(1)

    # Strategy 4: Look for any PDF link
    if not download_url:
        m = re.search(
            r'["\'](https?://[^"\']+\.pdf)["\']',
            html, re.IGNORECASE,
        )
        if m:
            download_url = m.group(1)

    if download_url:
        return {
            "source": f"libgen.{mirror}",
            "page_url": search_url,
            "pdf_url": download_url,
        }
    return None


def _libgen_download(doi: str, output_path: Path, email: str | None) -> dict | None:
    for mirror in LIBGEN_MIRRORS:
        candidate = _libgen_candidate(mirror, doi, email)
        if not candidate:
            continue
        try:
            download_result = _download_pdf(
                candidate["pdf_url"], output_path, email
            )
            return {**candidate, "download": download_result}
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
            continue
    return None


# ── OpenAlex / Unpaywall OA fallback ──────────────────────────────────────────

def _request_json(url: str, *, email: str | None = None) -> dict:
    headers = {"User-Agent": f"engg-skills/0.1 ({email or 'mailto optional'})"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _oa_candidates(doi: str, email: str | None) -> list[dict]:
    candidates: list[dict] = []

    # OpenAlex
    try:
        work_url = "https://api.openalex.org/works/" + quote(f"doi:{doi}", safe=":")
        if email:
            work_url += "?" + urllib.parse.urlencode({"mailto": email})
        work = _request_json(work_url, email=email)
        for location in (work.get("best_oa_location"), work.get("primary_location")):
            if location and location.get("pdf_url"):
                candidates.append({
                    "source": "openalex",
                    "pdf_url": location["pdf_url"],
                    "landing_page_url": location.get("landing_page_url") or location.get("url"),
                    "license": location.get("license"),
                    "version": location.get("version"),
                })
        for loc in work.get("locations") or []:
            if loc.get("pdf_url"):
                candidates.append({
                    "source": "openalex.locations",
                    "pdf_url": loc["pdf_url"],
                    "landing_page_url": loc.get("landing_page_url") or loc.get("url"),
                    "license": loc.get("license"),
                    "version": loc.get("version"),
                })
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        pass

    # Unpaywall
    if email:
        try:
            uw_url = "https://api.unpaywall.org/v2/" + quote(doi, safe="") + "?" + urllib.parse.urlencode({"email": email})
            uw = _request_json(uw_url, email=email)
            for loc in ([uw.get("best_oa_location")] + (uw.get("oa_locations") or [])):
                if loc and loc.get("pdf_url"):
                    candidates.append({
                        "source": "unpaywall",
                        "pdf_url": loc["pdf_url"],
                        "landing_page_url": loc.get("landing_page_url") or loc.get("url"),
                        "license": loc.get("license"),
                        "version": loc.get("version"),
                    })
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
            pass

    # Deduplicate by pdf_url
    seen = set()
    unique = []
    for c in candidates:
        url = c.get("pdf_url")
        if url and url not in seen:
            seen.add(url)
            unique.append(c)
    return unique


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download a paper PDF by DOI using Sci-Hub / LibGen mirrors"
    )
    parser.add_argument("--doi", required=True,
                        help="DOI of the paper (e.g. 10.1000/xyz123)")
    parser.add_argument("--email",
                        help="Contact email for polite API access (Unpaywall requires it)")
    parser.add_argument("--download-dir", default="pdf",
                        help="Directory to save downloaded PDF (default: pdf/)")
    parser.add_argument("--no-scihub", action="store_true",
                        help="Skip Sci-Hub mirror attempts")
    parser.add_argument("--no-libgen", action="store_true",
                        help="Skip LibGen mirror attempts")
    parser.add_argument("--no-oa", action="store_true",
                        help="Skip OpenAlex/Unpaywall OA fallback")
    parser.add_argument("--output", required=True,
                        help="Output JSON file")
    args = parser.parse_args()

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=[
            "https://sci-hub.se/about",
            "https://libgen.is/",
            "https://docs.openalex.org/",
            "https://unpaywall.org/products/api",
        ],
        extra_notes=(
            "Sci-Hub and LibGen are third-party services. Review their terms "
            "and your local copyright regulations before use. Downloaded PDFs "
            "are for personal research and educational purposes."
        ),
    )

    doi = _normalise_doi(args.doi)
    output_path = Path(args.download_dir) / _filename_from_doi(doi)
    safe_inputs = {
        **vars(args),
        "doi": doi,
        "email": "<provided>" if args.email else None,
    }

    sources_tried: list[str] = []
    result: dict | None = None

    # 1 ── Sci-Hub mirrors ──
    if not args.no_scihub:
        scihub = _scihub_download(doi, output_path, args.email)
        if scihub:
            sources_tried.append(scihub["source"])
            result = scihub

    # 2 ── LibGen mirrors ──
    if not result and not args.no_libgen:
        libgen = _libgen_download(doi, output_path, args.email)
        if libgen:
            sources_tried.append(libgen["source"])
            result = libgen

    # 3 ── OA fallback ──
    oa_cands: list[dict] = []
    if not result and not args.no_oa:
        oa_cands = _oa_candidates(doi, args.email)
        for oa in oa_cands:
            try:
                dl = _download_pdf(oa["pdf_url"], output_path, args.email)
                sources_tried.append(oa["source"])
                result = {
                    "source": oa["source"],
                    "page_url": oa.get("landing_page_url"),
                    "pdf_url": oa["pdf_url"],
                    "license": oa.get("license"),
                    "version": oa.get("version"),
                    "download": dl,
                }
                break
            except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
                continue

    warnings: list[str] = []
    if not result:
        warnings.append(
            "No PDF could be downloaded from Sci-Hub, LibGen, or OA repositories. "
            "The paper may not be available through any of these services."
        )
    if not args.email:
        warnings.append(
            "No --email provided; Unpaywall OA lookup was skipped. "
            "Provide an email for broader OA coverage."
        )

    results = {
        "doi": doi,
        "sources_tried": sources_tried,
        "source": result["source"] if result else None,
        "pdf_url": result["pdf_url"] if result else None,
        "title": result.get("title") if result else None,
        "license": result.get("license") if result else None,
        "version": result.get("version") if result else None,
        "download": result["download"] if result else None,
        "oa_candidates": [
            {"source": c["source"], "pdf_url": c["pdf_url"], "landing_page_url": c.get("landing_page_url")}
            for c in oa_cands
        ],
        "mirrors_checked": {
            "sci_hub": [] if args.no_scihub else list(SCI_HUB_MIRRORS),
            "libgen": [] if args.no_libgen else list(LIBGEN_MIRRORS),
        },
    }

    data = result_envelope(
        skill=SKILL,
        inputs=safe_inputs,
        results=results,
        warnings=warnings,
        ok=result is not None,
        sources=[
            "https://sci-hub.se/",
            "https://libgen.is/",
            "https://docs.openalex.org/",
            "https://unpaywall.org/products/api",
        ],
    )
    data["source_notice"] = license_notice_for(SKILL)
    path = write_json(data, args.output)
    if result:
        print(f"Success — PDF from {result['source']}. JSON: {path}")
    else:
        print(f"No PDF found. JSON: {path}")
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve and optionally download PDFs for a DOI from OA repositories and mirrors.

Tries in order:
  1. OpenAlex / Unpaywall open-access locations (best_oa_location, primary_location)
  2. Sci-Hub via scihub-cli (multi-source: OA + Sci-Hub with robust PDF extraction)
  3. LibGen Sci-Mag mirrors (libgen.vg, .gl, .la, .bz)

Each candidate is checked (HTTPS, PDF magic %PDF) before downloading.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
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

# ── DOI-based mirror domains ──────────────────────────────────────────────
# LibGen mirrors provide access to papers via their DOI URL and are tried
# as fallback sources. Sci-Hub is handled by scihub-cli (external subprocess).
LIBGEN_MIRRORS = ("vg", "gl", "la", "bz")


def _normalise_doi(doi: str) -> str:
    value = doi.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:", "", value, flags=re.IGNORECASE)
    return value.strip()


def _safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https" or not parsed.netloc:
        return False
    return True


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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError):
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError):
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


def _ping_url(url: str, timeout: float = 5) -> bool:
    """Quickly check if a URL is reachable. Returns True if any response is received."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except Exception:
        return False


def _download_pdf(url: str, output_path: Path, email: str | None) -> dict:
    if not _safe_url(url):
        raise ValueError("refusing non-HTTPS or empty-host PDF URL")
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


# ── Sci-Hub (via scihub-cli) ────────────────────────────────────────────

def _scihub_cli_download(doi: str, output_path: Path, email: str | None) -> dict | None:
    """Download a paper PDF using scihub-cli (handles OA + Sci-Hub internally).

    scihub-cli (https://github.com/Oxidane-bot/scihub-cli) is a maintained,
    multi-source downloader with robust PDF extraction, mirror management,
    and CAPTCHA handling. We shell out to it via uvx for zero local deps.
    """
    # Create a temp input file with the DOI
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as fh:
        fh.write(doi + "\n")
        input_file = fh.name

    # Use a temp output directory so scihub-cli can name files freely
    tmp_out = Path(tempfile.mkdtemp(prefix="scihub_"))

    try:
        cmd = [
            "uvx", "--from", "git+https://github.com/Oxidane-bot/scihub-cli.git",
            "scihub-cli", input_file,
            "-o", str(tmp_out),
            "--fast-fail",
            "--no-academic-only",
            "-p", "1",
        ]
        if email:
            cmd.extend(["--email", email])

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=180,
        )

        if result.returncode != 0:
            return None

        # Find the downloaded PDF in the temp directory
        pdf_files = sorted(
            tmp_out.glob("*.pdf"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not pdf_files:
            return None

        pdf_path = pdf_files[0]

        # Move to our desired output path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pdf_path), str(output_path))

        return {
            "source": "scihub-cli",
            "pdf_url": None,
            "landing_page_url": None,
            "license": None,
            "version": "publisher",
            "is_oa": False,
            "host_type": "scihub-cli",
            "safe_url": True,
            "download": {
                "path": str(output_path),
                "bytes": output_path.stat().st_size,
                "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
                "content_type": "application/pdf",
            },
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
    finally:
        Path(input_file).unlink(missing_ok=True)
        shutil.rmtree(str(tmp_out), ignore_errors=True)


# ── LibGen Sci-Mag candidates ─────────────────────────────────────────────

def _libgen_candidate(doi: str, email: str | None) -> dict | None:
    """Try LibGen Sci-Mag mirrors and return the first matching download candidate."""
    for mirror in ("vg", "gl", "la", "bz"):
        # Pre-ping the mirror to skip dead ones quickly
        if not _ping_url(f"https://libgen.{mirror}/", timeout=4):
            continue
        search_url = (
            f"https://libgen.{mirror}/scimag/?"
            + urllib.parse.urlencode({"s": doi})
        )
        try:
            headers = {"User-Agent": f"engg-skills/0.1 ({email or 'mailto optional'})"}
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
            continue

        download_url = None

        # Strategy 1: link containing get.php or ads.php
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

        # Strategy 2: library.lol direct link
        if not download_url:
            m = re.search(
                r'["\'](https?://(?:download\.)?library\.lol/[^"\']+)["\']',
                html, re.IGNORECASE,
            )
            if m:
                download_url = m.group(1)

        # Strategy 3: any .pdf link in the page
        if not download_url:
            m = re.search(r'["\'](https?://[^"\']+\.pdf)["\']', html, re.IGNORECASE)
            if m:
                download_url = m.group(1)

        if download_url:
            return {
                "source": f"libgen.{mirror}",
                "pdf_url": download_url,
                "landing_page_url": search_url,
                "license": None,
                "version": "publisher",
                "is_oa": False,
                "host_type": "libgen-mirror",
            }
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve PDF URLs for a DOI (OA + mirrors)")
    parser.add_argument("--doi", required=True)
    parser.add_argument("--email", help="Contact email for polite API access and Unpaywall lookup")
    parser.add_argument("--download-dir", default="pdf")
    parser.add_argument("--no-download", action="store_true", help="Resolve candidates without downloading")
    parser.add_argument("--no-scihub", action="store_true", help="Skip scihub-cli download attempt")
    parser.add_argument("--no-libgen", action="store_true", help="Skip LibGen mirror attempts")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=[
            "https://docs.openalex.org/",
            "https://unpaywall.org/products/api",
            "https://sci-hub.se/about",
            "https://libgen.is/",
        ],
        extra_notes=(
            "Tries OA repositories first, then Sci-Hub / LibGen mirrors. "
            "Sci-Hub and LibGen are third-party services — review their terms "
            "and your local copyright regulations before use."
        ),
    )

    doi = _normalise_doi(args.doi)
    safe_inputs = {**vars(args), "doi": doi, "email": "<provided>" if args.email else None}
    try:
        # 1 ── OA repositories (OpenAlex + Unpaywall) ──
        openalex_record, openalex = _openalex_candidates(doi, args.email)
        unpaywall_record, unpaywall = _unpaywall_candidates(doi, args.email)
        oa_candidates = _dedupe_candidates(openalex + unpaywall)
        safe_oa = [c for c in oa_candidates if c.get("safe_url")]

        download = None
        selected_source = None
        selected_pdf_url = None
        output_path = Path(args.download_dir) / _filename_from_doi(doi)

        # Try all safe OA candidates in order
        if safe_oa and not args.no_download:
            for candidate in safe_oa:
                try:
                    download = _download_pdf(candidate["pdf_url"], output_path, args.email)
                    selected_source = candidate.get("source", "open-access")
                    selected_pdf_url = candidate["pdf_url"]
                    break
                except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
                    continue

        # 2 ── Sci-Hub (via scihub-cli) ──
        if not download and not args.no_download and not args.no_scihub:
            scihub = _scihub_cli_download(doi, output_path, args.email)
            if scihub:
                download = scihub.get("download")
                selected_source = scihub["source"]
                selected_pdf_url = scihub.get("pdf_url")
                oa_candidates.append(scihub)

        # 3 ── LibGen mirror fallback ──
        if not download and not args.no_download and not args.no_libgen:
            libgen = _libgen_candidate(doi, args.email)
            if libgen and libgen.get("pdf_url"):
                try:
                    download = _download_pdf(libgen["pdf_url"], output_path, args.email)
                    selected_source = libgen["source"]
                    selected_pdf_url = libgen["pdf_url"]
                    libgen["safe_url"] = True
                    oa_candidates.append(libgen)
                except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
                    pass

        results = {
            "doi": doi,
            "openalex_id": (openalex_record or {}).get("id"),
            "title": (openalex_record or {}).get("title") or (unpaywall_record or {}).get("title"),
            "is_oa": (openalex_record or {}).get("open_access", {}).get("is_oa") if openalex_record else (unpaywall_record or {}).get("is_oa"),
            "candidates": oa_candidates,
            "source": selected_source,
            "selected_pdf_url": selected_pdf_url,
            "download": download,
            "resolution_path": "OA → scihub-cli → LibGen (first successful download wins)",
        }
        warnings = []
        if not oa_candidates:
            warnings.append("No PDF candidate was found from any source (OA repositories, Sci-Hub, or LibGen).")
        if oa_candidates and not download:
            warnings.append("PDF candidate URLs were found but none could be downloaded successfully.")
        if args.no_download:
            warnings.append("PDF download skipped because --no-download was set.")

        data = result_envelope(
            skill=SKILL,
            inputs=safe_inputs,
            results=results,
            warnings=warnings,
            sources=[
                "https://docs.openalex.org/",
                "https://unpaywall.org/products/api",
                "https://sci-hub.se/",
                "https://libgen.is/",
            ],
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

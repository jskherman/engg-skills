---
name: literature-search-engineering
description: >-
  Search, screen, retrieve PDFs, and build literature-review matrices for
  engineering, applied-science, statistics, and physics topics using scholarly
  indexes (OpenAlex, Crossref, arXiv, Semantic Scholar, CORE, Scopus, PubMed Central,
  Google Scholar) and DOI-based PDF retrieval through open-access repositories
  and Sci-Hub / LibGen mirror portals. Use when the user needs a reproducible
  literature pull, source inventory, citation-trail expansion, PDF retrieval,
  or a structured review synthesis.
version: 3.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+, uv,
  and network access to the selected scholarly services are required for
  bundled scripts. Some services require an API key or a contact email for
  authenticated or polite access.
metadata:
  hermes:
    tags: [engineering, literature-search, research, review, open-access, sci-hub, libgen]
    category: research
---

# Engineering Literature Search and Review

## Overview

This skill supports reproducible literature search and review workflows for
engineering and applied-science tasks. It searches metadata services, records
queries, resolves DOI-linked metadata, retrieves PDFs through open-access
repositories and Sci-Hub / LibGen mirrors, and builds a review matrix for
manual or agent-assisted synthesis.

The retrieval pipeline cascades: open-access repositories first, then
Sci-Hub mirrors, then LibGen. This maximises coverage for engineering
literature that may be behind paywalls.

## Prerequisites

1. `uv` available.
2. Network access to the selected public APIs or scholarly websites.
3. A contact email for polite API access where requested.
4. Optional API keys for services that require or strongly prefer them, such
   as Semantic Scholar, CORE, or Unpaywall.
5. A project folder with `search/`, `pdf/`, and `review/` subfolders when the
   workflow is more than a quick one-off search.

## When to Use

- Finding peer-reviewed papers, preprints, reports, theses, or open repository
  copies for a technical basis.
- Conducting a broad or targeted literature review on engineering,
  statistics, physics, modelling, or process-design topics.
- Expanding from seed papers by DOI, author, venue, reference list, or citing
  works.
- Downloading PDFs by DOI using OA repositories, Sci-Hub mirrors
  (sci-hub.{ee,st,su,vg}), or LibGen Sci-Mag mirrors
  (libgen.{vg,gl,la,bz}).
- Building a review matrix with search source, DOI, access status, screening
  decision, method quality, key findings, and limitations.

## Don't use for

- Treating search snippets or abstracts as if the full paper was reviewed.
- Claiming a systematic review without a search protocol, inclusion criteria,
  exclusion criteria, deduplication method, and search date.
- Citing papers solely because they have high citation counts.
- Copying copyrighted article text into reports beyond permitted quotation or
  license terms.
- Redistributing downloaded PDFs outside of personal research or educational
  fair-use contexts.

## Utility Scripts

Run scripts from the skill directory or pass paths explicitly.

### Metadata Search

- `uv run scripts/search_openalex.py --query "amine treating mercaptan LPG" --limit 20 --mailto name@example.com --output search/openalex.json`
- `uv run scripts/search_crossref.py --query "Peng Robinson volume translation hydrocarbons" --limit 20 --mailto name@example.com --output search/crossref.json`
- `uv run scripts/search_arxiv.py --query "physics informed neural networks heat transfer" --limit 20 --output search/arxiv.json`
- `uv run scripts/search_semantic_scholar.py --query "design of experiments chemical process optimization" --limit 20 --api-key "$S2_API_KEY" --output search/semantic_scholar.json`
- `uv run scripts/search_core.py --query "mercaptan extraction LPG caustic" --limit 20 --api-key "$CORE_API_KEY" --output search/core.json`
- `uv run scripts/search_scopus.py --keywords "amine treating mercaptan LPG" --count 20 --api-key "$ELSEVIER_API_KEY" --output search/scopus.json`
- `uv run scripts/search_scopus.py --doi 10.1016/j.ces.2020.115678 --api-key "$ELSEVIER_API_KEY" --output search/scopus_doi.json`
- `uv run scripts/search_scopus.py --query "TITLE-ABS-KEY(mercaptan) AND DOI(10.1000/xyz)" --api-key "$ELSEVIER_API_KEY" --output search/scopus_raw.json`

### PDF Retrieval

- `uv run scripts/resolve_open_access_pdf.py --doi 10.1016/j.ces.2020.115678 --email name@example.com --download-dir pdf --output search/oa_pdf.json`
  (Cascade: OA → Sci-Hub → LibGen; first successful download wins)
- `uv run scripts/download_doi_pdf.py --doi 10.1016/j.ces.2020.115678 --email name@example.com --download-dir pdf --output search/doi_pdf.json`
  (Dedicated DOI-to-PDF via Sci-Hub / LibGen mirrors with OA fallback)

### Review Matrix

- `uv run scripts/build_review_matrix.py --inputs search/openalex.json search/semantic_scholar.json search/arxiv.json --output review/matrix.json --markdown-output review/matrix.md`

## Procedure

1. Define the review question in one sentence. For engineering work, include
   process, material, equipment, method, measured variable, and required
   decision.
2. Write inclusion and exclusion criteria before searching. Record dates,
   document types, disciplines, languages, minimum metadata fields, and whether
   preprints are allowed.
3. Run at least two complementary metadata searches. Use OpenAlex or Crossref
   for broad DOI metadata, Semantic Scholar for citation-neighbour discovery,
   arXiv for preprints, CORE for open-access repository aggregation, Scopus
   for citation tracking and journal-level metrics, and Google Scholar
   manually when API coverage misses grey literature.
4. Export every search result with the query string, source, date, limit, and
   filters. Do not merge hits without keeping source provenance.
5. Deduplicate by DOI first, then by normalized title and year. Keep conflicts
   visible when title, year, journal, or DOI disagree across sources.
6. Resolve and download PDFs by DOI. The cascade is:
   - OpenAlex / Unpaywall OA locations (lawful OA repositories)
   - Sci-Hub mirrors: sci-hub.{ee,st,su,vg}
   - LibGen Sci-Mag mirrors: libgen.{vg,gl,la,bz}
   Store DOI, landing page, PDF URL, retrieval source, license/OA version
   (if available), and retrieval date.
7. Screen title and abstract first; then screen full text only for included or
   maybe-included papers. Mark reasons for exclusion.
8. Build the review matrix. Separate bibliographic metadata, study design,
   methods, data basis, equations/correlations, validation scope, assumptions,
   limitations, and claims relevant to the engineering decision.
9. Synthesize by evidence class instead of by paper order: standards or
   authoritative handbooks, peer-reviewed experiments, validated models,
   preprints, theses, vendor notes, and review articles.
10. Report the final search protocol, exact queries, databases, dates,
    inclusion/exclusion criteria, deduplication method, number of records, and
    access status for every cited source.

## Quality Gates

- Every claim in the final review must trace to a row in the review matrix.
- Every paper row must include at least title, year, source, DOI or stable URL,
  access status, screening decision, and reason.
- Full-text findings must be labelled as full-text reviewed; abstract-only
  findings must be labelled as abstract-only.
- PDF downloads must start with the `%PDF` magic header and be stored with
  source provenance (OA repository, Sci-Hub mirror, or LibGen mirror).
- For engineering formulas, correlations, parameters, or threshold values,
  record the equation number or page number when available; otherwise mark the
  value as unverified.

## Pitfalls

- Using Google Scholar hit counts as a reproducible evidence measure. Scholar
  is useful for discovery, but query results are not stable enough for a strict
  audit trail.
- Treating OpenAlex or Semantic Scholar citation counts as authoritative.
  Citation metadata varies by source and update cycle.
- Sci-Hub and LibGen mirrors can change or go offline. The scripts try
  multiple mirror domains in sequence, but no single mirror is guaranteed.
- Mixing preprints and peer-reviewed papers without version labels.
- Ignoring retractions, corrections, expressions of concern, or superseded
  preprint versions.
- Letting review articles dominate when the engineering decision depends on
  primary experimental data or validated correlations.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.
- For literature workflows, additionally confirm that every downloaded PDF URL is recorded, the file starts with `%PDF`, the download source is tracked, and the review matrix preserves the original search provenance.

## References

- `references/query_strategies.md` — Boolean, field-specific, and source-specific search strategy notes.
- `references/literature_review_protocol.md` — Reproducible screening, deduplication, retrieval, and synthesis protocol.
- OpenAlex API docs: https://docs.openalex.org/
- Crossref REST API docs: https://api.crossref.org/
- arXiv API docs: https://info.arxiv.org/help/api/user-manual.html
- Semantic Scholar Graph API docs: https://api.semanticscholar.org/api-docs/graph
- CORE API docs: https://api.core.ac.uk/docs/v3
- Scopus Search API docs: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
- Unpaywall API docs: https://unpaywall.org/products/api
- Sci-Hub mirrors: https://sci-hub.{ee,st,su,vg}
- LibGen mirrors: https://libgen.{vg,gl,la,bz}
- Google Scholar: https://scholar.google.com

## Anti-Patterns

- Starting with PDF downloads before defining the review question.
- Searching one database only and calling the result comprehensive.
- Citing papers that were not screened beyond title or abstract.
- Storing PDF files without DOI, source URL, download source, and retrieval date.
- Reporting formulas or threshold values from secondary papers when the primary
  source or standard is needed for design.
- Redistributing Sci-Hub or LibGen retrieved PDFs outside of personal fair-use
  research contexts.
---
name: literature-search-engineering
description: >-
  Search, screen, retrieve open-access PDFs, and build literature-review
  matrices for engineering, applied-science, statistics, and physics topics
  using lawful scholarly indexes such as OpenAlex, Crossref, arXiv,
  Semantic Scholar, CORE, PubMed Central, publisher landing pages, DOI
  resolvers, and institutional repositories. Use when the user needs a
  reproducible literature pull, source inventory, citation-trail expansion,
  open-access PDF retrieval, or a structured review synthesis. Do not use
  to bypass publisher access controls, use Sci-Hub or mirror domains, or
  download content without a lawful access basis.
version: 2.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+, uv,
  and network access to the selected scholarly services are required for
  bundled scripts. Some services require an API key or a contact email for
  authenticated or polite access.
metadata:
  hermes:
    tags: [engineering, literature-search, research, review, open-access]
    category: research
---

# Engineering Literature Search and Review

## Overview

This skill supports reproducible literature search and review workflows for
engineering and applied-science tasks. It searches metadata services, records
queries, resolves DOI-linked metadata, identifies lawful open-access full text,
downloads only verified open-access PDFs, and builds a review matrix for manual
or agent-assisted synthesis.

The retrieval boundary is deliberate: use publisher landing pages, DOI records,
open-access repositories, arXiv, PubMed Central, institutional repositories,
CORE records, OpenAlex open-access locations, Semantic Scholar
`openAccessPdf`, and Unpaywall-style OA locations. Do not use Sci-Hub,
LibGen, mirror domains, credential sharing, proxy abuse, or any workflow that
bypasses access controls.

## Prerequisites

1. `uv` available.
2. Network access to the selected public APIs or scholarly websites.
3. A contact email for polite API access where requested.
4. Optional API keys for services that require or strongly prefer them, such
   as Semantic Scholar or CORE.
5. A project folder with `search/`, `pdf/`, and `review/` subfolders when the
   workflow is more than a quick one-off search.

## When to Use

- Finding peer-reviewed papers, preprints, reports, theses, or open repository
  copies for a technical basis.
- Conducting a broad or targeted literature review on engineering,
  statistics, physics, modelling, or process-design topics.
- Expanding from seed papers by DOI, author, venue, reference list, or citing
  works.
- Downloading PDFs only when the metadata identifies a lawful open-access PDF
  URL or the user already has legitimate access.
- Building a review matrix with search source, DOI, access status, screening
  decision, method quality, key findings, and limitations.

## Don't use for

- Downloading paywalled papers through Sci-Hub, LibGen, mirror portals, leaked
  URLs, institutional proxy abuse, or credential sharing.
- Treating search snippets or abstracts as if the full paper was reviewed.
- Claiming a systematic review without a search protocol, inclusion criteria,
  exclusion criteria, deduplication method, and search date.
- Citing papers solely because they have high citation counts.
- Copying copyrighted article text into reports beyond permitted quotation or
  license terms.

## Utility Scripts

Run scripts from the skill directory or pass paths explicitly.

- `uv run scripts/search_openalex.py --query "amine treating mercaptan LPG" --limit 20 --mailto name@example.com --output search/openalex.json`
- `uv run scripts/search_crossref.py --query "Peng Robinson volume translation hydrocarbons" --limit 20 --mailto name@example.com --output search/crossref.json`
- `uv run scripts/search_arxiv.py --query "physics informed neural networks heat transfer" --limit 20 --output search/arxiv.json`
- `uv run scripts/search_semantic_scholar.py --query "design of experiments chemical process optimization" --limit 20 --api-key "$S2_API_KEY" --output search/semantic_scholar.json`
- `uv run scripts/resolve_open_access_pdf.py --doi 10.48550/arXiv.2205.01833 --email name@example.com --download-dir pdf --output search/oa_pdf.json`
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
   arXiv for preprints, CORE or repository search for open-access copies, and
   Google Scholar manually when API coverage misses grey literature.
4. Export every search result with the query string, source, date, limit, and
   filters. Do not merge hits without keeping source provenance.
5. Deduplicate by DOI first, then by normalized title and year. Keep conflicts
   visible when title, year, journal, or DOI disagree across sources.
6. Resolve open-access PDFs by DOI or repository metadata. Download only if a
   public OA PDF URL is present or the user confirms lawful access. Store DOI,
   landing page, PDF URL, license, OA version, and retrieval date.
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
- PDF downloads must come from OA repositories, publisher OA links, arXiv,
  PubMed Central, institutional repositories, or user-supplied lawful files.
- For engineering formulas, correlations, parameters, or threshold values,
  record the equation number or page number when available; otherwise mark the
  value as unverified.

## Pitfalls

- Using Google Scholar hit counts as a reproducible evidence measure. Scholar
  is useful for discovery, but query results are not stable enough for a strict
  audit trail.
- Treating OpenAlex or Semantic Scholar citation counts as authoritative.
  Citation metadata varies by source and update cycle.
- Downloading a PDF URL without checking whether it is an open-access copy.
- Mixing preprints and peer-reviewed papers without version labels.
- Ignoring retractions, corrections, expressions of concern, or superseded
  preprint versions.
- Letting review articles dominate when the engineering decision depends on
  primary experimental data or validated correlations.

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.
- For literature workflows, additionally confirm that every downloaded PDF URL is recorded, the file starts with `%PDF`, the source domain is not an access-control bypass service, and the review matrix preserves the original search provenance.

## References

- `references/query_strategies.md` — Boolean, field-specific, and source-specific search strategy notes.
- `references/literature_review_protocol.md` — Reproducible screening, deduplication, retrieval, and synthesis protocol.
- OpenAlex API docs: https://docs.openalex.org/
- Crossref REST API docs: https://api.crossref.org/
- arXiv API docs: https://info.arxiv.org/help/api/user-manual.html
- Semantic Scholar Graph API docs: https://api.semanticscholar.org/api-docs/graph
- CORE API docs: https://api.core.ac.uk/docs/v3
- Unpaywall API docs: https://unpaywall.org/products/api

## Anti-Patterns

- Starting with PDF downloads before defining the review question.
- Searching one database only and calling the result comprehensive.
- Citing papers that were not screened beyond title or abstract.
- Storing PDF files without DOI, source URL, access status, and retrieval date.
- Using Sci-Hub or mirror portals as a normal retrieval path.
- Reporting formulas or threshold values from secondary papers when the primary
  source or standard is needed for design.

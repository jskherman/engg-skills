---
name: literature-search-engineering
description: >-
  Build OpenAlex and Crossref query URLs / arguments for chemical and
  process-engineering literature searches, with DOI / metadata tracking
  and per-source terms reminders. Use when the user needs a literature
  pull for a design basis, a property regression source, or a citation
  for a method. Don't use to download full-text articles (publisher
  paywalls and terms apply) or to perform AI-assisted summarization of
  retrieved content (a separate skill).
version: 1.0.0
license: Apache-2.0
compatibility: >-
  Compatible with Agent Skills clients and Hermes Agent; Python 3.11+ and uv
  are required for bundled Python scripts.
metadata:
  hermes:
    tags: [engineering, literature-search, research, literature, search]
    category: research
---

# Engineering Literature Search

## Overview

This skill helps you build well-formed search queries for the OpenAlex
and Crossref public APIs (and provides reminders for arXiv and PubMed
when needed). The actual HTTP call is performed by the script, but the
purpose is to deliver:

- A clean OpenAlex / Crossref query URL.
- A short, structured JSON of hits (title, authors, year, DOI, journal).
- A reminder of the source's terms of use and rate-limit policy.

## Prerequisites

1. `uv` available.
2. On first use, the script writes `LICENSE_NOTIFICATION.txt` reminding
   you to check the OpenAlex and Crossref API terms.

## When to Use

- Looking for a property regression reference for a design.
- Finding a published method behind a vendor correlation.
- Pulling a short list of recent papers on a niche topic for a literature
  survey.

## Don't use for

- Downloading full-text articles (publisher terms apply).
- AI-driven summarisation of paper content (different skill).
- Patent search (use a patent database).

## Utility Scripts

- `uv run scripts/search_openalex.py --query "merox caustic mercaptan extraction" --rows 10 --output /tmp/oa.json`
- `uv run scripts/search_crossref.py --query "Peng-Robinson volume translation hydrocarbon" --rows 10 --output /tmp/cr.json`

## Procedure

1. Define the query precisely; include the chemistry / unit operation
   and any domain qualifier.
2. Run the search; inspect the top 10 hits.
3. If results are noisy, refine: add a year filter, a journal filter, or
   exclude unrelated subject codes.
4. Resolve DOIs and add to your literature inventory.
5. Verify each source's licence before quoting figures or text.

## Pitfalls

- Quoting an abstract without naming the DOI and access status (open
  vs subscription).
- Confusing OpenAlex IDs (W…) with DOIs.
- Ignoring rate limits (Crossref: 50 req/s polite; OpenAlex: 10 req/s
  free tier).
- Reporting "n hits" without the query string and date filter that
  produced them.
- Using broad search terms (e.g. "amine") and expecting a clean list.
- Forgetting to set a UA / contact email for "polite pool" Crossref
  access.
- Treating OpenAlex citation counts as ground truth; they aggregate
  multiple sources with varying recency.

## Fallback Strategies

- If OpenAlex returns nothing for a specific term, try Crossref (broader
  scope of journals).
- If both return little, expand to Google Scholar (manual) or arXiv (for
  recent preprints in computational chemistry / process modelling).

## Verification

- Run the listed script with representative inputs and an `--output` file when a deterministic calculation is available.
- Confirm the JSON result contains `ok: true`, expected units, and no unhandled warnings.
- Check result magnitudes against the stated assumptions, references, and a hand calculation or known operating range before reporting them.

## References

- `references/query_strategies.md` — Boolean and field-specific tricks
  for OpenAlex and Crossref.
- OpenAlex docs: https://docs.openalex.org/
- Crossref docs: https://api.crossref.org/

## Anti-Patterns

- Pulling 100 hits and citing them all without quality filtering.
- Using a search hit's abstract text directly in a report without
  reviewing the licence.
- Forgetting to cite the search query and date when reporting a
  literature pull.

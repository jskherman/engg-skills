# Query Strategies

Use specific process names, material names, unit operation terms, and synonyms.
Prefer DOI, title, authors, year, source, access status, landing page, and
open-access URL in summaries.

## Query Construction

Start with a precise engineering question and split it into concepts:

- System: unit operation, equipment, chemical system, material, catalyst,
  instrument, or statistical method.
- Phenomenon: mass transfer, reaction, fouling, solubility, phase equilibrium,
  reliability, bias, uncertainty, or causal effect.
- Outcome: property, correlation, design parameter, operating limit, validation
  metric, failure mode, or economic objective.
- Context: refinery, petrochemical, water, gas processing, pharmaceutical,
  laboratory, pilot plant, computational study, or field data.

Use blocks of synonyms rather than one broad query. Example:

```text
("mercaptan" OR "thiol" OR "RSH") AND ("LPG" OR "liquefied petroleum gas") AND ("caustic extraction" OR Merox)
```

For physical-property and design-method searches, add the model or method name:

```text
("Peng-Robinson" OR PRSV OR "volume translation") AND (propane OR propylene OR LPG) AND density
```

## Source Selection

- OpenAlex: broad scholarly metadata, DOI lookup, open-access locations,
  citation counts, topics, source filtering, repository indicators.
- Crossref: DOI metadata, publisher landing pages, references, registered
  metadata, funder and relation fields.
- Semantic Scholar: citation-neighbour discovery, influential citations,
  open-access PDF metadata, abstracts where available.
- arXiv: preprints in physics, statistics, computer science, applied math,
  quantitative biology, and related modelling areas.
- CORE: open-access repository aggregation and full-text search; requires
  an API key. Excellent for locating repository copies and institutional
  OA deposits. Use with `--fulltext-only` to filter for downloadable content.
- Google Scholar: manual discovery, backward/forward citation chasing, theses,
  reports, and items missed by structured APIs. Record the exact query and
  date; do not rely on hit counts. Google Scholar has no public API — search
  manually and import results into the review matrix.
- Scopus: Elsevier's abstract and citation database; excellent for engineering
  and applied-science literature with robust citation tracking, author profiles,
  and journal-level metrics. Requires an Elsevier API key. Supports field-code
  queries (TITLE-ABS-KEY, DOI, TITLE, AUTH, etc.), Boolean operators, and
  sort-by-citation-count. Use `--keywords` for topic searches or `--query` for
  raw Scopus syntax.
- PubMed Central: biomedical and some chemical/biochemical engineering full
  text where relevant.
- Publisher and society pages: final landing page, version, errata,
  correction, and license confirmation.
- Sci-Hub mirrors (sci-hub.{ee,st,su,vg}): retrieve paywalled PDFs by DOI
  for personal research use.
- LibGen Sci-Mag mirrors (libgen.{vg,gl,la,bz}): alternative DOI-based
  retrieval for articles not available through Sci-Hub.

## Search Escalation

1. Run a broad OpenAlex or Crossref query for DOI-bearing literature.
2. Run a narrow query with exact phrases and domain terms.
3. Add method-specific terms, author names, or seminal paper titles.
4. Use Semantic Scholar or Google Scholar for citation-neighbour expansion.
5. Search arXiv when the field is computational, mathematical, statistical,
   physics-related, or fast-moving.
6. Search CORE, institutional repositories, and PubMed Central for lawful
   full-text availability.
7. Use DOI lookup for every high-value record before screening full text.
8. When a paper is behind a paywall, retrieve it via `download_doi_pdf.py`
   or `resolve_open_access_pdf.py` which cascade through Sci-Hub and
   LibGen mirrors.

## Audit Trail Fields

Record these fields for every search batch:

- Database or website.
- Exact query string.
- Filters, sort order, and date range.
- Search date and timezone.
- Result limit and pagination range.
- API endpoint or manual-search URL when practical.
- Number of raw hits exported.
- Deduplication rule.
- Notes on known gaps, such as API key limits or manual Google Scholar use.

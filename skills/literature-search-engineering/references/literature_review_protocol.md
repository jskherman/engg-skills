# Literature Review Protocol

## Review Setup

Write the review question before searching. A usable engineering question names
what decision the review must support, not only the topic. Example:

```text
Which published correlations or validated models support preliminary estimation
of LPG mercaptan extraction performance in caustic/Merox service, and what
operating range limits their use?
```

Define inclusion and exclusion criteria before looking at results. At minimum,
state accepted document types, year range, language, required metadata, whether
preprints are allowed, and what counts as direct evidence.

## Search and Retrieval Workflow

1. Search at least two structured metadata sources.
2. Export raw results before manual screening.
3. Deduplicate by DOI. If DOI is absent, deduplicate by normalized title,
   first author, and publication year.
4. Resolve DOI metadata and access status.
5. Retrieve full text only through lawful routes: publisher OA link, arXiv,
   PubMed Central, institutional repository, CORE repository record, author
   accepted manuscript, public report repository, user-provided file, or other
   legitimate access held by the user.
6. Do not use Sci-Hub, mirror portals, leaked PDFs, institutional proxy abuse,
   shared credentials, or tools designed to bypass access controls.
7. Store the PDF with adjacent metadata: DOI, title, source URL, PDF URL,
   license or access basis, retrieval date, and checksum if practical.

## Screening Levels

Use three levels of screening:

- Title/abstract screening: decide `include`, `exclude`, or `maybe` and record
  one reason.
- Full-text screening: confirm whether the paper directly supports the review
  question.
- Evidence extraction: record only claims that are tied to the engineering
  decision, formula, experimental range, validation data, uncertainty, or
  limitation.

## Review Matrix Columns

Use these columns for a technical review matrix:

- `record_id`
- `source_database`
- `query`
- `title`
- `authors`
- `year`
- `doi`
- `stable_url`
- `pdf_url`
- `access_status`
- `document_type`
- `version`
- `screening_decision`
- `screening_reason`
- `evidence_class`
- `system_or_material`
- `method_or_correlation`
- `operating_range`
- `key_result`
- `limitations`
- `relevance_to_decision`
- `verification_notes`

## Synthesis Rules

Synthesize by evidence class and applicability, not by citation count.
Separate:

1. Standards, codes, and authoritative handbooks.
2. Primary experimental papers.
3. Validated models and correlations.
4. Review papers.
5. Preprints and theses.
6. Vendor papers and application notes.
7. Unverified web sources.

For safety-critical engineering use, mark standards and handbooks as requiring
primary-text procurement and edition verification. Do not quote clause numbers,
tables, or design thresholds unless the primary source was checked.

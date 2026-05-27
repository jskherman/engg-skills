# JSON Result Envelope Schema

All deterministic scripts in this repository write a single JSON file to
`--output`. The structure is created by
`engg_skills_common.io.result_envelope`.

```json
{
  "ok": true,
  "skill": "skill_name_in_snake_case",
  "inputs": { "...": "all parsed CLI arguments" },
  "results": { "...": "calculation outputs, plain JSON-serialisable" },
  "assumptions": ["list of plain-text assumption statements"],
  "warnings": [
    "Preliminary engineering calculation only. ...",
    "Any additional skill-specific warnings."
  ],
  "source_notice": "Either the default `SOURCE_NOTICE` or the `license_notice_for(<skill>)` string.",
  "sources": [
    "Library names",
    "Public references (textbooks, standards by number)"
  ]
}
```

## Field guidance

- **ok**: `true` on success, `false` on caught error.
- **skill**: the snake_case skill name; do not invent.
- **inputs**: usually `vars(args)`. Strip secrets if any.
- **results**: keep the keys descriptive (`density_kg_m3` not `rho`); units
  in the key name.
- **assumptions**: human-readable list; include the EOS / property method
  chosen, kij assumptions, etc.
- **warnings**: the `PRELIMINARY_ENGINEERING_WARNING` is added
  automatically; append domain-specific warnings.
- **source_notice**: if the script uses `write_license_notification`,
  override the default `SOURCE_NOTICE` with `license_notice_for(<skill>)`.
- **sources**: short tags identifying the underlying methods and libraries.

## Error envelope

On caught exception:

```json
{
  "ok": false,
  "skill": "skill_name",
  "inputs": { "...": "..." },
  "results": { "error": "<exception message>" },
  "assumptions": [],
  "warnings": ["Preliminary engineering calculation only. ..."],
  "source_notice": "...",
  "sources": []
}
```

Always write the error envelope to `--output` even on failure so downstream
agents can read the result deterministically.

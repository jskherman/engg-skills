# Python CLI Script Template

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["chemicals>=1.5"]  # add only what THIS script needs
# ///
"""<one-line description>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"
sys.path.insert(0, str(COMMON_ROOT))

from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "<skill_name_snake_case>"
SKILL_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="<short description>")
    p.add_argument("--input-a", type=float, required=True)
    p.add_argument("--output", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["<upstream terms URL>"],
        library_attributions=["<lib name (author) — license>"],
        standards_referenced=["<standard number — title>"],  # optional
    )
    try:
        res = {"answer": args.input_a * 2}  # replace with real call
        data = result_envelope(
            skill=SKILL,
            inputs=vars(args),
            results=res,
            assumptions=["<assumption 1>", "<assumption 2>"],
            sources=["<source 1>"],
        )
        data["source_notice"] = license_notice_for(SKILL)
        path = write_json(data, args.output)
        print(f"Success. JSON written to: {path}")
        return 0
    except Exception as exc:
        write_json(
            result_envelope(skill=SKILL, inputs=vars(args), results={"error": str(exc)}, ok=False),
            args.output,
        )
        print(f"Error. JSON written to: {args.output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

## Conventions

- PEP-723 dependencies are per-script: declare only what the script needs.
- The shared library is imported via the `sys.path.insert` pattern; do not
  install `engg_skills_common` separately.
- Use `--<long-form>` flags throughout; argparse converts hyphens to
  underscores via `dest=`.
- One success message on stdout; everything else goes in the JSON envelope.
- Errors are caught and written to the envelope; the script returns 1
  on error so the caller can detect failure.

"""Shared warning strings, source notices, and license notification helpers.

The LICENSE_NOTIFICATION pattern mirrors Google DeepMind's `science-skills`
convention: each skill drops a `LICENSE_NOTIFICATION.txt` file the first time
it runs so users get a one-time, dated reminder of upstream licensing terms
(Caleb Bell libraries, IAPWS, API/ASME/ISA/GPSA standards referenced, etc.).
The file is never read back into the agent context.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

PRELIMINARY_ENGINEERING_WARNING = (
    "Preliminary engineering calculation only. Verify inputs, units, "
    "correlations, safety factors, applicable standards, and site-specific "
    "constraints before design or operations use."
)

SOURCE_NOTICE = (
    "Original implementation using common engineering equations and public "
    "domain physical relationships; no proprietary standard text or tables "
    "are included."
)

SAFETY_RELIEF_NOTICE = (
    "Relief device, vessel, and safety-critical sizing here is a preliminary "
    "screening calculation. Final sizing must follow the latest editions of "
    "API 520/521/526, ASME BPVC Section VIII/XIII, jurisdictional codes, "
    "and qualified pressure-relief engineering review."
)

STATISTICAL_INFERENCE_NOTICE = (
    "Reported intervals depend on stated distributional and independence "
    "assumptions. For autocorrelated process data, censored lab data, or "
    "compositional data, the intervals will understate uncertainty unless "
    "the matching specialized method is used."
)


def write_license_notification(
    *,
    skill_dir: str | Path,
    skill_name: str,
    terms_urls: list[str],
    library_attributions: list[str] | None = None,
    standards_referenced: list[str] | None = None,
    extra_notes: str | None = None,
) -> Path | None:
    """Create LICENSE_NOTIFICATION.txt if it does not exist.

    Returns the path written, or None if the file already exists. Scripts call
    this on the first invocation only; the presence of the file signals that
    the user has been notified at least once. The file content is informational
    and is not meant to be re-read by the agent.
    """

    target = Path(skill_dir) / "LICENSE_NOTIFICATION.txt"
    if target.exists():
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        f"Skill: {skill_name}",
        f"First-use notification (UTC): {timestamp}",
        "",
        "Review the upstream terms before any design, operations, or",
        "regulated/commercial use of outputs from this skill:",
        "",
    ]
    for url in terms_urls:
        lines.append(f"  - {url}")
    if library_attributions:
        lines.append("")
        lines.append("Underlying Python libraries (check each license):")
        for entry in library_attributions:
            lines.append(f"  - {entry}")
    if standards_referenced:
        lines.append("")
        lines.append("Engineering standards referenced (text NOT reproduced):")
        for entry in standards_referenced:
            lines.append(f"  - {entry}")
    if extra_notes:
        lines.append("")
        lines.append(extra_notes.rstrip())
    lines.append("")
    lines.append(
        "This file is a one-time attribution record. Delete it to force the "
        "notification to be regenerated."
    )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def license_notice_for(skill_name: str) -> str:
    """Standard short attribution string for the JSON `source_notice` field."""

    return (
        f"Skill `{skill_name}` first-use license notice written to "
        "LICENSE_NOTIFICATION.txt in the skill directory. Review listed "
        "library and standards terms before regulated or commercial use."
    )

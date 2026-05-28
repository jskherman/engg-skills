"""Shared utilities for Engineering Skills CLI scripts.

This package centralises pure-Python helpers (math, validation, JSON I/O)
and thin wrappers around Caleb Bell's `thermo`, `chemicals`, `fluids`, and
`ht` libraries. Heavy optional dependencies (`pymc`, `statsmodels`, `pgmpy`)
are imported lazily inside the skills that need them and are not re-exported
here, so `import engg_skills_common` is cheap.
"""

from .notices import (
    PRELIMINARY_ENGINEERING_WARNING,
    SAFETY_RELIEF_NOTICE,
    SOURCE_NOTICE,
    STATISTICAL_INFERENCE_NOTICE,
    license_notice_for,
    write_license_notification,
)

__all__ = [
    "PRELIMINARY_ENGINEERING_WARNING",
    "SAFETY_RELIEF_NOTICE",
    "SOURCE_NOTICE",
    "STATISTICAL_INFERENCE_NOTICE",
    "license_notice_for",
    "write_license_notification",
]

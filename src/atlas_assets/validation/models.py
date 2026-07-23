"""Data models for the atlas-assets spec validator."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Severity(str, Enum):
    """Severity level of a validation finding."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    """A single validation result.

    ``asset`` is the ``<type>/<name>/<version>`` (or shorter) identifier
    the finding applies to; ``path`` is the offending item when relevant.
    """

    severity: Severity
    code: str
    message: str
    asset: str = ""
    path: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Return a JSON-serializable representation of the finding."""
        return {
            "severity": self.severity.value,
            "code": self.code,
            "asset": self.asset,
            "path": self.path,
            "message": self.message,
        }


@dataclass
class Report:
    """Collection of findings produced by a validation run."""

    root: str = ""
    findings: List[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        """Append a finding to the report."""
        self.findings.append(finding)

    @property
    def errors(self) -> List[Finding]:
        """Return findings with error severity."""
        return [f for f in self.findings if f.severity is Severity.ERROR]

    @property
    def warnings(self) -> List[Finding]:
        """Return findings with warning severity."""
        return [f for f in self.findings if f.severity is Severity.WARNING]

    @property
    def has_errors(self) -> bool:
        """Return whether the report contains any errors."""
        return any(f.severity is Severity.ERROR for f in self.findings)

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serializable representation of the report."""
        return {
            "root": self.root,
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
            },
            "findings": [f.to_dict() for f in self.findings],
        }

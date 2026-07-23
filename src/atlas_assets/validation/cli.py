"""Command-line interface for the atlas-assets spec validator."""

import argparse
import json
import sys
from typing import List, Optional

from atlas_assets.validation.models import Report, Severity
from atlas_assets.validation.store import open_store
from atlas_assets.validation.validator import validate

_GLYPH = {Severity.ERROR: "✖", Severity.WARNING: "⚠"}


def _format_text(report: Report) -> str:
    """Render a report as a human-readable, grouped text summary."""
    lines = ["Validating {}".format(report.root), ""]
    if not report.findings:
        lines.append("No issues found.")
        lines.append("")
    else:
        groups: dict = {}
        for finding in report.findings:
            groups.setdefault(finding.asset, []).append(finding)
        for asset in sorted(groups):
            lines.append(asset or "(root)")
            for finding in groups[asset]:
                lines.append(
                    "  {} {}  {}".format(
                        _GLYPH[finding.severity],
                        finding.code,
                        finding.message,
                    )
                )
                if finding.path:
                    lines.append("      {}".format(finding.path))
            lines.append("")
    lines.append(
        "Summary: {} error(s), {} warning(s).".format(
            len(report.errors), len(report.warnings)
        )
    )
    return "\n".join(lines)


def _format_json(report: Report) -> str:
    """Render a report as indented JSON."""
    return json.dumps(report.to_dict(), indent=2)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the validator CLI."""
    parser = argparse.ArgumentParser(
        prog="atlas-assets-validate",
        description=(
            "Validate an atlas-assets tree (local path or s3:// URI) "
            "for spec compliance."
        ),
    )
    parser.add_argument(
        "location",
        help="Local directory path or s3://bucket/prefix URI to validate.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on warnings as well as errors.",
    )
    parser.add_argument(
        "--region",
        default="",
        help="AWS region for s3:// locations (default: us-west-2).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Run the validator CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    store = open_store(args.location, region=args.region)
    report = validate(store)
    if args.format == "json":
        print(_format_json(report))
    else:
        print(_format_text(report))
    if report.has_errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

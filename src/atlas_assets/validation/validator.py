"""Structural spec-compliance validator for atlas-assets trees.

Discovers ``<type>/<name>/<version>/`` assets in a store and checks them
against :mod:`atlas_assets.validation.spec`. Phase 1 covers layout,
required/optional files, naming (as warnings, since naming conventions
are guidelines), version-directory format, JSON parseability, and
shallow manifest-key presence. Content-level validation is out of scope.
"""

import json

from atlas_assets.validation import content as content_rules
from atlas_assets.validation.models import Finding, Report, Severity
from atlas_assets.validation.spec import (
    ASSET_SPECS,
    TOP_LEVEL_DIRS,
    VERSION_RE,
    AssetSpec,
)
from atlas_assets.validation.store import AssetStore


def validate(store: AssetStore, content: bool = False) -> Report:
    """Validate an atlas-assets ``store`` and return a :class:`Report`.

    When ``content`` is true, content-level checks (metadata schema,
    manifest cross-references, terminology CSV, OME-Zarr) run in
    addition to the structural checks.
    """
    report = Report(root=store.location)
    ctx = None
    if content:
        ctx = content_rules.build_context()
        if ctx.models is None:
            report.add(
                Finding(
                    Severity.WARNING,
                    "W100",
                    "Metadata schema validation skipped: aind-data-schema "
                    "is not installed (pip install "
                    "atlas-assets[validate]).",
                )
            )
        if not ctx.zarr_ok:
            report.add(
                Finding(
                    Severity.WARNING,
                    "W101",
                    "OME-Zarr validation skipped: zarr is not installed "
                    "(pip install atlas-assets[validate]).",
                )
            )
    for entry in store.list(""):
        if not entry.is_dir:
            report.add(
                Finding(
                    Severity.WARNING,
                    "W001",
                    "Unexpected file at the store root.",
                    path=entry.name,
                )
            )
        elif entry.name not in TOP_LEVEL_DIRS:
            report.add(
                Finding(
                    Severity.WARNING,
                    "W001",
                    "Unexpected top-level directory not defined in the "
                    "specification.",
                    path=entry.name + "/",
                )
            )
        else:
            _validate_type(
                store, ASSET_SPECS[entry.name], report, content, ctx
            )
    return report


def _validate_type(
    store: AssetStore,
    spec: AssetSpec,
    report: Report,
    content: bool,
    ctx,
) -> None:
    """Validate every asset under a single asset-type directory."""
    for entry in store.list(spec.type_dir):
        asset_name = "{}/{}".format(spec.type_dir, entry.name)
        if not entry.is_dir:
            report.add(
                Finding(
                    Severity.WARNING,
                    "W002",
                    "Unexpected file directly under the asset-type "
                    "directory.",
                    asset=spec.type_dir,
                    path=asset_name,
                )
            )
            continue
        _check_name(spec, entry.name, asset_name, report)
        children = store.list("{}/{}".format(spec.type_dir, entry.name))
        version_dirs = [c for c in children if c.is_dir]
        for stray in (c for c in children if not c.is_dir):
            report.add(
                Finding(
                    Severity.WARNING,
                    "W003",
                    "File found at the asset-name level; files belong "
                    "under a version directory.",
                    asset=asset_name,
                    path="{}/{}".format(asset_name, stray.name),
                )
            )
        if not version_dirs:
            report.add(
                Finding(
                    Severity.ERROR,
                    "E010",
                    "Asset has no version directory.",
                    asset=asset_name,
                )
            )
        for version in version_dirs:
            _validate_version(
                store,
                spec,
                entry.name,
                version.name,
                report,
                content,
                ctx,
            )


def _check_name(
    spec: AssetSpec, name: str, asset_name: str, report: Report
) -> None:
    """Emit naming-convention warnings for an asset name."""
    if spec.name_suffix and not name.endswith(spec.name_suffix):
        report.add(
            Finding(
                Severity.WARNING,
                "W020",
                "Name does not end with the conventional suffix "
                "'{}' (naming is a guideline).".format(spec.name_suffix),
                asset=asset_name,
            )
        )
    if spec.name_regex and not spec.name_regex.search(name):
        report.add(
            Finding(
                Severity.WARNING,
                "W021",
                "Name does not match the conventional pattern "
                "(naming is a guideline).",
                asset=asset_name,
            )
        )


def _validate_version(
    store: AssetStore,
    spec: AssetSpec,
    name: str,
    version: str,
    report: Report,
    content: bool = False,
    ctx=None,
) -> None:
    """Validate the contents of a single asset version directory."""
    asset = "{}/{}/{}".format(spec.type_dir, name, version)
    children = store.list(asset)
    files = {c.name for c in children if not c.is_dir}
    dirs = {c.name for c in children if c.is_dir}

    for required in sorted(spec.required_files):
        if required not in files:
            report.add(
                Finding(
                    Severity.ERROR,
                    "E001",
                    "Missing required file '{}'.".format(required),
                    asset=asset,
                    path="{}/{}".format(asset, required),
                )
            )
    for required in sorted(spec.required_dirs):
        if required not in dirs:
            report.add(
                Finding(
                    Severity.ERROR,
                    "E002",
                    "Missing required directory '{}'.".format(required),
                    asset=asset,
                    path="{}/{}".format(asset, required),
                )
            )
    for conditional in sorted(spec.conditional_files):
        if conditional not in files:
            report.add(
                Finding(
                    Severity.WARNING,
                    "W010",
                    "Missing '{}', which is required if the asset is "
                    "computed.".format(conditional),
                    asset=asset,
                    path="{}/{}".format(asset, conditional),
                )
            )

    if not VERSION_RE.match(version):
        report.add(
            Finding(
                Severity.WARNING,
                "W011",
                "Version directory name is not a recognized format "
                "(expected YYYY, YYYY-MM, or semver).",
                asset=asset,
            )
        )

    _check_unexpected(spec, files, dirs, asset, report)
    _check_required_json(store, spec, files, asset, report)

    if content:
        content_rules.check_version(
            store, spec, asset, files, dirs, ctx, report
        )


def _check_unexpected(
    spec: AssetSpec,
    files: set,
    dirs: set,
    asset: str,
    report: Report,
) -> None:
    """Warn about files/directories not defined for the asset type."""
    if spec.allow_extra:
        return
    known_files = (
        spec.required_files | spec.optional_files | spec.conditional_files
    )
    for name in sorted(files):
        if name in known_files:
            continue
        if any(p.match(name) for p in spec.optional_file_patterns):
            continue
        report.add(
            Finding(
                Severity.WARNING,
                "W030",
                "Unexpected file not defined in the specification.",
                asset=asset,
                path="{}/{}".format(asset, name),
            )
        )
    known_dirs = spec.required_dirs | spec.optional_dirs
    for name in sorted(dirs):
        if name not in known_dirs:
            report.add(
                Finding(
                    Severity.WARNING,
                    "W031",
                    "Unexpected directory not defined in the "
                    "specification.",
                    asset=asset,
                    path="{}/{}/".format(asset, name),
                )
            )


def _check_required_json(
    store: AssetStore,
    spec: AssetSpec,
    files: set,
    asset: str,
    report: Report,
) -> None:
    """Parse required JSON files and check draft manifest keys."""
    for name in sorted(spec.required_files):
        if not name.endswith(".json") or name not in files:
            continue
        path = "{}/{}".format(asset, name)
        try:
            data = json.loads(store.read_text(path))
        except (ValueError, OSError) as exc:
            report.add(
                Finding(
                    Severity.ERROR,
                    "E003",
                    "File is not valid JSON: {}.".format(exc),
                    asset=asset,
                    path=path,
                )
            )
            continue
        if name == "manifest.json" and spec.manifest_keys:
            if not isinstance(data, dict):
                report.add(
                    Finding(
                        Severity.WARNING,
                        "W040",
                        "manifest.json is not a JSON object.",
                        asset=asset,
                        path=path,
                    )
                )
                continue
            for key in sorted(spec.manifest_keys):
                if key not in data:
                    report.add(
                        Finding(
                            Severity.WARNING,
                            "W041",
                            "manifest.json is missing the draft "
                            "minimal key '{}'.".format(key),
                            asset=asset,
                            path=path,
                        )
                    )

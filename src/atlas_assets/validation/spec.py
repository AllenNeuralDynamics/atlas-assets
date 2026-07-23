"""Declarative model of the atlas-assets specification layout.

This encodes the directory/file tables and naming conventions from the
specification so the validator can be driven from data. Only the
structural aspects needed for Phase 1 validation are represented;
content-level rules (schema validation, cross-references, OME-Zarr
metadata, terminology graph checks) are handled separately.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Pattern, Set

# Token allowed in a ``{resolution}`` placeholder, e.g. ``25`` or ``10um``.
_RES = r"[A-Za-z0-9.]+"

# Recognized version-directory formats: ``YYYY``, ``YYYY-MM``, semver,
# or a ``v``-prefixed tag.
VERSION_RE = re.compile(r"^(\d{4}(-\d{2})?|\d+\.\d+\.\d+|v\d+.*)$")


@dataclass(frozen=True)
class AssetSpec:
    """Required/optional contents and naming rules for one asset type."""

    type_dir: str
    required_files: Set[str] = field(default_factory=set)
    required_dirs: Set[str] = field(default_factory=set)
    optional_files: Set[str] = field(default_factory=set)
    optional_dirs: Set[str] = field(default_factory=set)
    # Required only when the asset is computed; reported as a warning
    # when absent because "computed" cannot be determined structurally.
    conditional_files: Set[str] = field(default_factory=set)
    # Optional files matched by pattern (e.g. ``template_{resolution}``).
    optional_file_patterns: List[Pattern] = field(default_factory=list)
    # Draft "minimal required keys" the spec enumerates for a manifest.
    manifest_keys: Set[str] = field(default_factory=set)
    name_suffix: str = ""
    name_regex: Optional[Pattern] = None
    # When True, arbitrary extra files are permitted (e.g. ANTs outputs
    # under coordinate-transformations) and not flagged as unexpected.
    allow_extra: bool = False


ASSET_SPECS = {
    "atlases": AssetSpec(
        type_dir="atlases",
        required_files={"data_description.json", "manifest.json"},
        manifest_keys={
            "coordinate_space",
            "templates",
            "annotation_sets",
            "created",
            "schema_version",
        },
        name_suffix="-atlas",
    ),
    "templates": AssetSpec(
        type_dir="templates",
        required_files={"data_description.json", "manifest.json"},
        required_dirs={"template.ome.zarr"},
        conditional_files={"processing.json"},
        optional_file_patterns=[
            re.compile(r"^template_" + _RES + r"\.nii\.gz$")
        ],
        manifest_keys={
            "coordinate_space",
            "created",
            "schema_version",
        },
        name_suffix="-template",
    ),
    "annotation-sets": AssetSpec(
        type_dir="annotation-sets",
        required_files={"data_description.json", "manifest.json"},
        required_dirs={"annotations.ome.zarr", "annotations.precomputed"},
        optional_dirs={
            "annotations_compressed.ome.zarr",
            "annotations_smooth.precomputed",
        },
        optional_files={"parcellation_volumes.csv"},
        optional_file_patterns=[
            re.compile(r"^annotations_compressed_" + _RES + r"\.nii\.gz$")
        ],
        manifest_keys={
            "name",
            "version",
            "location",
            "schema_version",
            "coordinate_space",
            "terminology",
            "scales",
        },
        name_suffix="-annotation",
    ),
    "terminologies": AssetSpec(
        type_dir="terminologies",
        required_files={
            "data_description.json",
            "manifest.json",
            "terminology.csv",
        },
        optional_files={"terminology.parquet"},
        optional_dirs={"legacy_files"},
        manifest_keys={"name", "version", "location", "schema_version"},
        name_suffix="-terminology",
    ),
    "coordinate-spaces": AssetSpec(
        type_dir="coordinate-spaces",
        required_files={"data_description.json", "manifest.json"},
        manifest_keys={
            "name",
            "version",
            "location",
            "schema_version",
            "origin",
            "spacing",
            "template",
        },
        name_suffix="-space",
    ),
    "coordinate-transformations": AssetSpec(
        type_dir="coordinate-transformations",
        required_files={"data_description.json", "manifest.json"},
        conditional_files={"processing.json"},
        optional_dirs={"coordinate_transformations.ome.zarr"},
        manifest_keys={"source", "target", "directionality"},
        name_regex=re.compile(r".+_to_.+"),
        allow_extra=True,
    ),
}

# The only directories permitted at the store root.
TOP_LEVEL_DIRS = set(ASSET_SPECS)

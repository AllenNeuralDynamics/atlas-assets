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

from atlas_assets import __version__

# Token allowed in a ``{resolution}`` placeholder, e.g. ``25`` or ``10um``.
_RES = r"[A-Za-z0-9.]+"

# Base URL of the rendered specification. A ``described_by`` value is the
# asset type's page under a version of this site, e.g.
# ``https://atlas-assets.readthedocs.io/en/v0.2.0/atlas.html``.
DOCS_BASE_URL = "https://atlas-assets.readthedocs.io/en"

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
    # Whether ``data_description.json`` may declare modalities. A modality
    # records how a volume was acquired, so it belongs only to asset types
    # that are images: templates, and the atlases that compose them.
    # Parcellations, vocabularies, spaces and mappings are not acquisitions.
    allows_modality: bool = False
    # Filename of the specification page describing this asset type. A
    # manifest's ``described_by`` URL must point at this page; see
    # :func:`described_by_url`.
    docs_page: str = ""


ASSET_SPECS = {
    "atlases": AssetSpec(
        type_dir="atlases",
        required_files={"data_description.json", "manifest.json"},
        manifest_keys={
            "coordinate_space",
            "templates",
            "annotation_sets",
            "schema_version",
            "described_by",
        },
        name_suffix="-atlas",
        allows_modality=True,
        docs_page="atlas.html",
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
            "schema_version",
            "described_by",
        },
        name_suffix="-template",
        allows_modality=True,
        docs_page="template.html",
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
            "described_by",
            "coordinate_space",
            "terminology",
            "scales",
        },
        name_suffix="-annotation",
        docs_page="annotation_set.html",
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
        manifest_keys={
            "name",
            "version",
            "location",
            "schema_version",
            "described_by",
        },
        name_suffix="-terminology",
        docs_page="terminology.html",
    ),
    "coordinate-spaces": AssetSpec(
        type_dir="coordinate-spaces",
        required_files={"data_description.json", "manifest.json"},
        manifest_keys={
            "name",
            "version",
            "location",
            "schema_version",
            "described_by",
            "origin",
            "spacing",
            "template",
        },
        name_suffix="-space",
        docs_page="coordinate_space.html",
    ),
    "coordinate-transformations": AssetSpec(
        type_dir="coordinate-transformations",
        required_files={"data_description.json", "manifest.json"},
        conditional_files={"processing.json"},
        optional_dirs={"coordinate_transformations.ome.zarr"},
        manifest_keys={
            "source",
            "target",
            "directionality",
            "described_by",
        },
        name_regex=re.compile(r".+_to_.+"),
        allow_extra=True,
        docs_page="coordinate_transformation.html",
    ),
}

# The only directories permitted at the store root.
TOP_LEVEL_DIRS = set(ASSET_SPECS)


def described_by_url(type_dir: str, version: str = __version__) -> str:
    """Return the canonical ``described_by`` URL for an asset type.

    ``version`` is the specification version the manifest was written
    against and defaults to the installed one. The result is the URL of
    that asset type's page in the rendered specification, for example
    ``https://atlas-assets.readthedocs.io/en/v0.2.0/atlas.html``.
    """
    return "{}/v{}/{}".format(
        DOCS_BASE_URL, version.lstrip("v"), ASSET_SPECS[type_dir].docs_page
    )

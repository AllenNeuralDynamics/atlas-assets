"""Content-level (Phase 2) validation rules.

These checks read file contents and require the ``validate`` extra:

* metadata: ``data_description.json`` / ``processing.json`` against
  aind-data-schema (skipped with a note if that package is absent);
* manifest cross-references resolve to existing assets;
* ``terminology.csv`` integrity (columns and the identifier graph);
* OME-Zarr metadata (version, units, axes, compression,
  ``annotation_values``).
"""

import csv
import io
import json
import re

from atlas_assets.validation.models import Finding, Severity

_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
_OME_MIN = (0, 5)
_TERMINOLOGY_COLUMNS = (
    "identifier",
    "parent_identifier",
    "annotation_value",
    "name",
    "abbreviation",
    "color_hex_triplet",
)


def load_schema_models():
    """Return aind-data-schema models by filename, or None if absent."""
    try:
        import aind_data_schema  # noqa: F401
    except Exception:
        return None
    from aind_data_schema.core.data_description import (  # pragma: no cover
        DataDescription,
    )
    from aind_data_schema.core.processing import (  # pragma: no cover
        Processing,
    )

    return {  # pragma: no cover - requires the optional aind-data-schema
        "data_description.json": DataDescription,
        "processing.json": Processing,
    }


def zarr_available():
    """Return whether the zarr package can be imported."""
    try:
        import zarr  # noqa: F401
    except ImportError:  # pragma: no cover - zarr is present in dev/CI
        return False
    return True


class ContentContext:
    """Availability of the optional content-validation backends."""

    def __init__(self, models, zarr_ok):
        """Store the metadata models and zarr availability flag."""
        self.models = models
        self.zarr_ok = zarr_ok


def build_context():
    """Detect optional backends and return a :class:`ContentContext`."""
    return ContentContext(load_schema_models(), zarr_available())


def check_version(store, spec, asset, files, dirs, ctx, report):
    """Run all content checks for a single asset version."""
    _check_metadata(store, asset, files, ctx.models, report)
    _check_manifest_refs(store, asset, files, report)
    if spec.type_dir == "terminologies":
        _check_terminology_csv(store, asset, files, report)
    if ctx.zarr_ok:
        for name in sorted(dirs):
            if name.endswith(".ome.zarr"):
                _check_ome_zarr(store, asset, name, report)


def _check_metadata(store, asset, files, models, report):
    """Validate metadata JSON against aind-data-schema when available."""
    if models is None:
        return
    for name in ("data_description.json", "processing.json"):
        if name not in files:
            continue
        model = models.get(name)
        try:
            model.model_validate_json(store.read_text(f"{asset}/{name}"))
        except Exception as exc:  # noqa: BLE001 - report any failure
            report.add(
                Finding(
                    Severity.ERROR,
                    "E100",
                    "{} does not validate against aind-data-schema: "
                    "{}.".format(name, str(exc).splitlines()[0]),
                    asset=asset,
                    path=f"{asset}/{name}",
                )
            )


def _iter_refs(obj):
    """Yield reference objects (name+version+location) within ``obj``."""
    if isinstance(obj, dict):
        if {"name", "version", "location"} <= set(obj):
            yield obj
        for value in obj.values():
            yield from _iter_refs(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _iter_refs(value)


def _check_manifest_refs(store, asset, files, report):
    """Check that manifest references resolve to existing assets."""
    if "manifest.json" not in files:
        return
    path = f"{asset}/manifest.json"
    try:
        data = json.loads(store.read_text(path))
    except ValueError:
        return  # unparseable JSON is already an error in Phase 1
    seen = set()
    for ref in _iter_refs(data):
        location = str(ref["location"]).strip("/")
        if location in seen or location == asset.strip("/"):
            continue
        seen.add(location)
        if not store.exists(location):
            report.add(
                Finding(
                    Severity.ERROR,
                    "E101",
                    "Manifest references a component that does not "
                    "exist: {} {}.".format(ref["name"], ref["version"]),
                    asset=asset,
                    path=location,
                )
            )


def _check_terminology_csv(store, asset, files, report):
    """Validate terminology.csv columns and the identifier graph."""
    if "terminology.csv" not in files:
        return
    path = f"{asset}/terminology.csv"
    text = store.read_text(path)
    reader = csv.DictReader(io.StringIO(text))
    columns = set(reader.fieldnames or [])
    missing = [c for c in _TERMINOLOGY_COLUMNS if c not in columns]
    if missing:
        report.add(
            Finding(
                Severity.ERROR,
                "E120",
                "terminology.csv is missing required column(s): "
                "{}.".format(", ".join(missing)),
                asset=asset,
                path=path,
            )
        )
        return
    rows = list(reader)
    _check_terminology_graph(rows, asset, path, report)


def _add(report, severity, code, message, asset, path):
    """Append a finding (compact helper)."""
    report.add(Finding(severity, code, message, asset=asset, path=path))


def _check_terminology_graph(rows, asset, path, report):
    """Enforce identifier uniqueness, references, and acyclicity."""
    ids = [r["identifier"] for r in rows]
    id_set = set(ids)
    if len(ids) != len(id_set):
        _add(
            report,
            Severity.ERROR,
            "E121",
            "terminology.csv has duplicate identifier values.",
            asset,
            path,
        )
    values = [
        r["annotation_value"]
        for r in rows
        if (r.get("annotation_value") or "").strip()
    ]
    if len(values) != len(set(values)):
        _add(
            report,
            Severity.ERROR,
            "E123",
            "terminology.csv has duplicate annotation_value values.",
            asset,
            path,
        )
    parent = {}
    for row in rows:
        node = row["identifier"]
        par = (row.get("parent_identifier") or "").strip()
        parent[node] = par
        if par and par not in id_set:
            _add(
                report,
                Severity.ERROR,
                "E122",
                "parent_identifier '{}' does not reference an existing "
                "identifier.".format(par),
                asset,
                path,
            )
        color = (row.get("color_hex_triplet") or "").strip()
        if color and not _HEX.match(color):
            _add(
                report,
                Severity.WARNING,
                "W120",
                "color_hex_triplet '{}' is not a #RRGGBB value.".format(color),
                asset,
                path,
            )
    if _has_cycle(parent):
        _add(
            report,
            Severity.ERROR,
            "E124",
            "terminology.csv parent relationships contain a cycle.",
            asset,
            path,
        )


def _has_cycle(parent):
    """Return whether the parent map contains a cycle."""
    for start in parent:
        seen = set()
        node = start
        while node and node in parent:
            if node in seen:
                return True
            seen.add(node)
            node = parent.get(node)
    return False


def _ome_version_ok(version):
    """Return whether an OME-Zarr version string is at least 0.5."""
    match = re.match(r"(\d+)\.(\d+)", str(version))
    if not match:
        return False
    return (int(match.group(1)), int(match.group(2))) >= _OME_MIN


def _has_compressor(array):
    """Return whether a zarr array uses a compression codec."""
    codecs = getattr(array, "compressors", None)
    if not codecs:
        codecs = getattr(array, "codecs", None) or ()
    names = " ".join(type(c).__name__.lower() for c in codecs)
    return any(n in names for n in ("zstd", "blosc", "gzip", "lz4", "zlib"))


def _check_ome_zarr(store, asset, zdir, report):
    """Validate OME-Zarr metadata for one ``.ome.zarr`` directory."""
    path = f"{asset}/{zdir}"
    try:
        group = store.open_zarr_group(path)
    except Exception as exc:  # noqa: BLE001 - report any read failure
        _add(
            report,
            Severity.WARNING,
            "W114",
            "Could not open OME-Zarr group: {}.".format(
                str(exc).splitlines()[0]
            ),
            asset,
            path,
        )
        return
    ome = dict(group.attrs).get("ome")
    if not isinstance(ome, dict) or "multiscales" not in ome:
        _add(
            report,
            Severity.ERROR,
            "E110",
            "OME-Zarr metadata is missing 'multiscales'.",
            asset,
            path,
        )
        return
    if not _ome_version_ok(ome.get("version")):
        _add(
            report,
            Severity.ERROR,
            "E110",
            "OME-Zarr version '{}' is below the required 0.5.".format(
                ome.get("version")
            ),
            asset,
            path,
        )
    axes = ome["multiscales"][0].get("axes", [])
    space = [a for a in axes if a.get("type") == "space"]
    if any(a.get("unit") != "millimeter" for a in space):
        _add(
            report,
            Severity.WARNING,
            "W110",
            "OME-Zarr spatial axes are not in millimeters.",
            asset,
            path,
        )
    array_keys = list(group.array_keys())
    if zdir == "annotations.ome.zarr":
        members = array_keys + list(group.group_keys())
        if "annotation_values" not in members:
            _add(
                report,
                Severity.ERROR,
                "E111",
                "annotations.ome.zarr is missing the 'annotation_values' "
                "array.",
                asset,
                path,
            )
    for key in array_keys:
        if not _has_compressor(group[key]):
            _add(
                report,
                Severity.WARNING,
                "W111",
                "OME-Zarr array '{}' is uncompressed.".format(key),
                asset,
                path,
            )
            break

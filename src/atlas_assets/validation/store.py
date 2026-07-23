"""Read-only storage backends for atlas-assets trees.

A store exposes a uniform view over a local directory or an S3 prefix so
that validation rules do not need to know where the assets live. Both
backends are powered by obstore; paths are POSIX-style and relative to
the store root.
"""

import os
from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse

# Default AWS region for AIND buckets; overridable via environment.
_DEFAULT_REGION = "us-west-2"


@dataclass(frozen=True)
class Entry:
    """An immediate child of a directory or prefix."""

    name: str
    is_dir: bool


def _require_obstore():
    """Import and return the obstore module, or raise a helpful error."""
    try:
        import obstore
        import obstore.store  # noqa: F401  (ensure submodule is loaded)

        return obstore
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "The validator requires obstore. Install it with "
            "'pip install atlas-assets[validate]'."
        ) from exc


def _require_zarr():
    """Import and return the zarr module, or raise a helpful error."""
    try:
        import zarr

        return zarr
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "OME-Zarr validation requires zarr. Install it with "
            "'pip install atlas-assets[validate]'."
        ) from exc


class AssetStore:
    """Abstract read-only view over an atlas-assets tree."""

    def list(self, path: str = "") -> List[Entry]:
        """List the immediate children of ``path`` (relative to root)."""
        raise NotImplementedError

    def read_text(self, path: str) -> str:
        """Read the file at ``path`` as UTF-8 text."""
        raise NotImplementedError

    def exists(self, path: str) -> bool:
        """Return whether ``path`` exists as a file or directory."""
        rel = path.strip("/")
        if not rel:
            return True
        parent, _, name = rel.rpartition("/")
        return any(entry.name == name for entry in self.list(parent))

    def open_zarr_group(self, path: str):
        """Open the OME-Zarr group at ``path`` read-only via zarr."""
        raise NotImplementedError

    @property
    def location(self) -> str:
        """Return a human-readable description of the store root."""
        raise NotImplementedError


class _ObstoreStore(AssetStore):
    """Base class wrapping an obstore store with relative paths."""

    def __init__(self, store, location: str):
        """Wrap an obstore ``store`` rooted at ``location``."""
        self._store = store
        self._location = location

    def list(self, path: str = "") -> List[Entry]:
        """List the immediate children of ``path``."""
        obstore = _require_obstore()
        rel = path.strip("/")
        prefix = (rel + "/") if rel else ""
        result = obstore.list_with_delimiter(self._store, prefix=prefix)
        plen = len(prefix)
        entries = []
        for common in result["common_prefixes"]:
            name = common[plen:].strip("/")
            if name and "/" not in name:
                entries.append(Entry(name=name, is_dir=True))
        for obj in result["objects"]:
            name = obj["path"][plen:]
            if name and "/" not in name:
                entries.append(Entry(name=name, is_dir=False))
        return entries

    def read_text(self, path: str) -> str:
        """Read the file at ``path`` as UTF-8 text."""
        obstore = _require_obstore()
        response = obstore.get(self._store, path.strip("/"))
        return bytes(response.bytes()).decode("utf-8")

    def open_zarr_group(self, path: str):
        """Open the OME-Zarr group at ``path`` read-only via zarr."""
        zarr = _require_zarr()
        from zarr.storage import ObjectStore

        return zarr.open_group(
            store=ObjectStore(self._store, read_only=True),
            path=path.strip("/"),
            mode="r",
        )

    @property
    def location(self) -> str:
        """Return the store root location."""
        return self._location


class LocalStore(_ObstoreStore):
    """A store backed by a local filesystem directory."""

    def __init__(self, root: str):
        """Create a store rooted at the local directory ``root``."""
        obstore = _require_obstore()
        abs_root = os.path.abspath(root)
        super().__init__(obstore.store.LocalStore(abs_root), abs_root)


class S3Store(_ObstoreStore):
    """A store backed by an S3 prefix, read with unsigned requests."""

    def __init__(self, uri: str, region: str = ""):
        """Create a store for an ``s3://bucket/prefix`` URI.

        The region defaults to ``$AWS_REGION`` / ``$AWS_DEFAULT_REGION``
        and then to AIND's ``us-west-2``. Requests are unsigned so that
        public buckets can be read without credentials.
        """
        obstore = _require_obstore()
        parsed = urlparse(uri)
        prefix = parsed.path.strip("/")
        region = (
            region
            or os.environ.get("AWS_REGION")
            or os.environ.get("AWS_DEFAULT_REGION")
            or _DEFAULT_REGION
        )
        store = obstore.store.S3Store(
            parsed.netloc,
            prefix=prefix,
            region=region,
            skip_signature=True,
        )
        super().__init__(store, uri.rstrip("/") + "/")


def open_store(uri: str, region: str = "") -> AssetStore:
    """Return a store for a local path or ``s3://bucket/prefix`` URI."""
    if uri.startswith("s3://"):
        return S3Store(uri, region=region)
    return LocalStore(uri)

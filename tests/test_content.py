"""Tests for Phase 2 content validation."""

import os
import tempfile
import unittest
from unittest import mock

import zarr

from atlas_assets.validation import content as content_rules
from atlas_assets.validation.cli import main
from atlas_assets.validation.models import Report
from atlas_assets.validation.spec import ASSET_SPECS
from atlas_assets.validation.store import LocalStore
from atlas_assets.validation.validator import validate


def _write(path, text=""):
    """Create parent dirs and write ``text`` to ``path``."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _make_ome_zarr(
    path, axes=None, version="0.5", with_values=False, compressed=True
):
    """Create a minimal OME-Zarr v3 group fixture at ``path``."""
    group = zarr.open_group(path, mode="w")
    if axes is None:
        axes = [
            {"name": n, "type": "space", "unit": "millimeter"}
            for n in ("z", "y", "x")
        ]
    group.attrs["ome"] = {
        "version": version,
        "multiscales": [{"axes": axes, "datasets": [{"path": "s0"}]}],
    }
    kwargs = {} if compressed else {"compressors": []}
    group.create_array(
        "s0", shape=(2, 2, 2), dtype="i2", chunks=(2, 2, 2), **kwargs
    )
    if with_values:
        group.create_array(
            "annotation_values", shape=(2,), dtype="i4", chunks=(2,)
        )


def _ctx(models=None, zarr_ok=True):
    """Build a ContentContext for direct check_version calls."""
    return content_rules.ContentContext(models=models, zarr_ok=zarr_ok)


def _run(root, type_dir, name, version, ctx=None):
    """Run content checks for one asset and return the finding codes."""
    store = LocalStore(root)
    spec = ASSET_SPECS[type_dir]
    asset = "{}/{}/{}".format(type_dir, name, version)
    children = store.list(asset)
    files = {c.name for c in children if not c.is_dir}
    dirs = {c.name for c in children if c.is_dir}
    report = Report()
    content_rules.check_version(
        store, spec, asset, files, dirs, ctx or _ctx(), report
    )
    return {f.code for f in report.findings}


class _OkModel:
    """Stub aind-data-schema model that always validates."""

    @staticmethod
    def model_validate_json(text):
        """Accept any input."""
        return None


class _BadModel:
    """Stub aind-data-schema model that always fails."""

    @staticmethod
    def model_validate_json(text):
        """Reject any input."""
        raise ValueError("invalid\nsecond line")


class MetadataTest(unittest.TestCase):
    """Tests for aind-data-schema metadata validation."""

    def _space(self, root, dd="{}", processing=None):
        base = os.path.join(root, "coordinate-spaces", "x-space", "2015")
        _write(os.path.join(base, "data_description.json"), dd)
        _write(os.path.join(base, "manifest.json"), "{}")
        if processing is not None:
            _write(os.path.join(base, "processing.json"), processing)

    def test_valid_metadata(self):
        """A passing model yields no metadata error."""
        with tempfile.TemporaryDirectory() as root:
            self._space(root, processing="{}")
            models = {
                "data_description.json": _OkModel,
                "processing.json": _OkModel,
            }
            codes = _run(
                root,
                "coordinate-spaces",
                "x-space",
                "2015",
                _ctx(models=models),
            )
            self.assertNotIn("E100", codes)

    def test_invalid_metadata(self):
        """A failing model yields E100."""
        with tempfile.TemporaryDirectory() as root:
            self._space(root)
            codes = _run(
                root,
                "coordinate-spaces",
                "x-space",
                "2015",
                _ctx(models={"data_description.json": _BadModel}),
            )
            self.assertIn("E100", codes)

    def test_no_models_skips(self):
        """No models means metadata is not checked."""
        with tempfile.TemporaryDirectory() as root:
            self._space(root)
            self.assertNotIn(
                "E100", _run(root, "coordinate-spaces", "x-space", "2015")
            )


class ManifestRefTest(unittest.TestCase):
    """Tests for manifest cross-reference resolution."""

    def _atlas(self, root, ref_location, version="2017"):
        base = os.path.join(root, "atlases", "x-atlas", version)
        _write(os.path.join(base, "data_description.json"), "{}")
        manifest = (
            '{"name": "x-atlas", "version": "%s",'
            ' "location": "/atlases/x-atlas/%s",'
            ' "coordinate_space": {"name": "s", "version": "2015",'
            ' "location": "%s"},'
            ' "dupe": {"name": "s", "version": "2015",'
            ' "location": "%s"}}'
        ) % (version, version, ref_location, ref_location)
        _write(os.path.join(base, "manifest.json"), manifest)

    def test_reference_resolves(self):
        """A reference to an existing asset produces no error."""
        with tempfile.TemporaryDirectory() as root:
            loc = "/coordinate-spaces/s-space/2015"
            _write(
                os.path.join(
                    root, "coordinate-spaces", "s-space", "2015", "x"
                ),
                "",
            )
            self._atlas(root, loc)
            self.assertNotIn("E101", _run(root, "atlases", "x-atlas", "2017"))

    def test_reference_unresolved(self):
        """A reference to a missing asset produces E101."""
        with tempfile.TemporaryDirectory() as root:
            self._atlas(root, "/coordinate-spaces/missing/2015")
            self.assertIn("E101", _run(root, "atlases", "x-atlas", "2017"))

    def test_missing_manifest_is_skipped(self):
        """No manifest.json means no cross-reference check."""
        report = Report()
        content_rules._check_manifest_refs(
            None, "atlases/x/2017", set(), report
        )
        self.assertEqual(report.findings, [])

    def test_iter_refs_handles_lists(self):
        """References nested inside lists are discovered."""
        data = {
            "templates": [
                {"name": "t", "version": "1", "location": "/a"},
                {"name": "u", "version": "2", "location": "/b"},
            ]
        }
        found = [r["location"] for r in content_rules._iter_refs(data)]
        self.assertEqual(found, ["/a", "/b"])

    def test_unparseable_manifest_is_skipped(self):
        """An unparseable manifest is not cross-checked here."""
        with tempfile.TemporaryDirectory() as root:
            base = os.path.join(root, "atlases", "x-atlas", "2017")
            _write(os.path.join(base, "manifest.json"), "{bad")
            self.assertNotIn("E101", _run(root, "atlases", "x-atlas", "2017"))


class TerminologyCsvTest(unittest.TestCase):
    """Tests for terminology.csv content validation."""

    HEADER = (
        "identifier,parent_identifier,annotation_value,name,"
        "abbreviation,color_hex_triplet"
    )

    def _term(self, root, csv_text, version="2020"):
        base = os.path.join(root, "terminologies", "x-terminology", version)
        _write(os.path.join(base, "data_description.json"), "{}")
        _write(os.path.join(base, "manifest.json"), "{}")
        _write(os.path.join(base, "terminology.csv"), csv_text)

    def _codes(self, csv_text):
        with tempfile.TemporaryDirectory() as root:
            self._term(root, csv_text)
            return _run(root, "terminologies", "x-terminology", "2020")

    def test_clean(self):
        """A well-formed terminology yields no findings."""
        text = (
            self.HEADER + "\n1,,10,Root,RT,#AABBCC\n2,1,20,Child,CH,#112233\n"
        )
        self.assertEqual(self._codes(text), set())

    def test_missing_column(self):
        """A missing required column yields E120."""
        self.assertIn("E120", self._codes("identifier,name\n1,Root\n"))

    def test_duplicate_identifier(self):
        """Duplicate identifiers yield E121."""
        text = self.HEADER + "\n1,,10,A,A,#AABBCC\n1,,20,B,B,#AABBCC\n"
        self.assertIn("E121", self._codes(text))

    def test_duplicate_annotation_value(self):
        """Duplicate annotation values yield E123."""
        text = self.HEADER + "\n1,,10,A,A,#AABBCC\n2,,10,B,B,#AABBCC\n"
        self.assertIn("E123", self._codes(text))

    def test_bad_parent(self):
        """An unknown parent identifier yields E122."""
        text = self.HEADER + "\n1,,10,A,A,#AABBCC\n2,99,20,B,B,#AABBCC\n"
        self.assertIn("E122", self._codes(text))

    def test_bad_color(self):
        """A malformed color triplet yields W120."""
        text = self.HEADER + "\n1,,10,A,A,#19399\n"
        self.assertIn("W120", self._codes(text))

    def test_cycle(self):
        """A parent cycle yields E124."""
        text = self.HEADER + "\n1,2,10,A,A,#AABBCC\n2,1,20,B,B,#AABBCC\n"
        self.assertIn("E124", self._codes(text))

    def test_missing_csv_is_skipped(self):
        """No terminology.csv means no CSV check."""
        report = Report()
        content_rules._check_terminology_csv(
            None, "terminologies/x/2020", set(), report
        )
        self.assertEqual(report.findings, [])


class OmeZarrTest(unittest.TestCase):
    """Tests for OME-Zarr metadata validation."""

    def _template(self, root, **kw):
        base = os.path.join(root, "templates", "x-template", "2015")
        _write(os.path.join(base, "data_description.json"), "{}")
        _write(os.path.join(base, "manifest.json"), "{}")
        _make_ome_zarr(os.path.join(base, "template.ome.zarr"), **kw)
        return base

    def test_valid(self):
        """A well-formed OME-Zarr yields no findings."""
        with tempfile.TemporaryDirectory() as root:
            self._template(root)
            self.assertEqual(
                _run(root, "templates", "x-template", "2015"), set()
            )

    def test_old_version(self):
        """A version below 0.5 yields E110."""
        with tempfile.TemporaryDirectory() as root:
            self._template(root, version="0.4")
            self.assertIn(
                "E110", _run(root, "templates", "x-template", "2015")
            )

    def test_unparseable_version(self):
        """A non-numeric version yields E110."""
        with tempfile.TemporaryDirectory() as root:
            self._template(root, version="draft")
            self.assertIn(
                "E110", _run(root, "templates", "x-template", "2015")
            )

    def test_non_millimeter_units(self):
        """Non-millimeter spatial units yield W110."""
        with tempfile.TemporaryDirectory() as root:
            axes = [
                {"name": n, "type": "space", "unit": "micrometer"}
                for n in ("z", "y", "x")
            ]
            self._template(root, axes=axes)
            self.assertIn(
                "W110", _run(root, "templates", "x-template", "2015")
            )

    def test_uncompressed(self):
        """An uncompressed array yields W111."""
        with tempfile.TemporaryDirectory() as root:
            self._template(root, compressed=False)
            self.assertIn(
                "W111", _run(root, "templates", "x-template", "2015")
            )

    def test_missing_multiscales(self):
        """Missing OME multiscales metadata yields E110."""
        with tempfile.TemporaryDirectory() as root:
            base = os.path.join(root, "templates", "x-template", "2015")
            _write(os.path.join(base, "data_description.json"), "{}")
            _write(os.path.join(base, "manifest.json"), "{}")
            zarr.open_group(os.path.join(base, "template.ome.zarr"), mode="w")
            self.assertIn(
                "E110", _run(root, "templates", "x-template", "2015")
            )

    def test_unreadable(self):
        """A directory that is not a zarr group yields W114."""
        with tempfile.TemporaryDirectory() as root:
            base = os.path.join(root, "templates", "x-template", "2015")
            _write(os.path.join(base, "data_description.json"), "{}")
            _write(os.path.join(base, "manifest.json"), "{}")
            _write(os.path.join(base, "template.ome.zarr", "junk.txt"), "x")
            self.assertIn(
                "W114", _run(root, "templates", "x-template", "2015")
            )

    def _annotation(self, root, with_values):
        base = os.path.join(root, "annotation-sets", "x-annotation", "2020")
        _write(os.path.join(base, "data_description.json"), "{}")
        _write(os.path.join(base, "manifest.json"), "{}")
        _make_ome_zarr(
            os.path.join(base, "annotations.ome.zarr"),
            with_values=with_values,
        )
        os.makedirs(os.path.join(base, "annotations.precomputed"))
        return base

    def test_annotation_values_present(self):
        """An annotation_values array satisfies the requirement."""
        with tempfile.TemporaryDirectory() as root:
            self._annotation(root, with_values=True)
            self.assertNotIn(
                "E111",
                _run(root, "annotation-sets", "x-annotation", "2020"),
            )

    def test_annotation_values_missing(self):
        """A missing annotation_values array yields E111."""
        with tempfile.TemporaryDirectory() as root:
            self._annotation(root, with_values=False)
            self.assertIn(
                "E111",
                _run(root, "annotation-sets", "x-annotation", "2020"),
            )


class IntegrationTest(unittest.TestCase):
    """Tests wiring content checks through validate() and the CLI."""

    def _tree(self, root):
        base = os.path.join(root, "terminologies", "x-terminology", "2020")
        _write(os.path.join(base, "data_description.json"), "{}")
        _write(os.path.join(base, "manifest.json"), "{}")
        _write(
            os.path.join(base, "terminology.csv"),
            TerminologyCsvTest.HEADER + "\n1,,10,Root,RT,#AABBCC\n",
        )

    def test_metadata_unavailable_warns(self):
        """W100 is emitted when aind-data-schema is unavailable."""
        with tempfile.TemporaryDirectory() as root:
            self._tree(root)
            with mock.patch.object(
                content_rules, "load_schema_models", return_value=None
            ):
                report = validate(LocalStore(root), content=True)
            self.assertIn("W100", {f.code for f in report.findings})

    def test_zarr_unavailable_warns(self):
        """W101 is emitted when zarr is unavailable."""
        with tempfile.TemporaryDirectory() as root:
            self._tree(root)
            with mock.patch.object(
                content_rules, "zarr_available", return_value=False
            ):
                report = validate(LocalStore(root), content=True)
            self.assertIn("W101", {f.code for f in report.findings})

    def test_cli_full_level(self):
        """The CLI runs content checks at --level full."""
        with tempfile.TemporaryDirectory() as root:
            self._tree(root)
            # Keep this independent of whether aind-data-schema is
            # installed: the stub fixtures are not real metadata.
            with mock.patch.object(
                content_rules, "load_schema_models", return_value=None
            ):
                self.assertEqual(main([root, "--level", "full"]), 0)


if __name__ == "__main__":
    unittest.main()

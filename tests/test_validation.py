"""Tests for the atlas-assets spec validator."""

import json
import os
import tempfile
import unittest

from atlas_assets.validation import (
    Finding,
    LocalStore,
    Report,
    S3Store,
    Severity,
    open_store,
    validate,
)
from atlas_assets.validation.cli import main
from atlas_assets.validation.store import AssetStore

_TEMPLATE_MANIFEST = {
    "coordinate_space": {"name": "s", "version": "2015"},
    "alignment": "defining",
    "created": "2015-01-01",
    "schema_version": "0.1.0",
}


def _write(path, text=""):
    """Create parent dirs and write ``text`` to ``path``."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _valid_template(root, name="allen-adult-mouse-stpt-template"):
    """Create a fully valid template asset under ``root``."""
    base = os.path.join(root, "templates", name, "2015")
    _write(os.path.join(base, "data_description.json"), "{}")
    _write(
        os.path.join(base, "manifest.json"),
        json.dumps(_TEMPLATE_MANIFEST),
    )
    _write(os.path.join(base, "processing.json"), "{}")
    os.makedirs(os.path.join(base, "template.ome.zarr"), exist_ok=True)
    return base


def _valid_ct(root, name="a-template-2024_to_b-template-2015"):
    """Create a minimal coordinate-transformation asset under ``root``."""
    base = os.path.join(root, "coordinate-transformations", name, "2024")
    _write(os.path.join(base, "data_description.json"), "{}")
    _write(os.path.join(base, "manifest.json"), "{}")
    return base


def _codes(report):
    """Return the set of finding codes in a report."""
    return {f.code for f in report.findings}


class OpenStoreTest(unittest.TestCase):
    """Tests for the store factory."""

    def test_local_path_returns_local_store(self):
        """A plain path yields a LocalStore."""
        self.assertIsInstance(open_store("."), LocalStore)

    def test_s3_uri_returns_s3_store(self):
        """An s3:// URI yields an S3Store."""
        store = open_store("s3://bucket/prefix/")
        self.assertIsInstance(store, S3Store)

    def test_exists_root_and_child(self):
        """exists() is true for the root and known children."""
        with tempfile.TemporaryDirectory() as root:
            _valid_template(root)
            store = LocalStore(root)
            self.assertTrue(store.exists(""))
            self.assertTrue(store.exists("templates"))
            self.assertFalse(store.exists("nope"))


class ValidatorTest(unittest.TestCase):
    """Tests for the structural validator."""

    def test_valid_template_has_no_errors(self):
        """A complete template asset produces no findings."""
        with tempfile.TemporaryDirectory() as root:
            _valid_template(root)
            report = validate(LocalStore(root))
            self.assertFalse(report.has_errors)
            self.assertEqual(report.findings, [])

    def test_missing_required_file_is_error(self):
        """Removing data_description.json triggers E001."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            os.remove(os.path.join(base, "data_description.json"))
            report = validate(LocalStore(root))
            self.assertTrue(report.has_errors)
            self.assertIn("E001", _codes(report))

    def test_missing_required_dir_is_error(self):
        """Removing template.ome.zarr triggers E002."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            os.rmdir(os.path.join(base, "template.ome.zarr"))
            report = validate(LocalStore(root))
            self.assertIn("E002", _codes(report))

    def test_unexpected_top_level_dir_is_warning(self):
        """A directory not in the spec triggers W001."""
        with tempfile.TemporaryDirectory() as root:
            _valid_template(root)
            os.makedirs(os.path.join(root, "output"))
            report = validate(LocalStore(root))
            self.assertIn("W001", _codes(report))
            self.assertFalse(report.has_errors)

    def test_naming_suffix_is_warning(self):
        """A name missing the conventional suffix triggers W020."""
        with tempfile.TemporaryDirectory() as root:
            _valid_template(root, name="allen-adult-mouse-stpt")
            report = validate(LocalStore(root))
            self.assertIn("W020", _codes(report))
            self.assertFalse(report.has_errors)

    def test_resolution_nii_is_accepted(self):
        """template_{resolution}.nii.gz is an accepted optional file."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            _write(os.path.join(base, "template_25.nii.gz"), "x")
            report = validate(LocalStore(root))
            self.assertNotIn("W030", _codes(report))

    def test_unexpected_file_is_warning(self):
        """An unknown file triggers W030."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            _write(os.path.join(base, "notes.txt"), "hi")
            report = validate(LocalStore(root))
            self.assertIn("W030", _codes(report))

    def test_invalid_json_is_error(self):
        """A required JSON file that does not parse triggers E003."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            _write(os.path.join(base, "data_description.json"), "{bad")
            report = validate(LocalStore(root))
            self.assertIn("E003", _codes(report))

    def test_missing_manifest_key_is_warning(self):
        """A manifest missing a draft minimal key triggers W041."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            _write(os.path.join(base, "manifest.json"), "{}")
            report = validate(LocalStore(root))
            self.assertIn("W041", _codes(report))

    def test_no_version_dir_is_error(self):
        """An asset name with no version directory triggers E010."""
        with tempfile.TemporaryDirectory() as root:
            name_dir = os.path.join(
                root, "atlases", "allen-adult-mouse-ccf-atlas"
            )
            os.makedirs(name_dir)
            report = validate(LocalStore(root))
            self.assertIn("E010", _codes(report))

    def test_conditional_processing_missing_is_warning(self):
        """A template without processing.json triggers W010."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            os.remove(os.path.join(base, "processing.json"))
            report = validate(LocalStore(root))
            self.assertIn("W010", _codes(report))
            self.assertFalse(report.has_errors)


class CliTest(unittest.TestCase):
    """Tests for the CLI entry point."""

    def test_exit_zero_when_valid(self):
        """A valid tree exits 0."""
        with tempfile.TemporaryDirectory() as root:
            _valid_template(root)
            self.assertEqual(main([root]), 0)

    def test_exit_one_on_error(self):
        """A tree with an error exits 1."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            os.remove(os.path.join(base, "manifest.json"))
            self.assertEqual(main([root]), 1)

    def test_strict_fails_on_warning(self):
        """--strict exits 1 when only warnings are present."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            _write(os.path.join(base, "notes.txt"), "hi")
            self.assertEqual(main([root, "--strict"]), 1)
            self.assertEqual(main([root]), 0)

    def test_json_format_runs(self):
        """--format json exits 0 on a valid tree."""
        with tempfile.TemporaryDirectory() as root:
            _valid_template(root)
            self.assertEqual(main([root, "--format", "json"]), 0)


class ModelTest(unittest.TestCase):
    """Tests for the finding/report data models."""

    def test_finding_to_dict(self):
        """Finding.to_dict exposes all fields."""
        finding = Finding(Severity.ERROR, "E001", "msg", asset="a", path="a/x")
        self.assertEqual(
            finding.to_dict(),
            {
                "severity": "error",
                "code": "E001",
                "asset": "a",
                "path": "a/x",
                "message": "msg",
            },
        )

    def test_report_to_dict_counts(self):
        """Report.to_dict summarizes error and warning counts."""
        report = Report(root="r")
        report.add(Finding(Severity.ERROR, "E001", "e"))
        report.add(Finding(Severity.WARNING, "W001", "w"))
        result = report.to_dict()
        self.assertEqual(result["summary"], {"errors": 1, "warnings": 1})
        self.assertEqual(len(result["findings"]), 2)


class AbstractStoreTest(unittest.TestCase):
    """The abstract store raises for unimplemented methods."""

    def test_abstract_methods_raise(self):
        """AssetStore base methods are not implemented."""
        store = AssetStore()
        with self.assertRaises(NotImplementedError):
            store.list()
        with self.assertRaises(NotImplementedError):
            store.read_text("x")
        with self.assertRaises(NotImplementedError):
            store.open_zarr_group("x")
        with self.assertRaises(NotImplementedError):
            store.location


class BranchTest(unittest.TestCase):
    """Tests exercising the remaining validator branches."""

    def test_file_at_store_root_is_warning(self):
        """A loose file at the root triggers W001."""
        with tempfile.TemporaryDirectory() as root:
            _write(os.path.join(root, "loose.txt"), "x")
            self.assertIn("W001", _codes(validate(LocalStore(root))))

    def test_file_under_type_dir_is_warning(self):
        """A file directly under a type directory triggers W002."""
        with tempfile.TemporaryDirectory() as root:
            _write(os.path.join(root, "atlases", "stray.txt"), "x")
            self.assertIn("W002", _codes(validate(LocalStore(root))))

    def test_file_at_name_level_is_warning(self):
        """A file at the asset-name level triggers W003."""
        with tempfile.TemporaryDirectory() as root:
            base = os.path.join(root, "atlases", "x-atlas")
            _write(os.path.join(base, "2011", "manifest.json"), "{}")
            _write(os.path.join(base, "readme.txt"), "x")
            self.assertIn("W003", _codes(validate(LocalStore(root))))

    def test_bad_version_format_is_warning(self):
        """An unrecognized version directory name triggers W011."""
        with tempfile.TemporaryDirectory() as root:
            base = os.path.join(root, "atlases", "x-atlas", "latest")
            _write(os.path.join(base, "data_description.json"), "{}")
            _write(os.path.join(base, "manifest.json"), "{}")
            self.assertIn("W011", _codes(validate(LocalStore(root))))

    def test_unexpected_dir_is_warning(self):
        """An unexpected directory in a version triggers W031."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            os.makedirs(os.path.join(base, "surprise"))
            self.assertIn("W031", _codes(validate(LocalStore(root))))

    def test_manifest_not_object_is_warning(self):
        """A manifest that is valid JSON but not an object triggers W040."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_template(root)
            _write(os.path.join(base, "manifest.json"), "[]")
            self.assertIn("W040", _codes(validate(LocalStore(root))))

    def test_ct_naming_pattern_is_warning(self):
        """A transformation name without '_to_' triggers W021."""
        with tempfile.TemporaryDirectory() as root:
            _valid_ct(root, name="badname")
            self.assertIn("W021", _codes(validate(LocalStore(root))))

    def test_ct_allows_extra_files(self):
        """Coordinate-transformations permit arbitrary extra files."""
        with tempfile.TemporaryDirectory() as root:
            base = _valid_ct(root)
            _write(os.path.join(base, "0GenericAffine.mat"), "x")
            codes = _codes(validate(LocalStore(root)))
            self.assertNotIn("W030", codes)
            self.assertNotIn("W021", codes)


if __name__ == "__main__":
    unittest.main()

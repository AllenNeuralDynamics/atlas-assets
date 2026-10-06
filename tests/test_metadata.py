"""Tests that repository metadata stays in step with the package."""

import os
import re
import unittest

from atlas_assets import __version__

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CitationTest(unittest.TestCase):
    """Tests for the repository's CITATION.cff."""

    def setUp(self):
        """Read CITATION.cff from the repository root."""
        path = os.path.join(_ROOT, "CITATION.cff")
        with open(path, encoding="utf-8") as handle:
            self.cff = handle.read()

    def _field(self, key):
        """Return the value of a top-level ``key: "value"`` line."""
        match = re.search(
            r'^{}:\s*"?([^"\n]+)"?\s*$'.format(re.escape(key)),
            self.cff,
            re.MULTILINE,
        )
        self.assertIsNotNone(match, f"{key} missing from CITATION.cff")
        return match.group(1)

    def test_version_matches_package(self):
        """The cited version is the package version."""
        self.assertEqual(self._field("version"), f"v{__version__}")

    def test_author_is_allen_institute(self):
        """The author is the Allen Institute, as an organization."""
        self.assertIn('- name: "Allen Institute"\n', self.cff)


if __name__ == "__main__":
    unittest.main()

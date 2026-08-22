"""Tests for version parsing and comparison.

Every case marked "regression" produced a wrong answer when versions were
compared with float(), or when addon versions were matched by substring.
"""

import unittest

from src.analyzer.compatibility import CompatibilityAnalyzer
from src.analyzer.deprecation import DeprecationAnalyzer
from src.utils.version import (
    addon_version_at_least,
    compare_versions,
    parse_addon_version,
    parse_version,
    version_at_least,
    version_sort_key,
)


class TestParseVersion(unittest.TestCase):
    def test_parses_common_shapes(self):
        self.assertEqual(parse_version("1.30"), (1, 30))
        self.assertEqual(parse_version("v1.30"), (1, 30))
        self.assertEqual(parse_version("1.30.1"), (1, 30, 1))
        self.assertEqual(parse_version(" 1.9 "), (1, 9))

    def test_rejects_junk(self):
        for bad in ("", "abc", "1.x", None, "1..2", "v"):
            with self.subTest(bad=bad):
                self.assertIsNone(parse_version(bad))


class TestCompareVersions(unittest.TestCase):
    def test_regression_1_9_is_below_1_16(self):
        """float("1.9") > float("1.16") - the original bug."""
        self.assertEqual(compare_versions("1.9", "1.16"), -1)
        self.assertFalse(version_at_least("1.9", "1.16"))

    def test_regression_1_30_differs_from_1_3(self):
        """float() collapses "1.30" and "1.3" to the same number."""
        self.assertEqual(compare_versions("1.30", "1.3"), 1)
        self.assertNotEqual(compare_versions("1.30", "1.3"), 0)

    def test_ordering(self):
        self.assertEqual(compare_versions("1.29", "1.30"), -1)
        self.assertEqual(compare_versions("1.30", "1.30"), 0)
        self.assertEqual(compare_versions("1.31", "1.30"), 1)
        self.assertEqual(compare_versions("1.30.1", "1.30"), 1)
        self.assertEqual(compare_versions("1.30.0", "1.30"), 0)

    def test_unparseable_returns_none(self):
        self.assertIsNone(compare_versions("1.30", "nope"))
        self.assertIsNone(version_at_least("nope", "1.30"))

    def test_sort_key_orders_correctly(self):
        versions = ["1.10", "1.9", "1.31", "1.30"]
        self.assertEqual(
            sorted(versions, key=version_sort_key),
            ["1.9", "1.10", "1.30", "1.31"],
        )

    def test_sort_key_puts_junk_last_without_raising(self):
        versions = ["1.30", "bogus", "1.29"]
        self.assertEqual(
            sorted(versions, key=version_sort_key),
            ["1.29", "1.30", "bogus"],
        )


class TestAddonVersions(unittest.TestCase):
    def test_parses_eksbuild_suffix(self):
        self.assertEqual(parse_addon_version("v1.11.1-eksbuild.2"), (1, 11, 1, 2))
        self.assertEqual(parse_addon_version("v1.30.0-eksbuild.3"), (1, 30, 0, 3))
        self.assertEqual(parse_addon_version("1.18.0"), (1, 18, 0, 0))

    def test_build_number_breaks_ties(self):
        self.assertTrue(
            addon_version_at_least("v1.11.1-eksbuild.2", "v1.11.1-eksbuild.1")
        )
        self.assertFalse(
            addon_version_at_least("v1.11.1-eksbuild.1", "v1.11.1-eksbuild.2")
        )

    def test_equal_versions_are_acceptable(self):
        self.assertTrue(
            addon_version_at_least("v1.11.1-eksbuild.1", "v1.11.1-eksbuild.1")
        )

    def test_regression_newer_versions_are_not_rejected(self):
        """Substring matching flagged anything past 'recommended' as broken."""
        for newer in ("v1.11.3-eksbuild.1", "v1.12.0-eksbuild.1", "v2.0.0-eksbuild.1"):
            with self.subTest(newer=newer):
                self.assertTrue(addon_version_at_least(newer, "v1.11.1-eksbuild.1"))

    def test_older_versions_are_still_rejected(self):
        self.assertFalse(
            addon_version_at_least("v1.10.0-eksbuild.1", "v1.11.1-eksbuild.1")
        )

    def test_regression_partial_string_is_not_accepted(self):
        """'v1.30.0-eksbuild.' used to pass as a substring of the real version."""
        self.assertFalse(
            addon_version_at_least("v1.30.0-eksbuild.", "v1.30.0-eksbuild.1")
        )


class TestCallSitesUseTheHelper(unittest.TestCase):
    """The analyzers must give correct answers, not just the helper."""

    def test_deprecation_respects_the_removal_version(self):
        analyzer = DeprecationAnalyzer()

        # regression: both of these returned True under float() comparison
        self.assertFalse(analyzer.is_api_removed("apps/v1beta1", "1.9"))
        self.assertFalse(analyzer.is_api_removed("batch/v1beta1", "1.9"))

        # and the genuinely-removed cases still report True
        self.assertTrue(analyzer.is_api_removed("apps/v1beta1", "1.16"))
        self.assertTrue(analyzer.is_api_removed("apps/v1beta1", "1.29"))
        self.assertFalse(analyzer.is_api_removed("apps/v1beta1", "1.15"))

    def test_addon_compatibility_is_semantic(self):
        analyzer = CompatibilityAnalyzer()

        compatible, _ = analyzer.check_addon_compatibility(
            "coredns", "v1.12.0-eksbuild.1", "1.30"
        )
        self.assertTrue(compatible, "a version above the minimum must be accepted")

        incompatible, recommended = analyzer.check_addon_compatibility(
            "coredns", "v1.10.0-eksbuild.1", "1.30"
        )
        self.assertFalse(incompatible, "a version below the minimum must be rejected")
        self.assertIsNotNone(recommended)

    def test_supported_versions_sort_numerically(self):
        analyzer = CompatibilityAnalyzer()
        analyzer.EKS_K8S_VERSIONS = {"1.9": "", "1.10": "", "1.30": "", "1.31": ""}
        self.assertEqual(
            analyzer.get_supported_versions(), ["1.9", "1.10", "1.30", "1.31"]
        )


if __name__ == "__main__":
    unittest.main()

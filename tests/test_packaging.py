"""Tests that the bundled YAML data ships with the package.

These guard against a regression where data/ and config/ sat at the repository
root. `pip install -e .` worked because __file__ pointed into the checkout, but
a real install put the code in site-packages with no data/ sibling, so every EKS
version was reported as unsupported. Nothing caught it because the whole test
suite ran from the repository root.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import src
from src.analyzer.compatibility import CompatibilityAnalyzer

PACKAGE_DIR = Path(src.__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent


class TestBundledDataLocation(unittest.TestCase):
    """The YAML must live inside the package directory, not beside it."""

    def test_data_files_are_inside_the_package(self):
        for name in ("compatibility_matrix.yaml", "addon_versions.yaml"):
            with self.subTest(name=name):
                self.assertTrue(
                    (PACKAGE_DIR / "data" / name).is_file(),
                    f"{name} must live in src/data/ so it ships in the wheel",
                )

    def test_config_is_inside_the_package(self):
        self.assertTrue((PACKAGE_DIR / "config" / "config.yaml").is_file())


class TestAnalyzerLoadsBundledData(unittest.TestCase):
    """The analyzer must actually parse that data."""

    def test_matrix_and_addons_are_populated(self):
        analyzer = CompatibilityAnalyzer()

        self.assertTrue(
            analyzer.get_supported_versions(), "compatibility matrix loaded empty"
        )
        self.assertTrue(
            analyzer.ADDON_COMPATIBILITY, "addon compatibility data loaded empty"
        )

    def test_a_known_upgrade_is_accepted(self):
        analyzer = CompatibilityAnalyzer()
        versions = analyzer.get_supported_versions()

        # Two adjacent supported versions must form a valid upgrade.
        pairs = [
            (a, b)
            for a, b in zip(versions, versions[1:])
            if int(b.split(".")[1]) - int(a.split(".")[1]) == 1
        ]
        self.assertTrue(pairs, "no adjacent version pair in the matrix")

        current, target = pairs[0]
        can_upgrade, reason = analyzer.can_upgrade_directly(current, target)
        self.assertTrue(can_upgrade, f"{current} -> {target} rejected: {reason}")


class TestInstalledLayout(unittest.TestCase):
    """Simulate a wheel install: the package alone, with no repository around it."""

    def test_analyzer_works_with_only_the_package_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(
                PACKAGE_DIR,
                Path(tmp) / "src",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            # Keep the real repository off sys.path so `src` can only resolve to
            # the copy. Preserve any other entries (test stubs, virtualenvs).
            kept = [
                entry
                for entry in os.environ.get("PYTHONPATH", "").split(os.pathsep)
                if entry and Path(entry).resolve() != REPO_ROOT
            ]
            env = dict(os.environ, PYTHONPATH=os.pathsep.join([tmp] + kept))

            code = (
                "from src.analyzer.compatibility import CompatibilityAnalyzer\n"
                "versions = CompatibilityAnalyzer().get_supported_versions()\n"
                "assert versions, 'no versions loaded from installed layout'\n"
                "print('loaded', len(versions))\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                result.returncode,
                0,
                f"package failed standalone:\n{result.stdout}\n{result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()

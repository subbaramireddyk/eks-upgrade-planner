"""Tests that reports survive a non-UTF-8 locale.

The reporters emit characters such as U+2705 and U+26A0 that cp1252 cannot
represent. `Path.write_text()` without an explicit encoding picks the locale
default, so on a typical Windows install `plan --output report.md` raised
UnicodeEncodeError after all the scanning work had already been done.
"""

import tempfile
import unittest
from pathlib import Path

from src.reporter.markdown import MarkdownReporter

CLUSTER_INFO = {
    "cluster": {
        "name": "test-cluster",
        "version": "1.29",
        "status": "ACTIVE",
        "platform_version": "eks.1",
        "endpoint": "https://abc.gr7.us-west-2.eks.amazonaws.com",
        "vpc_config": {"vpcId": "vpc-0abc123"},
    },
    "node_groups": [],
    "addons": [],
}
UPGRADE_PLAN = {"upgrade_path": ["1.28", "1.29", "1.30"]}
RISK = {"overall_risk": "LOW"}


def _report():
    return MarkdownReporter().generate_report(
        CLUSTER_INFO, {}, {}, UPGRADE_PLAN, RISK, {}
    )


class TestReportEncoding(unittest.TestCase):
    def test_report_contains_non_ascii(self):
        """Guard the premise: if this stops being true the risk is gone."""
        report = _report()
        self.assertTrue(
            any(ord(ch) > 127 for ch in report),
            "report is pure ASCII; the encoding tests below no longer test anything",
        )

    def test_report_is_not_representable_in_cp1252(self):
        """The exact condition that broke the Windows path."""
        with self.assertRaises(UnicodeEncodeError):
            _report().encode("cp1252")

    def test_report_round_trips_through_a_utf8_file(self):
        report = _report()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            path.write_text(report, encoding="utf-8")
            self.assertEqual(path.read_text(encoding="utf-8"), report)

    def test_cli_writes_reports_as_utf8(self):
        """cli.py must not call write_text() without an encoding."""
        source = Path("src/cli.py").read_text(encoding="utf-8")
        self.assertIn('write_text(report, encoding="utf-8")', source)
        self.assertNotIn("write_text(report)", source)

    def test_log_handler_uses_utf8(self):
        source = Path("src/utils/logger.py").read_text(encoding="utf-8")
        self.assertIn('FileHandler(log_file, encoding="utf-8")', source)


if __name__ == "__main__":
    unittest.main()

"""Tests for planner modules."""

import unittest
from src.planner.upgrade_path import UpgradePathPlanner
from src.planner.risk_assessment import RiskAssessment
from src.analyzer.compatibility import CompatibilityAnalyzer


class TestUpgradePathPlanner(unittest.TestCase):
    """Test upgrade path planner."""

    def setUp(self):
        """Set up test fixtures."""
        self.compat_analyzer = CompatibilityAnalyzer()
        self.planner = UpgradePathPlanner(self.compat_analyzer)

    def test_generate_upgrade_path(self):
        """Test upgrade path generation."""
        path = self.planner.generate_upgrade_path("1.27", "1.29")

        self.assertEqual(len(path), 3)  # 1.27 -> 1.28 -> 1.29
        self.assertEqual(path[0], "1.27")
        self.assertEqual(path[-1], "1.29")

    def test_single_version_upgrade(self):
        """Test single version upgrade path."""
        path = self.planner.generate_upgrade_path("1.28", "1.29")

        self.assertEqual(len(path), 2)  # 1.28 -> 1.29

    def test_same_version(self):
        """Test same version (no upgrade)."""
        path = self.planner.generate_upgrade_path("1.29", "1.29")

        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], "1.29")

    def test_addon_upgrade_order(self):
        """Test addon upgrade ordering."""
        addons = [
            {"name": "aws-ebs-csi-driver", "version": "v1.0.0"},
            {"name": "vpc-cni", "version": "v1.0.0"},
            {"name": "coredns", "version": "v1.0.0"},
        ]

        ordered = self.planner.determine_addon_upgrade_order(addons)

        # vpc-cni should be first (critical network addon)
        self.assertEqual(ordered[0]["name"], "vpc-cni")

    def test_estimate_upgrade_time(self):
        """Test upgrade time estimation."""
        upgrade_path = ["1.27", "1.28", "1.29"]
        node_groups = [{"name": "ng1"}, {"name": "ng2"}]
        addons = [{"name": "coredns"}, {"name": "kube-proxy"}]

        estimation = self.planner.estimate_upgrade_time(
            upgrade_path, node_groups, addons
        )

        self.assertIn("total_minutes", estimation)
        self.assertIn("total_hours", estimation)
        self.assertGreater(estimation["total_hours"], 0)


class TestRiskAssessment(unittest.TestCase):
    """Test risk assessment."""

    def setUp(self):
        """Set up test fixtures."""
        self.risk_assessment = RiskAssessment()

    def test_assess_deprecated_api_risk(self):
        """Test deprecated API risk assessment."""
        deprecated_apis = {
            "apps/v1beta1": [
                {"name": "dep1", "deprecation_info": {"removed_in": "1.16"}},
                {"name": "dep2", "deprecation_info": {"removed_in": "1.16"}},
            ]
        }

        risk = self.risk_assessment.assess_deprecated_api_risk(deprecated_apis)

        self.assertIn("risk_level", risk)
        self.assertGreater(risk["total_deprecated"], 0)

    def test_assess_version_jump_risk(self):
        """Test version jump risk assessment."""
        # Single version jump - low risk
        risk = self.risk_assessment.assess_version_jump_risk(["1.28", "1.29"])
        self.assertEqual(risk["risk_level"], "LOW")

        # Multiple version jumps - higher risk
        risk = self.risk_assessment.assess_version_jump_risk(
            ["1.26", "1.27", "1.28", "1.29"]
        )
        self.assertIn(risk["risk_level"], ["MEDIUM", "HIGH"])

    def test_assess_cluster_size_risk(self):
        """Test cluster size risk assessment."""
        small_cluster = [
            {"scaling_config": {"desiredSize": 5}},
            {"scaling_config": {"desiredSize": 5}},
        ]

        risk = self.risk_assessment.assess_cluster_size_risk(small_cluster)
        self.assertEqual(risk["total_nodes"], 10)


if __name__ == "__main__":
    unittest.main()

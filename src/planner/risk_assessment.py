"""Risk assessment for EKS upgrades."""

from typing import Dict, Any, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RiskAssessment:
    """Risk assessment for EKS cluster upgrades."""

    RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def __init__(self):
        """Initialize risk assessment."""
        pass

    def assess_deprecated_api_risk(
        self, deprecated_apis: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Assess risk from deprecated APIs.

        Args:
            deprecated_apis: Dictionary of deprecated APIs and affected resources

        Returns:
            Risk assessment dictionary
        """
        total_deprecated = sum(len(resources) for resources in deprecated_apis.values())
        removed_apis = sum(
            1
            for api_version, resources in deprecated_apis.items()
            if any(r.get("deprecation_info", {}).get("removed_in") for r in resources)
        )

        if removed_apis > 0:
            risk_level = "CRITICAL"
            message = f"{removed_apis} APIs will be removed in target version"
        elif total_deprecated > 10:
            risk_level = "HIGH"
            message = f"{total_deprecated} resources using deprecated APIs"
        elif total_deprecated > 5:
            risk_level = "MEDIUM"
            message = f"{total_deprecated} resources using deprecated APIs"
        elif total_deprecated > 0:
            risk_level = "LOW"
            message = f"{total_deprecated} resources using deprecated APIs"
        else:
            risk_level = "LOW"
            message = "No deprecated APIs found"

        return {
            "risk_level": risk_level,
            "total_deprecated": total_deprecated,
            "removed_apis": removed_apis,
            "message": message,
        }

    def assess_breaking_changes_risk(
        self, breaking_changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess risk from breaking changes.

        Args:
            breaking_changes: List of breaking changes

        Returns:
            Risk assessment dictionary
        """
        if not breaking_changes:
            return {
                "risk_level": "LOW",
                "total_changes": 0,
                "message": "No breaking changes identified",
            }

        critical_changes = [c for c in breaking_changes if c.get("impact") == "HIGH"]

        if len(critical_changes) >= 3:
            risk_level = "HIGH"
        elif len(critical_changes) >= 1:
            risk_level = "MEDIUM"
        elif len(breaking_changes) > 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_level": risk_level,
            "total_changes": len(breaking_changes),
            "critical_changes": len(critical_changes),
            "message": f"{len(breaking_changes)} breaking changes, {len(critical_changes)} critical",
        }

    def assess_addon_compatibility_risk(
        self, addon_recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess risk from addon incompatibilities.

        Args:
            addon_recommendations: List of addon recommendations

        Returns:
            Risk assessment dictionary
        """
        incompatible_addons = [
            a for a in addon_recommendations if not a.get("is_compatible", True)
        ]

        if not incompatible_addons:
            return {
                "risk_level": "LOW",
                "incompatible_count": 0,
                "message": "All addons compatible",
            }

        critical_addons = ["vpc-cni", "kube-proxy", "coredns"]
        critical_incompatible = [
            a for a in incompatible_addons if a.get("addon_name") in critical_addons
        ]

        if critical_incompatible:
            risk_level = "HIGH"
            message = f"{len(critical_incompatible)} critical addons need updates"
        elif len(incompatible_addons) > 3:
            risk_level = "MEDIUM"
            message = f"{len(incompatible_addons)} addons need updates"
        else:
            risk_level = "LOW"
            message = f"{len(incompatible_addons)} addons need updates"

        return {
            "risk_level": risk_level,
            "incompatible_count": len(incompatible_addons),
            "critical_incompatible": len(critical_incompatible),
            "message": message,
        }

    def assess_version_jump_risk(self, upgrade_path: List[str]) -> Dict[str, Any]:
        """
        Assess risk based on number of version jumps.

        Args:
            upgrade_path: List of versions in upgrade path

        Returns:
            Risk assessment dictionary
        """
        num_jumps = len(upgrade_path) - 1

        if num_jumps == 0:
            risk_level = "LOW"
            message = "No upgrade needed"
        elif num_jumps == 1:
            risk_level = "LOW"
            message = "Single version upgrade"
        elif num_jumps == 2:
            risk_level = "MEDIUM"
            message = "Two version upgrades required"
        else:
            risk_level = "HIGH"
            message = f"{num_jumps} sequential upgrades required"

        return {
            "risk_level": risk_level,
            "version_jumps": num_jumps,
            "message": message,
        }

    def assess_cluster_size_risk(
        self, node_groups: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess risk based on cluster size and complexity.

        Args:
            node_groups: List of node groups

        Returns:
            Risk assessment dictionary
        """
        total_nodes = sum(
            ng.get("scaling_config", {}).get("desiredSize", 0) for ng in node_groups
        )

        if total_nodes > 100:
            risk_level = "HIGH"
            message = f"Large cluster with {total_nodes} nodes"
        elif total_nodes > 50:
            risk_level = "MEDIUM"
            message = f"Medium cluster with {total_nodes} nodes"
        elif total_nodes > 20:
            risk_level = "MEDIUM"
            message = f"Cluster with {total_nodes} nodes"
        else:
            risk_level = "LOW"
            message = f"Small cluster with {total_nodes} nodes"

        return {
            "risk_level": risk_level,
            "total_nodes": total_nodes,
            "node_groups": len(node_groups),
            "message": message,
        }

    def _get_risk_score(self, risk_level: str) -> int:
        """Convert risk level to numeric score."""
        scores = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        return scores.get(risk_level, 1)

    def _calculate_overall_risk(self, risk_assessments: List[Dict[str, Any]]) -> str:
        """
        Calculate overall risk level from individual assessments.

        Args:
            risk_assessments: List of individual risk assessments

        Returns:
            Overall risk level
        """
        if not risk_assessments:
            return "LOW"

        # Get maximum risk score
        max_score = max(
            self._get_risk_score(assessment.get("risk_level", "LOW"))
            for assessment in risk_assessments
        )

        # Map back to level
        score_to_level = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
        return score_to_level.get(max_score, "MEDIUM")

    def perform_comprehensive_assessment(
        self,
        cluster_info: Dict[str, Any],
        upgrade_path: List[str],
        deprecated_apis: Dict[str, List[Dict[str, Any]]],
        breaking_changes: List[Dict[str, Any]],
        addon_recommendations: List[Dict[str, Any]],
        node_groups: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment.

        Args:
            cluster_info: Cluster information
            upgrade_path: Upgrade path
            deprecated_apis: Deprecated APIs found
            breaking_changes: Breaking changes
            addon_recommendations: Addon recommendations
            node_groups: Node groups

        Returns:
            Comprehensive risk assessment
        """
        logger.info("Performing comprehensive risk assessment")

        # Individual assessments
        api_risk = self.assess_deprecated_api_risk(deprecated_apis)
        breaking_risk = self.assess_breaking_changes_risk(breaking_changes)
        addon_risk = self.assess_addon_compatibility_risk(addon_recommendations)
        version_risk = self.assess_version_jump_risk(upgrade_path)
        size_risk = self.assess_cluster_size_risk(node_groups)

        # Calculate overall risk
        all_assessments = [api_risk, breaking_risk, addon_risk, version_risk, size_risk]
        overall_risk = self._calculate_overall_risk(all_assessments)

        # Compile risk factors
        risk_factors = []
        mitigation_strategies = []

        if api_risk["risk_level"] in ["HIGH", "CRITICAL"]:
            risk_factors.append(f"⚠️  {api_risk['message']}")
            mitigation_strategies.append(
                "Update all deprecated API usage before upgrade"
            )

        if breaking_risk["risk_level"] in ["MEDIUM", "HIGH"]:
            risk_factors.append(f"⚠️  {breaking_risk['message']}")
            mitigation_strategies.append(
                "Review and test all breaking changes in staging"
            )

        if addon_risk["risk_level"] in ["MEDIUM", "HIGH"]:
            risk_factors.append(f"⚠️  {addon_risk['message']}")
            mitigation_strategies.append(
                "Upgrade incompatible addons before EKS upgrade"
            )

        if version_risk["version_jumps"] > 1:
            risk_factors.append(f"ℹ️  {version_risk['message']}")
            mitigation_strategies.append(
                "Plan for sequential upgrades with validation between"
            )

        if size_risk["risk_level"] in ["MEDIUM", "HIGH"]:
            risk_factors.append(f"ℹ️  {size_risk['message']}")
            mitigation_strategies.append("Plan for extended maintenance window")

        # Add positive factors
        positive_factors = []
        if api_risk["total_deprecated"] == 0:
            positive_factors.append("✅ No deprecated APIs in use")
        if addon_risk["incompatible_count"] == 0:
            positive_factors.append("✅ All addons compatible")
        if version_risk["version_jumps"] == 1:
            positive_factors.append("✅ Single version upgrade")

        # Estimate downtime
        downtime_estimate = self._estimate_downtime(
            overall_risk, version_risk["version_jumps"], size_risk["total_nodes"]
        )

        assessment = {
            "overall_risk": overall_risk,
            "risk_score": self._get_risk_score(overall_risk),
            "individual_assessments": {
                "deprecated_apis": api_risk,
                "breaking_changes": breaking_risk,
                "addon_compatibility": addon_risk,
                "version_jumps": version_risk,
                "cluster_size": size_risk,
            },
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "mitigation_strategies": mitigation_strategies,
            "estimated_downtime": downtime_estimate,
            "rollback_required": overall_risk in ["HIGH", "CRITICAL"],
            "staging_test_required": True,
        }

        logger.info(f"Risk assessment complete: Overall risk = {overall_risk}")
        return assessment

    def _estimate_downtime(
        self, risk_level: str, version_jumps: int, total_nodes: int
    ) -> Dict[str, Any]:
        """
        Estimate downtime window.

        Args:
            risk_level: Overall risk level
            version_jumps: Number of version jumps
            total_nodes: Total number of nodes

        Returns:
            Downtime estimation
        """
        # Base downtime in minutes
        base_downtime = 15  # Minimal downtime for control plane

        # Add time based on complexity
        additional_time = 0
        if risk_level in ["HIGH", "CRITICAL"]:
            additional_time += 30
        if version_jumps > 1:
            additional_time += 15 * version_jumps
        if total_nodes > 50:
            additional_time += 30

        total_downtime = base_downtime + additional_time

        return {
            "minimum_minutes": total_downtime,
            "recommended_window": f"{round(total_downtime / 60, 1)} - {round(total_downtime / 60 + 0.5, 1)} hours",
            "notes": "Control plane upgrade causes brief API unavailability",
        }

    def generate_risk_summary(self, assessment: Dict[str, Any]) -> str:
        """
        Generate human-readable risk summary.

        Args:
            assessment: Risk assessment dictionary

        Returns:
            Risk summary text
        """
        lines = [
            f"Risk Assessment Summary",
            "=" * 60,
            "",
            f"Overall Risk Level: {assessment['overall_risk']}",
            "",
        ]

        if assessment["risk_factors"]:
            lines.append("Risk Factors:")
            for factor in assessment["risk_factors"]:
                lines.append(f"  {factor}")
            lines.append("")

        if assessment["positive_factors"]:
            lines.append("Positive Factors:")
            for factor in assessment["positive_factors"]:
                lines.append(f"  {factor}")
            lines.append("")

        if assessment["mitigation_strategies"]:
            lines.append("Recommended Mitigations:")
            for i, strategy in enumerate(assessment["mitigation_strategies"], 1):
                lines.append(f"  {i}. {strategy}")
            lines.append("")

        lines.append(
            f"Estimated Downtime: {assessment['estimated_downtime']['recommended_window']}"
        )

        return "\n".join(lines)

"""JSON export for EKS upgrade plans."""

import json
from typing import Dict, Any
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JSONExporter:
    """Export upgrade plans in JSON format for programmatic consumption."""

    def __init__(self):
        """Initialize JSON exporter."""
        pass

    def export_report(
        self,
        cluster_info: Dict[str, Any],
        scan_results: Dict[str, Any],
        analysis_results: Dict[str, Any],
        upgrade_plan: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        migration_plan: Dict[str, Any],
    ) -> str:
        """
        Export comprehensive upgrade report as JSON.

        Args:
            cluster_info: Cluster information
            scan_results: Scan results
            analysis_results: Analysis results
            upgrade_plan: Upgrade plan
            risk_assessment: Risk assessment
            migration_plan: Migration plan

        Returns:
            JSON formatted string
        """
        logger.info("Generating JSON export")

        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool": "eks-upgrade-planner",
                "version": "1.0.0",
            },
            "cluster": {
                "name": cluster_info.get("cluster", {}).get("name"),
                "current_version": cluster_info.get("cluster", {}).get("version"),
                "target_version": (
                    upgrade_plan.get("upgrade_path", [])[-1]
                    if upgrade_plan.get("upgrade_path")
                    else None
                ),
                "region": cluster_info.get("cluster", {})
                .get("vpc_config", {})
                .get("vpcId"),
                "status": cluster_info.get("cluster", {}).get("status"),
            },
            "scan_results": scan_results,
            "analysis": {
                "compatibility": {
                    "addon_recommendations": analysis_results.get(
                        "addon_recommendations", []
                    ),
                    "version_compatibility": analysis_results.get(
                        "version_compatibility", {}
                    ),
                },
                "deprecations": {
                    "deprecated_apis": analysis_results.get("deprecated_apis", {}),
                    "summary": analysis_results.get("deprecation_summary", {}),
                },
                "breaking_changes": analysis_results.get("breaking_changes", []),
            },
            "upgrade_plan": {
                "upgrade_path": upgrade_plan.get("upgrade_path", []),
                "addon_upgrade_order": upgrade_plan.get("addon_upgrade_order", []),
                "pre_upgrade_checklist": upgrade_plan.get("pre_upgrade_checklist", []),
                "node_rotation_plan": upgrade_plan.get("node_rotation_plan", {}),
                "runbook": upgrade_plan.get("runbook", {}),
                "time_estimation": upgrade_plan.get("time_estimation", {}),
            },
            "risk_assessment": risk_assessment,
            "migration_plan": migration_plan,
        }

        json_output = json.dumps(report, indent=2, default=str)
        logger.info("JSON export generated successfully")
        return json_output

    def export_summary(
        self,
        cluster_info: Dict[str, Any],
        upgrade_plan: Dict[str, Any],
        risk_assessment: Dict[str, Any],
    ) -> str:
        """
        Export summary information as JSON.

        Args:
            cluster_info: Cluster information
            upgrade_plan: Upgrade plan
            risk_assessment: Risk assessment

        Returns:
            JSON formatted summary
        """
        logger.info("Generating JSON summary")

        summary = {
            "cluster_name": cluster_info.get("cluster", {}).get("name"),
            "current_version": cluster_info.get("cluster", {}).get("version"),
            "target_version": (
                upgrade_plan.get("upgrade_path", [])[-1]
                if upgrade_plan.get("upgrade_path")
                else None
            ),
            "risk_level": risk_assessment.get("overall_risk"),
            "version_jumps": len(upgrade_plan.get("upgrade_path", [])) - 1,
            "estimated_hours": upgrade_plan.get("time_estimation", {}).get(
                "total_hours"
            ),
            "node_groups": len(cluster_info.get("node_groups", [])),
            "addons": len(cluster_info.get("addons", [])),
            "deprecated_api_count": len(
                risk_assessment.get("individual_assessments", {})
                .get("deprecated_apis", {})
                .get("deprecated_apis", {})
            ),
            "breaking_changes_count": len(
                risk_assessment.get("individual_assessments", {})
                .get("breaking_changes", {})
                .get("breaking_changes", [])
            ),
        }

        return json.dumps(summary, indent=2)

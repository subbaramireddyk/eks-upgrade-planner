"""Markdown report generator for EKS upgrade plans."""

from typing import Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MarkdownReporter:
    """Generate Markdown format upgrade reports."""

    def __init__(self):
        """Initialize Markdown reporter."""
        pass

    def generate_report(
        self,
        cluster_info: Dict[str, Any],
        scan_results: Dict[str, Any],
        analysis_results: Dict[str, Any],
        upgrade_plan: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        migration_plan: Dict[str, Any],
    ) -> str:
        """
        Generate comprehensive Markdown upgrade report.

        Args:
            cluster_info: Cluster information
            scan_results: Scan results
            analysis_results: Analysis results
            upgrade_plan: Upgrade plan
            risk_assessment: Risk assessment
            migration_plan: Migration plan

        Returns:
            Markdown formatted report
        """
        logger.info("Generating Markdown report")

        sections = []

        # Title and metadata
        sections.append(self._generate_header(cluster_info, upgrade_plan))

        # Executive summary
        sections.append(
            self._generate_executive_summary(
                cluster_info, upgrade_plan, risk_assessment
            )
        )

        # Current state
        sections.append(self._generate_current_state(cluster_info, scan_results))

        # Upgrade path
        sections.append(self._generate_upgrade_path(upgrade_plan))

        # Pre-upgrade requirements
        sections.append(
            self._generate_pre_upgrade_requirements(upgrade_plan, analysis_results)
        )

        # Deprecated APIs
        if analysis_results.get("deprecated_apis"):
            sections.append(self._generate_deprecated_apis(analysis_results))

        # Breaking changes
        if analysis_results.get("breaking_changes"):
            sections.append(self._generate_breaking_changes(analysis_results))

        # Migration requirements
        if migration_plan.get("migration_required"):
            sections.append(self._generate_migration_requirements(migration_plan))

        # Detailed upgrade steps
        sections.append(self._generate_upgrade_steps(upgrade_plan))

        # Risk assessment
        sections.append(self._generate_risk_assessment(risk_assessment))

        # Rollback plan
        sections.append(self._generate_rollback_plan())

        # Timeline
        sections.append(self._generate_timeline(upgrade_plan))

        report = "\n\n".join(sections)
        logger.info("Markdown report generated successfully")
        return report

    def _generate_header(
        self, cluster_info: Dict[str, Any], upgrade_plan: Dict[str, Any]
    ) -> str:
        """Generate report header."""
        cluster = cluster_info.get("cluster", {})
        cluster_name = cluster.get("name", "Unknown")
        current_version = cluster.get("version", "Unknown")
        target_version = (
            upgrade_plan.get("upgrade_path", [])[-1]
            if upgrade_plan.get("upgrade_path")
            else "Unknown"
        )

        return f"""# EKS Upgrade Plan: {cluster_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Current Version:** {current_version}  
**Target Version:** {target_version}"""

    def _generate_executive_summary(
        self,
        cluster_info: Dict[str, Any],
        upgrade_plan: Dict[str, Any],
        risk_assessment: Dict[str, Any],
    ) -> str:
        """Generate executive summary."""
        cluster = cluster_info.get("cluster", {})
        upgrade_path = upgrade_plan.get("upgrade_path", [])
        time_est = upgrade_plan.get("time_estimation", {})

        current_version = cluster.get("version", "Unknown")
        target_version = upgrade_path[-1] if upgrade_path else "Unknown"
        risk_level = risk_assessment.get("overall_risk", "UNKNOWN")
        total_hours = time_est.get("total_hours", "Unknown")
        downtime = risk_assessment.get("estimated_downtime", {}).get(
            "recommended_window", "Unknown"
        )

        return f"""## Executive Summary

- **Current EKS Version:** {current_version}
- **Target EKS Version:** {target_version}
- **Risk Level:** {risk_level}
- **Estimated Effort:** {total_hours} hours
- **Recommended Downtime Window:** {downtime}
- **Version Jumps Required:** {len(upgrade_path) - 1 if upgrade_path else 0}"""

    def _generate_current_state(
        self, cluster_info: Dict[str, Any], scan_results: Dict[str, Any]
    ) -> str:
        """Generate current state section."""
        cluster = cluster_info.get("cluster", {})
        node_groups = cluster_info.get("node_groups", [])
        addons = cluster_info.get("addons", [])

        total_nodes = sum(
            ng.get("scaling_config", {}).get("desiredSize", 0) for ng in node_groups
        )

        return f"""## Current State

- **Cluster:** {cluster.get('name')} ({cluster.get('vpc_config', {}).get('vpcId', 'N/A')})
- **EKS Version:** {cluster.get('version')}
- **Platform Version:** {cluster.get('platform_version')}
- **Status:** {cluster.get('status')}
- **Node Groups:** {len(node_groups)} groups (total {total_nodes} nodes)
- **Addons:** {len(addons)} installed
- **Region:** {cluster.get('endpoint', '').split('.')[2] if cluster.get('endpoint') else 'Unknown'}

### Node Groups
{self._format_node_groups(node_groups)}

### Installed Addons
{self._format_addons(addons)}"""

    def _format_node_groups(self, node_groups: List[Dict[str, Any]]) -> str:
        """Format node groups as table."""
        if not node_groups:
            return "No node groups found."

        lines = [
            "| Name | Version | AMI Type | Capacity | Instance Types |",
            "| --- | --- | --- | --- | --- |",
        ]

        for ng in node_groups:
            name = ng.get("name", "N/A")
            version = ng.get("version", "N/A")
            ami_type = ng.get("ami_type", "N/A")
            desired = ng.get("scaling_config", {}).get("desiredSize", 0)
            instances = ", ".join(ng.get("instance_types", ["N/A"])[:2])

            lines.append(
                f"| {name} | {version} | {ami_type} | {desired} | {instances} |"
            )

        return "\n".join(lines)

    def _format_addons(self, addons: List[Dict[str, Any]]) -> str:
        """Format addons as table."""
        if not addons:
            return "No addons installed."

        lines = ["| Addon | Version | Status |", "| --- | --- | --- |"]

        for addon in addons:
            name = addon.get("name", "N/A")
            version = addon.get("version", "N/A")
            status = addon.get("status", "N/A")

            lines.append(f"| {name} | {version} | {status} |")

        return "\n".join(lines)

    def _generate_upgrade_path(self, upgrade_plan: Dict[str, Any]) -> str:
        """Generate upgrade path section."""
        upgrade_path = upgrade_plan.get("upgrade_path", [])

        if not upgrade_path or len(upgrade_path) < 2:
            return "## Upgrade Path\n\nNo upgrade needed."

        lines = ["## Upgrade Path\n"]

        for i, version in enumerate(upgrade_path, 1):
            if i == 1:
                lines.append(f"{i}. **Current:** EKS {version}")
            else:
                lines.append(f"{i}. ✅ Upgrade to EKS {version}")

        if len(upgrade_path) > 2:
            lines.append(
                "\n⚠️  **Note:** Cannot skip minor versions - sequential upgrades required"
            )

        return "\n".join(lines)

    def _generate_pre_upgrade_requirements(
        self, upgrade_plan: Dict[str, Any], analysis_results: Dict[str, Any]
    ) -> str:
        """Generate pre-upgrade requirements section."""
        addon_recs = analysis_results.get("addon_recommendations", [])
        deprecated_count = len(analysis_results.get("deprecated_apis", {}))

        lines = ["## Pre-Upgrade Requirements\n"]

        # Addon upgrades
        for addon in addon_recs:
            if addon.get("action_required"):
                current = addon.get("current_version", "Unknown")
                recommended = addon.get("recommended_version", "Unknown")
                lines.append(
                    f"- [ ] Update {addon.get('addon_name')}: {current} → {recommended}"
                )

        # API deprecations
        if deprecated_count > 0:
            lines.append(f"- [ ] Fix {deprecated_count} deprecated APIs in workloads")

        # Standard items
        lines.extend(
            [
                "- [ ] Backup cluster configuration and data",
                "- [ ] Test upgrade in staging environment",
                "- [ ] Review breaking changes documentation",
                "- [ ] Prepare rollback plan",
            ]
        )

        return "\n".join(lines)

    def _generate_deprecated_apis(self, analysis_results: Dict[str, Any]) -> str:
        """Generate deprecated APIs section."""
        deprecated_apis = analysis_results.get("deprecated_apis", {})

        total_count = sum(len(resources) for resources in deprecated_apis.values())

        lines = [
            f"## Deprecated APIs Found\n",
            f"⚠️  {total_count} resources using deprecated APIs:\n",
        ]

        for api_version, resources in deprecated_apis.items():
            deprecation_info = (
                resources[0].get("deprecation_info", {}) if resources else {}
            )
            replacement = deprecation_info.get("replacement", "N/A")
            removed_in = deprecation_info.get("removed_in", "N/A")

            lines.append(f"### {api_version} (removed in {removed_in})")
            lines.append(f"**Replacement:** {replacement}\n")

            for resource in resources[:10]:  # Limit to 10
                name = resource.get("name", "Unknown")
                kind = resource.get("kind", "Unknown")
                ns = resource.get("namespace", "default")
                lines.append(f"- {kind} `{name}` in namespace `{ns}`")

            if len(resources) > 10:
                lines.append(f"\n*... and {len(resources) - 10} more*")
            lines.append("")

        return "\n".join(lines)

    def _generate_breaking_changes(self, analysis_results: Dict[str, Any]) -> str:
        """Generate breaking changes section."""
        breaking_changes = analysis_results.get("breaking_changes", [])

        lines = [
            f"## Breaking Changes\n",
            f"Found {len(breaking_changes)} breaking changes:\n",
        ]

        for change in breaking_changes:
            impact = change.get("impact", "UNKNOWN")
            title = change.get("title", "Unknown")
            description = change.get("description", "")
            action = change.get("action", "Review manually")
            version = change.get("affects_version", "N/A")

            lines.append(f"### [{impact}] {title} (v{version})")
            lines.append(f"{description}")
            lines.append(f"**Action Required:** {action}\n")

        return "\n".join(lines)

    def _generate_migration_requirements(self, migration_plan: Dict[str, Any]) -> str:
        """Generate migration requirements section."""
        critical_migrations = migration_plan.get("critical_migrations", 0)
        total_resources = migration_plan.get("total_resources_affected", 0)

        lines = [
            "## Migration Requirements\n",
            f"- **Manifest Updates Required:** {total_resources} resources",
            f"- **Critical Migrations:** {critical_migrations}",
            f"- **Estimated Migration Time:** {migration_plan.get('estimated_migration_time', {}).get('total_hours', 'Unknown')} hours\n",
        ]

        # Manual interventions
        interventions = migration_plan.get("manual_interventions", [])
        if interventions:
            lines.append("### Manual Interventions Required\n")
            for intervention in interventions:
                priority = intervention.get("priority", "MEDIUM")
                description = intervention.get("description", "")
                action = intervention.get("action", "")
                lines.append(f"- **[{priority}]** {description}")
                lines.append(f"  - Action: {action}\n")

        return "\n".join(lines)

    def _generate_upgrade_steps(self, upgrade_plan: Dict[str, Any]) -> str:
        """Generate detailed upgrade steps."""
        runbook = upgrade_plan.get("runbook", {})
        phases = runbook.get("phases", [])

        lines = ["## Detailed Upgrade Steps\n"]

        for i, phase in enumerate(phases, 1):
            phase_name = phase.get("phase", f"Phase {i}")
            duration = phase.get("duration", "Unknown")
            steps = phase.get("steps", [])

            lines.append(f"### Phase {i}: {phase_name}")
            lines.append(f"**Estimated Duration:** {duration}\n")

            for j, step in enumerate(steps, 1):
                lines.append(f"{j}. {step}")

            lines.append("")

        return "\n".join(lines)

    def _generate_risk_assessment(self, risk_assessment: Dict[str, Any]) -> str:
        """Generate risk assessment section."""
        risk_level = risk_assessment.get("overall_risk", "UNKNOWN")
        risk_factors = risk_assessment.get("risk_factors", [])
        positive_factors = risk_assessment.get("positive_factors", [])
        mitigations = risk_assessment.get("mitigation_strategies", [])

        lines = [
            "## Risk Assessment\n",
            f"**Overall Risk Level:** {risk_level}\n",
        ]

        if risk_factors:
            lines.append("### Risk Factors\n")
            for factor in risk_factors:
                lines.append(f"- {factor}")
            lines.append("")

        if positive_factors:
            lines.append("### Positive Factors\n")
            for factor in positive_factors:
                lines.append(f"- {factor}")
            lines.append("")

        if mitigations:
            lines.append("### Mitigation Strategies\n")
            for i, mitigation in enumerate(mitigations, 1):
                lines.append(f"{i}. {mitigation}")
            lines.append("")

        return "\n".join(lines)

    def _generate_rollback_plan(self) -> str:
        """Generate rollback plan section."""
        return """## Rollback Plan

In case of issues during upgrade:

### Immediate Rollback (Control Plane)
EKS control plane upgrades cannot be rolled back. However, you can:
1. Keep worker nodes on previous version temporarily
2. Restore from backup if data corruption occurs
3. Deploy new cluster from backup if necessary

### Node Group Rollback
1. Create new node group with previous AMI version
2. Drain pods from upgraded nodes
3. Delete upgraded node group
4. Verify all workloads are healthy

### Application Rollback
1. Revert any manifest changes using backups
2. Re-deploy previous application versions
3. Verify functionality

### Prevention
- Maintain comprehensive backups before upgrade
- Test rollback procedures in staging
- Document all changes made during upgrade"""

    def _generate_timeline(self, upgrade_plan: Dict[str, Any]) -> str:
        """Generate estimated timeline section."""
        time_est = upgrade_plan.get("time_estimation", {})
        breakdown = time_est.get("breakdown", {})

        lines = [
            "## Estimated Timeline\n",
        ]

        for category, time in breakdown.items():
            formatted_category = category.replace("_", " ").title()
            lines.append(f"- **{formatted_category}:** {time}")

        total_hours = time_est.get("total_hours", "Unknown")
        lines.append(f"\n**Total Estimated Time:** {total_hours} hours")
        lines.append(
            f"**Recommended Maintenance Window:** {time_est.get('recommended_window', 'Unknown')}"
        )

        return "\n".join(lines)

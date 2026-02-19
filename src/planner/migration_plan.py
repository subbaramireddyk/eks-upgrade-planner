"""Migration plan generator for deprecated APIs and breaking changes."""

from typing import Dict, Any, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MigrationPlanner:
    """Planner for resource migrations and updates."""

    def __init__(self):
        """Initialize migration planner."""
        pass

    def detect_migration_requirements(
        self, deprecated_apis: Dict[str, List[Dict[str, Any]]], target_version: str
    ) -> Dict[str, Any]:
        """
        Detect if migrations are required for upgrade.

        Args:
            deprecated_apis: Deprecated APIs and affected resources
            target_version: Target Kubernetes version

        Returns:
            Migration requirements dictionary
        """
        logger.info(f"Detecting migration requirements for K8s {target_version}")

        migrations_required = []
        total_resources = 0

        for api_version, resources in deprecated_apis.items():
            for resource in resources:
                total_resources += 1
                deprecation_info = resource.get("deprecation_info", {})
                removed_in = deprecation_info.get("removed_in", "999.0")

                try:
                    if float(target_version) >= float(removed_in):
                        migrations_required.append(
                            {
                                "resource_name": resource.get("name"),
                                "resource_kind": resource.get("kind"),
                                "namespace": resource.get("namespace"),
                                "current_api": api_version,
                                "replacement_api": deprecation_info.get("replacement"),
                                "migration_notes": deprecation_info.get(
                                    "migration_notes"
                                ),
                                "priority": "CRITICAL",
                            }
                        )
                except ValueError:
                    pass

        result = {
            "migrations_required": len(migrations_required) > 0,
            "total_resources_affected": total_resources,
            "critical_migrations": len(migrations_required),
            "migrations": migrations_required,
        }

        logger.info(
            f"Migration detection complete: {len(migrations_required)} "
            f"critical migrations required"
        )

        return result

    def generate_manifest_examples(self, migration: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate before/after manifest examples for migration.

        Args:
            migration: Migration information

        Returns:
            Dictionary with 'before' and 'after' manifest examples
        """
        resource_kind = migration.get("resource_kind", "Deployment")
        resource_name = migration.get("resource_name", "example")
        namespace = migration.get("namespace", "default")
        current_api = migration.get("current_api", "apps/v1beta1")
        replacement_api = migration.get("replacement_api", "apps/v1")

        # Generate example manifests
        before = f"""# BEFORE - Deprecated API
apiVersion: {current_api}
kind: {resource_kind}
metadata:
  name: {resource_name}
  namespace: {namespace}
spec:
  # ... existing spec ...
"""

        after = f"""# AFTER - Updated API
apiVersion: {replacement_api}
kind: {resource_kind}
metadata:
  name: {resource_name}
  namespace: {namespace}
spec:
  # ... existing spec ...
  # Note: Review for any spec changes required
"""

        return {
            "before": before.strip(),
            "after": after.strip(),
        }

    def identify_manual_intervention_points(
        self, migrations: List[Dict[str, Any]], breaking_changes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify points requiring manual intervention.

        Args:
            migrations: List of migrations
            breaking_changes: List of breaking changes

        Returns:
            List of manual intervention points
        """
        logger.info("Identifying manual intervention points")

        intervention_points = []

        # API migrations always require manual review
        if migrations:
            intervention_points.append(
                {
                    "type": "api_migration",
                    "priority": "HIGH",
                    "description": f"{len(migrations)} resources need API version updates",
                    "action": "Update manifests and re-apply resources",
                    "estimated_time": f"{len(migrations) * 5} minutes",
                }
            )

        # Breaking changes may require code changes
        for change in breaking_changes:
            if change.get("impact") == "HIGH":
                intervention_points.append(
                    {
                        "type": "breaking_change",
                        "priority": "HIGH",
                        "description": change.get("title"),
                        "action": change.get("action"),
                        "estimated_time": "30-60 minutes",
                        "details": change.get("description"),
                    }
                )

        # CRD updates
        intervention_points.append(
            {
                "type": "crd_validation",
                "priority": "MEDIUM",
                "description": "Verify all CRDs are compatible",
                "action": "Check CRD versions and update if needed",
                "estimated_time": "15-30 minutes",
            }
        )

        logger.info(f"Identified {len(intervention_points)} intervention points")
        return intervention_points

    def create_testing_recommendations(
        self, migrations: List[Dict[str, Any]], cluster_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create testing recommendations for migrations.

        Args:
            migrations: List of migrations
            cluster_info: Cluster information

        Returns:
            List of testing recommendations
        """
        logger.info("Creating testing recommendations")

        recommendations = [
            {
                "category": "Pre-Migration Testing",
                "tests": [
                    "Backup all workload manifests",
                    "Export current resource definitions",
                    "Document current application behavior",
                ],
                "importance": "CRITICAL",
            },
            {
                "category": "Manifest Validation",
                "tests": [
                    "Validate updated manifests with kubectl apply --dry-run=server",
                    "Check for deprecation warnings with kubectl",
                    "Use pluto or kubent tools to scan for deprecated APIs",
                ],
                "importance": "HIGH",
            },
            {
                "category": "Staging Environment Testing",
                "tests": [
                    "Deploy updated manifests to staging cluster",
                    "Verify all pods start successfully",
                    "Test application functionality",
                    "Monitor for unexpected errors or warnings",
                    "Validate networking and service discovery",
                ],
                "importance": "CRITICAL",
            },
            {
                "category": "Rollback Testing",
                "tests": [
                    "Test rollback procedure",
                    "Verify ability to restore from backups",
                    "Document rollback steps",
                ],
                "importance": "HIGH",
            },
        ]

        if migrations:
            recommendations.append(
                {
                    "category": "API Migration Testing",
                    "tests": [
                        f"Test updated manifests for {len(migrations)} affected resources",
                        "Verify resource spec compatibility",
                        "Check for field renames or changes",
                    ],
                    "importance": "CRITICAL",
                }
            )

        logger.info(f"Created {len(recommendations)} testing categories")
        return recommendations

    def flag_resources_needing_recreation(
        self, migrations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Flag resources that may need to be recreated.

        Args:
            migrations: List of migrations

        Returns:
            List of resources needing recreation
        """
        logger.info("Flagging resources that may need recreation")

        # Resources that typically need recreation for API changes
        recreation_required = ["StatefulSet", "DaemonSet"]

        resources_to_recreate = []

        for migration in migrations:
            resource_kind = migration.get("resource_kind")

            if resource_kind in recreation_required:
                resources_to_recreate.append(
                    {
                        "resource_name": migration.get("resource_name"),
                        "resource_kind": resource_kind,
                        "namespace": migration.get("namespace"),
                        "reason": f"{resource_kind} may require recreation for API version change",
                        "procedure": [
                            "Export current resource definition",
                            "Update API version in manifest",
                            "Delete existing resource",
                            "Recreate with updated manifest",
                            "Verify pods are running",
                        ],
                        "risk": "HIGH",
                    }
                )

        logger.info(
            f"Flagged {len(resources_to_recreate)} resources for potential recreation"
        )
        return resources_to_recreate

    def generate_migration_plan(
        self,
        deprecated_apis: Dict[str, List[Dict[str, Any]]],
        breaking_changes: List[Dict[str, Any]],
        target_version: str,
        cluster_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive migration plan.

        Args:
            deprecated_apis: Deprecated APIs and affected resources
            breaking_changes: Breaking changes
            target_version: Target Kubernetes version
            cluster_info: Cluster information

        Returns:
            Complete migration plan
        """
        logger.info("Generating comprehensive migration plan")

        # Detect migration requirements
        migration_reqs = self.detect_migration_requirements(
            deprecated_apis, target_version
        )

        # Generate manifest examples for critical migrations
        manifest_examples = []
        for migration in migration_reqs.get("migrations", [])[
            :5
        ]:  # Limit to 5 examples
            examples = self.generate_manifest_examples(migration)
            manifest_examples.append(
                {
                    "resource": f"{migration['resource_kind']}/{migration['resource_name']}",
                    "namespace": migration["namespace"],
                    "examples": examples,
                }
            )

        # Identify manual interventions
        manual_interventions = self.identify_manual_intervention_points(
            migration_reqs.get("migrations", []), breaking_changes
        )

        # Create testing recommendations
        testing_recommendations = self.create_testing_recommendations(
            migration_reqs.get("migrations", []), cluster_info
        )

        # Flag resources needing recreation
        recreation_required = self.flag_resources_needing_recreation(
            migration_reqs.get("migrations", [])
        )

        migration_plan = {
            "migration_required": migration_reqs["migrations_required"],
            "total_resources_affected": migration_reqs["total_resources_affected"],
            "critical_migrations": migration_reqs["critical_migrations"],
            "migrations": migration_reqs["migrations"],
            "manifest_examples": manifest_examples,
            "manual_interventions": manual_interventions,
            "testing_recommendations": testing_recommendations,
            "resources_needing_recreation": recreation_required,
            "estimated_migration_time": self._estimate_migration_time(migration_reqs),
        }

        logger.info("Migration plan generated successfully")
        return migration_plan

    def _estimate_migration_time(
        self, migration_reqs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estimate time required for migrations.

        Args:
            migration_reqs: Migration requirements

        Returns:
            Time estimation
        """
        critical_migrations = migration_reqs.get("critical_migrations", 0)
        total_resources = migration_reqs.get("total_resources_affected", 0)

        # Base times in minutes
        time_per_critical = 10
        time_per_resource = 5
        testing_time = 60

        total_time = (
            (critical_migrations * time_per_critical)
            + ((total_resources - critical_migrations) * time_per_resource)
            + testing_time
        )

        return {
            "total_minutes": total_time,
            "total_hours": round(total_time / 60, 1),
            "breakdown": {
                "critical_migrations": f"{critical_migrations * time_per_critical} minutes",
                "other_updates": f"{(total_resources - critical_migrations) * time_per_resource} minutes",
                "testing": f"{testing_time} minutes",
            },
        }

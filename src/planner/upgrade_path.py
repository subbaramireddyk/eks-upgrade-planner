"""Upgrade path planning for EKS clusters."""

from typing import Dict, Any, List, Optional, Tuple
from ..utils.logger import get_logger
from ..analyzer.compatibility import CompatibilityAnalyzer

logger = get_logger(__name__)


class UpgradePathPlanner:
    """Planner for EKS upgrade paths."""

    def __init__(self, compatibility_analyzer: CompatibilityAnalyzer):
        """
        Initialize upgrade path planner.

        Args:
            compatibility_analyzer: Compatibility analyzer instance
        """
        self.compatibility_analyzer = compatibility_analyzer

    def generate_upgrade_path(
        self, current_version: str, target_version: str
    ) -> List[str]:
        """
        Generate sequential upgrade path from current to target version.

        Args:
            current_version: Current EKS version
            target_version: Target EKS version

        Returns:
            List of versions in upgrade sequence
        """
        logger.info(f"Generating upgrade path: {current_version} -> {target_version}")

        try:
            # Parse versions as major.minor
            current_parts = current_version.split(".")
            target_parts = target_version.split(".")

            if len(current_parts) != 2 or len(target_parts) != 2:
                logger.error("Invalid version format")
                return [current_version]

            current_major = int(current_parts[0])
            current_minor = int(current_parts[1])
            target_major = int(target_parts[0])
            target_minor = int(target_parts[1])

            # Check if already at or beyond target
            if current_major > target_major or (
                current_major == target_major and current_minor >= target_minor
            ):
                logger.warning("Current version is already at or beyond target")
                return [current_version]

            # Generate sequential path (can't skip minor versions in EKS)
            path = [current_version]

            # Only handle same major version upgrades (typical for EKS)
            if current_major == target_major:
                for minor in range(current_minor + 1, target_minor + 1):
                    path.append(f"{current_major}.{minor}")
            else:
                # Handle cross-major version (rare for EKS)
                logger.warning("Cross-major version upgrade detected")
                # First upgrade to latest minor in current major
                # Then to target (this is simplified and may need refinement)
                path.append(target_version)

            logger.info(f"Generated upgrade path: {' → '.join(path)}")
            return path

        except (ValueError, IndexError) as e:
            logger.error(f"Failed to generate upgrade path: {e}")
            return [current_version]

    def determine_addon_upgrade_order(
        self, addons: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Determine the order in which addons should be upgraded.

        Args:
            addons: List of addon information

        Returns:
            Ordered list of addons with upgrade priority
        """
        logger.info("Determining addon upgrade order")

        # Priority order for common addons (some must be upgraded before EKS)
        priority_order = {
            "vpc-cni": 1,  # Network plugin, critical
            "kube-proxy": 2,  # Core networking
            "coredns": 3,  # DNS
            "aws-ebs-csi-driver": 4,  # Storage
        }

        ordered_addons = []

        for addon in addons:
            addon_name = addon.get("name", "")
            priority = priority_order.get(addon_name, 99)  # Default low priority

            ordered_addons.append(
                {
                    **addon,
                    "upgrade_priority": priority,
                    "upgrade_timing": "before_eks" if priority <= 3 else "after_eks",
                }
            )

        # Sort by priority
        ordered_addons.sort(key=lambda x: x["upgrade_priority"])

        logger.info(f"Ordered {len(ordered_addons)} addons for upgrade")
        return ordered_addons

    def create_pre_upgrade_checklist(
        self, cluster_info: Dict[str, Any], target_version: str
    ) -> List[Dict[str, Any]]:
        """
        Create pre-upgrade checklist.

        Args:
            cluster_info: Current cluster information
            target_version: Target EKS version

        Returns:
            List of pre-upgrade tasks
        """
        logger.info("Creating pre-upgrade checklist")

        checklist = [
            {
                "category": "Backup",
                "task": "Backup etcd and cluster configuration",
                "required": True,
                "estimated_time": "30 minutes",
                "description": "Create full cluster backup including etcd snapshots",
            },
            {
                "category": "Backup",
                "task": "Document current cluster state",
                "required": True,
                "estimated_time": "15 minutes",
                "description": "Record current versions, node counts, and configurations",
            },
            {
                "category": "Testing",
                "task": "Test upgrade in non-production environment",
                "required": True,
                "estimated_time": "2-4 hours",
                "description": "Perform complete upgrade test in staging/dev cluster",
            },
            {
                "category": "Validation",
                "task": "Review breaking changes and deprecations",
                "required": True,
                "estimated_time": "1 hour",
                "description": f"Review all breaking changes for target version {target_version}",
            },
            {
                "category": "Addon",
                "task": "Verify addon compatibility",
                "required": True,
                "estimated_time": "30 minutes",
                "description": "Ensure all addons are compatible with target version",
            },
            {
                "category": "Workload",
                "task": "Update deprecated API usage in manifests",
                "required": True,
                "estimated_time": "1-3 hours",
                "description": "Update all workloads using deprecated APIs",
            },
            {
                "category": "Planning",
                "task": "Schedule maintenance window",
                "required": True,
                "estimated_time": "15 minutes",
                "description": "Coordinate downtime window with stakeholders",
            },
            {
                "category": "Rollback",
                "task": "Prepare rollback plan",
                "required": True,
                "estimated_time": "30 minutes",
                "description": "Document rollback procedure and test restoration",
            },
            {
                "category": "Monitoring",
                "task": "Set up enhanced monitoring",
                "required": False,
                "estimated_time": "20 minutes",
                "description": "Configure alerts for upgrade process",
            },
            {
                "category": "Access",
                "task": "Verify IAM permissions",
                "required": True,
                "estimated_time": "10 minutes",
                "description": "Ensure proper permissions for upgrade operations",
            },
        ]

        logger.info(f"Created checklist with {len(checklist)} items")
        return checklist

    def plan_node_group_rotation(
        self, node_groups: List[Dict[str, Any]], strategy: str = "rolling"
    ) -> Dict[str, Any]:
        """
        Plan node group rotation strategy.

        Args:
            node_groups: List of node groups
            strategy: Rotation strategy ('rolling' or 'blue-green')

        Returns:
            Node rotation plan
        """
        logger.info(f"Planning node group rotation with {strategy} strategy")

        rotation_plan = {
            "strategy": strategy,
            "node_groups": [],
            "estimated_time": "1-2 hours per node group",
        }

        for ng in node_groups:
            ng_plan = {
                "name": ng.get("name"),
                "current_version": ng.get("version"),
                "current_capacity": ng.get("scaling_config", {}).get("desiredSize", 0),
                "strategy": strategy,
            }

            if strategy == "rolling":
                ng_plan["steps"] = [
                    "Update node group AMI version",
                    "Set max unavailable to 1",
                    "Trigger rolling update",
                    "Monitor node replacement",
                    "Verify workload health",
                ]
            elif strategy == "blue-green":
                ng_plan["steps"] = [
                    "Create new node group with target version",
                    "Cordon old nodes",
                    "Drain workloads to new nodes",
                    "Verify workload health",
                    "Delete old node group",
                ]

            rotation_plan["node_groups"].append(ng_plan)

        logger.info(f"Planned rotation for {len(node_groups)} node groups")
        return rotation_plan

    def create_upgrade_runbook(
        self,
        cluster_name: str,
        upgrade_path: List[str],
        addons: List[Dict[str, Any]],
        node_groups: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create detailed step-by-step upgrade runbook.

        Args:
            cluster_name: Cluster name
            upgrade_path: Upgrade path versions
            addons: Addons to upgrade
            node_groups: Node groups to rotate

        Returns:
            Complete upgrade runbook
        """
        logger.info(f"Creating upgrade runbook for cluster {cluster_name}")

        runbook = {
            "cluster_name": cluster_name,
            "upgrade_path": upgrade_path,
            "phases": [],
        }

        # Phase 1: Pre-upgrade
        runbook["phases"].append(
            {
                "phase": "Pre-Upgrade Preparation",
                "duration": "2-4 hours",
                "steps": [
                    "Complete all checklist items",
                    "Backup cluster and workload data",
                    "Verify rollback plan",
                    "Communicate maintenance window",
                ],
            }
        )

        # Phase 2: Addon upgrades (before EKS)
        ordered_addons = self.determine_addon_upgrade_order(addons)
        pre_eks_addons = [
            a for a in ordered_addons if a.get("upgrade_timing") == "before_eks"
        ]

        if pre_eks_addons:
            addon_steps = []
            for addon in pre_eks_addons:
                addon_steps.append(f"Upgrade {addon.get('name')} to compatible version")

            runbook["phases"].append(
                {
                    "phase": "Critical Addon Updates (Pre-EKS)",
                    "duration": "30-60 minutes",
                    "steps": addon_steps,
                }
            )

        # Phase 3: EKS control plane upgrades
        for i, version in enumerate(upgrade_path[1:], 1):
            runbook["phases"].append(
                {
                    "phase": f"EKS Control Plane Upgrade to {version}",
                    "duration": "30-45 minutes",
                    "steps": [
                        f"Update cluster version to {version}",
                        "Wait for control plane to be active",
                        "Verify control plane health",
                        "Check API server logs",
                    ],
                }
            )

        # Phase 4: Node group updates
        runbook["phases"].append(
            {
                "phase": "Node Group Updates",
                "duration": "1-2 hours",
                "steps": [
                    "Update node group AMI to match control plane version",
                    "Perform rolling update of nodes",
                    "Monitor pod rescheduling",
                    "Verify all nodes are ready",
                ],
            }
        )

        # Phase 5: Post-upgrade addon updates
        post_eks_addons = [
            a for a in ordered_addons if a.get("upgrade_timing") == "after_eks"
        ]

        if post_eks_addons:
            addon_steps = []
            for addon in post_eks_addons:
                addon_steps.append(
                    f"Upgrade {addon.get('name')} to recommended version"
                )

            runbook["phases"].append(
                {
                    "phase": "Additional Addon Updates (Post-EKS)",
                    "duration": "20-30 minutes",
                    "steps": addon_steps,
                }
            )

        # Phase 6: Validation
        runbook["phases"].append(
            {
                "phase": "Post-Upgrade Validation",
                "duration": "30-60 minutes",
                "steps": [
                    "Verify cluster version",
                    "Check all nodes are ready",
                    "Verify all pods are running",
                    "Test critical workloads",
                    "Review cluster logs",
                    "Validate monitoring and alerts",
                    "Run smoke tests",
                ],
            }
        )

        logger.info(f"Created runbook with {len(runbook['phases'])} phases")
        return runbook

    def estimate_upgrade_time(
        self,
        upgrade_path: List[str],
        node_groups: List[Dict[str, Any]],
        addons: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Estimate total upgrade time.

        Args:
            upgrade_path: Upgrade path versions
            node_groups: Node groups
            addons: Addons to upgrade

        Returns:
            Time estimation breakdown
        """
        # Base times in minutes
        pre_upgrade_time = 120  # 2 hours for prep
        control_plane_time_per_version = 40  # 40 min per version upgrade
        node_rotation_time_per_group = 90  # 1.5 hours per node group
        addon_time = 10 * len(addons)  # 10 min per addon
        validation_time = 45  # 45 min for validation

        # Calculate
        num_upgrades = len(upgrade_path) - 1  # Number of version jumps
        control_plane_time = control_plane_time_per_version * num_upgrades
        node_time = node_rotation_time_per_group * len(node_groups)

        total_minutes = (
            pre_upgrade_time
            + control_plane_time
            + node_time
            + addon_time
            + validation_time
        )

        estimation = {
            "breakdown": {
                "pre_upgrade": f"{pre_upgrade_time} minutes",
                "control_plane_upgrades": f"{control_plane_time} minutes ({num_upgrades} upgrades)",
                "node_rotations": f"{node_time} minutes ({len(node_groups)} groups)",
                "addon_upgrades": f"{addon_time} minutes ({len(addons)} addons)",
                "validation": f"{validation_time} minutes",
            },
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 1),
            "recommended_window": f"{round(total_minutes / 60 + 1)} hours",  # Add buffer
        }

        logger.info(f"Estimated total upgrade time: {estimation['total_hours']} hours")
        return estimation

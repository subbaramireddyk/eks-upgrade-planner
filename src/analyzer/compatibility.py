"""Compatibility analysis for EKS versions, addons, and APIs."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CompatibilityAnalyzer:
    """Analyzer for version compatibility checks."""

    def __init__(
        self,
        compatibility_matrix: Optional[Dict] = None,
        addon_data: Optional[Dict] = None,
    ):
        """
        Initialize compatibility analyzer.

        Args:
            compatibility_matrix: Optional custom compatibility matrix
            addon_data: Optional custom addon version data
        """
        self.compatibility_matrix = (
            compatibility_matrix or self._load_compatibility_matrix()
        )
        self.addon_data = addon_data or self._load_addon_data()

        # Extract EKS to K8s version mapping from loaded data
        self.EKS_K8S_VERSIONS = {}
        if "eks_versions" in self.compatibility_matrix:
            for version, info in self.compatibility_matrix["eks_versions"].items():
                self.EKS_K8S_VERSIONS[version] = info.get("kubernetes_version", version)

        # Extract addon compatibility from loaded data
        self.ADDON_COMPATIBILITY = self._build_addon_compatibility()

    def _load_compatibility_matrix(self) -> Dict[str, Any]:
        """Load compatibility matrix from YAML file."""
        try:
            # Find the data directory relative to this file
            current_dir = Path(__file__).parent.parent.parent
            data_file = current_dir / "data" / "compatibility_matrix.yaml"

            if data_file.exists():
                with open(data_file, "r") as f:
                    data = yaml.safe_load(f)
                    logger.debug(f"Loaded compatibility matrix from {data_file}")
                    return data
            else:
                logger.warning(f"Compatibility matrix file not found: {data_file}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load compatibility matrix: {e}")
            return {}

    def _load_addon_data(self) -> Dict[str, Any]:
        """Load addon version data from YAML file."""
        try:
            # Find the data directory relative to this file
            current_dir = Path(__file__).parent.parent.parent
            data_file = current_dir / "data" / "addon_versions.yaml"

            if data_file.exists():
                with open(data_file, "r") as f:
                    data = yaml.safe_load(f)
                    logger.debug(f"Loaded addon data from {data_file}")
                    return data
            else:
                logger.warning(f"Addon data file not found: {data_file}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load addon data: {e}")
            return {}

    def _build_addon_compatibility(self) -> Dict[str, Dict[str, List[str]]]:
        """Build addon compatibility dictionary from loaded YAML data."""
        compatibility = {}

        if "addons" not in self.addon_data:
            return compatibility

        for addon_name, addon_info in self.addon_data["addons"].items():
            if "versions" not in addon_info:
                continue

            for eks_version, version_info in addon_info["versions"].items():
                if eks_version not in compatibility:
                    compatibility[eks_version] = {}

                minimum = version_info.get("minimum", "")
                recommended = version_info.get("recommended", "")

                # Store as list with [minimum, recommended]
                compatibility[eks_version][addon_name] = [minimum, recommended]

        logger.debug(f"Built addon compatibility for {len(compatibility)} EKS versions")
        return compatibility

    def _validate_version_format(self, version: str) -> bool:
        """
        Validate EKS version format.

        Args:
            version: Version string to validate

        Returns:
            True if valid, False otherwise
        """
        if not version:
            return False

        # Check if version matches pattern like "1.27", "1.28", etc.
        parts = version.split(".")
        if len(parts) != 2:
            return False

        try:
            major = int(parts[0])
            minor = int(parts[1])
            return major > 0 and minor >= 0
        except ValueError:
            return False

    def _parse_version(self, version: str) -> Tuple[int, int]:
        """
        Parse version string into major and minor components.

        Args:
            version: Version string (e.g., "1.27")

        Returns:
            Tuple of (major, minor)

        Raises:
            ValueError: If version format is invalid
        """
        if not self._validate_version_format(version):
            raise ValueError(f"Invalid version format: {version}")

        parts = version.split(".")
        return int(parts[0]), int(parts[1])

    def get_k8s_version(self, eks_version: str) -> Optional[str]:
        """
        Get Kubernetes version for an EKS version.

        Args:
            eks_version: EKS version

        Returns:
            Kubernetes version or None
        """
        return self.EKS_K8S_VERSIONS.get(eks_version)

    def is_version_supported(self, eks_version: str) -> bool:
        """
        Check if EKS version is supported.

        Args:
            eks_version: EKS version to check

        Returns:
            True if supported, False otherwise
        """
        return eks_version in self.EKS_K8S_VERSIONS

    def can_upgrade_directly(
        self, from_version: str, to_version: str
    ) -> Tuple[bool, str]:
        """
        Check if direct upgrade is possible between versions.

        Args:
            from_version: Current EKS version
            to_version: Target EKS version

        Returns:
            Tuple of (can_upgrade, reason)
        """
        # Validate version formats
        if not self._validate_version_format(from_version):
            return False, f"Invalid source version format: {from_version}"

        if not self._validate_version_format(to_version):
            return False, f"Invalid target version format: {to_version}"

        if not self.is_version_supported(from_version):
            return False, f"Unsupported source version: {from_version}"

        if not self.is_version_supported(to_version):
            return False, f"Unsupported target version: {to_version}"

        try:
            from_major, from_minor = self._parse_version(from_version)
            to_major, to_minor = self._parse_version(to_version)

            # Compare versions
            if to_major < from_major or (
                to_major == from_major and to_minor < from_minor
            ):
                return False, "Cannot downgrade EKS versions"

            if to_major == from_major and to_minor == from_minor:
                return True, "Same version (no upgrade needed)"

            # EKS requires sequential minor version upgrades (can't skip versions)
            # Check if versions are consecutive
            if to_major == from_major:
                # Same major version, check minor version difference
                if to_minor - from_minor == 1:
                    return True, "Direct upgrade supported"
                elif to_minor - from_minor > 1:
                    return False, "Cannot skip minor versions in EKS upgrade"
                else:
                    return True, "Direct upgrade supported"
            else:
                # Different major versions - not typical for EKS but handle it
                return False, "Cannot upgrade across major versions"

        except ValueError as e:
            return False, f"Invalid version format: {e}"

    def check_addon_compatibility(
        self, addon_name: str, addon_version: str, eks_version: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if addon version is compatible with EKS version.

        Args:
            addon_name: Name of the addon
            addon_version: Current addon version
            eks_version: Target EKS version

        Returns:
            Tuple of (is_compatible, recommended_version)
        """
        if eks_version not in self.ADDON_COMPATIBILITY:
            logger.warning(f"No compatibility data for EKS {eks_version}")
            return False, None

        if addon_name not in self.ADDON_COMPATIBILITY[eks_version]:
            logger.warning(f"No compatibility data for addon {addon_name}")
            return False, None

        compatible_versions = self.ADDON_COMPATIBILITY[eks_version][addon_name]

        # Check if current version is in compatible list
        is_compatible = any(addon_version in v for v in compatible_versions)

        # Recommend latest version
        recommended = compatible_versions[-1] if compatible_versions else None

        return is_compatible, recommended

    def get_addon_recommendations(
        self, current_addons: List[Dict[str, Any]], target_eks_version: str
    ) -> List[Dict[str, Any]]:
        """
        Get addon upgrade recommendations for target EKS version.

        Args:
            current_addons: List of current addon information
            target_eks_version: Target EKS version

        Returns:
            List of addon recommendations
        """
        recommendations = []

        for addon in current_addons:
            addon_name = addon.get("name")
            addon_version = addon.get("version", "")

            is_compatible, recommended = self.check_addon_compatibility(
                addon_name, addon_version, target_eks_version
            )

            recommendation = {
                "addon_name": addon_name,
                "current_version": addon_version,
                "target_eks_version": target_eks_version,
                "is_compatible": is_compatible,
                "recommended_version": recommended,
                "action_required": not is_compatible,
            }

            if not is_compatible and recommended:
                recommendation["action"] = f"Upgrade to {recommended}"
            elif is_compatible:
                recommendation["action"] = "No action required"
            else:
                recommendation["action"] = "Review addon compatibility manually"

            recommendations.append(recommendation)

        return recommendations

    def validate_upgrade_path(
        self,
        current_version: str,
        target_version: str,
        current_addons: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validate complete upgrade path including addons.

        Args:
            current_version: Current EKS version
            target_version: Target EKS version
            current_addons: List of current addons

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating upgrade path: {current_version} -> {target_version}")

        can_upgrade, reason = self.can_upgrade_directly(current_version, target_version)

        # Get addon recommendations for target version
        addon_recommendations = self.get_addon_recommendations(
            current_addons, target_version
        )

        # Check if any addons require action
        addons_need_upgrade = any(
            rec["action_required"] for rec in addon_recommendations
        )

        result = {
            "current_version": current_version,
            "target_version": target_version,
            "can_upgrade": can_upgrade,
            "reason": reason,
            "addons_compatible": not addons_need_upgrade,
            "addon_recommendations": addon_recommendations,
            "blocking_issues": [],
        }

        if not can_upgrade:
            result["blocking_issues"].append(
                {
                    "type": "version_incompatibility",
                    "message": reason,
                }
            )

        if addons_need_upgrade:
            result["blocking_issues"].append(
                {
                    "type": "addon_compatibility",
                    "message": "Some addons require updates before upgrade",
                    "addons": [
                        rec for rec in addon_recommendations if rec["action_required"]
                    ],
                }
            )

        logger.info(
            f"Validation complete: {len(result['blocking_issues'])} issues found"
        )
        return result

    def get_supported_versions(self) -> List[str]:
        """
        Get list of supported EKS versions.

        Returns:
            List of supported version strings
        """
        return sorted(self.EKS_K8S_VERSIONS.keys(), key=lambda x: float(x))

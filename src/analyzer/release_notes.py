"""Release notes fetcher for EKS and addon versions."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from ..utils.logger import get_logger
from ..utils.cache import Cache

logger = get_logger(__name__)


class ReleaseNotesAnalyzer:
    """Analyzer for EKS and addon release notes."""

    # AWS EKS documentation URLs
    EKS_RELEASE_NOTES_BASE = "https://docs.aws.amazon.com/eks/latest/userguide"
    EKS_VERSION_URL_TEMPLATE = f"{EKS_RELEASE_NOTES_BASE}/kubernetes-versions.html"

    # GitHub release URLs for common addons
    ADDON_RELEASE_URLS = {
        "vpc-cni": "https://github.com/aws/amazon-vpc-cni-k8s/releases",
        "aws-ebs-csi-driver": "https://github.com/kubernetes-sigs/aws-ebs-csi-driver/releases",
        "coredns": "https://github.com/coredns/coredns/releases",
        "kube-proxy": "https://github.com/kubernetes/kubernetes/releases",
    }

    def __init__(self, cache: Optional[Cache] = None):
        """
        Initialize release notes analyzer.

        Args:
            cache: Optional cache instance
        """
        self.cache = cache or Cache()

    def _fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch URL content with error handling.

        Args:
            url: URL to fetch

        Returns:
            Response text or None
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def fetch_eks_version_info(self, eks_version: str) -> Dict[str, Any]:
        """
        Fetch EKS version information and release notes.

        Args:
            eks_version: EKS version (e.g., '1.29')

        Returns:
            Version information dictionary
        """
        cache_key = f"eks_version_info_{eks_version}"

        # Check cache first
        cached = self.cache.get_json(cache_key)
        if cached:
            logger.debug(f"Using cached EKS version info for {eks_version}")
            return cached

        logger.info(f"Fetching EKS version info for {eks_version}")

        # Static information (in production, this would be fetched from AWS docs)
        version_info = {
            "eks_version": eks_version,
            "kubernetes_version": eks_version,
            "release_date": None,
            "end_of_support": None,
            "end_of_extended_support": None,
            "breaking_changes": [],
            "important_changes": [],
            "notes": f"EKS {eks_version} release information",
        }

        # Try to fetch from AWS documentation
        content = self._fetch_url(self.EKS_VERSION_URL_TEMPLATE)
        if content:
            # Parse HTML to extract version-specific information
            # This is a simplified implementation
            version_info["notes"] = (
                f"See {self.EKS_VERSION_URL_TEMPLATE} for full details"
            )

        # Cache the result
        self.cache.set_json(cache_key, version_info)

        return version_info

    def fetch_addon_release_notes(
        self, addon_name: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch addon release notes.

        Args:
            addon_name: Name of the addon
            version: Optional specific version

        Returns:
            Release notes dictionary
        """
        cache_key = f"addon_release_{addon_name}_{version or 'latest'}"

        # Check cache first
        cached = self.cache.get_json(cache_key)
        if cached:
            logger.debug(f"Using cached addon release notes for {addon_name}")
            return cached

        logger.info(f"Fetching release notes for addon {addon_name}")

        release_notes = {
            "addon_name": addon_name,
            "version": version,
            "release_url": self.ADDON_RELEASE_URLS.get(addon_name),
            "notes": [],
            "breaking_changes": [],
        }

        # In production, fetch from actual release URLs
        # This is simplified for now
        if addon_name in self.ADDON_RELEASE_URLS:
            release_notes["notes"].append(
                f"See {self.ADDON_RELEASE_URLS[addon_name]} for release notes"
            )

        # Cache the result
        self.cache.set_json(cache_key, release_notes)

        return release_notes

    def get_breaking_changes(
        self, from_version: str, to_version: str
    ) -> List[Dict[str, Any]]:
        """
        Get breaking changes between EKS versions.

        Args:
            from_version: Current EKS version
            to_version: Target EKS version

        Returns:
            List of breaking changes
        """
        logger.info(f"Fetching breaking changes: {from_version} -> {to_version}")

        breaking_changes = []

        # Known breaking changes by version
        known_changes = {
            "1.22": [
                {
                    "type": "api_removal",
                    "title": "Beta API removals",
                    "description": "Several beta APIs removed including Ingress v1beta1",
                    "impact": "HIGH",
                    "action": "Update manifests to use stable API versions",
                },
            ],
            "1.23": [
                {
                    "type": "deprecation",
                    "title": "FlexVolume deprecated",
                    "description": "FlexVolume is deprecated, use CSI drivers",
                    "impact": "MEDIUM",
                    "action": "Migrate to CSI drivers",
                },
            ],
            "1.24": [
                {
                    "type": "feature_removal",
                    "title": "Dockershim removed",
                    "description": "Docker runtime support removed, use containerd",
                    "impact": "HIGH",
                    "action": "Ensure using containerd runtime",
                },
            ],
            "1.25": [
                {
                    "type": "api_removal",
                    "title": "PodSecurityPolicy removed",
                    "description": "PSP API removed, migrate to Pod Security Standards",
                    "impact": "HIGH",
                    "action": "Implement Pod Security Standards",
                },
                {
                    "type": "api_removal",
                    "title": "Beta API removals",
                    "description": "CronJob v1beta1, PodDisruptionBudget v1beta1 removed",
                    "impact": "HIGH",
                    "action": "Update to stable v1 APIs",
                },
            ],
            "1.26": [
                {
                    "type": "api_removal",
                    "title": "HPA v2beta2 removed",
                    "description": "HorizontalPodAutoscaler v2beta2 API removed",
                    "impact": "MEDIUM",
                    "action": "Update to autoscaling/v2",
                },
            ],
            "1.27": [
                {
                    "type": "deprecation",
                    "title": "CSI migration",
                    "description": "In-tree storage plugins being migrated to CSI",
                    "impact": "MEDIUM",
                    "action": "Review storage configuration",
                },
            ],
        }

        # Collect breaking changes for all versions in upgrade path
        try:
            from_minor = float(from_version)
            to_minor = float(to_version)

            for version, changes in known_changes.items():
                version_minor = float(version)
                if from_minor < version_minor <= to_minor:
                    for change in changes:
                        change["affects_version"] = version
                        breaking_changes.append(change)
        except ValueError:
            logger.warning("Invalid version format for breaking changes lookup")

        logger.info(f"Found {len(breaking_changes)} breaking changes")
        return breaking_changes

    def get_upgrade_notes(
        self, from_version: str, to_version: str, addons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get comprehensive upgrade notes including version and addon changes.

        Args:
            from_version: Current EKS version
            to_version: Target EKS version
            addons: List of current addons

        Returns:
            Comprehensive upgrade notes
        """
        logger.info(f"Generating upgrade notes: {from_version} -> {to_version}")

        # Get version information
        target_version_info = self.fetch_eks_version_info(to_version)

        # Get breaking changes
        breaking_changes = self.get_breaking_changes(from_version, to_version)

        # Get addon release notes
        addon_notes = []
        for addon in addons:
            addon_name = addon.get("name")
            addon_version = addon.get("version")
            if addon_name:
                notes = self.fetch_addon_release_notes(addon_name, addon_version)
                addon_notes.append(notes)

        upgrade_notes = {
            "from_version": from_version,
            "to_version": to_version,
            "target_version_info": target_version_info,
            "breaking_changes": breaking_changes,
            "addon_release_notes": addon_notes,
            "important_links": [
                {
                    "title": "EKS Kubernetes Versions",
                    "url": self.EKS_VERSION_URL_TEMPLATE,
                },
                {
                    "title": "EKS Best Practices",
                    "url": "https://aws.github.io/aws-eks-best-practices/",
                },
            ],
        }

        logger.info("Upgrade notes generated successfully")
        return upgrade_notes

    def summarize_changes(self, upgrade_notes: Dict[str, Any]) -> str:
        """
        Create a human-readable summary of upgrade changes.

        Args:
            upgrade_notes: Upgrade notes dictionary

        Returns:
            Summary text
        """
        breaking_changes = upgrade_notes.get("breaking_changes", [])

        summary_lines = [
            f"Upgrade Summary: {upgrade_notes['from_version']} → {upgrade_notes['to_version']}",
            "=" * 60,
            "",
        ]

        if breaking_changes:
            summary_lines.append(f"⚠️  {len(breaking_changes)} Breaking Changes:")
            for change in breaking_changes:
                summary_lines.append(
                    f"  - [{change['impact']}] {change['title']} (v{change['affects_version']})"
                )
                summary_lines.append(f"    Action: {change['action']}")
            summary_lines.append("")
        else:
            summary_lines.append("✅ No known breaking changes")
            summary_lines.append("")

        addon_notes = upgrade_notes.get("addon_release_notes", [])
        if addon_notes:
            summary_lines.append(f"📦 {len(addon_notes)} Addons to Review:")
            for addon in addon_notes:
                summary_lines.append(
                    f"  - {addon['addon_name']} ({addon.get('version', 'N/A')})"
                )
            summary_lines.append("")

        return "\n".join(summary_lines)

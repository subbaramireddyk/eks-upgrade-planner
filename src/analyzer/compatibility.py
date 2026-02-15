"""Compatibility analysis for EKS versions, addons, and APIs."""

from typing import Dict, Any, List, Optional, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CompatibilityAnalyzer:
    """Analyzer for version compatibility checks."""
    
    # EKS to Kubernetes version mapping
    EKS_K8S_VERSIONS = {
        '1.23': '1.23',
        '1.24': '1.24',
        '1.25': '1.25',
        '1.26': '1.26',
        '1.27': '1.27',
        '1.28': '1.28',
        '1.29': '1.29',
        '1.30': '1.30',
    }
    
    # Core addon minimum versions per EKS version
    ADDON_COMPATIBILITY = {
        '1.27': {
            'coredns': ['v1.9.3-eksbuild.1', 'v1.10.1-eksbuild.1'],
            'kube-proxy': ['v1.27.1-eksbuild.1', 'v1.27.6-eksbuild.1'],
            'vpc-cni': ['v1.12.0-eksbuild.1', 'v1.15.1-eksbuild.1'],
            'aws-ebs-csi-driver': ['v1.19.0-eksbuild.1', 'v1.25.0-eksbuild.1'],
        },
        '1.28': {
            'coredns': ['v1.10.1-eksbuild.1', 'v1.10.1-eksbuild.2'],
            'kube-proxy': ['v1.28.1-eksbuild.1', 'v1.28.6-eksbuild.1'],
            'vpc-cni': ['v1.13.0-eksbuild.1', 'v1.16.0-eksbuild.1'],
            'aws-ebs-csi-driver': ['v1.20.0-eksbuild.1', 'v1.26.0-eksbuild.1'],
        },
        '1.29': {
            'coredns': ['v1.10.1-eksbuild.1', 'v1.11.1-eksbuild.1'],
            'kube-proxy': ['v1.29.0-eksbuild.1', 'v1.29.3-eksbuild.1'],
            'vpc-cni': ['v1.14.0-eksbuild.1', 'v1.16.2-eksbuild.1'],
            'aws-ebs-csi-driver': ['v1.22.0-eksbuild.1', 'v1.27.0-eksbuild.1'],
        },
        '1.30': {
            'coredns': ['v1.11.1-eksbuild.1', 'v1.11.1-eksbuild.2'],
            'kube-proxy': ['v1.30.0-eksbuild.1', 'v1.30.0-eksbuild.3'],
            'vpc-cni': ['v1.16.0-eksbuild.1', 'v1.18.0-eksbuild.1'],
            'aws-ebs-csi-driver': ['v1.25.0-eksbuild.1', 'v1.28.0-eksbuild.1'],
        },
    }
    
    def __init__(self, compatibility_matrix: Optional[Dict] = None):
        """
        Initialize compatibility analyzer.
        
        Args:
            compatibility_matrix: Optional custom compatibility matrix
        """
        self.compatibility_matrix = compatibility_matrix or {}
    
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
    
    def can_upgrade_directly(self, from_version: str, to_version: str) -> Tuple[bool, str]:
        """
        Check if direct upgrade is possible between versions.
        
        Args:
            from_version: Current EKS version
            to_version: Target EKS version
            
        Returns:
            Tuple of (can_upgrade, reason)
        """
        if not self.is_version_supported(from_version):
            return False, f"Unsupported source version: {from_version}"
        
        if not self.is_version_supported(to_version):
            return False, f"Unsupported target version: {to_version}"
        
        try:
            from_minor = float(from_version)
            to_minor = float(to_version)
            
            if to_minor < from_minor:
                return False, "Cannot downgrade EKS versions"
            
            if to_minor == from_minor:
                return True, "Same version (no upgrade needed)"
            
            # EKS requires sequential minor version upgrades
            if to_minor - from_minor > 0.01:  # More than one minor version
                return False, "Cannot skip minor versions in EKS upgrade"
            
            return True, "Direct upgrade supported"
            
        except ValueError:
            return False, "Invalid version format"
    
    def check_addon_compatibility(
        self,
        addon_name: str,
        addon_version: str,
        eks_version: str
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
        self,
        current_addons: List[Dict[str, Any]],
        target_eks_version: str
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
            addon_name = addon.get('name')
            addon_version = addon.get('version', '')
            
            is_compatible, recommended = self.check_addon_compatibility(
                addon_name,
                addon_version,
                target_eks_version
            )
            
            recommendation = {
                'addon_name': addon_name,
                'current_version': addon_version,
                'target_eks_version': target_eks_version,
                'is_compatible': is_compatible,
                'recommended_version': recommended,
                'action_required': not is_compatible,
            }
            
            if not is_compatible and recommended:
                recommendation['action'] = f"Upgrade to {recommended}"
            elif is_compatible:
                recommendation['action'] = "No action required"
            else:
                recommendation['action'] = "Review addon compatibility manually"
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def validate_upgrade_path(
        self,
        current_version: str,
        target_version: str,
        current_addons: List[Dict[str, Any]]
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
            current_addons,
            target_version
        )
        
        # Check if any addons require action
        addons_need_upgrade = any(
            rec['action_required'] for rec in addon_recommendations
        )
        
        result = {
            'current_version': current_version,
            'target_version': target_version,
            'can_upgrade': can_upgrade,
            'reason': reason,
            'addons_compatible': not addons_need_upgrade,
            'addon_recommendations': addon_recommendations,
            'blocking_issues': [],
        }
        
        if not can_upgrade:
            result['blocking_issues'].append({
                'type': 'version_incompatibility',
                'message': reason,
            })
        
        if addons_need_upgrade:
            result['blocking_issues'].append({
                'type': 'addon_compatibility',
                'message': 'Some addons require updates before upgrade',
                'addons': [rec for rec in addon_recommendations if rec['action_required']],
            })
        
        logger.info(f"Validation complete: {len(result['blocking_issues'])} issues found")
        return result
    
    def get_supported_versions(self) -> List[str]:
        """
        Get list of supported EKS versions.
        
        Returns:
            List of supported version strings
        """
        return sorted(self.EKS_K8S_VERSIONS.keys(), key=lambda x: float(x))

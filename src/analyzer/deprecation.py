"""API deprecation detection and analysis."""

from typing import Dict, Any, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DeprecationAnalyzer:
    """Analyzer for Kubernetes API deprecations."""
    
    # Comprehensive API deprecation mapping
    API_DEPRECATIONS = {
        'apps/v1beta1': {
            'deprecated_in': '1.8',
            'removed_in': '1.16',
            'replacement': 'apps/v1',
            'resources': ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet'],
            'migration_notes': 'Update apiVersion to apps/v1. No other changes required for most resources.',
        },
        'apps/v1beta2': {
            'deprecated_in': '1.9',
            'removed_in': '1.16',
            'replacement': 'apps/v1',
            'resources': ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet'],
            'migration_notes': 'Update apiVersion to apps/v1. Check for selector immutability.',
        },
        'extensions/v1beta1': {
            'deprecated_in': '1.14',
            'removed_in': '1.16',
            'replacement': 'apps/v1 or networking.k8s.io/v1',
            'resources': ['Deployment', 'DaemonSet', 'ReplicaSet', 'Ingress', 'NetworkPolicy', 'PodSecurityPolicy'],
            'migration_notes': 'Use apps/v1 for workloads, networking.k8s.io/v1 for Ingress.',
        },
        'networking.k8s.io/v1beta1': {
            'deprecated_in': '1.19',
            'removed_in': '1.22',
            'replacement': 'networking.k8s.io/v1',
            'resources': ['Ingress', 'IngressClass'],
            'migration_notes': 'Update apiVersion and review pathType and backend changes.',
        },
        'admissionregistration.k8s.io/v1beta1': {
            'deprecated_in': '1.19',
            'removed_in': '1.22',
            'replacement': 'admissionregistration.k8s.io/v1',
            'resources': ['MutatingWebhookConfiguration', 'ValidatingWebhookConfiguration'],
            'migration_notes': 'Update apiVersion and review webhook configuration.',
        },
        'apiextensions.k8s.io/v1beta1': {
            'deprecated_in': '1.19',
            'removed_in': '1.22',
            'replacement': 'apiextensions.k8s.io/v1',
            'resources': ['CustomResourceDefinition'],
            'migration_notes': 'Update CRD schema to structural schema format.',
        },
        'batch/v1beta1': {
            'deprecated_in': '1.21',
            'removed_in': '1.25',
            'replacement': 'batch/v1',
            'resources': ['CronJob'],
            'migration_notes': 'Update apiVersion to batch/v1. Review schedule format.',
        },
        'policy/v1beta1': {
            'deprecated_in': '1.21',
            'removed_in': '1.25',
            'replacement': 'policy/v1',
            'resources': ['PodDisruptionBudget', 'PodSecurityPolicy'],
            'migration_notes': 'Update to policy/v1. Note: PSP is removed, migrate to Pod Security Standards.',
        },
        'autoscaling/v2beta1': {
            'deprecated_in': '1.22',
            'removed_in': '1.25',
            'replacement': 'autoscaling/v2',
            'resources': ['HorizontalPodAutoscaler'],
            'migration_notes': 'Update apiVersion and review metrics format.',
        },
        'autoscaling/v2beta2': {
            'deprecated_in': '1.23',
            'removed_in': '1.26',
            'replacement': 'autoscaling/v2',
            'resources': ['HorizontalPodAutoscaler'],
            'migration_notes': 'Update apiVersion to autoscaling/v2.',
        },
        'discovery.k8s.io/v1beta1': {
            'deprecated_in': '1.21',
            'removed_in': '1.25',
            'replacement': 'discovery.k8s.io/v1',
            'resources': ['EndpointSlice'],
            'migration_notes': 'Update apiVersion to discovery.k8s.io/v1.',
        },
        'flowcontrol.apiserver.k8s.io/v1beta1': {
            'deprecated_in': '1.23',
            'removed_in': '1.26',
            'replacement': 'flowcontrol.apiserver.k8s.io/v1beta2',
            'resources': ['FlowSchema', 'PriorityLevelConfiguration'],
            'migration_notes': 'Update apiVersion to v1beta2 or v1beta3.',
        },
        'storage.k8s.io/v1beta1': {
            'deprecated_in': '1.19',
            'removed_in': '1.22',
            'replacement': 'storage.k8s.io/v1',
            'resources': ['CSIDriver', 'CSINode', 'StorageClass', 'VolumeAttachment'],
            'migration_notes': 'Update apiVersion to storage.k8s.io/v1.',
        },
    }
    
    def __init__(self):
        """Initialize deprecation analyzer."""
        pass
    
    def is_api_deprecated(self, api_version: str) -> bool:
        """
        Check if API version is deprecated.
        
        Args:
            api_version: API version to check
            
        Returns:
            True if deprecated, False otherwise
        """
        return api_version in self.API_DEPRECATIONS
    
    def is_api_removed(self, api_version: str, k8s_version: str) -> bool:
        """
        Check if API version is removed in target Kubernetes version.
        
        Args:
            api_version: API version to check
            k8s_version: Target Kubernetes version
            
        Returns:
            True if removed, False otherwise
        """
        if api_version not in self.API_DEPRECATIONS:
            return False
        
        deprecation_info = self.API_DEPRECATIONS[api_version]
        removed_in = deprecation_info.get('removed_in', '999.0')
        
        try:
            return float(k8s_version) >= float(removed_in)
        except ValueError:
            logger.warning(f"Invalid version format: {k8s_version}")
            return False
    
    def get_deprecation_info(self, api_version: str) -> Optional[Dict[str, Any]]:
        """
        Get deprecation information for an API version.
        
        Args:
            api_version: API version to look up
            
        Returns:
            Deprecation information dictionary or None
        """
        return self.API_DEPRECATIONS.get(api_version)
    
    def analyze_resource(
        self,
        resource_name: str,
        resource_kind: str,
        api_version: str,
        namespace: str,
        target_k8s_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single resource for deprecations.
        
        Args:
            resource_name: Resource name
            resource_kind: Resource kind
            api_version: Resource API version
            namespace: Resource namespace
            target_k8s_version: Target Kubernetes version
            
        Returns:
            Analysis result dictionary
        """
        result = {
            'resource_name': resource_name,
            'resource_kind': resource_kind,
            'api_version': api_version,
            'namespace': namespace,
            'is_deprecated': False,
            'is_removed': False,
            'severity': 'INFO',
            'action_required': False,
        }
        
        if self.is_api_deprecated(api_version):
            deprecation_info = self.get_deprecation_info(api_version)
            result['is_deprecated'] = True
            result['deprecation_info'] = deprecation_info
            
            if target_k8s_version:
                is_removed = self.is_api_removed(api_version, target_k8s_version)
                result['is_removed'] = is_removed
                
                if is_removed:
                    result['severity'] = 'CRITICAL'
                    result['action_required'] = True
                    result['message'] = (
                        f"API {api_version} is removed in Kubernetes {target_k8s_version}. "
                        f"Must migrate to {deprecation_info['replacement']}"
                    )
                else:
                    result['severity'] = 'WARNING'
                    result['action_required'] = True
                    result['message'] = (
                        f"API {api_version} is deprecated and will be removed in "
                        f"Kubernetes {deprecation_info['removed_in']}. "
                        f"Plan migration to {deprecation_info['replacement']}"
                    )
            else:
                result['severity'] = 'WARNING'
                result['message'] = f"API {api_version} is deprecated"
        else:
            result['message'] = f"API {api_version} is current"
        
        return result
    
    def analyze_resources(
        self,
        resources: List[Dict[str, Any]],
        target_k8s_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple resources for deprecations.
        
        Args:
            resources: List of resources to analyze
            target_k8s_version: Target Kubernetes version
            
        Returns:
            Analysis summary dictionary
        """
        logger.info(f"Analyzing {len(resources)} resources for API deprecations")
        
        results = []
        deprecated_count = 0
        removed_count = 0
        critical_resources = []
        
        for resource in resources:
            analysis = self.analyze_resource(
                resource_name=resource.get('name', 'unknown'),
                resource_kind=resource.get('kind', 'unknown'),
                api_version=resource.get('api_version', ''),
                namespace=resource.get('namespace', 'default'),
                target_k8s_version=target_k8s_version
            )
            
            results.append(analysis)
            
            if analysis['is_deprecated']:
                deprecated_count += 1
            
            if analysis['is_removed']:
                removed_count += 1
                critical_resources.append(analysis)
        
        summary = {
            'total_resources': len(resources),
            'deprecated_count': deprecated_count,
            'removed_count': removed_count,
            'target_k8s_version': target_k8s_version,
            'critical_resources': critical_resources,
            'all_results': results,
        }
        
        if removed_count > 0:
            summary['severity'] = 'CRITICAL'
            summary['message'] = (
                f"{removed_count} resources use APIs removed in target version. "
                "Immediate action required!"
            )
        elif deprecated_count > 0:
            summary['severity'] = 'WARNING'
            summary['message'] = (
                f"{deprecated_count} resources use deprecated APIs. "
                "Plan migration before upgrade."
            )
        else:
            summary['severity'] = 'INFO'
            summary['message'] = "No deprecated APIs found"
        
        logger.info(
            f"Analysis complete: {deprecated_count} deprecated, "
            f"{removed_count} removed APIs"
        )
        
        return summary
    
    def get_migration_guide(self, api_version: str) -> Optional[str]:
        """
        Get migration guide for deprecated API.
        
        Args:
            api_version: Deprecated API version
            
        Returns:
            Migration guide text or None
        """
        deprecation_info = self.get_deprecation_info(api_version)
        if not deprecation_info:
            return None
        
        guide = f"""
Migration Guide for {api_version}
{'=' * 50}

Deprecated in: Kubernetes {deprecation_info['deprecated_in']}
Removed in: Kubernetes {deprecation_info['removed_in']}
Replacement: {deprecation_info['replacement']}

Affected Resources:
{', '.join(deprecation_info['resources'])}

Migration Notes:
{deprecation_info['migration_notes']}

Action Required:
1. Update apiVersion field to {deprecation_info['replacement']}
2. Review and test the updated manifests
3. Apply changes before upgrading to {deprecation_info['removed_in']}
"""
        return guide.strip()
    
    def get_all_deprecations_for_version(self, k8s_version: str) -> List[Dict[str, Any]]:
        """
        Get all deprecations removed in a specific Kubernetes version.
        
        Args:
            k8s_version: Kubernetes version
            
        Returns:
            List of deprecation information
        """
        deprecations = []
        
        for api_version, info in self.API_DEPRECATIONS.items():
            if info.get('removed_in') == k8s_version:
                deprecations.append({
                    'api_version': api_version,
                    **info
                })
        
        return deprecations

"""Kubernetes resource scanner for EKS Upgrade Planner."""

from typing import Dict, Any, List, Optional
from collections import defaultdict
from ..utils.logger import get_logger
from ..utils.k8s_helper import K8sHelper

try:
    from kubernetes.client.exceptions import ApiException
except ImportError:
    ApiException = Exception

logger = get_logger(__name__)


class K8sScanner:
    """Scanner for Kubernetes resources and API versions."""
    
    # Known deprecated API versions and their replacements
    DEPRECATED_APIS = {
        'apps/v1beta1': {
            'removed_in': '1.16',
            'replacement': 'apps/v1',
            'resources': ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet'],
        },
        'apps/v1beta2': {
            'removed_in': '1.16',
            'replacement': 'apps/v1',
            'resources': ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet'],
        },
        'extensions/v1beta1': {
            'removed_in': '1.16',
            'replacement': 'apps/v1 or networking.k8s.io/v1',
            'resources': ['Deployment', 'DaemonSet', 'ReplicaSet', 'Ingress', 'NetworkPolicy'],
        },
        'networking.k8s.io/v1beta1': {
            'removed_in': '1.22',
            'replacement': 'networking.k8s.io/v1',
            'resources': ['Ingress', 'IngressClass'],
        },
        'policy/v1beta1': {
            'removed_in': '1.25',
            'replacement': 'policy/v1',
            'resources': ['PodDisruptionBudget', 'PodSecurityPolicy'],
        },
        'batch/v1beta1': {
            'removed_in': '1.25',
            'replacement': 'batch/v1',
            'resources': ['CronJob'],
        },
        'autoscaling/v2beta1': {
            'removed_in': '1.25',
            'replacement': 'autoscaling/v2',
            'resources': ['HorizontalPodAutoscaler'],
        },
        'autoscaling/v2beta2': {
            'removed_in': '1.26',
            'replacement': 'autoscaling/v2',
            'resources': ['HorizontalPodAutoscaler'],
        },
    }
    
    def __init__(self, k8s_helper: K8sHelper):
        """
        Initialize Kubernetes scanner.
        
        Args:
            k8s_helper: Kubernetes helper instance
        """
        self.k8s_helper = k8s_helper
    
    def get_cluster_version(self) -> Optional[str]:
        """
        Get Kubernetes cluster version.
        
        Returns:
            Kubernetes version string or None
        """
        try:
            from kubernetes import client
            version_api = client.VersionApi(self.k8s_helper.api_client)
            version = version_api.get_code()
            return version.git_version.lstrip('v')
        except Exception as e:
            logger.error(f"Failed to get cluster version: {e}")
            return None
    
    def scan_deployments(self, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Scan all deployments in cluster or namespace.
        
        Args:
            namespace: Optional namespace filter
            
        Returns:
            List of deployment information
        """
        deployments = []
        try:
            if namespace:
                items = self.k8s_helper.apps_v1.list_namespaced_deployment(namespace).items
            else:
                items = self.k8s_helper.apps_v1.list_deployment_for_all_namespaces().items
            
            for item in items:
                deployments.append({
                    'name': item.metadata.name,
                    'namespace': item.metadata.namespace,
                    'api_version': item.api_version,
                    'kind': item.kind,
                    'replicas': item.spec.replicas,
                    'created_at': item.metadata.creation_timestamp,
                })
            
            logger.info(f"Scanned {len(deployments)} deployments")
        except ApiException as e:
            logger.error(f"Failed to scan deployments: {e}")
        
        return deployments
    
    def scan_statefulsets(self, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Scan all statefulsets in cluster or namespace.
        
        Args:
            namespace: Optional namespace filter
            
        Returns:
            List of statefulset information
        """
        statefulsets = []
        try:
            if namespace:
                items = self.k8s_helper.apps_v1.list_namespaced_stateful_set(namespace).items
            else:
                items = self.k8s_helper.apps_v1.list_stateful_set_for_all_namespaces().items
            
            for item in items:
                statefulsets.append({
                    'name': item.metadata.name,
                    'namespace': item.metadata.namespace,
                    'api_version': item.api_version,
                    'kind': item.kind,
                    'replicas': item.spec.replicas,
                    'created_at': item.metadata.creation_timestamp,
                })
            
            logger.info(f"Scanned {len(statefulsets)} statefulsets")
        except ApiException as e:
            logger.error(f"Failed to scan statefulsets: {e}")
        
        return statefulsets
    
    def scan_daemonsets(self, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Scan all daemonsets in cluster or namespace.
        
        Args:
            namespace: Optional namespace filter
            
        Returns:
            List of daemonset information
        """
        daemonsets = []
        try:
            if namespace:
                items = self.k8s_helper.apps_v1.list_namespaced_daemon_set(namespace).items
            else:
                items = self.k8s_helper.apps_v1.list_daemon_set_for_all_namespaces().items
            
            for item in items:
                daemonsets.append({
                    'name': item.metadata.name,
                    'namespace': item.metadata.namespace,
                    'api_version': item.api_version,
                    'kind': item.kind,
                    'created_at': item.metadata.creation_timestamp,
                })
            
            logger.info(f"Scanned {len(daemonsets)} daemonsets")
        except ApiException as e:
            logger.error(f"Failed to scan daemonsets: {e}")
        
        return daemonsets
    
    def scan_crds(self) -> List[Dict[str, Any]]:
        """
        Scan all Custom Resource Definitions.
        
        Returns:
            List of CRD information
        """
        crds = []
        try:
            items = self.k8s_helper.apiextensions_v1.list_custom_resource_definition().items
            
            for item in items:
                versions = []
                if item.spec.versions:
                    versions = [
                        {
                            'name': v.name,
                            'served': v.served,
                            'storage': v.storage,
                            'deprecated': getattr(v, 'deprecated', False),
                        }
                        for v in item.spec.versions
                    ]
                
                crds.append({
                    'name': item.metadata.name,
                    'group': item.spec.group,
                    'versions': versions,
                    'scope': item.spec.scope,
                    'created_at': item.metadata.creation_timestamp,
                })
            
            logger.info(f"Scanned {len(crds)} CRDs")
        except ApiException as e:
            logger.error(f"Failed to scan CRDs: {e}")
        
        return crds
    
    def scan_ingresses(self, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Scan all ingresses in cluster or namespace.
        
        Args:
            namespace: Optional namespace filter
            
        Returns:
            List of ingress information
        """
        ingresses = []
        try:
            if namespace:
                items = self.k8s_helper.networking_v1.list_namespaced_ingress(namespace).items
            else:
                items = self.k8s_helper.networking_v1.list_ingress_for_all_namespaces().items
            
            for item in items:
                ingresses.append({
                    'name': item.metadata.name,
                    'namespace': item.metadata.namespace,
                    'api_version': item.api_version,
                    'kind': item.kind,
                    'created_at': item.metadata.creation_timestamp,
                })
            
            logger.info(f"Scanned {len(ingresses)} ingresses")
        except ApiException as e:
            logger.error(f"Failed to scan ingresses: {e}")
        
        return ingresses
    
    def detect_deprecated_apis(self, target_version: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect resources using deprecated API versions.
        
        Args:
            target_version: Target Kubernetes version to check against
            
        Returns:
            Dictionary of deprecated APIs found with affected resources
        """
        logger.info("Detecting deprecated APIs in cluster")
        deprecated_resources = defaultdict(list)
        
        # Note: This is a simplified implementation
        # In production, you'd want to scan actual resource manifests
        # or use kubectl to get all resources with their API versions
        
        # Scan common workload types
        workloads = []
        workloads.extend(self.scan_deployments())
        workloads.extend(self.scan_statefulsets())
        workloads.extend(self.scan_daemonsets())
        workloads.extend(self.scan_ingresses())
        
        # Check for deprecated APIs
        for resource in workloads:
            api_version = resource.get('api_version', '')
            if api_version in self.DEPRECATED_APIS:
                deprecated_resources[api_version].append({
                    'name': resource['name'],
                    'namespace': resource['namespace'],
                    'kind': resource['kind'],
                    'deprecation_info': self.DEPRECATED_APIS[api_version],
                })
        
        if deprecated_resources:
            logger.warning(f"Found {len(deprecated_resources)} deprecated API versions in use")
        else:
            logger.info("No deprecated APIs detected")
        
        return dict(deprecated_resources)
    
    def scan_cluster(self, namespace: str = None) -> Dict[str, Any]:
        """
        Perform complete Kubernetes cluster scan.
        
        Args:
            namespace: Optional namespace filter
            
        Returns:
            Complete scan results
        """
        logger.info("Starting complete Kubernetes cluster scan")
        
        result = {
            'cluster_version': self.get_cluster_version(),
            'deployments': self.scan_deployments(namespace),
            'statefulsets': self.scan_statefulsets(namespace),
            'daemonsets': self.scan_daemonsets(namespace),
            'crds': self.scan_crds(),
            'ingresses': self.scan_ingresses(namespace),
            'deprecated_apis': self.detect_deprecated_apis(),
            'summary': {
                'total_deployments': len(self.scan_deployments(namespace)),
                'total_statefulsets': len(self.scan_statefulsets(namespace)),
                'total_daemonsets': len(self.scan_daemonsets(namespace)),
                'total_crds': len(self.scan_crds()),
                'deprecated_api_count': len(self.detect_deprecated_apis()),
            }
        }
        
        logger.info("Kubernetes cluster scan complete")
        return result

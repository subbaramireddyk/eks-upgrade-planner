"""EKS cluster scanner for EKS Upgrade Planner."""

from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
from ..utils.logger import get_logger
from ..utils.aws_helper import AWSHelper

logger = get_logger(__name__)


class EKSScanner:
    """Scanner for EKS cluster information."""
    
    def __init__(self, aws_helper: AWSHelper):
        """
        Initialize EKS scanner.
        
        Args:
            aws_helper: AWS helper instance
        """
        self.aws_helper = aws_helper
        self.eks_client = aws_helper.get_client('eks')
        self.ec2_client = aws_helper.get_client('ec2')
    
    def list_clusters(self) -> List[str]:
        """
        List all EKS clusters in the region.
        
        Returns:
            List of cluster names
        """
        try:
            clusters = []
            paginator = self.eks_client.get_paginator('list_clusters')
            
            for page in paginator.paginate():
                clusters.extend(page.get('clusters', []))
            
            logger.info(f"Found {len(clusters)} EKS clusters")
            return clusters
        except ClientError as e:
            logger.error(f"Failed to list clusters: {e}")
            raise
    
    def describe_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """
        Get detailed information about an EKS cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            Cluster details dictionary
        """
        try:
            response = self.eks_client.describe_cluster(name=cluster_name)
            cluster = response['cluster']
            
            logger.info(f"Retrieved details for cluster: {cluster_name}")
            logger.debug(f"Cluster version: {cluster.get('version')}")
            
            return {
                'name': cluster['name'],
                'version': cluster.get('version'),
                'endpoint': cluster.get('endpoint'),
                'platform_version': cluster.get('platformVersion'),
                'status': cluster.get('status'),
                'created_at': cluster.get('createdAt'),
                'role_arn': cluster.get('roleArn'),
                'vpc_config': cluster.get('resourcesVpcConfig', {}),
                'encryption_config': cluster.get('encryptionConfig', []),
                'tags': cluster.get('tags', {}),
            }
        except ClientError as e:
            logger.error(f"Failed to describe cluster {cluster_name}: {e}")
            raise
    
    def list_node_groups(self, cluster_name: str) -> List[str]:
        """
        List all node groups for a cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of node group names
        """
        try:
            node_groups = []
            paginator = self.eks_client.get_paginator('list_nodegroups')
            
            for page in paginator.paginate(clusterName=cluster_name):
                node_groups.extend(page.get('nodegroups', []))
            
            logger.info(f"Found {len(node_groups)} node groups for cluster {cluster_name}")
            return node_groups
        except ClientError as e:
            logger.error(f"Failed to list node groups: {e}")
            raise
    
    def describe_node_group(self, cluster_name: str, node_group_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a node group.
        
        Args:
            cluster_name: Name of the cluster
            node_group_name: Name of the node group
            
        Returns:
            Node group details dictionary
        """
        try:
            response = self.eks_client.describe_nodegroup(
                clusterName=cluster_name,
                nodegroupName=node_group_name
            )
            ng = response['nodegroup']
            
            return {
                'name': ng['nodegroupName'],
                'status': ng.get('status'),
                'capacity_type': ng.get('capacityType'),
                'ami_type': ng.get('amiType'),
                'release_version': ng.get('releaseVersion'),
                'version': ng.get('version'),
                'instance_types': ng.get('instanceTypes', []),
                'scaling_config': ng.get('scalingConfig', {}),
                'disk_size': ng.get('diskSize'),
                'created_at': ng.get('createdAt'),
                'tags': ng.get('tags', {}),
            }
        except ClientError as e:
            logger.error(f"Failed to describe node group {node_group_name}: {e}")
            raise
    
    def list_addons(self, cluster_name: str) -> List[str]:
        """
        List all addons for a cluster.
        
        Args:
            cluster_name: Name of the cluster
            
        Returns:
            List of addon names
        """
        try:
            addons = []
            paginator = self.eks_client.get_paginator('list_addons')
            
            for page in paginator.paginate(clusterName=cluster_name):
                addons.extend(page.get('addons', []))
            
            logger.info(f"Found {len(addons)} addons for cluster {cluster_name}")
            return addons
        except ClientError as e:
            logger.error(f"Failed to list addons: {e}")
            raise
    
    def describe_addon(self, cluster_name: str, addon_name: str) -> Dict[str, Any]:
        """
        Get detailed information about an addon.
        
        Args:
            cluster_name: Name of the cluster
            addon_name: Name of the addon
            
        Returns:
            Addon details dictionary
        """
        try:
            response = self.eks_client.describe_addon(
                clusterName=cluster_name,
                addonName=addon_name
            )
            addon = response['addon']
            
            return {
                'name': addon['addonName'],
                'version': addon.get('addonVersion'),
                'status': addon.get('status'),
                'created_at': addon.get('createdAt'),
                'modified_at': addon.get('modifiedAt'),
                'service_account_role_arn': addon.get('serviceAccountRoleArn'),
                'tags': addon.get('tags', {}),
            }
        except ClientError as e:
            logger.error(f"Failed to describe addon {addon_name}: {e}")
            raise
    
    def describe_addon_versions(self, addon_name: Optional[str] = None, 
                               kubernetes_version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available addon versions.
        
        Args:
            addon_name: Optional addon name to filter
            kubernetes_version: Optional K8s version to filter
            
        Returns:
            List of addon version information
        """
        try:
            kwargs = {}
            if addon_name:
                kwargs['addonName'] = addon_name
            if kubernetes_version:
                kwargs['kubernetesVersion'] = kubernetes_version
            
            addons = []
            paginator = self.eks_client.get_paginator('describe_addon_versions')
            
            for page in paginator.paginate(**kwargs):
                addons.extend(page.get('addons', []))
            
            return addons
        except ClientError as e:
            logger.error(f"Failed to describe addon versions: {e}")
            raise
    
    def scan_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """
        Perform a complete scan of an EKS cluster.
        
        Args:
            cluster_name: Name of the cluster to scan
            
        Returns:
            Complete cluster information including node groups and addons
        """
        logger.info(f"Starting complete scan of cluster: {cluster_name}")
        
        # Get cluster details
        cluster_info = self.describe_cluster(cluster_name)
        
        # Get node groups
        node_group_names = self.list_node_groups(cluster_name)
        node_groups = []
        for ng_name in node_group_names:
            try:
                ng_info = self.describe_node_group(cluster_name, ng_name)
                node_groups.append(ng_info)
            except Exception as e:
                logger.warning(f"Failed to get details for node group {ng_name}: {e}")
        
        # Get addons
        addon_names = self.list_addons(cluster_name)
        addons = []
        for addon_name in addon_names:
            try:
                addon_info = self.describe_addon(cluster_name, addon_name)
                addons.append(addon_info)
            except Exception as e:
                logger.warning(f"Failed to get details for addon {addon_name}: {e}")
        
        result = {
            'cluster': cluster_info,
            'node_groups': node_groups,
            'addons': addons,
            'summary': {
                'cluster_name': cluster_name,
                'cluster_version': cluster_info.get('version'),
                'node_group_count': len(node_groups),
                'addon_count': len(addons),
                'status': cluster_info.get('status'),
            }
        }
        
        logger.info(f"Cluster scan complete for {cluster_name}")
        return result

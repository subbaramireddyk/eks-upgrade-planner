"""Tests for scanner modules."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.utils.aws_helper import AWSHelper
from src.scanner.eks_scanner import EKSScanner


class TestEKSScanner(unittest.TestCase):
    """Test EKS scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aws_helper = Mock(spec=AWSHelper)
        self.eks_client = MagicMock()
        self.aws_helper.get_client.return_value = self.eks_client
        self.scanner = EKSScanner(self.aws_helper)
    
    def test_list_clusters(self):
        """Test listing EKS clusters."""
        # Mock response
        self.eks_client.get_paginator.return_value.paginate.return_value = [
            {'clusters': ['cluster1', 'cluster2']},
            {'clusters': ['cluster3']},
        ]
        
        clusters = self.scanner.list_clusters()
        
        self.assertEqual(len(clusters), 3)
        self.assertIn('cluster1', clusters)
        self.assertIn('cluster3', clusters)
    
    def test_describe_cluster(self):
        """Test describing a cluster."""
        # Mock response
        self.eks_client.describe_cluster.return_value = {
            'cluster': {
                'name': 'test-cluster',
                'version': '1.29',
                'status': 'ACTIVE',
                'endpoint': 'https://test.eks.amazonaws.com',
                'platformVersion': 'eks.1',
                'createdAt': '2024-01-01',
                'roleArn': 'arn:aws:iam::123456789012:role/eks-cluster-role',
                'resourcesVpcConfig': {},
                'encryptionConfig': [],
                'tags': {},
            }
        }
        
        cluster_info = self.scanner.describe_cluster('test-cluster')
        
        self.assertEqual(cluster_info['name'], 'test-cluster')
        self.assertEqual(cluster_info['version'], '1.29')
        self.assertEqual(cluster_info['status'], 'ACTIVE')


class TestK8sScanner(unittest.TestCase):
    """Test Kubernetes scanner functionality."""
    
    @patch('src.scanner.k8s_scanner.K8sHelper')
    def test_deprecated_api_detection(self, mock_k8s_helper):
        """Test deprecated API detection."""
        from src.scanner.k8s_scanner import K8sScanner
        
        scanner = K8sScanner(mock_k8s_helper)
        
        # Test that deprecated APIs dictionary is defined
        self.assertIn('apps/v1beta1', scanner.DEPRECATED_APIS)
        self.assertIn('extensions/v1beta1', scanner.DEPRECATED_APIS)
        
        # Check deprecation info structure
        dep_info = scanner.DEPRECATED_APIS['apps/v1beta1']
        self.assertIn('removed_in', dep_info)
        self.assertIn('replacement', dep_info)


if __name__ == '__main__':
    unittest.main()

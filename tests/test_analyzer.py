"""Tests for analyzer modules."""

import unittest
from src.analyzer.compatibility import CompatibilityAnalyzer
from src.analyzer.deprecation import DeprecationAnalyzer


class TestCompatibilityAnalyzer(unittest.TestCase):
    """Test compatibility analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CompatibilityAnalyzer()
    
    def test_version_supported(self):
        """Test version support checking."""
        self.assertTrue(self.analyzer.is_version_supported('1.29'))
        self.assertTrue(self.analyzer.is_version_supported('1.28'))
        self.assertFalse(self.analyzer.is_version_supported('1.15'))
    
    def test_can_upgrade_directly(self):
        """Test direct upgrade validation."""
        # Valid sequential upgrade
        can_upgrade, reason = self.analyzer.can_upgrade_directly('1.28', '1.29')
        self.assertTrue(can_upgrade)
        
        # Invalid - skipping versions
        can_upgrade, reason = self.analyzer.can_upgrade_directly('1.27', '1.29')
        self.assertFalse(can_upgrade)
        self.assertIn('skip', reason.lower())
        
        # Invalid - downgrade
        can_upgrade, reason = self.analyzer.can_upgrade_directly('1.29', '1.28')
        self.assertFalse(can_upgrade)
    
    def test_addon_compatibility(self):
        """Test addon compatibility checking."""
        is_compatible, recommended = self.analyzer.check_addon_compatibility(
            'coredns',
            'v1.10.1-eksbuild.1',
            '1.29'
        )
        
        self.assertIsNotNone(recommended)
    
    def test_get_supported_versions(self):
        """Test getting supported versions."""
        versions = self.analyzer.get_supported_versions()
        
        self.assertIsInstance(versions, list)
        self.assertGreater(len(versions), 0)
        self.assertIn('1.29', versions)


class TestDeprecationAnalyzer(unittest.TestCase):
    """Test deprecation analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = DeprecationAnalyzer()
    
    def test_is_api_deprecated(self):
        """Test API deprecation detection."""
        self.assertTrue(self.analyzer.is_api_deprecated('apps/v1beta1'))
        self.assertTrue(self.analyzer.is_api_deprecated('extensions/v1beta1'))
        self.assertFalse(self.analyzer.is_api_deprecated('apps/v1'))
    
    def test_is_api_removed(self):
        """Test API removal detection."""
        # apps/v1beta1 was removed in 1.16
        self.assertTrue(self.analyzer.is_api_removed('apps/v1beta1', '1.16'))
        self.assertTrue(self.analyzer.is_api_removed('apps/v1beta1', '1.29'))
        self.assertFalse(self.analyzer.is_api_removed('apps/v1beta1', '1.15'))
    
    def test_get_deprecation_info(self):
        """Test getting deprecation information."""
        info = self.analyzer.get_deprecation_info('apps/v1beta1')
        
        self.assertIsNotNone(info)
        self.assertIn('removed_in', info)
        self.assertIn('replacement', info)
        self.assertEqual(info['replacement'], 'apps/v1')
    
    def test_analyze_resource(self):
        """Test resource analysis."""
        result = self.analyzer.analyze_resource(
            resource_name='test-deployment',
            resource_kind='Deployment',
            api_version='apps/v1beta1',
            namespace='default',
            target_k8s_version='1.29'
        )
        
        self.assertTrue(result['is_deprecated'])
        self.assertTrue(result['is_removed'])
        self.assertEqual(result['severity'], 'CRITICAL')


if __name__ == '__main__':
    unittest.main()

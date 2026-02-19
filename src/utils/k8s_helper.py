"""Kubernetes helper utilities for EKS Upgrade Planner."""

from typing import Optional, Any
from pathlib import Path
import os

try:
    from kubernetes import client, config
    from kubernetes.client.exceptions import ApiException
except ImportError:
    client = None
    config = None
    ApiException = Exception

from src.utils.logger import get_logger

logger = get_logger(__name__)


class K8sHelper:
    """Helper class for Kubernetes client management."""

    def __init__(self, kubeconfig: Optional[str] = None, context: Optional[str] = None):
        """
        Initialize Kubernetes helper.

        Args:
            kubeconfig: Path to kubeconfig file (defaults to ~/.kube/config)
            context: Kubernetes context name (defaults to current context)
        """
        if client is None or config is None:
            raise ImportError("kubernetes library not installed")

        self.kubeconfig = kubeconfig or os.environ.get(
            "KUBECONFIG", str(Path.home() / ".kube" / "config")
        )
        self.context = context
        self._api_client: Optional[Any] = None
        self._core_v1: Optional[Any] = None
        self._apps_v1: Optional[Any] = None
        self._batch_v1: Optional[Any] = None
        self._networking_v1: Optional[Any] = None
        self._apiextensions_v1: Optional[Any] = None

    def load_config(self) -> bool:
        """
        Load kubeconfig.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.context:
                config.load_kube_config(
                    config_file=self.kubeconfig, context=self.context
                )
                logger.debug(f"Loaded kubeconfig with context: {self.context}")
            else:
                config.load_kube_config(config_file=self.kubeconfig)
                logger.debug(f"Loaded kubeconfig from: {self.kubeconfig}")
            return True
        except Exception as e:
            logger.error(f"Failed to load kubeconfig: {e}")
            return False

    @property
    def api_client(self) -> Any:
        """Get or create API client."""
        if self._api_client is None:
            if not self.load_config():
                raise RuntimeError("Failed to load kubeconfig")
            self._api_client = client.ApiClient()
        return self._api_client

    @property
    def core_v1(self) -> Any:
        """Get or create CoreV1Api client."""
        if self._core_v1 is None:
            self._core_v1 = client.CoreV1Api(self.api_client)
        return self._core_v1

    @property
    def apps_v1(self) -> Any:
        """Get or create AppsV1Api client."""
        if self._apps_v1 is None:
            self._apps_v1 = client.AppsV1Api(self.api_client)
        return self._apps_v1

    @property
    def batch_v1(self) -> Any:
        """Get or create BatchV1Api client."""
        if self._batch_v1 is None:
            self._batch_v1 = client.BatchV1Api(self.api_client)
        return self._batch_v1

    @property
    def networking_v1(self) -> Any:
        """Get or create NetworkingV1Api client."""
        if self._networking_v1 is None:
            self._networking_v1 = client.NetworkingV1Api(self.api_client)
        return self._networking_v1

    @property
    def apiextensions_v1(self) -> Any:
        """Get or create ApiextensionsV1Api client."""
        if self._apiextensions_v1 is None:
            self._apiextensions_v1 = client.ApiextensionsV1Api(self.api_client)
        return self._apiextensions_v1

    def test_connection(self) -> bool:
        """
        Test connection to Kubernetes cluster.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            version = client.VersionApi(self.api_client).get_code()
            logger.info(
                f"Connected to Kubernetes cluster version: {version.git_version}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Kubernetes cluster: {e}")
            return False

    def get_current_context(self) -> Optional[str]:
        """
        Get current context name.

        Returns:
            Context name or None if failed
        """
        try:
            contexts, active_context = config.list_kube_config_contexts(
                config_file=self.kubeconfig
            )
            if active_context:
                return active_context["name"]
        except Exception as e:
            logger.error(f"Failed to get current context: {e}")
        return None

    def list_contexts(self) -> list:
        """
        List available contexts.

        Returns:
            List of context names
        """
        try:
            contexts, _ = config.list_kube_config_contexts(config_file=self.kubeconfig)
            return [ctx["name"] for ctx in contexts]
        except Exception as e:
            logger.error(f"Failed to list contexts: {e}")
            return []

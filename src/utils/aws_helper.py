"""AWS helper utilities for EKS Upgrade Planner."""

import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AWSHelper:
    """Helper class for AWS session and client management."""

    def __init__(self, region: Optional[str] = None, profile: Optional[str] = None):
        """
        Initialize AWS helper.

        Args:
            region: AWS region (defaults to default region)
            profile: AWS profile name (defaults to default profile)
        """
        self.region = region
        self.profile = profile
        self._session: Optional[boto3.Session] = None
        self._clients: Dict[str, Any] = {}

    @property
    def session(self) -> boto3.Session:
        """
        Get or create boto3 session.

        Returns:
            boto3.Session instance
        """
        if self._session is None:
            try:
                session_kwargs = {}
                if self.profile:
                    session_kwargs["profile_name"] = self.profile
                if self.region:
                    session_kwargs["region_name"] = self.region

                self._session = boto3.Session(**session_kwargs)
                logger.debug(
                    f"Created AWS session for region: {self._session.region_name}"
                )
            except Exception as e:
                logger.error(f"Failed to create AWS session: {e}")
                raise

        return self._session

    def get_client(self, service_name: str, **kwargs) -> Any:
        """
        Get or create AWS service client.

        Args:
            service_name: AWS service name (e.g., 'eks', 'ec2')
            **kwargs: Additional client configuration

        Returns:
            Boto3 client instance

        Raises:
            NoCredentialsError: If AWS credentials are not found
            ClientError: If client creation fails
        """
        cache_key = f"{service_name}_{self.region}"

        if cache_key not in self._clients:
            try:
                client_kwargs = kwargs.copy()
                if self.region and "region_name" not in client_kwargs:
                    client_kwargs["region_name"] = self.region

                self._clients[cache_key] = self.session.client(
                    service_name, **client_kwargs
                )
                logger.debug(f"Created {service_name} client for region: {self.region}")
            except NoCredentialsError:
                logger.error(
                    "AWS credentials not found. Please configure AWS credentials."
                )
                raise
            except Exception as e:
                logger.error(f"Failed to create {service_name} client: {e}")
                raise

        return self._clients[cache_key]

    def validate_credentials(self) -> bool:
        """
        Validate AWS credentials.

        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            sts = self.get_client("sts")
            identity = sts.get_caller_identity()
            logger.info(f"AWS credentials validated for account: {identity['Account']}")
            return True
        except NoCredentialsError:
            logger.error("No AWS credentials found")
            return False
        except ClientError as e:
            logger.error(f"Invalid AWS credentials: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to validate credentials: {e}")
            return False

    def get_account_id(self) -> Optional[str]:
        """
        Get AWS account ID.

        Returns:
            Account ID or None if failed
        """
        try:
            sts = self.get_client("sts")
            identity = sts.get_caller_identity()
            return identity["Account"]
        except Exception as e:
            logger.error(f"Failed to get account ID: {e}")
            return None

    def list_regions(self, service: str = "eks") -> list:
        """
        List available AWS regions for a service.

        Args:
            service: AWS service name

        Returns:
            List of region names
        """
        try:
            ec2 = self.get_client("ec2")
            regions = ec2.describe_regions()
            return [region["RegionName"] for region in regions["Regions"]]
        except Exception as e:
            logger.error(f"Failed to list regions: {e}")
            return []

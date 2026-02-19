"""Cache utility for EKS Upgrade Planner."""

import json
import pickle
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Cache:
    """Simple file-based cache with TTL support."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: int = 24):
        """
        Initialize cache.

        Args:
            cache_dir: Cache directory (defaults to ~/.eks-upgrade-planner/cache)
            ttl_hours: Time-to-live in hours for cache entries
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".eks-upgrade-planner" / "cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        logger.debug(f"Cache initialized at: {self.cache_dir}")

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        # Sanitize key for filesystem
        safe_key = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
        return self.cache_dir / f"{safe_key}.cache"

    def _is_expired(self, cache_path: Path) -> bool:
        """Check if cache entry is expired."""
        if not cache_path.exists():
            return True

        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - mtime
        return age > self.ttl

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found or expired

        Returns:
            Cached value or default
        """
        cache_path = self._get_cache_path(key)

        if self._is_expired(cache_path):
            logger.debug(f"Cache miss or expired for key: {key}")
            return default

        try:
            with open(cache_path, "rb") as f:
                value = pickle.load(f)
            logger.debug(f"Cache hit for key: {key}")
            return value
        except Exception as e:
            logger.warning(f"Failed to read cache for key {key}: {e}")
            return default

    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache

        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)
            logger.debug(f"Cached value for key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to write cache for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete cache entry.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(key)

        try:
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Deleted cache for key: {key}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete cache for key {key}: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_json(self, key: str, default: Any = None) -> Any:
        """
        Get JSON value from cache.

        Args:
            key: Cache key
            default: Default value if key not found or expired

        Returns:
            Cached JSON value or default
        """
        cache_path = self._get_cache_path(key)

        if self._is_expired(cache_path):
            return default

        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read JSON cache for key {key}: {e}")
            return default

    def set_json(self, key: str, value: Any) -> bool:
        """
        Set JSON value in cache.

        Args:
            key: Cache key
            value: JSON-serializable value to cache

        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "w") as f:
                json.dump(value, f, indent=2)
            return True
        except Exception as e:
            logger.warning(f"Failed to write JSON cache for key {key}: {e}")
            return False

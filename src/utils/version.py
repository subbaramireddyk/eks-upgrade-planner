"""Version parsing and comparison helpers.

Kubernetes and EKS versions are dotted integers, not decimals. Comparing them
with float() is wrong in two ways: "1.9" becomes 1.9 and compares greater than
"1.16" (1.16), and "1.30" and "1.3" both become 1.3. Addon versions carry an
eksbuild suffix on top of that, so they need their own parser.
"""

import re
from typing import Optional, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)

# e.g. "1.30", "v1.30", "1.30.1"
_VERSION_RE = re.compile(r"^v?(\d+(?:\.\d+)*)$")

# e.g. "v1.11.1-eksbuild.2", "v1.30.0-eksbuild.3", "1.18.0"
_ADDON_VERSION_RE = re.compile(
    r"^v?(?P<version>\d+(?:\.\d+)*)(?:-eksbuild\.(?P<build>\d+))?",
    re.IGNORECASE,
)


def parse_version(version: str) -> Optional[Tuple[int, ...]]:
    """
    Parse a dotted version into a tuple of integers.

    Args:
        version: Version string such as "1.30", "v1.30" or "1.30.1"

    Returns:
        Tuple of integers, or None if the string is not a version
    """
    if not version or not isinstance(version, str):
        return None

    match = _VERSION_RE.match(version.strip())
    if not match:
        return None

    return tuple(int(part) for part in match.group(1).split("."))


def parse_addon_version(version: str) -> Optional[Tuple[int, ...]]:
    """
    Parse an EKS addon version, including its eksbuild suffix.

    "v1.11.1-eksbuild.2" becomes (1, 11, 1, 2). A version with no eksbuild
    suffix is treated as build 0, so "v1.11.1" sorts below "v1.11.1-eksbuild.1".

    Args:
        version: Addon version string

    Returns:
        Tuple of integers, or None if the string cannot be parsed
    """
    if not version or not isinstance(version, str):
        return None

    match = _ADDON_VERSION_RE.match(version.strip())
    if not match:
        return None

    parts = [int(p) for p in match.group("version").split(".")]
    build = match.group("build")
    parts.append(int(build) if build is not None else 0)
    return tuple(parts)


def _pad(left: Tuple[int, ...], right: Tuple[int, ...]) -> Tuple[tuple, tuple]:
    """Pad the shorter tuple with zeros so comparison is positional."""
    width = max(len(left), len(right))
    return (
        left + (0,) * (width - len(left)),
        right + (0,) * (width - len(right)),
    )


def compare_versions(left: str, right: str) -> Optional[int]:
    """
    Compare two dotted versions.

    Args:
        left: First version
        right: Second version

    Returns:
        -1, 0 or 1 as left is less than, equal to or greater than right;
        None if either version cannot be parsed
    """
    parsed_left = parse_version(left)
    parsed_right = parse_version(right)

    if parsed_left is None or parsed_right is None:
        return None

    a, b = _pad(parsed_left, parsed_right)
    if a < b:
        return -1
    return 0 if a == b else 1


def version_at_least(version: str, minimum: str) -> Optional[bool]:
    """
    Check whether a version is at or above a minimum.

    Args:
        version: Version to test
        minimum: Minimum acceptable version

    Returns:
        True or False, or None if either version cannot be parsed
    """
    result = compare_versions(version, minimum)
    return None if result is None else result >= 0


def addon_version_at_least(version: str, minimum: str) -> Optional[bool]:
    """
    Check whether an addon version is at or above a minimum.

    Args:
        version: Addon version to test, e.g. "v1.11.1-eksbuild.2"
        minimum: Minimum acceptable addon version

    Returns:
        True or False, or None if either version cannot be parsed
    """
    parsed_version = parse_addon_version(version)
    parsed_minimum = parse_addon_version(minimum)

    if parsed_version is None or parsed_minimum is None:
        return None

    a, b = _pad(parsed_version, parsed_minimum)
    return a >= b


def version_sort_key(version: str) -> Tuple[int, ...]:
    """
    Sort key for dotted versions.

    Unparseable versions sort last rather than raising, so a malformed entry in
    the data files cannot break listing the supported versions.

    Args:
        version: Version string

    Returns:
        Tuple usable as a sort key
    """
    parsed = parse_version(version)
    if parsed is None:
        logger.debug(f"Unparseable version in sort: {version}")
        return (1,)
    return (0,) + parsed

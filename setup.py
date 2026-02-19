"""Setup configuration for eks-upgrade-planner."""

import os
import sys
from setuptools import setup, find_packages

# Add src to path to import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
try:
    from src import __version__
except ImportError:
    __version__ = "1.0.0"  # Fallback

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eks-upgrade-planner",
    version=__version__,
    author="EKS Upgrade Planner Contributors",
    description="A production-ready CLI tool for EKS cluster upgrade planning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/subbaramireddyk/eks-upgrade-planner",
    packages=find_packages(include=['src', 'src.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "eks-upgrade-planner=src.cli:main",
        ],
    },
    package_data={
        "": ["*.yaml", "*.yml"],
    },
    include_package_data=True,
)

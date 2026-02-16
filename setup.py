"""Setup configuration for eks-upgrade-planner."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eks-upgrade-planner",
    version="1.0.0",
    author="EKS Upgrade Planner Contributors",
    description="A production-ready CLI tool for EKS cluster upgrade planning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/subbaramireddyk/eks-upgrade-planner",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
            "eks-upgrade-planner=cli:main",
        ],
    },
    package_data={
        "": ["*.yaml", "*.yml"],
    },
    include_package_data=True,
)

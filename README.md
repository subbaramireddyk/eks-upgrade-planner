# EKS Upgrade Planner

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready CLI tool that automates EKS cluster upgrade planning, eliminating manual research and reducing upgrade preparation time from hours to minutes.

## 🚀 Features

- **Automated Cluster Scanning**: Discover EKS cluster versions, node groups, and addons
- **Kubernetes Resource Analysis**: Scan deployments, statefulsets, and CRDs for deprecated APIs
- **Compatibility Checking**: Validate addon versions and API compatibility with target EKS versions
- **Upgrade Path Generation**: Create sequential upgrade paths (can't skip minor versions)
- **Risk Assessment**: Assess upgrade risk based on deprecated APIs, breaking changes, and cluster size
- **Migration Planning**: Generate manifest update recommendations and migration guides
- **Comprehensive Reports**: Export plans in Markdown, JSON, or HTML formats
- **Production-Ready**: Proper error handling, logging, caching, and security practices

## 📋 Requirements

- Python 3.8 or higher
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)
- kubectl configured with access to the cluster (for Kubernetes resource scanning)
- Required IAM permissions:
  - `eks:DescribeCluster`
  - `eks:ListClusters`
  - `eks:ListNodegroups`
  - `eks:DescribeNodegroup`
  - `eks:ListAddons`
  - `eks:DescribeAddon`
  - `eks:DescribeAddonVersions`

## 🔧 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/subbaramireddyk/eks-upgrade-planner.git
cd eks-upgrade-planner

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Using Docker

```bash
# Build the Docker image
docker build -t eks-upgrade-planner .

# Run with AWS credentials
docker run --rm \
  -v ~/.aws:/home/eksplanner/.aws:ro \
  -v ~/.kube:/home/eksplanner/.kube:ro \
  eks-upgrade-planner --help
```

## 🎯 Quick Start

### 1. Scan a Cluster

```bash
eks-upgrade-planner scan \
  --cluster my-prod-cluster \
  --region us-west-2
```

### 2. Analyze Compatibility

```bash
eks-upgrade-planner analyze \
  --cluster my-prod-cluster \
  --region us-west-2 \
  --target-version 1.29
```

### 3. Generate Upgrade Plan

```bash
eks-upgrade-planner plan \
  --cluster my-prod-cluster \
  --region us-west-2 \
  --target-version 1.29 \
  --format markdown \
  --output upgrade-plan.md
```

### 4. Check Addon Compatibility

```bash
eks-upgrade-planner check-addon \
  --addon coredns \
  --current v1.8.7-eksbuild.1 \
  --eks-version 1.29
```

## 📖 Detailed Usage

### CLI Commands

#### `scan` - Discover Cluster State

Scans EKS cluster configuration and Kubernetes resources.

```bash
eks-upgrade-planner scan \
  --cluster <cluster-name> \
  --region <aws-region> \
  [--profile <aws-profile>]
```

**Output:**
- Cluster version and status
- Node group details
- Installed addons with versions
- Kubernetes resource summary (if kubeconfig available)

#### `analyze` - Check Compatibility

Analyzes compatibility and detects potential issues.

```bash
eks-upgrade-planner analyze \
  --cluster <cluster-name> \
  --target-version <eks-version> \
  --region <aws-region> \
  [--profile <aws-profile>]
```

**Checks:**
- Version compatibility (can upgrade directly?)
- Addon version compatibility
- Breaking changes in target version
- Deprecated API usage

#### `plan` - Generate Full Upgrade Plan

Creates comprehensive upgrade plan with risk assessment.

```bash
eks-upgrade-planner plan \
  --cluster <cluster-name> \
  --target-version <eks-version> \
  --region <aws-region> \
  --format <markdown|json|html> \
  --output <file-path> \
  [--profile <aws-profile>]
```

**Generates:**
- Sequential upgrade path
- Pre-upgrade checklist
- Addon upgrade order
- Node rotation strategy
- Step-by-step runbook
- Risk assessment
- Migration requirements
- Time estimation

#### `check-addon` - Validate Addon Version

Quickly check if an addon version is compatible.

```bash
eks-upgrade-planner check-addon \
  --addon <addon-name> \
  --current <current-version> \
  --eks-version <eks-version>
```

### Global Options

- `--debug`: Enable debug logging
- `--log-file <path>`: Write logs to file

## 📊 Sample Output

### Markdown Report Structure

```markdown
# EKS Upgrade Plan: prod-cluster

## Executive Summary
- Current EKS Version: 1.27
- Target EKS Version: 1.29
- Risk Level: MEDIUM
- Estimated Effort: 4-6 hours

## Current State
[Cluster details, node groups, addons]

## Upgrade Path
1. Current: EKS 1.27
2. ✅ Upgrade to EKS 1.28
3. ✅ Upgrade to EKS 1.29

## Pre-Upgrade Requirements
- [ ] Update CoreDNS to v1.11.1
- [ ] Fix 3 deprecated APIs
- [ ] Backup cluster data

## Deprecated APIs Found
⚠️ 3 resources using deprecated APIs:
- Deployment "legacy-app" uses apps/v1beta1

## Detailed Upgrade Steps
[Step-by-step runbook with commands]

## Risk Assessment
Overall Risk: MEDIUM
[Risk factors and mitigations]

## Timeline
Total: 4-5 hours
```

## 🏗️ Architecture

The tool is organized into modular components:

```
src/
├── scanner/         # EKS and K8s cluster scanning
│   ├── eks_scanner.py
│   └── k8s_scanner.py
├── analyzer/        # Compatibility and deprecation analysis
│   ├── compatibility.py
│   ├── deprecation.py
│   └── release_notes.py
├── planner/         # Upgrade planning and risk assessment
│   ├── upgrade_path.py
│   ├── risk_assessment.py
│   └── migration_plan.py
├── reporter/        # Report generation
│   ├── markdown.py
│   ├── json_export.py
│   └── html.py
├── utils/           # Helper utilities
│   ├── aws_helper.py
│   ├── k8s_helper.py
│   ├── logger.py
│   └── cache.py
└── cli.py          # CLI interface
```

## 🔒 Security

- No credentials are logged or stored
- Uses AWS credential chain (IAM roles preferred)
- All inputs are validated
- Minimal required IAM permissions
- Non-root Docker image

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test module
python -m pytest tests/test_scanner.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### "Failed to validate AWS credentials"

Ensure AWS credentials are properly configured:
```bash
aws configure
# or
export AWS_PROFILE=your-profile
```

### "Could not scan Kubernetes resources"

Configure kubectl to access your cluster:
```bash
aws eks update-kubeconfig --name <cluster-name> --region <region>
```

### "No module named 'src'"

Install the package in development mode:
```bash
pip install -e .
```

## 📚 Additional Resources

- [EKS Kubernetes Versions](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Deprecation Policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)

## 👥 Authors

EKS Upgrade Planner Contributors

## 🙏 Acknowledgments

- AWS EKS team for comprehensive documentation
- Kubernetes community for API deprecation guidelines
- All contributors who have helped improve this tool

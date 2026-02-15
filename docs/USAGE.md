# Detailed Usage Guide

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Command Reference](#command-reference)
4. [Workflow Examples](#workflow-examples)
5. [Report Formats](#report-formats)
6. [Advanced Scenarios](#advanced-scenarios)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

Before installing EKS Upgrade Planner, ensure you have:

- Python 3.8 or higher
- pip package manager
- AWS CLI configured
- kubectl (for K8s resource scanning)

### Installation Methods

#### Method 1: From Source

```bash
git clone https://github.com/subbaramireddyk/eks-upgrade-planner.git
cd eks-upgrade-planner
pip install -r requirements.txt
pip install -e .
```

#### Method 2: Docker

```bash
docker build -t eks-upgrade-planner .
```

## Configuration

### AWS Credentials

The tool uses the standard AWS credential chain:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM instance profile (when running on EC2)

Example using AWS profile:
```bash
eks-upgrade-planner scan --cluster my-cluster --profile production
```

### Kubernetes Access

Configure kubectl to access your EKS cluster:

```bash
aws eks update-kubeconfig --name my-cluster --region us-west-2
```

## Command Reference

### scan

Scan an EKS cluster to discover current state.

**Syntax:**
```bash
eks-upgrade-planner scan --cluster <name> [OPTIONS]
```

**Options:**
- `--cluster`: (Required) Name of the EKS cluster
- `--region`: AWS region (defaults to configured region)
- `--profile`: AWS profile name

**Example:**
```bash
eks-upgrade-planner scan \
  --cluster production-cluster \
  --region us-west-2 \
  --profile prod-account
```

**Output:**
```
🔍 Scanning EKS cluster: production-cluster

✅ Scan complete!
  Cluster: production-cluster
  Version: 1.27
  Node Groups: 3
  Addons: 5
  Status: ACTIVE

🔍 Scanning Kubernetes resources...
  Deployments: 45
  StatefulSets: 12
  DaemonSets: 8
  CRDs: 23
```

### analyze

Analyze compatibility for a specific upgrade.

**Syntax:**
```bash
eks-upgrade-planner analyze --cluster <name> --target-version <version> [OPTIONS]
```

**Options:**
- `--cluster`: (Required) Cluster name
- `--target-version`: (Required) Target EKS version (e.g., 1.29)
- `--region`: AWS region
- `--profile`: AWS profile

**Example:**
```bash
eks-upgrade-planner analyze \
  --cluster production-cluster \
  --target-version 1.29 \
  --region us-west-2
```

**Output:**
```
🔍 Scanning cluster...
  Current version: 1.27
  Target version: 1.29

📊 Analyzing compatibility...
  ❌ Cannot skip minor versions in EKS upgrade

🔌 Analyzing addons...
  ⚠️  2 addons need updates:
     - coredns: Upgrade to v1.11.1-eksbuild.1
     - vpc-cni: Upgrade to v1.16.2-eksbuild.1

⚡ Checking for breaking changes...
  ⚠️  3 breaking changes found:
     - [HIGH] PodSecurityPolicy removed (v1.25)
     - [MEDIUM] HPA v2beta2 removed (v1.26)
```

### plan

Generate a comprehensive upgrade plan.

**Syntax:**
```bash
eks-upgrade-planner plan --cluster <name> --target-version <version> [OPTIONS]
```

**Options:**
- `--cluster`: (Required) Cluster name
- `--target-version`: (Required) Target EKS version
- `--region`: AWS region
- `--profile`: AWS profile
- `--format`: Output format (markdown, json, html) - default: markdown
- `--output`: Output file path (prints to stdout if not specified)

**Example:**
```bash
eks-upgrade-planner plan \
  --cluster production-cluster \
  --target-version 1.29 \
  --format markdown \
  --output plan.md
```

**Example with JSON output:**
```bash
eks-upgrade-planner plan \
  --cluster production-cluster \
  --target-version 1.29 \
  --format json \
  --output plan.json
```

### check-addon

Quickly verify addon compatibility.

**Syntax:**
```bash
eks-upgrade-planner check-addon --addon <name> --current <version> --eks-version <version>
```

**Options:**
- `--addon`: (Required) Addon name (e.g., coredns, vpc-cni)
- `--current`: (Required) Current addon version
- `--eks-version`: (Required) Target EKS version

**Example:**
```bash
eks-upgrade-planner check-addon \
  --addon coredns \
  --current v1.8.7-eksbuild.1 \
  --eks-version 1.29
```

**Output:**
```
Addon: coredns
Current Version: v1.8.7-eksbuild.1
EKS Version: 1.29
❌ Not compatible
Recommended Version: v1.11.1-eksbuild.1
```

## Workflow Examples

### Scenario 1: Simple Upgrade (1.28 → 1.29)

```bash
# Step 1: Scan current state
eks-upgrade-planner scan --cluster my-cluster --region us-west-2

# Step 2: Analyze compatibility
eks-upgrade-planner analyze \
  --cluster my-cluster \
  --target-version 1.29 \
  --region us-west-2

# Step 3: Generate upgrade plan
eks-upgrade-planner plan \
  --cluster my-cluster \
  --target-version 1.29 \
  --format markdown \
  --output my-cluster-upgrade-plan.md

# Step 4: Review the plan and execute
cat my-cluster-upgrade-plan.md
```

### Scenario 2: Multi-Version Upgrade (1.27 → 1.29)

```bash
# Generate plan - tool will create sequential path (1.27 → 1.28 → 1.29)
eks-upgrade-planner plan \
  --cluster my-cluster \
  --target-version 1.29 \
  --format html \
  --output upgrade-plan.html

# Open HTML report in browser for review
```

### Scenario 3: Multiple Clusters

```bash
#!/bin/bash
# Script to generate plans for multiple clusters

CLUSTERS=("prod-cluster-1" "prod-cluster-2" "prod-cluster-3")
TARGET_VERSION="1.29"

for cluster in "${CLUSTERS[@]}"; do
  echo "Planning upgrade for $cluster..."
  eks-upgrade-planner plan \
    --cluster "$cluster" \
    --target-version "$TARGET_VERSION" \
    --format markdown \
    --output "${cluster}-upgrade-plan.md"
done
```

### Scenario 4: CI/CD Integration

```bash
# Generate JSON report for automated processing
eks-upgrade-planner plan \
  --cluster my-cluster \
  --target-version 1.29 \
  --format json \
  --output plan.json

# Parse JSON in your pipeline
risk_level=$(jq -r '.risk_assessment.overall_risk' plan.json)

if [ "$risk_level" == "CRITICAL" ]; then
  echo "CRITICAL risk detected - manual review required"
  exit 1
fi
```

## Report Formats

### Markdown

Human-readable format, perfect for:
- Documentation
- GitHub/GitLab issues
- Team reviews
- Version control

**Example:**
```markdown
# EKS Upgrade Plan: my-cluster

## Executive Summary
- Current: 1.27
- Target: 1.29
- Risk: MEDIUM
...
```

### JSON

Machine-readable format, perfect for:
- CI/CD pipelines
- Automated processing
- Integration with other tools
- API consumption

**Example:**
```json
{
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "tool": "eks-upgrade-planner",
    "version": "1.0.0"
  },
  "cluster": {
    "name": "my-cluster",
    "current_version": "1.27",
    "target_version": "1.29"
  },
  "risk_assessment": {
    "overall_risk": "MEDIUM"
  }
}
```

### HTML

Visual format with styling, perfect for:
- Stakeholder presentations
- Web sharing
- Executive reports
- Printing

Features:
- Navigation menu
- Color-coded risk levels
- Responsive design
- Print-friendly

## Advanced Scenarios

### Using with Multiple AWS Accounts

```bash
# Account 1 - Development
AWS_PROFILE=dev-account eks-upgrade-planner plan \
  --cluster dev-cluster \
  --target-version 1.29 \
  --output dev-plan.md

# Account 2 - Production
AWS_PROFILE=prod-account eks-upgrade-planner plan \
  --cluster prod-cluster \
  --target-version 1.29 \
  --output prod-plan.md
```

### Docker Usage

```bash
# Run scan with Docker
docker run --rm \
  -v ~/.aws:/home/eksplanner/.aws:ro \
  -v ~/.kube:/home/eksplanner/.kube:ro \
  -v $(pwd):/output \
  eks-upgrade-planner plan \
    --cluster my-cluster \
    --target-version 1.29 \
    --output /output/plan.md
```

### Debug Mode

```bash
# Enable debug logging
eks-upgrade-planner --debug plan \
  --cluster my-cluster \
  --target-version 1.29 \
  --log-file debug.log
```

## Troubleshooting

### Issue: "Failed to validate AWS credentials"

**Solution:**
```bash
# Check AWS configuration
aws sts get-caller-identity

# Configure AWS credentials
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-west-2
```

### Issue: "Permission denied" errors

**Solution:**
Ensure your IAM user/role has required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:ListNodegroups",
        "eks:DescribeNodegroup",
        "eks:ListAddons",
        "eks:DescribeAddon",
        "eks:DescribeAddonVersions"
      ],
      "Resource": "*"
    }
  ]
}
```

### Issue: "Could not scan Kubernetes resources"

**Solution:**
```bash
# Update kubeconfig
aws eks update-kubeconfig --name my-cluster --region us-west-2

# Verify access
kubectl get nodes

# Check current context
kubectl config current-context
```

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
eks-upgrade-planner version
```

## Best Practices

1. **Always test in non-production first**
   ```bash
   # Test in dev/staging
   eks-upgrade-planner plan --cluster dev-cluster --target-version 1.29
   ```

2. **Review generated plans thoroughly**
   - Check all breaking changes
   - Verify addon compatibility
   - Review migration requirements

3. **Keep plans in version control**
   ```bash
   git add upgrade-plans/
   git commit -m "Add EKS upgrade plan for v1.29"
   ```

4. **Run multiple format exports**
   ```bash
   # Markdown for team review
   eks-upgrade-planner plan ... --format markdown --output plan.md
   
   # JSON for automation
   eks-upgrade-planner plan ... --format json --output plan.json
   
   # HTML for stakeholders
   eks-upgrade-planner plan ... --format html --output plan.html
   ```

5. **Schedule regular compatibility checks**
   ```bash
   # Cron job to check compatibility weekly
   0 9 * * 1 /usr/local/bin/eks-upgrade-planner analyze \
     --cluster prod-cluster \
     --target-version 1.29 > /var/log/eks-compatibility.log
   ```

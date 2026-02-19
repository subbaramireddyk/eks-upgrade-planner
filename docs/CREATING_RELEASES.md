# Creating Releases - EKS Upgrade Planner

## Quick Start - Create Your First Release

### Option 1: Using GitHub Web Interface (Easiest)

1. **Go to your repository on GitHub**
   https://github.com/subbaramireddyk/eks-upgrade-planner

2. **Click on "Releases"** (right sidebar)

3. **Click "Draft a new release"**

4. **Fill in the release details:**
   - **Tag version:** `v1.0.0` (must start with 'v')
   - **Release title:** `v1.0.0 - Initial Release`
   - **Description:** (See template below)
   - **Target:** `main` branch

5. **Click "Publish release"**

6. **Wait 5-10 minutes** - GitHub Actions will automatically:
   - Build Windows .exe file
   - Build Linux binary
   - Build macOS binary
   - Attach them to your release
   - Generate SHA256 checksums

7. **Done!** Users can now download binaries from:
   https://github.com/subbaramireddyk/eks-upgrade-planner/releases

---

### Option 2: Using GitHub CLI

```bash
# Install GitHub CLI if not already installed
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: https://github.com/cli/cli#installation

# Login to GitHub
gh auth login

# Create and publish release
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes "$(cat RELEASE_NOTES.md)" \
  --target main

# The workflow will automatically build and attach binaries!
```

---

### Option 3: Using Git Tags + GitHub Web UI

```bash
# Create and push a tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Then go to GitHub web interface and create release from the tag
```

---

## Release Notes Template

Copy this template when creating a release:

```markdown
## 🎉 EKS Upgrade Planner v1.0.0

Production-ready CLI tool for automating EKS cluster upgrade planning.

### 🚀 Features

- **Automated Cluster Scanning**: Discover EKS cluster versions, node groups, and addons
- **Kubernetes Resource Analysis**: Scan deployments, statefulsets, and CRDs for deprecated APIs
- **Compatibility Checking**: Validate addon versions and API compatibility
- **Upgrade Path Generation**: Create sequential upgrade paths (can't skip minor versions)
- **Risk Assessment**: Assess upgrade risk based on deprecated APIs and breaking changes
- **Migration Planning**: Generate manifest update recommendations
- **Comprehensive Reports**: Export plans in Markdown, JSON, or HTML formats

### 📦 Installation

#### Download Pre-built Binary (No Python Required!)

**Windows:**
```powershell
# Download from release assets
Invoke-WebRequest -Uri "https://github.com/subbaramireddyk/eks-upgrade-planner/releases/download/v1.0.0/eks-upgrade-planner-windows-amd64.exe" -OutFile "eks-upgrade-planner.exe"

# Run it
.\eks-upgrade-planner.exe --help
```

**Linux:**
```bash
# Download
wget https://github.com/subbaramireddyk/eks-upgrade-planner/releases/download/v1.0.0/eks-upgrade-planner-linux-amd64

# Make executable
chmod +x eks-upgrade-planner-linux-amd64

# Run it
./eks-upgrade-planner-linux-amd64 --help
```

**macOS:**
```bash
# Download
curl -L -o eks-upgrade-planner https://github.com/subbaramireddyk/eks-upgrade-planner/releases/download/v1.0.0/eks-upgrade-planner-macos-amd64

# Make executable
chmod +x eks-upgrade-planner

# Run it
./eks-upgrade-planner --help
```

#### Install via pip

```bash
pip install git+https://github.com/subbaramireddyk/eks-upgrade-planner.git@v1.0.0
```

#### Using Docker

```bash
docker pull ghcr.io/subbaramireddyk/eks-upgrade-planner:v1.0.0
docker run --rm eks-upgrade-planner:v1.0.0 --help
```

### 📝 Quick Start

```bash
# Scan a cluster
eks-upgrade-planner scan --cluster my-cluster --region us-west-2

# Analyze compatibility
eks-upgrade-planner analyze --cluster my-cluster --target-version 1.29 --region us-west-2

# Generate upgrade plan
eks-upgrade-planner plan --cluster my-cluster --target-version 1.29 --output plan.md
```

### 🔒 Security

- Verify downloads with SHA256 checksums (see SHA256SUMS file)
- All binaries are built automatically by GitHub Actions
- Source code is publicly auditable

### 📚 Documentation

- [Installation Guide](https://github.com/subbaramireddyk/eks-upgrade-planner/blob/main/docs/INSTALLATION.md)
- [Usage Guide](https://github.com/subbaramireddyk/eks-upgrade-planner/blob/main/docs/USAGE.md)
- [Architecture](https://github.com/subbaramireddyk/eks-upgrade-planner/blob/main/docs/ARCHITECTURE.md)

### 🐛 Known Issues

None reported yet! Please report issues at https://github.com/subbaramireddyk/eks-upgrade-planner/issues

### 🙏 Credits

Built with ❤️ by EKS Upgrade Planner Contributors

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## What Happens After You Create a Release?

1. **GitHub Actions triggers** (`.github/workflows/release.yml`)
2. **Builds binaries** for Windows, Linux, and macOS in parallel
3. **Tests each binary** (runs `--version` command)
4. **Uploads binaries** to the release automatically
5. **Generates checksums** for security verification
6. **Updates release** with all assets

### Expected Timeline:
- Windows build: ~5-7 minutes
- Linux build: ~4-5 minutes
- macOS build: ~5-7 minutes
- **Total: ~10-15 minutes**

---

## Verifying Your Release

After creating a release, verify it worked:

1. **Go to releases page:**
   https://github.com/subbaramireddyk/eks-upgrade-planner/releases

2. **Check for these files:**
   - ✅ `eks-upgrade-planner-windows-amd64.exe` (~50-80MB)
   - ✅ `eks-upgrade-planner-linux-amd64` (~50-80MB)
   - ✅ `eks-upgrade-planner-macos-amd64` (~50-80MB)
   - ✅ `SHA256SUMS` (checksums file)
   - ✅ `Source code (zip)`
   - ✅ `Source code (tar.gz)`

3. **Download and test one:**
   ```bash
   # Linux example
   wget https://github.com/subbaramireddyk/eks-upgrade-planner/releases/download/v1.0.0/eks-upgrade-planner-linux-amd64
   chmod +x eks-upgrade-planner-linux-amd64
   ./eks-upgrade-planner-linux-amd64 version
   ```

---

## Updating README with Download Links

After your first release, update your README.md:

```markdown
## Installation

### Download Pre-built Binary (Recommended)

No Python required! Download the latest release:

**[Download Latest Release](https://github.com/subbaramireddyk/eks-upgrade-planner/releases/latest)**

- Windows: `eks-upgrade-planner-windows-amd64.exe`
- Linux: `eks-upgrade-planner-linux-amd64`
- macOS: `eks-upgrade-planner-macos-amd64`

### Install via pip

\`\`\`bash
pip install git+https://github.com/subbaramireddyk/eks-upgrade-planner.git
\`\`\`
```

---

## Creating Subsequent Releases

### Version Numbering (Semantic Versioning)

- **Major version (1.0.0 → 2.0.0)**: Breaking changes
- **Minor version (1.0.0 → 1.1.0)**: New features, backwards compatible
- **Patch version (1.0.0 → 1.0.1)**: Bug fixes

### Example Release Workflow

```bash
# 1. Update version in src/__init__.py
# Edit: __version__ = "1.0.1"

# 2. Update CHANGELOG.md
# Document what changed

# 3. Commit changes
git add src/__init__.py CHANGELOG.md
git commit -m "Bump version to 1.0.1"

# 4. Create and push tag
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin main
git push origin v1.0.1

# 5. Create GitHub release (web UI or gh CLI)
gh release create v1.0.1 \
  --title "v1.0.1 - Bug Fixes" \
  --notes "See CHANGELOG.md for details"

# 6. Wait for GitHub Actions to build and attach binaries
```

---

## Troubleshooting

### Release workflow didn't trigger

**Check:**
1. Tag name starts with `v` (e.g., `v1.0.0`, not `1.0.0`)
2. Release is "Published" (not "Draft")
3. GitHub Actions are enabled in your repository

**Fix:**
```bash
# Re-trigger the workflow manually
gh workflow run release.yml
```

### Binaries not attached to release

**Check:**
1. Go to Actions tab and see if workflow failed
2. Check workflow logs for errors

**Common issues:**
- PyInstaller dependencies missing
- Import errors in the code
- Path issues with data files

### Binary is too large (>100MB)

This is normal for PyInstaller bundles. They include:
- Python interpreter
- All dependencies
- Your code

To reduce size (advanced):
- Use `--exclude-module` for unused packages
- Use UPX compression (add `--upx-dir` flag)

---

## Testing Before Release

Test the binary build locally first:

```bash
# Install PyInstaller
pip install pyinstaller

# Build binary
pyinstaller --onefile --name eks-upgrade-planner \
  --add-data "data:data" \
  --add-data "config:config" \
  --hidden-import=src \
  --hidden-import=src.analyzer \
  --hidden-import=src.planner \
  --hidden-import=src.reporter \
  --hidden-import=src.scanner \
  --hidden-import=src.utils \
  --collect-all boto3 \
  --collect-all botocore \
  --collect-all kubernetes \
  --collect-all yaml \
  src/cli.py

# Test it
./dist/eks-upgrade-planner version
./dist/eks-upgrade-planner check-addon --addon coredns --current v1.10.1-eksbuild.1 --eks-version 1.29
```

---

## Next Steps

1. **Create your first release** using the steps above
2. **Wait for binaries to build** (~10-15 minutes)
3. **Test downloading and running** a binary
4. **Update README** with download links
5. **Announce it!** Share on social media, forums, etc.

Your CLI tool will be available for download without requiring Python! 🎉

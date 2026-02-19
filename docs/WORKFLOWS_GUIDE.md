# GitHub Workflows Guide

## Overview

This project uses GitHub Actions for automation. Here's what each workflow does:

## Active Workflows

### 1. `ci.yml` - Continuous Integration ⭐

**Triggers:**
- Every push to `main` or `develop` branches
- Every pull request to `main` branch

**What it does:**
```
┌─────────────────────────────────────────┐
│  CI Workflow (on every push/PR)        │
├─────────────────────────────────────────┤
│  ✓ Test Job (Python 3.8, 3.9, 3.10, 3.11)│
│    - Install dependencies              │
│    - Run flake8 linting                │
│    - Run black format check            │
│    - Run mypy type checking            │
│    - Run 19 pytest tests               │
│    - Upload code coverage              │
│                                        │
│  ✓ Docker Build Job                    │
│    - Build Docker image                │
│    - Test Docker image                 │
│                                        │
│  ✓ Package Build Job                   │
│    - Build Python package              │
│    - Validate with twine               │
│    - Upload artifacts                  │
└─────────────────────────────────────────┘
```

**Duration:** ~5-8 minutes
**Purpose:** Ensure code quality before merging
**Status:** ✅ KEEP THIS - Essential for code quality!

---

### 2. `release.yml` - Release & Binary Builds 🎯

**Triggers:**
- When you publish a GitHub release
- Manual workflow dispatch (for testing)

**What it does:**
```
┌─────────────────────────────────────────┐
│  Release Workflow (on release)         │
├─────────────────────────────────────────┤
│  ✓ Build Windows Binary                │
│    - Compile to .exe                   │
│    - Test binary                       │
│    - Upload to release                 │
│                                        │
│  ✓ Build Linux Binary                  │
│    - Compile to executable             │
│    - Test binary                       │
│    - Upload to release                 │
│                                        │
│  ✓ Build macOS Binary                  │
│    - Compile to executable             │
│    - Test binary                       │
│    - Upload to release                 │
│                                        │
│  ✓ Create Checksums                    │
│    - Generate SHA256SUMS               │
│    - Upload to release                 │
└─────────────────────────────────────────┘
```

**Duration:** ~10-15 minutes
**Purpose:** Create downloadable binaries for users
**Status:** ✅ KEEP THIS - For releases!

---

### 3. `publish.yml` - PyPI Publishing 📦

**Triggers:**
- When you publish a GitHub release (if configured)
- Manual workflow dispatch with test_pypi flag

**What it does:**
```
┌─────────────────────────────────────────┐
│  Publish Workflow (on release)         │
├─────────────────────────────────────────┤
│  ✓ Build Python Package                │
│    - Build wheel and source dist       │
│    - Validate with twine               │
│                                        │
│  ✓ Publish to Test PyPI (optional)     │
│    - Test the package first            │
│                                        │
│  ✓ Publish to PyPI                     │
│    - Make installable via pip          │
└─────────────────────────────────────────┘
```

**Duration:** ~2-3 minutes
**Purpose:** Publish to Python Package Index
**Status:** ⚠️ OPTIONAL - Only if you want PyPI publishing

---

## Workflow Comparison

| Workflow | When | Purpose | Keep? |
|----------|------|---------|-------|
| `ci.yml` | Every push/PR | Test code quality | ✅ YES |
| `release.yml` | On GitHub release | Build binaries | ✅ YES |
| `publish.yml` | On release | Publish to PyPI | ⚠️ Optional |

---

## How They Work Together

### Normal Development Flow
```
1. Developer pushes code
   ↓
2. ci.yml runs automatically
   - Tests pass? ✅
   - Code formatted? ✅
   - Docker builds? ✅
   ↓
3. Code is merged
```

### Release Flow
```
1. Create GitHub release (v1.0.0)
   ↓
2. release.yml runs automatically
   - Builds Windows .exe
   - Builds Linux binary
   - Builds macOS binary
   - Attaches to release
   ↓
3. publish.yml runs (if configured)
   - Publishes to PyPI
   ↓
4. Users can download or pip install
```

---

## When Each Workflow Runs

### Every Commit/PR (Frequent)
- ✅ `ci.yml` - Quality checks

### Only on Releases (Rare)
- ✅ `release.yml` - Build binaries
- ⚠️ `publish.yml` - Publish to PyPI

---

## Disabling Workflows

If you don't want a workflow, you can:

### Option 1: Delete the file
```bash
rm .github/workflows/publish.yml
git commit -m "Remove PyPI publishing"
git push
```

### Option 2: Disable in GitHub UI
1. Go to Actions tab
2. Click on workflow name
3. Click "..." menu
4. Click "Disable workflow"

---

## Monitoring Workflows

### View Workflow Runs
https://github.com/subbaramireddyk/eks-upgrade-planner/actions

### Check Status
- Green checkmark ✅ = Success
- Red X ❌ = Failed
- Yellow circle ⭕ = In progress

### Get Notifications
- Go to repository → Watch → Custom → Check "Actions"

---

## Cost Considerations

All these workflows run on GitHub's free tier:

| Workflow | Frequency | Minutes/Run | Monthly Usage |
|----------|-----------|-------------|---------------|
| `ci.yml` | ~10 pushes/week | 8 min | ~320 min |
| `release.yml` | ~1 release/month | 15 min | ~15 min |
| `publish.yml` | ~1 release/month | 3 min | ~3 min |
| **Total** | - | - | **~340 min/month** |

**GitHub Free Tier:** 2,000 minutes/month ✅
**Your usage:** ~340 minutes/month (17% of limit)

---

## Recommendations

### For Most Users: Keep 2 Workflows
```bash
.github/workflows/
├── ci.yml          # ✅ Keep - Tests on every push
└── release.yml     # ✅ Keep - Binaries on release
```

### For PyPI Publishing: Keep 3 Workflows
```bash
.github/workflows/
├── ci.yml          # ✅ Keep - Tests on every push
├── release.yml     # ✅ Keep - Binaries on release
└── publish.yml     # ✅ Keep - PyPI publishing
```

---

## Troubleshooting

### CI Fails on Every Push
**Problem:** ci.yml is too strict
**Solution:**
- Check which check is failing (tests, linting, formatting)
- Fix the issue or adjust workflow

### Release Workflow Not Triggering
**Problem:** Workflow not running on release
**Solution:**
- Ensure release is "Published" not "Draft"
- Check that tag starts with 'v' (e.g., v1.0.0)

### Binaries Not Attaching to Release
**Problem:** release.yml fails to upload
**Solution:**
- Check Actions logs for errors
- Ensure GITHUB_TOKEN has permissions

---

## Next Steps

1. **Keep ci.yml** - Essential for quality
2. **Keep release.yml** - For downloadable binaries
3. **Decide on publish.yml** - Only if you want PyPI

Ready to create your first release? See [CREATING_RELEASES.md](CREATING_RELEASES.md)!

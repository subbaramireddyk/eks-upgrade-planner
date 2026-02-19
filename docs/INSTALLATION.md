# Installation Guide - EKS Upgrade Planner

## Quick Start (Works Now!)

### Method 1: Install from GitHub (Recommended)
```bash
pip install git+https://github.com/subbaramireddyk/eks-upgrade-planner.git
```

### Method 2: Clone and Install
```bash
git clone https://github.com/subbaramireddyk/eks-upgrade-planner.git
cd eks-upgrade-planner
pip install -e .
```

### Method 3: Docker (No Python Required)
```bash
docker pull ghcr.io/subbaramireddyk/eks-upgrade-planner:latest
docker run --rm eks-upgrade-planner --help
```

## Platform-Specific Installation

### Windows

#### Option 1: Python pip (Current)
```powershell
# Using PowerShell
pip install git+https://github.com/subbaramireddyk/eks-upgrade-planner.git

# Verify installation
eks-upgrade-planner version
```

#### Option 2: Standalone Executable (Coming Soon)
Download from [Releases](https://github.com/subbaramireddyk/eks-upgrade-planner/releases)
```powershell
# Download eks-upgrade-planner-windows.zip
# Extract and add to PATH
eks-upgrade-planner.exe --help
```

#### Option 3: Chocolatey (Future)
```powershell
choco install eks-upgrade-planner
```

#### Option 4: Scoop (Future)
```powershell
scoop bucket add eks-tools https://github.com/subbaramireddyk/scoop-bucket
scoop install eks-upgrade-planner
```

#### Option 5: WinGet (Future)
```powershell
winget install subbaramireddyk.eks-upgrade-planner
```

### Linux

#### Option 1: Python pip (Current)
```bash
# Using pip
pip install git+https://github.com/subbaramireddyk/eks-upgrade-planner.git

# Verify installation
eks-upgrade-planner version
```

#### Option 2: Standalone Binary (Coming Soon)
```bash
# Download from releases
wget https://github.com/subbaramireddyk/eks-upgrade-planner/releases/latest/download/eks-upgrade-planner-linux.tar.gz
tar -xzf eks-upgrade-planner-linux.tar.gz
sudo mv eks-upgrade-planner /usr/local/bin/
```

#### Option 3: Debian/Ubuntu (.deb) (Future)
```bash
# Add repository
curl -fsSL https://packages.example.com/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/eks-tools.gpg
echo "deb [signed-by=/usr/share/keyrings/eks-tools.gpg] https://packages.example.com/deb stable main" | sudo tee /etc/apt/sources.list.d/eks-tools.list

# Install
sudo apt update
sudo apt install eks-upgrade-planner
```

#### Option 4: RHEL/CentOS (.rpm) (Future)
```bash
# Add repository
sudo curl -o /etc/yum.repos.d/eks-tools.repo https://packages.example.com/rpm/eks-tools.repo

# Install
sudo yum install eks-upgrade-planner
```

#### Option 5: Arch Linux (AUR) (Future)
```bash
yay -S eks-upgrade-planner
# or
paru -S eks-upgrade-planner
```

### macOS

#### Option 1: Python pip (Current)
```bash
pip install git+https://github.com/subbaramireddyk/eks-upgrade-planner.git
```

#### Option 2: Homebrew (Future)
```bash
brew tap subbaramireddyk/eks-tools
brew install eks-upgrade-planner
```

#### Option 3: Standalone Binary (Coming Soon)
```bash
# Download from releases
curl -L https://github.com/subbaramireddyk/eks-upgrade-planner/releases/latest/download/eks-upgrade-planner-macos.tar.gz | tar xz
sudo mv eks-upgrade-planner /usr/local/bin/
```

## Container Images

### Docker Hub (Future)
```bash
docker pull subbaramireddyk/eks-upgrade-planner:latest
```

### GitHub Container Registry (Future)
```bash
docker pull ghcr.io/subbaramireddyk/eks-upgrade-planner:latest
```

## PyPI (Python Package Index) - Coming Soon!

Once published to PyPI:
```bash
pip install eks-upgrade-planner
```

This will be the simplest method for all platforms!

## Verification

After installation, verify it works:
```bash
# Check version
eks-upgrade-planner version

# Show help
eks-upgrade-planner --help

# Check addon compatibility (no AWS credentials needed)
eks-upgrade-planner check-addon --addon coredns --current v1.10.1-eksbuild.1 --eks-version 1.29
```

## Troubleshooting

### Windows: Command not found
Add Python Scripts directory to PATH:
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\AppData\Local\Programs\Python\Python311\Scripts", [EnvironmentVariableTarget]::User)
```

### Linux/macOS: Command not found
Add pip bin directory to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc to make permanent
```

### AWS Credentials
```bash
# Configure AWS credentials
aws configure
# or
export AWS_PROFILE=your-profile
```

## Uninstallation

```bash
# Python pip
pip uninstall eks-upgrade-planner

# Homebrew
brew uninstall eks-upgrade-planner

# Chocolatey
choco uninstall eks-upgrade-planner

# apt
sudo apt remove eks-upgrade-planner
```

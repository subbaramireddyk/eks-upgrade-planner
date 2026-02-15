# Architecture Documentation

## System Overview

EKS Upgrade Planner is designed as a modular, production-ready CLI tool for automating EKS cluster upgrade planning. The architecture follows clean separation of concerns with distinct layers for scanning, analysis, planning, and reporting.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│                  (User Interface & Commands)                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────────────────────────────────────────┐
             │                                                  │
┌────────────▼────────┐  ┌──────────────┐  ┌─────────────────┐│
│   Scanner Layer     │  │ Analyzer     │  │  Planner Layer  ││
│                     │  │   Layer      │  │                 ││
│ • EKS Scanner       │  │ • Compat.    │  │ • Path Planner  ││
│ • K8s Scanner       │  │ • Deprec.    │  │ • Risk Assess.  ││
│                     │  │ • Releases   │  │ • Migration     ││
└─────────────────────┘  └──────────────┘  └─────────────────┘│
             │                   │                   │          │
             └───────────────────┴───────────────────┘          │
                                 │                              │
                    ┌────────────▼──────────────┐               │
                    │    Reporter Layer         │               │
                    │                           │               │
                    │  • Markdown Generator     │               │
                    │  • JSON Exporter          │               │
                    │  • HTML Generator         │               │
                    └───────────────────────────┘               │
                                 │                              │
                    ┌────────────▼──────────────┐               │
                    │    Utilities Layer        │               │
                    │                           │               │
                    │  • AWS Helper             │               │
                    │  • K8s Helper             │               │
                    │  • Logger                 │               │
                    │  • Cache                  │               │
                    └───────────────────────────┘               │
                                                                │
┌───────────────────────────────────────────────────────────────┘
│                    External Integrations
├─────────────────────────────────────────────────────
│  • AWS EKS API
│  • Kubernetes API
│  • AWS Documentation (Release Notes)
└─────────────────────────────────────────────────────
```

## Component Details

### 1. CLI Layer (`src/cli.py`)

**Responsibility:** User interface and command orchestration

**Components:**
- Command parser (Click framework)
- Input validation
- Output formatting
- Error handling

**Commands:**
- `scan`: Discover cluster state
- `analyze`: Check compatibility
- `plan`: Generate upgrade plan
- `check-addon`: Validate addon version

**Design Patterns:**
- Command pattern for CLI commands
- Dependency injection for components
- Context passing for global options

### 2. Scanner Layer

#### EKS Scanner (`src/scanner/eks_scanner.py`)

**Responsibility:** Interact with AWS EKS API to gather cluster information

**Key Functions:**
- `list_clusters()`: Discover all EKS clusters
- `describe_cluster()`: Get detailed cluster info
- `list_node_groups()`: Find all node groups
- `describe_node_group()`: Get node group details
- `list_addons()`: List installed addons
- `describe_addon()`: Get addon details
- `scan_cluster()`: Complete cluster scan

**AWS APIs Used:**
- EKS: DescribeCluster, ListNodegroups, ListAddons
- EC2: DescribeRegions (for region discovery)

**Error Handling:**
- Boto3 client errors
- Permission errors
- Pagination handling
- Rate limiting

#### K8s Scanner (`src/scanner/k8s_scanner.py`)

**Responsibility:** Scan Kubernetes resources for API versions and deprecations

**Key Functions:**
- `get_cluster_version()`: Get K8s version
- `scan_deployments()`: List all deployments
- `scan_statefulsets()`: List statefulsets
- `scan_daemonsets()`: List daemonsets
- `scan_crds()`: List Custom Resource Definitions
- `detect_deprecated_apis()`: Find deprecated API usage
- `scan_cluster()`: Complete K8s scan

**Kubernetes APIs Used:**
- Core V1: Deployments, StatefulSets, DaemonSets
- ApiExtensions V1: CRDs
- Networking V1: Ingresses

**Deprecation Detection:**
- Maintains mapping of deprecated APIs
- Checks resource apiVersion fields
- Cross-references with removal versions

### 3. Analyzer Layer

#### Compatibility Analyzer (`src/analyzer/compatibility.py`)

**Responsibility:** Validate version compatibility

**Key Functions:**
- `can_upgrade_directly()`: Check if upgrade is allowed
- `check_addon_compatibility()`: Validate addon versions
- `get_addon_recommendations()`: Suggest addon updates
- `validate_upgrade_path()`: Complete validation

**Compatibility Rules:**
- No minor version skipping
- Sequential upgrades only
- Addon version requirements per EKS version

**Data Sources:**
- Built-in compatibility matrix
- AWS addon version requirements

#### Deprecation Analyzer (`src/analyzer/deprecation.py`)

**Responsibility:** Detect and analyze deprecated APIs

**Key Functions:**
- `is_api_deprecated()`: Check if API is deprecated
- `is_api_removed()`: Check if API is removed in version
- `analyze_resource()`: Analyze single resource
- `analyze_resources()`: Batch analysis
- `get_migration_guide()`: Generate migration docs

**Deprecation Database:**
- Comprehensive mapping of deprecated APIs
- Removal versions
- Replacement APIs
- Migration notes

#### Release Notes Analyzer (`src/analyzer/release_notes.py`)

**Responsibility:** Fetch and parse EKS release information

**Key Functions:**
- `fetch_eks_version_info()`: Get EKS version details
- `fetch_addon_release_notes()`: Get addon releases
- `get_breaking_changes()`: Find breaking changes
- `get_upgrade_notes()`: Generate comprehensive notes

**Features:**
- Caching for performance
- Fallback to static data
- Breaking change tracking

### 4. Planner Layer

#### Upgrade Path Planner (`src/planner/upgrade_path.py`)

**Responsibility:** Generate sequential upgrade paths and runbooks

**Key Functions:**
- `generate_upgrade_path()`: Create version sequence
- `determine_addon_upgrade_order()`: Order addon updates
- `create_pre_upgrade_checklist()`: Generate checklist
- `plan_node_group_rotation()`: Plan node updates
- `create_upgrade_runbook()`: Step-by-step guide
- `estimate_upgrade_time()`: Time estimation

**Planning Logic:**
- Sequential version progression
- Addon priority ordering
- Phase-based execution
- Time estimation algorithms

#### Risk Assessment (`src/planner/risk_assessment.py`)

**Responsibility:** Assess upgrade risks and impacts

**Key Functions:**
- `assess_deprecated_api_risk()`: API deprecation risk
- `assess_breaking_changes_risk()`: Breaking change impact
- `assess_addon_compatibility_risk()`: Addon risks
- `assess_version_jump_risk()`: Multi-version risk
- `assess_cluster_size_risk()`: Size-based risk
- `perform_comprehensive_assessment()`: Complete analysis

**Risk Levels:**
- LOW: Minimal impact, standard upgrade
- MEDIUM: Some manual work required
- HIGH: Significant effort, careful planning needed
- CRITICAL: Major issues, immediate action required

**Risk Factors:**
- Deprecated API count
- Breaking changes
- Addon incompatibilities
- Version jumps
- Cluster complexity

#### Migration Planner (`src/planner/migration_plan.py`)

**Responsibility:** Plan API migrations and manifest updates

**Key Functions:**
- `detect_migration_requirements()`: Find what needs migration
- `generate_manifest_examples()`: Create before/after examples
- `identify_manual_intervention_points()`: Flag manual steps
- `create_testing_recommendations()`: Testing guide
- `flag_resources_needing_recreation()`: Identify recreations

**Migration Planning:**
- API version updates
- Manifest transformations
- Resource recreation requirements
- Testing strategies

### 5. Reporter Layer

#### Markdown Reporter (`src/reporter/markdown.py`)

**Responsibility:** Generate Markdown format reports

**Output Sections:**
- Executive summary
- Current state
- Upgrade path
- Pre-upgrade requirements
- Deprecated APIs
- Breaking changes
- Migration requirements
- Detailed steps
- Risk assessment
- Rollback plan
- Timeline

#### JSON Exporter (`src/reporter/json_export.py`)

**Responsibility:** Export structured JSON for automation

**Use Cases:**
- CI/CD integration
- API consumption
- Automated processing
- Data exchange

#### HTML Reporter (`src/reporter/html.py`)

**Responsibility:** Generate styled HTML reports

**Features:**
- Navigation menu
- Color-coded risk levels
- Responsive design
- Print-friendly
- Embedded CSS

### 6. Utilities Layer

#### AWS Helper (`src/utils/aws_helper.py`)

**Responsibility:** AWS SDK abstraction and credential management

**Features:**
- Session management
- Client caching
- Credential validation
- Region handling
- Error handling

#### K8s Helper (`src/utils/k8s_helper.py`)

**Responsibility:** Kubernetes client abstraction

**Features:**
- Kubeconfig loading
- Context management
- API client creation
- Connection testing

#### Logger (`src/utils/logger.py`)

**Responsibility:** Structured logging

**Features:**
- Color-coded console output
- File logging
- Debug mode
- Log levels (DEBUG, INFO, WARNING, ERROR)

#### Cache (`src/utils/cache.py`)

**Responsibility:** File-based caching with TTL

**Features:**
- TTL-based expiration
- JSON and pickle support
- Cache invalidation
- Performance optimization

## Data Flow

### Typical Execution Flow

1. **User invokes CLI command**
   ```
   eks-upgrade-planner plan --cluster my-cluster --target-version 1.29
   ```

2. **CLI layer validates inputs**
   - Check required arguments
   - Validate version format
   - Set up logging

3. **Scanner layer collects data**
   - AWS Helper authenticates
   - EKS Scanner queries cluster
   - K8s Scanner queries resources
   - Results cached for reuse

4. **Analyzer layer processes data**
   - Compatibility Analyzer validates versions
   - Deprecation Analyzer checks APIs
   - Release Notes Analyzer fetches changes

5. **Planner layer generates plan**
   - Upgrade Path Planner creates sequence
   - Risk Assessment evaluates impact
   - Migration Planner identifies changes

6. **Reporter layer produces output**
   - Format selected (Markdown/JSON/HTML)
   - Report generated
   - Output to file or stdout

## Design Principles

### 1. Modularity
- Each component has single responsibility
- Clear interfaces between layers
- Easy to extend and modify

### 2. Testability
- Mock-friendly interfaces
- Dependency injection
- Isolated components

### 3. Error Handling
- Graceful degradation
- Clear error messages
- Proper logging
- User-friendly feedback

### 4. Security
- No credential logging
- Input validation
- IAM role support
- Minimal permissions

### 5. Performance
- Caching for expensive operations
- Efficient API calls
- Pagination handling
- Concurrent operations where safe

### 6. Maintainability
- Comprehensive documentation
- Type hints throughout
- Consistent code style
- Clear naming conventions

## Extension Points

### Adding New Analyzers

```python
# Create new analyzer in src/analyzer/
class CustomAnalyzer:
    def analyze(self, data):
        # Your analysis logic
        pass

# Integrate in CLI
from .analyzer import CustomAnalyzer
analyzer = CustomAnalyzer()
results = analyzer.analyze(cluster_info)
```

### Adding New Report Formats

```python
# Create new reporter in src/reporter/
class PDFReporter:
    def generate_report(self, ...):
        # PDF generation logic
        pass

# Add to CLI
elif format == 'pdf':
    reporter = PDFReporter()
    report = reporter.generate_report(...)
```

### Adding New Data Sources

```python
# Extend compatibility matrix
# Add to data/compatibility_matrix.yaml

# Or load from external source
class DynamicCompatibilityAnalyzer:
    def __init__(self):
        self.matrix = self.load_from_api()
```

## Security Considerations

### Credential Handling
- Uses AWS credential chain
- No credentials in logs
- Support for IAM roles
- Temporary credentials support

### Input Validation
- Cluster name validation
- Version format checking
- Path sanitization
- No shell injection

### Minimal Permissions
Required IAM permissions:
```json
{
  "eks:DescribeCluster",
  "eks:ListClusters",
  "eks:ListNodegroups",
  "eks:DescribeNodegroup",
  "eks:ListAddons",
  "eks:DescribeAddon"
}
```

### Data Privacy
- No data transmitted externally (except AWS API)
- Local caching only
- No telemetry
- No tracking

## Performance Optimization

### Caching Strategy
- Release notes cached for 24 hours
- Cluster scans not cached (real-time data)
- Configurable TTL

### API Call Optimization
- Batch operations where possible
- Pagination handled efficiently
- Client reuse via helper classes

### Resource Usage
- Minimal memory footprint
- Streaming for large reports
- Efficient data structures

## Future Enhancements

Potential areas for expansion:

1. **Multi-cluster Support**
   - Scan multiple clusters
   - Compare configurations
   - Batch planning

2. **Automated Execution**
   - Execute upgrade steps
   - Rollback automation
   - Validation testing

3. **AI-Powered Insights**
   - Intelligent recommendations
   - Pattern recognition
   - Historical analysis

4. **Web Interface**
   - Dashboard view
   - Interactive planning
   - Team collaboration

5. **Advanced Reporting**
   - PDF generation
   - Custom templates
   - Email notifications

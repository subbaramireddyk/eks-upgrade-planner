"""EKS Upgrade Planner - Production-ready CLI tool for EKS upgrade planning."""

__version__ = "1.0.0"
__author__ = "EKS Upgrade Planner Contributors"

from src.utils import setup_logger, get_logger
from src.scanner import EKSScanner, K8sScanner
from src.analyzer import CompatibilityAnalyzer, DeprecationAnalyzer, ReleaseNotesAnalyzer
from src.planner import UpgradePathPlanner, RiskAssessment, MigrationPlanner
from src.reporter import MarkdownReporter, JSONExporter, HTMLReporter

__all__ = [
    "setup_logger",
    "get_logger",
    "EKSScanner",
    "K8sScanner",
    "CompatibilityAnalyzer",
    "DeprecationAnalyzer",
    "ReleaseNotesAnalyzer",
    "UpgradePathPlanner",
    "RiskAssessment",
    "MigrationPlanner",
    "MarkdownReporter",
    "JSONExporter",
    "HTMLReporter",
]

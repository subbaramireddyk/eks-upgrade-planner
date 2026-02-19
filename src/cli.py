"""Main CLI interface for EKS Upgrade Planner."""

import click
import sys
import os
from pathlib import Path
from typing import Optional

from .utils import setup_logger, get_logger, AWSHelper, K8sHelper, Cache
from .scanner import EKSScanner, K8sScanner
from .analyzer import CompatibilityAnalyzer, DeprecationAnalyzer, ReleaseNotesAnalyzer
from .planner import UpgradePathPlanner, RiskAssessment, MigrationPlanner
from .reporter import MarkdownReporter, JSONExporter, HTMLReporter

logger = None

# Platform-safe symbols
# Use emojis on Unix-like systems, plain text on Windows
USE_EMOJI = os.name != "nt"
SYMBOLS = {
    "success": "✅" if USE_EMOJI else "[OK]",
    "error": "❌" if USE_EMOJI else "[ERROR]",
    "warning": "⚠️" if USE_EMOJI else "[WARNING]",
    "search": "🔍" if USE_EMOJI else "[SCAN]",
    "chart": "📊" if USE_EMOJI else "[ANALYZE]",
    "plug": "🔌" if USE_EMOJI else "[ADDON]",
    "bolt": "⚡" if USE_EMOJI else "[CHANGE]",
    "doc": "📄" if USE_EMOJI else "[REPORT]",
    "note": "📝" if USE_EMOJI else "[PLAN]",
}


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--log-file", type=click.Path(), help="Log file path")
@click.pass_context
def cli(ctx, debug, log_file):
    """EKS Upgrade Planner - Automate EKS cluster upgrade planning."""
    global logger

    log_path = Path(log_file) if log_file else None
    logger = setup_logger(debug=debug, log_file=log_path)

    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@cli.command()
@click.option("--cluster", required=True, help="EKS cluster name")
@click.option("--region", help="AWS region")
@click.option("--profile", help="AWS profile name")
@click.pass_context
def scan(ctx, cluster, region, profile):
    """Scan EKS cluster and Kubernetes resources."""
    try:
        logger.info(f"Starting scan of cluster: {cluster}")

        # Initialize AWS helper
        aws_helper = AWSHelper(region=region, profile=profile)

        # Validate credentials
        if not aws_helper.validate_credentials():
            click.echo(
                f"{SYMBOLS['error']} Failed to validate AWS credentials", err=True
            )
            sys.exit(1)

        # Initialize EKS scanner
        eks_scanner = EKSScanner(aws_helper)

        # Scan cluster
        click.echo(f"{SYMBOLS['search']} Scanning EKS cluster: {cluster}")
        cluster_info = eks_scanner.scan_cluster(cluster)

        # Display summary
        summary = cluster_info["summary"]
        click.echo(f"\n{SYMBOLS['success']} Scan complete!")
        click.echo(f"  Cluster: {summary['cluster_name']}")
        click.echo(f"  Version: {summary['cluster_version']}")
        click.echo(f"  Node Groups: {summary['node_group_count']}")
        click.echo(f"  Addons: {summary['addon_count']}")
        click.echo(f"  Status: {summary['status']}")

        # Try to scan Kubernetes resources if kubeconfig is available
        try:
            click.echo(f"\n{SYMBOLS['search']} Scanning Kubernetes resources...")
            k8s_helper = K8sHelper()
            k8s_scanner = K8sScanner(k8s_helper)
            k8s_results = k8s_scanner.scan_cluster()

            click.echo(f"  Deployments: {k8s_results['summary']['total_deployments']}")
            click.echo(
                f"  StatefulSets: {k8s_results['summary']['total_statefulsets']}"
            )
            click.echo(f"  DaemonSets: {k8s_results['summary']['total_daemonsets']}")
            click.echo(f"  CRDs: {k8s_results['summary']['total_crds']}")

        except Exception as e:
            logger.warning(f"Could not scan Kubernetes resources: {e}")
            click.echo(
                f"\n{SYMBOLS['warning']}  Could not scan Kubernetes resources (kubeconfig may not be configured)"
            )

    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=ctx.obj.get("debug"))
        click.echo(f"{SYMBOLS['error']} Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--cluster", required=True, help="EKS cluster name")
@click.option("--region", help="AWS region")
@click.option("--profile", help="AWS profile name")
@click.option("--target-version", required=True, help="Target EKS version")
@click.pass_context
def analyze(ctx, cluster, region, profile, target_version):
    """Analyze cluster compatibility and detect issues."""
    try:
        logger.info(f"Analyzing cluster: {cluster} for upgrade to {target_version}")

        # Initialize helpers
        aws_helper = AWSHelper(region=region, profile=profile)
        if not aws_helper.validate_credentials():
            click.echo(
                f"{SYMBOLS['error']} Failed to validate AWS credentials", err=True
            )
            sys.exit(1)

        # Scan cluster
        click.echo(f"{SYMBOLS['search']} Scanning cluster...")
        eks_scanner = EKSScanner(aws_helper)
        cluster_info = eks_scanner.scan_cluster(cluster)

        current_version = cluster_info["cluster"]["version"]
        click.echo(f"  Current version: {current_version}")
        click.echo(f"  Target version: {target_version}")

        # Initialize analyzers
        compat_analyzer = CompatibilityAnalyzer()
        deprecation_analyzer = DeprecationAnalyzer()
        release_notes_analyzer = ReleaseNotesAnalyzer()

        # Check version compatibility
        click.echo(f"\n{SYMBOLS['chart']} Analyzing compatibility...")
        can_upgrade, reason = compat_analyzer.can_upgrade_directly(
            current_version, target_version
        )

        if can_upgrade:
            click.echo(f"  {SYMBOLS['success']} {reason}")
        else:
            click.echo(f"  {SYMBOLS['error']} {reason}")

        # Check addon compatibility
        click.echo(f"\n{SYMBOLS['plug']} Analyzing addons...")
        addon_recs = compat_analyzer.get_addon_recommendations(
            cluster_info["addons"], target_version
        )

        incompatible = [a for a in addon_recs if a["action_required"]]
        if incompatible:
            click.echo(
                f"  {SYMBOLS['warning']}  {len(incompatible)} addons need updates:"
            )
            for addon in incompatible:
                click.echo(f"     - {addon['addon_name']}: {addon['action']}")
        else:
            click.echo(f"  {SYMBOLS['success']} All addons compatible")

        # Get breaking changes
        click.echo(f"\n{SYMBOLS['bolt']} Checking for breaking changes...")
        breaking_changes = release_notes_analyzer.get_breaking_changes(
            current_version, target_version
        )

        if breaking_changes:
            click.echo(
                f"  {SYMBOLS['warning']}  {len(breaking_changes)} breaking changes found:"
            )
            for change in breaking_changes[:5]:
                click.echo(f"     - [{change['impact']}] {change['title']}")
        else:
            click.echo(f"  {SYMBOLS['success']} No breaking changes identified")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=ctx.obj.get("debug"))
        click.echo(f"{SYMBOLS['error']} Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--cluster", required=True, help="EKS cluster name")
@click.option("--region", help="AWS region")
@click.option("--profile", help="AWS profile name")
@click.option("--target-version", required=True, help="Target EKS version")
@click.option(
    "--format",
    type=click.Choice(["markdown", "json", "html"]),
    default="markdown",
    help="Output format",
)
@click.option("--output", type=click.Path(), help="Output file path")
@click.pass_context
def plan(ctx, cluster, region, profile, target_version, format, output):
    """Generate comprehensive upgrade plan."""
    try:
        logger.info(f"Generating upgrade plan for {cluster} to {target_version}")

        # Initialize helpers
        aws_helper = AWSHelper(region=region, profile=profile)
        if not aws_helper.validate_credentials():
            click.echo(
                f"{SYMBOLS['error']} Failed to validate AWS credentials", err=True
            )
            sys.exit(1)

        cache = Cache()

        # Scan cluster
        click.echo(f"{SYMBOLS['search']} Scanning cluster...")
        eks_scanner = EKSScanner(aws_helper)
        cluster_info = eks_scanner.scan_cluster(cluster)

        # Scan Kubernetes resources
        k8s_results = {}
        try:
            k8s_helper = K8sHelper()
            k8s_scanner = K8sScanner(k8s_helper)
            k8s_results = k8s_scanner.scan_cluster()
        except Exception as e:
            logger.warning(f"Could not scan Kubernetes resources: {e}")

        current_version = cluster_info["cluster"]["version"]

        # Initialize analyzers
        click.echo(f"{SYMBOLS['chart']} Analyzing compatibility and risks...")
        compat_analyzer = CompatibilityAnalyzer()
        deprecation_analyzer = DeprecationAnalyzer()
        release_notes_analyzer = ReleaseNotesAnalyzer(cache)

        # Validate upgrade path
        validation = compat_analyzer.validate_upgrade_path(
            current_version, target_version, cluster_info["addons"]
        )

        # Get addon recommendations
        addon_recs = compat_analyzer.get_addon_recommendations(
            cluster_info["addons"], target_version
        )

        # Get breaking changes
        breaking_changes = release_notes_analyzer.get_breaking_changes(
            current_version, target_version
        )

        # Analyze deprecated APIs
        deprecated_apis = k8s_results.get("deprecated_apis", {})

        # Initialize planners
        click.echo(f"{SYMBOLS['note']} Generating upgrade plan...")
        upgrade_path_planner = UpgradePathPlanner(compat_analyzer)
        risk_assessment = RiskAssessment()
        migration_planner = MigrationPlanner()

        # Generate upgrade path
        upgrade_path = upgrade_path_planner.generate_upgrade_path(
            current_version, target_version
        )

        # Determine addon upgrade order
        addon_upgrade_order = upgrade_path_planner.determine_addon_upgrade_order(
            cluster_info["addons"]
        )

        # Create pre-upgrade checklist
        pre_upgrade_checklist = upgrade_path_planner.create_pre_upgrade_checklist(
            cluster_info, target_version
        )

        # Plan node rotation
        node_rotation_plan = upgrade_path_planner.plan_node_group_rotation(
            cluster_info["node_groups"]
        )

        # Create runbook
        runbook = upgrade_path_planner.create_upgrade_runbook(
            cluster, upgrade_path, cluster_info["addons"], cluster_info["node_groups"]
        )

        # Estimate time
        time_estimation = upgrade_path_planner.estimate_upgrade_time(
            upgrade_path, cluster_info["node_groups"], cluster_info["addons"]
        )

        # Perform risk assessment
        comprehensive_risk = risk_assessment.perform_comprehensive_assessment(
            cluster_info,
            upgrade_path,
            deprecated_apis,
            breaking_changes,
            addon_recs,
            cluster_info["node_groups"],
        )

        # Generate migration plan
        migration_plan_result = migration_planner.generate_migration_plan(
            deprecated_apis, breaking_changes, target_version, cluster_info
        )

        # Prepare results
        analysis_results = {
            "addon_recommendations": addon_recs,
            "deprecated_apis": deprecated_apis,
            "breaking_changes": breaking_changes,
        }

        upgrade_plan_result = {
            "upgrade_path": upgrade_path,
            "addon_upgrade_order": addon_upgrade_order,
            "pre_upgrade_checklist": pre_upgrade_checklist,
            "node_rotation_plan": node_rotation_plan,
            "runbook": runbook,
            "time_estimation": time_estimation,
        }

        # Generate report
        click.echo(f"{SYMBOLS['doc']} Generating {format} report...")

        if format == "markdown":
            reporter = MarkdownReporter()
            report = reporter.generate_report(
                cluster_info,
                k8s_results,
                analysis_results,
                upgrade_plan_result,
                comprehensive_risk,
                migration_plan_result,
            )
        elif format == "json":
            reporter = JSONExporter()
            report = reporter.export_report(
                cluster_info,
                k8s_results,
                analysis_results,
                upgrade_plan_result,
                comprehensive_risk,
                migration_plan_result,
            )
        else:  # html
            reporter = HTMLReporter()
            report = reporter.generate_report(
                cluster_info,
                k8s_results,
                analysis_results,
                upgrade_plan_result,
                comprehensive_risk,
                migration_plan_result,
            )

        # Output report
        if output:
            output_path = Path(output)
            output_path.write_text(report)
            click.echo(f"{SYMBOLS['success']} Report saved to: {output}")
        else:
            click.echo("\n" + "=" * 80)
            click.echo(report)
            click.echo("=" * 80)

        # Display summary
        click.echo(f"\n{SYMBOLS['chart']} Upgrade Plan Summary:")
        click.echo(f"  Risk Level: {comprehensive_risk['overall_risk']}")
        click.echo(f"  Version Jumps: {len(upgrade_path) - 1}")
        click.echo(f"  Estimated Time: {time_estimation['total_hours']} hours")
        click.echo(f"  Deprecated APIs: {len(deprecated_apis)}")
        click.echo(f"  Breaking Changes: {len(breaking_changes)}")

    except Exception as e:
        logger.error(f"Plan generation failed: {e}", exc_info=ctx.obj.get("debug"))
        click.echo(f"{SYMBOLS['error']} Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--addon", required=True, help="Addon name")
@click.option("--current", required=True, help="Current addon version")
@click.option("--eks-version", required=True, help="EKS version")
@click.pass_context
def check_addon(ctx, addon, current, eks_version):
    """Check addon version compatibility."""
    try:
        logger.info(f"Checking addon {addon} version {current} for EKS {eks_version}")

        analyzer = CompatibilityAnalyzer()
        is_compatible, recommended = analyzer.check_addon_compatibility(
            addon, current, eks_version
        )

        click.echo(f"Addon: {addon}")
        click.echo(f"Current Version: {current}")
        click.echo(f"EKS Version: {eks_version}")

        if is_compatible:
            click.echo(f"{SYMBOLS['success']} Compatible")
        else:
            click.echo(f"{SYMBOLS['error']} Not compatible")
            if recommended:
                click.echo(f"Recommended Version: {recommended}")

    except Exception as e:
        logger.error(f"Addon check failed: {e}", exc_info=ctx.obj.get("debug"))
        click.echo(f"{SYMBOLS['error']} Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    from . import __version__

    click.echo(f"EKS Upgrade Planner v{__version__}")


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()

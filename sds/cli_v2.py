#!/usr/bin/env python3
"""
SDS V2 - Version-Agnostic Stupid Dependency Solver
A doctor for your project that speaks multiple languages without hardcoded assumptions.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

from .core.solver_v2 import VersionAgnosticSolver, ConflictV2, FixV2
from .core.env_detector import EnvironmentDetector
from .core.manifest_parser import ManifestParser


class ColoredOutput:
    """Simple colored terminal output."""

    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "end": "\033[0m",
    }

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Colorize text if colors are supported."""
        if sys.stdout.isatty():
            return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['end']}"
        return text

    @classmethod
    def error(cls, text: str) -> str:
        return cls.colorize(f"❌ {text}", "red")

    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colorize(f"⚠️  {text}", "yellow")

    @classmethod
    def success(cls, text: str) -> str:
        return cls.colorize(f"✅ {text}", "green")

    @classmethod
    def info(cls, text: str) -> str:
        return cls.colorize(f"ℹ️  {text}", "blue")

    @classmethod
    def header(cls, text: str) -> str:
        return cls.colorize(f"\n🚀 {text}", "bold")


def main():
    parser = argparse.ArgumentParser(
        prog="sds",
        description="🧰 Version-Agnostic Dependency Solver - Your universal project doctor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 Universal Commands (work with any language/version):
  sds analyze              # 🔍 Complete project analysis
  sds check                # 🚨 Find compatibility conflicts
  sds fix                  # 🔧 Show fix suggestions
  sds validate <tool>      # ✅ Check specific tool compatibility

🌐 Analysis Features:
  sds analyze --json       # Machine-readable output
  sds analyze --tool elixir # Focus on specific tool
  sds check --errors-only  # Show only blocking issues

🛠️  Fix Management:
  sds fix --apply          # Apply suggested fixes (interactive)
  sds fix --risk low       # Only show low-risk fixes
  sds validate-fix <id>    # Check if fix can be safely applied

🔧 Tool Utilities:
  sds version-info <tool>  # Show version constraints and suggestions
  sds environment          # Show detected environment
  sds rules                # Show loaded compatibility rules

💡 Examples:
  sds analyze              # Full project analysis
  sds check --tool python  # Check Python compatibility
  sds fix --apply --risk low # Apply safe fixes
  sds validate elixir      # Check Elixir setup
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command - comprehensive analysis
    analyze_parser = subparsers.add_parser(
        "analyze", help="Perform comprehensive project analysis"
    )
    analyze_parser.add_argument(
        "--path", "-p", default=".", help="Project directory to analyze"
    )
    analyze_parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    analyze_parser.add_argument("--tool", help="Focus analysis on specific tool")
    analyze_parser.add_argument("--output", "-o", help="Save results to file")

    # Check command - find conflicts only
    check_parser = subparsers.add_parser(
        "check", help="Check for compatibility conflicts"
    )
    check_parser.add_argument(
        "--path", "-p", default=".", help="Project directory to check"
    )
    check_parser.add_argument("--tool", help="Check specific tool only")
    check_parser.add_argument(
        "--errors-only", action="store_true", help="Show only error-level conflicts"
    )
    check_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed conflict information",
    )

    # Fix command - show/apply fixes
    fix_parser = subparsers.add_parser("fix", help="Show and apply fix suggestions")
    fix_parser.add_argument("--path", "-p", default=".", help="Project directory path")
    fix_parser.add_argument(
        "--apply", action="store_true", help="Interactively apply fixes"
    )
    fix_parser.add_argument(
        "--risk", choices=["low", "medium", "high"], help="Filter fixes by risk level"
    )
    fix_parser.add_argument("--tool", help="Show fixes for specific tool only")
    fix_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without applying",
    )

    # Validate command - check tool compatibility
    validate_parser = subparsers.add_parser(
        "validate", help="Validate tool compatibility"
    )
    validate_parser.add_argument(
        "tool", help="Tool to validate (e.g., python, elixir, node)"
    )
    validate_parser.add_argument(
        "--path", "-p", default=".", help="Project directory path"
    )
    validate_parser.add_argument(
        "--version", help="Specific version to validate against"
    )

    # Version-info command - version analysis
    version_parser = subparsers.add_parser(
        "version-info", help="Show version constraints and suggestions"
    )
    version_parser.add_argument("tool", help="Tool to analyze")
    version_parser.add_argument(
        "--path", "-p", default=".", help="Project directory path"
    )

    # Environment command - show environment
    env_parser = subparsers.add_parser(
        "environment", help="Show detected development environment"
    )
    env_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # Rules command - show compatibility rules
    rules_parser = subparsers.add_parser(
        "rules", help="Show loaded compatibility rules"
    )
    rules_parser.add_argument("--tool", help="Show rules for specific tool")

    # Validate-fix command - validate specific fix
    validate_fix_parser = subparsers.add_parser(
        "validate-fix", help="Validate that a specific fix can be applied"
    )
    validate_fix_parser.add_argument("fix_id", help="Fix ID to validate")
    validate_fix_parser.add_argument(
        "--path", "-p", default=".", help="Project directory path"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Route to appropriate command handler
        if args.command == "analyze":
            cmd_analyze(args)
        elif args.command == "check":
            cmd_check(args)
        elif args.command == "fix":
            cmd_fix(args)
        elif args.command == "validate":
            cmd_validate(args)
        elif args.command == "version-info":
            cmd_version_info(args)
        elif args.command == "environment":
            cmd_environment(args)
        elif args.command == "rules":
            cmd_rules(args)
        elif args.command == "validate-fix":
            cmd_validate_fix(args)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()

    except KeyboardInterrupt:
        print(f"\n{ColoredOutput.warning('Operation cancelled by user')}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{ColoredOutput.error(f'Error: {e}')}")
        sys.exit(1)


def cmd_analyze(args):
    """Perform comprehensive project analysis."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(ColoredOutput.error(f"Path does not exist: {project_path}"))
        return

    print(ColoredOutput.header(f"Analyzing project: {project_path}"))

    solver = VersionAgnosticSolver()
    analysis = solver.analyze_project(project_path)

    if args.json:
        output = json.dumps(analysis, indent=2, default=str)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(ColoredOutput.success(f"Analysis saved to {args.output}"))
        else:
            print(output)
        return

    # Human-readable output
    _print_analysis_summary(analysis)

    if args.tool:
        _print_tool_specific_analysis(analysis, args.tool)
    else:
        _print_conflicts(analysis.get("conflicts", []), verbose=True)
        _print_fix_suggestions(analysis.get("fix_suggestions", {}))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2, default=str)
        print(ColoredOutput.success(f"\nFull analysis saved to {args.output}"))


def cmd_check(args):
    """Check for compatibility conflicts."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(ColoredOutput.error(f"Path does not exist: {project_path}"))
        return

    print(ColoredOutput.header(f"Checking compatibility: {project_path}"))

    solver = VersionAgnosticSolver()

    if args.tool:
        # Check specific tool
        env_detector = EnvironmentDetector()
        env_info = env_detector.detect_all()
        current_version = env_info.get(args.tool, {}).get("version")

        conflicts = solver.check_tool_compatibility(
            args.tool, current_version, project_path
        )
    else:
        # Check all tools
        conflicts = solver.find_conflicts(project_path)

    if args.errors_only:
        conflicts = [c for c in conflicts if c.severity == "error"]

    # Convert ConflictV2 objects to dictionaries for printing
    conflict_dicts = []
    for conflict in conflicts:
        if hasattr(conflict, "__dict__"):
            conflict_dict = {
                "severity": conflict.severity,
                "tool": conflict.tool,
                "message": conflict.message,
                "current_version": conflict.current_version,
                "required_version": conflict.required_version,
                "affected_packages": conflict.affected_packages,
                "description": conflict.description,
            }
            conflict_dicts.append(conflict_dict)
        else:
            conflict_dicts.append(conflict)

    _print_conflicts(conflict_dicts, args.verbose)

    if not conflicts:
        print(ColoredOutput.success("No compatibility conflicts found! 🎉"))
    else:
        error_count = len([c for c in conflicts if c.severity == "error"])
        warning_count = len([c for c in conflicts if c.severity == "warning"])

        print(f"\n📊 Summary: {error_count} errors, {warning_count} warnings")

        if error_count > 0:
            print(ColoredOutput.info("Run 'sds fix' to see suggested solutions"))


def cmd_fix(args):
    """Show and apply fix suggestions."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(ColoredOutput.error(f"Path does not exist: {project_path}"))
        return

    solver = VersionAgnosticSolver()

    # Find conflicts first
    conflicts = solver.find_conflicts(project_path)

    if args.tool:
        conflicts = [c for c in conflicts if c.tool == args.tool]

    if not conflicts:
        print(ColoredOutput.success("No conflicts found that need fixing! 🎉"))
        return

    # Get fix suggestions
    fix_suggestions = solver.suggest_fixes(conflicts, project_path)

    # Filter by risk level
    if args.risk:
        filtered_suggestions = {}
        for conflict_id, fixes in fix_suggestions.items():
            filtered_fixes = [f for f in fixes if f.risk_level == args.risk]
            if filtered_fixes:
                filtered_suggestions[conflict_id] = filtered_fixes
        fix_suggestions = filtered_suggestions

    if not fix_suggestions:
        print(ColoredOutput.warning("No fix suggestions available for current filters"))
        return

    print(ColoredOutput.header("Fix Suggestions"))
    _print_fix_suggestions(fix_suggestions, show_commands=not args.apply)

    if args.apply:
        _apply_fixes_interactively(fix_suggestions, solver, project_path, args.dry_run)
    elif not args.dry_run:
        print(ColoredOutput.info("\nTo apply fixes, run with --apply flag"))


def cmd_validate(args):
    """Validate tool compatibility."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(ColoredOutput.error(f"Path does not exist: {project_path}"))
        return

    solver = VersionAgnosticSolver()

    print(ColoredOutput.header(f"Validating {args.tool} compatibility"))

    conflicts = solver.check_tool_compatibility(args.tool, args.version, project_path)

    if not conflicts:
        print(ColoredOutput.success(f"{args.tool} is compatible! ✅"))
    else:
        print(ColoredOutput.warning(f"Found compatibility issues with {args.tool}:"))

        # Convert ConflictV2 objects to dictionaries for printing
        conflict_dicts = []
        for conflict in conflicts:
            if hasattr(conflict, "__dict__"):
                conflict_dict = {
                    "severity": conflict.severity,
                    "tool": conflict.tool,
                    "message": conflict.message,
                    "current_version": conflict.current_version,
                    "required_version": conflict.required_version,
                    "affected_packages": conflict.affected_packages,
                    "description": conflict.description,
                }
                conflict_dicts.append(conflict_dict)
            else:
                conflict_dicts.append(conflict)

        _print_conflicts(conflict_dicts, verbose=True)

        # Show suggestions
        fix_suggestions = solver.suggest_fixes(conflicts, project_path)
        if fix_suggestions:
            print(ColoredOutput.info("\nSuggested fixes:"))
            _print_fix_suggestions(fix_suggestions)


def cmd_version_info(args):
    """Show version information and suggestions."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(ColoredOutput.error(f"Path does not exist: {project_path}"))
        return

    solver = VersionAgnosticSolver()

    # Parse manifests to extract constraints
    manifests = solver._parse_manifests(project_path)
    constraints = []

    # Extract constraints for this tool
    for manifest_name, manifest_data in manifests.items():
        if isinstance(manifest_data, dict):
            version_requirements = solver._extract_version_requirements(
                manifest_data.get("type", ""), manifest_data
            )

            for req_name, req_value in version_requirements.items():
                if args.tool in req_name.lower():
                    constraints.append(req_value)

    version_info = solver.get_version_suggestions(args.tool, constraints, project_path)

    print(ColoredOutput.header(f"Version Information: {args.tool}"))
    print(f"Current Version: {version_info.get('current_version', 'Not found')}")
    print(f"Constraints: {', '.join(constraints) or 'None'}")

    suggestions = version_info.get("suggestions", {})
    if suggestions.get("recommendations"):
        print(ColoredOutput.info("\nRecommendations:"))
        for rec in suggestions["recommendations"]:
            print(f"  • {rec.get('description', 'No description')}")

    if version_info.get("compatibility_notes"):
        print(ColoredOutput.info("\nCompatibility Notes:"))
        for note in version_info["compatibility_notes"]:
            print(f"  • {note}")


def cmd_environment(args):
    """Show detected development environment."""
    print(ColoredOutput.header("Development Environment"))

    env_detector = EnvironmentDetector()
    env_info = env_detector.detect_all()

    if args.json:
        print(json.dumps(env_info, indent=2, default=str))
        return

    for tool, info in env_info.items():
        if info and "version" in info:
            version = info["version"]
            location = info.get("location", "Unknown")
            print(f"  {tool:12} {version:15} ({location})")
        else:
            print(f"  {tool:12} {'Not found':15}")


def cmd_rules(args):
    """Show loaded compatibility rules."""
    solver = VersionAgnosticSolver()

    print(ColoredOutput.header("Compatibility Rules"))

    if args.tool:
        rules = solver.compatibility_engine.rules.get(args.tool, [])
        if rules:
            print(f"\nRules for {args.tool}:")
            for rule in rules:
                print(f"  • {rule.id}: {rule.description}")
                if rule.affected_versions:
                    versions = rule.affected_versions
                    print(
                        f"    Affects: {versions.get('operator', '')} {versions.get('version', '')}"
                    )
        else:
            print(f"No rules found for {args.tool}")
    else:
        for tool, rules in solver.compatibility_engine.rules.items():
            print(f"\n{tool}:")
            for rule in rules:
                print(f"  • {rule.id}: {rule.description}")


def cmd_validate_fix(args):
    """Validate that a fix can be applied."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(ColoredOutput.error(f"Path does not exist: {project_path}"))
        return

    # This is a simplified implementation - in practice you'd need to
    # store fixes and look them up by ID
    print(
        ColoredOutput.warning(
            "Fix validation not implemented - this would validate fix safety"
        )
    )


# Helper functions for output formatting


def _print_analysis_summary(analysis: Dict[str, Any]):
    """Print analysis summary."""
    summary = analysis.get("summary", {})

    print(f"\n📊 Analysis Summary:")
    print(f"   Total Conflicts: {summary.get('total_conflicts', 0)}")
    print(f"   Errors: {summary.get('errors', 0)}")
    print(f"   Warnings: {summary.get('warnings', 0)}")
    print(f"   Tools Affected: {', '.join(summary.get('tools_affected', []))}")
    print(f"   Fixable: {summary.get('fixable_conflicts', 0)}")
    print(f"   Auto-fixable: {summary.get('auto_fixable', 0)}")


def _print_tool_specific_analysis(analysis: Dict[str, Any], tool: str):
    """Print analysis for a specific tool."""
    conflicts = [c for c in analysis.get("conflicts", []) if c.get("tool") == tool]
    fix_suggestions = {
        k: v
        for k, v in analysis.get("fix_suggestions", {}).items()
        if any(f.get("tool") == tool for f in v)
    }

    print(f"\n🔍 Analysis for {tool}:")
    _print_conflicts(conflicts, verbose=True)

    if fix_suggestions:
        print(ColoredOutput.info(f"\nFix suggestions for {tool}:"))
        _print_fix_suggestions(fix_suggestions)


def _print_conflicts(conflicts: List[Dict[str, Any]], verbose: bool = False):
    """Print conflicts in a readable format."""
    if not conflicts:
        return

    print(ColoredOutput.info(f"\n🚨 Found {len(conflicts)} conflicts:"))

    for conflict in conflicts:
        severity = conflict.get("severity", "unknown")
        tool = conflict.get("tool", "unknown")
        message = conflict.get("message", "No message")

        if severity == "error":
            prefix = ColoredOutput.error("ERROR")
        elif severity == "warning":
            prefix = ColoredOutput.warning("WARN")
        else:
            prefix = ColoredOutput.info("INFO")

        print(f"\n  {prefix} [{tool}] {message}")

        if verbose:
            if conflict.get("current_version"):
                print(f"    Current: {conflict['current_version']}")
            if conflict.get("required_version"):
                print(f"    Required: {conflict['required_version']}")
            if conflict.get("affected_packages"):
                packages = ", ".join(conflict["affected_packages"])
                print(f"    Packages: {packages}")


def _print_fix_suggestions(
    fix_suggestions: Dict[str, List[Dict[str, Any]]], show_commands: bool = True
):
    """Print fix suggestions."""
    if not fix_suggestions:
        return

    print(ColoredOutput.info(f"\n🔧 Fix Suggestions:"))

    for conflict_id, fixes in fix_suggestions.items():
        print(f"\n  Fixes for {conflict_id}:")

        for i, fix in enumerate(fixes, 1):
            risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(
                fix.get("risk_level", "medium"), "white"
            )

            risk_indicator = ColoredOutput.colorize(
                f"[{fix.get('risk_level', 'unknown').upper()}]", risk_color
            )

            print(
                f"    {i}. {risk_indicator} {fix.get('description', 'No description')}"
            )

            if show_commands and fix.get("command"):
                print(
                    f"       Command: {ColoredOutput.colorize(fix['command'], 'cyan')}"
                )

            if fix.get("alternatives"):
                print(f"       Alternatives: {len(fix['alternatives'])} available")


def _apply_fixes_interactively(
    fix_suggestions: Dict[str, List[Dict[str, Any]]],
    solver: VersionAgnosticSolver,
    project_path: Path,
    dry_run: bool,
):
    """Apply fixes interactively."""
    print(ColoredOutput.header("Interactive Fix Application"))

    for conflict_id, fixes in fix_suggestions.items():
        print(f"\n📋 Fixes for: {conflict_id}")

        # Show available fixes
        for i, fix in enumerate(fixes, 1):
            risk_level = fix.get("risk_level", "unknown")
            print(
                f"  {i}. [{risk_level.upper()}] {fix.get('description', 'No description')}"
            )

        print("  0. Skip this conflict")

        try:
            choice = input("\nSelect fix (number): ").strip()
            if choice == "0" or not choice:
                continue

            fix_index = int(choice) - 1
            if 0 <= fix_index < len(fixes):
                selected_fix = fixes[fix_index]

                if dry_run:
                    print(f"Would apply: {selected_fix.get('command', 'No command')}")
                else:
                    print(
                        f"Applying: {selected_fix.get('description', 'No description')}"
                    )
                    # Here you would implement actual fix application
                    print(ColoredOutput.warning("Fix application not implemented yet"))
            else:
                print(ColoredOutput.warning("Invalid selection"))

        except (ValueError, KeyboardInterrupt):
            print(ColoredOutput.warning("Skipping..."))
            continue


if __name__ == "__main__":
    main()

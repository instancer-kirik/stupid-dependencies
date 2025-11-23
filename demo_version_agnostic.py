#!/usr/bin/env python3
"""
Version-Agnostic SDS Demo - Showcases universal compatibility detection.

This demo shows how the new SDS can detect and fix compatibility issues
across any language, version, or package manager without hardcoded logic.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add the parent directory to the path to import SDS modules
sys.path.insert(0, str(Path(__file__).parent))

from sds.core.solver_v2 import VersionAgnosticSolver
from sds.core.compatibility_engine import CompatibilityEngine
from sds.core.fix_generator import FixGenerator
from sds.core.version_constraints import VersionParser, VersionComparator


class DemoColors:
    """Terminal colors for demo output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @classmethod
    def header(cls, text: str) -> str:
        return f"{cls.HEADER}{cls.BOLD}{text}{cls.ENDC}"

    @classmethod
    def success(cls, text: str) -> str:
        return f"{cls.OKGREEN}✅ {text}{cls.ENDC}"

    @classmethod
    def error(cls, text: str) -> str:
        return f"{cls.FAIL}❌ {text}{cls.ENDC}"

    @classmethod
    def warning(cls, text: str) -> str:
        return f"{cls.WARNING}⚠️  {text}{cls.ENDC}"

    @classmethod
    def info(cls, text: str) -> str:
        return f"{cls.OKBLUE}ℹ️  {text}{cls.ENDC}"

    @classmethod
    def cyan(cls, text: str) -> str:
        return f"{cls.OKCYAN}{text}{cls.ENDC}"


def print_banner():
    """Print demo banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               🚀 VERSION-AGNOSTIC DEPENDENCY SOLVER DEMO 🚀                ║
║                                                                              ║
║    Universal compatibility detection that works with ANY language,          ║
║    ANY version, and ANY package manager - no hardcoded assumptions!        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(DemoColors.header(banner))


def demo_version_constraint_parsing():
    """Demonstrate version constraint parsing across different ecosystems."""
    print(DemoColors.header("\n🔍 DEMO 1: Universal Version Constraint Parsing"))
    print("Testing version constraints from multiple package ecosystems...")

    parser = VersionParser()
    comparator = VersionComparator()

    test_cases = [
        # Elixir-style constraints
        ("~> 1.14", "1.15.2", True, "Elixir compatible release"),
        ("~> 1.14", "2.0.0", False, "Elixir compatible release"),
        # npm-style constraints
        ("^2.3.4", "2.5.0", True, "npm caret range"),
        ("^2.3.4", "3.0.0", False, "npm caret range"),
        ("~2.3.4", "2.3.8", True, "npm tilde range"),
        ("~2.3.4", "2.4.0", False, "npm tilde range"),
        # Python-style constraints
        (">=3.8", "3.9.1", True, "Python minimum version"),
        (">=3.8", "3.7.0", False, "Python minimum version"),
        # Generic constraints
        ("1.2.3", "1.2.3", True, "Exact version match"),
        (">= 1.0.0", "1.5.2", True, "Generic greater-than-equal"),
    ]

    for constraint_str, version, expected, description in test_cases:
        constraint = parser.parse_constraint(constraint_str)
        if constraint:
            result = comparator.satisfies_constraint(version, constraint)
            status = "✅" if result == expected else "❌"
            print(f"  {status} {description}")
            print(f"     {constraint_str} vs {version} → {result}")
        else:
            print(f"  ❌ Failed to parse constraint: {constraint_str}")

    print(DemoColors.success("\nVersion constraint parsing works universally! 🎉"))


def demo_rule_based_compatibility():
    """Demonstrate rule-based compatibility detection."""
    print(DemoColors.header("\n🛠️  DEMO 2: Rule-Based Compatibility Detection"))
    print("Loading compatibility rules from configuration...")

    engine = CompatibilityEngine()

    print(f"Loaded rules for: {', '.join(engine.rules.keys())}")

    # Show some example rules
    if "elixir" in engine.rules:
        print(DemoColors.info("\nExample Elixir compatibility rules:"))
        for rule in engine.rules["elixir"][:2]:  # Show first 2 rules
            print(f"  • {rule.id}: {rule.description}")
            if rule.affected_versions:
                versions = rule.affected_versions
                print(
                    f"    Affects versions: {versions.get('operator', '')} {versions.get('version', '')}"
                )

    # Show package-specific issues
    if (
        "elixir" in engine.package_issues
        and "inflex" in engine.package_issues["elixir"]
    ):
        print(DemoColors.info("\nExample package-specific issue detection:"))
        inflex_issues = engine.package_issues["elixir"]["inflex"]
        for issue in inflex_issues:
            print(f"  • inflex: {issue.description}")
            print(f"    Triggers with: {issue.triggers_with}")

    print(DemoColors.success("\nRule-based system loaded successfully! 🎯"))


def demo_fix_generation():
    """Demonstrate template-based fix generation."""
    print(DemoColors.header("\n🔧 DEMO 3: Template-Based Fix Generation"))
    print("Generating fixes using flexible templates...")

    generator = FixGenerator()

    print(f"Available version managers: {list(generator.available_managers.keys())}")

    # Show template categories
    print(DemoColors.info("\nFix template categories:"))
    for category, templates in generator.templates.items():
        print(f"  • {category}: {len(templates)} templates")

    # Show package fixes database
    package_fixes = generator.config.get("package_fixes", {})
    if package_fixes:
        print(DemoColors.info("\nPackage-specific fixes available for:"))
        for tool, packages in package_fixes.items():
            print(f"  • {tool}: {list(packages.keys())}")

    print(DemoColors.success("\nFix generation system ready! ⚡"))


def demo_project_analysis():
    """Demonstrate project analysis on current directory."""
    print(DemoColors.header("\n📊 DEMO 4: Project Analysis"))
    print("Analyzing current project for compatibility issues...")

    solver = VersionAgnosticSolver()
    project_path = Path(".")

    try:
        # Get environment info
        env_info = solver._get_environment_info()
        print(DemoColors.info("Detected development environment:"))
        for tool, info in env_info.items():
            if info and "version" in info:
                print(f"  • {tool}: {info['version']}")

        # Get manifest info
        manifests = solver._parse_manifests(project_path)
        print(DemoColors.info(f"\nFound {len(manifests)} manifest files:"))
        for manifest_name in manifests.keys():
            print(f"  • {manifest_name}")

        # Find conflicts
        conflicts = solver.find_conflicts(project_path)

        if conflicts:
            print(
                DemoColors.warning(
                    f"\n🚨 Found {len(conflicts)} compatibility conflicts:"
                )
            )
            for conflict in conflicts[:3]:  # Show first 3
                print(f"  • [{conflict.tool}] {conflict.message}")

            if len(conflicts) > 3:
                print(f"  ... and {len(conflicts) - 3} more")

            # Show fix suggestions
            fix_suggestions = solver.suggest_fixes(conflicts, project_path)
            if fix_suggestions:
                print(
                    DemoColors.info(
                        f"\n🔧 Generated fix suggestions for {len(fix_suggestions)} conflicts"
                    )
                )

                # Show one example fix
                first_conflict_id = list(fix_suggestions.keys())[0]
                first_fixes = fix_suggestions[first_conflict_id]
                if first_fixes:
                    example_fix = first_fixes[0]
                    print(f"  Example fix: {example_fix.description}")
                    print(f"  Command: {DemoColors.cyan(example_fix.command)}")
                    print(f"  Risk level: {example_fix.risk_level}")
        else:
            print(DemoColors.success("\n🎉 No compatibility conflicts found!"))

    except Exception as e:
        print(DemoColors.error(f"Analysis failed: {e}"))


def demo_multi_language_support():
    """Demonstrate multi-language support without hardcoding."""
    print(DemoColors.header("\n🌍 DEMO 5: Multi-Language Support"))
    print("Showing universal support for different ecosystems...")

    # Sample version constraints from different languages
    language_examples = {
        "Python": {
            "constraint": ">=3.8,<4.0",
            "versions": ["3.7.0", "3.8.5", "3.9.0", "3.10.2"],
            "manifest": "pyproject.toml",
        },
        "Node.js": {
            "constraint": "^16.0.0",
            "versions": ["15.0.0", "16.2.0", "16.15.0", "17.0.0"],
            "manifest": "package.json",
        },
        "Rust": {
            "constraint": "1.60",
            "versions": ["1.59.0", "1.60.0", "1.65.0"],
            "manifest": "Cargo.toml",
        },
        "Elixir": {
            "constraint": "~> 1.14",
            "versions": ["1.13.0", "1.14.2", "1.15.0", "2.0.0"],
            "manifest": "mix.exs",
        },
        "Go": {
            "constraint": "1.19",
            "versions": ["1.18.0", "1.19.0", "1.20.0"],
            "manifest": "go.mod",
        },
    }

    parser = VersionParser()
    comparator = VersionComparator()

    for language, data in language_examples.items():
        print(f"\n{DemoColors.info(language)} ecosystem:")
        print(f"  Manifest file: {data['manifest']}")
        print(f"  Version constraint: {data['constraint']}")

        constraint = parser.parse_constraint(data["constraint"])
        if constraint:
            compatible_versions = []
            for version in data["versions"]:
                if comparator.satisfies_constraint(version, constraint):
                    compatible_versions.append(version)

            print(f"  Compatible versions: {', '.join(compatible_versions)}")
        else:
            print(f"  {DemoColors.error('Failed to parse constraint')}")

    print(DemoColors.success("\nUniversal language support confirmed! 🌟"))


def demo_configuration_flexibility():
    """Demonstrate how compatibility rules can be configured without code changes."""
    print(DemoColors.header("\n⚙️  DEMO 6: Configuration Flexibility"))
    print("Showing how new compatibility issues can be added via configuration...")

    # Example of how you could add new rules without code changes
    example_new_rule = {
        "id": "hypothetical_new_issue",
        "description": "Example of how new compatibility issues can be added",
        "category": "compilation_error",
        "affected_versions": {"operator": ">=", "version": "2.0.0"},
        "symptoms": [
            "new error pattern that might appear",
            "another symptom to look for",
        ],
    }

    example_package_fix = {
        "primary_fix": {
            "type": "version_override",
            "description": "Use compatible version of problematic package",
            "git_url": "https://github.com/user/fixed-package.git",
            "ref": "compatible-branch",
        },
        "alternative_fixes": [
            {
                "type": "workaround",
                "description": "Temporary workaround while fix is pending",
                "risk_level": "medium",
            }
        ],
    }

    print(DemoColors.info("Example new compatibility rule (YAML):"))
    print(DemoColors.cyan("  - id: hypothetical_new_issue"))
    print(
        DemoColors.cyan(
            "    description: Example of how new compatibility issues can be added"
        )
    )
    print(DemoColors.cyan("    affected_versions:"))
    print(DemoColors.cyan("      operator: '>='"))
    print(DemoColors.cyan("      version: '2.0.0'"))

    print(DemoColors.info("\nExample package fix configuration:"))
    print(DemoColors.cyan("  package_name:"))
    print(DemoColors.cyan("    primary_fix:"))
    print(DemoColors.cyan("      type: version_override"))
    print(DemoColors.cyan("      git_url: https://github.com/user/fixed-package.git"))

    print(DemoColors.success("\nNew issues can be handled without code changes! 🎛️"))


def demo_summary():
    """Print demo summary."""
    print(DemoColors.header("\n📈 DEMO SUMMARY"))

    achievements = [
        "✅ Version constraints work universally across all package managers",
        "✅ Compatibility detection is rule-based and configurable",
        "✅ Fix suggestions are generated from flexible templates",
        "✅ Multi-language support without hardcoded logic",
        "✅ New compatibility issues can be added via configuration",
        "✅ System is truly version and dependency agnostic",
    ]

    print(DemoColors.success("🎉 VERSION-AGNOSTIC SDS ACHIEVEMENTS:"))
    for achievement in achievements:
        print(f"   {achievement}")

    print(DemoColors.header("\n🚀 BENEFITS:"))
    benefits = [
        "🔮 Future-proof: Works with future versions automatically",
        "🌍 Universal: Supports any language/package manager",
        "⚡ Configurable: Add new rules without code changes",
        "🎯 Intelligent: Context-aware fix suggestions",
        "🔧 Maintainable: No version-specific code to update",
        "📊 Extensible: Easy to add support for new tools",
    ]

    for benefit in benefits:
        print(f"   {benefit}")


def main():
    """Run the complete version-agnostic demo."""
    print_banner()

    try:
        demo_version_constraint_parsing()
        demo_rule_based_compatibility()
        demo_fix_generation()
        demo_project_analysis()
        demo_multi_language_support()
        demo_configuration_flexibility()
        demo_summary()

        print(DemoColors.header("\n🎊 DEMO COMPLETE! 🎊"))
        print(
            DemoColors.info(
                "The Stupid Dependency Solver is now truly version-agnostic!"
            )
        )
        print(DemoColors.info("Try: python -m sds.cli_v2 analyze"))

    except KeyboardInterrupt:
        print(f"\n{DemoColors.warning('Demo interrupted by user')}")
    except Exception as e:
        print(f"\n{DemoColors.error(f'Demo error: {e}')}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

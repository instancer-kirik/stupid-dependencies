#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced Kotlin/Gradle Issue Detection and Fixing

This script demonstrates the capabilities of the enhanced SDS Kotlin/Gradle
detector and fixer with real-world complex scenarios.
"""

import sys
import os
from pathlib import Path
import json
import tempfile
import shutil
from typing import List, Dict, Any

# Add the sds package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sds.core.kotlin_gradle_detector import KotlinGradleDetector, KotlinGradleIssue
    from sds.core.kotlin_gradle_fixer import KotlinGradleFixer, KotlinGradleFix
except ImportError as e:
    print(f"Failed to import SDS modules: {e}")
    print("Make sure you're running this from the SDS project root")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def colored_print(text: str, color: str):
    """Print colored text to terminal."""
    print(f"{color}{text}{Colors.END}")


def print_header(title: str):
    """Print a formatted header."""
    colored_print(f"\n{'=' * 60}", Colors.CYAN)
    colored_print(f"{title.center(60)}", Colors.CYAN + Colors.BOLD)
    colored_print(f"{'=' * 60}", Colors.CYAN)


def print_issue(issue: KotlinGradleIssue, index: int):
    """Print a formatted issue."""
    severity_colors = {
        "error": Colors.RED,
        "warning": Colors.YELLOW,
        "info": Colors.BLUE,
    }

    color = severity_colors.get(issue.severity, Colors.WHITE)

    print(
        f"\n{index + 1}. {color}{issue.severity.upper()}{Colors.END}: {Colors.BOLD}{issue.title}{Colors.END}"
    )
    print(f"   Type: {issue.issue_type}")
    print(f"   Description: {issue.description}")

    if issue.current_value:
        print(f"   Current: {issue.current_value}")
    if issue.expected_value:
        print(f"   Expected: {issue.expected_value}")
    if issue.file_path:
        print(f"   File: {issue.file_path}")
        if issue.line_number:
            print(f"   Line: {issue.line_number}")
    if issue.fix_suggestion:
        print(f"   💡 Suggestion: {issue.fix_suggestion}")
    if issue.documentation_url:
        print(f"   📖 Docs: {issue.documentation_url}")


def print_fix(fix: KotlinGradleFix, index: int):
    """Print a formatted fix."""
    risk_colors = {
        "low": Colors.GREEN,
        "medium": Colors.YELLOW,
        "high": Colors.RED,
    }

    color = risk_colors.get(fix.risk_level, Colors.WHITE)

    print(
        f"\n{index + 1}. {Colors.BOLD}{fix.title}{Colors.END} [{color}{fix.risk_level.upper()} RISK{Colors.END}]"
    )
    print(f"   Description: {fix.description}")
    print(f"   Actions ({len(fix.actions)}):")

    for i, action in enumerate(fix.actions):
        action_type = action.get("type", "unknown")
        print(f"     {i + 1}. {action_type.replace('_', ' ').title()}")

        if action_type == "update_build_file":
            print(f"        File: {action.get('file')}")
            print(f"        Changes: {len(action.get('changes', []))}")
        elif action_type == "run_command":
            print(f"        Command: {action.get('command')}")
        elif action_type == "manual_instruction":
            print(f"        Instruction: {action.get('instruction')}")

    if fix.requires_user_input:
        print(f"   ⚠️  Requires user input")
    if fix.validation_command:
        print(f"   🔍 Validation: {fix.validation_command}")


def test_complex_project():
    """Test detection on the complex test project."""
    print_header("Testing Complex Kotlin/Gradle Project")

    test_project = Path(__file__).parent / "test_kotlin_project"

    if not test_project.exists():
        colored_print("❌ Test project not found. Please create it first.", Colors.RED)
        return

    colored_print(f"🔍 Analyzing project: {test_project}", Colors.BLUE)

    # Initialize detector
    detector = KotlinGradleDetector(test_project)

    # Detect all issues
    issues = detector.detect_all_issues()

    colored_print(f"📊 Found {len(issues)} issues", Colors.CYAN)

    # Group issues by severity
    error_issues = [i for i in issues if i.severity == "error"]
    warning_issues = [i for i in issues if i.severity == "warning"]
    info_issues = [i for i in issues if i.severity == "info"]

    colored_print(f"   🔴 Errors: {len(error_issues)}", Colors.RED)
    colored_print(f"   🟡 Warnings: {len(warning_issues)}", Colors.YELLOW)
    colored_print(f"   🔵 Info: {len(info_issues)}", Colors.BLUE)

    # Print all issues
    for i, issue in enumerate(issues):
        print_issue(issue, i)

    return issues


def test_fix_generation(issues: List[KotlinGradleIssue]):
    """Test fix generation for detected issues."""
    print_header("Testing Fix Generation")

    if not issues:
        colored_print("No issues to fix", Colors.GREEN)
        return

    test_project = Path(__file__).parent / "test_kotlin_project"
    fixer = KotlinGradleFixer(test_project)

    colored_print(f"🔧 Generating fixes for {len(issues)} issues", Colors.BLUE)

    fixes = fixer.fix_issues(issues, auto_apply=False)

    colored_print(f"📝 Generated {len(fixes)} fixes", Colors.CYAN)

    # Group fixes by risk level
    low_risk = [f for f in fixes if f.risk_level == "low"]
    medium_risk = [f for f in fixes if f.risk_level == "medium"]
    high_risk = [f for f in fixes if f.risk_level == "high"]

    colored_print(f"   🟢 Low risk: {len(low_risk)}", Colors.GREEN)
    colored_print(f"   🟡 Medium risk: {len(medium_risk)}", Colors.YELLOW)
    colored_print(f"   🔴 High risk: {len(high_risk)}", Colors.RED)

    # Print all fixes
    for i, fix in enumerate(fixes):
        print_fix(fix, i)

    return fixes


def test_version_catalog_migration():
    """Test migration to version catalogs."""
    print_header("Testing Version Catalog Migration")

    # Create a temporary project for testing migration
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_project = Path(temp_dir) / "migration_test"
        temp_project.mkdir()

        # Create a build.gradle.kts with hardcoded versions
        build_file = temp_project / "build.gradle.kts"
        build_content = """
plugins {
    kotlin("jvm") version "1.9.20"
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib:1.9.20")
    implementation("org.springframework.boot:spring-boot-starter-web:3.2.0")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.15.2")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5:1.9.20")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}
        """
        build_file.write_text(build_content.strip())

        colored_print(
            f"📁 Created temporary project with hardcoded versions", Colors.BLUE
        )

        # Detect issues
        detector = KotlinGradleDetector(temp_project)
        issues = detector.detect_all_issues()

        # Look for version catalog suggestion
        catalog_issues = [i for i in issues if "Version Catalog" in i.title]

        if catalog_issues:
            colored_print(
                f"✅ Detected need for version catalog migration", Colors.GREEN
            )

            # Generate fix
            fixer = KotlinGradleFixer(temp_project)
            fixes = fixer.fix_issues(catalog_issues)

            if fixes:
                colored_print(f"🔧 Generated migration fix", Colors.GREEN)
                print_fix(fixes[0], 0)
            else:
                colored_print("❌ Failed to generate migration fix", Colors.RED)
        else:
            colored_print("❌ Version catalog migration not detected", Colors.RED)


def test_compatibility_matrix():
    """Test version compatibility matrix checking."""
    print_header("Testing Version Compatibility Matrix")

    # Test various version combinations
    test_cases = [
        ("kotlin", "1.9.20", "gradle", "8.5"),  # Should be compatible
        ("kotlin", "1.9.20", "gradle", "7.0"),  # Should be incompatible
        ("kotlin", "2.0.0", "gradle", "7.6"),  # Should be compatible
        ("gradle", "8.5", "java", "17"),  # Should be compatible
        ("gradle", "8.5", "java", "11"),  # Should be incompatible
        ("gradle", "7.6", "java", "21"),  # Should be incompatible
    ]

    colored_print(f"🧪 Testing {len(test_cases)} compatibility scenarios", Colors.BLUE)

    for i, (tool1, ver1, tool2, ver2) in enumerate(test_cases):
        print(f"\n{i + 1}. {tool1} {ver1} + {tool2} {ver2}")

        # Create a temporary project with these versions
        with tempfile.TemporaryDirectory() as temp_dir:
            test_project = Path(temp_dir) / f"compat_test_{i}"
            test_project.mkdir()

            # Create appropriate config files based on versions
            if tool1 == "kotlin" and tool2 == "gradle":
                build_content = f'''
plugins {{
    kotlin("jvm") version "{ver1}"
}}
                '''
                (test_project / "build.gradle.kts").write_text(build_content.strip())

                # Mock gradle wrapper
                wrapper_dir = test_project / "gradle" / "wrapper"
                wrapper_dir.mkdir(parents=True)
                wrapper_content = f"distributionUrl=https\\://services.gradle.org/distributions/gradle-{ver2}-bin.zip"
                (wrapper_dir / "gradle-wrapper.properties").write_text(wrapper_content)

            detector = KotlinGradleDetector(test_project)
            issues = detector.detect_all_issues()

            compatibility_issues = [
                i for i in issues if i.issue_type == "version_compatibility"
            ]

            if compatibility_issues:
                colored_print(f"   ⚠️  Compatibility issue detected", Colors.YELLOW)
                print(f"      {compatibility_issues[0].description}")
            else:
                colored_print(f"   ✅ No compatibility issues", Colors.GREEN)


def test_modern_patterns():
    """Test detection of modern Gradle patterns."""
    print_header("Testing Modern Gradle Pattern Detection")

    patterns_to_test = [
        ("toolchain_vs_compatibility", "Java toolchain vs sourceCompatibility"),
        ("version_catalog_usage", "Version catalog adoption"),
        ("plugin_management", "Plugin management best practices"),
        ("bom_usage", "BOM (Bill of Materials) usage"),
        ("dependency_bundles", "Dependency bundle patterns"),
    ]

    colored_print(f"🔍 Testing {len(patterns_to_test)} modern patterns", Colors.BLUE)

    for pattern_type, description in patterns_to_test:
        print(f"\n• {description}")

        # Create test scenarios for each pattern
        with tempfile.TemporaryDirectory() as temp_dir:
            test_project = Path(temp_dir) / f"pattern_test_{pattern_type}"
            test_project.mkdir()

            if pattern_type == "toolchain_vs_compatibility":
                # Test mixing toolchain and sourceCompatibility
                build_content = """
plugins {
    kotlin("jvm") version "1.9.20"
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_21  // Mismatch
}

kotlin {
    jvmToolchain(19)  // Different from java config
}
                """
            elif pattern_type == "version_catalog_usage":
                # Test hardcoded versions without catalog
                build_content = """
plugins {
    kotlin("jvm") version "1.9.20"
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web:3.2.0")
    implementation("com.fasterxml.jackson.core:jackson-core:2.15.2")
}
                """
            else:
                # Generic test
                build_content = """
plugins {
    kotlin("jvm") version "1.9.20"
}
                """

            (test_project / "build.gradle.kts").write_text(build_content.strip())

            detector = KotlinGradleDetector(test_project)
            issues = detector.detect_all_issues()

            relevant_issues = [
                i
                for i in issues
                if pattern_type in i.issue_type
                or description.lower() in i.title.lower()
            ]

            if relevant_issues:
                colored_print(
                    f"   ✅ Pattern detected ({len(relevant_issues)} issues)",
                    Colors.GREEN,
                )
                for issue in relevant_issues:
                    print(f"      - {issue.title}")
            else:
                colored_print(f"   ❌ Pattern not detected", Colors.RED)


def generate_report(issues: List[KotlinGradleIssue], fixes: List[KotlinGradleFix]):
    """Generate a comprehensive report."""
    print_header("Comprehensive Analysis Report")

    # Summary statistics
    total_issues = len(issues)
    total_fixes = len(fixes)

    issue_types = {}
    severity_counts = {"error": 0, "warning": 0, "info": 0}

    for issue in issues:
        issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    fix_risks = {"low": 0, "medium": 0, "high": 0}
    automated_fixes = 0

    for fix in fixes:
        fix_risks[fix.risk_level] = fix_risks.get(fix.risk_level, 0) + 1
        if not fix.requires_user_input:
            automated_fixes += 1

    # Print summary
    colored_print(f"📊 ANALYSIS SUMMARY", Colors.BOLD)
    print(f"   Total Issues Found: {total_issues}")
    print(f"   Total Fixes Generated: {total_fixes}")
    print(f"   Automated Fixes Available: {automated_fixes}")
    print(f"   Manual Intervention Required: {total_fixes - automated_fixes}")

    print(f"\n📈 ISSUE BREAKDOWN:")
    for issue_type, count in sorted(issue_types.items()):
        print(f"   {issue_type.replace('_', ' ').title()}: {count}")

    print(f"\n🚨 SEVERITY DISTRIBUTION:")
    print(f"   🔴 Errors: {severity_counts['error']}")
    print(f"   🟡 Warnings: {severity_counts['warning']}")
    print(f"   🔵 Info: {severity_counts['info']}")

    print(f"\n🔧 FIX RISK LEVELS:")
    print(f"   🟢 Low Risk: {fix_risks['low']}")
    print(f"   🟡 Medium Risk: {fix_risks['medium']}")
    print(f"   🔴 High Risk: {fix_risks['high']}")

    # Priority recommendations
    print(f"\n🎯 PRIORITY RECOMMENDATIONS:")

    high_priority_issues = [i for i in issues if i.severity == "error"]
    if high_priority_issues:
        print(f"   1. Address {len(high_priority_issues)} critical errors immediately")
        for issue in high_priority_issues[:3]:  # Show top 3
            print(f"      • {issue.title}")

    quick_wins = [
        f for f in fixes if f.risk_level == "low" and not f.requires_user_input
    ]
    if quick_wins:
        print(f"   2. Apply {len(quick_wins)} low-risk automated fixes")

    modernization_issues = [i for i in issues if i.issue_type == "best_practice"]
    if modernization_issues:
        print(f"   3. Consider {len(modernization_issues)} modernization improvements")


def main():
    """Main test execution."""
    print_header("SDS Enhanced Kotlin/Gradle Analysis Test Suite")

    colored_print(
        "🚀 Starting comprehensive Kotlin/Gradle analysis tests...", Colors.CYAN
    )

    # Test 1: Complex project analysis
    issues = test_complex_project()

    # Test 2: Fix generation
    fixes = []
    if issues:
        fixes = test_fix_generation(issues)

    # Test 3: Version catalog migration
    test_version_catalog_migration()

    # Test 4: Compatibility matrix
    test_compatibility_matrix()

    # Test 5: Modern patterns
    test_modern_patterns()

    # Generate final report
    if issues or fixes:
        generate_report(issues, fixes)

    print_header("Test Suite Complete")
    colored_print("✨ All tests completed successfully!", Colors.GREEN)

    # Provide next steps
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review the detected issues and generated fixes")
    print(f"   2. Run with --apply flag to automatically apply low-risk fixes")
    print(f"   3. Manually address high-risk issues and compatibility problems")
    print(
        f"   4. Consider adopting modern Gradle patterns (version catalogs, toolchains)"
    )
    print(f"   5. Set up CI checks to prevent future dependency conflicts")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        colored_print("\n❌ Test suite interrupted by user", Colors.RED)
        sys.exit(1)
    except Exception as e:
        colored_print(f"\n💥 Test suite failed with error: {e}", Colors.RED)
        import traceback

        traceback.print_exc()
        sys.exit(1)

"""
Enhanced Kotlin/Gradle/Maven Issue Fixer

This module provides comprehensive fixes for Kotlin, Gradle, and Maven dependency
issues including version conflicts, toolchain mismatches, and modernization suggestions.
"""

import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import toml
import tempfile
import json

from .kotlin_gradle_detector import KotlinGradleIssue, VersionInfo


@dataclass
class KotlinGradleFix:
    """Represents a fix for a Kotlin/Gradle issue."""

    issue_type: str
    title: str
    description: str
    actions: List[Dict[str, Any]]  # List of fix actions
    risk_level: str  # "low", "medium", "high"
    requires_user_input: bool = False
    backup_files: List[str] = None
    validation_command: Optional[str] = None


class KotlinGradleFixer:
    """Comprehensive Kotlin/Gradle issue fixer."""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.backup_dir = None

    def fix_issues(
        self, issues: List[KotlinGradleIssue], auto_apply: bool = False
    ) -> List[KotlinGradleFix]:
        """Generate and optionally apply fixes for detected issues."""
        fixes = []

        for issue in issues:
            fix = self._create_fix_for_issue(issue)
            if fix:
                fixes.append(fix)

                if (
                    auto_apply
                    and fix.risk_level == "low"
                    and not fix.requires_user_input
                ):
                    self._apply_fix(fix)

        return fixes

    def _create_fix_for_issue(
        self, issue: KotlinGradleIssue
    ) -> Optional[KotlinGradleFix]:
        """Create appropriate fix for a specific issue."""

        if issue.issue_type == "version_compatibility":
            return self._fix_version_compatibility(issue)
        elif issue.issue_type == "version_mismatch":
            return self._fix_version_mismatch(issue)
        elif issue.issue_type == "version_conflict":
            return self._fix_version_conflict(issue)
        elif issue.issue_type == "configuration_inconsistency":
            return self._fix_configuration_inconsistency(issue)
        elif issue.issue_type == "configuration_conflict":
            return self._fix_configuration_conflict(issue)
        elif issue.issue_type == "best_practice":
            return self._suggest_best_practice_improvement(issue)
        else:
            return self._create_generic_fix(issue)

    def _fix_version_compatibility(self, issue: KotlinGradleIssue) -> KotlinGradleFix:
        """Fix version compatibility issues."""

        if "Kotlin-Gradle" in issue.title:
            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Fix Kotlin-Gradle Compatibility",
                description="Update versions to compatible range",
                actions=[
                    {
                        "type": "update_gradle_wrapper",
                        "target_version": "8.5",
                        "reason": "Compatible with most Kotlin versions",
                    },
                    {
                        "type": "update_build_file",
                        "file": "build.gradle.kts",
                        "changes": [
                            {
                                "pattern": r'kotlin\("jvm"\)\s+version\s+"[^"]+"',
                                "replacement": 'kotlin("jvm") version "1.9.20"',
                                "description": "Update Kotlin version to stable compatible version",
                            }
                        ],
                    },
                ],
                risk_level="medium",
                validation_command="./gradlew --version && ./gradlew tasks",
            )

        elif "Gradle-Java" in issue.title:
            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Fix Gradle-Java Compatibility",
                description="Update Java or Gradle to compatible versions",
                actions=[
                    {
                        "type": "manual_instruction",
                        "instruction": "Install compatible Java version using your version manager",
                        "commands": [
                            "# Using SDKMAN:",
                            "sdk install java 17.0.8-tem",
                            "sdk use java 17.0.8-tem",
                            "",
                            "# Using Homebrew (macOS):",
                            "brew install openjdk@17",
                            "",
                            "# Or update Gradle wrapper:",
                            "./gradlew wrapper --gradle-version 8.5",
                        ],
                    }
                ],
                risk_level="medium",
                requires_user_input=True,
            )

        return self._create_generic_fix(issue)

    def _fix_version_mismatch(self, issue: KotlinGradleIssue) -> KotlinGradleFix:
        """Fix version mismatch issues."""

        if "Kotlin Plugin and Stdlib" in issue.title:
            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Align Kotlin Plugin and Stdlib Versions",
                description="Update stdlib version to match plugin version",
                actions=[
                    {
                        "type": "update_build_file",
                        "file": "build.gradle.kts",
                        "changes": [
                            {
                                "pattern": r'implementation\s*\(\s*"org\.jetbrains\.kotlin:kotlin-stdlib:[^"]+"\s*\)',
                                "replacement": 'implementation("org.jetbrains.kotlin:kotlin-stdlib")',
                                "description": "Remove explicit stdlib version (use BOM)",
                            }
                        ],
                    },
                    {
                        "type": "add_bom",
                        "bom": "org.jetbrains.kotlin:kotlin-bom",
                        "reason": "Ensures consistent Kotlin library versions",
                    },
                ],
                risk_level="low",
                validation_command="./gradlew dependencies --configuration compileClasspath",
            )

        elif "Wrapper Version" in issue.title:
            # Extract target version from the fix suggestion
            version_match = re.search(
                r"--gradle-version\s+([0-9.]+)", issue.fix_suggestion or ""
            )
            target_version = version_match.group(1) if version_match else "8.5"

            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Update Gradle Wrapper Version",
                description=f"Update wrapper to version {target_version}",
                actions=[
                    {
                        "type": "run_command",
                        "command": f"./gradlew wrapper --gradle-version {target_version}",
                        "description": f"Update Gradle wrapper to {target_version}",
                    }
                ],
                risk_level="low",
                validation_command="./gradlew --version",
            )

        return self._create_generic_fix(issue)

    def _fix_version_conflict(self, issue: KotlinGradleIssue) -> KotlinGradleFix:
        """Fix version conflict issues."""

        if "kotlinx-coroutines" in issue.title.lower():
            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Fix Kotlinx Coroutines Version Conflicts",
                description="Align all coroutines dependencies to same version",
                actions=[
                    {
                        "type": "update_build_file",
                        "file": "build.gradle.kts",
                        "changes": [
                            {
                                "pattern": r'implementation\s*\(\s*"org\.jetbrains\.kotlinx:kotlinx-coroutines-[^:]+:[^"]+"\s*\)',
                                "replacement_callback": self._standardize_coroutines_version,
                                "description": "Standardize coroutines versions",
                            }
                        ],
                    },
                    {
                        "type": "suggest_version_catalog",
                        "reason": "Prevent future version conflicts",
                    },
                ],
                risk_level="low",
            )

        # Generic dependency version conflict
        return KotlinGradleFix(
            issue_type=issue.issue_type,
            title="Resolve Dependency Version Conflicts",
            description="Use dependency resolution strategy or BOM",
            actions=[
                {
                    "type": "add_resolution_strategy",
                    "strategy": "force_versions",
                    "reason": "Resolve version conflicts",
                },
                {
                    "type": "manual_instruction",
                    "instruction": "Consider using a BOM (Bill of Materials) for consistent versions",
                },
            ],
            risk_level="medium",
            requires_user_input=True,
        )

    def _fix_configuration_inconsistency(
        self, issue: KotlinGradleIssue
    ) -> KotlinGradleFix:
        """Fix configuration inconsistency issues."""

        if "Java Version" in issue.title:
            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Align Java Version Configuration",
                description="Standardize Java version across all configurations",
                actions=[
                    {
                        "type": "update_build_file",
                        "file": "build.gradle.kts",
                        "changes": [
                            {
                                "pattern": r"java\s*\{[^}]*\}",
                                "replacement": """java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}""",
                                "description": "Use modern Java toolchain configuration",
                            },
                            {
                                "pattern": r"kotlin\s*\{[^}]*jvmToolchain\([^)]*\)[^}]*\}",
                                "replacement": """kotlin {
    jvmToolchain(17)
}""",
                                "description": "Align Kotlin toolchain with Java",
                            },
                        ],
                    }
                ],
                risk_level="low",
                validation_command="./gradlew build --dry-run",
            )

        return self._create_generic_fix(issue)

    def _fix_configuration_conflict(self, issue: KotlinGradleIssue) -> KotlinGradleFix:
        """Fix configuration conflict issues."""

        if "KAPT and KSP" in issue.title:
            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Migrate KAPT to KSP",
                description="Replace KAPT processors with KSP where possible",
                actions=[
                    {
                        "type": "manual_instruction",
                        "instruction": "Review annotation processors and migrate to KSP",
                        "details": [
                            "1. Check if your annotation processors support KSP",
                            "2. Replace kapt() configurations with ksp()",
                            "3. Remove kapt plugin if no longer needed",
                            "4. Test build to ensure everything works",
                        ],
                    },
                    {
                        "type": "update_build_file",
                        "file": "build.gradle.kts",
                        "changes": [
                            {
                                "pattern": r'kapt\s*\(\s*"([^"]+)"\s*\)',
                                "replacement": r'ksp("\1")',
                                "description": "Replace kapt with ksp (manual review required)",
                            }
                        ],
                    },
                ],
                risk_level="high",
                requires_user_input=True,
            )

        return self._create_generic_fix(issue)

    def _suggest_best_practice_improvement(
        self, issue: KotlinGradleIssue
    ) -> KotlinGradleFix:
        """Suggest best practice improvements."""

        if "Version Catalogs" in issue.title:
            return KotlinGradleFix(
                issue_type=issue.issue_type,
                title="Migrate to Gradle Version Catalogs",
                description="Create version catalog for centralized dependency management",
                actions=[
                    {
                        "type": "create_version_catalog",
                        "file": "gradle/libs.versions.toml",
                        "content": self._generate_version_catalog_content(),
                    },
                    {
                        "type": "update_build_file",
                        "file": "build.gradle.kts",
                        "changes": [
                            {
                                "pattern": r'implementation\s*\(\s*"([^:]+):([^:]+):([^"]+)"\s*\)',
                                "replacement_callback": self._convert_to_catalog_reference,
                                "description": "Convert hardcoded dependencies to catalog references",
                            }
                        ],
                    },
                ],
                risk_level="medium",
                backup_files=["build.gradle.kts", "build.gradle"],
            )

        return self._create_generic_fix(issue)

    def _create_generic_fix(self, issue: KotlinGradleIssue) -> KotlinGradleFix:
        """Create a generic fix for unhandled issues."""
        return KotlinGradleFix(
            issue_type=issue.issue_type,
            title=f"Manual Fix Required: {issue.title}",
            description=issue.description,
            actions=[
                {
                    "type": "manual_instruction",
                    "instruction": issue.fix_suggestion
                    or "Manual intervention required",
                    "documentation": issue.documentation_url,
                }
            ],
            risk_level="high",
            requires_user_input=True,
        )

    def _apply_fix(self, fix: KotlinGradleFix) -> bool:
        """Apply a fix to the project."""
        try:
            # Create backup if needed
            if fix.backup_files:
                self._create_backup(fix.backup_files)

            success = True
            for action in fix.actions:
                if not self._apply_action(action):
                    success = False
                    break

            # Validate fix if command provided
            if success and fix.validation_command:
                if not self._validate_fix(fix.validation_command):
                    success = False

            return success

        except Exception as e:
            print(f"Error applying fix: {e}")
            return False

    def _apply_action(self, action: Dict[str, Any]) -> bool:
        """Apply a specific fix action."""
        action_type = action.get("type")

        if action_type == "update_build_file":
            return self._update_build_file(action)
        elif action_type == "run_command":
            return self._run_command(action)
        elif action_type == "create_version_catalog":
            return self._create_version_catalog_file(action)
        elif action_type == "update_gradle_wrapper":
            return self._update_gradle_wrapper(action)
        elif action_type == "add_bom":
            return self._add_bom_to_build(action)
        elif action_type == "add_resolution_strategy":
            return self._add_resolution_strategy(action)
        elif action_type == "manual_instruction":
            # Manual instructions are just printed, not executed
            self._print_manual_instruction(action)
            return True
        else:
            print(f"Unknown action type: {action_type}")
            return False

    def _update_build_file(self, action: Dict[str, Any]) -> bool:
        """Update build file with specified changes."""
        file_path = self.project_path / action["file"]
        if not file_path.exists():
            return False

        try:
            content = file_path.read_text()
            modified = False

            for change in action["changes"]:
                pattern = change["pattern"]

                if "replacement" in change:
                    new_content = re.sub(pattern, change["replacement"], content)
                    if new_content != content:
                        content = new_content
                        modified = True
                        print(f"✓ {change['description']}")
                elif "replacement_callback" in change:
                    # Handle callback-based replacements
                    callback = change["replacement_callback"]
                    new_content = re.sub(pattern, callback, content)
                    if new_content != content:
                        content = new_content
                        modified = True
                        print(f"✓ {change['description']}")

            if modified:
                file_path.write_text(content)
                return True
            else:
                print(f"No changes needed in {action['file']}")
                return True

        except Exception as e:
            print(f"Error updating {action['file']}: {e}")
            return False

    def _run_command(self, action: Dict[str, Any]) -> bool:
        """Run a shell command."""
        try:
            command = action["command"]
            print(f"Running: {command}")

            result = subprocess.run(
                command.split(),
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print(f"✓ {action.get('description', 'Command executed successfully')}")
                return True
            else:
                print(f"✗ Command failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("✗ Command timed out")
            return False
        except Exception as e:
            print(f"✗ Error running command: {e}")
            return False

    def _create_version_catalog_file(self, action: Dict[str, Any]) -> bool:
        """Create a version catalog file."""
        try:
            file_path = self.project_path / action["file"]
            file_path.parent.mkdir(parents=True, exist_ok=True)

            content = action.get("content", "")
            if callable(content):
                content = content()

            file_path.write_text(content)
            print(f"✓ Created {action['file']}")
            return True

        except Exception as e:
            print(f"✗ Error creating version catalog: {e}")
            return False

    def _update_gradle_wrapper(self, action: Dict[str, Any]) -> bool:
        """Update Gradle wrapper version."""
        return self._run_command(
            {
                "command": f"./gradlew wrapper --gradle-version {action['target_version']}",
                "description": f"Updated Gradle wrapper to {action['target_version']}",
            }
        )

    def _add_bom_to_build(self, action: Dict[str, Any]) -> bool:
        """Add BOM to build file."""
        build_file = self.project_path / "build.gradle.kts"
        if not build_file.exists():
            return False

        try:
            content = build_file.read_text()
            bom_line = f'    implementation(platform("{action["bom"]}"))'

            # Find dependencies block and add BOM
            dependencies_match = re.search(r"dependencies\s*\{", content)
            if dependencies_match:
                insert_pos = dependencies_match.end()
                content = content[:insert_pos] + f"\n{bom_line}" + content[insert_pos:]
                build_file.write_text(content)
                print(f"✓ Added BOM: {action['bom']}")
                return True
            else:
                print("✗ Could not find dependencies block")
                return False

        except Exception as e:
            print(f"✗ Error adding BOM: {e}")
            return False

    def _add_resolution_strategy(self, action: Dict[str, Any]) -> bool:
        """Add dependency resolution strategy."""
        # This would add resolution strategy to build file
        # Implementation depends on specific strategy type
        print("ⓘ Resolution strategy addition requires manual implementation")
        return True

    def _print_manual_instruction(self, action: Dict[str, Any]):
        """Print manual instruction for user."""
        print(f"📋 Manual Action Required:")
        print(f"   {action['instruction']}")

        if "commands" in action:
            print("   Suggested commands:")
            for cmd in action["commands"]:
                print(f"   {cmd}")

        if "details" in action:
            print("   Details:")
            for detail in action["details"]:
                print(f"   {detail}")

        if "documentation" in action and action["documentation"]:
            print(f"   📖 Documentation: {action['documentation']}")

    def _validate_fix(self, command: str) -> bool:
        """Validate a fix by running a command."""
        try:
            result = subprocess.run(
                command.split(),
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except:
            return False

    def _create_backup(self, files: List[str]):
        """Create backup of specified files."""
        if not self.backup_dir:
            self.backup_dir = Path(tempfile.mkdtemp(prefix="sds_backup_"))

        for file_path in files:
            source = self.project_path / file_path
            if source.exists():
                dest = self.backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                print(f"📋 Backed up {file_path}")

    def _generate_version_catalog_content(self) -> str:
        """Generate version catalog content based on current build file."""
        # This would analyze current dependencies and create a version catalog
        # For now, return a basic template
        return """[versions]
kotlin = "1.9.20"
spring-boot = "3.2.0"

[libraries]
kotlin-stdlib = { group = "org.jetbrains.kotlin", name = "kotlin-stdlib", version.ref = "kotlin" }
spring-boot-starter-web = { group = "org.springframework.boot", name = "spring-boot-starter-web" }

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }

[bundles]
kotlin-core = ["kotlin-stdlib"]
"""

    def _standardize_coroutines_version(self, match) -> str:
        """Callback to standardize coroutines version."""
        # Extract dependency and use standard version
        return match.group(0).replace(
            match.group(0).split(":")[-1].rstrip('")'), '1.7.3")'
        )

    def _convert_to_catalog_reference(self, match) -> str:
        """Convert hardcoded dependency to catalog reference."""
        # This would convert "group:name:version" to libs.name.reference
        # Simplified implementation
        parts = match.group(0).split(":")
        if len(parts) >= 2:
            name = parts[1].replace("-", ".")
            return f"libs.{name}"
        return match.group(0)

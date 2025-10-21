"""
Android Kotlin Specific Issue Detector

This module provides specialized detection for Android Kotlin projects,
focusing on dependency injection conflicts, annotation processor performance,
and Android-specific build configuration issues with live version checking.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
import toml
import json

try:
    from .maven_central_client import LiveVersionChecker, MavenCentralClient

    LIVE_VERSION_CHECK_AVAILABLE = True
except ImportError:
    LIVE_VERSION_CHECK_AVAILABLE = False


@dataclass
class AndroidKotlinIssue:
    """Represents a specific Android Kotlin issue."""

    issue_type: str
    severity: str  # "critical", "error", "warning", "info"
    title: str
    description: str
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    fix_suggestion: Optional[str] = None
    performance_impact: Optional[str] = None
    migration_guide: Optional[str] = None


class AndroidKotlinDetector:
    """Specialized detector for Android Kotlin projects."""

    # Known dependency injection frameworks and their identifiers
    DEPENDENCY_INJECTION_FRAMEWORKS = {
        "hilt": {
            "dependencies": ["com.google.dagger:hilt-android", "androidx.hilt:hilt-"],
            "processors": ["com.google.dagger:hilt-compiler"],
            "plugins": ["dagger.hilt.android.plugin"],
            "annotations": ["@HiltAndroidApp", "@AndroidEntryPoint", "@Inject"],
        },
        "koin": {
            "dependencies": ["io.insert-koin:koin-", "org.koin:koin-"],
            "processors": [],
            "plugins": [],
            "annotations": ["by inject()", "by viewModel()"],
        },
        "dagger": {
            "dependencies": ["com.google.dagger:dagger"],
            "processors": ["com.google.dagger:dagger-compiler"],
            "plugins": [],
            "annotations": ["@Component", "@Module", "@Provides"],
        },
    }

    # KAPT vs KSP processor mapping
    PROCESSOR_MIGRATIONS = {
        "androidx.room:room-compiler": {
            "kapt_to_ksp": True,
            "performance_gain": "30-50% faster compilation",
            "min_version": "2.4.0",
        },
        "com.google.dagger:hilt-compiler": {
            "kapt_to_ksp": True,
            "performance_gain": "20-30% faster compilation",
            "min_version": "2.44",
        },
        "com.github.bumptech.glide:compiler": {
            "kapt_to_ksp": True,
            "performance_gain": "25% faster compilation",
            "min_version": "4.14.0",
        },
        "androidx.databinding:databinding-compiler": {
            "kapt_to_ksp": False,
            "note": "Consider migrating from DataBinding to Compose",
        },
    }

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.issues: List[AndroidKotlinIssue] = []

        # Parse build files
        self.build_gradle_kts = self._parse_build_gradle_kts()
        self.build_gradle = self._parse_build_gradle()

        # Initialize live version checker if available
        if LIVE_VERSION_CHECK_AVAILABLE:
            try:
                self.live_checker = LiveVersionChecker()
            except Exception:
                self.live_checker = None
        else:
            self.live_checker = None

        # Detect if project uses Compose
        self.has_compose = self._detect_compose_usage()

        # Analyze project structure
        self.has_android_manifest = (
            self.project_path / "src" / "main" / "AndroidManifest.xml"
        ).exists()
        self.has_compose = self._detect_compose_usage()

    def detect_all_issues(self) -> List[AndroidKotlinIssue]:
        """Run all Android Kotlin specific detections."""
        self.issues.clear()

        # Core Android Kotlin issues
        self._check_dependency_injection_conflicts()
        self._check_annotation_processor_performance()
        self._check_android_version_conflicts()
        self._check_kotlin_android_version_alignment()

        # Build configuration issues
        self._check_java_version_consistency()
        self._check_compose_configuration()
        self._check_build_feature_conflicts()

        # Performance and best practices
        self._check_kapt_configuration()
        self._check_dependency_version_conflicts()
        self._check_unused_processors()

        # Live version checking (if available)
        if self.live_checker:
            self._check_live_version_issues()

        return self.issues

    def _parse_build_gradle_kts(self) -> Optional[Dict[str, Any]]:
        """Parse Android build.gradle.kts file."""
        build_file = self.project_path / "build.gradle.kts"
        if not build_file.exists():
            return None

        content = build_file.read_text()

        # Extract plugins
        plugins = []
        plugin_patterns = [
            r'id\("([^"]+)"\)',
            r'kotlin\("([^"]+)"\)',
            r'"([^"]*kapt)"',
            r'"([^"]*ksp)"',
        ]

        for pattern in plugin_patterns:
            plugins.extend(re.findall(pattern, content))

        # Extract dependencies
        dependencies = {
            "implementation": [],
            "kapt": [],
            "ksp": [],
            "androidTestImplementation": [],
        }

        # Find dependencies block
        deps_match = re.search(r"dependencies\s*\{(.*?)\n\}", content, re.DOTALL)
        if deps_match:
            deps_content = deps_match.group(1)

            # Extract different types of dependencies
            for dep_type in dependencies.keys():
                pattern = rf'{dep_type}\s*\(["\']([^"\']+)["\']'
                matches = re.findall(pattern, deps_content)
                dependencies[dep_type].extend(matches)

        # Extract Android configuration
        android_config = {}
        android_match = re.search(r"android\s*\{(.*?)\n\}", content, re.DOTALL)
        if android_match:
            android_content = android_match.group(1)

            # Extract compile SDK
            compile_sdk = re.search(r"compileSdk\s*=\s*(\d+)", android_content)
            if compile_sdk:
                android_config["compile_sdk"] = int(compile_sdk.group(1))

            # Extract Java compatibility
            java_source = re.search(
                r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\w+)", android_content
            )
            java_target = re.search(
                r"targetCompatibility\s*=\s*JavaVersion\.VERSION_(\w+)", android_content
            )
            jvm_target = re.search(r'jvmTarget\s*=\s*"([^"]+)"', android_content)

            if java_source:
                android_config["source_compatibility"] = java_source.group(1)
            if java_target:
                android_config["target_compatibility"] = java_target.group(1)
            if jvm_target:
                android_config["jvm_target"] = jvm_target.group(1)

            # Check build features
            compose_enabled = "compose = true" in android_content
            databinding_enabled = "dataBinding = true" in android_content
            viewbinding_enabled = "viewBinding = true" in android_content

            android_config["build_features"] = {
                "compose": compose_enabled,
                "databinding": databinding_enabled,
                "viewbinding": viewbinding_enabled,
            }

        return {
            "plugins": plugins,
            "dependencies": dependencies,
            "android_config": android_config,
            "content": content,
        }

    def _parse_build_gradle(self) -> Optional[Dict[str, Any]]:
        """Parse Android build.gradle file (Groovy)."""
        build_file = self.project_path / "build.gradle"
        if not build_file.exists():
            return None

        content = build_file.read_text()
        return {"content": content}

    def _check_live_version_issues(self):
        """Check for version issues using live repository data."""
        if not self.build_gradle_kts or not self.live_checker:
            return

        build_file = self.project_path / "build.gradle.kts"
        if not build_file.exists():
            return

        try:
            content = build_file.read_text()

            # Get real version conflicts
            conflicts = self.live_checker.get_real_version_conflicts(content)

            for conflict in conflicts:
                if conflict["type"] == "outdated_dependency":
                    severity = (
                        "warning" if conflict["severity"] == "warning" else "info"
                    )
                    self.issues.append(
                        AndroidKotlinIssue(
                            issue_type="live_version_check",
                            severity=severity,
                            title=f"Outdated Dependency: {conflict['dependency']}",
                            description=f"Using {conflict['current_version']} but {conflict['latest_version']} is available from Maven Central",
                            current_value=f"Version: {conflict['current_version']}",
                            expected_value=f"Latest: {conflict['latest_version']}",
                            file_path="build.gradle.kts",
                            fix_suggestion=f"Update to latest version: {conflict['latest_version']}",
                        )
                    )
                elif conflict["type"] == "version_not_found":
                    self.issues.append(
                        AndroidKotlinIssue(
                            issue_type="live_version_check",
                            severity="error",
                            title=f"Version Not Found: {conflict['dependency']}",
                            description=f"Version {conflict['requested_version']} not found in repositories",
                            current_value=f"Requested: {conflict['requested_version']}",
                            expected_value=f"Closest match: {conflict.get('closest_match', 'N/A')}",
                            file_path="build.gradle.kts",
                            fix_suggestion=f"Use available version: {conflict.get('closest_match', 'check repository')}",
                        )
                    )

            # Check Kotlin-Gradle compatibility with live data
            kotlin_version = self._extract_kotlin_version(content)
            gradle_version = self._extract_gradle_version()

            if kotlin_version and gradle_version:
                compatibility = self.live_checker.kotlin_gradle_client.check_kotlin_gradle_compatibility(
                    kotlin_version, gradle_version
                )

                if not compatibility["compatible"]:
                    self.issues.append(
                        AndroidKotlinIssue(
                            issue_type="live_compatibility_check",
                            severity="error",
                            title="Live Kotlin-Gradle Compatibility Issue",
                            description="; ".join(compatibility["issues"]),
                            current_value=f"Kotlin {kotlin_version}, Gradle {gradle_version}",
                            expected_value="; ".join(compatibility["recommendations"]),
                            file_path="build.gradle.kts",
                            fix_suggestion="; ".join(compatibility["recommendations"]),
                        )
                    )

        except Exception as e:
            # Silently skip live checking if it fails
            pass

    def _extract_kotlin_version(self, content: str) -> Optional[str]:
        """Extract Kotlin version from build.gradle.kts content."""
        kotlin_match = re.search(r'kotlin.*version\s+"([^"]+)"', content)
        return kotlin_match.group(1) if kotlin_match else None

    def _extract_gradle_version(self) -> Optional[str]:
        """Extract Gradle version from wrapper properties."""
        wrapper_file = (
            self.project_path / "gradle" / "wrapper" / "gradle-wrapper.properties"
        )
        if wrapper_file.exists():
            try:
                content = wrapper_file.read_text()
                gradle_match = re.search(r"gradle-([0-9.]+)-", content)
                return gradle_match.group(1) if gradle_match else None
            except Exception:
                pass
        return None

    def _detect_compose_usage(self) -> bool:
        """Detect if project uses Jetpack Compose."""
        if not self.build_gradle_kts:
            return False

        compose_deps = ["androidx.compose", "compose-bom", "activity-compose"]

        all_deps = []
        for dep_list in self.build_gradle_kts["dependencies"].values():
            all_deps.extend(dep_list)

        return any(dep in " ".join(all_deps) for dep in compose_deps)

    def _check_dependency_injection_conflicts(self):
        """Check for conflicts between dependency injection frameworks."""
        if not self.build_gradle_kts:
            return

        detected_frameworks = []
        all_dependencies = []
        for dep_list in self.build_gradle_kts["dependencies"].values():
            all_dependencies.extend(dep_list)

        # Check for each dependency injection framework
        for (
            framework_name,
            framework_info,
        ) in self.DEPENDENCY_INJECTION_FRAMEWORKS.items():
            for dep_pattern in framework_info["dependencies"]:
                if any(dep_pattern in dep for dep in all_dependencies):
                    detected_frameworks.append(framework_name)
                    break

        # If multiple dependency injection frameworks detected, it's a critical issue
        if len(detected_frameworks) > 1:
            self.issues.append(
                AndroidKotlinIssue(
                    issue_type="dependency_injection_conflict",
                    severity="critical",
                    title="Conflicting Dependency Injection Framework Configuration",
                    description=f"Project uses multiple dependency injection frameworks ({', '.join(detected_frameworks)}). This creates conflicting runtime behavior and potential application instability.",
                    current_value=f"Active frameworks: {', '.join(detected_frameworks)}",
                    expected_value="Single dependency injection framework per project",
                    file_path="build.gradle.kts",
                    fix_suggestion=f"Standardize on a single dependency injection framework. For Android projects, Hilt provides optimal integration with the Android ecosystem.",
                    performance_impact="Application instability, increased binary size, degraded startup performance",
                )
            )

    def _check_annotation_processor_performance(self):
        """Check for KAPT usage that could be migrated to KSP for better performance."""
        if not self.build_gradle_kts:
            return

        kapt_processors = self.build_gradle_kts["dependencies"].get("kapt", [])
        ksp_processors = self.build_gradle_kts["dependencies"].get("ksp", [])

        migration_opportunities = []

        for kapt_dep in kapt_processors:
            # Extract group:artifact from dependency
            dep_parts = kapt_dep.split(":")
            if len(dep_parts) >= 2:
                group_artifact = f"{dep_parts[0]}:{dep_parts[1]}"

                if group_artifact in self.PROCESSOR_MIGRATIONS:
                    migration_info = self.PROCESSOR_MIGRATIONS[group_artifact]
                    if migration_info.get("kapt_to_ksp", False):
                        migration_opportunities.append(
                            {
                                "processor": group_artifact,
                                "performance_gain": migration_info.get(
                                    "performance_gain", "20-30% faster"
                                ),
                                "min_version": migration_info.get(
                                    "min_version", "latest"
                                ),
                            }
                        )

        if migration_opportunities:
            processors_list = ", ".join(
                [m["processor"] for m in migration_opportunities]
            )
            total_gain = "30-50% faster compilation overall"

            self.issues.append(
                AndroidKotlinIssue(
                    issue_type="annotation_processor_performance",
                    severity="warning",
                    title="Annotation Processors Using Legacy KAPT Implementation",
                    description=f"Project uses {len(migration_opportunities)} annotation processors that support Kotlin Symbol Processing (KSP) for improved build performance.",
                    current_value=f"Legacy KAPT processors: {processors_list}",
                    expected_value="Modern KSP annotation processing for optimal build performance",
                    file_path="build.gradle.kts",
                    fix_suggestion="Migrate annotation processors from KAPT to KSP implementation",
                    performance_impact=f"Expected improvement: {total_gain}",
                    migration_guide="1. Replace kapt() declarations with ksp() equivalents\n2. Verify processor version compatibility with KSP\n3. Remove kapt plugin configuration if no longer required",
                )
            )

    def _check_android_version_conflicts(self):
        """Check for Android-specific version conflicts."""
        if not self.build_gradle_kts:
            return

        all_deps = []
        for dep_list in self.build_gradle_kts["dependencies"].values():
            all_deps.extend(dep_list)

        # Check for Navigation component version conflicts
        nav_deps = [dep for dep in all_deps if "androidx.navigation" in dep]
        nav_versions = set()

        for dep in nav_deps:
            parts = dep.split(":")
            if len(parts) >= 3:
                version = parts[2]
                nav_versions.add(version)

        if len(nav_versions) > 1:
            self.issues.append(
                AndroidKotlinIssue(
                    issue_type="version_conflict",
                    severity="error",
                    title="Navigation Component Version Conflict",
                    description="Different versions of Navigation components detected",
                    current_value=f"Versions: {', '.join(sorted(nav_versions))}",
                    expected_value="All Navigation dependencies should use same version",
                    file_path="build.gradle.kts",
                    fix_suggestion="Align all androidx.navigation dependencies to same version",
                )
            )

        # Check for Compose BOM version conflicts
        compose_bom_deps = [dep for dep in all_deps if "compose-bom" in dep]
        if len(compose_bom_deps) > 1:
            bom_versions = [dep.split(":")[-1] for dep in compose_bom_deps]
            if len(set(bom_versions)) > 1:
                self.issues.append(
                    AndroidKotlinIssue(
                        issue_type="version_conflict",
                        severity="warning",
                        title="Multiple Compose BOM Versions",
                        description="Different Compose BOM versions found between main and test dependencies",
                        current_value=f"BOM versions: {', '.join(bom_versions)}",
                        expected_value="Use same BOM version across all configurations",
                        file_path="build.gradle.kts",
                        fix_suggestion="Standardize on single Compose BOM version",
                    )
                )

    def _check_kotlin_android_version_alignment(self):
        """Verify Kotlin version alignment with Android Gradle Plugin requirements."""
        if not self.build_gradle_kts:
            return

        kotlin_version = None
        for plugin in self.build_gradle_kts["plugins"]:
            if "kotlin.android" in plugin:
                # Extract version if specified
                version_match = re.search(r'version "([^"]+)"', plugin)
                if version_match:
                    kotlin_version = version_match.group(1)
                break

        # Verify Kotlin standard library version alignment
        kotlin_stdlib_deps = [
            dep
            for dep in self.build_gradle_kts["dependencies"].get("implementation", [])
            if "kotlin-stdlib" in dep
        ]

        if kotlin_version and kotlin_stdlib_deps:
            stdlib_versions = []
            for dep in kotlin_stdlib_deps:
                parts = dep.split(":")
                if len(parts) >= 3:
                    stdlib_versions.append(parts[2])

            if stdlib_versions and kotlin_version not in stdlib_versions[0]:
                self.issues.append(
                    AndroidKotlinIssue(
                        issue_type="version_mismatch",
                        severity="error",
                        title="Kotlin Plugin and Standard Library Version Misalignment",
                        description="Kotlin Gradle plugin version is inconsistent with standard library dependency version",
                        current_value=f"Plugin: {kotlin_version}, Stdlib: {stdlib_versions[0]}",
                        expected_value=f"Both should be {kotlin_version}",
                        file_path="build.gradle.kts",
                        fix_suggestion=f"Align kotlin-stdlib dependency to match plugin version {kotlin_version}",
                    )
                )

    def _check_java_version_consistency(self):
        """Check for Java version consistency in Android configuration."""
        if not self.build_gradle_kts or not self.build_gradle_kts.get("android_config"):
            return

        android_config = self.build_gradle_kts["android_config"]

        source_compat = android_config.get("source_compatibility")
        target_compat = android_config.get("target_compatibility")
        jvm_target = android_config.get("jvm_target")

        versions = {
            "sourceCompatibility": source_compat,
            "targetCompatibility": target_compat,
            "kotlinOptions.jvmTarget": jvm_target,
        }

        # Remove None values
        versions = {k: v for k, v in versions.items() if v}

        if len(set(versions.values())) > 1:
            self.issues.append(
                AndroidKotlinIssue(
                    issue_type="configuration_inconsistency",
                    severity="warning",
                    title="Inconsistent Java Version Configuration",
                    description="Different Java versions configured across Android build settings",
                    current_value=", ".join(f"{k}: {v}" for k, v in versions.items()),
                    expected_value="All Java version settings should match",
                    file_path="build.gradle.kts",
                    fix_suggestion="Align sourceCompatibility, targetCompatibility, and kotlinOptions.jvmTarget to same version",
                )
            )

    def _check_compose_configuration(self):
        """Check Compose-specific configuration issues."""
        if not self.has_compose or not self.build_gradle_kts:
            return

        android_config = self.build_gradle_kts.get("android_config", {})
        build_features = android_config.get("build_features", {})

        # Check for DataBinding + Compose conflict
        if build_features.get("compose") and build_features.get("databinding"):
            self.issues.append(
                AndroidKotlinIssue(
                    issue_type="build_feature_conflict",
                    severity="warning",
                    title="Compose and DataBinding Both Enabled",
                    description="Using both Compose and DataBinding increases build time and APK size",
                    current_value="compose = true, dataBinding = true",
                    expected_value="Use either Compose OR DataBinding",
                    file_path="build.gradle.kts",
                    fix_suggestion="Migrate from DataBinding to Compose for better performance",
                    performance_impact="Slower builds, larger APK size, conflicting UI paradigms",
                )
            )

    def _check_build_feature_conflicts(self):
        """Check for conflicting build features."""
        # Implemented in _check_compose_configuration for now
        pass

    def _check_kapt_configuration(self):
        """Check KAPT configuration for performance issues."""
        if not self.build_gradle_kts:
            return

        content = self.build_gradle_kts["content"]

        # Check for performance-hurting KAPT configurations
        if "useBuildCache = false" in content:
            self.issues.append(
                AndroidKotlinIssue(
                    issue_type="performance_configuration",
                    severity="info",
                    title="KAPT Build Cache Disabled",
                    description="KAPT build cache is disabled, slowing down builds",
                    current_value="useBuildCache = false",
                    expected_value="useBuildCache = true",
                    file_path="build.gradle.kts",
                    fix_suggestion="Enable KAPT build cache for faster incremental builds",
                    performance_impact="Slower incremental builds",
                )
            )

    def _check_dependency_version_conflicts(self):
        """Check for dependency version conflicts in related libraries."""
        if not self.build_gradle_kts:
            return

        all_deps = []
        for dep_list in self.build_gradle_kts["dependencies"].values():
            all_deps.extend(dep_list)

        # Group dependencies by group:artifact
        dep_groups = {}
        for dep in all_deps:
            parts = dep.split(":")
            if len(parts) >= 3:
                key = f"{parts[0]}:{parts[1]}"
                version = parts[2]
                if key not in dep_groups:
                    dep_groups[key] = []
                dep_groups[key].append(version)

        # Check for version conflicts
        for dep_name, versions in dep_groups.items():
            unique_versions = set(versions)
            if len(unique_versions) > 1:
                # Special handling for known problematic conflicts
                if any(
                    framework in dep_name.lower()
                    for framework in ["okhttp", "retrofit", "coroutines"]
                ):
                    severity = "error"
                else:
                    severity = "warning"

                self.issues.append(
                    AndroidKotlinIssue(
                        issue_type="version_conflict",
                        severity=severity,
                        title=f"Version Conflict: {dep_name}",
                        description=f"Multiple versions of {dep_name} detected",
                        current_value=f"Versions: {', '.join(sorted(unique_versions))}",
                        expected_value="Single version across all dependencies",
                        file_path="build.gradle.kts",
                        fix_suggestion="Align all versions or use BOM for version management",
                    )
                )

    def _check_unused_processors(self):
        """Check for unused annotation processors."""
        if not self.build_gradle_kts:
            return

        plugins = self.build_gradle_kts.get("plugins", [])
        kapt_deps = self.build_gradle_kts["dependencies"].get("kapt", [])
        ksp_deps = self.build_gradle_kts["dependencies"].get("ksp", [])

        # Check if KSP plugin is declared but no KSP processors used
        has_ksp_plugin = any("ksp" in plugin for plugin in plugins)
        if has_ksp_plugin and not ksp_deps and kapt_deps:
            self.issues.append(
                AndroidKotlinIssue(
                    issue_type="unused_configuration",
                    severity="info",
                    title="KSP Plugin Declared But Unused",
                    description="KSP plugin is declared but all processors use KAPT",
                    current_value="KSP plugin present, but using KAPT processors",
                    expected_value="Either use KSP processors or remove KSP plugin",
                    file_path="build.gradle.kts",
                    fix_suggestion="Migrate KAPT processors to KSP or remove unused KSP plugin",
                )
            )

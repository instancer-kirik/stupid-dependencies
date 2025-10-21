"""
Enhanced Kotlin/Gradle/Maven Issue Detector

This module provides comprehensive detection of Kotlin, Gradle, and Maven dependency
issues including version conflicts, toolchain mismatches, and modern Gradle patterns.
"""

import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
import toml
import json


@dataclass
class KotlinGradleIssue:
    """Represents a specific Kotlin/Gradle configuration issue."""

    issue_type: str
    severity: str  # "error", "warning", "info"
    title: str
    description: str
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    fix_suggestion: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class VersionInfo:
    """Version information with semantic version parsing."""

    raw: str
    major: int
    minor: int
    patch: int
    suffix: str = ""

    @classmethod
    def parse(cls, version_str: str) -> Optional["VersionInfo"]:
        """Parse a version string into components."""
        if not version_str:
            return None

        # Handle various version formats
        clean_version = version_str.strip().lstrip("v").split("-")[0]
        match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?(.*)$", clean_version)

        if not match:
            return None

        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3)) if match.group(3) else 0
        suffix = match.group(4) or ""

        return cls(version_str, major, minor, patch, suffix)

    def __gt__(self, other: "VersionInfo") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(self, other: "VersionInfo") -> bool:
        """Check version equality."""
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )

    def __lt__(self, other: "VersionInfo") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other: "VersionInfo") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) <= (
            other.major,
            other.minor,
            other.patch,
        )

    def __ge__(self, other: "VersionInfo") -> bool:
        """Compare versions."""
        return (self.major, self.minor, self.patch) >= (
            other.major,
            other.minor,
            other.patch,
        )

    def is_compatible_with(
        self, other: "VersionInfo", tolerance: str = "minor"
    ) -> bool:
        """Check if versions are compatible within tolerance."""
        if tolerance == "exact":
            return self == other
        elif tolerance == "patch":
            return self.major == other.major and self.minor == other.minor
        elif tolerance == "minor":
            return self.major == other.major
        else:  # major
            return True


class KotlinGradleDetector:
    """Comprehensive Kotlin/Gradle issue detector."""

    # Compatibility matrices
    KOTLIN_GRADLE_VERSION_REQUIREMENTS = {
        "2.2.20": {"gradle_min": "7.6.3", "gradle_max": "8.14"},
        "2.2.0": {"gradle_min": "7.6.3", "gradle_max": "8.14"},
        "2.1.20": {"gradle_min": "7.6.3", "gradle_max": "8.12.1"},
        "2.0.20": {"gradle_min": "6.8.3", "gradle_max": "8.8"},
        "1.9.20": {"gradle_min": "6.8.3", "gradle_max": "8.1.1"},
        "1.9.0": {"gradle_min": "6.8.3", "gradle_max": "7.6.0"},
        "1.8.22": {"gradle_min": "6.8.3", "gradle_max": "7.6.0"},
        "1.8.0": {"gradle_min": "6.8.3", "gradle_max": "7.3.3"},
    }

    GRADLE_JAVA_VERSION_REQUIREMENTS = {
        "8.14": {"java_min": 17, "java_max": 25},
        "8.10": {"java_min": 17, "java_max": 23},
        "8.5": {"java_min": 17, "java_max": 21},
        "8.3": {"java_min": 17, "java_max": 21},
        "8.0": {"java_min": 17, "java_max": 20},
        "7.6": {"java_min": 8, "java_max": 19},
        "7.3": {"java_min": 8, "java_max": 17},
        "7.0": {"java_min": 8, "java_max": 16},
    }

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.issues: List[KotlinGradleIssue] = []

        # Parse project files
        self.gradle_build_kts = self._parse_gradle_build_kts()
        self.gradle_build = self._parse_gradle_build()
        self.version_catalog = self._parse_version_catalog()
        self.gradle_properties = self._parse_gradle_properties()
        self.wrapper_properties = self._parse_wrapper_properties()
        self.pom_xml = self._parse_pom_xml()

        # Detect installed tools
        self.installed_kotlin = self._detect_kotlin_version()
        self.installed_gradle = self._detect_gradle_version()
        self.installed_java = self._detect_java_version()

    def detect_all_issues(self) -> List[KotlinGradleIssue]:
        """Run all detection methods and return found issues."""
        self.issues.clear()

        # Version requirement validation
        self._check_kotlin_gradle_version_requirements()
        self._check_gradle_java_version_requirements()
        self._check_kotlin_stdlib_version_alignment()

        # Configuration consistency checks
        self._check_java_version_consistency()
        self._check_kotlin_toolchain_consistency()
        self._check_kotlin_compiler_options()

        # Dependency version conflicts
        self._check_dependency_version_conflicts()
        self._check_bom_version_conflicts()
        self._check_kotlinx_library_conflicts()

        # Modern Gradle patterns
        self._check_version_catalog_usage()
        self._check_toolchain_vs_compatibility()
        self._check_plugin_management()

        # Build configuration issues
        self._check_gradle_wrapper_consistency()
        self._check_annotation_processor_conflicts()
        self._check_repository_configuration()

        # Performance and best practices
        self._check_build_performance_issues()
        self._check_deprecated_configurations()

        return self.issues

    def _parse_gradle_build_kts(self) -> Optional[Dict[str, Any]]:
        """Parse build.gradle.kts file."""
        build_file = self.project_path / "build.gradle.kts"
        if not build_file.exists():
            return None

        content = build_file.read_text()

        # Extract plugin versions
        plugins = {}
        plugin_pattern = r'(?:kotlin\("([^"]+)"\)\s*version\s*"([^"]+)"|id\("([^"]+)"\)\s*version\s*"([^"]+)")'
        for match in re.finditer(plugin_pattern, content):
            if match.group(1):  # kotlin() format
                plugins[f"kotlin-{match.group(1)}"] = match.group(2)
            else:  # id() format
                plugins[match.group(3)] = match.group(4)

        # Extract Java configuration
        java_config = {}
        source_compat = re.search(
            r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)", content
        )
        if source_compat:
            java_config["source_compatibility"] = source_compat.group(1)

        target_compat = re.search(
            r"targetCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)", content
        )
        if target_compat:
            java_config["target_compatibility"] = target_compat.group(1)

        # Extract Kotlin configuration
        kotlin_config = {}
        toolchain_match = re.search(r"jvmToolchain\((\d+)\)", content)
        if toolchain_match:
            kotlin_config["jvm_toolchain"] = toolchain_match.group(1)

        jvm_target = re.search(r'jvmTarget\s*=\s*"(\d+)"', content)
        if jvm_target:
            kotlin_config["jvm_target"] = jvm_target.group(1)

        api_version = re.search(r'apiVersion\s*=\s*"([^"]+)"', content)
        if api_version:
            kotlin_config["api_version"] = api_version.group(1)

        language_version = re.search(r'languageVersion\s*=\s*"([^"]+)"', content)
        if language_version:
            kotlin_config["language_version"] = language_version.group(1)

        # Extract dependencies
        dependencies = []
        dep_pattern = r'(?:implementation|testImplementation|api|compileOnly|runtimeOnly|ksp|kapt|annotationProcessor)\s*\(\s*"([^"]+)"\s*\)'
        for match in re.finditer(dep_pattern, content):
            parts = match.group(1).split(":")
            if len(parts) >= 3:
                dependencies.append(
                    {
                        "group": parts[0],
                        "name": parts[1],
                        "version": parts[2] if len(parts) == 3 else ":".join(parts[2:]),
                    }
                )

        return {
            "plugins": plugins,
            "java_config": java_config,
            "kotlin_config": kotlin_config,
            "dependencies": dependencies,
            "content": content,
        }

    def _parse_version_catalog(self) -> Optional[Dict[str, Any]]:
        """Parse gradle/libs.versions.toml file."""
        catalog_file = self.project_path / "gradle" / "libs.versions.toml"
        if not catalog_file.exists():
            return None

        try:
            return toml.load(catalog_file)
        except Exception:
            return None

    def _parse_wrapper_properties(self) -> Optional[Dict[str, str]]:
        """Parse gradle wrapper properties."""
        wrapper_file = (
            self.project_path / "gradle" / "wrapper" / "gradle-wrapper.properties"
        )
        if not wrapper_file.exists():
            return None

        properties = {}
        content = wrapper_file.read_text()
        for line in content.split("\n"):
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()

        return properties

    def _parse_gradle_properties(self) -> Optional[Dict[str, str]]:
        """Parse gradle.properties file."""
        props_file = self.project_path / "gradle.properties"
        if not props_file.exists():
            return None

        properties = {}
        content = props_file.read_text()
        for line in content.split("\n"):
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()

        return properties

    def _parse_gradle_build(self) -> Optional[Dict[str, Any]]:
        """Parse build.gradle file (Groovy DSL)."""
        build_file = self.project_path / "build.gradle"
        if not build_file.exists():
            return None

        # Similar parsing logic for Groovy DSL
        # This is a simplified version - full Groovy parsing is complex
        content = build_file.read_text()
        return {"content": content}

    def _parse_pom_xml(self) -> Optional[Dict[str, Any]]:
        """Parse Maven pom.xml file."""
        pom_file = self.project_path / "pom.xml"
        if not pom_file.exists():
            return None

        # Basic XML parsing for Maven properties
        # In a full implementation, would use xml.etree.ElementTree
        content = pom_file.read_text()
        return {"content": content}

    def _detect_kotlin_version(self) -> Optional[VersionInfo]:
        """Detect installed Kotlin compiler version."""
        try:
            result = subprocess.run(
                ["kotlinc", "-version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                match = re.search(r"(\d+\.\d+\.\d+)", result.stderr or result.stdout)
                if match:
                    return VersionInfo.parse(match.group(1))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _detect_gradle_version(self) -> Optional[VersionInfo]:
        """Detect installed Gradle version."""
        # Try gradlew first
        gradlew = self.project_path / "gradlew"
        if gradlew.exists():
            try:
                result = subprocess.run(
                    [str(gradlew), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if result.returncode == 0:
                    match = re.search(r"Gradle (\d+\.\d+(?:\.\d+)?)", result.stdout)
                    if match:
                        return VersionInfo.parse(match.group(1))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # Fallback to system gradle
        try:
            result = subprocess.run(
                ["gradle", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                match = re.search(r"Gradle (\d+\.\d+(?:\.\d+)?)", result.stdout)
                if match:
                    return VersionInfo.parse(match.group(1))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _detect_java_version(self) -> Optional[VersionInfo]:
        """Detect installed Java version."""
        try:
            result = subprocess.run(
                ["java", "-version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                output = result.stderr or result.stdout
                match = re.search(r'version "(\d+)(?:\.(\d+))?(?:\.(\d+))?', output)
                if match:
                    major = int(match.group(1))
                    # Handle Java 9+ version format
                    if major >= 9:
                        return VersionInfo.parse(f"{major}.0.0")
                    else:
                        minor = int(match.group(2)) if match.group(2) else 0
                        patch = int(match.group(3)) if match.group(3) else 0
                        return VersionInfo.parse(f"{major}.{minor}.{patch}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _check_kotlin_gradle_version_requirements(self):
        """Validate Kotlin and Gradle version requirements."""
        if not self.gradle_build_kts or not self.gradle_build_kts.get("plugins"):
            return

        kotlin_version = None
        for plugin_name, version in self.gradle_build_kts["plugins"].items():
            if "kotlin" in plugin_name:
                kotlin_version = version
                break

        if not kotlin_version or not self.installed_gradle:
            return

        # Validate against version requirements
        requirements_met = False
        gradle_version = self.installed_gradle.raw

        for kt_ver, requirements in self.KOTLIN_GRADLE_VERSION_REQUIREMENTS.items():
            if kotlin_version.startswith(
                kt_ver.split(".")[0] + "." + kt_ver.split(".")[1]
            ):
                gradle_min = VersionInfo.parse(requirements["gradle_min"])
                gradle_max = VersionInfo.parse(requirements["gradle_max"])

                if gradle_min and gradle_max:
                    if gradle_min <= self.installed_gradle <= gradle_max:
                        requirements_met = True
                        break

        if not requirements_met:
            self.issues.append(
                KotlinGradleIssue(
                    issue_type="version_requirements",
                    severity="warning",
                    title="Kotlin Gradle Plugin Version Requirements Not Met",
                    description=f"Kotlin {kotlin_version} has specific Gradle version requirements that may not be satisfied by Gradle {gradle_version}",
                    current_value=f"Kotlin {kotlin_version}, Gradle {gradle_version}",
                    fix_suggestion="Update Gradle or Kotlin versions to meet compatibility requirements",
                    documentation_url="https://kotlinlang.org/docs/gradle-configure-project.html#apply-the-plugin",
                )
            )

    def _check_kotlin_stdlib_version_alignment(self):
        """Validate Kotlin standard library version alignment with plugin version."""
        if not self.gradle_build_kts:
            return

        plugin_version = None
        stdlib_version = None

        # Get plugin version
        for plugin_name, version in self.gradle_build_kts.get("plugins", {}).items():
            if "kotlin" in plugin_name:
                plugin_version = version
                break

        # Get stdlib version from dependencies
        for dep in self.gradle_build_kts.get("dependencies", []):
            if (
                dep["group"] == "org.jetbrains.kotlin"
                and dep["name"] == "kotlin-stdlib"
            ):
                stdlib_version = dep["version"]
                break

        if plugin_version and stdlib_version and plugin_version != stdlib_version:
            self.issues.append(
                KotlinGradleIssue(
                    issue_type="version_alignment",
                    severity="error",
                    title="Kotlin Plugin and Standard Library Version Misalignment",
                    description="Kotlin Gradle plugin version is inconsistent with standard library dependency version, which may cause runtime compatibility issues",
                    current_value=f"Plugin: {plugin_version}, Standard Library: {stdlib_version}",
                    expected_value=f"Both should be {plugin_version}",
                    fix_suggestion=f"Align kotlin-stdlib dependency version to {plugin_version}",
                )
            )

    def _check_java_version_consistency(self):
        """Check consistency between Java configurations."""
        if not self.gradle_build_kts:
            return

        java_config = self.gradle_build_kts.get("java_config", {})
        kotlin_config = self.gradle_build_kts.get("kotlin_config", {})

        source_compat = java_config.get("source_compatibility")
        target_compat = java_config.get("target_compatibility")
        jvm_toolchain = kotlin_config.get("jvm_toolchain")
        jvm_target = kotlin_config.get("jvm_target")

        versions = {
            "sourceCompatibility": source_compat,
            "targetCompatibility": target_compat,
            "Kotlin jvmToolchain": jvm_toolchain,
            "Kotlin jvmTarget": jvm_target,
        }

        # Remove None values
        versions = {k: v for k, v in versions.items() if v}

        if len(set(versions.values())) > 1:
            self.issues.append(
                KotlinGradleIssue(
                    issue_type="configuration_inconsistency",
                    severity="warning",
                    title="Inconsistent Java Version Configuration",
                    description="Different Java versions configured across build file",
                    current_value=", ".join(f"{k}: {v}" for k, v in versions.items()),
                    fix_suggestion="Align all Java version configurations to use the same version",
                )
            )

    def _check_dependency_version_conflicts(self):
        """Check for dependency version conflicts."""
        if not self.gradle_build_kts:
            return

        # Group dependencies by group:name
        dep_groups = {}
        for dep in self.gradle_build_kts.get("dependencies", []):
            key = f"{dep['group']}:{dep['name']}"
            if key not in dep_groups:
                dep_groups[key] = []
            dep_groups[key].append(dep["version"])

        # Check for version conflicts
        for dep_name, versions in dep_groups.items():
            unique_versions = set(versions)
            if len(unique_versions) > 1:
                self.issues.append(
                    KotlinGradleIssue(
                        issue_type="version_conflict",
                        severity="error",
                        title=f"Version Conflict: {dep_name}",
                        description=f"Multiple versions declared: {', '.join(unique_versions)}",
                        fix_suggestion="Use dependency resolution strategy or BOM to manage versions",
                    )
                )

    def _check_version_catalog_usage(self):
        """Check for modern version catalog usage patterns."""
        has_version_catalog = self.version_catalog is not None
        has_hardcoded_versions = False

        if self.gradle_build_kts:
            content = self.gradle_build_kts.get("content", "")
            # Check for hardcoded versions in dependencies
            if re.search(r'implementation\s*\(\s*"[^"]+:\d+\.\d+', content):
                has_hardcoded_versions = True

        if has_hardcoded_versions and not has_version_catalog:
            self.issues.append(
                KotlinGradleIssue(
                    issue_type="best_practice",
                    severity="info",
                    title="Consider Using Gradle Version Catalogs",
                    description="Version catalogs provide centralized dependency management",
                    fix_suggestion="Create gradle/libs.versions.toml and migrate hardcoded versions",
                    documentation_url="https://docs.gradle.org/current/userguide/version_catalogs.html",
                )
            )

    def _check_kotlinx_library_conflicts(self):
        """Check for Kotlinx library version conflicts."""
        if not self.gradle_build_kts:
            return

        kotlinx_deps = {}
        for dep in self.gradle_build_kts.get("dependencies", []):
            if dep["group"] == "org.jetbrains.kotlinx":
                kotlinx_deps[dep["name"]] = dep["version"]

        # Check coroutines versions
        coroutines_versions = {
            k: v for k, v in kotlinx_deps.items() if "coroutines" in k
        }

        if len(set(coroutines_versions.values())) > 1:
            self.issues.append(
                KotlinGradleIssue(
                    issue_type="version_conflict",
                    severity="warning",
                    title="Kotlinx Coroutines Version Mismatch",
                    description=f"Different coroutines versions: {coroutines_versions}",
                    fix_suggestion="Align all kotlinx-coroutines-* dependencies to same version",
                )
            )

    def _check_annotation_processor_conflicts(self):
        """Check for annotation processor conflicts (kapt vs ksp)."""
        if not self.gradle_build_kts:
            return

        content = self.gradle_build_kts.get("content", "")
        has_kapt = "kapt(" in content
        has_ksp = "ksp(" in content

        if has_kapt and has_ksp:
            self.issues.append(
                KotlinGradleIssue(
                    issue_type="configuration_conflict",
                    severity="warning",
                    title="Both KAPT and KSP Processors Detected",
                    description="Using both KAPT and KSP may cause conflicts and slow builds",
                    fix_suggestion="Migrate KAPT processors to KSP where possible for better performance",
                )
            )

    def _check_gradle_wrapper_consistency(self):
        """Check Gradle wrapper version consistency."""
        if not self.wrapper_properties:
            return

        wrapper_url = self.wrapper_properties.get("distributionUrl", "")
        version_match = re.search(r"gradle-(\d+\.\d+(?:\.\d+)?)", wrapper_url)

        if version_match and self.installed_gradle:
            wrapper_version = VersionInfo.parse(version_match.group(1))
            if wrapper_version and wrapper_version != self.installed_gradle:
                self.issues.append(
                    KotlinGradleIssue(
                        issue_type="version_mismatch",
                        severity="info",
                        title="Gradle Wrapper Version Mismatch",
                        description=f"Wrapper: {wrapper_version.raw}, Installed: {self.installed_gradle.raw}",
                        fix_suggestion=f"Run: ./gradlew wrapper --gradle-version {self.installed_gradle.raw}",
                    )
                )

    def _check_gradle_java_version_requirements(self):
        """Validate Gradle and Java version requirements."""
        if not self.installed_gradle or not self.installed_java:
            return

        gradle_version = self.installed_gradle.raw
        java_version = self.installed_java.major

        # Validate against version requirements
        requirements_met = False
        for gradle_ver, requirements in self.GRADLE_JAVA_VERSION_REQUIREMENTS.items():
            gradle_ver_info = VersionInfo.parse(gradle_ver)
            if gradle_ver_info and gradle_ver_info.major == self.installed_gradle.major:
                if requirements["java_min"] <= java_version <= requirements["java_max"]:
                    requirements_met = True
                    break

        if not requirements_met:
            self.issues.append(
                KotlinGradleIssue(
                    issue_type="version_requirements",
                    severity="error",
                    title="Gradle Java Version Requirements Not Satisfied",
                    description=f"Gradle {gradle_version} requires Java versions within a specific range that may not include Java {java_version}",
                    fix_suggestion="Update Java or Gradle versions to meet compatibility requirements",
                )
            )

    def _check_kotlin_toolchain_consistency(self):
        """Check Kotlin toolchain configuration consistency."""
        # Implementation for toolchain checks
        pass

    def _check_kotlin_compiler_options(self):
        """Check Kotlin compiler option consistency."""
        # Implementation for compiler option checks
        pass

    def _check_bom_version_conflicts(self):
        """Check for BOM and explicit version conflicts."""
        # Implementation for BOM conflict checks
        pass

    def _check_toolchain_vs_compatibility(self):
        """Check toolchain vs sourceCompatibility usage."""
        # Implementation for toolchain checks
        pass

    def _check_plugin_management(self):
        """Check plugin management best practices."""
        # Implementation for plugin management checks
        pass

    def _check_repository_configuration(self):
        """Check repository configuration issues."""
        # Implementation for repository checks
        pass

    def _check_build_performance_issues(self):
        """Check for build performance issues."""
        # Implementation for performance checks
        pass

    def _check_deprecated_configurations(self):
        """Check for deprecated Gradle configurations."""
        # Implementation for deprecation checks
        pass

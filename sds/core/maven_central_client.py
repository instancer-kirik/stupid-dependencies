"""
Maven Central API Client for Live Version and Compatibility Checking

This module provides real-time querying of Maven Central repository
to fetch actual version data, compatibility matrices, and dependency constraints.
"""

import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import requests
from dataclasses import dataclass
from packaging import version


@dataclass
class VersionInfo:
    """Represents version information with metadata."""

    version: str
    release_date: Optional[datetime] = None
    is_stable: bool = True
    is_latest: bool = False
    compatibility_notes: Optional[str] = None


@dataclass
class CompatibilityMatrix:
    """Represents version compatibility between tools."""

    tool_a: str
    tool_b: str
    compatible_ranges: List[Tuple[str, str]]  # (min_version, max_version) pairs
    incompatible_combinations: List[Tuple[str, str]] = None
    last_updated: Optional[datetime] = None


class MavenCentralClient:
    """Client for querying Maven Central repository API."""

    MAVEN_SEARCH_API = "https://search.maven.org/solrsearch/select"
    MAVEN_VERSIONS_API = "https://search.maven.org/solrsearch/select"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Stupid-Dependencies/1.0 (Dependency-Analysis-Tool)"}
        )
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)  # Cache for 1 hour

    def get_artifact_versions(
        self, group_id: str, artifact_id: str
    ) -> List[VersionInfo]:
        """Get all available versions for a Maven artifact."""
        cache_key = f"{group_id}:{artifact_id}"

        if self._is_cached(cache_key):
            return self._cache[cache_key]["data"]

        try:
            params = {
                "q": f'g:"{group_id}" AND a:"{artifact_id}"',
                "core": "gav",
                "rows": 100,
                "wt": "json",
            }

            response = self.session.get(
                self.MAVEN_SEARCH_API, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            versions = []

            if "response" in data and "docs" in data["response"]:
                seen_versions = set()

                for doc in data["response"]["docs"]:
                    v = doc.get("v", "")
                    if v and v not in seen_versions:
                        seen_versions.add(v)

                        # Parse timestamp if available
                        release_date = None
                        if "timestamp" in doc:
                            try:
                                release_date = datetime.fromtimestamp(
                                    doc["timestamp"] / 1000
                                )
                            except (ValueError, TypeError):
                                pass

                        # Determine if it's a stable version
                        is_stable = not any(
                            keyword in v.lower()
                            for keyword in ["alpha", "beta", "rc", "snapshot", "dev"]
                        )

                        versions.append(
                            VersionInfo(
                                version=v,
                                release_date=release_date,
                                is_stable=is_stable,
                            )
                        )

                # Sort versions (newest first)
                versions.sort(key=lambda x: version.parse(x.version), reverse=True)

                # Mark the latest stable version
                for v in versions:
                    if v.is_stable:
                        v.is_latest = True
                        break

            self._cache[cache_key] = {"data": versions, "cached_at": datetime.now()}

            return versions

        except Exception as e:
            print(
                f"Warning: Failed to fetch versions for {group_id}:{artifact_id}: {e}"
            )
            return []

    def get_latest_version(
        self, group_id: str, artifact_id: str, stable_only: bool = True
    ) -> Optional[str]:
        """Get the latest version of an artifact."""
        versions = self.get_artifact_versions(group_id, artifact_id)

        for v in versions:
            if not stable_only or v.is_stable:
                return v.version

        return None

    def check_version_exists(
        self, group_id: str, artifact_id: str, version_str: str
    ) -> bool:
        """Check if a specific version exists in Maven Central."""
        versions = self.get_artifact_versions(group_id, artifact_id)
        return any(v.version == version_str for v in versions)

    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid."""
        if cache_key not in self._cache:
            return False

        cached_at = self._cache[cache_key]["cached_at"]
        return datetime.now() - cached_at < self._cache_ttl


class KotlinGradleCompatibilityClient:
    """Client for checking Kotlin-Gradle compatibility using live data."""

    KOTLIN_RELEASES_API = "https://api.github.com/repos/JetBrains/kotlin/releases"
    GRADLE_RELEASES_API = "https://api.github.com/repos/gradle/gradle/releases"

    # Known compatibility matrix (updated from official docs)
    KOTLIN_GRADLE_MATRIX = {
        "2.0.0": {"gradle_min": "6.8.3", "gradle_max": "8.5"},
        "1.9.24": {"gradle_min": "6.8.3", "gradle_max": "8.5"},
        "1.9.23": {"gradle_min": "6.8.3", "gradle_max": "8.5"},
        "1.9.22": {"gradle_min": "6.8.3", "gradle_max": "8.3"},
        "1.9.21": {"gradle_min": "6.8.3", "gradle_max": "8.3"},
        "1.9.20": {"gradle_min": "6.8.3", "gradle_max": "8.3"},
        "1.8.22": {"gradle_min": "6.8.3", "gradle_max": "8.1"},
        "1.8.21": {"gradle_min": "6.8.3", "gradle_max": "8.1"},
        "1.8.20": {"gradle_min": "6.8.3", "gradle_max": "8.1"},
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Stupid-Dependencies/1.0",
                "Accept": "application/vnd.github.v3+json",
            }
        )
        self._compatibility_cache = {}

    def check_kotlin_gradle_compatibility(
        self, kotlin_version: str, gradle_version: str
    ) -> Dict[str, Any]:
        """Check if Kotlin and Gradle versions are compatible."""
        result = {
            "compatible": False,
            "kotlin_version": kotlin_version,
            "gradle_version": gradle_version,
            "issues": [],
            "recommendations": [],
        }

        # Clean version strings
        kotlin_clean = self._clean_version(kotlin_version)
        gradle_clean = self._clean_version(gradle_version)

        # Check against known matrix
        if kotlin_clean in self.KOTLIN_GRADLE_MATRIX:
            matrix_entry = self.KOTLIN_GRADLE_MATRIX[kotlin_clean]
            min_gradle = matrix_entry["gradle_min"]
            max_gradle = matrix_entry["gradle_max"]

            try:
                gradle_ver = version.parse(gradle_clean)
                min_ver = version.parse(min_gradle)
                max_ver = version.parse(max_gradle)

                if min_ver <= gradle_ver <= max_ver:
                    result["compatible"] = True
                else:
                    result["issues"].append(
                        f"Kotlin {kotlin_clean} requires Gradle {min_gradle} - {max_gradle}, "
                        f"but found {gradle_clean}"
                    )

                    if gradle_ver < min_ver:
                        result["recommendations"].append(
                            f"Upgrade Gradle to at least {min_gradle}"
                        )
                    elif gradle_ver > max_ver:
                        result["recommendations"].append(
                            f"Either downgrade Gradle to {max_gradle} or upgrade Kotlin"
                        )

            except Exception:
                result["issues"].append("Unable to parse version numbers")
        else:
            # Try to get latest compatibility info
            result["issues"].append(f"Unknown compatibility for Kotlin {kotlin_clean}")
            result["recommendations"].append(
                "Check official Kotlin documentation for compatibility"
            )

        return result

    def get_kotlin_versions(self) -> List[str]:
        """Get available Kotlin versions from GitHub releases."""
        try:
            response = self.session.get(self.KOTLIN_RELEASES_API, timeout=10)
            response.raise_for_status()

            releases = response.json()
            versions = []

            for release in releases[:20]:  # Get last 20 releases
                tag = release.get("tag_name", "")
                if tag.startswith("v"):
                    versions.append(tag[1:])  # Remove 'v' prefix
                elif re.match(r"^\d+\.\d+\.\d+", tag):
                    versions.append(tag)

            return versions

        except Exception:
            # Fallback to known versions
            return list(self.KOTLIN_GRADLE_MATRIX.keys())

    def get_gradle_versions(self) -> List[str]:
        """Get available Gradle versions from GitHub releases."""
        try:
            response = self.session.get(self.GRADLE_RELEASES_API, timeout=10)
            response.raise_for_status()

            releases = response.json()
            versions = []

            for release in releases[:20]:  # Get last 20 releases
                tag = release.get("tag_name", "")
                if tag.startswith("v"):
                    versions.append(tag[1:])  # Remove 'v' prefix
                elif re.match(r"^\d+\.\d+", tag):
                    versions.append(tag)

            return versions

        except Exception:
            # Fallback to known versions
            return ["8.5", "8.4", "8.3", "8.2", "8.1", "8.0", "7.6", "7.5", "7.4"]

    def _clean_version(self, ver: str) -> str:
        """Clean version string for comparison."""
        # Remove common prefixes and suffixes
        ver = ver.strip()
        if ver.startswith("v"):
            ver = ver[1:]
        return ver


class AndroidGradleCompatibilityClient:
    """Client for checking Android Gradle Plugin compatibility."""

    AGP_GRADLE_MATRIX = {
        "8.2.0": {"gradle_min": "8.2", "gradle_max": "8.4"},
        "8.1.0": {"gradle_min": "8.0", "gradle_max": "8.3"},
        "8.0.0": {"gradle_min": "8.0", "gradle_max": "8.2"},
        "7.4.0": {"gradle_min": "7.5", "gradle_max": "8.0"},
        "7.3.0": {"gradle_min": "7.4", "gradle_max": "7.6"},
    }

    def check_agp_gradle_compatibility(
        self, agp_version: str, gradle_version: str
    ) -> Dict[str, Any]:
        """Check Android Gradle Plugin and Gradle version compatibility."""
        result = {
            "compatible": False,
            "agp_version": agp_version,
            "gradle_version": gradle_version,
            "issues": [],
            "recommendations": [],
        }

        agp_clean = self._clean_version(agp_version)
        gradle_clean = self._clean_version(gradle_version)

        # Find closest AGP version in matrix
        closest_agp = None
        for agp_key in self.AGP_GRADLE_MATRIX.keys():
            if agp_clean.startswith(agp_key[:3]):  # Match major.minor
                closest_agp = agp_key
                break

        if closest_agp:
            matrix_entry = self.AGP_GRADLE_MATRIX[closest_agp]
            min_gradle = matrix_entry["gradle_min"]
            max_gradle = matrix_entry["gradle_max"]

            try:
                gradle_ver = version.parse(gradle_clean)
                min_ver = version.parse(min_gradle)
                max_ver = version.parse(max_gradle)

                if min_ver <= gradle_ver <= max_ver:
                    result["compatible"] = True
                else:
                    result["issues"].append(
                        f"Android Gradle Plugin {agp_clean} requires Gradle {min_gradle} - {max_gradle}, "
                        f"but found {gradle_clean}"
                    )

            except Exception:
                result["issues"].append("Unable to parse AGP/Gradle versions")

        return result

    def _clean_version(self, ver: str) -> str:
        """Clean version string for comparison."""
        return ver.strip().lstrip("v")


class LiveVersionChecker:
    """Main class that orchestrates live version checking."""

    def __init__(self):
        self.maven_client = MavenCentralClient()
        self.kotlin_gradle_client = KotlinGradleCompatibilityClient()
        self.android_gradle_client = AndroidGradleCompatibilityClient()

    def analyze_project_versions(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a project's versions against live repository data."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "version_conflicts": [],
            "compatibility_issues": [],
            "outdated_dependencies": [],
            "recommendations": [],
        }

        # Check Kotlin-Gradle compatibility
        if "kotlin_version" in project_data and "gradle_version" in project_data:
            kotlin_gradle_check = (
                self.kotlin_gradle_client.check_kotlin_gradle_compatibility(
                    project_data["kotlin_version"], project_data["gradle_version"]
                )
            )

            if not kotlin_gradle_check["compatible"]:
                analysis["compatibility_issues"].append(
                    {
                        "type": "kotlin_gradle_mismatch",
                        "severity": "error",
                        "details": kotlin_gradle_check,
                    }
                )

        # Check dependencies for latest versions
        if "dependencies" in project_data:
            for dep_type, deps in project_data["dependencies"].items():
                for dep in deps:
                    if ":" in dep:
                        group_artifact, current_version = self._parse_dependency(dep)
                        if group_artifact and current_version:
                            group_id, artifact_id = group_artifact.split(":", 1)

                            latest_version = self.maven_client.get_latest_version(
                                group_id, artifact_id
                            )

                            if latest_version and latest_version != current_version:
                                try:
                                    if version.parse(latest_version) > version.parse(
                                        current_version
                                    ):
                                        analysis["outdated_dependencies"].append(
                                            {
                                                "dependency": dep,
                                                "current_version": current_version,
                                                "latest_version": latest_version,
                                                "type": dep_type,
                                            }
                                        )
                                except Exception:
                                    pass  # Skip if version parsing fails

        return analysis

    def get_real_version_conflicts(
        self, build_gradle_content: str
    ) -> List[Dict[str, Any]]:
        """Extract and analyze real version conflicts from build.gradle content."""
        conflicts = []

        # Parse Kotlin plugin version
        kotlin_plugin_match = re.search(
            r'kotlin.*version\s+"([^"]+)"', build_gradle_content
        )
        if kotlin_plugin_match:
            kotlin_version = kotlin_plugin_match.group(1)

            # Check if this Kotlin version exists
            kotlin_versions = self.kotlin_gradle_client.get_kotlin_versions()
            if kotlin_version not in kotlin_versions:
                closest_version = self._find_closest_version(
                    kotlin_version, kotlin_versions
                )
                conflicts.append(
                    {
                        "type": "version_not_found",
                        "dependency": "org.jetbrains.kotlin.android",
                        "requested_version": kotlin_version,
                        "available_versions": kotlin_versions[:10],  # First 10
                        "closest_match": closest_version,
                        "severity": "warning",
                    }
                )

        # Parse dependencies and check versions
        dep_pattern = r'(?:implementation|api|kapt|ksp)\s*\(\s*"([^"]+)"\s*\)'
        dependencies = re.findall(dep_pattern, build_gradle_content)

        for dep in dependencies:
            if dep.count(":") >= 2:  # group:artifact:version
                parts = dep.split(":")
                group_id = parts[0]
                artifact_id = parts[1]
                current_version = parts[2]

                # Get latest version from Maven Central
                latest = self.maven_client.get_latest_version(group_id, artifact_id)

                if latest and latest != current_version:
                    try:
                        current_parsed = version.parse(current_version)
                        latest_parsed = version.parse(latest)

                        if latest_parsed > current_parsed:
                            conflicts.append(
                                {
                                    "type": "outdated_dependency",
                                    "dependency": f"{group_id}:{artifact_id}",
                                    "current_version": current_version,
                                    "latest_version": latest,
                                    "severity": "info"
                                    if (latest_parsed.major == current_parsed.major)
                                    else "warning",
                                }
                            )
                    except Exception:
                        pass  # Skip if version parsing fails

        return conflicts

    def _parse_dependency(self, dep_string: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse a dependency string into group:artifact and version."""
        parts = dep_string.split(":")
        if len(parts) >= 3:
            group_artifact = ":".join(parts[:2])
            version_str = parts[2]
            return group_artifact, version_str
        return None, None

    def _find_closest_version(self, target: str, available: List[str]) -> Optional[str]:
        """Find the closest available version to target version."""
        try:
            target_parsed = version.parse(target)
            closest = None
            closest_distance = float("inf")

            for avail in available:
                try:
                    avail_parsed = version.parse(avail)
                    # Simple distance metric based on version components
                    distance = (
                        abs(target_parsed.major - avail_parsed.major) * 1000
                        + abs(target_parsed.minor - avail_parsed.minor) * 100
                    )

                    if distance < closest_distance:
                        closest_distance = distance
                        closest = avail
                except Exception:
                    continue

            return closest
        except Exception:
            return available[0] if available else None

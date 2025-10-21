"""
Dependency Solver - The intelligent core of SDS that finds conflicts and suggests fixes.
"""

import re
from typing import Dict, List, Optional, Any, NamedTuple, Set
from dataclasses import dataclass
from packaging import version as pkg_version
import subprocess
import shutil
from pathlib import Path


@dataclass
class Conflict:
    """Represents a dependency or version conflict."""

    tool: str
    severity: str  # "error", "warning", "info"
    message: str
    reason: str
    details: Optional[str] = None
    current_version: Optional[str] = None
    required_version: Optional[str] = None
    version_manager: Optional[str] = None
    available_versions: Optional[List[str]] = None


@dataclass
class Fix:
    """Represents a suggested fix for a conflict."""

    description: str
    command: Optional[str] = None
    risk_level: str = "low"  # "low", "medium", "high"
    tool: Optional[str] = None
    action_type: str = "version_change"  # "version_change", "install", "config"
    version_manager: Optional[str] = None
    alternatives: Optional[List[str]] = None


class VersionManagerDetector:
    """Detects and provides commands for various version managers."""

    def __init__(self):
        self.managers = {
            "asdf": self._check_asdf,
            "uv": self._check_uv,
            "poetry": self._check_poetry,
            "pyenv": self._check_pyenv,
            "nvm": self._check_nvm,
            "rustup": self._check_rustup,
            "zigup": self._check_zigup,
            "gvm": self._check_gvm,
            "kiex": self._check_kiex,  # Elixir
            "kerl": self._check_kerl,  # Erlang
        }

    def detect_available(self) -> Dict[str, bool]:
        """Detect which version managers are available."""
        available = {}
        for name, checker in self.managers.items():
            available[name] = checker()
        return available

    def get_manager_for_tool(
        self, tool: str, available_managers: Dict[str, bool]
    ) -> Optional[str]:
        """Get the best version manager for a tool."""
        tool_managers = {
            "python": ["uv", "asdf", "pyenv"],
            "node": ["asdf", "nvm"],
            "rust": ["asdf", "rustup"],
            "zig": ["asdf", "zigup"],
            "go": ["asdf", "gvm"],
            "elixir": ["asdf", "kiex"],
            "erlang": ["asdf", "kerl"],
            "java": ["asdf"],
            "kotlin": ["asdf"],
        }

        for manager in tool_managers.get(tool, []):
            if available_managers.get(manager, False):
                return manager

        # Default to asdf if available (it handles most tools)
        if available_managers.get("asdf", False):
            return "asdf"

        return None

    def _check_asdf(self) -> bool:
        return shutil.which("asdf") is not None

    def _check_uv(self) -> bool:
        return shutil.which("uv") is not None

    def _check_poetry(self) -> bool:
        return shutil.which("poetry") is not None

    def _check_pyenv(self) -> bool:
        return shutil.which("pyenv") is not None

    def _check_nvm(self) -> bool:
        # nvm is a shell function, check for its directory
        return Path.home().joinpath(".nvm").exists()

    def _check_rustup(self) -> bool:
        return shutil.which("rustup") is not None

    def _check_zigup(self) -> bool:
        return shutil.which("zigup") is not None

    def _check_gvm(self) -> bool:
        return Path.home().joinpath(".gvm").exists()

    def _check_kiex(self) -> bool:
        return shutil.which("kiex") is not None

    def _check_kerl(self) -> bool:
        return shutil.which("kerl") is not None


class PackageRepositoryClient:
    """Queries package repositories for version information."""

    def __init__(self):
        self.repositories = {
            "python": "https://pypi.org/pypi/{}/json",
            "node": "https://registry.npmjs.org/{}",
            "rust": "https://crates.io/api/v1/crates/{}",
            "elixir": "https://hex.pm/api/packages/{}",
            "go": "https://proxy.golang.org/{}/list",
        }

    def get_available_versions(self, tool: str, package: str = None) -> List[str]:
        """Get available versions for a tool/package."""
        try:
            import requests
            import json

            if tool == "python":
                url = "https://api.github.com/repos/python/cpython/releases"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    releases = response.json()
                    versions = []
                    for release in releases[:10]:  # Last 10 releases
                        tag = release["tag_name"]
                        if tag.startswith("v") and "." in tag:
                            versions.append(tag[1:])  # Remove 'v' prefix
                    return versions

            elif tool == "node":
                url = "https://api.github.com/repos/nodejs/node/releases"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    releases = response.json()
                    versions = []
                    for release in releases[:10]:
                        tag = release["tag_name"]
                        if tag.startswith("v") and "." in tag:
                            versions.append(tag[1:])
                    return versions

            elif tool == "rust":
                url = "https://api.github.com/repos/rust-lang/rust/releases"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    releases = response.json()
                    versions = []
                    for release in releases[:10]:
                        tag = release["tag_name"]
                        if re.match(r"\d+\.\d+\.\d+", tag):
                            versions.append(tag)
                    return versions

            elif tool == "zig":
                url = "https://api.github.com/repos/ziglang/zig/releases"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    releases = response.json()
                    versions = []
                    for release in releases[:10]:
                        tag = release["tag_name"]
                        if re.match(r"\d+\.\d+\.\d+", tag):
                            versions.append(tag)
                    return versions

        except Exception:
            # Fallback to common versions if API fails
            fallback_versions = {
                "python": ["3.12.1", "3.11.7", "3.10.13", "3.9.18"],
                "node": ["20.10.0", "18.19.0", "16.20.2"],
                "rust": ["1.75.0", "1.74.1", "1.73.0"],
                "zig": ["0.12.0", "0.11.0", "0.10.1"],
            }
            return fallback_versions.get(tool, [])

        return []


class DependencySolver:
    """Analyzes environment vs manifest requirements and suggests intelligent fixes."""

    def __init__(self):
        self.version_manager_detector = VersionManagerDetector()
        self.package_client = PackageRepositoryClient()
        self.available_managers = self.version_manager_detector.detect_available()

        # More intelligent and professional messages
        self.analysis_templates = {
            "zig": {
                "newer": "Zig {current} is newer than project requirement {required}. ABI compatibility may be compromised.",
                "older": "Zig {current} is older than project requirement {required}. Missing language features or bug fixes.",
                "missing": "Zig compiler not found. Project requires {required} for build.zig.zon support.",
            },
            "gleam": {
                "newer": "Gleam {current} exceeds project constraint {required}. Check for breaking changes.",
                "older": "Gleam {current} doesn't meet project requirement {required}. Language features may be missing.",
                "missing": "Gleam compiler not found. Install to compile .gleam files.",
            },
            "python": {
                "newer": "Python {current} is newer than project requirement {required}. Dependency compatibility should be verified.",
                "older": "Python {current} is below project requirement {required}. Some packages may not work.",
                "missing": "Python interpreter not found. Project requires {required} for dependencies.",
            },
            "node": {
                "newer": "Node.js {current} exceeds engines requirement {required}. Generally safe but monitor for deprecations.",
                "older": "Node.js {current} is below engines requirement {required}. Missing ES features or security updates.",
                "missing": "Node.js runtime not found. Install to run JavaScript/TypeScript code.",
            },
            "rust": {
                "newer": "Rust {current} is newer than MSRV {required}. Should be compatible.",
                "older": "Rust {current} is below MSRV {required}. Project may not compile due to missing features.",
                "missing": "Rust compiler not found. Install to build Rust crates.",
            },
            "kotlin": {
                "newer": "Kotlin {current} is ahead of build script version {required}. Check plugin compatibility.",
                "older": "Kotlin {current} is behind build script version {required}. Language features may be unavailable.",
                "missing": "Kotlin compiler not found. Install for JVM development.",
            },
            "java": {
                "newer": "Java {current} is newer than project requirement {required}. Usually compatible.",
                "older": "Java {current} is below project requirement {required}. Missing JVM features or security updates.",
                "missing": "Java runtime not found. Install JDK for compilation and runtime.",
            },
            "go": {
                "newer": "Go {current} exceeds module requirement {required}. Should be compatible.",
                "older": "Go {current} is below module requirement {required}. Language features may be missing.",
                "missing": "Go compiler not found. Install to build Go modules.",
            },
        }

    def find_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Find all conflicts between environment and manifest requirements."""
        conflicts = []

        # Check each tool type
        conflicts.extend(self._check_zig_conflicts(env_info, manifests))
        conflicts.extend(self._check_gleam_conflicts(env_info, manifests))
        conflicts.extend(self._check_kotlin_conflicts(env_info, manifests))
        conflicts.extend(self._check_node_conflicts(env_info, manifests))
        conflicts.extend(self._check_python_conflicts(env_info, manifests))
        conflicts.extend(self._check_rust_conflicts(env_info, manifests))
        conflicts.extend(self._check_go_conflicts(env_info, manifests))

        # Enrich conflicts with version manager info and available versions
        for conflict in conflicts:
            conflict.version_manager = (
                self.version_manager_detector.get_manager_for_tool(
                    conflict.tool, self.available_managers
                )
            )
            if conflict.required_version:
                conflict.available_versions = (
                    self.package_client.get_available_versions(conflict.tool)
                )

        return conflicts

    def suggest_fixes(
        self,
        conflicts: List[Conflict],
        env_info: Dict[str, Any],
        manifests: Dict[str, Any],
    ) -> List[Fix]:
        """Suggest intelligent fixes for conflicts."""
        fixes = []

        for conflict in conflicts:
            tool_fixes = self._suggest_tool_fixes(conflict, env_info, manifests)
            fixes.extend(tool_fixes)

        return self._prioritize_fixes(fixes)

    def _check_zig_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Check for Zig version conflicts with intelligent analysis."""
        conflicts = []

        zon_manifest = manifests.get("build.zig.zon")
        if not zon_manifest:
            return conflicts

        required_version = zon_manifest.get("minimum_zig_version")
        if not required_version:
            return conflicts

        zig_info = env_info.get("zig")
        if not zig_info:
            conflicts.append(
                Conflict(
                    tool="zig",
                    severity="error",
                    message="build.zig.zon requires zig, but zig not found",
                    reason="missing toolchain",
                    required_version=required_version,
                    details=self._get_analysis_message(
                        "zig", "missing", None, required_version
                    ),
                )
            )
            return conflicts

        current_version = zig_info["version"]
        comparison = self._compare_versions(current_version, required_version)

        if comparison != 0:
            # For Zig, version mismatches are serious due to ABI changes
            severity = "error" if abs(comparison) >= 1 else "warning"
            situation = "newer" if comparison > 0 else "older"

            # Check if it's a development version
            is_dev = "dev" in current_version.lower()
            reason = (
                "development version"
                if is_dev
                else "ABI compatibility risk"
                if comparison != 0
                else "version mismatch"
            )

            conflicts.append(
                Conflict(
                    tool="zig",
                    severity=severity,
                    message=f"build.zig.zon requires zig {required_version}, found {current_version}",
                    reason=reason,
                    current_version=current_version,
                    required_version=required_version,
                    details=self._get_analysis_message(
                        "zig", situation, current_version, required_version
                    ),
                )
            )

        return conflicts

    def _check_python_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Check Python conflicts with version manager awareness."""
        conflicts = []

        # Check pyproject.toml
        pyproject = manifests.get("pyproject.toml")
        if pyproject and pyproject.get("python_version"):
            python_constraint = pyproject["python_version"]
            python_info = env_info.get("python")

            if not python_info:
                conflicts.append(
                    Conflict(
                        tool="python",
                        severity="error",
                        message="pyproject.toml requires-python specified, but python not found",
                        reason="missing interpreter",
                        required_version=python_constraint,
                        details=self._get_analysis_message(
                            "python", "missing", None, python_constraint
                        ),
                    )
                )
            elif not self._version_satisfies_constraint(
                python_info["version"], python_constraint
            ):
                situation = (
                    "newer"
                    if self._compare_versions(
                        python_info["version"], python_constraint.lstrip(">=<~^")
                    )
                    > 0
                    else "older"
                )

                conflicts.append(
                    Conflict(
                        tool="python",
                        severity="warning",
                        message=f"Python {python_info['version']} vs requires-python {python_constraint}",
                        reason="constraint violation",
                        current_version=python_info["version"],
                        required_version=python_constraint,
                        details=self._get_analysis_message(
                            "python",
                            situation,
                            python_info["version"],
                            python_constraint,
                        ),
                    )
                )

        return conflicts

    def _check_node_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Check Node.js conflicts with intelligent analysis."""
        conflicts = []

        package_json = manifests.get("package.json")
        if not package_json:
            return conflicts

        node_constraint = package_json.get("node_version")
        npm_constraint = package_json.get("npm_version")

        # Check Node version
        if node_constraint:
            node_info = env_info.get("node")
            if not node_info:
                conflicts.append(
                    Conflict(
                        tool="node",
                        severity="error",
                        message="package.json engines.node specified, but node not found",
                        reason="missing runtime",
                        required_version=node_constraint,
                        details=self._get_analysis_message(
                            "node", "missing", None, node_constraint
                        ),
                    )
                )
            elif not self._version_satisfies_constraint(
                node_info["version"], node_constraint
            ):
                situation = (
                    "newer"
                    if self._compare_versions(
                        node_info["version"], node_constraint.lstrip(">=<~^")
                    )
                    > 0
                    else "older"
                )

                conflicts.append(
                    Conflict(
                        tool="node",
                        severity="warning",
                        message=f"Node {node_info['version']} vs engines constraint {node_constraint}",
                        reason="constraint violation",
                        current_version=node_info["version"],
                        required_version=node_constraint,
                        details=self._get_analysis_message(
                            "node", situation, node_info["version"], node_constraint
                        ),
                    )
                )

        return conflicts

    def _check_rust_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Check Rust conflicts with MSRV analysis."""
        conflicts = []

        cargo_toml = manifests.get("Cargo.toml")
        if not cargo_toml:
            return conflicts

        rust_version = cargo_toml.get("rust_version")
        if not rust_version:
            return conflicts

        rust_info = env_info.get("rust")
        if not rust_info:
            conflicts.append(
                Conflict(
                    tool="rust",
                    severity="error",
                    message="Cargo.toml rust-version specified, but rustc not found",
                    reason="missing compiler",
                    required_version=rust_version,
                    details=self._get_analysis_message(
                        "rust", "missing", None, rust_version
                    ),
                )
            )
        elif self._compare_versions(rust_info["version"], rust_version) < 0:
            conflicts.append(
                Conflict(
                    tool="rust",
                    severity="error",
                    message=f"Rust {rust_info['version']} < MSRV {rust_version}",
                    reason="below minimum supported version",
                    current_version=rust_info["version"],
                    required_version=rust_version,
                    details=self._get_analysis_message(
                        "rust", "older", rust_info["version"], rust_version
                    ),
                )
            )

        return conflicts

    def _check_gleam_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Check for Gleam version conflicts."""
        conflicts = []

        gleam_manifest = manifests.get("gleam.toml")
        if not gleam_manifest:
            return conflicts

        gleam_version_constraint = gleam_manifest.get("gleam_version")
        if not gleam_version_constraint:
            return conflicts

        gleam_info = env_info.get("gleam")
        if not gleam_info:
            conflicts.append(
                Conflict(
                    tool="gleam",
                    severity="error",
                    message="gleam.toml requires gleam compiler, but gleam not found",
                    reason="missing toolchain",
                    required_version=gleam_version_constraint,
                    details=self._get_analysis_message(
                        "gleam", "missing", None, gleam_version_constraint
                    ),
                )
            )
            return conflicts

        current_version = gleam_info["version"]

        if self._version_satisfies_constraint(
            current_version, gleam_version_constraint
        ):
            conflicts.append(
                Conflict(
                    tool="gleam",
                    severity="info",
                    message=f"gleam {current_version} ok",
                    reason="version match",
                    current_version=current_version,
                )
            )
        else:
            situation = (
                "newer"
                if self._compare_versions(
                    current_version, gleam_version_constraint.lstrip(">=<~^")
                )
                > 0
                else "older"
            )

            conflicts.append(
                Conflict(
                    tool="gleam",
                    severity="warning",
                    message=f"gleam.toml constraint {gleam_version_constraint}, found {current_version}",
                    reason="constraint violation",
                    current_version=current_version,
                    required_version=gleam_version_constraint,
                    details=self._get_analysis_message(
                        "gleam", situation, current_version, gleam_version_constraint
                    ),
                )
            )

        return conflicts

    def _check_kotlin_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Check for Kotlin, Java, and Gradle conflicts."""
        conflicts = []

        gradle_manifests = [
            manifests.get("build.gradle"),
            manifests.get("build.gradle.kts"),
        ]

        for gradle_manifest in gradle_manifests:
            if not gradle_manifest:
                continue

            # Check Gradle version
            required_gradle = gradle_manifest.get("gradle_version")
            gradle_info = env_info.get("gradle")

            if required_gradle and gradle_info:
                current_gradle = gradle_info["version"]
                comparison = self._compare_versions(current_gradle, required_gradle)

                if comparison != 0:
                    severity = "warning" if abs(comparison) <= 1 else "error"
                    reason = (
                        "minor version difference"
                        if abs(comparison) <= 1
                        else "major version difference"
                    )

                    conflicts.append(
                        Conflict(
                            tool="gradle",
                            severity=severity,
                            message=f"Gradle {current_gradle} found, target {required_gradle} declared",
                            reason=reason,
                            current_version=current_gradle,
                            required_version=required_gradle,
                        )
                    )

        return conflicts

    def _check_go_conflicts(
        self, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Conflict]:
        """Check for Go conflicts."""
        conflicts = []

        go_mod = manifests.get("go.mod")
        if not go_mod:
            return conflicts

        go_version = go_mod.get("go_version")
        if not go_version:
            return conflicts

        go_info = env_info.get("go")
        if not go_info:
            conflicts.append(
                Conflict(
                    tool="go",
                    severity="error",
                    message="go.mod specifies go version, but go not found",
                    reason="missing compiler",
                    required_version=go_version,
                    details=self._get_analysis_message(
                        "go", "missing", None, go_version
                    ),
                )
            )
        elif self._compare_versions(go_info["version"], go_version) < 0:
            conflicts.append(
                Conflict(
                    tool="go",
                    severity="warning",
                    message=f"Go {go_info['version']} < module requirement {go_version}",
                    reason="insufficient version",
                    current_version=go_info["version"],
                    required_version=go_version,
                    details=self._get_analysis_message(
                        "go", "older", go_info["version"], go_version
                    ),
                )
            )

        return conflicts

    def _suggest_tool_fixes(
        self, conflict: Conflict, env_info: Dict[str, Any], manifests: Dict[str, Any]
    ) -> List[Fix]:
        """Suggest intelligent fixes with version manager awareness."""
        fixes = []
        vm = conflict.version_manager

        if conflict.tool == "zig":
            if conflict.reason == "missing toolchain":
                if vm == "asdf":
                    fixes.append(
                        Fix(
                            description=f"Install Zig {conflict.required_version} via asdf",
                            command=f"asdf install zig {conflict.required_version} && asdf global zig {conflict.required_version}",
                            risk_level="low",
                            tool="zig",
                            action_type="install",
                            version_manager="asdf",
                        )
                    )
                elif vm == "zigup":
                    fixes.append(
                        Fix(
                            description=f"Install and switch to Zig {conflict.required_version}",
                            command=f"zigup {conflict.required_version}",
                            risk_level="low",
                            tool="zig",
                            version_manager="zigup",
                        )
                    )
                else:
                    fixes.append(
                        Fix(
                            description="Install Zig from official releases",
                            command="curl https://ziglang.org/download/ # Download and extract",
                            risk_level="medium",
                            tool="zig",
                            action_type="install",
                        )
                    )

            elif conflict.current_version and conflict.required_version:
                if vm == "asdf":
                    fixes.append(
                        Fix(
                            description=f"Switch to Zig {conflict.required_version} via asdf",
                            command=f"asdf install zig {conflict.required_version} && asdf global zig {conflict.required_version}",
                            risk_level="low",
                            tool="zig",
                            version_manager="asdf",
                        )
                    )
                elif vm == "zigup":
                    fixes.append(
                        Fix(
                            description=f"Switch to Zig {conflict.required_version}",
                            command=f"zigup {conflict.required_version}",
                            risk_level="low",
                            tool="zig",
                            version_manager="zigup",
                        )
                    )

        elif conflict.tool == "python":
            if conflict.required_version:
                target_version = conflict.required_version.lstrip(">=<~^")

                if vm == "uv":
                    fixes.append(
                        Fix(
                            description=f"Install Python {target_version} via uv",
                            command=f"uv python install {target_version}",
                            risk_level="low",
                            tool="python",
                            version_manager="uv",
                        )
                    )
                elif vm == "asdf":
                    fixes.append(
                        Fix(
                            description=f"Install Python {target_version} via asdf",
                            command=f"asdf install python {target_version} && asdf global python {target_version}",
                            risk_level="low",
                            tool="python",
                            version_manager="asdf",
                        )
                    )
                elif vm == "pyenv":
                    fixes.append(
                        Fix(
                            description=f"Install Python {target_version} via pyenv",
                            command=f"pyenv install {target_version} && pyenv global {target_version}",
                            risk_level="low",
                            tool="python",
                            version_manager="pyenv",
                        )
                    )

        elif conflict.tool == "node":
            if conflict.required_version:
                target_version = conflict.required_version.lstrip(">=<~^")

                if vm == "asdf":
                    fixes.append(
                        Fix(
                            description=f"Install Node.js {target_version} via asdf",
                            command=f"asdf install nodejs {target_version} && asdf global nodejs {target_version}",
                            risk_level="low",
                            tool="node",
                            version_manager="asdf",
                        )
                    )
                elif vm == "nvm":
                    fixes.append(
                        Fix(
                            description=f"Install Node.js {target_version} via nvm",
                            command=f"nvm install {target_version} && nvm use {target_version}",
                            risk_level="low",
                            tool="node",
                            version_manager="nvm",
                        )
                    )

        elif conflict.tool == "rust":
            if vm == "asdf":
                fixes.append(
                    Fix(
                        description=f"Install Rust {conflict.required_version} via asdf",
                        command=f"asdf install rust {conflict.required_version} && asdf global rust {conflict.required_version}",
                        risk_level="low",
                        tool="rust",
                        version_manager="asdf",
                    )
                )
            elif vm == "rustup":
                fixes.append(
                    Fix(
                        description=f"Update Rust toolchain to {conflict.required_version}",
                        command=f"rustup install {conflict.required_version} && rustup default {conflict.required_version}",
                        risk_level="low",
                        tool="rust",
                        version_manager="rustup",
                    )
                )

        elif conflict.tool == "gradle":
            if conflict.required_version:
                fixes.append(
                    Fix(
                        description=f"Update Gradle wrapper to {conflict.required_version}",
                        command=f"./gradlew wrapper --gradle-version {conflict.required_version}",
                        risk_level="low",
                        tool="gradle",
                    )
                )

        # Add alternative suggestions if available versions are known
        if conflict.available_versions:
            alternatives = []
            for version in conflict.available_versions[:3]:  # Top 3 versions
                if vm:
                    if vm == "asdf":
                        alternatives.append(f"asdf install {conflict.tool} {version}")
                    elif vm == "uv" and conflict.tool == "python":
                        alternatives.append(f"uv python install {version}")
                    elif vm == "zigup" and conflict.tool == "zig":
                        alternatives.append(f"zigup {version}")

            if alternatives and fixes:
                fixes[0].alternatives = alternatives

        return fixes

    def _prioritize_fixes(self, fixes: List[Fix]) -> List[Fix]:
        """Prioritize fixes by risk level and tool importance."""
        priority_order = {"low": 1, "medium": 2, "high": 3}
        tool_priority = {
            "python": 1,
            "node": 2,
            "rust": 3,
            "zig": 4,
            "go": 5,
            "java": 6,
            "kotlin": 7,
        }

        return sorted(
            fixes,
            key=lambda f: (
                priority_order.get(f.risk_level, 999),
                tool_priority.get(f.tool, 999),
            ),
        )

    def _get_analysis_message(
        self, tool: str, situation: str, current: str, required: str
    ) -> str:
        """Get intelligent analysis message for a tool conflict."""
        if tool not in self.analysis_templates:
            return f"Version issue: {current or 'missing'} vs {required}"

        template = self.analysis_templates[tool].get(
            situation, f"{tool} version issue: {current or 'missing'} vs {required}"
        )

        return template.format(current=current or "missing", required=required)

    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns <0, 0, >0 like strcmp."""
        try:
            # Handle development versions
            if "dev" in v1.lower() or "alpha" in v1.lower() or "beta" in v1.lower():
                # Development versions are considered newer than release versions
                if "dev" not in v2.lower():
                    return 1

            version1 = pkg_version.parse(v1)
            version2 = pkg_version.parse(v2)

            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            else:
                return 0
        except Exception:
            # Fallback to string comparison for non-standard versions
            return (v1 > v2) - (v1 < v2)

    def _version_satisfies_constraint(self, version: str, constraint: str) -> bool:
        """Check if a version satisfies a constraint like '>=1.0.0' or '~1.1'."""
        try:
            v = pkg_version.parse(version)

            # Handle different constraint formats
            if constraint.startswith(">="):
                required = pkg_version.parse(constraint[2:])
                return v >= required
            elif constraint.startswith("<="):
                required = pkg_version.parse(constraint[2:])
                return v <= required
            elif constraint.startswith(">"):
                required = pkg_version.parse(constraint[1:])
                return v > required
            elif constraint.startswith("<"):
                required = pkg_version.parse(constraint[1:])
                return v < required
            elif constraint.startswith("~"):
                # Tilde allows patch-level changes
                required = pkg_version.parse(constraint[1:])
                return (
                    v.major == required.major
                    and v.minor == required.minor
                    and v.micro >= required.micro
                )
            elif constraint.startswith("^"):
                # Caret allows compatible changes
                required = pkg_version.parse(constraint[1:])
                return v.major == required.major and v >= required
            else:
                # Exact match or simple version
                clean_constraint = constraint.lstrip(">=<~^")
                required = pkg_version.parse(clean_constraint)
                return v == required

        except Exception:
            # Fallback for non-standard version formats
            clean_version = version.split("+")[0]  # Remove build metadata
            clean_constraint = constraint.lstrip(">=<~^")
            return clean_version == clean_constraint

    def _versions_compatible(self, current: str, required: str) -> bool:
        """Check if two versions are reasonably compatible."""
        try:
            curr = pkg_version.parse(current)
            req = pkg_version.parse(required)

            # Same major and minor version is usually compatible
            return curr.major == req.major and curr.minor == req.minor
        except Exception:
            return current == required

    def _extract_java_major_version(self, version_string: str) -> Optional[str]:
        """Extract major version from Java version string."""
        # Handle both old (1.8.0_xxx) and new (11.0.x) formats
        if version_string.startswith("1."):
            match = re.search(r"1\.(\d+)", version_string)
            return match.group(1) if match else None
        else:
            match = re.search(r"(\d+)", version_string)
            return match.group(1) if match else None

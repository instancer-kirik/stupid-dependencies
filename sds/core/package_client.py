"""
Package Repository Client - Queries package repositories for version information.
"""

import json
import re
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin
from pathlib import Path


class PackageRepositoryClient:
    """Client for querying various package repositories."""

    def __init__(self):
        self.repositories = {
            "python": PyPIClient(),
            "node": NPMClient(),
            "rust": CratesIOClient(),
            "elixir": HexPMClient(),
            "go": GoProxyClient(),
            "zig": ZigReleaseClient(),
            "gleam": HexPMClient(),  # Gleam packages are on hex.pm too
        }

    def get_available_versions(
        self, tool: str, package_name: Optional[str] = None
    ) -> List[str]:
        """Get available versions for a language/tool."""
        if tool not in self.repositories:
            return []

        try:
            return self.repositories[tool].get_versions(package_name or tool)
        except Exception as e:
            print(f"Warning: Failed to fetch versions for {tool}: {e}")
            return self._get_fallback_versions(tool)

    def get_package_info(
        self, tool: str, package_name: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed package information."""
        if tool not in self.repositories:
            return {}

        try:
            return self.repositories[tool].get_package_info(package_name, version)
        except Exception:
            return {}

    def check_version_compatibility(
        self, tool: str, package: str, version: str, dependencies: List[str] = None
    ) -> Dict[str, Any]:
        """Check if a version is compatible with given dependencies."""
        if tool not in self.repositories:
            return {"compatible": True, "issues": []}

        try:
            return self.repositories[tool].check_compatibility(
                package, version, dependencies or []
            )
        except Exception:
            return {"compatible": True, "issues": []}

    def _get_fallback_versions(self, tool: str) -> List[str]:
        """Fallback versions when API queries fail."""
        fallback_data = {
            "python": ["3.12.1", "3.11.7", "3.10.13", "3.9.18", "3.8.18"],
            "node": ["20.11.0", "18.19.0", "16.20.2", "14.21.3"],
            "rust": ["1.76.0", "1.75.0", "1.74.1", "1.73.0"],
            "zig": ["0.12.0", "0.11.0", "0.10.1", "0.9.1"],
            "go": ["1.22.0", "1.21.6", "1.20.14", "1.19.13"],
            "elixir": ["1.16.0", "1.15.7", "1.14.5", "1.13.4"],
            "gleam": ["1.0.0", "0.34.1", "0.33.0", "0.32.4"],
        }
        return fallback_data.get(tool, [])


class BaseRepositoryClient:
    """Base class for repository clients."""

    def get_versions(self, package: str) -> List[str]:
        """Get available versions for a package."""
        raise NotImplementedError

    def get_package_info(
        self, package: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get package information."""
        raise NotImplementedError

    def check_compatibility(
        self, package: str, version: str, dependencies: List[str]
    ) -> Dict[str, Any]:
        """Check version compatibility."""
        return {"compatible": True, "issues": []}


class HexPMClient(BaseRepositoryClient):
    """Client for hex.pm (Elixir/Gleam packages)."""

    def __init__(self):
        self.base_url = "https://hex.pm/api"

    def get_versions(self, package: str) -> List[str]:
        """Get available versions from hex.pm."""
        try:
            import requests

            url = f"{self.base_url}/packages/{package}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                releases = data.get("releases", [])
                versions = []

                for release in releases:
                    version = release.get("version")
                    if version and not release.get("retired"):
                        versions.append(version)

                # Sort versions in descending order (newest first)
                return self._sort_versions(versions)

        except Exception:
            pass

        return []

    def get_package_info(
        self, package: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed package information from hex.pm."""
        try:
            import requests

            url = f"{self.base_url}/packages/{package}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                info = {
                    "name": data.get("name"),
                    "description": data.get("meta", {}).get("description"),
                    "repository": data.get("meta", {})
                    .get("links", {})
                    .get("Repository"),
                    "latest_version": None,
                    "releases": [],
                }

                releases = data.get("releases", [])
                if releases:
                    # Get latest non-retired release
                    active_releases = [r for r in releases if not r.get("retired")]
                    if active_releases:
                        latest = max(
                            active_releases, key=lambda x: x.get("inserted_at", "")
                        )
                        info["latest_version"] = latest.get("version")

                info["releases"] = [
                    {
                        "version": r.get("version"),
                        "inserted_at": r.get("inserted_at"),
                        "retired": r.get("retired", False),
                    }
                    for r in releases[:10]  # Last 10 releases
                ]

                return info

        except Exception:
            pass

        return {}

    def check_compatibility(
        self, package: str, version: str, dependencies: List[str]
    ) -> Dict[str, Any]:
        """Check Elixir/Gleam version compatibility."""
        try:
            import requests

            url = f"{self.base_url}/packages/{package}/releases/{version}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                requirements = data.get("requirements", {})

                issues = []

                # Check Elixir/OTP requirements
                elixir_req = requirements.get("elixir")
                if elixir_req:
                    # Parse elixir requirement like "~> 1.14"
                    issues.append(f"Requires Elixir {elixir_req}")

                return {"compatible": len(issues) == 0, "issues": issues}

        except Exception:
            pass

        return {"compatible": True, "issues": []}

    def _sort_versions(self, versions: List[str]) -> List[str]:
        """Sort versions in descending order."""
        try:
            from packaging import version

            return sorted(versions, key=version.parse, reverse=True)
        except Exception:
            return sorted(versions, reverse=True)


class PyPIClient(BaseRepositoryClient):
    """Client for PyPI (Python packages)."""

    def get_versions(self, package: str) -> List[str]:
        """Get Python versions from GitHub releases."""
        try:
            import requests

            if package == "python":
                # Get Python versions from GitHub
                url = "https://api.github.com/repos/python/cpython/releases"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    releases = response.json()
                    versions = []

                    for release in releases[:20]:
                        tag = release.get("tag_name", "")
                        if tag.startswith("v") and "." in tag:
                            clean_version = tag[1:]  # Remove 'v' prefix
                            if re.match(r"^\d+\.\d+\.\d+$", clean_version):
                                versions.append(clean_version)

                    return versions
            else:
                # Get package versions from PyPI
                url = f"https://pypi.org/pypi/{package}/json"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    versions = list(data.get("releases", {}).keys())
                    return self._sort_versions(versions)

        except Exception:
            pass

        return []

    def get_package_info(
        self, package: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Python package information."""
        try:
            import requests

            url = f"https://pypi.org/pypi/{package}/json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                info = data.get("info", {})

                return {
                    "name": info.get("name"),
                    "version": info.get("version"),
                    "summary": info.get("summary"),
                    "requires_python": info.get("requires_python"),
                    "home_page": info.get("home_page"),
                }

        except Exception:
            pass

        return {}

    def _sort_versions(self, versions: List[str]) -> List[str]:
        """Sort versions in descending order."""
        try:
            from packaging import version

            return sorted(versions, key=version.parse, reverse=True)
        except Exception:
            return sorted(versions, reverse=True)


class NPMClient(BaseRepositoryClient):
    """Client for npm registry."""

    def get_versions(self, package: str) -> List[str]:
        """Get Node.js versions."""
        try:
            import requests

            if package == "node":
                # Get Node.js versions from GitHub
                url = "https://api.github.com/repos/nodejs/node/releases"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    releases = response.json()
                    versions = []

                    for release in releases[:20]:
                        tag = release.get("tag_name", "")
                        if tag.startswith("v") and "." in tag:
                            clean_version = tag[1:]  # Remove 'v' prefix
                            versions.append(clean_version)

                    return versions
            else:
                # Get npm package versions
                url = f"https://registry.npmjs.org/{package}"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    versions = list(data.get("versions", {}).keys())
                    return self._sort_versions(versions)

        except Exception:
            pass

        return []

    def get_package_info(
        self, package: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get npm package information."""
        try:
            import requests

            url = f"https://registry.npmjs.org/{package}"
            if version:
                url += f"/{version}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if version:
                    return {
                        "name": data.get("name"),
                        "version": data.get("version"),
                        "description": data.get("description"),
                        "engines": data.get("engines", {}),
                    }
                else:
                    latest_version = data.get("dist-tags", {}).get("latest")
                    return {
                        "name": data.get("name"),
                        "latest_version": latest_version,
                        "description": data.get("description"),
                        "versions": list(data.get("versions", {}).keys())[:10],
                    }

        except Exception:
            pass

        return {}

    def _sort_versions(self, versions: List[str]) -> List[str]:
        """Sort versions in descending order."""
        try:
            from packaging import version

            return sorted(versions, key=version.parse, reverse=True)
        except Exception:
            return sorted(versions, reverse=True)


class CratesIOClient(BaseRepositoryClient):
    """Client for crates.io (Rust packages)."""

    def get_versions(self, package: str) -> List[str]:
        """Get Rust versions."""
        try:
            import requests

            if package == "rust":
                # Get Rust versions from GitHub
                url = "https://api.github.com/repos/rust-lang/rust/releases"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    releases = response.json()
                    versions = []

                    for release in releases[:15]:
                        tag = release.get("tag_name", "")
                        if re.match(r"^\d+\.\d+\.\d+$", tag):
                            versions.append(tag)

                    return versions
            else:
                # Get crate versions
                url = f"https://crates.io/api/v1/crates/{package}/versions"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    versions = []

                    for version_data in data.get("versions", []):
                        if not version_data.get("yanked", False):
                            versions.append(version_data.get("num"))

                    return versions[:20]  # First 20 versions

        except Exception:
            pass

        return []

    def get_package_info(
        self, package: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get crate information."""
        try:
            import requests

            url = f"https://crates.io/api/v1/crates/{package}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                crate_info = data.get("crate", {})

                return {
                    "name": crate_info.get("name"),
                    "description": crate_info.get("description"),
                    "max_version": crate_info.get("max_version"),
                    "downloads": crate_info.get("downloads"),
                    "repository": crate_info.get("repository"),
                }

        except Exception:
            pass

        return {}


class GoProxyClient(BaseRepositoryClient):
    """Client for Go module proxy."""

    def get_versions(self, package: str) -> List[str]:
        """Get Go versions."""
        try:
            import requests

            if package == "go":
                # Get Go versions from GitHub
                url = "https://api.github.com/repos/golang/go/releases"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    releases = response.json()
                    versions = []

                    for release in releases[:15]:
                        tag = release.get("tag_name", "")
                        if tag.startswith("go") and "." in tag:
                            clean_version = tag[2:]  # Remove 'go' prefix
                            versions.append(clean_version)

                    return versions
            else:
                # For Go modules, use the proxy
                url = f"https://proxy.golang.org/{package}/@v/list"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    versions = response.text.strip().split("\n")
                    return [v for v in versions if v and not v.startswith("v0.0.0")]

        except Exception:
            pass

        return []


class ZigReleaseClient(BaseRepositoryClient):
    """Client for Zig releases."""

    def get_versions(self, package: str) -> List[str]:
        """Get Zig versions from GitHub releases."""
        try:
            import requests

            url = "https://api.github.com/repos/ziglang/zig/releases"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                releases = response.json()
                versions = []

                for release in releases[:15]:
                    tag = release.get("tag_name", "")
                    if re.match(r"^\d+\.\d+\.\d+$", tag):
                        versions.append(tag)

                return versions

        except Exception:
            pass

        return []

    def get_package_info(
        self, package: str, version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Zig release information."""
        try:
            import requests

            if version:
                url = (
                    f"https://api.github.com/repos/ziglang/zig/releases/tags/{version}"
                )
            else:
                url = "https://api.github.com/repos/ziglang/zig/releases/latest"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                return {
                    "name": "zig",
                    "version": data.get("tag_name"),
                    "published_at": data.get("published_at"),
                    "prerelease": data.get("prerelease", False),
                    "body": data.get("body", "")[
                        :200
                    ],  # First 200 chars of release notes
                }

        except Exception:
            pass

        return {}


# Utility functions for version solving
def solve_version_constraints(
    tool: str, constraints: List[str], available_versions: List[str] = None
) -> Optional[str]:
    """Solve version constraints to find the best matching version."""
    if not available_versions:
        client = PackageRepositoryClient()
        available_versions = client.get_available_versions(tool)

    if not available_versions:
        return None

    try:
        from packaging import version, specifiers

        # Combine all constraints
        combined_constraint = ",".join(constraints)
        spec_set = specifiers.SpecifierSet(combined_constraint)

        # Find the highest version that satisfies all constraints
        compatible_versions = [
            v for v in available_versions if version.parse(v) in spec_set
        ]

        if compatible_versions:
            return max(compatible_versions, key=version.parse)

    except Exception:
        # Fallback to simple string matching
        for constraint in constraints:
            clean_constraint = constraint.lstrip(">=<~^")
            if clean_constraint in available_versions:
                return clean_constraint

    return None


def find_version_conflicts(
    dependencies: Dict[str, str], available_versions: Dict[str, List[str]] = None
) -> List[Dict[str, Any]]:
    """Find conflicts between dependency version requirements."""
    conflicts = []

    for dep_name, constraint in dependencies.items():
        if not available_versions or dep_name not in available_versions:
            continue

        try:
            from packaging import specifiers, version

            spec_set = specifiers.SpecifierSet(constraint)
            compatible = [
                v for v in available_versions[dep_name] if version.parse(v) in spec_set
            ]

            if not compatible:
                conflicts.append(
                    {
                        "dependency": dep_name,
                        "constraint": constraint,
                        "issue": "No available versions satisfy constraint",
                        "available": available_versions[dep_name][
                            :5
                        ],  # First 5 versions
                    }
                )

        except Exception:
            continue

    return conflicts

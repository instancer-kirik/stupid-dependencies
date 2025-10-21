"""
Manifest Parser - Parses project configuration files for dependency constraints.
"""

import json
import re
import toml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import xml.etree.ElementTree as ET


class ManifestParser:
    """Parses various project manifest files to extract dependency constraints."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.parsers = {
            "build.zig.zon": self._parse_zig_zon,
            "build.zig": self._parse_zig_build,
            "gleam.toml": self._parse_gleam_toml,
            "build.gradle": self._parse_gradle,
            "build.gradle.kts": self._parse_gradle_kts,
            "pom.xml": self._parse_maven_pom,
            "package.json": self._parse_package_json,
            "requirements.txt": self._parse_requirements_txt,
            "pyproject.toml": self._parse_pyproject_toml,
            "Pipfile": self._parse_pipfile,
            "Cargo.toml": self._parse_cargo_toml,
            "go.mod": self._parse_go_mod,
        }

    def parse_all(self) -> Dict[str, Any]:
        """Parse all available manifest files in the project."""
        results = {}

        for filename, parser in self.parsers.items():
            manifest_path = self.project_path / filename
            if manifest_path.exists():
                try:
                    parsed = parser(manifest_path)
                    if parsed:
                        results[filename] = parsed
                except Exception as e:
                    # In production, we might want to log this
                    results[filename] = {"error": str(e)}

        return results

    def parse_manifest(self, filename: str) -> Optional[Dict[str, Any]]:
        """Parse a specific manifest file."""
        if filename not in self.parsers:
            return None

        manifest_path = self.project_path / filename
        if not manifest_path.exists():
            return None

        try:
            return self.parsers[filename](manifest_path)
        except Exception:
            return None

    def _parse_zig_zon(self, path: Path) -> Dict[str, Any]:
        """Parse Zig's build.zig.zon file."""
        content = path.read_text()

        # This is a simplified parser - real Zig .zon files are more complex
        result = {
            "type": "zig",
            "minimum_zig_version": None,
            "dependencies": {},
        }

        # Look for minimum_zig_version
        zig_version_match = re.search(r'minimum_zig_version\s*=\s*"([^"]+)"', content)
        if zig_version_match:
            result["minimum_zig_version"] = zig_version_match.group(1)

        # Look for dependencies (simplified)
        deps_section = re.search(
            r"\.dependencies\s*=\s*\{([^}]+)\}", content, re.DOTALL
        )
        if deps_section:
            deps_content = deps_section.group(1)
            # Extract individual dependencies
            dep_matches = re.findall(
                r'(\w+)\s*=\s*\{[^}]*\.url\s*=\s*"([^"]+)"[^}]*\}', deps_content
            )
            for name, url in dep_matches:
                result["dependencies"][name] = {"url": url}

        return result

    def _parse_zig_build(self, path: Path) -> Dict[str, Any]:
        """Parse Zig's build.zig file for version constraints."""
        content = path.read_text()

        result = {
            "type": "zig",
            "zig_version": None,
        }

        # Look for Zig version requirements in comments or code
        version_patterns = [
            r"//\s*zig\s+(\d+\.\d+\.\d+)",
            r"//\s*requires?\s+zig\s+(\d+\.\d+\.\d+)",
            r'std\.zig\.version\(\s*"([^"]+)"',
        ]

        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result["zig_version"] = match.group(1)
                break

        return result

    def _parse_gleam_toml(self, path: Path) -> Dict[str, Any]:
        """Parse Gleam's gleam.toml file."""
        with open(path, "r") as f:
            data = toml.load(f)

        result = {
            "type": "gleam",
            "name": data.get("name"),
            "version": data.get("version"),
            "gleam_version": None,
            "dependencies": data.get("dependencies", {}),
            "dev_dependencies": data.get("dev-dependencies", {}),
        }

        # Check for Gleam version constraint
        if "gleam" in data:
            result["gleam_version"] = data["gleam"]

        return result

    def _parse_gradle(self, path: Path) -> Dict[str, Any]:
        """Parse Gradle build.gradle file."""
        content = path.read_text()

        result = {
            "type": "gradle",
            "kotlin_version": None,
            "java_version": None,
            "gradle_version": None,
            "dependencies": [],
        }

        # Extract Kotlin version
        kotlin_match = re.search(r'kotlin\s*\(\s*["\']([^"\']+)["\']', content)
        if kotlin_match:
            result["kotlin_version"] = kotlin_match.group(1)

        # Extract Java version
        java_matches = [
            r'sourceCompatibility\s*=\s*["\']?(\d+)["\']?',
            r'targetCompatibility\s*=\s*["\']?(\d+)["\']?',
            r"JavaVersion\.VERSION_(\d+)",
        ]
        for pattern in java_matches:
            match = re.search(pattern, content)
            if match:
                result["java_version"] = match.group(1)
                break

        # Look for Gradle wrapper version
        wrapper_props = (
            self.project_path / "gradle" / "wrapper" / "gradle-wrapper.properties"
        )
        if wrapper_props.exists():
            wrapper_content = wrapper_props.read_text()
            gradle_match = re.search(r"gradle-(\d+\.\d+(?:\.\d+)?)-", wrapper_content)
            if gradle_match:
                result["gradle_version"] = gradle_match.group(1)

        return result

    def _parse_gradle_kts(self, path: Path) -> Dict[str, Any]:
        """Parse Gradle build.gradle.kts file."""
        content = path.read_text()

        result = {
            "type": "gradle",
            "kotlin_version": None,
            "java_version": None,
            "gradle_version": None,
            "dependencies": [],
        }

        # Extract Kotlin version from plugins
        kotlin_match = re.search(r'kotlin\s*\(\s*"([^"]+)"\s*\)', content)
        if kotlin_match:
            result["kotlin_version"] = kotlin_match.group(1)

        # Extract Java version
        java_patterns = [
            r"JavaVersion\.VERSION_(\d+)",
            r'jvmTarget\s*=\s*"(\d+)"',
            r"sourceCompatibility\s*=\s*JavaVersion\.VERSION_(\d+)",
        ]
        for pattern in java_patterns:
            match = re.search(pattern, content)
            if match:
                result["java_version"] = match.group(1)
                break

        # Check Gradle wrapper
        wrapper_props = (
            self.project_path / "gradle" / "wrapper" / "gradle-wrapper.properties"
        )
        if wrapper_props.exists():
            wrapper_content = wrapper_props.read_text()
            gradle_match = re.search(r"gradle-(\d+\.\d+(?:\.\d+)?)-", wrapper_content)
            if gradle_match:
                result["gradle_version"] = gradle_match.group(1)

        return result

    def _parse_maven_pom(self, path: Path) -> Dict[str, Any]:
        """Parse Maven pom.xml file."""
        tree = ET.parse(path)
        root = tree.getroot()

        # Handle namespace
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag[root.tag.find("{") : root.tag.find("}") + 1]

        result = {
            "type": "maven",
            "java_version": None,
            "maven_version": None,
            "dependencies": [],
        }

        # Extract Java version
        java_version_paths = [
            f"./{ns}properties/{ns}maven.compiler.source",
            f"./{ns}properties/{ns}maven.compiler.target",
            f"./{ns}properties/{ns}java.version",
        ]

        for xpath in java_version_paths:
            element = root.find(xpath)
            if element is not None:
                result["java_version"] = element.text
                break

        return result

    def _parse_package_json(self, path: Path) -> Dict[str, Any]:
        """Parse Node.js package.json file."""
        with open(path, "r") as f:
            data = json.load(f)

        result = {
            "type": "node",
            "name": data.get("name"),
            "version": data.get("version"),
            "node_version": None,
            "npm_version": None,
            "dependencies": data.get("dependencies", {}),
            "devDependencies": data.get("devDependencies", {}),
        }

        # Check for Node version constraints
        engines = data.get("engines", {})
        if "node" in engines:
            result["node_version"] = engines["node"]
        if "npm" in engines:
            result["npm_version"] = engines["npm"]

        return result

    def _parse_requirements_txt(self, path: Path) -> Dict[str, Any]:
        """Parse Python requirements.txt file."""
        lines = path.read_text().strip().split("\n")

        result = {
            "type": "python",
            "dependencies": {},
        }

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse package==version or package>=version etc.
            match = re.match(r"^([a-zA-Z0-9_-]+)([<>=!]+)(.+)$", line)
            if match:
                package, operator, version = match.groups()
                result["dependencies"][package] = {
                    "operator": operator,
                    "version": version.strip(),
                }
            else:
                # Simple package name without version
                result["dependencies"][line] = {"version": "*"}

        return result

    def _parse_pyproject_toml(self, path: Path) -> Dict[str, Any]:
        """Parse Python pyproject.toml file."""
        with open(path, "r") as f:
            data = toml.load(f)

        result = {
            "type": "python",
            "python_version": None,
            "dependencies": {},
        }

        # Check for Python version requirement
        if "project" in data and "requires-python" in data["project"]:
            result["python_version"] = data["project"]["requires-python"]

        # Extract dependencies
        if "project" in data and "dependencies" in data["project"]:
            for dep in data["project"]["dependencies"]:
                # Parse "package>=1.0" format
                match = re.match(r"^([a-zA-Z0-9_-]+)([<>=!]+)(.+)$", dep)
                if match:
                    package, operator, version = match.groups()
                    result["dependencies"][package] = {
                        "operator": operator,
                        "version": version.strip(),
                    }
                else:
                    result["dependencies"][dep] = {"version": "*"}

        return result

    def _parse_pipfile(self, path: Path) -> Dict[str, Any]:
        """Parse Python Pipfile."""
        with open(path, "r") as f:
            data = toml.load(f)

        result = {
            "type": "python",
            "python_version": None,
            "dependencies": data.get("packages", {}),
            "dev_dependencies": data.get("dev-packages", {}),
        }

        # Check for Python version requirement
        if "requires" in data and "python_version" in data["requires"]:
            result["python_version"] = data["requires"]["python_version"]

        return result

    def _parse_cargo_toml(self, path: Path) -> Dict[str, Any]:
        """Parse Rust Cargo.toml file."""
        with open(path, "r") as f:
            data = toml.load(f)

        result = {
            "type": "rust",
            "name": data.get("package", {}).get("name"),
            "version": data.get("package", {}).get("version"),
            "rust_version": None,
            "dependencies": data.get("dependencies", {}),
            "dev_dependencies": data.get("dev-dependencies", {}),
        }

        # Check for Rust version requirement
        if "package" in data and "rust-version" in data["package"]:
            result["rust_version"] = data["package"]["rust-version"]

        return result

    def _parse_go_mod(self, path: Path) -> Dict[str, Any]:
        """Parse Go go.mod file."""
        content = path.read_text()

        result = {
            "type": "go",
            "module": None,
            "go_version": None,
            "dependencies": {},
        }

        # Extract module name
        module_match = re.search(r"^module\s+(.+)$", content, re.MULTILINE)
        if module_match:
            result["module"] = module_match.group(1).strip()

        # Extract Go version
        go_match = re.search(r"^go\s+(\d+\.\d+(?:\.\d+)?)$", content, re.MULTILINE)
        if go_match:
            result["go_version"] = go_match.group(1)

        # Extract dependencies (simplified)
        require_section = re.search(r"require\s*\((.*?)\)", content, re.DOTALL)
        if require_section:
            deps_content = require_section.group(1)
            dep_matches = re.findall(r"(\S+)\s+v?(\S+)", deps_content)
            for module, version in dep_matches:
                result["dependencies"][module] = version

        return result

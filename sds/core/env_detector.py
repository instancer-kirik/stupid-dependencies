"""
Environment Detector - Identifies toolchain versions and version managers.
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, Optional, Any
import shutil
import os


class EnvironmentDetector:
    """Detects development environment tools, versions, and version managers."""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.version_managers = self._detect_version_managers()
        self.detectors = {
            "zig": self._detect_zig,
            "gleam": self._detect_gleam,
            "kotlin": self._detect_kotlin,
            "java": self._detect_java,
            "gradle": self._detect_gradle,
            "node": self._detect_node,
            "npm": self._detect_npm,
            "python": self._detect_python,
            "pip": self._detect_pip,
            "rust": self._detect_rust,
            "cargo": self._detect_cargo,
            "go": self._detect_go,
            "elixir": self._detect_elixir,
            "erlang": self._detect_erlang,
        }

    def detect_all(self) -> Dict[str, Dict[str, Any]]:
        """Detect all available tools in the environment."""
        results = {}

        for tool, detector in self.detectors.items():
            try:
                info = detector()
                if info:
                    # Enhance with version manager info
                    info["managed_by"] = self._get_version_manager_for_tool(
                        tool, info.get("path")
                    )
                    results[tool] = info
            except Exception:
                # Silently ignore tools that can't be detected
                continue

        return results

    def detect_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Detect a specific tool."""
        if tool_name not in self.detectors:
            return None

        try:
            info = self.detectors[tool_name]()
            if info:
                info["managed_by"] = self._get_version_manager_for_tool(
                    tool_name, info.get("path")
                )
            return info
        except Exception:
            return None

    def _detect_version_managers(self) -> Dict[str, bool]:
        """Detect available version managers."""
        managers = {}

        # Check for asdf
        asdf_dir = Path.home() / ".asdf"
        managers["asdf"] = asdf_dir.exists() and shutil.which("asdf") is not None

        # Check for uv
        managers["uv"] = shutil.which("uv") is not None

        # Check for poetry
        managers["poetry"] = shutil.which("poetry") is not None

        # Check for pyenv
        pyenv_root = os.environ.get("PYENV_ROOT", str(Path.home() / ".pyenv"))
        managers["pyenv"] = (
            Path(pyenv_root).exists() and shutil.which("pyenv") is not None
        )

        # Check for nvm
        nvm_dir = os.environ.get("NVM_DIR", str(Path.home() / ".nvm"))
        managers["nvm"] = Path(nvm_dir).exists()

        # Check for rustup
        rustup_home = os.environ.get("RUSTUP_HOME", str(Path.home() / ".rustup"))
        managers["rustup"] = (
            Path(rustup_home).exists() and shutil.which("rustup") is not None
        )

        # Check for zigup
        managers["zigup"] = shutil.which("zigup") is not None

        # Check for gvm (Go Version Manager)
        gvm_root = os.environ.get("GVM_ROOT", str(Path.home() / ".gvm"))
        managers["gvm"] = Path(gvm_root).exists()

        # Check for kiex (Elixir)
        managers["kiex"] = shutil.which("kiex") is not None

        # Check for kerl (Erlang)
        managers["kerl"] = shutil.which("kerl") is not None

        return managers

    def _get_version_manager_for_tool(
        self, tool: str, tool_path: Optional[str]
    ) -> Optional[str]:
        """Determine which version manager is managing a tool."""
        if not tool_path:
            return None

        path_str = str(tool_path)

        # Check various version manager patterns
        if "/.asdf/" in path_str:
            return "asdf"
        elif "/.pyenv/" in path_str:
            return "pyenv"
        elif "/.nvm/" in path_str:
            return "nvm"
        elif "/.rustup/" in path_str or "/.cargo/" in path_str:
            return "rustup"
        elif "/.gvm/" in path_str:
            return "gvm"
        elif "/uv/" in path_str or tool == "python" and self.version_managers.get("uv"):
            # uv manages Python but might not be in the path
            return "uv"
        elif "/poetry/" in path_str:
            return "poetry"

        return None

    def _run_command(self, cmd: list, timeout: int = 5) -> Optional[str]:
        """Run a command and return stdout, or None if it fails."""
        try:
            if not shutil.which(cmd[0]):
                return None

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_path,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return None

    def _extract_version(self, text: str, patterns: list) -> Optional[str]:
        """Extract version number using regex patterns."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        return None

    def _detect_zig(self) -> Optional[Dict[str, Any]]:
        """Detect Zig compiler version."""
        output = self._run_command(["zig", "version"])
        if not output:
            return None

        # Zig version output is just the version number
        version = output.strip()
        # Handle both release and dev versions
        if re.match(r"\d+\.\d+\.\d+", version) or "dev" in version:
            return {
                "version": version,
                "command": "zig version",
                "path": shutil.which("zig"),
                "is_dev": "dev" in version,
            }
        return None

    def _detect_gleam(self) -> Optional[Dict[str, Any]]:
        """Detect Gleam compiler version."""
        output = self._run_command(["gleam", "--version"])
        if not output:
            return None

        # Gleam output: "gleam 1.1.0"
        version = self._extract_version(output, [r"gleam\s+(\d+\.\d+\.\d+)"])
        if version:
            return {
                "version": version,
                "command": "gleam --version",
                "path": shutil.which("gleam"),
            }
        return None

    def _detect_kotlin(self) -> Optional[Dict[str, Any]]:
        """Detect Kotlin compiler version."""
        output = self._run_command(["kotlinc", "-version"])
        if not output:
            return None

        # Kotlin output: "info: kotlinc-jvm 1.9.23 (JRE 17.0.8+7-Ubuntu-120.04)"
        version = self._extract_version(
            output, [r"kotlinc.*?(\d+\.\d+\.\d+)", r"kotlin.*?(\d+\.\d+\.\d+)"]
        )
        if version:
            return {
                "version": version,
                "command": "kotlinc -version",
                "path": shutil.which("kotlinc"),
            }
        return None

    def _detect_java(self) -> Optional[Dict[str, Any]]:
        """Detect Java version."""
        output = self._run_command(["java", "-version"])
        if not output:
            return None

        # Java output varies, try multiple patterns
        version = self._extract_version(
            output,
            [
                r'version "(\d+\.\d+\.\d+)',
                r'version "(\d+)',
                r"openjdk version \"(\d+\.\d+\.\d+)",
                r"openjdk (\d+\.\d+\.\d+)",
            ],
        )

        if version:
            return {
                "version": version,
                "command": "java -version",
                "path": shutil.which("java"),
            }
        return None

    def _detect_gradle(self) -> Optional[Dict[str, Any]]:
        """Detect Gradle version."""
        # Try gradlew first (project-specific)
        gradlew_path = self.project_path / "gradlew"
        if gradlew_path.exists():
            output = self._run_command(["./gradlew", "--version"])
            if output:
                version = self._extract_version(
                    output, [r"Gradle (\d+\.\d+(?:\.\d+)?)"]
                )
                if version:
                    return {
                        "version": version,
                        "command": "./gradlew --version",
                        "path": str(gradlew_path),
                        "wrapper": True,
                    }

        # Fallback to system gradle
        output = self._run_command(["gradle", "--version"])
        if output:
            version = self._extract_version(output, [r"Gradle (\d+\.\d+(?:\.\d+)?)"])
            if version:
                return {
                    "version": version,
                    "command": "gradle --version",
                    "path": shutil.which("gradle"),
                    "wrapper": False,
                }

        return None

    def _detect_node(self) -> Optional[Dict[str, Any]]:
        """Detect Node.js version."""
        output = self._run_command(["node", "--version"])
        if not output:
            return None

        # Node output: "v18.17.0"
        version = self._extract_version(output, [r"v?(\d+\.\d+\.\d+)"])
        if version:
            return {
                "version": version,
                "command": "node --version",
                "path": shutil.which("node"),
            }
        return None

    def _detect_npm(self) -> Optional[Dict[str, Any]]:
        """Detect npm version."""
        output = self._run_command(["npm", "--version"])
        if not output:
            return None

        version = output.strip()
        if re.match(r"\d+\.\d+\.\d+", version):
            return {
                "version": version,
                "command": "npm --version",
                "path": shutil.which("npm"),
            }
        return None

    def _detect_python(self) -> Optional[Dict[str, Any]]:
        """Detect Python version."""
        # Try python3 first, then python
        for cmd in ["python3", "python"]:
            output = self._run_command([cmd, "--version"])
            if output:
                version = self._extract_version(output, [r"Python (\d+\.\d+\.\d+)"])
                if version:
                    return {
                        "version": version,
                        "command": f"{cmd} --version",
                        "path": shutil.which(cmd),
                    }
        return None

    def _detect_pip(self) -> Optional[Dict[str, Any]]:
        """Detect pip version."""
        for cmd in ["pip3", "pip"]:
            output = self._run_command([cmd, "--version"])
            if output:
                # pip output: "pip 23.1.2 from /usr/lib/python3/dist-packages/pip (python 3.11)"
                version = self._extract_version(output, [r"pip (\d+\.\d+(?:\.\d+)?)"])
                if version:
                    return {
                        "version": version,
                        "command": f"{cmd} --version",
                        "path": shutil.which(cmd),
                    }
        return None

    def _detect_rust(self) -> Optional[Dict[str, Any]]:
        """Detect Rust version."""
        output = self._run_command(["rustc", "--version"])
        if not output:
            return None

        # Rust output: "rustc 1.71.0 (8ede3aae2 2023-07-12)"
        version = self._extract_version(output, [r"rustc (\d+\.\d+\.\d+)"])
        if version:
            return {
                "version": version,
                "command": "rustc --version",
                "path": shutil.which("rustc"),
            }
        return None

    def _detect_cargo(self) -> Optional[Dict[str, Any]]:
        """Detect Cargo version."""
        output = self._run_command(["cargo", "--version"])
        if not output:
            return None

        # Cargo output: "cargo 1.71.0 (cfd3bbd8f 2023-06-08)"
        version = self._extract_version(output, [r"cargo (\d+\.\d+\.\d+)"])
        if version:
            return {
                "version": version,
                "command": "cargo --version",
                "path": shutil.which("cargo"),
            }
        return None

    def _detect_go(self) -> Optional[Dict[str, Any]]:
        """Detect Go version."""
        output = self._run_command(["go", "version"])
        if not output:
            return None

        # Go output: "go version go1.21.0 linux/amd64"
        version = self._extract_version(output, [r"go(\d+\.\d+(?:\.\d+)?)"])
        if version:
            return {
                "version": version,
                "command": "go version",
                "path": shutil.which("go"),
            }
        return None

    def get_project_indicators(self) -> Dict[str, bool]:
        """Check which project types are indicated by files in the project."""
        indicators = {}

        # File-based project detection
        file_indicators = {
            "zig": ["build.zig", "build.zig.zon"],
            "gleam": ["gleam.toml"],
            "kotlin": ["build.gradle.kts", "build.gradle"],
            "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "node": ["package.json", "package-lock.json"],
            "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "go": ["go.mod", "go.sum"],
        }

        for tool, files in file_indicators.items():
            indicators[tool] = any(
                (self.project_path / file).exists() for file in files
            )

        return indicators

    def _detect_elixir(self) -> Optional[Dict[str, Any]]:
        """Detect Elixir version."""
        output = self._run_command(["elixir", "--version"])
        if not output:
            return None

        # Elixir output: "Erlang/OTP 25 [erts-13.0] [source] [64-bit] ..."
        # "Elixir 1.14.0 (compiled with Erlang/OTP 25)"
        version_match = re.search(r"Elixir (\d+\.\d+\.\d+)", output)
        if version_match:
            return {
                "version": version_match.group(1),
                "command": "elixir --version",
                "path": shutil.which("elixir"),
            }
        return None

    def _detect_erlang(self) -> Optional[Dict[str, Any]]:
        """Detect Erlang/OTP version."""
        output = self._run_command(["erl", "-eval", "halt()", "-noshell"])
        if not output:
            # Try alternative method
            output = self._run_command(["erl", "-version"])

        if not output:
            return None

        # Parse Erlang version from various formats
        version_patterns = [
            r"Erlang/OTP (\d+)",
            r"Eshell V(\d+\.\d+)",
            r"erl.*?(\d+\.\d+)",
        ]

        version = self._extract_version(output, version_patterns)
        if version:
            return {
                "version": version,
                "command": "erl -version",
                "path": shutil.which("erl"),
            }
        return None

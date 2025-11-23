"""
Fix Generator - Template-based system for generating version-agnostic fix suggestions.

This module provides a flexible, template-based approach to generating fix
suggestions that work across all versions and package systems without
hardcoded logic.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from string import Template

from .compatibility_engine import CompatibilityIssue, IssueSeverity
from .version_constraints import VersionParser, VersionComparator


class FixType(Enum):
    """Types of fixes that can be generated."""

    VERSION_INSTALL = "version_install"
    VERSION_SWITCH = "version_switch"
    PACKAGE_OVERRIDE = "package_override"
    CONFIG_CHANGE = "config_change"
    DEPENDENCY_UPDATE = "dependency_update"
    TEMPORARY_WORKAROUND = "temporary_workaround"
    ENVIRONMENT_SETUP = "environment_setup"


class RiskLevel(Enum):
    """Risk levels for fixes."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class FixSuggestion:
    """Represents a fix suggestion."""

    id: str
    description: str
    command: str
    fix_type: FixType
    risk_level: RiskLevel
    tool: str
    version_manager: Optional[str] = None
    alternatives: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    validation_steps: List[str] = field(default_factory=list)
    rollback_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FixTemplate:
    """Represents a fix template."""

    id: str
    description_template: str
    command_template: str
    fix_type: FixType
    risk_level: RiskLevel
    version_manager: Optional[str] = None
    prerequisites_template: List[str] = field(default_factory=list)
    validation_template: List[str] = field(default_factory=list)
    rollback_template: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)


class VersionManagerDetector:
    """Detects available version managers for different tools."""

    def __init__(self):
        self.version_managers = {
            "asdf": self._check_asdf,
            "uv": self._check_uv,
            "poetry": self._check_poetry,
            "pyenv": self._check_pyenv,
            "nvm": self._check_nvm,
            "rustup": self._check_rustup,
            "zigup": self._check_zigup,
            "gvm": self._check_gvm,
            "kiex": self._check_kiex,
            "kerl": self._check_kerl,
        }

        # Tool-specific version managers
        self.tool_managers = {
            "python": ["asdf", "pyenv", "uv", "poetry"],
            "node": ["asdf", "nvm"],
            "rust": ["asdf", "rustup"],
            "elixir": ["asdf", "kiex"],
            "erlang": ["asdf", "kerl"],
            "zig": ["asdf", "zigup"],
            "go": ["asdf", "gvm"],
        }

    def detect_available(self) -> Dict[str, bool]:
        """Detect which version managers are available."""
        available = {}
        for name, checker in self.version_managers.items():
            available[name] = checker()
        return available

    def get_manager_for_tool(
        self, tool: str, available_managers: Dict[str, bool]
    ) -> Optional[str]:
        """Get the best available version manager for a tool."""
        tool_managers = self.tool_managers.get(tool, ["asdf"])

        for manager in tool_managers:
            if available_managers.get(manager, False):
                return manager

        return None

    def _check_asdf(self) -> bool:
        """Check if asdf is available."""
        import shutil

        return shutil.which("asdf") is not None

    def _check_uv(self) -> bool:
        """Check if uv is available."""
        import shutil

        return shutil.which("uv") is not None

    def _check_poetry(self) -> bool:
        """Check if poetry is available."""
        import shutil

        return shutil.which("poetry") is not None

    def _check_pyenv(self) -> bool:
        """Check if pyenv is available."""
        import shutil

        return shutil.which("pyenv") is not None

    def _check_nvm(self) -> bool:
        """Check if nvm is available."""
        return Path.home().joinpath(".nvm").exists()

    def _check_rustup(self) -> bool:
        """Check if rustup is available."""
        import shutil

        return shutil.which("rustup") is not None

    def _check_zigup(self) -> bool:
        """Check if zigup is available."""
        import shutil

        return shutil.which("zigup") is not None

    def _check_gvm(self) -> bool:
        """Check if gvm is available."""
        return Path.home().joinpath(".gvm").exists()

    def _check_kiex(self) -> bool:
        """Check if kiex is available."""
        import shutil

        return shutil.which("kiex") is not None

    def _check_kerl(self) -> bool:
        """Check if kerl is available."""
        import shutil

        return shutil.which("kerl") is not None


class FixGenerator:
    """Main fix generator using templates."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent / "config" / "compatibility_rules.yaml"
            )

        self.config = self._load_config(config_path)
        self.templates = self._load_fix_templates()
        self.version_manager_detector = VersionManagerDetector()
        self.available_managers = self.version_manager_detector.detect_available()
        self.version_parser = VersionParser()
        self.version_comparator = VersionComparator()

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return {}

    def _load_fix_templates(self) -> Dict[str, List[FixTemplate]]:
        """Load and parse fix templates from config."""
        templates = {}

        fix_templates_config = self.config.get("fix_templates", {})

        # Load version manager templates
        vm_templates = fix_templates_config.get("version_manager_install", {})
        for vm_name, vm_config in vm_templates.items():
            if vm_name == "asdf":
                template = FixTemplate(
                    id=f"asdf_install",
                    description_template=vm_config.get(
                        "description", "Install {tool} {version} via asdf"
                    ),
                    command_template=vm_config.get(
                        "command",
                        "asdf install {tool} {version} && asdf global {tool} {version}",
                    ),
                    fix_type=FixType.VERSION_INSTALL,
                    risk_level=RiskLevel(vm_config.get("risk_level", "low")),
                    version_manager="asdf",
                    parameters=["tool", "version"],
                )

                if "version_manager" not in templates:
                    templates["version_manager"] = []
                templates["version_manager"].append(template)

        # Load tool-specific templates
        tool_specific = fix_templates_config.get("tool_specific", {})
        for tool_name, tool_config in tool_specific.items():
            for vm_name, vm_config in tool_config.items():
                template = FixTemplate(
                    id=f"{tool_name}_{vm_name}_install",
                    description_template=vm_config.get(
                        "description", f"Install {tool_name} {{version}} via {vm_name}"
                    ),
                    command_template=vm_config.get(
                        "command", f"{vm_name} install {{version}}"
                    ),
                    fix_type=FixType.VERSION_INSTALL,
                    risk_level=RiskLevel(vm_config.get("risk_level", "low")),
                    version_manager=vm_name,
                    parameters=["version"],
                )

                tool_key = f"{tool_name}_install"
                if tool_key not in templates:
                    templates[tool_key] = []
                templates[tool_key].append(template)

        # Load package override templates
        package_templates = fix_templates_config.get("package_override", {})
        for template_name, template_config in package_templates.items():
            template = FixTemplate(
                id=template_name,
                description_template=template_config.get(
                    "description", "Override {package} dependency"
                ),
                command_template=template_config.get(
                    "command", "Update dependency in manifest"
                ),
                fix_type=FixType.PACKAGE_OVERRIDE,
                risk_level=RiskLevel(template_config.get("risk_level", "medium")),
                parameters=template_config.get("parameters", ["package"]),
            )

            if "package_override" not in templates:
                templates["package_override"] = []
            templates["package_override"].append(template)

        return templates

    def generate_fixes(
        self,
        issue: CompatibilityIssue,
        env_info: Dict[str, Any],
        manifests: Dict[str, Any],
    ) -> List[FixSuggestion]:
        """Generate fix suggestions for a compatibility issue."""
        fixes = []

        # Version-related fixes
        if issue.current_version and issue.required_version:
            version_fixes = self._generate_version_fixes(issue, env_info)
            fixes.extend(version_fixes)

        # Package-specific fixes
        if issue.affected_packages:
            package_fixes = self._generate_package_fixes(issue, manifests)
            fixes.extend(package_fixes)

        # Error pattern-based fixes
        if issue.error_patterns:
            pattern_fixes = self._generate_pattern_fixes(issue, env_info, manifests)
            fixes.extend(pattern_fixes)

        # Environment setup fixes
        if issue.severity == IssueSeverity.ERROR:
            env_fixes = self._generate_environment_fixes(issue, env_info)
            fixes.extend(env_fixes)

        return self._prioritize_fixes(fixes)

    def _generate_version_fixes(
        self, issue: CompatibilityIssue, env_info: Dict[str, Any]
    ) -> List[FixSuggestion]:
        """Generate version-related fixes."""
        fixes = []

        tool = issue.tool
        current_version = issue.current_version
        required_version = issue.required_version

        # Get best version manager for this tool
        best_manager = self.version_manager_detector.get_manager_for_tool(
            tool, self.available_managers
        )

        # Parse required version to determine target
        target_version = self._extract_target_version(required_version)

        if target_version:
            # Generate install/switch fix
            if best_manager:
                # Use tool-specific template if available
                tool_templates = self.templates.get(f"{tool}_install", [])
                manager_template = None

                for template in tool_templates:
                    if template.version_manager == best_manager:
                        manager_template = template
                        break

                if manager_template:
                    fix = self._create_fix_from_template(
                        manager_template,
                        {
                            "tool": tool,
                            "version": target_version,
                            "current_version": current_version,
                            "required_version": required_version,
                        },
                    )
                    fixes.append(fix)

                # Add alternative managers
                alternatives = self._generate_version_alternatives(
                    tool, target_version, best_manager
                )
                if fixes and alternatives:
                    fixes[0].alternatives = alternatives

            # Fallback to generic instructions
            if not fixes:
                generic_fix = FixSuggestion(
                    id=f"{tool}_manual_install",
                    description=f"Install {tool} {target_version} manually",
                    command=f"Visit official {tool} installation guide",
                    fix_type=FixType.ENVIRONMENT_SETUP,
                    risk_level=RiskLevel.MEDIUM,
                    tool=tool,
                    metadata={
                        "target_version": target_version,
                        "reason": "No suitable version manager found",
                    },
                )
                fixes.append(generic_fix)

        return fixes

    def _generate_package_fixes(
        self, issue: CompatibilityIssue, manifests: Dict[str, Any]
    ) -> List[FixSuggestion]:
        """Generate package-specific fixes."""
        fixes = []

        package_fixes_config = self.config.get("package_fixes", {}).get(issue.tool, {})

        for package_name in issue.affected_packages:
            if package_name in package_fixes_config:
                package_config = package_fixes_config[package_name]

                # Primary fix
                primary_fix = package_config.get("primary_fix", {})
                if primary_fix:
                    fix = self._create_package_fix(
                        issue.tool, package_name, primary_fix, "primary"
                    )
                    fixes.append(fix)

                    # Alternative fixes
                    alternatives = []
                    alt_fixes = package_config.get("alternative_fixes", [])
                    for alt_fix in alt_fixes:
                        alt_description = self._create_alternative_description(
                            alt_fix, package_name
                        )
                        alternatives.append(alt_description)

                    if alternatives:
                        fix.alternatives = alternatives

        return fixes

    def _generate_pattern_fixes(
        self,
        issue: CompatibilityIssue,
        env_info: Dict[str, Any],
        manifests: Dict[str, Any],
    ) -> List[FixSuggestion]:
        """Generate fixes based on error patterns."""
        fixes = []

        # Look for pattern-specific fixes in metadata
        if "detected_pattern" in issue.metadata:
            pattern_name = issue.metadata["detected_pattern"]

            # Check if we have specific fixes for this pattern
            if pattern_name == "module_attribute_injection":
                # This suggests an inflex-style issue
                fixes.extend(self._generate_package_fixes(issue, manifests))

        return fixes

    def _generate_environment_fixes(
        self, issue: CompatibilityIssue, env_info: Dict[str, Any]
    ) -> List[FixSuggestion]:
        """Generate environment setup fixes."""
        fixes = []

        tool = issue.tool

        # Check if tool is missing entirely
        if tool not in env_info or not env_info[tool].get("version"):
            # Generate installation fix
            best_manager = self.version_manager_detector.get_manager_for_tool(
                tool, self.available_managers
            )

            if best_manager:
                fix = FixSuggestion(
                    id=f"{tool}_install_missing",
                    description=f"Install {tool} (tool not found)",
                    command=f"Install {tool} using {best_manager}",
                    fix_type=FixType.ENVIRONMENT_SETUP,
                    risk_level=RiskLevel.LOW,
                    tool=tool,
                    version_manager=best_manager,
                    prerequisites=[f"Ensure {best_manager} is installed"],
                    validation_steps=[f"Run '{tool} --version' to verify installation"],
                )
                fixes.append(fix)

        return fixes

    def _create_fix_from_template(
        self, template: FixTemplate, parameters: Dict[str, str]
    ) -> FixSuggestion:
        """Create a fix suggestion from a template."""
        # Use Template for safe substitution
        desc_template = Template(template.description_template)
        cmd_template = Template(template.command_template)

        try:
            description = desc_template.safe_substitute(**parameters)
            command = cmd_template.safe_substitute(**parameters)
        except KeyError as e:
            # Fallback if substitution fails
            description = template.description_template
            command = template.command_template

        # Generate prerequisites, validation, and rollback steps
        prerequisites = []
        for prereq_template in template.prerequisites_template:
            prereq = Template(prereq_template).safe_substitute(**parameters)
            prerequisites.append(prereq)

        validation_steps = []
        for val_template in template.validation_template:
            val_step = Template(val_template).safe_substitute(**parameters)
            validation_steps.append(val_step)

        rollback_steps = []
        for rollback_template in template.rollback_template:
            rollback = Template(rollback_template).safe_substitute(**parameters)
            rollback_steps.append(rollback)

        return FixSuggestion(
            id=template.id,
            description=description,
            command=command,
            fix_type=template.fix_type,
            risk_level=template.risk_level,
            tool=parameters.get("tool", ""),
            version_manager=template.version_manager,
            prerequisites=prerequisites,
            validation_steps=validation_steps,
            rollback_steps=rollback_steps,
            metadata={"template_id": template.id, "parameters": parameters},
        )

    def _create_package_fix(
        self,
        tool: str,
        package_name: str,
        fix_config: Dict[str, Any],
        fix_category: str,
    ) -> FixSuggestion:
        """Create a package-specific fix."""
        fix_type = fix_config.get("type", "git_override")
        description = fix_config.get("description", f"Fix {package_name} compatibility")
        risk_level = RiskLevel(fix_config.get("risk_level", "low"))

        # Generate command based on fix type
        command = self._generate_package_command(tool, package_name, fix_config)

        return FixSuggestion(
            id=f"{tool}_{package_name}_{fix_type}",
            description=description,
            command=command,
            fix_type=FixType.PACKAGE_OVERRIDE,
            risk_level=risk_level,
            tool=tool,
            metadata={
                "package_name": package_name,
                "fix_config": fix_config,
                "fix_category": fix_category,
            },
        )

    def _generate_package_command(
        self, tool: str, package_name: str, fix_config: Dict[str, Any]
    ) -> str:
        """Generate package fix command based on tool and fix type."""
        fix_type = fix_config.get("type", "git_override")

        if tool == "elixir" and fix_type == "git_override":
            git_url = fix_config.get("git_url", "")
            ref = fix_config.get("ref", "master")
            return f'Add {{{package_name}, git: "{git_url}", ref: "{ref}", override: true}} to mix.exs deps'

        elif tool == "python" and fix_type == "version_pin":
            version = fix_config.get("version", "")
            return f"Pin {package_name} to version {version} in requirements.txt"

        elif tool == "node" and fix_type == "fork_replacement":
            fork_name = fix_config.get("fork_name", "")
            return f"Replace {package_name} with {fork_name} in package.json"

        # Generic fallback
        return f"Apply {fix_type} fix for {package_name}"

    def _create_alternative_description(
        self, alt_fix: Dict[str, Any], package_name: str
    ) -> str:
        """Create alternative fix description."""
        fix_type = alt_fix.get("type", "")
        description = alt_fix.get("description", "")

        if fix_type == "git_override":
            fork_name = alt_fix.get("fork_name", "alternative")
            return f"Use {fork_name} fork: {description}"
        elif fix_type == "version_downgrade":
            target_version = alt_fix.get("target_version", "")
            return f"Downgrade to {target_version}: {description}"
        elif fix_type == "temporary_removal":
            return f"Temporarily remove {package_name}: {description}"

        return description

    def _extract_target_version(self, required_version: str) -> Optional[str]:
        """Extract target version from requirement string."""
        if not required_version:
            return None

        # Remove operators to get base version
        cleaned = re.sub(r"^[~^<>=!]+", "", required_version.strip())

        # Normalize version format
        normalized = self.version_parser.normalize_version(cleaned)
        return normalized

    def _generate_version_alternatives(
        self, tool: str, target_version: str, primary_manager: str
    ) -> List[str]:
        """Generate alternative version management commands."""
        alternatives = []

        # Get available managers for this tool
        tool_managers = self.version_manager_detector.tool_managers.get(tool, [])

        for manager in tool_managers:
            if manager != primary_manager and self.available_managers.get(
                manager, False
            ):
                # Find template for this manager
                tool_templates = self.templates.get(f"{tool}_install", [])
                for template in tool_templates:
                    if template.version_manager == manager:
                        cmd = Template(template.command_template).safe_substitute(
                            version=target_version
                        )
                        alternatives.append(f"{manager}: {cmd}")
                        break

        return alternatives

    def _prioritize_fixes(self, fixes: List[FixSuggestion]) -> List[FixSuggestion]:
        """Prioritize fixes by risk level and effectiveness."""

        def fix_priority(fix: FixSuggestion) -> int:
            # Lower numbers = higher priority
            risk_priority = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3}

            type_priority = {
                FixType.VERSION_INSTALL: 1,
                FixType.VERSION_SWITCH: 2,
                FixType.PACKAGE_OVERRIDE: 3,
                FixType.CONFIG_CHANGE: 4,
                FixType.ENVIRONMENT_SETUP: 5,
                FixType.TEMPORARY_WORKAROUND: 6,
            }

            return risk_priority.get(fix.risk_level, 2) * 10 + type_priority.get(
                fix.fix_type, 5
            )

        return sorted(fixes, key=fix_priority)

    def generate_validation_command(self, fix: FixSuggestion) -> str:
        """Generate command to validate that a fix worked."""
        tool = fix.tool

        if fix.fix_type in [FixType.VERSION_INSTALL, FixType.VERSION_SWITCH]:
            return f"{tool} --version"

        elif fix.fix_type == FixType.PACKAGE_OVERRIDE:
            if tool == "elixir":
                return "mix deps.compile"
            elif tool == "python":
                return "pip install -r requirements.txt"
            elif tool == "node":
                return "npm install"
            elif tool == "rust":
                return "cargo check"

        return f"# Validate {tool} installation and configuration"

    def generate_rollback_command(self, fix: FixSuggestion) -> str:
        """Generate command to rollback a fix if needed."""
        if fix.rollback_steps:
            return "; ".join(fix.rollback_steps)

        tool = fix.tool
        version_manager = fix.version_manager

        if (
            fix.fix_type in [FixType.VERSION_INSTALL, FixType.VERSION_SWITCH]
            and version_manager
        ):
            if version_manager == "asdf":
                return f"asdf uninstall {tool} <version>; asdf global {tool} <previous_version>"
            elif version_manager in ["pyenv", "nvm", "rustup"]:
                return f"{version_manager} uninstall <version>"

        return "# Manual rollback required - check documentation"

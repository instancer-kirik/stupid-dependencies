"""
Compatibility Engine - Rule-based system for detecting compatibility issues.

This module provides a version-agnostic approach to detecting compatibility
issues by loading rules from configuration and applying them generically.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .version_constraints import VersionParser, VersionComparator, VersionConstraint


class IssueCategory(Enum):
    """Categories of compatibility issues."""

    COMPILATION_ERROR = "compilation_error"
    RUNTIME_REQUIREMENT = "runtime_requirement"
    LANGUAGE_FEATURE = "language_feature"
    DEPRECATION = "deprecation"
    SECURITY = "security"
    PERFORMANCE = "performance"


class IssueSeverity(Enum):
    """Severity levels for compatibility issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CompatibilityIssue:
    """Represents a detected compatibility issue."""

    id: str
    tool: str
    description: str
    severity: IssueSeverity
    category: IssueCategory
    current_version: Optional[str] = None
    required_version: Optional[str] = None
    affected_packages: List[str] = field(default_factory=list)
    error_patterns: List[str] = field(default_factory=list)
    fix_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompatibilityRule:
    """Represents a compatibility rule from configuration."""

    id: str
    tool: str
    description: str
    category: IssueCategory
    severity: IssueSeverity = IssueSeverity.ERROR
    affected_versions: Optional[Dict[str, str]] = None
    symptoms: List[str] = field(default_factory=list)
    causes: List[str] = field(default_factory=list)
    dependencies: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PackageIssue:
    """Represents a package-specific compatibility issue."""

    package_name: str
    tool: str
    issue_id: str
    description: str
    severity: IssueSeverity
    affects_versions: str  # "all", version constraint, or specific versions
    triggers_with: List[Dict[str, Any]] = field(default_factory=list)
    error_patterns: List[str] = field(default_factory=list)
    dependency_chain: List[str] = field(default_factory=list)


class CompatibilityEngine:
    """Main compatibility detection engine."""

    def __init__(self, config_path: Optional[Path] = None):
        self.version_parser = VersionParser()
        self.version_comparator = VersionComparator()

        # Load configuration
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent / "config" / "compatibility_rules.yaml"
            )

        self.config = self._load_config(config_path)
        self.rules = self._parse_rules()
        self.package_issues = self._parse_package_issues()
        self.detection_patterns = self._parse_detection_patterns()

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return {}

    def _parse_rules(self) -> Dict[str, List[CompatibilityRule]]:
        """Parse compatibility rules from config."""
        rules = {}

        tools_config = self.config.get("tools", {})
        for tool_name, tool_config in tools_config.items():
            tool_rules = []

            compatibility_rules = tool_config.get("compatibility_rules", [])
            for rule_data in compatibility_rules:
                try:
                    rule = CompatibilityRule(
                        id=rule_data["id"],
                        tool=tool_name,
                        description=rule_data["description"],
                        category=IssueCategory(
                            rule_data.get("category", "compilation_error")
                        ),
                        severity=IssueSeverity(rule_data.get("severity", "error")),
                        affected_versions=rule_data.get("affected_versions"),
                        symptoms=rule_data.get("symptoms", []),
                        causes=rule_data.get("causes", []),
                        dependencies=rule_data.get("dependencies", []),
                    )
                    tool_rules.append(rule)
                except Exception as e:
                    print(
                        f"Warning: Could not parse rule {rule_data.get('id', 'unknown')}: {e}"
                    )

            if tool_rules:
                rules[tool_name] = tool_rules

        return rules

    def _parse_package_issues(self) -> Dict[str, Dict[str, List[PackageIssue]]]:
        """Parse package-specific issues from config."""
        package_issues = {}

        tools_config = self.config.get("tools", {})
        for tool_name, tool_config in tools_config.items():
            tool_package_issues = {}

            package_issues_config = tool_config.get("package_issues", {})
            for package_name, issues_list in package_issues_config.items():
                package_issue_objects = []

                for issue_data in issues_list:
                    try:
                        issue = PackageIssue(
                            package_name=package_name,
                            tool=tool_name,
                            issue_id=issue_data["issue_id"],
                            description=issue_data["description"],
                            severity=IssueSeverity(issue_data.get("severity", "error")),
                            affects_versions=issue_data.get("affects_versions", "all"),
                            triggers_with=issue_data.get("triggers_with", []),
                            error_patterns=issue_data.get("error_patterns", []),
                            dependency_chain=issue_data.get("dependency_chain", []),
                        )
                        package_issue_objects.append(issue)
                    except Exception as e:
                        print(
                            f"Warning: Could not parse package issue for {package_name}: {e}"
                        )

                if package_issue_objects:
                    tool_package_issues[package_name] = package_issue_objects

            if tool_package_issues:
                package_issues[tool_name] = tool_package_issues

        return package_issues

    def _parse_detection_patterns(self) -> Dict[str, Any]:
        """Parse error detection patterns from config."""
        return self.config.get("detection_patterns", {})

    def check_compatibility(
        self,
        tool: str,
        current_version: Optional[str],
        manifests: Dict[str, Any],
        error_logs: List[str] = None,
    ) -> List[CompatibilityIssue]:
        """Check for compatibility issues with a specific tool."""
        issues = []

        # Check general compatibility rules
        issues.extend(self._check_general_rules(tool, current_version, manifests))

        # Check package-specific issues
        issues.extend(self._check_package_issues(tool, current_version, manifests))

        # Check error patterns if logs provided
        if error_logs:
            issues.extend(self._check_error_patterns(tool, error_logs, manifests))

        return issues

    def _check_general_rules(
        self, tool: str, current_version: Optional[str], manifests: Dict[str, Any]
    ) -> List[CompatibilityIssue]:
        """Check general compatibility rules for a tool."""
        issues = []

        if tool not in self.rules:
            return issues

        for rule in self.rules[tool]:
            # Check if rule applies to current version
            if self._rule_applies_to_version(rule, current_version):
                # Check if symptoms are present in manifests
                if self._symptoms_present(rule, manifests):
                    issue = CompatibilityIssue(
                        id=rule.id,
                        tool=tool,
                        description=rule.description,
                        severity=rule.severity,
                        category=rule.category,
                        current_version=current_version,
                        metadata={
                            "rule_id": rule.id,
                            "causes": rule.causes,
                            "symptoms": rule.symptoms,
                        },
                    )
                    issues.append(issue)

        return issues

    def _check_package_issues(
        self, tool: str, current_version: Optional[str], manifests: Dict[str, Any]
    ) -> List[CompatibilityIssue]:
        """Check package-specific compatibility issues."""
        issues = []

        if tool not in self.package_issues:
            return issues

        # Get dependencies from manifests
        dependencies = self._extract_dependencies(tool, manifests)

        for package_name, package_issues_list in self.package_issues[tool].items():
            # Check if this package is present in dependencies
            if not self._package_is_present(package_name, dependencies, manifests):
                continue

            for package_issue in package_issues_list:
                # Check if issue triggers with current tool version
                if self._package_issue_triggers(
                    package_issue, current_version, manifests
                ):
                    issue = CompatibilityIssue(
                        id=f"{tool}_{package_name}_{package_issue.issue_id}",
                        tool=tool,
                        description=f"{package_name}: {package_issue.description}",
                        severity=package_issue.severity,
                        category=IssueCategory.COMPILATION_ERROR,  # Default for package issues
                        current_version=current_version,
                        affected_packages=[package_name],
                        error_patterns=package_issue.error_patterns,
                        metadata={
                            "package_name": package_name,
                            "issue_id": package_issue.issue_id,
                            "dependency_chain": package_issue.dependency_chain,
                            "affects_versions": package_issue.affects_versions,
                        },
                    )
                    issues.append(issue)

        return issues

    def _check_error_patterns(
        self, tool: str, error_logs: List[str], manifests: Dict[str, Any]
    ) -> List[CompatibilityIssue]:
        """Check error logs against known patterns."""
        issues = []

        detection_patterns = self.detection_patterns.get("compilation_errors", {}).get(
            tool, {}
        )

        for pattern_name, pattern_config in detection_patterns.items():
            patterns = pattern_config.get("patterns", [])
            suggests_rules = pattern_config.get("suggests_rules", [])
            suggests_packages = pattern_config.get("suggests_packages", [])

            # Check if any error logs match these patterns
            for error_log in error_logs:
                for pattern in patterns:
                    if re.search(pattern, error_log, re.IGNORECASE):
                        # Create issue based on pattern match
                        issue = CompatibilityIssue(
                            id=f"{tool}_pattern_{pattern_name}",
                            tool=tool,
                            description=f"Detected {pattern_name} in error logs",
                            severity=IssueSeverity.ERROR,
                            category=IssueCategory.COMPILATION_ERROR,
                            error_patterns=[pattern],
                            affected_packages=suggests_packages,
                            metadata={
                                "detected_pattern": pattern_name,
                                "matched_pattern": pattern,
                                "suggests_rules": suggests_rules,
                                "error_snippet": error_log[:200],  # First 200 chars
                            },
                        )
                        issues.append(issue)
                        break  # Only report once per pattern type

        return issues

    def _rule_applies_to_version(
        self, rule: CompatibilityRule, current_version: Optional[str]
    ) -> bool:
        """Check if a rule applies to the current version."""
        if not rule.affected_versions or not current_version:
            return True  # Rule applies to all versions if not specified

        operator = rule.affected_versions.get("operator", ">=")
        target_version = rule.affected_versions.get("version", "0.0.0")

        constraint_str = f"{operator}{target_version}"
        constraint = self.version_parser.parse_constraint(constraint_str)

        if not constraint:
            return True  # If we can't parse, assume it applies

        return self.version_comparator.satisfies_constraint(current_version, constraint)

    def _symptoms_present(
        self, rule: CompatibilityRule, manifests: Dict[str, Any]
    ) -> bool:
        """Check if rule symptoms are present in manifests or environment."""
        if not rule.symptoms:
            return True  # No symptoms to check

        # For now, assume symptoms are present if rule applies
        # In a real implementation, this would check for specific conditions
        return True

    def _extract_dependencies(
        self, tool: str, manifests: Dict[str, Any]
    ) -> Dict[str, str]:
        """Extract dependencies from manifests for a given tool."""
        dependencies = {}

        # Tool-specific dependency extraction
        if tool == "elixir":
            mix_exs = manifests.get("mix.exs", {})
            deps = mix_exs.get("dependencies", {})
            for dep_name, dep_info in deps.items():
                if isinstance(dep_info, dict):
                    dependencies[dep_name] = dep_info.get("version", "*")
                else:
                    dependencies[dep_name] = str(dep_info)

            # Also check mix.lock for locked versions
            mix_lock = manifests.get("mix.lock", {})
            locked_deps = mix_lock.get("locked_dependencies", {})
            for dep_name, dep_info in locked_deps.items():
                if isinstance(dep_info, dict):
                    dependencies[dep_name] = dep_info.get("version", "*")

        elif tool == "python":
            # Check various Python manifest files
            for manifest_name in ["pyproject.toml", "requirements.txt", "Pipfile"]:
                manifest = manifests.get(manifest_name, {})
                deps = manifest.get("dependencies", {})
                dependencies.update(deps)

        elif tool == "node":
            package_json = manifests.get("package.json", {})
            deps = package_json.get("dependencies", {})
            dev_deps = package_json.get("devDependencies", {})
            dependencies.update(deps)
            dependencies.update(dev_deps)

        elif tool == "rust":
            cargo_toml = manifests.get("Cargo.toml", {})
            deps = cargo_toml.get("dependencies", {})
            dev_deps = cargo_toml.get("dev-dependencies", {})
            dependencies.update(deps)
            dependencies.update(dev_deps)

        return dependencies

    def _package_is_present(
        self, package_name: str, dependencies: Dict[str, str], manifests: Dict[str, Any]
    ) -> bool:
        """Check if a package is present in dependencies."""
        # Direct dependency check
        if package_name in dependencies:
            return True

        # Check for transitive dependencies in lock files
        # This is a simplified check - in practice, you'd parse lock files more thoroughly
        for manifest_name, manifest_data in manifests.items():
            if "lock" in manifest_name.lower():
                locked_deps = manifest_data.get("locked_dependencies", {})
                if package_name in locked_deps:
                    return True

        return False

    def _package_issue_triggers(
        self,
        package_issue: PackageIssue,
        current_version: Optional[str],
        manifests: Dict[str, Any],
    ) -> bool:
        """Check if a package issue should trigger given current conditions."""
        if not package_issue.triggers_with:
            return True  # Always triggers if no conditions specified

        for trigger_condition in package_issue.triggers_with:
            trigger_tool = trigger_condition.get("tool")
            version_constraint = trigger_condition.get("version_constraint")

            if trigger_tool and version_constraint and current_version:
                constraint = self.version_parser.parse_constraint(version_constraint)
                if constraint and self.version_comparator.satisfies_constraint(
                    current_version, constraint
                ):
                    return True

        return False

    def get_fix_suggestions(self, issue: CompatibilityIssue) -> List[Dict[str, Any]]:
        """Get fix suggestions for a compatibility issue."""
        suggestions = []

        # Get fix suggestions from package fixes database
        package_fixes = self.config.get("package_fixes", {}).get(issue.tool, {})

        for package_name in issue.affected_packages:
            if package_name in package_fixes:
                package_fix = package_fixes[package_name]

                # Primary fix
                primary_fix = package_fix.get("primary_fix", {})
                if primary_fix:
                    suggestions.append(
                        {
                            "type": "primary",
                            "description": primary_fix.get("description", ""),
                            "fix_type": primary_fix.get("type", ""),
                            "details": primary_fix,
                            "risk_level": "low",
                        }
                    )

                # Alternative fixes
                alternative_fixes = package_fix.get("alternative_fixes", [])
                for alt_fix in alternative_fixes:
                    suggestions.append(
                        {
                            "type": "alternative",
                            "description": alt_fix.get("description", ""),
                            "fix_type": alt_fix.get("type", ""),
                            "details": alt_fix,
                            "risk_level": alt_fix.get("risk_level", "medium"),
                        }
                    )

        return suggestions

    def analyze_environment_compatibility(
        self,
        env_info: Dict[str, Any],
        manifests: Dict[str, Any],
        error_logs: List[str] = None,
    ) -> Dict[str, List[CompatibilityIssue]]:
        """Analyze compatibility across all detected tools in environment."""
        all_issues = {}

        for tool, tool_info in env_info.items():
            if tool_info and "version" in tool_info:
                current_version = tool_info["version"]
                issues = self.check_compatibility(
                    tool, current_version, manifests, error_logs
                )
                if issues:
                    all_issues[tool] = issues

        return all_issues

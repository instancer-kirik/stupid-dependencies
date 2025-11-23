"""
Version-Agnostic Dependency Solver - Refactored to use rule-based compatibility engine.

This is a complete rewrite of the solver that removes all hardcoded version logic
and uses the new compatibility engine, version constraints, and fix generator.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .compatibility_engine import CompatibilityEngine, CompatibilityIssue, IssueSeverity
from .fix_generator import FixGenerator, FixSuggestion, RiskLevel
from .version_constraints import (
    VersionParser,
    VersionComparator,
    VersionConstraintResolver,
)
from .manifest_parser import ManifestParser
from .env_detector import EnvironmentDetector


@dataclass
class ConflictV2:
    """Modern conflict representation with enhanced metadata."""

    id: str
    tool: str
    severity: str
    category: str
    message: str
    description: str
    current_version: Optional[str] = None
    required_version: Optional[str] = None
    affected_packages: List[str] = field(default_factory=list)
    error_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Legacy compatibility
    @property
    def reason(self) -> str:
        return self.description

    @property
    def details(self) -> str:
        return self.metadata.get("details", self.description)


@dataclass
class FixV2:
    """Modern fix representation with enhanced features."""

    id: str
    description: str
    command: str
    risk_level: str
    tool: str
    action_type: str
    version_manager: Optional[str] = None
    alternatives: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    validation_steps: List[str] = field(default_factory=list)
    rollback_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VersionAgnosticSolver:
    """
    Version-agnostic dependency solver that uses rule-based compatibility detection.

    This solver doesn't contain any hardcoded version checks or tool-specific logic.
    All compatibility rules are loaded from configuration files.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the version-agnostic solver."""
        # Core engines
        self.compatibility_engine = CompatibilityEngine(config_path)
        self.fix_generator = FixGenerator(config_path)
        self.version_parser = VersionParser()
        self.version_comparator = VersionComparator()
        self.version_resolver = VersionConstraintResolver()

        # Detectors
        self.env_detector = EnvironmentDetector()

        # Cache for performance
        self._env_cache = None
        self._manifest_cache = {}

    def find_conflicts(
        self, project_path: Path, error_logs: List[str] = None
    ) -> List[ConflictV2]:
        """
        Find compatibility conflicts in a project.

        Args:
            project_path: Path to the project directory
            error_logs: Optional list of error log strings to analyze

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Detect environment
        env_info = self._get_environment_info()

        # Parse project manifests
        manifests = self._parse_manifests(project_path)

        # Run compatibility analysis
        compatibility_issues = (
            self.compatibility_engine.analyze_environment_compatibility(
                env_info, manifests, error_logs
            )
        )

        # Convert compatibility issues to conflicts
        for tool, issues in compatibility_issues.items():
            for issue in issues:
                conflict = self._convert_issue_to_conflict(issue)
                conflicts.append(conflict)

        return conflicts

    def suggest_fixes(
        self, conflicts: List[ConflictV2], project_path: Path
    ) -> Dict[str, List[FixV2]]:
        """
        Suggest fixes for detected conflicts.

        Args:
            conflicts: List of conflicts to fix
            project_path: Path to the project directory

        Returns:
            Dictionary mapping conflict IDs to lists of fix suggestions
        """
        fix_suggestions = {}

        # Get environment and manifest info for context
        env_info = self._get_environment_info()
        manifests = self._parse_manifests(project_path)

        for conflict in conflicts:
            # Convert conflict back to compatibility issue for fix generation
            issue = self._convert_conflict_to_issue(conflict)

            # Generate fixes
            fixes = self.fix_generator.generate_fixes(issue, env_info, manifests)

            # Convert to FixV2 format
            fix_v2_list = [self._convert_fix_to_v2(fix) for fix in fixes]

            if fix_v2_list:
                fix_suggestions[conflict.id] = fix_v2_list

        return fix_suggestions

    def analyze_project(
        self, project_path: Path, error_logs: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive project analysis.

        Args:
            project_path: Path to the project directory
            error_logs: Optional error logs to analyze

        Returns:
            Complete analysis report
        """
        # Find conflicts
        conflicts = self.find_conflicts(project_path, error_logs)

        # Generate fix suggestions
        fix_suggestions = self.suggest_fixes(conflicts, project_path)

        # Get environment and manifest info
        env_info = self._get_environment_info()
        manifests = self._parse_manifests(project_path)

        # Analyze version constraints
        constraint_analysis = self._analyze_version_constraints(manifests, env_info)

        return {
            "project_path": str(project_path),
            "environment": env_info,
            "manifests": manifests,
            "conflicts": [self._conflict_to_dict(c) for c in conflicts],
            "fix_suggestions": {
                conflict_id: [self._fix_to_dict(f) for f in fixes]
                for conflict_id, fixes in fix_suggestions.items()
            },
            "version_constraints": constraint_analysis,
            "summary": self._generate_summary(conflicts, fix_suggestions),
        }

    def check_tool_compatibility(
        self, tool: str, current_version: Optional[str], project_path: Path
    ) -> List[ConflictV2]:
        """
        Check compatibility for a specific tool.

        Args:
            tool: Tool name to check
            current_version: Current version of the tool
            project_path: Path to project directory

        Returns:
            List of conflicts for this tool
        """
        manifests = self._parse_manifests(project_path)

        # Create minimal env info for this tool
        env_info = {tool: {"version": current_version}} if current_version else {}

        # Check compatibility
        issues = self.compatibility_engine.check_compatibility(
            tool, current_version, manifests
        )

        # Convert to conflicts
        return [self._convert_issue_to_conflict(issue) for issue in issues]

    def validate_fix(self, fix: FixV2, project_path: Path) -> Dict[str, Any]:
        """
        Validate that a fix can be applied safely.

        Args:
            fix: Fix to validate
            project_path: Project path for context

        Returns:
            Validation result with recommendations
        """
        validation_result = {
            "fix_id": fix.id,
            "can_apply": True,
            "warnings": [],
            "prerequisites_met": True,
            "missing_prerequisites": [],
            "estimated_risk": fix.risk_level,
            "validation_steps": fix.validation_steps,
        }

        # Check prerequisites
        for prereq in fix.prerequisites:
            if not self._check_prerequisite(prereq):
                validation_result["prerequisites_met"] = False
                validation_result["missing_prerequisites"].append(prereq)

        # Check if version manager is available
        if fix.version_manager:
            if not self._check_version_manager_available(fix.version_manager):
                validation_result["can_apply"] = False
                validation_result["warnings"].append(
                    f"Version manager {fix.version_manager} not available"
                )

        # Risk assessment
        if fix.risk_level == "high":
            validation_result["warnings"].append(
                "High risk fix - backup project before applying"
            )

        return validation_result

    def get_version_suggestions(
        self, tool: str, constraints: List[str], project_path: Path
    ) -> Dict[str, Any]:
        """
        Get version suggestions for a tool given constraints.

        Args:
            tool: Tool name
            constraints: List of version constraints
            project_path: Project path

        Returns:
            Version suggestions and compatibility info
        """
        env_info = self._get_environment_info()
        current_version = env_info.get(tool, {}).get("version")

        # Use version resolver to suggest compatible versions
        suggestions = self.version_resolver.suggest_version_resolution(
            current_version, constraints, available_versions=None
        )

        return {
            "tool": tool,
            "current_version": current_version,
            "constraints": constraints,
            "suggestions": suggestions,
            "compatibility_notes": self._get_compatibility_notes(tool, suggestions),
        }

    # Private helper methods

    def _get_environment_info(self) -> Dict[str, Any]:
        """Get cached environment information."""
        if self._env_cache is None:
            self._env_cache = self.env_detector.detect_all()
        return self._env_cache

    def _parse_manifests(self, project_path: Path) -> Dict[str, Any]:
        """Get cached manifest information."""
        path_key = str(project_path)
        if path_key not in self._manifest_cache:
            parser = ManifestParser(project_path)
            self._manifest_cache[path_key] = parser.parse_all()
        return self._manifest_cache[path_key]

    def _convert_issue_to_conflict(self, issue: CompatibilityIssue) -> ConflictV2:
        """Convert CompatibilityIssue to ConflictV2."""
        return ConflictV2(
            id=issue.id,
            tool=issue.tool,
            severity=issue.severity.value,
            category=issue.category.value,
            message=issue.description,
            description=issue.description,
            current_version=issue.current_version,
            required_version=issue.required_version,
            affected_packages=issue.affected_packages,
            error_patterns=issue.error_patterns,
            metadata=issue.metadata,
        )

    def _convert_conflict_to_issue(self, conflict: ConflictV2) -> CompatibilityIssue:
        """Convert ConflictV2 back to CompatibilityIssue."""
        from .compatibility_engine import IssueCategory, IssueSeverity

        return CompatibilityIssue(
            id=conflict.id,
            tool=conflict.tool,
            description=conflict.description,
            severity=IssueSeverity(conflict.severity),
            category=IssueCategory(conflict.category),
            current_version=conflict.current_version,
            required_version=conflict.required_version,
            affected_packages=conflict.affected_packages,
            error_patterns=conflict.error_patterns,
            metadata=conflict.metadata,
        )

    def _convert_fix_to_v2(self, fix: FixSuggestion) -> FixV2:
        """Convert FixSuggestion to FixV2."""
        return FixV2(
            id=fix.id,
            description=fix.description,
            command=fix.command,
            risk_level=fix.risk_level.value,
            tool=fix.tool,
            action_type=fix.fix_type.value,
            version_manager=fix.version_manager,
            alternatives=fix.alternatives,
            prerequisites=fix.prerequisites,
            validation_steps=fix.validation_steps,
            rollback_steps=fix.rollback_steps,
            metadata=fix.metadata,
        )

    def _analyze_version_constraints(
        self, manifests: Dict[str, Any], env_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze version constraints across all manifest files."""
        constraint_analysis = {}

        for manifest_name, manifest_data in manifests.items():
            if isinstance(manifest_data, dict) and "type" in manifest_data:
                tool_type = manifest_data["type"]

                # Extract version requirements
                version_requirements = self._extract_version_requirements(
                    tool_type, manifest_data
                )

                if version_requirements:
                    constraint_analysis[manifest_name] = {
                        "tool_type": tool_type,
                        "requirements": version_requirements,
                        "current_satisfaction": self._check_requirements_satisfaction(
                            version_requirements, env_info
                        ),
                    }

        return constraint_analysis

    def _extract_version_requirements(
        self, tool_type: str, manifest_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Extract version requirements from manifest data."""
        requirements = {}

        version_fields = {
            "python": ["python_version"],
            "node": ["node_version", "npm_version"],
            "rust": ["rust_version"],
            "elixir": ["elixir_version"],
            "go": ["go_version"],
            "java": ["java_version"],
            "kotlin": ["kotlin_version"],
        }

        fields = version_fields.get(tool_type, [])
        for field in fields:
            if field in manifest_data and manifest_data[field]:
                requirements[field] = manifest_data[field]

        return requirements

    def _check_requirements_satisfaction(
        self, requirements: Dict[str, str], env_info: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check if current environment satisfies requirements."""
        satisfaction = {}

        for req_name, req_constraint in requirements.items():
            # Map requirement names to environment keys
            tool_mapping = {
                "python_version": "python",
                "node_version": "node",
                "npm_version": "npm",
                "rust_version": "rust",
                "elixir_version": "elixir",
                "go_version": "go",
                "java_version": "java",
                "kotlin_version": "kotlin",
            }

            tool_key = tool_mapping.get(req_name)
            if tool_key and tool_key in env_info:
                current_version = env_info[tool_key].get("version")
                if current_version:
                    constraint = self.version_parser.parse_constraint(req_constraint)
                    if constraint:
                        satisfaction[req_name] = (
                            self.version_comparator.satisfies_constraint(
                                current_version, constraint
                            )
                        )
                    else:
                        satisfaction[req_name] = False
                else:
                    satisfaction[req_name] = False
            else:
                satisfaction[req_name] = False

        return satisfaction

    def _generate_summary(
        self, conflicts: List[ConflictV2], fix_suggestions: Dict[str, List[FixV2]]
    ) -> Dict[str, Any]:
        """Generate analysis summary."""
        total_conflicts = len(conflicts)
        errors = len([c for c in conflicts if c.severity == "error"])
        warnings = len([c for c in conflicts if c.severity == "warning"])

        tools_with_issues = set(c.tool for c in conflicts)
        fixable_conflicts = len(fix_suggestions)

        return {
            "total_conflicts": total_conflicts,
            "errors": errors,
            "warnings": warnings,
            "tools_affected": list(tools_with_issues),
            "fixable_conflicts": fixable_conflicts,
            "auto_fixable": len(
                [
                    fixes
                    for fixes in fix_suggestions.values()
                    if any(f.risk_level == "low" for f in fixes)
                ]
            ),
            "needs_attention": total_conflicts - fixable_conflicts,
        }

    def _conflict_to_dict(self, conflict: ConflictV2) -> Dict[str, Any]:
        """Convert conflict to dictionary for serialization."""
        return {
            "id": conflict.id,
            "tool": conflict.tool,
            "severity": conflict.severity,
            "category": conflict.category,
            "message": conflict.message,
            "description": conflict.description,
            "current_version": conflict.current_version,
            "required_version": conflict.required_version,
            "affected_packages": conflict.affected_packages,
            "error_patterns": conflict.error_patterns,
            "metadata": conflict.metadata,
        }

    def _fix_to_dict(self, fix: FixV2) -> Dict[str, Any]:
        """Convert fix to dictionary for serialization."""
        return {
            "id": fix.id,
            "description": fix.description,
            "command": fix.command,
            "risk_level": fix.risk_level,
            "tool": fix.tool,
            "action_type": fix.action_type,
            "version_manager": fix.version_manager,
            "alternatives": fix.alternatives,
            "prerequisites": fix.prerequisites,
            "validation_steps": fix.validation_steps,
            "rollback_steps": fix.rollback_steps,
            "metadata": fix.metadata,
        }

    def _check_prerequisite(self, prerequisite: str) -> bool:
        """Check if a prerequisite is met."""
        # Simple check for common prerequisites
        if "install" in prerequisite.lower() and any(
            tool in prerequisite.lower() for tool in ["asdf", "pyenv", "nvm", "rustup"]
        ):
            # Check if version manager is available
            tool_name = next(
                (
                    tool
                    for tool in ["asdf", "pyenv", "nvm", "rustup"]
                    if tool in prerequisite.lower()
                ),
                None,
            )
            return (
                self._check_version_manager_available(tool_name) if tool_name else False
            )

        return True  # Assume other prerequisites are met

    def _check_version_manager_available(self, version_manager: str) -> bool:
        """Check if a version manager is available."""
        return self.fix_generator.available_managers.get(version_manager, False)

    def _get_compatibility_notes(
        self, tool: str, suggestions: Dict[str, Any]
    ) -> List[str]:
        """Get compatibility notes for version suggestions."""
        notes = []

        if suggestions.get("issues"):
            notes.append(
                f"Current version has compatibility issues with project requirements"
            )

        if suggestions.get("compatible_versions"):
            count = len(suggestions["compatible_versions"])
            notes.append(f"Found {count} compatible versions available")

        if suggestions.get("recommendations"):
            for rec in suggestions["recommendations"]:
                if rec.get("type") == "upgrade":
                    notes.append(f"Recommend upgrading to {rec.get('target_version')}")
                elif rec.get("type") == "keep_current":
                    notes.append("Current version is compatible")

        return notes


# Backward compatibility wrapper
class DependencySolver(VersionAgnosticSolver):
    """Backward compatibility wrapper for the original DependencySolver interface."""

    def __init__(self):
        super().__init__()

    def find_conflicts(
        self, project_path: Path, error_logs: List[str] = None
    ) -> List[ConflictV2]:
        """Legacy interface compatibility."""
        return super().find_conflicts(project_path, error_logs)

    def suggest_fixes(
        self, conflicts: List[ConflictV2], project_path: Path
    ) -> List[FixV2]:
        """Legacy interface - returns flat list of fixes."""
        fix_dict = super().suggest_fixes(conflicts, project_path)
        all_fixes = []
        for fixes in fix_dict.values():
            all_fixes.extend(fixes)
        return all_fixes

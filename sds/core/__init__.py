"""
SDS Core - The heart of the Version-Agnostic Dependency Solver.

This package contains the core functionality for universal compatibility detection,
version constraint parsing, and intelligent fix generation across all languages
and package managers without hardcoded assumptions.

Components:
- VersionAgnosticSolver: Main solver with rule-based compatibility detection
- CompatibilityEngine: Rule-based issue detection from configuration
- FixGenerator: Template-based fix suggestion system
- VersionConstraints: Universal version parsing and comparison
- ManifestParser: Multi-format project file parsing
- EnvironmentDetector: Development environment detection
"""

# Version-agnostic core components (primary API)
from .solver_v2 import VersionAgnosticSolver, ConflictV2, FixV2
from .compatibility_engine import (
    CompatibilityEngine,
    CompatibilityIssue,
    CompatibilityRule,
    PackageIssue,
    IssueCategory,
    IssueSeverity,
)
from .fix_generator import (
    FixGenerator,
    FixSuggestion,
    FixTemplate,
    FixType,
    RiskLevel,
    VersionManagerDetector,
)
from .version_constraints import (
    VersionParser,
    VersionComparator,
    VersionConstraintResolver,
    VersionConstraint,
    ConstraintType,
    parse_constraint,
    version_satisfies,
    compare_versions,
)

# Shared utilities
from .env_detector import EnvironmentDetector
from .manifest_parser import ManifestParser
from .fixer import ProjectFixer
from .package_client import PackageRepositoryClient

# Legacy components (for backward compatibility)
from .solver import DependencySolver as LegacyDependencySolver, Conflict, Fix

__all__ = [
    # Primary version-agnostic API
    "VersionAgnosticSolver",
    "ConflictV2",
    "FixV2",
    # Compatibility engine
    "CompatibilityEngine",
    "CompatibilityIssue",
    "CompatibilityRule",
    "PackageIssue",
    "IssueCategory",
    "IssueSeverity",
    # Fix generation
    "FixGenerator",
    "FixSuggestion",
    "FixTemplate",
    "FixType",
    "RiskLevel",
    "VersionManagerDetector",
    # Version constraints
    "VersionParser",
    "VersionComparator",
    "VersionConstraintResolver",
    "VersionConstraint",
    "ConstraintType",
    "parse_constraint",
    "version_satisfies",
    "compare_versions",
    # Shared utilities
    "EnvironmentDetector",
    "ManifestParser",
    "ProjectFixer",
    "PackageRepositoryClient",
    # Legacy compatibility
    "LegacyDependencySolver",
    "Conflict",
    "Fix",
]

# Module metadata
__version__ = "2.0.0"
__description__ = "Version-agnostic dependency solver core components"

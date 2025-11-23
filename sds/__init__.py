"""
SDS - Version-Agnostic Dependency Solver

Universal project doctor that works with ANY language, ANY version, ANY package manager
without hardcoded assumptions. Detect compatibility issues and get intelligent fix
suggestions across Python, Elixir, Node.js, Rust, Go, Java, Kotlin, Zig, and more.

Key Features:
- Rule-based compatibility detection from configuration
- Universal version constraint parsing across all ecosystems
- Template-based fix generation with risk assessment
- Future-proof design that works with unknown versions
- Multi-language support without tool-specific code
- Community-contributable compatibility knowledge base

Usage:
    from sds import VersionAgnosticSolver

    solver = VersionAgnosticSolver()
    conflicts = solver.find_conflicts(project_path)
    fixes = solver.suggest_fixes(conflicts, project_path)

CLI:
    sds analyze              # Comprehensive project analysis
    sds check                # Find compatibility conflicts
    sds fix                  # Show/apply fix suggestions
    sds validate <tool>      # Check tool compatibility
"""

__version__ = "2.0.0"
__author__ = "SDS Team"
__description__ = "Version-Agnostic Dependency Solver - Universal project doctor"

# Version-agnostic core (primary API)
from .core.solver_v2 import VersionAgnosticSolver, ConflictV2, FixV2
from .core.compatibility_engine import CompatibilityEngine, CompatibilityIssue
from .core.fix_generator import FixGenerator, FixSuggestion
from .core.version_constraints import (
    VersionParser,
    VersionComparator,
    VersionConstraint,
    parse_constraint,
    version_satisfies,
    compare_versions,
)

# Legacy compatibility (for existing code)
from .core.solver import DependencySolver as LegacyDependencySolver
from .core.env_detector import EnvironmentDetector
from .core.manifest_parser import ManifestParser
from .core.fixer import ProjectFixer

# Aliases for backward compatibility
DependencySolver = VersionAgnosticSolver  # Primary solver is now version-agnostic
Conflict = ConflictV2
Fix = FixV2

__all__ = [
    # Primary version-agnostic API
    "VersionAgnosticSolver",
    "CompatibilityEngine",
    "FixGenerator",
    "ConflictV2",
    "FixV2",
    "CompatibilityIssue",
    "FixSuggestion",
    # Version constraint system
    "VersionParser",
    "VersionComparator",
    "VersionConstraint",
    "parse_constraint",
    "version_satisfies",
    "compare_versions",
    # Common utilities
    "EnvironmentDetector",
    "ManifestParser",
    # Backward compatibility aliases
    "DependencySolver",
    "Conflict",
    "Fix",
    "ProjectFixer",
    "LegacyDependencySolver",
]

# Version information
VERSION_INFO = {
    "version": __version__,
    "major": 2,
    "minor": 0,
    "patch": 0,
    "type": "version-agnostic",
    "features": [
        "Universal language support",
        "Rule-based compatibility detection",
        "Template-based fix generation",
        "Future-proof version constraints",
        "Configuration-driven issue detection",
        "Multi-ecosystem compatibility",
    ],
}

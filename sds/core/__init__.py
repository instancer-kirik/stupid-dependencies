"""
SDS Core - The heart of the Stupid Dependency Solver.

This package contains the core functionality for detecting environment
inconsistencies and suggesting fixes.
"""

from .env_detector import EnvironmentDetector
from .manifest_parser import ManifestParser
from .solver import DependencySolver, Conflict, Fix
from .fixer import ProjectFixer
from .package_client import PackageRepositoryClient

__all__ = [
    "EnvironmentDetector",
    "ManifestParser",
    "DependencySolver",
    "Conflict",
    "Fix",
    "ProjectFixer",
    "PackageRepositoryClient",
]

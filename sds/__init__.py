"""
SDS - Stupid Dependency Solver

A doctor for your project that speaks Zig, Gleam, Kotlin, and common sense.

This package provides tools to detect dependency and environment inconsistencies
and help you get back to a buildable state without reinventing your toolchain.
"""

__version__ = "0.1.0"
__author__ = "SDS Team"
__description__ = "A doctor for your project dependencies"

from .core import (
    EnvironmentDetector,
    ManifestParser,
    DependencySolver,
    Conflict,
    Fix,
    ProjectFixer,
)

__all__ = [
    "EnvironmentDetector",
    "ManifestParser",
    "DependencySolver",
    "Conflict",
    "Fix",
    "ProjectFixer",
]

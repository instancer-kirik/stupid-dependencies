"""
Version Constraints System - Generic version constraint parsing and evaluation.

This module provides version-agnostic constraint handling that works across
all package managers and tools without hardcoded version logic.
"""

import re
from typing import Dict, List, Optional, Tuple, Union, Any
from packaging import version as pkg_version
from packaging.specifiers import SpecifierSet, InvalidSpecifier
import semver
from dataclasses import dataclass
from enum import Enum


class ConstraintType(Enum):
    """Types of version constraints."""

    EXACT = "exact"
    GREATER = "greater"
    GREATER_EQUAL = "greater_equal"
    LESS = "less"
    LESS_EQUAL = "less_equal"
    COMPATIBLE = "compatible"  # ~> in Elixir, ^ in npm
    TILDE = "tilde"  # ~ in npm
    RANGE = "range"
    ANY = "any"


@dataclass
class VersionConstraint:
    """Represents a version constraint."""

    type: ConstraintType
    version: str
    original: str
    operator: str = ""

    def __str__(self) -> str:
        return self.original


class VersionParser:
    """Parses version strings and constraints from different ecosystems."""

    def __init__(self):
        # Operator patterns ordered by specificity (longer first)
        self.operators = {
            "~>": ConstraintType.COMPATIBLE,  # Elixir compatible release
            ">=": ConstraintType.GREATER_EQUAL,
            "<=": ConstraintType.LESS_EQUAL,
            "==": ConstraintType.EXACT,
            "!=": None,  # Not supported in basic constraint
            "^": ConstraintType.COMPATIBLE,  # npm caret
            "~": ConstraintType.TILDE,  # npm tilde
            ">": ConstraintType.GREATER,
            "<": ConstraintType.LESS,
            "=": ConstraintType.EXACT,
        }

        # Version normalization patterns
        self.version_patterns = {
            # Standard semver
            "semver": r"^(\d+)\.(\d+)\.(\d+)(?:-([^+]+))?(?:\+(.+))?$",
            # Loose semver (missing patch)
            "semver_loose": r"^(\d+)\.(\d+)(?:\.(\d+))?(?:-([^+]+))?(?:\+(.+))?$",
            # Major only
            "major_only": r"^(\d+)$",
            # Major.minor only
            "major_minor": r"^(\d+)\.(\d+)$",
        }

    def parse_constraint(self, constraint_str: str) -> Optional[VersionConstraint]:
        """Parse a version constraint string into a VersionConstraint object."""
        if not constraint_str or constraint_str.strip() == "*":
            return VersionConstraint(
                type=ConstraintType.ANY,
                version="*",
                original=constraint_str,
                operator="*",
            )

        constraint_str = constraint_str.strip()

        # Find the operator
        found_op = None
        found_type = None

        # Check operators in order of specificity
        for op, constraint_type in self.operators.items():
            if constraint_str.startswith(op):
                found_op = op
                found_type = constraint_type
                break

        if found_op:
            version_part = constraint_str[len(found_op) :].strip()
        else:
            # No operator means exact match
            found_op = "="
            found_type = ConstraintType.EXACT
            version_part = constraint_str

        # Normalize the version
        normalized_version = self.normalize_version(version_part)

        if not normalized_version:
            return None

        return VersionConstraint(
            type=found_type,
            version=normalized_version,
            original=constraint_str,
            operator=found_op,
        )

    def normalize_version(self, version_str: str) -> Optional[str]:
        """Normalize a version string to a consistent format."""
        if not version_str:
            return None

        version_str = version_str.strip()

        # Try different patterns
        for pattern_name, pattern in self.version_patterns.items():
            match = re.match(pattern, version_str)
            if match:
                groups = match.groups()
                major = groups[0]
                minor = groups[1] if len(groups) > 1 and groups[1] else "0"
                patch = groups[2] if len(groups) > 2 and groups[2] else "0"

                # Handle pre-release and build metadata if present
                prerelease = groups[3] if len(groups) > 3 and groups[3] else ""
                build = groups[4] if len(groups) > 4 and groups[4] else ""

                normalized = f"{major}.{minor}.{patch}"
                if prerelease:
                    normalized += f"-{prerelease}"
                if build:
                    normalized += f"+{build}"

                return normalized

        # If no pattern matches, return as-is if it looks like a version
        if re.match(r"^\d+", version_str):
            return version_str

        return None

    def extract_version_from_string(
        self, text: str, patterns: Dict[str, str]
    ) -> Optional[str]:
        """Extract version from text using provided patterns."""
        for pattern_name, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                return self.normalize_version(match.group(1))
        return None


class VersionComparator:
    """Compares versions and checks constraint satisfaction."""

    def __init__(self):
        self.parser = VersionParser()

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        Returns: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        try:
            # Try using packaging library first (handles most cases)
            v1 = pkg_version.parse(version1)
            v2 = pkg_version.parse(version2)

            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        except Exception:
            # Fallback to string comparison for non-standard versions
            return self._string_version_compare(version1, version2)

    def _string_version_compare(self, v1: str, v2: str) -> int:
        """Fallback version comparison using string parsing."""
        try:
            # Extract numeric parts
            v1_parts = [int(x) for x in re.findall(r"\d+", v1)]
            v2_parts = [int(x) for x in re.findall(r"\d+", v2)]

            # Pad to same length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for i in range(max_len):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1

            return 0
        except Exception:
            # Final fallback to lexical comparison
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            return 0

    def satisfies_constraint(self, version: str, constraint: VersionConstraint) -> bool:
        """Check if a version satisfies a constraint."""
        if constraint.type == ConstraintType.ANY:
            return True

        if not version or not constraint.version:
            return False

        try:
            comparison = self.compare_versions(version, constraint.version)

            if constraint.type == ConstraintType.EXACT:
                return comparison == 0
            elif constraint.type == ConstraintType.GREATER:
                return comparison > 0
            elif constraint.type == ConstraintType.GREATER_EQUAL:
                return comparison >= 0
            elif constraint.type == ConstraintType.LESS:
                return comparison < 0
            elif constraint.type == ConstraintType.LESS_EQUAL:
                return comparison <= 0
            elif constraint.type == ConstraintType.COMPATIBLE:
                return self._compatible_version(
                    version, constraint.version, constraint.operator
                )
            elif constraint.type == ConstraintType.TILDE:
                return self._tilde_version(version, constraint.version)

        except Exception:
            # If comparison fails, be conservative and return False
            return False

        return False

    def _compatible_version(
        self, version: str, constraint_version: str, operator: str
    ) -> bool:
        """Handle compatible version constraints (~> in Elixir, ^ in npm)."""
        try:
            v_parts = [int(x) for x in re.findall(r"\d+", version)]
            c_parts = [int(x) for x in re.findall(r"\d+", constraint_version)]

            if not v_parts or not c_parts:
                return False

            if operator == "~>":
                # Elixir ~> means >= constraint but < next significant version
                # ~> 1.4 means >= 1.4.0 and < 2.0.0
                # ~> 1.4.2 means >= 1.4.2 and < 1.5.0

                # Must be >= constraint
                if self.compare_versions(version, constraint_version) < 0:
                    return False

                # Find next significant version boundary
                if len(c_parts) == 1:
                    # ~> 1 means >= 1.0.0 and < 2.0.0
                    return v_parts[0] == c_parts[0]
                elif len(c_parts) == 2:
                    # ~> 1.4 means >= 1.4.0 and < 2.0.0
                    return v_parts[0] == c_parts[0]
                else:
                    # ~> 1.4.2 means >= 1.4.2 and < 1.5.0
                    return v_parts[0] == c_parts[0] and v_parts[1] == c_parts[1]

            elif operator == "^":
                # npm ^ means compatible within the same major version
                return (
                    v_parts[0] == c_parts[0]
                    and self.compare_versions(version, constraint_version) >= 0
                )

        except Exception:
            pass

        return False

    def _tilde_version(self, version: str, constraint_version: str) -> bool:
        """Handle tilde version constraints (~ in npm)."""
        try:
            # ~1.2.3 := >=1.2.3 <1.(2+1).0 := >=1.2.3 <1.3.0
            v_parts = [int(x) for x in re.findall(r"\d+", version)]
            c_parts = [int(x) for x in re.findall(r"\d+", constraint_version)]

            if not v_parts or not c_parts:
                return False

            # Must be >= constraint version
            if self.compare_versions(version, constraint_version) < 0:
                return False

            # Must be same major and minor
            if len(v_parts) >= 2 and len(c_parts) >= 2:
                return v_parts[0] == c_parts[0] and v_parts[1] == c_parts[1]
            elif len(c_parts) >= 1:
                return v_parts[0] == c_parts[0]

        except Exception:
            pass

        return False


class VersionConstraintResolver:
    """Resolves version constraints and finds compatible versions."""

    def __init__(self):
        self.parser = VersionParser()
        self.comparator = VersionComparator()

    def find_compatible_versions(
        self, available_versions: List[str], constraints: List[VersionConstraint]
    ) -> List[str]:
        """Find versions that satisfy all constraints."""
        compatible = []

        for version in available_versions:
            if self.version_satisfies_all_constraints(version, constraints):
                compatible.append(version)

        # Sort by version (newest first)
        try:
            compatible.sort(key=lambda x: pkg_version.parse(x), reverse=True)
        except Exception:
            # Fallback to simple sort
            compatible.sort(reverse=True)

        return compatible

    def version_satisfies_all_constraints(
        self, version: str, constraints: List[VersionConstraint]
    ) -> bool:
        """Check if a version satisfies all given constraints."""
        for constraint in constraints:
            if not self.comparator.satisfies_constraint(version, constraint):
                return False
        return True

    def suggest_version_resolution(
        self,
        current_version: Optional[str],
        required_constraints: List[str],
        available_versions: List[str] = None,
    ) -> Dict[str, Any]:
        """Suggest version resolution strategy."""
        result = {
            "current_version": current_version,
            "constraints": required_constraints,
            "compatible_versions": [],
            "recommendations": [],
            "issues": [],
        }

        # Parse constraints
        parsed_constraints = []
        for constraint_str in required_constraints:
            constraint = self.parser.parse_constraint(constraint_str)
            if constraint:
                parsed_constraints.append(constraint)
            else:
                result["issues"].append(f"Could not parse constraint: {constraint_str}")

        if not parsed_constraints:
            return result

        # Check current version against constraints
        if current_version:
            satisfies_all = self.version_satisfies_all_constraints(
                current_version, parsed_constraints
            )
            if satisfies_all:
                result["recommendations"].append(
                    {
                        "type": "keep_current",
                        "description": f"Current version {current_version} satisfies all constraints",
                        "action": "no_action_needed",
                    }
                )
            else:
                # Find which constraints are violated
                for constraint in parsed_constraints:
                    if not self.comparator.satisfies_constraint(
                        current_version, constraint
                    ):
                        result["issues"].append(
                            {
                                "constraint": str(constraint),
                                "current": current_version,
                                "issue": self._describe_constraint_violation(
                                    current_version, constraint
                                ),
                            }
                        )

        # Find compatible versions if available
        if available_versions:
            compatible = self.find_compatible_versions(
                available_versions, parsed_constraints
            )
            result["compatible_versions"] = compatible[:10]  # Top 10

            if compatible:
                newest_compatible = compatible[0]
                if not current_version or current_version != newest_compatible:
                    result["recommendations"].append(
                        {
                            "type": "upgrade",
                            "description": f"Upgrade to {newest_compatible}",
                            "target_version": newest_compatible,
                            "action": "version_change",
                        }
                    )

        return result

    def _describe_constraint_violation(
        self, version: str, constraint: VersionConstraint
    ) -> str:
        """Describe why a version violates a constraint."""
        comparison = self.comparator.compare_versions(version, constraint.version)

        if constraint.type == ConstraintType.EXACT:
            return f"requires exactly {constraint.version} but got {version}"
        elif constraint.type == ConstraintType.GREATER:
            return f"requires > {constraint.version} but got {version}"
        elif constraint.type == ConstraintType.GREATER_EQUAL:
            return f"requires >= {constraint.version} but got {version}"
        elif constraint.type == ConstraintType.LESS:
            return f"requires < {constraint.version} but got {version}"
        elif constraint.type == ConstraintType.LESS_EQUAL:
            return f"requires <= {constraint.version} but got {version}"
        elif constraint.type == ConstraintType.COMPATIBLE:
            return f"requires compatible with {constraint.version} but got {version}"
        elif constraint.type == ConstraintType.TILDE:
            return f"requires ~{constraint.version} but got {version}"

        return f"does not satisfy {constraint.original}"


# Convenience functions
def parse_constraint(constraint_str: str) -> Optional[VersionConstraint]:
    """Parse a version constraint string."""
    parser = VersionParser()
    return parser.parse_constraint(constraint_str)


def version_satisfies(version: str, constraint_str: str) -> bool:
    """Check if a version satisfies a constraint string."""
    parser = VersionParser()
    comparator = VersionComparator()

    constraint = parser.parse_constraint(constraint_str)
    if not constraint:
        return False

    return comparator.satisfies_constraint(version, constraint)


def compare_versions(version1: str, version2: str) -> int:
    """Compare two version strings."""
    comparator = VersionComparator()
    return comparator.compare_versions(version1, version2)

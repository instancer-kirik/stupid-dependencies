#!/usr/bin/env python3
"""
Setup script for SDS - Stupid Dependency Solver (Version-Agnostic)
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (
    (this_directory / "README_VERSION_AGNOSTIC.md").read_text()
    if (this_directory / "README_VERSION_AGNOSTIC.md").exists()
    else (this_directory / "README.md").read_text()
    if (this_directory / "README.md").exists()
    else ""
)


# Read version from the package
def get_version():
    version_file = this_directory / "sds" / "__init__.py"
    if version_file.exists():
        for line in version_file.read_text().splitlines():
            if line.startswith("__version__"):
                return line.split('"')[1]
    return "2.0.0"  # Version-agnostic major version


setup(
    name="stupid-dependencies",
    version=get_version(),
    author="SDS Team",
    author_email="sds@example.com",
    description="Version-Agnostic Dependency Solver - Universal project doctor for ANY language, ANY version",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/stupid-dependencies",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "toml>=0.10.2",
        "packaging>=21.0",
        "requests>=2.25.0",
        "PyYAML>=6.0",
        "semver>=2.13.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "pre-commit>=3.0.0",
        ],
        "full": [
            "rich>=12.0.0",  # Enhanced terminal output
            "tabulate>=0.9.0",  # Better table formatting
            "colorama>=0.4.4",  # Cross-platform colors
        ],
    },
    entry_points={
        "console_scripts": [
            # Version-agnostic CLI (primary)
            "sds=sds.cli_v2:main",
            "sds-v2=sds.cli_v2:main",
            # Legacy CLI (for compatibility)
            "stupid-dependencies=sds.cli:main",
            "stupid=sds.cli:main",
            "sds-legacy=sds.cli:main",
            # Convenience aliases
            "dependency-doctor=sds.cli_v2:main",
            "project-doctor=sds.cli_v2:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sds": [
            "config/*.yaml",
            "config/*.yml",
            "templates/*",
            "templates/**/*",
        ],
    },
    data_files=[
        ("share/sds/config", ["sds/config/compatibility_rules.yaml"]),
    ],
    project_urls={
        "Bug Reports": "https://github.com/example/stupid-dependencies/issues",
        "Source": "https://github.com/example/stupid-dependencies",
        "Documentation": "https://stupid-dependencies.readthedocs.io/",
        "Changelog": "https://github.com/example/stupid-dependencies/blob/main/CHANGELOG.md",
        "Demo": "https://github.com/example/stupid-dependencies/blob/main/demo_version_agnostic.py",
    },
    keywords=[
        "dependencies",
        "version-management",
        "toolchain",
        "compatibility",
        "universal",
        "python",
        "elixir",
        "nodejs",
        "rust",
        "go",
        "java",
        "kotlin",
        "zig",
        "gleam",
        "gradle",
        "maven",
        "npm",
        "cargo",
        "mix",
        "version-agnostic",
    ],
    zip_safe=False,  # Needed for config files to be accessible
)

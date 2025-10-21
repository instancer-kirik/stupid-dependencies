#!/usr/bin/env python3
"""
Setup script for SDS - Stupid Dependency Solver
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (
    (this_directory / "README.md").read_text()
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
    return "0.1.0"


setup(
    name="stupid-dependencies",
    version=get_version(),
    author="SDS Team",
    author_email="sds@example.com",
    description="A doctor for your project that speaks Zig, Gleam, Kotlin, and common sense",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/stupid-dependencies",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "toml>=0.10.2",
        "packaging>=21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stupid-dependencies=sds.cli:main",
            "stupid=sds.cli:main",
            "sds=sds.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sds": ["templates/*"],
    },
    project_urls={
        "Bug Reports": "https://github.com/example/stupid-dependencies/issues",
        "Source": "https://github.com/example/stupid-dependencies",
        "Documentation": "https://stupid-dependencies.readthedocs.io/",
    },
    keywords="dependencies version-management toolchain zig gleam kotlin gradle",
)

# Changelog

All notable changes to SDS (Stupid Dependency Solver) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and core architecture
- Command-line interface with `check`, `fix`, `snapshot`, `diff`, and `explain` commands
- Environment detection for multiple toolchains:
  - Zig (version detection, build.zig.zon parsing)
  - Gleam (version detection, gleam.toml parsing)  
  - Kotlin/Java (version detection, Gradle build file parsing)
  - Node.js (version detection, package.json engines parsing)
  - Python (version detection, pyproject.toml, requirements.txt parsing)
  - Rust (version detection, Cargo.toml parsing)
  - Go (version detection, go.mod parsing)
- Personality-rich conflict explanations with humor and helpful suggestions
- Environment snapshot functionality with sds.lock files
- Automatic fix suggestions with risk level assessment
- Comprehensive test suite and example projects

### Features
- **Smart Conflict Detection**: Identifies version mismatches, ABI conflicts, and missing toolchains
- **Actionable Fix Suggestions**: Provides specific commands to resolve conflicts
- **Personality with Purpose**: Explains conflicts in an entertaining but informative way
- **Offline Operation**: No internet connectivity required for basic functionality
- **Cross-Platform Support**: Works on Linux, macOS, and Windows
- **Safe by Default**: Shows what will be changed before making any modifications

## [0.1.0] - 2025-01-20

### Added
- 🎉 Initial release of SDS (Stupid Dependency Solver)
- Core dependency conflict detection engine
- Support for 7 major development toolchains
- Command-line interface with 5 primary commands
- Example projects demonstrating common conflict scenarios
- Comprehensive documentation and setup instructions

### Technical Details
- Python 3.8+ compatibility
- Modern packaging with pyproject.toml
- Type hints throughout codebase
- Comprehensive test coverage
- Development tooling (black, flake8, mypy, pytest)

### Personality Highlights
- 🤔 Zig version conflicts: "Detected zig 0.13.0, which thinks it's better than 0.12.1"
- ☕ Java compatibility: "Java 8 might not support features from Java 17"
- 🦀 Rust updates: "Rust 1.70.0 trailing 1.71.0. Update with: rustup update"
- 🐍 Python upgrades: "Python needs upgrade. Consider: pyenv install"

---

## Release Notes

### What is SDS?

SDS (Stupid Dependency Solver) is a command-line tool that acts as a "doctor for your project." It detects dependency and environment inconsistencies across multiple programming languages and toolchains, then provides actionable suggestions to get your project back to a buildable state.

### Key Philosophy

- **Doctor, not dictator**: SDS diagnoses problems and suggests fixes, but doesn't make changes without permission
- **Personality with purpose**: Error messages are informative AND entertaining
- **Minimal interference**: Works with your existing toolchain, doesn't replace it
- **Offline capable**: No internet required for basic conflict detection
- **Polyglot friendly**: Understands projects using multiple programming languages

### Supported Languages & Tools

| Language | Version Detection | Manifest Parsing | Special Features |
|----------|-------------------|------------------|------------------|
| Zig | ✅ `zig version` | ✅ build.zig.zon | ABI mismatch detection |
| Gleam | ✅ `gleam --version` | ✅ gleam.toml | Constraint validation |
| Kotlin | ✅ `kotlinc -version` | ✅ build.gradle(.kts) | Java compatibility |
| Java | ✅ `java -version` | ✅ Maven/Gradle | Version mapping |
| Node.js | ✅ `node --version` | ✅ package.json | Engine constraints |
| Python | ✅ `python --version` | ✅ pyproject.toml | MSRV checking |
| Rust | ✅ `rustc --version` | ✅ Cargo.toml | MSRV validation |
| Go | ✅ `go version` | ✅ go.mod | Module requirements |

### Installation

```bash
# Recommended: Install with pipx
pipx install stupid-dependency-solver

# Alternative: Install with pip
pip install stupid-dependency-solver

# From source
git clone https://github.com/example/stupid-dependency-solver.git
cd stupid-dependency-solver
pip install -e .
```

### Basic Usage

```bash
# Check for conflicts
sds check

# Get fix suggestions
sds fix

# Apply fixes automatically
sds fix --apply

# Create environment snapshot
sds snapshot

# Compare current state to snapshot
sds diff

# Get detailed explanations
sds explain zig
```

### Future Roadmap

- **v0.2.0**: Additional language support (C/C++, C#, Swift)
- **v0.3.0**: CI/CD integration helpers
- **v0.4.0**: Plugin system for custom toolchains
- **v0.5.0**: Web dashboard for team environments
- **v1.0.0**: Production-ready with comprehensive language support

### Contributing

SDS is open source and welcomes contributions! Areas where help is especially appreciated:

- **New Language Support**: Add detection and parsing for additional toolchains
- **Personality Enhancement**: Improve conflict messages with better humor and clarity
- **Platform Testing**: Ensure compatibility across different operating systems
- **Documentation**: Examples, tutorials, and integration guides

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### License

MIT License - see [LICENSE](LICENSE) for full details.

### Acknowledgments

- Inspired by every developer who's said "but it works on my machine!"
- Built for polyglot projects that juggle multiple languages
- Designed for teams who want clarity, not complexity

---

*"Dependencies are like teenagers - they never do what you expect, but with the right approach, you can get them back in line."* 🎯
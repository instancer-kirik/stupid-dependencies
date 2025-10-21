# 🧰 SDS - Stupid Dependency Solver

> A doctor for your project that speaks Zig, Gleam, Kotlin, and common sense.

📖 **[Full Documentation & Live Demo](https://your-username.github.io/stupid-dependency-solver)** 📖

SDS is a command-line tool that inspects your project directory, detects dependency and environment inconsistencies, and helps you get back to a buildable state. It doesn't try to own your dependencies — it just tells you what's broken, why, and how to fix it without reinventing your toolchain.

## 🧩 What's the Point?

Ever had this happen?

```bash
$ cd cool-project
$ make build
zig: error: expected zig version 0.12.x, found 0.13.0
```

Or maybe this?

```bash
$ ./gradlew build
> Task :compileKotlin FAILED
Kotlin version mismatch: compiler 1.9.23, target 1.8.22
```

SDS catches these mismatches **before** you waste time debugging, and tells you exactly how to fix them with personality:

```bash
$ sds check
🩺 Scanning project...
[zig] build.zig.zon requires zig 0.12.x, found 0.13.0 → ⚠️ ABI mismatch
[gleam] compiler 1.1.0 ok
[kotlin] Gradle 8.5 found, target 8.3 declared → ⚠️ minor mismatch
Status: not buildable
Run `sds fix` for repair suggestions.

$ sds fix
🔧 Suggested actions:
1. Downgrade zig to 0.12.1 (matches zon manifest) 🟢
   → zigup 0.12.1
2. Sync Gradle wrapper to 8.3 🟢
   → ./gradlew wrapper --gradle-version 8.3
Apply fixes? [y/N] y
```

## 🚀 Installation

### Via pipx (Recommended)
```bash
pipx install stupid-dependency-solver
```

### Via pip
```bash
pip install stupid-dependency-solver
```

### From Source
```bash
git clone https://github.com/example/stupid-dependency-solver.git
cd stupid-dependency-solver
pip install -e .
```

## 📖 Usage

### Basic Commands

| Command | Purpose |
|---------|---------|
| `sds check` | Scan current directory and report version/dependency issues |
| `sds fix` | Suggest or apply minimal repairs |
| `sds snapshot` | Capture a buildable environment as `sds.lock` |
| `sds diff` | Compare current state to last known snapshot |
| `sds explain` | Print reasoning for conflicts in plain English |

### Examples

#### Check Your Project
```bash
$ cd my-awesome-project
$ sds check
🩺 Scanning project...
[zig] build.zig.zon requires zig 0.12.1, found 0.13.0 → ❌ ABI mismatch
[kotlin] Gradle 8.5 vs target 8.3 → ⚠️ minor mismatch
[node] package.json engines.node ">=18.0.0", found 16.20.0 → ❌ insufficient
Status: not buildable
Run `sds fix` for repair suggestions.
```

#### Get Personality-Rich Explanations
```bash
$ sds explain zig
🧠 Detailed conflict analysis:

🔍 ZIG Issue:
   Problem: build.zig.zon requires zig 0.12.1, found 0.13.0
   Reason: ABI mismatch
   Details: 🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1.
            Try humbling it with: zigup 0.12.1
```

#### Create a Snapshot of Working State
```bash
$ sds snapshot
📸 Environment snapshot saved to sds.lock
🎯 Tools captured:
  zig = 0.12.1
  gleam = 1.1.0
  gradle = 8.3
  node = 18.17.0
```

#### Compare Against Snapshot
```bash
$ sds diff
📊 Environment diff:
  zig: 0.12.1 → 0.13.0
  gleam: 1.1.0 ✓
  gradle: 8.3 ✓
  node: 18.17.0 → 16.20.0
```

#### Apply Fixes Automatically
```bash
$ sds fix --apply
🚀 Applying fixes...
🔧 [1/2] Downgrade zig to 0.12.1 (matches zon manifest)
   ✅ Applied successfully
🔧 [2/2] Sync Gradle wrapper to 8.3
   ✅ Applied successfully
📊 Applied 2/2 fixes
```

## 🛠️ Supported Tools & Manifests

### Languages & Toolchains
- **Zig** - `zig version`, `build.zig.zon`, `build.zig`
- **Gleam** - `gleam --version`, `gleam.toml`
- **Kotlin/Java** - `kotlinc -version`, `java -version`, `build.gradle(.kts)`
- **Node.js** - `node --version`, `npm --version`, `package.json`
- **Python** - `python --version`, `pip --version`, `pyproject.toml`, `requirements.txt`
- **Rust** - `rustc --version`, `cargo --version`, `Cargo.toml`
- **Go** - `go version`, `go.mod`
- **Gradle** - `./gradlew --version`, `gradle --version`, wrapper properties

### What SDS Detects
- ✅ Version mismatches between toolchain and manifest requirements
- ✅ Missing toolchains that projects depend on
- ✅ ABI compatibility issues (especially Zig)
- ✅ Gradle wrapper vs system Gradle conflicts
- ✅ Node.js engines constraints violations
- ✅ Python version requirements in pyproject.toml
- ✅ Rust MSRV (Minimum Supported Rust Version) violations

## 🧠 The SDS Philosophy

### What SDS Does
- 🩺 **Diagnoses** your project's environment health
- 🔧 **Suggests** minimal, targeted fixes
- 📸 **Snapshots** working environments for reproducibility
- 🧠 **Explains** conflicts in plain English (with humor)
- ⚡ **Works offline** - no central registry required

### What SDS Doesn't Do
- ❌ Replace your build system
- ❌ Manage your dependencies (that's npm/cargo/etc.)
- ❌ Make breaking changes without asking
- ❌ Install tools you haven't approved
- ❌ Require internet connectivity

### Personality Examples

SDS doesn't just give you dry error messages:

```
🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1.
Try humbling it with: zigup 0.12.1

☕ Java 8 might not support features from Java 17.
Consider upgrading: sdk install java 17

🦀 Rust 1.70.0 trailing 1.71.0.
Update with: rustup update
```

## 🏗️ Advanced Usage

### Working with Complex Projects
```bash
# Check specific subdirectory
sds check --path ./backend

# Verbose output for debugging
sds check --verbose

# Dry run fixes without applying
sds fix --dry-run

# Force snapshot overwrite
sds snapshot --force
```

### Integration with CI/CD
```bash
# In your CI pipeline
sds check || echo "Environment issues detected"
sds snapshot  # Capture working state for future builds
```

### Configuration via sds.lock
```toml
[env]
zig = "0.12.1"
gleam = "1.1.0"
kotlin = "1.9.23"
gradle = "8.3"

[notes]
generated = "2025-01-20T12:00:00Z"
status = "buildable"

[overrides]
# Force specific tool versions if detection fails
# custom_tool = "1.2.3"
```

## 🔧 Development

### Setup Development Environment
```bash
git clone https://github.com/example/stupid-dependency-solver.git
cd stupid-dependency-solver

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black sds/
```

### Project Structure
```
sds/
├── core/
│   ├── env_detector.py       # Tool version detection
│   ├── manifest_parser.py    # Parse project config files
│   ├── solver.py            # Conflict detection + suggestions
│   └── fixer.py             # Apply fixes
├── cli.py                   # Command-line interface
└── templates/sds.lock       # Snapshot file template
```

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. **Report Issues** - Found a tool we don't support? Let us know!
2. **Add Tool Support** - Each tool needs detection + parsing logic
3. **Improve Messages** - Make our personality even better
4. **Fix Bugs** - Check out our issues page

### Adding a New Tool
1. Add detection logic to `env_detector.py`
2. Add manifest parsing to `manifest_parser.py`  
3. Add conflict detection to `solver.py`
4. Add personality messages for the tool
5. Update tests and documentation

## 📝 License

MIT License - see `LICENSE` file for details.

## 🙏 Acknowledgments

- Inspired by every developer who's ever said "but it works on my machine!"
- Built for the polyglot projects that use 5 different languages
- Designed for teams who want sanity, not magic

---

**"Dependencies are like teenagers - they never do what you expect, but with the right approach, you can get them back in line."** 🎯
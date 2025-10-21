# 🧰 Stupid Dependencies

> A doctor for your project that speaks Zig, Gleam, Kotlin, and common sense.

📖 **[Full Documentation & Live Demo](https://instancer-kirik.github.io/stupid-dependencies)** 📖

Stupid Dependencies is a command-line tool that inspects your project directory, detects dependency and environment inconsistencies, and helps you get back to a buildable state. It doesn't try to own your dependencies — it just tells you what's broken, why, and how to fix it without reinventing your toolchain.

## 🧩 What's the Point?

Ever had this happen?

```bash
$ ./gradlew build
> Task :compileKotlin FAILED
Kotlin version 1.8.20 requires Gradle 6.8.3-8.1, but found 8.3
```

Or this absolute nightmare (Android Navigation + KAPT→KSP migration)?

```bash
$ ./gradlew build
> Task :app:kaptGenerateStubsDebugKotlin FAILED
KAPT deprecated, migrate to KSP

$ # Hours later, after KSP migration...
$ ./gradlew build  
> Multiple build failures across 3 Gradle files:
  - Navigation 2.7.5 requires KSP 1.9.20, found 1.8.22 (gradle/libs.versions.toml)
  - Hilt 2.48 incompatible with KSP 1.9.20 (app/build.gradle) 
  - Room 2.6.0 needs Kotlin 1.9.20, found 1.8.20 (project/build.gradle)
  - Compose BOM 2023.08.00 conflicts with Navigation Compose 2.7.5
```

Stupid Dependencies catches these version conflicts **before** you waste hours debugging, and shows you exactly what's broken with real version data:

```bash
$ stupid look
🩺 Scanning Android project (3 Gradle files)...

❌ CRITICAL: KAPT→KSP migration incomplete
   • KAPT still enabled in app/build.gradle 
   • KSP 1.8.22 incompatible with Navigation 2.7.5 (requires KSP 1.9.20+)
   • 💡 Complete KSP migration + upgrade Kotlin to 1.9.20

❌ CRITICAL: Multi-file version conflicts
   • gradle/libs.versions.toml: kotlin = "1.8.20"
   • project/build.gradle: Room 2.6.0 needs Kotlin 1.9.20+
   • app/build.gradle: Hilt 2.48 incompatible with KSP 1.9.20

⚠️  NAVIGATION NIGHTMARE: 4 conflicting versions
   • navigation-compose 2.7.5 vs compose-bom 2023.08.00 (incompatible)
   • material3 1.2.0 requires compose-bom 2024.02.00+
   • Room navigation integration broken by version mismatch

$ stupid cope --live
📡 Querying Maven Central + Android compatibility matrices...

🔧 KAPT→KSP Migration Plan:
1. Upgrade Kotlin: 1.8.20 → 1.9.20 (minimum for KSP + Navigation) 🟢
   → gradle/libs.versions.toml: kotlin = "1.9.20", ksp = "1.9.20-1.0.14"
   
2. Complete KSP migration 🟢
   → Remove kapt plugin from app/build.gradle
   → Add ksp plugin, update all kapt() → ksp()
   
3. Fix Navigation compatibility chain 🟢
   → Compose BOM 2023.08.00 → 2024.02.00 
   → Navigation Compose 2.7.5 (compatible with new BOM)
   → Material3 automatically resolved to 1.2.1
   
4. Update Hilt + Room for KSP compatibility 🟢
   → Hilt 2.48 → 2.50 (first KSP-compatible version)
   → Room 2.6.0 → 2.6.1 (KSP stability fixes)

⚡ Estimated build time improvement: 40% faster (KSP vs KAPT)
Apply all fixes? [y/N]
```

## 🚀 Installation

### Via pip
```bash
pip install stupid-dependencies
```

### Via uv (Recommended)
```bash
uv tool install stupid-dependencies
```

### Try it instantly
```bash
# See it in action with live API demo
stupid demo --live
```

### From Source
```bash
git clone https://github.com/instancer-kirik/stupid-dependencies.git
cd stupid-dependencies
pip install -e .
```

## 📖 Usage

### Basic Commands

| Command | Purpose |
|---------|---------|
| `stupid look` | Scan current directory and report version/dependency issues |
| `stupid cope` | Suggest or apply minimal repairs |
| `stupid snapshot` | Capture a buildable environment as `stupid.lock` |
| `stupid diff` | Compare current state to last known snapshot |
| `stupid explain` | Print reasoning for conflicts in plain English |

### Examples

#### Check Your Project
```bash
$ cd my-awesome-project
$ stupid look
🩺 Scanning project...
[kotlin] Gradle 8.5 vs target 8.3 → ⚠️ minor mismatch
[android] Hilt 2.48 → 2.56.2 available (8 versions behind)
[dependencies] Version conflicts: coroutines 1.6.3 vs 1.7.3
Status: not buildable
Run `stupid cope` for repair suggestions.
```

#### Get Personality-Rich Explanations
```bash
$ stupid explain kotlin
🧠 Detailed conflict analysis:

🔍 KOTLIN/GRADLE Issue:
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
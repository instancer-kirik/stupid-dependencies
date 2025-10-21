# 🚀 Getting Started with SDS

Welcome to **SDS (Stupid Dependency Solver)** - your project's new best friend! This guide will get you up and running in minutes.

## 🎯 What You'll Learn

- How to install and set up SDS
- Your first conflict detection
- Understanding SDS output and personality
- Fixing conflicts with confidence
- Advanced workflows for teams

## 📦 Installation

### Quick Start (Recommended)

```bash
# Install with pipx (isolated environment)
pipx install stupid-dependency-solver

# Verify installation
sds --help
```

### Alternative Installation Methods

```bash
# Install with pip
pip install stupid-dependency-solver

# Install from source (for developers)
git clone https://github.com/example/stupid-dependency-solver.git
cd stupid-dependency-solver
pip install -e .
```

### Requirements

- **Python 3.8+** (SDS is written in Python)
- **Your development tools** (zig, node, kotlin, etc.)
- **Terminal/Command prompt**

> 💡 **Tip**: SDS works by calling your existing tools (like `zig version`, `node --version`), so you need them installed for detection to work.

## 🧪 Your First SDS Check

Let's dive right in! Navigate to any project directory and run:

```bash
cd your-project
sds check
```

### What You'll See

#### ✅ Healthy Project
```
🩺 Scanning project...
[node] package.json engines.node ">=16.0.0", found 18.17.0 ✓
[npm] version 9.8.0 ✓
Status: buildable
✨ All good! Project looks healthy.
```

#### ⚠️ Project with Issues
```
🩺 Scanning project...
[zig] build.zig.zon requires zig 0.12.x, found 0.13.0 → ⚠️ ABI mismatch
[node] package.json engines.node ">=18.0.0", found 16.20.0 → ❌ insufficient
Status: not buildable
Run `sds fix` for repair suggestions.
```

## 🔧 Understanding and Fixing Conflicts

When SDS finds issues, it's time to get them fixed!

### Step 1: Get Detailed Explanations

```bash
sds explain
```

**Example Output:**
```
🧠 Detailed conflict analysis:

🔍 ZIG Issue:
   Problem: build.zig.zon requires zig 0.12.1, found 0.13.0
   Reason: ABI mismatch
   Details: 🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1.
            Try humbling it with: zigup 0.12.1
```

### Step 2: Get Fix Suggestions

```bash
sds fix
```

**Example Output:**
```
🔧 Suggested actions:
1. Downgrade zig to 0.12.1 (matches zon manifest) 🟢
   → zigup 0.12.1
2. Upgrade Node.js to meet engine requirements 🟡
   → nvm install 18.17.0 && nvm use 18.17.0
Apply fixes? [y/N]
```

### Step 3: Apply Fixes

You have several options:

```bash
# Review fixes interactively (safest)
sds fix

# See what would be done without applying
sds fix --dry-run

# Apply fixes automatically (for CI/scripts)
sds fix --apply
```

## 🎭 Understanding SDS Personality

SDS isn't your typical dry command-line tool. It has personality! Here's how to interpret its messages:

### Conflict Severity Levels

| Icon | Severity | Meaning | Action Needed |
|------|----------|---------|---------------|
| ✅ | OK | Everything looks good | None |
| ⚠️ | Warning | Minor issues, usually buildable | Optional fixes |
| ❌ | Error | Major problems, likely unbuildable | Required fixes |

### Personality Examples

```
🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1.
   → Newer version causing ABI issues

☕ Java 8 might not support features from Java 17.
   → Version too old for requirements

🦀 Rust 1.70.0 trailing 1.71.0. Update with: rustup update
   → Helpful update suggestion

🐍 Python needs upgrade. Consider: pyenv install 3.11.0
   → Specific command to fix the issue
```

## 📸 Environment Snapshots

One of SDS's most powerful features is creating reproducible environment snapshots.

### Creating a Snapshot

```bash
# Capture current working environment
sds snapshot
```

This creates an `sds.lock` file:
```toml
[env]
zig = "0.12.1"
node = "18.17.0"
kotlin = "1.9.23"
gradle = "8.3"

[notes]
generated = "2025-01-20T12:00:00Z"
status = "buildable"
```

### Using Snapshots

```bash
# Compare current state to snapshot
sds diff

# Check if environment matches snapshot
sds check  # Will reference sds.lock if present
```

**Example Diff Output:**
```
📊 Environment diff:
  zig: 0.12.1 ✓
  node: 18.17.0 → 16.20.0
  kotlin: 1.9.23 ✓
```

## 🌟 Common Workflows

### Daily Development
```bash
# Morning routine - check project health
cd my-project
sds check

# If issues found, investigate
sds explain

# Fix issues
sds fix
```

### New Team Member Setup
```bash
# Clone project
git clone project-repo
cd project-repo

# Check what's needed
sds check

# Follow SDS suggestions to match team environment
sds fix --apply
```

### Before Important Builds
```bash
# Ensure environment is stable
sds check

# Create snapshot of working state
sds snapshot

# Proceed with confidence
make build  # or your build command
```

### CI/CD Integration
```bash
# In your CI script
sds check || {
  echo "Environment conflicts detected"
  sds explain
  exit 1
}
```

## 🛠️ Language-Specific Tips

### Zig Projects
- SDS reads `build.zig.zon` for version constraints
- ABI mismatches are serious - SDS will flag them as errors
- Use `zigup` for easy version switching

### Node.js Projects
- SDS checks `package.json` engines constraints
- Use `nvm` for Node version management
- Both `node` and `npm` versions are validated

### Kotlin/Java Projects
- SDS parses Gradle build files for version requirements
- Java version compatibility is checked
- Gradle wrapper vs system Gradle conflicts detected

### Multi-Language Projects
- SDS handles polyglot projects naturally
- Each language is checked independently
- Cross-language compatibility issues flagged

## 🚨 Troubleshooting

### "No tools detected"
**Problem**: SDS can't find any development tools.
**Solution**: Make sure tools are installed and in your PATH.

```bash
# Check if tools are available
which zig node java kotlinc
echo $PATH
```

### "Permission denied" on fixes
**Problem**: SDS can't apply fixes due to permissions.
**Solution**: Check file permissions or run with appropriate privileges.

### "Command not found" errors
**Problem**: Tool version managers (nvm, zigup, etc.) not available.
**Solution**: Install the appropriate version manager or apply fixes manually.

## 📚 Next Steps

### Explore Examples
```bash
# Try SDS on included examples
cd examples/conflicted-zig-project
sds check
sds explain
sds fix

cd ../polyglot-project
sds check
```

### Team Integration
1. **Share snapshots**: Commit `sds.lock` files to version control
2. **CI integration**: Add `sds check` to your build pipeline
3. **Onboarding**: New developers run `sds check` to verify setup

### Advanced Usage
- Learn about `sds explain <tool>` for specific tool analysis
- Use `--verbose` flag for detailed debugging
- Explore `--dry-run` for safe fix previews

## 💡 Pro Tips

### 🎯 Best Practices
1. **Run `sds check` before starting work** - catch issues early
2. **Create snapshots after successful builds** - document working states
3. **Use in CI/CD** - prevent environment drift in deployments
4. **Share team environments** - commit sds.lock files

### 🔧 Power User Features
```bash
# Check specific directory
sds check --path ./backend

# Verbose output for debugging
sds check --verbose

# Force snapshot overwrite
sds snapshot --force
```

### 🤝 Team Workflows
- **Morning standup**: "Any environment conflicts?"
- **Code reviews**: Include sds.lock changes
- **Release preparation**: Verify with `sds check`

## 🆘 Getting Help

### Built-in Help
```bash
sds --help          # General help
sds check --help    # Command-specific help
sds fix --help      # Fix command options
```

### Community Resources
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Full API reference and guides
- **Examples**: Real-world usage scenarios

### Contributing
SDS is open source and welcomes contributions:
- Add support for new languages/tools
- Improve personality messages
- Write documentation and examples
- Fix bugs and add features

## 🎉 You're Ready!

Congratulations! You now know how to:
- ✅ Install and run SDS
- ✅ Interpret conflict messages
- ✅ Apply fixes safely
- ✅ Create and use environment snapshots
- ✅ Integrate SDS into your workflow

**Remember**: SDS is your project's doctor, not its dictator. It diagnoses problems and suggests treatments, but you're always in control.

---

*"Dependencies are like teenagers - they never do what you expect, but with the right approach, you can get them back in line."* 🎯

**Happy dependency solving!** 🧰
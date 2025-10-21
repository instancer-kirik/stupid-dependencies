---
layout: default
title: Documentation
---

# 📚 Documentation

Welcome to the Stupid Dependencies documentation! Here you'll find everything you need to master dependency hell and emerge victorious.

## 🚀 Quick Navigation

### Getting Started
- [Installation & Setup](../getting-started.html) - Get up and running in minutes
- [First Steps](../getting-started.html#your-first-scan) - Your first dependency scan
- [Basic Commands](../getting-started.html#basic-commands) - Essential commands to know

### Features & Capabilities
- [Live Demo](../demo.html) - See it in action with real data
- [Kotlin/Gradle Enhancement](../kotlin-gradle-enhancement.html) - Deep dive into Kotlin ecosystem support
- [Multi-language Support](../showcase.html#multi-language-architecture) - Beyond just Kotlin

### Advanced Usage
- [Command Reference](#command-reference) - All available commands
- [Configuration](#configuration) - Customize SDS for your needs
- [Troubleshooting](#troubleshooting) - When things go wrong

---

## 🎯 Command Reference

### Core Commands

#### `stupid check`
Scans your project for dependency issues.

```bash
# Basic scan
stupid check

# Scan specific directory
stupid check --path ./my-project

# Verbose output
stupid check --verbose
```

#### `stupid fix`
Shows available fixes for detected issues.

```bash
# Show potential fixes
stupid fix

# Apply fixes automatically
stupid fix --apply

# Interactive mode
stupid fix --interactive
```

#### `stupid demo`
Runs demonstration mode.

```bash
# Basic demo with sample data
stupid demo

# Live demo with real API queries
stupid demo --live

# Android-specific demo
stupid demo --android
```

### Analysis Commands

#### `stupid explain`
Provides detailed explanations for issues.

```bash
# Explain Kotlin-related issues
stupid explain kotlin

# Explain specific dependency
stupid explain androidx.compose
```

#### `stupid snapshot`
Manages project dependency snapshots.

```bash
# Create snapshot
stupid snapshot

# Compare with previous snapshot
stupid diff
```

---

## ⚙️ Configuration

### Environment Variables

- `STUPID_CACHE_DIR` - Custom cache directory (default: `~/.stupid/cache`)
- `STUPID_LOG_LEVEL` - Logging level (`DEBUG`, `INFO`, `WARN`, `ERROR`)
- `STUPID_TIMEOUT` - API timeout in seconds (default: 30)

### Config File

Create `.stupid.toml` in your project root:

```toml
[general]
cache_enabled = true
timeout = 30
verbose = false

[kotlin]
gradle_compatibility_strict = true
check_preview_versions = false

[output]
format = "table"  # table, json, yaml
show_suggestions = true
max_suggestions = 5
```

---

## 🔧 Language-Specific Features

### Kotlin/Gradle
- **Compatibility Matrix**: Built-in Kotlin-Gradle compatibility checking
- **Version Conflicts**: Detects and resolves version mismatches
- **Android Support**: AGP (Android Gradle Plugin) compatibility
- **Live Queries**: Real-time Maven Central and GitHub API queries

### Zig (Coming Soon)
- **Package Manager**: Zig package manager integration
- **Build System**: Zig build system compatibility

### Gleam (Coming Soon)
- **Hex Package Manager**: Gleam package ecosystem support
- **OTP Compatibility**: Erlang/OTP version checking

---

## 🚨 Troubleshooting

### Common Issues

#### "No dependencies found"
```bash
# Make sure you're in a project directory with build files
ls build.gradle* # Kotlin/Android
ls build.zig     # Zig
ls gleam.toml    # Gleam
```

#### Network timeouts
```bash
# Increase timeout
export SDS_TIMEOUT=60
stupid check
```

#### Permission errors
```bash
# Check cache directory permissions
ls -la ~/.stupid/
```

### Debug Mode

Enable verbose logging:

```bash
export STUPID_LOG_LEVEL=DEBUG
stupid check --verbose
```

---

## 🌐 API Integration

### Maven Central
- Real-time version queries
- Release date information
- Stability classification

### GitHub API
- Latest release information
- Compatibility matrices
- Issue tracking integration

### Custom Repositories
Configure additional repositories in `.stupid.toml`:

```toml
[repositories]
maven_central = "https://search.maven.org/solrsearch/select"
jitpack = "https://jitpack.io/api/builds/"

[repositories.custom]
name = "corporate-nexus"
url = "https://nexus.company.com/repository/maven-public/"
type = "maven"
```

---

## 📊 Output Formats

### Table Format (Default)
```
┌─────────────────────┬─────────┬──────────┬──────────┐
│ Dependency          │ Current │ Latest   │ Severity │
├─────────────────────┼─────────┼──────────┼──────────┤
│ kotlin-stdlib       │ 1.8.20  │ 1.9.22   │ info     │
│ hilt-android        │ 2.48    │ 2.56.2   │ warning  │
└─────────────────────┴─────────┴──────────┴──────────┘
```

### JSON Format
```json
{
  "issues": [
    {
      "dependency": "kotlin-stdlib",
      "current": "1.8.20",
      "latest": "1.9.22",
      "severity": "info",
      "suggestions": ["upgrade to 1.9.22"]
    }
  ]
}
```

---

## 🤝 Contributing

Want to help make dependency management less painful? Check out our [contribution guidelines]({{ site.project.repo_url }}/blob/main/CONTRIBUTING.md).

### Development Setup

```bash
git clone {{ site.project.repo_url }}
cd stupid-dependencies
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Adding Language Support

1. Create parser in `sds/parsers/your_language.py`
2. Add repository client in `sds/clients/your_repo.py`
3. Update CLI in `sds/cli.py`
4. Add tests in `tests/test_your_language.py`

---

## 📞 Support

- **GitHub Issues**: [Report bugs and request features]({{ site.project.repo_url }}/issues)
- **Discussions**: [Community discussion]({{ site.project.repo_url }}/discussions)
- **Documentation**: This site!

---

<div style="text-align: center; margin: 2rem 0; padding: 2rem; background: #f8f9fa; border-radius: 8px;">
  <h3>Ready to conquer dependency hell?</h3>
  <p>Start with the <a href="../getting-started.html">Getting Started guide</a> or jump straight into the <a href="../demo.html">live demo</a>!</p>
</div>
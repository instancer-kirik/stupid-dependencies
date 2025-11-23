# Version-Agnostic Stupid Dependency Solver

> **The Universal Project Doctor** - Detect and fix compatibility issues across ANY language, ANY version, ANY package manager without hardcoded assumptions.

## 🚀 Revolutionary Approach

The Version-Agnostic SDS represents a complete paradigm shift from traditional dependency solvers. Instead of hardcoding version checks and tool-specific logic, this system uses:

- **Rule-Based Compatibility Detection** - All compatibility rules are loaded from configuration files
- **Universal Version Constraint Parsing** - Works with any version format (semver, Elixir ~>, npm ^, etc.)
- **Template-Based Fix Generation** - Fixes are generated from flexible templates, not hardcoded commands
- **Configuration-Driven Issue Detection** - New compatibility issues can be added without code changes

## ✨ Key Features

### 🌍 Universal Language Support
- **Python** - pyproject.toml, requirements.txt, Pipfile support
- **Node.js** - package.json with npm/yarn version constraints
- **Rust** - Cargo.toml with MSRV and dependency management
- **Elixir** - mix.exs and mix.lock with OTP compatibility
- **Go** - go.mod with module version requirements
- **Java/Kotlin** - Maven POM and Gradle build files
- **Zig** - build.zig.zon support
- **Gleam** - gleam.toml compatibility

### 🔮 Future-Proof Design
- **No Version Hardcoding** - Works with future tool versions automatically
- **Configurable Rules** - Add new compatibility issues via YAML configuration
- **Extensible Templates** - New fix types can be added without code changes
- **Generic Constraint Handling** - Supports any version constraint format

### 🎯 Intelligent Fix Suggestions
- **Context-Aware** - Fixes are generated based on available version managers
- **Risk-Assessed** - All fixes include risk levels (low/medium/high)
- **Alternative Solutions** - Multiple fix options with pros/cons
- **Validation Support** - Pre-flight checks before applying fixes

## 🛠️ How It Works

### 1. Rule-Based Compatibility Detection

Instead of hardcoded version checks, the system loads rules from `compatibility_rules.yaml`:

```yaml
tools:
  elixir:
    compatibility_rules:
      - id: "module_attribute_restrictions"
        description: "Stricter module attribute handling in newer versions"
        affected_versions:
          operator: ">="
          version: "1.18.0"
        symptoms:
          - "cannot inject attribute.*into function/macro"
        category: "compilation_error"
```

### 2. Universal Version Constraint Parsing

The system can parse and evaluate constraints from any ecosystem:

```python
# Works with all of these automatically:
"~> 1.14"     # Elixir compatible release
"^2.3.4"      # npm caret range  
">=3.8,<4.0"  # Python version range
"1.60"        # Rust MSRV
">= 16.0.0"   # Node.js engine requirement
```

### 3. Template-Based Fix Generation

Fixes are generated from flexible templates that work across versions:

```yaml
fix_templates:
  version_manager_install:
    asdf:
      description: "Install {tool} {version} via asdf"
      command: "asdf install {tool} {version} && asdf global {tool} {version}"
      risk_level: "low"
```

### 4. Package-Specific Issue Database

Known compatibility issues are stored in configuration, not code:

```yaml
package_issues:
  inflex:
    - issue_id: "deprecated_module_attrs"
      description: "Uses deprecated module attribute patterns"
      triggers_with:
        - tool: "elixir"
          version_constraint: ">=1.18.0"
      error_patterns:
        - "cannot inject attribute @\\w+ into function/macro"
```

## 🚀 Quick Start

### Installation

```bash
cd "Stupid Dependency Solver"
pip install -e .
```

### Basic Usage

```bash
# Comprehensive project analysis
sds analyze

# Check for compatibility conflicts
sds check

# Show fix suggestions
sds fix

# Validate specific tool compatibility  
sds validate elixir

# Show version constraints and suggestions
sds version-info python
```

### Advanced Usage

```bash
# Focus on specific tool
sds analyze --tool elixir

# Show only error-level conflicts
sds check --errors-only

# Filter fixes by risk level
sds fix --risk low

# Apply fixes interactively
sds fix --apply

# JSON output for automation
sds analyze --json --output results.json
```

## 🎯 Real-World Examples

### Elixir + OTP 28 Compatibility Issue

**Problem**: The `inflex` package fails to compile with Elixir 1.18+ due to deprecated module attribute usage.

**Traditional Approach** (hardcoded):
```python
if "inflex" in dependencies and elixir_version >= "1.18":
    suggest_fix("Use fork: https://github.com/improvingjef/inflex.git")
```

**Version-Agnostic Approach** (configurable):
```yaml
package_issues:
  inflex:
    - triggers_with:
        - tool: "elixir"  
          version_constraint: ">=1.18.0"
      primary_fix:
        type: "git_override"
        git_url: "https://github.com/improvingjef/inflex.git"
        description: "improvingjef's OTP 28 compatible fork"
```

**Benefits**:
- Works with Elixir 1.19, 2.0, etc. automatically
- New forks can be added without code changes
- Risk levels and alternatives included
- Error detection patterns configurable

### Python Version Compatibility

**Problem**: Project requires Python 3.8+ but system has 3.7.

**Version-Agnostic Detection**:
```bash
$ sds check --tool python
❌ ERROR [python] Python 3.7.0 is below project requirement >=3.8
```

**Version-Agnostic Fixes**:
```bash
$ sds fix
🔧 Fix Suggestions:
1. [LOW] Install Python 3.8.16 via pyenv
   Command: pyenv install 3.8.16 && pyenv global 3.8.16
2. [LOW] Install Python 3.8.16 via asdf  
   Command: asdf install python 3.8.16 && asdf global python 3.8.16
```

## 📊 Architecture

### Core Components

1. **CompatibilityEngine** - Rule-based issue detection
2. **VersionConstraints** - Universal version parsing and comparison  
3. **FixGenerator** - Template-based fix suggestion
4. **ManifestParser** - Multi-format project file parsing
5. **VersionAgnosticSolver** - Main orchestration layer

### Configuration Files

- `compatibility_rules.yaml` - Compatibility rules and issue detection
- Templates for fix generation
- Package-specific issue database
- Version manager detection and commands

### Data Flow

```
Project Files → ManifestParser → CompatibilityEngine → Issues
                      ↓
Environment Detection → VersionConstraints → FixGenerator → Solutions
```

## 🌟 Benefits Over Traditional Approaches

### ❌ Traditional Dependency Solvers
- Hardcode version checks (`if version == "1.18"`)
- Tool-specific logic scattered throughout codebase
- New issues require code changes and releases
- Limited to known version combinations
- Fixes are hardcoded commands

### ✅ Version-Agnostic SDS
- **Future-Proof**: Works with unknown future versions
- **Configurable**: New issues added via configuration files
- **Universal**: Same logic works across all languages
- **Maintainable**: No version-specific code to update
- **Extensible**: Easy to add support for new tools
- **Intelligent**: Context-aware fix generation

## 🔧 Adding New Compatibility Issues

### Step 1: Define the Rule
Add to `compatibility_rules.yaml`:

```yaml
tools:
  your_tool:
    compatibility_rules:
      - id: "your_issue_id"
        description: "Description of the compatibility issue"
        affected_versions:
          operator: ">="
          version: "2.0.0"
        symptoms:
          - "error pattern to detect"
        category: "compilation_error"
```

### Step 2: Add Package-Specific Issues
```yaml
package_issues:
  problematic_package:
    - issue_id: "specific_problem"
      description: "What goes wrong"
      triggers_with:
        - tool: "your_tool"
          version_constraint: ">=2.0.0"
      error_patterns:
        - "specific error message pattern"
```

### Step 3: Define Fixes
```yaml
package_fixes:
  your_tool:
    problematic_package:
      primary_fix:
        type: "git_override"
        git_url: "https://github.com/user/fixed-package.git"
        description: "Compatible fork"
      alternative_fixes:
        - type: "version_downgrade"
          description: "Use older tool version"
          risk_level: "medium"
```

## 🎪 Demo

Run the comprehensive demo to see the version-agnostic capabilities:

```bash
python demo_version_agnostic.py
```

This demonstrates:
- Universal version constraint parsing
- Rule-based compatibility detection
- Template-based fix generation
- Multi-language support
- Configuration flexibility

## 🤝 Contributing

### Adding New Language Support

1. Add manifest parser for the language's project files
2. Define version patterns in `compatibility_rules.yaml`
3. Add version manager templates
4. Create test cases

### Adding New Compatibility Rules

1. Research the compatibility issue
2. Define detection patterns
3. Create fix templates
4. Test across different versions
5. Document the issue and fix

## 🔮 Future Enhancements

- **Machine Learning Integration** - Learn compatibility patterns from community data
- **Real-Time Package Registry Queries** - Check latest compatible versions
- **Dependency Graph Analysis** - Detect transitive compatibility issues  
- **Community Rule Sharing** - Crowdsourced compatibility knowledge
- **IDE Integration** - Real-time compatibility hints in editors

## 📈 Impact

### Before Version-Agnostic SDS
```python
# Hardcoded, brittle, version-specific
if tool == "elixir" and version.startswith("1.18") and "inflex" in deps:
    return "Use fork: github.com/user/inflex.git"  # What about 1.19? 2.0?
```

### After Version-Agnostic SDS  
```yaml
# Configurable, future-proof, universal
triggers_with:
  - tool: "elixir"
    version_constraint: ">=1.18.0"  # Works with ANY future version
```

The Version-Agnostic SDS transforms dependency solving from a reactive, tool-specific approach to a proactive, universal system that adapts to any language, version, or package manager without requiring code changes.

**The future of dependency solving is here - and it's version-agnostic! 🚀**
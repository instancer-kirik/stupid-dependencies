# Conflicted Zig Project Example

This is an example project designed to demonstrate how **SDS (Stupid Dependency Solver)** detects and helps resolve dependency conflicts in Zig projects.

## 🎯 Purpose

This project intentionally creates version conflicts that SDS can detect:

- **Zig Version Mismatch**: `build.zig.zon` requires Zig 0.12.1, but you might have 0.13.0+ installed
- **Dependency Conflicts**: Uses dependencies that may not be compatible with your current Zig version
- **ABI Issues**: Demonstrates the kind of ABI mismatches that break Zig builds

## 🧪 Testing SDS

### 1. Check for Conflicts
```bash
cd examples/conflicted-zig-project
sds check
```

Expected output:
```
🩺 Scanning project...
[zig] build.zig.zon requires zig 0.12.1, found 0.13.0 → ⚠️ ABI mismatch
Status: not buildable
Run `sds fix` for repair suggestions.
```

### 2. Get Fix Suggestions
```bash
sds fix
```

Expected output:
```
🔧 Suggested actions:
1. Downgrade zig to 0.12.1 (matches zon manifest) 🟢
   → zigup 0.12.1
Apply fixes? [y/N]
```

### 3. Get Detailed Explanations
```bash
sds explain zig
```

Expected output:
```
🧠 Detailed conflict analysis:

🔍 ZIG Issue:
   Problem: build.zig.zon requires zig 0.12.1, found 0.13.0
   Reason: ABI mismatch
   Details: 🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1.
            Try humbling it with: zigup 0.12.1
```

### 4. Create Environment Snapshot
```bash
sds snapshot
```

This creates an `sds.lock` file capturing your current environment.

## 🛠️ Manual Build (Will Likely Fail)

Try building without fixing the conflicts:

```bash
zig build
```

You'll likely see errors like:
- Version incompatibility messages
- ABI mismatch errors
- Dependency resolution failures

## 🎯 After Using SDS

1. Use `zigup` to switch to the correct version:
   ```bash
   zigup 0.12.1
   ```

2. Verify the fix:
   ```bash
   sds check
   ```

3. Now building should work:
   ```bash
   zig build run
   ```

## 📁 Project Structure

```
conflicted-zig-project/
├── build.zig          # Build configuration
├── build.zig.zon      # Dependencies with version constraints
├── src/
│   └── main.zig       # Main application code
├── README.md          # This file
└── sds.lock           # Generated after `sds snapshot`
```

## 🧠 What This Demonstrates

- **Version Detection**: SDS detects your actual Zig version vs. requirements
- **Manifest Parsing**: SDS reads `build.zig.zon` to understand constraints
- **Conflict Analysis**: SDS identifies ABI and compatibility issues
- **Fix Suggestions**: SDS provides actionable commands to resolve issues
- **Personality**: SDS explains problems with humor and clarity

## 🔄 Try Different Scenarios

### Scenario 1: Newer Zig Version
Install Zig 0.13.0+ and run `sds check` to see newer-version warnings.

### Scenario 2: Older Zig Version
Install Zig 0.11.x and run `sds check` to see compatibility errors.

### Scenario 3: Missing Zig
Temporarily move `zig` out of PATH and run `sds check` to see missing tool detection.

## 🤝 Contributing

This example project helps test and demonstrate SDS functionality. If you find ways to improve the examples or add new conflict scenarios, contributions are welcome!

## 📚 Related

- [SDS Main Documentation](../../README.md)
- [Zig Language Reference](https://ziglang.org/documentation/)
- [zigup Version Manager](https://github.com/marler8997/zigup)
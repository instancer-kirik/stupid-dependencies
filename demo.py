#!/usr/bin/env python3
"""
SDS Demo Script - Showcases the Stupid Dependency Solver in action
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def colored_print(text: str, color: str = Colors.WHITE) -> None:
    """Print text with color."""
    print(f"{color}{text}{Colors.END}")


def demo_header(title: str) -> None:
    """Print a demo section header."""
    print("\n" + "=" * 60)
    colored_print(f"🎬 {title}", Colors.BOLD + Colors.CYAN)
    print("=" * 60)


def simulate_typing(text: str, delay: float = 0.03) -> None:
    """Simulate typing effect for commands."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def demo_sds_check_output():
    """Simulate SDS check command output."""
    colored_print("🩺 Scanning project...", Colors.BLUE)
    time.sleep(1)

    print("[zig] build.zig.zon requires zig 0.12.x, found 0.13.0 → ⚠️  ABI mismatch")
    print("[gleam] compiler 1.1.0 ok")
    print("[kotlin] Gradle 8.5 found, target 8.3 declared → ⚠️  minor mismatch")
    print(
        '[node] package.json engines.node ">=18.0.0", found 16.20.0 → ❌ insufficient'
    )

    colored_print("Status: not buildable", Colors.RED + Colors.BOLD)
    colored_print("Run `sds fix` for repair suggestions.", Colors.YELLOW)


def demo_sds_fix_output():
    """Simulate SDS fix command output."""
    colored_print("🔧 Suggested actions:", Colors.GREEN)
    print("1. Downgrade zig to 0.12.1 (matches zon manifest) 🟢")
    print("   → zigup 0.12.1")
    print("2. Sync Gradle wrapper to 8.3 🟢")
    print("   → ./gradlew wrapper --gradle-version 8.3")
    print("3. Upgrade Node.js to meet engine requirements 🟡")
    print("   → nvm install 18.17.0 && nvm use 18.17.0")

    print("\nApply fixes? [y/N] ", end="")
    time.sleep(1)
    colored_print("y", Colors.GREEN)

    time.sleep(0.5)
    colored_print("\n🚀 Applying fixes...", Colors.BLUE)

    time.sleep(0.8)
    colored_print(
        "🔧 [1/3] Downgrade zig to 0.12.1 (matches zon manifest)", Colors.BLUE
    )
    time.sleep(0.5)
    colored_print("   ✅ Applied successfully", Colors.GREEN)

    time.sleep(0.8)
    colored_print("🔧 [2/3] Sync Gradle wrapper to 8.3", Colors.BLUE)
    time.sleep(0.5)
    colored_print("   ✅ Applied successfully", Colors.GREEN)

    time.sleep(0.8)
    colored_print("🔧 [3/3] Upgrade Node.js to meet engine requirements", Colors.BLUE)
    time.sleep(0.5)
    colored_print("   ⚠️  Manual action required: nvm install 18.17.0", Colors.YELLOW)

    time.sleep(0.5)
    colored_print("📊 Applied 2/3 fixes", Colors.GREEN)


def demo_sds_explain_output():
    """Simulate SDS explain command output."""
    colored_print("🧠 Detailed conflict analysis:", Colors.MAGENTA)
    print()

    colored_print("🔍 ZIG Issue:", Colors.YELLOW + Colors.BOLD)
    print("   Problem: build.zig.zon requires zig 0.12.1, found 0.13.0")
    print("   Reason: ABI mismatch")
    colored_print(
        "   Details: 🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1.",
        Colors.CYAN,
    )
    colored_print("            Try humbling it with: zigup 0.12.1", Colors.CYAN)
    print()

    colored_print("🔍 NODE Issue:", Colors.YELLOW + Colors.BOLD)
    print('   Problem: package.json engines.node ">=18.0.0", found 16.20.0')
    print("   Reason: Insufficient version")
    colored_print("   Details: 🔄 Node 16.20.0 is behind 18.0.0.", Colors.CYAN)
    colored_print(
        "            Upgrade with: nvm install 18.17.0 && nvm use 18.17.0", Colors.CYAN
    )


def demo_sds_snapshot_output():
    """Simulate SDS snapshot command output."""
    colored_print("📸 Environment snapshot saved to sds.lock", Colors.GREEN)
    colored_print("🎯 Tools captured:", Colors.BLUE)
    print("  zig = 0.12.1")
    print("  gleam = 1.1.0")
    print("  kotlin = 1.9.23")
    print("  gradle = 8.3")
    print("  node = 18.17.0")
    print("  npm = 9.8.0")


def demo_sds_diff_output():
    """Simulate SDS diff command output."""
    colored_print("📊 Environment diff:", Colors.BLUE)
    print("  zig: 0.12.1 → 0.13.0")
    print("  gleam: 1.1.0 ✓")
    print("  kotlin: 1.9.23 ✓")
    print("  gradle: 8.3 ✓")
    print("  node: 16.20.0 → 18.17.0")
    print("  npm: 9.8.0 ✓")


def demo_personality_messages():
    """Show off SDS personality with various tool conflicts."""
    colored_print("🎭 SDS Personality Examples:", Colors.MAGENTA + Colors.BOLD)
    print()

    messages = [
        (
            "Zig",
            "🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1.\nTry humbling it with: zigup 0.12.1",
        ),
        (
            "Java",
            "☕ Java 8 might not support features from Java 17.\nConsider upgrading: sdk install java 17",
        ),
        ("Rust", "🦀 Rust 1.70.0 trailing 1.71.0.\nUpdate with: rustup update"),
        (
            "Python",
            "🐍 Python 3.8.0 needs upgrade to 3.11.0.\nConsider: pyenv install 3.11.0 && pyenv local 3.11.0",
        ),
        (
            "Node",
            "🟢 Node 16.20.0 vs 18.0.0 in engines - time for an upgrade!\nUpgrade with: nvm install 18.17.0 && nvm use 18.17.0",
        ),
        (
            "Go",
            "🔵 Go 1.19.0 behind 1.21.0.\nUpgrade with: go install golang.org/dl/go1.21.0@latest",
        ),
    ]

    for tool, message in messages:
        colored_print(f"💬 {tool}:", Colors.YELLOW + Colors.BOLD)
        colored_print(f"   {message}", Colors.CYAN)
        print()
        time.sleep(1)


def create_demo_project():
    """Create a temporary demo project with conflicts."""
    demo_dir = Path(tempfile.mkdtemp(prefix="sds_demo_"))

    # Create build.zig.zon
    zon_content = """.{
    .name = "demo-project",
    .version = "0.1.0",
    .minimum_zig_version = "0.12.1",
}"""
    (demo_dir / "build.zig.zon").write_text(zon_content)

    # Create package.json
    package_content = """{
    "name": "demo-project",
    "version": "0.1.0",
    "engines": {
        "node": ">=18.0.0",
        "npm": ">=9.0.0"
    }
}"""
    (demo_dir / "package.json").write_text(package_content)

    # Create build.gradle.kts
    gradle_content = """plugins {
    kotlin("jvm") version "1.8.22"
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
}"""
    (demo_dir / "build.gradle.kts").write_text(gradle_content)

    return demo_dir


def main():
    """Run the SDS demo."""
    colored_print("🧰 SDS - Stupid Dependency Solver Demo", Colors.BOLD + Colors.GREEN)
    colored_print(
        "A doctor for your project that speaks Zig, Gleam, Kotlin, and common sense.",
        Colors.CYAN,
    )

    print("\nThis demo shows how SDS detects and helps fix dependency conflicts")
    print("in polyglot projects. Let's see it in action!\n")

    input("Press Enter to start the demo...")

    # Demo 1: Check command
    demo_header("SDS Check - Detecting Conflicts")
    print("$ cd my-awesome-project")
    simulate_typing("$ sds check")
    demo_sds_check_output()

    input("\nPress Enter to continue...")

    # Demo 2: Fix command
    demo_header("SDS Fix - Suggesting Solutions")
    simulate_typing("$ sds fix")
    demo_sds_fix_output()

    input("\nPress Enter to continue...")

    # Demo 3: Explain command
    demo_header("SDS Explain - Detailed Analysis")
    simulate_typing("$ sds explain")
    demo_sds_explain_output()

    input("\nPress Enter to continue...")

    # Demo 4: Snapshot command
    demo_header("SDS Snapshot - Capture Working State")
    simulate_typing("$ sds snapshot")
    demo_sds_snapshot_output()

    input("\nPress Enter to continue...")

    # Demo 5: Diff command
    demo_header("SDS Diff - Compare Environments")
    colored_print("(After making some changes to the environment)", Colors.YELLOW)
    simulate_typing("$ sds diff")
    demo_sds_diff_output()

    input("\nPress Enter to continue...")

    # Demo 6: Personality
    demo_header("SDS Personality - Conflicts with Character")
    demo_personality_messages()

    input("\nPress Enter to continue...")

    # Demo 7: Real example
    demo_header("Try SDS on a Real Example Project")

    print("SDS comes with example projects you can test:")
    print()
    colored_print("📁 examples/conflicted-zig-project/", Colors.BLUE)
    print("   - Zig project with intentional version conflicts")
    print("   - Perfect for testing ABI mismatch detection")
    print()
    colored_print("📁 examples/polyglot-project/", Colors.BLUE)
    print("   - Multi-language project (Node.js, Kotlin, Gleam, Zig)")
    print("   - Shows cross-language dependency conflicts")
    print()

    print("To try them:")
    colored_print("$ cd examples/conflicted-zig-project", Colors.GREEN)
    colored_print("$ sds check", Colors.GREEN)
    colored_print("$ sds fix", Colors.GREEN)

    print()

    # Demo wrap-up
    demo_header("SDS Philosophy")

    philosophy = [
        "✅ SDS tells you what's broken and why",
        "🔧 SDS suggests minimal, targeted fixes",
        "🏥 SDS is a doctor, not a replacement for your build system",
        "🎭 SDS explains problems with personality and humor",
        "⚡ SDS works offline - no internet required",
        "🤝 SDS doesn't make changes without your permission",
    ]

    for point in philosophy:
        colored_print(point, Colors.GREEN)
        time.sleep(0.5)

    print()
    colored_print(
        '"Dependencies are like teenagers - they never do what you expect,',
        Colors.CYAN + Colors.BOLD,
    )
    colored_print(
        'but with the right approach, you can get them back in line." 🎯',
        Colors.CYAN + Colors.BOLD,
    )

    print("\n" + "=" * 60)
    colored_print(
        "🎉 Demo Complete! Thanks for watching SDS in action.",
        Colors.GREEN + Colors.BOLD,
    )
    print("=" * 60)

    print()
    print("Next steps:")
    print("1. Install SDS: pipx install stupid-dependency-solver")
    print("2. Try it on your projects: sds check")
    print("3. Let SDS help you fix conflicts: sds fix")
    print("4. Create snapshots of working environments: sds snapshot")
    print()
    colored_print("Happy dependency solving! 🧰", Colors.GREEN + Colors.BOLD)


if __name__ == "__main__":
    main()

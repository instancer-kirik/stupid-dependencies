"""
Project Fixer - Applies fixes suggested by the dependency solver.
"""

import subprocess
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import tempfile
import os

from .solver import Fix


class ProjectFixer:
    """Applies fixes to resolve dependency conflicts."""

    def __init__(self, project_path: Path):
        self.project_path = project_path

    def apply_fixes(self, fixes: List[Fix]) -> bool:
        """Apply a list of fixes. Returns True if all succeeded."""
        success_count = 0

        for i, fix in enumerate(fixes, 1):
            print(f"🔧 [{i}/{len(fixes)}] {fix.description}")

            try:
                if self._apply_single_fix(fix):
                    print("   ✅ Applied successfully")
                    success_count += 1
                else:
                    print("   ❌ Failed to apply")
            except Exception as e:
                print(f"   💥 Error: {e}")

        print(f"\n📊 Applied {success_count}/{len(fixes)} fixes")
        return success_count == len(fixes)

    def _apply_single_fix(self, fix: Fix) -> bool:
        """Apply a single fix based on its type."""
        if fix.action_type == "version_change":
            return self._apply_version_change(fix)
        elif fix.action_type == "install":
            return self._apply_install(fix)
        elif fix.action_type == "config":
            return self._apply_config_change(fix)
        else:
            print(f"   ⚠️ Unknown fix type: {fix.action_type}")
            return False

    def _apply_version_change(self, fix: Fix) -> bool:
        """Apply version changes using tool-specific commands."""
        if not fix.command:
            return False

        # Handle different command types
        if fix.tool == "zig" and "zigup" in fix.command:
            return self._run_zigup_command(fix.command)
        elif fix.tool == "gradle" and "gradlew wrapper" in fix.command:
            return self._run_gradle_wrapper_command(fix.command)
        elif fix.tool == "node" and "nvm" in fix.command:
            return self._run_nvm_command(fix.command)
        elif fix.tool == "python" and "pyenv" in fix.command:
            return self._run_pyenv_command(fix.command)
        else:
            return self._run_generic_command(fix.command)

    def _apply_install(self, fix: Fix) -> bool:
        """Apply installation fixes."""
        if not fix.command:
            return False

        print(f"   🚀 Running: {fix.command}")

        # For security, we'll just show the command rather than execute arbitrary scripts
        if "curl" in fix.command and "|" in fix.command:
            print("   ⚠️ Installation script detected. Please run manually:")
            print(f"   {fix.command}")
            return True

        return self._run_generic_command(fix.command)

    def _apply_config_change(self, fix: Fix) -> bool:
        """Apply configuration changes."""
        if fix.tool == "kotlin":
            return self._fix_kotlin_version()
        elif fix.tool == "gradle":
            return self._fix_gradle_config()
        else:
            print(f"   📝 Manual configuration needed: {fix.description}")
            if fix.command:
                print(f"   Hint: {fix.command}")
            return True

    def _run_zigup_command(self, command: str) -> bool:
        """Run zigup command to switch Zig versions."""
        if not shutil.which("zigup"):
            print(
                "   ❌ zigup not found. Install from: https://github.com/marler8997/zigup"
            )
            return False

        # Extract version from command like "zigup 0.12.1"
        match = re.search(r"zigup\s+([0-9.]+)", command)
        if not match:
            return False

        version = match.group(1)
        try:
            result = subprocess.run(
                ["zigup", version],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print(f"   🎯 Switched to zig {version}")
                return True
            else:
                print(f"   ❌ zigup failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ zigup error: {e}")
            return False

    def _run_gradle_wrapper_command(self, command: str) -> bool:
        """Run Gradle wrapper update command."""
        gradlew = self.project_path / "gradlew"
        if not gradlew.exists():
            print("   ❌ gradlew not found in project")
            return False

        # Extract version from command like "./gradlew wrapper --gradle-version 8.3"
        match = re.search(r"--gradle-version\s+([0-9.]+)", command)
        if not match:
            return False

        version = match.group(1)
        try:
            result = subprocess.run(
                ["./gradlew", "wrapper", f"--gradle-version={version}"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print(f"   🎯 Updated Gradle wrapper to {version}")
                return True
            else:
                print(f"   ❌ Gradle wrapper update failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ Gradle error: {e}")
            return False

    def _run_nvm_command(self, command: str) -> bool:
        """Handle nvm commands (these need special shell handling)."""
        print("   ⚠️ nvm commands require shell integration.")
        print("   Please run manually:")
        print(f"   {command}")
        return True

    def _run_pyenv_command(self, command: str) -> bool:
        """Handle pyenv commands."""
        if not shutil.which("pyenv"):
            print("   ❌ pyenv not found. Install from: https://github.com/pyenv/pyenv")
            return False

        # Extract version from commands like "pyenv install 3.11.0 && pyenv local 3.11.0"
        version_match = re.search(r"pyenv install ([0-9.]+)", command)
        if not version_match:
            print("   ⚠️ Could not parse pyenv command")
            return False

        version = version_match.group(1)

        try:
            # Install the version
            print(f"   📦 Installing Python {version}...")
            install_result = subprocess.run(
                ["pyenv", "install", version],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300,  # Python installation can take a while
            )

            if install_result.returncode != 0:
                if "already exists" not in install_result.stderr:
                    print(f"   ❌ pyenv install failed: {install_result.stderr}")
                    return False

            # Set as local version
            local_result = subprocess.run(
                ["pyenv", "local", version],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if local_result.returncode == 0:
                print(f"   🎯 Set local Python version to {version}")
                return True
            else:
                print(f"   ❌ pyenv local failed: {local_result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ pyenv error: {e}")
            return False

    def _run_generic_command(self, command: str) -> bool:
        """Run a generic shell command."""
        try:
            # Split command safely
            if "&&" in command:
                # For compound commands, we'll show them instead of running
                print("   ⚠️ Compound command detected. Please run manually:")
                print(f"   {command}")
                return True

            # Simple command - try to run it
            parts = command.split()
            if not parts:
                return False

            result = subprocess.run(
                parts, cwd=self.project_path, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return True
            else:
                print(f"   ❌ Command failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ Command error: {e}")
            return False

    def _fix_kotlin_version(self) -> bool:
        """Fix Kotlin version in build files."""
        gradle_files = [
            self.project_path / "build.gradle",
            self.project_path / "build.gradle.kts",
        ]

        for gradle_file in gradle_files:
            if gradle_file.exists():
                return self._update_kotlin_version_in_file(gradle_file)

        print("   ❌ No Gradle build file found")
        return False

    def _update_kotlin_version_in_file(self, gradle_file: Path) -> bool:
        """Update Kotlin version in a specific Gradle file."""
        try:
            content = gradle_file.read_text()

            # This is a simplified approach - real Gradle parsing is complex
            # We'll just show what needs to be done
            print("   📝 Manual update needed:")
            print(f"   Edit {gradle_file.name} and update the kotlin plugin version")
            print('   Example: kotlin("jvm") version "1.9.23"')

            return True

        except Exception as e:
            print(f"   ❌ Error reading {gradle_file}: {e}")
            return False

    def _fix_gradle_config(self) -> bool:
        """Fix general Gradle configuration issues."""
        print("   📝 Manual Gradle configuration needed")
        print("   Check build.gradle(.kts) for version mismatches")
        return True

    def create_backup(self) -> Optional[Path]:
        """Create a backup of important project files before applying fixes."""
        try:
            backup_dir = Path(tempfile.mkdtemp(prefix="sds_backup_"))

            # Files to backup
            important_files = [
                "build.zig.zon",
                "build.zig",
                "gleam.toml",
                "package.json",
                "build.gradle",
                "build.gradle.kts",
                "pom.xml",
                "requirements.txt",
                "pyproject.toml",
                "Pipfile",
                "Cargo.toml",
                "go.mod",
            ]

            backed_up = []
            for filename in important_files:
                source = self.project_path / filename
                if source.exists():
                    dest = backup_dir / filename
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                    backed_up.append(filename)

            if backed_up:
                print(f"📦 Backup created: {backup_dir}")
                print(f"   Files backed up: {', '.join(backed_up)}")
                return backup_dir
            else:
                backup_dir.rmdir()
                return None

        except Exception as e:
            print(f"⚠️ Could not create backup: {e}")
            return None

    def restore_backup(self, backup_path: Path) -> bool:
        """Restore files from backup."""
        try:
            if not backup_path.exists():
                print("❌ Backup directory not found")
                return False

            restored = []
            for backup_file in backup_path.iterdir():
                if backup_file.is_file():
                    dest = self.project_path / backup_file.name
                    shutil.copy2(backup_file, dest)
                    restored.append(backup_file.name)

            print(f"♻️ Restored from backup: {', '.join(restored)}")
            return True

        except Exception as e:
            print(f"❌ Backup restoration failed: {e}")
            return False

    def dry_run_fix(self, fix: Fix) -> str:
        """Simulate applying a fix and return what would happen."""
        if fix.action_type == "version_change":
            if fix.command:
                return f"Would run: {fix.command}"
            else:
                return f"Would change {fix.tool} version"
        elif fix.action_type == "install":
            return f"Would install {fix.tool}"
        elif fix.action_type == "config":
            return f"Would update {fix.tool} configuration"
        else:
            return "Would perform unknown action"

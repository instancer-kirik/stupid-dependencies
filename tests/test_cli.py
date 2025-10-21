"""
Tests for SDS CLI functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from sds.cli import main, cmd_check, cmd_fix, cmd_snapshot, cmd_diff, cmd_explain
from sds.core.solver import Conflict, Fix


class TestCLI:
    """Test the command-line interface."""

    def test_main_no_args(self, capsys):
        """Test that help is shown when no arguments are provided."""
        with patch("sys.argv", ["sds"]):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "usage:" in captured.out.lower() or "help" in captured.out.lower()

    def test_main_with_check_command(self):
        """Test main function with check command."""
        with (
            patch("sys.argv", ["sds", "check"]),
            patch("sds.cli.cmd_check", return_value=0) as mock_check,
        ):
            result = main()
            assert result == 0
            mock_check.assert_called_once()

    def test_main_keyboard_interrupt(self, capsys):
        """Test graceful handling of keyboard interrupt."""
        with (
            patch("sys.argv", ["sds", "check"]),
            patch("sds.cli.cmd_check", side_effect=KeyboardInterrupt),
        ):
            result = main()
            captured = capsys.readouterr()
            assert result == 1
            assert "Interrupted by user" in captured.out


class TestCheckCommand:
    """Test the check command functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_dependencies(self):
        """Mock the core SDS dependencies."""
        with (
            patch("sds.cli.EnvironmentDetector") as mock_detector,
            patch("sds.cli.ManifestParser") as mock_parser,
            patch("sds.cli.DependencySolver") as mock_solver,
        ):
            yield {
                "detector": mock_detector,
                "parser": mock_parser,
                "solver": mock_solver,
            }

    def test_check_no_conflicts(self, temp_project_dir, mock_dependencies, capsys):
        """Test check command when no conflicts are found."""
        # Setup mocks
        mock_detector_instance = mock_dependencies["detector"].return_value
        mock_parser_instance = mock_dependencies["parser"].return_value
        mock_solver_instance = mock_dependencies["solver"].return_value

        mock_detector_instance.detect_all.return_value = {"zig": {"version": "0.12.1"}}
        mock_parser_instance.parse_all.return_value = {
            "build.zig.zon": {"minimum_zig_version": "0.12.1"}
        }
        mock_solver_instance.find_conflicts.return_value = []

        result = cmd_check(temp_project_dir)

        captured = capsys.readouterr()
        assert result == 0
        assert "All good!" in captured.out
        assert "buildable" in captured.out

    def test_check_with_conflicts(self, temp_project_dir, mock_dependencies, capsys):
        """Test check command when conflicts are found."""
        # Setup mocks
        mock_detector_instance = mock_dependencies["detector"].return_value
        mock_parser_instance = mock_dependencies["parser"].return_value
        mock_solver_instance = mock_dependencies["solver"].return_value

        mock_detector_instance.detect_all.return_value = {"zig": {"version": "0.13.0"}}
        mock_parser_instance.parse_all.return_value = {
            "build.zig.zon": {"minimum_zig_version": "0.12.1"}
        }

        conflict = Conflict(
            tool="zig",
            severity="error",
            message="version mismatch",
            reason="ABI mismatch",
            current_version="0.13.0",
            required_version="0.12.1",
        )
        mock_solver_instance.find_conflicts.return_value = [conflict]

        result = cmd_check(temp_project_dir)

        captured = capsys.readouterr()
        assert result == 1  # Should return 1 for errors
        assert "zig" in captured.out
        assert "version mismatch" in captured.out
        assert "not buildable" in captured.out
        assert "sds fix" in captured.out

    def test_check_with_warnings_only(
        self, temp_project_dir, mock_dependencies, capsys
    ):
        """Test check command with warning-level conflicts."""
        mock_detector_instance = mock_dependencies["detector"].return_value
        mock_parser_instance = mock_dependencies["parser"].return_value
        mock_solver_instance = mock_dependencies["solver"].return_value

        mock_detector_instance.detect_all.return_value = {"gradle": {"version": "8.5"}}
        mock_parser_instance.parse_all.return_value = {
            "build.gradle": {"gradle_version": "8.3"}
        }

        conflict = Conflict(
            tool="gradle",
            severity="warning",
            message="minor version mismatch",
            reason="minor mismatch",
            current_version="8.5",
            required_version="8.3",
        )
        mock_solver_instance.find_conflicts.return_value = [conflict]

        result = cmd_check(temp_project_dir)

        captured = capsys.readouterr()
        assert result == 0  # Should return 0 for warnings only
        assert "buildable with warnings" in captured.out

    def test_check_verbose_mode(self, temp_project_dir, mock_dependencies, capsys):
        """Test check command with verbose output."""
        mock_detector_instance = mock_dependencies["detector"].return_value
        mock_parser_instance = mock_dependencies["parser"].return_value
        mock_solver_instance = mock_dependencies["solver"].return_value

        mock_detector_instance.detect_all.return_value = {"zig": {"version": "0.12.1"}}
        mock_parser_instance.parse_all.return_value = {}
        mock_solver_instance.find_conflicts.return_value = []

        result = cmd_check(temp_project_dir, verbose=True)

        captured = capsys.readouterr()
        assert result == 0
        assert "Project:" in captured.out
        assert "Found tools:" in captured.out


class TestFixCommand:
    """Test the fix command functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_dependencies(self):
        with (
            patch("sds.cli.EnvironmentDetector") as mock_detector,
            patch("sds.cli.ManifestParser") as mock_parser,
            patch("sds.cli.DependencySolver") as mock_solver,
            patch("sds.cli.ProjectFixer") as mock_fixer,
        ):
            yield {
                "detector": mock_detector,
                "parser": mock_parser,
                "solver": mock_solver,
                "fixer": mock_fixer,
            }

    def test_fix_no_conflicts(self, temp_project_dir, mock_dependencies, capsys):
        """Test fix command when no conflicts exist."""
        mock_solver_instance = mock_dependencies["solver"].return_value
        mock_solver_instance.find_conflicts.return_value = []

        result = cmd_fix(temp_project_dir)

        captured = capsys.readouterr()
        assert result == 0
        assert "Nothing to fix" in captured.out
        assert "already healthy" in captured.out

    def test_fix_with_suggested_fixes(
        self, temp_project_dir, mock_dependencies, capsys
    ):
        """Test fix command with available fixes."""
        mock_solver_instance = mock_dependencies["solver"].return_value
        mock_fixer_instance = mock_dependencies["fixer"].return_value

        conflict = Conflict(
            tool="zig",
            severity="error",
            message="version mismatch",
            reason="ABI mismatch",
        )
        fix = Fix(
            description="Downgrade zig to 0.12.1",
            command="zigup 0.12.1",
            risk_level="low",
            tool="zig",
        )

        mock_solver_instance.find_conflicts.return_value = [conflict]
        mock_solver_instance.suggest_fixes.return_value = [fix]

        # Test without applying fixes
        with patch("builtins.input", return_value="n"):
            result = cmd_fix(temp_project_dir)

        captured = capsys.readouterr()
        assert result == 0
        assert "Suggested actions:" in captured.out
        assert "Downgrade zig to 0.12.1" in captured.out
        assert "zigup 0.12.1" in captured.out
        assert "No changes made" in captured.out

    def test_fix_apply_fixes_success(self, temp_project_dir, mock_dependencies, capsys):
        """Test fix command with successful fix application."""
        mock_solver_instance = mock_dependencies["solver"].return_value
        mock_fixer_instance = mock_dependencies["fixer"].return_value

        conflict = Conflict(tool="zig", severity="error", message="test", reason="test")
        fix = Fix(description="Test fix", command="test command", tool="zig")

        mock_solver_instance.find_conflicts.return_value = [conflict]
        mock_solver_instance.suggest_fixes.return_value = [fix]
        mock_fixer_instance.apply_fixes.return_value = True

        result = cmd_fix(temp_project_dir, apply=True)

        captured = capsys.readouterr()
        assert result == 0
        assert "Applying fixes" in captured.out
        assert "All fixes applied successfully" in captured.out

    def test_fix_dry_run(self, temp_project_dir, mock_dependencies, capsys):
        """Test fix command in dry run mode."""
        mock_solver_instance = mock_dependencies["solver"].return_value

        conflict = Conflict(tool="zig", severity="error", message="test", reason="test")
        fix = Fix(description="Test fix", command="test command", tool="zig")

        mock_solver_instance.find_conflicts.return_value = [conflict]
        mock_solver_instance.suggest_fixes.return_value = [fix]

        result = cmd_fix(temp_project_dir, dry_run=True)

        captured = capsys.readouterr()
        assert result == 0
        assert "Dry run" in captured.out
        assert "no changes made" in captured.out


class TestSnapshotCommand:
    """Test the snapshot command functionality."""

    def test_snapshot_creates_file(self, capsys):
        """Test that snapshot command creates sds.lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            with patch("sds.cli.EnvironmentDetector") as mock_detector:
                mock_detector_instance = mock_detector.return_value
                mock_detector_instance.detect_all.return_value = {
                    "zig": {"version": "0.12.1"},
                    "node": {"version": "18.17.0"},
                }

                result = cmd_snapshot(project_path)

                captured = capsys.readouterr()
                assert result == 0
                assert "snapshot saved" in captured.out.lower()
                assert "zig = 0.12.1" in captured.out
                assert "node = 18.17.0" in captured.out

                # Check that sds.lock file was created
                sds_lock = project_path / "sds.lock"
                assert sds_lock.exists()

                # Verify content
                content = sds_lock.read_text()
                assert 'zig = "0.12.1"' in content
                assert 'node = "18.17.0"' in content

    def test_snapshot_no_tools_detected(self, capsys):
        """Test snapshot command when no tools are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            with patch("sds.cli.EnvironmentDetector") as mock_detector:
                mock_detector_instance = mock_detector.return_value
                mock_detector_instance.detect_all.return_value = {}

                result = cmd_snapshot(project_path)

                captured = capsys.readouterr()
                assert result == 1
                assert "No development tools detected" in captured.out


if __name__ == "__main__":
    pytest.main([__file__])

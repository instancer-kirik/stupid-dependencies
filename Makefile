# Makefile for SDS - Stupid Dependency Solver
# A doctor for your project that speaks Zig, Gleam, Kotlin, and common sense.

.PHONY: help install install-dev test test-verbose test-cov lint format type-check security clean build upload docs run-example

# Default target
help:
	@echo "🧰 SDS - Stupid Dependency Solver"
	@echo "Available commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  install      - Install SDS in development mode"
	@echo "  install-dev  - Install with development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test         - Run tests"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  test-cov     - Run tests with coverage report"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black + isort)"
	@echo "  format-check - Check if code is formatted"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  security     - Run security checks (bandit + safety)"
	@echo ""
	@echo "🏗️ Build & Release:"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  upload       - Upload to PyPI (requires credentials)"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs         - Build documentation"
	@echo ""
	@echo "🚀 Examples:"
	@echo "  run-example  - Run SDS on example project"
	@echo "  demo         - Show SDS demo output"

# Installation
install:
	@echo "📦 Installing SDS in development mode..."
	pip install -e .

install-dev:
	@echo "📦 Installing SDS with development dependencies..."
	pip install -e .
	pip install -r requirements-dev.txt

# Testing
test:
	@echo "🧪 Running tests..."
	pytest

test-verbose:
	@echo "🧪 Running tests (verbose)..."
	pytest -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=sds --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report generated in htmlcov/"

# Code Quality
lint:
	@echo "🔍 Running linter..."
	flake8 sds/ tests/

format:
	@echo "🎨 Formatting code..."
	black sds/ tests/
	isort sds/ tests/

format-check:
	@echo "🎨 Checking code formatting..."
	black --check sds/ tests/
	isort --check-only sds/ tests/

type-check:
	@echo "🔍 Running type checker..."
	mypy sds/

security:
	@echo "🔒 Running security checks..."
	bandit -r sds/
	safety check

# All quality checks
quality: lint format-check type-check security
	@echo "✅ All quality checks passed!"

# Build and Release
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	@echo "🏗️ Building distribution packages..."
	python -m build

upload: build
	@echo "🚀 Uploading to PyPI..."
	twine upload dist/*

# Documentation
docs:
	@echo "📚 Building documentation..."
	@echo "📝 Documentation setup not yet implemented"
	@echo "   TODO: Add Sphinx documentation"

# Examples and Demo
run-example:
	@echo "🚀 Running SDS on example projects..."
	@echo "Creating temporary test projects..."
	@mkdir -p /tmp/sds-test-zig
	@echo '.{.name = "test", .version = "0.1.0", .minimum_zig_version = "0.12.1"}' > /tmp/sds-test-zig/build.zig.zon
	@echo "🎯 Testing Zig project..."
	cd /tmp/sds-test-zig && sds check || true
	@echo ""
	@mkdir -p /tmp/sds-test-node
	@echo '{"name": "test", "engines": {"node": ">=18.0.0"}}' > /tmp/sds-test-node/package.json
	@echo "🎯 Testing Node project..."
	cd /tmp/sds-test-node && sds check || true
	@echo ""
	@echo "🧹 Cleaning up..."
	@rm -rf /tmp/sds-test-zig /tmp/sds-test-node

demo:
	@echo "🎬 SDS Demo Output:"
	@echo ""
	@echo "🩺 Scanning project..."
	@echo "[zig] build.zig.zon requires zig 0.12.x, found 0.13.0 → ⚠️ ABI mismatch"
	@echo "[gleam] compiler 1.1.0 ok"
	@echo "[kotlin] Gradle 8.5 found, target 8.3 declared → ⚠️ minor mismatch"
	@echo "Status: not buildable"
	@echo "Run \`sds fix\` for repair suggestions."
	@echo ""
	@echo "$ sds fix"
	@echo "🔧 Suggested actions:"
	@echo "1. Downgrade zig to 0.12.1 (matches zon manifest) 🟢"
	@echo "   → zigup 0.12.1"
	@echo "2. Sync Gradle wrapper to 8.3 🟢"
	@echo "   → ./gradlew wrapper --gradle-version 8.3"
	@echo ""
	@echo "🤔 Detected zig 0.13.0, which thinks it's better than 0.12.1."
	@echo "Try humbling it with: zigup 0.12.1"

# Development workflow
dev-setup: install-dev
	@echo "🔧 Setting up development environment..."
	pre-commit install || echo "⚠️  pre-commit not available"

dev-check: format lint type-check test
	@echo "✅ Development checks complete!"

# CI/CD helpers
ci-test:
	@echo "🤖 CI: Running tests..."
	pytest --cov=sds --cov-report=xml

ci-quality:
	@echo "🤖 CI: Running quality checks..."
	black --check sds/ tests/
	flake8 sds/ tests/
	mypy sds/
	bandit -r sds/

# Release helpers
version-bump-patch:
	@echo "📈 Bumping patch version..."
	@echo "TODO: Implement version bumping"

version-bump-minor:
	@echo "📈 Bumping minor version..."
	@echo "TODO: Implement version bumping"

# Quick commands for common tasks
check: lint type-check
fix: format
all: clean install-dev quality test build

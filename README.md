# pytreqt - Requirements Traceability for Python Tests

A pytest plugin and CLI tool for tracking requirements coverage in test suites.

## Features

- ✅ **Validates** requirement IDs in test docstrings against specification files
- 🎨 **Colorful reporting** with ✓ (passed), ✗ (failed), ⊝ (skipped) status
- 📊 **Coverage analysis** showing which requirements are tested
- 🚫 **Prevents typos** by catching invalid requirement references
- 📈 **Auto-generates** TEST_COVERAGE.md with traceability matrix
- 🔍 **Change detection** identifies tests affected by requirement updates

## Installation

```bash
pip install pytreqt
```

## Quick Start

```bash
# Generate initial configuration
pytreqt init

# Run coverage analysis
pytreqt coverage

# Show last run results
pytreqt show
```

## pytest Integration

Add to your `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-p pytreqt"
```

## Configuration

Create a `pytreqt.toml` file or add to your `pyproject.toml`:

```toml
[tool.pytreqt]
requirements_file = "docs/requirements.md"
requirement_patterns = ["FR-\\d+\\.?\\d*", "BR-\\d+\\.?\\d*"]
```

## Development

### Local Testing with Nox

We use [Nox](https://nox.thea.codes/) for testing across multiple Python and pytest versions:

```bash
# Install nox
uv add --dev nox

# Test all Python/pytest combinations
uv run nox

# Test specific Python version
uv run nox -s tests-3.13

# Test specific combination
uv run nox -s "tests-3.13(pytest_version='8.3')"

# Run linting and type checking
uv run nox -s lint mypy

# Generate coverage report
uv run nox -s coverage

# List all available sessions
uv run nox --list
```

**Available sessions**:
- `tests-{python}(pytest_version='{version}')` - Run tests with specific Python/pytest versions
- `lint-{python}` - Run ruff linting
- `mypy-{python}` - Run type checking
- `format_check-{python}` - Check code formatting
- `format` - Format code
- `coverage` - Generate coverage report

**Supported versions**:
- Python: 3.10, 3.11, 3.12, 3.13
- pytest: 8.0, 8.3
- Automatically skips incompatible combinations (e.g., Python 3.13 + pytest 8.0)

### Manual Development

```bash
# Install in development mode
uv sync --all-extras --dev

# Run tests
uv run pytest tests/

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/
```

This package is in active development. Features and API may change.

## License

MIT License. See LICENSE file for details.

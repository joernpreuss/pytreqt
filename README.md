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

This package is in active development. Features and API may change.

## License

MIT License - see LICENSE file for details.
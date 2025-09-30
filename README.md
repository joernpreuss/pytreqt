# pytreqt

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Requirements traceability for Python test suites** – Ensure every requirement is tested and every test is traceable.

A pytest plugin and CLI tool that validates requirement coverage, prevents specification drift, and auto-generates traceability documentation for compliance-critical projects.

---

## Why pytreqt?

In regulated industries (medical devices, aerospace, automotive) and quality-critical software, you need to prove that every requirement has corresponding tests. Manual traceability matrices become outdated instantly. **pytreqt** automates this:

- **Prevents broken references**: Catches typos in requirement IDs before they reach production
- **Enforces bidirectional traceability**: Links requirements ↔ tests in both directions
- **Detects coverage gaps**: Shows which requirements lack test coverage
- **Identifies change impact**: When a requirement changes, immediately see affected tests
- **Generates compliance artifacts**: Auto-creates TEST_COVERAGE.md for audits and reviews

---

## Features

| Feature | Description |
|---------|-------------|
| ✅ **Real-time validation** | Validates requirement IDs in test docstrings against specification files during test runs |
| 🎨 **Rich terminal output** | Colorful reporting with ✓ (passed), ✗ (failed), ⊝ (skipped) status indicators |
| 📊 **Coverage analysis** | Reports showing which requirements are tested and which are missing |
| 🚫 **Typo prevention** | Catches invalid requirement references before they cause compliance issues |
| 📈 **Auto-generated docs** | Creates TEST_COVERAGE.md with complete traceability matrix |
| 🔍 **Change detection** | Identifies tests affected by requirement updates |
| 🔌 **Seamless integration** | Works as both a pytest plugin and standalone CLI tool |
| ⚙️ **Flexible configuration** | Supports custom requirement patterns (FR-*, US-*, REQ-*, etc.) |

---

## Installation

```bash
pip install pytreqt
```

Or with `uv` (recommended):

```bash
uv add pytreqt
```

---

## Quick Start

### 1. Initialize configuration

```bash
pytreqt init
```

This creates a `pytreqt.toml` configuration file with sensible defaults.

### 2. Write tests with requirement references

```python
def test_user_login():
    """
    Verify user authentication functionality.

    Tests: FR-1.1, FR-1.2
    """
    assert authenticate_user("user", "password") == True
```

### 3. Run coverage analysis

```bash
pytreqt coverage
```

### 4. View results

```bash
pytreqt show
```

---

## Configuration

Create a `pytreqt.toml` file or add to your `pyproject.toml`:

```toml
[tool.pytreqt]
requirements_file = "docs/requirements.md"
requirement_patterns = ["FR-\\d+\\.?\\d*", "BR-\\d+\\.?\\d*"]
```

### Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `requirements_file` | Path to requirements specification | `"docs/requirements.md"` |
| `requirement_patterns` | Regex patterns for requirement IDs | `["FR-\\d+", "US-\\d+"]` |

---

## pytest Integration

pytreqt works seamlessly as a pytest plugin. Enable it in your `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-p pytreqt"
```

Now pytreqt will automatically validate requirement references during test runs:

```bash
pytest  # pytreqt validation runs automatically
```

---

## Use Cases

### Medical Device Software (IEC 62304)
Ensure every safety requirement has corresponding test coverage and maintain traceability matrices for regulatory submissions.

### Automotive (ISO 26262)
Track safety requirements through the entire test suite, automatically detect untested requirements.

### Aerospace (DO-178C)
Generate traceability documentation required for certification, validate requirement-test linkage.

### Financial Systems
Maintain compliance audit trails, prove that security requirements are properly tested.

### Agile Teams
Keep living documentation synchronized with tests, prevent requirement drift during rapid iterations.

---

## Development

### Prerequisites

- Python 3.10 or newer
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/pytreqt/pytreqt.git
cd pytreqt

# Install in development mode with all dependencies
uv sync --all-extras --dev
```

### Testing with Nox

We use [Nox](https://nox.thea.codes/) for automated testing across multiple Python and pytest versions:

```bash
# Test all Python/pytest combinations
uv run nox

# Test specific Python version
uv run nox -s tests-3.13

# Test specific combination
uv run nox -s "tests-3.13(pytest_version='8.3')"

# Run quality checks
uv run nox -s lint mypy

# Generate coverage report
uv run nox -s coverage

# List all available sessions
uv run nox --list
```

**Supported test matrix**:
- Python: 3.10, 3.11, 3.12, 3.13
- pytest: 8.0, 8.3
- Automatically skips incompatible combinations

### Manual Development Commands

```bash
# Run tests
uv run pytest tests/

# Linting and formatting
uv run ruff check src/
uv run ruff format src/

# Type checking
uv run mypy src/

# Check file endings
uv run ./src/pytreqt/tools/check_newlines.py
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Run** quality checks: `uv run nox`
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

Please ensure:
- All tests pass across supported Python/pytest versions
- Code follows ruff formatting standards
- Type hints are present and mypy checks pass
- Documentation is updated for new features

---

## Project Status

🚧 **Alpha** – This package is in active development. Core features are functional, but the API may change. Production use is possible but expect updates.

**Roadmap**:
- [ ] Support for additional requirement formats (YAML, JSON, DOORS exports)
- [ ] Integration with CI/CD systems (GitHub Actions, GitLab CI)
- [ ] HTML report generation
- [ ] VSCode extension for real-time validation
- [ ] Requirements change impact visualization

---

## License

MIT License - Copyright (c) 2025 Jörn Preuß

See [LICENSE](LICENSE) file for full details.

---

## Author

**Jörn Preuß**
📧 [joern.preuss@gmail.com](mailto:joern.preuss@gmail.com)
🔗 [GitHub](https://github.com/pytreqt/pytreqt)

---

## Acknowledgments

Built with:
- [pytest](https://pytest.org) – Testing framework
- [Click](https://click.palletsprojects.com) – CLI interface
- [Rich](https://rich.readthedocs.io) – Terminal formatting
- [Nox](https://nox.thea.codes) – Test automation

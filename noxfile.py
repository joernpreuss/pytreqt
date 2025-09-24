"""Nox configuration for testing pytreqt across multiple Python/pytest versions."""

import nox

# Python versions to test
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

# Pytest versions to test
PYTEST_VERSIONS = ["8.0", "8.3"]


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("pytest_version", PYTEST_VERSIONS)
def tests(session: nox.Session, pytest_version: str) -> None:
    """Run tests with different Python and pytest versions."""
    # Skip incompatible combinations
    if session.python == "3.13" and pytest_version == "8.0":
        session.skip("Python 3.13 + pytest 8.0 has AST compatibility issues")

    # Install dependencies
    session.install("-e", ".[dev]")
    session.install(f"pytest=={pytest_version}")

    # Run tests
    session.run("pytest", "tests/", "-v", "--tb=short")


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Run linting with different Python versions."""
    session.install("-e", ".[dev]")
    session.run("ruff", "check", "src/")


@nox.session(python=PYTHON_VERSIONS)
def mypy(session: nox.Session) -> None:
    """Run type checking with different Python versions."""
    session.install("-e", ".[dev]")
    session.run("mypy", "src/")


@nox.session(python=PYTHON_VERSIONS)
def format_check(session: nox.Session) -> None:
    """Check code formatting."""
    session.install("-e", ".[dev]")
    session.run("ruff", "format", "src/", "tests/", "--check")


@nox.session
def format(session: nox.Session) -> None:
    """Format code."""
    session.install("-e", ".[dev]")
    session.run("ruff", "format", "src/", "tests/")


@nox.session
def newlines(session: nox.Session) -> None:
    """Check trailing newlines in files."""
    session.install("-e", ".")
    session.run("python", "-m", "pytreqt.tools.check_newlines")


@nox.session(python="3.12")
def coverage(session: nox.Session) -> None:
    """Run tests with coverage reporting."""
    session.install("-e", ".[dev]")
    session.install("coverage[toml]")
    session.run("coverage", "run", "-m", "pytest", "tests/")
    session.run("coverage", "report")
    session.run("coverage", "html")

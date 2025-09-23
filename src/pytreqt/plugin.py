"""
Custom pytest plugin to extract and display requirements coverage from test docstrings.

This plugin parses test docstrings for requirement references and can generate
coverage reports showing which requirements are tested.
"""

import getpass
import json
import os
import platform
import socket
import subprocess
import sys
from collections import defaultdict
from datetime import datetime

import pytest
from rich.console import Console

from .config import get_config
from .requirements import RequirementsParser


class RequirementsCollector:
    """Collects requirements coverage from test docstrings."""

    def __init__(self):
        self.test_requirements: dict[str, set[str]] = {}
        self.requirement_tests: dict[str, list[str]] = defaultdict(list)
        self.test_results: dict[str, str] = {}  # Track test outcomes
        self.parser = RequirementsParser()
        self.config = get_config()

    def collect_test_requirements(self, item: pytest.Item) -> None:
        """Collect requirements from a test item's docstring."""
        if item.function.__doc__:
            requirements = self.parser.extract_requirements(item.function.__doc__)
            if requirements:
                # Validate requirements exist in requirements file
                self.parser.validate_requirements(requirements, item.nodeid)

                # Use item.nodeid for consistency with test result capture
                test_name = item.nodeid
                self.test_requirements[test_name] = requirements

                for req in requirements:
                    self.requirement_tests[req].append(test_name)


# Global collector instance
requirements_collector = RequirementsCollector()


# Remove pytest_configure_node - not a standard pytest hook
# Worker node configuration handled through other mechanisms


# Remove pytest_testnodedown - not a standard pytest hook
# Worker communication handled through other mechanisms


def pytest_runtest_logreport(report):
    """Called for each test report - runs on workers, sends data to master."""
    # Only handle the main test call
    if report.when == "call" and hasattr(report, "nodeid"):
        # Get requirements for this test
        test_name = report.nodeid
        if test_name in requirements_collector.test_requirements:
            # Send requirements data to master via the report
            requirements = requirements_collector.test_requirements[test_name]
            if not hasattr(report, "_requirements_data"):
                report._requirements_data = {
                    "test_requirements": {test_name: requirements},
                    "requirement_tests": {},
                    "test_results": {test_name: report.outcome},
                }
                # Build requirement_tests mapping
                for req in requirements:
                    if req not in report._requirements_data["requirement_tests"]:
                        report._requirements_data["requirement_tests"][req] = []
                    report._requirements_data["requirement_tests"][req].append(
                        test_name
                    )


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Hook called before each test runs - collect requirements."""
    requirements_collector.collect_test_requirements(item)

    # Show docstring if flag is set
    if item.config.getoption("--show-docstrings") and item.function.__doc__:
        item.config.hook.pytest_runtest_logstart(
            nodeid=item.nodeid, location=item.location
        )
        print(f"\n{item.function.__doc__.strip()}")
        print("-" * 40)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook called after each test runs - capture results."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":  # Only capture the main test call, not setup/teardown
        requirements_collector.test_results[item.nodeid] = report.outcome
    elif report.when == "setup" and report.outcome == "skipped":
        # Handle skipped tests (they don't reach "call" phase)
        requirements_collector.test_results[item.nodeid] = "skipped"


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Hook called at end of test session - generate requirements report."""
    # Check if we should display cached coverage instead of live data
    if getattr(config.option, "show_last_coverage", False):
        _display_cached_coverage(terminalreporter)
        return

    is_xdist_worker = os.getenv("PYTEST_XDIST_WORKER") is not None

    # For xdist master process, collect data from all test reports
    if not is_xdist_worker:
        # Collect requirements data from all test reports
        aggregated_test_requirements: dict[str, set[str]] = {}
        aggregated_requirement_tests: dict[str, list[str]] = defaultdict(list)
        aggregated_test_results: dict[str, str] = {}

        # Check if we have reports with requirements data
        if hasattr(terminalreporter, "stats"):
            for category in ["passed", "failed", "skipped"]:
                if category in terminalreporter.stats:
                    for report in terminalreporter.stats[category]:
                        if hasattr(report, "_requirements_data"):
                            data = report._requirements_data
                            aggregated_test_requirements.update(
                                data["test_requirements"]
                            )
                            aggregated_test_results.update(data["test_results"])
                            for req, tests in data["requirement_tests"].items():
                                for test in tests:
                                    if test not in aggregated_requirement_tests[req]:
                                        aggregated_requirement_tests[req].append(test)

        # If we have aggregated data, temporarily set it in the collector
        if aggregated_test_requirements:
            original_test_requirements = requirements_collector.test_requirements
            original_requirement_tests = requirements_collector.requirement_tests
            original_test_results = requirements_collector.test_results

            requirements_collector.test_requirements = aggregated_test_requirements
            requirements_collector.requirement_tests = defaultdict(
                list, aggregated_requirement_tests
            )
            requirements_collector.test_results = aggregated_test_results

            _save_coverage_data()

            # Restore original data
            requirements_collector.test_requirements = original_test_requirements
            requirements_collector.requirement_tests = original_requirement_tests
            requirements_collector.test_results = original_test_results
        elif requirements_collector.test_requirements:
            # Fallback for single-threaded execution
            _save_coverage_data()

    # Check if verbose mode or custom flag is set
    if terminalreporter.config.getoption("verbose") >= 1 or getattr(
        config.option, "requirements_report", False
    ):
        terminalreporter.section("Requirements Coverage")

        # Use aggregated data if available, otherwise use collector data
        test_requirements = (
            aggregated_test_requirements
            if "aggregated_test_requirements" in locals()
            and aggregated_test_requirements
            else requirements_collector.test_requirements
        )
        requirement_tests = (
            aggregated_requirement_tests
            if "aggregated_requirement_tests" in locals()
            and aggregated_requirement_tests
            else requirements_collector.requirement_tests
        )
        test_results = (
            aggregated_test_results
            if "aggregated_test_results" in locals() and aggregated_test_results
            else requirements_collector.test_results
        )

        # Show tests grouped by requirements
        all_requirements: set[str] = set()
        for reqs in test_requirements.values():
            all_requirements.update(reqs)

        for req in sorted(all_requirements):
            tests = requirement_tests[req]
            terminalreporter.write_line(f"  {req}:")
            for test in tests:
                # Extract just the test function name for brevity
                short_name = test.split("::")[-1]

                # Get test result and show appropriate status
                result = test_results.get(test, "unknown")
                if result == "passed":
                    symbol = terminalreporter._tw.markup("✓", green=True)
                elif result == "failed":
                    symbol = terminalreporter._tw.markup("✗", red=True)
                elif result == "skipped":
                    symbol = terminalreporter._tw.markup("⊝", yellow=True)
                else:
                    symbol = terminalreporter._tw.markup("?", purple=True)

                terminalreporter.write_line(f"    {symbol} {short_name}")

        # Summary statistics
        total_tests = len(test_requirements)
        total_requirements = len(all_requirements)

        terminalreporter.write_line("")
        terminalreporter.write_line("Requirements Coverage Summary:")
        terminalreporter.write_line(f"  Tests with requirements: {total_tests}")
        terminalreporter.write_line(f"  Requirements covered: {total_requirements}")


def pytest_addoption(parser):
    """Add command line option for requirements reporting."""
    parser.addoption(
        "--requirements-report",
        action="store_true",
        default=False,
        help="Show requirements coverage report even without verbose mode",
    )
    parser.addoption(
        "--requirements-only",
        action="store_true",
        default=False,
        help="Show only requirements coverage, skip test execution",
    )
    parser.addoption(
        "--show-docstrings",
        action="store_true",
        default=False,
        help="Show test docstrings during test execution",
    )
    parser.addoption(
        "--show-last-coverage",
        action="store_true",
        default=False,
        help="Show requirements coverage from last test run (cached)",
    )


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    """Modify collected items based on requirements flags."""
    # Always collect requirements for all items during collection phase
    # This ensures workers have the requirements data
    for item in items:
        requirements_collector.collect_test_requirements(item)

    if config.getoption("--requirements-only") or config.getoption(
        "--show-last-coverage"
    ):
        # Skip all test execution
        if config.getoption("--requirements-only"):
            reason = "Requirements analysis only"
        else:
            reason = "Showing cached coverage only"

        skip_marker = pytest.mark.skip(reason=reason)
        for item in items:
            item.add_marker(skip_marker)


# Custom marker for requirements
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "requirements(fr_list, br_list): mark test with specific requirements",
    )


def requirements(*reqs: str):
    """Decorator to explicitly mark tests with requirements.

    Usage:
        @requirements("FR-1.1", "FR-1.2", "BR-2.1")
        def test_something():
            pass
    """

    def decorator(func):
        # Store requirements in function metadata
        func._requirements = {req.upper() for req in reqs}

        # Add to docstring if not already present
        if func.__doc__:
            existing_reqs = requirements_collector.parser.extract_requirements(
                func.__doc__
            )
            new_reqs = {req.upper() for req in reqs} - existing_reqs
            if new_reqs:
                func.__doc__ += (
                    f"\n    Additional requirements: {', '.join(sorted(new_reqs))}"
                )
        else:
            func.__doc__ = (
                f"Requirements: {', '.join(sorted(req.upper() for req in reqs))}"
            )

        return func

    return decorator


def _save_coverage_data():
    """Save current requirements coverage data to cache file (single worker)."""
    config = get_config()
    cache_dir = config.cache_dir
    cache_dir.mkdir(exist_ok=True)

    # Prepare coverage data
    all_requirements = set()
    for reqs in requirements_collector.test_requirements.values():
        all_requirements.update(reqs)

    # Determine database type from environment
    database_type = config.get_database_type()

    # Get comprehensive execution context
    pytest_command = " ".join(sys.argv)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get git information
    git_info: dict[str, str | bool] = {}
    try:
        git_info["branch"] = (
            subprocess.check_output(
                ["git", "branch", "--show-current"],
                cwd=os.getcwd(),
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )

        git_info["commit"] = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=os.getcwd(), stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )

        git_info["commit_short"] = git_info["commit"][:8]  # type: ignore[index]

        # Check if working directory is clean
        git_status = (
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=os.getcwd(),
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        git_info["clean"] = len(git_status) == 0

    except (subprocess.CalledProcessError, FileNotFoundError):
        git_info = {"error": "Git not available or not a git repository"}

    # Capture relevant environment variables
    env_vars = {}
    relevant_env_vars = [
        "TEST_DATABASE",
        "DATABASE_URL",
        "PYTEST_XDIST_WORKER",
        "CI",
        "GITHUB_ACTIONS",
        "VIRTUAL_ENV",
        "CONDA_DEFAULT_ENV",
    ]
    for var in relevant_env_vars:
        if var in os.environ:
            env_vars[var] = os.environ[var]

    coverage_data = {
        "command_info": {
            "command": pytest_command,
            "timestamp": timestamp,
            "database": database_type,
            "working_directory": os.getcwd(),
            "user": getpass.getuser(),
            "hostname": socket.gethostname(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
            "environment_variables": env_vars,
            "git": git_info,
        },
        "requirements": {},
        "summary": {
            "total_tests": len(requirements_collector.test_requirements),
            "total_requirements": len(all_requirements),
        },
    }

    # Store requirements with their tests and results
    for req in sorted(all_requirements):
        tests = requirements_collector.requirement_tests[req]
        coverage_data["requirements"][req] = []  # type: ignore[assignment,index]

        for test in tests:
            short_name = test.split("::")[-1]
            result = requirements_collector.test_results.get(test, "unknown")
            coverage_data["requirements"][req].append(  # type: ignore[attr-defined,index]
                {"test_name": short_name, "full_name": test, "result": result}
            )

    # Save to cache file
    cache_file = cache_dir / "requirements_coverage.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(coverage_data, f, indent=2)


def _display_cached_coverage(terminalreporter):
    """Display requirements coverage from cached data."""
    config = get_config()
    cache_file = config.cache_dir / "requirements_coverage.json"

    if not cache_file.exists():
        terminalreporter.write_line(
            "No cached requirements coverage found. Run tests first.", red=True
        )
        return

    try:
        with open(cache_file, encoding="utf-8") as f:
            coverage_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        terminalreporter.write_line(f"Error reading cached coverage: {e}", red=True)
        return

    terminalreporter.section("Requirements Coverage (Last Run)")

    # Show command info
    command_info = coverage_data.get("command_info", {})
    if command_info:
        terminalreporter.write_line(
            f"Database: {command_info.get('database', 'unknown')}"
        )
        terminalreporter.write_line(
            f"Generated: {command_info.get('timestamp', 'unknown')}"
        )
        terminalreporter.write_line(
            f"Command: {command_info.get('command', 'unknown')}"
        )

        git_info = command_info.get("git", {})
        if "error" not in git_info and git_info:
            branch = git_info.get("branch", "unknown")
            commit_short = git_info.get("commit_short", "unknown")
            clean_status = "clean" if git_info.get("clean", False) else "dirty"
            terminalreporter.write_line(
                f"Git: {branch}@{commit_short} ({clean_status})"
            )

        env_vars = command_info.get("environment_variables", {})
        if env_vars:
            env_str = ", ".join(f"{k}={v}" for k, v in env_vars.items())
            terminalreporter.write_line(f"Environment: {env_str}")

        terminalreporter.write_line("")

    # Display requirements and their tests
    for req in sorted(coverage_data["requirements"].keys()):
        tests = coverage_data["requirements"][req]
        terminalreporter.write_line(f"  {req}:")

        for test_info in tests:
            result = test_info["result"]
            if result == "passed":
                symbol = terminalreporter._tw.markup("✓", green=True)
            elif result == "failed":
                symbol = terminalreporter._tw.markup("✗", red=True)
            elif result == "skipped":
                symbol = terminalreporter._tw.markup("⊝", yellow=True)
            else:
                symbol = terminalreporter._tw.markup("?", purple=True)

            terminalreporter.write_line(f"    {symbol} {test_info['test_name']}")

    # Summary statistics
    summary = coverage_data["summary"]
    terminalreporter.write_line("")
    terminalreporter.write_line("Requirements Coverage Summary:")
    terminalreporter.write_line(f"  Tests with requirements: {summary['total_tests']}")
    terminalreporter.write_line(
        f"  Requirements covered: {summary['total_requirements']}"
    )


def show_requirements_coverage_rich() -> None:
    """Show requirements coverage from last test run using Rich formatting."""
    console = Console(force_terminal=True)
    config = get_config()

    console.print("📋 Showing requirements coverage from last run...", style="cyan")

    cache_file = config.cache_dir / "requirements_coverage.json"
    if not cache_file.exists():
        console.print(
            "❌ No cached requirements coverage found. Run tests first.", style="red"
        )
        return

    try:
        with open(cache_file, encoding="utf-8") as f:
            coverage_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        console.print(f"❌ Error reading cached coverage: {e}", style="red")
        return

    console.print("Requirements Coverage (Last Run)", style="green")
    console.print()

    # Show command info
    command_info = coverage_data.get("command_info", {})
    if command_info:
        console.print(
            f"Database: {command_info.get('database', 'unknown')}", style="dim"
        )
        console.print(
            f"Generated: {command_info.get('timestamp', 'unknown')}", style="dim"
        )
        console.print(f"Command: {command_info.get('command', 'unknown')}", style="dim")

        git_info = command_info.get("git", {})
        if "error" not in git_info and git_info:
            branch = git_info.get("branch", "unknown")
            commit_short = git_info.get("commit_short", "unknown")
            clean_status = "clean" if git_info.get("clean", False) else "dirty"
            console.print(f"Git: {branch}@{commit_short} ({clean_status})", style="dim")

        env_vars = command_info.get("environment_variables", {})
        if env_vars:
            env_str = ", ".join(f"{k}={v}" for k, v in env_vars.items())
            console.print(f"Environment: {env_str}", style="dim")

        console.print()

    # Display requirements and their tests
    for req in sorted(coverage_data["requirements"].keys()):
        tests = coverage_data["requirements"][req]
        console.print(f"  {req}:", style="white")

        for test_info in tests:
            result = test_info["result"]
            if result == "passed":
                symbol = "✓"
                color = "green"
            elif result == "failed":
                symbol = "✗"
                color = "red"
            elif result == "skipped":
                symbol = "⊝"
                color = "yellow"
            else:
                symbol = "?"
                color = "purple"

            console.print(f"    {symbol} {test_info['test_name']}", style=color)

    # Summary statistics
    summary = coverage_data["summary"]
    console.print()
    console.print("Requirements Coverage Summary:", style="cyan")
    console.print(f"  Tests with requirements: {summary['total_tests']}")
    console.print(f"  Requirements covered: {summary['total_requirements']}")

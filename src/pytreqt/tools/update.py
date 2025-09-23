#!/usr/bin/env python3
"""
Update requirements traceability - regenerate coverage and check for changes.
"""

import subprocess
import sys
from pathlib import Path

from ..config import get_config


def _run_command(cmd, description, suppress_output=False):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        if suppress_output:
            subprocess.run(cmd, check=True, cwd=Path.cwd(), capture_output=True)
        else:
            subprocess.run(cmd, check=True, cwd=Path.cwd())
        print(f"✅ {description} completed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}\n")
        return False


def main():
    """Update all traceability artifacts."""
    config = get_config()

    if not config.requirements_file.exists():
        print(f"ERROR: Requirements file not found: {config.requirements_file}")
        print("Please check your pytreqt configuration.")
        sys.exit(1)

    print("🏃 Updating requirements traceability...\n")

    # Check for requirement changes
    print("1️⃣  Checking for requirement changes...")
    try:
        from .changes import RequirementChangeDetector

        detector = RequirementChangeDetector()
        changes = detector.detect_changes()
        if changes["file_changed"]:
            print("   ⚠️  Changes detected - continuing with updates...\n")
        else:
            print("   ✅ No changes detected\n")
    except Exception:
        print("   ⚠️  Warning: Could not check for changes\n")

    # Regenerate coverage report
    print("🔄 2️⃣  Regenerating coverage report...")
    try:
        from .coverage import main as generate_main

        generate_main()
        print("✅ 2️⃣  Regenerating coverage report completed\n")
        success = True
    except Exception as e:
        print(f"❌ 2️⃣  Regenerating coverage report failed: {e}\n")
        success = False

    if not success:
        sys.exit(1)

    # Run tests with requirements coverage
    # Determine appropriate database environment
    database_type = config.get_database_type()
    env_vars = {}
    if database_type.lower() == "sqlite":
        env_vars["DATABASE_URL"] = "sqlite://"

    # Construct test command
    test_cmd = ["pytest", "-q"]
    if env_vars:
        # Add environment variables to the command
        import os

        test_env = {**os.environ, **env_vars}
        success = _run_command_with_env(
            test_cmd, "3️⃣  Running tests with requirements coverage", test_env
        )
    else:
        success = _run_command(test_cmd, "3️⃣  Running tests with requirements coverage")

    if success:
        print("🎉 Traceability update completed successfully!")
        coverage_file = config.reports_output_dir / config.coverage_filename
        print(f"📋 Check {coverage_file} for updated coverage matrix")
    else:
        print("⚠️  Traceability update completed with test failures")
        print("🔍 Review test results and fix any issues")
        sys.exit(1)


def _run_command_with_env(cmd, description, env=None):
    """Run a command with specific environment variables."""
    print(f"🔄 {description}...")
    try:
        subprocess.run(cmd, check=True, cwd=Path.cwd(), env=env)
        print(f"✅ {description} completed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}\n")
        return False


if __name__ == "__main__":
    main()

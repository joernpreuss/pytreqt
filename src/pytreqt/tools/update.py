#!/usr/bin/env python3
"""
Update requirements traceability - regenerate coverage and check for changes.
"""

import sys

from ..config import get_config
from .common import run_command, run_command_with_env, validate_requirements_file_exists


def main() -> None:
    """Update all traceability artifacts."""
    config = get_config()
    validate_requirements_file_exists()

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
        success = run_command_with_env(
            test_cmd, "3️⃣  Running tests with requirements coverage", test_env
        )
    else:
        success = run_command(test_cmd, "3️⃣  Running tests with requirements coverage")

    if success:
        print("🎉 Traceability update completed successfully!")
        coverage_file = config.reports_output_dir / config.coverage_filename
        print(f"📋 Check {coverage_file} for updated coverage matrix")
    else:
        print("⚠️  Traceability update completed with test failures")
        print("🔍 Review test results and fix any issues")
        sys.exit(1)


if __name__ == "__main__":
    main()

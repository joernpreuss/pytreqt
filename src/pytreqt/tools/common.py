#!/usr/bin/env python3
"""
Common utilities shared across pytreqt tools.
"""

import os
import subprocess
import sys
from pathlib import Path

from ..config import get_config


def run_command(
    cmd: list[str], description: str, suppress_output: bool = False
) -> bool:
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


def run_command_with_env(
    cmd: list[str], description: str, env: dict[str, str] | None = None
) -> bool:
    """Run a command with specific environment variables."""
    print(f"🔄 {description}...")
    try:
        run_env = dict(os.environ)
        if env:
            run_env.update(env)
        subprocess.run(cmd, check=True, cwd=Path.cwd(), env=run_env)
        print(f"✅ {description} completed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}\n")
        return False


def validate_requirements_file_exists() -> bool:
    """Validate that the requirements file exists."""
    config = get_config()
    if not config.requirements_file.exists():
        print(f"ERROR: Requirements file not found: {config.requirements_file}")
        print("Please check your pytreqt configuration.")
        sys.exit(1)
    return True

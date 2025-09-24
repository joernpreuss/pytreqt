#!/usr/bin/env uv run python
"""Check for trailing newlines in text files."""

import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
@click.option("--fix", is_flag=True, help="Fix missing newlines")
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
def main(fix: bool, files: tuple[Path, ...]) -> None:
    """Check that all relevant files end with a newline."""
    missing: list[Path] = []

    if files:
        # Check specific files
        for f in files:
            if not f.is_file() or f.stat().st_size == 0:
                continue
            # Check if file ends with newline
            if f.read_bytes()[-1:] != b"\n":
                missing.append(f)
    else:
        # Check all files matching patterns
        patterns = [
            "*.py",
            "*.md",
            "*.toml",
            "*.yml",
            "*.yaml",
            "*.sh",
            ".gitignore",
            "*.txt",
            "*.json",
            "*.html",
            "*.css",
        ]
        exclude = {
            ".venv",
            ".git",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            ".nox",
            "__pycache__",
            ".claude",
            "htmlcov",
        }

        # Check files with extensions
        for pattern in patterns:
            for f in Path(".").rglob(pattern):
                # Skip excluded directories
                if any(p in f.parts for p in exclude):
                    continue

                # Skip specific files that are auto-generated
                if f.name == "SOURCES.txt" and any(
                    "egg-info" in str(part) for part in f.parts
                ):
                    continue

                # Skip non-files or empty files
                if not f.is_file() or f.stat().st_size == 0:
                    continue

                # Check if file ends with newline
                if f.read_bytes()[-1:] != b"\n":
                    missing.append(f)

        # Check specific root-level executable scripts
        root_executables = ["noxfile.py"]
        for name in root_executables:
            f = Path(".") / name
            if f.is_file() and f.stat().st_size > 0:
                # Check if file ends with newline
                if f.read_bytes()[-1:] != b"\n":
                    missing.append(f)

    if missing:
        if fix:
            console.print("🔧 Fixing missing trailing newlines:", style="bold yellow")
            for f in missing:
                console.print(f"  [cyan]{f}[/cyan]")
                # Add newline to file
                with f.open("ab") as file:
                    file.write(b"\n")
            console.print("✅ Fixed all missing newlines", style="bold green")
        else:
            console.print("❌ Files missing trailing newlines:", style="bold red")
            for f in missing:
                console.print(f"  [red]{f}[/red]")
            sys.exit(1)
    else:
        console.print("✅ All files have trailing newlines", style="bold green")


if __name__ == "__main__":
    main()

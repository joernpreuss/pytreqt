"""Command-line interface for pytreqt."""

import sys
from typing import Optional

import click


def main(args: Optional[list[str]] = None) -> int:
    """Main CLI entry point for pytreqt."""
    if args is None:
        args = sys.argv[1:]

    # For now, just provide a placeholder CLI
    # This will be implemented in Phase 1 when we extract the actual code
    click.echo("pytreqt CLI - Coming soon in Phase 1!")
    click.echo("This is a placeholder implementation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
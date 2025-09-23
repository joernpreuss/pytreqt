"""CLI entry point for pytreqt."""

import click

from .plugin import show_requirements_coverage_rich


class OrderedGroup(click.Group):
    """Click group that preserves command order."""

    def list_commands(self, ctx):
        return list(self.commands.keys())


@click.group(cls=OrderedGroup)
@click.help_option("-h", "--help")
def cli():
    """pytreqt - pytest requirements tracking"""
    pass


@cli.command()
@click.help_option("-h", "--help")
def validate():
    """Validate requirements file format"""
    from .requirements import RequirementsParser

    parser = RequirementsParser()
    valid_requirements = parser.load_valid_requirements()

    if not valid_requirements:
        click.echo("❌ No requirements found or requirements file not accessible")
        return

    click.echo(f"✅ Found {len(valid_requirements)} valid requirements:")
    for req in sorted(valid_requirements):
        click.echo(f"  {req}")


@cli.command()
@click.help_option("-h", "--help")
def config():
    """Show current configuration"""
    from .config import get_config

    config_obj = get_config()
    click.echo("Current pytreqt configuration:")
    click.echo(f"  Requirements file: {config_obj.requirements_file}")
    click.echo(f"  Requirement patterns: {config_obj.requirement_patterns}")
    click.echo(f"  Cache directory: {config_obj.cache_dir}")
    click.echo(f"  Database type: {config_obj.get_database_type()}")
    click.echo(f"  Reports output dir: {config_obj.reports_output_dir}")
    click.echo(f"  Coverage filename: {config_obj.coverage_filename}")


@cli.command()
@click.help_option("-h", "--help")
def coverage():
    """Generate TEST_COVERAGE.md report"""
    from .tools.coverage import main as coverage_main

    coverage_main()


@cli.command("show")
@click.help_option("-h", "--help")
def show():
    """Show requirements coverage from last test run"""
    show_requirements_coverage_rich()


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    help="Output format",
)
@click.help_option("-h", "--help")
def stats(format):
    """Show detailed requirements statistics"""
    from .tools.stats import show_stats

    show_stats(format=format)


@cli.command()
@click.help_option("-h", "--help")
def changes():
    """Check for requirement changes"""
    from .tools.changes import main as changes_main

    changes_main()


@cli.command()
@click.help_option("-h", "--help")
def update():
    """Update all traceability artifacts"""
    from .tools.update import main as update_main

    update_main()


def main():
    """Main CLI entry point for pytreqt."""
    cli()


if __name__ == "__main__":
    main()

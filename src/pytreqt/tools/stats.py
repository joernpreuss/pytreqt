"""Requirements statistics and detailed reporting."""

import csv
import json
import sys

from rich.console import Console
from rich.table import Table

from ..config import get_config


def show_stats(format: str = "text") -> None:
    """Show detailed requirements statistics."""
    config = get_config()

    # Load valid requirements using same method as coverage report
    from .coverage import extract_requirements_from_specs

    valid_requirements_dict = extract_requirements_from_specs()
    valid_requirements = set(valid_requirements_dict.keys())

    # Load test coverage data
    coverage_file = config.reports_output_dir / config.coverage_filename
    if not coverage_file.exists():
        print("❌ Coverage report not found. " + "Run: pytreqt coverage")
        return

    # Parse coverage data
    content = coverage_file.read_text()
    tested_requirements = set()
    untested_requirements = set()

    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "**Status**: ✅ **Tested**" in line:
            # Find requirement ID in the line immediately before
            if i > 0:
                prev_line = lines[i - 1]
                if "###" in prev_line:
                    # Extract requirement ID from lines like "### FR-1.1: Description"
                    req = prev_line.split(":")[0].replace("### ", "").strip()
                    tested_requirements.add(req)
        elif "**Status**: ❌ **Not Tested**" in line:
            if i > 0:
                prev_line = lines[i - 1]
                if "###" in prev_line:
                    req = prev_line.split(":")[0].replace("### ", "").strip()
                    untested_requirements.add(req)

    # Calculate statistics
    total_requirements = len(valid_requirements)
    tested_count = len(tested_requirements)
    # Calculate actual untested requirements
    untested_requirements = valid_requirements - tested_requirements
    untested_count = len(untested_requirements)
    coverage_percentage = (
        (tested_count / total_requirements * 100) if total_requirements > 0 else 0
    )

    # Show all requirements
    requirements_to_show = valid_requirements

    # Output in requested format
    if format == "json":
        data = {
            "total_requirements": total_requirements,
            "tested_requirements": tested_count,
            "untested_requirements": untested_count,
            "coverage_percentage": round(coverage_percentage, 1),
            "tested": list(tested_requirements),
            "untested": list(untested_requirements),
        }
        print(json.dumps(data, indent=2))

    elif format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["Requirement", "Status", "Category"])
        for req in requirements_to_show:
            status = "Tested" if req in tested_requirements else "Not Tested"
            # Determine category from configured patterns
            category = "Unknown"
            for pattern in config.requirement_patterns:
                if req.upper().startswith(pattern.split("-")[0] + "-"):
                    category = pattern.split("-")[0]
                    break
            writer.writerow([req, status, category])

    else:  # text format
        console = Console()

        # Overall statistics
        console.print("\n📊 Requirements Coverage Statistics", style="bold blue")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Requirements", str(total_requirements))
        table.add_row("Tested Requirements", str(tested_count))
        table.add_row("Untested Requirements", str(untested_count))
        table.add_row("Coverage Percentage", f"{coverage_percentage:.1f}%")

        console.print(table)

        # Show breakdown by category
        console.print("\n📋 Breakdown by Category", style="bold blue")

        breakdown_table = Table(show_header=True, header_style="bold magenta")
        breakdown_table.add_column("Category", style="cyan")
        breakdown_table.add_column("Tested", style="green")
        breakdown_table.add_column("Total", style="yellow")
        breakdown_table.add_column("Coverage", style="blue")

        # Group by configured patterns
        for pattern in config.requirement_patterns:
            prefix = pattern.split("-")[0] + "-"
            category_reqs = [r for r in valid_requirements if r.startswith(prefix)]
            category_tested = [r for r in tested_requirements if r.startswith(prefix)]

            if category_reqs:  # Only show categories that have requirements
                category_total = len(category_reqs)
                category_tested_count = len(category_tested)
                category_coverage = (
                    (category_tested_count / category_total * 100)
                    if category_total > 0
                    else 0
                )

                # Create readable category name
                category_name = f"{prefix[:-1]} Requirements"
                if prefix == "FR-":
                    category_name = "Functional Requirements (FR)"
                elif prefix == "BR-":
                    category_name = "Business Rules (BR)"

                breakdown_table.add_row(
                    category_name,
                    str(category_tested_count),
                    str(category_total),
                    f"{category_coverage:.1f}%",
                )

        console.print(breakdown_table)

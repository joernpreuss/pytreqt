#!/usr/bin/env python3
"""
Generate TEST_COVERAGE.md from requirements and test coverage data.
"""

import re
import sys

from ..config import get_config
from .common import validate_requirements_file_exists


def extract_requirements_from_specs() -> dict[str, str]:
    """Extract all defined requirements from requirements file."""
    config = get_config()
    requirements_file = config.requirements_file

    if not requirements_file.exists():
        print(f"ERROR: {requirements_file} not found")
        return {}

    content = requirements_file.read_text(encoding="utf-8")
    requirements = {}

    # Extract requirements with descriptions using configured patterns
    for pattern in config.requirement_patterns:
        # Pattern matches lines like "**FR-1.1**: Users can create objects"
        markdown_pattern = rf"\*\*({pattern})\*\*:\s+(.+)"
        matches = re.findall(markdown_pattern, content, re.MULTILINE | re.IGNORECASE)

        for req_id, description in matches:
            requirements[req_id.upper()] = description.strip()

    return requirements


def _get_test_coverage() -> dict[str, list[str]]:
    """Get requirements coverage data from change detector."""
    try:
        from .changes import RequirementChangeDetector

        detector = RequirementChangeDetector()
        return detector.get_test_coverage_mapping()
    except Exception as e:
        print(f"ERROR getting test coverage: {e}")
        return {}


def _get_previous_coverage() -> dict[str, str | int | float] | None:
    """Get previous coverage data from existing report."""
    config = get_config()
    coverage_file = config.reports_output_dir / config.coverage_filename

    if not coverage_file.exists():
        return None

    try:
        content = coverage_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Extract previous stats
        previous_data = {}
        for line in lines:
            if "Last updated" in line:
                # Extract date from **Last updated**: 2025-09-13**
                match = re.search(r"Last updated\*\*:\s*([^\*]+)", line)
                if match:
                    previous_data["timestamp"] = match.group(1).strip()
            elif "Total Requirements" in line:
                match = re.search(r"(\d+)", line)
                if match:
                    previous_data["total_requirements"] = int(match.group(1))
            elif "Requirements with Tests" in line:
                match = re.search(r"(\d+)", line)
                if match:
                    previous_data["tested_requirements"] = int(match.group(1))
            elif "Coverage Percentage" in line:
                match = re.search(r"([\d.]+)%", line)
                if match:
                    previous_data["coverage_percentage"] = float(match.group(1))

        return previous_data if previous_data else None
    except Exception:
        return None


def _coverage_changed(
    previous: dict[str, str | int | float] | None, current: dict[str, str | int | float]
) -> bool:
    """Check if coverage data has meaningfully changed."""
    if not previous:
        return True

    # Check if key metrics changed
    prev_total = previous.get("total_requirements", 0)
    prev_tested = previous.get("tested_requirements", 0)
    prev_pct = previous.get("coverage_percentage", 0)

    return (
        prev_total != current["total_requirements"]
        or prev_tested != current["tested_requirements"]
        or abs(float(prev_pct) - float(current["coverage_percentage"])) > 0.1
    )


def _generate_coverage_matrix() -> str | None:
    """Generate the complete coverage matrix."""
    get_config()

    print("Extracting requirements from specifications...")
    all_requirements = extract_requirements_from_specs()

    print("Analyzing test coverage...")
    test_coverage = _get_test_coverage()

    # Get previous coverage to check if it changed
    previous_coverage = _get_previous_coverage()
    current_coverage_data: dict[str, str | int | float] = {
        "total_requirements": len(all_requirements),
        "tested_requirements": len(test_coverage),
        "coverage_percentage": (
            len(test_coverage) / len(all_requirements) * 100 if all_requirements else 0
        ),
    }

    # Only update timestamp if coverage actually changed
    if _coverage_changed(previous_coverage, current_coverage_data):
        timestamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    else:
        timestamp = (
            previous_coverage.get("timestamp", "unchanged")
            if previous_coverage
            else __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        )

    if not all_requirements:
        print("No requirements found!")
        return None

    # Generate the coverage report
    report_lines = [
        "# Test Coverage Matrix",
        "",
        "This document shows the traceability between requirements and test cases.",
        "",
        f"**Last updated**: {timestamp}",
        "",
        "## Coverage Summary",
        "",
        f"- **Total Requirements**: {len(all_requirements)}",
        f"- **Requirements with Tests**: {len(test_coverage)}",
        "- **Requirements without Tests**: "
        + f"{len(all_requirements) - len(test_coverage)}",
        "",
        "**Coverage Percentage**: "
        + f"{len(test_coverage) / len(all_requirements) * 100:.1f}%",
        "",
        "## Requirements Coverage",
        "",
    ]

    # Sort requirements by ID
    sorted_requirements = sorted(all_requirements.items())

    for req_id, description in sorted_requirements:
        tests = test_coverage.get(req_id, [])
        # Remove duplicates while preserving order
        unique_tests = list(dict.fromkeys(tests))
        status = "✅ **Tested**" if unique_tests else "❌ **Not Tested**"

        report_lines.extend(
            [f"### {req_id}: {description}", f"**Status**: {status}", ""]
        )

        if unique_tests:
            report_lines.append("**Test Cases**:")
            for test in sorted(unique_tests):  # Also sort for consistency
                report_lines.append(f"- `{test}`")
            report_lines.append("")
        else:
            report_lines.extend(
                ["**Test Cases**: None", "⚠️ *This requirement needs test coverage*", ""]
            )

    # Add untested requirements section
    untested = [req for req in all_requirements if req not in test_coverage]
    if untested:
        report_lines.extend(
            [
                "## Requirements Needing Tests",
                "",
                "The following requirements have no test coverage:",
                "",
            ]
        )

        for req_id in sorted(untested):
            description = all_requirements[req_id]
            report_lines.append(f"- **{req_id}**: {description}")

        report_lines.append("")

    # Add test statistics (deduplicated)
    total_tests = sum(
        len(list(dict.fromkeys(tests))) for tests in test_coverage.values()
    )
    report_lines.extend(
        [
            "## Test Statistics",
            "",
            f"- **Total Test Cases with Requirements**: {total_tests}",
            f"- **Unique Requirements Tested**: {len(test_coverage)}",
            (
                "- **Average Tests per Requirement**: "
                + f"{total_tests / len(test_coverage):.1f}"
                if test_coverage
                else "- **Average Tests per Requirement**: 0"
            ),
            "",
            "---",
            "",
            "*This file is auto-generated by pytreqt*",
            "*To update, run: `pytreqt coverage`*",
        ]
    )

    return "\n".join(report_lines) + "\n"


def main() -> None:
    """Main function to generate and write the coverage report."""
    config = get_config()
    validate_requirements_file_exists()

    # Generate the report
    report_content = _generate_coverage_matrix()
    if not report_content:
        print("Failed to generate coverage report")
        sys.exit(1)

    # Write to the reports directory
    reports_dir = config.reports_output_dir
    reports_dir.mkdir(exist_ok=True)

    coverage_file = reports_dir / config.coverage_filename
    coverage_file.write_text(report_content, encoding="utf-8")

    print(f"✅ Coverage report generated: {coverage_file}")
    print(
        "📊 Coverage summary: "
        + f"{len(extract_requirements_from_specs())} total requirements"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Detect changes in requirements and identify affected tests.
"""

import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..config import get_config
from .common import validate_requirements_file_exists


class RequirementChangeDetector:
    """Detects changes in requirements and identifies affected tests."""

    def __init__(self, cache_file: Path | str | None = None) -> None:
        self.config = get_config()
        if cache_file is None:
            cache_file = self.config.cache_dir / "req_cache.json"
        self.cache_file = Path(cache_file)
        self.requirements_file = self.config.requirements_file

    def get_requirements_hash(self) -> str | None:
        """Calculate hash of requirements file content."""
        if not self.requirements_file.exists():
            return None

        content = self.requirements_file.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode()).hexdigest()

    def extract_requirements(self) -> dict[str, str]:
        """Extract requirements with their full text from requirements file."""
        if not self.requirements_file.exists():
            return {}

        content = self.requirements_file.read_text(encoding="utf-8")
        requirements = {}

        # Extract requirements with their descriptions using configured patterns
        for pattern in self.config.requirement_patterns:
            markdown_pattern = rf"-\s+\*\*({pattern})\*\*:\s+(.+)"
            matches = re.findall(
                markdown_pattern, content, re.MULTILINE | re.IGNORECASE
            )

            for req_id, description in matches:
                requirements[req_id.upper()] = description.strip()

        return requirements

    def get_requirement_hashes(self, requirements: dict[str, str]) -> dict[str, str]:
        """Calculate individual hashes for each requirement."""
        req_hashes = {}
        for req_id, description in requirements.items():
            combined = f"{req_id}:{description}"
            req_hashes[req_id] = hashlib.sha256(combined.encode()).hexdigest()
        return req_hashes

    def load_cache(self) -> dict[str, Any]:
        """Load the previous requirements cache."""
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def save_cache(self, data: dict[str, Any]) -> None:
        """Save the current requirements cache."""
        try:
            # Ensure cache directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"Warning: Could not save cache: {e}")

    def get_test_coverage_mapping(self) -> dict[str, list[str]]:
        """Get mapping of requirements to tests, only including passing tests."""
        try:
            # Determine database type for test run
            database_type = self.config.get_database_type()
            env_vars = dict(__import__("os").environ)

            # Set appropriate database URL for tests
            if database_type.lower() == "sqlite":
                env_vars["DATABASE_URL"] = "sqlite://"

            # Run full test suite to get actual results
            result = subprocess.run(
                ["pytest", "--requirements-report", "-v"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                env=env_vars,
            )

            # Parse both the requirements mapping and test results
            req_to_tests = defaultdict(list)
            test_results = {}  # test_name -> passed/failed
            lines = result.stdout.split("\n")

            # First pass: collect test results
            for line in lines:
                line = line.strip()
                if " PASSED " in line or " FAILED " in line:
                    # Extract test name from pytest output lines
                    parts = line.split("::")
                    if len(parts) >= 2:
                        test_name = parts[-1].split()[
                            0
                        ]  # Get test name before PASSED/FAILED
                        test_results[test_name] = "PASSED" in line

            # Second pass: collect requirements mapping (only from passing tests)
            in_requirements_section = False
            current_req = None

            for line in lines:
                line = line.strip()

                if "Requirements Coverage" in line:
                    in_requirements_section = True
                    continue
                elif "Requirements Coverage Summary" in line:
                    break

                if not in_requirements_section:
                    continue

                # Look for requirement headers using configured patterns
                for pattern in self.config.requirement_patterns:
                    if re.match(rf"^{pattern}:$", line, re.IGNORECASE):
                        current_req = line.rstrip(":").upper()
                        break

                # Look for test entries like "    ✓ test_veto_idempotency"
                if current_req and line.startswith("✓"):
                    test_name = line[2:].strip()  # Remove "✓ " prefix
                    # Only include if test actually passed
                    if test_results.get(test_name, False):
                        req_to_tests[current_req].append(test_name)

            return dict(req_to_tests)

        except Exception as e:
            print(f"Warning: Could not get test coverage: {e}")
            return {}

    def detect_changes(self) -> dict[str, Any]:
        """Detect changes in requirements and identify affected tests."""
        # Get current requirements
        current_requirements = self.extract_requirements()
        current_req_hashes = self.get_requirement_hashes(current_requirements)
        current_file_hash = self.get_requirements_hash()

        # Load previous state
        cache = self.load_cache()
        previous_req_hashes = cache.get("requirement_hashes", {})
        previous_file_hash = cache.get("file_hash")

        # Determine what changed
        changes: dict[str, Any] = {
            "file_changed": current_file_hash != previous_file_hash,
            "added_requirements": [],
            "modified_requirements": [],
            "removed_requirements": [],
            "affected_tests": set(),
        }

        if not changes["file_changed"]:
            return changes  # No changes detected

        # Find specific requirement changes
        current_req_ids = set(current_req_hashes.keys())
        previous_req_ids = set(previous_req_hashes.keys())

        changes["added_requirements"] = list(current_req_ids - previous_req_ids)
        changes["removed_requirements"] = list(previous_req_ids - current_req_ids)

        # Find modified requirements
        for req_id in current_req_ids & previous_req_ids:
            if current_req_hashes[req_id] != previous_req_hashes.get(req_id):
                changes["modified_requirements"].append(req_id)

        # Get test coverage to identify affected tests
        req_to_tests = self.get_test_coverage_mapping()

        # Collect affected tests
        affected_reqs = (
            changes["added_requirements"]
            + changes["modified_requirements"]
            + changes["removed_requirements"]
        )

        for req_id in affected_reqs:
            tests = req_to_tests.get(req_id, [])
            changes["affected_tests"].update(tests)

        changes["affected_tests"] = list(changes["affected_tests"])

        # Update cache
        new_cache = {
            "file_hash": current_file_hash,
            "requirement_hashes": current_req_hashes,
            "last_check": __import__("datetime").datetime.now().isoformat(),
        }
        self.save_cache(new_cache)

        return changes

    def print_change_report(self, changes: dict[str, Any]) -> None:
        """Print a human-readable change report."""
        if not changes["file_changed"]:
            print("✅ No changes detected in requirements")
            return

        print("🔍 Requirements changes detected!\n")

        if changes["added_requirements"]:
            print("➕ **Added Requirements:**")
            for req_id in sorted(changes["added_requirements"]):
                print(f"   - {req_id}")
            print()

        if changes["modified_requirements"]:
            print("✏️  **Modified Requirements:**")
            for req_id in sorted(changes["modified_requirements"]):
                print(f"   - {req_id}")
            print()

        if changes["removed_requirements"]:
            print("❌ **Removed Requirements:**")
            for req_id in sorted(changes["removed_requirements"]):
                print(f"   - {req_id}")
            print()

        if changes["affected_tests"]:
            print("🧪 **Tests that may need review:**")
            for test in sorted(changes["affected_tests"]):
                print(f"   - {test}")
            print()
            print(
                '💡 Consider running: `pytest -k "'
                + f'{"|".join(changes["affected_tests"][:5])}" -v`'
            )
        else:
            print("ℹ️  No tests directly affected by requirement changes")

        print(
            f"\n📊 Total impact: {len(changes['affected_tests'])} tests may need review"
        )


def main() -> None:
    """Main function to detect and report requirement changes."""
    validate_requirements_file_exists()

    detector = RequirementChangeDetector()
    changes = detector.detect_changes()
    detector.print_change_report(changes)

    # Exit with non-zero if there are changes (useful for CI/CD)
    if changes["file_changed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

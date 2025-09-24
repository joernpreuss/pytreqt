"""Requirements parsing and validation logic for pytreqt."""

import re

from .config import get_config


class RequirementsParser:
    """Handles parsing and validation of requirements from files and docstrings."""

    def __init__(self) -> None:
        """Initialize the requirements parser."""
        self._valid_requirements: set[str] | None = None
        self.config = get_config()

    def extract_requirements(self, docstring: str) -> set[str]:
        """Extract requirements from docstring using configured patterns.

        Args:
            docstring: The docstring to parse

        Returns:
            Set of requirement IDs found in the docstring
        """
        if not docstring:
            return set()

        requirements: set[str] = set()
        for pattern in self.config.requirement_patterns:
            matches = re.findall(pattern, docstring, re.IGNORECASE)
            requirements.update(req.upper() for req in matches)

        return requirements

    def load_valid_requirements(self) -> set[str]:
        """Load valid requirement IDs from the requirements file.

        Returns:
            Set of valid requirement IDs
        """
        if self._valid_requirements is not None:
            return self._valid_requirements

        requirements_file = self.config.requirements_file
        if not requirements_file.exists():
            self._valid_requirements = set()
            return self._valid_requirements

        try:
            content = requirements_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            self._valid_requirements = set()
            return self._valid_requirements

        # Extract requirement IDs from markdown headers and bullet points
        # This pattern looks for requirement IDs in common markdown formats
        found_requirements: set[str] = set()
        for pattern in self.config.requirement_patterns:
            # Look for requirements in headers (## FR-1.1), bullet points
            # (- **FR-1.1**), and bold format (**FR-1.1**)
            combined_pattern = rf"(?:^|\s|-\s\*\*|\*\*)({pattern})"
            matches = re.findall(
                combined_pattern, content, re.MULTILINE | re.IGNORECASE
            )
            found_requirements.update(req.upper() for req in matches)

        self._valid_requirements = found_requirements
        return self._valid_requirements

    def validate_requirements(self, requirements: set[str], test_name: str) -> None:
        """Validate that all requirements exist in the requirements file.

        Args:
            requirements: Set of requirement IDs to validate
            test_name: Name of the test (for error reporting)

        Raises:
            ValueError: If any requirements are not found in the requirements file
        """
        valid_requirements = self.load_valid_requirements()

        if not valid_requirements:
            # If no requirements file found, don't validate
            return

        invalid_requirements = requirements - valid_requirements
        if invalid_requirements:
            invalid_list = ", ".join(sorted(invalid_requirements))
            raise ValueError(
                f"Test '{test_name}' references invalid requirements: {invalid_list}. "
                + f"Valid requirements are defined in {self.config.requirements_file}"
            )

    def clear_cache(self) -> None:
        """Clear the cached valid requirements."""
        self._valid_requirements = None

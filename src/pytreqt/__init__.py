"""pytreqt - Requirements traceability for Python tests.

A pytest plugin and CLI tool for tracking requirements coverage in test suites.
"""

__version__ = "0.1.0"
__author__ = "Jörn Preuß"
__email__ = "joern.preuss@gmail.com"

from .config import get_config, reload_config
from .plugin import requirements, show_requirements_coverage_rich
from .requirements import RequirementsParser

__all__ = [
    "get_config",
    "reload_config",
    "requirements",
    "show_requirements_coverage_rich",
    "RequirementsParser",
]

# -*- coding: utf-8 -*-
"""pytreqt - Requirements traceability for Python tests.

A pytest plugin and CLI tool for tracking requirements coverage in test suites.
"""

__version__ = "0.1.0"
__author__ = "Jörn Preuß"
__email__ = "joern.preuss@gmail.com"

from .plugin import RequirementsPlugin

__all__ = ["RequirementsPlugin"]
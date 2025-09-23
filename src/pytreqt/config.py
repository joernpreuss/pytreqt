"""Configuration management for pytreqt."""

import os
from pathlib import Path
from typing import Any

import tomllib


class PytreqtConfig:
    """Configuration manager for pytreqt."""

    def __init__(self, config_path: str | Path | None = None):
        """Initialize configuration.

        Args:
            config_path: Optional path to config file. If not provided, will search
                for config files.
        """
        self._config: dict[str, Any] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: str | Path | None = None) -> None:
        """Load configuration from file(s)."""
        # Set defaults first
        self._config = {
            "requirements_file": "requirements.md",
            "requirement_patterns": [
                r"FR-\d+\.?\d*",  # Functional Requirements
                r"BR-\d+\.?\d*",  # Business Rules
            ],
            "cache_dir": ".pytest_cache",
            "output_formats": ["markdown", "json", "csv"],
            "database": {
                "detect_from_env": ["TEST_DATABASE", "DATABASE_URL", "DB_TYPE"],
                "default_type": "SQLite",
            },
            "reports": {
                "output_dir": ".",
                "template_dir": "templates",
                "coverage_filename": "TEST_COVERAGE.md",
            },
        }

        # Try to load from specified config file or search for config files
        config_file = None
        if config_path:
            config_file = Path(config_path)
        else:
            # Search for config files in order of preference
            search_paths = [
                Path("pytreqt.toml"),
                Path("pyproject.toml"),
            ]
            for path in search_paths:
                if path.exists():
                    config_file = path
                    break

        if config_file and config_file.exists():
            try:
                with open(config_file, "rb") as f:
                    file_config = tomllib.load(f)

                # Extract pytreqt config from pyproject.toml or use entire file
                # for pytreqt.toml
                if config_file.name == "pyproject.toml":
                    pytreqt_config = file_config.get("tool", {}).get("pytreqt", {})
                else:
                    pytreqt_config = file_config

                # Merge with defaults
                self._merge_config(pytreqt_config)

            except (OSError, tomllib.TOMLDecodeError) as e:
                # Fall back to defaults if config file is unreadable
                print(f"Warning: Could not read config file {config_file}: {e}")

    def _merge_config(self, new_config: dict[str, Any]) -> None:
        """Merge new configuration with existing configuration."""
        for key, value in new_config.items():
            if (
                key in self._config
                and isinstance(self._config[key], dict)
                and isinstance(value, dict)
            ):
                # Deep merge for nested dictionaries
                self._config[key].update(value)
            else:
                self._config[key] = value

    @property
    def requirements_file(self) -> Path:
        """Get the requirements file path."""
        return Path(self._config["requirements_file"])

    @property
    def requirement_patterns(self) -> list[str]:
        """Get the requirement ID patterns."""
        return self._config["requirement_patterns"]

    @property
    def cache_dir(self) -> Path:
        """Get the cache directory path."""
        return Path(self._config["cache_dir"])

    @property
    def output_formats(self) -> list[str]:
        """Get supported output formats."""
        return self._config["output_formats"]

    @property
    def database_detect_env_vars(self) -> list[str]:
        """Get environment variables to check for database type detection."""
        return self._config["database"]["detect_from_env"]

    @property
    def database_default_type(self) -> str:
        """Get the default database type."""
        return self._config["database"]["default_type"]

    @property
    def reports_output_dir(self) -> Path:
        """Get the reports output directory."""
        return Path(self._config["reports"]["output_dir"])

    @property
    def reports_template_dir(self) -> Path:
        """Get the reports template directory."""
        return Path(self._config["reports"]["template_dir"])

    @property
    def coverage_filename(self) -> str:
        """Get the coverage report filename."""
        return self._config["reports"]["coverage_filename"]

    def get_database_type(self) -> str:
        """Determine database type from environment variables."""
        for env_var in self.database_detect_env_vars:
            value = os.getenv(env_var)
            if value:
                # Common detection patterns
                if "postgresql" in value.lower() or "postgres" in value.lower():
                    return "PostgreSQL"
                elif "mysql" in value.lower():
                    return "MySQL"
                elif "sqlite" in value.lower():
                    return "SQLite"
                elif env_var == "TEST_DATABASE" and value.lower() == "postgresql":
                    return "PostgreSQL"

        return self.database_default_type

    def to_dict(self) -> dict[str, Any]:
        """Get the full configuration as a dictionary."""
        return self._config.copy()


# Global config instance
_config: PytreqtConfig | None = None


def get_config(config_path: str | Path | None = None) -> PytreqtConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None or config_path is not None:
        _config = PytreqtConfig(config_path)
    return _config


def reload_config(config_path: str | Path | None = None) -> PytreqtConfig:
    """Reload the configuration."""
    global _config
    _config = PytreqtConfig(config_path)
    return _config

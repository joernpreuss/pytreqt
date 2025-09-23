# Contributing to pytreqt

Thank you for your interest in contributing to pytreqt!

## Development Setup

### Option 1: Using pip (Standard)

```bash
# Clone the repository
git clone https://github.com/pytreqt/pytreqt.git
cd pytreqt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
ruff check src/
mypy src/
```

### Option 2: Using uv (Faster)

If you have [uv](https://github.com/astral-sh/uv) installed:

```bash
# Clone the repository
git clone https://github.com/pytreqt/pytreqt.git
cd pytreqt

# Install in development mode (uv handles venv automatically)
uv pip install -e .[dev]

# Run tests
uv run pytest tests/

# Run linting
uv run ruff check src/
uv run mypy src/
```

### Option 3: Using conda

```bash
# Clone the repository
git clone https://github.com/pytreqt/pytreqt.git
cd pytreqt

# Create conda environment
conda create -n pytreqt python=3.11
conda activate pytreqt

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/
```

## Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Code Style

- Use `ruff format` for code formatting
- Follow type hints (checked with mypy)
- Write tests for new functionality
- Update documentation as needed

## Testing

Run the full test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```
# Project Structure

## Overview

- **Package**: `iwmaeda`
- **Version**: 0.1.0
- **Python**: >= 3.14
- **Purpose**: AI Engineer portfolio and Python project template

## Directory Structure

```text
iwmaeda/
├── src/iwmaeda/         # Main package
│   ├── functions.py     # Core functions
│   └── types.py         # Type definitions
├── tests/               # Test suite (pytest)
├── scripts/             # Utility scripts and examples
├── .claude/             # Claude AI configuration
│   ├── memory/
│   │   ├── guidelines/  # Coding guidelines (Python, Markdown, Prompting)
│   │   └── project/     # Project documentation
│   └── settings.json    # Claude settings
├── .github/workflows/   # CI/CD pipelines
├── .vscode/             # VS Code configuration
├── pyproject.toml       # Project configuration
└── README.md            # Portfolio information
```

## Development Tools

| Tool    | Purpose                      | Configuration       |
|---------|------------------------------|---------------------|
| uv      | Package management           | pyproject.toml      |
| Pyright | Type checking (strict mode)  | pyproject.toml      |
| Ruff    | Linting and formatting       | pyproject.toml      |
| pytest  | Testing framework            | pyproject.toml      |

## Command Reference

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint code (with auto-fix)
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type check
uv run pyright
```

## Configuration Highlights

### Pyright (Strict Mode)

- All type errors reported
- Unused imports/variables flagged
- Import cycles detected

### Ruff

- Line length: 120 characters
- McCabe complexity: max 15
- Comprehensive rule set: security, performance, best practices

# Project Structure

## Overview

- **Package**: `iwmaeda`
- **Version**: 0.1.0
- **Python**: >= 3.14
- **Purpose**: AI Engineer portfolio and Python project template

## Directory Structure

```text
iwmaeda/
├── src/iwmaeda/              # Main package
│   ├── functions.py         # Core functions
│   └── types.py             # Type definitions
├── tests/                   # Test suite (pytest)
├── scripts/                 # Utility scripts and examples
├── .claude/                 # Claude AI configuration
│   ├── memory/
│   │   ├── guidelines/      # Coding guidelines (Python, Markdown, Prompting)
│   │   └── project/         # Project documentation
│   └── settings.json        # Claude settings
├── .github/workflows/       # CI pipeline
│   └── ci.yaml              # check (format/lint/type) + test jobs
├── .vscode/                 # VS Code configuration
├── mise.toml                # Toolchain versions (Node.js, Python, uv)
├── package.json             # npm scripts + Prettier config
├── .prettierignore          # Prettier ignore patterns
├── .gitattributes           # Line-ending normalization (LF)
├── .markdownlint.json       # markdownlint rules
├── .markdownlint-cli2.jsonc # markdownlint-cli2 config (ignores)
├── pyproject.toml           # Project + tool configuration
└── README.md                # Portfolio information
```

## Development Tools

| Tool              | Purpose                        | Configuration        |
| ----------------- | ------------------------------ | -------------------- |
| uv                | Package management             | pyproject.toml       |
| mise              | Toolchain version management   | mise.toml            |
| Pyright           | Type checking (strict mode)    | pyproject.toml       |
| Pyrefly           | Type checking                  | pyproject.toml       |
| ty                | Type checking (Astral)         | pyproject.toml       |
| Ruff              | Python linting and formatting  | pyproject.toml       |
| Prettier          | JSON/YAML/Markdown formatting  | package.json         |
| markdownlint-cli2 | Markdown linting               | markdownlint configs |
| pytest            | Testing framework              | pyproject.toml       |
| npm scripts       | Unified check/fix entry points | package.json         |

## Command Reference

```bash
# Install toolchain and dependencies
mise install
uv sync
npm install

# Run all static checks (Prettier / markdownlint / Ruff / Pyright / Pyrefly / ty)
npm run check:all

# Auto-fix formatting and lint issues (Prettier / markdownlint / Ruff)
npm run fix:all

# Run tests
npm test                  # = uv run pytest

# Individual tools
uv run ruff check --fix .
uv run ruff format .
uv run pyright
uv run pyrefly check .
uv run ty check .
npm run format
npm run lint:md
```

## Configuration Highlights

### Pyright (Strict Mode)

- All type errors reported
- Unused imports/variables flagged
- Import cycles detected

### ty

- Astral's fast type checker
- `deprecated` bumped to error to match Pyright strict mode

### Ruff

- Line length: 120 characters
- McCabe complexity: max 15
- Comprehensive rule set: security, performance, best practices

### Prettier

- Targets: JSON, JSONC, YAML, Markdown
- Print width: 100, prose wrap: preserve
- JSONC override: no trailing commas

### CI (GitHub Actions)

- Triggers: push to `main` and pull requests
- `check` job: format, lint, and type checks (`npm run check:all`)
- `test` job: pytest (`npm test`)
- Toolchain provisioned via mise (jdx/mise-action)

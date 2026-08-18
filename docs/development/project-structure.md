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
├── docs/                    # Shared documentation (source of truth)
│   ├── README.md            # Documentation index
│   ├── development/         # Guidelines shared by Claude Code and Codex
│   └── recommended/         # Optional recommended configs (not enforced)
├── .claude/                 # Claude Code configuration
│   ├── settings.json        # Repository-wide settings (status line)
│   └── commands/pr/         # Slash commands (review-loop.md is the canonical workflow)
├── .agents/                 # Codex skills
│   └── skills/review-loop/  # Thin router; reads .claude/commands/pr/review-loop.md
├── .codex/                  # Codex configuration
│   └── config.toml          # Repository-wide policy (approval, sandbox, TUI)
├── .github/
│   ├── workflows/ci.yaml    # CI pipeline (check + test jobs)
│   └── dependabot.yml       # Grouped monthly dependency updates
├── .vscode/                 # VS Code settings, launch config, extension hints
├── CLAUDE.md                # Claude Code entry point (@ imports)
├── AGENTS.md                # Codex entry point (read-in-full instructions)
├── mise.toml                # Toolchain versions (Node.js, Python, uv, bun)
├── package.json             # npm scripts + Prettier config
├── .prettierignore          # Prettier ignore patterns
├── .gitattributes           # Line-ending normalization (LF)
├── .markdownlint.json       # markdownlint rules
├── .markdownlint-cli2.jsonc # markdownlint-cli2 config (ignores)
├── pyproject.toml           # Project + tool configuration
└── README.md                # Portfolio information
```

Guidelines live in `docs/development/` rather than under `.claude/` so that every agent
reads the same files. `CLAUDE.md` pulls them in with `@` imports; `AGENTS.md` lists the same
paths and tells Codex to read them in full. Neither entry file duplicates their content.

## Development Tools

| Tool              | Purpose                               | Configuration          |
| ----------------- | ------------------------------------- | ---------------------- |
| uv                | Package management                    | pyproject.toml         |
| mise              | Toolchain version management          | mise.toml              |
| Pyright           | Type checking (strict mode)           | pyproject.toml         |
| Pyrefly           | Type checking                         | pyproject.toml         |
| ty                | Type checking (Astral)                | pyproject.toml         |
| Ruff              | Python linting and formatting         | pyproject.toml         |
| Prettier          | JSON/YAML/Markdown formatting         | package.json           |
| markdownlint-cli2 | Markdown linting                      | markdownlint configs   |
| pytest            | Testing framework                     | pyproject.toml         |
| npm audit         | Dependency vulnerability scanning     | package.json           |
| Dependabot        | Grouped monthly dependency updates    | .github/dependabot.yml |
| npm scripts       | Unified check/fix entry points        | package.json           |
| Claude Code       | Agent entry point + status line       | CLAUDE.md, .claude/    |
| Codex             | Agent entry point + repository policy | AGENTS.md, .codex/     |

## Command Reference

コマンド一覧の正本は [`../../README.md`](../../README.md)。どの検証をいつ実行するかの判断基準は
[working-agreements.md](./working-agreements.md) を参照。

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
- `embeddedLanguageFormatting: "off"` — keeps Prettier out of fenced code blocks so the
  deliberately malformed "Bad" examples in `markdown.md` survive a format pass (commit `c744e48`)
- Configured inline in `package.json`; there is no separate `.prettierrc`

### CI (GitHub Actions)

- Triggers: push to `main` and pull requests, with a `concurrency` group that cancels superseded runs
- `permissions: contents: read` — no job writes to the repository
- `check` job: format, lint, and type checks (`npm run check:all`)
- `test` job: pytest (`npm test`); it skips `npm ci` because `npm test` only shells out to `uv run pytest`
- Toolchain provisioned via mise (jdx/mise-action); uv and npm downloads are cached across runs

### Agent configuration

- `docs/development/` is the single source of truth for guidelines; `CLAUDE.md` and `AGENTS.md`
  only point at it
- `.codex/config.toml` holds repository-wide Codex policy and is read only for trusted projects
- Per-developer state stays out of git: `.claude/settings.local.json` and personal
  `~/.codex/config.toml` preferences
- `.claude/commands/**/*.md` are the canonical workflow procedures. `.agents/skills/<name>/SKILL.md`
  are thin Codex routers that read the corresponding command file rather than restating it, so both
  agents follow one procedure — the same no-duplication rule that governs `CLAUDE.md` / `AGENTS.md`
- `.claude/**` and `.agents/**` are linted by Prettier and markdownlint (markdownlint-cli2 descends
  into dot-directories); run `npm run check:docs` after editing them

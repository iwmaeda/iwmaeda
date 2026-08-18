# CLAUDE.md

## Shared Project Guidance

作業を始める前に、次の共有ドキュメントを参照してください。

@docs/development/project-structure.md
@docs/development/working-agreements.md

## Coding Guidelines

変更対象に応じて、該当する共有ガイドを参照してください。

**Python:**
@docs/development/python.md

**Markdown:**
@docs/development/markdown.md

**LLM プロンプト:**
@docs/development/prompting.md

## Project Workflows

変更を PR に載せてレビューを回す作業には `/pr:review-loop` を使用してください
（`.claude/commands/pr/review-loop.md` が正本）。ブランチ作成・検証・分割コミット・push・PR 作成・
`@codex review` の起動・レビュー待ち・指摘の判定と修正・（任意で）マージ までを 1 つの手順として持ちます。
Codex は `$review-loop` を使います。

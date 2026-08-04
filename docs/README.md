# iwmaeda ドキュメント

`iwmaeda` は Python パッケージのポートフォリオ兼テンプレートリポジトリ。本ディレクトリは
AI エージェント（Claude Code / Codex）と人間が共有する開発ドキュメントの正本を置く。
セットアップ手順とコマンド一覧はリポジトリ直下の [`../README.md`](../README.md) を参照。

## ドキュメント地図

| ドキュメント                                                             | 内容                                                 |
| ------------------------------------------------------------------------ | ---------------------------------------------------- |
| [development/project-structure.md](./development/project-structure.md)   | ディレクトリ構成、ツールと設定ファイルの対応         |
| [development/working-agreements.md](./development/working-agreements.md) | 作業方針・検証・レビュー観点、エージェントの初期設定 |
| [development/python.md](./development/python.md)                         | Python コーディング規約                              |
| [development/markdown.md](./development/markdown.md)                     | Markdown コーディング規約                            |
| [development/prompting.md](./development/prompting.md)                   | LLM プロンプト設計ガイド                             |

## 関連ドキュメント

| 場所                           | 役割                                             |
| ------------------------------ | ------------------------------------------------ |
| [`../README.md`](../README.md) | セットアップ手順とコマンド一覧（入口・正本）     |
| [`../CLAUDE.md`](../CLAUDE.md) | Claude Code 用の入口（`@` インポートで自動展開） |
| [`../AGENTS.md`](../AGENTS.md) | Codex 用の入口（全文読み込みの指示）             |

`CLAUDE.md` と `AGENTS.md` は同じ節構成で同じドキュメント群を指す。差分は参照の機構だけで、
内容は複製しない。ルールを変えるときは `development/` 配下の該当ファイルだけを編集する。

## 表記規約

- 入口・索引・作業ルールは日本語で書く。`development/` のコーディングガイドは、既存の LLM 向け資産を
  そのまま移設したため英語のままとする。言語の統一より内容の安定を優先した意図的な例外。
- 見出しは ATX。Markdown は markdownlint（`MD013` 行長 120、コード・表・見出しは除外）と
  Prettier（`printWidth: 100`、`proseWrap: preserve`）に従う。
- `proseWrap` が `preserve` のため Prettier は本文を折り返さない。行長は手で 120 以内に保つ。
- Prettier の `embeddedLanguageFormatting` は `off`。`development/markdown.md` の意図的な「悪い例」
  コードフェンスが書き換えられるのを防ぐため（commit `c744e48`）。
- 表は Prettier が整列するため、列幅を手で揃える必要はない。
- 編集後は `npm run check:docs` で確認する。

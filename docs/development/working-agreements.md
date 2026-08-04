# 開発時の共通ルール

Claude Code と Codex を含む、プロジェクトで作業する AI エージェント向けの共通ルール。
各エージェント固有の入口ファイル（`CLAUDE.md` / `AGENTS.md`）には内容を複製せず、このファイルを正本とする。

## 作業方針

- 変更範囲を依頼に必要な最小限に保ち、既存のユーザー変更を維持する。
- 実装前に近接コードとテストを読み、既存の構造・命名・公開 API に合わせる。
- `src/iwmaeda/` をライブラリの正本とし、`main.py` と `scripts/` は薄い実行入口に保つ。
- 型注釈は全ての引数と戻り値に付ける（[python.md](./python.md)）。Ruff の `ANN` ルールがこれを機械的に検査する。
- 設定は既存ファイルに集約し、新しい設定ファイルを増やさない。ツール設定は `pyproject.toml`、
  npm スクリプトと Prettier 設定は `package.json`、markdownlint のルールは `.markdownlint.json`、
  無視パターンは `.markdownlint-cli2.jsonc` に置く。
- lint やフォーマッタが失敗したときは、まずコード側を直す。ルールを無効化して通すのは、
  抑止する理由を明記できる場合に限る。
- 生成物（`package-lock.json` / `uv.lock`）は手で編集せず、`npm install` / `uv lock` で再生成する。
- API キー、トークン、個人情報をコミットしない。
- リリース、タグ付け、外部公開は、ユーザーの明示依頼なしに行わない。

## 検証

変更した領域に最も近い検証を先に実行し、必要に応じて広げる。

| コマンド                                | 対象                                                      |
| --------------------------------------- | --------------------------------------------------------- |
| `npm run check:docs`                    | Prettier（JSON / JSONC / YAML / Markdown）と markdownlint |
| `npm run check:py`                      | Ruff format / Ruff lint / Pyright / Pyrefly / ty          |
| `npm run check:all`                     | 上記すべて                                                |
| `uv run pytest tests/test_functions.py` | 対象テストのみ                                            |
| `npm test`                              | 全テスト                                                  |
| `npm run fix:all`                       | 自動修正の一括適用                                        |
| `npm run audit`                         | 依存関係の脆弱性                                          |

npm が唯一の入口であり、Python 側のコマンドも npm スクリプトから `uv run` に委譲する。
CI（`.github/workflows/ci.yaml`）の各ジョブは同じ npm スクリプトを呼ぶため、ローカルと CI の検証内容は
構造的に一致する。

`.venv` が mise の提供する Python と食い違うと、ローカルと CI の結果がずれる。疑わしいときは
`.venv/bin/python --version` と `mise current` を比較し、必要なら `rm -rf .venv && uv sync --locked` で作り直す。

実行できなかった検証がある場合は、最終報告に明記する。

## レビュー観点

- 正しさ、型注釈の網羅性、公開 API の後方互換性を優先して確認する。
- 依存やツールを増やす変更では、既存ツールで代替できないかを先に検討する。
- 設定変更では、ローカル（`npm run check:all`）と CI で同じ結果になるかを確認する。
- バグ修正には、可能なら失敗を再現する回帰テストを `tests/` に追加する。

## エージェントの初期設定

### Codex

`.codex/config.toml` はリポジトリ共通のポリシー（承認方針・サンドボックス・status line）を保持する。
このレイヤは **trusted なプロジェクトでのみ** 読み込まれ、untrusted の場合はエラーも出さずスキップされる。
初回のみ、リポジトリ直下で `codex` を起動して信頼を承認するか、`~/.codex/config.toml` に次を追記する。

```toml
[projects."/path/to/iwmaeda"]
trust_level = "trusted"
```

読み込まれたかどうかは `codex doctor --json` で確認できる。`approvals_reviewer` や `[tui]` は
個人プロファイル側に存在しないため、これらが出力に現れればリポジトリレイヤが適用されている。

モデル・provider・reasoning effort などの個人設定は `~/.codex/config.toml` 側に置き、リポジトリにはコミットしない。

### Claude Code

`.claude/settings.json` はリポジトリ共通設定のみを保持する。個人設定は `.claude/settings.local.json`
（`.gitignore` 済み）に置く。

status line は `bun x` 経由で `ccstatusline` を起動する。bun は `mise.toml` で固定しているため
`mise install` で導入されるが、未導入の環境でも status line が表示されないだけで他の動作には影響しない。
ウィジェットの構成は各開発者の `~/.config/ccstatusline/settings.json` に委ねており、リポジトリでは指定しない。
強制はしないが、出発点として使える設定例を
[recommended/ccstatusline.md](../recommended/ccstatusline.md) に置いている。

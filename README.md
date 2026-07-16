# 前田 巌 (MAEDA, Iwao)

AIエンジニア。Pythonを中心に、LLM統合・機械学習・
コンピュータビジョンを活用したシステム開発に従事。

## 技術スタック

### 言語・フレームワーク

- Python 3.14+ (メイン)
- TypeScript (インフラ・フロントエンド)

### AI/ML

- LLM: LangChain/LangGraph, Google Gemini, Azure OpenAI
- DL: PyTorch
- ML: LightGBM, scikit-learn, Optuna
- CV: YOLO, MMDetection

### データ処理

- Polars, Pydantic 2.x

### インフラ

- AWS (Lambda, CDK, S3)
- Azure Cognitive Services

### 開発環境

- ツールチェーン管理: mise (Node.js / Python / uv を固定)
- パッケージ管理: uv, Poetry
- 型チェック: Pyright (strict mode), Pyrefly, ty
- リント: Ruff (Python), markdownlint-cli2 (Markdown)
- フォーマット: Ruff (Python), Prettier (JSON / YAML / Markdown)
- テスト: pytest

## プロジェクト経験

### 金融データ分析・予測システム

LLMとMLを組み合わせた市場分析。特徴量エンジニアリング、
時系列予測、非同期処理による高速化を実装。

### 医療AI・診断支援システム

物体検出モデルを活用した画像診断支援。
学習パイプラインの構築と推論システムの実装。

### 業務自動化・対話型AIシステム

DDDに基づく設計でAWS Lambda上に構築。
ストリーミング処理による大規模データ対応。

### マルチモーダルAI

音声・動画・テキストを統合処理するシステム。
リアルタイム処理とバッチ処理の両対応。

## 実装方針

- **型安全性**: Pyright strict mode による厳格な型チェック
- **パフォーマンス**: asyncio.TaskGroup、キャッシング、ストリーミング
- **セキュリティ**: 静的解析による脆弱性検出
- **保守性**: モジュール化とドメイン駆動設計

詳細な実装方針は、 [python.md](.claude/memory/guidelines/python.md) を参照してください。

## 開発手順

### セットアップ

```bash
# ツールチェーン (Node.js / Python / uv) を用意
mise install

# 依存パッケージのインストール (Python)
uv sync

# 依存パッケージのインストール (Node.js / Prettier・markdownlint)
npm install
```

### テスト

```bash
uv run pytest   # npm test でも可
```

### リント・型チェック・フォーマット

日常的には統合スクリプトを使う。個別コマンドは必要に応じて。

```bash
# すべてのチェックを実行 (Prettier / markdownlint / Ruff / Pyright / Pyrefly / ty)
npm run check:all

# 自動修正を一括適用 (Prettier / markdownlint / Ruff)
npm run fix:all
```

個別コマンド:

```bash
# Python リント (自動修正あり) / フォーマット
uv run ruff check --fix .
uv run ruff format .

# 型チェック (Pyright + Pyrefly + ty)
uv run pyright
uv run pyrefly check .
uv run ty check .

# Markdown リント / JSON・YAML・Markdown フォーマット
npm run lint:md
npm run format
```

## GitHub

[github.com/iwmaeda](https://github.com/iwmaeda)

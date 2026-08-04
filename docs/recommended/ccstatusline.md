# ccstatusline のおすすめ設定

Claude Code の status line を描画する [ccstatusline](https://github.com/sirmalloc/ccstatusline) の設定例。
リポジトリが強制するルールではなく、そのままコピーして使える出発点として置いている。
実際に使っている `~/.config/ccstatusline/settings.json` の内容をそのまま記録した。

## 前提

`.claude/settings.json` はリポジトリ共通設定として `bun x ccstatusline@latest` を status line に指定している。
bun は `mise.toml` で固定されているため `mise install` で入る。未導入の環境では status line が表示されないだけで、
他の動作には影響しない。

ウィジェットの構成は各開発者の `~/.config/ccstatusline/settings.json` に委ねる方針で、リポジトリでは指定しない
（[working-agreements.md](../development/working-agreements.md) の「エージェントの初期設定」を参照）。
本ファイルはその方針を変えるものではなく、ゼロから組むより速い出発点を示すだけ。

## 導入

```bash
# 設定ディレクトリを作る
mkdir -p ~/.config/ccstatusline

# 下記「設定全文」の JSON を保存する
${EDITOR:-vi} ~/.config/ccstatusline/settings.json
```

保存後、Claude Code の status line に反映される。

## 設定全文

```json
{
  "version": 3,
  "lines": [
    [
      {
        "id": "model",
        "type": "model",
        "color": "brightCyan",
        "bold": true
      },
      {
        "id": "thinking-effort",
        "type": "thinking-effort",
        "color": "brightMagenta"
      },
      {
        "id": "sandbox-status",
        "type": "sandbox-status",
        "color": "brightGreen",
        "metadata": {
          "format": "word"
        }
      },
      {
        "id": "git-branch",
        "type": "git-branch",
        "color": "brightMagenta",
        "bold": true,
        "maxWidth": 24
      },
      {
        "id": "git-clean-status",
        "type": "git-clean-status",
        "color": "brightGreen"
      },
      {
        "id": "git-status",
        "type": "git-status",
        "color": "brightYellow"
      },
      {
        "id": "git-ahead-behind",
        "type": "git-ahead-behind",
        "color": "brightCyan"
      }
    ],
    [
      {
        "id": "context-bar",
        "type": "context-percentage",
        "color": "brightGreen"
      },
      {
        "id": "tokens-input",
        "type": "tokens-input",
        "color": "brightCyan"
      },
      {
        "id": "tokens-output",
        "type": "tokens-output",
        "color": "brightMagenta"
      },
      {
        "id": "cache-hit-rate",
        "type": "cache-hit-rate",
        "color": "brightYellow"
      },
      {
        "id": "compaction-counter",
        "type": "compaction-counter",
        "color": "brightYellow",
        "metadata": {
          "hideZero": "true",
          "showReclaimed": "true"
        }
      },
      {
        "id": "session-clock",
        "type": "session-clock",
        "color": "brightBlue"
      },
      {
        "id": "session-cost",
        "type": "session-cost",
        "color": "brightYellow",
        "bold": true
      }
    ],
    [
      {
        "id": "session-usage",
        "type": "session-usage",
        "color": "brightCyan",
        "bold": true
      },
      {
        "id": "reset-timer",
        "type": "reset-timer",
        "color": "brightBlue",
        "metadata": {
          "compact": "true"
        }
      },
      {
        "id": "weekly-usage",
        "type": "weekly-usage",
        "color": "brightMagenta",
        "bold": true
      },
      {
        "id": "weekly-reset-timer",
        "type": "weekly-reset-timer",
        "color": "brightYellow",
        "metadata": {
          "compact": "true"
        }
      }
    ]
  ],
  "flexMode": "full-until-compact",
  "compactThreshold": 70,
  "colorLevel": 3,
  "defaultSeparator": "│",
  "defaultPadding": " ",
  "defaultPaddingSide": "both",
  "inheritSeparatorColors": false,
  "globalBold": false,
  "gitCacheTtlSeconds": 5,
  "minimalistMode": false,
  "powerline": {
    "enabled": false,
    "separators": [
      ""
    ],
    "separatorInvertBackground": [
      false
    ],
    "startCaps": [],
    "endCaps": [],
    "autoAlign": false,
    "continueThemeAcrossLines": false
  }
}
```

## 行構成

`lines` は 3 行構成。1 行目は「今どこで作業しているか」、2 行目は「このセッションで何を消費したか」、
3 行目は「使用量の残りとリセット時刻」という役割で分けている。

### 1 行目: モデルとリポジトリの状態

| type               | 色            | 表示内容                                                    |
| ------------------ | ------------- | ----------------------------------------------------------- |
| `model`            | brightCyan    | 使用中のモデル名（太字）                                    |
| `thinking-effort`  | brightMagenta | thinking（reasoning effort）の設定値                        |
| `sandbox-status`   | brightGreen   | サンドボックスの状態。`format: "word"` で記号でなく語で表示 |
| `git-branch`       | brightMagenta | 現在のブランチ名（太字）。`maxWidth: 24` で 24 文字に制限   |
| `git-clean-status` | brightGreen   | 作業ツリーがクリーンかどうか                                |
| `git-status`       | brightYellow  | 変更・追加・削除されたファイルの数                          |
| `git-ahead-behind` | brightCyan    | upstream に対する ahead / behind のコミット数               |

### 2 行目: コンテキストとコスト

| type                 | 色            | 表示内容                                                                               |
| -------------------- | ------------- | -------------------------------------------------------------------------------------- |
| `context-percentage` | brightGreen   | コンテキストウィンドウの使用率（`id` は `context-bar` だが type はパーセンテージ表示） |
| `tokens-input`       | brightCyan    | 入力トークン数                                                                         |
| `tokens-output`      | brightMagenta | 出力トークン数                                                                         |
| `cache-hit-rate`     | brightYellow  | プロンプトキャッシュのヒット率                                                         |
| `compaction-counter` | brightYellow  | コンパクション回数。`hideZero` で 0 のときは非表示、`showReclaimed` で回収量も表示     |
| `session-clock`      | brightBlue    | セッションの経過時間                                                                   |
| `session-cost`       | brightYellow  | セッションのコスト（太字）                                                             |

### 3 行目: 使用量とリセットまでの時間

| type                 | 色            | 表示内容                                       |
| -------------------- | ------------- | ---------------------------------------------- |
| `session-usage`      | brightCyan    | セッション単位の使用量（太字）                 |
| `reset-timer`        | brightBlue    | セッション使用量のリセットまで。`compact` 表記 |
| `weekly-usage`       | brightMagenta | 週次の使用量（太字）                           |
| `weekly-reset-timer` | brightYellow  | 週次リセットまで。`compact` 表記               |

## 全体設定

| キー                     | 値                     | 意味                                                        |
| ------------------------ | ---------------------- | ----------------------------------------------------------- |
| `version`                | `3`                    | 設定スキーマのバージョン                                    |
| `flexMode`               | `"full-until-compact"` | 幅に余裕があるうちは全項目を出し、狭くなったら詰めて表示    |
| `compactThreshold`       | `70`                   | 詰めた表示に切り替える閾値                                  |
| `colorLevel`             | `3`                    | 色深度。3 は truecolor（24 bit）                            |
| `defaultSeparator`       | `"│"`                  | ウィジェット間の区切り文字                                  |
| `defaultPadding`         | `" "`                  | 区切りの周りに入れる文字                                    |
| `defaultPaddingSide`     | `"both"`               | 余白を区切りの両側に入れる                                  |
| `inheritSeparatorColors` | `false`                | 区切りに隣接ウィジェットの色を継承しない                    |
| `globalBold`             | `false`                | 全体の太字化はせず、`bold` を指定したウィジェットだけ太字   |
| `gitCacheTtlSeconds`     | `5`                    | git 情報のキャッシュ有効期間（秒）。頻繁な git 実行を抑える |
| `minimalistMode`         | `false`                | ミニマリスト表示を使わない                                  |
| `powerline.enabled`      | `false`                | Powerline 記号を使わない。Nerd Font がなくても崩れない      |

`powerline` を無効にしているため、`separators` などの下位キーは使われないが、既定値のまま残している。

## カスタマイズ

ウィジェットの追加・削除・色の変更は、`bun x ccstatusline@latest` を引数なしで実行すると開く対話 UI から行える。
UI での変更はそのまま `~/.config/ccstatusline/settings.json` に書き戻る。

3 行は情報量が多い分だけ画面を使う。1 行に減らしたい場合は、1 行目（モデルと git の状態）を残して
2・3 行目を削るのが扱いやすい。

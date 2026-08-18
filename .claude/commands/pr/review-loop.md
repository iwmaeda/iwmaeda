---
description: ブランチ → 分割コミット → push → PR → レビュー起動 → 指摘の修正 を、収束するまで回す
argument-hint: （引数なし＝対話・codex・マージなし）／`--reviewer codex|gemini` `--merge` `--auto` `--max-rounds 10` `--timeout 30m`
allowed-tools: Bash(gh api *), Bash(gh pr *), Bash(gh repo *), Bash(git *), Bash(npm run *), Bash(npm test), Read, Edit, Write, Grep, Glob
---

# レビューと修正のループ

作業ツリーの変更を ブランチ作成 → 検証 → 分割コミット → push → PR 作成 → レビュー起動 → 指摘の判定と修正 の
順に回し、レビュアーが指摘を返さなくなるまで反復する。`$ARGUMENTS` でレビュアー・マージの有無・ユーザー確認で
止まるかどうかを決める。既定のレビュアーは Codex（本文が `@codex review` だけの issue コメントで起動する）。

**このコマンドは変更の中身を作らない** — 実装やドキュメントの編集は通常の作業で行い、ここはその結果を PR に
載せてレビューを回す層だけを持つ。**各段は「もう済んでいるか」を先に見る**ので、中断しても同じコマンドで
再開できる（巡目は `git log --grep` から導き直すので、セッションをまたいでも失われない）。

| フラグ              | 既定     | 効果                                                           |
| ------------------- | -------- | -------------------------------------------------------------- |
| `--reviewer <name>` | `codex`  | `codex` / `gemini`。トリガー文と期待する bot login を変える    |
| `--merge`           | 付けない | 収束後に **CI green を待ってから** マージコミットする          |
| `--auto`            | 付けない | 確認で止まらず最後まで進む。**このフラグ自体を承認として扱う** |
| `--max-rounds <n>`  | `10`     | この巡数で収束しなければ中断する                               |
| `--timeout <dur>`   | `30m`    | 1 巡あたりのレビュー待ちの**累計**上限。超えたら中断する       |

止まるのは **コミット分割案の提示** と **マージ直前** の 2 か所だけで、`--auto` は両方を抑止する。
**中断は停止であって確認ではない** — どちらのモードでも報告を出して終わる。

## いつ実行するか

- 作業がひと区切りついて、PR に載せてレビューを受けたいとき
- レビュー指摘を直したあと、同じ PR で次の巡を回したいとき
- 中断したループを再開したいとき（どの段から再開するかはコマンドが判定する）
- **使わないとき**: 変更の中身そのものを作る作業と、レビューを起動せずコミットだけしたいとき

## 手順

1. 引数を解釈し、解決した設定を表で出してから現在地を確かめる。**`--state open` を落とすと過去の
   マージ済み PR を掴む**（この repo は `delete_branch_on_merge: false` なので古い枝が生き残る）。
   **upstream も必ず見る** —— トピックブランチの upstream が `origin/main` だと、この先の push が
   PR を経ずに `main` を直接撃つ（下の注意）:

   ```bash
   git branch --show-current
   git status --porcelain
   git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo '(upstream なし = 正常)'
   gh pr list --head "$(git branch --show-current)" --state open --json number,url
   ```

   **判定**: 3 行目が `origin/main` を返し、かつ現在地が `main` でないなら、**push する前に**
   `git branch --unset-upstream` で外す。手順 5 の `git push -u origin HEAD` が正しい upstream を
   貼り直すので、外して困ることは無い。

2. `main` に居るならブランチを切る（**`main` の上では 1 つもコミットしない**）。既にトピックブランチなら
   何もしない。命名は履歴に合わせて `feat/*` `fix/*` `docs/*` `chore/*` `ci/*` `build/*`:

   ```bash
   git checkout -b feat/<slug>
   ```

   **`git switch -c <slug> origin/main` は使わない。** 始点にリモート追跡ブランチを書くと git が
   upstream を**自動で `origin/main` に貼る**。そのブランチからの push は宛先が `main` になるので、
   **PR も レビューも CI も通らずに `main` が進む**。この repo の `main` に branch protection は
   無いので（`branches/main/protection` は 404）、事故は黙って通る。ローカル `main` が古くて
   `origin/main` から切りたいときは `--no-track` を付けるか、`main` を先に更新してから上の形で切る:

   ```bash
   git checkout -b fix/<slug> --no-track origin/main   # 始点にリモートを書くなら --no-track
   git switch main && git pull && git checkout -b fix/<slug>   # あるいは main を進めてから切る
   ```

3. 変更領域に最も近い検証を先に通す（`docs/development/working-agreements.md` の 検証 節）。
   **`npm run check:all` にテストは含まれない** —— `check:all` は `check:docs` と `check:py` だけで、
   CI は `check` と `test` の 2 ジョブに分かれている。**赤い CI はレビュー 1 巡ぶんの枠を無駄にする**
   ので、push の前に両方通す:

   ```bash
   npm run check:all
   npm test
   git diff --check
   ```

4. 変更を概念単位に分けてコミットする。分割案を提示して確認を取る（`--auto` なら提示だけして止まらない）。
   **`git add -A` を使わない** — `git status --porcelain` を読んで明示的に stage し、依頼の外にある
   ユーザーの変更はそのまま残す。subject は履歴の形（英語の Conventional Commits）に合わせる:

   ```text
   fix: address review round <N> on PR #<n>

   <何が誤っていたか / 根はどこか / 何を測ったか / 何を敢えて変えなかったか>

   Verified: <実際に走らせたコマンドと結果。走らせられなかったものはそう書く>

   Co-Authored-By: <実行中のモデル名> <noreply@anthropic.com>
   ```

   trailer は**実際に作業したモデル**を書く（この repo の履歴には `Claude Opus 5 (1M context)` と
   `Claude Sonnet 5` の両方が在る）。Codex で回すときは Codex 側の慣習に従う。

   `<N>` は `git log --oneline --grep="on PR #<n>$" | wc -l` ＋ 1。**1 巡 1 コミットを基本にする**
   — 返信が sha を名乗るので、1 巡に 2 つ sha があるとどの返信も曖昧になる。スコープが本当に割れる
   ときだけ分け、その 2 つには**同じ巡目番号**を書く。

5. push する。**`--force` は使わない**（下の注意）:

   ```bash
   git push -u origin HEAD
   ```

6. PR が無ければ作る。タイトルは英語の型 prefix ＋ 日本語の説明（履歴の最新の形）。本文の更新は
   `--body-file` でそのまま渡す（JSON へエスケープし直さない）:

   ```bash
   gh pr create --base main --title '<type>: <日本語の説明>' --body-file <scratch>/body.md
   gh pr edit <n> --body-file <scratch>/body.md                                    # 更新はこちら
   ```

7. レビューを起動する。**直前のトリガー時の HEAD と今の HEAD が同じなら起動してはいけない**（下の注意の
   暴走不変条件）。**HEAD と `created_at` の両方を控える** —— `created_at` は 8 の検算に、HEAD は
   次の巡の不変条件の判定に要る（**HEAD を控えないと不変条件は次の巡で検証できない**）:

   ```bash
   git rev-parse --short=8 HEAD
   gh api "repos/iwmaeda/iwmaeda/issues/<n>/comments" -f body='@codex review' \
     --jq '"TRIGGER=\(.id) SINCE=\(.created_at)"'
   ```

   | reviewer | トリガー本文     | bot login                      | この repo での状態                              |
   | -------- | ---------------- | ------------------------------ | ----------------------------------------------- |
   | `codex`  | `@codex review`  | `chatgpt-codex-connector[bot]` | **既定・実測済み**（PR #8 / #11、約 3〜4 分）   |
   | `gemini` | `/gemini review` | `gemini-code-assist[bot]`      | 実測あり（PR #4 / #5）。PR #7 は 2 回ともエラー |
   | `claude` | `@claude review` | `claude[bot]`                  | **無反応**（PR #7 で実測）。使わない            |

   **2 巡目以降は焦点を付けてよい** —— codex は `@codex review <焦点>` を one-off focus として
   サポートしている。前の巡で直したクラスの残りを名指しすると、限られた指摘枠がそこへ向く:

   ```bash
   gh api "repos/iwmaeda/iwmaeda/issues/<n>/comments" \
     -f body='@codex review 前の巡で直した <クラス名> と同じ型が他に残っていないかを見てください' \
     --jq '"TRIGGER=\(.id) SINCE=\(.created_at)"'
   ```

8. 待つ。**このスクリプトは `run_in_background` で 1 回だけ投げ、下のフェンスを 1 バイトも変えずに貼る**
   （理由は下の注意）。stdout は **通常 1 行**（review と bot コメントが同巡に来たときだけ `EXTRA=` の
   2 行目が付く）なので、待機のトークン費用はほぼ 1 行で済む。**「最終行だけ読む」実装にしない** ——
   `EXTRA=` を落とすとレート制限の signal が消える。

   **このフェンスの予算 480 秒は 1 チャンクであって `--timeout` ではない。** `--timeout`（既定 `30m`）は
   チャンクの**累計**に当たるので、`pending` が返るたびに 8 だけを撃ち直し、**投げた回数 × 8 分**が
   `--timeout` を超えたら中断する（既定なら約 4 チャンク）。フェンスは引数を取らない設計なので、
   累計を数えるのは呼び出し側の仕事である:

   ```bash
   set -uo pipefail
   S=$(timeout 25 gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null) || { echo "VERDICT=error reason=api stage=setup"; exit 0; }
   PR=$(timeout 25 gh pr list --head "$(git branch --show-current)" --state open --json number -q '.[0].number' 2>/dev/null) || { echo "VERDICT=error reason=api stage=setup"; exit 0; }
   [ -n "${S:-}" ] || { echo "VERDICT=error reason=no-pr"; exit 0; }
   case "${PR:-}" in ''|*[!0-9]*) echo "VERDICT=error reason=no-pr"; exit 0;; esac
   Q='query($o:String!,$n:String!,$p:Int!){repository(owner:$o,name:$n){pullRequest(number:$p){
   comments(last:30){nodes{createdAt databaseId body author{login __typename} reactionGroups{content users{totalCount}}}}
   reviews(last:10){nodes{submittedAt databaseId state author{login __typename} commit{oid}}}}}}'
   J='.data.repository.pullRequest as $p|[($p.comments.nodes[]|select(.author.__typename!="Bot")|select(.body|test("^[@/](codex|gemini|claude) review([[:space:]]|$)"))|"TRIG \(.createdAt) \(.databaseId) \([.reactionGroups[]|select(.content=="THUMBS_UP")|.users.totalCount]|add // 0)"),($p.reviews.nodes[]|select(.author.__typename=="Bot")|select(.state!="DISMISSED")|"review \(.submittedAt) commit=\(.commit.oid[0:8]) \(.author.login) review_id=\(.databaseId)"),($p.comments.nodes[]|select(.author.__typename=="Bot")|select(.body|test("^## Summary of Changes")|not)|"comment \(.createdAt) \(.author.login) \(.body|split("\n")[0][0:110])")]|.[]'
   F=0; TS=""; END=$((SECONDS + 480))
   while [ "$SECONDS" -lt "$END" ]; do
     O=$(timeout 25 gh api graphql -F o="${S%%/*}" -F n="${S##*/}" -F p="$PR" -f query="$Q" --jq "$J" 2>/dev/null); r=$?
     if [ $r -ne 0 ]; then
       F=$((F + 1)); [ $F -ge 5 ] && { echo "VERDICT=error reason=api pr=$PR"; exit 0; }; sleep 30; continue
     fi
     F=0
     T=$(printf '%s\n' "$O" | grep '^TRIG ' | tail -1)
     if [ -z "$T" ]; then
       B=$(printf '%s\n' "$O" | grep -e '^review ' -e '^comment ' | tail -1)
       [ -n "$B" ] && echo "VERDICT=error reason=untriggered-verdict pr=$PR bot=$B" || echo "VERDICT=error reason=no-trigger pr=$PR"
       exit 0
     fi
     set -- $T; TS=$2; TID=$3; RX=$4
     R=$(printf '%s\n' "$O" | grep '^review ' | awk -v t="$TS" '$2>t' | tail -1)
     C=$(printf '%s\n' "$O" | grep '^comment ' | awk -v t="$TS" '$2>t' | tail -1)
     if [ -n "$R" ] || [ -n "$C" ]; then
       echo "VERDICT=${R:-$C} pr=$PR trigger=$TS"
       [ -n "$R" ] && [ -n "$C" ] && echo "EXTRA=$C"
       exit 0
     fi
     [ "${RX:-0}" != 0 ] && { echo "VERDICT=reaction pr=$PR trigger=$TS id=$TID"; exit 0; }
     sleep 30
   done
   echo "VERDICT=pending pr=$PR trigger=$TS waited=480"
   ```

   返ってきた `trigger=` を 7 で控えた `SINCE` と**必ず突き合わせる** — 食い違っていたら GitHub が新しい
   トリガーをまだ見せておらず、スクリプトは**前の巡のトリガー**を拾っている。その判定は捨てて撃ち直す。

9. 1 行で 継続 / 終了 / 中断 を決める。**表を引く前に 3 つ突き合わせる** ——
   (a) `pr=` が 6 で得た PR 番号と同じか（**違えば別の PR を見ている**）、
   (b) `trigger=` が 7 で控えた `SINCE` と同じか、(c) 判定を出した bot の login が
   7 の表のレビュアーのものか（`review` / `comment` の行は login を載せている。
   **`$J` は `__typename=="Bot"` しか見ていないので、別の bot の判定もここまで届く** ——
   この repo には `copilot-pull-request-reviewer` の review が PR #1 / #2 に実在する）。
   そのうえで `VERDICT=review` は `commit=` を `git rev-parse --short=8 HEAD` と突き合わせる。
   一致しないときは `git merge-base --is-ancestor <commit> HEAD` で祖先かどうかを見る —— 祖先でも
   ローカルにも無いのでもないなら、履歴が分岐しているので中断する。

   **`--is-ancestor` は真偽値ではなく 3 値を返す。`$?` を見る**（実測値）—— `0` = 祖先、
   `1` = 有効な commit だが祖先でない（履歴が分岐）、`128` = そもそもローカルに無い
   （`fatal: Not a valid commit name`）。`if git merge-base …; then … else … fi` と書くと
   **`128` が `1` に潰れ**、`git fetch` すべき場面を「分岐した」と誤診して中断する。
   下の表の 3 行目と 4 行目は、この 2 つの終了コードの区別そのものである:

   | シグナル                                          | 判定             | 次の行動                                                           |
   | ------------------------------------------------- | ---------------- | ------------------------------------------------------------------ |
   | `review` ＋ `commit` が HEAD と一致               | 継続             | 10 へ                                                              |
   | `review` ＋ `commit` が HEAD の祖先               | 継続（1 度だけ） | 指摘は**捨てて** 7 を撃ち直す。2 度目は中断                        |
   | `review` ＋ `commit` がローカルに無い（`128`）    | **中断**         | `git fetch` して無ければ他者の push。手を止める                    |
   | `review` ＋ `commit` が祖先でもない（`1`）        | **中断**         | 履歴が分岐している（reset / force push の跡）。手を止める          |
   | `review` だが inline comment が 0 件              | **終了（成功）** | **判定は 10 の取得後**（8 は件数を引いていない）                   |
   | `comment` ＋ `Didn't find any major issues`       | **終了（成功）** | 12 へ                                                              |
   | `comment` ＋ `You have reached your Codex usage…` | **中断**         | **再試行しない**。時間で回復する枠なので巡を消すだけ               |
   | `comment` ＋ 上記以外の bot 本文                  | **中断**         | 本文を全文出して人に渡す。推測しない                               |
   | `reaction`                                        | **終了（成功）** | 未観測の経路なので報告にその旨を書く                               |
   | `pending`（`--timeout` 内）                       | 継続             | **7 は撃ち直さず** 8 だけを撃ち直す                                |
   | `pending`（`--timeout` 超過）                     | **中断**         | codex は導入済みなので、無反応なら別の理由を探す                   |
   | 判定の bot login が 7 の表と違う                  | **中断**         | 別の bot の判定を今巡のものとして読まない。login を報告に出す      |
   | `EXTRA=` の 2 行目が付いている                    | 上の判定に従う   | 同じ巡に来た bot コメント。レート制限なら**中断が優先**            |
   | `error reason=untriggered-verdict`                | **中断**         | **判定は在るがトリガーが無い**。`bot=` の本文で理由を見る          |
   | `error reason=no-pr` / `no-trigger`               | **中断**         | 理由をそのまま報告する。PR の有無と手順 6 を疑う                   |
   | `error reason=api`（`stage=setup` 無し）          | **中断**         | ループ内で 5 周連続の取得失敗。`gh` の疎通を疑う                   |
   | `error reason=api stage=setup`                    | **中断**         | **PR を引く前に落ちた**。認証・ネットワークを疑う。PR 不在ではない |
   | `--max-rounds` 到達                               | **中断**         | 成功ではない。マージしない                                         |

10. 指摘を読む。**review の body は定型文で、指摘は inline review comment のほうに在る**。重大度は本文頭の
    `![P1 Badge]` / `P2` / `P3` から採る。**`<review_id>` は 8 が `VERDICT=review …` 行の
    `review_id=` フィールドとして出している**ので、引き直さない。**キーで取る。位置で取らない** ——
    8 は `review_id=` の後ろに `pr=…` と `trigger=…` を足すので、**行の末尾は `trigger=` である**。
    「最後のフィールド」を取る実装は `trigger=` を掴み、下の `pull_request_review_id==` が
    黙って空を返す（エラーにはならない）:

    ```bash
    gh api --paginate "repos/iwmaeda/iwmaeda/pulls/<n>/comments?per_page=100" \
      --jq '.[]|select(.pull_request_review_id==<review_id>)|{id,path,line:(.line // .original_line),body}'
    ```

    1 件ずつ **対応する / 対応済み / 提案は採らない** に分ける。既に直っているものは
    `reviewThreads { isOutdated }` で先に仕分けると読む量が減る（誰も Resolve を押さないので
    `isResolved` は使えない）が、最後は差分を読んで確かめる。

    **そして 1 件を直したら、その形をコードベース全体に当てる。** レビュアが 1 巡に返す件数は少ないので、
    兄弟を残すことはそのまま巡を 1 つ買うことである。**巡を減らす唯一の道は、撃つ前に欠陥を減らすこと**
    であって、待ち方を工夫することではない:

    - **クラスを名指しする** —— 直す前に「この指摘は何の形か」を 1 文で書く。書けないなら掃けない。
    - **コードベース全体を掃き、件数と列挙の仕方を返信に書く。** **語で数えた件数を掃いた証拠にしない**
      —— 同じ対象を毎回ちがう「形」で掃くと、同じ 1 件が何巡も生き残る。
    - **規約を書いたら同じコミットでコーパスに当てる。** 規約だけ書いて次の巡に掃かせない。
    - **数や主張を動かしたら、その複製を全部当て直す**（README・docs・コミット本文・PR 本文）。
    - **先送りしない。** 「弱い」と書いて次バッチへ送るのは掃いたことにならない。維持するなら
      **理由をコード側のコメントか docs に**書く —— PR コメントに書くと、次の読み手は
      「見て残した」と「見ていない」を区別できない。

11. 全件に返信する。返信の下書きは **セッションの scratchpad に置き、作業ツリーに置かない**
    （コミットに紛れ込む）。本文はファイルから読ませる —— **`-F` の `@` はファイル読み込み**なので、
    バッククォート・改行・`**` をそのまま通せる。**単体 GET は自分が今作った返信でも 404 を返す**ので、
    検算は一覧側で行う:

    ```bash
    gh api -X POST "repos/iwmaeda/iwmaeda/pulls/<n>/comments/<commentId>/replies" \
      -F body=@<scratch>/reply.md
    gh api --paginate "repos/iwmaeda/iwmaeda/pulls/<n>/comments?per_page=100" \
      --jq '.[]|select(.in_reply_to_id==<commentId>)|"\(.id) \(.body|length)"'
    ```

    1 行目は `<N> 巡目で対応しました（<sha>）。`、続けて 指摘が正しかったのか / 読みは正しいが前提が
    古かったのか / 提案を採らなかったのか を明示する。**対応済みは直したコミットの sha を必ず引く**
    （引かない対応済みは、逃げと区別が付かない）。**提案を採らないときは `path:line` かテスト名か
    doc を挙げる** —「設計上の意図です」だけでは足りない。
    直すものが 1 件でもあれば 3 へ戻る。**全件が 対応済み / 提案は採らない なら 12 へ抜ける**。

12. `--merge` が無ければ完了を報告して終わる。**P1 を「提案は採らない」と判定していたら、報告の冒頭に
    出す**。あるなら CI green を待ってマージし、**マージできたことを検算する**（`--auto` でなければ直前に
    確認を取る）。

    **CI 待ちは「pending が無い」で判定してはいけない** —— 取得に失敗した出力は空で、空文字は
    `pending` も `fail` も含まないので、素朴な否定形の判定は**失敗を green に化けさせる**。だから
    `status` が全件 `COMPLETED` かつ `conclusion` が全件 `SUCCESS` のときだけ `ALL_PASS` を出し、
    それ以外（0 件・取得失敗・走行中）は `retry` に倒す。**この待ちも `run_in_background` で投げる**
    —— 20 周 ×（`timeout 25` ＋ `sleep 30`）で最悪 約 18 分。前景だとツールの既定タイムアウトに
    殺されて何も出ない:

    ```bash
    V='CI_WAIT=timeout'; F=0
    PR=$(timeout 25 gh pr list --head "$(git branch --show-current)" --state open --json number -q '.[0].number' 2>/dev/null) || { echo "CI_WAIT=error reason=api stage=setup"; exit 0; }
    case "${PR:-}" in ''|*[!0-9]*) echo "CI_WAIT=error reason=no-pr"; exit 0;; esac
    for i in $(seq 1 20); do
      out=$(timeout 25 gh pr view "$PR" --json statusCheckRollup \
        --jq '.statusCheckRollup[]|"\(.status) \(.conclusion) \(.name)"' 2>/dev/null); r=$?
      if [ $r -ne 0 ]; then
        F=$((F + 1)); [ $F -ge 5 ] && { echo "CI_WAIT=error reason=api pr=$PR"; exit 0; }; sleep 30; continue
      fi
      F=0
      k=$(printf '%s\n' "$out" | awk 'NF==0{next}{n++; if($1!="COMPLETED")p=1; else if($2!="SUCCESS")b=1}
        END{print (n==0||p)?"retry":(b?"CHECKS_FAILED":"ALL_PASS")}')
      [ "$k" = retry ] && { sleep 30; continue; }
      echo "$out"; V=$k; break
    done
    echo "$V"
    ```

    出力は `ALL_PASS` / `CHECKS_FAILED` / `CI_WAIT=timeout` / `CI_WAIT=error reason=api`
    （`stage=setup` 付きを含む）/ `CI_WAIT=error reason=no-pr` の 5 つ。
    `no-pr` は**ブランチに開いている PR が無い**ので、マージではなく手順 6 の側を疑う。
    `api` は**取得そのものが失敗した**ので、CI の遅さではなく `gh` の疎通を疑う。

    **失敗側を `CHECKS_FAILED` と名付けているのは意図的** —— `NOT_ALL_PASS` のような名前だと
    `ALL_PASS` を**部分文字列として含む**ので、`grep -q ALL_PASS` や `[[ "$V" == *ALL_PASS* ]]` が
    **CI 失敗時にも真になる**。12 の awk が `$1 $2` を先に並べたのと同じで、穴は構造的に消す。

    **マージしてよいのは `[ "$V" = "ALL_PASS" ]` が真のときだけ**（完全一致。部分一致や
    「`ALL_PASS` という語が出力に在るか」で判定しない）。そのうえでマージし、検算する。
    **`sha=` で検査した commit を pin する** —— `ALL_PASS` を見た commit と、実際にマージされる
    commit が同じである保証は無い。不一致なら GitHub が 409 を返すので、fail-closed の側に倒れる:

    ```bash
    gh api -X PUT "repos/iwmaeda/iwmaeda/pulls/<n>/merge" \
      -f merge_method=merge -f sha="$(git rev-parse HEAD)"
    gh pr view <n> --json state,mergedAt --jq '"MERGED=\(.state) at=\(.mergedAt)"'
    ```

    **`MERGED=MERGED` かつ `at=` が `null` でないときだけマージ成功と読む。** 各コマンドは
    `&&` で繋がっておらず、`PUT` が 409（sha 不一致・conflict）や 405 で落ちても
    **後続は変わらず成功する** —— `main` は元々在るので `git checkout main && git pull` は
    マージの有無に関わらず通り、**未マージを「マージ済み」と報告できてしまう**（`--auto` では
    誰も気付かない）。合格しなければ**ここで止め**、`PUT` のエラー本文を報告に出す。
    合格したときだけ次へ進む:

    ```bash
    git checkout main && git pull
    ```

## 注意

- **終端シグナルは 2 つのエンドポイントに割れている** — codex は指摘なし
  （`Codex Review: Didn't find any major issues.`）も失敗（`You have reached your Codex usage limits`）も
  `/issues/<n>/comments` の **issue コメント**として返し、PR #8 / #11 の `/pulls/<n>/reviews` は空だった。
  gemini は逆に `/pulls/<n>/reviews` の **review** で返す（PR #4 / #5）。片方だけ見るポーリングは、
  レビュアーによって永久に待つか、レート制限に気づかず待つかのどちらかになる。8 の GraphQL クエリが毎周
  comments・reviews・reactions を**1 回の呼び出しで同時に**引いているのはこのため。
- **PR は `gh pr view` ではなく `gh pr list --state open` で引く** —— `gh pr view` は
  **マージ済み PR を返す**。この repo は `deleteBranchOnMerge` が `false` で、マージ済みのローカル枝が
  6 本残っている。掴んだ瞬間 8 は**その PR の古い履歴**からトリガーを拾い、前の PR の最後の判定が
  今巡の判定として出てくる。`gh pr list --head … --state open` はマージ済みの枝で空を返すので
  `no-pr` に落ちる＝ fail-closed。
- **トリガー検出の正規表現はレビュアー名に閉じる** —— `[a-z-]+` は
  `@iwmaeda review this before merging` のような**ごく自然な人間のコメント**に当たる。8 は毎周
  `tail -1` で最新のトリガーを採り直すので、本物のトリガーの後にデコイが来ると基準時刻が前進し、
  **その間に届いていた判定が `$2>t` で落ちる**。**応答済みを未導入と診断する**向きの壊れ方なので、
  `(codex|gemini|claude)` に閉じてある。
- **`gh` の呼び出しは `timeout` で包む** —— `gh` がエラーを返さず**ハングした**場合、コマンド置換が
  戻らないので `r=$?` にも `[ "$SECONDS" -lt "$END" ]` にも到達せず、**1 行も出さないまま黙る**。
  9 の表にも 12 の出力一覧にも「1 行も来なかった」は無いので、沈黙は読み手に何も伝えない。`timeout` の 124 は
  非ゼロなので、既存の `F` カウンタと `retry` にそのまま流れる（新しい分岐は要らない）。
- **8 と 12 のスクリプトは引数を取らず、自分で repo・PR を引く。これは体裁ではなく機能** — 権限規則は
  コマンド文字列の前方一致で当たるので、巡ごとに PR 番号やタイムスタンプを埋め込むと**文字列が毎巡
  変わり、毎巡プロンプトが出る**。`--auto` はそこで死ぬ。文字列が恒久的に同一だからこそ「常に許可」が
  1 度で永久に効く。**だから貼るときに整形し直してはいけない** — 改行を詰めた写しは別の文字列になる。
  **禁じているのは「貼るたびに変える」ことであって、このファイルを直すことではない** —— フェンスを
  編集すると新しい恒久文字列が定まるだけで、代償は**再承認 1 回**。ただし直したら分岐を実走し直す。
  埋め込みの `<n>` は、貼り替えを忘れると `n` という名のファイルからの**リダイレクト**として通って
  しまい、`bash -n` でも捕まらない。
- **暴走はここから起きる: 新しいコミットが無いのにレビューを撃ち直すこと。** レビュアーが見るのは差分で
  あって返信ではないので、HEAD が同じまま撃つと同じ指摘が返り、レビュアーの枠だけが減る。**トリガーを
  撃ってよいのは `git rev-parse HEAD` が前回のトリガー時と違うときだけ**、を不変条件として守る。
  全件が 対応済み / 提案は採らない で終わった巡は、返信だけ出して抜ける。
  **セッションをまたいで再開したときは、控えた HEAD がもう手元に無い。** そのときは
  `--force` を禁じてあることを使って導出する —— **HEAD のコミット日時が最後のトリガーより後なら、
  そのトリガー以降に新しいコミットが在る**（手順は commit → push → トリガーの順なので、
  既に撃った HEAD のコミット日時は必ずそのトリガーより前）:

  ```bash
  TZ=UTC git log -1 --format=%cd --date=format-local:%Y-%m-%dT%H:%M:%SZ   # 8 の trigger= と比較する
  ```

  **`--date=format:` を使ってはいけない** —— あれは変換せず `+09:00` の壁時計をそのまま `Z` と
  改称するので **9 時間ぶん未来にずれ**、しかも**常に「HEAD のほうが新しい」側に転ぶ**。
  つまり不変条件が防ぎたい暴走を、そのまま許す向きに壊れる。変換するのは `format-local:` のほう。

- **フェンスの終端 exit は、9 の表の 終了／中断 の行と `pending` だけに対応していなければならない。**
  8 は「もう報告した」を記憶せず、`TS` はトリガー時刻に固定されたままである。だから
  **「継続」と分類されるシグナルを終端 exit にすると、撃ち直すたびに同じ行が初回反復で再び一致して
  即 exit する** —— `sleep 30` に一度も入らない無限ループになる。gemini の前口上
  （`## Summary of Changes`）を `$J` の comment 分岐で落としているのはこのため。**親切心で
  復元してはいけない。** 前口上を見せたいなら、終端にしない別の行（`INTERIM=` など）として出す。
- **stale review は指摘を捨てて撃ち直す、拾わない** — `.line` が `null` のことが多く、既に無い差分に対する
  「この行を直せ」は対応先を推測することになる。推測で作ったコミットは「直したと称して直っていない」
  ものになり、次の巡で同じ指摘が返る。撃ち直しは 1 巡に 1 度だけ許し、2 度目は中断する。
- **stale の判定は body ではなく commit の sha で行う** — REST の `commit_id`（GraphQL では
  `commit{oid}`）は必ず在るが、body の `**Reviewed commit:**` 行は欠けることがある。
  body を読む実装は黙って照合を飛ばす。
- **comment・review の IO は `gh api`（REST）と GraphQL を通す** — この環境の `gh` は
  **2.4.0 (2022-03)** で、`gh pr checks` は `--web` しか持たない（`--watch` も `--json` も無い）。
  マージも `gh pr merge` ではなく REST の `PUT …/merge` を使い、`state` / `mergedAt` で
  **マージできたことを検算する**。`gh pr view --json …` / `gh pr list` / `gh pr edit --body-file` と
  GraphQL は使ってよい —— **PR 本文の更新まで REST に回す必要は無い**（`--body-file` は 2.4.0 に在る）。
- **`-f` と `-F` を取り違えるとトリガーが投稿できない** — `-F` は `@` をファイル読み込みと解釈するので
  `-F body='@codex review'` は `open codex review: no such file` で落ちる。トリガーは `-f`、
  ファイルから読む返信は `-F body=@reply.md`。**同じコマンドの中で使い分ける**。
- **standalone の `jq` はこの環境に無い** — `command -v jq` は空。`gh api --jq` が動くのは
  **gh が jq 実装を内蔵**しているからで、`jq` コマンドがあることを意味しない。
  **パイプで `jq` に渡す手順を書かない。**
- **`gh api` の失敗はエラー**オブジェクト**で返るので、素朴な `--jq` はもっともらしい数を出す** —
  `{message, documentation_url, status}` に `length` を当てると **`3`** が返る。配列の要素数に見えるが
  キー数である。だから 8 は**失敗を出力の空さで判定せず、`gh` の終了コードだけで判定する** ——
  「取得に失敗した」（`error reason=api`）と「トリガーが本当に無い」（`error reason=no-trigger`）は
  別の結論で、空文字はその両方に見える。
- **「悪い印が無い」を「良い」と読まない** — 取得に失敗した出力は空で、空文字は `pending` も `fail` も
  含まないので、**素朴な否定形の判定はすべて失敗を成功に化けさせる**。ただし**手当ては 8 と 12 で違う**:
  **8 は `gh` の終了コードだけで判定する**（上の `--jq` が `3` を返す例のとおり、失敗の出力は空とは
  限らない）。**12 は取得できた行の形で判定する** —— `status` が全件 `COMPLETED` かつ `conclusion` が
  全件 `SUCCESS` のときだけ緑と読み、0 件・走行中・欠損はすべて `retry` に倒す。
- **トリガーが無いことは、判定が無いことではない** — 8 は `TRIG` 行が 1 つも無いと中断するが、
  **bot の判定はトリガー無しでも来る**（この repo でも PR #1 / #2 / #3 / #6 は自動レビューだけで
  トリガーが 0 件）。だから `TRIG` が無いときは bot 行の有無で `no-trigger` と
  **`untriggered-verdict`** に割り、後者は `bot=` に本文を載せる。**判定は自動で採用しない** —
  トリガー時刻が無いと「それが今の HEAD のものか」を言えないので、中断のまま理由だけを正す。
- **`VERDICT=` 行のキーはアンカーを付けて取る。位置で取らない** — `$J` は bot コメント本文を
  最大 110 文字**そのまま**行へ埋め、8 はその後ろに `pr=…` と `trigger=…` を足す。区切りも引用も
  無いので、bot の本文に `pr=` や `commit=` に見える文字列が入ると（`__typename=="Bot"` しか
  見ていない以上、別の bot の本文もここまで届く）、**「最初に見つかった `key=`」を取る実装は
  bot 側の文字列を掴む**。`pr=` / `trigger=` / `commit=` / `review_id=` は行末側から、
  キー名にアンカーを付けて取る。**「最後のフィールド」も使えない** —— 末尾は常に `trigger=` である。
- **12 のフェンスがチェック名を末尾に置いているのは意図的** — `gh pr checks` のタブ区切り出力を
  `awk` の既定 FS で読むと、名前に空白を含むチェック（`Build and Test`）が来たとき `$2` が状態列を
  指さず、**落ちているチェックが緑に化ける**。`statusCheckRollup` から `status` / `conclusion` を
  先に並べれば、この穴は構造的に消える（`$1` `$2` が名前に依存しない）。現在この repo のチェックは
  `check` と `test` の 2 本だけだが、外部のチェックは複数語の名前を出す。
- **12 の jq は CheckRun 前提** — legacy の `StatusContext`（`.state` / `.context` を持ち
  `.status` を持たない）が `statusCheckRollup` に混ざると `null null null` になり、`retry` に
  倒れ続けて **`ALL_PASS` に到達しない**。fail-closed 側なので誤マージにはならないが、毎回
  `CI_WAIT=timeout` で終わる。現在このリポジトリのチェックは Actions の check-run 2 本だけなので
  起きない。**外部の status API チェックを足すときは jq を見直す**（`.status // "COMPLETED"` /
  `.conclusion // .state` / `.name // .context` へフォールバックさせる）。
- **`SKIPPED` は `ALL_PASS` を止める。それでよい** — 12 は全件が literally `SUCCESS` のときだけ緑と
  読む。止まったら印字された行を読み、意図した skip なら**人が判断してマージする**。判定は緩めない。
- **CI の `concurrency` は `cancel-in-progress: true`** — CI 待ちの最中に push すると前の run が
  cancel され、`conclusion` が `CANCELLED` になって `CHECKS_FAILED` に落ちる。これは fail-closed だが、
  **待っている間に push しない**規則を守れば起きない。
- **待っている間に push しない。`--force` は絶対に使わない** — rebase は inline comment の錨を全部
  打ち直し、開いているスレッドを迷子にし、`commit_id` の照合を無意味にする。force push が要ると
  判断したら、そこで中断して人に返す。
- **待機は同時に 1 つだけ** — 2 つ armed だと二重に報告が来て巡目の数え方が狂う。前の待機が生きている
  可能性があるなら、撃ち直さずその判定を待つ。
- **bot の定型文は「指摘が無ければ 👍 を付ける」と書くが、その経路は観測されていない** — この repo の
  トリガーはリアクションが全件ゼロで、指摘なしは毎回コメントで返っている。受理シグナルの本命は
  コメントで、👍 は最後の受け皿。👍 で終わった巡は「未観測の経路を通った」と報告に書く。
- **数秒で返ってきた応答はまず失敗を疑う** — 実測の応答は codex が約 3〜4 分（PR #8 / #11）。
  中断したときは巡数と PR 番号を報告に残し、再開できるようにする。
- **シェルの状態は Bash 呼び出しをまたいで残らない** — 前の呼び出しで置いた `S=…` は次の呼び出しでは
  空になる。だから各コマンドは自己完結させ、repo は直書きするか `gh repo view` でその場で引く。
- **`.env*` の中身をコメントに引かない** — 秘密に触れる指摘には `path:line` だけで答える。
- **`mise exec --` は前置しない** — この環境では mise が入れた Linux の `node` / `npm` が PATH の
  先頭側に居り、素の `npm run …` がそのまま当たる（Windows 側のシムは後方で完全に隠れている）。
  CI も `npm run check:all` を素で呼ぶので、前置するとローカルと CI の呼び方がずれる。
- `.claude/**` と `.agents/**` は markdownlint と Prettier の**対象**（`markdownlint-cli2` は
  `dot: true` でドットディレクトリに降りる）。このファイルを編集したら `npm run check:docs` を通す。
- **未実走の経路がある。実データで踏めていないものを列挙しておく** —— どれも fail-closed 側
  （誤マージではなく `retry` / `timeout` / 中断）に倒れるが、**正しく分類される保証は無い**。
  ここを踏んだ巡は、報告に「未実走の経路を通った」と書く:
  - `VERDICT=reaction` —— この repo のトリガーはリアクションが全件ゼロで、一度も発火していない。
  - 9 の表の**分岐履歴の中断**（`--is-ancestor` が `1`）と**ローカルに無い**（`128`）——
    終了コード自体は実測したが、bot の review がその状態で届くところまでは踏めていない。
  - 12 の `CHECKS_FAILED` / `SKIPPED` / legacy `StatusContext` —— この repo の CI は
    `check` と `test` の 2 本で、いずれも `SUCCESS` 以外を返したことがない。
  - **回帰テストを置いていない理由** —— 分類ロジックをテスト側へ写すと、正本を複製することになり、
    `docs/development/project-structure.md` の不複製規則と衝突する。上の開示で代える。
    フェンスを直したときは、代わりに**実データで分岐を実走し直す**（この文書の冒頭の規則）。
